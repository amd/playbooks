#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT
"""
Tests for a pull request's runs of a change to the OrchestrAI config or
scripts (orchestrai_config_changes.py): the entries the change makes run
differently, each on its own device, or a sample of them when it reaches many.

Usage:
    python3 .github/tests/test_orchestrai_config_changes.py
"""
import contextlib
import copy
import io
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

import orchestrai_config_changes as C  # noqa: E402
from orchestrai_matrix import build  # noqa: E402

APUS = ("halo", "halo_box", "stx", "grgh")
RADEONS = ("rx9070xt", "r9700")
CFG = {
    "playbook_repo": "https://github.com/amd/playbooks",
    "test_path_template": "L4-sys/playbooks/{platform}/sys_func-playbook_runner",
    "device_to_tags": {d: [f"tag_{d}"] for d in APUS + RADEONS},
    "device_to_gfx": {"halo": "gfx1151", "halo_box": "gfx1151", "stx": "gfx1150",
                      "grgh": "gfx1151", "rx9070xt": "gfx120X", "r9700": "gfx120X"},
    "device_families": {**{d: "ryzen_apu" for d in APUS}, **{d: "radeon" for d in RADEONS}},
    "pr_devices": {"ryzen_apu": ["halo", "stx", "grgh", "halo_box"], "radeon": ["rx9070xt", "r9700"]},
    "device_names": {"halo": "Halo"},
    "device_runs_as": {"grgh": "halo"},
    "device_site_ids": {"halo": ["maas-mkm-mnb"]},
    "extra_tags": {},
    "device_extra_tags": {},
    "extra_tag_devices": {"ram_128gb": ["halo", "halo_box"]},
    "superset_tags": ["ram_128gb"],
    "extra_install_scripts": {},
    "skip_devices": [],
    "skip_playbook_devices": {"heavy": ["stx"]},
    "run_settings": {"max_duration": 480, "max_test_case_duration": 90,
                     "acquire_timeout": 360, "default_machines_per_hw_group": 1},
    "provisioning": {
        "linux_install_scripts": [{"script": "gfx/linux-therock.sh", "reboot_after": False}],
        "linux_kernel_driver": {"install_scripts": [{"script": "gfx/linux.sh",
                                                     "reboot_after": True}]},
        "windows_driver": {"use": "public"},
        "windows_public_driver": {"install_scripts": [{"script": "gfx/windows-public-url.ps1",
                                                       "reboot_after": True}]},
    },
    "config_change_runs": {"max_entries": 8, "canary_playbooks": ["light"]},
}
EVERY_DEVICE = {d: ["linux", "windows"] for d in ("halo", "stx", "grgh", "rx9070xt", "r9700")}


def changed(**edits):
    """CFG with top-level keys replaced."""
    cfg = copy.deepcopy(CFG)
    cfg.update(copy.deepcopy(edits))
    return cfg


class Repo:
    """A repository with English playbooks and zh-CN overlays."""

    def __init__(self, root):
        self.root = Path(root)

    def playbook(self, pb, tested):
        d = self.root / "playbooks" / "core" / pb
        d.mkdir(parents=True)
        (d / "playbook.json").write_text(json.dumps({
            "id": pb, "title": pb, "description": pb,
            "supported_platforms": tested, "tested_platforms": tested,
            "required_platforms": tested}))
        (d / "README.md").write_text(f"# {pb}\n")

    def chinese(self, pb):
        d = self.root / "localized-playbooks" / "zh-CN" / "core" / pb
        d.mkdir(parents=True)
        (d / "README.md").write_text(f"# {pb}\n")


class Selection(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Repo(tmp.name)
        for pb in ("heavy", "light", "other"):
            self.repo.playbook(pb, EVERY_DEVICE)
        self.repo.playbook("zenith", {"halo_box": ["windows"]})
        self.repo.chinese("light")
        self.languages = {"": ["heavy", "light", "other", "zenith"], "zh-CN": ["light"]}
        env = mock.patch.dict(os.environ, {"ORCHESTRAI_DEVICE_TAGS": ""})
        env.start()
        self.addCleanup(env.stop)

    def select(self, head, base=CFG, scripts=False):
        with contextlib.redirect_stderr(io.StringIO()) as err:
            keys = C.select(base, head, self.languages, self.repo.root, controller_changed=scripts)
        self.notices = err.getvalue()
        return keys

    def test_the_same_config_runs_nothing(self):
        self.assertEqual(self.select(changed()), [])

    def test_names_and_pr_devices_run_nothing(self):
        head = changed(device_names={"halo": "Strix Halo"},
                       pr_devices={"ryzen_apu": ["stx", "halo"], "radeon": ["r9700"]})
        self.assertEqual(self.select(head), [])

    def test_a_new_runs_as_runs_that_device_only(self):
        head = changed(device_runs_as={"grgh": "halo", "halo_box": "halo"})
        self.assertEqual(self.select(head), [("", "zenith", "windows", "halo_box")])
        self.assertIn("group.variables.PLAYBOOK_DEVICE", self.notices)

    def test_an_extra_tag_runs_that_playbook_on_that_device(self):
        head = changed(device_extra_tags={"heavy": {"halo": ["ram_128gb"]}})
        self.assertEqual(self.select(head), [("", "heavy", "linux", "halo"),
                                             ("", "heavy", "windows", "halo")])

    def test_notices_name_what_differs_not_the_tags(self):
        head = changed(device_extra_tags={"heavy": {"halo": ["ram_128gb"]}})
        self.select(head)
        self.assertIn("machines.tags", self.notices)
        self.assertNotIn("ram_128gb", self.notices)

    def test_an_install_script_runs_its_playbook_where_it_applies(self):
        head = changed(extra_install_scripts={"other": [
            {"script": "gfx/windows-wsl.ps1", "reboot_after": True, "platforms": ["windows"],
             "devices": ["halo", "r9700"]}]})
        self.assertEqual(self.select(head), [("", "other", "windows", "halo"),
                                             ("", "other", "windows", "r9700")])

    def test_a_site_or_image_runs_that_device(self):
        head = changed(device_os_images={"r9700": {"linux": "ubuntu/resolute"}})
        self.assertEqual(sorted({k[2:] for k in self.select(head)}), [("linux", "r9700")])
        head = changed(device_site_ids={"halo": ["maas-mkm-mnb", "maas-mkm-cs"]})
        self.assertEqual(sorted({k[3] for k in self.select(head)}), ["halo"])

    def test_an_entry_no_longer_skipped_runs_and_a_newly_skipped_one_does_not(self):
        self.assertEqual(self.select(changed(skip_playbook_devices={})),
                         [("", "heavy", "linux", "stx"), ("", "heavy", "windows", "stx")])
        self.assertEqual(self.select(changed(skip_playbook_devices={"heavy": ["stx", "halo"]})), [])

    def test_localized_entries_run_with_their_english_ones(self):
        head = changed(device_site_ids={"halo": ["maas-mkm-mnb"], "rx9070xt": ["maas-mkm-cs"]})
        self.assertIn(("zh-CN", "light", "linux", "rx9070xt"), self.select(head))

    def test_a_change_to_every_entry_runs_one_per_os_and_family(self):
        head = changed(run_settings={**CFG["run_settings"], "max_duration": 600})
        self.assertEqual(self.select(head), [("", "light", "linux", "halo"),
                                             ("", "light", "linux", "rx9070xt"),
                                             ("", "light", "windows", "halo"),
                                             ("", "light", "windows", "rx9070xt")])
        self.assertIn("more than config_change_runs.max_entries (8)", self.notices)

    def test_the_scripts_changing_runs_one_per_os_and_family(self):
        self.assertEqual(self.select(changed(), scripts=True), [
            ("", "light", "linux", "halo"), ("", "light", "linux", "rx9070xt"),
            ("", "light", "windows", "halo"), ("", "light", "windows", "rx9070xt")])

    def test_a_broad_change_to_some_devices_runs_one_on_each(self):
        # grgh now runs as itself: every grgh entry, more than max_entries.
        head = changed(device_runs_as={}, config_change_runs={"max_entries": 3,
                                                              "canary_playbooks": ["light"]})
        self.assertEqual(self.select(head), [("", "light", "linux", "grgh"),
                                             ("", "light", "windows", "grgh")])

    def test_a_windows_provisioning_change_samples_windows_only(self):
        prov = copy.deepcopy(CFG["provisioning"])
        prov["windows_public_driver"]["install_scripts"][0]["reboot_after"] = False
        self.assertEqual(self.select(changed(provisioning=prov)),
                         [("", "light", "windows", "halo"), ("", "light", "windows", "rx9070xt")])

    def test_without_canaries_the_first_playbook_by_name_runs(self):
        head = changed(run_settings={**CFG["run_settings"], "acquire_timeout": 300},
                       config_change_runs={"max_entries": 2})
        self.assertEqual({k[1] for k in self.select(head)}, {"heavy"})

    def test_an_unreadable_base_config_samples_every_entry(self):
        self.assertEqual(len(self.select(changed(), base=None)), 4)
        self.assertEqual(len(self.select(changed(), base={"run_settings": {}})), 4)
        self.assertIn("Cannot apply the base revision's config", self.notices)

    def test_device_tags_come_from_the_repo_variable(self):
        tags = json.dumps({**CFG["device_to_tags"], "halo": ["tag_halo", "ram_64gb"]})
        with mock.patch.dict(os.environ, {"ORCHESTRAI_DEVICE_TAGS": tags}):
            self.assertEqual(self.select(changed(), base=changed(device_to_tags={})), [])

    def test_without_device_tags_every_known_device_stands_in(self):
        cfg = changed(device_to_tags={})
        self.assertEqual(self.select(changed(device_to_tags={}, device_runs_as={}), base=cfg),
                         sorted((loc, pb, os_, "grgh") for loc, pb in
                                (("", "heavy"), ("", "light"), ("", "other"), ("zh-CN", "light"))
                                for os_ in ("linux", "windows")))


class KeepThroughDeviceScope(unittest.TestCase):
    """orchestrai_matrix.py keeps a config-selected entry on its own device,
    where a pull request's device scope would pick another."""

    def test_kept_entries_survive_the_representative_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Repo(tmp)
            repo.playbook("p", {"halo": ["windows"], "halo_box": ["windows"]})
            key = ("", "p", "windows", "halo_box")
            with contextlib.redirect_stderr(io.StringIO()):
                matrix, _ = build(["p"], CFG, root=tmp, device_scope="representative")
                self.assertEqual([e["arch"] for e in matrix], ["halo"])
                matrix, _ = build(["p"], CFG, root=tmp, device_scope="representative",
                                  only={key}, keep={key})
                self.assertEqual([e["arch"] for e in matrix], ["halo_box"])
                matrix, _ = build(["p"], CFG, root=tmp, device_scope="representative",
                                  keep={key})
                self.assertEqual(sorted(e["arch"] for e in matrix), ["halo", "halo_box"])


class ControllerChanges(unittest.TestCase):
    def test_the_scripts_and_workflow_a_pr_run_uses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            def git(*args):
                subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)

            files = [".github/scripts/orchestrai_trigger.py", ".github/scripts/orchestrai_command.py",
                     ".github/scripts/orchestrai_config_changes.py",
                     ".github/scripts/run_playbook_tests.py",
                     ".github/workflows/test-playbooks-orchestrai.yml",
                     ".github/workflows/orchestrai-pr-command.yml"]
            for f in files:
                (root / f).parent.mkdir(parents=True, exist_ok=True)
                (root / f).write_text("v1\n")
            git("init", "-q")
            git("add", ".")
            git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base")
            base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                                  capture_output=True, text=True).stdout.strip()
            self.assertEqual(C.controller_changes(base, root), [])
            for f in files:
                (root / f).write_text("v2\n")
            (root / ".github/scripts/orchestrai_new.sh").write_text("new\n")
            git("add", ".")
            git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "head")
            self.assertEqual(C.controller_changes(base, root), [
                ".github/scripts/orchestrai_new.sh",
                ".github/scripts/orchestrai_trigger.py",
                ".github/workflows/test-playbooks-orchestrai.yml"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
