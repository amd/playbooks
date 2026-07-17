<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> このプレイブックは、GitHub でレンダリングできない特殊なタグを使用しています。このコンテンツを正しくプレビューするには、[amd.com/playbooks](https://amd.com/playbooks) をご覧ください。
<!-- @github-only:end -->


## 概要

vLLM は、大規模言語モデル（LLM）向けに設計された高性能推論エンジンです。高スループットを実現する継続的バッチ処理による最適化されたサービング機能と、シームレスなアプリケーション統合のための OpenAI 互換 API を提供します。これにより、vLLM はスピードとリソース効率が重要な本番環境のデプロイメントに最適です。

このプレイブックでは、コンテナ化された vLLM を統合 GPU 上で使用して LLM をサービングし、OpenAI Python API を通じてモデルと対話する方法を学びます。

## 学習内容

- AMD ROCm™ サポートを備えた vLLM サーバーのセットアップと起動方法
- OpenAI 互換 API エンドポイントを介したモデルとの対話方法
- `vllm-prompt` を使用してローカルサーバーにプロンプトを送信する方法

## メモリ設定

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアアップデートの確認

> **注意**: VS Code がインストールされていない場合は、AMD Ryzen™ AI Developer Center からインストールできます。

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェア前提条件のインストール

このプレイブックでは、vLLM、ROCm サポート、およびサーバーの起動に必要なヘルパースクリプトを含む事前ビルド済みコンテナイメージを使用します。PyTorch、vLLM、またはローカルのプレイブックスクリプトを手動でインストールする必要はありません。

ホスト側での vLLM インストール手順はありません。vLLM を起動するには以下を実行します：

```bash
vllm-launch
```

ランチャーはコンテナを起動し、統合 GPU をターゲットにして、ローカルの OpenAI 互換 vLLM サーバーを公開します。または、タスクバーの vLLM アイコンをクリックしてください。

## クイックスタート

### 1. vLLM サーバーが実行中であることを確認する

`vllm-launch` はすべての初期化に数分かかる場合があります。起動すると、サーバーは `http://localhost:8001` で利用可能になります。サーバーはフォアグラウンドで実行されるため、起動ターミナルは開いたままにしておき、残りの手順は別のターミナルを開いて実行してください。以下の例では `Qwen/Qwen3-1.7B` を使用しています。ランチャーが別のモデル用に設定されている場合は、リクエスト内のモデル ID をそのモデルに置き換えてください。

### 2. プロンプトを送信する

提供されている `vllm-prompt` スクリプトを使用して、ローカルの vLLM OpenAI 互換サーバーにリクエストを送信します：

```bash
vllm-prompt "Tell me a story"
```

### 3. OpenAI Python API を使用してモデルとチャットする

vLLM は OpenAI 互換 API を公開しているため、`openai` Python パッケージを使用して対話できます。

まず、Python 仮想環境を作成します：

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

OpenAI のサーバーではなく、ローカルの vLLM サーバーを指す `OpenAI` クライアントを作成します。`api_key` はクライアントで必須ですが、vLLM は検証しないため、任意の文字列で構いません：

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

次に、チャット補完リクエストを送信します。これは OpenAI API と同じメッセージ形式を使用します — `"user"` や `"assistant"` などのロールを持つメッセージのリストです。`stream=True` を設定すると、レスポンスが一度にすべて届くのではなく、段階的に届きます：

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

最後に、ストリーミングされたチャンクを反復処理し、届いたテキストの各部分を順次出力します：

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

付属の [chat_with_model.py](assets/chat_with_model.py) スクリプトにはサンプル全体が含まれており、ダウンロードできます。


## トラブルシューティング

### 接続が拒否される

サーバーが実行中であることを確認してください：
```bash
curl http://localhost:8001/health
```

## まとめ

このプレイブックでは、以下の方法を学びました：

- 統合 GPU 上で ROCm サポートを備えたコンテナ化された vLLM を起動する
- ポート 8001 で OpenAI 互換 API エンドポイントを持つ vLLM サーバーを起動する
- `vllm-prompt` でプロンプトを送信する
- ストリーミングおよび非ストリーミングリクエストの両方を使用して vLLM サーバーへの API 呼び出しを行う
- サーバーの起動、メモリ、クライアント接続に関する一般的な問題をトラブルシューティングする

これで、統合 GPU 上で最適化されたパフォーマンスにより大規模言語モデルをサービングするためのコンテナ化された vLLM デプロイメントが完成しました。

## 次のステップ

- **さまざまなモデルを試す** — `vllm-launch` 設定のモデルを変更して、異なる LLM を試し、パフォーマンスを比較してみましょう。
- **アプリケーションを構築する** — OpenAI 互換 API を使用して、vLLM を Python アプリ、チャットボット、または自動化ワークフローに統合しましょう。
- **ファインチューニングとサービング** — LoRA または QLoRA を使用してモデルをファインチューニングし、最適化された推論のために vLLM でデプロイしましょう。

## 追加リソース

- **[vLLM 公式ドキュメント](https://docs.vllm.ai/)** — 包括的なガイドと API リファレンス
- **[vLLM GitHub リポジトリ](https://github.com/vllm-project/vllm)** — ソースコード、Issue、およびコミュニティディスカッション