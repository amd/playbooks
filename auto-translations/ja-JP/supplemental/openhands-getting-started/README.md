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
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## 概要

[OpenHands](https://github.com/All-Hands-AI/OpenHands) は、コードの記述、コマンドの実行、Web ブラウジング、実際のワークスペース内でのファイル編集を行える AI ソフトウェアエージェントです。チャットウィンドウから提案をコピーする代わりに、エージェントにプロジェクトフォルダーを指定して、機能の実装、バグの修正、テストの作成、コードベースの説明といった作業を任せることができます。

[Agent Canvas](https://github.com/OpenHands/agent-canvas) は、OpenHands を実行するために推奨されるブラウザ UI です。1 つの `agent-canvas` コマンドで、エージェントサーバー、自動化バックエンド、Web フロントエンドがまとめて起動するため、ブラウザからエージェントとの会話を進めることができます。

すべてを AMD システム上に保つため、エージェントは Lemonade Server によって提供されるローカルモデルと通信します。Lemonade はそのモデルを OpenAI 互換の API として公開するため、Agent Canvas は他の OpenAI 形式のエンドポイントと同様にこれを設定でき、モデル、コード、会話のコンテキストはすべて自分のマシン上にとどまります。

このプレイブックでは、ローカルモデルを起動し、Agent Canvas を起動してそのモデルを指定し、実際のプロジェクトフォルダーに対して最初のコーディングタスクを実行します。

## 学習内容

- Lemonade Server を起動し、ローカルモデルがチャットリクエストに応答することを確認する方法
- npm パッケージから Agent Canvas をインストールして起動する方法
- Agent Canvas がローカルの Lemonade モデルを LLM として使用するように設定する方法
- OpenHands の会話を開始し、エージェントがワークスペース内でファイルを編集したりコマンドを実行したりする様子を確認する方法
- エージェントが変更した内容を確認し、追加のメッセージで方向付けする方法

## 主要な概念

| 概念 | 内容 | このプレイブックでの位置付け |
| --- | --- | --- |
| Lemonade Server | AMD ハードウェア向けに構築された、OpenAI 互換の API を公開するローカル LLM サービングプラットフォーム。データはマシンの外に出ません。 | エージェントを動かすモデルを実行します。 |
| OpenHands | ワークスペース内でファイルの読み書き、シェルコマンドの実行、Web ブラウジングを行う AI ソフトウェアエージェント。 | チャットから操作するエージェントです。 |
| Agent Canvas | OpenHands の会話を実行し、ツール呼び出しやファイルの変更を表示するブラウザ UI およびバックエンド。 | スタックを起動し、会話をホストします。 |
| ワークスペース | エージェントが読み書きを許可されているプロジェクトフォルダー。 | エージェントによる編集やコマンドの対象です。 |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> コーディングエージェントのワークフローでは、より大きなモデルとコンテキストウィンドウを使用すると有利です。システムメモリは少なくとも 32 GB を使用し、より大きな GGUF モデルの場合は 64 GB 以上を推奨します。
<!-- @device:end -->

## メモリ構成の設定

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## ソフトウェアアップデートの確認

<!-- @require:software-update -->
<!-- @device:end -->

## 前提条件


<!-- @os:linux -->
<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-6-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so the host needs only Docker and the model.
     lemonade-chat-windows asserts the model is already downloaded. -->
<!-- @prereq:docker,lemonade-models-qwen3-6-35b-a3b -->
<!-- @os:end -->

必要なもの:

- Lemonade Server がインストールされており、以下のモデルを提供できること。

<!-- @os:linux -->
- Node.js 22.12 以降と `npm`(`agent-canvas` CLI で使用されます)。
- `uv`。これは Agent Canvas がエージェントサーバー環境の管理に使用する Python パッケージマネージャーです。お使いのシステムにまだインストールされていない場合は、Agent Canvas を起動する前に
  [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/) からインストールしてください。
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) がインストールされ、実行中であること。Windows では、Agent Canvas スタックは公開されている Docker イメージから実行されます。このイメージには Node.js、`uv`、`@openhands/agent-canvas` パッケージがバンドルされているため、ホストにこれらをインストールする必要はありません。
<!-- @os:end -->

- 作業対象となるプロジェクトフォルダー。これはエージェントに作業させたいローカルの git リポジトリや、任意のコードディレクトリで構いません。

<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @os:linux -->
<!-- @test:id=prereq-clis-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

lemonade --version
node -v
npm -v

# uv is a required prerequisite (agent-canvas uses it to build its Python env).
# Install it only if the runner doesn't already have it.
# TODO: remove this self-provisioning once the runners ship uv by default.
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"
uv --version

echo "OK: lemonade, node, npm, and uv are all available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=prereq-clis-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# On Windows the Agent Canvas stack runs from the published Docker image, so the
# only host prerequisites are Lemonade and a running Docker engine. Node.js, uv,
# and agent-canvas are bundled inside the container.
lemonade --version
docker version --format "{{.Server.Version}}"

Write-Host "OK: lemonade and docker are available"
```
<!-- @test:end -->
<!-- @os:end -->

## 1. Lemonade Server の起動

Lemonade CLI からモデルを起動します:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **ハードウェアに合ったモデルを選んでください。** `Qwen3.6-35B-A3B-GGUF`(約 20 GB)は強力なコーディングモデルですが、大きなメモリプールが必要です。デバイスのメモリや GPU VRAM が限られている場合は、代わりに Lemonade のモデルライブラリからより小さな GGUF モデルを選び、このプレイブック全体でそのモデル ID を使用してください。

> **注:** 最初の `lemonade run` では、モデルがまだ存在しない場合にダウンロードが行われるため、モデルのサイズと接続状況によっては時間がかかることがあります。

Lemonade は次の場所に OpenAI 互換の API を公開します:

```text
http://127.0.0.1:13305/api/v1
```

## 2. ローカルモデルの確認

Lemonade が選択したモデルを提供できることを確認します:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

次に、小さなチャットリクエストを送信します:

```bash
curl -sS "http://127.0.0.1:13305/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.6-35B-A3B-GGUF",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

これが `choices` 配列を返せば、Lemonade は Agent Canvas の準備ができています。

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
model_id = "${lemonade_model}"

entry = None
for item in data.get("data", []):
    if item.get("id") == model_id:
        entry = item
        break

if entry is None:
    print(f"Model {model_id} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print(f"Model {model_id} is present but not downloaded in Lemonade. Please download it before running CI.")
    sys.exit(1)

print(f"OK: {model_id} model is downloaded in Lemonade")
PY

body='{
  "model": "${lemonade_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Lemonade chat/completions returned a response"
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

if (-not $modelsJson) {throw "Lemonade server not ready on http://127.0.0.1:13305"}
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

$body = @{
  model = "${lemonade_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openhands-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) {throw "Empty response from Lemonade chat/completions"}
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->
# 3. Agent Canvas のインストールと起動

<!-- @os:linux -->
公開されている Agent Canvas パッケージをグローバルにインストールします:

```bash
npm install -g @openhands/agent-canvas
```

<!-- @test:id=agent-canvas-version-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# agent-canvas is expected to be provisioned on the runner. Fail loudly if it
# isn't, rather than installing it here.
if ! command -v agent-canvas >/dev/null 2>&1; then
  echo "agent-canvas is not on PATH; the runner must provision it before CI runs"
  exit 1
fi

# Prefer --version; fall back to --help if this build has no --version flag.
agent-canvas --version || agent-canvas --help

echo "OK: agent-canvas CLI is on PATH"
```
<!-- @test:end -->

次に、ターミナルからフルスタックを起動します:

```bash
agent-canvas
```

デフォルトでは、Agent Canvas は `http://localhost:8000` で起動します。ブラウザでその URL を
開いてください。このポートに特別な意味はありません。8000 がすでに使用されている場合は、
Agent Canvas を起動する際に `--port`(または `-p`)で任意の空いているポートを指定できます:

```bash
agent-canvas --port 3000
```

その場合は代わりに `http://localhost:3000` を開いてください。デフォルトのローカルバックエンドは
ホーム画面で正常(healthy)と表示されるはずです。

`agent-canvas` コマンドは、エージェントサーバー、自動化バックエンド、Web フロントエンドを
まとめて起動します。OpenHands をローカルで実行するには、このコマンド1つだけで済みます。

<!-- @test:id=agent-canvas-server-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

log="/tmp/agent-canvas-ci.log"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

# First launch builds the agent server's uv-managed Python env, so allow a generous startup window.
agent-canvas >"$log" 2>&1 &
p=$!

# Probe the agent-server backend health (18000/server_info), NOT just the 8000
# ingress root: the ingress serves the static frontend and returns 200 for /
# even when the agent-server is down.
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
  echo "---- agent-canvas log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: agent-canvas agent-server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
Windows では、Docker Desktop を使って公開されている Agent Canvas コンテナイメージを実行します。
このイメージには Agent Server、自動化バックエンド、Web フロントエンドがすべて含まれているため、
ホストに Node.js、`uv`、CLI をインストールする必要はありません。

まず、コンテナがマウントする設定フォルダとワークスペースフォルダを作成します:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

公開イメージを pull します(パブリックなのでログインは不要です):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

次に、スタックを起動します:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

ブラウザで `http://localhost:8000/canvas` を開いてください。ポート 8000 がすでに使用されている
場合は、別のホストポートをマップしてください(例: `-p 8080:8000`)。その場合は代わりに
`http://localhost:8080/canvas` を開いてください。

> **注:** 初回起動時にはコンテナ内で Agent Server が初期化されるため、バックエンドが
> 正常(healthy)と報告されるまでに1〜2分かかることがあります。

`.openhands` マウントは、コンテナの再起動後も LLM プロファイルと設定を保持します。
このプレイブックの残りの部分では、ブラウザ上の Agent Canvas UI を通じてすべてを設定していきます。

<!-- @test:id=agent-canvas-docker-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$image    = "ghcr.io/openhands/agent-canvas:1.14.0"
$name     = "openhands-agent-canvas-ci"
$hostPort = 18080

# The image is expected to be provisioned on the runner. Fail loudly if it
# isn't, rather than pulling it here.
$imgId = docker images -q $image
if (-not $imgId) {
  throw "Image $image is not present; the runner must provision it before CI runs"
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

## 4. ローカル LLM の設定

初回起動時、Agent Canvas はオンボーディングフローを開きます。そのフローの中で:

1. エージェントとして **OpenHands** を選択したまま **Next** をクリックします。
2. **Set up your LLM** で **Advanced** を選択します。
3. **Authentication** は **API key** のままにしておきます。
4. **Custom Model** に `openai/Qwen3.6-35B-A3B-GGUF` を設定します。
5. **Base URL** に `http://127.0.0.1:13305/api/v1` を設定します。
   <!-- @os:windows -->
   > Windows ではスタックがコンテナ内で実行されるため、ホストの `127.0.0.1` に
   > アクセスできません。コンテナ化されたエージェントが Windows ホスト上で実行されている
   > Lemonade にアクセスできるように、代わりに `http://host.docker.internal:13305/api/v1`
   > を使用してください。
   <!-- @os:end -->
6. **API Key** には、`lemonade-local` のような空でない任意のプレースホルダーを入力します。
   Lemonade は実際のキーを必要としませんが、OpenHands クライアント側で送信する値が必要です。
7. **Next** をクリックします。

設定が完了した Advanced 設定は以下のようになります。API key フィールドは
UI によってマスクされています。

![Lemonade モデルとローカルのベース URL を使用した Agent Canvas 初回利用時の LLM Advanced 設定](assets/01-llm-advanced-settings.png)

Agent Canvas はこれらの値を LLM プロファイルとして保存します。お使いのバージョンでそのプロファイルに
名前を付けるよう求められた場合は、`lemonade-local` のようにスペースを含まない名前を使用してください。
後でモデルを変更する場合は、**Settings > LLM** を開いて同じ Advanced フィールドを更新してください。
チャット入力欄から `/model` コマンドを使って、保存済みのプロファイルを切り替えることもできます。

## 5. ワークスペースを開く

エージェントは、選択したワークスペース内のファイルのみを読み書きできます。タスクを
開始する前に、Agent Canvas にプロジェクトフォルダを指定してください:

1. ホーム画面から **Open Workspace** を選択します。
2. プロジェクトを含むフォルダを選択します(例: エージェントに作業させたい git リポジトリ)。
3. そのワークスペースで新しい会話を開始します。

ファイルの読み取り、コマンドの実行、コードの編集など、エージェントが行うすべての操作は
そのワークスペースの範囲内に限定されます。

![オンボーディング後の Agent Canvas ホーム画面](assets/02-agent-canvas-home.png)

## 6. 最初のコーディングタスクを実行する

ワークスペースを開き、ローカル LLM を選択した状態で、チャットに具体的なタスクを入力します。
最初のタスクとしては、小規模で検証可能なものが適しています。例えば:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

会話のタイムラインを見てみましょう。OpenHands は以下を行います:

- ワークスペースを読み取り、構成を把握する。
- 要求された関数とテストブロックを含む `hello.py` を作成する。
- 必要に応じて `python3 hello.py` を実行し、出力を検証する。
- 実行した内容とコマンドの出力をチャットで報告する。

ワークスペースに新しいファイルが表示され、エージェントの最終メッセージには行った変更の
説明が含まれているはずです。これは達成の瞬間です。エージェントがあなたのプロジェクト
フォルダ内で実際にコードを書き、実行したのです。

## 7. エージェントのレビューと誘導

エージェントがステップを完了したら、次のステップを承認する前に、その成果をレビューしてください:

- **ファイルの変更**: ワークスペースのファイルブラウザ、またはエージェントの diff ビューを使って、
  追加・変更・削除された内容を正確に確認します。
- **コマンドの出力**: エージェントが実行したコマンドを展開して、stdout、stderr、終了コードを確認します。
- **フォローアップ**: 結果が期待通りでない場合は、同じ会話の中で修正内容を返信してください。
  エージェントは以前の文脈を保持したまま、同じファイルに対して反復作業を行います。

例えば、テストが期待していた挨拶文を出力しなかった場合は、次のように返信します:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

エージェントはファイルを再度読み取り、コマンドを実行して問題を診断し、再びファイルを
編集します。これらはすべて同じ会話の中で行われます。
## トラブルシューティング

<!-- @os:linux -->
- **`agent-canvas` が PATH に存在しない場合:** `npm install -g @openhands/agent-canvas` で再インストールし、新しいターミナルから `agent-canvas` を起動できるように、npm のグローバルバイナリディレクトリが PATH に含まれていることを確認してください。
- **`npm install -g` が権限エラーで失敗する場合:** ユーザー所有のグローバル npm ディレクトリを設定してから、ターミナルを再度開き、Agent Canvas を再度インストールしてください。

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` が見つからない場合:**
  [uv インストールガイド](https://docs.astral.sh/uv/getting-started/installation/)からインストールしてください。
  Agent Canvas は `uv` を使用してエージェントサーバーの Python 環境を管理します。
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` または `docker run` が接続に失敗する場合:** Docker Desktop が実行中であること（システムトレイにクジラのアイコンが表示されていること）と、エンジンの起動が完了していることを確認してください。`docker version` を実行すると、Client と Server の両方のセクションが表示されるはずです。
- **コンテナは起動するがバックエンドが正常な状態にならない場合:** 初回起動時はコンテナ内で Agent Server が初期化されます。1～2分待ってから、`docker logs <container>` でエラーを確認してください。
- **コンテナが Lemonade に到達できない場合:** コンテナは `host.docker.internal` 経由でホストに到達します。Windows ホスト上で Lemonade が `lemonade status` でサービスを提供していることを確認し、LLM を設定する際のベース URL として `http://host.docker.internal:13305/api/v1` を使用してください。
<!-- @os:end -->

- **UI は読み込まれるがバックエンドが異常状態を示す場合:** エージェントサーバーの起動が完了するまで1～2分待ってから更新してください。それでも異常状態が続く場合は、スタックを再起動してログでエラーを確認してください。
- **Lemonade のチャットリクエストが接続エラーで失敗する場合:** `curl -fsS "http://127.0.0.1:13305/api/v1/health"` が成功することと、`lemonade status` で Lemonade が引き続きモデルを提供していることを確認してください。
- **エージェントがコンテキスト長またはトークン上限のエラーを出す場合:** 新しい会話を開始し、エージェントが過大な履歴を抱えないようにしてください。問題が繰り返し発生する場合は、メモリが許す範囲で、デフォルトの 65536 より大きい `ctx_size`（例: `ctx_size=131072`）を指定して Lemonade を再起動してください。
- **エージェントが低品質または不完全な編集を生成する場合:** Lemonade でより大きなモデルに切り替えるか、エージェントに対してより小さく具体的なタスクを与え、完了してから次の変更を依頼してください。

## 次のステップ

- 同じワークスペース内で、ユニットテストファイルの追加や既知のバグの修正など、より大きなタスクを試し、変更を維持する前にエージェントの差分を確認してください。
- **Customize** で GitHub や Slack などの MCP サーバーを接続すると、作業中にエージェントが issue を読み取ったり、更新を投稿したりできるようになります。
- 複数の LLM プロファイル（高速な小型モデルと強力な大型モデル）を保存し、会話の途中で `/model` を使って切り替えてください。
- [OpenHands の自動化](https://docs.openhands.dev/openhands/usage/automations/overview)に進み、繰り返し発生する開発ループを、スケジュールまたはイベントによってトリガーされるエージェント実行に変えましょう。

## リソース

- [OpenHands ドキュメント](https://docs.openhands.dev/)
- [Agent Canvas の概要](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Agent Canvas のセットアップ](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM プロファイルとモデル設定](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Lemonade Server ドキュメント](https://lemonade-server.ai/docs)

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