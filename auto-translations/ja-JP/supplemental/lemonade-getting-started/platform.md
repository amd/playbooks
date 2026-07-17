<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# プラットフォーム設定 — Lemonade Local AI

このドキュメントでは、このプレイブックが前提とする、プリインストール済みソフトウェア、モデルパス、およびプラットフォーム固有の前提条件について説明します。

## プリインストール済みソフトウェア

| ソフトウェア | バージョン | 目的 |
|----------|---------|---------|
| Lemonade Server | 最新リリース | OpenAI互換APIを備えたローカルLLMサーバー |
| Python | 3.10–3.13 | OpenAI Pythonクライアントの例に必要 |

## デフォルトのモデルストレージ

Lemonade を通じてダウンロードされたモデルは、Hugging Face Hub の仕様に従って保存されます：

| プラットフォーム | デフォルトパス |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

ストレージの場所を変更するには、`HF_HOME` 環境変数を設定してください。

## ハードウェア要件

| ハードウェアターゲット | 要件 |
|----------------|-------------|
| **CPU** | 最新のx86-64プロセッサー（AMD またはIntel） |
| **GPU (Vulkan)** | Vulkanドライバーをサポートする任意の GPU |
| **GPU (ROCm)** | AMD Radeon RX 7000/9000シリーズ または Radeon PRO W7000シリーズ；AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | AMD Ryzen AI 300シリーズプロセッサー、Windows 11 |

## ネットワーク要件

- 初回モデルダウンロード時にインターネット接続が必要（モデルによって1〜25 GB）
- モデルのダウンロード完了後はインターネット不要