<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機器翻譯。**本頁面是由英文自動翻譯而成，尚未經過人工審閱。內容可能包含錯誤，且某些指示、命令、下載項目、產品供應情況或其他內容可能因語言或地區而異。如本文件與英文版本之間存在任何不一致或差異，應以該 playbook 之英文原始版本為準。
<!-- auto-translated-disclaimer:end -->

# 平台配置 — Lemonade 本地 AI

本文件說明此指南所假設的預先安裝軟體、模型路徑，以及平台特定的先決條件。

## 預先安裝軟體

| 軟體 | 版本 | 用途 |
|----------|---------|---------|
| Lemonade Server | 最新版本 | 具備 OpenAI 相容 API 的本地 LLM 伺服器 |
| Python | 3.10–3.13 | OpenAI Python 用戶端範例所需 |

## 預設模型儲存位置

透過 Lemonade 下載的模型會依照 Hugging Face Hub 規範進行儲存：

| 平台 | 預設路徑 |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

若要變更儲存位置，請設定 `HF_HOME` 環境變數。

## 硬體需求

| 硬體目標 | 需求 |
|----------------|-------------|
| **CPU** | 任何現代 x86-64 處理器（AMD 或 Intel） |
| **GPU (Vulkan)** | 任何支援 Vulkan 驅動程式的 GPU |
| **GPU (ROCm)** | AMD Radeon RX 7000/9000 系列或 Radeon PRO W7000 系列；AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | AMD Ryzen AI 300 系列處理器，Windows 11 |

## 網路需求

- 初次下載模型時需要網際網路連線（依模型不同約 1–25 GB）
- 模型下載完成後即無需網際網路連線