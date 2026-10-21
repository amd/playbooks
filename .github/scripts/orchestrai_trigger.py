#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
OrchestrAI pipeline trigger
==========================

For each batch (one per platform/device[+extra-tags]) builds a plan -- one
session per playbook, sharing the batch's hardware -- and starts it through the
OrchestrAI Control Plane CI API (GitHub OIDC; see .github/orchestrai/V2.md).
Waits until the Control Plane has started each batch's pipeline build and
records its URL so the matrix jobs can wait on it.

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
    build_urls={...}  -> $GITHUB_OUTPUT   (batch_id -> pipeline build URL)
    run_urls={...}    -> $GITHUB_OUTPUT   (batch_id -> OrchestrAI run URL)
    --dry-run prints each plan/builds payload and starts nothing.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.parse

import yaml

ORCHESTRAI_LIB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              "orchestrai")
sys.path.insert(0, ORCHESTRAI_LIB)

def load_config(path):
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
    elif isinstance(rs.get("max_duration"), int) and 0 < rs["max_duration"] <= (acquire or 0):
        # The acquire wait counts against the build's overall time limit, so a
        # timeout this long would leave no time to run anything.
        errs.append(f"run_settings.acquire_timeout ({acquire}m) must be shorter than "
                    f"run_settings.max_duration ({rs['max_duration']}m)")
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
            "PLAYBOOK_DEVICE": device,
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=".github/orchestrai-config.yml")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

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
    prov_missing = {}
    for bid, batch in batches.items():
        builds, missing = make_builds(batch, cfg)
        if missing:
            prov_missing[bid] = missing
        if args.dry_run:
            print(f"--- plan for {bid} ---")
            print(json.dumps(make_plan(batch, git_ref, cfg, mphg, repo, sha, rocm_index_url), indent=2))
            print(f"--- builds for {bid} ---")
            print(json.dumps(builds, indent=2))
    if args.dry_run:
        return
    if prov_missing:
        for bid, miss in prov_missing.items():
            print(f"::error::batch {bid}: unset provisioning {miss} — "
                  f"set the corresponding repo variable(s)", file=sys.stderr)
        sys.exit(1)

    import orchestrai_v2  # noqa: E402  (imports this module; loaded lazily)
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
        sha = resolve_sha(repo, sha)
        build_urls, run_urls = orchestrai_v2.trigger_batches(
            batches, cfg, sha, orchestrai_v2.resolve_workspace(""), publisher,
            os.environ.get("RUNNER_TEMP", ".") + "/orchestrai-v2-state",
            git_ref=git_ref, machines_per_hw_group=mphg)
    except (ValueError, subprocess.SubprocessError) as exc:
        print(f"::error::{exc}", file=sys.stderr)
        sys.exit(1)
    failed = [bid for bid in batches if bid not in build_urls]
    print(f"\nTriggered {len(build_urls)} OrchestrAI pipeline build(s)", file=sys.stderr)

    # Emit the URLs FIRST so the batches that did trigger still run downstream,
    # even if we exit non-zero for an empty result below.
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"build_urls={json.dumps(build_urls)}\n")
            f.write(f"run_urls={json.dumps(run_urls)}\n")

    # Surface dropped batches HERE, at the trigger, instead of letting each of
    # their downstream test jobs discover the gap one-by-one as "No build URL".
    if not build_urls:
        # Nothing triggered at all: fail hard. There is no partial run to
        # preserve, and every downstream job would otherwise fail identically.
        print("::error::No OrchestrAI pipeline builds were triggered — every batch "
              f"failed to submit ({len(failed)} batch(es): {', '.join(failed)}).",
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
