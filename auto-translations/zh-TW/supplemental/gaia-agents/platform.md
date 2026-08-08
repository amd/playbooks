<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機器翻譯。**本頁面是由英文自動翻譯而成，尚未經過人工審閱。內容可能包含錯誤，且某些指示、命令、下載項目、產品供應情況或其他內容可能因語言或地區而異。如本文件與英文版本之間存在任何不一致或差異，應以該 playbook 之英文原始版本為準。
<!-- auto-translated-disclaimer:end -->

# 平台設定

本文件說明執行此手冊所需的預期平台設定。

## 必要的應用程式／框架

### Windows/Linux

應依照 [GAIA 安裝指南](../../dependencies/gaia.md) 中提供的說明，預先安裝 GAIA。

應依照 [Lemonade 安裝指南](../../dependencies/lemonade.md) 中提供的說明，預先安裝 Lemonade Server。

## 必要的模型

### Windows/Linux

Hardware Advisor Agent 使用 **Qwen3-Coder-30B** 進行代理推理。此模型會在執行 `gaia init` 期間自動下載，無需手動下載模型。