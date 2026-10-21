# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""Released Windows driver selection and fail-fast provisioning payloads."""

import contextlib
import copy
import io
import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

import yaml

GITHUB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GITHUB / "scripts"))
import orchestrai_trigger as trigger

PUBLIC_SCRIPT = "InstallationScripts/gfx/windows-public-url.ps1"
INTERNAL_SCRIPT = "InstallationScripts/gfx/windows.ps1"
URL = "https://example.invalid/approved-adrenalin.exe"


class WindowsDriverSelection(unittest.TestCase):
    def setUp(self):
        self.cfg = trigger.load_config(GITHUB / "orchestrai-config.yml")
        self.prov = self.cfg["provisioning"]
        self.batch = {"platform": "windows", "arch": "rx7900xt",
                      "tags": ["gpu_navi31xtx"], "playbooks": ["ollama-getting-started"]}

    def public(self):
        self.prov["windows_public_driver"]["url"] = URL
        return trigger.make_builds(self.batch, self.cfg)

    def test_repository_defaults_to_released_driver(self):
        self.assertEqual(trigger.windows_driver_choice(self.prov), "public")
        builds, missing = self.public()
        self.assertEqual(missing, [])
        self.assertEqual(builds["install_scripts"], [{"script": PUBLIC_SCRIPT, "reboot_after": True}])
        self.assertEqual(builds["vars"], {"driver_url": URL})

    def test_internal_source_cannot_leak_into_public_payload(self):
        self.prov["windows_driver"].update(source="internal-share", copy="direct")
        builds, missing = self.public()
        self.assertEqual(missing, [])
        self.assertNotIn("driver_source", builds["vars"])
        self.assertNotIn("driver_copy", builds["vars"])
        self.assertNotIn(INTERNAL_SCRIPT, [s["script"] for s in builds["install_scripts"]])

    def test_every_windows_device_uses_the_configured_public_installer(self):
        for device in ["halo", "halo_box", "stx", "krk", "rx7900xt", "rx9070xt", "r9700"]:
            with self.subTest(device=device):
                self.batch["arch"] = device
                builds, missing = self.public()
                self.assertEqual(missing, [])
                self.assertEqual(builds["vars"], {"driver_url": URL})
                self.assertEqual(builds["install_scripts"][0]["script"], PUBLIC_SCRIPT)

    def test_missing_public_url_does_not_fall_back_to_share(self):
        self.prov["windows_driver"]["source"] = "internal-share"
        _, missing = trigger.make_builds(self.batch, self.cfg)
        self.assertEqual(missing, ["ORCHESTRAI_WINDOWS_DRIVER_URL"])

    def test_bad_public_url_fails_preflight(self):
        for url in ["http://example.invalid/driver.exe", "file:///driver.exe", "https://",
                    "https://user:password@example.invalid/driver.exe", "https://example.invalid/a\nb.exe"]:
            with self.subTest(url=url):
                self.prov["windows_public_driver"]["url"] = url
                _, missing = trigger.make_builds(self.batch, self.cfg)
                self.assertTrue(any("ORCHESTRAI_WINDOWS_DRIVER_URL" in m for m in missing))

    def test_explicit_internal_override_preserves_existing_install(self):
        self.prov["windows_driver"].update(use="internal", source="internal-share")
        builds, missing = trigger.make_builds(self.batch, self.cfg)
        self.assertEqual(missing, [])
        self.assertEqual(builds["install_scripts"], [{"script": INTERNAL_SCRIPT, "reboot_after": True}])
        self.assertEqual(builds["vars"], {"driver_source": "internal-share", "driver_copy": "direct"})

    def test_internal_requires_source_but_not_public_url(self):
        self.prov["windows_driver"]["use"] = "internal"
        _, missing = trigger.make_builds(self.batch, self.cfg)
        self.assertEqual(missing, ["ORCHESTRAI_WINDOWS_DRIVER_SOURCE"])

    def test_env_choice_and_url_are_forwarded(self):
        with mock.patch.dict(os.environ, {"ORCHESTRAI_WINDOWS_DRIVER": " Public ",
                                         "ORCHESTRAI_WINDOWS_DRIVER_URL": URL}, clear=True):
            trigger.apply_env_overrides(self.cfg)
        builds, missing = trigger.make_builds(self.batch, self.cfg)
        self.assertEqual(missing, [])
        self.assertEqual(builds["vars"], {"driver_url": URL})

    def test_empty_env_preserves_repository_default(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            trigger.apply_env_overrides(self.cfg)
        self.assertEqual(trigger.windows_driver_choice(self.prov), "public")

    def test_unknown_choice_cannot_silently_use_internal(self):
        self.prov["windows_driver"]["use"] = "nightly"
        self.assertTrue(trigger.validate_config(self.cfg, {"windows/rx7900xt": self.batch}))
        _, missing = trigger.make_builds(self.batch, self.cfg)
        self.assertTrue(any("windows_driver.use" in m for m in missing))

    def test_validation_requires_only_selected_script_list(self):
        self.prov["windows_install_scripts"] = []
        self.assertEqual(trigger.validate_config(self.cfg, {"windows/rx7900xt": self.batch}), [])
        self.prov["windows_public_driver"]["install_scripts"] = []
        self.assertIn("provisioning.windows_public_driver.install_scripts",
                      trigger.validate_config(self.cfg, {"windows/rx7900xt": self.batch}))

    def test_linux_does_not_require_windows_driver(self):
        self.prov["windows_driver"]["use"] = "invalid"
        self.prov["therock_url"] = "https://example.invalid/linux.tar.gz"
        linux = dict(self.batch, platform="linux", arch="stx")
        self.assertEqual(trigger.validate_config(self.cfg, {"linux/stx": linux}), [])
        builds, missing = trigger.make_builds(linux, self.cfg)
        self.assertEqual(missing, [])
        self.assertNotIn("driver_url", builds["vars"])

    def test_therock_stays_after_driver_reboot_and_does_not_mutate_config(self):
        self.prov["windows_public_driver"]["url"] = URL
        self.prov["windows_therock_url"] = "https://example.invalid/windows.tar.gz"
        self.batch["playbooks"] = ["pytorch-finetuning", "unsloth-llms-finetuning"]
        before = copy.deepcopy(self.cfg)
        builds, missing = trigger.make_builds(self.batch, self.cfg)
        self.assertEqual(missing, [])
        self.assertEqual(builds["install_scripts"][0], {"script": PUBLIC_SCRIPT, "reboot_after": True})
        self.assertEqual([s["script"] for s in builds["install_scripts"]].count(trigger.WINDOWS_THEROCK_SCRIPT), 1)
        self.assertEqual(builds["vars"]["THEROCK_PUBLISH_ENV"], "0")
        self.assertEqual(self.cfg, before)

    def test_wsl_provisioning_remains_after_public_driver(self):
        self.batch["playbooks"] = ["openhands-getting-started"]
        builds, missing = self.public()
        self.assertEqual(missing, [])
        self.assertEqual([s["script"] for s in builds["install_scripts"]],
                         [PUBLIC_SCRIPT, "InstallationScripts/gfx/windows-wsl.ps1"])

    def test_missing_url_stops_main_before_any_submission(self):
        env = {"BATCHES_JSON": json.dumps({"windows/rx7900xt": self.batch}),
               "ORCHESTRAI_ROCM_MULTI_ARCH_INDEX_URL": "https://example.invalid/wheels"}
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch.object(sys, "argv", ["trigger", "--config", str(GITHUB / "orchestrai-config.yml")]), \
                mock.patch.object(trigger, "start_run") as submit, \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()), \
                self.assertRaises(SystemExit) as exited:
            trigger.main()
        self.assertEqual(exited.exception.code, 1)
        submit.assert_not_called()

    def test_both_entrypoints_forward_selector_and_url(self):
        for name in ["test-playbooks-orchestrai.yml", "orchestrai-pr-command.yml"]:
            workflow = yaml.load((GITHUB / "workflows" / name).read_text(), Loader=yaml.BaseLoader)
            trigger_steps = [s for s in workflow["jobs"]["detect-and-trigger" if name.startswith("test-") else "command"]["steps"]
                             if "orchestrai_trigger.py" in s.get("run", "")]
            self.assertEqual(len(trigger_steps), 1)
            env = trigger_steps[0]["env"]
            self.assertIn("ORCHESTRAI_WINDOWS_DRIVER", env)
            self.assertEqual(env["ORCHESTRAI_WINDOWS_DRIVER_URL"], "${{ vars.ORCHESTRAI_WINDOWS_DRIVER_URL }}")

    def test_manual_override_defaults_to_repository_policy(self):
        workflow = yaml.load((GITHUB / "workflows/test-playbooks-orchestrai.yml").read_text(), Loader=yaml.BaseLoader)
        field = workflow["on"]["workflow_dispatch"]["inputs"]["windows_driver"]
        self.assertEqual(field["default"], "default")
        self.assertEqual(field["options"], ["default", "public", "internal"])


if __name__ == "__main__":
    unittest.main()
