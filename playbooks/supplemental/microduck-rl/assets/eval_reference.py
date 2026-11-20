#!/usr/bin/env python
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""Render the bundled reference policy on 16 parallel MicroDuck environments."""

import os
import subprocess

import lab_paths


def main() -> None:
    demo = lab_paths.DEMO
    if not (demo / "model_950.pt").is_file():
        raise SystemExit(
            "Reference checkpoint is missing. Run prepare_workspace.py first."
        )
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
            str(demo),
            "training.play_steps=200",
            "training.play_env_num=16",
            "training.log_root=" + str(lab_paths.LOG_ROOT),
        ],
        cwd=lab_paths.TASK_ROOT,
        check=True,
        env=os.environ,
    )

    video = demo / "play_video.mp4"
    if not video.is_file():
        raise SystemExit(
            "Demo eval finished, but play_video.mp4 was not found. Check the logs above."
        )
    print(f"Robot playback: {video} ({video.stat().st_size / 1024:.0f} KiB)")
    print("Open that file. Each robot uses the same policy and its own velocity command.")


if __name__ == "__main__":
    main()
