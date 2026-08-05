#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
OrchestrAI PR-comment report
============================

Aggregates the per-playbook test-results artifacts produced by the matrix job
into a single Markdown body for the !orc sticky PR comment.

Each artifact is a directory named `test-results-<playbook>-<platform>-<arch>`
containing summary.json ({playbook_id, platform, passed, failed, ...}). This
walks the download dir, reads each summary, and prints the comment body
(prefixed with a stable marker so the workflow can upsert one sticky comment).

Usage:
    orchestrai_report.py --artifacts <dir> [--run-url URL] [--sha SHA] [--ref REF]

Exit code is always 0 — it only renders; the gate job decides pass/fail.
"""

import argparse
import glob
import json
import os

MARKER = "<!-- orchestrai-orc-report -->"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifacts", required=True)
    ap.add_argument("--run-url", default="")
    ap.add_argument("--sha", default="")
    ap.add_argument("--ref", default="")
    args = ap.parse_args()

    rows = []
    for path in glob.glob(os.path.join(args.artifacts, "**", "summary.json"), recursive=True):
        try:
            d = json.load(open(path))
        except Exception:
            continue
        pb = d.get("playbook_id", "?")
        platform = d.get("platform", "?")
        # arch isn't in summary.json; recover it from the artifact dir name
        # (test-results-<pb>-<platform>-<arch>).
        arch = "?"
        dirname = os.path.basename(os.path.dirname(path))
        if dirname.startswith("test-results-"):
            parts = dirname[len("test-results-"):].rsplit("-", 2)
            if len(parts) == 3:
                arch = parts[2]
        passed = int(d.get("passed", 0) or 0)
        failed = int(d.get("failed", 0) or 0)
        ok = failed == 0 and passed > 0
        rows.append((pb, platform, arch, ok))

    rows.sort(key=lambda r: (r[0], r[1], r[2]))
    n_pass = sum(1 for r in rows if r[3])
    n_fail = len(rows) - n_pass
    overall = "✅ all passed" if rows and n_fail == 0 else (
        "❌ failures" if rows else "⚠️ no results")

    lines = [MARKER, f"### OrchestrAI results — {overall} ({n_pass} passed, {n_fail} failed)", ""]
    if rows:
        lines += ["| Playbook | Platform | Device | Result |", "|---|---|---|---|"]
        for pb, platform, arch, ok in rows:
            lines.append(f"| `{pb}` | {platform} | {arch} | {'✅ pass' if ok else '❌ fail'} |")
    else:
        lines.append("_No playbooks were scheduled (nothing matched, or all devices were skipped)._")
    lines.append("")
    foot = []
    if args.sha:
        foot.append(f"tested `{args.sha[:8]}`" + (f" ({args.ref})" if args.ref else ""))
    if args.run_url:
        foot.append(f"[workflow run]({args.run_url}) — per-playbook ReportPortal links are in each job summary")
    if foot:
        lines.append(" · ".join(foot))

    print("\n".join(lines))


if __name__ == "__main__":
    main()
