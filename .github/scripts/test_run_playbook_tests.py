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
import shutil
import subprocess
import sys
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

    def test_a_multi_line_setup_is_refused(self):
        """The bash wrapper checks only a setup's final status, so a setup is one line."""
        fixture = FIXTURE.replace('command="source venv/bin/activate"',
                                  'command="[ -d venv ] && source venv/bin/activate\nexport X=1"')
        with tempfile.TemporaryDirectory() as d:
            readme = Path(d) / "README.md"
            readme.write_text(fixture, encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()), \
                    self.assertRaisesRegex(ValueError, "deps-linux.*one line"):
                rpt.extract_tests(readme, "linux")


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


@unittest.skipIf(sys.platform == "win32", "bash test")
class SetupFailureTest(unittest.TestCase):
    def run_block(self, setup, language="bash", code="echo test body ran"):
        test = rpt.TestBlock(id="uses-venv", timeout=30, setup=setup, language=language, code=code)
        with tempfile.TemporaryDirectory() as d, contextlib.redirect_stdout(io.StringIO()):
            return rpt.run_test(test, Path(d), Path(d))

    def test_a_failed_setup_stops_the_test(self):
        """A venv that a skipped step never created must not fall back to system Python."""
        result = self.run_block("source missing-env/bin/activate")
        self.assertFalse(result.success)
        self.assertNotIn("test body ran", result.stdout)
        self.assertIn("setup failed", result.stderr)

    def test_an_early_failure_in_a_multi_command_setup_stops_the_test(self):
        result = self.run_block("false; export SETUP_OK=1")
        self.assertFalse(result.success)
        self.assertNotIn("test body ran", result.stdout)

    def test_a_failed_guard_in_a_setup_stops_the_test(self):
        """set -e ignores a failure before the last command of an && list."""
        result = self.run_block("[ -d missing-env ] && source missing-env/bin/activate")
        self.assertFalse(result.success)
        self.assertNotIn("test body ran", result.stdout)
        self.assertIn("setup failed", result.stderr)

    def test_a_failing_command_in_a_setup_pipeline_stops_the_test(self):
        result = self.run_block("false | cat")
        self.assertFalse(result.success)
        self.assertNotIn("test body ran", result.stdout)

    def test_a_failed_setup_stops_python_and_unknown_language_tests(self):
        for language, code in (("python", "print('test body ran')"), ("console", "echo test body ran")):
            with self.subTest(language=language):
                result = self.run_block("false; true", language, code)
                self.assertFalse(result.success)
                self.assertNotIn("test body ran", result.stdout)
                self.assertIn("setup failed", result.stderr)

    def test_a_real_venv_activation_passes_under_set_e(self):
        """Every bash setup in the playbooks is `source <venv>/bin/activate`."""
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "assets").mkdir()  # tests run in the playbook's assets folder
            subprocess.run([sys.executable, "-m", "venv", "env"], cwd=Path(d) / "assets", check=True)
            test = rpt.TestBlock(id="uses-venv", timeout=30, setup="source env/bin/activate",
                                 code='echo "test body ran in $VIRTUAL_ENV"')
            with contextlib.redirect_stdout(io.StringIO()):
                result = rpt.run_test(test, Path(d), Path(d))
        self.assertTrue(result.success, result.stderr)
        self.assertIn("test body ran in ", result.stdout)
        self.assertIn("env", result.stdout.split("test body ran in ", 1)[1])

    def test_a_working_setup_still_runs_the_test(self):
        result = self.run_block("export SETUP_OK=1", code='false; echo "test body ran $SETUP_OK"')
        self.assertTrue(result.success, result.stderr)  # set -e does not leak into the body
        self.assertIn("test body ran 1", result.stdout)


POWERSHELL = shutil.which("powershell") or shutil.which("pwsh")


@unittest.skipUnless(POWERSHELL, "needs powershell or pwsh")
class PowerShellSetupFailureTest(unittest.TestCase):
    BODY = "Get-Item missing-file 2>$null; Write-Output \"test body ran $env:VIRTUAL_ENV\""
    NATIVE_FAIL = "cmd /c exit 3" if sys.platform == "win32" else "sh -c 'exit 3'"
    NATIVE_STDERR_OK = 'cmd /c "echo harmless 1>&2"' if sys.platform == "win32" else "sh -c 'echo harmless >&2'"

    def run_setup(self, setup, cwd, *flags, before=""):
        script = before + rpt.powershell_with_setup(setup, self.BODY)
        return subprocess.run([POWERSHELL, "-NoProfile", *flags, "-Command", script],
                              cwd=cwd, capture_output=True, text=True, timeout=60)

    def make_venv(self, d):
        subprocess.run([sys.executable, "-m", "venv", "env"], cwd=d, check=True)
        return str(Path("env", "Scripts" if sys.platform == "win32" else "bin", "Activate.ps1"))

    def test_a_working_activation_runs_the_body_in_the_venv(self):
        with tempfile.TemporaryDirectory() as d:
            proc = self.run_setup(self.make_venv(d), d)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("test body ran", proc.stdout)  # the body's own errors do not stop it
        self.assertIn("env", proc.stdout.split("test body ran", 1)[1])

    def test_a_failed_setup_stops_the_test(self):
        for setup in ("missing-env\\Scripts\\activate", self.NATIVE_FAIL,
                      f"{self.NATIVE_FAIL}; $env:SETUP_OK = '1'",
                      "Get-Item missing-file; $env:SETUP_OK = '1'"):
            with self.subTest(setup=setup), tempfile.TemporaryDirectory() as d:
                proc = self.run_setup(setup, d)
                self.assertNotEqual(proc.returncode, 0)
                self.assertNotIn("test body ran", proc.stdout)
                self.assertIn("setup failed", proc.stderr)

    def test_the_setup_error_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            proc = self.run_setup("Get-Item \"it's-missing\"", d)  # quotes must not break the script
        self.assertIn("setup failed: ", proc.stderr)
        self.assertIn("it's-missing", proc.stderr)

    def test_a_native_command_writing_to_stderr_but_succeeding_passes(self):
        """Windows PowerShell 5.1 may turn native stderr into an error record under Stop."""
        with tempfile.TemporaryDirectory() as d:
            proc = self.run_setup(self.NATIVE_STDERR_OK, d)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("test body ran", proc.stdout)

    def test_an_earlier_native_exit_code_does_not_fail_the_setup(self):
        """A profile or earlier command can leave $LASTEXITCODE nonzero."""
        with tempfile.TemporaryDirectory() as d:
            proc = self.run_setup("$env:SETUP_OK = '1'", d, before=f"{self.NATIVE_FAIL}\n")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("test body ran", proc.stdout)

    @unittest.skipUnless(sys.platform == "win32", "run_test uses powershell.exe on Windows only")
    def test_run_test_stops_a_powershell_test_whose_setup_fails(self):
        """The production invocation: powershell -Command, with the profile loaded."""
        for setup, ok in (("$env:SETUP_OK = '1'", True), ("missing-env\\Scripts\\activate", False)):
            with self.subTest(setup=setup), tempfile.TemporaryDirectory() as d, \
                    contextlib.redirect_stdout(io.StringIO()):
                test = rpt.TestBlock(id="ps-setup", timeout=60, setup=setup, language="powershell",
                                     code="Write-Output 'test body ran'")
                result = rpt.run_test(test, Path(d), Path(d))
            self.assertEqual(result.success, ok, result.stderr)
            self.assertEqual("test body ran" in result.stdout, ok)

    @unittest.skipUnless(sys.platform == "win32", "execution policy is enforced on Windows only")
    def test_an_activation_blocked_by_execution_policy_stops_the_test(self):
        with tempfile.TemporaryDirectory() as d:
            proc = self.run_setup(self.make_venv(d), d, "-ExecutionPolicy", "Restricted")
        self.assertNotEqual(proc.returncode, 0)
        self.assertNotIn("test body ran", proc.stdout)


if __name__ == "__main__":
    unittest.main()
