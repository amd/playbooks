#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
Discover self-hosted runners and build a restart matrix.

This script is invoked from the ``Restart Runners`` workflow. It queries the
GitHub REST API for every self-hosted runner registered to the repository
(name, OS, online/offline status, and labels) and filters that live list down
to the set the caller asked to restart. Nothing about the fleet is hardcoded:
machines added to or removed from a group are picked up automatically on the
next run, which is why this is preferred over a static name list.

Filtering is done by ANDing three optional criteria:

* ``--name``   exact runner name (e.g. ``xsj-aimlab-halo-0``). Restarts one box.
* ``--os``     ``Windows`` or ``Linux`` (or ``any``). Matched against the
               runner's OS label.
* ``--group``  a hardware label (e.g. ``halo``, ``stx``, ``krk``,
               ``rx7900xt``, ``rx9070xt``) or ``any``. Matched against the
               runner's labels.

So ``--os Windows --group halo`` selects the Windows Ryzen AI Max machines,
``--group any --os any`` (the cron default) selects the whole fleet, and
``--name xsj-aimlab-krk-02`` targets a single machine.

Offline runners are skipped: a job can never be dispatched to a runner that is
not connected, so including them would just hang the matrix entry.

The result is written to ``GITHUB_OUTPUT`` as ``matrix`` (a JSON array of
``{"runner": "<name>"}`` objects consumed by ``strategy.matrix.include``) and
``has_entries`` (``true``/``false``). It also prints a human-readable summary
to the step log.

Listing self-hosted runners requires an admin-scoped token, so ``GITHUB_TOKEN``
here must be a PAT with ``repo`` + ``manage_runners`` (classic: ``repo``)
scope, supplied via a secret. The default ``GITHUB_TOKEN`` cannot read this
endpoint.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any, Optional


GITHUB_API = "https://api.github.com"


def _api_request(method: str, url: str, token: str) -> tuple[int, Any]:
    """Perform an authenticated GitHub REST request.

    Returns ``(status_code, parsed_json_or_text)``. 5xx errors are raised;
    4xx errors are returned so the caller can surface a clear message (e.g. a
    403 when the token lacks ``manage_runners`` scope).
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "playbooks-runner-restarter",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            payload = resp.read().decode("utf-8")
            return resp.status, json.loads(payload) if payload else None
    except urllib.error.HTTPError as e:
        payload = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError:
            parsed = payload
        if e.code >= 500:
            sys.stderr.write(f"GitHub API {method} {url} -> {e.code}: {parsed}\n")
            raise
        return e.code, parsed


def list_runners(repo: str, token: str) -> list[dict]:
    """Return every self-hosted runner registered to ``repo`` (paginated)."""
    runners: list[dict] = []
    page = 1
    while True:
        url = f"{GITHUB_API}/repos/{repo}/actions/runners?per_page=100&page={page}"
        status, body = _api_request("GET", url, token)
        if status == 403:
            sys.stderr.write(
                "GitHub API returned 403 listing runners. The token needs "
                "admin/manage_runners scope (a PAT stored as a secret), not "
                "the default GITHUB_TOKEN.\n"
            )
            sys.exit(1)
        if status != 200 or not isinstance(body, dict):
            sys.stderr.write(f"Unexpected response listing runners ({status}): {body}\n")
            sys.exit(1)
        batch = body.get("runners", [])
        runners.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return runners


def label_names(runner: dict) -> set[str]:
    """Return the set of label names attached to a runner."""
    return {lbl.get("name", "") for lbl in runner.get("labels", [])}


def matches(
    runner: dict,
    name: Optional[str],
    os_filter: Optional[str],
    group: Optional[str],
) -> bool:
    """Return True if ``runner`` satisfies all active filters."""
    labels = label_names(runner)

    if name:
        if runner.get("name") != name:
            return False

    if os_filter and os_filter.lower() != "any":
        # GitHub attaches an OS label ("Windows"/"Linux") to self-hosted
        # runners; match case-insensitively to be safe.
        os_labels = {lbl.lower() for lbl in labels}
        if os_filter.lower() not in os_labels:
            return False

    if group and group.lower() != "any":
        if group not in labels:
            return False

    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a runner restart matrix.")
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--name", default="", help="Exact runner name, or empty")
    parser.add_argument("--os", dest="os_filter", default="any", help="Windows|Linux|any")
    parser.add_argument("--group", default="any", help="Hardware label, or any")
    args = parser.parse_args()

    token = os.environ.get("RUNNER_ADMIN_TOKEN") or os.environ.get("GITHUB_TOKEN", "")
    if not token:
        sys.stderr.write("No token in RUNNER_ADMIN_TOKEN or GITHUB_TOKEN.\n")
        return 1

    runners = list_runners(args.repo, token)

    selected: list[dict] = []
    skipped_offline: list[str] = []
    for r in runners:
        if not matches(r, args.name.strip() or None, args.os_filter, args.group):
            continue
        if r.get("status") != "online":
            skipped_offline.append(r.get("name", "<unknown>"))
            continue
        selected.append(r)

    # Human-readable summary in the step log.
    print(f"Discovered {len(runners)} runner(s) total.")
    print(
        f"Filters -> name={args.name or 'any'}, os={args.os_filter}, "
        f"group={args.group}"
    )
    if skipped_offline:
        print(f"Skipping {len(skipped_offline)} offline match(es): "
              f"{', '.join(skipped_offline)}")
    if selected:
        print("Will restart:")
        for r in selected:
            print(f"  - {r['name']} (labels: {', '.join(sorted(label_names(r)))})")
    else:
        print("No online runners matched the selection.")

    matrix = [{"runner": r["name"]} for r in selected]

    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as fh:
            fh.write(f"matrix={json.dumps(matrix)}\n")
            fh.write(f"has_entries={'true' if matrix else 'false'}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
