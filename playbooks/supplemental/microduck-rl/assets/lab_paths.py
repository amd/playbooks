#!/usr/bin/env python
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""Paths shared by the MicroDuck playbook scripts."""

import os
from pathlib import Path

ASSETS = Path(__file__).resolve().parent
WORKSPACE = ASSETS / "microduck_workspace"
TASK_ROOT = WORKSPACE / "microduck_rl_unilab"
LAB_ROOT = WORKSPACE / "microduck_rl_tutorial"
LOG_ROOT = Path(os.environ.get("LAB_LOG_ROOT", ASSETS / "runs"))
DEMO = LAB_ROOT / "examples" / "velocity_flat_demo"
VENV_BIN = ASSETS / "microduck-venv" / "bin"
ENV_FILE = ASSETS / "lab-env.sh"

TASK_SHA = "20fb528fa6c4a9559155b33e5304568668c7b7e2"
LAB_SHA = "0e515b775273f96af4b45b5eed0db886880d6ccc"


def tool(name: str) -> str:
    """Return the venv copy of a console script when the lab environment exists."""
    candidate = VENV_BIN / name
    if candidate.is_file():
        return str(candidate)
    return name
