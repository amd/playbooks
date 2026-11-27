#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
Regression tests for orchestrai_report.py.

Guards the aggregated !orc comment: playbooks that never ran must be rendered as
their own infrastructure category (not counted as test failures), the shared
infrastructure reason must be stated once — not repeated for all 13 of them —
and every row names its device and links its OrchestrAI run.

These tests drive the script through its COMMAND LINE, the same way
orchestrai-pr-command.yml does, and assert on the rendered Markdown.

Usage:
    python3 .github/tests/test_orchestrai_report.py
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "orchestrai_report.py"
CONFIG = Path(__file__).resolve().parents[1] / "orchestrai-config.yml"

_SPEC = importlib.util.spec_from_file_location("orchestrai_report", SCRIPT)
report = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(report)

MARKER = "<!-- orchestrai-orc-report -->"
REASON = "host did not return from reboot"
RUN = "https://orchestrai.example/#/runs/42"


def row(pb, outcome, arch="stx", platform="linux", locale="", reason="", **extra):
    """One batch.json row, as orchestrai_batch_verdict.py writes it."""
    return {"playbook": f"{locale}/{pb}" if locale else pb, "playbook_id": pb, "locale": locale,
            "platform": platform, "arch": arch, "batch_id": f"{platform}/{arch}",
            "outcome": outcome, "reason": reason, "run_url": RUN, "rp_url": "",
            "job_url": "https://github.example/job/1", "attempt": 1, **extra}


def artifacts(rows):
    """Materialise rows as one batch-results artifact per batch."""
    tmp = tempfile.mkdtemp()
    by_batch = {}
    for r in rows:
        by_batch.setdefault(r["batch_id"], []).append(r)
    for i, (batch_id, batch_rows) in enumerate(by_batch.items()):
        d = Path(tmp) / f"batch-results-{i}-{batch_id.replace('/', '-')}"
        d.mkdir(parents=True)
        (d / "batch.json").write_text(json.dumps(batch_rows))
    return tmp


def render(rows, expected=None, tmp=None, **kwargs):
    """Run the script exactly as the workflow does and return its stdout."""
    cmd = [sys.executable, str(SCRIPT), "--artifacts", tmp or artifacts(rows),
           "--config", str(CONFIG)]
    for key, value in kwargs.items():
        cmd += [f"--{key.replace('_', '-')}", value]
    env = {**os.environ, "PYTHONUTF8": "1", "EXPECTED_BATCHES": json.dumps(expected or [])}
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False, env=env,
                          encoding="utf-8")
    assert proc.returncode == 0, f"report script exited {proc.returncode}: {proc.stderr}"
    return proc.stdout


class TestInfrastructureRendering(unittest.TestCase):
    """2 real failures + 13 playbooks that never ran + 5 passes must render as
    three categories, not as 15 failures."""

    def setUp(self):
        rows = [row(f"fail{i}", "FAILED") for i in range(2)]
        rows += [row(f"nr{i:02d}", "NOT_RUN", reason=REASON) for i in range(13)]
        rows += [row(f"pass{i}", "PASSED") for i in range(5)]
        self.body = render(rows)

    def test_headline_separates_the_three_categories(self):
        self.assertIn("❌ 2 failed", self.body)
        self.assertIn("⚠️ 13 not run (infrastructure)", self.body)
        self.assertIn("✅ 5 passed", self.body)

    def test_not_run_rows_are_not_marked_as_failures(self):
        self.assertEqual(self.body.count("| ⚠️ not run |"), 13)
        self.assertEqual(self.body.count("| ❌ fail |"), 2)

    def test_reason_is_stated_once_not_per_playbook(self):
        self.assertEqual(self.body.count(REASON), 1)
        self.assertIn("13 playbooks did not run", self.body)

    def test_every_playbook_still_appears_in_the_table(self):
        for i in range(13):
            self.assertIn(f"| `nr{i:02d}` |", self.body)
        self.assertEqual(self.body.count("| `"), 20)


class TestRows(unittest.TestCase):
    def test_each_row_names_its_device_and_links_its_run(self):
        body = render([row("a", "PASSED", arch="rx9070xt", rp_url="https://rp/1")])
        self.assertIn("| Playbook | Device | OS | Result | Results |", body)
        self.assertIn(f"| `a` | RX 9070 XT | linux | ✅ pass | [OrchestrAI]({RUN}) · "
                      "[ReportPortal](https://rp/1) |", body)

    def test_an_unnamed_device_shows_its_id(self):
        self.assertIn("| `a` | newgpu | linux |", render([row("a", "PASSED", arch="newgpu")]))

    def test_languages_get_a_locale_column(self):
        body = render([row("a", "PASSED", arch="halo"),
                       row("a", "PASSED", arch="halo", locale="zh-CN", covered_by="a"),
                       row("b", "FAILED", arch="halo", locale="zh-CN")])
        self.assertIn("| Playbook | Locale | Device | OS | Result | Results |", body)
        self.assertIn("| `a` | en | Halo | linux | ✅ pass |", body)
        self.assertIn("| `a` | zh-CN | Halo | linux | ✅ pass (same tests as en, not run again) |", body)
        self.assertIn("| `b` | zh-CN | Halo | linux | ❌ fail |", body)
        self.assertIn("❌ 1 failed, ✅ 2 passed", body)

    def test_a_retried_playbook_says_so(self):
        body = render([row("a", "PASSED", attempt=2, first_outcome="NOT_RUN")])
        self.assertIn("✅ pass (retried; first: NOT_RUN)", body)

    def test_a_batch_that_uploaded_nothing_is_never_silently_missing(self):
        expected = [{"batch_id": "linux/stx", "platform": "linux", "arch": "stx",
                     "playbooks": ["a"]},
                     {"batch_id": "windows/halo", "platform": "windows", "arch": "halo",
                      "playbooks": ["b", "zh-CN/c"], "covered": {"zh-CN/b": "b"}}]
        body = render([row("a", "PASSED")], expected=expected)
        self.assertIn("| `a` | en | Strix | linux | ✅ pass |", body)
        for line in ("| `b` | en | Halo | windows | ⚠️ not run |",
                     "| `b` | zh-CN | Halo | windows | ⚠️ not run |",
                     "| `c` | zh-CN | Halo | windows | ⚠️ not run |"):
            self.assertIn(line, body)
        self.assertIn("3 playbooks did not run** — infrastructure: the batch job uploaded no results",
                      body)


class TestOtherShapes(unittest.TestCase):
    def test_distinct_reasons_are_grouped_separately(self):
        body = render([row("a", "NOT_RUN", reason="reboot"), row("b", "NOT_RUN", reason="reboot"),
                       row("c", "NOT_RUN", reason="acquisition timed out")])
        self.assertIn("2 playbooks did not run", body)
        self.assertIn("1 playbook did not run", body)
        self.assertEqual(body.count("reboot"), 1)
        self.assertEqual(body.count("acquisition timed out"), 1)

    def test_not_run_without_a_reason_still_renders_infrastructure(self):
        body = render([row("a", "NOT_RUN")])
        self.assertIn("⚠️ not run", body)
        self.assertIn("1 playbook did not run** — infrastructure: reason not reported", body)

    def test_interrupted_is_infrastructure_too(self):
        body = render([row("a", "INTERRUPTED", reason=REASON)])
        self.assertIn("⚠️ not run", body)
        self.assertNotIn("❌", body)

    def test_all_passed_has_no_infrastructure_section(self):
        body = render([row("a", "PASSED")])
        self.assertIn("all passed", body)
        self.assertNotIn("did not run", body)

    def test_no_artifacts(self):
        body = render([])
        self.assertIn("no results", body)
        self.assertIn("No playbooks were scheduled", body)
        self.assertIn(MARKER, body)

    def test_footer_and_marker_are_preserved(self):
        body = render([row("a", "PASSED")], sha="0123456789abcdef", ref="my-branch",
                      run_url="https://example.invalid/run/1",
                      filters="locales: en, zh-CN · devices: stx")
        self.assertTrue(body.startswith(MARKER))
        self.assertIn("tested `01234567` (my-branch) · locales: en, zh-CN · devices: stx · "
                      "[workflow run](https://example.invalid/run/1)", body)

    def test_unreadable_artifact_is_skipped_not_fatal(self):
        tmp = artifacts([row("a", "PASSED")])
        bad = Path(tmp) / "batch-results-9-linux-halo"
        bad.mkdir()
        (bad / "batch.json").write_text("{not json")
        body = render([], tmp=tmp)
        self.assertIn("| `a` |", body)
        self.assertEqual(body.count("| `"), 1)


class TestClassifyUnit(unittest.TestCase):
    def test_classify(self):
        self.assertEqual(report.classify({"outcome": "NOT_RUN"})[0], report.INFRA)
        self.assertEqual(report.classify({"outcome": "INTERRUPTED"})[0], report.INFRA)
        self.assertEqual(report.classify({"outcome": "PASSED"})[0], report.PASS)
        self.assertEqual(report.classify({"outcome": "FAILED"})[0], report.FAIL)
        self.assertEqual(report.classify({"outcome": "ERROR"})[0], report.FAIL)
        self.assertEqual(report.classify({})[0], report.FAIL)


if __name__ == "__main__":
    unittest.main()
