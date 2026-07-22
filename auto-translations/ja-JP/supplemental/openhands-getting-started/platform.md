<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

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
