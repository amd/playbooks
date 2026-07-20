<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# 平台設定

本文件描述執行此教戰手冊所需的預期平台設定。

## Windows

### LM Studio 安裝

LM Studio 應已預先安裝：

| 元件 | 版本 | 位置 |
|-----------|---------|----------|
| **LM Studio（模型 + Msc）** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio（程式）** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio（快取）** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### 模型下載

以下模型應已存在於 LM Studio 模型目錄中（`C:\Users\...\.lmstudio\models`）：

| 裝置 | 模型類型 | 量化 | 大小（GB） | 位置 |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### LM Studio 安裝

詳情請參閱 [lmstudio.md](../../dependencies/lmstudio.md)。

### 模型下載

與 Windows 相同。