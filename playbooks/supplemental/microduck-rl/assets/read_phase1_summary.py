#!/usr/bin/env python
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""Print reward, episode length, and iteration count for the latest training run."""

import json

import lab_paths


def main() -> None:
    log_root = lab_paths.LOG_ROOT / "MicroduckVelocityFlat"
    runs = sorted(log_root.glob("*_mujoco"), key=lambda path: path.stat().st_mtime)
    if not runs:
        raise SystemExit("No training run found. Finish Phase 1 training first.")
    phase1_run = runs[-1]
    summary = json.loads((phase1_run / "run_summary.json").read_text(encoding="utf-8"))
    iterations = summary["completed_iterations"]
    print(f"Phase 1 run: {phase1_run.name}")
    print(
        f"  reward={summary['final_mean_reward']:.2f}  "
        f"ep_len={summary['mean_episode_length']:.1f}  "
        f"iters={iterations}"
    )
    if iterations < 100:
        print(
            "This run is much shorter than the 300-iteration Phase 1 exercise. "
            "Train Phase 1 before comparing it with the reference policy."
        )


if __name__ == "__main__":
    main()
