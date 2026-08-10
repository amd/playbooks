<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機器翻譯。**本頁面是由英文自動翻譯而成，尚未經過人工審閱。內容可能包含錯誤，且某些指示、命令、下載項目、產品供應情況或其他內容可能因語言或地區而異。如本文件與英文版本之間存在任何不一致或差異，應以該 playbook 之英文原始版本為準。
<!-- auto-translated-disclaimer:end -->

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