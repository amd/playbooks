<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **机器翻译。**本页面由英文自动翻译，未经人工审核。其中可能包含错误，某些说明、命令、下载内容、产品可用性或其他内容可能因语言或地区而异。如内容存在任何不一致或差异，应以英文原版 playbook 为准。
<!-- auto-translated-disclaimer:end -->

# 平台配置

本文档描述了运行本手册所需的预期平台配置。

## Windows

### LM Studio 安装

应预先安装 LM Studio：

| 组件 | 版本 | 位置 |
|-----------|---------|----------|
| **LM Studio（模型 + Msc）** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio（程序）** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio（缓存）** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### 模型下载

以下模型应已存在于 LM Studio 模型目录中（`C:\Users\...\.lmstudio\models`）：

| 模型类型 | 量化方式 | 大小 | 位置 |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### LM Studio 安装

有关更多详细信息，请参阅 lmstudio.md（位于 dependencies 文件夹内）。

### 模型下载

与 Windows 上相同。