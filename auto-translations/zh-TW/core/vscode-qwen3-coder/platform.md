<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# 平台配置

本文件說明執行此 playbook 的預期平台配置。

## Windows

### LM Studio 安裝

LM Studio 應預先安裝：

| 元件 | 版本 | 位置 |
|-----------|---------|----------|
| **LM Studio（模型與雜項）** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio（程式）** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio（快取）** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### 模型下載

以下模型應已存在於 LM Studio 模型目錄（`C:\Users\...\.lmstudio\models`）中：

| 模型類型 | 量化方式 | 大小 | 位置 |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### LM Studio 安裝

詳情請參閱 lmstudio.md（位於 dependencies 資料夾內）。

### 模型下載

與 Windows 相同。