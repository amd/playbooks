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

vLLMは、大規模言語モデル(LLM)向けに設計された高性能な推論エンジンです。高スループットのための継続的バッチ処理による最適化されたサービングと、シームレスなアプリケーション統合のためのOpenAI互換APIを提供します。これにより、vLLMは速度とリソース効率が重要となる本番環境でのデプロイに最適です。

本プレイブックでは、統合GPU上でコンテナ化されたvLLMを使用してLLMをサービングし、OpenAI Python APIを通じてモデルと対話する方法を学びます。

## 学習内容

- AMD ROCm™対応のvLLMサーバーをセットアップして起動する方法
- OpenAI互換APIエンドポイントを介してモデルと対話する方法
- `vllm-prompt`を使用してローカルサーバーにプロンプトを送信する方法

## メモリ設定

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアアップデートの確認

> **注**: VS Codeがインストールされていない場合、AMD Ryzen™ AI Developer Centerからインストールできます。

<!-- @require:software-update -->
<!-- @device:end -->

## 必須ソフトウェアのインストール

vLLMは、ROCmとその依存関係があらかじめ整合された事前構築済みコンテナ内で実行されます。追加のインストールは不要です。

ホスト側でのvLLMインストール手順はありません。以下でvLLMを起動してください。

```bash
vllm-launch
```

ランチャーはコンテナを起動し、統合GPUをターゲットとして、ローカルのOpenAI互換vLLMサーバーを公開します。あるいは、タスクバーのvLLMアイコンをクリックしてください。

## クイックスタート

### 1. vLLMサーバーが動作していることを確認する

`vllm-launch`は、すべての初期化が完了するまで数分かかる場合があります。起動すると、サーバーは`http://localhost:8001`で利用可能になります。サーバーはフォアグラウンドで動作するため、起動用のターミナルは開いたままにし、残りの手順には別のターミナルを開いてください。以下の例では`Qwen/Qwen3-1.7B`を使用しています。ランチャーが別のモデル用に設定されている場合は、そのモデルIDをリクエスト内で置き換えてください。

### 2. プロンプトを送信する

提供された`vllm-prompt`スクリプトを使用して、ローカルのvLLM OpenAI互換サーバーにリクエストを送信します。

```bash
vllm-prompt "Tell me a story"
```

### 3. OpenAI Python APIを使用してモデルとチャットする

vLLMはOpenAI互換APIを公開しているため、`openai` Pythonパッケージを使用して対話できます。

まず、Python仮想環境を作成します。

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->
<!-- @os:end -->

OpenAIパッケージをインストールします
```bash
pip install openai
```

OpenAIのサーバーではなく、ローカルのvLLMサーバーを指す`OpenAI`クライアントを作成します。`api_key`はクライアントに必要ですが、vLLMはそれを検証しないため、任意の文字列で構いません。

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

次に、チャット補完リクエストを送信します。これはOpenAI APIと同じメッセージ形式を使用します。つまり、`"user"`や`"assistant"`のようなロールを持つメッセージのリストです。`stream=True`に設定すると、応答は一度にすべて届くのではなく、段階的に届くようになります。

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

最後に、ストリーミングされたチャンクを反復処理し、到着したテキストの各部分を出力します。

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

同梱の[chat_with_model.py](assets/chat_with_model.py)スクリプトには、この例全体が含まれており、ダウンロードできます。


## モデルの選択と設定

デフォルトでは、`vllm-launch`はテストモデルとして`Qwen/Qwen3-1.7B`をポート`8001`でサービングします。コンテナを再構築したり編集したりすることなく、モデル、ポート、vLLMサービングパラメータを変更できます。

### AMDによってテストされたモデル

以下のモデルは、AMDによって事前設定・検証済みです。

| モデル | 注記 |
|-------|-------|
| `Qwen/Qwen3-1.7B` | デフォルトモデル。軽量で読み込みが高速です。 |
| `openai/gpt-oss-20b` | より高品質な応答を得るための大規模モデルです。 |

### 別のモデルを起動する

`--model`(または`-m`)でモデルIDを渡します。

```bash
vllm-launch --model openai/gpt-oss-20b
```

### ポートの変更

`--port`(または`-p`)で1024より大きいポートを渡します。デフォルトは`8001`です。

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

ポートを変更する場合は、クライアントの`base_url`を同じポートに向けてください(例: `http://localhost:8080/v1`)。

### 追加のvLLMパラメータを渡す

追加の引数はすべてvLLMに直接転送されるため、コンテキスト長やデータ型などのサービング動作を調整できます。これを指定する方法は2通りあります。

**インライン**で、ランチャーオプションの後に指定します。

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**永続的**に、`~/.local/share/vLLM/vllm-launch.conf`の設定ファイルに指定します。このファイルはデフォルトでは存在しないため、作成してBash配列として引数を追加してください。

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

デフォルトの引数を置き換えるのではなく追加するには、`+=`を使用します。

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

いつでもすべてのランチャーオプションを確認するには、以下を実行してください。

```bash
vllm-launch --help
```

### モデルの保存場所

`vllm-launch`は、次の2つの場所でモデルを探します。

| 場所 | パス |
|----------|------|
| システムモデル | `/var/cache/models` |
| ユーザーモデル | `~/.local/share/vLLM/models` |

ダウンロードしたモデルをいずれかのディレクトリに配置し、そのパスまたはIDを`--model`に渡すことで起動できます。

```bash
vllm-launch --model /var/cache/models/my-model
```

> **注**: この方法で独自のダウンロード済みモデルを実行することは、モデルが上記のいずれかのディレクトリに配置されていれば動作すると想定されますが、このワークフローはまだAMDによって正式に検証されていません。

## トラブルシューティング

### 接続が拒否される

サーバーが動作していることを確認してください。
```bash
curl http://localhost:8001/health
```

## まとめ

本プレイブックでは、以下の方法を学びました。

- 統合GPU上でROCm対応のコンテナ化されたvLLMを起動する
- ポート8001でOpenAI互換APIエンドポイントを持つvLLMサーバーを起動する
- `vllm-prompt`でプロンプトを送信する
- ストリーミングリクエストと非ストリーミングリクエストの両方を使用してvLLMサーバーにAPI呼び出しを行う
- サーバー起動、メモリ、クライアント接続に関する一般的な問題をトラブルシューティングする

これで、統合GPU上で最適化されたパフォーマンスで大規模言語モデルをサービングするための、コンテナ化されたvLLMデプロイが完成しました。

## 次のステップ

- **さまざまなモデルを試す** — `vllm-launch --model <model>`を使用して、さまざまなLLMを試し、パフォーマンスを比較してください([モデルの選択と設定](#choosing-and-configuring-a-model)を参照)。
- **アプリケーションを構築する** — OpenAI互換APIを使用して、vLLMをPythonアプリ、チャットボット、または自動化ワークフローに統合してください。
- **ファインチューニングとサービング** — LoRAまたはQLoRAを使用してモデルをファインチューニングし、最適化された推論のためにvLLMでデプロイしてください。
## 追加リソース

- **[vLLM公式ドキュメント](https://docs.vllm.ai/)** — 包括的なガイドおよびAPIリファレンス
- **[vLLM GitHubリポジトリ](https://github.com/vllm-project/vllm)** — ソースコード、課題、コミュニティディスカッション