#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
Regression tests for prereq_validate.py.

Covers:
- @require scoping across @os:/@device: blocks (including the @os:end vs
  @os:<name> parsing hazard that would otherwise swallow requires after an
  end tag).
- The validate -> install -> re-validate loop's five outcomes: OK, INSTALLED,
  FAILED, MISSING_NO_INSTALL, unchecked.
"""

import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "prereq_validate", Path(__file__).with_name("prereq_validate.py")
)
pv = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(pv)

# Mirrors the shape of n8n-automation-gpt-oss: an @os-scoped require, a
# device-scoped model require, and requires that follow an @os:end tag.
FIXTURE = """\
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @require:lemonade,podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @require:lemonade-models-gpt-oss-120b -->
<!-- @device:end -->
"""


class ScopingTests(unittest.TestCase):
    def test_linux_halo_includes_model_after_os_end(self):
        # The model require sits after an @os:end tag; it must not be swallowed.
        deps = pv.extract_scoped_requires(FIXTURE, "linux", "halo")
        self.assertEqual(deps, ["lemonade", "podman", "lemonade-models-gpt-oss-120b"])

    def test_windows_halo_uses_windows_os_block(self):
        deps = pv.extract_scoped_requires(FIXTURE, "windows", "halo")
        self.assertEqual(deps, ["lemonade", "nodejs", "lemonade-models-gpt-oss-120b"])

    def test_non_halo_device_excludes_model(self):
        deps = pv.extract_scoped_requires(FIXTURE, "linux", "stx")
        self.assertNotIn("lemonade-models-gpt-oss-120b", deps)
        self.assertIn("podman", deps)

    def test_driver_only_for_its_devices(self):
        self.assertIn("driver", pv.extract_scoped_requires(FIXTURE, "linux", "r9700"))
        self.assertNotIn("driver", pv.extract_scoped_requires(FIXTURE, "linux", "halo"))


class LoopTests(unittest.TestCase):
    def test_ok_when_validate_passes(self):
        spec = {"validate": {"linux": {"cmd": "true", "expect_rc": 0}}}
        r = pv.check_dependency("d", spec, "linux")
        self.assertEqual(r["status"], "OK")
        self.assertFalse(r["install_ran"])

    def test_installed_when_install_heals(self):
        flag = tempfile.mktemp()
        try:
            spec = {
                "validate": {"linux": {"cmd": f"test -f {flag}", "expect_rc": 0}},
                "install": {"linux": {"cmd": f"touch {flag}", "timeout": 5}},
            }
            r = pv.check_dependency("d", spec, "linux")
            self.assertEqual(r["status"], "INSTALLED")
            self.assertTrue(r["install_ran"])
        finally:
            if os.path.exists(flag):
                os.remove(flag)

    def test_failed_when_install_does_not_heal(self):
        spec = {
            "validate": {"linux": {"cmd": "false", "expect_rc": 0}},
            "install": {"linux": {"cmd": "true", "timeout": 5}},
        }
        self.assertEqual(pv.check_dependency("d", spec, "linux")["status"], "FAILED")

    def test_missing_no_install(self):
        spec = {"validate": {"linux": {"cmd": "false", "expect_rc": 0}}}
        self.assertEqual(
            pv.check_dependency("d", spec, "linux")["status"], "MISSING_NO_INSTALL"
        )

    def test_optional_miss_warns_not_fails(self):
        # An optional dep whose validate fails and has no install must not be a
        # hard failure (status not in the unresolved set).
        spec = {"optional": True, "validate": {"linux": {"cmd": "false", "expect_rc": 0}}}
        self.assertEqual(
            pv.check_dependency("d", spec, "linux")["status"], "MISSING_OPTIONAL"
        )

    def test_unchecked_when_no_validate_for_platform(self):
        spec = {"validate": {"windows": {"cmd": "true", "expect_rc": 0}}}
        self.assertEqual(pv.check_dependency("d", spec, "linux")["status"], "unchecked")


if __name__ == "__main__":
    unittest.main()
