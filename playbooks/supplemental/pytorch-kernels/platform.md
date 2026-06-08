<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

This document describes the expected platform configuration for running this playbook.

## Required Apps / Frameworks

| Component       | Expected Configuration               | Notes                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python with `venv` support         | Used to create and activate `kernel-env`                                     |
| ROCm Python SDK | ROCm 7.13 package family             | Installed through the playbook dependency flow                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Required for `torch.cuda`, HIP runtime, JIT compilation, and `CUDAExtension` |
| GPU Driver      | AMD GPU driver with ROCm/HIP support | Required before PyTorch can detect the AMD GPU                               |

> Note: If you're running on AMD Ryzen™ AI Halo Developer Platform, AMD ROCm™ software and PyTorch are preinstalled.

## Linux Prerequisites

The following system packages are required:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` is required to create `kernel-env`.
* `build-essential`, `gcc`, and `g++` are required for the C++ extension walkthroughs.
* `amd-smi` is used for Linux GPU visibility/utilization checks.

The C++ extension examples build native `.so` modules from `.cu` files using PyTorch’s `CUDAExtension` path.

## Windows Prerequisites

Windows runners require:

* Python available through `python`
* Install latest: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) or [newer](https://visualstudio.microsoft.com/vs/community/) with the **Desktop development with C++** workload

The Visual Studio C++ environment must provide:
* `vcvars64.bat`
* `cl.exe`
* Windows SDK include and library paths

The C++ extension examples build native `.pyd` modules from `.cu` files using PyTorch’s `CUDAExtension` path.