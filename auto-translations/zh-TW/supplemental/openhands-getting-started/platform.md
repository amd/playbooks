<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機器翻譯。**本頁面是由英文自動翻譯而成，尚未經過人工審閱。內容可能包含錯誤，且某些指示、命令、下載項目、產品供應情況或其他內容可能因語言或地區而異。如本文件與英文版本之間存在任何不一致或差異，應以該 playbook 之英文原始版本為準。
<!-- auto-translated-disclaimer:end -->

# 平台配置

本文件說明執行此 playbook 時所預期的平台配置。

## 必要的應用程式/框架

### Windows/Linux

- **Lemonade Server** 應依照
  [Lemonade 安裝指南](https://lemonade-server.ai/docs/guide/install/)進行安裝。
- **Node.js 22.12 或更新版本**以及 `npm`，供 `agent-canvas` CLI 使用。
- **uv**，Agent Canvas 用來管理 agent 伺服器環境的 Python 套件管理工具。請從
  [uv 安裝指南](https://docs.astral.sh/uv/getting-started/installation/)進行安裝。

## 必要的模型

### Windows/Linux

在啟動此 playbook 之前，以下模型必須在 Lemonade Server 中可用。

| 模型類型 | 模型 ID | 備註 |
| --- | --- | --- |
| GGUF 聊天模型 | `Qwen3.6-35B-A3B-GGUF` | 由 Lemonade Server 於 `http://127.0.0.1:13305/api/v1` 提供服務。若裝置記憶體少於 32 GB，請使用較小的 GGUF 模型。 |

使用以下指令啟動模型：

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```
