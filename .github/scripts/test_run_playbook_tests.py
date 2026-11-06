#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
Regression tests for run_playbook_tests.py setup resolution.

Guards issue #677: a @setup defined only under one @os block must not emit
"Setup '...' has no command for platform '...'" warnings when building the
other platform's view. setup= is resolved only for tests that survive
platform/device filtering, so a filtered-out test never triggers the warning.
"""

import contextlib
import importlib.util
import io
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

_SPEC = importlib.util.spec_from_file_location(
    "run_playbook_tests", Path(__file__).with_name("run_playbook_tests.py")
)
rpt = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(rpt)

# activate-venv is defined only inside @os:linux and referenced only by the
# Linux test; the Windows test uses no setup. This mirrors comfyui-image-gen.
FIXTURE = """\
<!-- @os:linux -->
<!-- @setup:id=activate-venv command="source venv/bin/activate" -->
<!-- @test:id=deps-linux timeout=60 setup=activate-venv -->
```bash
echo linux
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=deps-windows timeout=60 -->
```powershell
echo windows
```
<!-- @test:end -->
<!-- @os:end -->
"""

WARNING_SUBSTR = "has no command for platform"


def _extract(view):
    """Return (test_list, stdout) for extracting the fixture for `view`."""
    with tempfile.TemporaryDirectory() as d:
        readme = Path(d) / "README.md"
        readme.write_text(FIXTURE, encoding="utf-8")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            tests = rpt.extract_tests(readme, view)
    return tests, buf.getvalue()


class SetupResolutionTest(unittest.TestCase):
    def test_windows_view_has_no_setup_warning_for_linux_only_setup(self):
        tests, out = _extract("windows")
        self.assertNotIn(WARNING_SUBSTR, out, "spurious setup warning on Windows view (#677)")
        self.assertEqual([t.id for t in tests], ["deps-windows"])
        self.assertIsNone(tests[0].setup)

    def test_linux_view_still_resolves_setup(self):
        tests, out = _extract("linux")
        self.assertNotIn(WARNING_SUBSTR, out)
        self.assertEqual([t.id for t in tests], ["deps-linux"])
        self.assertEqual(tests[0].setup, "source venv/bin/activate")


class TimeoutOutputTest(unittest.TestCase):
    def test_a_timed_out_test_keeps_what_it_printed(self):
        test = rpt.TestBlock(id="hangs", timeout=1, code="echo waiting for the lock\nsleep 5")
        with tempfile.TemporaryDirectory() as d:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                result = rpt.run_test(test, Path(d), Path(d))
            saved = (Path(d) / "hangs_stdout.txt").read_text(encoding="utf-8")
        self.assertEqual((result.success, result.error_message), (False, "Test timed out after 1 seconds"))
        self.assertIn("waiting for the lock", result.stdout)
        self.assertIn("waiting for the lock", saved)
        self.assertIn("waiting for the lock", buf.getvalue())

    @unittest.skipIf(os.name == "nt", "bash step")
    def test_a_timeout_kills_the_child_holding_the_output(self):
        with tempfile.TemporaryDirectory() as d:
            pidfile = Path(d) / "pid"
            script = f"sleep 60 & echo $! > {pidfile}; wait"
            start = time.monotonic()
            with mock.patch.object(rpt.os, "isatty", return_value=False):  # as in CI
                _, timed_out, _, _ = rpt.run_step_command(["bash", "-c", script], d, 1, dict(os.environ))
            self.assertLess(time.monotonic() - start, 10)
            self.assertTrue(timed_out)
            with self.assertRaises(ProcessLookupError):
                os.kill(int(pidfile.read_text()), 0)


if __name__ == "__main__":
    unittest.main()
