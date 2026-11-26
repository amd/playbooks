#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
Show a batch's progress live in its Test job's log
==================================================

orchestrai_wait_build.sh starts this in the background while it waits for the
batch's pipeline build. It prints, as they happen:

    stage 05-L4-sys (System)
    machine MNB-UCICD-DT494
    PASSED         comfyui-image-gen                 (1/27 done)
    ERROR          zh-CN/hermes-lemonade-server      (3/27 done)

It reads the build's console as it grows (Jenkins progressiveText, only the new
part on each poll) for the stage, the machine and the done count, and the run's
test results (CI API GET /runs/{id}/tests, results:read) for each outcome as
it is recorded.

A test row names only the runner test and its pipeline session, so the
playbook comes from the console, and only where the console proves it (see
pair_sessions): other processes write to the console at the same time and can
garble or drop a line. A session the console does not prove is shown by its
session id, never under a playbook name it may not be.

It only prints. orchestrai_wait_build.sh decides when the build is done, and
the verdict step decides each playbook's result; nothing here can fail the job.

Inputs (env): STARTED_BUILD_URL, ORCHESTRAI_PIPELINE_USER/TOKEN (the build's
console), RUN_ID and ORCHESTRAI_V2_* (the run's test results; without them the
outcomes are not shown, the rest is), FOLLOW_BATCHES and BATCH_ID (the
trigger's batches, {batch_id: {"playbooks": [...]}}: which groups the build
runs, not their order).
"""

import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import orchestrai_trigger as trigger
from orchestrai_keys import group_id

POLL_SECONDS = 30
HTTP_TIMEOUT = 30
# One poll reads at most this much new console; a busy build writes far less
# in POLL_SECONDS, and a job that starts late reads on at once until caught up.
MAX_CHUNK = 4 << 20
# The longest a build can run (max_duration) plus the time it takes to wind down.
WIND_DOWN_SECONDS = 30 * 60
# How long one read of the test results retries; a failed read is tried again
# when the next test ends, and once more, for longer, when the build ends. The
# final read must end before orchestrai_wait_build.sh stops the follower, 180 s
# after the build has ended.
RESULTS_RETRY_SECONDS = 60
FINAL_RESULTS_RETRY_SECONDS = 90

TIMESTAMP = re.compile(r"^\[\d{4}-\d\d-\d\dT[\d:.]+Z\]\s?")
STAGE = re.compile(r"^── (\S.*?) ──")
MACHINE = re.compile(r"Actor started on (\S+)")
# Whole lines only: a garbled line must not pass for one of these.
GROUP = re.compile(r"^\[[^\]]+\] Submitting group (\S+)(?: to machine \S+)? \(.*\)\.\.\.$")
SESSIONS = re.compile(r"^\[[^\]]+\]\s+→ session\(s\): (sess-\d+(?:,sess-\d+)*)$")
TRACKING = re.compile(r"^\[[^\]]+\] Tracking sessions: (sess-\d+(?:,sess-\d+)*)$")
COUNT = re.compile(r"\b(\d+) active, (\d+) done \((\d+)/(\d+) tests\)")
SESSION_ID = re.compile(r"(sess-\d+)")


def say(line):
    print(f"[live {time.strftime('%H:%M', time.gmtime())}Z] {line}", flush=True)


class Console:
    """The build's console, read a new part at a time. The pipeline login goes
    to the build's host only: a redirect is refused, never followed."""

    def __init__(self, build_url, user, token):
        self.url = build_url.rstrip("/") + "/logText/progressiveText"
        self.auth = "Basic " + base64.b64encode(f"{user}:{token}".encode()).decode()
        self.opener = urllib.request.build_opener(trigger._NoRedirect)
        self.start, self.more, self.partial, self.truncated = 0, True, b"", False

    def read(self):
        """New complete lines since the last read; sets self.more. Raises
        OSError (a redirect is an HTTPError) or ValueError when the answer is
        not the build's console."""
        req = urllib.request.Request(f"{self.url}?start={self.start}",
                                     headers={"Authorization": self.auth})
        with self.opener.open(req, timeout=HTTP_TIMEOUT) as resp:
            raw = resp.read(MAX_CHUNK)
            size = resp.headers.get("X-Text-Size", "")
            more = resp.headers.get("X-More-Data", "")
        # A login page or a proxy's answer: not the console, and not its end.
        if not size.isdigit():
            raise ValueError("the answer is not a Jenkins console (no X-Text-Size)")
        self.more = more.lower() == "true"
        self.truncated = len(raw) >= MAX_CHUNK
        if self.truncated:  # the rest comes on the next read, at once
            self.start += len(raw)
            self.more = True
        else:
            self.start = int(size)
        # Split bytes, not text: a character cut at a read's end ("→", "──")
        # is decoded whole, with the rest of its line, on the next read.
        lines = (self.partial + raw).split(b"\n")
        # An unfinished last line waits for the rest, unless nothing more comes.
        self.partial = lines.pop() if self.more else b""
        return [TIMESTAMP.sub("", line.decode("utf-8", errors="replace").rstrip("\r")) for line in lines]


def pair_sessions(sessions, groups, submitted, pairs):
    """{session: group} for the sessions the console proves, {} on any
    contradiction.

    The pipeline submits its groups one at a time, in one loop, and then logs
    "Tracking sessions: ..." in that order (ucicd-pipeline 05-test-common.sh),
    so sessions is the submission order. submitted lists the "Submitting group"
    lines that survived, in order; pairs the (group, session) of a "Submitting
    group" line directly followed by its "-> session(s)" line. groups is the
    set the build runs (from the batch), or empty when unknown.

    Proven: a session of a pair (an anchor); the surviving groups between two
    anchors when they exactly fill the sessions between them; and, when one
    group's line was lost and one session is left, that one. Nothing relies on
    the order of the batch's groups. Without groups only the anchors are
    proven: a group whose submit failed (no session) could shift the rest."""
    n = len(sessions)
    known = set(groups or ())
    if known:
        if len(known) != n:
            return {}  # not this build's groups, or a group whose submit failed
        submitted = [g for g in submitted if g in known]
        pairs = [(g, s) for g, s in pairs if g in known]
    if len(set(submitted)) != len(submitted) or len(submitted) > n:
        return {}
    where = {s: i for i, s in enumerate(sessions)}
    rank = {g: i for i, g in enumerate(submitted)}
    anchors = {}
    for g, s in pairs:
        if s not in where or g not in rank or anchors.get(g, where[s]) != where[s]:
            return {}
        anchors[g] = where[s]
    anchored = sorted(anchors, key=rank.get)
    positions = [anchors[g] for g in anchored]
    if positions != sorted(positions) or len(set(positions)) != len(positions):
        return {}
    mapping = {sessions[anchors[g]]: g for g in anchored}
    if not known:
        return mapping
    lost = n - len(submitted)
    open_gaps = []
    bounds = [(-1, -1)] + [(anchors[g], rank[g]) for g in anchored] + [(n, len(submitted))]
    for (lo, lo_rank), (hi, hi_rank) in zip(bounds, bounds[1:]):
        between, slots = submitted[lo_rank + 1:hi_rank], list(range(lo + 1, hi))
        if len(between) > len(slots):
            return {}
        if len(between) == len(slots):
            mapping.update((sessions[k], g) for k, g in zip(slots, between))
        else:
            open_gaps.append((slots, between))
    if sum(len(slots) - len(between) for slots, between in open_gaps) != lost:
        return {}
    if lost == 1 and len(open_gaps) == 1 and len(open_gaps[0][0]) == 1:
        (missing,) = known - set(submitted)
        mapping[sessions[open_gaps[0][0][0]]] = missing
    return mapping


class Follower:
    def __init__(self, console, run_id, cp, names=None):
        self.console, self.run_id, self.cp = console, run_id, cp
        self.names = dict(names or {})  # group id -> the batch's key (zh-CN/foo)
        self.stage = self.machine = None
        self.submitted, self.pairs, self.last_group = [], [], None
        self.session_group = {}   # sess-N -> group id
        self.done = self.total = None
        self.reported = set()     # rows already printed
        self.results_ok = bool(run_id and cp)
        self.results_failing = False

    def on_line(self, line):
        """What one console line says; True when a test has just ended."""
        if not line.strip():
            return False  # a blank line is not a lost one: "directly followed" skips it
        last_group, self.last_group = self.last_group, None
        if m := STAGE.match(line):
            if m.group(1) != self.stage:
                self.stage = m.group(1)
                say(f"stage {self.stage}")
        elif m := MACHINE.search(line):
            if m.group(1) != self.machine:
                self.machine = m.group(1)
                say(f"machine {self.machine}")
        elif m := GROUP.match(line):
            self.submitted.append(m.group(1))
            self.last_group = m.group(1)
        elif m := SESSIONS.match(line):
            sessions = SESSION_ID.findall(m.group(1))
            if last_group and len(sessions) == 1:
                self.pairs.append((last_group, sessions[0]))
        elif m := TRACKING.match(line):
            sessions = SESSION_ID.findall(m.group(1))
            mapping = pair_sessions(sessions, list(self.names), self.submitted, self.pairs)
            if len(mapping) < len(sessions):
                say(f"{len(mapping)} of {len(sessions)} sessions matched to their playbook; "
                    "the others show by session id, and the next step names them all")
            self.session_group.update(mapping)
            self.submitted, self.pairs = [], []
        elif m := COUNT.search(line):
            done, total = int(m.group(3)), int(m.group(4))
            # A job that starts late finds tests already done: report them too.
            ended = done != self.done and (self.done is not None or done > 0)
            if self.done is None:
                say(f"{done}/{total} playbooks done")
            self.done, self.total = done, total
            return ended
        return False

    def report_results(self, retry_seconds=RESULTS_RETRY_SECONDS):
        """Print each test result recorded since the last call. A failed read
        is said once and tried again next time."""
        if not self.results_ok:
            return
        try:
            answer = trigger.api(self.cp, "GET", f"/runs/{urllib.parse.quote(self.run_id, safe='')}/tests",
                                 retry_seconds=retry_seconds)
        except trigger.Refused as exc:
            say(f"test results not readable ({exc}); the next step shows every outcome")
            self.results_ok = False  # a definite refusal: asking again changes nothing
            return
        except ValueError as exc:
            if not self.results_failing:
                say(f"test results unavailable for now ({exc}); trying again when the next test ends")
            self.results_failing = True
            return
        self.results_failing = False
        fresh = []
        for test in answer.get("tests") or []:
            # A row whose outcome or attempt changes is printed again.
            key = json.dumps([test.get(k) for k in
                              ("execution_id", "suite", "name", "attempt", "outcome", "recorded_at")])
            if key not in self.reported:
                self.reported.add(key)
                fresh.append(test)
        for test in sorted(fresh, key=lambda t: t.get("recorded_at") or ""):
            sid = SESSION_ID.search(test.get("execution_id") or test.get("suite") or "")
            group = self.session_group.get(sid.group(1)) if sid else None
            name = (self.names.get(group) or group) if group else (test.get("suite") or test.get("name") or "?")
            outcome = (test.get("outcome") or "?").upper()
            extra = []
            if (test.get("attempt") or 1) > 1:
                extra.append(f"attempt {test['attempt']}")
            if test.get("flaky"):
                extra.append("flaky")
            if self.total:
                extra.append(f"{self.done}/{self.total} done")
            say(f"{outcome:<15}{name:<45}" + (f" ({', '.join(extra)})" if extra else ""))

    def poll(self):
        ended = any([self.on_line(line) for line in self.console.read()])
        if not self.console.more:
            self.report_results(FINAL_RESULTS_RETRY_SECONDS)
        elif ended or self.results_failing:
            self.report_results()


def batch_names():
    """{group id: member key} of the batch the build runs (FOLLOW_BATCHES[BATCH_ID]), or {}."""
    try:
        batch = json.loads(os.environ.get("FOLLOW_BATCHES") or "{}").get(os.environ.get("BATCH_ID", "")) or {}
        return {group_id(key): key for key in batch.get("playbooks") or []}
    except (ValueError, AttributeError, TypeError):
        return {}


def main():
    build_url = os.environ.get("STARTED_BUILD_URL", "")
    user = os.environ.get("ORCHESTRAI_PIPELINE_USER", "")
    token = os.environ.get("ORCHESTRAI_PIPELINE_TOKEN", "")
    if not (build_url and user and token):
        return
    run_id, cp = os.environ.get("RUN_ID", ""), None
    if run_id:
        try:
            cp = trigger.control_plane()
        except ValueError:
            cp = None
    follower = Follower(Console(build_url, user, token), run_id, cp, batch_names())
    config = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "orchestrai-config.yml")
    try:
        limit = trigger.max_duration_minutes(config) * 60 + WIND_DOWN_SECONDS
    except (OSError, ValueError):
        limit = 9 * 3600
    deadline, failures = time.monotonic() + limit, 0
    say(f"following {build_url}")
    while time.monotonic() < deadline:
        try:
            follower.poll()
            failures = 0
        except (OSError, ValueError) as exc:  # urllib errors are OSErrors
            failures += 1
            if failures == 10:  # ~5 min unreadable: stop; the wait goes on without us
                say(f"stopped following: build console unreadable ({type(exc).__name__}: {exc})")
                return
        if not follower.console.more:
            if follower.total:
                say(f"build finished: {follower.done}/{follower.total} done")
            return
        if not follower.console.truncated:  # catching up: read on at once
            time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as exc:  # noqa: BLE001 -- progress output must never fail the job
        print(f"[live] stopped: {type(exc).__name__}: {exc}", file=sys.stderr)
