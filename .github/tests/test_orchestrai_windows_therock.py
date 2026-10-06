# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""Windows SDK provisioning is opt-in, scoped and platform-specific."""

import copy
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

import yaml

GITHUB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GITHUB / "scripts"))
import orchestrai_trigger as trigger


class WindowsTheRockProvisioning(unittest.TestCase):
    def setUp(self):
        self.cfg = trigger.load_config(GITHUB / "orchestrai-config.yml")
        self.cfg["provisioning"]["windows_driver"]["source"] = "driver"
        self.cfg["provisioning"]["therock_url"] = "https://example.invalid/linux.tar.gz"
        self.source = self.cfg["provisioning"]["windows_therock"]
        self.batch = {"platform": "windows", "arch": "rx7900xt",
                      "playbooks": ["llama-factory-finetuning"]}

    def builds(self):
        return trigger.make_builds(self.batch, self.cfg)

    def test_unset_source_preserves_existing_windows_provisioning(self):
        builds, missing = self.builds()
        self.assertEqual(missing, [])
        self.assertEqual(builds["install_scripts"],
                         self.cfg["provisioning"]["windows_install_scripts"])
        self.assertEqual(builds["vars"], {"driver_source": "driver", "driver_copy": "direct"})

    def test_windows_tarball_is_separate_and_follows_driver_reboot(self):
        self.source["url"] = "https://example.invalid/windows.tar.gz"
        original = copy.deepcopy(self.cfg)
        builds, missing = self.builds()
        self.assertEqual(missing, [])
        self.assertEqual(builds["vars"]["THEROCK_URL"], self.source["url"])
        self.assertEqual(builds["install_scripts"], [
            {"script": "InstallationScripts/gfx/windows.ps1", "reboot_after": True},
            {"script": "InstallationScripts/gfx/windows-therock-tarball.ps1", "reboot_after": False},
        ])
        self.assertEqual(self.cfg, original)

    def test_artifacts_have_device_family_and_pinned_source(self):
        self.source.update(run_id="123456", run_repo="ROCm/rocm-systems", ref="pinned-installer")
        for device, family in (("rx7900xt", "gfx110X-all"),
                               ("rx9070xt", "gfx120X-all"), ("r9700", "gfx120X-all")):
            with self.subTest(device=device):
                self.batch["arch"] = device
                builds, missing = self.builds()
                self.assertEqual(missing, [])
                self.assertEqual(builds["vars"]["THEROCK_AMDGPU_FAMILY"], family)
                self.assertEqual(builds["vars"]["THEROCK_RUN_ID"], "123456")
                self.assertEqual(builds["vars"]["THEROCK_RUN_REPO"], "ROCm/rocm-systems")
                self.assertEqual(builds["vars"]["THEROCK_REF"], "pinned-installer")
                self.assertNotIn("THEROCK_URL", builds["vars"])

    def test_other_playbooks_and_apus_are_unchanged(self):
        self.source["url"] = "https://example.invalid/windows.tar.gz"
        for device, playbook in (("halo", "unsloth-llms-finetuning"),
                                 ("stx", "llama-factory-finetuning"),
                                 ("krk", "pytorch-finetuning"),
                                 ("rx7900xt", "ollama-getting-started")):
            with self.subTest(device=device, playbook=playbook):
                self.batch.update(arch=device, playbooks=[playbook])
                builds, missing = self.builds()
                self.assertEqual(missing, [])
                self.assertNotIn("THEROCK_URL", builds["vars"])

    def test_mixed_batch_installs_sdk_only_once(self):
        self.source["url"] = "https://example.invalid/windows.tar.gz"
        self.batch["playbooks"] = self.source["playbooks"] + ["ollama-getting-started"]
        builds, missing = self.builds()
        self.assertEqual(missing, [])
        paths = [entry["script"] for entry in builds["install_scripts"]]
        self.assertEqual(paths.count("InstallationScripts/gfx/windows-therock-tarball.ps1"), 1)

    def test_linux_keeps_its_own_tarball(self):
        self.source["url"] = "https://example.invalid/windows.tar.gz"
        self.batch.update(platform="linux", arch="stx", playbooks=["gaia-agents"])
        builds, missing = self.builds()
        self.assertEqual(missing, [])
        self.assertEqual(builds["vars"]["THEROCK_URL"], self.cfg["provisioning"]["therock_url"])
        self.assertEqual(builds["install_scripts"], self.cfg["provisioning"]["linux_install_scripts"])

    def test_bad_configured_sources_fail_before_provisioning(self):
        cases = [
            {"url": "https://example.invalid/windows.tar.gz", "run_id": "123"},
            {"url": "https://example.invalid/linux.tar.gz"},
            {"url": "not-a-url"},
            {"url": "https://example.invalid/windows archive.tar.gz"},
            {"url": "https://example.invalid/windows\narchive.tar.gz"},
            {"url": "https://[malformed/windows.tar.gz"},
            {"url": "https://user:password@example.invalid/windows.tar.gz"},
            {"run_id": "123"},
            {"run_id": "0", "run_repo": "ROCm/rocm-systems"},
            {"run_id": "123", "run_repo": "missing-owner"},
            {"run_repo": "ROCm/rocm-systems"},
            {"url": "https://example.invalid/windows.tar.gz", "ref": "main"},
        ]
        for values in cases:
            with self.subTest(values=values):
                source = dict(self.source, **values)
                self.cfg["provisioning"]["windows_therock"] = source
                builds, missing = self.builds()
                self.assertTrue(missing)
                self.assertEqual(builds["install_scripts"], self.cfg["provisioning"]["windows_install_scripts"])

    def test_artifact_mode_rejects_unknown_device_architecture(self):
        self.source.update(run_id="123", run_repo="ROCm/rocm-systems")
        del self.cfg["device_to_gfx"]["rx7900xt"]
        _, missing = self.builds()
        self.assertTrue(any("device_to_gfx.rx7900xt" in error for error in missing))

    def test_repository_overrides_do_not_forward_tokens(self):
        env = {f"ORCHESTRAI_WINDOWS_THEROCK_{key.upper()}": value for key, value in
               {"run_id": "123", "run_repo": "ROCm/rocm-systems", "ref": "pinned"}.items()}
        env["GITHUB_TOKEN"] = "must-not-be-serialized"
        with mock.patch.dict(os.environ, env, clear=True):
            trigger.apply_env_overrides(self.cfg)
            builds, missing = self.builds()
        self.assertEqual(missing, [])
        self.assertNotIn("GITHUB_TOKEN", builds["vars"])
        self.assertEqual(builds["vars"]["THEROCK_RUN_ID"], "123")

    def test_both_workflow_entrypoints_forward_source_variables(self):
        for name in ("test-playbooks-orchestrai.yml", "orchestrai-pr-command.yml"):
            workflow = yaml.safe_load((GITHUB / "workflows" / name).read_text())
            steps = [step for job in workflow["jobs"].values() for step in job.get("steps", [])
                     if "orchestrai_trigger.py" in step.get("run", "")]
            self.assertTrue(steps, name)
            for step in steps:
                for key in ("URL", "RUN_ID", "RUN_REPO", "REF"):
                    variable = f"ORCHESTRAI_WINDOWS_THEROCK_{key}"
                    self.assertEqual(step["env"][variable], "${{ vars." + variable + " }}")


if __name__ == "__main__":
    unittest.main()
