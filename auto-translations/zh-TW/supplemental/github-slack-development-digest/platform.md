<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# 平台設定

本文件說明執行此 playbook 所需的預期平台設定。

## 所需應用程式／框架

### Windows/Linux

- 應依照 [Lemonade 安裝指南](https://lemonade-server.ai/docs/guide/install/) 安裝 **Lemonade Server**。
- **Node.js 22.12 或更新版本** 及 `npm`，供 `agent-canvas` CLI 與使用 `npx` 啟動的 MCP
  伺服器使用。
- **uv**，Agent Canvas 用來管理代理伺服器環境的 Python 套件管理工具。請從
  [uv 安裝指南](https://docs.astral.sh/uv/getting-started/installation/) 進行安裝。

## 所需模型

### Windows/Linux

在啟動此 playbook 之前，下列模型必須已在 Lemonade Server 上可用。

| 模型類型 | 模型 ID | 備註 |
| --- | --- | --- |
| GGUF 聊天模型 | `Qwen3.6-35B-A3B-GGUF` | 由 Lemonade Server 於 `http://127.0.0.1:13305/api/v1` 提供服務。若裝置記憶體小於 32 GB，請使用較小的 GGUF 模型。 |

使用以下方式啟動模型：

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

## 外部憑證

此 playbook 需要：

- 具有對所摘要的儲存庫讀取權限的 GitHub token。
- 具有 `chat:write` 及頻道讀取權限的 Slack bot token。
- 一個 Slack 團隊 ID 以及目標 Slack 頻道 ID。