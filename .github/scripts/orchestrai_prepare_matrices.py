#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""Validate separate OrchestrAI matrices and prepare workflow outputs."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


MATRIX_JOB_LIMIT = 256


class MatrixLimitError(ValueError):
    """Raised when one GitHub Actions matrix exceeds its per-job limit."""


def prepare(
    english_matrix: list[dict[str, Any]],
    english_batches: dict[str, Any],
    localized_matrix: list[dict[str, Any]],
    localized_batches: dict[str, Any],
) -> dict[str, Any]:
    """Return independently bounded matrices and their shared batch map."""
    for name, matrix in (
        ("English", english_matrix),
        ("Localized", localized_matrix),
    ):
        if len(matrix) > MATRIX_JOB_LIMIT:
            raise MatrixLimitError(
                f"{name} matrix has {len(matrix)} entries; GitHub Actions allows "
                f"{MATRIX_JOB_LIMIT} per matrix job"
            )

    collisions = english_batches.keys() & localized_batches.keys()
    if collisions:
        joined = ", ".join(sorted(collisions))
        raise ValueError(f"English/localized batch IDs collide: {joined}")

    return {
        "english_matrix": english_matrix,
        "localized_matrix": localized_matrix,
        "batches": {**english_batches, **localized_batches},
        "batch_matrix": batch_matrix(english_matrix + localized_matrix, device_names()),
        "has_english_entries": bool(english_matrix),
        "has_localized_entries": bool(localized_matrix),
        "has_entries": bool(english_matrix or localized_matrix),
    }


CONFIG = Path(__file__).resolve().parents[1] / "orchestrai-config.yml"


def device_names() -> dict[str, str]:
    try:
        import yaml
        return (yaml.safe_load(CONFIG.read_text()) or {}).get("device_names") or {}
    except (ImportError, OSError, ValueError):
        return {}


def batch_matrix(matrix: list[dict[str, Any]], names: dict[str, str] | None = None) -> list[dict[str, Any]]:
    """One entry per batch (English or localized): the job that waits on its build
    and resolves every playbook in it. ``required`` lists the playbooks whose
    failure fails the job; ``label`` is its display name, e.g. "Halo · Windows"."""
    names = names or {}
    batches: dict[str, dict[str, Any]] = {}
    for entry in matrix:
        if "batch_id" not in entry:
            continue
        label = f"{names.get(entry['arch'], entry['arch'])} · {entry['platform'].capitalize()}"
        if entry.get("locale"):
            label += f" [{entry['locale']}]"
        batch = batches.setdefault(entry["batch_id"], {
            "batch_id": entry["batch_id"], "platform": entry["platform"],
            "arch": entry["arch"], "locale": entry.get("locale", ""), "label": label,
            "playbooks": [], "required": []})
        if entry["playbook"] not in batch["playbooks"]:
            batch["playbooks"].append(entry["playbook"])
        if entry.get("required") and entry["playbook"] not in batch["required"]:
            batch["required"].append(entry["playbook"])
    seen: dict[str, int] = {}
    for batch in batches.values():
        batch["count"] = len(batch["playbooks"])
        seen[batch["label"]] = seen.get(batch["label"], 0) + 1
    for batch in batches.values():  # two batches of one device+OS: name the extra tags
        if seen[batch["label"]] > 1 and "+" in batch["batch_id"]:
            batch["label"] += f" ({batch['batch_id'].split('+', 1)[1]})"
    return list(batches.values())


def _load_json_env(name: str, expected: type) -> Any:
    raw = os.environ.get(name, "")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{name} is not valid JSON: {exc}") from exc
    if not isinstance(value, expected):
        raise ValueError(f"{name} must contain a {expected.__name__}")
    return value


def main() -> int:
    try:
        outputs = prepare(
            _load_json_env("ENGLISH_MATRIX", list),
            _load_json_env("ENGLISH_BATCHES", dict),
            _load_json_env("LOCALIZED_MATRIX", list),
            _load_json_env("LOCALIZED_BATCHES", dict),
        )
    except (MatrixLimitError, ValueError) as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 1

    print(f"English matrix: {len(outputs['english_matrix'])} entries")
    print(f"Localized matrix: {len(outputs['localized_matrix'])} entries")
    print(f"Batches: {len(outputs['batch_matrix'])}")

    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        print("::error::GITHUB_OUTPUT is not set", file=sys.stderr)
        return 1
    with Path(output_path).open("a", encoding="utf-8") as stream:
        for key, value in outputs.items():
            if isinstance(value, bool):
                encoded = str(value).lower()
            else:
                encoded = json.dumps(value, separators=(",", ":"))
            stream.write(f"{key}={encoded}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
