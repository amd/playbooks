<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機械翻訳。** このページは英語から自動的に翻訳されたものであり、人による確認は行われていません。誤りが含まれている場合や、特定の手順、コマンド、ダウンロード、製品の提供状況、その他のコンテンツが言語や地域によって異なる場合があります。内容に矛盾または相違がある場合は、playbookの原文である英語版が優先されるものとします。
<!-- auto-translated-disclaimer:end -->

# プラットフォーム構成 — Lemonade Local AI

このドキュメントでは、このプレイブックが前提とする事前インストール済みソフトウェア、モデルパス、およびプラットフォーム固有の前提条件について説明します。

## 事前インストール済みソフトウェア

| ソフトウェア | バージョン | 用途 |
|----------|---------|---------|
| Lemonade Server | 最新リリース | OpenAI互換APIを備えたローカルLLMサーバー |
| Python | 3.10–3.13 | OpenAI Pythonクライアントのサンプルに必要 |

## デフォルトのモデル保存場所

Lemonadeを通じてダウンロードされたモデルは、Hugging Face Hubの仕様を使用して保存されます。

| プラットフォーム | デフォルトパス |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

保存場所を変更するには、`HF_HOME` 環境変数を設定してください。

## ハードウェア要件

| ハードウェアターゲット | 要件 |
|----------------|-------------|
| **CPU** | 最新のx86-64プロセッサ（AMDまたはIntel） |
| **GPU (Vulkan)** | Vulkanドライバーをサポートする任意のGPU |
| **GPU (ROCm)** | AMD Radeon RX 7000/9000シリーズまたはRadeon PRO W7000シリーズ；AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | AMD Ryzen AI 300シリーズプロセッサ、Windows 11 |

## ネットワーク要件

- 初回のモデルダウンロードにはインターネット接続が必要です（モデルによって1〜25GB）
- モデルのダウンロード後はインターネット接続は不要です