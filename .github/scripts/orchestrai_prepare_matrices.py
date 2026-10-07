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
        "has_english_entries": bool(english_matrix),
        "has_localized_entries": bool(localized_matrix),
        "has_entries": bool(english_matrix or localized_matrix),
    }


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
