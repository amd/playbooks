#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
Regression tests for orchestrai_report.py.

Guards the aggregated !orc comment: playbooks that never ran must be rendered as
their own infrastructure category (not counted as test failures), and the shared
infrastructure_reason must be stated once — not repeated for all 13 of them.

These tests drive the script through its COMMAND LINE, the same way
orchestrai-pr-command.yml does, and assert on the rendered Markdown. That is
deliberate: an earlier version imported internal helpers, so against the
pre-change script every test errored with AttributeError instead of failing on
behaviour — proving only that a refactor had happened. Going through argv means
the pre-change script runs fine and the assertions fail on what it actually
renders (13 never-run playbooks shown as `❌ fail`, no infrastructure section).

The one structural class is marked as such.

Usage:
    python3 .github/scripts/test_orchestrai_report.py
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("orchestrai_report.py")

_SPEC = importlib.util.spec_from_file_location("orchestrai_report", SCRIPT)
report = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(report)

MARKER = "<!-- orchestrai-orc-report -->"
REASON = "host did not return from reboot"


def artifacts(docs):
    """Materialise {(pb, platform, arch): summary_dict} as artifact dirs."""
    tmp = tempfile.mkdtemp()
    for (pb, platform, arch), doc in docs.items():
        d = Path(tmp) / f"test-results-{pb}-{platform}-{arch}"
        d.mkdir(parents=True)
        (d / "summary.json").write_text(json.dumps(doc))
    return tmp


def render(docs, **kwargs):
    """Run the script exactly as the workflow does and return its stdout."""
    cmd = [sys.executable, str(SCRIPT), "--artifacts", artifacts(docs)]
    for key, value in kwargs.items():
        cmd += [f"--{key.replace('_', '-')}", value]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert proc.returncode == 0, f"report script exited {proc.returncode}: {proc.stderr}"
    return proc.stdout


def passed(pb):
    return {"playbook_id": pb, "platform": "linux", "total_tests": 3, "passed": 3,
            "failed": 0, "skipped": 0, "outcome": "PASSED",
            "infrastructure_reason": None,
            "results": [{"test_id": pb, "success": True, "skipped": False,
                         "duration": 0, "error_message": "", "status": "PASSED"}]}


def failed(pb):
    return {"playbook_id": pb, "platform": "linux", "total_tests": 3, "passed": 2,
            "failed": 1, "skipped": 0, "outcome": "FAILED",
            "infrastructure_reason": None,
            "results": [{"test_id": pb, "success": False, "skipped": False,
                         "duration": 0, "error_message": "boom", "status": "FAILED"}]}


def not_run(pb, reason=REASON):
    """The artifact a never-executed playbook now produces: zero counts,
    `failed` NOT fabricated to 1, and an explicit outcome."""
    return {"playbook_id": pb, "platform": "linux", "total_tests": 0, "passed": 0,
            "failed": 0, "skipped": 0, "outcome": "NOT_RUN",
            "infrastructure_reason": reason,
            "results": [{"test_id": pb, "success": False, "skipped": True,
                         "duration": 0, "error_message": reason, "status": "NOT_RUN"}]}


class TestInfrastructureRendering(unittest.TestCase):
    """The reported bug, end to end: 2 real failures + 13 playbooks that never
    ran + 5 passes must render as three categories, not as 15 failures."""

    def setUp(self):
        docs = {}
        for i in range(2):
            docs[(f"fail{i}", "linux", "stx")] = failed(f"fail{i}")
        for i in range(13):
            docs[(f"nr{i:02d}", "linux", "stx")] = not_run(f"nr{i:02d}")
        for i in range(5):
            docs[(f"pass{i}", "linux", "stx")] = passed(f"pass{i}")
        self.body = render(docs)

    def test_headline_separates_the_three_categories(self):
        self.assertIn("❌ 2 failed", self.body)
        self.assertIn("⚠️ 13 not run (infrastructure)", self.body)
        self.assertIn("✅ 5 passed", self.body)

    def test_not_run_rows_are_not_marked_as_failures(self):
        self.assertEqual(self.body.count("⚠️ not run"), 13)
        self.assertEqual(self.body.count("❌ fail |"), 2)

    def test_reason_is_stated_once_not_per_playbook(self):
        self.assertEqual(self.body.count(REASON), 1)
        self.assertIn("13 playbooks did not run", self.body)

    def test_every_playbook_still_appears_in_the_table(self):
        for i in range(13):
            self.assertIn(f"| `nr{i:02d}` |", self.body)
        self.assertEqual(self.body.count("| `"), 20)


class TestOtherShapes(unittest.TestCase):
    def test_distinct_reasons_are_grouped_separately(self):
        docs = {("a", "linux", "stx"): not_run("a", "reboot"),
                ("b", "linux", "stx"): not_run("b", "reboot"),
                ("c", "linux", "stx"): not_run("c", "acquisition timed out")}
        body = render(docs)
        self.assertIn("2 playbooks did not run", body)
        self.assertIn("1 playbook did not run", body)
        self.assertEqual(body.count("reboot"), 1)
        self.assertEqual(body.count("acquisition timed out"), 1)

    def test_not_run_without_a_reason_still_renders_infrastructure(self):
        body = render({("a", "linux", "stx"): not_run("a", None)})
        self.assertIn("⚠️ not run", body)
        self.assertIn("1 playbook did not run", body)

    def test_interrupted_is_infrastructure_too(self):
        doc = dict(not_run("a"), outcome="INTERRUPTED")
        body = render({("a", "linux", "stx"): doc})
        self.assertIn("⚠️ not run", body)
        self.assertNotIn("❌", body)

    def test_legacy_artifact_without_outcome_still_classifies(self):
        # An artifact written by the OLD verdict script has no `outcome`; the
        # pass/fail derivation must be byte-for-byte what it was.
        legacy_pass = {"playbook_id": "a", "platform": "linux", "total_tests": 1,
                       "passed": 1, "failed": 0, "skipped": 0, "results": []}
        legacy_fail = {"playbook_id": "b", "platform": "linux", "total_tests": 1,
                       "passed": 0, "failed": 1, "skipped": 0, "results": []}
        body = render({("a", "linux", "stx"): legacy_pass,
                       ("b", "linux", "stx"): legacy_fail})
        self.assertIn("| `a` | linux | stx | ✅ pass |", body)
        self.assertIn("| `b` | linux | stx | ❌ fail |", body)
        self.assertNotIn("did not run", body)

    def test_all_passed_has_no_infrastructure_section(self):
        body = render({("a", "linux", "stx"): passed("a")})
        self.assertIn("all passed", body)
        self.assertNotIn("did not run", body)

    def test_no_artifacts(self):
        body = render({})
        self.assertIn("no results", body)
        self.assertIn(MARKER, body)

    def test_footer_and_marker_are_preserved(self):
        body = render({("a", "linux", "stx"): passed("a")},
                      sha="0123456789abcdef", ref="my-branch",
                      run_url="https://example.invalid/run/1")
        self.assertTrue(body.startswith(MARKER))
        self.assertIn("tested `01234567` (my-branch)", body)
        self.assertIn("https://example.invalid/run/1", body)

    def test_unreadable_artifact_is_skipped_not_fatal(self):
        tmp = artifacts({("a", "linux", "stx"): passed("a")})
        bad = Path(tmp) / "test-results-b-linux-stx"
        bad.mkdir()
        (bad / "summary.json").write_text("{not json")
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--artifacts", tmp],
            capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("| `a` |", proc.stdout)
        self.assertNotIn("| `b` |", proc.stdout)


class TestClassifyUnit(unittest.TestCase):
    """STRUCTURAL: unit-level checks on the classifier introduced by this
    change. Against the pre-change script these error (no such helper); the
    behavioural coverage lives in the CLI-driven classes above."""

    def test_classify(self):
        self.assertEqual(report.classify({"outcome": "NOT_RUN"})[0], report.INFRA)
        self.assertEqual(report.classify({"outcome": "INTERRUPTED"})[0], report.INFRA)
        self.assertEqual(report.classify({"outcome": "PASSED"})[0], report.PASS)
        self.assertEqual(report.classify({"outcome": "FAILED"})[0], report.FAIL)
        # Legacy: no outcome -> derived from counts, exactly as before.
        self.assertEqual(report.classify({"passed": 1, "failed": 0})[0], report.PASS)
        self.assertEqual(report.classify({"passed": 0, "failed": 1})[0], report.FAIL)
        self.assertEqual(report.classify({"passed": 0, "failed": 0})[0], report.FAIL)


if __name__ == "__main__":
    unittest.main()
