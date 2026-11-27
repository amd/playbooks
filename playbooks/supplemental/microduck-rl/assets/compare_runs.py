#!/usr/bin/env python
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""Compare the latest Phase 1 run with the reference checkpoint and save curves."""

import json
import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

import lab_paths


def plot_scalars(run_dir: Path, tags: list[str]) -> dict[str, tuple[list[int], list[float]]]:
    events = list(run_dir.glob("events.out.tfevents.*"))
    if not events:
        return {}
    accumulator = EventAccumulator(str(events[0]))
    accumulator.Reload()
    available = set(accumulator.Tags().get("scalars", []))
    curves = {}
    for tag in tags:
        if tag not in available:
            continue
        scalars = accumulator.Scalars(tag)
        curves[tag] = ([point.step for point in scalars], [point.value for point in scalars])
    return curves


def main() -> None:
    log_root = lab_paths.LOG_ROOT / "MicroduckVelocityFlat"
    runs = sorted(log_root.glob("*_mujoco"), key=lambda path: path.stat().st_mtime)
    if not runs:
        raise SystemExit("No Phase 1 run found. Finish Phase 1 training first.")
    phase1 = runs[-1]
    student = json.loads((phase1 / "run_summary.json").read_text(encoding="utf-8"))
    reference = json.loads((lab_paths.DEMO / "run_summary.json").read_text(encoding="utf-8"))

    print("=== Phase 1: this training run ===")
    for name, value in (
        ("num_envs", student["global_num_envs"]),
        ("iterations", student["completed_iterations"]),
        ("total_env_steps", student["total_env_steps"]),
        ("final_reward", f"{student['final_mean_reward']:.1f}"),
        ("episode_length", f"{student['mean_episode_length']:.0f}"),
        ("train_wall_sec", f"{student['training_wall_time_sec']:.0f}"),
    ):
        print(f"{name:24} {value}")

    print("\n=== Phase 2: reference demo fixed-command gate ===")
    for name, value in (
        ("checkpoint", reference["checkpoint"]),
        ("training_iterations", reference["completed_iterations"]),
        ("selection_mean_score", f"{reference['selection_eval_mean_score']:.1f}"),
        ("worst_direction_score", f"{reference['selection_eval_worst_direction_score']:.1f}"),
        ("yaw_rate", reference["selection_eval_yaw_rate"]),
    ):
        print(f"{name:24} {value}")
    print(
        "\nPPO reward and the six-direction gate score are different metrics. "
        "Do not compare them by raw magnitude."
    )

    tags = ["Train/mean_reward", "Train/mean_episode_length"]
    curves = plot_scalars(phase1, tags)
    if not curves:
        print("No TensorBoard scalars found. The numeric summary above is still valid.")
        return

    figure, axes = plt.subplots(1, 2, figsize=(11, 4))
    for axis, tag in zip(axes, tags):
        if tag in curves:
            steps, values = curves[tag]
            axis.plot(steps, values)
        axis.set_title(tag)
        axis.set_xlabel("iteration")
    figure.suptitle(f"Phase 1 training curves · {phase1.name}")
    figure.tight_layout()
    destination = lab_paths.LOG_ROOT / "phase1_curves.png"
    figure.savefig(destination)
    print(f"Saved training curves to {destination}")


if __name__ == "__main__":
    main()
