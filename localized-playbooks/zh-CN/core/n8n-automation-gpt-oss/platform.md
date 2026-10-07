<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# 平台配置

本文档描述运行此 playbook 所需的平台配置。

## 前提条件

### Windows

| 组件 | 版本 | 说明 |
|-----------|---------|-------|
| **Node.js** | 22.16+ | 在 AMD Ryzen™ AI Halo Developer Platform 上已预安装并可在 PATH 中使用；其他设备需要手动安装 |
| **Lemonade Server** | latest | 运行于 `http://localhost:13305/api/v1` |

### Linux

| 组件 | 版本 | 说明 |
|-----------|---------|-------|
| **Node.js** | 22.16+ | 在 AMD Ryzen™ AI Halo Developer Platform 上已预安装并可在 PATH 中使用；其他设备需要手动安装 |
| **Lemonade Server** | latest | 运行于 `http://localhost:13305/api/v1` |


## Lemonade LLM

Lemonade server 应保持运行，并加载适合当前设备的模型。适用于各设备的 `lemonade run` 命令请参阅 README：

| 设备 | 端点 | 模型 |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `Qwen3.5-35B-A3B-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `Qwen3.5-9B-GGUF` |
