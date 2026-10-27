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
Exit: 1 when the batch failed as above, else 0.

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
    return {"playbook": playbook, "platform": batch["platform"], "arch": batch["arch"],
            "batch_id": batch["batch_id"], "label": batch.get("label") or batch["batch_id"],
            "locale": batch.get("locale", ""), "required": playbook in batch["required"],
            "outcome": outcome, "rc": rc, "rp_url": outputs.get("rp_url", ""),
            "reason": summary.get("infrastructure_reason") or ""}


def table(rows, run_url="", with_batch=False):
    lines = ["| Playbook |" + (" System |" if with_batch else "") + " Required | Result | Results |",
             "|---|" + ("---|" if with_batch else "") + "---|---|---|"]
    for r in rows:
        link = r["rp_url"] or run_url
        note = f" — {r['reason']}" if r["reason"] else ""
        lines.append(f"| `{r['playbook']}` |" + (f" {r.get('label') or r['batch_id']} |" if with_batch else "")
                     + f" {'✦' if r['required'] else ''} | "
                     f"{ICON.get(r['outcome'], '❌')} {r['outcome']}{note} | "
                     f"{f'[View]({link})' if link else ''} |")
    return "\n".join(lines)


def system_status(rows):
    """PASS when every playbook passed, FAIL when any failed, else NOT RUN."""
    outcomes = {r["outcome"] for r in rows}
    if outcomes == {"PASSED"}:
        return "PASS"
    return "FAIL" if "FAILED" in outcomes else "NOT RUN"


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
    rows.sort(key=lambda r: (r.get("label") or r["batch_id"], r["playbook"]))
    text = ("\n".join(lines) + "\n\n" + ("_No batch results._" if not rows else
            "<details><summary>Every playbook</summary>\n\n" + table(rows, with_batch=True)
            + "\n\n</details>") + "\n")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(text)
    print(text)
    return 0


def main():
    if sys.argv[1:2] == ["--merge"]:
        return merge(sys.argv[2])
    batch = json.loads(os.environ["BATCH_JSON"])
    out_dir = Path("test-results")
    out_dir.mkdir(exist_ok=True)
    rows = [resolve(pb, batch, out_dir) for pb in batch["playbooks"]]
    (out_dir / "batch.json").write_text(json.dumps(rows, indent=2))
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(f"### {batch.get('label') or batch['batch_id']} ({len(rows)} playbooks)\n\n"
                    f"{table(rows, os.environ.get('RUN_URL', ''))}\n\n")
    failed = [r["playbook"] for r in rows if r["required"] and r["rc"] != 0]
    for r in rows:
        if r["rc"] != 0:
            kind = "error" if r["required"] else "warning"
            print(f"::{kind}::{r['playbook']} ({batch['batch_id']}): {r['outcome']}"
                  + (f" — {r['reason']}" if r["reason"] else ""))
    if not batch["required"]:
        failed = [r["playbook"] for r in rows if r["rc"] != 0]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
