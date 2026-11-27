#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
Regression tests for orchestrai_trigger.py --checks-*: one GitHub check run per OrchestrAI
batch, created by Detect & Trigger, moved along by Wait for OrchestrAI,
finished by the batch's Test job and cancelled by the cancel paths.

Usage:
    python3 .github/tests/test_orchestrai_checks.py
"""

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
GITHUB_DIR = os.path.dirname(HERE)
SCRIPTS_DIR = os.path.join(GITHUB_DIR, "scripts")
sys.path.insert(0, SCRIPTS_DIR)

import orchestrai_trigger as trigger  # noqa: E402

checks = trigger

ENV = {"GITHUB_TOKEN": "t", "GITHUB_REPOSITORY": "amd/playbooks",
       "GITHUB_SERVER_URL": "https://github.com", "GITHUB_RUN_ID": "9"}
BATCH = {"batch_id": "linux/halo", "label": "Strix Halo · Linux", "platform": "linux",
         "arch": "halo", "playbooks": ["a", "b"], "required": ["a"], "count": 2}


def row(playbook, outcome, required=False):
    return {"playbook": playbook, "outcome": outcome, "required": required,
            "rp_url": "", "reason": "", "attempt": 1}


class Base(unittest.TestCase):
    def setUp(self):
        for p in (mock.patch.dict(os.environ, ENV, clear=True),
                  contextlib.redirect_stderr(io.StringIO())):
            p.__enter__()
            self.addCleanup(p.__exit__, None, None, None)


class Describe(unittest.TestCase):
    def test_each_stage_of_a_run(self):
        self.assertEqual(checks.check_state({"status": "queued"}), ("queued", "Waiting for machines"))
        self.assertEqual(checks.check_state({"status": "queued", "message": "2 of 3 machines ready"}),
                         ("queued", "Waiting for machines: 2 of 3 machines ready"))
        self.assertEqual(checks.check_state({"status": "running", "pipeline_url": "https://j/queue/item/4/"}),
                         ("in_progress", "Preparing machines (running)"))
        self.assertEqual(checks.check_state({"status": "running", "pipeline_url": "https://j/job/p/7/"}),
                         ("in_progress", "Tests running"))

    def test_an_ended_run_is_not_yet_the_batch_verdict(self):
        """The Test job reads each playbook and may retry: only it completes the check."""
        for status in checks.TERMINAL:
            state, title = checks.check_state({"status": status})
            self.assertEqual(state, "in_progress")
            self.assertIn(status, title)


class Create(Base):
    def test_one_queued_check_per_batch_linked_to_its_run(self):
        other = {**BATCH, "batch_id": "windows/halo", "label": "Strix Halo · Windows"}
        posted = []
        gh = mock.Mock(side_effect=lambda m, p, b=None: posted.append(b) or {"id": 100 + len(posted)})
        with tempfile.NamedTemporaryFile("r", delete=False) as out, \
                mock.patch.object(checks, "github_api", gh), \
                mock.patch.dict(os.environ, {"HEAD_SHA": "f" * 40, "GITHUB_OUTPUT": out.name,
                                             "BATCH_MATRIX": json.dumps([BATCH, other]),
                                             "RUN_URLS": json.dumps({"linux/halo": "https://cp/#/runs/r1"})}):
            checks.checks_create_main()
            lines = open(out.name).read().splitlines()
        os.unlink(out.name)
        self.assertEqual([b["name"] for b in posted],
                         ["OrchestrAI · Strix Halo · Linux", "OrchestrAI · Strix Halo · Windows"])
        self.assertEqual({b["status"] for b in posted}, {"queued"})
        self.assertEqual({b["head_sha"] for b in posted}, {"f" * 40})
        self.assertEqual(posted[0]["details_url"], "https://cp/#/runs/r1")
        self.assertNotIn("details_url", posted[1])  # this batch has no run
        self.assertEqual(posted[1]["output"]["title"], "No OrchestrAI run was started")
        # Rewritten after each, the last line holding every id.
        self.assertEqual(json.loads(lines[-1].split("=", 1)[1]), {"linux/halo": 101, "windows/halo": 102})

    def test_a_prefix_tells_the_pr_command_apart(self):
        gh = mock.Mock(return_value={"id": 1})
        with mock.patch.object(checks, "github_api", gh), \
                mock.patch.dict(os.environ, {"HEAD_SHA": "f" * 40, "CHECK_PREFIX": "OrchestrAI !orc",
                                             "BATCH_MATRIX": json.dumps([BATCH])}):
            checks.checks_create_main()
        self.assertEqual(gh.call_args.args[2]["name"], "OrchestrAI !orc · Strix Halo · Linux")

    def test_without_a_commit_nothing_is_created(self):
        gh = mock.Mock()
        with mock.patch.object(checks, "github_api", gh), \
                mock.patch.dict(os.environ, {"BATCH_MATRIX": json.dumps([BATCH])}):
            checks.checks_create_main()
        gh.assert_not_called()


class Update(Base):
    def test_github_is_called_only_when_the_state_changes(self):
        gh = mock.Mock(return_value={})
        up = checks.CheckUpdater({"linux/halo": 7}, {"linux/halo": "https://cp/#/runs/r1"})
        with mock.patch.object(checks, "github_api", gh):
            for run in ({"status": "queued"}, {"status": "queued"},
                        {"status": "running", "pipeline_url": "https://j/job/p/7/"},
                        {"status": "running", "pipeline_url": "https://j/job/p/7/"},
                        {"status": "passed", "pipeline_url": "https://j/job/p/7/"}):
                up.update("linux/halo", run)
        bodies = [c.args[2] for c in gh.call_args_list]
        self.assertEqual([b["status"] for b in bodies], ["queued", "in_progress", "in_progress"])
        self.assertEqual(["started_at" in b for b in bodies], [False, True, False])
        self.assertTrue(all(c.args[1] == "/check-runs/7" for c in gh.call_args_list))
        self.assertIn("https://cp/#/runs/r1", bodies[0]["output"]["summary"])

    def test_a_failed_update_is_tried_again_and_never_raises(self):
        up = checks.CheckUpdater({"linux/halo": 7})
        with mock.patch.object(checks, "github_api", return_value=None) as gh:
            up.update("linux/halo", {"status": "queued"})
            up.update("linux/halo", {"status": "queued"})
        self.assertEqual(gh.call_count, 2)  # GitHub did not take it: ask again
        with mock.patch.object(checks, "github_api", side_effect=RuntimeError("boom")):
            up.update("linux/halo", {"status": "running"})  # a warning, not an exception

    def test_a_batch_without_a_check_is_left_alone(self):
        with mock.patch.object(checks, "github_api") as gh:
            checks.CheckUpdater({}).update("linux/halo", {"status": "queued"})
        gh.assert_not_called()

    def test_the_wait_reports_every_run_it_reads(self):
        seen = []
        runs = iter([{"status": "queued"}, {"status": "passed"}])
        with mock.patch.object(trigger, "api", side_effect=lambda *a, **k: {"run": next(runs)}), \
                mock.patch.object(trigger.time, "sleep"):
            left = trigger.await_runs({}, {"linux/halo": "r1"}, 3600,
                                      lambda bid, run: seen.append((bid, run["status"])))
        self.assertEqual(left, [])
        self.assertEqual(seen, [("linux/halo", "queued"), ("linux/halo", "passed")])

    def test_the_wait_builds_an_updater_from_the_check_ids(self):
        env = {"RUN_ID_MAP": json.dumps({"linux/halo": "r1"}),
               "CHECK_ID_MAP": json.dumps({"linux/halo": 7}),
               "RUN_URL_MAP": json.dumps({"linux/halo": "https://cp/#/runs/r1"}),
               "ORCHESTRAI_V2_CI_API_URL": "https://cp/api", "ORCHESTRAI_V2_OIDC_AUDIENCE": "https://cp",
               "ORCHESTRAI_V2_PORTAL_URL": "https://cp", "ORCHESTRAI_V2_WORKSPACE": "w"}
        with mock.patch.dict(os.environ, env), \
                mock.patch.object(trigger, "await_runs", return_value=[]) as wait:
            trigger.await_runs_main(os.path.join(GITHUB_DIR, "orchestrai-config.yml"))
        on_status = wait.call_args.args[3]
        self.assertEqual(on_status.__self__.check_ids, {"linux/halo": 7})


class Finish(Base):
    def finish(self, rows, check_id="7"):
        gh = mock.Mock(return_value={})
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "batch.json")
            if rows is not None:
                with open(path, "w") as f:
                    json.dump(rows, f)
            with mock.patch.object(checks, "github_api", gh), \
                    mock.patch.dict(os.environ, {"CHECK_ID": check_id, "BATCH_JSON": json.dumps(BATCH),
                                                 "RUN_URL": "https://cp/#/runs/r1"}):
                checks.checks_finish_main(path)
        return gh

    def test_verdicts(self):
        cases = [
            ([row("a", "PASSED", True), row("b", "PASSED")], "success", "2 of 2 playbook(s) passed"),
            ([row("a", "PASSED", True), row("b", "FAILED")], "failure", "1 of 2 playbook(s) passed"),
            ([row("a", "NOT_RUN", True), row("b", "PASSED")], "failure", "Not run: 1 of 2 playbook(s) passed"),
            ([row("a", "PASSED", True), row("b", "NOT_RUN")], "neutral", "Not run: 1 of 2 playbook(s) passed"),
            (None, "neutral", "No results"),
        ]
        for rows, conclusion, title in cases:
            body = self.finish(rows).call_args.args[2]
            self.assertEqual((body["status"], body["conclusion"], body["output"]["title"]),
                             ("completed", conclusion, title), rows)

    def test_the_summary_lists_every_playbook(self):
        body = self.finish([row("a", "PASSED", True), row("b", "FAILED")]).call_args.args[2]
        self.assertIn("`a`", body["output"]["summary"])
        self.assertIn("`b`", body["output"]["summary"])
        self.assertIn("https://cp/#/runs/r1", body["output"]["summary"])

    def test_a_batch_without_a_check_is_left_alone(self):
        self.finish([row("a", "PASSED", True)], check_id="").assert_not_called()


class Cancel(Base):
    def test_cancels_only_what_has_not_finished(self):
        state = {"1": "completed", "2": "in_progress", "3": "queued"}
        patched = []

        def gh(method, path, body=None):
            cid = path.rsplit("/", 1)[1]
            if method == "GET":
                return {"status": state[cid]}
            patched.append((cid, body["conclusion"]))
            return {}
        for ids in (json.dumps({"x": 1, "y": 2, "z": 3}), "1 2 3"):
            patched.clear()
            with mock.patch.object(checks, "github_api", side_effect=gh), \
                    mock.patch.dict(os.environ, {"CHECK_IDS": ids}):
                checks.checks_cancel_main()
            self.assertEqual(patched, [("2", "cancelled"), ("3", "cancelled")], ids)

    def test_errors_never_fail_the_step(self):
        with mock.patch.object(checks, "checks_create_main", side_effect=KeyError("batch_id")), \
                mock.patch.object(sys, "argv", ["orchestrai_trigger.py", "--checks-create"]):
            checks.main()


class Workflows(unittest.TestCase):
    @staticmethod
    def load(name):
        with open(os.path.join(GITHUB_DIR, "workflows", name), encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_every_job_that_touches_check_runs_may_write_them_and_never_fails_on_them(self):
        for name in ("test-playbooks-orchestrai.yml", "orchestrai-pr-command.yml"):
            for job_id, job in self.load(name)["jobs"].items():
                for step in job.get("steps") or []:
                    run = step.get("run") or ""
                    uses_checks = "--checks-" in run or "CHECK_ID_MAP" in (step.get("env") or {})
                    if not uses_checks:
                        continue
                    where = f"{name}:{job_id}: {step.get('name')}"
                    self.assertEqual(job["permissions"].get("checks"), "write", where)
                    self.assertTrue(step.get("continue-on-error"), where)
                    self.assertIn("github.token", step["env"]["GITHUB_TOKEN"], where)

    def test_no_new_script_makes_a_pr_test_every_playbook(self):
        """A new file under .github/scripts/ is a test-harness change for the
        playbook selection (build_test_matrix.py): it sends every playbook to
        hardware. The check runs live in orchestrai_trigger.py for that reason."""
        sys.path.insert(0, SCRIPTS_DIR)
        import build_test_matrix
        self.assertIn(".github/scripts/orchestrai_trigger.py", build_test_matrix.HARNESS_EXCLUDED)
        self.assertFalse(os.path.exists(os.path.join(SCRIPTS_DIR, "orchestrai_checks.py")))

    def test_checks_are_created_finished_and_cancelled(self):
        for name, first in (("test-playbooks-orchestrai.yml", "detect-and-trigger"),
                            ("orchestrai-pr-command.yml", "command")):
            jobs = self.load(name)["jobs"]
            self.assertEqual(jobs[first]["outputs"]["check_ids"], "${{ steps.checks.outputs.check_ids }}")
            steps = jobs[first]["steps"]
            ids = [s.get("id") for s in steps]
            self.assertLess(ids.index("trigger"), ids.index("checks"), name)
            wait_env = jobs["await-runs"]["steps"][-1]["env"]
            self.assertIn("check_ids", wait_env["CHECK_ID_MAP"], name)
            batch = [s.get("name") for s in jobs["test-batches"]["steps"]]
            self.assertLess(batch.index("Finish the batch's check run"), batch.index("Batch result"), name)
            self.assertIn("Cancel the batch's check run", batch, name)
            self.assertIn("Cancel the check runs", [s.get("name") for s in jobs["cancel-runs"]["steps"]], name)


if __name__ == "__main__":
    unittest.main()
