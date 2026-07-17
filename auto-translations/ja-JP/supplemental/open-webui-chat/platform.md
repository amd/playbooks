<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# プラットフォーム設定

このドキュメントでは、このプレイブックを実行するために必要なプラットフォーム設定について説明します。

## 必要なアプリ/フレームワーク

### Windows/Linux
Lemonade は[こちら](https://lemonade-server.ai/install_options.html)から事前にインストールしておく必要があります。

- **Open WebUI**（フロントエンド Web アプリ）
- **Lemonade Server**（バックエンドモデルサーバー）

> このプレイブックは **Lemonade**（Lemonade サーバー/アプリ）を**ネイティブ**で実行します。**Open WebUI** は Linux では（Podman 経由で）**コンテナ**として、Windows では **Python パッケージ**として実行されます。`open-webui` PyPI パッケージは Python ≤ 3.12 のみをサポートしているため、Linux コンテナを使用することで古い Python バージョンの管理が不要になります。

## モデル（Lemonade 内）

モデルは **Lemonade アプリ**内（組み込みのモデルマネージャーを使用）または Lemonade のモデル管理コマンド（`lemonade pull <model_name>`）を使ってダウンロードする必要があります。このプレイブックでは、以下の推奨モデルがダウンロード済みであり、モデル一覧エンドポイントに表示されていることを前提としています。

モデルの利用可否を確認する:
- 開く: `http://localhost:13305/api/v1/models`
- ダウンロード済みのモデルは `"data"` の下に一覧表示されます。

### 推奨モデル

| 機能 | モデル ID | 備考 |
|---|----|-----|
| LLM（テキスト入力 → テキスト出力） | `Qwen3-4B-Hybrid`（または同等のもの） | チャット、テキスト補完、コーディング、推論に対応した任意の Lemonade LLM モデル |
| VLM（画像 → テキスト） | `Qwen3.5-4B-GGUF`（または **Vision** カテゴリの任意のモデル） | 入力の一部として画像を受け取ることができる任意のマルチモーダル/ビジョン対応モデル |
| 画像生成（テキスト → 画像） | `SDXL-Turbo`（または **Image** カテゴリの任意のモデル） | テキストプロンプトから画像を生成する任意の Stable Diffusion モデル |
| 音声（音声 → テキスト） | `Whisper-Large-v3`（または **Audio** カテゴリの任意のモデル） | 音声をテキストに変換する任意の ASR モデル |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## 使用ポート

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

これらのポートがすでにシステムで使用されている場合は、サーバーの起動時に変更してください。