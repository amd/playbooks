#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
OrchestrAI pipeline trigger
==========================

For each batch (one per platform/device[+extra-tags]) builds a pipeline plan —
one group per playbook, sharing the batch's hardware — and POSTs it to the
OrchestrAI pipeline job (buildWithParameters). Polls the queue item until the
build starts and records its URL so the matrix job can wait on it.

Environment-specific values (OrchestrAI pipeline URL/job, provisioning scripts, TheRock
URLs, Linux/Windows driver sources, run settings) come from
.github/orchestrai-config.yml. Credentials come from env
(ORCHESTRAI_PIPELINE_USER / ORCHESTRAI_PIPELINE_TOKEN).

Usage:
    orchestrai_trigger.py [--config .github/orchestrai-config.yml] [--dry-run]

Inputs (env):
    BATCHES_JSON            batches from orchestrai_matrix.py
    GIT_REF                 github.ref (recorded as PLAYBOOK_REF)
    MACHINES_PER_HW_GROUP   override; falls back to config default
    ORCHESTRAI_PIPELINE_USER, ORCHESTRAI_PIPELINE_TOKEN

Outputs:
    build_urls={...}  -> $GITHUB_OUTPUT   (batch_id -> OrchestrAI pipeline build URL)
    --dry-run prints each plan/builds payload and POSTs nothing.

Fails fast (exit 1) on a misconfigured run rather than acquiring scarce
hardware that can't provision: missing config keys, missing creds, or a batch
whose required provisioning value (TheRock URL or Linux/Windows driver source)
is unset.
"""

import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import yaml

# Request timeouts so a stalled OrchestrAI pipeline can never hang the job (vs the
# default: wait forever). Values are generous; the point is a finite ceiling, not
# tight SLAs.
POST_TIMEOUT = 120
POLL_TIMEOUT = 30
# The submit (buildWithParameters POST) is retried, because a submit that fails
# before Jenkins creates a queue item leaves nothing behind and re-sending is
# safe. A submit that DID create a queue item is never retried (see trigger()),
# so a slow queue can never produce a duplicate build on scarce hardware.
SUBMIT_ATTEMPTS = 3
SUBMIT_BACKOFF = 5  # seconds, multiplied by the attempt number


def load_config(path):
    with open(path) as f:
        return yaml.safe_load(f)


def apply_env_overrides(cfg):
    """Internal coordinates are kept out of the committed (public) config and
    supplied at run time via repo variables. Env values win over config."""
    j = cfg.setdefault("pipeline", {})
    j["url"] = os.environ.get("ORCHESTRAI_PIPELINE_URL") or j.get("url", "")
    j["job"] = os.environ.get("ORCHESTRAI_PIPELINE_JOB") or j.get("job", "")
    prov = cfg.setdefault("provisioning", {})
    therock = os.environ.get("ORCHESTRAI_THEROCK_URL")
    if therock:
        prov["therock_url"] = therock
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
    return cfg


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
    prov = cfg.get("provisioning") or {}
    platforms = {b.get("platform") for b in batches.values()}
    if "linux" in platforms and not prov.get("linux_install_scripts"):
        errs.append("provisioning.linux_install_scripts")
    if "windows" in platforms and not prov.get("windows_install_scripts"):
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
            "PLAYBOOK_DEVICE": device,
            "ROCM_MULTI_ARCH_INDEX_URL": rocm_index_url,
        }
        # Authenticate HuggingFace traffic (models/datasets primed by deps fall
        # back to a live HF pull on a mirror miss; unauthenticated calls from the
        # shared egress IP hit HF's per-IP rate limit). Optional: omitted when the
        # secret is unset so runs still work (just unauthenticated).
        if hf_token:
            variables["HF_TOKEN"] = hf_token
        groups.append({
            "id": f"playbook-{pb_id}",
            "level": "L4-sys",
            "tests": [test],
            "maas_tags": tags,
            "variables": variables,
        })

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


def make_builds(batch, cfg):
    """Return (builds, missing) — missing names required provisioning vars left empty."""
    platform = batch["platform"]
    prov = cfg.get("provisioning", {})
    missing = []

    if platform == "windows":
        # Copy so appending per-playbook extras below doesn't mutate cfg.
        scripts = list(prov.get("windows_install_scripts", []))
        drv = prov.get("windows_driver", {})
        source = drv.get("source", "")
        if not source:
            missing.append("ORCHESTRAI_WINDOWS_DRIVER_SOURCE")
        build_vars = {"driver_source": source, "driver_copy": drv.get("copy", "direct")}
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

    # Per-playbook extra provisioning scripts (e.g. enabling WSL for
    # openclaw-lemonade-server). Appended only to batches that actually contain
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
            script = entry.get("script")
            if not script or script in seen:
                continue
            seen.add(script)
            scripts.append({
                "script": script,
                "reboot_after": bool(entry.get("reboot_after", False)),
            })

    builds = {"install_scripts": scripts, "vars": build_vars}
    return builds, missing


def auth_header(user, token):
    """Basic-auth header value, built in memory.

    SECURITY: the credentials are deliberately NOT handed to a `curl -u
    user:token` subprocess. argv is world-readable via /proc/<pid>/cmdline and
    `ps` for the lifetime of the process, so on a shared/persistent self-hosted
    runner any other local process could read the pipeline token. Doing the HTTP
    in-process keeps the secret in this process's memory only.
    """
    return "Basic " + base64.b64encode(f"{user}:{token}".encode()).decode()


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Match curl's default (no -L): don't follow redirects, so the queue URL is
    read from the original response's Location header."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def submit(plan, builds, platform, pipeline, user, token):
    """POST the build request; return the queue-item URL, or None on failure.

    A None return means no queue item was created (network error, timeout, or a
    non-redirect HTTP error), so the caller may safely retry without risking a
    duplicate build.
    """
    os_image = "windows" if platform == "windows" else "ubuntu"
    # Same wire format as the previous `curl --data-urlencode NAME@file`: a
    # urlencoded form body. Building it here also drops the temp files entirely.
    body = urllib.parse.urlencode({
        "PLAN_JSON": json.dumps(plan),
        "BUILDS_JSON": json.dumps(builds),
        "OS_IMAGE": os_image,
    }).encode()

    req = urllib.request.Request(
        f"{pipeline['url']}/job/{pipeline['job']}/buildWithParameters",
        data=body, method="POST")
    req.add_header("Authorization", auth_header(user, token))
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.build_opener(_NoRedirect).open(req, timeout=POST_TIMEOUT) as r:
            return (r.headers.get("Location") or "").strip() or None
    except urllib.error.HTTPError as e:
        # Redirects surface as HTTPError because they're disabled above; a 3xx
        # still carries the queue item in Location. Anything else is a failure
        # (matches `curl -sf`, which fails on HTTP errors).
        if 300 <= e.code < 400:
            return (e.headers.get("Location") or "").strip() or None
        return None
    except Exception:
        return None


def await_build(queue_url, user, token):
    """Poll a queue item until Jenkins assigns it an executable; return its URL."""
    for _ in range(60):
        time.sleep(10)
        try:
            q = urllib.request.Request(f"{queue_url}api/json")
            q.add_header("Authorization", auth_header(user, token))
            with urllib.request.urlopen(q, timeout=POLL_TIMEOUT) as resp:
                payload = json.loads(resp.read().decode("utf-8", "replace"))
            exe = payload.get("executable", {})
            if exe and exe.get("url"):
                return exe["url"]
        except Exception:
            pass
    return None


def trigger(plan, builds, platform, pipeline, user, token):
    """Submit a build and return its URL, or None if it could not be created.

    Only the submit is retried: a failed submit leaves no queue item, so
    re-sending is safe. Once a submit succeeds we hold that one queue URL and
    only wait on it, so a slow queue never spawns a duplicate build.
    """
    queue_url = None
    for attempt in range(1, SUBMIT_ATTEMPTS + 1):
        queue_url = submit(plan, builds, platform, pipeline, user, token)
        if queue_url:
            break
        if attempt < SUBMIT_ATTEMPTS:
            print(f"  submit attempt {attempt}/{SUBMIT_ATTEMPTS} failed; retrying",
                  file=sys.stderr)
            time.sleep(SUBMIT_BACKOFF * attempt)
    if not queue_url:
        return None
    return await_build(queue_url, user, token)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=".github/orchestrai-config.yml")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cfg = apply_env_overrides(load_config(args.config))
    batches = json.loads(os.environ.get("BATCHES_JSON", "{}") or "{}")
    git_ref = os.environ.get("GIT_REF", "")
    user = os.environ.get("ORCHESTRAI_PIPELINE_USER", "")
    token = os.environ.get("ORCHESTRAI_PIPELINE_TOKEN", "")

    cfg_errs = validate_config(cfg, batches)
    if cfg_errs:
        print(f"::error::orchestrai-config.yml missing required keys: {', '.join(cfg_errs)}",
              file=sys.stderr)
        sys.exit(1)

    if not args.dry_run:
        need = [f"pipeline.{k}" for k in ("url", "job") if not cfg["pipeline"].get(k)]
        if not user:
            need.append("ORCHESTRAI_PIPELINE_USER")
        if not token:
            need.append("ORCHESTRAI_PIPELINE_TOKEN")
        if need:
            print(f"::error::OrchestrAI not configured — missing: {', '.join(need)} "
                  f"(set ORCHESTRAI_PIPELINE_URL/JOB vars and ORCHESTRAI_PIPELINE_* secrets)",
                  file=sys.stderr)
            sys.exit(1)

    rs = cfg["run_settings"]
    try:
        mphg = int(os.environ.get("MACHINES_PER_HW_GROUP", "")
                   or rs.get("default_machines_per_hw_group", 1))
    except ValueError:
        mphg = 1

    # The pipeline clones PLAYBOOK_REPO@PLAYBOOK_SHA on the test machine. By
    # default that's the configured repo at main; the !orc PR path overrides both
    # so the PR's own code (including a fork head) is what actually gets tested.
    repo = os.environ.get("ORCHESTRAI_PLAYBOOK_REPO") or cfg["playbook_repo"]
    sha = os.environ.get("ORCHESTRAI_PLAYBOOK_SHA") or "main"
    rocm_index_url = os.environ.get("ORCHESTRAI_ROCM_MULTI_ARCH_INDEX_URL", "")
    if not rocm_index_url:
        print("::error::ORCHESTRAI_ROCM_MULTI_ARCH_INDEX_URL repository variable is required",
              file=sys.stderr)
        sys.exit(1)

    # Optional: HuggingFace token so live HF pulls (dep cache misses, uncached
    # datasets) are authenticated and avoid the shared-IP rate limit. Not
    # required -- runs still work unauthenticated, just exposed to 429s.
    hf_token = os.environ.get("ORCHESTRAI_HF_TOKEN", "")
    if not hf_token:
        print("::warning::ORCHESTRAI_HF_TOKEN not set — HuggingFace traffic will be "
              "unauthenticated and may hit the shared-IP rate limit (429)", file=sys.stderr)

    # Prepare every batch first, and fail fast (before any POST) if a batch is
    # missing required provisioning — otherwise we'd acquire a scarce machine
    # that can't install its GPU stack and only fail much later on hardware.
    prepared = []
    prov_missing = {}
    for bid, batch in batches.items():
        builds, missing = make_builds(batch, cfg)
        if missing:
            prov_missing[bid] = missing
        prepared.append((bid, batch,
                         make_plan(batch, git_ref, cfg, mphg, repo, sha,
                                   rocm_index_url, hf_token),
                         builds))

    if not args.dry_run and prov_missing:
        for bid, miss in prov_missing.items():
            print(f"::error::batch {bid}: unset provisioning {miss} — "
                  f"set the corresponding repo variable(s)", file=sys.stderr)
        sys.exit(1)

    build_urls = {}
    failed = []
    for bid, batch, plan, builds in prepared:
        print(f"Batch {bid}: {', '.join(batch['playbooks'])}", file=sys.stderr)
        if args.dry_run:
            print(f"--- plan for {bid} ---")
            print(json.dumps(plan, indent=2))
            print(f"--- builds for {bid} ---")
            print(json.dumps(builds, indent=2))
            continue
        url = trigger(plan, builds, batch["platform"], cfg["pipeline"], user, token)
        if url:
            print(f"  Build: {url}", file=sys.stderr)
            build_urls[bid] = url
        else:
            failed.append(bid)
            print(f"  WARNING: trigger failed / timed out for {bid}", file=sys.stderr)

    print(f"\nTriggered {len(build_urls)} OrchestrAI pipeline build(s)", file=sys.stderr)

    # Emit the URLs FIRST so the batches that did trigger still run downstream,
    # even if we exit non-zero for an empty result below.
    out = os.environ.get("GITHUB_OUTPUT")
    if out and not args.dry_run:
        with open(out, "a") as f:
            f.write(f"build_urls={json.dumps(build_urls)}\n")

    if args.dry_run:
        return

    # Surface dropped batches HERE, at the trigger, instead of letting each of
    # their downstream test jobs discover the gap one-by-one as "No build URL".
    if not build_urls:
        # Nothing triggered at all: fail hard. There is no partial run to
        # preserve, and every downstream job would otherwise fail identically.
        print("::error::No OrchestrAI pipeline builds were triggered — every batch "
              f"failed to submit ({len(failed)} batch(es): {', '.join(failed)}). "
              "The pipeline was likely unreachable or rejecting builds.",
              file=sys.stderr)
        sys.exit(1)
    if failed:
        # Some batches triggered. Do NOT exit non-zero: that would skip the
        # good batches (downstream jobs `needs` this one). A prominent error
        # annotation names the dropped batches so the cause is visible at the
        # trigger; their own downstream jobs still fail, so the run as a whole
        # is not reported green.
        print(f"::error::{len(failed)} batch(es) failed to trigger and will report "
              f"no build URL downstream: {', '.join(failed)}. The other "
              f"{len(build_urls)} batch(es) were triggered and will run.",
              file=sys.stderr)


if __name__ == "__main__":
    main()
