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

[OpenHands](https://github.com/All-Hands-AI/OpenHands) は、実際のワークスペース内でコードを書いたり、コマンドを実行したり、ウェブを閲覧したり、ファイルを編集したりできる AI ソフトウェアエージェントです。チャットウィンドウから提案をコピーする代わりに、エージェントにプロジェクトフォルダーを指し示し、機能の実装、バグ修正、テストの作成、コードベースの説明といった作業を実行させます。

[Agent Canvas](https://github.com/OpenHands/agent-canvas) は、OpenHands を実行するために推奨されるブラウザ UI です。単一の `agent-canvas` コマンドで、エージェントサーバー、自動化バックエンド、Web フロントエンドをまとめて起動できるため、ブラウザからエージェントとの対話を進めることができます。

すべてを AMD システム上に留めるため、エージェントは Lemonade Server によって提供されるローカルモデルと通信します。Lemonade はそのモデルを OpenAI 互換の API として公開するため、Agent Canvas は他の OpenAI 形式のエンドポイントと同様にこれを設定でき、モデル、あなたのコード、会話のコンテキストはすべてあなたのマシン上に留まります。

このプレイブックでは、ローカルモデルを起動し、Agent Canvas を立ち上げ、そのモデルを指定し、実際のプロジェクトフォルダーに対して最初のコーディングタスクを実行します。

## 学習内容

- Lemonade Server を起動し、ローカルモデルがチャットリクエストに応答することを確認する方法
- npm パッケージから Agent Canvas をインストールして起動する方法
- Agent Canvas を設定して、ローカルの Lemonade モデルを LLM として使用する方法
- OpenHands の会話を開始し、エージェントがワークスペース内でファイルを編集し、コマンドを実行する様子を確認する方法
- エージェントが変更した内容を確認し、フォローアップメッセージで操作を誘導する方法

## 主要な概念

| 概念 | 内容 | このプレイブックでの位置づけ |
| --- | --- | --- |
| Lemonade Server | AMD ハードウェア向けに構築された、OpenAI 互換の API を公開するローカル LLM サービングプラットフォーム。データがあなたのマシンから外に出ることはありません。 | エージェントを動かすモデルを実行します。 |
| OpenHands | ワークスペース内でファイルの読み書き、シェルコマンドの実行、ウェブ閲覧を行う AI ソフトウェアエージェント。 | チャットから操作するエージェントです。 |
| Agent Canvas | OpenHands の会話を実行し、ツール呼び出しとファイルの変更を表示するブラウザ UI およびバックエンド。 | スタックを起動し、会話をホストします。 |
| ワークスペース | エージェントが読み取りと変更を許可されたプロジェクトフォルダー。 | エージェントによる編集とコマンドの対象です。 |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> コーディングエージェントのワークフローは、より大きなモデルとコンテキストウィンドウの恩恵を受けます。少なくとも 32 GB のシステムメモリを使用し、より大きな GGUF モデルの場合は 64 GB 以上を推奨します。
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
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here.
     lemonade-chat-windows asserts the model is already downloaded. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

次のものが必要です。

- 以下のモデルを提供できる状態の、インストール済みの Lemonade Server。

<!-- @os:linux -->
- Node.js 22.12 以降と `npm`(`agent-canvas` CLI が使用します)。
- `uv`。これは Agent Canvas がエージェントサーバー環境の管理に使用する Python パッケージマネージャーです。お使いのシステムにまだ入っていない場合は、Agent Canvas を起動する前に[uv インストールガイド](https://docs.astral.sh/uv/getting-started/installation/)からインストールしてください。
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) がインストールされ、実行されていること。Windows では、Agent Canvas スタックは公開済みの Docker イメージから実行されます。このイメージには Node.js、`uv`、`@openhands/agent-canvas` パッケージが同梱されているため、ホスト側にこれらをインストールする必要はありません。
<!-- @os:end -->

- 作業対象のプロジェクトフォルダー。エージェントに作業させたい、任意のローカル git リポジトリまたはコードディレクトリで構いません。

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

## 1. Lemonade Server を起動する

Lemonade CLI からモデルを起動します。

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **お使いのハードウェアに適したモデルを選択してください。** `Qwen3.6-35B-A3B-GGUF`(約 20 GB)は強力なコーディングモデルですが、大きなメモリプールが必要です。お使いのデバイスのメモリや GPU VRAM が限られている場合は、代わりに Lemonade モデルライブラリからより小さな GGUF モデルを選び、このプレイブック全体を通してそのモデル ID を使用してください。

> **注:** 最初の `lemonade run` では、モデルがまだ存在しない場合にダウンロードが行われます。モデルのサイズや接続状況によっては、時間がかかることがあります。

Lemonade は OpenAI 互換の API を次の場所に公開します。

```text
http://127.0.0.1:13305/api/v1
```

## 2. ローカルモデルを確認する

Lemonade が選択したモデルを提供できることを確認します。

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

次に、小さなチャットリクエストを送信します。

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

これが `choices` 配列を返せば、Lemonade は Agent Canvas の準備が整っています。

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
## 3. Agent Canvas のインストールと起動

<!-- @os:linux -->
公開されている Agent Canvas パッケージをグローバルにインストールします。

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

次に、ターミナルからフルスタックを起動します。

```bash
agent-canvas
```

デフォルトでは、Agent Canvas は `http://localhost:8000` で起動します。ブラウザでその
URL を開いてください。このポート番号自体に特別な意味はありません。8000 がすでに
使用されている場合は、Agent Canvas 起動時に `--port`(または `-p`)で空いている
任意のポートを指定できます。

```bash
agent-canvas --port 3000
```

その後、代わりに `http://localhost:3000` を開いてください。デフォルトのローカル
バックエンドは、ホーム画面で正常(healthy)と表示されるはずです。

`agent-canvas` コマンドは、エージェントサーバー、自動化バックエンド、Web フロント
エンドをまとめて起動します。OpenHands をローカルで実行するために必要なコマンドは
この 1 つだけです。

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
Windows では、Docker Desktop を使って公開済みの Agent Canvas コンテナイメージを
実行します。このイメージには Agent Server、自動化バックエンド、Web フロントエンド
がバンドルされているため、ホスト側に Node.js、`uv`、CLI をインストールする必要は
ありません。

まず、コンテナがマウントする config フォルダと workspace フォルダを作成します。

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

公開イメージを pull します(公開イメージのためログインは不要です)。

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

次に、スタックを起動します。

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

ブラウザで `http://localhost:8000/canvas` を開いてください。ポート 8000 がすでに
使用されている場合は、別のホストポートにマップしてください。たとえば
`-p 8080:8000` とした場合は、代わりに `http://localhost:8080/canvas` を開いて
ください。

> **注:** 初回起動時にはコンテナ内で Agent Server が初期化されるため、バックエンド
> が正常(healthy)と報告されるまで 1〜2 分かかることがあります。

`.openhands` マウントにより、LLM プロファイルと設定はコンテナの再起動後も保持
されます。本ガイドの残りの部分では、ブラウザ上の Agent Canvas UI からすべてを
設定していきます。

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

初回起動時、Agent Canvas はオンボーディングフローを開きます。そのフローでは、
以下の手順を行います。

1. エージェントとして **OpenHands** が選択されたままにして、**Next** をクリックします。
2. **Set up your LLM** で、**Advanced** を選択します。
3. **Authentication** は **API key** のままにします。
4. **Custom Model** に `openai/Qwen3.6-35B-A3B-GGUF` を設定します。
5. **Base URL** に `http://127.0.0.1:13305/api/v1` を設定します。
   <!-- @os:windows -->
   > Windows ではスタックがコンテナ内で実行されるため、`127.0.0.1` でホストに
   > アクセスすることはできません。代わりに `http://host.docker.internal:13305/api/v1`
   > を使用することで、コンテナ化されたエージェントが Windows ホスト上で実行されて
   > いる Lemonade にアクセスできるようになります。
   <!-- @os:end -->
6. **API Key** には、`lemonade-local` のような空でないプレースホルダーを入力します。
   Lemonade は実際のキーを必要としませんが、OpenHands クライアント側で送信する値が
   必要です。
7. **Next** をクリックします。

設定が完了した Advanced 設定は、次のようになります。API key フィールドは UI に
よってマスクされています。

![Agent Canvas の初回利用時の LLM Advanced 設定(Lemonade モデルとローカルベース URL を使用)](assets/01-llm-advanced-settings.png)

Agent Canvas はこれらの値を LLM プロファイルとして保存します。使用しているバージョン
でそのプロファイルに名前を付けるよう求められた場合は、`lemonade-local` のような
スペースを含まない名前を使用してください。後でモデルを変更する場合は、
**Settings > LLM** を開き、同じ Advanced フィールドを更新してください。保存済みの
プロファイルは、チャット入力欄から `/model` コマンドで切り替えることができます。

## 5. ワークスペースを開く

エージェントは、選択したワークスペース内のファイルのみを読み書きできます。タスクを
開始する前に、Agent Canvas にプロジェクトフォルダを指定してください。

1. ホーム画面から **Open Workspace** を選択します。
2. プロジェクトを含むフォルダ(たとえば、エージェントに作業させたい git リポジトリ)
   を選択します。
3. そのワークスペースで新しい会話を開始します。

エージェントが行うすべてのこと(ファイルの読み取り、コマンドの実行、コードの編集)
は、そのワークスペースに限定されます。

![オンボーディング後の Agent Canvas ホーム画面](assets/02-agent-canvas-home.png)

## 6. 最初のコーディングタスクを実行する

ワークスペースを開き、ローカル LLM を選択した状態で、具体的なタスクをチャットに
入力します。最初のタスクとしては、小さく検証しやすいものが適しています。たとえば
次のようなものです。

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

会話のタイムラインを確認してください。OpenHands は次のことを行います。

- ワークスペースを読み取り、構成を把握します。
- 要求された関数とテストブロックを含む `hello.py` を作成します。
- 必要に応じて `python3 hello.py` を実行し、出力を確認します。
- 実行した内容やコマンド出力をチャットで報告します。

ワークスペースに新しいファイルが表示され、エージェントの最終メッセージには、行った
変更内容が説明されているはずです。これが成果の瞬間です。エージェントが実際に
プロジェクトフォルダ内でコードを記述し、実行したのです。

## 7. エージェントの作業を確認し、方向付けする

エージェントがステップを完了したら、次のステップを承認する前にその作業内容を
確認してください。

- **ファイルの変更**: ワークスペースのファイルブラウザやエージェントの diff 表示
  を使って、追加、変更、削除された内容を正確に確認します。
- **コマンド出力**: エージェントが実行したコマンドを展開し、stdout、stderr、
  終了コードを確認します。
- **フォローアップ**: 結果が期待どおりでない場合は、同じ会話内で修正内容を返信
  してください。エージェントは以前の文脈を保持したまま、同じファイルに対して
  反復的に作業を行います。

たとえば、テストが期待どおりの挨拶文を出力しなかった場合は、次のように返信します。

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

エージェントはファイルを再読み込みし、コマンドを実行して問題を診断した上で、
同じ会話の中でファイルを再度編集します。
## トラブルシューティング

<!-- @os:linux -->
- **`agent-canvas` が PATH 上にない場合:** `npm install -g @openhands/agent-canvas` で再インストールし、新しいターミナルから `agent-canvas` を起動できるよう、npm のグローバルバイナリディレクトリが PATH に含まれていることを確認してください。
- **`npm install -g` が権限エラーで失敗する場合:** ユーザー所有のグローバル npm ディレクトリを設定し、ターミナルを開き直してから Agent Canvas を再度インストールしてください。

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` が見つからない場合:** [uv インストールガイド](https://docs.astral.sh/uv/getting-started/installation/)からインストールしてください。Agent Canvas はエージェントサーバーの Python 環境を管理するために `uv` を使用します。
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` または `docker run` が接続に失敗する場合:** Docker Desktop が起動していること(システムトレイにクジラのアイコンが表示されていること)、およびエンジンの起動が完了していることを確認してください。`docker version` を実行すると、Client セクションと Server セクションの両方が表示されるはずです。
- **コンテナは起動するがバックエンドがいつまでも正常にならない場合:** 初回起動時はコンテナ内で Agent Server が初期化されます。1、2分ほど待ってから `docker logs <container>` でエラーを確認してください。
- **コンテナが Lemonade に到達できない場合:** コンテナはホストに `host.docker.internal` 経由で到達します。`lemonade status` で Lemonade が Windows ホスト上で稼働していることを確認し、LLM を設定する際のベース URL として `http://host.docker.internal:13305/api/v1` を使用してください。
<!-- @os:end -->

- **UI は読み込まれるがバックエンドが unhealthy と表示される場合:** エージェントサーバーの起動が完了するまで1、2分待ってから再読み込みしてください。それでも unhealthy のままの場合は、スタックを再起動してログでエラーを確認してください。
- **Lemonade のチャットリクエストが接続エラーで失敗する場合:** `curl -fsS "http://127.0.0.1:13305/api/v1/health"` が成功すること、および `lemonade status` で Lemonade がまだモデルを提供していることを確認してください。
- **エージェントがコンテキスト長やトークン数の上限に関するエラーを出す場合:** 新しい会話を開始し、エージェントが肥大化した履歴を引き継がないようにしてください。それでも頻発する場合は、デフォルトの 65536 より大きな `ctx_size`(例: `ctx_size=131072`)でメモリーが許す範囲で Lemonade を再起動してください。
- **エージェントが低品質または不完全な編集を行う場合:** Lemonade でより大きなモデルに切り替えるか、より小さく具体的なタスクをエージェントに与え、次の変更を依頼する前に完了させてください。

## 次のステップ

- 同じワークスペースでより大きなタスク、例えばユニットテストファイルの追加や既知のバグの修正などを試し、変更を採用する前にエージェントの diff をレビューしてください。
- **Customize** の下で GitHub や Slack などの MCP サーバーを接続すると、エージェントが作業中に issue を読んだり更新を投稿したりできるようになります。
- 複数の LLM プロファイル(高速な小規模モデルとより強力な大規模モデル)を保存しておき、会話の途中で `/model` を使って切り替えてください。
- [OpenHands automations](https://docs.openhands.dev/openhands/usage/automations/overview) に進み、繰り返し発生する開発ループをスケジュールまたはイベントトリガー型のエージェント実行に変えましょう。

## リソース

- [OpenHands ドキュメント](https://docs.openhands.dev/)
- [Agent Canvas 概要](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Agent Canvas セットアップ](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
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