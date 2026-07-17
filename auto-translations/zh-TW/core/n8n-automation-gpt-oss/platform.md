<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# 平台配置

本文件說明執行此 playbook 的預期平台配置。

## 先決條件

### Windows

| 元件 | 版本 | 備註 |
|-----------|---------|-------|
| **Node.js** | 22.16+ | 已預先安裝並可在 AMD Ryzen™ AI Halo 開發者平台的 PATH 中使用；其他所有裝置須手動安裝 |
| **Lemonade Server** | 最新版 | 執行於 `http://localhost:13305/api/v1` |

### Linux

| 元件 | 版本 | 備註 |
|-----------|---------|-------|
| **Node.js** | 22.16+ | 已預先安裝並可在 AMD Ryzen™ AI Halo 開發者平台的 PATH 中使用；其他所有裝置須手動安裝 |
| **Lemonade Server** | 最新版 | 執行於 `http://localhost:13305/api/v1` |


## Lemonade LLM

Lemonade 伺服器應在載入適合裝置的模型後執行（請參閱 README 以取得適用於您裝置的 `lemonade run` 指令）：

| 裝置 | 端點 | 模型 |
|--------|----------|-------|
| AMD Ryzen™ AI Halo 開發者平台 <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |