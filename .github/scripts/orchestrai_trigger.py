#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
OrchestrAI pipeline trigger
==========================

For each batch (one per platform/device[+extra-tags]) builds a plan -- one
session per playbook, sharing the batch's hardware -- and starts it through the
OrchestrAI Control Plane CI API with the job's GitHub OIDC token.
Records each batch's run id; every Test job then waits (--await-build) until
the Control Plane has started its batch's pipeline build.

Environment-specific values (provisioning scripts, TheRock URLs, Linux/Windows
driver sources, run settings) come from .github/orchestrai-config.yml and the
repo variables that override it.

Usage:
    orchestrai_trigger.py [--config .github/orchestrai-config.yml] [--dry-run]

Inputs (env):
    BATCHES_JSON            batches from orchestrai_matrix.py
    GIT_REF                 github.ref (recorded as PLAYBOOK_REF)
    MACHINES_PER_HW_GROUP   override; falls back to config default
    ORCHESTRAI_REPORTING    reportportal (default) or api
    ORCHESTRAI_V2_*         Control Plane endpoint, workspace and ReportPortal credential

Outputs:
    run_ids={...}     -> $GITHUB_OUTPUT   (batch_id -> OrchestrAI run id)
    run_urls={...}    -> $GITHUB_OUTPUT   (batch_id -> OrchestrAI run URL)
    --dry-run prints each plan/builds payload and starts nothing.
    --await-build (Test jobs, RUN_ID/BATCH_ID env): build_url -> $GITHUB_OUTPUT
"""

import argparse
import hashlib
import http.client
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# Control Plane CI API timing. Transient errors (network, 5xx, 429) are retried
# for API_RETRY_SECONDS. A run waits for machines for its acquire_timeout; ours
# waits that long plus BUILD_WAIT_MARGIN for its build.
API_TIMEOUT = 30
API_RETRY_SECONDS = 600
BUILD_WAIT_MARGIN = 30 * 60
POLL_SECONDS = 30
TERMINAL = {"passed", "failed", "unstable", "cancelled", "error"}


def load_config(path):
    import yaml  # only the config path needs it; --await-build runs without PyYAML
    with open(path) as f:
        return yaml.safe_load(f)


def apply_env_overrides(cfg):
    """Internal coordinates are kept out of the committed (public) config and
    supplied at run time via repo variables. Env values win over config."""
    prov = cfg.setdefault("provisioning", {})
    therock = os.environ.get("ORCHESTRAI_THEROCK_URL")
    if therock:
        prov["therock_url"] = therock
    windows_therock = os.environ.get("ORCHESTRAI_WINDOWS_THEROCK_URL")
    if windows_therock:
        prov["windows_therock_url"] = windows_therock
    linux_driver = os.environ.get("ORCHESTRAI_LINUX_DRIVER_SOURCE")
    if linux_driver:
        prov.setdefault("linux_kernel_driver", {})["source"] = linux_driver
    # Optional per-release map, so one batch can install the right amdgpu package
    # whatever Ubuntu release the broker hands back:
    #   {"ubuntu:24.04": "https://.../ubuntu/noble/amdgpu-install_X_all.deb", ...}
    linux_driver_map = os.environ.get("ORCHESTRAI_LINUX_DRIVER_SOURCES_JSON")
    if linux_driver_map:
        prov.setdefault("linux_kernel_driver", {})["sources_json"] = linux_driver_map
    npu_xrt = os.environ.get("ORCHESTRAI_RYZENAI_NPU_XRT_URL")
    if npu_xrt:
        prov["ryzenai_npu_xrt_url"] = npu_xrt
    driver = os.environ.get("ORCHESTRAI_WINDOWS_DRIVER_SOURCE")
    if driver:
        prov.setdefault("windows_driver", {})["source"] = driver
    driver_choice = os.environ.get("ORCHESTRAI_WINDOWS_DRIVER")
    if driver_choice:
        prov.setdefault("windows_driver", {})["use"] = driver_choice
    driver_url = os.environ.get("ORCHESTRAI_WINDOWS_DRIVER_URL")
    if driver_url:
        prov.setdefault("windows_public_driver", {})["url"] = driver_url
    return cfg


def windows_driver_choice(prov):
    """The repository opts into public; legacy configs retain internal behavior."""
    return str((prov.get("windows_driver") or {}).get("use") or "internal").strip().lower()


def validate_config(cfg, batches):
    """Return a list of missing required config keys (given the batches' platforms)."""
    errs = []
    for k in ("test_path_template", "playbook_repo"):
        if not cfg.get(k):
            errs.append(k)
    rs = cfg.get("run_settings") or {}
    for k in ("max_duration", "max_test_case_duration", "acquire_timeout"):
        if k not in rs:
            errs.append(f"run_settings.{k}")
    acquire = rs.get("acquire_timeout")
    if "acquire_timeout" in rs and (
            isinstance(acquire, bool) or not isinstance(acquire, int) or acquire <= 0):
        errs.append(f"run_settings.acquire_timeout must be a positive number of "
                    f"minutes, got {acquire!r}")
    prov = cfg.get("provisioning") or {}
    platforms = {b.get("platform") for b in batches.values()}
    if "linux" in platforms and not prov.get("linux_install_scripts"):
        errs.append("provisioning.linux_install_scripts")
    if "windows" in platforms:
        choice = windows_driver_choice(prov)
        if choice not in {"internal", "public"}:
            errs.append("provisioning.windows_driver.use (must be internal or public)")
        elif choice == "public":
            if not (prov.get("windows_public_driver") or {}).get("install_scripts"):
                errs.append("provisioning.windows_public_driver.install_scripts")
        elif not prov.get("windows_install_scripts"):
            errs.append("provisioning.windows_install_scripts")
    return errs


def make_plan(batch, git_ref, cfg, machines_per_hw_group, repo, sha, rocm_index_url,
              hf_token=""):
    platform = batch["platform"]
    device = batch["arch"]
    tags = batch["tags"]
    test = cfg["test_path_template"].format(platform=platform)
    rs = cfg["run_settings"]

    groups = []
    for pb_id in batch["playbooks"]:
        variables = {
            "PLAYBOOK_REPO": repo,
            "PLAYBOOK_SHA": sha,
            "PLAYBOOK_REF": git_ref,
            "PLAYBOOK_ID": pb_id,
            "PLAYBOOK_PLATFORM": platform,
            # device_runs_as: playbooks run as another device's (same silicon).
            "PLAYBOOK_DEVICE": (cfg.get("device_runs_as") or {}).get(device, device),
            "ROCM_MULTI_ARCH_INDEX_URL": rocm_index_url,
        }
        locale = batch.get("locale", "")
        if locale:
            localized_only = batch.get("localized_only", {}).get(pb_id, True)
            if not isinstance(localized_only, bool):
                raise ValueError(
                    f"Localized OrchestrAI batch has non-boolean localized_only "
                    f"for {pb_id!r}"
                )
            variables["PLAYBOOK_LOCALE"] = locale
            variables["PLAYBOOK_LOCALIZED_ONLY"] = str(localized_only).lower()
        # Authenticate HuggingFace traffic (models/datasets primed by deps fall
        # back to a live HF pull on a mirror miss; unauthenticated calls from the
        # shared egress IP hit HF's per-IP rate limit). Optional: omitted when the
        # secret is unset so runs still work (just unauthenticated).
        if hf_token:
            variables["HF_TOKEN"] = hf_token
        group = {
            "id": f"playbook-{pb_id}",
            "level": "L4-sys",
            "tests": [test],
            "maas_tags": tags,
            "variables": variables,
        }
        # Only machines at these sites (device_site_ids in the config).
        sites = (cfg.get("device_site_ids") or {}).get(device)
        if sites:
            group["site_ids"] = list(sites)
        # An OS image of its own for this device and platform (device_os_images).
        os_image = ((cfg.get("device_os_images") or {}).get(device) or {}).get(platform)
        if os_image:
            group["os_image"] = os_image
        groups.append(group)

    return {
        "source": "external-playbook-batch",
        "groups": groups,
        "run_settings": {
            "max_duration": rs["max_duration"],
            "max_test_case_duration": rs["max_test_case_duration"],
            "acquire_timeout": rs["acquire_timeout"],
            "machines_per_hw_group": machines_per_hw_group,
        },
    }


WINDOWS_THEROCK_SCRIPT = "InstallationScripts/gfx/windows-therock-tarball.ps1"


def make_builds(batch, cfg):
    """Return (builds, missing) — missing names required provisioning vars left empty."""
    platform = batch["platform"]
    prov = cfg.get("provisioning", {})
    missing = []

    if platform == "windows":
        # Copy so appending per-playbook extras below doesn't mutate cfg.
        choice = windows_driver_choice(prov)
        if choice == "public":
            public = prov.get("windows_public_driver") or {}
            scripts = list(public.get("install_scripts", []))
            url = str(public.get("url") or "").strip()
            if not url:
                missing.append("ORCHESTRAI_WINDOWS_DRIVER_URL")
            else:
                try:
                    parsed = urllib.parse.urlsplit(url)
                    valid = (parsed.scheme == "https" and bool(parsed.hostname)
                             and not parsed.username and not parsed.password
                             and not re.search(r"\s", url))
                except ValueError:
                    valid = False
                if not valid:
                    missing.append("ORCHESTRAI_WINDOWS_DRIVER_URL (must be an HTTPS installer URL without embedded credentials or whitespace)")
            # Pipeline build vars become DRIVER_URL on the DUT. Do not send the
            # internal share or driver_copy in this mode, even if configured.
            build_vars = {"driver_url": url}
        elif choice == "internal":
            scripts = list(prov.get("windows_install_scripts", []))
            drv = prov.get("windows_driver", {})
            source = drv.get("source", "")
            if not source:
                missing.append("ORCHESTRAI_WINDOWS_DRIVER_SOURCE")
            build_vars = {"driver_source": source, "driver_copy": drv.get("copy", "direct")}
        else:
            return {"install_scripts": [], "vars": {}}, ["provisioning.windows_driver.use (must be internal or public)"]
    else:
        scripts = list(prov.get("linux_install_scripts", []))
        device = batch.get("arch", "")
        device_family = (cfg.get("device_families") or {}).get(device)
        if device_family not in {"radeon", "ryzen_apu"}:
            missing.append(f"device_families.{device}")
        kernel_driver = prov.get("linux_kernel_driver", {})
        if device_family == "radeon":
            source = kernel_driver.get("source", "")
            sources_json = kernel_driver.get("sources_json", "")
            # Either form is sufficient: a single URL (the original behaviour) or
            # a per-release map. The map wins on the host when both are present.
            if not source and not sources_json:
                missing.append("ORCHESTRAI_LINUX_DRIVER_SOURCE")
            if sources_json:
                # Validate here, before any hardware is acquired -- a malformed
                # map would otherwise fail on the machine after the acquire wait.
                sources_json = sources_json.strip()
                # Pasting into the repo-variable UI sometimes leaves the whole
                # value wrapped in quotes. Unwrap only when what is inside is
                # itself valid JSON, so this cannot mask a genuinely broken map.
                if (len(sources_json) >= 2 and sources_json[0] == sources_json[-1]
                        and sources_json[0] in "\"'"):
                    inner = sources_json[1:-1].strip()
                    try:
                        json.loads(inner)
                        print("::warning::ORCHESTRAI_LINUX_DRIVER_SOURCES_JSON was wrapped "
                              f"in {sources_json[0]} quotes; using the value inside them",
                              file=sys.stderr)
                        sources_json = inner
                    except ValueError:
                        pass
                # A value pasted into the variable box often carries the line
                # breaks it was wrapped at. JSON allows whitespace between tokens
                # but not inside a string, so a break landing in a URL is an
                # "Invalid control character". URLs cannot contain raw newlines
                # or tabs, so dropping them is safe -- and only attempted when
                # the value does not already parse, so valid input is untouched.
                try:
                    json.loads(sources_json)
                except ValueError:
                    _rejoined = re.sub(r"[\n\r\t]+", "", sources_json)
                    try:
                        json.loads(_rejoined)
                        print("::warning::ORCHESTRAI_LINUX_DRIVER_SOURCES_JSON contained "
                              "line breaks inside its values; they were removed. Set it as "
                              "a single line to avoid this.", file=sys.stderr)
                        sources_json = _rejoined
                    except ValueError:
                        pass
                try:
                    parsed = json.loads(sources_json)
                except ValueError as exc:
                    # Say what is wrong and show enough of the value to spot it;
                    # "not valid JSON" alone leaves nothing to act on.
                    hint = ""
                    if any(c in sources_json for c in "\u201c\u201d\u2018\u2019"):
                        hint = (" -- the value contains smart quotes, so it was probably "
                                "copied from rendered text; retype it with plain \" quotes")
                    elif "'" in sources_json and '"' not in sources_json:
                        hint = " -- JSON requires double quotes, not single quotes"
                    missing.append(
                        f"ORCHESTRAI_LINUX_DRIVER_SOURCES_JSON (not valid JSON: {exc}{hint}"
                        f"; {len(sources_json)} chars, begins {sources_json[:24]!r})")
                    parsed = None
                if parsed is not None and not (
                    isinstance(parsed, dict)
                    and parsed
                    and all(isinstance(k, str) and isinstance(v, str) and v
                            for k, v in parsed.items())
                ):
                    missing.append(
                        "ORCHESTRAI_LINUX_DRIVER_SOURCES_JSON (expected a non-empty "
                        'object of "<id>:<version_id>" -> URL)')
                elif parsed is not None:
                    # Finish repairing a value that was broken across lines. The
                    # pre-parse rescue drops the newline, but the indentation that
                    # followed it stays inside the string: the JSON then parses
                    # while the URL is unusable, and the run fails much later on
                    # the machine with "curl: (3) URL rejected". A URL cannot
                    # contain whitespace, so remove it there and nowhere else.
                    repaired = [k for k, v in parsed.items()
                                if v.startswith(("http://", "https://")) and re.search(r"\s", v)]
                    if repaired:
                        for k in repaired:
                            parsed[k] = re.sub(r"\s+", "", parsed[k])
                        print("::warning::ORCHESTRAI_LINUX_DRIVER_SOURCES_JSON: removed whitespace "
                              f"from the URL(s) for {', '.join(sorted(repaired))}; set the variable "
                              "as a single line to avoid this", file=sys.stderr)
                        sources_json = json.dumps(parsed, separators=(",", ":"))
            # The kernel driver must be active before TheRock user-space is
            # installed. Keep this device-specific so APUs retain the inbox
            # amdgpu module they are validated with.
            scripts = list(kernel_driver.get("install_scripts", [])) + scripts
        # TheRock ships a single multi-arch tarball, so the URL is used as-is
        # (no per-gfx templating).
        url = prov.get("therock_url", "")
        if not url:
            missing.append("ORCHESTRAI_THEROCK_URL")
        build_vars = {"THEROCK_URL": url}
        if device_family == "radeon":
            # Every key here reaches the install script as an upper-cased env var
            # (DRIVER_SOURCE / DRIVER_SOURCES_JSON), which is how gfx/linux.sh
            # picks the package matching the release it actually booted.
            if source:
                build_vars["driver_source"] = source
            if sources_json:
                build_vars["driver_sources_json"] = sources_json
        if "cvml" in batch.get("playbooks", []):
            npu_xrt_url = prov.get("ryzenai_npu_xrt_url", "")
            if not npu_xrt_url:
                missing.append("ORCHESTRAI_RYZENAI_NPU_XRT_URL")
            build_vars["RAI_NPU_XRT_URL"] = npu_xrt_url

    # Per-playbook extra provisioning scripts (e.g. enabling WSL for playbooks
    # whose Windows flow runs tools inside Ubuntu). Appended only to batches that
    # actually contain
    # the playbook, so the cost (an extra feature install + reboot) is scoped to
    # batches with that playbook instead of every run on the platform. This is
    # batch-level, not group-level: any other playbook co-scheduled in the same
    # batch also gets these scripts, so they must be idempotent. Each entry may
    # carry an optional "platforms" filter (e.g. windows-only); it is stripped
    # before the script list is handed to the pipeline, which expects only
    # {script, reboot_after}.
    extra_map = cfg.get("extra_install_scripts", {})
    seen = {s.get("script") for s in scripts}
    for pb_id in batch.get("playbooks", []):
        for entry in extra_map.get(pb_id, []):
            plats = entry.get("platforms")
            if plats and platform not in plats:
                continue
            devs = entry.get("devices")
            if devs and batch.get("arch") not in devs:
                continue
            script = entry.get("script")
            if not script or script in seen:
                continue
            seen.add(script)
            scripts.append({
                "script": script,
                "reboot_after": bool(entry.get("reboot_after", False)),
            })

    # TheRock is scheduled via extra_install_scripts (hipInfo for GPU isolation).
    # The installer needs a Windows source, and THEROCK_PUBLISH_ENV=0 keeps it
    # off the machine env/PATH so it can't leak into other playbooks.
    if any(s["script"] == WINDOWS_THEROCK_SCRIPT for s in scripts):
        url = prov.get("windows_therock_url", "")
        if not url:
            missing.append("ORCHESTRAI_WINDOWS_THEROCK_URL")
        build_vars.update(THEROCK_URL=url, THEROCK_PUBLISH_ENV="0")

    builds = {"install_scripts": scripts, "vars": build_vars}
    return builds, missing


def resolve_sha(repo, ref):
    """The commit the test machines check out: pinned before submitting."""
    if re.fullmatch(r"[0-9a-f]{40}", ref):
        return ref
    out = subprocess.run(["git", "ls-remote", repo, ref], capture_output=True, text=True,
                         timeout=60, check=True).stdout.split()
    if not out:
        raise ValueError(f"{repo} has no ref {ref!r}")
    return out[0]


# ---------------------------------------------------------------------------
# OrchestrAI Control Plane CI API. One run per batch; the Control Plane queues it
# for machines and starts its pipeline build. Auth is the job's GitHub OIDC token
# (the job needs `id-token: write`); no stored OrchestrAI token is used.
# ---------------------------------------------------------------------------

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Never forward a bearer token to a redirect target."""

    def redirect_request(self, *args, **kwargs):
        return None


def control_plane():
    """Endpoint settings from the ORCHESTRAI_V2_* repo variables."""
    cp = {}
    for key in ("CI_API_URL", "OIDC_AUDIENCE", "PORTAL_URL", "WORKSPACE"):
        value = os.environ.get(f"ORCHESTRAI_V2_{key}", "").strip().rstrip("/")
        if not value:
            raise ValueError(f"Set repository variable ORCHESTRAI_V2_{key}")
        if key != "WORKSPACE" and not value.startswith("https://"):
            raise ValueError(f"ORCHESTRAI_V2_{key} must be an https:// URL")
        cp[key.lower()] = value
    return cp


def http_json(method, url, headers, body=None):
    """(status, JSON body or None). Raises OSError/HTTPException on transport failure."""
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        resp = urllib.request.build_opener(_NoRedirect).open(req, timeout=API_TIMEOUT)
    except urllib.error.HTTPError as e:
        resp = e
    with resp:
        raw = resp.read()
    try:
        return resp.code, (json.loads(raw) if raw else None)
    except ValueError:
        return resp.code, None


def oidc_token(audience):
    url = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL", "")
    request_token = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN", "")
    if not url or not request_token:
        raise ValueError("GitHub OIDC is unavailable; the job needs permissions id-token: write")
    sep = "&" if "?" in url else "?"
    status, payload = http_json("GET", f"{url}{sep}audience={urllib.parse.quote(audience, safe='')}",
                                {"Authorization": f"Bearer {request_token}"})
    token = payload.get("value") if isinstance(payload, dict) else None
    if status != 200 or not token:
        raise ValueError(f"GitHub could not issue an OIDC token (HTTP {status})")
    print(f"::add-mask::{token}")
    return token


def api(cp, method, path, body=None, key=None):
    """Call the CI API and return its JSON body, retrying transient failures.

    A start is retried with the same Idempotency-Key, so a lost response can
    never start a second run. A fresh OIDC token is used for every call.
    """
    deadline, delay = time.monotonic() + API_RETRY_SECONDS, 2
    while True:
        headers = {"Authorization": "Bearer " + oidc_token(cp["oidc_audience"]),
                   "Accept": "application/json", "Content-Type": "application/json",
                   "X-OrchestrAI-Workspace": cp["workspace"]}
        if key:
            headers["Idempotency-Key"] = key
        try:
            status, payload = http_json(method, cp["ci_api_url"] + path, headers, body)
        except (OSError, http.client.HTTPException) as exc:
            status, payload = None, {"error": {"message": f"network error ({type(exc).__name__})"}}
        if status and 200 <= status < 300 and isinstance(payload, dict):
            return payload
        err = payload.get("error") if isinstance(payload, dict) else None
        err = err if isinstance(err, dict) else {}
        code = err.get("code", "")
        if (status is None or status in (408, 429) or status >= 500
                or code == "idempotency_in_progress") and time.monotonic() < deadline:
            time.sleep(delay)
            delay = min(delay * 2, 30)
            continue
        request_id = payload.get("request_id", "") if isinstance(payload, dict) else ""
        raise ValueError(f"CI API {method} {path}: HTTP {status} {code}: {err.get('message', '')}"
                         + (f" (request_id={request_id})" if request_id else ""))


def start_run(cp, bid, plan, builds, platform, publisher, sha):
    """Start one batch as a Control Plane run; return its run id."""
    image = os.environ.get(f"ORCHESTRAI_V2_{platform.upper()}_IMAGE") or (
        "windows" if platform == "windows" else "ubuntu")
    settings = {**plan["run_settings"], "executor": "jenkins", "os_image": image}
    gh_run = os.environ.get("GITHUB_RUN_ID", "")
    # A retry of a batch's NOT_RUN playbooks (ORCHESTRAI_RETRY=n) is a new run.
    retry = os.environ.get("ORCHESTRAI_RETRY", "")
    attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if publisher:
        # Required: a failed ReportPortal export fails the run, never silently.
        settings["result_publishers"] = [{
            "kind": "reportportal", "credential": publisher,
            "project": os.environ.get("ORCHESTRAI_V2_RP_PROJECT") or "ucicd_project_slim",
            "when": "always", "required": True, "sources": "published",
            "attributes": {"lane": "playbooks", "batch": bid, "playbook_sha": sha,
                           "github_run_id": gh_run},
        }]
    sessions = [{"name": g["id"], "level": g["level"], "machine_tags": g["maas_tags"],
                 "os_image": g.get("os_image") or image, "tests": g["tests"],
                 "variables": g["variables"],
                 **({"site_ids": g["site_ids"]} if g.get("site_ids") else {})}
                for g in plan["groups"]]
    body = {
        "require_capacity": "queue",
        "plan_document": {
            "name": f"Playbooks {bid} {gh_run}/{attempt}" + (f" retry {retry}" if retry else ""),
            "description": f"Started by https://github.com/{repo}/actions/runs/{gh_run}",
            "document": {"sessions": sessions, "run_settings": settings},
        },
        "builds_json": builds,
    }
    key = hashlib.sha256(json.dumps([repo, gh_run, attempt, bid] + ([retry] if retry else []))
                         .encode()).hexdigest()
    run = api(cp, "POST", "/runs", body, key).get("run") or {}
    if not run.get("id"):
        raise ValueError("the CI API start response has no run id")
    return run["id"]


def failure_reason(run):
    """Why a run ended: its error/reason/message/failure/detail fields, one level
    deep (the Control Plane does not always use the same key)."""
    found = []
    def scan(obj, prefix=""):
        for key, value in (obj or {}).items():
            if isinstance(value, dict) and not prefix:
                scan(value, f"{key}.")
            elif value and any(w in key.lower() for w in ("error", "reason", "message", "failure", "detail")):
                found.append(f"{prefix}{key}={value if isinstance(value, str) else json.dumps(value)}")
    scan(run)
    return "; ".join(found)[:800]


def await_builds(cp, runs, wait_seconds):
    """Wait until each run has started its pipeline build; {batch_id: build URL}."""
    urls, pending = {}, dict(runs)
    deadline = time.monotonic() + wait_seconds
    while pending and time.monotonic() < deadline:
        for bid, rid in list(pending.items()):
            try:
                run = api(cp, "GET", f"/runs/{urllib.parse.quote(rid, safe='')}").get("run") or {}
            except ValueError as exc:
                print(f"::warning::{bid}: run status unavailable: {exc}", file=sys.stderr)
                continue
            url = run.get("pipeline_url") or ""
            # Until Jenkins starts the build this is its queue item, which never
            # reports a result; only a build URL can be handed to the test jobs.
            if url and "/queue/" not in url:
                urls[bid] = url.rstrip("/") + "/"
                print(f"  {bid}: build {urls[bid]}", file=sys.stderr)
                del pending[bid]
            elif run.get("status") in TERMINAL:
                reason = failure_reason(run)
                print(f"::error::{bid}: run {rid} ended {run.get('status')} without a build"
                      + (f": {reason}" if reason else ""), file=sys.stderr)
                del pending[bid]
        if pending:
            time.sleep(POLL_SECONDS)
    for bid in pending:
        print(f"::error::{bid}: run did not start a build in time", file=sys.stderr)
    return urls


def acquire_timeout_minutes(config_path):
    """run_settings.acquire_timeout from the config, read without PyYAML (the
    Test jobs that wait for builds do not install it)."""
    text = open(config_path, encoding="utf-8").read()
    m = re.search(r"^\s*acquire_timeout:\s*(\d+)", text, re.M)
    if not m:
        raise ValueError(f"{config_path} has no run_settings.acquire_timeout")
    return int(m.group(1))


def await_build_main(config_path):
    """--await-build: one Test job waits for its batch's build (RUN_ID, BATCH_ID).

    Writes build_url to $GITHUB_OUTPUT; leaves it unset when the run ends or
    times out without a build, which the verdict step reports as NOT_RUN.
    """
    rid, bid = os.environ.get("RUN_ID", ""), os.environ.get("BATCH_ID", "")
    if not rid:
        print(f"::error::batch {bid} has no OrchestrAI run (it failed to start; "
              f"see Detect & Trigger)", file=sys.stderr)
        return
    try:
        # The Control Plane holds a queued run for its acquire_timeout; never
        # give up on it sooner.
        wait = acquire_timeout_minutes(config_path) * 60 + BUILD_WAIT_MARGIN
        url = await_builds(control_plane(), {bid: rid}, wait).get(bid, "")
    except ValueError as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return
    out = os.environ.get("GITHUB_OUTPUT")
    if url and out:
        with open(out, "a") as f:
            f.write(f"build_url={url}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=".github/orchestrai-config.yml")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--await-build", action="store_true",
                    help="wait for one batch's build (Test jobs); see await_build_main")
    args = ap.parse_args()
    if args.await_build:
        await_build_main(args.config)
        return

    cfg = apply_env_overrides(load_config(args.config))
    batches = json.loads(os.environ.get("BATCHES_JSON", "{}") or "{}")
    git_ref = os.environ.get("GIT_REF", "")

    cfg_errs = validate_config(cfg, batches)
    if cfg_errs:
        print(f"::error::orchestrai-config.yml has missing or invalid keys: {', '.join(cfg_errs)}",
              file=sys.stderr)
        sys.exit(1)

    rs = cfg["run_settings"]
    try:
        mphg = int(os.environ.get("MACHINES_PER_HW_GROUP", "")
                   or rs.get("default_machines_per_hw_group", 1))
    except ValueError:
        mphg = 1

    # The test machines clone PLAYBOOK_REPO@PLAYBOOK_SHA. By default that's the
    # configured repo at main (or the dispatch's playbook_ref); the !orc PR path
    # passes the PR head commit so the PR's own code is what gets tested.
    repo = os.environ.get("ORCHESTRAI_PLAYBOOK_REPO") or cfg["playbook_repo"]
    sha = os.environ.get("ORCHESTRAI_PLAYBOOK_SHA") or os.environ.get("ORCHESTRAI_PLAYBOOK_REF") or "main"
    rocm_index_url = os.environ.get("ORCHESTRAI_ROCM_MULTI_ARCH_INDEX_URL", "")
    if not rocm_index_url:
        print("::error::ORCHESTRAI_ROCM_MULTI_ARCH_INDEX_URL repository variable is required",
              file=sys.stderr)
        sys.exit(1)

    # Prepare every batch first, and fail fast (before any submission) if a
    # batch is missing required provisioning -- otherwise we'd acquire a scarce
    # machine that can't install its GPU stack and only fail much later.
    if not args.dry_run:
        try:
            sha = resolve_sha(repo, sha)
        except (ValueError, subprocess.SubprocessError) as exc:
            print(f"::error::cannot resolve {repo}@{sha}: {exc}", file=sys.stderr)
            sys.exit(1)
    prepared = []
    prov_missing = {}
    machines = 0
    for bid, batch in batches.items():
        builds, missing = make_builds(batch, cfg)
        if missing:
            prov_missing[bid] = missing
        # Never more machines than the batch has playbooks: a spare machine
        # sits idle and still counts against the CI identity's quota.
        batch_machines = max(1, min(mphg, len(batch.get("playbooks") or [])))
        machines += batch_machines
        plan = make_plan(batch, git_ref, cfg, batch_machines, repo, sha, rocm_index_url)
        prepared.append((bid, batch, plan, builds))
        if args.dry_run:
            print(f"--- plan for {bid} ---")
            print(json.dumps(plan, indent=2))
            print(f"--- builds for {bid} ---")
            print(json.dumps(builds, indent=2))
    # Every started batch holds its machines until it ends; a run that needs
    # more than the CI identity's quota leaves the excess queued for admission.
    print(f"{len(batches)} batch(es), {machines} machine(s) requested "
          f"(machines_per_hw_group={mphg})", file=sys.stderr)
    if args.dry_run:
        return
    if prov_missing:
        for bid, miss in prov_missing.items():
            print(f"::error::batch {bid}: unset provisioning {miss} — "
                  f"set the corresponding repo variable(s)", file=sys.stderr)
        sys.exit(1)

    # reportportal: the Control Plane also publishes each run to ReportPortal
    # (required). api: results stay in OrchestrAI; jobs link to the run.
    reporting = os.environ.get("ORCHESTRAI_REPORTING") or "reportportal"
    if reporting not in ("reportportal", "api"):
        print(f"::error::ORCHESTRAI_REPORTING must be reportportal or api, got {reporting!r}",
              file=sys.stderr)
        sys.exit(1)
    publisher = ""
    if reporting == "reportportal":
        publisher = os.environ.get("ORCHESTRAI_V2_RP_CREDENTIAL", "").strip()
        if not publisher:
            print("::error::ReportPortal reporting needs the ORCHESTRAI_V2_RP_CREDENTIAL variable",
                  file=sys.stderr)
            sys.exit(1)
    try:
        cp = control_plane()
    except ValueError as exc:
        print(f"::error::{exc}", file=sys.stderr)
        sys.exit(1)
    runs, run_urls = {}, {}
    for bid, batch, plan, builds in prepared:
        try:
            runs[bid] = start_run(cp, bid, plan, builds, batch["platform"], publisher, sha)
        except ValueError as exc:
            print(f"::error::{bid}: the Control Plane refused the run: {exc}", file=sys.stderr)
            continue
        run_urls[bid] = f"{cp['portal_url']}/#/runs/{urllib.parse.quote(runs[bid], safe='')}"
        print(f"Batch {bid}: {', '.join(batch['playbooks'])}: run {run_urls[bid]}", file=sys.stderr)
    # Each Test job waits for its own batch's build (--await-build), so a batch
    # still queued for machines never holds back the batches that have started.
    failed = [bid for bid in batches if bid not in runs]
    print(f"\nStarted {len(runs)} OrchestrAI run(s)", file=sys.stderr)

    # Emit the runs FIRST so the batches that started still run downstream,
    # even if we exit non-zero for an empty result below.
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"run_ids={json.dumps(runs)}\n")
            f.write(f"run_urls={json.dumps(run_urls)}\n")

    # Surface dropped batches HERE, at the trigger, instead of letting each of
    # their downstream test jobs discover the gap one-by-one as "No build URL".
    if not runs:
        # Nothing triggered at all: fail hard. There is no partial run to
        # preserve, and every downstream job would otherwise fail identically.
        print("::error::No OrchestrAI runs were started — every batch "
              f"failed to submit ({len(failed)} batch(es): {', '.join(failed)}).",
              file=sys.stderr)
        sys.exit(1)
    if failed:
        # Some batches triggered. Do NOT exit non-zero: that would skip the
        # good batches (downstream jobs `needs` this one). A prominent error
        # annotation names the dropped batches so the cause is visible at the
        # trigger; their own downstream jobs still fail, so the run as a whole
        # is not reported green.
        print(f"::error::{len(failed)} batch(es) failed to start and will report "
              f"no build URL downstream: {', '.join(failed)}. The other "
              f"{len(runs)} batch(es) were started and will run.",
              file=sys.stderr)


if __name__ == "__main__":
    main()
