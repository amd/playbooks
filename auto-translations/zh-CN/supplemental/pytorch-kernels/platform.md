<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# 平台配置

本文档描述了运行此 playbook 所需的预期平台配置。

## 所需应用程序 / 框架

| 组件            | 预期配置                               | 说明                                                                         |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | 支持 `venv` 的 Python              | 用于创建和激活 `kernel-env`                                                  |
| ROCm Python SDK | ROCm 7.13 软件包系列                  | 通过 playbook 依赖流程安装                                                   |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | `torch.cuda`、HIP 运行时、JIT 编译和 `CUDAExtension` 所必需                 |
| GPU 驱动        | 支持 ROCm/HIP 的 AMD GPU 驱动        | PyTorch 检测 AMD GPU 之前必须安装                                            |

> 注意：如果您在 AMD Ryzen™ AI Halo 开发者平台上运行，AMD ROCm™ 软件和 PyTorch 已预先安装。

## Linux 前提条件

以下系统软件包为必需项：

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` 用于创建 `kernel-env`。
* `build-essential`、`gcc` 和 `g++` 用于 C++ 扩展演练。
* `amd-smi` 用于 Linux GPU 可见性/利用率检查。

C++ 扩展示例使用 PyTorch 的 `CUDAExtension` 路径，从 `.cu` 文件构建原生 `.so` 模块。

## Windows 前提条件

Windows 运行环境需要：

* 可通过 `python` 访问的 Python
* 安装最新版本：[AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) 或[更新版本](https://visualstudio.microsoft.com/vs/community/)，并安装 **使用 C++ 的桌面开发** 工作负载

Visual Studio C++ 环境必须提供：
* `vcvars64.bat`
* `cl.exe`
* Windows SDK 头文件和库路径

C++ 扩展示例使用 PyTorch 的 `CUDAExtension` 路径，从 `.cu` 文件构建原生 `.pyd` 模块。