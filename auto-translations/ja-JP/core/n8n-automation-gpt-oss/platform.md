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

## 前提条件

### Windows

| コンポーネント | バージョン | 備考 |
|-----------|---------|-------|
| **Node.js** | 22.16+ | AMD Ryzen™ AI Halo Developer Platform には事前インストール済みで PATH 上で利用可能。それ以外のすべてのデバイスでは手動でインストールする必要があります |
| **Lemonade Server** | latest | `http://localhost:13305/api/v1` 上で実行中 |

### Linux

| コンポーネント | バージョン | 備考 |
|-----------|---------|-------|
| **Node.js** | 22.16+ | AMD Ryzen™ AI Halo Developer Platform には事前インストール済みで PATH 上で利用可能。それ以外のすべてのデバイスでは手動でインストールする必要があります |
| **Lemonade Server** | latest | `http://localhost:13305/api/v1` 上で実行中 |


## Lemonade LLM

Lemonade server は、デバイスに適したモデルをロードした状態で実行されている必要があります(お使いのデバイス向けの `lemonade run` コマンドについては README を参照してください)。

| デバイス | エンドポイント | モデル |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |