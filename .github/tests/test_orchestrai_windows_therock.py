# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""Windows TheRock (for hipInfo) is scoped to the Radeon ML batches."""

import os
import sys
import unittest
from pathlib import Path
from unittest import mock

import yaml

GITHUB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GITHUB / "scripts"))
import orchestrai_trigger as trigger

DRIVER = {"script": "InstallationScripts/gfx/windows.ps1", "reboot_after": True}
THEROCK = {"script": "InstallationScripts/gfx/windows-therock-tarball.ps1", "reboot_after": False}
SCOPED = ["llama-factory-finetuning", "pytorch-finetuning",
          "pytorch-rocm-llms", "unsloth-llms-finetuning"]


class WindowsTheRockProvisioning(unittest.TestCase):
    def setUp(self):
        self.cfg = trigger.load_config(GITHUB / "orchestrai-config.yml")
        self.cfg["provisioning"]["windows_driver"]["source"] = "driver"
        self.cfg["provisioning"]["therock_url"] = "https://example.invalid/linux.tar.gz"
        self.cfg["provisioning"]["windows_therock_url"] = "https://example.invalid/windows.tar.gz"

    def make(self, platform="windows", arch="rx7900xt", playbooks=SCOPED[:1]):
        batch = {"platform": platform, "arch": arch, "playbooks": list(playbooks)}
        return trigger.make_builds(batch, self.cfg)

    def builds(self, **batch):
        builds, missing = self.make(**batch)
        self.assertEqual(missing, [])
        return builds

    def test_scoped_playbooks_install_therock_after_the_driver_reboot(self):
        for device in ("rx7900xt", "rx9070xt", "r9700"):
            for playbook in SCOPED:
                with self.subTest(device=device, playbook=playbook):
                    builds = self.builds(arch=device, playbooks=[playbook])
                    self.assertEqual(builds["install_scripts"], [DRIVER, THEROCK])
                    self.assertEqual(builds["vars"]["THEROCK_URL"],
                                     "https://example.invalid/windows.tar.gz")
                    self.assertEqual(builds["vars"]["THEROCK_PUBLISH_ENV"], "0")

    def test_unset_url_is_reported_before_acquiring_hardware(self):
        self.cfg["provisioning"]["windows_therock_url"] = ""
        _, missing = self.make()
        self.assertEqual(missing, ["ORCHESTRAI_WINDOWS_THEROCK_URL"])

    def test_unset_url_is_not_required_where_therock_is_not_scheduled(self):
        self.cfg["provisioning"]["windows_therock_url"] = ""
        self.builds(arch="stx")
        self.builds(playbooks=["ollama-getting-started"])

    def test_apus_and_other_playbooks_do_not_install_therock(self):
        for device, playbook in (("halo", "unsloth-llms-finetuning"),
                                 ("stx", "llama-factory-finetuning"),
                                 ("krk", "pytorch-finetuning"),
                                 ("rx7900xt", "ollama-getting-started")):
            with self.subTest(device=device, playbook=playbook):
                builds = self.builds(arch=device, playbooks=[playbook])
                self.assertNotIn(THEROCK, builds["install_scripts"])
                self.assertNotIn("THEROCK_URL", builds["vars"])
                self.assertNotIn("THEROCK_PUBLISH_ENV", builds["vars"])

    def test_mixed_batch_installs_therock_once(self):
        builds = self.builds(playbooks=SCOPED + ["ollama-getting-started"])
        self.assertEqual(builds["install_scripts"].count(THEROCK), 1)

    def test_linux_keeps_its_own_tarball(self):
        builds = self.builds(platform="linux", arch="stx", playbooks=SCOPED)
        self.assertNotIn(THEROCK, builds["install_scripts"])
        self.assertEqual(builds["vars"]["THEROCK_URL"], "https://example.invalid/linux.tar.gz")

    def test_repository_variable_sets_the_windows_url_only(self):
        env = {"ORCHESTRAI_WINDOWS_THEROCK_URL": "https://example.invalid/from-var.tar.gz"}
        with mock.patch.dict(os.environ, env, clear=True):
            trigger.apply_env_overrides(self.cfg)
        self.assertEqual(self.builds()["vars"]["THEROCK_URL"], env["ORCHESTRAI_WINDOWS_THEROCK_URL"])
        self.assertEqual(self.cfg["provisioning"]["therock_url"], "https://example.invalid/linux.tar.gz")

    def test_both_workflow_entrypoints_forward_the_url(self):
        for name in ("test-playbooks-orchestrai.yml", "orchestrai-pr-command.yml"):
            workflow = yaml.safe_load((GITHUB / "workflows" / name).read_text())
            steps = [step for job in workflow["jobs"].values() for step in job.get("steps", [])
                     if "orchestrai_trigger.py" in step.get("run", "")]
            self.assertTrue(steps, name)
            for step in steps:
                self.assertEqual(step["env"]["ORCHESTRAI_WINDOWS_THEROCK_URL"],
                                 "${{ vars.ORCHESTRAI_WINDOWS_THEROCK_URL }}")


if __name__ == "__main__":
    unittest.main()
