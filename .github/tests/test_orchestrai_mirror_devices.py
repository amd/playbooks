#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
Tests for mirrored devices and per-device OS images in the OrchestrAI matrix
and trigger.

A mirrored device (mirror_devices in orchestrai-config.yml) is one no
playbook.json declares yet, tested wherever another device is. The fleet may
hold a single machine for it, so all of its playbooks must land in one batch
per platform, and a device kept on another OS between runs gets its image from
device_os_images, which the broker deploys at acquire time.

Usage:
    python3 .github/tests/test_orchestrai_mirror_devices.py
"""

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
GITHUB_DIR = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(GITHUB_DIR, "scripts"))

import orchestrai_matrix as matrix_mod  # noqa: E402
import orchestrai_trigger as trigger  # noqa: E402

PLAYBOOKS = {
    # id: tested_platforms
    "both-platforms": {"halo": ["linux", "windows"]},
    "big-model": {"halo": ["linux"]},
    "windows-only": {"halo": ["windows"]},
    "stx-only": {"stx": ["linux"]},
}


def config():
    return {
        "device_to_tags": {
            "halo": ["halo_tag"],
            "stx": ["stx_tag"],
            "grgh": ["grgh_tag", "pinning_group_tag"],
        },
        "device_to_gfx": {"halo": "gfx1151", "stx": "gfx1150", "grgh": "gfx1151"},
        "extra_tags": {"big-model": ["ram_128gb"]},
        "device_extra_tags": {"both-platforms": {"halo": ["ram_128gb"]}},
        "extra_tag_devices": {"ram_128gb": ["halo"]},
        "mirror_devices": {"grgh": {"from": "halo", "platforms": ["linux"]}},
        "device_os_images": {"grgh": {"linux": "custom/test-image"}},
    }


class MirroredDevices(unittest.TestCase):

    def setUp(self):
        self.cwd = os.getcwd()
        self.tmp = tempfile.TemporaryDirectory()
        for pb_id, tested in PLAYBOOKS.items():
            d = Path(self.tmp.name, "playbooks", "core", pb_id)
            d.mkdir(parents=True)
            (d / "playbook.json").write_text(json.dumps(
                {"tested_platforms": tested, "required_platforms": tested}))
        os.chdir(self.tmp.name)

    def tearDown(self):
        os.chdir(self.cwd)
        self.tmp.cleanup()

    def build(self, cfg=None, **kwargs):
        with contextlib.redirect_stderr(io.StringIO()) as err:
            matrix, batches = matrix_mod.build(list(PLAYBOOKS), cfg or config(), **kwargs)
        return matrix, batches, err.getvalue()

    def test_every_playbook_tested_on_the_source_device_runs_on_the_mirror(self):
        _, batches, _ = self.build()
        self.assertEqual(sorted(batches["linux/grgh"]["playbooks"]),
                         ["big-model", "both-platforms"])

    def test_only_the_listed_platforms_are_mirrored(self):
        matrix, batches, _ = self.build()
        self.assertNotIn("windows/grgh", batches)
        self.assertFalse([e for e in matrix if e["arch"] == "grgh" and e["platform"] != "linux"])

    def test_mirrored_entries_are_never_required(self):
        matrix, _, _ = self.build()
        self.assertTrue(any(e["required"] for e in matrix if e["arch"] == "halo"))
        self.assertTrue(all(not e["required"] for e in matrix if e["arch"] == "grgh"))

    def test_extra_tags_do_not_split_the_mirror_into_several_batches(self):
        """ram_128gb would split halo's playbooks across batches competing for
        the mirror's only machine, and is not satisfiable there anyway."""
        _, batches, _ = self.build()
        grgh = [b for b in batches if "grgh" in b]
        self.assertEqual(grgh, ["linux/grgh"])
        self.assertEqual(batches["linux/grgh"]["tags"], ["grgh_tag", "pinning_group_tag"])

    def test_the_source_device_is_unchanged(self):
        _, with_mirror, _ = self.build()
        cfg = config()
        del cfg["mirror_devices"]
        _, without, _ = self.build(cfg)
        self.assertEqual({k: v for k, v in with_mirror.items() if "grgh" not in k}, without)

    def test_without_a_tag_mapping_the_mirror_is_skipped_with_a_warning(self):
        cfg = config()
        del cfg["device_to_tags"]["grgh"]
        matrix, batches, err = self.build(cfg)
        self.assertFalse([b for b in batches if "grgh" in b])
        self.assertIn("grgh", err)

    def test_a_run_limited_to_the_mirror_selects_only_it(self):
        _, batches, _ = self.build(devices={"grgh"})
        self.assertEqual(list(batches), ["linux/grgh"])


class PerDeviceOsImage(unittest.TestCase):

    def plan(self, arch, platform):
        batch = {"platform": platform, "arch": arch, "gfx": "gfx1151",
                 "tags": ["t"], "playbooks": ["a", "b"]}
        cfg = dict(config(), test_path_template="L4-sys/playbooks/{platform}/runner",
                   run_settings={"max_duration": 240, "max_test_case_duration": 90,
                                 "acquire_timeout": 60})
        return trigger.make_plan(batch, "refs/heads/main", cfg, 1,
                                 "https://github.com/amd/playbooks", "main", "https://index")

    def test_the_configured_image_is_requested_for_every_group(self):
        groups = self.plan("grgh", "linux")["groups"]
        self.assertEqual([g.get("os_image") for g in groups], ["custom/test-image"] * 2)

    def test_other_devices_and_platforms_keep_the_stock_image(self):
        for arch, platform in (("halo", "linux"), ("grgh", "windows")):
            groups = self.plan(arch, platform)["groups"]
            self.assertTrue(all("os_image" not in g for g in groups), (arch, platform))

    def sessions(self, arch):
        api = mock.Mock(return_value={"run": {"id": "r1"}})
        with mock.patch.object(trigger, "api", api), mock.patch.dict(os.environ, {}, clear=True):
            trigger.start_run(None, f"linux/{arch}", self.plan(arch, "linux"), {}, "linux", "", "sha")
        return api.call_args[0][3]["plan_document"]["document"]["sessions"]

    def test_each_session_asks_the_control_plane_for_its_image(self):
        self.assertEqual({s["os_image"] for s in self.sessions("grgh")}, {"custom/test-image"})
        self.assertEqual({s["os_image"] for s in self.sessions("halo")}, {"ubuntu"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
