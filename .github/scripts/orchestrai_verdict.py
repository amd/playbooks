#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
OrchestrAI per-playbook verdict
===============================

A batch build runs several playbooks on one machine, so the OrchestrAI pipeline build's
overall result can't tell us whether THIS playbook passed. The pipeline writes a
per-group rollup to its summary.json:

    groups["playbook-<id>"] = {passed, failed, skipped, errors, status}

keyed by the submission group id (independent of completion order). This script
resolves THIS playbook's verdict, preferring that rollup and falling back to the
build console's per-suite lifecycle if the rollup is absent.

Usage:
    orchestrai_verdict.py     (all inputs via env)

Env:
    BUILD_URL, ORCHESTRAI_PIPELINE_USER, ORCHESTRAI_PIPELINE_TOKEN, PLAYBOOK_ID, PLATFORM

Outputs:
    test-results/summary.json   (per-playbook counts, for artifact upload)
    rp_url=<reportportal launch url>  -> $GITHUB_OUTPUT
    exit 0 if PASSED, 1 otherwise (including: no verdict found for this playbook)
"""

import base64
import json
import os
import re
import sys
import urllib.request

COUNT_KEYS = ("passed", "failed", "skipped", "errors")

FETCH_TIMEOUT = 60


def fetch(url, user, token):
    """GET `url` with basic auth, returning "" on any failure.

    SECURITY: the credentials are deliberately NOT handed to a `curl -u
    user:token` subprocess. argv is world-readable via /proc/<pid>/cmdline and
    `ps` for the lifetime of the process, so on a shared/persistent self-hosted
    runner any other local process could read the pipeline token. Doing the HTTP
    in-process (stdlib only — this job has no pip install step) keeps the secret
    in this process's memory only.
    """
    req = urllib.request.Request(url)
    req.add_header("Authorization",
                   "Basic " + base64.b64encode(f"{user}:{token}".encode()).decode())
    try:
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as r:
            return r.read().decode("utf-8", "replace")
    except Exception:
        return ""


def status_from_group(grp):
    """PASSED/FAILED from a group rollup, or None if it carries no verdict
    (no status field and zero counts — i.e. nothing actually ran)."""
    status = grp.get("status")
    if status:
        return status
    counts = {k: grp.get(k) or 0 for k in COUNT_KEYS}
    if sum(counts.values()) == 0:
        return None  # ambiguous: group exists but ran nothing — don't call it PASS
    return "FAILED" if (counts["failed"] or counts["errors"]) else "PASSED"


def status_from_console(console, playbook):
    """Fallback: the console exposes the per-playbook suite lifecycle even when
    summary.json has no group for it:
        Started suite "playbook-<id> #<n>" ... id=<sid>
        Finished item <sid> -> PASSED|FAILED
    """
    esc = re.escape(playbook)
    m = re.search(rf'Started suite "playbook-{esc} #\d+".*?id=([0-9a-fA-F-]+)', console)
    if not m:
        return None
    sid = m.group(1)
    # The separator between the item id and the status is an arrow that renders
    # differently across console encodings (Unicode "→", ASCII "->", or mojibake
    # if the log was decoded wrong). Match any run of non-alphanumeric characters
    # rather than a specific arrow so the status is captured regardless.
    fin = re.findall(rf'Finished item {re.escape(sid)}[^A-Za-z0-9]+([A-Z]+)', console)
    return fin[-1] if fin else None


def main():
    user = os.environ.get("ORCHESTRAI_PIPELINE_USER", "")
    token = os.environ.get("ORCHESTRAI_PIPELINE_TOKEN", "")
    build_url = os.environ.get("BUILD_URL", "")
    playbook = os.environ.get("PLAYBOOK_ID", "")
    platform = os.environ.get("PLATFORM", "")

    if not playbook or not platform:
        print("::error::orchestrai_verdict.py: PLAYBOOK_ID and PLATFORM must be set",
              file=sys.stderr)
        sys.exit(1)

    group_key = f"playbook-{playbook}"
    os.makedirs("test-results", exist_ok=True)

    def write_summary(ok):
        json.dump(
            {"playbook_id": playbook, "platform": platform, "total_tests": 1,
             "passed": 1 if ok else 0, "failed": 0 if ok else 1,
             "skipped": 0, "results": []},
            open("test-results/summary.json", "w"), indent=2)

    if not build_url:
        write_summary(False)
        print(f"::error::No OrchestrAI pipeline build URL for {playbook} ({platform})")
        sys.exit(1)

    raw = fetch(f"{build_url}artifact/.pipeline/summary.json", user, token) or "{}"
    try:
        summary = json.loads(raw)
    except Exception:
        summary = {}

    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"rp_url={summary.get('rp_launch_url', '')}\n")

    # Primary: per-group rollup in summary.json.
    status, how = None, ""
    grp = (summary.get("groups") or {}).get(group_key)
    if isinstance(grp, dict):
        status = status_from_group(grp)
        if status:
            how = "summary.json groups"

    # Fallback: scrape the build console's suite lifecycle.
    if status is None:
        console = fetch(f"{build_url}consoleText", user, token)
        status = status_from_console(console, playbook)
        if status:
            how = "console suite lifecycle"

    if status is None:
        write_summary(False)
        groups_present = list((summary.get("groups") or {}).keys())
        print(f"::error::No verdict for {playbook} ({platform}): "
              f"no groups['{group_key}'] in summary.json and no suite result in the "
              f"console. groups present: {groups_present}")
        sys.exit(1)

    ok = (status == "PASSED")
    write_summary(ok)
    counts = {k: grp.get(k) for k in COUNT_KEYS} if isinstance(grp, dict) else {}
    print(f"{playbook} ({platform}): {'PASS' if ok else 'FAIL'} "
          f"(status={status}, via {how}, counts={counts})")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
