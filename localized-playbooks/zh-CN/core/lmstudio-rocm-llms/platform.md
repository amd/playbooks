<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# 平台配置

本文档描述运行此 playbook 所需的平台配置。

## Windows

### LM Studio 安装

LM Studio 应已预安装：

| 组件 | 版本 | 位置 |
|-----------|---------|----------|
| **LM Studio (Models + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### 模型下载

以下模型应已存在于 LM Studio 模型目录（`C:\Users\...\.lmstudio\models`）中：

| 设备 | 模型类型 | 量化 | 大小 (GB) | 位置 |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | Qwen3.5-35B-A3B | `Q4_K_M` | 22.07 | `models\lmstudio-community` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### LM Studio 安装

更多详情请参阅 [lmstudio.md](../../dependencies/lmstudio.md)。

### 模型下载

与 Windows 相同。
