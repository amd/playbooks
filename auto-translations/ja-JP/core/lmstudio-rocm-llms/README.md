<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## 概要

LM Studio は [llama.cpp](https://github.com/ggml-org/llama.cpp) の強力な GUI ベースのラッパーであり、ローカルモデルサービング向けの [OpenAI 準拠エンドポイント](https://lmstudio.ai/docs/developer/openai-compat)も提供しています。LM Studio はモデルを簡単にダウンロードしてデプロイできる、シンプルながら強力なインターフェースを提供します。AMD ユーザー向けに、LM Studio は Vulkan と AMD ROCm™ ソフトウェアバックエンド（ランタイムと呼ばれる）の両方を提供しています。


## 学習内容
- ローカルハードウェアを活用するための LM Studio の設定と使用方法
- 完全オフライン環境での LLM のテストと管理
- カスタムワークフローやアプリを動かすための OpenAI 互換 API によるモデルサービング


## メモリ設定の構成

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアアップデートの確認

<!-- @os:linux -->
> **注意**: VS Code は AMD Ryzen™ AI Developer Center からインストールできます。LM Studio については、以下のインストール手順に従ってください。
<!-- @os:end -->

<!-- @os:windows -->
> **注意**: VS Code または LM Studio がインストールされていない場合は、AMD Ryzen™ AI Developer Center からインストールできます。
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェア前提条件のインストール

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## モデルのダウンロード

<!-- @var:id=lms_model device=halo,halo_box value="gpt-oss-120b" -->
<!-- @var:id=lms_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="qwen3.5-9b" -->
<!-- @var:id=model_name device=halo,halo_box value="GPT-OSS 120B" -->
<!-- @var:id=model_name device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen3.5 9B" -->

<!-- @device:halo,halo_box -->
<!-- @require:lmstudio-models-gpt-oss-120b -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @require:lmstudio-models-qwen3-9b -->
<!-- @device:end -->

## LLM とのチャット
ChatGPT レベルの LLM と完全にローカルでチャットを始める方法を学びます。

1. LMStudio を開きます。
2. `Ctrl + L` を押してモデルローダーを開き、`Manually choose model load parameters` を選択して `${model_name}` をクリックします。
3. 「show advanced settings」にチェックが入っていることを確認します。
4. `Context Length` を必要に応じて変更します。コンテキスト長が長いほどモデルのメモリが増えますが、システムメモリの使用量も増加します。このプレイブックでは 4096 を推奨します。
5. `GPU Offload` が最大に設定されており、`Flash Attention` がオンになっていることを確認します（Cache Quantizations はオフのままで構いません）。
6. `Remember settings` にチェックを入れ、`Load Model` をクリックします。
7. チャットウィンドウにいない場合は、`Ctrl + 1` を押すか、画面左上の 👾 ボタンをクリックします。
8. メッセージを送信してモデルとのやり取りを始めましょう！

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-model-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "${lms_model}-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-model-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="${lms_model}-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<p align="center">
  <img src="assets/chat.png" alt="Chatting with ${model_name} on LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<p align="center">
  <img src="assets/chat_qwen.png" alt="Chatting with ${model_name} on LM Studio" width="600"/>
</p>
<!-- @device:end -->

> **ヒント**: コンテキスト長はモデルのメモリを指します。Flash Attention はメモリ使用量を削減しながら処理速度を向上させます。GPU Offload は計算をグラフィックスカードに移行し、応答を高速化します。

## OpenAI 互換エンドポイントを通じた LLM のサービング

LM Studio は LM Studio Server という形で OpenAI 準拠エンドポイントも提供しています。これはすでに Cline を使ったエージェント型コーディングワークフローで[こちら](../playbooks/vscode-qwen3-coder)にて実演されています。もう一つの一般的なユースケースは、LM Studio Server を任意の Web アプリケーション（React、Node.js、Python）に接続し、推論エンドポイントへ標準的な HTTP リクエストを送信することです。

LM Studio Server を設定するには、以下の手順に従ってください：

1. 左側の `Developer` タブ（コマンドラインアイコン）をクリックするか `Ctrl + 2` を押し、`Server Settings` をクリックします。
2. （オプション）: LAN 上でモデルをサービングしたい場合は `Serve on Local Network` にチェックを入れます。Web サイトや VS Code 内での大量の呼び出しに使用したい場合は `Enable CORS` にチェックを入れます。
3. 左上隅で、`Status` の前にあるトグルボタンをクリックしてサーバーが起動していることを確認します。
4. OpenAI 準拠エンドポイントが起動します。アドレスは通常 http://127.0.0.1:1234 です。
5. モデルがまだ読み込まれていない場合は、`Load Model` をクリックし、前述の手順に従って読み込むことができます。

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-up-windows timeout=120 hidden=True -->
```powershell
lms server start --port 1234
curl.exe -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-up-linux timeout=120 hidden=True -->
```bash
lms server start --port 1234
curl -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end --> 
<!-- @os:end -->


このモデルは LM Studio Server エンドポイントを通じてアクセス可能になり、以下の OpenAI エンドポイントをサポートします：

| エンドポイント | メソッド | ドキュメント |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST | [Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |


#### 例: エンドポイントへの疎通確認
作成した OpenAI 互換エンドポイントを使って、Python 開発環境（VSCode など）に統合し、システムをローカル API プロバイダーとして使用する方法を見てみましょう。

1. Python 仮想環境を作成します：

<!-- @os:linux -->
<!-- @device:halo_box -->
    Linux では、任意のディレクトリでターミナルを開き、以下のコマンドに従って venv を作成します。
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**GPU デバイスへのユーザーアクセスを許可します**（有効にするにはログアウトして再度ログインしてください）：

```bash
sudo usermod -aG render,video $LOGNAME
```

    Linux では、任意のディレクトリでターミナルを開き、以下のコマンドに従って venv を作成します。
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
    Windows では、任意のディレクトリでターミナルを開き、以下のコマンドに従って venv を作成します。
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **ヒント**: Windows ユーザーは、一部の PowerShell コマンドを実行する前に PowerShell 実行ポリシーを変更する必要がある場合があります（例：RemoteSigned または Unrestricted に設定する）。

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    Windows では、任意のディレクトリでターミナルを開き、以下のコマンドに従って venv を作成します。
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **ヒント**: Windows ユーザーは、一部の PowerShell コマンドを実行する前に PowerShell 実行ポリシーを変更する必要がある場合があります（例：RemoteSigned または Unrestricted に設定する）。

<!-- @device:end -->
<!-- @os:end -->

2. OpenAI パッケージをインストールします
    ```bash
    pip install openai
    ```

3. 以下のスクリプトを実行して、作成したエンドポイントへの疎通確認を行います。
    ```python
    from openai import OpenAI

    # Initialize the client specifically for your local server
    # The API key is required by the library but ignored by LM Studio
    client = OpenAI(
        base_url="http://localhost:1234/v1", 
        api_key="lm-studio"
    )
    print("Attempting to connect to local LM Studio server...")

    try:
        # Create a simple chat completion request
        completion = client.chat.completions.create(
            model="local-model", # The model identifier is optional in local mode
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": "Explain Python decorators in 1 sentence"}
            ],
            temperature=0.7,
        )
        # Print the response
        print("\nConnection Successful! Server Response:\n")
        print(completion.choices[0].message.content)

    except Exception as e:
        print(f"\nConnection Failed: {e}. Ensure LM Studio server is running on port 1234.")
    ```
<!-- @os:windows -->
<!-- @test:id=lmstudio-ping-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
 "http://127.0.0.1:1234/v1/chat/completions",
 data=json.dumps({
   "model": model_id,
   "messages": [{"role":"user","content":"What is 2 + 2? Reply with only the number."}],
   "temperature": 0,
   "max_tokens": 500
 }).encode("utf-8"),
 headers={"Content-Type":"application/json"},
 method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
 print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-ping-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request

with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
 "http://127.0.0.1:1234/v1/chat/completions",
 data=json.dumps({
   "model": model_id,
   "messages": [{"role":"user","content":"What is 47 + 42? Reply with only the number in words."}],
   "temperature": 0,
   "max_tokens": 500
 }).encode("utf-8"),
 headers={"Content-Type":"application/json"},
 method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
 print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-stop-windows timeout=300 hidden=True -->
```powershell
$ID = Get-Content "$env:TEMP\lmstudio_model_id.txt" -Raw
$ID = $ID.Trim()
lms unload "$ID"
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-stop-linux timeout=300 hidden=True -->
```bash
ID="$(cat /tmp/lmstudio_model_id.txt)"
lms unload "$ID" || true
lms ps
lms server stop
```
<!-- @test:end --> 
<!-- @os:end -->

#### （オプション）: ランタイムの切り替え

1. キーボードで `Ctrl + Shift + R` を押します。または、左側の `Discover` タブ（虫眼鏡アイコン）をクリックし、ポップアップで `Runtime` をクリックします。
2. `Runtime Selections` が表示され、ドロップダウンメニューでランタイムを変更できます。


## 次のステップ

- **カスタムアプリの統合**: ローカルの OpenAI 互換 API を使用して、独自の Python スクリプトやアプリケーションを統合します。
- **高度なフロントエンド**: Open WebUI などの強力なインターフェースをサーバーに接続して、チャット履歴やペルソナ管理を行います。

詳細なドキュメントについては、https://lmstudio.ai/docs/developer をご覧ください。