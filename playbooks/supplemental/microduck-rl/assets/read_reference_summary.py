#!/usr/bin/env python
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""Print the six-direction selection summary for the reference checkpoint."""

import json

import lab_paths


KEYS = (
    "checkpoint",
    "completed_iterations",
    "num_envs",
    "selection_eval_yaw_rate",
    "selection_eval_mean_score",
    "selection_eval_worst_direction_score",
    "selection_reason",
)


def main() -> None:
    summary_path = lab_paths.DEMO / "run_summary.json"
    if not summary_path.is_file():
        raise SystemExit(
            "Reference summary is missing. Run prepare_workspace.py first."
        )
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    print("=== Phase 2 reference demo run_summary ===")
    print(json.dumps({key: summary[key] for key in KEYS}, indent=2, ensure_ascii=False))
    print(
        "This score is a six-direction selection score out of 100, "
        "not the PPO reward from Phase 1."
    )


if __name__ == "__main__":
    main()
