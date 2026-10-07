#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
Playbook Prerequisite Validator
===============================

Runs on a CI runner *before* ``run_playbook_tests.py`` to make sure the
prerequisites a playbook needs are actually present on the machine -- and to
**self-heal** the runner by installing anything that is missing.

For each ``@require:<dep>`` or ``@prereq:<dep>`` a playbook declares (scoped to the active
``@os:``/``@device:`` blocks), this reads a ``validate`` and optional
``install`` step from ``playbooks/dependencies/registry.json`` and runs a
validate -> (if missing) install -> re-validate loop. A step is an inline ``cmd``
or a ``script`` under ``.github/scripts/prereqs/``. An install step may also name
a ``mirror`` group, seeded first (``mirror/get.py seed``) so the install runs only
if still needed. A step that is only a ``mirror`` group checks or seeds the cache
of models the tests download themselves; such dependencies are ``optional``, so a
miss warns.

    validate passes                -> OK                 (provisioned; no install)
    validate fails, install fixes  -> INSTALLED          (self-healed; job continues)
    validate fails, install fails  -> FAILED             (hard fail)
    validate fails, no install     -> MISSING_NO_INSTALL (hard fail)
    no validate for this platform  -> unchecked          (nothing to verify)

Exit code is non-zero only when a dependency ends FAILED or MISSING_NO_INSTALL.
A per-dependency status report is always written to
``test-results/<playbook>/prereq.json`` so a self-heal (or a hard fail) is
visible in the uploaded CI artifacts and is clearly distinct from an ordinary
test failure.

Usage:
    python prereq_validate.py --playbook <id> --platform linux|windows [--device <device>] [--locale <locale>]
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

VALID_DEVICES = {"halo", "stx", "krk", "rx7900xt", "rx9070xt", "r9700"}
# halo_box is a valid @device: scope in READMEs even though it is not a CI
# --device value, so accept it when matching require scopes.
KNOWN_DEVICE_SCOPES = VALID_DEVICES | {"halo_box"}
# Multi-step recipes live here as files; registry steps reference them via "script".
PREREQ_SCRIPTS_DIR = Path(__file__).parent / "prereqs"
# Seeds an install step's "mirror" group into its tool's store before the install runs.
MIRROR_GET = Path(__file__).parent / "mirror" / "get.py"
# A fully seeded tool may notice its new files a few seconds later (LM Studio's folder watcher).
SEED_SETTLE_TRIES, SEED_SETTLE_SECONDS = 4, 5


def find_playbook_path(playbook_id: str, repo_root: Path, locale: str = "") -> Optional[Path]:
    """Find the playbook directory by ID (mirrors run_playbook_tests.py); a locale's own README replaces English."""
    base = repo_root / "localized-playbooks" / locale if locale else repo_root / "playbooks"
    for category in ["core", "supplemental"]:
        playbook_path = base / category / playbook_id
        if playbook_path.exists() and (playbook_path / "README.md").exists():
            return playbook_path
    return None


def load_registry(repo_root: Path, locale: str = "") -> dict:
    """English dependencies, overlaid field by field with a locale's own.

    A locale's entry localizes the docs and may add its own steps; steps it leaves
    out come from English, so a shared dependency is checked the same way everywhere.
    """
    deps = json.loads((repo_root / "playbooks" / "dependencies" / "registry.json").read_text(encoding="utf-8"))
    deps = deps.get("dependencies", {})
    localized = repo_root / "localized-playbooks" / locale / "dependencies" / "registry.json"
    if locale and localized.is_file():
        for dep_id, spec in json.loads(localized.read_text(encoding="utf-8")).get("dependencies", {}).items():
            deps[dep_id] = {**deps.get(dep_id, {}), **spec}
    return deps


def extract_scoped_requires(
    content: str, platform: str, device: Optional[str]
) -> list[str]:
    """Return the ordered, de-duplicated list of dep-ids that apply to the
    active platform/device.

    Two tags are honored, and their results are unioned:

    * ``@require:<ids>`` -- the existing tag. It is also consumed by the website,
      which inlines each dependency doc at the tag site, so it is user-facing.
    * ``@prereq:<ids>``  -- CI-only. Nothing renders it, so it declares a
      dependency that must be validated (and auto-installed) before the tests
      run without changing any published page.

    Either tag may be wrapped in ``@os:<p>``/``@device:<d,...>`` blocks. A tag is
    in scope when the current @os block (if any) matches ``platform`` AND the
    current @device block (if any) matches ``device``. A tag with no enclosing
    block of a given kind is unscoped for that kind (applies to all).
    """
    os_re = re.compile(r"<!--\s*@os:([\w,]+)\s*-->")
    os_end_re = re.compile(r"<!--\s*@os:end\s*-->")
    dev_re = re.compile(r"<!--\s*@device:([\w,]+)\s*-->")
    dev_end_re = re.compile(r"<!--\s*@device:end\s*-->")
    # Matches @require: and @prereq: alike; both feed the same dependency list.
    req_re = re.compile(r"<!--\s*@(?:require|prereq):([a-z0-9\-,]+)\s*-->")

    cur_os: Optional[set[str]] = None
    cur_dev: Optional[set[str]] = None
    ordered: list[str] = []
    seen: set[str] = set()

    for line in content.splitlines():
        # End tags must be checked before the open patterns: the open regex
        # ``@os:([\w,]+)`` would otherwise match ``@os:end`` as a block named
        # "end".
        if os_end_re.search(line):
            cur_os = None
            continue
        m = os_re.search(line)
        if m:
            cur_os = {p.strip() for p in m.group(1).split(",") if p.strip()}
            continue
        if dev_end_re.search(line):
            cur_dev = None
            continue
        m = dev_re.search(line)
        if m:
            cur_dev = {d.strip() for d in m.group(1).split(",") if d.strip()}
            continue

        m = req_re.search(line)
        if not m:
            continue

        # OS scope: if an @os block is active and doesn't include our platform, skip.
        if cur_os is not None and platform not in cur_os:
            continue
        # Device scope: if a @device block is active, only apply when it names a
        # known device scope AND (we have no --device, or our device is listed).
        if cur_dev is not None:
            device_scopes = cur_dev & KNOWN_DEVICE_SCOPES
            if device_scopes and device is not None and device not in cur_dev:
                continue

        for dep_id in (d.strip() for d in m.group(1).split(",")):
            if dep_id and dep_id not in seen:
                seen.add(dep_id)
                ordered.append(dep_id)

    return ordered


def _step_args(step: dict, platform: str) -> list[str]:
    """Build argv for a registry step: an inline ``cmd``, or a ``script`` under prereqs/."""
    script = step.get("script")
    if script:
        path = str(PREREQ_SCRIPTS_DIR / script)
        if platform == "windows":
            return ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", path]
        return ["bash", path]
    if platform == "windows":
        # Use PowerShell so validate/install strings match the doc conventions.
        return ["powershell", "-NoProfile", "-Command", step["cmd"]]
    return ["bash", "-c", step["cmd"]]


def _run(step: dict, platform: str, timeout: int) -> int:
    """Run a registry step and return its exit code (best-effort)."""
    if step.get("script") and not (PREREQ_SCRIPTS_DIR / step["script"]).is_file():
        print(f"  (prereq script not found: {step['script']})")
        return 127
    return _run_args(_step_args(step, platform), timeout)


def _mirror(command: str, group: str, timeout: int) -> int:
    """mirror/get.py seed or present, for one artifacts.json group."""
    return _run_args([sys.executable, str(MIRROR_GET), command, group], timeout)


def _run_args(args: list[str], timeout: int) -> int:
    """Run a command with bounded, surfaced output and return its exit code."""
    # Scripts run mirror/get.py with this interpreter, not whatever `python` resolves to.
    env = dict(os.environ, PREREQ_PYTHON=sys.executable)
    try:
        proc = subprocess.run(
            args,
            timeout=timeout,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=env,
        )
        if proc.stdout:
            # Surface command output for CI logs, but keep it bounded.
            sys.stdout.write(proc.stdout[-4000:])
            sys.stdout.flush()
        return proc.returncode
    except subprocess.TimeoutExpired:
        print(f"  (timed out after {timeout}s)")
        return 124
    except Exception as exc:  # pragma: no cover - defensive
        print(f"  (failed to launch: {exc})")
        return 1


def _registry_path_entries() -> list[str]:
    """Machine then user PATH as the Windows registry holds it now (installers write there)."""
    import winreg
    entries = []
    for root, key in ((winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
                      (winreg.HKEY_CURRENT_USER, "Environment")):
        try:
            with winreg.OpenKey(root, key) as handle:
                value = winreg.QueryValueEx(handle, "Path")[0]
        except OSError:
            continue
        entries += [winreg.ExpandEnvironmentStrings(p) for p in value.split(";") if p]
    return entries


def _refresh_windows_path() -> None:
    """Pick up PATH entries an install just added, for the re-validate and, via GITHUB_PATH, the tests."""
    have = {p.rstrip("\\").lower() for p in os.environ.get("PATH", "").split(os.pathsep) if p}
    new = [p for p in dict.fromkeys(_registry_path_entries()) if p.rstrip("\\").lower() not in have]
    if not new:
        return
    os.environ["PATH"] = os.pathsep.join(new + [os.environ.get("PATH", "")])
    if os.environ.get("GITHUB_PATH"):
        with open(os.environ["GITHUB_PATH"], "a", encoding="utf-8") as fh:
            fh.writelines(p + "\n" for p in new)
    print(f"  (PATH now also has: {'; '.join(new)})")


def _validate(spec: dict, platform: str) -> bool:
    v = (spec.get("validate") or {}).get(platform)
    if not v:
        return False
    timeout = v.get("timeout", 60)
    rc = _mirror("present", v["mirror"], timeout) if _mirror_only(v) else _run(v, platform, timeout)
    return rc == v.get("expect_rc", 0)


def _mirror_only(step: dict) -> bool:
    return bool(step.get("mirror")) and not (step.get("cmd") or step.get("script"))


def check_dependency(dep_id: str, spec: dict, platform: str) -> dict:
    """Run the validate -> install -> re-validate loop for one dependency."""
    result = {"dep": dep_id, "status": "unchecked", "install_ran": False}

    validate = (spec.get("validate") or {}).get(platform)
    if not validate:
        print(f"- {dep_id}: no validate command for {platform} -> unchecked")
        return result

    print(f"- {dep_id}: validating ...")
    if _validate(spec, platform):
        result["status"] = "OK"
        print(f"  OK: {dep_id} present")
        return result

    # ---- validate miss: attempt self-heal ----
    install = (spec.get("install") or {}).get(platform)
    if not install:
        # Optional deps warn instead of hard-failing: the runner may have the
        # prerequisite provisioned in a way our check can't see (e.g. an LM
        # Studio model whose CLI needs a running backend), so we record the
        # miss for diagnostics but let the job proceed to its tests.
        if spec.get("optional"):
            result["status"] = "MISSING_OPTIONAL"
            print(f"  WARN: {dep_id} not detected and no install recipe; continuing (optional)")
        else:
            result["status"] = "MISSING_NO_INSTALL"
            print(f"  MISSING: {dep_id} not present and no install recipe for {platform}")
        return result

    print(f"  MISSING: {dep_id} -> installing (this may take a while) ...")
    result["install_ran"] = True
    timeout = install.get("timeout", 1800)
    if install.get("mirror"):
        result["mirror_rc"] = _mirror("seed", install["mirror"], timeout)
        for attempt in range(SEED_SETTLE_TRIES if result["mirror_rc"] == 0 else 1):
            if attempt:
                time.sleep(SEED_SETTLE_SECONDS)
            if _validate(spec, platform):
                result["status"] = "INSTALLED"
                print(f"  INSTALLED: {dep_id} now present (from the internal mirror)")
                return result
    if not _mirror_only(install):
        result["install_rc"] = _run(install, platform, timeout)
        if platform == "windows":
            _refresh_windows_path()

    print(f"  re-validating {dep_id} ...")
    if _validate(spec, platform):
        result["status"] = "INSTALLED"
        print(f"  INSTALLED: {dep_id} now present")
    elif spec.get("optional"):
        # Optional means the tests can get it themselves; the prereq only gets it ahead of them.
        result["status"] = "MISSING_OPTIONAL"
        print(f"  WARN: {dep_id} still missing after install; continuing (optional)")
    else:
        result["status"] = "FAILED"
        print(f"  FAILED: {dep_id} still missing after install")
    return result


def validate_prereqs(playbook_id: str, platform: str, device: Optional[str], locale: str = "") -> bool:
    repo_root = Path(__file__).parent.parent.parent
    label = f"{locale}/{playbook_id}" if locale else playbook_id

    playbook_path = find_playbook_path(playbook_id, repo_root, locale)
    if not playbook_path:
        print(f"Error: playbook '{label}' not found")
        return False

    try:
        deps_map = load_registry(repo_root, locale)
    except Exception as exc:
        print(f"Error: could not read registry.json: {exc}")
        return False

    content = (playbook_path / "README.md").read_text(encoding="utf-8")
    required = extract_scoped_requires(content, platform, device)

    scope = f"{platform}/{device}" if device else platform
    print(f"Prerequisite validation for {label} ({scope})")
    if not required:
        print("No @require/@prereq dependencies in scope; nothing to validate.")
    print(f"In-scope dependencies: {', '.join(required) if required else '(none)'}\n")

    results = []
    for dep_id in required:
        spec = deps_map.get(dep_id)
        if not spec:
            print(f"- {dep_id}: not found in registry -> unchecked")
            results.append({"dep": dep_id, "status": "unchecked", "install_ran": False})
            continue
        results.append(check_dependency(dep_id, spec, platform))

    # Always write a report artifact.
    results_dir = repo_root / "test-results" / playbook_id
    results_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "playbook_id": playbook_id,
        "platform": platform,
        "device": device,
        "required": required,
        "results": results,
    }
    (results_dir / "prereq.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    unresolved = [r for r in results if r["status"] in ("FAILED", "MISSING_NO_INSTALL")]
    healed = [r for r in results if r["status"] == "INSTALLED"]

    print()
    if healed:
        names = ", ".join(r["dep"] for r in healed)
        print(f"Self-healed on runner: {names}")

    if unresolved:
        print("=" * 60)
        print(f"PREREQ UNRESOLVED - {label} ({scope})")
        for r in unresolved:
            why = (
                "auto-install did not resolve it"
                if r["status"] == "FAILED"
                else "auto-install is not available"
            )
            print(f"  {r['dep']}: missing and {why}.")
        print("  -> runner-provisioning issue, NOT a playbook bug.")
        print("=" * 60)
        return False

    print(f"All prerequisites satisfied for {label} ({scope}).")
    return True


def main():
    parser = argparse.ArgumentParser(description="Validate & provision playbook prerequisites")
    parser.add_argument("--playbook", required=True, help="Playbook ID")
    parser.add_argument(
        "--platform", required=True, choices=["windows", "linux"], help="Target platform"
    )
    parser.add_argument(
        "--device",
        choices=sorted(VALID_DEVICES),
        default=None,
        help="Target device (filters @device: blocks)",
    )
    parser.add_argument("--locale", default="", help="Check a localized playbook, e.g. zh-CN")
    args = parser.parse_args()

    ok = validate_prereqs(args.playbook, args.platform, args.device, args.locale)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
