<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機器翻譯。**本頁面是由英文自動翻譯而成，尚未經過人工審閱。內容可能包含錯誤，且某些指示、命令、下載項目、產品供應情況或其他內容可能因語言或地區而異。如本文件與英文版本之間存在任何不一致或差異，應以該 playbook 之英文原始版本為準。
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## 總覽

開發者花費大量時間在小型且重複的循環工作上：審查已標記的 pull request、回覆 GitHub 留言、篩選新的 issue、將 Slack 討論串轉換為每日站立會議記錄或事故後續追蹤，以及追蹤發佈或研究相關訊號。
每個循環都很熟悉，但仍需要判斷力：蒐集正確的內容脈絡、決定哪些事項重要，並在團隊已在使用的地方張貼清楚的更新。

[OpenHands automations](https://docs.openhands.dev/openhands/usage/automations/overview) 將這些循環轉變為排程式或事件觸發式的代理對話：也就是讓 AI 軟體代理可以讀取內容脈絡、呼叫工具，並產生更新的執行過程。
OpenHands 擴充功能目錄中共用的自動化範本，針對 GitHub pull request 審查、儲存庫監控、Linear issue 篩選、事故回顧、Slack 每日站立會議摘要以及研究簡報，遵循同一種模式：自動化被喚醒後，使用像 GitHub 或 Slack 這類已設定的整合服務來取得內容脈絡，透過大型語言模型（LLM）針對這些內容脈絡進行推理，並將結果寫回。

[Agent Canvas](https://github.com/OpenHands/agent-canvas) 是用來建置與測試這些自動化的本機控制平台。
在本教學中，它負責執行 OpenHands Agent Server（也就是執行代理對話的後端程序），並將代理連接到 GitHub 與 Slack 等外部服務。

為了讓整個工作流程留在您的 AMD 系統上，代理會與 Lemonade Server 所提供的本機模型進行溝通。
Lemonade 透過與 OpenAI 相容的 API 公開該模型，因此 Agent Canvas 可以像設定遠端的 OpenAI 風格端點一樣進行設定，同時模型、提示詞與工作流程內容脈絡都保留在本機。

在本教學中，您將建置一個具體的自動化：排程式的 GitHub 到 Slack 開發摘要。
它使用 GitHub 檢視最近的儲存庫活動、Slack 張貼摘要、Agent Canvas API 呼叫來設定與測試自動化，以及 Lemonade 在本機執行 LLM。

![顯示 GitHub MCP、OpenHands automation、Lemonade Server 與 Slack MCP 的架構圖](assets/00-architecture-overview.png)

## 您將學到什麼

- 如何啟動 Lemonade Server 並驗證本機模型能回應聊天請求
- 如何啟動 Agent Canvas 並將其 Agent Server 指向本機 LLM
- 如何透過 Agent Server API 安裝 GitHub 與 Slack Model Context Protocol（MCP）伺服器
- 如何建立並派送排程式的 OpenHands automation，將開發摘要張貼到 Slack
- 如何排解最常見的本機模型與自動化失敗問題

## 核心概念

| 概念 | 說明 | 在本教學中的角色 |
| --- | --- | --- |
| Lemonade Server | 專為 AMD 硬體打造、公開與 OpenAI 相容 API 的本機 LLM 服務平台。您的資料絕不會離開您的機器。 | 執行為代理提供動力的模型。 |
| OpenHands Agent Server | 執行 OpenHands 代理對話的後端程序。 | 承載代理、其 LLM 設定檔以及其 MCP 伺服器。 |
| Agent Canvas | OpenHands 的本機控制平台，執行 Agent Server 以及用於檢視代理執行情況的 UI。 | 啟動後端服務並提供您呼叫的 API。 |
| MCP 伺服器 | 讓代理能取得像 GitHub 或 Slack 這類外部服務工具的 Model Context Protocol 伺服器。 | 讓代理能讀取 GitHub 並寫入 Slack。 |
| OpenHands automation | 一種排程式或事件觸發式的代理對話，會取得內容脈絡、進行推理，並將結果寫到某處。 | 您在此建置的 GitHub 到 Slack 摘要。 |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> 程式碼撰寫代理工作流程受益於較大的模型與內容脈絡視窗。
> 請至少使用 32 GB 的系統記憶體，對於較大的 GGUF 模型，建議使用 64 GB 以上。
<!-- @device:end -->

## 設定記憶體組態

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 檢查軟體更新

<!-- @require:software-update -->
<!-- @device:end -->

## 先決條件

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- @os:end -->

您需要：

- 依照標準的 [Lemonade 安裝指南](https://lemonade-server.ai/docs/guide/install/) 安裝 Lemonade Server。

<!-- @os:linux -->
- Node.js 22.12 或更新版本以及 `npm`，用於安裝已發佈的 Agent Canvas CLI，並透過 `npx` 執行 MCP 伺服器。
- `uv`，Agent Canvas 用來建置 Agent Server 環境的 Python 套件管理工具。若尚未安裝，請從 [uv 安裝指南](https://docs.astral.sh/uv/getting-started/installation/) 進行安裝。
- 最新發佈版本的 `@openhands/agent-canvas` 套件，具備結構描述（schema）驅動的代理設定、`LLMSummarizingCondenserSettings.max_tokens`，以及 LLM 的 `custom_tokenizer` 支援。
- Agent Server 環境中須提供 Python 的 `transformers` 套件。當設定 `custom_tokenizer` 時，這是進行聊天範本（chat-template）權杖計數所必需的。
<!-- @os:end -->

<!-- @os:windows -->
- 已安裝並執行中的 [適用於 Windows 的 Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)。在 Windows 上，Agent Canvas 堆疊會從已發佈的 Docker 映像檔執行，其中已包含 Node.js、`uv`、`transformers` 以及 `@openhands/agent-canvas` 套件，因此您不需要在主機上另行安裝這些項目。
<!-- @os:end -->

- 具有對欲摘要之儲存庫讀取權限的 GitHub token。
- 具有 `chat:write` 與頻道讀取權限的 Slack bot token（`xoxb-...`）。
- Slack 團隊 ID（`T...`）。
- 應張貼摘要之 Slack 頻道 ID（`C...`）。

在測試自動化之前，請先將 Slack 應用程式邀請加入目標頻道。
## 本手冊使用的變數

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

以下驗證指令會使用這兩個變數。
模型、tokenizer 及其他 LLM 設定會在後續步驟中直接輸入 Agent Canvas UI，因此在需要用到的地方會以字面值直接顯示。

以下的值會在後續步驟中輸入 Agent Canvas UI。
請先在此設定好，之後即可直接複製使用：

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

請為 `GITHUB_REPO_FILTER` 使用明確的 `owner/repo` 值。
過於廣泛的組織萬用字元可能會回傳過多 MCP 內容給本地模型。

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. 啟動 Lemonade Server

從 Lemonade CLI 啟動模型：

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

> **選擇適合您硬體的模型。** `Qwen3.6-35B-A3B-GGUF`（約 20 GB）是此工作流程中一個表現強勁的模型，但需要較大的記憶體池。
> 若您的裝置記憶體或 GPU VRAM 有限，請從 Lemonade 模型庫中選擇較小的 GGUF 模型，並在本手冊全程使用該模型 ID（及其對應的 tokenizer）。

> **注意：** 第一次執行 `lemonade run` 時，若模型尚未存在，系統會下載該模型，依模型大小及您的網路連線速度，這可能需要一段時間。

Lemonade 會在以下位置公開一個相容 OpenAI 的 API：

```text
http://127.0.0.1:13305/api/v1
```

選用：若 Agent Canvas 或自動化執行器不在同一台機器上，請透過安全通道公開 Lemonade 端點，並使用該 HTTPS URL 作為 LLM base URL。
[ngrok](https://ngrok.com/) 可透過安全的 HTTPS URL 將本機連接埠公開至網際網路；它需要免費的 ngrok 帳號，請將 `YOUR_NGROK_DOMAIN.ngrok-free.dev` 替換為您自己保留的網域：

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. 驗證本地模型

確認 Lemonade 能夠提供所選模型的服務：

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

然後傳送一個小型聊天請求：

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

然後傳送一個小型聊天請求：

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

若回傳結果包含 `choices` 陣列，即表示 Lemonade 已準備好供 Agent Canvas 使用。

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

## 3. 啟動 Agent Canvas

<!-- @os:linux -->
安裝已發布的 Agent Canvas 套件並啟動完整堆疊：

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

若全域 npm 安裝因權限錯誤而失敗，請參閱下方的 npm 權限疑難排解項目。

依預設，Agent Canvas 會在 `http://localhost:8000` 啟動。
請在瀏覽器中開啟該 URL。
此連接埠並非固定必用——若 8000 已被占用，可透過 `--port`（或 `-p`）指定任何空閒的連接埠。
預設的本地後端應在首頁顯示為健康狀態。

> **注意：** 第一次啟動時會建置 Agent Server 由 `uv` 管理的 Python 環境，因此後端回報健康狀態前可能需要幾分鐘時間。

`agent-canvas` 指令會一併啟動 agent server、自動化後端及網頁前端。
您只需要這一個指令即可在本地執行 OpenHands。
本手冊其餘部分將透過瀏覽器中的 Agent Canvas UI 完成所有設定。
<!-- @os:end -->

<!-- @os:windows -->
在 Windows 上，請使用 Docker Desktop 執行已發布的 Agent Canvas 容器映像檔。
該映像檔已內含 Agent Server、自動化後端及網頁前端，因此您不需要在主機上安裝 Node.js、`uv` 或 CLI。

首先，建立容器要掛載的設定與工作區資料夾：

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

拉取已發布的映像檔（約 6 GB；此映像檔為公開，無需登入）：

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

然後啟動堆疊：

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

在瀏覽器中開啟 `http://localhost:8000/canvas`。
若連接埠 8000 已被占用，請對應到其他主機連接埠，例如 `-p 8080:8000`，並改為開啟 `http://localhost:8080/canvas`。

> **注意：** 第一次啟動時會在容器內建置 Agent Server 環境，因此後端回報健康狀態前可能需要幾分鐘時間。

`.openhands` 掛載點會在容器重新啟動之間保留您的 LLM 設定檔、MCP 伺服器及自動化設定。
本手冊其餘部分將透過瀏覽器中位於 `http://localhost:8000/canvas` 的 Agent Canvas UI 完成所有設定。
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
## 4. 在 UI 中配置本機 LLM

首次啟動時，Agent Canvas 會開啟新手導覽流程。
在該流程中：

1. 保持 **OpenHands** 為選定的代理，然後點擊 **Next**。
2. 在 **Set up your LLM** 頁面，選擇 **Advanced**。
3. 保持 **Authentication** 設為 **API key**。
4. 將 **Custom Model** 設定為 `openai/Qwen3.6-35B-A3B-GGUF`。
5. 將 **Base URL** 設定為 `http://127.0.0.1:13305/api/v1`。
6. 對於 **API Key**，輸入任何非空的預留值，例如 `lemonade-local`。Lemonade 不需要真正的金鑰，但 OpenHands 客戶端需要一個值才能傳送。

<!-- @os:windows -->
> **Windows（Docker）：** 由於 Agent Server 是在容器內執行，因此請將 **Base URL** 設定為 `http://host.docker.internal:13305/api/v1`，而不是 `http://127.0.0.1:13305/api/v1`。
> 從容器內部來看，`127.0.0.1` 指的是容器本身；`host.docker.internal` 則可連線到執行於 Windows 主機上的 Lemonade，而 Docker Desktop 會自動提供這個主機名稱。
<!-- @os:end -->

連線欄位應如下所示。
API 金鑰欄位會被 UI 遮蔽。

![Agent Canvas 首次使用時的 LLM Advanced 設定，包含 Lemonade 模型與本機基底 URL](assets/01-llm-advanced-settings.png)

接著選擇 **All**，並設定額外的本機模型欄位：

1. 捲動至 **Custom Tokenizer**，並設定為 `Qwen/Qwen3.6-35B-A3B`。
2. 捲動至 **LiteLLM Extra Body**，並設定為 `{"enable_thinking": true}`。
3. 點擊 **Next**。

![Agent Canvas 首次使用時的 LLM All 分頁，包含 Qwen 自訂 tokenizer](assets/02-llm-all-tokenizer-settings.png)

![Agent Canvas 首次使用時的 LLM All 分頁，已配置 LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

LLM 設定應顯示為：

| 欄位 | 值 |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

`openai/` 前綴會告訴 LiteLLM 使用與 OpenAI 相容的請求格式，向 Lemonade 端點發出請求。
自訂 tokenizer 是該 GGUF 模型原始的 Hugging Face tokenizer；它讓 OpenHands 能夠計算與本機模型伺服器所見相同的聊天範本 token 數量。
目前的首次使用 LLM 表單並未顯示 condenser 設定。
如果您的 Agent Canvas 版本之後在 **Settings > LLM** 下開放了 condenser 設定，請使用 `llm_summarizing`，並將最大 token 數設定為低於 Lemonade 內容視窗（context window）的值，例如 `56000`。

## 5. 安裝 GitHub 與 Slack MCP 伺服器

在 Agent Canvas UI 中，開啟 **Customize**（或 **Settings > MCP**），以新增能為代理提供 GitHub 與 Slack 工具的 MCP 伺服器。
權杖（token）值僅會傳送至您本機的 Agent Server，並以加密設定的形式保存。

<!-- @os:windows -->
> **Windows（Docker）：** 下方的 `npx` MCP 伺服器指令會在容器內執行，而容器已內建 Node.js，因此主機上不需要額外安裝任何東西。
> 由於 `.openhands` 已掛載，MCP 伺服器及其權杖會在容器重新啟動後仍然保留。
<!-- @os:end -->

### GitHub MCP 伺服器

以下列設定新增一個新的 MCP 伺服器：

| 欄位 | 值 |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = 您的 GitHub 權杖 |

請使用對您想摘要的儲存庫具有讀取權限的 GitHub 權杖。

### Slack MCP 伺服器

以下列設定新增第二個 MCP 伺服器：

| 欄位 | 值 |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = 您的摘要頻道 ID |

請將 `SLACK_CHANNEL_IDS` 設定為摘要頻道的 ID（與 `SLACK_DIGEST_CHANNEL` 相同的值），這樣代理就不需要逐一翻閱每個 Slack 頻道。

新增兩個伺服器後，請使用每個伺服器上的 **Test** 按鈕確認其能夠連線並宣告可用的工具。
GitHub 伺服器應列出 GitHub 工具，而 Slack 伺服器應列出 Slack 工具。

![已安裝 GitHub 與 Slack 伺服器的 Agent Canvas MCP 頁面](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. 建立摘要自動化流程

在 Agent Canvas UI 中，開啟 **Automations** 頁面並建立一個新的自動化流程：

1. 選擇 **Create automation**，並選取 **Prompt preset** 類型。
2. 將 **Name** 設定為 `GitHub Development Digest to Slack`。
3. 將 **Prompt** 設定為以下文字，並將儲存庫與頻道的預留位置替換為您的實際值：

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

4. 將 **Trigger** 設定為 **Cron**，排程設為 `0 9 * * 1-5`（工作日上午 9 點），並將 **Timezone** 設定為您所在的時區，例如 `America/New_York`。
5. 將 **Timeout** 設定為 `900` 秒。
6. 儲存此自動化流程。

自動化流程詳細頁面會顯示新建立的自動化流程，包含其 cron 觸發條件與產生的 prompt-preset 進入點。

![建立後的 Agent Canvas 自動化流程詳細頁面](assets/05-automation-created.png)
## 7. 測試自動化流程

在 Agent Canvas UI 的自動化詳細資料頁面：

1. 點擊 **Run now**（或 **Dispatch**）以立即執行一次自動化流程。
2. 觀察同一頁面上的執行清單。最新的執行應會轉變為 `COMPLETED`。
3. 開啟你的目標 Slack 頻道，應該會看到產生的摘要。

你不需要等待 cron 排程觸發——**Run now** 會依需求觸發一次執行，讓你可以在依賴排程之前，先確認提示詞、MCP 連線以及 Slack 發佈都能正常運作。

![Agent Canvas automation run completed successfully](assets/06-automation-run-completed.png)

![Slack channel showing the generated OpenHands digest](assets/07-slackbot-message.png)

## 疑難排解

<!-- @os:windows -->
- **Docker port 8000 已被使用：** 對應到不同的主機通訊埠，例如 `docker run ... -p 8080:8000 ...`，然後開啟 `http://localhost:8080/canvas`。
- **`docker pull` 因憑證錯誤而失敗**（例如「A specified logon session does not exist」）：從互動式 Windows 工作階段執行拉取，或預先拉取映像檔。此映像檔為公開映像檔，因此不需要 `docker login`。
- **UI 已載入但後端狀態不健康：** 首次啟動時會在容器內建置 Agent Server 環境。請稍候一分鐘後重新整理，並檢查 `docker logs <container>` 以查看進度。
- **Agent Canvas 無法從容器連線到 Lemonade：** 將 LLM 的 **Base URL** 設定為 `http://host.docker.internal:13305/api/v1`（而非 `127.0.0.1`），並確認 Lemonade 正在 Windows 主機上執行。
<!-- @os:end -->

- **Lemonade 已停止運作：** 使用步驟 1 中的 `lemonade run "${LEMONADE_MODEL}"` 指令重新啟動它，然後重新執行健康狀態檢查。
- **`npm install -g` 因權限錯誤而失敗：** 在 Linux 或 WSL 上，設定一個屬於使用者的全域 npm 目錄，將其加入到 shell 啟動檔案中，然後重新安裝 Agent Canvas：

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

若你使用 `zsh`，請將相同的 `export PATH=...` 這一行加入到 `~/.zshrc`，而非 `~/.bashrc`。
- **設定 `custom_tokenizer` 後，Agent Canvas 拒絕接受 LLM 設定：** 在 Agent Server 的 Python 環境中安裝 `transformers`，如有需要請重新啟動 Agent Canvas，然後重試儲存 LLM 設定。當設定 `custom_tokenizer` 時，OpenHands 需要 Transformers 才能載入 tokenizer 的聊天範本。
- **Agent Canvas 無法連線到 Lemonade：** 驗證 `curl -fsS "${LEMONADE_BASE_URL}/health"`，並確認你在首次使用的 LLM 表單或 **Settings > LLM** 中輸入的基本 URL，與正在執行的本機端點或 HTTPS 通道一致。
- **LLM 設定未儲存：** 確認你在輸入數值後已點擊 **Next**。重新開啟 **Settings > LLM** 以確認數值是否已持久保存。
- **GitHub MCP 無法看見私有儲存庫：** 確認 GitHub token 對目標儲存庫具有讀取權限，且 **Customize** 中的 MCP **Test** 按鈕能顯示出 GitHub 工具。
- **Slack 可以讀取頻道但無法發佈：** 將 Slack 應用程式邀請至目標頻道，並確認該機器人擁有 `chat:write` 權限。
- **自動化流程列出過多 Slack 頻道：** 使用 Slack 頻道 ID，並在 **Customize** 中於 Slack MCP 伺服器上設定 `SLACK_CHANNEL_IDS`。
- **自動化執行失敗或超出內容長度限制：** 確認 Lemonade 是以 `ctx_size=65536` 啟動的，確認 OpenHands LLM 已設定 `custom_tokenizer`，並使用明確指定的儲存庫，將 GitHub 結果集上限設為 3 到 5 個項目。如果你的 Agent Canvas 版本有提供壓縮器（condenser）設定，請將壓縮器的最大 token 數設定為低於 Lemonade 的內容視窗大小。

## 後續步驟

- 新增每週僅限發佈版本的摘要。
- 新增由 GitHub 事件觸發的自動化流程，以取得更快速的 PR 或推送提醒。
- 將相同的摘要傳送至 Notion、Linear 或其他以 MCP 為基礎的工具。

## 資源

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