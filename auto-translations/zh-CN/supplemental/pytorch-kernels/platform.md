<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **机器翻译。**本页面由英文自动翻译，未经人工审核。其中可能包含错误，某些说明、命令、下载内容、产品可用性或其他内容可能因语言或地区而异。如内容存在任何不一致或差异，应以英文原版 playbook 为准。
<!-- auto-translated-disclaimer:end -->

# 平台配置

本文档描述了运行此 playbook 所需的平台配置。

## 所需应用程序 / 框架

| 组件       | 预期配置               | 说明                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | 支持 `venv` 的 Python         | 用于创建和激活 `kernel-env`                                     |
| ROCm Python SDK | ROCm 7.13 软件包系列             | 通过 playbook 依赖流程安装                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | `torch.cuda`、HIP 运行时、JIT 编译以及 `CUDAExtension` 均需要此项 |
| GPU 驱动程序      | 支持 ROCm/HIP 的 AMD GPU 驱动程序 | PyTorch 检测 AMD GPU 之前需要此项                                 |

> 注意：如果你正在 AMD Ryzen™ AI Halo Developer Platform 上运行，AMD ROCm™ 软件和 PyTorch 已预先安装。

## Linux 先决条件

需要以下系统软件包：

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* 创建 `kernel-env` 需要 `python3-venv`。
* C++ 扩展演示需要 `build-essential`、`gcc` 和 `g++`。
* `amd-smi` 用于 Linux GPU 可见性/利用率检查。

C++ 扩展示例使用 PyTorch 的 `CUDAExtension` 路径从 `.cu` 文件构建原生 `.so` 模块。

## Windows 先决条件

Windows 运行环境需要：

* 通过 `python` 可用的 Python
* 安装最新版：[AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) 或[更新版本](https://visualstudio.microsoft.com/vs/community/)，并安装 **使用 C++ 的桌面开发** 工作负载

Visual Studio C++ 环境必须提供：
* `vcvars64.bat`
* `cl.exe`
* Windows SDK 包含文件和库路径

C++ 扩展示例使用 PyTorch 的 `CUDAExtension` 路径从 `.cu` 文件构建原生 `.pyd` 模块。