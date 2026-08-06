<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機器翻譯。**本頁面是由英文自動翻譯而成，尚未經過人工審閱。內容可能包含錯誤，且某些指示、命令、下載項目、產品供應情況或其他內容可能因語言或地區而異。如本文件與英文版本之間存在任何不一致或差異，應以該 playbook 之英文原始版本為準。
<!-- auto-translated-disclaimer:end -->

# 平台配置

本文件說明執行此 playbook 所預期的平台配置。

## 必要的應用程式／框架

| 元件       | 預期配置               | 備註                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | 支援 `venv` 的 Python         | 用於建立並啟用 `kernel-env`                                     |
| ROCm Python SDK | ROCm 7.13 套件家族             | 透過 playbook 相依性流程安裝                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | `torch.cuda`、HIP 執行環境、JIT 編譯與 `CUDAExtension` 所需 |
| GPU 驅動程式      | 支援 ROCm/HIP 的 AMD GPU 驅動程式 | PyTorch 偵測 AMD GPU 前的必要條件                               |

> 注意：如果您在 AMD Ryzen™ AI Halo Developer Platform 上執行，AMD ROCm™ 軟體與 PyTorch 皆已預先安裝。

## Linux 先決條件

需要以下系統套件：

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* 建立 `kernel-env` 需要 `python3-venv`。
* C++ 擴充功能演練需要 `build-essential`、`gcc` 與 `g++`。
* `amd-smi` 用於 Linux GPU 可見性／使用率檢查。

C++ 擴充功能範例使用 PyTorch 的 `CUDAExtension` 路徑，從 `.cu` 檔案建置原生 `.so` 模組。

## Windows 先決條件

Windows 執行環境需要：

* 透過 `python` 可使用的 Python
* 安裝最新版：[AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) 或[更新版本](https://visualstudio.microsoft.com/vs/community/)，並搭配 **Desktop development with C++** 工作負載

Visual Studio C++ 環境必須提供：
* `vcvars64.bat`
* `cl.exe`
* Windows SDK 標頭檔與函式庫路徑

C++ 擴充功能範例使用 PyTorch 的 `CUDAExtension` 路徑，從 `.cu` 檔案建置原生 `.pyd` 模組。