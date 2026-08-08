<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機械翻訳。** このページは英語から自動的に翻訳されたものであり、人による確認は行われていません。誤りが含まれている場合や、特定の手順、コマンド、ダウンロード、製品の提供状況、その他のコンテンツが言語や地域によって異なる場合があります。内容に矛盾または相違がある場合は、playbookの原文である英語版が優先されるものとします。
<!-- auto-translated-disclaimer:end -->

# プラットフォーム構成

このドキュメントでは、このプレイブックを実行するために必要なプラットフォーム構成について説明します。

## 必須アプリ/フレームワーク

### Windows/Linux

- **Lemonade Server** は、[Lemonade インストールガイド](https://lemonade-server.ai/docs/guide/install/)に従ってインストールしてください。
- **Node.js 22.12 以降**と `npm`（`agent-canvas` CLI や `npx` で起動する MCP
  サーバーで使用されます）。
- **uv**（Agent Canvas がエージェントサーバー環境の管理に使用する Python パッケージマネージャー）。
  [uv インストールガイド](https://docs.astral.sh/uv/getting-started/installation/)からインストールしてください。

## 必須モデル

### Windows/Linux

プレイブックを開始する前に、以下のモデルが Lemonade Server で利用可能である必要があります。

| モデルタイプ | モデル ID | 備考 |
| --- | --- | --- |
| GGUF チャットモデル | `Qwen3.6-35B-A3B-GGUF` | `http://127.0.0.1:13305/api/v1` で Lemonade Server により提供されます。メモリが32 GB未満のデバイスでは、より小さい GGUF モデルを使用してください。 |

以下のコマンドでモデルを起動します:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

## 外部認証情報

このプレイブックには以下が必要です:

- 要約対象のリポジトリへの読み取りアクセス権を持つ GitHub トークン。
- `chat:write` 権限とチャンネル読み取りアクセス権を持つ Slack ボットトークン。
- Slack チーム ID と対象の Slack チャンネル ID。