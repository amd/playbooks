#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT
"""
Tests for English and localized playbooks sharing OrchestrAI batches.

A device and OS is one batch, so one run on one machine, for every language.
Batch members are keys ("<id>", "<locale>/<id>"); each is its own plan group.
A localized entry that executes exactly what its English entry in the same run
does is not run again: it reports the English result.

Usage:
    python3 .github/tests/test_orchestrai_localized_batches.py
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
import orchestrai_trigger as trigger  # noqa: E402
from orchestrai_keys import group_id, member_key, split_key  # noqa: E402
from orchestrai_matrix import build, parse_languages, unknown_filters  # noqa: E402
from orchestrai_prepare_matrices import batch_matrix  # noqa: E402

CFG = {"device_to_tags": {"halo": ["apu_halo"]}, "device_to_gfx": {"halo": "gfx1151"}}


def readme_test(code, timeout=300):
    return (f"<!-- @test:id=step timeout={timeout} -->\n```bash\n{code}\n```\n"
            "<!-- @test:end -->\n")


class Fixture:
    """A repository with English playbooks and a zh-CN overlay of each."""

    def __init__(self, root):
        self.root = Path(root)

    def english(self, pb, code, devices=None):
        d = self.root / "playbooks" / "core" / pb
        d.mkdir(parents=True)
        (d / "playbook.json").write_text(json.dumps({
            "id": pb, "title": pb, "description": pb,
            "supported_platforms": {"halo": ["linux", "windows"]},
            "tested_platforms": devices or {"halo": ["linux", "windows"]}}))
        (d / "README.md").write_text(f"# {pb}\n\nRun it:\n\n" + readme_test(code))
        return d

    def chinese(self, pb, code, timeout=300, strict=False):
        d = self.root / "localized-playbooks" / "zh-CN" / "core" / pb
        d.mkdir(parents=True)
        if strict:
            (d / "playbook.json").write_text(json.dumps({
                "id": pb, "title": pb, "description": pb, "localized_only": True,
                "supported_platforms": {"halo": ["linux"]},
                "tested_platforms": {"halo": ["linux"]}}))
        (d / "README.md").write_text(f"# {pb}\n\n运行：\n\n" + readme_test(code, timeout))
        return d


class Batches(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Fixture(tmp.name)
        self.repo.english("same", "echo hello")
        self.repo.chinese("same", "echo hello", timeout=120)  # prose and time limit only
        self.repo.english("changed", "pip install torch")
        self.repo.chinese("changed", "pip install torch -i https://mirror.example")
        self.repo.chinese("china-only", "echo modelscope", strict=True)

    def build(self, english, localized, **kw):
        return build(english, CFG, locale="zh-CN", localized_playbooks=localized,
                     root=self.repo.root, **kw)

    def test_both_languages_share_one_batch_per_device_and_os(self):
        _, batches = self.build(["same", "changed"], ["same", "changed", "china-only"])
        self.assertEqual(sorted(batches), ["linux/halo", "windows/halo"])
        linux = batches["linux/halo"]
        self.assertEqual(linux["playbooks"], ["same", "changed", "zh-CN/changed", "zh-CN/china-only"])
        self.assertEqual(linux["localized_only"], {"zh-CN/changed": False, "zh-CN/china-only": True})
        self.assertEqual(batches["windows/halo"]["playbooks"], ["same", "changed", "zh-CN/changed"])

    def test_a_translation_that_runs_the_same_tests_is_not_run_again(self):
        matrix, batches = self.build(["same", "changed"], ["same", "changed"])
        self.assertEqual(batches["linux/halo"]["covered"], {"zh-CN/same": "same"})
        self.assertNotIn("zh-CN/same", batches["linux/halo"]["playbooks"])
        covered = [e for e in matrix if e.get("covered_by")]
        self.assertEqual({(e["key"], e["platform"]) for e in covered},
                         {("zh-CN/same", "linux"), ("zh-CN/same", "windows")})

    def test_a_different_playbook_asset_is_run(self):
        (self.repo.root / "localized-playbooks/zh-CN/core/same/assets").mkdir()
        (self.repo.root / "localized-playbooks/zh-CN/core/same/assets/run.sh").write_text("exit 1\n")
        _, batches = self.build(["same"], ["same"])
        self.assertIn("zh-CN/same", batches["linux/halo"]["playbooks"])
        self.assertNotIn("covered", batches["linux/halo"])

    def test_nothing_is_skipped_without_its_english_entry_in_the_run(self):
        # The English playbook is not in this run, or not on this OS.
        _, batches = self.build([], ["same"])
        self.assertEqual(batches["linux/halo"]["playbooks"], ["zh-CN/same"])
        _, batches = self.build(["same"], ["same"], platforms={"linux"})
        self.assertEqual(batches["linux/halo"]["covered"], {"zh-CN/same": "same"})

    def test_an_entry_that_cannot_be_compared_is_run(self):
        with mock.patch("orchestrai_matrix.localized_execution", side_effect=ValueError("boom")):
            _, batches = self.build(["same"], ["same"])
        self.assertIn("zh-CN/same", batches["linux/halo"]["playbooks"])

    def test_one_language_alone_is_unchanged(self):
        # !orc locale=zh-CN: the locale's playbooks only, nothing to compare with.
        _, batches = build(["same", "china-only"], CFG, locale="zh-CN", root=self.repo.root)
        self.assertEqual(batches["linux/halo"]["playbooks"], ["zh-CN/same", "zh-CN/china-only"])
        _, batches = build(["same"], CFG, root=self.repo.root)
        self.assertEqual(batches["linux/halo"]["playbooks"], ["same"])

    def test_the_batch_job_lists_what_runs_and_what_is_covered(self):
        matrix, _ = self.build(["same"], ["same", "changed"])
        jobs = {b["batch_id"]: b for b in batch_matrix(matrix, {"halo": "Halo"})}
        linux = jobs["linux/halo"]
        self.assertEqual((linux["label"], linux["locale"]), ("Halo · Linux", ""))
        self.assertEqual(linux["playbooks"], ["same", "zh-CN/changed"])
        self.assertEqual(linux["covered"], {"zh-CN/same": "same"})
        self.assertEqual(linux["count"], 3)


class Languages(Batches):
    """--languages: any number of locales in the same batches."""

    def setUp(self):
        super().setUp()
        d = self.repo.root / "localized-playbooks" / "ja" / "core" / "changed"
        d.mkdir(parents=True)
        (d / "README.md").write_text("# changed\n\n" + readme_test("pip install torch --pre"))

    def test_every_locale_shares_the_device_batches(self):
        _, batches = build([], CFG, root=self.repo.root, languages={
            "ja": ["changed"], "zh-CN": ["changed", "same"], "": ["changed", "same"]})
        self.assertEqual(sorted(batches), ["linux/halo", "windows/halo"])
        linux = batches["linux/halo"]
        # English first, then the locales in order; zh-CN/same runs English's tests.
        self.assertEqual(linux["playbooks"], ["changed", "same", "ja/changed", "zh-CN/changed"])
        self.assertEqual(linux["covered"], {"zh-CN/same": "same"})
        self.assertEqual(set(linux["localized_only"]), {"ja/changed", "zh-CN/changed"})

    def test_a_locale_without_english_runs_alone(self):
        _, batches = build([], CFG, root=self.repo.root, languages={"zh-CN": ["same"], "": []})
        self.assertEqual(batches["linux/halo"]["playbooks"], ["zh-CN/same"])

    def test_languages_json_reads_en_as_english(self):
        self.assertEqual(parse_languages('{"EN": ["a"], "": ["b", "a"], "zh-CN": ["a"]}'),
                         {"": ["a", "b"], "zh-CN": ["a"]})
        for bad in ('["a"]', '{"zh-CN": "a"}', "not json"):
            with self.assertRaises(ValueError):
                parse_languages(bad)

    def test_unknown_devices_and_platforms_are_errors(self):
        cfg = {"device_to_tags": {"halo": []}, "device_to_gfx": {"stx": "gfx1150"}}
        self.assertEqual(unknown_filters(cfg, {"halo", "stx"}, {"linux"}), [])
        self.assertEqual(unknown_filters(cfg, None, None), [])
        problems = unknown_filters(cfg, {"hallo"}, {"macos"})
        self.assertEqual(len(problems), 2)
        self.assertIn("unknown device(s): hallo (known: halo, stx)", problems[0])
        self.assertIn("unknown platform(s): macos", problems[1])


class Keys(unittest.TestCase):
    def test_keys_and_group_ids(self):
        self.assertEqual(member_key("demo"), "demo")
        self.assertEqual(member_key("demo", "zh-CN"), "zh-CN/demo")
        self.assertEqual(split_key("zh-CN/demo"), ("zh-CN", "demo"))
        self.assertEqual(split_key("demo"), ("", "demo"))
        self.assertEqual(group_id("demo"), "playbook-demo")
        self.assertEqual(group_id("zh-CN/demo"), "playbook-zh-CN-demo")


class Plan(unittest.TestCase):
    def test_each_language_is_its_own_group_on_the_same_machine(self):
        import yaml
        cfg = yaml.safe_load((HERE.parent / "orchestrai-config.yml").read_text())
        batch = {"platform": "linux", "arch": "halo", "tags": ["apu_halo"],
                 "playbooks": ["cvml", "zh-CN/cvml", "zh-CN/china-only"],
                 "localized_only": {"zh-CN/cvml": False, "zh-CN/china-only": True}}
        plan = trigger.make_plan(batch, "refs/heads/main", cfg, 1, "https://github.com/amd/playbooks",
                                 "a" * 40, "https://index.example")
        groups = {g["id"]: g["variables"] for g in plan["groups"]}
        self.assertEqual(list(groups), ["playbook-cvml", "playbook-zh-CN-cvml",
                                        "playbook-zh-CN-china-only"])
        self.assertNotIn("PLAYBOOK_LOCALE", groups["playbook-cvml"])
        self.assertEqual((groups["playbook-zh-CN-cvml"]["PLAYBOOK_ID"],
                          groups["playbook-zh-CN-cvml"]["PLAYBOOK_LOCALE"],
                          groups["playbook-zh-CN-cvml"]["PLAYBOOK_LOCALIZED_ONLY"]),
                         ("cvml", "zh-CN", "false"))
        self.assertEqual(groups["playbook-zh-CN-china-only"]["PLAYBOOK_LOCALIZED_ONLY"], "true")
        self.assertEqual(plan["run_settings"]["machines_per_hw_group"], 1)

    def test_provisioning_is_per_playbook_whatever_its_languages(self):
        batch = {"playbooks": ["cvml", "zh-CN/cvml", "zh-CN/openhands-getting-started"]}
        self.assertEqual(trigger.batch_playbook_ids(batch), ["cvml", "openhands-getting-started"])


STUB = '''import json, os, sys
pb, locale = os.environ["PLAYBOOK_ID"], os.environ.get("PLAYBOOK_LOCALE", "")
outcome = os.environ.get("STUB_" + (locale + "_" if locale else "") + pb.replace("-", "_"), "PASSED")
os.makedirs("test-results", exist_ok=True)
json.dump({"outcome": outcome, "cause": "never_ran" if outcome == "NOT_RUN" else None,
           "infrastructure_reason": "machine never came back" if outcome == "NOT_RUN" else ""},
          open("test-results/summary.json", "w"))
open(os.environ["GITHUB_OUTPUT"], "a").write(f"rp_url=https://rp/{locale}{pb}\\n")
sys.exit({"PASSED": 0, "FAILED": 1}.get(outcome, 2))
'''


class Results(unittest.TestCase):
    BATCH = {"batch_id": "linux/halo", "label": "Halo · Linux", "platform": "linux", "arch": "halo",
             "playbooks": ["demo", "zh-CN/changed"], "covered": {"zh-CN/demo": "demo"},
             "required": ["zh-CN/demo"]}

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.stub = self.dir / "verdict.py"
        self.stub.write_text(STUB)

    def resolve(self, batch, outcomes, **env):
        cwd = os.getcwd()
        os.chdir(self.dir)
        try:
            with mock.patch.object(bv, "VERDICT", self.stub), mock.patch("sys.stdout"), \
                    mock.patch.dict(os.environ, {"BATCH_JSON": json.dumps(batch), "DEFER_EXIT": "1",
                                                 "GITHUB_STEP_SUMMARY": "", **outcomes, **env}):
                bv.main()
            return {r["playbook"]: r for r in json.loads(Path("test-results/batch.json").read_text())}
        finally:
            os.chdir(cwd)

    def test_a_covered_translation_reports_its_english_result(self):
        rows = self.resolve(self.BATCH, {"STUB_demo": "FAILED", "STUB_zh-CN_changed": "PASSED"})
        self.assertEqual({k: r["outcome"] for k, r in rows.items()},
                         {"demo": "FAILED", "zh-CN/changed": "PASSED", "zh-CN/demo": "FAILED"})
        covered = rows["zh-CN/demo"]
        self.assertEqual((covered["covered_by"], covered["locale"], covered["playbook_id"],
                          covered["required"]), ("demo", "zh-CN", "demo", True))
        self.assertEqual(rows["zh-CN/changed"]["rp_url"], "https://rp/zh-CNchanged")
        self.assertTrue((self.dir / "test-results" / "zh-CN" / "changed").is_dir())
        self.assertFalse((self.dir / "test-results" / "zh-CN" / "demo").exists())
        self.assertEqual(bv.batch_failed(list(rows.values()), self.BATCH), ["zh-CN/demo"])
        self.assertIn("(same tests as `demo`, not run again)", bv.table(list(rows.values())))

    def test_a_covered_translation_is_never_retried_itself(self):
        rows = [{"playbook": "demo", "outcome": "NOT_RUN", "cause": "never_ran"},
                {"playbook": "zh-CN/demo", "outcome": "NOT_RUN", "cause": "never_ran",
                 "covered_by": "demo"}]
        with tempfile.TemporaryDirectory() as d:
            Path(d, "batch.json").write_text(json.dumps(rows))
            out = subprocess.run([sys.executable, str(HERE.parent / "scripts/orchestrai_batch_verdict.py"),
                                  "--retryable", str(Path(d, "batch.json"))], capture_output=True, text=True)
        self.assertEqual(out.stdout.split(), ["demo"])

    def test_a_retried_english_playbook_updates_its_translation(self):
        self.resolve(self.BATCH, {"STUB_demo": "NOT_RUN"})
        (self.dir / "first.json").write_text((self.dir / "test-results/batch.json").read_text())
        rows = self.resolve(dict(self.BATCH, playbooks=["demo"]), {"STUB_demo": "PASSED"},
                            RETRY_OF=str(self.dir / "first.json"))
        self.assertEqual((rows["demo"]["outcome"], rows["demo"]["attempt"]), ("PASSED", 2))
        self.assertEqual((rows["zh-CN/demo"]["outcome"], rows["zh-CN/demo"]["covered_by"]),
                         ("PASSED", "demo"))
        self.assertEqual(rows["zh-CN/changed"]["attempt"], 1)
        self.assertEqual(len(rows), 3)

    def test_a_localized_retry_finds_its_first_attempt(self):
        self.resolve(self.BATCH, {"STUB_zh-CN_changed": "NOT_RUN"})
        (self.dir / "first.json").write_text((self.dir / "test-results/batch.json").read_text())
        rows = self.resolve(dict(self.BATCH, playbooks=["zh-CN/changed"]), {},
                            RETRY_OF=str(self.dir / "first.json"))
        self.assertEqual((rows["zh-CN/changed"]["outcome"], rows["zh-CN/changed"]["first_outcome"]),
                         ("PASSED", "NOT_RUN"))
        self.assertTrue((self.dir / "test-results" / "zh-CN" / "changed-attempt1").is_dir())

    def test_the_configuration_table_lists_each_language(self):
        rows = self.resolve(self.BATCH, {})
        text = bv.by_configuration(list(rows.values()))
        for key in ("`demo`", "`zh-CN/changed`", "`zh-CN/demo`"):
            self.assertIn(key, text)


if __name__ == "__main__":
    unittest.main()
