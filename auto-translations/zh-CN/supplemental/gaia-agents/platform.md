<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **机器翻译。**本页面由英文自动翻译而成,尚未经过人工审核。其中可能存在错误,部分步骤、命令、下载内容或产品的可用性在您所在的语言或地区可能有所不同。如发现任何问题,请以英文原版 playbook 为准。
<!-- auto-translated-disclaimer:end -->

# 平台配置

本文档介绍了运行此 playbook 所需的预期平台配置。

## 所需应用程序/框架

### Windows/Linux

应按照 [GAIA 安装指南](../../dependencies/gaia.md) 中提供的说明预先安装 GAIA。

应按照 [Lemonade 安装指南](../../dependencies/lemonade.md) 中提供的说明预先安装 Lemonade Server。

## 所需模型

### Windows/Linux

Hardware Advisor Agent 使用 **Qwen3-Coder-30B** 进行代理推理。此模型会在 `gaia init` 期间自动下载。无需手动下载模型。