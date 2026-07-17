<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# 平台配置

本文件說明執行此 playbook 的預期平台配置。

## 必要應用程式/框架

### Windows/Linux

GAIA 應依照 [GAIA 安裝指南](../../dependencies/gaia.md) 中提供的說明預先安裝。

Lemonade Server 應依照 [Lemonade 安裝指南](../../dependencies/lemonade.md) 中提供的說明預先安裝。

## 必要模型

### Windows/Linux

Hardware Advisor Agent 使用 **Qwen3-Coder-30B** 進行代理推理。此模型會在執行 `gaia init` 期間自動下載，無需手動下載模型。