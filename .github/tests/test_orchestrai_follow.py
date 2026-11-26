# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""orchestrai_follow.py: a batch's live progress in its Test job's log."""

import contextlib
import io
import os
import sys
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))

import orchestrai_follow as follow  # noqa: E402

# The console of a real batch build (run ffec2a54, windows/rx9070xt), cut down.
CONSOLE = """\
[2026-11-26T01:16:51.061Z] ── 02-Plan ──
[2026-11-26T01:17:05.268Z] ── 05-L4-sys (White-Box) ──
[2026-11-26T01:30:14.190Z] [05-L4-sys] [deploy] Actor started on MNB-UCICD-DT494 (10.5.124.213)
[2026-11-26T01:30:21.975Z] [05-L4-sys] Submitting group playbook-comfyui-image-gen (parallelization=spread, on_failure=continue, iterations=1, affinity_group=none)...
[2026-11-26T01:30:21.975Z] [05-L4-sys]   → session(s): sess-1795656621871974896
[2026-11-26T01:30:21.975Z] [05-L4-sys] Submitting group playbook-zh-CN-gaia-agents (parallelization=spread, on_failure=continue, iterations=1, affinity_group=none)...
[2026-11-26T01:30:21.976Z] [timeout] L4-sys/playbooks/windows/sys_func-playbook_runner: catalog budget 120m capped by the plan test time limit
[2026-11-26T01:30:22.360Z] [05-L4-sys]   → session(s): sess-1795656621951187895
[2026-11-26T01:30:24.334Z] [05-L4-sys] Tracking sessions: sess-1795656621871974896,sess-1795656621951187895
[2026-11-26T01:30:24.335Z] [05-L4-sys]   2 active, 0 done (0/2 tests) — 0s elapsed
[2026-11-26T01:30:55.289Z] [05-L4-sys]   2 active, 0 done (0/2 tests) — 30s elapsed
[2026-11-26T01:44:05.185Z] [05-L4-sys]   ✓ sys_func-playbook_runner: passed [10.5.124.213 MNB-UCICD-DT494]
[2026-11-26T01:44:25.311Z] [05-L4-sys]   1 active, 1 done (1/2 tests) — 840s elapsed
"""

GROUPS = ["playbook-comfyui-image-gen", "playbook-zh-CN-gaia-agents"]

TESTS = {"tests": [
    {"execution_id": "sess-1795656621871974896-job-0", "suite": "05-L4-sys_sess-1795656621871974896",
     "name": "L4-sys/playbooks/windows/sys_func-playbook_runner", "outcome": "passed",
     "recorded_at": "2026-11-26T01:44:00Z", "attempt": 1, "flaky": False},
]}


class FakeConsole:
    def __init__(self, *chunks):
        self.chunks, self.more = list(chunks), True

    def read(self):
        lines = self.chunks.pop(0)
        self.more = bool(self.chunks)
        return [follow.TIMESTAMP.sub("", line) for line in lines.splitlines()]


class Follower(unittest.TestCase):

    def run_polls(self, console, api_answers, run_id="r1", cp=None):
        out = io.StringIO()
        calls = []

        def api(cp_, method, path, **kwargs):
            calls.append(path)
            return api_answers.pop(0)
        f = follow.Follower(console, run_id, cp if cp is not None else {"x": 1}, GROUPS)
        with mock.patch.object(follow.trigger, "api", api), contextlib.redirect_stdout(out):
            while True:
                f.poll()
                if not console.more:
                    break
        return f, out.getvalue(), calls

    def test_prints_stage_machine_and_each_playbook_by_name(self):
        f, out, calls = self.run_polls(FakeConsole(CONSOLE), [TESTS])
        self.assertIn("stage 02-Plan", out)
        self.assertIn("stage 05-L4-sys (White-Box)", out)
        self.assertIn("machine MNB-UCICD-DT494", out)
        self.assertIn("0/2 playbooks done", out)
        self.assertRegex(out, r"PASSED\s+comfyui-image-gen\s+\(1/2 done\)")
        self.assertEqual(f.session_group["sess-1795656621951187895"], "playbook-zh-CN-gaia-agents")
        self.assertEqual(calls, ["/runs/r1/tests"])

    def test_results_are_read_only_when_a_test_ends_and_printed_once(self):
        first, second = CONSOLE.split("[2026-11-26T01:44:05.185Z]")
        console = FakeConsole(first, "[2026-11-26T01:44:05.185Z]" + second, "")
        _, out, calls = self.run_polls(console, [TESTS, TESTS])
        # Once when the count moved, once more when the build ended.
        self.assertEqual(len(calls), 2)
        self.assertEqual(out.count("comfyui-image-gen"), 1)

    def test_a_job_that_starts_late_reports_what_is_already_done(self):
        late = CONSOLE.replace("0/2 tests", "1/2 tests").replace("0 done", "1 done")
        console = FakeConsole(late, "")
        f = follow.Follower(console, "r1", {"x": 1}, GROUPS)
        out = io.StringIO()
        with mock.patch.object(follow.trigger, "api", return_value=TESTS), contextlib.redirect_stdout(out):
            f.poll()  # still building, but tests are already done
        self.assertIn("comfyui-image-gen", out.getvalue())

    def test_unreadable_results_are_said_once_and_the_rest_still_shows(self):
        def refuse(*a, **k):
            raise ValueError("HTTP 403 forbidden")
        console = FakeConsole(CONSOLE, "")
        f = follow.Follower(console, "r1", {"x": 1}, GROUPS)
        out = io.StringIO()
        with mock.patch.object(follow.trigger, "api", refuse), contextlib.redirect_stdout(out):
            f.poll()
            f.poll()
        self.assertEqual(out.getvalue().count("test results unavailable"), 1)
        self.assertIn("machine MNB-UCICD-DT494", out.getvalue())

    def test_without_a_run_only_the_console_is_followed(self):
        f, out, calls = self.run_polls(FakeConsole(CONSOLE), [], run_id="", cp={})
        self.assertEqual(calls, [])
        self.assertIn("stage 05-L4-sys (White-Box)", out)

    def test_an_unknown_session_falls_back_to_its_suite(self):
        tests = {"tests": [dict(TESTS["tests"][0], execution_id="sess-9-job-0", suite="05-L4-sys_sess-9",
                                outcome="error", attempt=2)]}
        _, out, _ = self.run_polls(FakeConsole(CONSOLE), [tests])
        self.assertRegex(out, r"ERROR\s+05-L4-sys_sess-9\s+\(attempt 2, 1/2 done\)")


class PairSessions(unittest.TestCase):
    """Sessions get playbook names only when the console confirms the order."""

    SESSIONS = ["sess-1", "sess-2", "sess-3", "sess-4"]
    GROUPS = ["playbook-a", "playbook-b", "playbook-c", "playbook-zh-CN-a"]

    def test_plan_order_confirmed_by_the_surviving_lines(self):
        # From a real build: other writers garbled b's session line and c's
        # submit line; what survived still agrees with the plan order.
        mapping = follow.pair_sessions(self.SESSIONS, self.GROUPS,
                                       ["playbook-a", "playbook-b", "playbook-zh-CN-a"],
                                       [("playbook-a", "sess-1"), ("playbook-zh-CN-a", "sess-4")])
        self.assertEqual(mapping, dict(zip(self.SESSIONS, self.GROUPS)))

    def test_a_pipeline_that_sorted_the_groups_is_still_named(self):
        shuffled = ["playbook-c", "playbook-a", "playbook-zh-CN-a", "playbook-b"]
        mapping = follow.pair_sessions(self.SESSIONS, shuffled, ["playbook-a", "playbook-b"],
                                       [("playbook-a", "sess-1")])
        self.assertEqual(mapping["sess-3"], "playbook-c")

    def test_any_disagreement_names_nothing(self):
        self.assertEqual(follow.pair_sessions(self.SESSIONS, self.GROUPS, ["playbook-a"],
                                              [("playbook-a", "sess-2")]), {})
        self.assertEqual(follow.pair_sessions(self.SESSIONS, self.GROUPS[:3], [], []), {})
        self.assertEqual(follow.pair_sessions(self.SESSIONS, self.GROUPS, ["playbook-c", "playbook-b"], []), {})

    def test_without_the_plan_order_a_complete_console_still_names_them(self):
        self.assertEqual(follow.pair_sessions(self.SESSIONS, [], self.GROUPS, []),
                         dict(zip(self.SESSIONS, self.GROUPS)))
        self.assertEqual(follow.pair_sessions(self.SESSIONS, [], self.GROUPS[:3], []), {})

    def test_batch_groups_come_from_the_triggers_batches(self):
        env = {"FOLLOW_BATCHES": '{"windows/stx": {"playbooks": ["a", "zh-CN/b"]}}', "BATCH_ID": "windows/stx"}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(follow.batch_groups(), ["playbook-a", "playbook-zh-CN-b"])
        with mock.patch.dict(os.environ, {"FOLLOW_BATCHES": "not json"}, clear=True):
            self.assertEqual(follow.batch_groups(), [])


class Console(unittest.TestCase):

    def response(self, body, size, more):
        resp = mock.MagicMock()
        resp.__enter__.return_value = resp
        resp.read.side_effect = lambda n: body[:n]
        resp.headers = {"X-Text-Size": str(size), "X-More-Data": "true" if more else "false"}
        return resp

    def test_reads_only_the_new_part_and_keeps_an_unfinished_line(self):
        console = follow.Console("https://j/job/p/9/", "u", "t")
        seen = []

        def urlopen(req, timeout):
            seen.append(req.full_url)
            return answers.pop(0)
        answers = [self.response(b"[2026-11-26T01:16:51.061Z] \xe2\x94\x80\xe2\x94\x80 02-Plan \xe2\x94\x80\xe2\x94\x80\npart", 40, True),
                   self.response(b"ial line\n", 49, False)]
        with mock.patch.object(follow.urllib.request, "urlopen", urlopen):
            self.assertEqual(console.read(), ["── 02-Plan ──"])
            self.assertEqual(console.read(), ["partial line", ""])
        self.assertEqual(seen, ["https://j/job/p/9/logText/progressiveText?start=0",
                                "https://j/job/p/9/logText/progressiveText?start=40"])
        self.assertFalse(console.more)

    def test_the_credentials_go_in_a_header_never_the_url(self):
        console = follow.Console("https://j/job/p/9/", "user", "secret-token")
        with mock.patch.object(follow.urllib.request, "urlopen",
                               return_value=self.response(b"", 0, True)) as urlopen:
            console.read()
        req = urlopen.call_args.args[0]
        self.assertNotIn("secret", req.full_url)
        self.assertTrue(req.get_header("Authorization").startswith("Basic "))


class Main(unittest.TestCase):

    def test_does_nothing_without_a_build(self):
        with mock.patch.dict(os.environ, {}, clear=True), \
                mock.patch.object(follow, "Console", side_effect=AssertionError("no build to follow")):
            follow.main()


if __name__ == "__main__":
    unittest.main()
