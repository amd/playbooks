#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
Create GitHub issues for playbooks that failed in the nightly OrchestrAI run.

test-playbooks-orchestrai.yml runs this after its batch jobs, on the scheduled
run of main only. It reads every batch.json the batch jobs uploaded
(orchestrai_batch_verdict.py) and, for each playbook that failed on a device
and OS:

1. Builds a stable title, ``[CI] <playbook> failed on <device> (<platform>)``,
   with ``<locale>/`` before a localized playbook's ID.
2. Looks for an open issue with exactly that title and the ``ci-test-failure``
   label. If there is one, it comments with the new run instead of opening
   another, so nightly failures do not pile up.
3. Otherwise opens an issue with the run, the OrchestrAI and ReportPortal
   results, the test counts, and the command that runs the playbook again on
   that device and OS.

Only test failures open issues. A playbook the machine or pipeline never let
finish (NOT_RUN, INTERRUPTED: orchestrai_verdict.INFRA_STATUSES) is an
infrastructure problem, and a localized playbook that ran exactly its English
version's tests (``covered_by``) is reported through the English issue.

The script calls the GitHub REST API with ``urllib``; ``GITHUB_TOKEN`` must be
set unless ``--dry-run`` is given.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Optional


ISSUE_LABEL = "ci-test-failure"
TITLE_PREFIX = "[CI]"
GITHUB_API = "https://api.github.com"
WORKFLOW_FILE = "test-playbooks-orchestrai.yml"

# Outcomes that open no issue: a pass, or a playbook that never got to finish
# (orchestrai_verdict.INFRA_STATUSES).
NOT_A_TEST_FAILURE = frozenset({"PASSED", "NOT_RUN", "INTERRUPTED"})


def build_title(playbook: str, device: str, platform: str) -> str:
    """The canonical title, stable so the dedupe lookup always finds it:

        [CI] <playbook> failed on <device> (<platform>)
    """
    return f"{TITLE_PREFIX} {playbook} failed on {device} ({platform})"



def _api_request(
    method: str,
    url: str,
    token: str,
    body: Optional[dict] = None,
) -> tuple[int, Any]:
    """Perform an authenticated GitHub REST request.

    Returns ``(status_code, parsed_json_or_text)``.  Network/HTTP errors
    above 500 are raised; 4xx errors are returned to the caller so callers
    can decide what to do (e.g. 404s during dedupe lookups).
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "playbooks-ci-failure-reporter",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            payload = resp.read().decode("utf-8")
            try:
                return resp.status, json.loads(payload) if payload else None
            except json.JSONDecodeError:
                return resp.status, payload
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


def find_existing_issue(repo: str, token: str, title: str) -> Optional[dict]:
    """Return the open issue matching ``title`` exactly, or None.

    GitHub's search API is tokenized, so we list all open issues carrying the
    automation label and compare titles client-side. The label keeps the
    candidate list bounded.
    """
    page = 1
    while True:
        url = (
            f"{GITHUB_API}/repos/{repo}/issues"
            f"?state=open&labels={urllib.parse.quote(ISSUE_LABEL)}"
            f"&per_page=100&page={page}"
        )
        status, body = _api_request("GET", url, token)
        if status != 200 or not isinstance(body, list):
            sys.stderr.write(
                f"Could not list issues (status={status}): {body!r}\n"
            )
            return None

        for issue in body:
            # /issues returns PRs too; skip them.
            if issue.get("pull_request"):
                continue
            if issue.get("title") == title:
                return issue

        if len(body) < 100:
            return None
        page += 1


def create_issue(
    repo: str, token: str, title: str, body: str, labels: list[str]
) -> Optional[dict]:
    url = f"{GITHUB_API}/repos/{repo}/issues"
    status, payload = _api_request(
        "POST",
        url,
        token,
        body={"title": title, "body": body, "labels": labels},
    )
    if status not in (200, 201):
        sys.stderr.write(
            f"Failed to create issue '{title}' (status={status}): {payload!r}\n"
        )
        return None
    return payload if isinstance(payload, dict) else None


def comment_on_issue(
    repo: str, token: str, issue_number: int, body: str
) -> bool:
    url = f"{GITHUB_API}/repos/{repo}/issues/{issue_number}/comments"
    status, payload = _api_request("POST", url, token, body={"body": body})
    if status not in (200, 201):
        sys.stderr.write(
            f"Failed to comment on issue #{issue_number} (status={status}): {payload!r}\n"
        )
        return False
    return True




def render_dispatch_command(repo: str, row: dict) -> str:
    """The command that runs this playbook again on the same device and OS."""
    command = (f"gh workflow run {WORKFLOW_FILE} --repo {repo} "
               f"-f playbook_id={row['playbook_id']} -f device={row['arch']} "
               f"-f platform={row['platform']}")
    if row.get("locale"):
        command += f" -f locale={row['locale']}"
    return command


def failed_rows(results_root: Path) -> list[dict]:
    """The test failures in every batch.json under results_root, each with the
    playbook's counts from the summary.json next to it when there is one."""
    rows = []
    for batch in sorted(results_root.rglob("batch.json")):
        try:
            batch_rows = json.loads(batch.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            sys.stderr.write(f"Skipping {batch}: {exc}\n")
            continue
        for row in batch_rows:
            if row.get("covered_by") or row.get("outcome") in NOT_A_TEST_FAILURE:
                continue
            try:
                summary = json.loads((batch.parent / row["playbook"] / "summary.json")
                                     .read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                summary = {}
            rows.append({**row, "summary": summary})
    return rows


def render_body(row: dict, repo: str, run_url: str, sha: str) -> str:
    """The markdown body of a new failure issue."""
    summary = row.get("summary") or {}
    lines = [
        f"`{row['playbook']}` failed in the nightly OrchestrAI run on "
        f"**{row['arch']}** ({row['platform']}).",
        "",
        f"- **Result:** {row['outcome']}" + (f": {row['reason']}" if row.get("reason") else ""),
    ]
    if summary.get("total_tests"):
        lines.append(f"- **Tests:** {summary.get('passed', 0)} passed, "
                     f"{summary.get('failed', 0)} failed, {summary.get('skipped', 0)} skipped")
    if row.get("required"):
        lines.append("- **Required:** yes (✦): a pull request changing this playbook "
                     "cannot pass with this failure")
    lines += [
        f"- **Workflow run:** {run_url or 'n/a'}",
        f"- **Batch job:** {row.get('job_url') or 'n/a'}",
        f"- **OrchestrAI run:** {row.get('run_url') or 'n/a'}",
        f"- **ReportPortal:** {row.get('rp_url') or 'n/a'}",
        f"- **Commit:** `{sha or 'unknown'}`",
        "",
        "Each test's output is in the OrchestrAI run and in ReportPortal.",
        "",
        "## Run it again on this device and OS",
        "",
        "```bash",
        render_dispatch_command(repo, row),
        "```",
        "",
        "Or comment on a pull request that fixes it: "
        f"`!orc {row['playbook_id']} device={row['arch']} platform={row['platform']}"
        + (f" locale={row['locale']}" if row.get("locale") else "") + "`",
        "",
        "---",
        "_Opened and deduplicated by `.github/scripts/create_failure_issues.py`. Close it "
        "once the failure is fixed; a later failure on the same device and OS opens a new one._",
    ]
    return "\n".join(lines)


def process_failures(*, repo: str, token: str, results_root: Path, run_url: str,
                     sha: str, dry_run: bool) -> int:
    """Open, or comment on, an issue for every failed playbook. Returns the count opened."""
    rows = failed_rows(results_root)
    if not rows:
        print(f"No failed playbooks in {results_root}.")
        return 0
    if not dry_run and not token:
        sys.stderr.write("Error: GITHUB_TOKEN is required to create issues. "
                         "Re-run with --dry-run to preview without writing.\n")
        sys.exit(2)

    created = 0
    for row in rows:
        title = build_title(row["playbook"], row["arch"], row["platform"])
        print(f"\n--- Failure: {title} ---")
        if dry_run:
            print("(dry-run) would create issue with body:\n")
            print(render_body(row, repo, run_url, sha))
            continue

        existing = find_existing_issue(repo, token, title)
        if existing:
            print(f"Open issue already exists (#{existing.get('number')}): "
                  f"{existing.get('html_url')}. Adding a follow-up comment.")
            comment_on_issue(repo, token, int(existing["number"]), "\n".join([
                "Failed again in a later nightly run.",
                "",
                f"- **Result:** {row['outcome']}"
                + (f": {row['reason']}" if row.get("reason") else ""),
                f"- **Workflow run:** {run_url or 'n/a'}",
                f"- **OrchestrAI run:** {row.get('run_url') or 'n/a'}",
                f"- **ReportPortal:** {row.get('rp_url') or 'n/a'}",
                f"- **Commit:** `{sha or 'unknown'}`",
            ]))
            continue

        issue = create_issue(repo, token, title, render_body(row, repo, run_url, sha),
                             [ISSUE_LABEL, "bug"])
        if issue is not None:
            print(f"Created issue: {issue.get('html_url')}")
            created += 1
    return created


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", required=True, help="GitHub repo, e.g. owner/name")
    parser.add_argument("--results-dir", required=True, type=Path,
                        help="Directory holding the batch jobs' batch.json artifacts")
    parser.add_argument("--run-url", default="")
    parser.add_argument("--sha", default="")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the issue bodies instead of calling the GitHub API")
    args = parser.parse_args()

    created = process_failures(repo=args.repo, token=os.environ.get("GITHUB_TOKEN", ""),
                               results_root=args.results_dir, run_url=args.run_url,
                               sha=args.sha, dry_run=args.dry_run)
    print(f"\nDone. Issues created: {created}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
