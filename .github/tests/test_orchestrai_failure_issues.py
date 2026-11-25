#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT
"""
Tests for create_failure_issues.py: which OrchestrAI results open an issue, its
title, and that a failure already reported gets a comment instead of a duplicate.

Usage:
    python3 .github/tests/test_orchestrai_failure_issues.py
"""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import create_failure_issues as cfi  # noqa: E402


def row(playbook, outcome, arch="halo", platform="linux", **extra):
    locale, _, playbook_id = playbook.rpartition("/")
    return {"playbook": playbook, "playbook_id": playbook_id, "locale": locale,
            "platform": platform, "arch": arch, "outcome": outcome, "required": False,
            "reason": "", "job_url": "https://github/job", "run_url": "https://orc/run",
            "rp_url": "", **extra}


class Results(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def batch(self, name, rows, summaries=None):
        d = self.root / name
        d.mkdir(parents=True)
        (d / "batch.json").write_text(json.dumps(rows))
        for key, summary in (summaries or {}).items():
            (d / key).mkdir(parents=True)
            (d / key / "summary.json").write_text(json.dumps(summary))


class FailedRows(Results):
    def test_only_test_failures_open_issues(self):
        self.batch("batch-results-0-linux-halo", [
            row("a", "PASSED"), row("b", "FAILED"), row("c", "ERROR"),
            row("d", "NOT_RUN"), row("e", "INTERRUPTED"),
            row("zh-CN/b", "FAILED", covered_by="b"), row("zh-CN/f", "FAILED"),
        ])
        self.assertEqual([r["playbook"] for r in cfi.failed_rows(self.root)],
                         ["b", "c", "zh-CN/f"])

    def test_each_failure_carries_its_test_counts(self):
        self.batch("batch-results-1-windows-stx", [row("b", "FAILED", arch="stx", platform="windows")],
                   {"b": {"total_tests": 5, "passed": 3, "failed": 2, "skipped": 0}})
        (failure,) = cfi.failed_rows(self.root)
        body = cfi.render_body(failure, "amd/playbooks", "https://github/run", "abc123")
        self.assertIn("3 passed, 2 failed, 0 skipped", body)
        self.assertIn("gh workflow run test-playbooks-orchestrai.yml --repo amd/playbooks "
                      "-f playbook_id=b -f device=stx -f platform=windows", body)
        self.assertIn("`!orc b device=stx platform=windows`", body)

    def test_a_localized_failure_is_run_again_in_its_locale(self):
        body = cfi.render_body(row("zh-CN/f", "FAILED"), "amd/playbooks", "", "")
        self.assertIn("-f playbook_id=f -f device=halo -f platform=linux -f locale=zh-CN", body)
        self.assertIn("`!orc f device=halo platform=linux locale=zh-CN`", body)

    def test_an_unreadable_batch_is_skipped(self):
        (self.root / "x").mkdir()
        (self.root / "x" / "batch.json").write_text("{not json")
        self.batch("y", [row("b", "FAILED")])
        self.assertEqual([r["playbook"] for r in cfi.failed_rows(self.root)], ["b"])


class Issues(Results):
    def test_title(self):
        self.assertEqual(cfi.build_title("zh-CN/f", "halo", "linux"),
                         "[CI] zh-CN/f failed on halo (linux)")

    def test_a_reported_failure_gets_a_comment_not_a_new_issue(self):
        self.batch("b0", [row("b", "FAILED"), row("c", "FAILED")])
        existing = {"[CI] b failed on halo (linux)": {"number": 7, "html_url": "u"}}
        with mock.patch.object(cfi, "find_existing_issue",
                               side_effect=lambda repo, token, title: existing.get(title)), \
             mock.patch.object(cfi, "comment_on_issue") as comment, \
             mock.patch.object(cfi, "create_issue", return_value={"html_url": "new"}) as create, \
             contextlib.redirect_stdout(io.StringIO()):
            created = cfi.process_failures(repo="amd/playbooks", token="t", results_root=self.root,
                                           run_url="https://github/run", sha="abc", dry_run=False)
        self.assertEqual(created, 1)
        self.assertEqual(comment.call_args.args[2], 7)
        self.assertEqual(create.call_args.args[2], "[CI] c failed on halo (linux)")
        self.assertEqual(create.call_args.args[4], ["ci-test-failure", "bug"])

    def test_dry_run_writes_nothing(self):
        self.batch("b0", [row("b", "FAILED")])
        with mock.patch.object(cfi, "_api_request") as api, \
             contextlib.redirect_stdout(io.StringIO()) as out:
            created = cfi.process_failures(repo="amd/playbooks", token="", results_root=self.root,
                                           run_url="", sha="", dry_run=True)
        self.assertEqual(created, 0)
        api.assert_not_called()
        self.assertIn("[CI] b failed on halo (linux)", out.getvalue())


if __name__ == "__main__":
    unittest.main()
