#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT
"""Start playbook batches through the OrchestrAI Control Plane (V2) CI API."""

import os
from pathlib import Path
import re
import sys
import time
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import orchestrai_trigger as legacy
import orchestrai_v2_api as api

EXTERNAL_REPO = "https://github.com/amd/playbooks"


def resolve_workspace(value, env=None):
    env = os.environ if env is None else env
    workspace = (value or "").strip() or env.get("ORCHESTRAI_V2_WORKSPACE", "").strip()
    if not workspace or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", workspace):
        raise ValueError("Set ORCHESTRAI_V2_WORKSPACE to the production workspace slug, "
                         "or provide an explicit workspace input")
    return workspace


def request_for(batch_id, batch, cfg, sha, workspace, catalog, publisher, git_ref=None,
                machines_per_hw_group=1):
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("The external checkout must resolve to an immutable commit SHA")
    workspace = resolve_workspace(workspace)
    index = os.environ.get("ORCHESTRAI_ROCM_MULTI_ARCH_INDEX_URL", "")
    if not index:
        raise ValueError("ORCHESTRAI_ROCM_MULTI_ARCH_INDEX_URL is required")
    builds, missing = legacy.make_builds(batch, cfg)
    if missing:
        raise ValueError(f"{batch_id}: missing provisioning: {', '.join(missing)}")
    old_plan = legacy.make_plan(batch, git_ref or f"external/{sha}", cfg, machines_per_hw_group,
                                EXTERNAL_REPO, sha, index)
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


def trigger_batches(batches, cfg, sha, workspace, publisher, state_dir, **plan_args):
    """Start each batch; return ({batch_id: build URL}, {batch_id: run URL}).

    The per-playbook jobs read the build's summary.json; the run URL is the
    OrchestrAI page linked when results are not exported to ReportPortal.
    """
    settings = api.Settings.from_env(workspace, os.environ)
    pending, run_urls = {}, {}
    for bid, batch in batches.items():
        request = request_for(bid, batch, cfg, sha, workspace, "", publisher, **plan_args)
        client = api.Client(settings, dict(os.environ))
        try:
            rid = client.start(request, api.start_body(request, os.environ),
                               Path(state_dir) / f"{bid.replace('/', '_')}.json")
        except api.ApiError as exc:
            print(f"::error::{bid}: V2 refused the run: {exc}", file=sys.stderr)
            continue
        run_urls[bid] = f"{settings.portal}/#/runs/{quote(rid, safe='')}"
        print(f"Batch {bid}: {', '.join(batch['playbooks'])}: run {run_urls[bid]}", file=sys.stderr)
        pending[bid] = (client, rid)
    urls = {}
    deadline = time.monotonic() + settings.timeout
    while pending and time.monotonic() < deadline:
        for bid, (client, rid) in list(pending.items()):
            try:
                run = api.run_of(client.retry("GET", f"/runs/{quote(rid, safe='')}")) or {}
            except api.ApiError as exc:
                print(f"::warning::{bid}: V2 status unavailable: {exc}", file=sys.stderr)
                continue
            url = run.get("pipeline_url") or ""
            # Until Jenkins starts the build this is its queue item, which never
            # reports a result; only a build URL can be handed to the test jobs.
            if url and "/queue/" not in url:
                urls[bid] = url.rstrip("/") + "/"
                print(f"  {bid}: build {urls[bid]}", file=sys.stderr)
                del pending[bid]
            elif run.get("status") in api.TERMINAL:
                reason = run.get("error") or run.get("status_reason") or run.get("message") or ""
                print(f"::error::{bid}: run {rid} ended {run.get('status')} without a build"
                      + (f": {reason}" if reason else ""), file=sys.stderr)
                del pending[bid]
        if pending:
            time.sleep(settings.poll)
    for bid in pending:
        print(f"::error::{bid}: V2 run did not start a build in time", file=sys.stderr)
    return urls, run_urls
