<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機械翻訳。** このページは英語から自動的に翻訳されたものであり、人による確認は行われていません。誤りが含まれている場合や、特定の手順、コマンド、ダウンロード、製品の提供状況、その他のコンテンツが言語や地域によって異なる場合があります。内容に矛盾または相違がある場合は、playbookの原文である英語版が優先されるものとします。
<!-- auto-translated-disclaimer:end -->

# プラットフォーム構成

このドキュメントでは、このプレイブックを実行するために想定されるプラットフォーム構成について説明します。

## 必要なアプリ/フレームワーク

### Windows/Linux

- **Lemonade Server** は [Lemonade installation guide](https://lemonade-server.ai/docs/guide/install/) に従ってインストールしてください。
- **Node.js 22.12 以降** および `npm`（`agent-canvas` CLI で使用）。
- **uv**、Agent Canvas がエージェントサーバー環境の管理に使用する Python パッケージマネージャーです。[uv installation guide](https://docs.astral.sh/uv/getting-started/installation/) からインストールしてください。

## 必要なモデル

### Windows/Linux

プレイブックを開始する前に、次のモデルが Lemonade Server で利用可能である必要があります。

| モデルタイプ | モデル ID | 備考 |
| --- | --- | --- |
| GGUF チャットモデル | `Qwen3.6-35B-A3B-GGUF` | Lemonade Server が `http://127.0.0.1:13305/api/v1` で提供します。メモリが 32 GB 未満のデバイスでは、より小さい GGUF モデルを使用してください。 |

次のコマンドでモデルを起動します。

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```
