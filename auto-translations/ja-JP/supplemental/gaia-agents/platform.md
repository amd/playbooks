<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# プラットフォーム構成

このドキュメントでは、このプレイブックを実行するために想定されるプラットフォーム構成について説明します。

## 必要なアプリ/フレームワーク

### Windows/Linux

GAIA は、[GAIA インストールガイド](../../dependencies/gaia.md)に記載されている手順を使用して事前にインストールしておく必要があります。

Lemonade Server は、[Lemonade インストールガイド](../../dependencies/lemonade.md)に記載されている手順を使用して事前にインストールしておく必要があります。

## 必要なモデル

### Windows/Linux

Hardware Advisor Agent は、エージェントの推論に **Qwen3-Coder-30B** を使用します。このモデルは `gaia init` の実行時に自動的にダウンロードされます。手動でモデルをダウンロードする必要はありません。