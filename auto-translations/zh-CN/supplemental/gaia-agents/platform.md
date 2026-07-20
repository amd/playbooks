<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# 平台配置

本文档介绍了运行此 playbook 所需的预期平台配置。

## 所需应用程序/框架

### Windows/Linux

应按照 [GAIA 安装指南](../../dependencies/gaia.md) 中提供的说明预先安装 GAIA。

应按照 [Lemonade 安装指南](../../dependencies/lemonade.md) 中提供的说明预先安装 Lemonade Server。

## 所需模型

### Windows/Linux

Hardware Advisor Agent 使用 **Qwen3-Coder-30B** 进行代理推理。此模型会在 `gaia init` 期间自动下载。无需手动下载模型。