#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT
"""
Tests for a pull request's device scope (orchestrai_matrix.py --device-scope
representative): each playbook runs on one device per family and OS, chosen
from pr_devices in orchestrai-config.yml, instead of on every declared device.

Usage:
    python3 .github/tests/test_orchestrai_pr_devices.py
"""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
GITHUB = HERE.parent
sys.path.insert(0, str(GITHUB / "scripts"))

from orchestrai_matrix import build, representative  # noqa: E402

DEVICES = ["halo", "stx", "krk", "grgh", "rx9070xt", "rx7900xt", "r9700"]
CFG = {
    "device_to_tags": {d: [f"tag_{d}"] for d in DEVICES},
    "device_to_gfx": {},
    "device_families": {**{d: "ryzen_apu" for d in ("halo", "stx", "krk", "grgh")},
                        **{d: "radeon" for d in ("rx9070xt", "rx7900xt", "r9700")}},
    "pr_devices": {"ryzen_apu": ["halo", "stx", "krk"], "radeon": ["rx9070xt", "rx7900xt", "r9700"]},
}


def entry(playbook, platform, device, required=False, locale=""):
    e = {"playbook": playbook, "platform": platform, "arch": device, "required": required}
    if locale:
        e["locale"] = locale
    return e


def kept(matrix, cfg=CFG):
    return sorted((e["playbook"], e.get("locale", ""), e["platform"], e["arch"])
                  for e in representative(matrix, cfg))


class Representative(unittest.TestCase):
    def test_one_apu_and_one_radeon_per_os(self):
        matrix = [entry("p", os_, d, required=True) for d in DEVICES for os_ in ("linux", "windows")]
        self.assertEqual(kept(matrix), [("p", "", "linux", "halo"), ("p", "", "linux", "rx9070xt"),
                                        ("p", "", "windows", "halo"), ("p", "", "windows", "rx9070xt")])

    def test_each_os_picks_from_the_devices_it_has(self):
        matrix = [entry("p", "linux", "halo"), entry("p", "windows", "stx"),
                  entry("p", "windows", "krk"), entry("p", "linux", "r9700")]
        self.assertEqual(kept(matrix), [("p", "", "linux", "halo"), ("p", "", "linux", "r9700"),
                                        ("p", "", "windows", "stx")])

    def test_a_required_device_wins_over_a_preferred_one(self):
        # The Test Gate still checks a required device when the playbook has one.
        matrix = [entry("p", "linux", "halo"), entry("p", "linux", "stx", required=True)]
        self.assertEqual(kept(matrix), [("p", "", "linux", "stx")])

    def test_a_device_not_in_the_list_is_used_only_when_nothing_listed_is(self):
        self.assertEqual(kept([entry("p", "linux", "grgh"), entry("p", "linux", "krk")]),
                         [("p", "", "linux", "krk")])
        self.assertEqual(kept([entry("p", "linux", "grgh")]), [("p", "", "linux", "grgh")])

    def test_a_family_without_a_list_keeps_every_device(self):
        cfg = {**CFG, "device_families": {**CFG["device_families"], "npu1": "npu", "npu2": "npu"}}
        matrix = [entry("p", "linux", "npu1"), entry("p", "linux", "npu2")]
        self.assertEqual(kept(matrix, cfg), [("p", "", "linux", "npu1"), ("p", "", "linux", "npu2")])

    def test_every_language_of_a_playbook_gets_the_same_device(self):
        # English on halo and stx, its translation only on stx: one device, stx,
        # for both, so the translation can still report the English result.
        matrix = [entry("p", "linux", "halo"), entry("p", "linux", "stx"),
                  entry("p", "linux", "stx", required=True, locale="zh-CN")]
        self.assertEqual(kept(matrix), [("p", "", "linux", "stx"), ("p", "zh-CN", "linux", "stx")])

    def test_playbooks_choose_independently(self):
        matrix = [entry("a", "linux", "halo"), entry("a", "linux", "stx"),
                  entry("b", "linux", "stx"), entry("b", "linux", "krk")]
        self.assertEqual(kept(matrix), [("a", "", "linux", "halo"), ("b", "", "linux", "stx")])


class Build(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        d = self.root / "playbooks" / "core" / "p"
        d.mkdir(parents=True)
        tested = {dev: ["linux", "windows"] for dev in DEVICES}
        (d / "playbook.json").write_text(json.dumps({
            "id": "p", "tested_platforms": tested,
            "required_platforms": {dev: ["linux", "windows"] for dev in DEVICES if dev != "grgh"}}))
        (d / "README.md").write_text("# p\n\n<!-- @test:id=s timeout=60 -->\n```bash\necho hi\n```\n"
                                     "<!-- @test:end -->\n")

    def build(self, scope):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            matrix, batches = build(["p"], CFG, root=self.root, device_scope=scope)
        return matrix, batches, err.getvalue()

    def test_a_pull_request_runs_four_batches_instead_of_fourteen(self):
        matrix, batches, err = self.build("representative")
        self.assertEqual(sorted(batches), ["linux/halo", "linux/rx9070xt",
                                           "windows/halo", "windows/rx9070xt"])
        self.assertTrue(all(e["required"] for e in matrix))
        self.assertIn("not tested here: grgh (linux), grgh (windows), krk (linux)", err)
        self.assertIn("Comment !orc", err)

    def test_every_other_run_keeps_every_device(self):
        matrix, batches, err = self.build("all")
        self.assertEqual(len(batches), 14)
        self.assertNotIn("not tested here", err)

    def test_an_unknown_scope_is_refused(self):
        with self.assertRaises(ValueError):
            self.build("some")

    def test_only_the_entries_the_pull_request_changed_run(self):
        # The PR changed p's Linux tests only: its Windows entries do not run,
        # and of the Linux ones one APU and one Radeon GPU do.
        only = {("", "p", "linux", d) for d in DEVICES}
        with contextlib.redirect_stderr(io.StringIO()):
            matrix, batches = build(["p"], CFG, root=self.root, device_scope="representative",
                                    only=only)
        self.assertEqual(sorted(batches), ["linux/halo", "linux/rx9070xt"])
        with contextlib.redirect_stderr(io.StringIO()):
            matrix, _ = build(["p"], CFG, root=self.root, only={("", "p", "windows", "stx")})
        self.assertEqual([(e["platform"], e["arch"]) for e in matrix], [("windows", "stx")])
        with contextlib.redirect_stderr(io.StringIO()):
            matrix, _ = build(["p"], CFG, root=self.root, only=None)
        self.assertEqual(len(matrix), 14)


class Config(unittest.TestCase):
    def test_the_shipped_lists_name_known_devices_of_their_family(self):
        cfg = yaml.safe_load((GITHUB / "orchestrai-config.yml").read_text())
        families = cfg["device_families"]
        self.assertEqual(set(cfg["pr_devices"]), set(families.values()))
        for family, devices in cfg["pr_devices"].items():
            for device in devices:
                self.assertEqual(families.get(device), family, device)

    def test_only_a_pull_request_narrows_the_devices(self):
        wf = yaml.load((GITHUB / "workflows" / "test-playbooks-orchestrai.yml").read_text(),
                       Loader=yaml.BaseLoader)
        step = next(s for s in wf["jobs"]["detect-and-trigger"]["steps"] if s.get("id") == "build")
        self.assertEqual(step["env"]["DEVICE_SCOPE"],
                         "${{ github.event_name == 'pull_request' && 'representative' || 'all' }}")
        # A pull request hands the selector's exact entries on, not just playbook IDs.
        self.assertEqual(step["env"]["ONLY_ENTRIES"], "${{ steps.detect.outputs.only }}")
        detect = next(s for s in wf["jobs"]["detect-and-trigger"]["steps"] if s.get("id") == "detect")
        self.assertEqual(detect["run"].count("--keys"), 2)
        self.assertIn('echo "only=${ONLY:-}"', detect["run"])
        cmd = yaml.load((GITHUB / "workflows" / "orchestrai-pr-command.yml").read_text(),
                        Loader=yaml.BaseLoader)
        for job in cmd["jobs"].values():
            for s in job.get("steps") or []:
                self.assertNotIn("DEVICE_SCOPE", s.get("env") or {}, "!orc tests every device")


if __name__ == "__main__":
    unittest.main()
