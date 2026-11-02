#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT
"""
Resolve every playbook of one OrchestrAI batch
==============================================
The batch job waits on its build once; this runs orchestrai_verdict.py for each
of its playbooks, keeps each one's test-results/ under test-results/<playbook>/,
writes a per-playbook table to the job summary and test-results/batch.json, and
fails when a REQUIRED playbook did not pass. A batch with no required playbook
(e.g. a device being brought up) fails when any playbook did not pass; the
workflow marks such jobs continue-on-error, so they show red without failing
the run, as the per-playbook jobs did.

Env:
    BATCH_JSON   {"batch_id", "label", "platform", "arch", "locale", "playbooks": [...], "required": [...]}
    BUILD_URL, ORCHESTRAI_PIPELINE_USER, ORCHESTRAI_PIPELINE_TOKEN  (for the verdict)
    RUN_URL      optional OrchestrAI run link, shown when there is no ReportPortal link
    JOB_URL      optional link to this batch's GitHub job (the configuration table links to it)
Exit: 1 when the batch failed as above, else 0.

Retry: with RETRY_OF=<first attempt's batch.json>, BATCH_JSON lists only the
playbooks being retried (those that did NOT_RUN or were INTERRUPTED); their new
results replace the first attempt's in batch.json, marked with the attempt and
the first outcome, and the first attempt's files move to <playbook>-attempt1/.
DEFER_EXIT=1 records results without failing; orchestrai_batch_verdict.py
--exit-code then decides the job from the final batch.json.

orchestrai_batch_verdict.py --merge DIR reads every batch.json under DIR (the
downloaded batch artifacts) and reports each system (device + OS) as PASS, FAIL
or NOT RUN: a device x OS grid and one annotation per system on the run page,
then every playbook's row.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

VERDICT = Path(__file__).with_name("orchestrai_verdict.py")
LABEL = {0: "PASSED", 1: "FAILED", 2: "NOT_RUN"}
ICON = {"PASSED": "✅", "FAILED": "❌", "NOT_RUN": "⚠️", "INTERRUPTED": "⚠️"}
SYSTEM_ICON = {"PASS": "✅", "FAIL": "❌", "NOT RUN": "⚠️"}


def resolve(playbook, batch, out_dir):
    """Run the per-playbook verdict in its own directory; return its row."""
    with tempfile.TemporaryDirectory() as tmp:
        gh_out = Path(tmp, "github_output")
        gh_out.touch()
        env = {**os.environ, "PLAYBOOK_ID": playbook, "PLATFORM": batch["platform"],
               "GITHUB_OUTPUT": str(gh_out)}
        rc = subprocess.run([sys.executable, str(VERDICT)], cwd=tmp, env=env).returncode
        summary = {}
        if Path(tmp, "test-results").is_dir():
            dest = out_dir / playbook
            shutil.rmtree(dest, ignore_errors=True)
            shutil.copytree(Path(tmp, "test-results"), dest)
            try:
                summary = json.loads((dest / "summary.json").read_text())
            except (OSError, ValueError):
                pass
        outputs = dict(line.split("=", 1) for line in gh_out.read_text().splitlines() if "=" in line)
    outcome = (summary.get("outcome") or LABEL.get(rc, "FAILED")).upper()
    return {"playbook": playbook, "platform": batch["platform"], "arch": batch["arch"], "attempt": 1,
            "job_url": os.environ.get("JOB_URL", ""), "run_url": os.environ.get("RUN_URL", ""),
            "batch_id": batch["batch_id"], "label": batch.get("label") or batch["batch_id"],
            "locale": batch.get("locale", ""), "required": playbook in batch["required"],
            "outcome": outcome, "rc": rc, "rp_url": outputs.get("rp_url", ""),
            "reason": summary.get("infrastructure_reason") or ""}


def retry_note(r):
    if r.get("attempt", 1) < 2:
        return ""
    return f" (retry {r['attempt'] - 1}; first: {r.get('first_outcome', '?')})"


RETRYABLE = ("NOT_RUN", "INTERRUPTED")


def batch_failed(rows, batch):
    """Required playbooks that did not pass; with nothing required, any that did not."""
    pool = [r for r in rows if r["required"]] if batch["required"] else rows
    return [r["playbook"] for r in pool if r["outcome"] != "PASSED"]


def table(rows, run_url=""):
    lines = ["| Playbook | Required | Result | Results |", "|---|---|---|---|"]
    for r in rows:
        link = r["rp_url"] or run_url
        note = (f" — {r['reason']}" if r["reason"] else "") + retry_note(r)
        lines.append(f"| `{r['playbook']}` | {'✦' if r['required'] else ''} | "
                     f"{ICON.get(r['outcome'], '❌')} {r['outcome']}{note} | "
                     f"{f'[View]({link})' if link else ''} |")
    return "\n".join(lines)


def system_status(rows):
    """PASS when every playbook passed, FAIL when any failed, else NOT RUN."""
    outcomes = {r["outcome"] for r in rows}
    if outcomes == {"PASSED"}:
        return "PASS"
    return "FAIL" if "FAILED" in outcomes else "NOT RUN"


def by_configuration(rows):
    """Playbooks x configurations: each cell links its result to the batch's job
    and to ReportPortal; each column header links the configuration's live run."""
    configs = {}
    for r in rows:
        configs.setdefault(r.get("label") or r["batch_id"], r.get("run_url", ""))
    labels = sorted(configs)
    cells = {(r["playbook"], r.get("label") or r["batch_id"]): r for r in rows}
    def header(label):
        return f"{label}<br>[live results]({configs[label]})" if configs[label] else label
    def cell(r):
        if not r:
            return "—"
        status = f"[{r['outcome']}]({r['job_url']})" if r.get("job_url") else r["outcome"]
        rp = f" · [ReportPortal]({r['rp_url']})" if r.get("rp_url") else ""
        return f"{ICON.get(r['outcome'], '❌')} {status}{rp}{' ✦' if r.get('required') else ''}{retry_note(r)}"
    out = ["## OrchestrAI playbooks by configuration", "",
           "Result links open the batch's GitHub job; ReportPortal links open the recorded "
           "launch when available. ✦ = required.", "",
           "| Playbook | " + " | ".join(header(l) for l in labels) + " |",
           "|---|" + "---|" * len(labels)]
    for pb in sorted({r["playbook"] for r in rows}):
        out.append(f"| `{pb}` | " + " | ".join(cell(cells.get((pb, l))) for l in labels) + " |")
    return "\n".join(out) + "\n"


def merge(root):
    rows = [r for f in sorted(Path(root).rglob("batch.json")) for r in json.loads(f.read_text())]
    systems = {}
    for r in rows:
        systems.setdefault(r.get("label") or r["batch_id"], []).append(r)
    platforms = sorted({r["platform"] for r in rows})
    grid = {}
    for label, group in systems.items():
        platform = group[0]["platform"]
        device = label.replace(f" · {platform.capitalize()}", "")
        passed = sum(r["outcome"] == "PASSED" for r in group)
        status = system_status(group)
        grid.setdefault(device, {})[platform] = f"{SYSTEM_ICON[status]} {status} ({passed}/{len(group)})"
        level = {"PASS": "notice", "FAIL": "error", "NOT RUN": "warning"}[status]
        print(f"::{level} title={label}::{status} — {passed}/{len(group)} playbooks passed")
    lines = ["## Results by device", "",
             "| Device | " + " | ".join(p.capitalize() for p in platforms) + " |",
             "|---|" + "---|" * len(platforms)]
    for device in sorted(grid):
        lines.append(f"| {device} | " + " | ".join(grid[device].get(p, "—") for p in platforms) + " |")
    text = "\n".join(lines) + "\n\n" + (by_configuration(rows) if rows else "_No batch results._\n")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(text)
    print(text)
    return 0


def main():
    if sys.argv[1:2] == ["--merge"]:
        return merge(sys.argv[2])
    if sys.argv[1:2] == ["--exit-code"]:  # the batch job's result, from the final batch.json
        failed = batch_failed(json.loads(Path(sys.argv[2]).read_text()), json.loads(os.environ["BATCH_JSON"]))
        if failed:
            print(f"::error::did not pass: {', '.join(failed)}")
        return 1 if failed else 0
    if sys.argv[1:2] == ["--retryable"]:  # playbooks to retry, one per line
        rows = json.loads(Path(sys.argv[2]).read_text())
        print("\n".join(r["playbook"] for r in rows if r["outcome"] in RETRYABLE))
        return 0
    batch = json.loads(os.environ["BATCH_JSON"])
    out_dir = Path("test-results")
    out_dir.mkdir(exist_ok=True)
    first = {}
    if os.environ.get("RETRY_OF"):
        first = {r["playbook"]: r for r in json.loads(Path(os.environ["RETRY_OF"]).read_text())}
        for pb in batch["playbooks"]:  # keep the first attempt's files
            if (out_dir / pb).is_dir():
                shutil.rmtree(out_dir / f"{pb}-attempt1", ignore_errors=True)
                (out_dir / pb).rename(out_dir / f"{pb}-attempt1")
    rows = [resolve(pb, batch, out_dir) for pb in batch["playbooks"]]
    for r in rows:
        if r["playbook"] in first:
            prev = first[r["playbook"]]
            r.update(attempt=prev.get("attempt", 1) + 1, first_outcome=prev["outcome"],
                     first_reason=prev.get("reason", ""))
    retried = rows
    if first:
        rows = [next((n for n in retried if n["playbook"] == pb), old) for pb, old in first.items()]
    (out_dir / "batch.json").write_text(json.dumps(rows, indent=2))
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            title = batch.get("label") or batch["batch_id"]
            title += f" — retry of {len(retried)} that did not run" if first else f" ({len(rows)} playbooks)"
            f.write(f"### {title}\n\n{table(retried, os.environ.get('RUN_URL', ''))}\n\n")
    for r in retried:
        if r["rc"] != 0:
            kind = "error" if r["required"] else "warning"
            print(f"::{kind}::{r['playbook']} ({batch['batch_id']}): {r['outcome']}"
                  + (f" — {r['reason']}" if r["reason"] else ""))
    if os.environ.get("DEFER_EXIT"):
        return 0
    return 1 if batch_failed(rows, batch) else 0


if __name__ == "__main__":
    sys.exit(main())
