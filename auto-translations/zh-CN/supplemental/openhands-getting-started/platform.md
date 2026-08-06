<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **机器翻译。**本页面由英文自动翻译，未经人工审核。其中可能包含错误，某些说明、命令、下载内容、产品可用性或其他内容可能因语言或地区而异。如内容存在任何不一致或差异，应以英文原版 playbook 为准。
<!-- auto-translated-disclaimer:end -->

# 平台配置

本文档介绍了运行此 playbook 所需的预期平台配置。

## 必需的应用程序/框架

### Windows/Linux

- **Lemonade Server** 应按照
  [Lemonade 安装指南](https://lemonade-server.ai/docs/guide/install/) 进行安装。
- **Node.js 22.12 或更高版本**以及 `npm`，供 `agent-canvas` CLI 使用。
- **uv**，Agent Canvas 用于管理代理服务器环境的 Python 包管理器。请从
  [uv 安装指南](https://docs.astral.sh/uv/getting-started/installation/) 进行安装。

## 必需的模型

### Windows/Linux

在启动 playbook 之前，以下模型必须已在 Lemonade Server 中可用。

| 模型类型 | 模型 ID | 备注 |
| --- | --- | --- |
| GGUF 聊天模型 | `Qwen3.6-35B-A3B-GGUF` | 由 Lemonade Server 在 `http://127.0.0.1:13305/api/v1` 上提供服务。在内存小于 32 GB 的设备上，请使用较小的 GGUF 模型。 |

使用以下命令启动模型：

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```
