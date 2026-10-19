#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""A step's timeout is a hard limit and kills everything the step started.

subprocess.run(capture_output=True, timeout=...) killed only the shell, then on
Windows waited with no limit for the output pipes its children (pip, python)
still held: 300s steps ran 1,857s. On Linux it returned but left the children
running into the next step. These run real processes (POSIX shells here; the
Windows path is the same code with taskkill /T).
"""

import importlib.util
import os
import signal
import sys
import tempfile
import time
import unittest
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "run_playbook_tests", Path(__file__).with_name("run_playbook_tests.py")
)
rpt = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(rpt)


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


@unittest.skipIf(os.name == "nt", "POSIX shells; Windows uses taskkill /T")
class TimeoutKillsTheTree(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.pidfile = self.tmp / "child.pid"

    def tearDown(self):
        if self.pidfile.exists():
            pid = int(self.pidfile.read_text())
            if _alive(pid):
                os.kill(pid, signal.SIGKILL)

    def test_a_child_holding_the_output_does_not_extend_the_timeout(self):
        # The pip-install case: the shell's child keeps running and keeps the
        # step's stdout open.
        script = f"echo starting; sleep 60 & echo $! > {self.pidfile}; wait"
        start = time.monotonic()
        run = rpt.run_step_command(["bash", "-c", script], self.tmp, 2, dict(os.environ))
        elapsed = time.monotonic() - start
        self.assertTrue(run["timed_out"])
        self.assertIsNone(run["returncode"])
        self.assertLess(elapsed, 2 + rpt.TIMEOUT_KILL_GRACE_SECONDS)
        time.sleep(0.2)
        self.assertFalse(_alive(int(self.pidfile.read_text())), "the step's child survived the timeout")
        self.assertIn("starting", run["stdout"])  # output before the kill is kept

    def test_a_passing_step_keeps_the_server_it_started(self):
        # Steps start servers in the background for later steps; a normal exit
        # must not kill them.
        script = f"sleep 60 >/dev/null 2>&1 & echo $! > {self.pidfile}; echo up"
        run = rpt.run_step_command(["bash", "-c", script], self.tmp, 10, dict(os.environ))
        self.assertFalse(run["timed_out"])
        self.assertEqual(run["returncode"], 0)
        self.assertEqual(run["stdout"].strip(), "up")
        self.assertTrue(_alive(int(self.pidfile.read_text())))

    def test_exit_code_and_stderr_of_a_normal_step(self):
        run = rpt.run_step_command(["bash", "-c", "echo out; echo err >&2; exit 3"], self.tmp, 10, dict(os.environ))
        self.assertEqual((run["returncode"], run["stdout"], run["stderr"]), (3, "out\n", "err\n"))
        self.assertEqual(run["terminate"], 0.0)

    def test_run_test_reports_the_timeout_with_partial_output_and_timings(self):
        test = rpt.TestBlock(id="slow", language="bash", platform="linux",
                                code=f"echo before; sleep 60 & echo $! > {self.pidfile}; wait",
                                timeout=2)
        start = time.monotonic()
        result = rpt.run_test(test, self.tmp, self.tmp)
        self.assertLess(time.monotonic() - start, 2 + rpt.TIMEOUT_KILL_GRACE_SECONDS)
        self.assertTrue(result.timed_out)
        self.assertFalse(result.success)
        self.assertIn("before", result.stdout)
        self.assertGreaterEqual(result.terminate_seconds, 0.0)


if __name__ == "__main__":
    unittest.main()
