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

For each ``@require:<dep>`` a playbook declares (scoped to the active
``@os:``/``@device:`` blocks), this reads a ``validate`` and optional
``install`` command from ``playbooks/dependencies/registry.json`` and runs a
validate -> (if missing) install -> re-validate loop:

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
    python prereq_validate.py --playbook <id> --platform linux|windows [--device <device>]
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

VALID_DEVICES = {"halo", "stx", "krk", "rx7900xt", "rx9070xt", "r9700"}
# halo_box is a valid @device: scope in READMEs even though it is not a CI
# --device value, so accept it when matching require scopes.
KNOWN_DEVICE_SCOPES = VALID_DEVICES | {"halo_box"}


def find_playbook_path(playbook_id: str, repo_root: Path) -> Optional[Path]:
    """Find the playbook directory by ID (mirrors run_playbook_tests.py)."""
    for category in ["core", "supplemental"]:
        playbook_path = repo_root / "playbooks" / category / playbook_id
        if playbook_path.exists() and (playbook_path / "README.md").exists():
            return playbook_path
    return None


def extract_scoped_requires(
    content: str, platform: str, device: Optional[str]
) -> list[str]:
    """Return the ordered, de-duplicated list of @require dep-ids that apply
    to the active platform/device.

    @require tags may be wrapped in ``@os:<p>``/``@device:<d,...>`` blocks. A
    require is in scope when the current @os block (if any) matches ``platform``
    AND the current @device block (if any) matches ``device``. A require with no
    enclosing block of a given kind is unscoped for that kind (applies to all).
    """
    os_re = re.compile(r"<!--\s*@os:([\w,]+)\s*-->")
    os_end_re = re.compile(r"<!--\s*@os:end\s*-->")
    dev_re = re.compile(r"<!--\s*@device:([\w,]+)\s*-->")
    dev_end_re = re.compile(r"<!--\s*@device:end\s*-->")
    req_re = re.compile(r"<!--\s*@require:([a-z0-9\-,]+)\s*-->")

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


def _run(cmd: str, platform: str, timeout: int) -> int:
    """Run a shell command and return its exit code (best-effort)."""
    shell_exe = None
    if platform == "windows":
        # Use PowerShell so validate/install strings match the doc conventions.
        args = ["powershell", "-NoProfile", "-Command", cmd]
    else:
        args = ["bash", "-c", cmd]
    try:
        proc = subprocess.run(
            args,
            timeout=timeout,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
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


def _validate(spec: dict, platform: str) -> bool:
    v = (spec.get("validate") or {}).get(platform)
    if not v:
        return False
    rc = _run(v["cmd"], platform, v.get("timeout", 60))
    return rc == v.get("expect_rc", 0)


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
    install_rc = _run(install["cmd"], platform, install.get("timeout", 1800))
    result["install_rc"] = install_rc

    print(f"  re-validating {dep_id} ...")
    if _validate(spec, platform):
        result["status"] = "INSTALLED"
        print(f"  INSTALLED: {dep_id} now present")
    else:
        result["status"] = "FAILED"
        print(f"  FAILED: {dep_id} still missing after install")
    return result


def validate_prereqs(playbook_id: str, platform: str, device: Optional[str]) -> bool:
    repo_root = Path(__file__).parent.parent.parent
    dependencies_root = repo_root / "playbooks" / "dependencies"
    registry_path = dependencies_root / "registry.json"

    playbook_path = find_playbook_path(playbook_id, repo_root)
    if not playbook_path:
        print(f"Error: playbook '{playbook_id}' not found")
        return False

    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Error: could not read registry.json: {exc}")
        return False
    deps_map = registry.get("dependencies", {})

    content = (playbook_path / "README.md").read_text(encoding="utf-8")
    required = extract_scoped_requires(content, platform, device)

    scope = f"{platform}/{device}" if device else platform
    print(f"Prerequisite validation for {playbook_id} ({scope})")
    if not required:
        print("No @require dependencies in scope; nothing to validate.")
    print(f"In-scope requires: {', '.join(required) if required else '(none)'}\n")

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
        print(f"PREREQ UNRESOLVED - {playbook_id} ({scope})")
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

    print(f"All prerequisites satisfied for {playbook_id} ({scope}).")
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
    args = parser.parse_args()

    ok = validate_prereqs(args.playbook, args.platform, args.device)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
