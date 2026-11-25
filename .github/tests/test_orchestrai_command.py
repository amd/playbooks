#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT
"""
Tests for the !orc PR command: which playbooks, languages, devices and OSes a
comment asks for, and the errors a typo gets instead of a run that tests nothing.

Usage:
    python3 .github/tests/test_orchestrai_command.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "orchestrai_command.py"
sys.path.insert(0, str(SCRIPT.parent))

import orchestrai_command as command  # noqa: E402
from orchestrai_command import CommandError, parse, resolve  # noqa: E402

CONFIG = "device_to_tags: {}\ndevice_to_gfx:\n  halo: gfx1151\n  stx: gfx1150\n"


class Repo(unittest.TestCase):
    """English a, b, c; zh-CN a, b; ja a."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        for pb in ("a", "b"):
            (self.root / "playbooks/core" / pb).mkdir(parents=True)
            (self.root / "localized-playbooks/zh-CN/core" / pb).mkdir(parents=True)
        (self.root / "playbooks/supplemental/c").mkdir(parents=True)
        (self.root / "localized-playbooks/ja/supplemental/a").mkdir(parents=True)
        self.config = self.root / "orchestrai-config.yml"
        self.config.write_text(CONFIG)

    def run_command(self, body, changed=""):
        languages, devices, platforms, filters, _ = resolve(body, changed, self.root, self.config)
        return languages, devices, platforms, filters

    def languages(self, body, changed=""):
        return self.run_command(body, changed)[0]

    def error(self, body, changed=""):
        with self.assertRaises(CommandError) as ctx:
            resolve(body, changed, self.root, self.config)
        return str(ctx.exception)


class Selection(Repo):
    CHANGED = "\n".join([
        "playbooks/core/a/README.md",
        "localized-playbooks/zh-CN/core/b/README.md",
        "localized-playbooks/ja/supplemental/a/playbook.json",
        "website/src/app/page.tsx",
        "playbooks/core/a/assets/run.sh",
    ])

    def test_bare_orc_tests_each_change_in_its_own_language(self):
        self.assertEqual(self.languages("!orc", self.CHANGED),
                         {"": ["a"], "zh-CN": ["b"], "ja": ["a"]})

    def test_a_locale_also_tests_the_english_changes_it_inherits(self):
        self.assertEqual(self.languages("!orc locale=zh-CN", self.CHANGED), {"zh-CN": ["a", "b"]})
        self.assertEqual(self.languages("!orc locale=en,ja", self.CHANGED), {"": ["a"], "ja": ["a"]})

    def test_nothing_changed_is_nothing_to_test(self):
        self.assertEqual(self.languages("!orc", "README.md"), {})

    def test_named_playbooks_default_to_english(self):
        self.assertEqual(self.languages("!orc a,b c"), {"": ["a", "b", "c"]})
        self.assertEqual(self.languages("!orc  a, b"), {"": ["a", "b"]})

    def test_all(self):
        self.assertEqual(self.languages("!orc all"), {"": ["a", "b", "c"]})
        self.assertEqual(self.languages("!orc all locale=all"),
                         {"": ["a", "b", "c"], "ja": ["a"], "zh-CN": ["a", "b"]})

    def test_named_playbooks_in_several_languages(self):
        self.assertEqual(self.languages("!orc a,b locale=en,zh-CN"),
                         {"": ["a", "b"], "zh-CN": ["a", "b"]})
        # b has no ja version: tested where it exists, noted where it does not.
        languages, _, _, _, notes = resolve("!orc a b locale=EN,ja", "", self.root, self.config)
        self.assertEqual(languages, {"": ["a", "b"], "ja": ["a"]})
        self.assertEqual(notes, ["not in ja: b"])

    def test_only_the_first_line_is_the_command(self):
        self.assertEqual(self.languages("!orc a\r\nplease also test b\n"), {"": ["a"]})


class LocalizedOrc(Repo):
    """`!localized-orc`, from before locale=, keeps its meaning: one locale."""
    CHANGED = Selection.CHANGED

    def test_bare_tests_the_localized_changes_of_the_one_changed_locale(self):
        zh_only = "playbooks/core/a/README.md\nlocalized-playbooks/zh-CN/core/b/README.md"
        self.assertEqual(self.languages("!localized-orc", zh_only), {"zh-CN": ["b"]})
        self.assertEqual(self.languages("!localized-orc", "playbooks/core/a/README.md"), {})
        self.assertIn("zh-CN; name one", self.error("!localized-orc", self.CHANGED))

    def test_a_locale_alone_tests_its_changes(self):
        self.assertEqual(self.languages("!localized-orc zh-CN", self.CHANGED), {"zh-CN": ["b"]})
        self.assertEqual(self.languages("!localized-orc ja", self.CHANGED), {"ja": ["a"]})
        # A localized playbook the PR deleted is not tested.
        deleted = "localized-playbooks/zh-CN/core/gone/README.md"
        self.assertEqual(self.languages("!localized-orc zh-CN", deleted), {})

    def test_a_locale_and_playbooks(self):
        self.assertEqual(self.languages("!localized-orc zh-CN all"), {"zh-CN": ["a", "b"]})
        self.assertEqual(self.languages("!localized-orc zh-CN a, b"), {"zh-CN": ["a", "b"]})
        _, _, _, filters = self.run_command("!localized-orc ja a")
        self.assertEqual(filters, "locales: ja")
        self.assertIn("unknown locale `zh-TW`", self.error("!localized-orc zh-TW a"))
        self.assertIn("no such playbook in ja: `c`", self.error("!localized-orc ja c"))

    def test_playbooks_alone_need_a_single_locale(self):
        self.assertIn("name the locale", self.error("!localized-orc a"))
        shutil.rmtree(self.root / "localized-playbooks/ja")
        self.assertEqual(self.languages("!localized-orc all"), {"zh-CN": ["a", "b"]})


class Filters(Repo):
    def test_devices_and_platforms(self):
        _, devices, platforms, filters = self.run_command("!orc a device=halo,STX platform=linux")
        self.assertEqual((devices, platforms), (["halo", "stx"], ["linux"]))
        self.assertEqual(filters, "devices: halo, stx · platforms: linux")

    def test_options_in_any_order_and_plural_names(self):
        languages, devices, platforms, filters = self.run_command(
            "!orc platforms=windows a locales=zh-CN devices=halo")
        self.assertEqual((languages, devices, platforms), ({"zh-CN": ["a"]}, ["halo"], ["windows"]))
        self.assertEqual(filters, "locales: zh-CN · devices: halo · platforms: windows")

    def test_no_filters_means_everything(self):
        self.assertEqual(self.run_command("!orc a")[1:], ([], [], ""))

    def test_devices_from_the_tag_variable_are_known(self):
        os.environ["ORCHESTRAI_DEVICE_TAGS"] = json.dumps({"r9700": ["x"]})
        self.addCleanup(os.environ.pop, "ORCHESTRAI_DEVICE_TAGS")
        self.assertEqual(self.run_command("!orc a device=r9700")[1], ["r9700"])


class Errors(Repo):
    def test_typos_fail_the_command(self):
        self.assertIn("unknown device `hallo` (known: halo, stx)", self.error("!orc a device=hallo"))
        self.assertIn("unknown platform `macos`", self.error("!orc a platform=macos"))
        self.assertIn("unknown locale `zh-TW` (available: en, ja, zh-CN)",
                      self.error("!orc a locale=zh-TW"))
        self.assertIn("unknown option `os=`", self.error("!orc a os=linux"))
        self.assertIn("no such playbook in en: `nope`", self.error("!orc a,nope"))
        self.assertIn("no such playbook in ja: `c`", self.error("!orc c locale=ja"))

    def test_malformed_commands(self):
        self.assertIn("`device=` needs a value", self.error("!orc a device="))
        self.assertIn("cannot be combined", self.error("!orc all a"))
        self.assertIn("not a playbook ID", self.error("!orc ../etc"))
        self.assertIn("not an `!orc` command", self.error("!orchestrate a"))
        self.assertIn("not an `!orc` command", self.error("!localized-orcs zh-CN a"))

    def test_a_locale_name_cannot_escape_the_directory(self):
        self.assertIn("unknown locale", self.error("!orc a locale=../playbooks"))


class CommandLine(Repo):
    def run_script(self, body, changed=""):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d, "github_output")
            env = {**os.environ, "BODY": body, "CHANGED": changed, "GITHUB_OUTPUT": str(out),
                   "PYTHONUTF8": "1"}
            proc = subprocess.run([sys.executable, str(SCRIPT), "--config", str(self.config),
                                   "--root", str(self.root)], env=env, capture_output=True, text=True)
            outputs = dict(line.split("=", 1) for line in out.read_text().splitlines())
        return proc.returncode, outputs, proc.stdout

    def test_outputs(self):
        rc, outputs, _ = self.run_script("!orc a locale=en,zh-CN device=halo")
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(outputs["languages"]), {"": ["a"], "zh-CN": ["a"]})
        self.assertEqual((outputs["devices"], outputs["platforms"]), ("halo", ""))
        self.assertEqual(outputs["filters"], "locales: en, zh-CN · devices: halo")
        self.assertNotIn("error", outputs)

    def test_a_refused_command_says_why(self):
        rc, outputs, stdout = self.run_script("!orc a device=hallo")
        self.assertEqual(rc, 1)
        self.assertIn("unknown device `hallo`", outputs["error"])
        self.assertIn("::error::unknown device", stdout)
        self.assertNotIn("languages", outputs)


class Parse(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(parse("!orc"), (None, {}))
        self.assertEqual(parse("!orc all device=halo device=stx,halo"),
                         ("all", {"devices": ["halo", "stx"]}))
        self.assertEqual(command.changed_playbooks(
            "playbooks/core/x/a.md\nlocalized-playbooks/zh-CN/supplemental/y/b.md\n"
            "localized-playbooks/zh-CN/README.md\nplaybooks/README.md"),
            {"": {"x"}, "zh-CN": {"y"}})


if __name__ == "__main__":
    unittest.main()
