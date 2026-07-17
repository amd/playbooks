<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> このプレイブックは、GitHub でレンダリングできない特殊なタグを使用しています。このコンテンツを正しくプレビューするには、[amd.com/playbooks](https://amd.com/playbooks) をご覧ください。
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> このプレイブックには、最低 **32GB** のシステムメモリが必要です。
<!-- @device:end -->

## 概要

コーディングエージェントは、大規模言語モデル（LLM）を搭載した AI エージェントとの協働を通じて、開発者を強力にサポートするツールです。ターミナルや VS Code などの開発環境に組み込むことができ、開発者のワークフローにシームレスに統合できます。

このチュートリアルでは、Cline、VS Code、および LM Studio を使用して、コーディングエージェントをローカルマシン上で完全に実行する方法を説明します。

## 学習内容

* ソフトウェアエンジニアリングタスクを支援するために、Cline コーディングエージェントと共に VS Code を実行する方法。
* コーディングエージェントのローカル推論のために、Cline が LM Studio と通信するよう設定する方法。
* ローカルコーディングエージェントを使用して、実際のソフトウェアエンジニアリングタスクを解決する方法。

## メモリ設定の構成

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアアップデートの確認
> **注意**: VS Code がインストールされていない場合は、Ryzen AI Developer Center からインストールできます。

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェア前提条件のインストール

<!-- @require:lmstudio,vscode -->

## LM Studio の起動と設定

コーディングエージェントを動かす LLM を提供するために LM Studio を使用します。

- 検索バーで `LM Studio` を検索し、アプリケーションを起動します。次のページが表示されます。

![LM Studio 初期画面](assets/initial-lm-studio.png)

次に、システムに LLM を読み込む必要があります。大きなコンテキスト長を持つ `Qwen3-Coder-30B-A3B` モデルを使用します。（まだインストールしていない場合は、「モデル」タブからインストールしてください。）
- LM Studio ウィンドウ上部の検索バーをクリックするか、`CTRL+L` を押します。`Manually choose model load parameters` スイッチをクリックし、Qwen3-Coder-30B-A3B モデルをクリックします。
- コンテキスト長を `4096` から `32768` に変更し、`GPU Offload` が最大になっていることを確認します。その後、`Load Model` をクリックします。

![モデルの選択](assets/model-list-zoomed.png)

エージェントが大規模なコードベースを処理し、加えられた変更を記憶できるよう、大きなコンテキスト長を使用します。

![モデルの設定](assets/selecting-model-zoomed.png)

次に、LM Studio サーバーを有効にする必要があります。
- LM Studio の左側にある「Developer」タブをクリックするか、`CTRL+2` を押します。
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

![サーバーステータス](assets/lm-studio-server-status.png)

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

## VS Code の起動と設定

Cline 拡張機能を VS Code にインストールし、先ほど作成した LM Studio サーバーに接続します。
- 検索バーで `VS Code` を検索し、アプリケーションを起動します。
- VS Code の左列にある `Extensions` アイコンをクリックし、`Cline` を検索します。次に、`Install` ボタンをクリックします。

![Cline 拡張機能のインストール](assets/installing-cline-vscode-extension.png)

- 左側に Cline アイコンが表示されます。それをクリックして Cline を開きます。`How will you use Cline?` というウィンドウが表示されます。LM Studio 経由でローカル LLM を使用するため、`Bring my own API Key` を選択し、`Continue` をクリックします。

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

![アカウント作成](assets/cline-how-will-you-use-cline-zoomed.png)

次に、設定した LM Studio サーバーと通信するよう Cline を設定する必要があります。
- API プロバイダーを `LM Studio`、モデルを `Qwen3-Coder-30B-A3B-GGUF` に設定します。

>**ヒント**: より新しいモデルが利用可能な場合があります。必要に応じて Qwen3.6 モデルをダウンロードして切り替えることを検討してください。


![モデルの設定](assets/cline-model-configuration-zoomed.png)

## 最初のプロジェクトの作成

ローカルエージェントを使ってウェブサイトを作成しましょう！Cline がファイルを作成する任意のディレクトリに VS Code を開きます。
- これを行うには、VS Code の左上にある `File -> Open Folder` に移動し、`Documents` などのフォルダーを選択します。

![VS Code 空フォルダー](assets/open-cline-test.png)

これでローカルコーディングエージェントにプロンプトを入力する準備が整いました。
- 左列の Cline 拡張機能をクリックし、エージェントを起動するプロンプトを入力します。例として、次のプロンプトを使用しましょう：
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

エージェントはプロンプトに従ってファイルの作成を開始します。ユーザーは、以下に示すように VS Code でコードが生成される様子を確認できます。Cline がファイルを作成するたびに `Save` をクリックする必要がある場合があります。

![Cline コード生成](assets/cline-code-generation.png)

ソフトウェアの生成後、エージェントは完了し、アプリケーションを実行できます。この場合、エージェントは `index.html`、`script.js`、`styles.css` の 3 つのファイルに書き込みました。HTML ファイルをダブルクリックするだけで、生成されたウェブサイトを読み込んで操作できます。

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

ウェブサイトを生成した後も、Cline を使ってウェブサイトを改善し続けることができます。考えられる改善点として次の 2 つがあります：

- **ドキュメント**: エージェントに `Add a README` とプロンプトを入力するだけで、ウェブサイトを説明する `README.md` ファイルが生成されます。
- **アニメーション**: `Add an animation that visually represents a large language model running on a laptop.` とモデルにプロンプトを入力して、ウェブサイトにアニメーションを追加します。

このセットアップを使って他のアプリケーションの生成にも挑戦してみることをお勧めします。以下は私たちが試したいくつかの楽しい例です：

- **レトロアーケードゲーム**: 他のプロンプトも試してみてください。次のプロンプトを使って、エージェントが `PyGame` パッケージを使用した Python のレトロスタイルゲームを作成するのも楽しいです：

```code
Create a simple pong game using the PyGame python package.
```

- **データ分析**: コーディングエージェントが特に役立つ分野の一つがスクリプティングとデータ分析です。これは、株価の可視化のためのデータ分析ソフトウェアを生成するローカルモデルの能力を示すプロンプトです：

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## リソース

コーディングエージェント、Cline、およびワークロードの実行についてさらに詳しく学ぶための追加リソースを以下に示します。

* AMD と LM Studio のパートナーシップおよび統合に関する詳細情報: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD Ryzen™ AI および Radeon™ グラフィックスカードで Cline を実行する方法を解説した AMD ブログ: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* AI PC でコーディングエージェントをローカルに実行することに関する Cline ブログ: https://cline.bot/blog/local-models-amd