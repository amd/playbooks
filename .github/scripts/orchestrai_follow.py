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
    1/27 playbooks done
    PASSED         comfyui-image-gen
    3/27 playbooks done
    ERROR          zh-CN/hermes-lemonade-server

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
outcomes are not shown, the rest is), FOLLOW_PLAYBOOKS (the JSON list of the
batch's members, e.g. ["foo", "zh-CN/foo"]: which groups the build runs, not
their order), FOLLOW_MACHINES_PER_HW_GROUP (the run's machines_per_hw_group;
above 1 a group may get several sessions, and only adjacent lines name them).
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
# A job that starts late reads hours of console at once: give it time.
HTTP_TIMEOUT = 120
# The longest a build can run (max_duration) plus the time it takes to wind down.
WIND_DOWN_SECONDS = 30 * 60
# How long one read of the test results retries; a failed read is tried again
# on the next polls after a test ends (CATCH_UP_POLLS), and when the build ends.
RESULTS_RETRY_SECONDS = 60
# After a test ends, the results are read on each poll until its row is there,
# at most this many polls (5 min).
CATCH_UP_POLLS = 10
# After the build: one read retrying FINAL_RESULTS_RETRY_SECONDS, then reads
# every FINAL_POLL_SECONDS for FINAL_CATCH_UP_SECONDS while rows are missing.
# At worst, from the build's end: a poll's sleep (30 s), a console read
# (HTTP_TIMEOUT), that read (30 s plus one OIDC and one API call, 60 s), the
# catch-up (90 s) and its last read (15 s plus 60 s): about 7 min, within the
# 8 min orchestrai_wait_build.sh waits before it stops the follower. Normally
# the rows are there and it ends within seconds.
FINAL_RESULTS_RETRY_SECONDS = 30
FINAL_POLL_SECONDS = 15
FINAL_CATCH_UP_SECONDS = 90

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
        self.start, self.more, self.partial = 0, True, b""

    def read(self):
        """New complete lines since the last read; sets self.more. Raises one
        of OSError, http.client.HTTPException or ValueError (a redirect is an
        HTTPError, an answer that is not the build's console a ValueError);
        main() counts any of them as a failed poll. The whole new part is read: start and
        X-Text-Size count the raw log, which Jenkins sends with its notes
        stripped, so only Jenkins can say where the next read starts."""
        req = urllib.request.Request(f"{self.url}?start={self.start}",
                                     headers={"Authorization": self.auth})
        with self.opener.open(req, timeout=HTTP_TIMEOUT) as resp:
            raw = resp.read()
            size = resp.headers.get("X-Text-Size", "")
            more = resp.headers.get("X-More-Data", "")
        # A login page or a proxy's answer: not the console, and not its end.
        if not size.isdigit():
            raise ValueError("the answer is not a Jenkins console (no X-Text-Size)")
        self.more = more.lower() == "true"
        self.start = int(size)
        # Split bytes, not text: a character cut at a read's end ("→", "──")
        # is decoded whole, with the rest of its line, on the next read.
        lines = (self.partial + raw).split(b"\n")
        # An unfinished last line waits for the rest, unless nothing more comes.
        self.partial = lines.pop() if self.more else b""
        return [TIMESTAMP.sub("", line.decode("utf-8", errors="replace").rstrip("\r")) for line in lines]


def pair_sessions(sessions, groups, submitted, pairs, one_each=True):
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
    the order of the batch's groups. Unless every group of the batch has a
    session (no batch, or a group whose submit failed), and unless each has
    exactly one (one_each), only the anchors are proven: a group without a
    session, or with two, could shift the rest."""
    n = len(sessions)
    known = set(groups or ())
    if known:
        submitted = [g for g in submitted if g in known]
        pairs = [(g, s) for g, s in pairs if g in known]
    complete = one_each and bool(known) and len(known) == n
    if len(set(submitted)) != len(submitted) or (complete and len(submitted) > n):
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
    if not complete:
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
    if lost == 1 and len(open_gaps) == 1 and len(open_gaps[0][0]) == 1:
        (missing,) = known - set(submitted)
        mapping[sessions[open_gaps[0][0][0]]] = missing
    return mapping


class Follower:
    def __init__(self, console, run_id, cp, names=None, one_each=True):
        self.console, self.run_id, self.cp = console, run_id, cp
        self.names = dict(names or {})  # group id -> the batch's key (zh-CN/foo)
        # Each group runs in one session (one machine per hardware group); a
        # "-> session(s)" line naming two turns this off for the build.
        self.one_each = one_each
        self.stage = self.machine = None
        self.submitted, self.pairs, self.last_group = [], [], None
        self.session_group = {}   # sess-N -> group id
        self.done = self.total = None
        self.reported = set()     # rows already printed
        self.results_ok = bool(run_id and cp)
        self.results_failing = False
        # Polls left to read the results again after a test ended: its row can
        # be recorded a little after the console's count moves.
        self.catch_up = 0
        self.recorded = 0         # rows in the last answer

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
            if len(sessions) > 1:
                self.one_each = False
                if last_group:  # proven by the adjacent lines, all of them
                    self.session_group.update((s, last_group) for s in sessions)
            elif last_group:
                self.pairs.append((last_group, sessions[0]))
        elif m := TRACKING.match(line):
            sessions = SESSION_ID.findall(m.group(1))
            if self.submitted or self.pairs or not all(s in self.session_group for s in sessions):
                # A repeated line with no new evidence keeps what was proven.
                mapping = pair_sessions(sessions, list(self.names), self.submitted, self.pairs, self.one_each)
                mapping.update((s, self.session_group[s]) for s in sessions if s in self.session_group)
                if len(mapping) < len(sessions) and (self.submitted or self.pairs):
                    say(f"{len(mapping)} of {len(sessions)} sessions matched to their playbook; "
                        "the others show by session id, and the next step names them all")
                self.session_group.update(mapping)
            self.submitted, self.pairs = [], []
        elif m := COUNT.search(line):
            done, total = int(m.group(3)), int(m.group(4))
            # A job that starts late finds tests already done: report them too.
            ended = done != self.done and (self.done is not None or done > 0)
            if done != self.done or total != self.total:
                say(f"{done}/{total} playbooks done")
            self.done, self.total = done, total
            return ended
        return False

    def report_results(self, retry_seconds=RESULTS_RETRY_SECONDS):
        """Print each test result recorded since the last call. A failed read
        is said once and tried again when the next test ends or the build does.
        The answer is every test of the run: the CI API and the Portal behind
        it do not page this list."""
        if not self.results_ok:
            return
        try:
            answer = trigger.api(self.cp, "GET", f"/runs/{urllib.parse.quote(self.run_id, safe='')}/tests",
                                 retry_seconds=retry_seconds)
        except ValueError as exc:
            # 401/403 is final, even when an earlier attempt of the same call
            # failed (then api() raises a plain ValueError, not Refused).
            if re.search(r"HTTP 40[13]\b", str(exc)):
                say(f"test results not readable ({exc}); the next step shows every outcome")
                self.results_ok = False  # not allowed: asking again changes nothing
                return
            if not self.results_failing:
                say(f"test results unavailable for now ({exc}); trying again when the next test ends")
            self.results_failing = True
            return
        self.results_failing = False
        rows = answer.get("tests") if isinstance(answer.get("tests"), list) else []
        rows = [t for t in rows if isinstance(t, dict)]
        self.recorded = len(rows)
        if not self.behind():
            self.catch_up = 0  # every test the console counts is recorded
        fresh = []
        for test in rows:
            # A row whose outcome or attempt changes is printed again.
            key = json.dumps([test.get(k) for k in
                              ("execution_id", "suite", "name", "attempt", "outcome", "recorded_at")])
            if key not in self.reported:
                self.reported.add(key)
                fresh.append(test)
        for test in sorted(fresh, key=lambda t: str(t.get("recorded_at") or "")):
            sid = SESSION_ID.search(f"{test.get('execution_id') or ''} {test.get('suite') or ''}")
            group = self.session_group.get(sid.group(1)) if sid else None
            name = (self.names.get(group) or group) if group else (test.get("suite") or test.get("name") or "?")
            outcome = str(test.get("outcome") or "?").upper()
            attempt = test.get("attempt")
            extra = []
            if isinstance(attempt, int) and attempt > 1:
                extra.append(f"attempt {attempt}")
            if test.get("flaky"):
                extra.append("flaky")
            say((f"{outcome:<15}{name:<45}" + (f" ({', '.join(extra)})" if extra else "")).rstrip())

    def behind(self):
        """True while fewer results are recorded than the console counts done."""
        return self.results_ok and self.recorded < (self.done or 0)

    def poll(self):
        ended = any([self.on_line(line) for line in self.console.read()])
        if ended:
            self.catch_up = CATCH_UP_POLLS
        if not self.console.more:
            self.report_results(FINAL_RESULTS_RETRY_SECONDS)
        elif ended:
            self.report_results()
        elif self.catch_up > 0:  # a test ended but its row was not there yet
            self.catch_up -= 1
            self.report_results()

    def finish(self, seconds):
        """After the build: the last rows can be recorded a little after its
        end; read again, for at most seconds, until they are all there."""
        end = time.monotonic() + seconds
        while self.behind() and time.monotonic() < end:
            time.sleep(FINAL_POLL_SECONDS)
            self.report_results(FINAL_POLL_SECONDS)


def batch_names():
    """{group id: member key} of the batch the build runs (FOLLOW_PLAYBOOKS), or {}."""
    try:
        members = json.loads(os.environ.get("FOLLOW_PLAYBOOKS") or "[]")
        if not isinstance(members, list):
            return {}
        return {group_id(key): key for key in members if isinstance(key, str)}
    except (ValueError, TypeError):
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
    config = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "orchestrai-config.yml")
    # More than one machine per hardware group may give a group several
    # sessions. The same value the trigger uses: the input, else the config's.
    machines = os.environ.get("FOLLOW_MACHINES_PER_HW_GROUP", "").strip() or default_machines_per_hw_group(config)
    follower = Follower(Console(build_url, user, token), run_id, cp, batch_names(), machines in ("", "1"))
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
        except Exception as exc:  # noqa: BLE001 -- a bad answer must not end the progress
            failures += 1
            if failures == 10:  # ~5 min unreadable: stop; the wait goes on without us
                say(f"stopped following: build console unreadable ({type(exc).__name__}: {exc})")
                return
        if not follower.console.more:
            follower.finish(FINAL_CATCH_UP_SECONDS)
            if follower.total:
                say(f"build finished: {follower.done}/{follower.total} done")
            return
        time.sleep(POLL_SECONDS)


def default_machines_per_hw_group(config_path):
    """run_settings.default_machines_per_hw_group, read without PyYAML, or ''."""
    try:
        text = open(config_path, encoding="utf-8").read()
    except OSError:
        return ""
    m = re.search(r"^\s*default_machines_per_hw_group:\s*(\d+)", text, re.M)
    return m.group(1) if m else ""


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as exc:  # noqa: BLE001 -- progress output must never fail the job
        print(f"[live] stopped: {type(exc).__name__}: {exc}", file=sys.stderr)
