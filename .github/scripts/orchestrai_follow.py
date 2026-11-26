#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
Show a batch's progress live in its Test job's log
==================================================

orchestrai_wait_build.sh starts this in the background while it waits for the
batch's pipeline build. It prints, as they happen:

    stage 05-L4-sys
    machine MNB-UCICD-DT494
    PASSED  comfyui-image-gen                 (1/27 done)
    ERROR   hermes-lemonade-server            (3/27 done)

It reads the build's console as it grows (Jenkins progressiveText, only the new
part on each poll) for the stage and the machine, and the run's test results
(CI API GET /runs/{id}/tests, results:read) for each outcome as it is recorded.

A test row names only the runner test and its pipeline session, so the
playbook comes from the console. The pipeline submits the plan's groups one
after another and then logs "Tracking sessions: sess-A,sess-B,..." in that
order, so the sessions in that order are the batch's groups in plan order
(FOLLOW_BATCHES, BATCH_ID). Other processes write to the console at the same
time and can garble a line, so that pairing is used only when the console's
own "Submitting group X" lines that survived agree with it: their order, and
every "Submitting group X" line directly followed by its "-> session(s)" line.
Otherwise the outcomes are shown by session: never under a wrong name.

It only prints. orchestrai_wait_build.sh decides when the build is done, and
the verdict step decides each playbook's result; nothing here can fail the job.

Inputs (env): STARTED_BUILD_URL, ORCHESTRAI_PIPELINE_USER/TOKEN (the build's
console), RUN_ID and ORCHESTRAI_V2_* (the run's test results; without them the
outcomes are not shown, the rest is), FOLLOW_BATCHES and BATCH_ID (the
trigger's batches, {batch_id: {"playbooks": [...]}}: the groups' plan order).
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
# in POLL_SECONDS, and a job that starts late catches up over a few polls.
MAX_CHUNK = 4 << 20
# The longest a build can run (max_duration) plus the time it takes to wind down.
WIND_DOWN_SECONDS = 30 * 60

TIMESTAMP = re.compile(r"^\[\d{4}-\d\d-\d\dT[\d:.]+Z\]\s?")
STAGE = re.compile(r"^── (\S.*?) ──")
MACHINE = re.compile(r"Actor started on (\S+)")
GROUP = re.compile(r"Submitting group (\S+)")
SESSIONS = re.compile(r"→ session\(s\): (.+)$")
TRACKING = re.compile(r"Tracking sessions: (\S+)")
COUNT = re.compile(r"\b(\d+) active, (\d+) done \((\d+)/(\d+) tests\)")
SESSION_ID = re.compile(r"(sess-\d+)")


def say(line):
    print(f"[live {time.strftime('%H:%M', time.gmtime())}Z] {line}", flush=True)


def playbook_name(group):
    """playbook-zh-CN-foo -> zh-CN-foo: the batch's own name for it."""
    return group[len("playbook-"):] if group.startswith("playbook-") else group


class Console:
    """The build's console, read a new part at a time."""

    def __init__(self, build_url, user, token):
        self.url = build_url.rstrip("/") + "/logText/progressiveText"
        self.auth = "Basic " + base64.b64encode(f"{user}:{token}".encode()).decode()
        self.start, self.more, self.partial = 0, True, ""

    def read(self):
        """New complete lines since the last read; sets self.more."""
        req = urllib.request.Request(f"{self.url}?start={self.start}",
                                     headers={"Authorization": self.auth})
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            raw = resp.read(MAX_CHUNK)
            size = resp.headers.get("X-Text-Size", "")
            self.more = resp.headers.get("X-More-Data", "").lower() == "true"
        if len(raw) >= MAX_CHUNK:  # a short read: the rest comes on the next poll
            self.start += len(raw)
            self.more = True
        else:
            self.start = int(size) if size.isdigit() else self.start + len(raw)
        lines = (self.partial + raw.decode("utf-8", errors="replace")).split("\n")
        # An unfinished last line waits for the rest, unless nothing more comes.
        self.partial = lines.pop() if self.more else ""
        return [TIMESTAMP.sub("", line.rstrip("\r")) for line in lines]


def is_subsequence(items, sequence):
    it = iter(sequence)
    return all(item in it for item in items)


def pair_sessions(sessions, groups, submitted, pairs):
    """{session: group}: the sessions in submission order paired with the
    first candidate group order that the console's surviving lines confirm,
    or {} when none does. submitted: the "Submitting group" lines that
    survived, in order; pairs: (group, session) seen on two adjacent lines."""
    candidates = [c for c in (groups, sorted(groups), submitted) if c]
    for order in candidates:
        if len(order) != len(sessions) or len(set(order)) != len(order):
            continue
        mapping = dict(zip(sessions, order))
        if is_subsequence(submitted, order) and all(mapping.get(s) == g for g, s in pairs):
            return mapping
    return {}


class Follower:
    def __init__(self, console, run_id, cp, groups=()):
        self.console, self.run_id, self.cp = console, run_id, cp
        self.groups = list(groups)  # the batch's plan groups, in plan order
        self.stage = self.machine = None
        self.submitted, self.pairs, self.last_group = [], [], None
        self.session_group = {}   # sess-N -> playbook-X
        self.done = self.total = None
        self.reported = set()     # execution ids already printed
        self.results_ok = bool(run_id and cp)

    def on_line(self, line):
        """What one console line says; True when a test has just ended."""
        last_group, self.last_group = self.last_group, None
        if m := STAGE.match(line):
            if m.group(1) != self.stage:
                self.stage = m.group(1)
                say(f"stage {self.stage}")
        elif m := MACHINE.search(line):
            if m.group(1) != self.machine:
                self.machine = m.group(1)
                say(f"machine {self.machine}")
        elif m := GROUP.search(line):
            self.submitted.append(m.group(1))
            self.last_group = m.group(1)
        elif m := SESSIONS.search(line):
            sessions = SESSION_ID.findall(m.group(1))
            if last_group and len(sessions) == 1:
                self.pairs.append((last_group, sessions[0]))
        elif m := TRACKING.search(line):
            sessions = SESSION_ID.findall(m.group(1))
            mapping = pair_sessions(sessions, self.groups, self.submitted, self.pairs)
            if not mapping:
                say("playbook names could not be matched to the pipeline's sessions; "
                    "outcomes below are by session, the next step names them")
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

    def report_results(self):
        """Print each test result recorded since the last call."""
        if not self.results_ok:
            return
        try:
            answer = trigger.api(self.cp, "GET", f"/runs/{urllib.parse.quote(self.run_id, safe='')}/tests",
                                 retry_seconds=60)
        except ValueError as exc:
            say(f"test results unavailable ({exc}); outcomes show in the next step")
            self.results_ok = False  # say it once, not every poll
            return
        rows = [t for t in answer.get("tests") or [] if t.get("execution_id") not in self.reported]
        for test in sorted(rows, key=lambda t: t.get("recorded_at") or ""):
            self.reported.add(test.get("execution_id"))
            sid = SESSION_ID.search(test.get("execution_id") or test.get("suite") or "")
            group = self.session_group.get(sid.group(1)) if sid else None
            name = playbook_name(group) if group else (test.get("suite") or test.get("name") or "?")
            outcome = (test.get("outcome") or "?").upper()
            extra = []
            if (test.get("attempt") or 1) > 1:
                extra.append(f"attempt {test['attempt']}")
            if test.get("flaky"):
                extra.append("flaky")
            count = f"{len(self.reported)}/{self.total} done" if self.total else f"{len(self.reported)} done"
            say(f"{outcome:<15}{name:<45} ({', '.join(extra + [count])})")

    def poll(self):
        ended = any([self.on_line(line) for line in self.console.read()])
        if ended or not self.console.more:
            self.report_results()


def batch_groups():
    """The batch's plan groups in plan order (FOLLOW_BATCHES[BATCH_ID]), or []."""
    try:
        batch = json.loads(os.environ.get("FOLLOW_BATCHES") or "{}").get(os.environ.get("BATCH_ID", "")) or {}
        return [group_id(key) for key in batch.get("playbooks") or []]
    except (ValueError, AttributeError, TypeError):
        return []


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
    follower = Follower(Console(build_url, user, token), run_id, cp, batch_groups())
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
            if failures == 10:  # ~5 min unreachable: stop; the wait goes on without us
                say(f"stopped following: build console unreachable ({type(exc).__name__})")
                return
        if not follower.console.more:
            if follower.total:
                say(f"build finished: {len(follower.reported)}/{follower.total} results recorded")
            return
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as exc:  # noqa: BLE001 -- progress output must never fail the job
        print(f"[live] stopped: {type(exc).__name__}: {exc}", file=sys.stderr)
