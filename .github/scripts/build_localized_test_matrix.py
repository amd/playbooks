#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""Build a GitHub Actions matrix for human-authored localized playbooks."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Optional


def locale_to_slug(locale: str) -> str:
    """Convert a locale into a lowercase GitHub runner-label segment."""

    locale_slug = re.sub(r"[^a-z0-9]+", "-", locale.lower()).strip("-")

    if not locale_slug:
        raise ValueError(f"Unable to generate a runner label from locale {locale!r}")

    return locale_slug


def load_merged_metadata(locale: str, category: str, playbook_id: str) -> dict[str, Any]:
    """Load localized metadata, optionally inheriting canonical English fields."""
    repo_root = Path(__file__).parent.parent.parent

    localized_file = repo_root / "localized-playbooks" / locale / category / playbook_id / "playbook.json"
    english_file = repo_root / "playbooks" / category / playbook_id / "playbook.json"

    localized_metadata: dict[str, Any] = {}
    if localized_file.is_file():
        localized_metadata = json.loads(localized_file.read_text(encoding="utf-8"))

    localized_only = localized_metadata.get("localized_only", True)
    if not isinstance(localized_only, bool):
        raise ValueError(f"'localized_only' in {localized_file} must be a boolean")

    metadata: dict[str, Any] = {}

    # Same-ID localized playbooks inherit English metadata unless strict
    # localized-only resolution was requested.
    if not localized_only and english_file.is_file():
        metadata.update(json.loads(english_file.read_text(encoding="utf-8")))

    # Human-authored localized metadata has the highest precedence.
    metadata.update(localized_metadata)
    # Keep the policy derived from localized metadata (including its default)
    # instead of ever inheriting this CI-only field from canonical metadata.
    metadata["localized_only"] = localized_only

    if not metadata:
        raise ValueError(f"Playbook '{playbook_id}' has no effective playbook.json metadata")

    metadata_id = metadata.get("id")

    if metadata_id != playbook_id:
        raise ValueError(f"Metadata ID mismatch for '{playbook_id}': found {metadata_id!r}")

    # A locale-only or strict localized playbook has no English metadata to
    # inherit from, so its local metadata must be complete.
    if localized_only or not english_file.is_file():
        required_fields = {
            "id",
            "title",
            "description",
            "supported_platforms",
        }

        missing = sorted(required_fields - metadata.keys())

        if missing:
            playbook_kind = "Strict localized" if localized_only else "Localized-only"
            raise ValueError(f"{playbook_kind} playbook '{playbook_id}' is missing: {', '.join(missing)}")

    return metadata


def discover_playbooks(locale: str, selected_playbooks: Optional[set[str]] = None) -> list[tuple[str, str]]:
    """Return localized playbook directories."""
    repo_root = Path(__file__).parent.parent.parent
    localized_root = repo_root / "localized-playbooks" / locale

    if not localized_root.is_dir():
        raise ValueError(f"Localized content directory does not exist: localized-playbooks/{locale}")

    discovered: list[tuple[str, str]] = []

    for category in ("core", "supplemental"):
        category_root = localized_root / category

        if not category_root.is_dir():
            continue

        for playbook_dir in sorted(category_root.iterdir()):
            if not playbook_dir.is_dir():
                continue

            playbook_id = playbook_dir.name

            if selected_playbooks is not None and playbook_id not in selected_playbooks:
                continue

            discovered.append((category, playbook_id))

    return discovered


def build_matrix(locale: str, selected_playbooks: Optional[set[str]] = None) -> list[dict[str, Any]]:
    """Build the localized hardware test matrix."""
    locale_slug = locale_to_slug(locale)
    matrix: list[dict[str, Any]] = []

    discovered = discover_playbooks(locale, selected_playbooks)

    for category, playbook_id in discovered:
        metadata = load_merged_metadata(locale, category, playbook_id)
        localized_only = metadata.get("localized_only", True)
        repo_root = Path(__file__).parent.parent.parent
        localized_readme = repo_root / "localized-playbooks" / locale / category / playbook_id / "README.md"
        english_readme = repo_root / "playbooks" / category / playbook_id / "README.md"

        if localized_only and not localized_readme.is_file():
            raise ValueError(f"Localized README.md not found for strict localized playbook '{locale}/{category}/{playbook_id}'")

        if not localized_only and not localized_readme.is_file() and not english_readme.is_file():
            raise ValueError(f"No effective README.md found for localized playbook '{locale}/{category}/{playbook_id}'")

        tested_platforms = metadata.get("tested_platforms", {})

        required_platforms = metadata.get("required_platforms", {})

        if not tested_platforms:
            print(f"Skipping '{playbook_id}': no tested_platforms metadata", file=sys.stderr)
            continue

        if not isinstance(tested_platforms, dict):
            raise ValueError(f"'tested_platforms' for '{playbook_id}' must be an object")

        if not isinstance(required_platforms, dict):
            raise ValueError(f"'required_platforms' for '{playbook_id}' must be an object")

        for device, platforms in tested_platforms.items():
            if not isinstance(device, str) or not device:
                raise ValueError(f"Invalid device name for '{playbook_id}': {device!r}")

            if not isinstance(platforms, list):
                raise ValueError(f"tested_platforms.{device} for '{playbook_id}' must be an array")

            required_for_device = required_platforms.get(device, [])

            if not isinstance(required_for_device, list):
                raise ValueError(f"required_platforms.{device} for '{playbook_id}' must be an array")

            required_for_device_set = set(required_for_device)

            for platform in platforms:
                if platform not in ["windows", "linux"]:
                    raise ValueError(f"Unsupported platform '{platform}' for '{playbook_id}'")

                runner_label = f"localized-{locale_slug}-{device}-{platform}"

                matrix.append(
                    {
                        "locale": locale,
                        "playbook": playbook_id,
                        "platform": platform,
                        "arch": device,
                        "runner_label": runner_label,
                        "required": platform in required_for_device_set,
                        "localized_only": localized_only,
                    }
                )

    return matrix


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a human-localized playbook GitHub Actions test matrix")
    parser.add_argument(
        "--playbook",
        action="append",
        default=[],
        help=(
            "Optional playbook ID; repeat for multiple playbooks; "
            "omit to scan all"
        ),
    )
    parser.add_argument(
        "--locale",
        default="zh-CN",
        help=(
            "Locale under localized-playbooks; "
            "default: zh-CN"
        ),
    )
    args = parser.parse_args()

    try:
        selected_playbooks = set(args.playbook) or None
        matrix = build_matrix(args.locale, selected_playbooks)
    except (RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(json.dumps(matrix, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
