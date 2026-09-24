#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
Regression tests for the OrchestrAI acquire-timeout retry.

The costly mistakes here are resubmitting when it is not safe -- a batch whose
build already ran something, or whose previous build is still live -- and
resubmitting without bound. Every case drives the real watch loop against a
scripted Jenkins, with a fake clock so nothing sleeps.

Usage:
    python3 .github/tests/test_orchestrai_acquire_retry.py
"""

import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
GITHUB_DIR = os.path.dirname(HERE)
SCRIPTS_DIR = os.path.join(GITHUB_DIR, "scripts")
ORCHESTRAI_DIR = os.path.join(GITHUB_DIR, "orchestrai")
CONFIG = os.path.join(GITHUB_DIR, "orchestrai-config.yml")
sys.path.insert(0, SCRIPTS_DIR)
sys.path.insert(0, ORCHESTRAI_DIR)

import acquire_retry  # noqa: E402

# Console lines exactly as stages/04-provision.sh writes them.
PREAMBLE = ("[validate] plan ok\n"
            "[provision] Acquiring 1 machine(s) [tags=apu_stxh] for pipeline-7-L4...\n"
            "[provision]   Queue position 3 (ticket 91) - 60s/2400s\n")
ACQUIRED = PREAMBLE + "[provision] Acquired 1 machine(s) for pipeline-7-L4\n"
TIMED_OUT = (PREAMBLE
             + "[provision] Cancelling queue ticket for pipeline-7-L4...\n"
             + "[provision] ERROR: Timed out waiting for machines after 2400s\n")


class FakeJenkins:
    """Each build is a timeline of (building, console so far); one poll per step."""

    def __init__(self):
        self.timelines = {}
        self.position = {}
        self.unreachable_polls = {}

    def add(self, url, *states):
        self.timelines[url] = list(states)
        self.position[url] = 0

    def _state(self, url):
        timeline = self.timelines[url]
        return timeline[min(self.position[url], len(timeline) - 1)]

    def fetch_building(self, url):
        if self.unreachable_polls.get(url, 0):
            self.unreachable_polls[url] -= 1
            raise OSError("jenkins unreachable")
        return self._state(url)[0]

    def fetch_console(self, url, start):
        text = self._state(url)[1]
        self.position[url] += 1
        return text[start:], len(text)


class Resubmitter:
    def __init__(self, *urls):
        self.urls = list(urls)
        self.calls = []

    def __call__(self, batch_id):
        self.calls.append(batch_id)
        return self.urls.pop(0) if self.urls else None


class Clock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


def watch(jenkins, resubmit, build_urls, retries=3, **kwargs):
    clock = Clock()
    logs = []
    watches = acquire_retry.watch_acquisition(
        build_urls, resubmit, retries=retries,
        fetch_building=jenkins.fetch_building, fetch_console=jenkins.fetch_console,
        clock=clock, sleep=clock.sleep, log=logs.append, **kwargs)
    return watches, logs


class RetryDecisions(unittest.TestCase):

    def test_a_build_that_acquires_is_left_alone(self):
        jenkins = FakeJenkins()
        jenkins.add("u1/", (True, PREAMBLE), (True, ACQUIRED))
        resubmit = Resubmitter()
        watches, _ = watch(jenkins, resubmit, {"linux/stx": "u1/"})
        self.assertEqual(watches["linux/stx"].outcome, "acquired")
        self.assertEqual(watches["linux/stx"].url, "u1/")
        self.assertEqual(resubmit.calls, [])

    def test_an_acquire_timeout_is_resubmitted_until_a_machine_is_acquired(self):
        jenkins = FakeJenkins()
        jenkins.add("u1/", (True, PREAMBLE), (False, TIMED_OUT))
        jenkins.add("u2/", (True, PREAMBLE), (True, ACQUIRED))
        resubmit = Resubmitter("u2/")
        watches, logs = watch(jenkins, resubmit, {"linux/stx": "u1/"})
        w = watches["linux/stx"]
        self.assertEqual(resubmit.calls, ["linux/stx"])
        self.assertEqual((w.outcome, w.url, w.attempt), ("acquired", "u2/", 2))
        self.assertEqual(w.earlier_urls, ["u1/"])
        self.assertTrue(any(line.startswith("::warning::") and "2400s" in line for line in logs))

    def test_the_timed_out_build_must_end_before_it_is_resubmitted(self):
        """Never two live builds for one batch on the same scarce hardware."""
        jenkins = FakeJenkins()
        # The timeout line is already in the console while Jenkins still reports
        # the build as running (cleanup is still in progress).
        jenkins.add("u1/", (True, TIMED_OUT), (True, TIMED_OUT), (False, TIMED_OUT))
        jenkins.add("u2/", (True, ACQUIRED))
        order = []
        resubmit = Resubmitter("u2/")
        building = jenkins.fetch_building

        def tracked_building(url):
            state = building(url)
            order.append((url, state))
            return state

        clock = Clock()
        acquire_retry.watch_acquisition(
            {"b": "u1/"}, resubmit, retries=3, fetch_building=tracked_building,
            fetch_console=jenkins.fetch_console, clock=clock, sleep=clock.sleep,
            log=lambda _: None)
        self.assertEqual(resubmit.calls, ["b"])
        self.assertEqual(order[:3], [("u1/", True), ("u1/", True), ("u1/", False)])

    def test_a_build_that_acquired_anything_is_never_resubmitted(self):
        """A multi-level plan that ran level 1 and then timed out on level 2."""
        jenkins = FakeJenkins()
        jenkins.add("u1/", (False, ACQUIRED + "[test] level L4 done\n" + TIMED_OUT))
        resubmit = Resubmitter("u2/")
        watches, _ = watch(jenkins, resubmit, {"b": "u1/"})
        self.assertEqual(resubmit.calls, [])
        self.assertEqual(watches["b"].url, "u1/")

    def test_a_failure_other_than_acquire_timeout_is_not_retried(self):
        jenkins = FakeJenkins()
        jenkins.add("u1/", (True, "[validate] plan ok\n"),
                    (False, "[validate] ERROR: plan rejected\n"))
        resubmit = Resubmitter("u2/")
        watches, _ = watch(jenkins, resubmit, {"b": "u1/"})
        self.assertEqual((watches["b"].outcome, watches["b"].url), ("finished", "u1/"))
        self.assertEqual(resubmit.calls, [])

    def test_retries_are_bounded(self):
        jenkins = FakeJenkins()
        for url in ("u1/", "u2/", "u3/", "u4/"):
            jenkins.add(url, (False, TIMED_OUT))
        resubmit = Resubmitter("u2/", "u3/", "u4/", "u5/")
        watches, _ = watch(jenkins, resubmit, {"b": "u1/"}, retries=3)
        w = watches["b"]
        self.assertEqual(len(resubmit.calls), 3)
        self.assertEqual((w.outcome, w.attempt, w.url), ("retries-exhausted", 4, "u4/"))
        self.assertEqual(w.earlier_urls, ["u1/", "u2/", "u3/"])

    def test_a_failed_resubmission_keeps_the_timed_out_build(self):
        jenkins = FakeJenkins()
        jenkins.add("u1/", (False, TIMED_OUT))
        resubmit = Resubmitter()  # submit fails: no URL
        watches, _ = watch(jenkins, resubmit, {"b": "u1/"})
        self.assertEqual((watches["b"].outcome, watches["b"].url), ("resubmit-failed", "u1/"))

    def test_batches_are_retried_independently(self):
        jenkins = FakeJenkins()
        jenkins.add("a1/", (False, TIMED_OUT))
        jenkins.add("a2/", (True, ACQUIRED))
        jenkins.add("b1/", (True, PREAMBLE), (True, ACQUIRED))
        resubmit = Resubmitter("a2/")
        watches, _ = watch(jenkins, resubmit, {"linux/stx": "a1/", "windows/halo": "b1/"})
        self.assertEqual(resubmit.calls, ["linux/stx"])
        self.assertEqual({b: w.url for b, w in watches.items()},
                         {"linux/stx": "a2/", "windows/halo": "b1/"})


class Robustness(unittest.TestCase):

    def test_a_marker_split_across_console_chunks_is_still_seen(self):
        jenkins = FakeJenkins()
        split = TIMED_OUT.index("Timed out") + 5
        jenkins.add("u1/", (True, TIMED_OUT[:split]), (False, TIMED_OUT))
        jenkins.add("u2/", (True, ACQUIRED))
        resubmit = Resubmitter("u2/")
        watch(jenkins, resubmit, {"b": "u1/"})
        self.assertEqual(resubmit.calls, ["b"])

    def test_jenkins_being_briefly_unreachable_causes_no_resubmission(self):
        jenkins = FakeJenkins()
        jenkins.add("u1/", (True, PREAMBLE), (True, ACQUIRED))
        jenkins.unreachable_polls["u1/"] = 4
        resubmit = Resubmitter("u2/")
        watches, logs = watch(jenkins, resubmit, {"b": "u1/"})
        self.assertEqual(watches["b"].outcome, "acquired")
        self.assertEqual(resubmit.calls, [])
        # Reported once per outage, not once per failed poll.
        self.assertEqual(sum("could not poll" in line for line in logs), 1)

    def test_a_build_that_never_reaches_acquisition_stops_being_watched(self):
        jenkins = FakeJenkins()
        jenkins.add("u1/", (True, PREAMBLE))
        resubmit = Resubmitter("u2/")
        watches, _ = watch(jenkins, resubmit, {"b": "u1/"}, attempt_window=600)
        self.assertEqual((watches["b"].outcome, watches["b"].url), ("watch-expired", "u1/"))
        self.assertEqual(resubmit.calls, [])

    def test_the_markers_match_what_the_pipeline_prints(self):
        self.assertRegex("[provision] Acquired 2 machine(s) for pipeline-44-L4",
                         acquire_retry.ACQUIRED_RE)
        self.assertRegex("[2026-09-23T10:00:00.000Z] [provision] ERROR: Timed out "
                         "waiting for machines after 2400s", acquire_retry.ACQUIRE_TIMEOUT_RE)
        # A playbook's own output must not look like the pipeline giving up.
        self.assertIsNone(acquire_retry.ACQUIRE_TIMEOUT_RE.search(
            "ERROR: Timed out waiting for machines after 5s"))


class Configuration(unittest.TestCase):

    def test_valid_retry_counts(self):
        for value in range(0, acquire_retry.MAX_RETRIES + 1):
            self.assertIsNone(acquire_retry.check_retries(value), value)

    def test_invalid_retry_counts(self):
        for value in (-1, acquire_retry.MAX_RETRIES + 1, True, "3", 2.0, None):
            self.assertIsNotNone(acquire_retry.check_retries(value), value)

    def test_the_cap_keeps_the_trigger_job_inside_githubs_six_hour_limit(self):
        per_attempt = (acquire_retry.ATTEMPT_WINDOW_SECONDS
                       + acquire_retry.RESUBMIT_ALLOWANCE_SECONDS)
        self.assertLess((acquire_retry.MAX_RETRIES + 1) * per_attempt, 6 * 3600 - 1800)

    def test_watch_window_exceeds_the_shipped_acquire_timeout(self):
        import yaml
        with open(CONFIG) as f:
            cfg = yaml.safe_load(f)
        configured = cfg["run_settings"]["acquire_timeout"] * 60
        self.assertGreaterEqual(acquire_retry.ATTEMPT_WINDOW_SECONDS,
                                configured + 600)


class Reporting(unittest.TestCase):

    def _watch(self, **fields):
        w = acquire_retry.BatchWatch("linux/stx", "u4/", 0.0)
        for key, value in fields.items():
            setattr(w, key, value)
        return w

    def test_nothing_is_reported_when_no_batch_needed_a_retry(self):
        annotations, summary = acquire_retry.report(
            {"linux/stx": self._watch(outcome="acquired")}, 3)
        self.assertEqual((annotations, summary), ([], ""))

    def test_exhausted_retries_are_reported_as_capacity_not_a_playbook_failure(self):
        w = self._watch(outcome="retries-exhausted", attempt=4, timeout_seconds=2400,
                        earlier_urls=["u1/", "u2/", "u3/"])
        annotations, summary = acquire_retry.report({"linux/stx": w}, 3)
        self.assertEqual(len(annotations), 1)
        self.assertTrue(annotations[0].startswith("::error::"))
        self.assertIn("not a playbook failure", annotations[0])
        self.assertIn("| `linux/stx` | 4 | retries-exhausted |", summary)

    def test_a_successful_retry_is_still_visible(self):
        """Silent retries would hide a fleet that is short on machines."""
        w = self._watch(outcome="acquired", attempt=2, earlier_urls=["u1/"])
        annotations, summary = acquire_retry.report({"linux/stx": w}, 3)
        self.assertEqual(annotations, [])
        self.assertIn("| `linux/stx` | 2 | acquired | [1](u1/) |", summary)


@unittest.skipUnless(importlib.util.find_spec("yaml"),
                     "orchestrai_trigger.py needs pyyaml")
class TriggerWiring(unittest.TestCase):
    """retry_acquire_timeouts must resubmit each batch with its own plan."""

    def setUp(self):
        import orchestrai_trigger
        self.trigger = orchestrai_trigger
        real = acquire_retry.watch_acquisition

        def no_sleep(*args, **kwargs):
            kwargs["sleep"] = lambda _: None
            return real(*args, **kwargs)

        self.patches = [mock.patch.object(acquire_retry, "watch_acquisition", no_sleep)]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def test_each_batch_is_resubmitted_with_its_own_plan(self):
        jenkins = FakeJenkins()
        jenkins.add("a1/", (False, TIMED_OUT))
        jenkins.add("a2/", (True, ACQUIRED))
        jenkins.add("b1/", (True, ACQUIRED))
        plan_a, plan_b = {"plan": "a"}, {"plan": "b"}
        prepared = [("linux/stx", {"platform": "linux"}, plan_a, {"builds": "a"}),
                    ("windows/halo", {"platform": "windows"}, plan_b, {"builds": "b"})]
        submitted = []

        def fake_trigger(plan, builds, platform, pipeline, user, token):
            submitted.append((plan, builds, platform))
            return "a2/"

        with tempfile.NamedTemporaryFile("r", suffix=".md") as summary, \
                mock.patch.object(self.trigger, "trigger", fake_trigger), \
                mock.patch.object(acquire_retry, "fetch_building",
                                  lambda url, auth: jenkins.fetch_building(url)), \
                mock.patch.object(acquire_retry, "fetch_console",
                                  lambda url, start, auth: jenkins.fetch_console(url, start)), \
                mock.patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": summary.name}), \
                contextlib.redirect_stderr(io.StringIO()):
            urls = self.trigger.retry_acquire_timeouts(
                {"linux/stx": "a1/", "windows/halo": "b1/"}, prepared,
                {"pipeline": {"url": "x", "job": "y"}}, 3, "user", "token")
            written = open(summary.name).read()

        self.assertEqual(urls, {"linux/stx": "a2/", "windows/halo": "b1/"})
        self.assertEqual(submitted, [(plan_a, {"builds": "a"}, "linux")])
        self.assertIn("linux/stx", written)
        self.assertNotIn("windows/halo", written)

    def _run_main(self, config_path, jenkins, submitted_urls):
        batches = {"linux/stx": {"platform": "linux", "arch": "stx", "gfx": "gfx1150",
                                 "tags": ["apu_stx"], "playbooks": ["gaia-agents"]}}
        urls = iter(submitted_urls)
        polled = []

        def fetch_building(url, auth):
            polled.append(url)
            return jenkins.fetch_building(url)

        with tempfile.NamedTemporaryFile("r") as out, \
                tempfile.NamedTemporaryFile("r") as summary, \
                mock.patch.object(self.trigger, "trigger", lambda *args: next(urls)), \
                mock.patch.object(acquire_retry, "fetch_building", fetch_building), \
                mock.patch.object(acquire_retry, "fetch_console",
                                  lambda url, start, auth: jenkins.fetch_console(url, start)), \
                mock.patch.dict(os.environ, {
                    "BATCHES_JSON": json.dumps(batches),
                    "ORCHESTRAI_PIPELINE_USER": "user", "ORCHESTRAI_PIPELINE_TOKEN": "token",
                    "ORCHESTRAI_PIPELINE_URL": "https://jenkins.example",
                    "ORCHESTRAI_PIPELINE_JOB": "pipeline",
                    "ORCHESTRAI_ROCM_MULTI_ARCH_INDEX_URL": "https://index.example",
                    "ORCHESTRAI_THEROCK_URL": "https://therock.example",
                    "ORCHESTRAI_HF_TOKEN": "hf",
                    "GITHUB_OUTPUT": out.name, "GITHUB_STEP_SUMMARY": summary.name}), \
                mock.patch.object(sys, "argv", ["orchestrai_trigger.py", "--config", config_path]), \
                contextlib.redirect_stderr(io.StringIO()):
            self.trigger.main()
            return open(out.name).read(), polled

    def test_main_hands_the_wait_jobs_the_resubmitted_build(self):
        """The shipped config enables retries, and the wait jobs get the new URL."""
        jenkins = FakeJenkins()
        jenkins.add("u1/", (False, TIMED_OUT))
        jenkins.add("u2/", (True, ACQUIRED))
        written, _ = self._run_main(CONFIG, jenkins, ["u1/", "u2/"])
        self.assertIn('build_urls={"linux/stx": "u2/"}', written)

    def test_zero_retries_turns_the_watch_off_entirely(self):
        import yaml
        with open(CONFIG) as f:
            cfg = yaml.safe_load(f)
        cfg["run_settings"]["acquire_retries"] = 0
        with tempfile.NamedTemporaryFile("w", suffix=".yml") as tmp:
            yaml.safe_dump(cfg, tmp)
            tmp.flush()
            jenkins = FakeJenkins()
            jenkins.add("u1/", (False, TIMED_OUT))
            written, polled = self._run_main(tmp.name, jenkins, ["u1/", "u2/"])
        self.assertIn('build_urls={"linux/stx": "u1/"}', written)
        self.assertEqual(polled, [])

    def test_a_failure_while_watching_leaves_the_original_builds(self):
        def broken(*args, **kwargs):
            raise RuntimeError("boom")

        stderr = io.StringIO()
        with mock.patch.object(acquire_retry, "watch_acquisition", broken), \
                contextlib.redirect_stderr(stderr):
            urls = self.trigger.retry_acquire_timeouts(
                {"linux/stx": "a1/"}, [("linux/stx", {"platform": "linux"}, {}, {})],
                {"pipeline": {}}, 3, "user", "token")
        self.assertEqual(urls, {"linux/stx": "a1/"})
        self.assertIn("::warning::", stderr.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
