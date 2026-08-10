#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
Run tests from a human-authored localized playbook.

This adapter reuses the canonical run_playbook_tests.py engine without changing
the canonical English CI behavior. It only replaces:

1. playbook directory resolution;
2. @require dependency resolution.

Resolution order for dependency files:

    localized-playbooks/<locale>/dependencies/
    playbooks/dependencies/
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Optional
import run_playbook_tests as base


def materialize_playbook(locale: str, playbook_id: str, destination: Path) -> Path:
    """Build a per-file localized overlay in a temporary directory."""
    repo_root = Path(__file__).parent.parent.parent

    localized_candidates = [
        repo_root / "localized-playbooks" / locale / category / playbook_id
        for category in ("core", "supplemental")
    ]
    localized_matches = [
        candidate
        for candidate in localized_candidates
        if candidate.is_dir()
    ]

    if not localized_matches:
        raise ValueError(f"Localized playbook directory does not exist: localized-playbooks/{locale}/{{core,supplemental}}/{playbook_id}")

    if len(localized_matches) > 1:
        raise ValueError(f"Localized playbook ID '{playbook_id}' exists in both core and supplemental")

    localized_source = localized_matches[0]
    category = localized_source.parent.name

    # Copy from lowest to highest precedence. copytree(..., dirs_exist_ok=True)
    # replaces individual files while preserving files missing from an overlay.
    layers = [
        repo_root / "playbooks" / category / playbook_id,
        localized_source,
    ]

    for layer in layers:
        if layer.is_dir():
            shutil.copytree(layer, destination, dirs_exist_ok=True)

    if not (destination / "README.md").is_file():
        raise ValueError(f"No effective README.md found for localized playbook '{locale}/{category}/{playbook_id}'")

    return destination


def load_dependency_registry(locale: str) -> dict:
    """Load English registry and apply an optional human-localized override."""
    repo_root = Path(__file__).parent.parent.parent

    merged_dependencies: dict = {}

    english_registry = repo_root / "playbooks" / "dependencies" / "registry.json"

    localized_registry = repo_root / "localized-playbooks" / locale / "dependencies" / "registry.json"

    for registry_path in (english_registry, localized_registry):
        if not registry_path.is_file():
            continue

        try:
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise RuntimeError(f"Unable to read dependency registry {registry_path}: {error}") from error

        dependencies = registry.get("dependencies", {})

        if not isinstance(dependencies, dict):
            raise ValueError(f"'dependencies' in {registry_path} must be an object")

        merged_dependencies.update(dependencies)

    return merged_dependencies


def find_localized_dependency(locale: str, relative_file: str) -> Optional[Path]:
    """Resolve one dependency file using the repository overlay order."""
    repo_root = Path(__file__).parent.parent.parent

    candidates = [
        repo_root / "localized-playbooks" / locale / "dependencies" / relative_file,
        repo_root / "playbooks" / "dependencies" / relative_file,
    ]

    return next((candidate for candidate in candidates if candidate.is_file()), None)


def resolve_localized_require_tags(locale: str, content: str) -> str:
    """Expand @require tags using localized dependency overlays."""

    deps_map = load_dependency_registry(locale)

    require_pattern = r"<!-- @require:([a-z0-9-,]+) -->"

    def _replace_require(match: re.Match[str]) -> str:
        dep_ids = [d.strip() for d in match.group(1).split(",") if d.strip()]
        parts: list[str] = []
        for dep_id in dep_ids:
            dep_info = deps_map.get(dep_id)
            if not dep_info:
                print(f"Warning: @require dependency '{dep_id}' not found in registry")
                continue
            if not isinstance(dep_info, dict):
                print(f"Warning: dependency '{dep_id}' has invalid registry metadata")
                continue
            rel_file = dep_info.get("file")
            if not rel_file:
                print(f"Warning: dependency '{dep_id}' does not define a file")
                continue
            dep_file = find_localized_dependency(locale, rel_file)
            if dep_file is None:
                print(f"Warning: dependency file for '{dep_id}' was not found")
                continue
            print(f"Resolved dependency '{dep_id}' from {dep_file}")
            parts.append(dep_file.read_text(encoding="utf-8"))
        return "\n".join(parts) if parts else match.group(0)

    return re.sub(require_pattern, _replace_require, content)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run tests from a human-authored localized playbook")
    parser.add_argument(
        "--playbook",
        required=True,
        help="Localized playbook ID",
    )
    parser.add_argument(
        "--platform",
        required=True,
        choices=["windows", "linux"],
        help="Target operating system",
    )
    parser.add_argument(
        "--device",
        choices=sorted(base.VALID_DEVICES),
        default=None,
        help="Target device",
    )
    parser.add_argument(
        "--locale",
        default="zh-CN",
        help="Human-authored locale to test; default: zh-CN",
    )
    args = parser.parse_args()

    temp_parent = Path(os.environ.get("RUNNER_TEMP") or tempfile.gettempdir())

    try:
        temp_parent.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(prefix="localized-playbook-", dir=temp_parent) as temp_dir:
            merged_playbook = materialize_playbook(args.locale, args.playbook, Path(temp_dir))

            # The canonical engine resolves these names from its own module
            # globals. Replacing them here leaves the original file unchanged
            # but makes this invocation use the merged localized tree.
            base.find_playbook_path = (
                lambda playbook_id: merged_playbook
                if playbook_id == args.playbook
                else None
            )
            base.resolve_require_tags = lambda content: resolve_localized_require_tags(args.locale, content)

            success = base.run_playbook_tests(args.playbook, args.platform, args.device)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    results_dir = Path.cwd() / "test-results" / args.playbook

    if results_dir.is_dir():
        locale_file = results_dir / "locale.txt"
        locale_file.write_text(f"{args.locale}\n", encoding="utf-8")

    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
