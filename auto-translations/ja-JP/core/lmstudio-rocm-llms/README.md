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

LM Studio は、[llama.cpp](https://github.com/ggml-org/llama.cpp) 向けの強力な GUI ベースのラッパーであり、ローカルモデルの提供のために [OpenAI 準拠のエンドポイント](https://lmstudio.ai/docs/developer/openai-compat) も提供しています。LM Studio は、モデルを簡単にダウンロードしてデプロイできる、シンプルながら強力なインターフェースを提供します。LM Studio は、AMD ユーザー向けに Vulkan と AMD ROCm™ ソフトウェアの両方のバックエンド(ランタイムと呼ばれます)を提供しています。


## このプレイブックで学べること
- ローカルハードウェアを活用するために LM Studio を構成し、使用する方法
- 完全にオフラインの環境で LLM をテストおよび管理する方法
- カスタムワークフローやアプリを動作させるために、OpenAI 互換 API 経由でモデルを提供する方法


<!-- @device:halo_box,halo,stx,krk -->
## メモリ構成の設定

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ソフトウェアの更新を確認する

<!-- @os:linux -->
> **注**: VS Code は AMD Ryzen™ AI Developer Center からインストールできます。LM Studio については、以下のインストール手順に従ってください。
<!-- @os:end -->

<!-- @os:windows -->
> **注**: VS Code または LM Studio がインストールされていない場合は、AMD Ryzen™ AI Developer Center からインストールできます。
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェアの前提条件のインストール

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
ChatGPT クラスの LLM と完全にローカル環境でチャットを開始する方法を学びます。

1. LMStudio を開きます。
2. `Ctrl + L` を押してモデルローダーを開き、`Manually choose model load parameters` を選択して、`${model_name}` をクリックします。
3. "show advanced settings" にチェックが入っていることを確認します。
4. `Context Length` を必要に応じて変更します。コンテキスト長を大きくするほど、モデルのメモリ使用量は増えますが、その分システムメモリの使用量も増加します。このプレイブックでは 4096 を推奨します。
5. `GPU Offload` が最大に設定されており、`Flash Attention` が On になっていることを確認します(Cache Quantizations はオフのままで構いません)。
6. `Remember settings` にチェックを入れ、`Load Model` をクリックします。
7. チャットウィンドウが表示されていない場合は、`Ctrl + 1` を押すか、画面左上の 👾 ボタンをクリックします。
8. メッセージを送信して、モデルとの対話を開始しましょう!

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
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y }
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
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y; }
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

> **ヒント**: コンテキスト長とは、モデルの記憶容量のことを指します。Flash attention はメモリ使用量を抑えつつ処理速度を向上させます。GPU Offload は計算処理をグラフィックカードにシフトし、より高速な応答を可能にします。

## OpenAI 互換エンドポイントを通じて LLM を提供する

LM Studio は、LM Studio Server という形で OpenAI 準拠のエンドポイントも提供しています。これについては、Cline を用いたエージェント型コーディングワークフローの中で[こちら](../playbooks/vscode-qwen3-coder)ですでに紹介されています。もう一つの一般的な使用例は、標準的な HTTP リクエストを推論エンドポイントに送信することで、LM Studio Server を任意の Web アプリケーション(React、Node.js、Python)に接続することです。

LM Studio Server をセットアップするには、以下の手順に従ってください。

1. 左側にある `Developer` タブ(コマンドラインアイコン)をクリックするか `Ctrl + 2` を押し、続けて `Server Settings` をクリックします。
2. (任意): モデルを LAN 経由で提供したい場合は、`Serve on Local Network` にチェックを入れます。Web サイトや VS Code 内での広範な呼び出しに使用したい場合は、`Enable CORS` にチェックを入れます。
3. 左上隅にある `Status` の前のトグルボタンをクリックして、サーバーが起動していることを確認します。
4. これで OpenAI 準拠のエンドポイントが起動します。アドレスは通常 http://127.0.0.1:1234 です。
5. モデルがまだロードされていない場合は、`Load Model` をクリックし、前述の手順に従ってロードできます。

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


これで、このモデルは LM Studio Server エンドポイント経由でアクセス可能になり、以下を含む OpenAI エンドポイントをサポートします。

| エンドポイント | メソッド | ドキュメント |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### 例:エンドポイントへの疎通確認

OpenAI互換エンドポイントを作成したところで、これをPython開発環境(VSCodeなど)に統合し、システムをローカルAPIプロバイダーとして使用する方法を見ていきましょう。

1. Python仮想環境を作成します:

<!-- @os:linux -->
<!-- @device:halo_box -->
    Linuxの場合、任意のディレクトリでターミナルを開き、以下のコマンドに従ってvenvを作成します。
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**ユーザーにGPUデバイスへのアクセス権を付与します**(反映させるには一度ログアウトして再度ログインしてください):

```bash
sudo usermod -aG render,video $LOGNAME
```

    Linuxの場合、任意のディレクトリでターミナルを開き、以下のコマンドに従ってvenvを作成します。
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
    Windowsの場合、任意のディレクトリでターミナルを開き、以下のコマンドに従ってvenvを作成します。
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **ヒント**:Windowsユーザーは、一部のPowerShellコマンドを実行する前に、PowerShellの実行ポリシーを変更する必要がある場合があります(例:RemoteSignedまたはUnrestrictedに設定するなど)。

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    Windowsの場合、任意のディレクトリでターミナルを開き、以下のコマンドに従ってvenvを作成します。
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **ヒント**:Windowsユーザーは、一部のPowerShellコマンドを実行する前に、PowerShellの実行ポリシーを変更する必要がある場合があります(例:RemoteSignedまたはUnrestrictedに設定するなど)。

<!-- @device:end -->
<!-- @os:end -->

2. OpenAIパッケージをインストールします
    ```bash
    pip install openai
    ```

3. 以下のスクリプトを実行して、先ほど作成したエンドポイントへの疎通確認を行います。
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

#### (オプション):ランタイムの切り替え

1. キーボードで`Ctrl + Shift + R`を押します。あるいは、左側の`Discover`タブ(虫眼鏡アイコン)をクリックし、ポップアップ内の`Runtime`をクリックします。
2. `Runtime Selections`が表示されるので、ドロップダウンメニューを使用してランタイムを変更できます。


## 次のステップ

- **カスタムアプリの統合**:ローカルのOpenAI互換APIを使用して、独自のPythonスクリプトやアプリケーションを統合します。
- **高度なフロントエンド**:Open WebUIのような強力なインターフェースをサーバーに接続し、チャット履歴やペルソナ管理を行います。

詳細なドキュメントについては、以下をご覧ください:https://lmstudio.ai/docs/developer