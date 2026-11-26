#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
One GitHub check run per OrchestrAI batch
=========================================
Wait for OrchestrAI holds one runner for the whole workflow run, and GitHub
shows the batch jobs only once it is done. Until then this keeps one check run
per batch on the tested commit (the pull request's Checks tab, or the commit
on main), named after the batch, with its OrchestrAI run linked:

    Detect & Trigger   --create   queued, "Waiting for machines"
    Wait for OrchestrAI           updates it as the run moves (orchestrai_trigger.py
                                  --await-runs calls Updater.update each poll)
    Test job           --finish   the batch's verdict from test-results/batch.json
    cancel paths       --cancel   cancelled, unless it already finished

The checks are for visibility only: Test Gate (Required) still decides the
run, and every failure here is a warning that never fails a job.

Env:
    GITHUB_TOKEN        token with checks: write
    GITHUB_REPOSITORY, GITHUB_API_URL, GITHUB_SERVER_URL, GITHUB_RUN_ID
    CHECK_PREFIX        check name prefix (default "OrchestrAI")

--create:  BATCH_MATRIX (the batch matrix), RUN_URLS ({batch_id: run URL}),
           HEAD_SHA -> check_ids={batch_id: check run id} in $GITHUB_OUTPUT
--finish FILE:  CHECK_ID, BATCH_JSON (the matrix entry), RUN_URL; FILE is the
           batch's batch.json (missing: the batch has no results)
--cancel:  CHECK_IDS: a {batch_id: id} map, or ids separated by spaces
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API_TIMEOUT = 30
ATTEMPTS = 3
TERMINAL = {"passed", "failed", "unstable", "cancelled", "error"}
# GitHub caps a check run's output summary at 65535 characters.
SUMMARY_LIMIT = 60000


def warn(msg):
    print(f"::warning::{msg}", file=sys.stderr)


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def github(method, path, body=None):
    """Call the GitHub REST API; return the JSON body, or None after a warning.
    Network errors, 5xx and rate limits are retried a few times."""
    token = os.environ.get("GITHUB_TOKEN", "")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not token or not repo:
        warn("check runs need GITHUB_TOKEN and GITHUB_REPOSITORY")
        return None
    url = f"{os.environ.get('GITHUB_API_URL', 'https://api.github.com')}/repos/{repo}{path}"
    data = None if body is None else json.dumps(body).encode()
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28", "Content-Type": "application/json"}
    for attempt in range(ATTEMPTS):
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=API_TIMEOUT) as resp:
                raw = resp.read()
            return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            retry = exc.code >= 500 or exc.code == 429 or (
                exc.code == 403 and exc.headers.get("x-ratelimit-remaining") == "0")
            detail = f"HTTP {exc.code}"
        except (OSError, ValueError) as exc:
            retry, detail = True, type(exc).__name__
        if not retry or attempt == ATTEMPTS - 1:
            warn(f"GitHub {method} {path}: {detail}")
            return None
        time.sleep(2 ** (attempt + 1))
    return None


def check_name(label):
    return f"{os.environ.get('CHECK_PREFIX') or 'OrchestrAI'} · {label}"


def workflow_run_url():
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    return (f"{server}/{os.environ.get('GITHUB_REPOSITORY', '')}"
            f"/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}")


def links(run_url):
    parts = [f"[OrchestrAI run]({run_url})"] if run_url else []
    return " · ".join(parts + [f"[Workflow run]({workflow_run_url()})"])


def create_main():
    """--create: one queued check run per batch; check_ids -> $GITHUB_OUTPUT,
    rewritten after each so a cancelled step still hands on the ones it made."""
    head_sha = os.environ.get("HEAD_SHA", "")
    if not head_sha:
        warn("no HEAD_SHA: no check runs")
        return
    batches = json.loads(os.environ.get("BATCH_MATRIX") or "[]")
    run_urls = json.loads(os.environ.get("RUN_URLS") or "{}")
    out = os.environ.get("GITHUB_OUTPUT")
    ids = {}
    for batch in batches:
        bid = batch["batch_id"]
        run_url = run_urls.get(bid, "")
        title = "Waiting for machines" if run_url else "No OrchestrAI run was started"
        body = {"name": check_name(batch.get("label") or bid), "head_sha": head_sha,
                "status": "queued", "external_id": bid,
                "output": {"title": title,
                           "summary": f"{batch.get('count', len(batch.get('playbooks', [])))} "
                                      f"playbook(s). {links(run_url)}"}}
        if run_url:
            body["details_url"] = run_url
        made = github("POST", "/check-runs", body)
        if made and made.get("id"):
            ids[bid] = made["id"]
            if out:
                with open(out, "a") as f:
                    f.write(f"check_ids={json.dumps(ids)}\n")
    print(f"Created {len(ids)} of {len(batches)} check run(s)", file=sys.stderr)


def describe(run):
    """(GitHub status, title) for an OrchestrAI run, as the Control Plane reports it."""
    status = run.get("status") or ""
    build = run.get("pipeline_url") or ""
    if status in TERMINAL:
        # The run's status is not the batch's verdict: the Test job reads each
        # playbook's result and may retry the ones that never ran.
        return "in_progress", f"Run {status}; reading results"
    if build and "/queue/" not in build:
        return "in_progress", "Tests running"
    if status in ("", "queued"):
        message = run.get("message")
        return "queued", ("Waiting for machines"
                          + (f": {message}" if isinstance(message, str) and message else ""))[:200]
    return "in_progress", f"Preparing machines ({status})"


class Updater:
    """Moves each batch's check run along as Wait for OrchestrAI polls its run.
    Calls GitHub only when the status or title changes; never raises."""

    def __init__(self, check_ids, run_urls=None):
        self.check_ids = check_ids
        self.run_urls = run_urls or {}
        self.last = {}

    def update(self, bid, run):
        try:
            cid = self.check_ids.get(bid)
            if not cid:
                return
            status, title = describe(run)
            if self.last.get(bid) == (status, title):
                return
            body = {"status": status,
                    "output": {"title": title, "summary": links(self.run_urls.get(bid, ""))}}
            if status == "in_progress" and (self.last.get(bid) or ("queued",))[0] != "in_progress":
                body["started_at"] = now()
            if github("PATCH", f"/check-runs/{cid}", body) is not None:
                self.last[bid] = (status, title)
        except Exception as exc:  # visibility only: never stop the wait
            warn(f"{bid}: check run not updated: {exc}")


def conclusion(rows, batch):
    """(conclusion, title) for a batch from its final batch.json rows."""
    from orchestrai_batch_verdict import batch_failed, system_status
    if not rows:
        return "neutral", "No results"
    passed = sum(r["outcome"] == "PASSED" for r in rows)
    title = f"{passed} of {len(rows)} playbook(s) passed"
    state = system_status(rows)
    if state == "PASS":
        return "success", title
    if state == "NOT RUN":
        # Required playbooks that never ran fail the gate; say so here too.
        return ("failure" if batch_failed(rows, batch) else "neutral"), f"Not run: {title}"
    return "failure", title


def finish_main(path):
    """--finish FILE: the batch's verdict, from its final batch.json."""
    cid = os.environ.get("CHECK_ID", "")
    if not cid:
        print("No check run for this batch", file=sys.stderr)
        return
    batch = json.loads(os.environ.get("BATCH_JSON") or "{}")
    run_url = os.environ.get("RUN_URL", "")
    try:
        rows = json.loads(Path(path).read_text())
    except (OSError, ValueError):
        rows = []
    result, title = conclusion(rows, batch)
    summary = links(run_url)
    if rows:
        from orchestrai_batch_verdict import table
        summary += "\n\n" + table(rows, run_url)
    github("PATCH", f"/check-runs/{cid}", {
        "status": "completed", "conclusion": result, "completed_at": now(),
        "output": {"title": title, "summary": summary[:SUMMARY_LIMIT]}})
    print(f"check run {cid}: {result} ({title})", file=sys.stderr)


def cancel_main():
    """--cancel: mark each check run in CHECK_IDS cancelled, unless it finished."""
    raw = (os.environ.get("CHECK_IDS") or "").strip()
    if not raw:
        return
    ids = list(json.loads(raw).values()) if raw.startswith("{") else raw.split()
    for cid in ids:
        current = github("GET", f"/check-runs/{cid}")
        if current is None or current.get("status") == "completed":
            continue
        github("PATCH", f"/check-runs/{cid}", {
            "status": "completed", "conclusion": "cancelled", "completed_at": now(),
            "output": {"title": "Cancelled",
                       "summary": f"The workflow run was cancelled. {links('')}"}})


def main():
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--create", action="store_true")
    mode.add_argument("--finish", metavar="BATCH_JSON_FILE")
    mode.add_argument("--cancel", action="store_true")
    args = ap.parse_args()
    try:
        if args.create:
            create_main()
        elif args.finish:
            finish_main(args.finish)
        else:
            cancel_main()
    except Exception as exc:  # visibility only: never fail the job
        warn(f"check runs: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
