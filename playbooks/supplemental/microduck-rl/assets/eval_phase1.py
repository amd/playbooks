#!/usr/bin/env python
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""Render a 10-second replay of the latest MicroDuck training run."""

import os
import subprocess

import lab_paths


def main() -> None:
    log_root = lab_paths.LOG_ROOT / "MicroduckVelocityFlat"
    subprocess.run(
        [
            lab_paths.tool("microduck-eval"),
            "--algo",
            "ppo",
            "--task",
            "microduck_velocity_flat",
            "--sim",
            "mujoco",
            "--load-run",
            "-1",
            "training.play_steps=500",
            "training.play_env_num=1",
            "training.cam_distance=0.9",
            "training.cam_tracking=true",
            "training.log_root=" + str(lab_paths.LOG_ROOT),
        ],
        cwd=lab_paths.TASK_ROOT,
        check=True,
        env=os.environ,
    )

    videos = sorted(
        log_root.glob("*_mujoco/play_video.mp4"),
        key=lambda path: path.stat().st_mtime,
    )
    if not videos:
        raise SystemExit(
            "Eval finished, but play_video.mp4 was not found. Check the logs above."
        )
    video = videos[-1]
    print(f"Robot playback: {video} ({video.stat().st_size / 1024:.0f} KiB)")
    print("Open that file to watch the 10-second close-up replay.")


if __name__ == "__main__":
    main()
