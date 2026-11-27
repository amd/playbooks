#!/usr/bin/env python
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""Print the active ROCm PyTorch environment and fail if no AMD GPU is visible."""

import os
import platform
import sys


def os_name() -> str:
    values = {}
    try:
        with open("/etc/os-release", encoding="utf-8") as release:
            for line in release:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    values[key] = value.strip('"')
    except OSError:
        return platform.platform()
    return values.get("PRETTY_NAME", platform.platform())


def main() -> None:
    try:
        import torch
    except ImportError as exc:
        raise SystemExit(
            "PyTorch is not installed in this interpreter. Start the ROCm PyTorch "
            "container in the playbook, then run this script inside it."
        ) from exc

    gpu_count = torch.cuda.device_count()  # ROCm PyTorch uses the torch.cuda API.
    rows = [
        ("Operating system", os_name()),
        ("Python", sys.version.split()[0]),
        ("Interpreter", sys.executable),
        ("PyTorch", torch.__version__),
        ("PyTorch location", os.path.dirname(torch.__file__)),
        ("ROCm / HIP", torch.version.hip or "unavailable"),
        ("Visible AMD GPUs", str(gpu_count)),
    ]
    rows += [
        (f"GPU {index}", torch.cuda.get_device_name(index))
        for index in range(gpu_count)
    ]

    print("| Component | Active environment |")
    print("|---|---|")
    for name, value in rows:
        print(f"| {name} | {value} |")

    if not torch.version.hip or gpu_count < 1:
        raise SystemExit(
            "This playbook needs HIP-enabled PyTorch and a visible AMD GPU."
        )


if __name__ == "__main__":
    main()
