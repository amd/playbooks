#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
Regression tests for orchestrai_verdict.py.

Guards three things:

1. The infrastructure-vs-failure distinction: a playbook that never ran (the
   batch died — machine never came back from a reboot, no build was produced,
   the build summary was unreachable) must NOT be reported as a failed playbook.
2. An artifact is written on EVERY exit path. `upload-artifact` runs with
   `if-no-files-found: ignore`, so a crash makes the playbook vanish from the
   aggregated report and the sticky comment undercounts — silently.
3. The `results` rows keep the shape the website dashboard already reads
   (website/src/lib/github-test-results.ts).

Every case drives main() with a fixture summary.json; fetch() is stubbed, so
nothing here touches the network or the OrchestrAI pipeline.

Usage:
    python3 .github/scripts/test_orchestrai_verdict.py
"""

import contextlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "orchestrai_verdict", Path(__file__).with_name("orchestrai_verdict.py")
)
verdict = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(verdict)

BUILD = "https://ci.example.invalid/job/x/1/"

#: Sentinel for "fetch() hit a transport failure" (401, network, aborted build)
#: as opposed to "fetch() returned an empty document".
UNREACHABLE = object()

# A batch where every playbook ran and passed.
OLD_SCHEMA = {
    "build_url": BUILD,
    "rp_launch_url": "https://rp.example.invalid/launch/1",
    "groups": {
        "playbook-alpha": {"passed": 4, "failed": 0, "skipped": 1, "errors": 0,
                           "status": "PASSED"},
        "playbook-beta": {"passed": 2, "failed": 1, "skipped": 0, "errors": 0,
                          "status": "FAILED"},
    },
}

# The real-world failure: a batch of three, none of which ran.
NEW_SCHEMA_NOT_RUN = {
    "status": "INTERRUPTED",
    "infrastructure_reason": "host did not return from reboot",
    "expected_groups": ["playbook-alpha", "playbook-beta", "playbook-gamma"],
    "groups": {
        "playbook-alpha": {"passed": 0, "failed": 0, "skipped": 0, "errors": 0,
                           "status": "NOT_RUN",
                           "infrastructure_reason": "host did not return from reboot"},
    },
}

# Keys deliberately removed from the artifact schema: the pipeline emits no
# producer for any of them, and `jenkins_url` contradicts the repo's explicit
# "the pipeline build URL is intentionally not shown" policy.
REMOVED_KEYS = ("machine", "ticket", "last_phase", "jenkins_url")

# The row schema the website dashboard already reads for this same filename.
DASHBOARD_ROW_KEYS = ("test_id", "success", "skipped", "duration", "error_message")


def run_verdict(summary, playbook, console="", platform="linux", build_url=BUILD,
                patch=None):
    """Run main() in a temp cwd against a fixture summary.json.

    `summary`/`console` may be UNREACHABLE to simulate a fetch transport
    failure (fetch() returns None) rather than an empty document.
    `patch` is an optional {attribute: replacement} applied to the module, used
    to inject an unexpected exception.

    Returns (exit_code, artifact_dict_or_None, stdout).
    """
    raw = (UNREACHABLE if summary is UNREACHABLE
           else json.dumps(summary) if summary is not None else "{}")

    def fake_fetch(url, user, token):
        value = console if url.endswith("consoleText") else raw
        return None if value is UNREACHABLE else value

    env = {"BUILD_URL": build_url, "PLAYBOOK_ID": playbook, "PLATFORM": platform,
           "ORCHESTRAI_PIPELINE_USER": "u", "ORCHESTRAI_PIPELINE_TOKEN": "t"}
    old_env = {k: os.environ.get(k) for k in list(env) + ["GITHUB_OUTPUT"]}
    saved = {"fetch": verdict.fetch}
    for name in (patch or {}):
        saved[name] = getattr(verdict, name)
    cwd = os.getcwd()
    buf = io.StringIO()
    try:
        verdict.fetch = fake_fetch
        for name, value in (patch or {}).items():
            setattr(verdict, name, value)
        os.environ.pop("GITHUB_OUTPUT", None)
        os.environ.update(env)
        with tempfile.TemporaryDirectory() as tmp:
            os.chdir(tmp)
            with contextlib.redirect_stdout(buf):
                try:
                    verdict.main()
                    code = 0
                except SystemExit as e:
                    code = e.code or 0
            path = Path(tmp) / "test-results" / "summary.json"
            doc = json.loads(path.read_text()) if path.exists() else None
    finally:
        os.chdir(cwd)
        for name, value in saved.items():
            setattr(verdict, name, value)
        for k, v in old_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    return code, doc, buf.getvalue()


class TestPassingPath(unittest.TestCase):
    def test_group_passed_exits_zero_with_populated_results(self):
        code, doc, _ = run_verdict(OLD_SCHEMA, "alpha")
        self.assertEqual(code, 0)
        self.assertEqual(doc["outcome"], "PASSED")
        self.assertEqual(doc["failed"], 0)
        self.assertGreater(doc["passed"], 0)
        self.assertIsNone(doc["infrastructure_reason"])
        # The bug: `results` was always [], hiding the real outcome.
        self.assertTrue(doc["results"], "results must never be empty")

    def test_passing_artifact_carries_reportportal_url_and_outcome(self):
        _, doc, _ = run_verdict(OLD_SCHEMA, "alpha")
        for key in ("outcome", "infrastructure_reason", "reportportal_url"):
            self.assertIn(key, doc)
        self.assertEqual(doc["reportportal_url"], "https://rp.example.invalid/launch/1")

    def test_producerless_fields_are_not_emitted(self):
        # No pipeline key feeds these; emitting them made an unimplemented
        # feature look implemented (and leaked the build URL).
        _, doc, _ = run_verdict(OLD_SCHEMA, "alpha")
        for key in REMOVED_KEYS:
            self.assertNotIn(key, doc)


class TestResultRowSchema(unittest.TestCase):
    """`results` rows must be a superset of the row shape the website already
    reads for this filename — not a second, incompatible shape."""

    def test_passing_row_matches_dashboard_schema(self):
        _, doc, _ = run_verdict(OLD_SCHEMA, "alpha")
        row = doc["results"][0]
        for key in DASHBOARD_ROW_KEYS:
            self.assertIn(key, row)
        self.assertEqual(row["test_id"], "alpha")
        self.assertIs(row["success"], True)
        self.assertIs(row["skipped"], False)
        self.assertEqual(row["error_message"], "")
        self.assertEqual(row["status"], "PASSED")

    def test_failing_row_matches_dashboard_schema(self):
        _, doc, _ = run_verdict(OLD_SCHEMA, "beta")
        row = doc["results"][0]
        for key in DASHBOARD_ROW_KEYS:
            self.assertIn(key, row)
        self.assertIs(row["success"], False)
        self.assertIs(row["skipped"], False)
        self.assertEqual(row["status"], "FAILED")
        self.assertTrue(row["error_message"])

    def test_not_run_row_matches_dashboard_schema(self):
        _, doc, _ = run_verdict(NEW_SCHEMA_NOT_RUN, "alpha")
        row = doc["results"][0]
        for key in DASHBOARD_ROW_KEYS:
            self.assertIn(key, row)
        self.assertEqual(row["test_id"], "alpha")
        self.assertIs(row["success"], False)
        # A consumer that only knows success/skipped must not count a
        # never-executed playbook as a red test.
        self.assertIs(row["skipped"], True)
        self.assertEqual(row["duration"], 0)
        self.assertEqual(row["status"], "NOT_RUN")
        self.assertIn("host did not return from reboot", row["error_message"])


class TestFailingPath(unittest.TestCase):
    def test_group_failed_exits_one(self):
        code, doc, _ = run_verdict(OLD_SCHEMA, "beta")
        self.assertEqual(code, 1)
        self.assertEqual(doc["outcome"], "FAILED")
        self.assertGreater(doc["failed"], 0)
        self.assertTrue(doc["results"])

    def test_old_schema_missing_group_still_fails(self):
        # No expected_groups, no console result -> today's behaviour exactly.
        code, doc, out = run_verdict(OLD_SCHEMA, "gamma")
        self.assertEqual(code, 1)
        self.assertEqual(doc["outcome"], "FAILED")
        self.assertEqual(doc["failed"], 1)
        self.assertIn("No verdict for gamma", out)

    def test_old_schema_console_fallback_still_works(self):
        console = ('Started suite "playbook-gamma #3" id=abc-123\n'
                   'Finished item abc-123 -> PASSED\n')
        code, doc, _ = run_verdict(OLD_SCHEMA, "gamma", console=console)
        self.assertEqual(code, 0)
        self.assertEqual(doc["outcome"], "PASSED")

    def test_empty_summary_document_keeps_old_behaviour(self):
        # A reachable but empty summary.json is a real (if unhelpful) answer,
        # NOT a transport failure — it must stay a hard failure as today.
        code, doc, _ = run_verdict({}, "alpha")
        self.assertEqual(code, 1)
        self.assertEqual(doc["outcome"], "FAILED")


class TestInfrastructure(unittest.TestCase):
    def test_not_run_group_exits_two_without_fabricating_a_failure(self):
        code, doc, out = run_verdict(NEW_SCHEMA_NOT_RUN, "alpha")
        self.assertEqual(code, 2)
        self.assertEqual(doc["outcome"], "NOT_RUN")
        self.assertEqual(doc["failed"], 0, "NOT_RUN must not fabricate a failure")
        self.assertEqual(doc["infrastructure_reason"], "host did not return from reboot")
        self.assertTrue(doc["results"])
        self.assertEqual(doc["results"][0]["status"], "NOT_RUN")
        self.assertIn("host did not return from reboot", doc["results"][0]["error_message"])
        self.assertIn("::warning::", out)

    def test_group_missing_from_new_schema_is_infrastructure_not_failure(self):
        code, doc, _ = run_verdict(NEW_SCHEMA_NOT_RUN, "gamma")
        self.assertEqual(code, 2, "a planned-but-absent group is not a test failure")
        self.assertEqual(doc["outcome"], "NOT_RUN")
        self.assertEqual(doc["failed"], 0)
        self.assertTrue(doc["infrastructure_reason"])
        self.assertTrue(doc["results"])

    def test_interrupted_group_exits_two(self):
        summary = {"expected_groups": ["playbook-alpha"],
                   "groups": {"playbook-alpha": {
                       "passed": 0, "failed": 0, "skipped": 0, "errors": 0,
                       "status": "INTERRUPTED",
                       "infrastructure_reason": "machine acquisition timed out"}}}
        code, doc, _ = run_verdict(summary, "alpha")
        self.assertEqual(code, 2)
        self.assertEqual(doc["outcome"], "INTERRUPTED")
        self.assertEqual(doc["failed"], 0)
        self.assertEqual(doc["infrastructure_reason"], "machine acquisition timed out")

    def test_missing_build_url_is_infrastructure_not_a_failure(self):
        # This is the 79-job shape: no build means NO playbook in the batch
        # ran, so it must not fan out into N alleged test failures.
        code, doc, out = run_verdict(OLD_SCHEMA, "alpha", build_url="")
        self.assertEqual(code, 2)
        self.assertEqual(doc["outcome"], "NOT_RUN")
        self.assertEqual(doc["failed"], 0)
        self.assertEqual(doc["total_tests"], 0)
        self.assertIn("no OrchestrAI build was produced", doc["infrastructure_reason"])
        self.assertTrue(doc["results"])
        self.assertIn("::warning::", out)

    def test_unreachable_build_summary_is_infrastructure_not_a_failure(self):
        # 401 / network / aborted build: fetch() returns None, which must be
        # distinguishable from an empty document.
        code, doc, out = run_verdict(UNREACHABLE, "alpha", console=UNREACHABLE)
        self.assertEqual(code, 2)
        self.assertEqual(doc["outcome"], "NOT_RUN")
        self.assertEqual(doc["failed"], 0)
        self.assertIn("could not retrieve the build summary",
                      doc["infrastructure_reason"])
        self.assertIn("::warning::", out)

    def test_unreachable_summary_still_defers_to_a_readable_console(self):
        console = ('Started suite "playbook-alpha #1" id=abc-123\n'
                   'Finished item abc-123 -> PASSED\n')
        code, doc, _ = run_verdict(UNREACHABLE, "alpha", console=console)
        self.assertEqual(code, 0)
        self.assertEqual(doc["outcome"], "PASSED")


class TestNeverCrashWithoutAnArtifact(unittest.TestCase):
    """`if-no-files-found: ignore` turns a crash into a silent undercount."""

    def test_non_dict_groups_writes_an_artifact_and_exits_two(self):
        code, doc, out = run_verdict({"groups": [1, 2]}, "alpha")
        self.assertIsNotNone(doc, "an artifact must be written even on bad input")
        self.assertEqual(code, 2)
        self.assertEqual(doc["outcome"], "INTERRUPTED")
        self.assertEqual(doc["failed"], 0)
        self.assertTrue(doc["infrastructure_reason"])
        self.assertNotIn("Traceback", out)

    def test_non_dict_groups_variants_all_write_an_artifact(self):
        for bad in ([1, 2], "groups", 7, True):
            _, doc, _ = run_verdict({"groups": bad}, "alpha")
            self.assertIsNotNone(doc, f"no artifact written for groups={bad!r}")

    def test_unexpected_exception_still_writes_an_artifact(self):
        def boom(_grp):
            raise RuntimeError("kaboom")

        code, doc, out = run_verdict(OLD_SCHEMA, "alpha",
                                     patch={"status_from_group": boom})
        self.assertIsNotNone(doc, "an artifact must survive an unexpected crash")
        self.assertEqual(code, 2)
        self.assertEqual(doc["outcome"], "INTERRUPTED")
        self.assertEqual(doc["failed"], 0)
        self.assertIn("kaboom", doc["infrastructure_reason"])
        self.assertIn("::warning::", out)


class TestZeroCountsNeverPass(unittest.TestCase):
    def test_group_claiming_passed_with_zero_counts_is_not_passed(self):
        summary = {"groups": {"playbook-alpha": {
            "passed": 0, "failed": 0, "skipped": 0, "errors": 0, "status": "PASSED"}}}
        code, doc, _ = run_verdict(summary, "alpha")
        self.assertNotEqual(doc["outcome"], "PASSED")
        self.assertNotEqual(code, 0)
        self.assertEqual(code, 2)

    def test_no_artifact_ever_has_passed_with_zero_tests(self):
        for summary, pb in ((OLD_SCHEMA, "alpha"), (OLD_SCHEMA, "beta"),
                            (NEW_SCHEMA_NOT_RUN, "alpha"),
                            (NEW_SCHEMA_NOT_RUN, "gamma")):
            _, doc, _ = run_verdict(summary, pb)
            if doc["outcome"] == "PASSED":
                self.assertGreater(doc["total_tests"], 0)


class TestExitCodeMap(unittest.TestCase):
    """STRUCTURAL: asserts the helper exists and maps as the contract says.
    (Against the pre-change script this errors rather than fails — the helper
    did not exist. The behavioural coverage is in the classes above.)"""

    def test_exit_code_for(self):
        self.assertEqual(verdict.exit_code_for("PASSED"), 0)
        self.assertEqual(verdict.exit_code_for("FAILED"), 1)
        self.assertEqual(verdict.exit_code_for("NOT_RUN"), 2)
        self.assertEqual(verdict.exit_code_for("INTERRUPTED"), 2)


if __name__ == "__main__":
    unittest.main()
