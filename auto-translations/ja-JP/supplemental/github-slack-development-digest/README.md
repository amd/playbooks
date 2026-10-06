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
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## 概要

開発者は、ラベル付けされたプルリクエストのレビュー、GitHub コメントへの返信、新規 issue のトリアージ、Slack スレッドをスタンドアップノートやインシデント対応へと変換する作業、リリースやリサーチの動向の追跡といった、小さく繰り返されるループに多くの時間を費やしています。
どのループも見慣れたものですが、それでも判断が必要です。適切なコンテキストを集め、何が重要かを見極め、チームが日常的に使っている場所に明確な更新を投稿しなければなりません。

[OpenHands automations](https://docs.openhands.dev/openhands/usage/automations/overview) は、こうしたループをスケジュール実行またはイベントトリガー型のエージェント会話に変換します。これは、AI ソフトウェアエージェントがコンテキストを読み取り、ツールを呼び出し、更新を生成できる実行単位です。
OpenHands extensions カタログに含まれる共有自動化テンプレートは、GitHub プルリクエストのレビュー、リポジトリの監視、Linear issue のトリアージ、インシデントの振り返り、Slack スタンドアップダイジェスト、リサーチブリーフといった用途向けに、この共通パターンに従っています。自動化が起動し、GitHub や Slack などの設定済みインテグレーションを使ってコンテキストを取得し、大規模言語モデル (LLM) でそのコンテキストを推論し、結果を書き戻します。

[Agent Canvas](https://github.com/OpenHands/agent-canvas) は、こうした自動化を構築・テストするためのローカルコントロールプレーンです。
このプレイブックでは、エージェント会話を実行するバックエンドプロセスである OpenHands Agent Server を実行し、エージェントを GitHub や Slack などの外部サービスに接続します。

ワークフローを AMD システム上に留めるため、エージェントは Lemonade Server によって提供されるローカルモデルと通信します。
Lemonade はそのモデルを OpenAI 互換の API として公開するため、Agent Canvas はそれをリモートの OpenAI 形式のエンドポイントのように設定でき、一方でモデル、プロンプト、ワークフローのコンテキストはすべてローカルに保たれます。

このプレイブックでは、具体的な自動化を 1 つ構築します。スケジュール実行される GitHub から Slack への開発ダイジェストです。
これは、GitHub を使って最近のリポジトリの活動を調べ、Slack でダイジェストを投稿し、Agent Canvas API 呼び出しで自動化を設定・テストし、Lemonade を使ってローカルで LLM を実行します。

![GitHub MCP、OpenHands automation、Lemonade Server、Slack MCP を示すアーキテクチャ図](assets/00-architecture-overview.png)

## このプレイブックで学べること

- Lemonade Server を起動し、ローカルモデルがチャットリクエストに応答することを確認する方法
- Agent Canvas を起動し、その Agent Server をローカル LLM に向ける方法
- Agent Server API を通じて GitHub と Slack の Model Context Protocol (MCP) サーバーをインストールする方法
- スケジュール実行される OpenHands automation を作成し、開発ダイジェストを Slack に投稿するようディスパッチする方法
- よく発生するローカルモデルおよび自動化の障害をトラブルシューティングする方法

## 基本概念

| 概念 | 説明 | このプレイブックでの位置付け |
| --- | --- | --- |
| Lemonade Server | AMD ハードウェア向けに構築された、OpenAI 互換 API を公開するローカル LLM 提供プラットフォーム。データはマシンの外に出ません。 | エージェントを動かすモデルを実行します。 |
| OpenHands Agent Server | OpenHands のエージェント会話を実行するバックエンドプロセス。 | エージェント、その LLM プロファイル、その MCP サーバーをホストします。 |
| Agent Canvas | Agent Server と、エージェントの実行状況を確認する UI を実行する、OpenHands のローカルコントロールプレーン。 | バックエンドを起動し、呼び出す API を提供します。 |
| MCP server | GitHub や Slack などの外部サービス向けのツールをエージェントに提供する Model Context Protocol サーバー。 | エージェントが GitHub を読み取り、Slack へ書き込めるようにします。 |
| OpenHands automation | コンテキストを取得し、それを推論し、どこかへ結果を書き込む、スケジュール実行またはイベントトリガー型のエージェント会話。 | ここで構築する GitHub から Slack へのダイジェストです。 |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> コーディングエージェントのワークフローは、より大きなモデルとコンテキストウィンドウの恩恵を受けます。
> システムメモリは少なくとも 32 GB を使用し、より大きな GGUF モデルには 64 GB 以上を推奨します。
<!-- @device:end -->

## メモリ設定の構成

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアアップデートの確認

<!-- @require:software-update -->
<!-- @device:end -->

## 前提条件

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

以下が必要です。

- 標準の [Lemonade installation guide](https://lemonade-server.ai/docs/guide/install/) に従ってインストールされた Lemonade Server。

<!-- @os:linux -->
- 公開されている Agent Canvas CLI をインストールし、`npx` で MCP サーバーを実行するために使用する Node.js 22.12 以降と `npm`。
- Agent Canvas が Agent Server 環境を構築するために使用する Python パッケージマネージャーである `uv`。まだインストールしていない場合は、[uv installation guide](https://docs.astral.sh/uv/getting-started/installation/) からインストールしてください。
- スキーマ駆動のエージェント設定、`LLMSummarizingCondenserSettings.max_tokens`、LLM の `custom_tokenizer` サポートを備えた、最近公開された `@openhands/agent-canvas` パッケージ。
- Agent Server 環境内で利用可能な Python の `transformers` パッケージ。`custom_tokenizer` が設定されている場合、チャットテンプレートのトークンカウントに必要です。
<!-- @os:end -->

<!-- @os:windows -->
- インストール済みで実行中の [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/)。Windows では、Agent Canvas スタックは Node.js、`uv`、`transformers`、`@openhands/agent-canvas` パッケージをバンドルした公開 Docker イメージから実行されるため、これらをホストにインストールする必要はありません。
<!-- @os:end -->

- 要約対象のリポジトリへの読み取りアクセス権を持つ GitHub トークン。
- `chat:write` とチャンネル読み取りアクセス権を持つ Slack ボットトークン (`xoxb-...`)。
- Slack チーム ID (`T...`)。
- ダイジェストを投稿する Slack チャンネル ID (`C...`)。

自動化をテストする前に、対象チャンネルに Slack アプリを招待してください。
## このプレイブックで使用する変数

<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @os:linux -->
```bash
export LEMONADE_BASE_URL="http://127.0.0.1:13305/api/v1"
export LEMONADE_MODEL="Qwen3.6-35B-A3B-GGUF"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
$env:LEMONADE_BASE_URL = "http://127.0.0.1:13305/api/v1"
$env:LEMONADE_MODEL = "Qwen3.6-35B-A3B-GGUF"
```
<!-- @os:end -->

これら2つの変数は、以下の検証コマンドで使用されます。
モデル、トークナイザー、その他のLLM設定は、後続の手順でAgent Canvas UIに直接入力するため、必要な箇所ではそれらの実際の値をインラインで示しています。

以下の値は、後続の手順でAgent Canvas UIに入力されます。
コピーして使えるように、ここで設定しておきます。

<!-- @os:linux -->
```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
$env:GITHUB_REPO_FILTER = "your-org/your-repo"
$env:SLACK_DIGEST_CHANNEL = "C0123456789"
$env:DIGEST_TIMEZONE = "America/New_York"
```
<!-- @os:end -->

`GITHUB_REPO_FILTER` には明示的な `owner/repo` の値を使用してください。
組織全体を対象とする広範なワイルドカードを使うと、ローカルモデルにとってMCPコンテキストが大きくなりすぎる場合があります。

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Lemonade Serverを起動する

Lemonade CLIからモデルを起動します。

<!-- @os:linux -->
```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "$env:LEMONADE_MODEL"
```
<!-- @os:end -->

> **お使いのハードウェアに合ったモデルを選んでください。** `Qwen3.6-35B-A3B-GGUF`(約20 GB)はこのワークフローに適した強力なモデルですが、大きなメモリプールが必要です。
> お使いのデバイスのメモリやGPU VRAMに限りがある場合は、Lemonadeモデルライブラリからより小さいGGUFモデルを選び、そのモデルID(および対応するトークナイザー)をこのプレイブック全体で使用してください。

> **注意:** 最初の `lemonade run` では、モデルがまだ存在しない場合にダウンロードが行われるため、モデルのサイズや接続状況によっては時間がかかることがあります。

Lemonadeは、以下の場所にOpenAI互換のAPIを公開します。

```text
http://127.0.0.1:13305/api/v1
```

オプション: Agent Canvasや自動化ランナーが同じマシン上にない場合は、Lemonadeエンドポイントを安全なトンネル経由で公開し、そのHTTPS URLをLLMのベースURLとして使用してください。
[ngrok](https://ngrok.com/) は、安全なHTTPS URLを介してローカルポートをインターネットに公開します。利用には無料のngrokアカウントが必要で、`YOUR_NGROK_DOMAIN.ngrok-free.dev` の部分は自分専用に予約したドメインに置き換えてください。

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. ローカルモデルを検証する

Lemonadeが選択したモデルを正しく提供できることを確認します。

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

次に、簡単なチャットリクエストを送信します。

```bash
curl -sS "${LEMONADE_BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"${LEMONADE_MODEL}"'",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
curl.exe -s "$env:LEMONADE_BASE_URL/models"
```

次に、簡単なチャットリクエストを送信します。

```powershell
$body = @{
  model    = "$env:LEMONADE_MODEL"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens  = 64
} | ConvertTo-Json -Depth 5
curl.exe -sS "$env:LEMONADE_BASE_URL/chat/completions" -H "Content-Type: application/json" -d $body
```
<!-- @os:end -->

これが `choices` 配列を返せば、LemonadeはAgent Canvasから利用できる状態です。

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
  "max_tokens": 64
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
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$modelsJson = $null
for ($i = 0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}

if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1

if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

$body = @{
  model    = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens  = 64
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "digest-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->
<!-- @os:end -->

## 3. Agent Canvasを起動する

<!-- @os:linux -->
公開されているAgent Canvasパッケージをインストールし、スタック全体を起動します。

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

グローバルなnpmインストールが権限エラーで失敗する場合は、下記のnpm権限のトラブルシューティング項目を参照してください。

デフォルトでは、Agent Canvasは `http://localhost:8000` で起動します。
ブラウザでそのURLを開いてください。
このポート番号自体に特別な意味はありません。8000がすでに使用されている場合は、`--port`(または `-p`)で任意の空きポートを指定できます。
デフォルトのローカルバックエンドは、ホーム画面で正常(healthy)と表示されるはずです。

> **注意:** 初回起動時にはAgent Serverの `uv` 管理によるPython環境が構築されるため、バックエンドが正常と報告されるまでに数分かかることがあります。

`agent-canvas` コマンドは、エージェントサーバー、自動化バックエンド、Webフロントエンドをまとめて起動します。
OpenHandsをローカルで実行するには、このコマンド1つだけで十分です。
このプレイブックの残りの部分では、ブラウザ上のAgent Canvas UIを通じてすべてを設定していきます。
<!-- @os:end -->

<!-- @os:windows -->
Windowsでは、Docker Desktopを使って公開されているAgent Canvasコンテナイメージを実行します。
このイメージにはAgent Server、自動化バックエンド、Webフロントエンドがすべて含まれているため、ホスト側にNode.js、`uv`、CLIをインストールする必要はありません。

まず、コンテナがマウントする設定用フォルダとワークスペース用フォルダを作成します。

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

公開されているイメージをプル(pull)します(サイズは約6 GB。公開イメージのためログインは不要です)。

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

続いて、スタックを起動します。

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

ブラウザで `http://localhost:8000/canvas` を開いてください。
ポート8000がすでに使用されている場合は、別のホストポートにマッピングします(例: `-p 8080:8000`)。その場合は代わりに `http://localhost:8080/canvas` を開いてください。

> **注意:** 初回起動時には、コンテナ内でAgent Server環境が構築されるため、バックエンドが正常と報告されるまでに数分かかることがあります。

`.openhands` マウントは、コンテナを再起動してもLLMプロファイル、MCPサーバー、自動化設定を保持します。
このプレイブックの残りの部分では、`http://localhost:8000/canvas` のブラウザ上のAgent Canvas UIを通じてすべてを設定していきます。
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=uv-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->

<!-- @test:id=agent-canvas-version timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
# Prefer --version; fall back to --help if this build has no --version flag.
agent-canvas --version || agent-canvas --help
echo "OK: agent-canvas CLI is on PATH"
```
<!-- @test:end -->

<!-- @test:id=agent-canvas-start timeout=1200 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
log="/tmp/agent-canvas-test.log"
p=""
cleanup() {
  set +e
  for port in 8000 18000 18001 3001; do
    pid="$(ss -ltnp 2>/dev/null | grep ":$port " | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2)"
    [ -n "$pid" ] && kill "$pid" 2>/dev/null
  done
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null
    sleep 2
    kill -9 "$p" 2>/dev/null
  fi
}
# Preserve the real exit code; cleanup must never flip a pass to a fail (or vice versa).
trap 'rc=$?; cleanup; exit $rc' EXIT

# First launch builds the agent server's uv-managed Python env, so allow a generous startup window.
agent-canvas >"$log" 2>&1 &
p=$!

# Probe the agent-server backend health (18000/server_info), NOT just the 8000 ingress root:
# the ingress serves the static frontend and returns 200 for / even when the agent-server is down.
ok=false
for i in $(seq 1 300); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18000/server_info || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  if ! kill -0 "$p" 2>/dev/null; then
    echo "agent-canvas process exited before it finished starting"
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "agent-server not ready on http://127.0.0.1:18000/server_info"
  cat "$log" || true
  exit 1
fi

echo "OK: agent-canvas agent-server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=agent-canvas-docker-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$image    = "ghcr.io/openhands/agent-canvas:1.14.0"
$name     = "digest-agent-canvas-ci"
$hostPort = 18080

# Pull the image if the runner doesn't already have it. The published image is
# public, so no login is needed. A non-interactive session can trip over a
# configured Docker credential helper (ghcr is unauthenticated here), so pull
# with an isolated, empty Docker config that has no credsStore/credHelpers.
# TODO: remove this self-provisioning once the runners ship the image by default.
$imgId = docker images -q $image
if (-not $imgId) {
  Write-Host "Image $image not present; pulling..."
  $dockerCfg = Join-Path $env:TEMP "digest-docker-cfg"
  New-Item -ItemType Directory -Force -Path $dockerCfg | Out-Null
  '{}' | Set-Content -Path (Join-Path $dockerCfg "config.json") -Encoding ascii
  docker --config $dockerCfg pull $image
  if ($LASTEXITCODE -ne 0) { throw "docker pull failed for $image" }
}
Write-Host "OK: $image is present"

if (docker ps -aq -f "name=$name") { docker rm -f $name | Out-Null }

try {
  docker run -d --name $name -p "${hostPort}:8000" $image | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "docker run failed for $image" }

  # Probe the agent-server backend health through the container proxy
  # (/server_info -> agent-server on 18000 inside the container), not just the
  # /canvas static UI, which can return 200 while the backend is still down.
  $ok = $false
  for ($i = 0; $i -lt 300; $i++) {
    $canvas = try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:${hostPort}/canvas").StatusCode } catch { 0 }
    $info   = try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:${hostPort}/server_info").StatusCode } catch { 0 }
    if ($canvas -eq 200 -and $info -eq 200) { $ok = $true; break }
    $state = docker inspect -f "{{.State.Status}}" $name 2>$null
    if ($state -ne "running") { throw "Container $name exited before it finished starting" }
    Start-Sleep -Seconds 2
  }

  if (-not $ok) {
    docker logs --tail 40 $name
    throw "agent-canvas backend not healthy on http://localhost:${hostPort}/server_info"
  }
  Write-Host "OK: agent-canvas Docker stack is healthy (/canvas and /server_info return 200)"
}
finally {
  if (docker ps -aq -f "name=$name") { docker rm -f $name | Out-Null }
}
```
<!-- @test:end -->
<!-- @os:end -->
## 4. UI でローカル LLM を設定する

初回起動時、Agent Canvas はオンボーディングフローを開きます。
そのフローで次の操作を行います。

1. エージェントとして **OpenHands** を選択したままにし、**Next** をクリックします。
2. **Set up your LLM** で **Advanced** を選択します。
3. **Authentication** は **API key** のままにします。
4. **Custom Model** に `openai/Qwen3.6-35B-A3B-GGUF` を設定します。
5. **Base URL** に `http://127.0.0.1:13305/api/v1` を設定します。
6. **API Key** には、`lemonade-local` のような空でないプレースホルダーを入力します。Lemonade は実際のキーを必要としませんが、OpenHands クライアント側では何らかの値を送信する必要があります。

<!-- @os:windows -->
> **Windows（Docker）:** Agent Server はコンテナ内で動作するため、**Base URL** には `http://127.0.0.1:13305/api/v1` の代わりに `http://host.docker.internal:13305/api/v1` を設定してください。
> コンテナ内部から見ると、`127.0.0.1` はコンテナ自身を指します。`host.docker.internal` は Windows ホスト上で動作している Lemonade に到達するためのもので、このホスト名は Docker Desktop によって自動的に提供されます。
<!-- @os:end -->

接続用の各フィールドは次のようになるはずです。
API キーのフィールドは UI によってマスクされます。

![Lemonade モデルとローカルのベース URL が設定された、Agent Canvas 初回利用時の LLM Advanced 設定](assets/01-llm-advanced-settings.png)

次に **All** を選択し、ローカルモデル用の追加フィールドを設定します。

1. **Custom Tokenizer** までスクロールし、`Qwen/Qwen3.6-35B-A3B` を設定します。
2. **LiteLLM Extra Body** までスクロールし、`{"enable_thinking": true}` を設定します。
3. **Next** をクリックします。

![Qwen のカスタムトークナイザーが設定された、Agent Canvas 初回利用時の LLM All タブ](assets/02-llm-all-tokenizer-settings.png)

![LiteLLM の extra body が設定された、Agent Canvas 初回利用時の LLM All タブ](assets/03-llm-all-extra-body-settings.png)

LLM の設定は次のように表示されるはずです。

| フィールド | 値 |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

`openai/` というプレフィックスは、Lemonade のエンドポイントに対して LiteLLM に OpenAI 互換のリクエスト形式を使用するよう指示するものです。
カスタムトークナイザーは、この GGUF モデルの元となる Hugging Face トークナイザーであり、OpenHands がローカルのモデルサーバーと同じチャットテンプレートのトークンをカウントできるようにします。
現在の初回利用時の LLM フォームには、コンデンサー（condenser）設定は表示されません。
お使いの Agent Canvas のビルドで、後から **Settings > LLM** 配下にコンデンサー設定が表示される場合は、`llm_summarizing` を使用し、最大トークン数を Lemonade のコンテキストウィンドウよりも小さい値（例えば `56000`）に設定してください。

## 5. GitHub および Slack の MCP サーバーをインストールする

Agent Canvas の UI で **Customize**（または **Settings > MCP**）を開き、エージェントに GitHub と Slack 用のツールを与える MCP サーバーを追加します。
トークンの値はローカルの Agent Server にのみ送信され、暗号化された設定として保存されます。

<!-- @os:windows -->
> **Windows（Docker）:** 以下の `npx` による MCP サーバーのコマンドはコンテナ内部で実行されます。コンテナにはすでに Node.js が含まれているため、ホスト側には追加で何もインストールされません。
> `.openhands` がマウントされているため、MCP サーバーとそのトークンは、コンテナを再起動しても保持されます。
<!-- @os:end -->

### GitHub MCP サーバー

次の設定で新しい MCP サーバーを追加します。

| フィールド | 値 |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = お使いの GitHub トークン |

要約対象のリポジトリに対して読み取りアクセス権を持つ GitHub トークンを使用してください。

### Slack MCP サーバー

次の設定で、2つ目の MCP サーバーを追加します。

| フィールド | 値 |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = ダイジェスト用チャンネルの ID |

`SLACK_CHANNEL_IDS` には、ダイジェスト用チャンネルの ID（`SLACK_DIGEST_CHANNEL` と同じ値）を設定し、エージェントがすべての Slack チャンネルをページングして探す必要がないようにします。

両方のサーバーを追加したら、それぞれで **Test** ボタンを使い、接続が確立され、ツールが正しくアドバタイズされることを確認します。
GitHub サーバーからは GitHub 用のツールが、Slack サーバーからは Slack 用のツールが一覧表示されるはずです。

![GitHub と Slack のサーバーがインストールされた、Agent Canvas の MCP ページ](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. ダイジェスト自動化を作成する

Agent Canvas の UI で **Automations** ページを開き、新しい自動化を作成します。

1. **Create automation** を選び、**Prompt preset** タイプを選択します。
2. **Name** に `GitHub Development Digest to Slack` を設定します。
3. **Prompt** に次のテキストを設定し、リポジトリとチャンネルのプレースホルダーを実際の値に置き換えます。

   ```text
   Use the GitHub MCP server for exactly one repository: your-org/your-repo.
   Inspect recent development activity since the previous weekday, including
   merged pull requests, newly opened or reopened pull requests, notable
   commits pushed to main or release branches, new issues, important issue
   updates, releases, risks, blockers, and review requests. Keep GitHub
   lookups small: inspect the latest 3 to 5 commits, pull requests, issues,
   and releases. Use the Slack MCP server to post directly to channel ID
   C0123456789. Keep the Slack message concise: title with date range, 3 to 7
   bullets, links back to GitHub, and a Needs attention section only if
   needed. End with: This digest was generated by an AI agent (OpenHands) on
   behalf of the user. Do not include secrets, raw tokens, private
   environment variables, or unrelated Slack messages.
   ```

4. **Trigger** を **Cron** に設定し、スケジュールを `0 9 * * 1-5`（平日の午前9時）とし、**Timezone** をご自身のタイムゾーン（例: `America/New_York`）に設定します。
5. **Timeout** を `900` 秒に設定します。
6. 自動化を保存します。

自動化の詳細ページには、cron トリガーと生成された prompt-preset のエントリーポイントとともに、新しく作成された自動化が表示されます。

![作成後の Agent Canvas 自動化の詳細ページ](assets/05-automation-created.png)
## 7. 自動化をテストする

Agent Canvas UI の自動化詳細ページから:

1. **Run now**（または **Dispatch**）をクリックして、自動化をすぐに一度実行します。
2. 同じページの実行リストを確認します。最新の実行は `COMPLETED` に遷移するはずです。
3. 対象の Slack チャンネルを開きます。生成されたダイジェストが投稿されているはずです。

cron スケジュールの発火を待つ必要はありません。**Run now** を使うとオンデマンドで実行をトリガーできるため、スケジュールに頼る前にプロンプト、MCP 接続、Slack への投稿がすべて機能していることを確認できます。

![Agent Canvas automation run completed successfully](assets/06-automation-run-completed.png)

![Slack channel showing the generated OpenHands digest](assets/07-slackbot-message.png)

## トラブルシューティング

<!-- @os:windows -->
- **Docker のポート 8000 がすでに使用されている場合:** 別のホストポートにマッピングします。例えば `docker run ... -p 8080:8000 ...` のようにして、`http://localhost:8080/canvas` を開きます。
- **`docker pull` が資格情報エラーで失敗する場合**（例: "A specified logon session does not exist"）: 対話的な Windows セッションからプルを実行するか、イメージを事前にプルしておきます。このイメージはパブリックなので、`docker login` は不要です。
- **UI は読み込まれるがバックエンドが unhealthy な場合:** 初回起動時にコンテナ内で Agent Server 環境がビルドされます。しばらく待ってから再読み込みし、`docker logs <container>` で進行状況を確認してください。
- **Agent Canvas がコンテナから Lemonade に到達できない場合:** LLM の **Base URL** を `http://host.docker.internal:13305/api/v1` に設定し（`127.0.0.1` ではなく）、Lemonade が Windows ホスト上で実行中であることを確認します。
<!-- @os:end -->

- **Lemonade が停止している場合:** ステップ 1 の `lemonade run "${LEMONADE_MODEL}"` コマンドで再起動し、ヘルスチェックを再実行します。
- **`npm install -g` が権限エラーで失敗する場合:** Linux または WSL では、ユーザー所有のグローバル npm ディレクトリを設定し、シェル起動ファイルに追加してから、Agent Canvas を再インストールします:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

`zsh` を使用している場合は、同じ `export PATH=...` 行を `~/.bashrc` ではなく `~/.zshrc` に追加してください。
- **`custom_tokenizer` を設定した後、Agent Canvas が LLM 設定を拒否する場合:** Agent Server の Python 環境に `transformers` をインストールし、必要に応じて Agent Canvas を再起動してから、LLM 設定の保存を再試行します。`custom_tokenizer` が設定されている場合、OpenHands はトークナイザーのチャットテンプレートを読み込むために Transformers を必要とします。
- **Agent Canvas が Lemonade に到達できない場合:** `curl -fsS "${LEMONADE_BASE_URL}/health"` を確認し、初回利用時の LLM フォームまたは **Settings > LLM** に入力したベース URL が、実行中のローカルエンドポイントまたは HTTPS トンネルと一致していることを確認します。
- **LLM 設定が保存されない場合:** 値を入力した後に **Next** をクリックしたことを確認してください。**Settings > LLM** を再度開いて、値が保持されていることを確認します。
- **GitHub MCP がプライベートリポジトリを参照できない場合:** GitHub トークンが対象リポジトリへの読み取りアクセス権を持っていること、および **Customize** の MCP **Test** ボタンが GitHub ツールを表示することを確認します。
- **Slack はチャンネルを読み取れるが投稿できない場合:** 対象チャンネルに Slack アプリを招待し、ボットに `chat:write` 権限があることを確認します。
- **自動化が表示する Slack チャンネルが多すぎる場合:** Slack チャンネル ID を使用し、**Customize** の Slack MCP サーバーで `SLACK_CHANNEL_IDS` を設定します。
- **自動化の実行が失敗する、またはコンテキストを超過する場合:** Lemonade が `ctx_size=65536` で起動されていること、OpenHands の LLM に `custom_tokenizer` が設定されていることを確認し、GitHub の結果セットを 3 〜 5 件に制限した明示的なリポジトリを使用します。お使いの Agent Canvas ビルドで condenser 設定が公開されている場合は、condenser の最大トークン数を Lemonade のコンテキストウィンドウより小さく設定してください。

## 次のステップ

- 週次のリリース専用ダイジェストを追加する。
- より迅速な PR やプッシュのアラートのために、GitHub イベントトリガーの自動化を追加する。
- 同じダイジェストを Notion、Linear、または他の MCP 対応ツールに流す。

## リソース

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Lemonade Server documentation](https://lemonade-server.ai/docs)
- [OpenHands extensions repository](https://github.com/OpenHands/extensions)
- [Model Context Protocol servers](https://github.com/modelcontextprotocol/servers)
- [Slack MCP package](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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
try { lemonade unload } catch {}
```
<!-- @test:end -->
<!-- @os:end -->