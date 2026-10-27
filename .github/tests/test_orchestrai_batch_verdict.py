#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT
"""
Tests for one job per batch: the batch matrix and orchestrai_batch_verdict.py.

The per-playbook verdict is replaced by a stub that passes, fails or reports
NOT_RUN by playbook name, so these tests need no pipeline.

Usage:
    python3 .github/tests/test_orchestrai_batch_verdict.py
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import orchestrai_batch_verdict as bv  # noqa: E402
from orchestrai_prepare_matrices import batch_matrix  # noqa: E402

STUB = '''import json, os, sys
pb = os.environ["PLAYBOOK_ID"]
rc = {"good": 0, "bad": 1, "norun": 2}[pb.split("-")[0]]
os.makedirs("test-results", exist_ok=True)
json.dump({"outcome": ["PASSED", "FAILED", "NOT_RUN"][rc],
           "infrastructure_reason": "machine never came back" if rc == 2 else ""},
          open("test-results/summary.json", "w"))
open(os.environ["GITHUB_OUTPUT"], "a").write(f"rp_url=https://rp/{pb}\\n")
sys.exit(rc)
'''


class BatchMatrix(unittest.TestCase):
    def test_one_entry_per_batch_with_its_playbooks_and_required_ones(self):
        matrix = [
            {"playbook": "a", "platform": "linux", "arch": "halo", "batch_id": "linux/halo", "required": True},
            {"playbook": "b", "platform": "linux", "arch": "halo", "batch_id": "linux/halo", "required": False},
            {"playbook": "a", "platform": "linux", "arch": "grgh", "batch_id": "linux/grgh", "required": False},
        ]
        self.assertEqual(batch_matrix(matrix), [
            {"batch_id": "linux/halo", "platform": "linux", "arch": "halo",
             "playbooks": ["a", "b"], "required": ["a"], "count": 2},
            {"batch_id": "linux/grgh", "platform": "linux", "arch": "grgh",
             "playbooks": ["a"], "required": [], "count": 1},
        ])


class BatchVerdict(unittest.TestCase):
    def run_batch(self, playbooks, required):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        stub = Path(tmp.name, "verdict.py")
        stub.write_text(STUB)
        summary = Path(tmp.name, "summary.md")
        batch = {"batch_id": "linux/halo", "platform": "linux", "arch": "halo",
                 "playbooks": playbooks, "required": required}
        cwd = os.getcwd()
        os.chdir(tmp.name)
        try:
            with mock.patch.object(bv, "VERDICT", stub), \
                    mock.patch.dict(os.environ, {"BATCH_JSON": json.dumps(batch),
                                                 "GITHUB_STEP_SUMMARY": str(summary)}), \
                    mock.patch("sys.stdout"):
                rc = bv.main()
            rows = json.loads(Path("test-results/batch.json").read_text())
            kept = sorted(p.name for p in Path("test-results").iterdir() if p.is_dir())
        finally:
            os.chdir(cwd)
        return rc, rows, kept, summary.read_text()

    def test_every_playbook_is_resolved_and_kept_apart(self):
        rc, rows, kept, summary = self.run_batch(["good-a", "bad-b", "norun-c"], ["good-a"])
        self.assertEqual([(r["playbook"], r["outcome"]) for r in rows],
                         [("good-a", "PASSED"), ("bad-b", "FAILED"), ("norun-c", "NOT_RUN")])
        self.assertEqual(kept, ["bad-b", "good-a", "norun-c"])
        self.assertEqual(rows[0]["rp_url"], "https://rp/good-a")
        self.assertIn("machine never came back", summary)
        self.assertIn("### linux/halo (3 playbooks)", summary)

    def test_only_a_required_failure_fails_the_batch(self):
        self.assertEqual(self.run_batch(["good-a", "bad-b"], ["good-a"])[0], 0)
        self.assertEqual(self.run_batch(["good-a", "bad-b"], ["bad-b"])[0], 1)
        self.assertEqual(self.run_batch(["norun-c"], ["norun-c"])[0], 1)

    def test_a_batch_with_nothing_required_still_shows_its_failures(self):
        # continue-on-error in the workflow keeps it from failing the run.
        self.assertEqual(self.run_batch(["good-a", "bad-b"], [])[0], 1)
        self.assertEqual(self.run_batch(["good-a"], [])[0], 0)

    def test_merge_writes_one_table_for_every_batch(self):
        with tempfile.TemporaryDirectory() as d:
            for i, (bid, pb, outcome) in enumerate((("linux/halo", "a", "PASSED"), ("windows/stx", "a", "FAILED"))):
                Path(d, f"batch-results-{i}").mkdir()
                Path(d, f"batch-results-{i}", "batch.json").write_text(json.dumps([
                    {"playbook": pb, "batch_id": bid, "required": True, "outcome": outcome,
                     "rp_url": "", "reason": ""}]))
            out = subprocess.run([sys.executable, str(HERE.parent / "scripts/orchestrai_batch_verdict.py"),
                                  "--merge", d], capture_output=True, text=True, env={**os.environ, "GITHUB_STEP_SUMMARY": ""})
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("| `a` | linux/halo | ✦ | ✅ PASSED |", out.stdout)
        self.assertIn("| `a` | windows/stx | ✦ | ❌ FAILED |", out.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
