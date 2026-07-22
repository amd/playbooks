<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **机器翻译。**本页面由英文自动翻译而成,尚未经过人工审核。其中可能存在错误,部分步骤、命令、下载内容或产品的可用性在您所在的语言或地区可能有所不同。如发现任何问题,请以英文原版 playbook 为准。
<!-- auto-translated-disclaimer:end -->

# 平台配置

本文档描述运行此 playbook 所需的预期平台配置。

## Windows

### LM Studio 安装

应预先安装 LM Studio：

| 组件 | 版本 | 位置 |
|-----------|---------|----------|
| **LM Studio (Models + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### 模型下载

以下模型应已存在于 LM Studio 模型目录（`C:\Users\...\.lmstudio\models`）中：

| 设备 | 模型类型 | 量化 | 大小 (GB) | 位置 |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### LM Studio 安装

更多详情请参阅 [lmstudio.md](../../dependencies/lmstudio.md)。

### 模型下载

与 Windows 相同。