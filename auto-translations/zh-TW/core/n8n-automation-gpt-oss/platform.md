<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機器翻譯。**本頁面是由英文自動翻譯而成，尚未經過人工審閱。內容可能包含錯誤，且某些指示、命令、下載項目、產品供應情況或其他內容可能因語言或地區而異。如本文件與英文版本之間存在任何不一致或差異，應以該 playbook 之英文原始版本為準。
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