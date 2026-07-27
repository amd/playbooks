<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **機器翻譯。**本頁面為英文自動翻譯版本,尚未經過人工審閱。內容可能存在錯誤,部分步驟、指令、下載項目或產品供應情況可能因您的語言或地區而有所不同。如發現任何內容有誤,請以英文原版 playbook 為準。
<!-- auto-translated-disclaimer:end -->

# 平台配置

本文件說明執行此 playbook 所需的預期平台配置。

## 先決條件

### Windows

| 元件 | 版本 | 備註 |
|-----------|---------|-------|
| **Node.js** | 22.16+ | 已預先安裝並可在 AMD Ryzen™ AI Halo Developer Platform 的 PATH 中使用；在其他所有裝置上皆須手動安裝 |
| **Lemonade Server** | latest | 執行於 `http://localhost:13305/api/v1` |

### Linux

| 元件 | 版本 | 備註 |
|-----------|---------|-------|
| **Node.js** | 22.16+ | 已預先安裝並可在 AMD Ryzen™ AI Halo Developer Platform 的 PATH 中使用；在其他所有裝置上皆須手動安裝 |
| **Lemonade Server** | latest | 執行於 `http://localhost:13305/api/v1` |


## Lemonade LLM

Lemonade server 應已在執行中，並載入適合該裝置的模型（請參閱 README 中適用於您裝置的 `lemonade run` 指令）：

| 裝置 | 端點 | 模型 |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |