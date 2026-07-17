<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# プラットフォーム設定

このドキュメントでは、このプレイブックを実行するために必要なプラットフォーム設定について説明します。

## 必要なアプリ/フレームワーク

### Windows/Linux

GAIA は [GAIA インストールガイド](../../dependencies/gaia.md) に記載されている手順に従って、事前にインストールしておく必要があります。

Lemonade Server は [Lemonade インストールガイド](../../dependencies/lemonade.md) に記載されている手順に従って、事前にインストールしておく必要があります。

## 必要なモデル

### Windows/Linux

Hardware Advisor Agent はエージェントの推論に **Qwen3-Coder-30B** を使用します。このモデルは `gaia init` の実行中に自動的にダウンロードされます。手動でモデルをダウンロードする必要はありません。