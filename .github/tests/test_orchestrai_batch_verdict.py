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
            {"playbook": "a", "platform": "windows", "arch": "grgh", "batch_id": "windows/grgh", "required": False},
        ]
        self.assertEqual(batch_matrix(matrix, {"halo": "Halo", "grgh": "Gorgon Halo"}), [
            {"batch_id": "linux/halo", "platform": "linux", "arch": "halo", "locale": "",
             "label": "Halo · Linux", "playbooks": ["a", "b"], "required": ["a"], "count": 2},
            {"batch_id": "windows/grgh", "platform": "windows", "arch": "grgh", "locale": "",
             "label": "Gorgon Halo · Windows", "playbooks": ["a"], "required": [], "count": 1},
        ])

    def test_localized_batches_are_batches_too(self):
        matrix = [{"playbook": "a", "platform": "linux", "arch": "halo", "required": False,
                   "batch_id": "localized/zh-CN/linux/halo", "locale": "zh-CN"}]
        self.assertEqual([(b["label"], b["locale"]) for b in batch_matrix(matrix, {"halo": "Halo"})],
                         [("Halo · Linux [zh-CN]", "zh-CN")])

    def test_two_batches_of_one_device_and_os_are_told_apart(self):
        matrix = [{"playbook": "a", "platform": "linux", "arch": "halo", "batch_id": "linux/halo"},
                  {"playbook": "b", "platform": "linux", "arch": "halo", "batch_id": "linux/halo+ram_128gb"}]
        self.assertEqual([b["label"] for b in batch_matrix(matrix, {"halo": "Halo"})],
                         ["Halo · Linux", "Halo · Linux (ram_128gb)"])

    def test_the_config_names_every_device_it_tags(self):
        import yaml
        cfg = yaml.safe_load((HERE.parent / "orchestrai-config.yml").read_text())
        self.assertLessEqual(set(cfg["device_to_gfx"]) - {"grgh_box", "mdsh", "grgp", "mdsp"},
                             set(cfg["device_names"]))


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

    def test_only_playbooks_that_did_not_run_are_retried(self):
        rows = [{"playbook": p, "outcome": o} for p, o in
                (("good-a", "PASSED"), ("bad-b", "FAILED"), ("norun-c", "NOT_RUN"), ("cut-d", "INTERRUPTED"))]
        with tempfile.TemporaryDirectory() as d:
            Path(d, "batch.json").write_text(json.dumps(rows))
            out = subprocess.run([sys.executable, str(HERE.parent / "scripts/orchestrai_batch_verdict.py"),
                                  "--retryable", str(Path(d, "batch.json"))], capture_output=True, text=True)
        self.assertEqual(out.stdout.split(), ["norun-c", "cut-d"])  # never a FAILED test

    def test_a_retry_replaces_the_first_attempt_and_the_job_judges_both(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        stub = Path(tmp.name, "verdict.py")
        stub.write_text(STUB)
        batch = {"batch_id": "linux/halo", "label": "Halo · Linux", "platform": "linux", "arch": "halo",
                 "playbooks": ["good-a", "norun-c"], "required": ["good-a", "norun-c"]}
        cwd = os.getcwd()
        os.chdir(tmp.name)
        try:
            with mock.patch.object(bv, "VERDICT", stub), mock.patch("sys.stdout"), \
                    mock.patch.dict(os.environ, {"BATCH_JSON": json.dumps(batch), "DEFER_EXIT": "1",
                                                 "GITHUB_STEP_SUMMARY": ""}):
                self.assertEqual(bv.main(), 0)  # deferred, though norun-c did not run
            Path("first.json").write_text(Path("test-results/batch.json").read_text())
            # The retry: norun-c now passes (the stub decides by name, so rename it).
            retry = dict(batch, playbooks=["norun-c"])
            stub.write_text(STUB.replace('pb.split("-")[0]', '"good" if pb == "norun-c" else pb.split("-")[0]'))
            with mock.patch.object(bv, "VERDICT", stub), mock.patch("sys.stdout"), \
                    mock.patch.dict(os.environ, {"BATCH_JSON": json.dumps(retry), "RETRY_OF": "first.json",
                                                 "DEFER_EXIT": "1", "GITHUB_STEP_SUMMARY": ""}):
                bv.main()
            rows = {r["playbook"]: r for r in json.loads(Path("test-results/batch.json").read_text())}
            kept = sorted(p.name for p in Path("test-results").iterdir() if p.is_dir())
            with mock.patch.dict(os.environ, {"BATCH_JSON": json.dumps(batch)}), \
                    mock.patch.object(sys, "argv", ["v", "--exit-code", "test-results/batch.json"]), \
                    mock.patch("sys.stdout"):
                final = bv.main()
        finally:
            os.chdir(cwd)
        self.assertEqual((rows["norun-c"]["outcome"], rows["norun-c"]["attempt"], rows["norun-c"]["first_outcome"]),
                         ("PASSED", 2, "NOT_RUN"))
        self.assertEqual((rows["good-a"]["outcome"], rows["good-a"]["attempt"]), ("PASSED", 1))
        self.assertEqual(kept, ["good-a", "norun-c", "norun-c-attempt1"])
        self.assertEqual(final, 0)  # passed on retry
        self.assertIn("(retry 1; first: NOT_RUN)", bv.by_configuration(list(rows.values())))

    def test_the_job_still_fails_when_the_retry_does_not_run_either(self):
        rows = [{"playbook": "norun-c", "required": True, "outcome": "NOT_RUN"}]
        self.assertEqual(bv.batch_failed(rows, {"required": ["norun-c"]}), ["norun-c"])

    def test_merge_reports_each_system_then_every_playbook(self):
        batches = {"Halo · Linux": ("linux", [("a", "PASSED"), ("b", "FAILED")]),
                   "Halo · Windows": ("windows", [("a", "PASSED"), ("b", "PASSED")]),
                   "Strix · Linux": ("linux", [("a", "NOT_RUN")])}
        with tempfile.TemporaryDirectory() as d:
            for i, (label, (platform, rows)) in enumerate(batches.items()):
                Path(d, f"batch-results-{i}").mkdir()
                Path(d, f"batch-results-{i}", "batch.json").write_text(json.dumps([
                    {"playbook": pb, "batch_id": f"{platform}/x", "label": label, "platform": platform,
                     "required": True, "outcome": outcome, "rp_url": "", "reason": ""} for pb, outcome in rows]))
            out = subprocess.run([sys.executable, str(HERE.parent / "scripts/orchestrai_batch_verdict.py"),
                                  "--merge", d], capture_output=True, text=True,
                                 env={**os.environ, "GITHUB_STEP_SUMMARY": ""})
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("| Halo | ❌ FAIL (1/2) | ✅ PASS (2/2) |", out.stdout)
        self.assertIn("| Strix | ⚠️ NOT RUN (0/1) | — |", out.stdout)
        self.assertIn("::error title=Halo · Linux::FAIL", out.stdout)
        self.assertIn("::notice title=Halo · Windows::PASS", out.stdout)
        # The configuration table: playbooks x configurations, — where a playbook did not run.
        self.assertIn("## OrchestrAI playbooks by configuration", out.stdout)
        self.assertIn("| Playbook | Halo · Linux | Halo · Windows | Strix · Linux |", out.stdout)
        self.assertIn("| `b` | ❌ FAILED ✦ | ✅ PASSED ✦ | — |", out.stdout)

    def test_configuration_cells_link_the_job_reportportal_and_live_run(self):
        row = {"playbook": "a", "batch_id": "linux/halo", "label": "Halo · Linux", "platform": "linux",
               "required": False, "outcome": "PASSED", "rp_url": "https://rp/1", "reason": "",
               "job_url": "https://gh/job/9", "run_url": "https://oai/run/7"}
        table = bv.by_configuration([row])
        self.assertIn("| Playbook | Halo · Linux<br>[live results](https://oai/run/7) |", table)
        self.assertIn("| `a` | ✅ [PASSED](https://gh/job/9) · [ReportPortal](https://rp/1) |", table)

    def test_a_retried_row_keeps_the_batch_run_in_the_header(self):
        first = {"playbook": "a", "batch_id": "linux/halo", "label": "Halo · Linux", "platform": "linux",
                 "required": False, "outcome": "PASSED", "rp_url": "", "reason": "", "job_url": "",
                 "attempt": 2, "first_outcome": "NOT_RUN", "run_url": "https://oai/run/retry",
                 "batch_run_url": "https://oai/run/batch"}
        second = dict(first, playbook="b", attempt=1, run_url="https://oai/run/batch")
        table = bv.by_configuration([first, second])
        self.assertIn("Halo · Linux<br>[live results](https://oai/run/batch)", table)
        self.assertIn("[retry run](https://oai/run/retry)", table)


class FetchCache(unittest.TestCase):
    def test_a_batch_downloads_each_url_once_and_never_caches_a_failure(self):
        import orchestrai_verdict as v
        calls = []

        class Response:
            def __init__(self, body):
                self.body = body
            def __enter__(self):
                return self
            def __exit__(self, *exc):
                return False
            def read(self):
                return self.body

        def urlopen(req, timeout):
            calls.append(req.full_url)
            if req.full_url.endswith("down"):
                raise OSError("unreachable")
            return Response(b"{}")

        with tempfile.TemporaryDirectory() as cache, \
                mock.patch.dict(os.environ, {"ORCHESTRAI_FETCH_CACHE": cache}), \
                mock.patch.object(v.urllib.request, "urlopen", urlopen):
            self.assertEqual([v.fetch("https://b/summary", "u", "t") for _ in range(3)], ["{}"] * 3)
            self.assertEqual([v.fetch("https://b/down", "u", "t") for _ in range(2)], [None, None])
        self.assertEqual(calls, ["https://b/summary", "https://b/down", "https://b/down"])


class Workflows(unittest.TestCase):
    """The workflow contracts the batch job and !orc rely on."""

    @staticmethod
    def load(name):
        import yaml
        return yaml.safe_load((HERE.parent / "workflows" / name).read_text())

    def test_no_wait_fails_the_batch_job_and_no_retry_runs_once_cancelled(self):
        job = self.load("test-playbooks-orchestrai.yml")["jobs"]["test-batches"]
        steps = {s.get("id"): s for s in job["steps"] if s.get("id")}
        for sid in ("build", "wait", "retry_trigger", "retry_build", "retry_wait"):
            self.assertIs(steps[sid].get("continue-on-error"), True, sid)
        retry = [s for s in job["steps"] if "pick" in str(s.get("if", "")) or "retry" in str(s.get("if", ""))
                 or s.get("id") == "pick"]
        self.assertGreaterEqual(len(retry), 7)
        for s in retry:
            self.assertTrue(s["if"].startswith("!cancelled()"), s.get("name") or s.get("uses"))
        self.assertLessEqual(job["timeout-minutes"], 1440)  # the GITHUB_TOKEN's lifetime

    def test_orc_runs_the_controller_from_its_own_revision(self):
        jobs = self.load("orchestrai-pr-command.yml")["jobs"]
        command = jobs["command"]["steps"]
        self.assertIn({"path": ".orc", "persist-credentials": False},
                      [s.get("with") for s in command if "checkout" in s.get("uses", "")])
        for s in command:
            if ".github/scripts/" in s.get("run", ""):
                self.assertIn(".orc/.github/scripts/", s["run"], s.get("name"))
        for name in ("test-playbooks", "report"):
            for s in jobs[name]["steps"]:
                if "checkout" in s.get("uses", ""):
                    self.assertNotIn("ref", s.get("with") or {}, name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
