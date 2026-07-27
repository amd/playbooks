<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **機械翻訳。** このページは英語から自動的に翻訳されたものであり、人による確認は行われていません。誤りが含まれている可能性があり、一部の手順、コマンド、ダウンロード、または製品の提供状況がお住まいの言語や地域と異なる場合があります。おかしな点がございましたら、英語版のプレイブックを正としてご参照ください。
<!-- auto-translated-disclaimer:end -->

# プラットフォーム構成

このドキュメントでは、このプレイブックを実行するために想定されるプラットフォーム構成について説明します。

## 必要なアプリ/フレームワーク

### Windows/Linux

GAIA は、[GAIA インストールガイド](../../dependencies/gaia.md)に記載されている手順を使用して事前にインストールしておく必要があります。

Lemonade Server は、[Lemonade インストールガイド](../../dependencies/lemonade.md)に記載されている手順を使用して事前にインストールしておく必要があります。

## 必要なモデル

### Windows/Linux

Hardware Advisor Agent は、エージェントの推論に **Qwen3-Coder-30B** を使用します。このモデルは `gaia init` の実行時に自動的にダウンロードされます。手動でモデルをダウンロードする必要はありません。