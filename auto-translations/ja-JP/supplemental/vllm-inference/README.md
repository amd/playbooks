<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> このプレイブックはGitHubがレンダリングできない特別なタグを使用しています。このコンテンツを正しくプレビューするには、[amd.com/playbooks](https://amd.com/playbooks) をご覧ください。
<!-- @github-only:end -->


## 概要

vLLMは、大規模言語モデル(LLM)向けに設計された高性能な推論エンジンです。高スループットを実現する継続的バッチ処理による最適化されたサービングと、シームレスなアプリケーション統合のためのOpenAI互換APIを提供します。これにより、速度とリソース効率が重要となる本番環境デプロイメントにvLLMは最適です。

このプレイブックでは、統合GPU上でコンテナ化されたvLLMを使用してLLMをサービングし、OpenAI Python APIを通じてモデルとやり取りする方法を学びます。

## 学習内容

- AMD ROCm™サポート付きでvLLMサーバーをセットアップおよび起動する方法
- OpenAI互換APIエンドポイントを通じてモデルとやり取りする方法
- `vllm-prompt`を使用してローカルサーバーにプロンプトを送信する方法

## メモリ設定

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアアップデートの確認

> **注**: VS Codeがインストールされていない場合は、AMD Ryzen™ AI Developer Centerでインストールできます。

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェア前提条件のインストール

このプレイブックでは、vLLM、ROCmサポート、およびサーバーの起動に必要なヘルパースクリプトを含む事前ビルド済みのコンテナイメージを使用します。PyTorch、vLLM、またはローカルのプレイブックスクリプトを手動でインストールする必要はありません。

ホスト側でのvLLMインストール手順はありません。以下でvLLMを起動します：

```bash
vllm-launch
```

このランチャーはコンテナを起動し、統合GPUをターゲットにして、ローカルのOpenAI互換vLLMサーバーを公開します。あるいは、タスクバーのvLLMアイコンをクリックしてください。

## クイックスタート

### 1. vLLMサーバーが実行されていることを確認する

`vllm-launch`はすべてを初期化するのに数分かかる場合があります。起動すると、サーバーは`http://localhost:8001`で利用可能になります。サーバーはフォアグラウンドで実行されるため、起動用ターミナルは開いたままにしておき、残りの手順には別のターミナルを開いてください。以下の例では`Qwen/Qwen3-1.7B`を使用しています。ランチャーが別のモデル用に設定されている場合は、そのモデルIDをリクエスト内で置き換えてください。

### 2. プロンプトを送信する

提供されている`vllm-prompt`スクリプトを使用して、ローカルのvLLM OpenAI互換サーバーにリクエストを送信します：

```bash
vllm-prompt "Tell me a story"
```

### 3. OpenAI Python APIを使用してモデルとチャットする

vLLMはOpenAI互換APIを公開しているため、`openai` Pythonパッケージを使用してやり取りできます。

まず、Python仮想環境を作成します：

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

OpenAIパッケージをインストールします
```bash
pip install openai
```

OpenAIのサーバーではなく、ローカルのvLLMサーバーを指す`OpenAI`クライアントを作成します。`api_key`はクライアントに必須ですが、vLLMはそれを検証しないため、任意の文字列で構いません：

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

次に、チャット完了リクエストを送信します。これはOpenAI APIと同じメッセージ形式(`"user"`や`"assistant"`のようなロールを持つメッセージのリスト)を使用します。`stream=True`に設定すると、レスポンスは一度にまとめてではなく、段階的に届きます：

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

最後に、ストリーミングされたチャンクを反復処理し、届いたテキストの断片を順次表示します：

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

含まれている[chat_with_model.py](assets/chat_with_model.py)スクリプトには、この例全体が記載されており、ダウンロードできます。


## トラブルシューティング

### 接続が拒否される

サーバーが実行されていることを確認してください：
```bash
curl http://localhost:8001/health
```

## まとめ

このプレイブックでは、以下の方法を学びました：

- 統合GPU上でROCmサポート付きのコンテナ化されたvLLMを起動する
- ポート8001でOpenAI互換APIエンドポイントを持つvLLMサーバーを起動する
- `vllm-prompt`を使用してプロンプトを送信する
- ストリーミングと非ストリーミングの両方のリクエストを使用してvLLMサーバーにAPI呼び出しを行う
- サーバー起動、メモリ、クライアント接続に関する一般的な問題をトラブルシューティングする

これで、統合GPU上で最適化されたパフォーマンスで大規模言語モデルをサービングするための、コンテナ化されたvLLMデプロイメントが完成しました。

## 次のステップ

- **さまざまなモデルを試す** — `vllm-launch`の設定でモデルを入れ替えて、さまざまなLLMを試し、パフォーマンスを比較します。
- **アプリケーションを構築する** — OpenAI互換APIを使用して、vLLMをPythonアプリ、チャットボット、または自動化ワークフローに統合します。
- **ファインチューニングとサービング** — LoRAまたはQLoRAを使用してモデルをファインチューニングし、最適化された推論のためにvLLMでデプロイします。

## 追加リソース

- **[vLLM公式ドキュメント](https://docs.vllm.ai/)** — 包括的なガイドとAPIリファレンス
- **[vLLM GitHubリポジトリ](https://github.com/vllm-project/vllm)** — ソースコード、issue、コミュニティディスカッション