<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# 平台配置

本文档描述了运行此 playbook 的预期平台配置。

## 前提条件

### Windows

| 组件 | 版本 | 说明 |
|-----------|---------|-------|
| **Node.js** | 22.16+ | 在 AMD Ryzen™ AI Halo 开发者平台上已预装并可在 PATH 中使用；其他所有设备需手动安装 |
| **Lemonade Server** | 最新版 | 运行于 `http://localhost:13305/api/v1` |

### Linux

| 组件 | 版本 | 说明 |
|-----------|---------|-------|
| **Node.js** | 22.16+ | 在 AMD Ryzen™ AI Halo 开发者平台上已预装并可在 PATH 中使用；其他所有设备需手动安装 |
| **Lemonade Server** | 最新版 | 运行于 `http://localhost:13305/api/v1` |


## Lemonade LLM

Lemonade 服务器应在加载了适合当前设备的模型后运行（请参阅 README 中针对您设备的 `lemonade run` 命令）：

| 设备 | 端点 | 模型 |
|--------|----------|-------|
| AMD Ryzen™ AI Halo 开发者平台 <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 系列显卡 <br> AMD Radeon™ 9000 系列显卡 | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |