#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT
"""Manual V2 lane: reuse playbook planning, call the supported CI API directly."""

import argparse
from collections import Counter
import contextlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import quote, urlsplit

import orchestrai_matrix as matrix
import orchestrai_trigger as legacy
import orchestrai_v2_api as api

EXTERNAL_REPO = "https://github.com/amd/playbooks"


def cell(value):
    return (" ".join(str(value if value is not None else "").split())
            .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("|", "\\|"))


def result_link(url, label):
    if not isinstance(url, str) or re.search(r"[\s\x00-\x1f\x7f]", url):
        return ""
    try:
        parts = urlsplit(url)
        if parts.scheme != "https" or not parts.hostname or parts.username or parts.password:
            return ""
        parts.port
    except ValueError:
        return ""
    return f"[{label}]({quote(url, safe=':/?&=#%')})"


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def output(name, value):
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as handle:
            handle.write(f"{name}={json.dumps(value, separators=(',', ':'))}\n")


@contextlib.contextmanager
def cwd(path):
    original = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original)


def select(config, source, playbooks, devices, platforms):
    ids = list(dict.fromkeys(x.strip() for x in playbooks.split(",") if x.strip()))
    select_all = not ids or ids == ["all"]
    if select_all:
        ids = sorted({path.parent.name for category in ("core", "supplemental")
                      for path in (source / "playbooks" / category).glob("*/playbook.json")})
    if not ids:
        raise ValueError("No playbook metadata found in the external checkout")
    for pb in ids:
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", pb):
            raise ValueError(f"Invalid playbook ID: {pb!r}")
        if not any((source / "playbooks" / category / pb / "playbook.json").is_file()
                   for category in ("core", "supplemental")):
            raise ValueError(f"Playbook {pb!r} is absent from the external checkout")
    requested_platforms = None if platforms == "all" else {platforms}
    if platforms not in {"all", "linux", "windows"}:
        raise ValueError("platform must be all, linux or windows")
    requested_devices = None if devices.strip() in {"", "all"} else {
        x.strip() for x in devices.split(",") if x.strip()
    }
    with cwd(source):
        entries, batches = matrix.build(ids, config, requested_devices, requested_platforms)
    missing = set(ids) - {entry["playbook"] for entry in entries}
    if missing and not select_all:
        raise ValueError("No eligible configured hardware for: " + ", ".join(sorted(missing)))
    if not batches:
        raise ValueError("No eligible playbooks match the requested hardware and OS")
    if len(batches) > 32:
        raise ValueError("The manual V2 lane supports at most 32 configuration batches")
    return batches


def resolve_workspace(value, env=None):
    env = os.environ if env is None else env
    workspace = (value or "").strip() or env.get("ORCHESTRAI_V2_WORKSPACE", "").strip()
    if not workspace or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", workspace):
        raise ValueError("Set ORCHESTRAI_V2_WORKSPACE to the production workspace slug, "
                         "or provide an explicit workspace input")
    return workspace


def request_for(batch_id, batch, cfg, sha, workspace, catalog, publisher):
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("The external checkout must resolve to an immutable commit SHA")
    workspace = resolve_workspace(workspace)
    index = os.environ.get("ORCHESTRAI_ROCM_MULTI_ARCH_INDEX_URL", "")
    if not index:
        raise ValueError("ORCHESTRAI_ROCM_MULTI_ARCH_INDEX_URL is required")
    builds, missing = legacy.make_builds(batch, cfg)
    if missing:
        raise ValueError(f"{batch_id}: missing provisioning: {', '.join(missing)}")
    old_plan = legacy.make_plan(batch, f"external/{sha}", cfg, 1, EXTERNAL_REPO, sha, index)
    platform = batch["platform"]
    image = os.environ.get(f"ORCHESTRAI_V2_{platform.upper()}_IMAGE") or (
        "windows" if platform == "windows" else "ubuntu"
    )
    sessions = [{
        "name": group["id"],
        "level": group["level"],
        "machine_tags": group["maas_tags"],
        "os_image": image,
        "tests": group["tests"],
        "variables": group["variables"],
    } for group in old_plan["groups"]]
    plan = {"sessions": sessions, "run_settings": {
        **old_plan["run_settings"], "executor": "jenkins", "os_image": image,
    }}
    plan["run_settings"].pop("result_publishers", None)
    if catalog:
        plan["catalog_release_id"] = catalog
    cp = {
        "workspace": workspace, "auth": "oidc", "require_capacity": "queue",
        "timeout_minutes": 300, "cancel_on_exit": True,
        "fail_on_test_failures": True, "unique_plan_name": True,
    }
    project = os.environ.get("ORCHESTRAI_V2_RP_PROJECT") or "ucicd_project_slim"
    if publisher:
        cp["result_publishers"] = [{
            "kind": "reportportal", "credential": publisher, "project": project,
            "when": "always", "required": True, "sources": "published",
            "attributes": {
                "lane": "playbooks-v2", "batch": batch_id,
                "playbook_sha": sha, "github_run_id": "{GITHUB_RUN_ID}",
            },
        }]
    parameters = {"PLAN_JSON": plan, "BUILDS_JSON": builds,
                  "OS_IMAGE": image, "MAX_DURATION": cfg["run_settings"]["max_duration"]}
    if publisher:
        parameters["RP_PROJECT"] = project
    return {
        "config": {"version": 2, "trigger": "control_plane", "nightly": True,
                   "component_name": "Playbooks V2", "control_plane": cp},
        "parameters": parameters,
        "batch_id": batch_id, "playbook_sha": sha,
    }


def prepare(args):
    workspace = resolve_workspace(args.workspace)
    cfg = legacy.apply_env_overrides(legacy.load_config(args.config))
    tag_override = os.environ.get("ORCHESTRAI_DEVICE_TAGS")
    if tag_override:
        cfg["device_to_tags"] = json.loads(tag_override)
    batches = select(cfg, Path(args.source).resolve(), args.playbooks, args.devices, args.platform)
    errors = legacy.validate_config(cfg, batches)
    if errors:
        raise ValueError("Invalid configuration: " + ", ".join(errors))
    publisher = ""
    if args.publish_reportportal:
        publisher = os.environ.get("ORCHESTRAI_V2_RP_CREDENTIAL", "").strip()
        if not publisher:
            raise ValueError("ReportPortal export was requested; set ORCHESTRAI_V2_RP_CREDENTIAL")
    if not args.prepare_only:
        api.Settings.from_env(workspace, os.environ)
    root = Path(args.requests)
    items, preview = [], []
    for bid, batch in batches.items():
        request = request_for(bid, batch, cfg, args.sha, workspace, args.catalog, publisher)
        key = bid.replace("/", "_")
        write_json(root / f"{key}.json", request)
        items.append({"batch_id": bid, "key": key, "playbook_count": len(batch["playbooks"])})
        # Full requests contain driver coordinates supplied as repository secrets.
        # Publish identities and script names, never provisioning variable values.
        preview.append({
            **items[-1], "playbooks": batch["playbooks"], "tags": batch["tags"],
            "playbook_repo": EXTERNAL_REPO, "playbook_sha": args.sha,
            "os_image": request["parameters"]["OS_IMAGE"], "workspace": workspace,
            "catalog_release_id": args.catalog or "platform active release",
            "result_destination": "native + ReportPortal (required)" if publisher else "native",
            "install_scripts": request["parameters"]["BUILDS_JSON"]["install_scripts"],
            "provisioning_variable_names": sorted(request["parameters"]["BUILDS_JSON"]["vars"]),
        })
    write_json(Path(args.preview) / "plan.json", preview)
    output("matrix", items)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as handle:
            handle.write(f"## Playbooks V2 plan\n\nExternal source: `{EXTERNAL_REPO}@{args.sha}`\n\n")
            handle.write("Results: " + ("native + required ReportPortal export" if publisher else
                         "native OrchestrAI results; no ReportPortal credential needed") + "\n\n")
            handle.write("| Configuration | Playbooks | OS image |\n|---|---|---|\n")
            for item in preview:
                handle.write(f"| {item['batch_id']} | {', '.join(item['playbooks'])} | {item['os_image']} |\n")
            if args.prepare_only:
                handle.write("\nPlan-only validation: no V2 run or hardware acquisition.\n")


def execute(args):
    request = json.loads(Path(args.request).read_text(encoding="utf-8"))
    settings = api.Settings.from_env(request["config"]["control_plane"]["workspace"], os.environ)
    result = api.Client(settings, dict(os.environ)).execute(request, args.state)
    # A green executor with missing adapter verdicts must not pass validation.
    expected = len(request["parameters"]["PLAN_JSON"]["sessions"])
    result = validate_result(result, expected)
    if result.get("verdict") == "success":
        wanted = Counter(test for session in request["parameters"]["PLAN_JSON"]["sessions"]
                         for test in session["tests"])
        tests = result.get("tests", [])
        if (any(not isinstance(t.get("path"), str) for t in tests) or
                Counter(t.get("path") for t in tests) != wanted or
                any(t.get("outcome") != "passed" for t in tests)):
            result.update(verdict="failure", status="tests-errored",
                          error="V2 test records do not match the exact requested passed adapters")
    result.update(batch_id=request["batch_id"], playbook_sha=request["playbook_sha"],
                  expected=expected, result_destination=("native + ReportPortal (required)"
                  if request["config"]["control_plane"].get("result_publishers") else "native"))
    result["report"] = result_report(result, request["batch_id"])
    write_json(Path(args.results) / "result.json", result)
    write_json(Path(args.results) / "identity.json", {
        "batch_id": request["batch_id"], "playbook_repo": EXTERNAL_REPO,
        "playbook_sha": request["playbook_sha"],
    })
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as handle:
            handle.write(result.get("report") or "V2 did not return a report.\n")
    print(f"V2 {request['batch_id']}: {result.get('status', 'error')}; {result.get('url', '')}")
    if result.get("verdict") != "success" or not result.get("run_id"):
        raise ValueError(result.get("error") or "V2 did not complete a successful run")


def validate_result(result, expected):
    if result.get("verdict") != "success":
        return result
    counts = result.get("tests_summary") or {}
    counters = ("total", "passed", "failed", "errors", "blocked", "running", "skipped",
                "not_run", "interrupted", "cancelled", "unknown")
    if (isinstance(counts, dict) and
            all(type(counts.get(k, 0)) is int and counts.get(k, 0) >= 0 for k in counters)
            and counts.get("total") == expected and counts.get("passed") == expected
            and not any(counts.get(k, 0) for k in counters if k not in ("total", "passed"))):
        return result
    detail = f"Expected {expected} passed playbook adapter(s); V2 reported {counts}"
    return {**result, "verdict": "failure", "status": "tests-errored", "error": detail,
            "report": (result.get("report") or "") + f"\n**Validation failed:** {detail}\n"}


def result_report(result, batch):
    lines = [f"## OrchestrAI V2 — {cell(batch)}", "",
             f"Run: **{cell(result.get('status'))}** · gate: **{cell(result.get('verdict'))}**", "",
             f"Result destination: {cell(result.get('result_destination', 'native'))}", ""]
    counts = Counter(item.get("outcome", "unknown") for item in result.get("tests", []))
    lines += [f"Native executions: **{counts['passed']} passed · {counts['failed']} failed · "
              f"{sum(v for k, v in counts.items() if k not in ('passed', 'failed'))} other**.", ""]
    if result.get("pipeline_status"):
        lines += [f"Executor/publishing status: **{cell(result['pipeline_status'])}**.", ""]
    if counts and counts['passed'] == sum(counts.values()) and result.get('verdict') != 'success':
        lines += ["All returned test executions passed; the run/gate did not. "
                  "Inspect pipeline, publishing and result-completeness diagnostics separately.", ""]
    # The native run is the user-facing entry point, independent of its executor.
    link = result_link(result.get("url"), "V2 run")
    if link:
        lines += [link, ""]
    if result.get("error"):
        lines += [cell(result["error"]), ""]
    lines += ["Raw stdout/stderr and attachments are in the V2 run's Tests and Artifacts tabs. "
              "The CI API currently returns verdicts, not evidence downloads or reliable playbook "
              "session identity; repeated adapter names are not individual playbook names.", ""]
    lines += ["| Adapter | Outcome | Immediate reason |", "|---|---|---|"]
    for item in result.get("tests", []):
        reason = item.get("error") or (f"exit code {item['exit_code']}" if item.get("exit_code") else "")
        lines.append(f"| {cell(item.get('path') or item.get('test_id'))} | {cell(item.get('outcome'))} | {cell(reason)} |")
    return "\n".join(lines) + "\n"


def summary(args):
    """Aggregate safe artifacts, including configurations with no result file."""
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    expected = {item["batch_id"]: item for item in plan}
    if not expected or len(expected) != len(plan):
        raise ValueError("V2 summary requires a nonempty plan with unique configurations")
    found = {}
    for path in Path(args.artifacts).glob("**/result.json"):
        result = json.loads(path.read_text(encoding="utf-8"))
        batch = result.get("batch_id")
        if batch not in expected:
            raise ValueError("Unexpected V2 result configuration")
        if batch in found:
            raise ValueError(f"Duplicate V2 result configuration: {batch}")
        if result.get("playbook_sha") != expected[batch]["playbook_sha"]:
            raise ValueError(f"V2 result source mismatch: {batch}")
        found[batch] = result
    lines = ["## V2 results by configuration", "",
             "Test execution and the overall run/gate are separate. Missing artifacts are UNKNOWN, not passed.", "",
             "| Configuration | Requested | Passed | Failed | Not run/interrupted | Other | Missing | Run | Gate | Evidence |",
             "|---|---:|---:|---:|---:|---:|---:|---|---|---|"]
    for batch, item in expected.items():
        result = found.get(batch, {})
        counts = Counter(t.get("outcome", "unknown") for t in result.get("tests", []))
        not_run = sum(counts[k] for k in ("not_run", "interrupted", "cancelled"))
        other = sum(counts.values()) - counts['passed'] - counts['failed'] - not_run
        missing = max(0, item['playbook_count'] - sum(counts.values()))
        link = result_link(result.get("url"), "V2 logs")
        lines.append(f"| {cell(batch)} | {item['playbook_count']} | {counts['passed']} | {counts['failed']} | "
                     f"{not_run} | {other} | {missing} | {cell(result.get('status', 'UNKNOWN'))} | "
                     f"{cell(result.get('verdict', 'UNKNOWN'))} | {link or 'No V2 run link'} |")
    lines += ["", "Per-playbook naming and automated evidence downloads require additional supported CI API "
              "fields/routes. This summary does not infer identity from adapter names or record order.", ""]
    text = "\n".join(lines)
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as handle:
            handle.write(text)
    if set(found) != set(expected):
        raise ValueError("V2 result artifacts are missing; see UNKNOWN configurations in the summary")
    return text


def cleanup(args):
    if not Path(args.state).is_file():
        return
    request = json.loads(Path(args.request).read_text(encoding="utf-8"))
    settings = api.Settings.from_env(request["config"]["control_plane"]["workspace"], os.environ)
    client = api.Client(settings, dict(os.environ))
    client.cancel(request, api.start_body(request, os.environ), args.state)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="mode", required=True)
    plan = subs.add_parser("prepare")
    plan.add_argument("--config", default=".github/orchestrai-config.yml")
    plan.add_argument("--source", default="playbook-source")
    plan.add_argument("--playbooks", required=True)
    plan.add_argument("--devices", required=True)
    plan.add_argument("--platform", choices=["all", "linux", "windows"], required=True)
    plan.add_argument("--sha", required=True)
    plan.add_argument("--workspace", required=True)
    plan.add_argument("--catalog", default="")
    plan.add_argument("--requests", required=True)
    plan.add_argument("--preview", default="v2-preview")
    plan.add_argument("--prepare-only", action="store_true")
    plan.add_argument("--publish-reportportal", action="store_true",
                      help="Also export to ReportPortal (required when explicitly requested)")
    report = subs.add_parser("summary")
    report.add_argument("--plan", required=True)
    report.add_argument("--artifacts", required=True)
    for name in ("run", "cleanup"):
        sub = subs.add_parser(name)
        sub.add_argument("--request", required=True)
        sub.add_argument("--state", required=True)
        if name == "run":
            sub.add_argument("--results", default="v2-results")
    args = parser.parse_args()
    try:
        {"prepare": prepare, "run": execute, "cleanup": cleanup, "summary": summary}[args.mode](args)
    except (ValueError, OSError) as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
