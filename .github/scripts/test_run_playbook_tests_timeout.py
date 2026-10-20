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
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock
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
        shutil.rmtree(self.tmp, ignore_errors=True)

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

    def test_progress_bar_carriage_returns_become_lines(self):
        run = rpt.run_step_command(["bash", "-c", r"printf '10%%\r20%%\r\n'"], self.tmp, 10, dict(os.environ))
        self.assertEqual(run["stdout"], "10%\n20%\n")

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
        self.assertLess(result.terminate_seconds, rpt.TIMEOUT_KILL_GRACE_SECONDS)

    def _stop_runner_during(self, step: str) -> int:
        """Run step in a runner, SIGTERM the runner once the step wrote its pid file,
        and return the runner's exit code."""
        runner = subprocess.Popen([sys.executable, "-c", (
            "import importlib.util, os, signal, sys\n"
            f"spec = importlib.util.spec_from_file_location('r', {str(Path(rpt.__file__))!r})\n"
            "r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)\n"
            "signal.signal(signal.SIGTERM, lambda *_: sys.exit(128 + signal.SIGTERM))\n"
            f"r.run_step_command(['bash', '-c', {step!r}], {str(self.tmp)!r}, 60, dict(os.environ))\n"
        )])
        self.addCleanup(lambda: runner.poll() is None and runner.kill())
        deadline = time.monotonic() + 10
        while not (self.pidfile.exists() and self.pidfile.read_text().strip()):
            self.assertLess(time.monotonic(), deadline, "the step never started")
            time.sleep(0.05)
        runner.send_signal(signal.SIGTERM)
        return runner.wait(timeout=30)

    def test_a_stopped_runner_lets_the_step_clean_up_then_kills_its_tree(self):
        # SIGTERM to the runner alone (docker stop): the step gets SIGTERM and time
        # to clean up, and nothing it started outlives the runner.
        marker = self.tmp / "cleaned"
        step = f"trap 'echo yes > {marker}; exit' TERM; sleep 60 & echo $! > {self.pidfile}; wait"
        self.assertEqual(self._stop_runner_during(step), 128 + signal.SIGTERM)
        self.assertEqual(marker.read_text().strip(), "yes")
        time.sleep(0.2)
        self.assertFalse(_alive(int(self.pidfile.read_text())), "the step's child outlived the runner")

    def test_a_stopped_runner_gives_the_steps_children_time_to_clean_up(self):
        # The usual step: the shell has no TERM trap and dies at once, but its child
        # (apt, dpkg) still gets the grace to clean up.
        marker = self.tmp / "cleaned"
        child = (
            "import os, signal, sys, time\n"
            "signal.signal(signal.SIGTERM, lambda *_: (time.sleep(1),"
            f" open({str(marker)!r}, 'w').write('yes'), sys.exit()))\n"
            f"open({str(self.pidfile)!r}, 'w').write(str(os.getpid()))\n"
            "time.sleep(60)\n"
        )
        step = f"{shlex.quote(sys.executable)} -c {shlex.quote(child)}; echo done"
        self.assertEqual(self._stop_runner_during(step), 128 + signal.SIGTERM)
        self.assertEqual(marker.read_text(), "yes")


@unittest.skipIf(os.name == "nt", "POSIX signals; Windows uses taskkill /T")
class SignalTree(unittest.TestCase):
    def test_a_reaped_steps_reused_pid_is_not_followed(self):
        # The step exited and was reaped; another process now has its pid.
        proc = mock.Mock(pid=111, returncode=0)
        now = {111: (1, "b"), 112: (111, "b")}
        with mock.patch.object(rpt, "_process_table", return_value=now), \
                mock.patch.object(rpt.os, "kill") as kill:
            rpt._signal_tree(proc, {}, signal.SIGKILL)
        kill.assert_not_called()

    def test_root_processes_are_killed_with_sudo_unless_their_pid_was_reused(self):
        proc = mock.Mock()
        tree = {111: "Mon Oct 19 10:00:00 2026", 222: "Mon Oct 19 10:00:00 2026"}
        now = {111: (1, "Mon Oct 19 10:00:00 2026"), 222: (1, "Mon Oct 19 10:00:05 2026")}
        with mock.patch.object(rpt, "_process_table", return_value=now), \
                mock.patch.object(rpt.os, "kill", side_effect=PermissionError), \
                mock.patch.object(rpt.subprocess, "run") as run:
            rpt._signal_tree(proc, tree, signal.SIGKILL)
        proc.send_signal.assert_called_once_with(signal.SIGKILL)
        # 222's start time changed: a different process now has that pid.
        self.assertEqual(run.call_args.args[0], ["sudo", "-n", "kill", "-KILL", "111"])

    def test_descendants_follow_the_whole_tree(self):
        table = {10: (1, "a"), 11: (10, "a"), 12: (11, "a"), 20: (1, "a")}
        self.assertEqual(sorted(rpt._descendants([10], table)), [11, 12])


if __name__ == "__main__":
    unittest.main()
