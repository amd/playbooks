<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **机器翻译。**本页面由英文自动翻译，未经人工审核。其中可能包含错误，某些说明、命令、下载内容、产品可用性或其他内容可能因语言或地区而异。如内容存在任何不一致或差异，应以英文原版 playbook 为准。
<!-- auto-translated-disclaimer:end -->

# 平台配置

本文档描述了运行此 playbook 所需的预期平台配置。

## 前提条件

### Windows

| 组件 | 版本 | 说明 |
|-----------|---------|-------|
| **Node.js** | 22.16+ | 在 AMD Ryzen™ AI Halo Developer Platform 上已预安装并可在 PATH 中使用；在所有其他设备上必须手动安装 |
| **Lemonade Server** | latest | 运行于 `http://localhost:13305/api/v1` |

### Linux

| 组件 | 版本 | 说明 |
|-----------|---------|-------|
| **Node.js** | 22.16+ | 在 AMD Ryzen™ AI Halo Developer Platform 上已预安装并可在 PATH 中使用；在所有其他设备上必须手动安装 |
| **Lemonade Server** | latest | 运行于 `http://localhost:13305/api/v1` |


## Lemonade LLM

Lemonade server 应处于运行状态，并加载适合设备的模型（有关适用于您设备的 `lemonade run` 命令，请参阅 README）：

| 设备 | 端点 | 模型 |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |