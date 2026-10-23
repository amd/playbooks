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

LM Studioは、[llama.cpp](https://github.com/ggml-org/llama.cpp)を強力なGUIベースでラップしたツールであり、ローカルモデルの提供のために[OpenAI準拠のエンドポイント](https://lmstudio.ai/docs/developer/openai-compat)も提供しています。LM Studioは、モデルを簡単にダウンロードしてデプロイできる、シンプルながら強力なインターフェースを提供します。LM Studioは、AMDユーザー向けにVulkanとAMD ROCm™ software（ランタイムと呼ばれる）の両方のバックエンドを提供しています。

<!-- @device:halo_box -->
> **注記：** AMD Ryzen AI Halo搭載システムの中には、このプレイブック用のモデルが既にインストールされているものと、されていないものがあります。どちらの場合もサポートされています。**Downloading Models**セクションに到達したら、LM Studio内でモデルが既に利用可能かどうかを確認してください。利用可能であればダウンロードを省略でき、利用できない場合はそのセクションの手順に従ってダウンロードしてください。
<!-- @device:end -->


## 学習内容
- LM Studioを設定し、ローカルハードウェアを活用する方法
- 完全にオフラインの環境でLLMをテストし、管理する方法
- OpenAI互換APIを介してモデルを提供し、カスタムワークフローやアプリを実現する方法


<!-- @device:halo_box,halo,stx,krk -->
## メモリ構成の設定

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ソフトウェアアップデートの確認

<!-- @os:linux -->
> **注記**：VS CodeはAMD Ryzen™ AI Developer Centerからインストールできます。LM Studioについては、以下のインストール手順に従ってください。
<!-- @os:end -->

<!-- @os:windows -->
> **注記**：VS CodeまたはLM Studioがインストールされていない場合は、AMD Ryzen™ AI Developer Centerからインストールできます。
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェアの前提条件のインストール

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->
<!-- @prereq:lmstudio -->

## モデルのダウンロード

<!-- @var:id=lms_model device=halo,halo_box value="gpt-oss-120b" -->
<!-- @var:id=lms_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="qwen3.5-9b" -->
<!-- @var:id=model_name device=halo,halo_box value="GPT-OSS 120B" -->
<!-- @var:id=model_name device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen3.5 9B" -->

<!-- @device:halo,halo_box -->
<!-- @require:lmstudio-models-gpt-oss-120b -->
<!-- @prereq:lmstudio-models-gpt-oss-120b -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @require:lmstudio-models-qwen3-9b -->
<!-- @prereq:lmstudio-models-qwen3-9b -->
<!-- @device:end -->

## LLMとチャットする
ChatGPT並みの性能を持つLLMと完全にローカルでチャットを開始する方法を学びましょう。

1. LMStudioを開きます。
2. `Ctrl + L`を押してモデルローダーを開き、`Manually choose model load parameters`を選択してから、`${model_name}`をクリックします。
3. 「show advanced settings」にチェックが入っていることを確認します。
4. 必要に応じて`Context Length`を変更します。コンテキスト長を大きくすると、モデルのメモリ使用量が増え、システムメモリの使用量も増加します。このプレイブックでは4096を推奨します。
5. `GPU Offload`が最大に設定されており、`Flash Attention`がOnになっていることを確認します（Cache Quantizationsはオフのままで構いません）。
6. `Remember settings`にチェックを入れ、`Load Model`をクリックします。
7. チャットウィンドウが表示されていない場合は、`Ctrl + 1`を押すか、画面左上の👾ボタンをクリックします。
8. メッセージを送信し、モデルとの対話を開始しましょう！

<!-- @os:windows -->
<!-- @test:id=lmstudio-select-gpu-runtime-windows timeout=120 hidden=True -->
```powershell
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
$rt = ((lms runtime ls) -match 'vulkan' | Select-Object -First 1)
if ($rt) {
  lms runtime select (($rt.Trim() -split '\s+')[0])
  lms runtime ls | Select-String 'ENGINE|✓'
} else {
  Write-Output "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-model-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "${lms_model}-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
# retry once: large-model loads can transiently fail under memory pressure
lms load ${lms_model} --context-length 4096 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load ${lms_model} --context-length 4096 --gpu max --identifier "$ID" -y }
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-select-gpu-runtime-linux timeout=120 hidden=True -->
```bash
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
GPU_RT="$(lms runtime ls 2>/dev/null | awk '/vulkan/{print $1; exit}')"
if [ -n "$GPU_RT" ]; then
  lms runtime select "$GPU_RT"
  lms runtime ls | grep -E 'ENGINE|✓'
else
  echo "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
fi
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
# retry once: large-model loads can transiently fail under memory pressure
lms load ${lms_model} --context-length 4096 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load ${lms_model} --context-length 4096 --gpu max --identifier "$ID" -y; }
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

> **ヒント**：コンテキスト長とは、モデルの記憶量を指します。Flash Attentionは、メモリ使用量を抑えつつ処理速度を向上させます。GPU Offloadは、処理をグラフィックスカードに移すことで応答を高速化します。

## OpenAI互換エンドポイントを介してLLMを提供する

LM Studioは、LM Studio Serverという形でOpenAI準拠のエンドポイントも提供しています。これは、Clineを使用したエージェント型コーディングワークフローの中で[こちら](../playbooks/vscode-qwen3-coder)で既に紹介されています。もう一つの一般的なユースケースは、標準のHTTPリクエストを推論エンドポイントに送信することで、LM Studio Serverを任意のWebアプリケーション（React、Node.js、Python）に接続することです。

LM Studio Serverを設定するには、以下の手順に従ってください。

1. 左側にある`Developer`タブ（コマンドラインアイコン）または`Ctrl + 2`をクリックし、続いて`Server Settings`をクリックします。
2. （任意）モデルをLAN経由で提供したい場合は、`Serve on Local Network`にチェックを入れてください。ウェブサイトと一緒に使用したい場合や、VS Code内で多数の呼び出しを行いたい場合は、`Enable CORS`にチェックを入れてください。
3. 左上隅で、`Status`の前にあるトグルボタンをクリックして、サーバーが実行中であることを確認します。
4. これで、OpenAI準拠のエンドポイントが稼働するようになります。アドレスは通常 http://127.0.0.1:1234 です。
5. モデルがまだロードされていない場合は、`Load Model`をクリックし、前述の手順に従ってロードできます。

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


これで、このモデルはLM Studio Serverのエンドポイントを通じてアクセス可能になり、以下を含むOpenAIエンドポイントをサポートするようになります。

| エンドポイント | メソッド | ドキュメント |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### 例: エンドポイントへの ping

OpenAI 互換エンドポイントを作成したので、これを Python 開発環境(VSCode など)に統合し、システムをローカル API プロバイダーとして使用する方法を見ていきましょう。

1. Python 仮想環境を作成します:

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
**GPU デバイスへのユーザーアクセスを許可します**(これを有効にするにはログアウトして再度ログインしてください):

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

    > **ヒント**: Windows ユーザーは、一部の PowerShell コマンドを実行する前に、PowerShell の実行ポリシーを変更する必要がある場合があります(例: RemoteSigned または Unrestricted に設定)。

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    Windows では、任意のディレクトリでターミナルを開き、以下のコマンドに従って venv を作成します。
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **ヒント**: Windows ユーザーは、一部の PowerShell コマンドを実行する前に、PowerShell の実行ポリシーを変更する必要がある場合があります(例: RemoteSigned または Unrestricted に設定)。

<!-- @device:end -->
<!-- @os:end -->

2. OpenAI パッケージをインストールします
    ```bash
    pip install openai
    ```

3. 次のスクリプトを実行して、先ほど作成したエンドポイントに ping します。
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
   "max_tokens": 64
 }).encode("utf-8"),
 headers={"Content-Type":"application/json"},
 method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
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
   "max_tokens": 64
 }).encode("utf-8"),
 headers={"Content-Type":"application/json"},
 method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
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

#### (任意): ランタイムの切り替え

1. キーボードで `Ctrl + Shift + R` を押します。または左側の `Discover` タブ(虫眼鏡アイコン)をクリックし、ポップアップ内の `Runtime` をクリックします。
2. `Runtime Selections` が表示され、ドロップダウンメニューを使用してランタイムを変更できます。


## 次のステップ

- **カスタムアプリの統合**: ローカルの OpenAI 互換 API を使用して、独自の Python スクリプトやアプリケーションを統合します。
- **高度なフロントエンド**: Open WebUI のような強力なインターフェースをサーバーに接続し、チャット履歴やペルソナ管理を行います。

詳細なドキュメントについては、以下をご覧ください: https://lmstudio.ai/docs/developer