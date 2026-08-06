<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機械翻訳。** このページは英語から自動的に翻訳されたものであり、人による確認は行われていません。誤りが含まれている場合や、特定の手順、コマンド、ダウンロード、製品の提供状況、その他のコンテンツが言語や地域によって異なる場合があります。内容に矛盾または相違がある場合は、playbookの原文である英語版が優先されるものとします。
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->


## 概要

vLLM は、大規模言語モデル（LLM）向けに設計された高性能推論エンジンです。高スループットのための継続的バッチ処理による最適化されたサービングと、シームレスなアプリケーション統合のための OpenAI 互換 API を提供します。これにより、速度とリソース効率が重要となる本番環境デプロイメントにおいて vLLM は非常に有用です。

このプレイブックでは、統合 GPU 上でコンテナ化された vLLM を使用して LLM をサービングし、OpenAI Python API を通じてモデルとやり取りする方法を学びます。

## 学習内容

- AMD ROCm™ サポート付きの vLLM サーバーをセットアップして起動する方法
- OpenAI 互換 API エンドポイントを通じてモデルとやり取りする方法
- `vllm-prompt` を使用してローカルサーバーにプロンプトを送信する方法

## メモリ構成の設定

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアアップデートの確認

> **注**: VS Code がインストールされていない場合は、AMD Ryzen™ AI Developer Center からインストールできます。

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェア前提条件のインストール

vLLM は、ROCm とその依存関係が事前に組み込まれた、あらかじめビルド済みのコンテナ内で実行されます。追加のインストールは不要です。

ホスト側での vLLM インストール手順はありません。以下のコマンドで vLLM を起動します。

```bash
vllm-launch
```

このランチャーはコンテナを起動し、統合 GPU をターゲットとし、ローカルの OpenAI 互換 vLLM サーバーを公開します。あるいは、タスクバーの vLLM アイコンをクリックしても構いません。

## クイックスタート

### 1. vLLM サーバーが実行中であることを確認する

`vllm-launch` は、すべてを初期化するまでに数分かかる場合があります。起動すると、サーバーは `http://localhost:8001` で利用可能になります。サーバーはフォアグラウンドで実行されるため、起動用のターミナルは開いたままにしておき、残りの手順用に別のターミナルを開いてください。以下の例では `Qwen/Qwen3-1.7B` を使用します。ランチャーが別のモデル用に構成されている場合は、リクエスト内のそのモデル ID に置き換えてください。

### 2. プロンプトを送信する

提供されている `vllm-prompt` スクリプトを使用して、ローカルの vLLM OpenAI 互換サーバーにリクエストを送信します。

```bash
vllm-prompt "Tell me a story"
```

### 3. OpenAI Python API を使用してモデルとチャットする

vLLM は OpenAI 互換 API を公開しているため、`openai` Python パッケージを使用してやり取りできます。

まず、Python 仮想環境を作成します。

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

OpenAI パッケージをインストールします
```bash
pip install openai
```

OpenAI のサーバーではなく、ローカルの vLLM サーバーを指す `OpenAI` クライアントを作成します。`api_key` はクライアントに必須ですが、vLLM はそれを検証しないため、任意の文字列で問題ありません。

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

次に、チャット補完リクエストを送信します。これは OpenAI API と同じメッセージ形式（`"user"` や `"assistant"` などのロールを持つメッセージのリスト）を使用します。`stream=True` を設定すると、レスポンスは一度にすべて届くのではなく、段階的に届きます。

```python
response = client.chat.completions.create(
    model="Qwen/Qwen3-1.7B",
    messages=[
        {"role": "user", "content": "Tell me a short story"},
    ],
    max_tokens=2048,  # Maximum number of tokens the model will generate in its response
    stream=True,
)
```

最後に、ストリーミングされたチャンクを反復処理し、届いたテキストの断片を順に表示します。

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

含まれている [chat_with_model.py](assets/chat_with_model.py) スクリプトには、この例全体が含まれており、ダウンロードできます。


## モデルの選択と構成

デフォルトでは、`vllm-launch` はテストモデルとして `Qwen/Qwen3-1.7B` をポート `8001` でサービングします。コンテナを再ビルドしたり編集したりすることなく、モデル、ポート、vLLM のサービングパラメーターを変更できます。

### AMD がテスト済みのモデル

以下のモデルは AMD によって事前構成および検証済みです。

| モデル | 注記 |
|-------|-------|
| `Qwen/Qwen3-1.7B` | デフォルトモデル。軽量で読み込みが高速です。 |
| `openai/gpt-oss-20b` | より高品質な応答を得るための大規模モデルです。 |

### 別のモデルを起動する

`--model`（または `-m`）でモデル ID を渡します。

```bash
vllm-launch --model openai/gpt-oss-20b
```

### ポートを変更する

`--port`（または `-p`）で 1024 より大きいポートを渡します。デフォルトは `8001` です。

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

ポートを変更した場合は、クライアントの `base_url` を同じポートに向けてください（例: `http://localhost:8080/v1`）。

### 追加の vLLM パラメーターを渡す

追加の引数はすべてそのまま vLLM に転送されるため、コンテキスト長やデータ型などのサービング動作を調整できます。これらを指定する方法は 2 通りあります。

**インライン**で、ランチャーのオプションの後に指定します。

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**永続的**には、`~/.local/share/vLLM/vllm-launch.conf` にある設定ファイルに指定します。このファイルはデフォルトでは存在しないため、作成して引数を Bash 配列として追加してください。

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

デフォルトの引数を置き換えるのではなく追加するには、`+=` を使用します。

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

いつでもすべてのランチャーオプションを確認するには、以下を実行します。

```bash
vllm-launch --help
```

### モデルの保存場所

`vllm-launch` は、以下の 2 つの場所からモデルを探します。

| 場所 | パス |
|----------|------|
| システムモデル | `/var/cache/models` |
| ユーザーモデル | `~/.local/share/vLLM/models` |

ダウンロードしたモデルをいずれかのディレクトリに配置し、そのパスまたは ID を `--model` に渡すことで起動できます。

```bash
vllm-launch --model /var/cache/models/my-model
```

> **注**: この方法で独自にダウンロードしたモデルを実行することは、モデルを上記いずれかのディレクトリに配置すれば動作することが期待されますが、このワークフローはまだ AMD によって正式に検証されていません。

## トラブルシューティング

### 接続が拒否される

サーバーが実行中であることを確認してください。
```bash
curl http://localhost:8001/health
```

## まとめ

このプレイブックでは、以下の方法を学びました。

- 統合 GPU 上で ROCm サポート付きのコンテナ化された vLLM を起動する
- ポート 8001 で OpenAI 互換 API エンドポイントを持つ vLLM サーバーを起動する
- `vllm-prompt` でプロンプトを送信する
- ストリーミングリクエストと非ストリーミングリクエストの両方を使用して vLLM サーバーに API 呼び出しを行う
- サーバー起動、メモリ、クライアント接続に関する一般的な問題をトラブルシューティングする

これで、統合 GPU 上で最適化されたパフォーマンスで大規模言語モデルをサービングするためのコンテナ化された vLLM デプロイメントが完成しました。

## 次のステップ

- **さまざまなモデルを試す** — `vllm-launch --model <model>` を使用してさまざまな LLM を試し、パフォーマンスを比較してください（[モデルの選択と構成](#choosing-and-configuring-a-model) を参照）。
- **アプリケーションを構築する** — OpenAI 互換 API を使用して、vLLM を Python アプリ、チャットボット、または自動化ワークフローに統合してください。
- **ファインチューニングしてサービングする** — LoRA または QLoRA を使用してモデルをファインチューニングし、最適化された推論のために vLLM でデプロイしてください。
## 追加リソース

- **[vLLM公式ドキュメント](https://docs.vllm.ai/)** — 包括的なガイドおよびAPIリファレンス
- **[vLLM GitHubリポジトリ](https://github.com/vllm-project/vllm)** — ソースコード、Issue、およびコミュニティディスカッション