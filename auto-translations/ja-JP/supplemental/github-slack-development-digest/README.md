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

開発者は、ラベル付けされたプルリクエストのレビュー、GitHub コメントへの返信、新しいイシューのトリアージ、Slack スレッドをスタンドアップメモやインシデント対応に変換する作業、リリースやリサーチの動向の追跡といった、小規模で繰り返し発生するループに多くの時間を費やしています。
それぞれのループはおなじみのものですが、それでも判断力が求められます。適切なコンテキストを収集し、何が重要かを見極め、チームがすでに使っている場所に明確な更新情報を投稿する必要があります。

[OpenHands automations](https://docs.openhands.dev/openhands/usage/automations/overview) は、こうしたループをスケジュール実行またはイベントトリガーによるエージェント会話に変換します。これは、AI ソフトウェアエージェントがコンテキストを読み取り、ツールを呼び出し、更新情報を生成する実行です。
OpenHands 拡張機能カタログにある共有オートメーションテンプレートは、GitHub プルリクエストのレビュー、リポジトリの監視、Linear イシューのトリアージ、インシデントの振り返り、Slack スタンドアップダイジェスト、リサーチブリーフといったユースケースにおいて、次のパターンに従います。オートメーションが起動し、GitHub や Slack などの設定済みインテグレーションを使ってコンテキストを取得し、大規模言語モデル（LLM）でそのコンテキストを推論し、結果を書き戻します。

[Agent Canvas](https://github.com/OpenHands/agent-canvas) は、こうしたオートメーションを構築・テストするためのローカルコントロールプレーンです。
このプレイブックでは、Agent Canvas がエージェント会話を実行するバックエンドプロセスである OpenHands Agent Server を実行し、GitHub や Slack などの外部サービスにエージェントを接続します。

ワークフローをお使いの AMD システム上に保つため、エージェントは Lemonade Server が提供するローカルモデルとやり取りします。
Lemonade はそのモデルを OpenAI 互換の API 経由で公開するため、Agent Canvas はそれをリモートの OpenAI 形式のエンドポイントのように設定でき、モデル、プロンプト、ワークフローのコンテキストはローカルに留まります。

このプレイブックでは、具体的なオートメーションを1つ構築します。スケジュール実行される GitHub から Slack への開発ダイジェストです。
これは、GitHub を使って最近のリポジトリの活動を調査し、Slack でダイジェストを投稿し、Agent Canvas API 呼び出しでオートメーションを設定・テストし、Lemonade を使ってローカルで LLM を実行します。

![GitHub MCP、OpenHands オートメーション、Lemonade Server、Slack MCP を示すアーキテクチャ図](assets/00-architecture-overview.png)

## このプレイブックで学べること

- Lemonade Server を起動し、ローカルモデルがチャットリクエストに応答することを確認する方法
- Agent Canvas を起動し、その Agent Server をローカル LLM に向ける方法
- Agent Server API を通じて GitHub と Slack の Model Context Protocol（MCP）サーバーをインストールする方法
- 開発ダイジェストを Slack に投稿するスケジュール実行の OpenHands オートメーションを作成・ディスパッチする方法
- 最も一般的なローカルモデルおよびオートメーションの障害をトラブルシューティングする方法

## 中心となる概念

| 概念 | 内容 | このプレイブックでの位置づけ |
| --- | --- | --- |
| Lemonade Server | AMD ハードウェア向けに構築された、OpenAI 互換の API を公開するローカル LLM サービングプラットフォーム。データがマシンの外に出ることはありません。 | エージェントを支えるモデルを実行します。 |
| OpenHands Agent Server | OpenHands エージェント会話を実行するバックエンドプロセス。 | エージェント、その LLM プロファイル、その MCP サーバーをホストします。 |
| Agent Canvas | Agent Server と、エージェントの実行を確認するための UI を実行する、OpenHands 向けのローカルコントロールプレーン。 | バックエンドを起動し、呼び出す API を提供します。 |
| MCP サーバー | GitHub や Slack などの外部サービス向けのツールをエージェントに提供する Model Context Protocol サーバー。 | エージェントが GitHub を読み取り、Slack に書き込めるようにします。 |
| OpenHands オートメーション | コンテキストを取得し、それを推論し、結果をどこかに書き込む、スケジュール実行またはイベントトリガーのエージェント会話。 | ここで構築する GitHub から Slack へのダイジェストです。 |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> コーディングエージェントのワークフローは、より大きなモデルとコンテキストウィンドウの恩恵を受けます。
> 少なくとも32 GBのシステムメモリを使用してください。より大きな GGUF モデルの場合は、64 GB以上を推奨します。
<!-- @device:end -->

## メモリ設定を行う

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアの更新を確認する

<!-- @require:software-update -->
<!-- @device:end -->

## 前提条件

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- @os:end -->

以下が必要です。

- 標準の [Lemonade インストールガイド](https://lemonade-server.ai/docs/guide/install/) に従ってインストールされた Lemonade Server。

<!-- @os:linux -->
- 公開されている Agent Canvas CLI をインストールし、`npx` で MCP サーバーを実行するための Node.js 22.12 以降と `npm`。
- Agent Canvas が Agent Server 環境を構築するために使用する Python パッケージマネージャーである `uv`。まだインストールされていない場合は、[uv インストールガイド](https://docs.astral.sh/uv/getting-started/installation/) からインストールしてください。
- スキーマ駆動のエージェント設定、`LLMSummarizingCondenserSettings.max_tokens`、および LLM の `custom_tokenizer` サポートを備えた、最近公開された `@openhands/agent-canvas` パッケージ。
- Agent Server 環境で利用可能な Python の `transformers` パッケージ。`custom_tokenizer` が設定されている場合、チャットテンプレートのトークンカウントに必要です。
<!-- @os:end -->

<!-- @os:windows -->
- インストールされて実行中の [Windows 用 Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)。Windows では、Agent Canvas スタックは公開済みの Docker イメージから実行され、これには Node.js、`uv`、`transformers`、`@openhands/agent-canvas` パッケージがバンドルされているため、これらをホストにインストールする必要はありません。
<!-- @os:end -->

- 要約対象のリポジトリへの読み取りアクセス権を持つ GitHub トークン。
- `chat:write` とチャンネル読み取りアクセス権を持つ Slack ボットトークン（`xoxb-...`）。
- Slack チームID（`T...`）。
- ダイジェストの投稿先となる Slack チャンネルID（`C...`）。

オートメーションをテストする前に、対象のチャンネルに Slack アプリを招待してください。
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

これら2つの変数は、以下の確認コマンドで使用されます。
モデル、トークナイザー、その他のLLM設定は、後の手順でAgent Canvas UIに直接入力するため、必要な箇所ではリテラル値をそのまま記載しています。

以下の値は、後の手順でAgent Canvas UIに入力します。
コピーして使えるように、ここに設定しておきます。

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
組織全体を対象とする広範なワイルドカードを指定すると、ローカルモデルにとってMCPコンテキストが大きくなりすぎる場合があります。

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Lemonade Server を起動する

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

> **お使いのハードウェアに合ったモデルを選択してください。** `Qwen3.6-35B-A3B-GGUF`（約20 GB）はこのワークフローに適した強力なモデルですが、大きなメモリプールが必要です。
> お使いのデバイスのメモリやGPU VRAMが限られている場合は、Lemonadeモデルライブラリからより小さいGGUFモデルを選び、そのモデルID（および対応するトークナイザー）をこのプレイブック全体で使用してください。

> **注:** 最初の `lemonade run` はモデルがまだ存在しない場合にダウンロードを行うため、モデルサイズや接続環境によっては時間がかかることがあります。

Lemonadeは、OpenAI互換のAPIを次のエンドポイントで公開します。

```text
http://127.0.0.1:13305/api/v1
```

オプション: Agent Canvasや自動化ランナーが同じマシン上にない場合は、Lemonadeエンドポイントをセキュアなトンネル経由で公開し、そのHTTPS URLをLLMベースURLとして使用してください。
[ngrok](https://ngrok.com/) は、セキュアなHTTPS URLを介してローカルポートをインターネットに公開します。無料のngrokアカウントが必要で、`YOUR_NGROK_DOMAIN.ngrok-free.dev` はご自身の予約済みドメインに置き換えてください。

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. ローカルモデルを確認する

Lemonadeが選択したモデルを提供できることを確認します。

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

続いて、小さなチャットリクエストを送信します。

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

続いて、小さなチャットリクエストを送信します。

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

これにより `choices` 配列が返された場合、LemonadeはAgent Canvasで使用する準備ができています。

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

## 3. Agent Canvas を起動する

<!-- @os:linux -->
公開されているAgent Canvasパッケージをインストールし、フルスタックを起動します。

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

グローバルなnpmインストールが権限エラーで失敗する場合は、下記のnpm権限のトラブルシューティング項目を参照してください。

デフォルトでは、Agent Canvasは `http://localhost:8000` で起動します。
そのURLをブラウザで開いてください。
このポート番号自体に特別な意味はありません。8000がすでに使用されている場合は、`--port`（または `-p`）で任意の空いているポートを指定できます。
デフォルトのローカルバックエンドは、ホーム画面でhealthyと表示されるはずです。

> **注:** 初回起動時にはAgent ServerのUv管理Python環境をビルドするため、バックエンドがhealthyと表示されるまで数分かかることがあります。

`agent-canvas` コマンドは、エージェントサーバー、自動化バックエンド、Webフロントエンドをまとめて起動します。
OpenHandsをローカルで実行するには、このコマンド1つだけで十分です。
このプレイブックの残りの部分では、ブラウザ上のAgent Canvas UIを通じてすべての設定を行います。
<!-- @os:end -->

<!-- @os:windows -->
Windowsでは、Docker Desktopを使用して公開されているAgent Canvasコンテナイメージを実行します。
このイメージにはAgent Server、自動化バックエンド、Webフロントエンドがバンドルされているため、ホスト側にNode.js、`uv`、CLIをインストールする必要はありません。

まず、コンテナがマウントする設定用フォルダとワークスペース用フォルダを作成します。

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

公開イメージをプルします（約6 GB。パブリックイメージのためログインは不要です）。

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
ポート8000がすでに使用されている場合は、別のホストポート（例: `-p 8080:8000`）にマッピングし、代わりに `http://localhost:8080/canvas` を開いてください。

> **注:** 初回起動時にはコンテナ内でAgent Server環境をビルドするため、バックエンドがhealthyと表示されるまで数分かかることがあります。

`.openhands` マウントにより、LLMプロファイル、MCPサーバー、自動化設定はコンテナを再起動しても保持されます。
このプレイブックの残りの部分では、ブラウザで `http://localhost:8000/canvas` を開いたAgent Canvas UIを通じてすべての設定を行います。
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
## 4. UIでのローカルLLMの設定

初回起動時、Agent Canvasはオンボーディングフローを開きます。
そのフローでは:

1. エージェントとして**OpenHands**を選択したまま**Next**をクリックします。
2. **Set up your LLM**で、**Advanced**を選択します。
3. **Authentication**は**API key**のままにしておきます。
4. **Custom Model**を`openai/Qwen3.6-35B-A3B-GGUF`に設定します。
5. **Base URL**を`http://127.0.0.1:13305/api/v1`に設定します。
6. **API Key**には、`lemonade-local`のような空でない任意のプレースホルダーを入力します。Lemonadeは実際のキーを必要としませんが、OpenHandsクライアントは送信する値を必要とします。

<!-- @os:windows -->
> **Windows(Docker)の場合:** Agent Serverはコンテナ内で実行されるため、**Base URL**は`http://127.0.0.1:13305/api/v1`ではなく`http://host.docker.internal:13305/api/v1`に設定します。
> コンテナ内から見ると、`127.0.0.1`はコンテナ自身を指します。`host.docker.internal`はWindowsホスト上で実行されているLemonadeに到達するためのもので、このホスト名はDocker Desktopによって自動的に提供されます。
<!-- @os:end -->

接続用のフィールドは次のようになるはずです。
APIキーのフィールドはUIによってマスクされています。

![LemonadeモデルとローカルベースURLを設定したAgent Canvas初回利用時のLLM Advanced設定](assets/01-llm-advanced-settings.png)

続いて**All**を選択し、追加のローカルモデル用フィールドを設定します:

1. **Custom Tokenizer**までスクロールし、`Qwen/Qwen3.6-35B-A3B`に設定します。
2. **LiteLLM Extra Body**までスクロールし、`{"enable_thinking": true}`に設定します。
3. **Next**をクリックします。

![Qwenカスタムトークナイザーを設定したAgent Canvas初回利用時のLLM Allタブ](assets/02-llm-all-tokenizer-settings.png)

![LiteLLM extra bodyを設定したAgent Canvas初回利用時のLLM Allタブ](assets/03-llm-all-extra-body-settings.png)

LLMの設定は次のように表示されるはずです:

| フィールド | 値 |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

`openai/`プレフィックスは、LiteLLMにLemonadeエンドポイントに対してOpenAI互換のリクエストフォーマットを使用するよう指示します。
カスタムトークナイザーは、GGUFモデルの元となったHugging Faceトークナイザーであり、これによりOpenHandsはローカルモデルサーバーが認識するのと同じチャットテンプレートトークンをカウントできるようになります。
現在の初回利用時のLLMフォームには、condenser設定は表示されません。
お使いのAgent Canvasビルドで後から**Settings > LLM**の下にcondenser設定が表示される場合は、`llm_summarizing`を使用し、最大トークン数をLemonadeのコンテキストウィンドウ未満、例えば`56000`に設定してください。

## 5. GitHubおよびSlack MCPサーバーのインストール

Agent Canvas UIで、**Customize**(または**Settings > MCP**)を開き、エージェントにGitHubとSlack用のツールを与えるMCPサーバーを追加します。
トークンの値はローカルのAgent Serverにのみ送信され、暗号化された設定として保存されます。

<!-- @os:windows -->
> **Windows(Docker)の場合:** 以下の`npx` MCPサーバーコマンドはコンテナ内で実行されます。コンテナにはすでにNode.jsが含まれているため、ホスト側には追加で何もインストールされません。
> `.openhands`がマウントされているため、MCPサーバーとそのトークンはコンテナの再起動をまたいで保持されます。
<!-- @os:end -->

### GitHub MCPサーバー

次の設定で新しいMCPサーバーを追加します:

| フィールド | 値 |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = お使いのGitHubトークン |

要約対象にしたいリポジトリに対する読み取りアクセス権を持つGitHubトークンを使用してください。

### Slack MCPサーバー

次の設定で2つ目のMCPサーバーを追加します:

| フィールド | 値 |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = お使いのダイジェスト用チャンネルID |

`SLACK_CHANNEL_IDS`にはダイジェスト用チャンネルID(`SLACK_DIGEST_CHANNEL`と同じ値)を設定し、エージェントがすべてのSlackチャンネルをページ送りで確認する必要がないようにします。

両方のサーバーを追加したら、それぞれで**Test**ボタンを使用して、接続が確立され、ツールが提供されることを確認します。
GitHubサーバーはGitHubツールを一覧表示し、SlackサーバーはSlackツールを一覧表示するはずです。

![GitHubとSlackのサーバーがインストールされたAgent CanvasのMCPページ](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. ダイジェスト自動化の作成

Agent Canvas UIで、**Automations**ページを開き、新しい自動化を作成します:

1. **Create automation**を選択し、**Prompt preset**タイプを選択します。
2. **Name**を`GitHub Development Digest to Slack`に設定します。
3. **Prompt**を以下のテキストに設定し、リポジトリとチャンネルのプレースホルダーを実際の値に置き換えます:

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

4. **Trigger**を**Cron**に設定し、スケジュールを`0 9 * * 1-5`(平日の午前9時)とし、**Timezone**をお使いのタイムゾーン、例えば`America/New_York`に設定します。
5. **Timeout**を`900`秒に設定します。
6. 自動化を保存します。

自動化の詳細ページには、cronトリガーと生成されたプロンプトプリセットのエントリーポイントとともに、新しい自動化が表示されます。

![作成後のAgent Canvas自動化詳細ページ](assets/05-automation-created.png)
## 7. 自動化のテスト

Agent Canvas UI の自動化詳細ページから:

1. **Run now**(または **Dispatch**)をクリックして、自動化を今すぐ1回実行します。
2. 同じページの実行リストを確認します。最新の実行が `COMPLETED` に遷移するはずです。
3. 対象の Slack チャンネルを開きます。生成されたダイジェストが投稿されているはずです。

cron スケジュールの発火を待つ必要はありません。**Run now** を使えばオンデマンドで実行をトリガーできるため、スケジュールに頼る前に、プロンプト、MCP 接続、Slack への投稿がすべて正しく機能することを確認できます。

![自動化の実行が正常に完了した Agent Canvas](assets/06-automation-run-completed.png)

![生成された OpenHands ダイジェストを表示している Slack チャンネル](assets/07-slackbot-message.png)

## トラブルシューティング

<!-- @os:windows -->
- **Docker のポート 8000 が既に使用されている場合:** 別のホストポートにマッピングします。例えば `docker run ... -p 8080:8000 ...` のようにし、`http://localhost:8080/canvas` を開きます。
- **`docker pull` が資格情報エラーで失敗する場合**(例:「指定されたログオン セッションは存在しません」):インタラクティブな Windows セッションから pull を実行するか、事前にイメージを pull しておいてください。このイメージはパブリックであるため、`docker login` は不要です。
- **UI はロードされるがバックエンドが unhealthy な場合:** 初回起動時はコンテナ内で Agent Server 環境をビルドします。1分ほど待ってから再読み込みし、`docker logs <container>` で進捗を確認してください。
- **Agent Canvas がコンテナから Lemonade に到達できない場合:** LLM の **Base URL** を `http://host.docker.internal:13305/api/v1`(`127.0.0.1` ではなく)に設定し、Lemonade が Windows ホスト上で実行されていることを確認してください。
<!-- @os:end -->

- **Lemonade が停止している場合:** ステップ1の `lemonade run "${LEMONADE_MODEL}"` コマンドで再起動し、ヘルスチェックを再実行してください。
- **`npm install -g` が権限エラーで失敗する場合:** Linux または WSL では、ユーザー所有のグローバル npm ディレクトリを設定し、シェルの起動ファイルに追加してから、Agent Canvas を再インストールしてください。

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

`zsh` を使用している場合は、同じ `export PATH=...` の行を `~/.bashrc` の代わりに `~/.zshrc` に追加してください。
- **`custom_tokenizer` を設定した後、Agent Canvas が LLM の設定を拒否する場合:** Agent Server の Python 環境に `transformers` をインストールし、必要であれば Agent Canvas を再起動してから、LLM 設定の保存を再試行してください。`custom_tokenizer` が設定されている場合、OpenHands はトークナイザーのチャットテンプレートを読み込むために Transformers を必要とします。
- **Agent Canvas が Lemonade に到達できない場合:** `curl -fsS "${LEMONADE_BASE_URL}/health"` で確認し、初回利用時の LLM フォームまたは **Settings > LLM** に入力したベース URL が、実行中のローカルエンドポイントまたは HTTPS トンネルと一致していることを確認してください。
- **LLM 設定が保存されなかった場合:** 値を入力した後に **Next** をクリックしたことを確認してください。**Settings > LLM** を再度開いて、値が保持されているか確認してください。
- **GitHub MCP がプライベートリポジトリを参照できない場合:** GitHub トークンが対象リポジトリへの読み取りアクセス権を持っていること、および **Customize** 内の MCP **Test** ボタンが GitHub ツールを提示していることを確認してください。
- **Slack がチャンネルを読み取れるが投稿できない場合:** Slack アプリを対象チャンネルに招待し、ボットが `chat:write` 権限を持っていることを確認してください。
- **自動化が Slack チャンネルを多数リストする場合:** Slack チャンネル ID を使用し、**Customize** 内の Slack MCP サーバーで `SLACK_CHANNEL_IDS` を設定してください。
- **自動化の実行が失敗する、またはコンテキストを超過する場合:** Lemonade が `ctx_size=65536` で起動されていること、OpenHands の LLM に `custom_tokenizer` が設定されていることを確認し、GitHub の結果セットを3〜5件に制限した明示的なリポジトリを使用してください。お使いの Agent Canvas ビルドで condenser 設定が公開されている場合は、condenser の最大トークン数を Lemonade のコンテキストウィンドウより低く設定してください。

## 次のステップ

- リリースのみを対象とする週次ダイジェストを追加する。
- より迅速な PR やプッシュ通知のために、GitHub イベントトリガーの自動化を追加する。
- 同じダイジェストを Notion、Linear、その他の MCP 対応ツールにルーティングする。

## リソース

- [AMD AI プレイブック](https://developer.amd.com/playbooks/)
- [Lemonade Server ドキュメント](https://lemonade-server.ai/docs)
- [OpenHands 拡張機能リポジトリ](https://github.com/OpenHands/extensions)
- [Model Context Protocol サーバー](https://github.com/modelcontextprotocol/servers)
- [Slack MCP パッケージ](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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