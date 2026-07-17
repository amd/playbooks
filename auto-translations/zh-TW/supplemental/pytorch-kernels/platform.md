<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# 平台配置

本文件說明執行此 playbook 的預期平台配置。

## 必要應用程式 / 框架

| 元件            | 預期配置                               | 備註                                                                         |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | 支援 `venv` 的 Python              | 用於建立並啟動 `kernel-env`                                                  |
| ROCm Python SDK | ROCm 7.13 套件系列                   | 透過 playbook 相依性流程安裝                                                 |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | `torch.cuda`、HIP runtime、JIT 編譯及 `CUDAExtension` 所必需                |
| GPU 驅動程式    | 支援 ROCm/HIP 的 AMD GPU 驅動程式    | PyTorch 偵測 AMD GPU 前的必要條件                                            |

> 注意：若您在 AMD Ryzen™ AI Halo 開發者平台上執行，AMD ROCm™ 軟體與 PyTorch 已預先安裝。

## Linux 先決條件

以下系統套件為必要項目：

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* `python3-venv` 為建立 `kernel-env` 所必需。
* `build-essential`、`gcc` 及 `g++` 為 C++ 擴充功能演練所必需。
* `amd-smi` 用於 Linux GPU 可見性/使用率檢查。

C++ 擴充功能範例使用 PyTorch 的 `CUDAExtension` 路徑，從 `.cu` 檔案建置原生 `.so` 模組。

## Windows 先決條件

Windows 執行環境需要：

* 可透過 `python` 存取的 Python
* 安裝最新版：[AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) 或[更新版本](https://visualstudio.microsoft.com/vs/community/)，並安裝 **使用 C++ 的桌面開發** 工作負載

Visual Studio C++ 環境必須提供：
* `vcvars64.bat`
* `cl.exe`
* Windows SDK 包含檔案與程式庫路徑

C++ 擴充功能範例使用 PyTorch 的 `CUDAExtension` 路徑，從 `.cu` 檔案建置原生 `.pyd` 模組。