<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **机器翻译。**本页面由英文自动翻译，未经人工审核。其中可能包含错误，某些说明、命令、下载内容、产品可用性或其他内容可能因语言或地区而异。如内容存在任何不一致或差异，应以英文原版 playbook 为准。
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