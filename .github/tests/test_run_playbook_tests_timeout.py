#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
Regression test for the per-test timeout in run_playbook_tests.py.

A test's shell can start a grandchild (pip, a server) that inherits the output
pipes. subprocess.run(timeout=...) killed only the shell and then waited for the
pipes to close, so a 300s test ran until pip finished on its own, and pip kept
running into the next test. run_with_tree_timeout must return at the timeout and
leave nothing behind.

Usage:
    python3 .github/tests/test_run_playbook_tests_timeout.py
"""

import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_playbook_tests  # noqa: E402


def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


@unittest.skipIf(os.name == "nt", "POSIX shell test; Windows uses taskkill /T")
class TreeTimeout(unittest.TestCase):
    def test_kills_grandchild_holding_the_pipes(self):
        with tempfile.TemporaryDirectory() as tmp:
            pidfile = Path(tmp) / "grandchild.pid"
            # The grandchild outlives the shell's own work and keeps stdout open.
            script = f"echo before; (sleep 30; echo after) & echo $! > {pidfile}; wait"
            start = time.monotonic()
            with self.assertRaises(subprocess.TimeoutExpired) as cm:
                run_playbook_tests.run_with_tree_timeout(
                    ["bash", "-c", script], cwd=tmp, env=dict(os.environ), timeout=2)
            elapsed = time.monotonic() - start

            self.assertLess(elapsed, 10, "timeout waited for the grandchild instead of killing it")
            self.assertIn("before", cm.exception.stdout)
            self.assertNotIn("after", cm.exception.stdout)
            time.sleep(0.5)
            self.assertFalse(alive(int(pidfile.read_text())), "grandchild still running after the timeout")

    def test_completed_run_returns_output_and_code(self):
        result = run_playbook_tests.run_with_tree_timeout(
            ["bash", "-c", "echo out; echo err >&2; exit 3"], cwd=".", env=dict(os.environ), timeout=10)
        self.assertEqual((result.returncode, result.stdout, result.stderr), (3, "out\n", "err\n"))


if __name__ == "__main__":
    unittest.main()
