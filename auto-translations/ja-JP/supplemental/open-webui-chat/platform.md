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
Lemonade は[こちら](https://lemonade-server.ai/install_options.html)からあらかじめインストールしておく必要があります。

- **Open WebUI**(フロントエンド Web アプリ)
- **Lemonade Server**(バックエンドモデルサーバー)

> このプレイブックは **Lemonade**(Lemonade server/app)を**ネイティブ**で実行します。**Open WebUI** は、Linux では(Podman 経由の)**コンテナ**として、Windows では **Python パッケージ**として実行されます。`open-webui` PyPI パッケージは Python 3.12 以下のみをサポートしているため、Linux コンテナを使用することで古い Python バージョンを管理する必要がなくなります。

## モデル(Lemonade 内)

モデルは、**Lemonade アプリ**内(組み込みの Model Manager を使用)、または Lemonade のモデル管理コマンド(`lemonade pull <model_name>`)からダウンロードする必要があります。このプレイブックでは、以下の推奨モデルがダウンロード済みであり、モデル一覧のエンドポイントに表示されていることを前提としています。

モデルの利用可否を確認する:
- 開く: `http://localhost:13305/api/v1/models`
- ダウンロード済みのモデルは `"data"` の下に一覧表示されます。

### 推奨モデル

| 機能 | モデル ID | 備考 |
|---|----|-----|
| LLM(テキスト入力 → テキスト出力) | `Qwen3-4B-Hybrid`(または類似モデル) | チャット、テキスト補完、コーディング、推論に使用できる任意の Lemonade LLM モデル |
| VLM(画像 → テキスト) | `Qwen3.5-4B-GGUF`(または **Vision** カテゴリの任意のモデル) | 画像を入力の一部として受け取ることができるマルチモーダル/ビジョン対応の任意のモデル |
| 画像生成(テキスト → 画像) | `SDXL-Turbo`(または **Image** カテゴリの任意のモデル) | テキストプロンプトから画像を生成する任意の Stable Diffusion モデル |
| 音声(音声 → テキスト) | `Whisper-Large-v3`(または **Audio** カテゴリの任意のモデル) | 音声をテキストに変換する任意の ASR モデル |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## 使用ポート

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

これらのポートがすでにシステムで使用されている場合は、サーバーを起動する際に変更してください。