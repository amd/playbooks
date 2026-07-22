<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **机器翻译。**本页面由英文自动翻译而成,尚未经过人工审核。其中可能存在错误,部分步骤、命令、下载内容或产品的可用性在您所在的语言或地区可能有所不同。如发现任何问题,请以英文原版 playbook 为准。
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