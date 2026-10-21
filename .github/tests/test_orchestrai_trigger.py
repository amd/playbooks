#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
Regression tests for orchestrai_trigger.py's config validation, scheduling
policy and the reporting switch (reportportal | api).

Usage:
    python3 .github/tests/test_orchestrai_trigger.py
"""

import contextlib
import io
import json
import os
import sys
import unittest
from unittest import mock

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
GITHUB_DIR = os.path.dirname(HERE)
SCRIPTS_DIR = os.path.join(GITHUB_DIR, "scripts")
CONFIG = os.path.join(GITHUB_DIR, "orchestrai-config.yml")
sys.path.insert(0, SCRIPTS_DIR)

import orchestrai_trigger as trigger  # noqa: E402

BATCH = {"platform": "linux", "arch": "stx", "gfx": "gfx1150",
         "tags": ["apu_stx"], "playbooks": ["gaia-agents"]}


def load_config():
    with open(CONFIG) as f:
        return yaml.safe_load(f)


class ReportingSwitch(unittest.TestCase):
    """reportportal adds the required ReportPortal publisher; api does not."""

    def run_main(self, reporting, credential="playbooks-reportportal"):
        env = {"BATCHES_JSON": json.dumps({"linux/stx": BATCH}),
               "ORCHESTRAI_ROCM_MULTI_ARCH_INDEX_URL": "https://index.example",
               "ORCHESTRAI_THEROCK_URL": "https://therock.example/t.tar.gz",
               "ORCHESTRAI_PLAYBOOK_SHA": "a" * 40, "ORCHESTRAI_V2_WORKSPACE": "ws",
               "ORCHESTRAI_REPORTING": reporting, "ORCHESTRAI_V2_RP_CREDENTIAL": credential}
        start = mock.Mock(return_value=({"linux/stx": "https://j/1/"}, {"linux/stx": "https://o/#/runs/r"}))
        import orchestrai_v2
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch.object(sys, "argv", ["trigger", "--config", CONFIG]), \
                mock.patch.object(orchestrai_v2, "trigger_batches", start), \
                contextlib.redirect_stderr(io.StringIO()):
            trigger.main()
        return start.call_args.args[4]

    def test_reportportal_is_the_default_and_exports(self):
        self.assertEqual(self.run_main(""), "playbooks-reportportal")
        self.assertEqual(self.run_main("reportportal"), "playbooks-reportportal")

    def test_api_keeps_results_in_orchestrai(self):
        self.assertEqual(self.run_main("api"), "")

    def test_reportportal_without_its_credential_fails_before_submitting(self):
        with self.assertRaises(SystemExit):
            self.run_main("reportportal", credential="")
        with self.assertRaises(SystemExit):
            self.run_main("both")


class AcquireTimeoutValidation(unittest.TestCase):

    def errors_for(self, **run_settings):
        cfg = load_config()
        cfg["run_settings"].update(run_settings)
        return [e for e in trigger.validate_config(cfg, {"b": BATCH}) if "acquire_timeout" in e]

    def test_the_shipped_config_is_valid(self):
        self.assertEqual(self.errors_for(), [])

    def test_non_positive_or_non_integer_values_are_rejected(self):
        for bad in (0, -5, "60", True, 60.5, None):
            self.assertTrue(self.errors_for(acquire_timeout=bad), bad)

    def test_a_timeout_that_leaves_no_time_to_run_is_rejected(self):
        self.assertTrue(self.errors_for(acquire_timeout=240, max_duration=240))
        self.assertEqual(self.errors_for(acquire_timeout=239, max_duration=240), [])

    def test_no_overall_limit_means_no_comparison(self):
        self.assertEqual(self.errors_for(acquire_timeout=600, max_duration=0), [])


class SchedulingPolicy(unittest.TestCase):

    def test_fixed_qwen_agent_playbooks_skip_stx_and_pin_krk_to_64gb(self):
        from orchestrai_matrix import build

        cfg = load_config()
        cfg["device_to_tags"] = {
            device: [f"fixture-{device}"] for device in cfg["device_to_gfx"]
        }
        affected = ("github-slack-development-digest", "openhands-getting-started")
        baseline_cfg = load_config()
        baseline_cfg["device_to_tags"] = cfg["device_to_tags"]
        for playbook in affected:
            baseline_cfg["skip_playbook_devices"].pop(playbook, None)

        old_cwd = os.getcwd()
        try:
            os.chdir(os.path.dirname(GITHUB_DIR))
            matrix, batches = build([*affected, "ollama-getting-started"], cfg)
            baseline, _ = build([*affected, "ollama-getting-started"], baseline_cfg)
        finally:
            os.chdir(old_cwd)

        def combinations(entries):
            return {(e["playbook"], e["platform"], e["arch"]) for e in entries}

        excluded = {(pb, os_name, "stx") for pb in affected
                    for os_name in ("linux", "windows")}
        self.assertEqual(combinations(matrix), combinations(baseline) - excluded)
        self.assertTrue(excluded <= combinations(baseline))
        for platform in ("linux", "windows"):
            self.assertEqual(batches[f"{platform}/stx"]["playbooks"],
                             ["ollama-getting-started"])
            self.assertEqual(batches[f"{platform}/krk+ram_64gb"]["playbooks"],
                             list(affected))


class OpenHandsProvisioning(unittest.TestCase):

    def test_windows_openhands_enables_wsl_without_installer_coordinates(self):
        """The Docker Desktop installer is the dependency's own business: this
        repository neither requires nor forwards its location."""
        cfg = {
            "provisioning": {
                "windows_install_scripts": [],
                "windows_driver": {"source": "driver", "copy": "direct"},
            },
            "extra_install_scripts": load_config()["extra_install_scripts"],
        }
        batch = {
            "platform": "windows",
            "arch": "halo",
            "playbooks": ["openhands-getting-started"],
        }
        builds, missing = trigger.make_builds(batch, cfg)
        self.assertEqual(missing, [])
        self.assertEqual(
            builds["install_scripts"],
            [{
                "script": "InstallationScripts/gfx/windows-wsl.ps1",
                "reboot_after": True,
            }],
        )
        self.assertEqual(builds["vars"], {"driver_source": "driver", "driver_copy": "direct"})

    def test_installer_repository_variables_are_not_read(self):
        cfg = {"pipeline": {}, "provisioning": {}}
        env = {
            "ORCHESTRAI_DOCKER_DESKTOP_INSTALLER_URL": "https://example.invalid/docker.exe",
            "ORCHESTRAI_DOCKER_DESKTOP_INSTALLER_SHA256": "b" * 64,
        }
        with mock.patch.dict(os.environ, env, clear=False):
            trigger.apply_env_overrides(cfg)
        self.assertFalse([k for k in cfg["provisioning"] if "docker" in k])

    def test_linux_openhands_does_not_run_windows_wsl_provisioning(self):
        cfg = {
            "device_families": {"stx": "ryzen_apu"},
            "provisioning": {
                "linux_install_scripts": [],
                "therock_url": "https://example.invalid/therock.tar.gz",
            },
            "extra_install_scripts": load_config()["extra_install_scripts"],
        }
        batch = {
            "platform": "linux",
            "arch": "stx",
            "playbooks": ["openhands-getting-started"],
        }
        builds, missing = trigger.make_builds(batch, cfg)
        self.assertEqual(missing, [])
        self.assertEqual(builds["install_scripts"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
