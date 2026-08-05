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

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> このプレイブックには、最低 **32GB** のシステムメモリが必要です。
<!-- @device:end -->

## 概要

コーディングエージェントは、大規模言語モデル(LLM)を活用した AI エージェントとの連携を通じて開発者の力を引き出す強力なツールです。ターミナルや VS Code などの開発環境に組み込むことができ、開発者のワークフローにシームレスに統合できます。

このチュートリアルでは、Cline、VS Code、LM Studio を使用して、コーディングエージェントをローカルマシン上で完全に実行する方法を説明します。

## このチュートリアルで学ぶこと

* ソフトウェアエンジニアリングタスクを支援するために、Cline コーディングエージェントを使って VS Code を実行する方法。
* コーディングエージェントのローカル推論のために、Cline を LM Studio と通信するように設定する方法。
* ローカルのコーディングエージェントを使って、実際のソフトウェアエンジニアリングタスクを解決する方法。

## メモリ設定の構成

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアの更新を確認する
> **Note**: VS Code がインストールされていない場合は、Ryzen AI Developer Center からインストールできます。

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェアの前提条件をインストールする

<!-- @require:lmstudio,vscode -->

## LM Studio を起動して設定する

コーディングエージェントを動かす LLM を提供するために LM Studio を使用します。

- 検索バーで `LM Studio` を検索し、アプリケーションを起動します。以下のページが表示されます。

![LM Studio Initial Screen](assets/initial-lm-studio.png)

次に、システムに LLM をロードする必要があります。今回は、大きなコンテキスト長を持つ `Qwen3-Coder-30B-A3B` モデルを使用します。(まだインストールしていない場合は、Model タブを使ってインストールしてください)。
- LM Studio ウィンドウ上部の検索バーをクリックするか、`CTRL+L` を押します。`Manually choose model load parameters` のスイッチをクリックし、次に Qwen3-Coder-30B-A3B モデルをクリックします。
- コンテキスト長を `4096` から `32768` に変更し、`GPU Offload` が最大に設定されていることを確認します。その後、`Load Model` をクリックします。

![Selecting Model](assets/model-list-zoomed.png)

大きなコンテキスト長を使用するのは、エージェントが大規模なコードベースを処理し、行われた変更を記憶できるようにするためです。

![Configuring Model](assets/selecting-model-zoomed.png)

次に、LM Studio Server を有効にする必要があります。
- LM Studio の左側にある Developer タブをクリックするか、`CTRL+2` を押します。
- ステータストグルを確認し、`Running` に設定されていることを確認します。

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

![Server Status](assets/lm-studio-server-status.png)

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
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y }
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
<!-- @test:id=lmstudio-load-qwen3-coder-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="qwen3coder-32k-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y; }
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## VS Code を起動して設定する

VS Code に Cline 拡張機能をインストールし、先ほど作成した LM Studio サーバーに接続します。
- 検索バーで `VS Code` を検索し、アプリケーションを起動します。
- VS Code の左側の列にある `Extensions` アイコンをクリックし、`Cline` を検索します。次に、`Install` ボタンをクリックします。

![Installing Cline Extension](assets/installing-cline-vscode-extension.png)

- 左側に Cline アイコンが表示されるはずです。それをクリックして Cline を開きます。`How will you use Cline?` と尋ねるウィンドウが表示されます。今回は LM Studio 経由で実行されているローカル LLM を使用するため、`Bring my own API Key` を選択し、`Continue` をクリックします。

<!-- @os:windows -->
<!-- @test:id=cline-install-and-verify-windows timeout=300 hidden=True -->
```powershell
code --install-extension saoudrizwan.claude-dev
code --list-extensions | Select-String -Pattern "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=cline-install-and-verify-linux timeout=300 hidden=True -->
```bash
code --install-extension saoudrizwan.claude-dev
code --list-extensions | grep -i "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

![Account Creation](assets/cline-how-will-you-use-cline-zoomed.png)

次に、設定した LM Studio サーバーと通信できるように Cline を設定する必要があります。
- API Provider を `LM Studio` に、モデルを `Qwen3-Coder-30B-A3B-GGUF` に設定します。

>**Tip**: より新しいモデルが利用可能な場合があります。必要に応じて Qwen3.6 モデルをダウンロードして切り替えることを検討してください。


![Model Configuration](assets/cline-model-configuration-zoomed.png)

## 最初のプロジェクトを作成する

ローカルエージェントを使ってウェブサイトを作成してみましょう!Cline がファイルを作成する任意のディレクトリで VS Code を開きます。
- これを行うには、VS Code の左上にある `File -> Open Folder` に移動し、`Documents` のようなフォルダを選択します。

![VS Code Empty Folder](assets/open-cline-test.png)

これでローカルのコーディングエージェントにプロンプトを入力する準備ができました。
- 左側の列にある Cline 拡張機能をクリックし、エージェントを起動するプロンプトを入力します。例として、次のプロンプトを使用してみましょう:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

すると、エージェントはプロンプトに従ってファイルの作成を開始します。ユーザーは、以下に示すように VS Code 内でコードが生成される様子を確認できます。Cline がファイルを作成しようとするたびに、`Save` をクリックする必要がある場合があります。

![Cline Code Generation](assets/cline-code-generation.png)

ソフトウェアの生成後、エージェントの処理は完了し、アプリケーションを実行できるようになります。今回のケースでは、エージェントは `index.html`、`script.js`、`styles.css` の3つのファイルを作成しました。HTML ファイルをダブルクリックするだけで、生成されたウェブサイトを読み込んで操作できます。

<!-- @os:windows -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
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
<!-- @test:id=lmstudio-coding-prompt-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request
with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()
req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
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
## 次のステップ

Webサイトを生成した後も、Clineを使ってWebサイトの改善を続けることができます。可能な改善例を2つ紹介します。

- **ドキュメント作成**: エージェントに`Add a README`とプロンプトを送るだけで、Webサイトを説明する`README.md`ファイルを生成できます。
- **アニメーション**: `Add an animation that visually represents a large language model running on a laptop.`とモデルにプロンプトを送ることで、Webサイトにアニメーションを生成できます。

読者の皆様にも、このセットアップを使って他のアプリケーションを生成してみることをお勧めします。以下は、私たちが試して楽しかった例です。

- **レトロアーケードゲーム**: 他のプロンプトも試してみてください。エージェントに`PyGame`パッケージを使ってPythonでレトロスタイルのゲームを作成させるのも、以下のプロンプトで楽しむことができます。

```code
Create a simple pong game using the PyGame python package.
```

- **データ分析**: コーディングエージェントが特に役立つ分野の一つが、スクリプト作成とデータ分析です。以下は、ローカルモデルの株価可視化のためのデータ分析ソフトウェアを生成する能力を示すプロンプトです。

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## リソース

Coding Agents、Cline、そしてAMD上でのワークロード実行について詳しく学ぶための追加リソースを以下に示します。

* AMDとLM Studioのパートナーシップおよび統合に関する詳細情報: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD Ryzen™ AIおよびRadeon™ Graphicsカード上でClineを実行する方法を解説するAMDブログ: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* AI PC上でコーディングエージェントをローカルで実行することに関するClineブログ: https://cline.bot/blog/local-models-amd