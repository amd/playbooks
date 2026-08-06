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
<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> このプレイブックには、最低でも **32GB** のシステムメモリが必要です。
<!-- @device:end -->
n8nは、ビジュアルなノードベースのエディターを使ってアプリやサービスを接続できるワークフロー自動化プラットフォームです。

このプレイブックでは、AP Newsのビジネスセクションをスクレイピングし、主要な見出しを抽出して、システム上で動作するローカルLLMを使って投資家向けのサマリーを生成する、AI駆動の金融ニュース要約ツールのセットアップ方法を学びます。

## 学べること

- n8nのインストールと起動方法
- 事前構築済みワークフローのインポートと設定
- ネイティブのn8n統合を使ったLemonadeへの接続
- ワークフローのノードとデータフローの理解

## Lemonadeとは？

[Lemonade](https://lemonade-server.ai)は、AMDハードウェア向けに構築されたローカルLLM提供プラットフォームです。OpenAI互換のAPIを提供し、完全にお使いのマシン上で動作するため、データが端末の外に出ることはありません。

このプレイブックでは、Lemonadeを使ってローカルLLMを提供し、n8nがAI駆動タスクのためにそれに接続します。

n8nには**ネイティブのLemonadeノード**（`Lemonade Chat Model`）が含まれており、手動設定不要でファーストクラスの統合を提供します。これにより、ローカルLLMを自動化ワークフローに簡単に接続できます。

## メモリ設定の構成
<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアの更新を確認する
<!-- @require:software-update -->
<!-- @device:end -->
## ソフトウェアの前提条件のインストール
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @require:lemonade,podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="gpt-oss-20b-mxfp4-GGUF" -->
<!-- @device:end -->


<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade (robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1
if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
  -H "Content-Type: application/json" `
  --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
}
finally {
  Remove-Item  $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-chat-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

export MODELS_JSON="$models_json"
python3 - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["MODELS_JSON"])
entry = None
for item in data.get("data", []):
    if item.get("id") == "${lemonade_model}":
        entry = item
        break

if entry is None:
    print("Model ${lemonade_model} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: ${lemonade_model} model is downloaded in Lemonade")
PY

body='{
  "model": "${lemonade_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->
## n8nのインストール
<!-- @os:windows -->
> **注**: いくつかの npm 警告が表示される場合がありますが、これは想定内です。

npm を使用して n8n をグローバルにインストールしてください。

```bash
npm install -g n8n
```

<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **ヒント**: Windows ユーザーは、一部の PowerShell コマンドを実行する前に、PowerShell の実行ポリシーを変更する必要がある場合があります(例: RemoteSigned または Unrestricted に設定する)。
<!-- @os:end -->


<!-- @os:windows -->
> **PATHの問題**:`n8n --version` を実行してコマンドが見つからないと表示される場合は、npmのグローバルbinディレクトリがユーザーの `PATH` に含まれていることを確認してください。通常のインストールパスは `C:\Users\<username>\AppData\Roaming\npm` です。
> これをユーザーパスに追加し(「システム環境変数の編集」>「環境変数」>「ユーザー環境変数を編集」)、ターミナルを再起動してください。
<!-- @os:end -->

<!-- @os:linux -->
これから、Podman サービスを使用して n8n のインストールをコンテナ化していきます。

任意のディレクトリに以下をダウンロードしてください: [compose.yml](assets/compose.yml)

そのディレクトリで、次のコマンドを実行します:
```bash
podman compose up -d
```

これにより n8n がインストールされ、永続ストレージに書き込みが行われます。

ブラウザのアドレスバーに `localhost:5678` と入力して n8n を起動してください。
<!-- @os:end -->

<!-- @os:windows -->
## n8nの起動

ターミナルからn8nを起動します:

```bash
n8n start
```

<!-- @test:id=n8n-start-windows timeout=300 hidden=True -->
```powershell
$N8N_CMD = "$env:APPDATA\npm\n8n.cmd"
$p = Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$N8N_CMD`" start" -NoNewWindow -PassThru
try {
  $ok = $false
  for ($i=0; $i -lt 120; $i++) {
    # Check HTTP status code only (body may be empty)
    $code = curl.exe -s -o NUL -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz
    if ($LASTEXITCODE -eq 0 -and $code -eq "200") { $ok = $true; break }
    Start-Sleep -Seconds 1
  }
  if (-not $ok) { throw "n8n not ready on http://127.0.0.1:5678/healthz" }
  Write-Host "OK: n8n server is responding"
} finally {
  # Kill the process actually listening on 5678
  $conn = Get-NetTCPConnection -LocalPort 5678 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($conn) { Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue }
  # Also kill wrapper pid just in case
  if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-start-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

n8n start >/tmp/n8n-test.log 2>&1 &
p=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "n8n not ready on http://127.0.0.1:5678/healthz"
  exit 1
fi

echo "OK: n8n server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
n8nはローカルWebサーバーを起動します。`'o'`を押すか、ブラウザで`http://localhost:5678`を開いてエディタにアクセスしてください。
<!-- @os:end -->
> **ヒント**: n8nを使用している間は、ターミナルウィンドウを開いたままにしておいてください。閉じるとサーバーが停止する場合があります。

## Lemonadeの起動

Lemonadeは、モデルを実行しn8nと接続するローカルサーバーです。
<!-- @os:linux -->
タスクバーの Lemonade アイコンをクリックして、Lemonade GUI を開きます。ここからモデルやバックエンドを閲覧したり、プリインストール済みのモデルを読み込んだりできます。
<!-- @os:end -->

<!-- @os:windows -->
Lemonade アイコンをクリックして Lemonade GUI を開きます。トレイアイコンを右クリックしてアプリを開きます。そこから、モデルやバックエンドを追加したり、プリインストール済みのモデルをロードしたりできます。
<!-- @os:end -->
>**ヒント**: 起動すると、Lemonade GUIは http://localhost:13305 でもアクセスできます

または、ターミナルを開いて `lemonade list` を実行し、インストール済みのモデルを確認することもできます。その後、以下を実行します。
<!-- @device:halo_box -->
<!-- @os:linux -->
```bash
lemonade run gpt-oss-120b-Q4_K_M --llamacpp vulkan
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo -->
```bash
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
```bash
lemonade run gpt-oss-20b-GGUF --llamacpp vulkan
```
<!-- @device:end -->
## ワークフローのセットアップ

### ステップ1: n8n にサインアップまたはログインする

n8n を初めて開くと、アカウントの作成またはログインを求められます。

1. ブラウザで `http://localhost:5678` を開きます
2. メールアドレスで新しいローカルアカウントを作成するか、既にアカウントをお持ちの場合はログインします
3. ログインすると、n8n のダッシュボードが表示されます

> **ヒント**: アカウントからロックアウトされた場合は、`n8n user-management:reset` を試してください

### ステップ2: ワークフローをインポートする

直接インポートできる、あらかじめ用意されたワークフローを提供しています。

1. 次のワークフローファイルをダウンロードします: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. **Start from Scratch** をクリックしてワークフローエディタを開きます。または、左上の + ボタンをクリックしてから **Add workflow** をクリックします。
3. 右上のバーにある **...** メニュー(3つの点)をクリックし、**Import from file** を選択します
4. ダウンロードした `financial-news-workflow.json` ファイルを選択します
5. ワークフローがキャンバス上に表示されます
### ステップ3：ワークフローを理解する

インポートされたワークフローには、9つの接続されたノードが含まれています。

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| ノード | 目的 |
|------|---------|
| **When clicking 'Execute workflow'** | ワークフローを開始するための手動トリガー |
| **Fetch Financial News Webpage** | `https://apnews.com/business` へのHTTP GETリクエスト |
| **Delay to Ensure Page Load** | ページコンテンツが完全に読み込まれるようにするためのWaitノード |
| **Extract News Headlines & Text** | CSSセレクターを使用して見出し、編集者のピック、トップニュース、地域ニュースを抽出するHTMLノード |
| **Clean Extracted News Data** | 抽出されたすべてのデータを1つのテキストフィールドに結合するSetノード |
| **AI Financial News Summarizer** | 金融アナリストのシステムプロンプトでニュースを処理するAI Agent |
| **Lemonade Chat Model** | LLMを実行しているローカルのLemonadeサーバーに接続 |
| **Structured Output Parser** | AIの出力を構造化されたJSONとしてフォーマット |
| **Convert to File** | サマリーをダウンロード可能なファイルに変換 |

### ステップ4：Lemonadeの認証情報を設定する

ワークフローを実行する前に、ローカルのLemonadeサーバーに接続する必要があります。

1. n8nで **Lemonade Chat Model** ノードをダブルクリックします
2. **Credential to connect with** のドロップダウンメニューから **Create New Credential** を選択します
3. 下の表の値を入力し、保存をクリックします。
4. Lemonade Serverにロードしている関連モデルを選択します。

  | フィールド | 値 |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **注**：テストする前に、ターミナルで `lemonade status` を実行して、Lemonadeサーバーが動作していることを確認してください。
<!-- @device:halo_box -->
> このワークフローはGPT-OSS-120Bを使用しており、Lemonadeにあらかじめインストールされています。Lemonade Chat Modelノードの設定で、他のロード済みモデルに変更できます。
<!-- @device:end -->

### ステップ5：ワークフローをテストする

1. モデルがロードされた状態でLemonadeが動作していることを確認します
2. キャンバスの下部中央にある **Execute workflow** をクリックします
3. 各ノードが左から右へ実行される様子を確認します—完了すると緑色になります
4. **AI Financial News Summarizer** ノードをダブルクリックして、下部ペインに生成されたサマリーを表示します。
5. **Convert to File** ノードをダブルクリックして、下部ペインで対応するテキストファイルをダウンロードします。

## AI Agentを理解する

AI Financial News Summarizerは、金融分析のために設計されたシステムプロンプトを使用しています。

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

このエージェントは、クリーンアップされたニュースデータを受け取り、市場センチメントを含む構造化されたサマリーを出力します。

### ワークフローを保存する

上部のワークフロー名をクリックして、必要に応じて名前を変更します。ワークフローは作業中に自動保存されます。

## 次のステップ

- **自動化のスケジュール設定**：手動トリガーを **Schedule Trigger** に置き換えて、毎日実行するようにします
- **通知の送信**：**Discord**、**Slack**、または **Email** ノードを追加して、サマリーを受信します
- **異なるモデルを試す**：Lemonade Chat Modelノードのモデルを変更して、さまざまなLLMを試します
- **抽出のカスタマイズ**：HTML Extractノードの CSSセレクターを変更して、異なるニュースセクションを対象にします
- **異なるバックエンドを試す**：n8nは[Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model)、LM Studio、その他のローカルLLMバックエンドもサポートしています

### n8nテンプレートを探索する

n8nには数百のプリビルドワークフローテンプレートがあります。公式テンプレートライブラリを以下で閲覧できます。

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

「AI」、「LLM」、または「automation」を検索して、インポートしてカスタマイズできるワークフローを見つけてください。

詳細については、[n8n Documentation](https://docs.n8n.io/)をご確認ください。

<!-- @os:linux -->
<!-- @test:id=lemonade-unload-linux timeout=60 hidden=True -->
```bash
# CI cleanup: unload the model so the GPU pool is free
lemonade unload || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-unload-windows timeout=60 hidden=True -->
```powershell
# CI cleanup: unload the model so the GPU pool is free
lemonade unload
exit 0
```
<!-- @test:end -->
<!-- @os:end -->