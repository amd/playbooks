#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
OrchestrAI PR-comment report
============================

Aggregates the batch results of an !orc run into a single Markdown body for the
sticky PR comment: one row per playbook, language, device and OS, with links to
its OrchestrAI run and ReportPortal launch.

Each batch job uploads a `batch-results-*` artifact holding batch.json, the rows
orchestrai_batch_verdict.py writes: {playbook (its key), playbook_id, locale,
platform, arch, outcome, reason, run_url, rp_url, job_url, attempt,
first_outcome, covered_by}. This walks the download dir, reads every batch.json
and prints the comment body (prefixed with a stable marker so the workflow can
upsert one sticky comment).

Playbooks that never ran (outcome NOT_RUN/INTERRUPTED) are reported as
infrastructure, in their own category — not as test failures — and the shared
reason is stated once rather than once per playbook. A batch in EXPECTED_BATCHES
(the batch matrix) whose job uploaded nothing is reported the same way, so a
playbook is never silently missing from the comment.

Usage:
    orchestrai_report.py --artifacts <dir> [--run-url URL] [--sha SHA]
        [--ref REF] [--filters TEXT] [--config orchestrai-config.yml]

Exit code is always 0 — it only renders; the gate job decides pass/fail.
"""

import argparse
import glob
import json
import os
from typing import NamedTuple

MARKER = "<!-- orchestrai-orc-report -->"

PASS, FAIL, INFRA = "pass", "fail", "infra"

INFRA_OUTCOMES = ("NOT_RUN", "INTERRUPTED")

NO_RESULTS_REASON = "the batch job uploaded no results"

_CELL = {
    PASS: "✅ pass",
    FAIL: "❌ fail",
    INFRA: "⚠️ not run",
}


class Row(NamedTuple):
    playbook: str
    locale: str  # "" = English
    platform: str
    device: str
    category: str
    reason: str | None  # infrastructure reason, for INFRA rows
    run_url: str = ""
    rp_url: str = ""
    note: str = ""


def classify(d):
    """(category, outcome_label) for one result row."""
    outcome = (d.get("outcome") or "").strip().upper()
    if outcome in INFRA_OUTCOMES:
        return INFRA, outcome
    if outcome == "PASSED":
        return PASS, outcome
    return FAIL, outcome


def device_names(config):
    if not config:
        return {}
    try:
        import yaml
        with open(config, encoding="utf-8") as f:
            return (yaml.safe_load(f) or {}).get("device_names") or {}
    except Exception:  # noqa: BLE001 - names are cosmetic: fall back to device ids
        return {}


def _note(r):
    if r.get("covered_by"):
        return "same tests as en, not run again"
    if int(r.get("attempt") or 1) > 1:
        return f"retried; first: {r.get('first_outcome') or '?'}"
    return ""


def collect(artifacts_dir, expected=None, names=None):
    """Rows for every batch.json under artifacts_dir, plus NO RESULTS rows for
    each expected batch that uploaded none."""
    names = names or {}
    rows, reported = [], set()
    for path in glob.glob(os.path.join(artifacts_dir, "**", "batch.json"), recursive=True):
        try:
            with open(path, encoding="utf-8") as f:
                doc = json.load(f)
        except Exception:  # noqa: BLE001 - one unreadable artifact must not hide the rest
            continue
        if not isinstance(doc, list):
            continue
        for r in doc:
            if not isinstance(r, dict):
                continue
            reported.add(r.get("batch_id"))
            category, _ = classify(r)
            reason = r.get("reason") if category == INFRA else None
            if not isinstance(reason, str) or not reason.strip():
                reason = None
            arch = r.get("arch") or "?"
            rows.append(Row(
                playbook=r.get("playbook_id") or r.get("playbook") or "?",
                locale=r.get("locale") or "",
                platform=r.get("platform") or "?",
                device=names.get(arch, arch),
                category=category, reason=reason,
                run_url=r.get("run_url") or "", rp_url=r.get("rp_url") or "",
                note=_note(r)))
    for batch in expected or []:
        if batch.get("batch_id") in reported:
            continue
        arch = batch.get("arch") or "?"
        for key in list(batch.get("playbooks") or []) + list(batch.get("covered") or {}):
            locale, _, playbook = key.rpartition("/")
            rows.append(Row(playbook=playbook, locale=locale, platform=batch.get("platform") or "?",
                            device=names.get(arch, arch), category=INFRA,
                            reason=NO_RESULTS_REASON))
    rows.sort(key=lambda r: (r.playbook, r.locale, r.device, r.platform))
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
    for row in rows:
        if row.category != INFRA:
            continue
        key = row.reason or "reason not reported by the pipeline"
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


def _links(row):
    links = []
    if row.run_url:
        links.append(f"[OrchestrAI]({row.run_url})")
    if row.rp_url:
        links.append(f"[ReportPortal]({row.rp_url})")
    return " · ".join(links) or "—"


def render(rows, run_url="", sha="", ref="", filters=""):
    n_pass = sum(1 for r in rows if r.category == PASS)
    n_fail = sum(1 for r in rows if r.category == FAIL)
    n_infra = sum(1 for r in rows if r.category == INFRA)

    lines = [MARKER, f"### OrchestrAI results — {_headline(n_pass, n_fail, n_infra)}", ""]
    if rows:
        # The language column only when the run tested more than English.
        localized = any(r.locale for r in rows)
        head = ["Playbook"] + (["Locale"] if localized else []) + ["Device", "OS", "Result", "Results"]
        lines += ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
        for r in rows:
            result = _CELL[r.category] + (f" ({r.note})" if r.note else "")
            cells = ([f"`{r.playbook}`"] + ([r.locale or "en"] if localized else [])
                     + [r.device, r.platform, result, _links(r)])
            lines.append("| " + " | ".join(cells) + " |")
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
    if filters:
        foot.append(filters)
    if run_url:
        foot.append(f"[workflow run]({run_url})")
    if foot:
        lines.append(" · ".join(foot))
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifacts", required=True)
    ap.add_argument("--run-url", default="")
    ap.add_argument("--sha", default="")
    ap.add_argument("--ref", default="")
    ap.add_argument("--filters", default="", help="the command's filters, shown in the footer")
    ap.add_argument("--config", default="", help="orchestrai-config.yml, for device names")
    args = ap.parse_args()

    try:
        expected = json.loads(os.environ.get("EXPECTED_BATCHES") or "[]")
    except json.JSONDecodeError:
        expected = []
    rows = collect(args.artifacts, expected if isinstance(expected, list) else [],
                   device_names(args.config))
    print(render(rows, run_url=args.run_url, sha=args.sha, ref=args.ref, filters=args.filters))


if __name__ == "__main__":
    main()
