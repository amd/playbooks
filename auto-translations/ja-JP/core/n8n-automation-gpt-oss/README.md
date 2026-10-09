<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機械翻訳。** このページは英語から自動的に翻訳されたものであり、人による確認は行われていません。誤りが含まれている場合や、特定の手順、コマンド、ダウンロード、製品の提供状況、その他のコンテンツが言語や地域によって異なる場合があります。内容に矛盾または相違がある場合は、playbookの原文である英語版が優先されるものとします。
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## 概要

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> このプレイブックには最低 **32GB** のシステムメモリが必要です。
<!-- @device:end -->

n8n は、ビジュアルなノードベースのエディターを使用してアプリやサービスを連携させることができるワークフロー自動化プラットフォームです。

このプレイブックでは、ニュース RSS フィードから最新のビジネスヘッドラインを取得し、システム上で動作するローカル LLM を使用して投資家向けの要約を生成する、AI 搭載の金融ニュース要約ツールの構築方法を学びます。

## 学べること

- n8n のインストールと起動方法
- 事前構築済みワークフローのインポートと設定
- n8n のネイティブ統合を使用した Lemonade への接続
- ワークフローのノードとデータフローの理解

## Lemonade とは?

[Lemonade](https://lemonade-server.ai) は、AMD ハードウェア向けに構築されたローカル LLM サービングプラットフォームです。OpenAI 互換の API を提供し、すべてお使いのマシン上で完結して動作します。データがデバイスの外に出ることはありません。

このプレイブックでは、Lemonade を使用してローカル LLM をサーブし、n8n がそれに接続して AI を活用したタスクを実行します。

n8n には **ネイティブの Lemonade ノード**(`Lemonade Chat Model`)が含まれており、ファーストクラスの統合機能を提供します。手動設定は不要です。これにより、ローカル LLM を自動化ワークフローに簡単に接続できます。

<!-- @device:halo_box,halo,stx,krk -->
## メモリ構成の設定

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## ソフトウェアアップデートの確認

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェア前提条件のインストール
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:n8n,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- Linux runs n8n as a Podman container (see compose.yml below), so Node.js and a host n8n install are not required; podman is the only extra prerequisite. -->
<!-- @require:lemonade,podman -->
<!-- @prereq:podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @prereq:lemonade-models-gpt-oss-120b -->
<!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @prereq:lemonade-models-gpt-oss-20b -->
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

<!-- @os:windows -->
<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->
<!-- @os:end -->

## n8n のインストール
<!-- @os:windows -->
npm を使用して n8n をグローバルにインストールします。

> **注**: いくつかの npm 警告が表示される場合がありますが、これは想定内です。

```bash
npm install -g n8n
```

<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **ヒント**: Windows ユーザーは、一部の PowerShell コマンドを実行する前に PowerShell 実行ポリシーを変更する必要がある場合があります(例: RemoteSigned または Unrestricted に設定)。
<!-- @os:end -->


<!-- @os:windows -->
> **PATH の問題**: `n8n --version` でコマンドが見つからないと表示される場合は、npm のグローバル bin ディレクトリがユーザーの `PATH` に含まれていることを確認してください。通常のインストールパスは `C:\Users\<username>\AppData\Roaming\npm` です。
> これをユーザーパスに追加し(システム環境変数の編集 > 環境変数 > ユーザーパスの編集)、ターミナルを再読み込みしてください。

<!-- @os:end -->

<!-- @os:linux -->
次に、Podman サービスを使用して n8n インストールをコンテナ化します。

以下のファイルを任意のディレクトリにダウンロードしてください: [compose.yml](assets/compose.yml)

そのディレクトリで、次のコマンドを実行します:
```bash
podman compose up -d
```

これにより n8n がインストールされ、永続ストレージに書き込まれます。

ブラウザのアドレスバーに `localhost:5678` を入力して n8n を起動します。
<!-- @os:end -->

<!-- @os:windows -->
## n8n の起動

ターミナルから n8n を起動します:

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

export PODMAN_COMPOSE_PROVIDER="$(command -v podman-compose)"
cleanup() {
  podman compose -f compose.yml down >/dev/null 2>&1 || true
}
trap cleanup EXIT

podman rm -f n8n >/dev/null 2>&1 || true
podman compose -f compose.yml up -d

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
  podman ps -a || true
  podman logs n8n 2>&1 | tail -30 || true
  exit 1
fi

echo "OK: n8n server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
n8n はローカル Web サーバーを起動します。`'o'` を押すか、ブラウザで `http://localhost:5678` を開いてエディターにアクセスしてください。
<!-- @os:end -->


> **ヒント**: n8n を使用している間は、ターミナルウィンドウを開いたままにしてください。閉じるとサーバーが停止する可能性があります。

## Lemonade の起動

Lemonade は、モデルを実行して n8n に接続するローカルサーバーです。

<!-- @os:linux -->
タスクバーの Lemonade アイコンをクリックして Lemonade GUI を開きます。ここからモデルやバックエンドを閲覧したり、事前インストール済みのモデルを読み込んだりできます。
<!-- @os:end -->

<!-- @os:windows -->
Lemonade アイコンをクリックして Lemonade GUI を開きます。トレイアイコンを右クリックしてアプリを開いてください。その後、モデルやバックエンドを追加し、事前インストール済みのモデルを読み込むことができます。
<!-- @os:end -->

>**ヒント**: 実行中は、Lemonade GUI に http://localhost:13305 からもアクセスできます。

または、ターミナルを開いて `lemonade list` を実行し、インストール済みのモデルを確認することもできます。その後、次を実行します:

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


## ワークフローの設定

### ステップ 1: n8n へのサインアップまたはログイン

n8n を初めて開くと、アカウントの作成またはログインを求められます:

1. ブラウザで `http://localhost:5678` を開きます
2. メールアドレスで新しいローカルアカウントを作成するか、既にアカウントをお持ちの場合はログインします
3. ログインすると、n8n ダッシュボードが表示されます

> **ヒント**: アカウントからロックアウトされた場合は、`n8n user-management:reset` を試してください

### ステップ 2: ワークフローのインポート

直接インポートできる事前構築済みのワークフローを用意しています:

1. 次のワークフローファイルをダウンロードします: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. **Start from Scratch** をクリックしてワークフローエディターを開きます。あるいは、左上の + ボタンをクリックしてから **Add workflow** をクリックします。
3. 右上バーの **...** メニュー(3 つの点)をクリックし、**Import from file** を選択します
4. ダウンロードした `financial-news-workflow.json` ファイルを選択します
5. ワークフローがキャンバス上に表示されます
### Step 3: ワークフローを理解する

インポートしたワークフローには、8つの接続されたノードが含まれています:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| ノード | 役割 |
|------|---------|
| **When clicking 'Execute workflow'** | ワークフローを開始する手動トリガー |
| **Fetch Financial News Feed** | RSSフィードから最新のビジネスヘッドラインを取得するRSS Readノード(デフォルトではNYT Businessフィードを使用し、APIキーは不要) |
| **Aggregate Headlines** | 各フィードアイテムからヘッドラインのタイトルと要約を収集し、1つのリストにまとめるAggregateノード |
| **Clean Extracted News Data** | すべてのヘッドラインを1つのテキストフィールドに結合するSetノード |
| **AI Financial News Summarizer** | 金融アナリストのシステムプロンプトでニュースを処理するAI Agent |
| **Lemonade Chat Model** | LLMを実行しているローカルのLemonadeサーバーに接続 |
| **Structured Output Parser** | AIの出力を構造化されたJSONとしてフォーマット |
| **Convert to File** | 要約をダウンロード可能なファイルに変換 |

> **ヒント**: 別のニュースソースを使用するには、**Fetch Financial News Feed**ノードをダブルクリックし、URLをお好みのビジネスまたはマーケット系RSSフィードに置き換えてください。

### Step 4: Lemonadeの認証情報を設定する

ワークフローを実行する前に、ローカルのLemonadeサーバーに接続する必要があります:

1. n8nで**Lemonade Chat Model**ノードをダブルクリックします
2. ドロップダウンメニュー**Credential to connect with**から**Create New Credential**を選択します
3. 下の表の値を入力し、保存をクリックします。
4. Lemonade Serverにロードしている該当するモデルを選択します。

  | フィールド | 値 |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **注**: テストする前に、ターミナルで`lemonade status`を実行し、Lemonadeサーバーが稼働していることを確認してください。
<!-- @device:halo_box -->
> このワークフローはGPT-OSS-120Bを使用しており、Lemonadeにプリインストールされています。Lemonade Chat Modelノードの設定で、ロード済みの他のモデルに変更することもできます。
<!-- @device:end -->

### Step 5: ワークフローをテストする

1. モデルがロードされた状態でLemonadeが稼働していることを確認します
2. キャンバス下部中央の**Execute workflow**をクリックします
3. 各ノードが左から右へ実行される様子を確認します—完了すると緑色に変わります
4. **AI Financial News Summarizer**ノードをダブルクリックすると、下部ペインに生成された要約が表示されます。
5. **Convert to File**ノードをダブルクリックすると、下部ペインから対応するテキストファイルをダウンロードできます。

## AI Agentについて

AI Financial News Summarizerは、金融分析用に設計されたシステムプロンプトを使用します:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

エージェントはクリーンアップされたニュースデータを受け取り、市場センチメントを含む構造化された要約を出力します。

### ワークフローを保存する

上部にあるワークフロー名をクリックして、必要に応じて名前を変更します。ワークフローは作業中に自動保存されます。

## 次のステップ

- **自動化をスケジュールする**: Manual Triggerを**Schedule Trigger**に置き換えて、毎日実行するようにします
- **通知を送信する**: **Discord**、**Slack**、または**Email**ノードを追加して要約を受け取ります
- **さまざまなモデルを試す**: Lemonade Chat Modelノードのモデルを変更して、さまざまなLLMを試してみます
- **ニュースソースを変更する**: **Fetch Financial News Feed**ノードを別のRSSフィードに設定し、他のセクションや出版物をフォローします
- **さまざまなバックエンドを試す**: n8nは[Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model)、LM Studio、その他のローカルLLMバックエンドにも対応しています

### n8nテンプレートを見る

n8nには数百種類の事前構築済みワークフローテンプレートがあります。公式テンプレートライブラリは以下から閲覧できます:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

「AI」「LLM」「automation」などで検索すると、インポートしてカスタマイズできるワークフローが見つかります。

詳細については、[n8n Documentation](https://docs.n8n.io/)をご覧ください。

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