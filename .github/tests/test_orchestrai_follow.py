# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""orchestrai_follow.py: a batch's live progress in its Test job's log."""

import contextlib
import http.server
import io
import os
import sys
import threading
import unittest
import urllib.error
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))

import orchestrai_follow as follow  # noqa: E402

# The console of a real batch build (run ffec2a54, windows/rx9070xt), cut down.
# Its "[timeout]" line was written by another process between a group's
# "Submitting group" line and its "-> session(s)" line.
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

NAMES = {"playbook-comfyui-image-gen": "comfyui-image-gen",
         "playbook-zh-CN-gaia-agents": "zh-CN/gaia-agents"}


def row(session, outcome="passed", **extra):
    return {"execution_id": f"{session}-job-0", "suite": f"05-L4-sys_{session}",
            "name": "L4-sys/playbooks/windows/sys_func-playbook_runner", "outcome": outcome,
            "recorded_at": "2026-11-26T01:44:00Z", "attempt": 1, "flaky": False, **extra}


TESTS = {"tests": [row("sess-1795656621871974896"), row("sess-1795656621951187895", "error")]}


class FakeConsole:
    def __init__(self, *chunks):
        self.chunks, self.more = list(chunks), True

    def read(self):
        lines = self.chunks.pop(0)
        self.more = bool(self.chunks)
        return [follow.TIMESTAMP.sub("", line) for line in lines.splitlines()]


class Follower(unittest.TestCase):

    def run_polls(self, console, api_answers, run_id="r1", cp=None, names=NAMES):
        out, calls = io.StringIO(), []

        def api(cp_, method, path, **kwargs):
            calls.append((path, kwargs.get("retry_seconds")))
            answer = api_answers.pop(0)
            if isinstance(answer, Exception):
                raise answer
            return answer
        f = follow.Follower(console, run_id, cp if cp is not None else {"x": 1}, names)
        with mock.patch.object(follow.trigger, "api", api), contextlib.redirect_stdout(out):
            while True:
                f.poll()
                if not console.more:
                    break
        return f, out.getvalue(), calls

    def test_prints_stage_machine_and_each_playbook_by_its_batch_name(self):
        _, out, calls = self.run_polls(FakeConsole(CONSOLE), [TESTS])
        self.assertIn("stage 02-Plan", out)
        self.assertIn("stage 05-L4-sys (White-Box)", out)
        self.assertIn("machine MNB-UCICD-DT494", out)
        self.assertIn("0/2 playbooks done", out)
        self.assertRegex(out, r"PASSED\s+comfyui-image-gen\s+\(1/2 done\)")
        # Its submit line and session line are not adjacent, but it is the one
        # session left after the anchored one: proven.
        self.assertRegex(out, r"ERROR\s+zh-CN/gaia-agents\s+\(1/2 done\)")
        self.assertNotIn("matched", out)
        self.assertEqual([c[0] for c in calls], ["/runs/r1/tests"])

    def test_results_are_read_when_a_test_ends_and_each_printed_once(self):
        first, second = CONSOLE.split("[2026-11-26T01:44:05.185Z]")
        console = FakeConsole(first, "[2026-11-26T01:44:05.185Z]" + second, "")
        _, out, calls = self.run_polls(console, [TESTS, TESTS])
        # Once when the count moved, once more, retrying longer, when the build ended.
        self.assertEqual([c[1] for c in calls], [follow.RESULTS_RETRY_SECONDS,
                                                 follow.FINAL_RESULTS_RETRY_SECONDS])
        self.assertEqual(out.count("comfyui-image-gen"), 1)

    def test_a_job_that_starts_late_reports_what_is_already_done(self):
        late = CONSOLE.replace("0/2 tests", "1/2 tests").replace("0 done", "1 done")
        console = FakeConsole(late, "")
        f = follow.Follower(console, "r1", {"x": 1}, NAMES)
        out = io.StringIO()
        with mock.patch.object(follow.trigger, "api", return_value=TESTS), contextlib.redirect_stdout(out):
            f.poll()  # still building, but tests are already done
        self.assertIn("comfyui-image-gen", out.getvalue())

    def test_unreadable_results_are_said_once_and_read_again_later(self):
        first, second = CONSOLE.split("[2026-11-26T01:44:05.185Z]")
        console = FakeConsole(first, "[2026-11-26T01:44:05.185Z]" + second, "", "")
        down = ValueError("HTTP 503")
        _, out, calls = self.run_polls(console, [down, down, TESTS])
        self.assertEqual(out.count("test results unavailable"), 1)
        self.assertIn("comfyui-image-gen", out)  # printed once the API answered again
        self.assertEqual(len(calls), 3)

    def test_rows_without_an_execution_id_are_each_printed(self):
        tests = {"tests": [row("sess-1795656621871974896", execution_id=None),
                           row("sess-1795656621951187895", execution_id=None)]}
        _, out, _ = self.run_polls(FakeConsole(CONSOLE), [tests])
        self.assertIn("comfyui-image-gen", out)
        self.assertIn("zh-CN/gaia-agents", out)

    def test_without_a_run_only_the_console_is_followed(self):
        _, out, calls = self.run_polls(FakeConsole(CONSOLE), [], run_id="", cp={})
        self.assertEqual(calls, [])
        self.assertIn("stage 05-L4-sys (White-Box)", out)

    def test_an_unproven_session_shows_by_its_suite(self):
        tests = {"tests": [row("sess-9", "error", attempt=2)]}
        _, out, _ = self.run_polls(FakeConsole(CONSOLE), [tests])
        self.assertRegex(out, r"ERROR\s+05-L4-sys_sess-9\s+\(attempt 2, 1/2 done\)")

    def test_a_garbled_console_names_nothing_it_cannot_prove(self):
        # comfyui's submit line was cut by another writer: one group is lost,
        # and nothing shows which of the two sessions it is.
        garbled = CONSOLE.replace("Submitting group playbook-comfyui-image-gen (parallelization=spread, on_failure",
                                  "Submitting group playbook-comf=1, affinity_group=none)... on_failure")
        _, out, _ = self.run_polls(FakeConsole(garbled), [TESTS])
        self.assertIn("0 of 2 sessions matched", out)
        self.assertNotIn("comfyui-image-gen", out)
        self.assertNotIn("gaia-agents", out)

    def test_a_blank_line_does_not_break_a_pair(self):
        spaced = CONSOLE.replace("affinity_group=none)...\n", "affinity_group=none)...\n\n", 1)
        _, out, _ = self.run_polls(FakeConsole(spaced), [TESTS])
        self.assertIn("comfyui-image-gen", out)


class PairSessions(unittest.TestCase):
    """Sessions get playbook names only where the console proves them."""

    S = ["sess-1", "sess-2", "sess-3", "sess-4"]
    G = ["playbook-a", "playbook-b", "playbook-c", "playbook-d"]

    def pair(self, submitted, pairs, groups=None):
        return follow.pair_sessions(self.S, self.G if groups is None else groups, submitted, pairs)

    def test_every_submit_line_surviving_names_every_session(self):
        self.assertEqual(self.pair(self.G, []), dict(zip(self.S, self.G)))
        self.assertEqual(follow.pair_sessions(self.S, [], self.G, []), dict(zip(self.S, self.G)))

    def test_with_a_lost_line_only_what_anchors_pin_down_is_named(self):
        # b's line was lost. a is anchored at sess-1; b can be anywhere in
        # sess-2..4, so nothing else is proven.
        self.assertEqual(self.pair(["playbook-a", "playbook-c", "playbook-d"], [("playbook-a", "sess-1")]),
                         {"sess-1": "playbook-a"})
        # d anchored at sess-4: b and c share sess-2 and sess-3 in an unknown order.
        self.assertEqual(self.pair(["playbook-a", "playbook-c", "playbook-d"],
                                   [("playbook-a", "sess-1"), ("playbook-d", "sess-4")]),
                         {"sess-1": "playbook-a", "sess-4": "playbook-d"})
        # c anchored at sess-3 too: the one free session, sess-2, is the lost b.
        self.assertEqual(self.pair(["playbook-a", "playbook-c", "playbook-d"],
                                   [("playbook-a", "sess-1"), ("playbook-c", "sess-3")]),
                         dict(zip(self.S, self.G)))

    def test_the_batch_order_is_never_assumed(self):
        # The plan lists a, c, b; the pipeline ran a, b, c. Only a's lines
        # survived: b and c stay unnamed, whatever order the batch has.
        s3 = ["sess-1", "sess-2", "sess-3"]
        mapping = follow.pair_sessions(s3, ["playbook-a", "playbook-c", "playbook-b"],
                                       ["playbook-a"], [("playbook-a", "sess-1")])
        self.assertEqual(mapping, {"sess-1": "playbook-a"})
        self.assertEqual(follow.pair_sessions(s3, ["playbook-a", "playbook-c", "playbook-b"], [], []), {})

    def test_contradictions_name_nothing(self):
        self.assertEqual(self.pair(self.G, [("playbook-a", "sess-2")]), {})   # order vs anchor
        self.assertEqual(self.pair(["playbook-b", "playbook-a"],
                                   [("playbook-a", "sess-1"), ("playbook-b", "sess-2")]), {})
        self.assertEqual(self.pair(self.G, [], groups=self.G[:3]), {})        # not this build's groups
        self.assertEqual(self.pair(self.G + ["playbook-a"], []), {})          # a group twice

    def test_lines_of_groups_the_batch_does_not_run_are_ignored(self):
        self.assertEqual(self.pair(self.G + ["playbook-x"], [("playbook-x", "sess-9")]),
                         dict(zip(self.S, self.G)))

    def test_batch_names_map_groups_to_the_batch_keys(self):
        env = {"FOLLOW_BATCHES": '{"windows/stx": {"playbooks": ["a", "zh-CN/b"]}}', "BATCH_ID": "windows/stx"}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(follow.batch_names(), {"playbook-a": "a", "playbook-zh-CN-b": "zh-CN/b"})
        with mock.patch.dict(os.environ, {"FOLLOW_BATCHES": "not json"}, clear=True):
            self.assertEqual(follow.batch_names(), {})


class Console(unittest.TestCase):

    def response(self, body, size, more):
        resp = mock.MagicMock()
        resp.__enter__.return_value = resp
        resp.read.side_effect = lambda n: body[:n]
        resp.headers = {"X-More-Data": "true" if more else "false"}
        if size is not None:
            resp.headers["X-Text-Size"] = str(size)
        return resp

    def console(self, *answers):
        console = follow.Console("https://j/job/p/9/", "user", "secret-token")
        console.opener = mock.Mock()
        console.opener.open.side_effect = list(answers)
        return console

    def test_reads_only_the_new_part_and_keeps_an_unfinished_line(self):
        console = self.console(
            self.response("[2026-11-26T01:16:51.061Z] ── 02-Plan ──\npart".encode(), 40, True),
            self.response(b"ial line\n", 49, False))
        self.assertEqual(console.read(), ["── 02-Plan ──"])
        self.assertEqual(console.read(), ["partial line", ""])
        urls = [c.args[0].full_url for c in console.opener.open.call_args_list]
        self.assertEqual(urls, ["https://j/job/p/9/logText/progressiveText?start=0",
                                "https://j/job/p/9/logText/progressiveText?start=40"])
        self.assertFalse(console.more)

    def test_an_answer_that_is_not_the_console_is_an_error_not_the_end(self):
        console = self.console(self.response(b"<html>Sign in</html>", None, False))
        with self.assertRaisesRegex(ValueError, "not a Jenkins console"):
            console.read()
        self.assertTrue(console.more)

    def test_the_credentials_go_in_a_header_never_the_url(self):
        console = self.console(self.response(b"", 0, True))
        console.read()
        req = console.opener.open.call_args.args[0]
        self.assertNotIn("secret", req.full_url)
        self.assertTrue(req.get_header("Authorization").startswith("Basic "))

    def test_a_redirect_is_refused_and_the_login_never_sent_on(self):
        seen = []

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                seen.append(self.path)
                self.send_response(302)
                self.send_header("Location", f"http://127.0.0.1:{self.server.server_port}/elsewhere")
                self.end_headers()

            def log_message(self, *args):
                pass
        server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        console = follow.Console(f"http://127.0.0.1:{server.server_port}/job/p/9/", "user", "secret-token")
        with self.assertRaises(urllib.error.HTTPError):
            console.read()
        self.assertEqual(seen, ["/job/p/9/logText/progressiveText?start=0"])


class Main(unittest.TestCase):

    def test_does_nothing_without_a_build(self):
        with mock.patch.dict(os.environ, {}, clear=True), \
                mock.patch.object(follow, "Console", side_effect=AssertionError("no build to follow")):
            follow.main()


if __name__ == "__main__":
    unittest.main()
