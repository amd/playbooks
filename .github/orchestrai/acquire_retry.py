#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
OrchestrAI acquisition-timeout retry
====================================

A batch build can fail before it touches any hardware: the pipeline asks the
MAAS broker for machines and gives up after its acquire timeout (2400 s by
default) when none free up. That is a fleet-capacity failure, not a playbook
failure, so the trigger resubmits the batch -- a bounded number of times --
instead of letting every playbook in it report as failed.

Detection uses two fixed lines stages/04-provision.sh writes to the build
console:

    [provision] Acquired <n> machine(s) for <pipeline-id>
    [provision] ERROR: Timed out waiting for machines after <n>s

A build is resubmitted only when the timeout line is present AND no "Acquired"
line ever appeared. Acquisition is all-or-nothing per level (a failed acquire
rolls back whatever it got), so that combination proves nothing was leased and
nothing ran, and resubmitting cannot repeat a test. A build that acquired
anything -- including a multi-level plan that acquired level 1 and then timed
out on level 2 -- is never resubmitted.

The pipeline cancels its broker queue ticket before it times out, and a batch
is resubmitted only after its previous build has ended, so there is never more
than one live build per batch.

This runs in the trigger job, once per batch. It cannot live in the
per-playbook wait jobs: several playbooks share one batch build, and each of
them resubmitting would put duplicate builds on the same scarce hardware.

If either console line changes shape this degrades safely. No timeout line
means no retry (the behaviour before this module existed); no "Acquired" line
means a batch is watched until its build ends or its watch window expires.

The module itself is stdlib-only; PyYAML remains confined to the trigger and
configuration layer.
"""

import json
import re
import sys
import time
import urllib.request
from dataclasses import dataclass, field

ACQUIRED_RE = re.compile(r"\[provision\] Acquired \d+ machine\(s\) for ")
ACQUIRE_TIMEOUT_RE = re.compile(
    r"\[provision\] ERROR: Timed out waiting for machines after (\d+)s")

POLL_SECONDS = 30
# How long one attempt is watched before giving up on seeing it acquire. The
# shipped configuration now waits up to 3600 s in the broker, so keep another
# ten minutes for the pipeline queue and the stages before provisioning. Four
# attempts at this window still fit inside GitHub's six-hour job limit.
ATTEMPT_WINDOW_SECONDS = 4200
# Headroom per attempt for resubmitting: trigger() may wait up to 10 minutes
# for Jenkins to start the new build.
RESUBMIT_ALLOWANCE_SECONDS = 600
# Each attempt can hold the trigger job for up to ~70 minutes, and GitHub ends a
# job at 6 hours. Four attempts (three retries) stay inside that.
MAX_RETRIES = 3
# Longest marker line still recognised when a console chunk boundary splits it.
_TAIL_CHARS = 512
_HTTP_TIMEOUT = 30


def check_retries(value):
    """Return an error string if ``value`` is not a valid acquire_retries."""
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= MAX_RETRIES:
        return f"run_settings.acquire_retries must be an integer 0-{MAX_RETRIES}, got {value!r}"
    return None


def fetch_building(build_url, auth):
    """True while Jenkins still reports the build as running."""
    req = urllib.request.Request(f"{build_url}api/json?tree=building")
    req.add_header("Authorization", auth)
    with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT) as r:
        return bool(json.loads(r.read().decode("utf-8", "replace")).get("building", True))


def fetch_console(build_url, start, auth):
    """Return (new console text since ``start``, next offset)."""
    req = urllib.request.Request(f"{build_url}logText/progressiveText?start={start}")
    req.add_header("Authorization", auth)
    with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT) as r:
        body = r.read()
        size = (r.headers.get("X-Text-Size") or "").strip()
    return body.decode("utf-8", "replace"), int(size) if size.isdigit() else start + len(body)


@dataclass
class BatchWatch:
    batch_id: str
    url: str
    started: float
    attempt: int = 1
    offset: int = 0
    tail: str = ""
    acquired: bool = False
    timeout_seconds: int = 0
    fetch_errors: int = 0
    outcome: str = ""
    earlier_urls: list = field(default_factory=list)

    def scan(self, chunk):
        # Search across the previous chunk's tail so a marker split by a chunk
        # boundary is still seen.
        window = self.tail + chunk
        if ACQUIRED_RE.search(window):
            self.acquired = True
        timed_out = ACQUIRE_TIMEOUT_RE.search(window)
        if timed_out:
            self.timeout_seconds = int(timed_out.group(1))
        self.tail = window[-_TAIL_CHARS:]

    def restart(self, url, now):
        self.earlier_urls.append(self.url)
        self.url = url
        self.started = now
        self.attempt += 1
        self.offset = 0
        self.tail = ""
        self.acquired = False
        self.timeout_seconds = 0
        self.fetch_errors = 0


def _log(message):
    print(message, file=sys.stderr)


def _step(watch, resubmit, retries, fetch_building, fetch_console, clock,
          attempt_window, log):
    try:
        # Building state first: if the build has already ended, the console read
        # that follows is complete, so a marker printed at the very end of the
        # build cannot be missed.
        building = fetch_building(watch.url)
        chunk, watch.offset = fetch_console(watch.url, watch.offset)
    except Exception as exc:
        # Jenkins briefly unreachable. Try again next poll; the attempt window
        # and the overall deadline bound how long that can go on.
        watch.fetch_errors += 1
        if watch.fetch_errors == 1:
            log(f"  {watch.batch_id}: could not poll {watch.url} ({exc}); will keep trying")
        return
    watch.fetch_errors = 0
    watch.scan(chunk)

    if watch.acquired:
        watch.outcome = "acquired"
    elif watch.timeout_seconds:
        if building:
            return  # never have two live builds for one batch
        if watch.attempt > retries:
            watch.outcome = "retries-exhausted"
            return
        log(f"::warning::OrchestrAI batch {watch.batch_id}: no machine was acquired within "
            f"{watch.timeout_seconds}s (attempt {watch.attempt} of {retries + 1}). Nothing ran; "
            f"resubmitting. Timed-out build: {watch.url}")
        new_url = resubmit(watch.batch_id)
        if not new_url:
            watch.outcome = "resubmit-failed"
            return
        watch.restart(new_url, clock())
        log(f"  {watch.batch_id}: attempt {watch.attempt}: {new_url}")
    elif not building:
        # Ended without reaching acquisition, or finished normally: either way
        # not an acquire timeout, and the wait jobs report it as usual.
        watch.outcome = "finished"
    elif clock() - watch.started > attempt_window:
        watch.outcome = "watch-expired"


def watch_acquisition(build_urls, resubmit, *, retries, fetch_building, fetch_console,
                      clock=time.monotonic, sleep=time.sleep, poll=POLL_SECONDS,
                      attempt_window=ATTEMPT_WINDOW_SECONDS, log=_log):
    """Watch every batch until it acquires machines, ends, or runs out of retries.

    ``resubmit(batch_id)`` submits that batch again and returns the new build
    URL, or None if it could not be created. Returns {batch_id: BatchWatch};
    each watch's ``url`` is the build the playbook jobs should wait on.
    """
    start = clock()
    watches = {bid: BatchWatch(bid, url, start) for bid, url in build_urls.items()}
    deadline = start + (retries + 1) * (attempt_window + RESUBMIT_ALLOWANCE_SECONDS)
    while True:
        pending = [w for w in watches.values() if not w.outcome]
        if not pending:
            break
        if clock() >= deadline:
            for w in pending:
                w.outcome = "watch-expired"
            break
        for w in pending:
            _step(w, resubmit, retries, fetch_building, fetch_console, clock,
                  attempt_window, log)
        if any(not w.outcome for w in watches.values()):
            sleep(poll)
    return watches


def report(watches, retries):
    """Return (annotation lines, markdown summary) for batches that needed retries."""
    annotations = []
    rows = []
    for w in watches.values():
        if w.outcome == "retries-exhausted":
            annotations.append(
                f"::error::OrchestrAI batch {w.batch_id}: no machine could be acquired in "
                f"{w.attempt} attempts ({w.timeout_seconds}s each). This is fleet capacity, "
                f"not a playbook failure; its playbooks will report the last build: {w.url}")
        elif w.outcome == "resubmit-failed":
            annotations.append(
                f"::error::OrchestrAI batch {w.batch_id}: acquisition timed out and the "
                f"resubmission could not be created; its playbooks will report the "
                f"timed-out build: {w.url}")
        if w.attempt > 1 or w.outcome in ("retries-exhausted", "resubmit-failed"):
            earlier = ", ".join(f"[{i}]({u})" for i, u in enumerate(w.earlier_urls, 1))
            rows.append(f"| `{w.batch_id}` | {w.attempt} | {w.outcome} | {earlier or '-'} |")
    if not rows:
        return annotations, ""
    lines = [
        "### OrchestrAI acquire retries",
        "",
        f"Batches whose build could not acquire machines before the pipeline's acquire "
        f"timeout were resubmitted (up to {retries} retries). Nothing had run on any "
        f"machine in the timed-out builds.",
        "",
        "| Batch | Attempts | Outcome | Timed-out builds |",
        "|---|---:|---|---|",
        *rows,
        "",
    ]
    return annotations, "\n".join(lines)
