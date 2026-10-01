# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""Drop test-matrix entries whose self-hosted runner group is offline.

A required playbook test whose runner group has no online machine would sit
'queued' forever and wedge the merge gate. This filter is run at matrix-build
time: it asks the GitHub API which self-hosted runners are online, maps them to
hardware groups, and removes any matrix entry that could never be picked up.

Fail-open by design: if the runner list cannot be fetched (missing token, API
error, non-self-hosted matrix), every entry is kept, so this can only ever
*reduce* spurious queuing, never hide a runnable test.

Input:  a JSON array of matrix entries on stdin (as build_test_matrix.py emits).
Output: the filtered JSON array on stdout.
Env:    GITHUB_REPOSITORY (owner/repo); RUNNER_STATUS_TOKEN (a token with repo
        'admin' / actions runner read access). Without the token, input is
        echoed unchanged.
Any dropped entries are reported on stderr as GitHub Actions warnings.
"""

import json
import os
import sys
import urllib.error
import urllib.request


def annotate(level: str, message: str) -> None:
    prefix = f"::{level}::" if os.environ.get("GITHUB_ACTIONS") else ""
    print(f"{prefix}{message}", file=sys.stderr)


def online_groups(repo: str, token: str) -> set[str] | None:
    """Return the set of hardware-group labels that have >=1 online runner.

    Returns None if the runner list cannot be established (fail-open signal).
    """
    url = f"https://api.github.com/repos/{repo}/actions/runners?per_page=100"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.load(resp)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        annotate("warning", f"Could not list runners ({exc}); keeping all matrix entries")
        return None

    groups: set[str] = set()
    for runner in data.get("runners", []):
        if runner.get("status") != "online":
            continue
        # A runner advertises its hardware group as one of its labels
        # (halo, stx, krk, grgh, ...). Collect them all; the matrix entry's
        # 'arch' is matched against this set.
        for label in runner.get("labels", []):
            name = label.get("name", "")
            groups.add(name)
    return groups


def main() -> int:
    entries = json.load(sys.stdin)
    if not isinstance(entries, list):
        annotate("error", "expected a JSON array of matrix entries on stdin")
        return 1

    repo = os.environ.get("GITHUB_REPOSITORY", "")
    token = os.environ.get("RUNNER_STATUS_TOKEN", "")
    if not repo or not token:
        annotate("notice", "No RUNNER_STATUS_TOKEN; keeping all matrix entries")
        json.dump(entries, sys.stdout)
        return 0

    groups = online_groups(repo, token)
    if groups is None:  # fail-open
        json.dump(entries, sys.stdout)
        return 0

    kept, dropped = [], []
    for entry in entries:
        arch = entry.get("arch", "")
        # Keep the entry if its device group currently has an online runner.
        if arch in groups:
            kept.append(entry)
        else:
            dropped.append(entry)

    for entry in dropped:
        label = f"{entry.get('playbook')} ({entry.get('platform')}/{entry.get('arch')})"
        annotate("warning", f"Skipping {label}: no online runner for group '{entry.get('arch')}'")

    if dropped:
        annotate("notice", f"Dropped {len(dropped)} entr(y/ies) with no online runner; kept {len(kept)}")

    json.dump(kept, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
