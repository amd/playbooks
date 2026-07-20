<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> This playbook requires a minimum of **32GB** of system memory.
<!-- @device:end -->

## 概要

コーディングエージェントは、大規模言語モデル(LLM)を活用したAIエージェントとの連携を通じて開発者を強力に支援するツールです。ターミナルやVS Codeなどの開発環境に組み込むことができ、開発者のワークフローにシームレスに統合できます。

このチュートリアルでは、Cline、VS Code、LM Studioを使用して、コーディングエージェントを完全にローカルマシン上で実行する方法を紹介します。

## このチュートリアルで学べること

* ソフトウェアエンジニアリングタスクを支援するために、Clineコーディングエージェントを搭載したVS Codeを実行する方法。
* コーディングエージェントのローカル推論のために、ClineをLM Studioと通信するよう設定する方法。
* ローカルコーディングエージェントを使用して、実際のソフトウェアエンジニアリングタスクを解決する方法。

## メモリ構成の設定

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアアップデートの確認
> **注記**: VS Codeがインストールされていない場合は、Ryzen AI Developer Centerからインストールできます。

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェア前提条件のインストール

<!-- @require:lmstudio,vscode -->

## LM Studioの起動と設定

コーディングエージェントを動かすLLMをサービングするためにLM Studioを使用します。

- 検索バーで`LM Studio`を検索し、アプリケーションを起動します。以下のページが表示されます。

![LM Studio Initial Screen](assets/initial-lm-studio.png)

次に、システム上にLLMをロードする必要があります。大きなコンテキスト長を持つ`Qwen3-Coder-30B-A3B`モデルを使用します。(まだインストールしていない場合は、Modelタブを使用してインストールしてください)。
- LM Studioウィンドウ上部の検索バーをクリックするか、`CTRL+L`を押します。`Manually choose model load parameters`のスイッチをクリックし、次にQwen3-Coder-30B-A3Bモデルをクリックします。
- コンテキスト長を`4096`から`32768`に変更し、`GPU Offload`が最大に設定されていることを確認します。その後、`Load Model`をクリックします。

![Selecting Model](assets/model-list-zoomed.png)

大きなコンテキスト長を使用することで、エージェントが大規模なコードベースを処理し、行われた変更を記憶できるようになります。

![Configuring Model](assets/selecting-model-zoomed.png)

次に、LM Studio Serverを有効にする必要があります。
- LM Studioの左側にあるDeveloperタブをクリックするか、`CTRL+2`を押します。
- ステータストグルをチェックし、`Running`に設定されていることを確認します。

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
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
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
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## VS Codeの起動と設定

VS CodeにCline拡張機能をインストールし、先ほど作成したLM Studioサーバーに接続します。
- 検索バーで`VS Code`を検索し、アプリケーションを起動します。
- VS Codeの左側の列にある`Extensions`アイコンをクリックし、`Cline`を検索します。次に`Install`ボタンをクリックします。

![Installing Cline Extension](assets/installing-cline-vscode-extension.png)

- 左側にClineアイコンが表示されます。それをクリックしてClineを開きます。`How will you use Cline?`と尋ねるウィンドウが表示されます。今回はLM Studio経由で動作するローカルLLMを使用するため、`Bring my own API Key`を選択し、`Continue`を押します。

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

次に、先ほどセットアップしたLM Studioサーバーと通信するようにClineを設定する必要があります。
- API Providerを`LM Studio`に、モデルを`Qwen3-Coder-30B-A3B-GGUF`に設定します。

>**ヒント**: 新しいモデルが利用可能な場合があります。必要に応じて、Qwen3.6モデルをダウンロードして切り替えることを検討してください。


![Model Configuration](assets/cline-model-configuration-zoomed.png)

## 最初のプロジェクトを作成する

ローカルエージェントを使ってウェブサイトを作成してみましょう!Clineがファイルを作成する任意のディレクトリでVS Codeを開いてください。
- これを行うには、VS Codeの左上にある`File -> Open Folder`に移動し、`Documents`のようなフォルダを選択します。

![VS Code Empty Folder](assets/open-cline-test.png)

これでローカルコーディングエージェントにプロンプトを送る準備が整いました。
- 左側の列にあるCline拡張機能をクリックし、エージェントを起動するためのプロンプトを入力します。例として、次のプロンプトを使用しましょう:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

すると、エージェントはプロンプトに従ってファイルの作成を開始します。ユーザーは、以下に示すようにVS Code内でコードが生成される様子を確認できます。Clineがファイルを作成しようとするたびに、`Save`をクリックする必要がある場合があります。

![Cline Code Generation](assets/cline-code-generation.png)

ソフトウェアの生成後、エージェントの作業は完了し、アプリケーションを実行できます。この例では、エージェントは`index.html`、`script.js`、`styles.css`の3つのファイルに書き込みました。HTMLファイルをダブルクリックするだけで、生成されたウェブサイトを読み込んで操作できます。

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
## 次のステップ

Webサイトを生成した後も、Clineを使ってWebサイトの改善を続けることができます。改善案として、以下の2つが考えられます。

- **ドキュメント作成**: `Add a README` とエージェントに指示するだけで、Webサイトを説明する `README.md` ファイルを生成できます。
- **アニメーション**: `Add an animation that visually represents a large language model running on a laptop.` とモデルに指示することで、Webサイトにアニメーションを追加できます。

読者の皆様には、この構成を使って他のアプリケーションを生成してみることをお勧めします。以下に、私たちが試して面白かった例をいくつか紹介します。

- **レトロアーケードゲーム**: 他のプロンプトも試してみてください。以下のプロンプトを使って、エージェントに `PyGame` パッケージを使ったPython製のレトロスタイルのゲームを作らせるのも面白いでしょう。

```code
Create a simple pong game using the PyGame python package.
```

- **データ分析**: コーディングエージェントが特に役立つ分野の一つが、スクリプト作成とデータ分析です。以下は、株価の可視化のためのデータ分析ソフトウェアをローカルモデルが生成できることを示すプロンプトです。

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## リソース

以下は、コーディングエージェント、Cline、そして 上でのワークロードの実行についてさらに詳しく学ぶための追加リソースです。

* AMDとLM Studioのパートナーシップおよび統合に関する詳細情報: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD Ryzen™ AIおよびRadeon™グラフィックスカードでClineを実行する方法を解説したAMDブログ: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* AI PC上でコーディングエージェントをローカル実行する方法についてのClineブログ: https://cline.bot/blog/local-models-amd