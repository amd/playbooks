#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
Create GitHub issues for failed playbook tests.

This script is invoked from the ``Test Playbooks`` workflow after the test
runner has executed.  For every failure record produced by
``run_playbook_tests.py`` (under ``test-results/<playbook>/failures/*.json``)
it:

1. Builds a stable, human-readable issue title that encodes the playbook,
   test id, device, and OS (``[CI] <playbook> / <test_id> failed on <device>
   (<platform>)``). Encoding all four pieces makes the title unique enough to
   safely dedupe against, while still satisfying the requirement that the
   title surface the playbook + device + OS.
2. Searches the repository for an open issue with the *exact* same title and
   the ``ci-test-failure`` label. If one already exists, it's left alone (and
   a comment is appended pointing at the new run for traceability). This
   prevents duplicate issues from accumulating across nightly runs.
3. Otherwise, opens a fresh issue containing everything a maintainer needs to
   reproduce the failure: the full failing test code, captured logs, the
   exact runner labels (so they know which OS / hardware to target), and the
   ``gh workflow run`` command to dispatch just that test on the same matrix
   entry.

The script talks to the GitHub REST API directly via ``urllib`` so it has no
binary dependency on the ``gh`` CLI (some self-hosted runners don't ship it).
``GITHUB_TOKEN`` must be present in the environment for write operations.
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


def build_title(playbook: str, test_id: str, device: str, platform: str) -> str:
    """Return the canonical issue title for a given failure scope.

    The format is intentionally stable so dedupe lookups always succeed:

        [CI] <playbook> / <test_id> failed on <device> (<platform>)
    """
    return f"{TITLE_PREFIX} {playbook} / {test_id} failed on {device} ({platform})"


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


def render_dispatch_command(repo: str, workflow_file: str, playbook: str) -> str:
    """Show maintainers how to re-run just this matrix entry via ``gh``.

    The Test Playbooks workflow already accepts a ``playbook_id`` input, so
    the simplest reproduction is a single ``gh workflow run``.
    """
    return (
        f"gh workflow run {workflow_file} --repo {repo} "
        f"-f playbook_id={playbook}"
    )


def render_body(
    failure: dict,
    repo: str,
    workflow_file: str,
    runner_labels: list[str],
    runner_name: str,
    run_url: str,
    sha: str,
) -> str:
    """Assemble the markdown body for a new failure issue."""
    playbook = failure["playbook_id"]
    platform = failure["platform"]
    device = failure.get("device") or "all"
    test = failure["test"]
    result = failure["result"]

    test_id = test["id"]
    language = test.get("language") or "bash"
    code = test.get("code") or ""
    setup = test.get("setup")
    workdir = test.get("workdir")
    line_number = test.get("line_number")
    timeout = test.get("timeout")

    stdout = result.get("stdout_excerpt") or ""
    stderr = result.get("stderr_excerpt") or ""
    error_message = result.get("error_message") or ""
    exit_code = result.get("exit_code")

    repro_command = render_dispatch_command(repo, workflow_file, playbook)
    runner_label_str = (
        ", ".join(f"`{lbl}`" for lbl in runner_labels) if runner_labels else "n/a"
    )

    parts: list[str] = []
    parts.append(
        f"This issue was opened automatically by the **Test Playbooks** workflow "
        f"after the test `{test_id}` failed on the `main` branch."
    )
    parts.append("")
    parts.append("## Failure scope")
    parts.append("")
    parts.append(f"- **Playbook:** `{playbook}`")
    parts.append(f"- **Test id:** `{test_id}`")
    parts.append(f"- **Device:** `{device}`")
    parts.append(f"- **Operating system:** `{platform}`")
    parts.append(f"- **Runner labels:** {runner_label_str}")
    parts.append(f"- **Runner name:** `{runner_name or 'unknown'}`")
    parts.append(f"- **Commit:** `{sha or 'unknown'}`")
    if run_url:
        parts.append(f"- **Workflow run:** {run_url}")
    parts.append("")

    parts.append("## Hardware / OS to use to reproduce")
    parts.append("")
    parts.append(
        f"Run the failing test on a machine that matches the runner labels above "
        f"(OS = `{platform}`, device = `{device}`). The repo's self-hosted runners "
        f"already advertise these labels; if you reproduce locally, use the same "
        f"OS family and the same AMD device class."
    )
    parts.append("")

    parts.append("## How to dispatch the same test from CI")
    parts.append("")
    parts.append(
        "Re-run only the failing playbook on the same matrix entry by triggering "
        "the workflow with the playbook id:"
    )
    parts.append("")
    parts.append("```bash")
    parts.append(repro_command)
    parts.append("```")
    parts.append("")
    parts.append(
        "The workflow's matrix narrows down to this `(device, platform)` "
        "combination automatically based on the playbook's `tested_platforms`."
    )
    parts.append("")

    parts.append("## How to run just this test locally")
    parts.append("")
    parts.append("```bash")
    parts.append(
        f"python .github/scripts/run_playbook_tests.py "
        f"--playbook {playbook} --platform {platform} --device {device}"
    )
    parts.append("```")
    parts.append("")
    parts.append(
        f"The runner extracts test blocks from "
        f"`playbooks/*/{playbook}/README.md` (the failing block starts around "
        f"line {line_number})."
    )
    parts.append("")

    parts.append("## Failing test (verbatim from the README)")
    parts.append("")
    if setup:
        parts.append(f"- **Setup:** `{setup}`")
    if workdir:
        parts.append(f"- **Working directory:** `assets/{workdir}`")
    if timeout:
        parts.append(f"- **Timeout:** `{timeout}s`")
    parts.append("")
    parts.append(f"```{language}")
    parts.append(code)
    parts.append("```")
    parts.append("")

    parts.append("## Result")
    parts.append("")
    parts.append(f"- **Exit code:** `{exit_code}`")
    if error_message:
        parts.append(f"- **Runner error:** {error_message}")
    parts.append("")

    if stderr:
        parts.append("### stderr (last lines)")
        parts.append("")
        parts.append("```")
        parts.append(stderr)
        parts.append("```")
        if result.get("stderr_truncated"):
            parts.append("")
            parts.append(
                "_stderr was truncated; see the workflow run artifacts for the full log._"
            )
        parts.append("")

    if stdout:
        parts.append("### stdout (last lines)")
        parts.append("")
        parts.append("```")
        parts.append(stdout)
        parts.append("```")
        if result.get("stdout_truncated"):
            parts.append("")
            parts.append(
                "_stdout was truncated; see the workflow run artifacts for the full log._"
            )
        parts.append("")

    parts.append("---")
    parts.append(
        "_This issue is opened and deduplicated by "
        "`.github/scripts/create_failure_issues.py`. Close it once the failure is "
        "fixed; subsequent failures with the same scope will reopen a fresh issue._"
    )

    return "\n".join(parts)


def collect_failure_files(results_root: Path, playbook: str) -> list[Path]:
    failures_dir = results_root / playbook / "failures"
    if not failures_dir.exists():
        return []
    return sorted(p for p in failures_dir.glob("*.json") if p.is_file())


def process_failures(
    *,
    repo: str,
    token: str,
    workflow_file: str,
    results_root: Path,
    playbook: str,
    runner_labels: list[str],
    runner_name: str,
    run_url: str,
    sha: str,
    dry_run: bool,
) -> int:
    """Create (or skip) issues for every recorded failure. Returns count created."""
    failure_files = collect_failure_files(results_root, playbook)
    if not failure_files:
        print(f"No failure records found under {results_root}/{playbook}/failures.")
        return 0

    if not dry_run and not token:
        sys.stderr.write(
            "Error: GITHUB_TOKEN is required to create issues. "
            "Re-run with --dry-run to preview without writing.\n"
        )
        sys.exit(2)

    created = 0
    for failure_file in failure_files:
        try:
            failure = json.loads(failure_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            sys.stderr.write(f"Skipping {failure_file}: {exc}\n")
            continue

        playbook_id = failure.get("playbook_id", playbook)
        platform = failure.get("platform", "unknown")
        device = failure.get("device") or "all"
        test_id = failure.get("test", {}).get("id", "unknown")

        title = build_title(playbook_id, test_id, device, platform)
        body = render_body(
            failure=failure,
            repo=repo,
            workflow_file=workflow_file,
            runner_labels=runner_labels,
            runner_name=runner_name,
            run_url=run_url,
            sha=sha,
        )

        print(f"\n--- Failure: {title} ---")

        if dry_run:
            print("(dry-run) would create issue with body:\n")
            print(body)
            continue

        existing = find_existing_issue(repo, token, title)
        if existing:
            print(
                f"Open issue already exists (#{existing.get('number')}): "
                f"{existing.get('html_url')}. Adding a follow-up comment."
            )
            comment_lines = [
                "Test failed again on a subsequent CI run.",
                "",
                f"- **Workflow run:** {run_url or 'n/a'}",
                f"- **Commit:** `{sha or 'unknown'}`",
                f"- **Runner:** `{runner_name or 'unknown'}` "
                f"({', '.join(runner_labels) if runner_labels else 'n/a'})",
            ]
            comment_on_issue(
                repo, token, int(existing["number"]), "\n".join(comment_lines)
            )
            continue

        issue = create_issue(repo, token, title, body, [ISSUE_LABEL, "bug"])
        if issue is None:
            continue

        print(f"Created issue: {issue.get('html_url')}")
        created += 1

    return created


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="GitHub repo, e.g. owner/name")
    parser.add_argument(
        "--playbook",
        required=True,
        help="Playbook id whose failure files we should process",
    )
    parser.add_argument(
        "--results-dir",
        default="test-results",
        help="Root directory containing per-playbook test-results subfolders",
    )
    parser.add_argument(
        "--workflow-file",
        default="test-playbooks.yml",
        help="Workflow file name used in the dispatch reproduction command",
    )
    parser.add_argument("--runner-name", default=os.environ.get("RUNNER_NAME", ""))
    parser.add_argument(
        "--runner-labels",
        default="",
        help="Comma-separated list of runner labels (e.g. 'self-hosted,Windows,halo')",
    )
    parser.add_argument("--run-url", default="")
    parser.add_argument("--sha", default="")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the issue body instead of calling the GitHub API",
    )
    args = parser.parse_args()

    runner_labels = [l.strip() for l in args.runner_labels.split(",") if l.strip()]
    token = os.environ.get("GITHUB_TOKEN", "")

    created = process_failures(
        repo=args.repo,
        token=token,
        workflow_file=args.workflow_file,
        results_root=Path(args.results_dir),
        playbook=args.playbook,
        runner_labels=runner_labels,
        runner_name=args.runner_name,
        run_url=args.run_url,
        sha=args.sha,
        dry_run=args.dry_run,
    )

    print(f"\nDone. Issues created: {created}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
