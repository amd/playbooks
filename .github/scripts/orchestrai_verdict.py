#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
OrchestrAI per-playbook verdict
===============================

A batch build runs several playbooks on one machine, so the OrchestrAI pipeline build's
overall result can't tell us whether THIS playbook passed. The pipeline writes a
per-group rollup to its summary.json:

    groups["playbook-<id>"] = {passed, failed, skipped, errors, status,
                               infrastructure_reason}
    expected_groups = ["playbook-a", ...]          # every group the batch planned

keyed by the submission group id (independent of completion order). This script
resolves THIS playbook's verdict, preferring that rollup and falling back to the
build console's per-suite lifecycle if the rollup is absent.

Infrastructure vs test failure
------------------------------
A group can be NOT_RUN (planned but never scheduled) or INTERRUPTED (started but
produced nothing) — e.g. the machine never came back from a reboot. That is an
infrastructure problem for the whole batch, NOT a failure of this playbook, so
the verdict is reported separately and `failed` is never fabricated to 1.

Backward compatibility: a summary.json without `expected_groups`/`NOT_RUN`
(old pipeline) is treated exactly as before — a missing group falls back to the
console and then to a hard failure.

An artifact is ALWAYS written
-----------------------------
`upload-artifact` runs with `if-no-files-found: ignore`, so a crash here makes
the playbook disappear from the aggregated report entirely and the sticky
comment silently undercounts. Every exit path — including an unexpected
exception and a malformed summary.json — writes test-results/summary.json first.

Usage:
    orchestrai_verdict.py     (all inputs via env)

Env:
    BUILD_URL, ORCHESTRAI_PIPELINE_USER, ORCHESTRAI_PIPELINE_TOKEN, PLAYBOOK_ID, PLATFORM

Outputs:
    test-results/summary.json   (per-playbook counts + outcome, for artifact upload)
    rp_url=<reportportal launch url>  -> $GITHUB_OUTPUT
    exit 0 PASSED, 1 FAILED (a real test failure), 2 NOT_RUN/INTERRUPTED
    (infrastructure — the playbook never produced results)
"""

import base64
import json
import os
import re
import sys
import urllib.request

COUNT_KEYS = ("passed", "failed", "skipped", "errors")

# Statuses that mean "this playbook never produced results" rather than
# "this playbook failed its tests".
INFRA_STATUSES = ("NOT_RUN", "INTERRUPTED")

EXIT_PASSED = 0
EXIT_FAILED = 1
EXIT_INFRA = 2

FETCH_TIMEOUT = 60

# Reasons reported when there is nothing to judge this playbook by. These are
# infrastructure conditions, never test failures.
REASON_NO_BUILD = "no OrchestrAI build was produced for this batch"
REASON_NO_SUMMARY = "could not retrieve the build summary"
REASON_BAD_SUMMARY = "the build summary was malformed (groups is not an object)"


def fetch(url, user, token):
    """GET `url` with basic auth.

    Returns the body (possibly "") on a successful response, and None on a
    transport failure — 401, DNS/connection error, an aborted build with no
    artifact. The caller must be able to tell "the pipeline said nothing" from
    "we could not reach the pipeline": the first is a real (if empty) answer,
    the second is infrastructure and must never be turned into a test failure.

    SECURITY: the credentials are deliberately NOT handed to a `curl -u
    user:token` subprocess. argv is world-readable via /proc/<pid>/cmdline and
    `ps` for the lifetime of the process, so on a shared/persistent self-hosted
    runner any other local process could read the pipeline token. Doing the HTTP
    in-process (stdlib only — this job has no pip install step) keeps the secret
    in this process's memory only.
    """
    req = urllib.request.Request(url)
    req.add_header("Authorization",
                   "Basic " + base64.b64encode(f"{user}:{token}".encode()).decode())
    try:
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as r:
            return r.read().decode("utf-8", "replace")
    except Exception:
        return None


def normalise_groups(summary):
    """(groups_dict, malformed) for `summary["groups"]`.

    The pipeline is supposed to emit an object here; anything else (a list, a
    string, a number) is a malformed document. Coercing to {} in ONE place
    keeps every later `.get()` safe — the previous code did
    `(summary.get("groups") or {}).get(...)`, which still raises AttributeError
    on a truthy non-dict and left no artifact behind.
    """
    raw = summary.get("groups")
    if isinstance(raw, dict):
        return raw, False
    return {}, raw is not None


def group_counts(grp):
    """The four count keys of a group rollup, coerced to ints."""
    out = {}
    for k in COUNT_KEYS:
        try:
            out[k] = int(grp.get(k) or 0)
        except (TypeError, ValueError):
            out[k] = 0
    return out


def status_from_group(grp):
    """Verdict from a group rollup, or None if it carries none.

    NOT_RUN/INTERRUPTED are passed through so the caller can report them as
    infrastructure rather than as a test failure. A group claiming PASSED while
    having run nothing is never believed (that is the bug this guards): with
    zero counts it can only be INTERRUPTED.
    """
    status = (grp.get("status") or "").strip().upper() or None
    counts = group_counts(grp)
    ran_something = sum(counts.values()) > 0

    if status in INFRA_STATUSES:
        return status
    if status == "PASSED" and not ran_something:
        return "INTERRUPTED"
    if status:
        return status
    if not ran_something:
        return None  # ambiguous: group exists but ran nothing — don't call it PASS
    return "FAILED" if (counts["failed"] or counts["errors"]) else "PASSED"


def status_from_console(console, playbook):
    """Fallback: the console exposes the per-playbook suite lifecycle even when
    summary.json has no group for it:
        Started suite "playbook-<id> #<n>" ... id=<sid>
        Finished item <sid> -> PASSED|FAILED
    """
    esc = re.escape(playbook)
    console = console or ""   # fetch() returns None when the console is unreachable
    m = re.search(rf'Started suite "playbook-{esc} #\d+".*?id=([0-9a-fA-F-]+)', console)
    if not m:
        return None
    sid = m.group(1)
    # The separator between the item id and the status is an arrow that renders
    # differently across console encodings (Unicode "→", ASCII "->", or mojibake
    # if the log was decoded wrong). Match any run of non-alphanumeric characters
    # rather than a specific arrow so the status is captured regardless.
    fin = re.findall(rf'Finished item {re.escape(sid)}[^A-Za-z0-9]+([A-Z]+)', console)
    return fin[-1] if fin else None


def has_infra_schema(summary):
    """True when the pipeline speaks the infrastructure-aware schema.

    Old pipelines emit neither `expected_groups` nor a batch INTERRUPTED status
    nor a batch `infrastructure_reason`; for those we must degrade to the
    previous behaviour (missing group -> console -> hard failure).
    """
    if isinstance(summary.get("expected_groups"), list):
        return True
    if (summary.get("status") or "").strip().upper() == "INTERRUPTED":
        return True
    return summary.get("infrastructure_reason") is not None


def infrastructure_reason(summary, grp, group_key):
    """The reason to report for a NOT_RUN/INTERRUPTED group.

    Per-group reason wins over the batch-level one; if the pipeline supplied
    neither, describe the shortfall from expected_groups vs groups.
    """
    for src in (grp, summary):
        if isinstance(src, dict):
            reason = src.get("infrastructure_reason")
            if isinstance(reason, str) and reason.strip():
                return reason.strip()

    expected = summary.get("expected_groups")
    groups, _ = normalise_groups(summary)
    if isinstance(expected, list) and expected:
        missing = [g for g in expected if g not in groups]
        if group_key not in expected:
            return (f"{group_key} is not in the batch plan "
                    f"({len(expected)} playbooks were planned)")
        if missing:
            return (f"batch did not complete; {len(missing)} of {len(expected)} "
                    f"playbooks never ran")
    return "batch did not complete; this playbook produced no results"


def build_results(playbook, outcome, grp, reason):
    """The single `results` row for the artifact.

    Never empty: an artifact with `results: []` hides what actually happened,
    which is exactly how 13 never-executed playbooks looked like 13 failures.

    The row is a SUPERSET of the row schema the website dashboard already reads
    (`{test_id, success, skipped, duration, error_message}` —
    website/src/lib/github-test-results.ts, produced by run_playbook_tests.py),
    plus an additive `status`. Inventing a second shape for the same filename
    would break every existing consumer of this artifact.
    """
    if outcome in INFRA_STATUSES:
        message = reason or "the playbook produced no results"
    elif isinstance(grp, dict):
        c = group_counts(grp)
        message = (f"{c['passed']} passed, {c['failed']} failed, "
                   f"{c['skipped']} skipped, {c['errors']} errors")
    elif outcome == "PASSED":
        message = "playbook suite passed (per-test detail not reported by the pipeline)"
    else:
        message = "playbook suite did not pass (per-test detail not reported by the pipeline)"

    return [{
        "test_id": playbook,
        "success": outcome == "PASSED",
        # NOT_RUN/INTERRUPTED is closer to "skipped" than to "failed" for a
        # consumer that only knows success/skipped — it must not be counted red.
        "skipped": outcome in INFRA_STATUSES,
        "duration": 0,
        "error_message": "" if outcome == "PASSED" else message,
        "status": outcome,
    }]


def make_summary(playbook, platform, outcome, grp=None, reason=None,
                 summary=None):
    """The per-playbook test-results/summary.json document."""
    summary = summary if isinstance(summary, dict) else {}

    if isinstance(grp, dict):
        c = group_counts(grp)
        # Errors are test outcomes too; fold them into `failed` so consumers
        # that only look at `failed` cannot miss them.
        passed, failed, skipped = c["passed"], c["failed"] + c["errors"], c["skipped"]
    elif outcome in INFRA_STATUSES:
        passed = failed = skipped = 0
    else:
        # Console fallback: no counts available, keep the historical 1-test shape.
        passed, failed, skipped = (1, 0, 0) if outcome == "PASSED" else (0, 1, 0)

    total = passed + failed + skipped
    if outcome == "PASSED" and total == 0:
        # Contract: never emit PASSED with nothing behind it.
        outcome, reason = "INTERRUPTED", reason or "no tests were recorded for this playbook"

    return {
        "playbook_id": playbook,
        "platform": platform,
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "outcome": outcome,
        "infrastructure_reason": reason if outcome in INFRA_STATUSES else None,
        "reportportal_url": (summary.get("rp_launch_url") or None),
        "results": build_results(playbook, outcome, grp, reason),
    }


def exit_code_for(outcome):
    if outcome == "PASSED":
        return EXIT_PASSED
    if outcome in INFRA_STATUSES:
        return EXIT_INFRA
    return EXIT_FAILED


def write_artifact(doc):
    os.makedirs("test-results", exist_ok=True)
    with open("test-results/summary.json", "w") as f:
        json.dump(doc, f, indent=2)


def _run():
    user = os.environ.get("ORCHESTRAI_PIPELINE_USER", "")
    token = os.environ.get("ORCHESTRAI_PIPELINE_TOKEN", "")
    build_url = os.environ.get("BUILD_URL", "")
    playbook = os.environ.get("PLAYBOOK_ID", "")
    platform = os.environ.get("PLATFORM", "")

    if not playbook or not platform:
        print("::error::orchestrai_verdict.py: PLAYBOOK_ID and PLATFORM must be set",
              file=sys.stderr)
        sys.exit(EXIT_FAILED)

    group_key = f"playbook-{playbook}"

    def finish(status, grp=None, reason=None, summary=None, how=""):
        """Write the artifact, annotate, and exit with the mapped code."""
        doc = make_summary(playbook, platform, status, grp=grp, reason=reason,
                           summary=summary)
        write_artifact(doc)
        outcome = doc["outcome"]
        code = exit_code_for(outcome)
        if code == EXIT_INFRA:
            print(f"::warning::{playbook} ({platform}): {outcome} — "
                  f"{doc['infrastructure_reason']} (infrastructure, not a test failure)")
        counts = group_counts(grp) if isinstance(grp, dict) else {}
        print(f"{playbook} ({platform}): {outcome} (via {how}, counts={counts})")
        sys.exit(code)

    # No build URL at all: the batch never produced a build, so this playbook —
    # and every other playbook in the same batch — never ran. That is
    # infrastructure, not 13 (or 79) test failures.
    if not build_url:
        # Deliberately NOT ::error:: — finish() immediately annotates this as
        # infrastructure, and emitting an error first contradicts that in the
        # very place a reader looks to tell the two apart.
        print(f"No OrchestrAI pipeline build URL for {playbook} ({platform})")
        finish("NOT_RUN", reason=REASON_NO_BUILD, how="no build url")

    raw = fetch(f"{build_url}artifact/.pipeline/summary.json", user, token)
    summary_unreachable = raw is None
    try:
        summary = json.loads(raw or "{}")
    except Exception:
        summary = {}
    if not isinstance(summary, dict):
        summary = {}

    groups, groups_malformed = normalise_groups(summary)

    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"rp_url={summary.get('rp_launch_url', '')}\n")

    # Primary: per-group rollup in summary.json.
    status, how = None, ""
    grp = groups.get(group_key)
    if not isinstance(grp, dict):
        grp = None
    if grp is not None:
        status = status_from_group(grp)
        if status:
            how = "summary.json groups"

    # Fallback: scrape the build console's suite lifecycle. A readable console
    # still wins over everything below — only if IT is silent too do we decide
    # between infrastructure and a hard failure.
    if status is None:
        console = fetch(f"{build_url}consoleText", user, token)
        status = status_from_console(console, playbook)
        if status:
            how = "console suite lifecycle"

    if status is None:
        # Neither source answered. Decide whether that is infrastructure or a
        # genuine "this playbook was expected to report and did not".
        if summary_unreachable:
            # 401, network, aborted build: we could not read the build summary
            # at all. Distinguishable from a legitimately empty document
            # precisely because fetch() returns None rather than "".
            finish("NOT_RUN", reason=REASON_NO_SUMMARY, summary=summary,
                   how="build summary unreachable")
        if groups_malformed:
            finish("INTERRUPTED", reason=REASON_BAD_SUMMARY, summary=summary,
                   how="malformed summary.json")
        if has_infra_schema(summary):
            # Infrastructure-aware pipeline: a planned group with no session
            # never ran; it is not a playbook failure.
            status = "NOT_RUN"
            how = "expected_groups (no session for this playbook)"

    if status is None:
        # Old pipeline, readable summary, no group and no console result:
        # today's behaviour exactly — a hard failure.
        write_artifact(make_summary(playbook, platform, "FAILED", summary=summary))
        print(f"::error::No verdict for {playbook} ({platform}): "
              f"no groups['{group_key}'] in summary.json and no suite result in the "
              f"console. groups present: {list(groups.keys())}")
        sys.exit(EXIT_FAILED)

    reason = (infrastructure_reason(summary, grp, group_key)
              if status in INFRA_STATUSES else None)
    finish(status, grp=grp, reason=reason, summary=summary, how=how)


def main():
    """_run() with a guaranteed artifact.

    `upload-artifact` uses `if-no-files-found: ignore`, so an uncaught exception
    here would delete this playbook from the aggregated report rather than
    colouring it red — the report would silently undercount, which is strictly
    worse than a wrong count. Any unexpected error becomes INTERRUPTED (2) with
    the error named as the infrastructure reason.
    """
    try:
        _run()
    except SystemExit:
        raise
    except Exception as exc:                                  # noqa: BLE001
        playbook = os.environ.get("PLAYBOOK_ID", "") or "unknown"
        platform = os.environ.get("PLATFORM", "") or "unknown"
        reason = f"the verdict step failed unexpectedly: {type(exc).__name__}: {exc}"
        try:
            write_artifact(make_summary(playbook, platform, "INTERRUPTED",
                                        reason=reason))
        except Exception:                                     # noqa: BLE001
            pass
        print(f"::warning::{playbook} ({platform}): INTERRUPTED — {reason} "
              f"(infrastructure, not a test failure)")
        sys.exit(EXIT_INFRA)


if __name__ == "__main__":
    main()
