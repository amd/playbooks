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
containing summary.json ({playbook_id, platform, passed, failed, outcome, ...}).
This walks the download dir, reads each summary, and prints the comment body
(prefixed with a stable marker so the workflow can upsert one sticky comment).

Playbooks that never ran (outcome NOT_RUN/INTERRUPTED) are reported as
infrastructure, in their own category — not as test failures — and the shared
`infrastructure_reason` is stated once rather than once per playbook.

Artifacts written by an older verdict script carry no `outcome`; those fall back
to the previous pass/fail derivation.

Usage:
    orchestrai_report.py --artifacts <dir> [--run-url URL] [--sha SHA] [--ref REF]

Exit code is always 0 — it only renders; the gate job decides pass/fail.
"""

import argparse
import glob
import json
import os

MARKER = "<!-- orchestrai-orc-report -->"

PASS, FAIL, INFRA = "pass", "fail", "infra"

INFRA_OUTCOMES = ("NOT_RUN", "INTERRUPTED")

_CELL = {
    PASS: "✅ pass",
    FAIL: "❌ fail",
    INFRA: "⚠️ not run",
}


def classify(d):
    """(category, outcome_label) for one summary.json document."""
    outcome = (d.get("outcome") or "").strip().upper()
    if outcome in INFRA_OUTCOMES:
        return INFRA, outcome
    if outcome == "PASSED":
        return PASS, outcome
    if outcome == "FAILED":
        return FAIL, outcome
    # Legacy artifact with no `outcome`: derive as before.
    passed = int(d.get("passed", 0) or 0)
    failed = int(d.get("failed", 0) or 0)
    return (PASS if (failed == 0 and passed > 0) else FAIL), ""


def collect(artifacts_dir):
    """Rows of (playbook, platform, arch, category, infrastructure_reason)."""
    rows = []
    for path in glob.glob(os.path.join(artifacts_dir, "**", "summary.json"), recursive=True):
        try:
            with open(path) as f:
                d = json.load(f)
        except Exception:
            continue
        if not isinstance(d, dict):
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
        category, _ = classify(d)
        reason = d.get("infrastructure_reason") if category == INFRA else None
        if not isinstance(reason, str) or not reason.strip():
            reason = None
        rows.append((pb, platform, arch, category, reason))
    rows.sort(key=lambda r: (r[0], r[1], r[2]))
    return rows


def _headline(n_pass, n_fail, n_infra):
    parts = []
    if n_fail:
        parts.append(f"❌ {n_fail} failed")
    if n_infra:
        parts.append(f"⚠️ {n_infra} not run (infrastructure)")
    if n_pass:
        parts.append(f"✅ {n_pass} passed")
    if not parts:
        return "⚠️ no results"
    if not n_fail and not n_infra:
        return f"✅ all passed ({n_pass} passed)"
    return ", ".join(parts)


def _infra_notes(rows):
    """One line per distinct infrastructure reason — never one per playbook."""
    order, counts = [], {}
    for _, _, _, category, reason in rows:
        if category != INFRA:
            continue
        key = reason or "reason not reported by the pipeline"
        if key not in counts:
            order.append(key)
            counts[key] = 0
        counts[key] += 1

    lines = []
    for reason in order:
        n = counts[reason]
        noun = "playbook" if n == 1 else "playbooks"
        lines.append(f"> ⚠️ **{n} {noun} did not run** — infrastructure: {reason}")
    if lines:
        lines.append("")
        lines.append("_Not-run playbooks are an infrastructure problem with the batch, "
                     "not test failures._")
    return lines


def render(rows, run_url="", sha="", ref=""):
    n_pass = sum(1 for r in rows if r[3] == PASS)
    n_fail = sum(1 for r in rows if r[3] == FAIL)
    n_infra = sum(1 for r in rows if r[3] == INFRA)

    lines = [MARKER, f"### OrchestrAI results — {_headline(n_pass, n_fail, n_infra)}", ""]
    if rows:
        lines += ["| Playbook | Platform | Device | Result |", "|---|---|---|---|"]
        for pb, platform, arch, category, _ in rows:
            lines.append(f"| `{pb}` | {platform} | {arch} | {_CELL[category]} |")
        notes = _infra_notes(rows)
        if notes:
            lines.append("")
            lines += notes
    else:
        lines.append("_No playbooks were scheduled (nothing matched, or all devices were skipped)._")
    lines.append("")
    foot = []
    if sha:
        foot.append(f"tested `{sha[:8]}`" + (f" ({ref})" if ref else ""))
    if run_url:
        foot.append(f"[workflow run]({run_url}) — per-playbook ReportPortal links are in each job summary")
    if foot:
        lines.append(" · ".join(foot))
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifacts", required=True)
    ap.add_argument("--run-url", default="")
    ap.add_argument("--sha", default="")
    ap.add_argument("--ref", default="")
    args = ap.parse_args()

    print(render(collect(args.artifacts), run_url=args.run_url, sha=args.sha,
                 ref=args.ref))


if __name__ == "__main__":
    main()
