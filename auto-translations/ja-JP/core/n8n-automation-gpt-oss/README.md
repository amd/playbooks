<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> このプレイブックは、GitHub でレンダリングできない特殊なタグを使用しています。このコンテンツを正しくプレビューするには、[amd.com/playbooks](https://amd.com/playbooks) をご覧ください。
<!-- @github-only:end -->

## 概要

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> このプレイブックには、最低 **32GB** のシステムメモリが必要です。
<!-- @device:end -->

n8n は、ビジュアルなノードベースのエディターを使用してアプリやサービスを接続できるワークフロー自動化プラットフォームです。

このプレイブックでは、AP News のビジネスセクションをスクレイピングし、主要な見出しを抽出して、システム上でローカルに動作する LLM を使用して投資家向けのサマリーを生成する、AI を活用した金融ニュースサマライザーのセットアップ方法を説明します。

## 学習内容

- n8n のインストールと起動方法
- 事前構築済みワークフローのインポートと設定
- n8n ネイティブ統合を使用した Lemonade への接続
- ワークフローノードとデータフローの理解

## Lemonade とは？

[Lemonade](https://lemonade-server.ai) は、AMD ハードウェア向けに構築されたローカル LLM サービングプラットフォームです。OpenAI 互換の API を提供し、完全にお使いのマシン上で動作します。データがデバイスの外に出ることはありません。

このプレイブックでは、Lemonade を使用してローカル LLM を提供し、n8n が AI を活用したタスクのために接続します。

n8n には **ネイティブの Lemonade ノード**（`Lemonade Chat Model`）が含まれており、ファーストクラスの統合を提供します。手動設定は不要です。これにより、ローカル LLM を自動化ワークフローに接続することが簡単になります。

## メモリ設定の構成

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアアップデートの確認

<!-- @require:software-update -->
<!-- @device:end -->

## ソフトウェア前提条件のインストール
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

## n8n のインストール
<!-- @os:windows -->
npm を使用して n8n をグローバルにインストールします。

> **注意**: npm の警告が表示される場合があります。これは想定内の動作です。

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
> **ヒント**: Windows ユーザーは、一部の PowerShell コマンドを実行する前に、PowerShell 実行ポリシーを変更する必要がある場合があります（例：
> RemoteSigned または Unrestricted に設定する）。
<!-- @os:end -->


<!-- @os:windows -->
> **PATH の問題**: `n8n --version` で「コマンドが見つかりません」と表示される場合は、npm のグローバル bin ディレクトリがユーザーの `PATH` に含まれていることを確認してください。通常のインストールパスは `C:\Users\<username>\AppData\Roaming\npm` です。
> これをユーザーパスに追加し（システム環境変数の編集 > 環境変数 > ユーザーパスの編集）、ターミナルを再起動してください。

<!-- @os:end -->

<!-- @os:linux -->
Podman サービスを使用して n8n インストールをコンテナ化します。

以下のファイルを任意のディレクトリにダウンロードしてください: [compose.yml](assets/compose.yml)

そのディレクトリで、次のコマンドを実行します:
```bash
podman compose up -d
```

これにより n8n がインストールされ、永続ストレージに書き込まれます。

ブラウザのアドレスバーに `localhost:5678` と入力して n8n を起動します。
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
n8n はローカル Web サーバーを起動します。`'o'` を押すか、ブラウザで `http://localhost:5678` を開いてエディターにアクセスしてください。
<!-- @os:end -->


> **ヒント**: n8n を使用している間はターミナルウィンドウを開いたままにしてください。閉じるとサーバーが停止する場合があります。

## Lemonade の起動

Lemonade は、モデルを実行して n8n に接続するローカルサーバーです。

<!-- @os:linux -->
タスクバーの Lemonade アイコンをクリックして Lemonade GUI を開きます。ここからモデル、バックエンドを参照し、事前インストール済みのモデルを読み込むことができます。
<!-- @os:end -->

<!-- @os:windows -->
Lemonade アイコンをクリックして Lemonade GUI を開きます。トレイアイコンを右クリックしてアプリを開きます。その後、モデルやバックエンドを追加し、事前インストール済みのモデルを読み込むことができます。
<!-- @os:end -->

>**ヒント**: 起動後、Lemonade GUI には http://localhost:13305 からもアクセスできます。

または、ターミナルを開いて `lemonade list` を実行してインストール済みのモデルを確認することもできます。その後、次を実行します:

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

### ステップ 1: n8n にサインアップまたはログイン

n8n を初めて開くと、アカウントの作成またはログインを求められます:

1. ブラウザで `http://localhost:5678` を開く
2. メールアドレスで新しいローカルアカウントを作成するか、既にアカウントがある場合はログインする
3. ログイン後、n8n ダッシュボードが表示されます

> **ヒント**: アカウントからロックアウトされた場合は、`n8n user-management:reset` を試してください。

### ステップ 2: ワークフローのインポート

直接インポートできる事前構築済みのワークフローを提供しています:

1. 次のワークフローファイルをダウンロードする: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. **Start from Scratch** をクリックしてワークフローエディターを開く。または、左上の + ボタンをクリックし、**Add workflow** をクリックする。
3. 右上バーの **...** メニュー（三点ドット）をクリックし、**Import from file** を選択する
4. ダウンロードした `financial-news-workflow.json` ファイルを選択する
5. ワークフローがキャンバスに表示されます


### ステップ 3: ワークフローの理解

インポートされたワークフローには、接続された 9 つのノードが含まれています:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| ノード | 目的 |
|------|---------|
| **When clicking 'Execute workflow'** | ワークフローを開始する手動トリガー |
| **Fetch Financial News Webpage** | `https://apnews.com/business` への HTTP GET リクエスト |
| **Delay to Ensure Page Load** | ページコンテンツが完全に読み込まれるまで待機するウェイトノード |
| **Extract News Headlines & Text** | CSS セレクターを使用して見出し、編集者のおすすめ、トップストーリー、地域ニュースを抽出する HTML ノード |
| **Clean Extracted News Data** | 抽出されたすべてのデータを単一のテキストフィールドに結合する Set ノード |
| **AI Financial News Summarizer** | 金融アナリストのシステムプロンプトでニュースを処理する AI エージェント |
| **Lemonade Chat Model** | LLM を実行しているローカルの Lemonade サーバーに接続する |
| **Structured Output Parser** | AI の出力を構造化された JSON としてフォーマットする |
| **Convert to File** | サマリーをダウンロード可能なファイルに変換する |

### ステップ 4: Lemonade 認証情報の設定

ワークフローを実行する前に、ローカルの Lemonade サーバーに接続する必要があります:

1. n8n で **Lemonade Chat Model** ノードをダブルクリックする
2. ドロップダウンメニュー **Credential to connect with** で **Create New Credential** を選択する
3. 以下の表の値を入力し、保存をクリックする
4. Lemonade Server に読み込んでいる関連モデルを選択する

  | フィールド | 値 |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **注意**: テストを実行する前に、ターミナルで `lemonade status` を実行して Lemonade サーバーが動作していることを確認してください。
<!-- @device:halo_box -->
> このワークフローは GPT-OSS-120B を使用しており、Lemonade に事前インストールされています。Lemonade Chat Model ノードの設定で、他の読み込み済みモデルに変更することができます。
<!-- @device:end -->

### ステップ 5: ワークフローのテスト

1. Lemonade がモデルを読み込んだ状態で実行されていることを確認する
2. キャンバス下部中央の **Execute workflow** をクリックする
3. 各ノードが左から右へ実行されるのを確認する—完了すると緑色に変わります
4. **AI Financial News Summarizer** ノードをダブルクリックして、下部ペインで生成されたサマリーを確認する
5. **Convert to File** ノードをダブルクリックして、下部ペインで対応するテキストファイルをダウンロードする

## AI エージェントの理解

AI Financial News Summarizer は、金融分析向けに設計されたシステムプロンプトを使用します:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

エージェントはクリーニングされたニュースデータを受け取り、市場センチメントを含む構造化されたサマリーを出力します。

### ワークフローの保存

上部のワークフロー名をクリックして、必要に応じて名前を変更してください。ワークフローは作業中に自動保存されます。

## 次のステップ

- **スケジュール自動化**: 手動トリガーを **Schedule Trigger** に置き換えて毎日実行する
- **通知の送信**: **Discord**、**Slack**、または **Email** ノードを追加してサマリーを受け取る
- **異なるモデルを試す**: Lemonade Chat Model ノードのモデルを変更して、さまざまな LLM を試す
- **抽出のカスタマイズ**: HTML Extract ノードの CSS セレクターを変更して、異なるニュースセクションをターゲットにする
- **異なるバックエンドを試す**: n8n は [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model)、LM Studio、その他のローカル LLM バックエンドもサポートしています

### n8n テンプレートの探索

n8n には数百の事前構築済みワークフローテンプレートがあります。公式テンプレートライブラリは以下で参照できます:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

「AI」、「LLM」、または「automation」で検索して、インポートしてカスタマイズできるワークフローを見つけてください。

詳細については、[n8n ドキュメント](https://docs.n8n.io/)をご覧ください。