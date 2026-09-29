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
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## 概觀

[OpenHands](https://github.com/All-Hands-AI/OpenHands) 是一款 AI 軟體代理，
能夠撰寫程式碼、執行命令、瀏覽網頁，並在實際工作環境中編輯檔案。您不必再從聊天視窗
複製建議內容，而是直接將代理指向專案資料夾，讓它完成工作：實作功能、修正錯誤、
撰寫測試，或說明程式碼庫。

[Agent Canvas](https://github.com/OpenHands/agent-canvas) 是執行 OpenHands
時建議使用的瀏覽器 UI。單一 `agent-canvas` 命令即可一併啟動代理伺服器、
自動化後端與網頁前端，讓您能透過瀏覽器與代理進行對話。

為了將所有內容保留在您的 AMD 系統上，代理會與 Lemonade Server 所提供的本機模型
溝通。Lemonade 透過與 OpenAI 相容的 API 公開該模型，因此 Agent Canvas
可以像設定任何其他 OpenAI 樣式的端點一樣設定它，同時模型、您的程式碼與對話
內容皆保留在您的機器上。

在本操作手冊中，您將啟動本機模型、啟動 Agent Canvas、將其指向該模型，
並針對實際的專案資料夾執行第一個編碼任務。

## 您將學到什麼

- 如何啟動 Lemonade Server 並確認本機模型能回應聊天請求
- 如何從 npm 套件安裝並啟動 Agent Canvas
- 如何設定 Agent Canvas 以使用本機 Lemonade 模型作為 LLM
- 如何開始 OpenHands 對話，並觀察代理在工作區中編輯檔案與執行命令
- 如何檢視代理所做的變更，並透過後續訊息引導其行為

## 核心概念

| 概念 | 說明 | 在本操作手冊中的定位 |
| --- | --- | --- |
| Lemonade Server | 專為 AMD 硬體打造的本機 LLM 服務平台，公開與 OpenAI 相容的 API。您的資料絕不會離開您的機器。 | 執行驅動代理的模型。 |
| OpenHands | 一款 AI 軟體代理，能在工作區內讀取與編輯檔案、執行 shell 命令並瀏覽網頁。 | 您在聊天中操作的代理。 |
| Agent Canvas | 執行 OpenHands 對話的瀏覽器 UI 與後端，會顯示工具呼叫與檔案變更。 | 啟動整套系統並託管您的對話。 |
| 工作區 | 允許代理讀取與修改的專案資料夾。 | 代理進行編輯與執行命令的目標。 |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> 編碼代理工作流程需要較大的模型與內容視窗才能發揮效益。請至少配置
> 32 GB 的系統記憶體，若使用較大的 GGUF 模型，建議準備 64 GB 或以上。
<!-- @device:end -->

## 設定記憶體配置

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

- 已安裝 Lemonade Server，並能夠提供以下模型服務。

<!-- @os:linux -->
- Node.js 22.12 或更新版本，以及 `npm`（供 `agent-canvas` CLI 使用）。
- `uv`，Agent Canvas 用來管理代理伺服器環境的 Python 套件管理工具。若您的
  系統尚未安裝，請在啟動 Agent Canvas 之前，先從
  [uv 安裝指南](https://docs.astral.sh/uv/getting-started/installation/)
  進行安裝。
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/)，
  已安裝並執行中。在 Windows 上，Agent Canvas 堆疊會透過已發布的 Docker
  映像檔執行，該映像檔已包含 Node.js、`uv` 與 `@openhands/agent-canvas`
  套件，因此您不需要在主機上另行安裝這些項目。
<!-- @os:end -->

- 一個供操作的專案資料夾。這可以是任何本機 git 儲存庫，或您希望代理
  處理的程式碼目錄。

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

## 1. 啟動 Lemonade Server

從 Lemonade CLI 啟動模型：

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **選擇適合您硬體的模型。** `Qwen3.6-35B-A3B-GGUF`（約 20 GB）是一款強大的
編碼模型，但需要較大的記憶體池。若您的裝置記憶體或 GPU VRAM 有限，
請改為從 Lemonade 模型庫中選擇較小的 GGUF 模型，並在本操作手冊中全程使用
該模型 ID。

> **注意：** 第一次執行 `lemonade run` 時，若模型尚未存在，系統會下載該
模型，依模型大小與您的連線速度不同，可能需要一段時間。

Lemonade 會在以下位置公開與 OpenAI 相容的 API：

```text
http://127.0.0.1:13305/api/v1
```

## 2. 驗證本機模型

確認 Lemonade 能夠提供所選模型的服務：

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

接著傳送一個小型聊天請求：

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

若傳回結果中包含 `choices` 陣列，即表示 Lemonade 已準備好供 Agent Canvas 使用。

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
## 3. 安裝並啟動 Agent Canvas

<!-- @os:linux -->
全域安裝已發布的 Agent Canvas 套件：

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

然後從終端機啟動完整堆疊：

```bash
agent-canvas
```

預設情況下，Agent Canvas 會在 `http://localhost:8000` 上啟動。請在瀏覽器中開啟該
網址。此連接埠並無特別之處——如果 8000 已被使用，可在啟動 Agent Canvas 時使用
`--port`（或 `-p`）指定任何可用的連接埠：

```bash
agent-canvas --port 3000
```

然後改為開啟 `http://localhost:3000`。首頁畫面上應顯示預設的本機後端狀態為正常。

`agent-canvas` 指令會一併啟動 agent 伺服器、自動化後端和網頁前端。您只需要
這一個指令，即可在本機執行 OpenHands。

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
在 Windows 上，請使用 Docker Desktop 執行已發布的 Agent Canvas 容器映像檔。
此映像檔已包含 Agent Server、自動化後端和網頁前端，因此您不需要在主機上
安裝 Node.js、`uv` 或 CLI。

首先，建立容器所要掛載的設定與工作區資料夾：

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

提取已發布的映像檔（這是公開的，因此不需要登入）：

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

在瀏覽器中開啟 `http://localhost:8000/canvas`。如果連接埠 8000 已被使用，
請對應到不同的主機連接埠，例如 `-p 8080:8000`，並改為開啟
`http://localhost:8080/canvas`。

> **注意：** 首次啟動時會在容器內初始化 Agent Server，
> 因此後端回報為正常狀態可能需要一兩分鐘的時間。

`.openhands` 掛載會在容器重新啟動後保留您的 LLM 設定檔與設定。本手冊接下來
的內容會透過瀏覽器中的 Agent Canvas UI 來設定一切。

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

## 4. 設定本機 LLM

首次啟動時，Agent Canvas 會開啟新手導覽流程。在該流程中：

1. 保持將 **OpenHands** 選為 agent，並按一下 **Next**。
2. 在 **Set up your LLM** 頁面，選擇 **Advanced**。
3. 保持 **Authentication** 設定為 **API key**。
4. 將 **Custom Model** 設定為 `openai/Qwen3.6-35B-A3B-GGUF`。
5. 將 **Base URL** 設定為 `http://127.0.0.1:13305/api/v1`。
   <!-- @os:windows -->
   > 在 Windows 上，此堆疊是在容器中執行，無法透過
   > `127.0.0.1` 連線到主機。請改用
   > `http://host.docker.internal:13305/api/v1`，讓容器化的 agent 能夠連線到
   > 在 Windows 主機上執行的 Lemonade。
   <!-- @os:end -->
6. 在 **API Key** 欄位中，輸入任何非空白的預留值，例如 `lemonade-local`。
   Lemonade 不需要真實的金鑰，但 OpenHands 用戶端需要一個值才能傳送。
7. 按一下 **Next**。

完成後的 Advanced 設定應如下所示。API 金鑰欄位在 UI 中會被遮蔽。

![Agent Canvas 首次使用的 LLM Advanced 設定，顯示 Lemonade 模型與本機基底網址](assets/01-llm-advanced-settings.png)

Agent Canvas 會將這些值儲存為 LLM 設定檔。如果您的版本要求您為該設定檔命名，
請使用不含空格的名稱，例如 `lemonade-local`。如果之後要變更模型，請開啟
**Settings > LLM** 並更新相同的 Advanced 欄位。您可以在聊天輸入框中使用
`/model` 指令來切換已儲存的設定檔。

## 5. 開啟工作區

agent 只能讀取和修改您所選工作區內的檔案。開始執行任務之前，請將 Agent
Canvas 指向您的專案資料夾：

1. 在首頁畫面中，選擇 **Open Workspace**。
2. 選取包含您專案的資料夾（例如，您希望 agent 處理的 git 儲存庫）。
3. 在該工作區中開始新的對話。

agent 所做的一切——讀取檔案、執行指令、編輯程式碼——都僅限於該工作區範圍內。

![新手導覽完成後的 Agent Canvas 首頁](assets/02-agent-canvas-home.png)

## 6. 執行您的第一個程式撰寫任務

在開啟工作區並選擇本機 LLM 之後，請在聊天中輸入一個具體的任務。一個良好的
起始任務應該規模小且可驗證，例如：

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

觀察對話時間軸。OpenHands 將會：

- 讀取工作區以了解其配置。
- 建立含有所需函式與測試區塊的 `hello.py`。
- 視需要執行 `python3 hello.py` 以驗證輸出結果。
- 在聊天中回報其所做的事情以及任何指令輸出結果。

您應該會看到新檔案出現在工作區中，而 agent 的最終訊息應該會描述它所做的
變更。這是關鍵時刻：agent 在您的專案資料夾中撰寫並執行了真實的程式碼。

## 7. 檢閱與引導 Agent

在 agent 完成一個步驟之後，請先檢閱其工作成果，再接受下一步：

- **檔案變更**：使用工作區檔案瀏覽器或 agent 的差異檢視畫面，
  確切查看新增、變更或刪除的內容。
- **指令輸出**：展開 agent 執行過的任何指令，查看標準輸出、標準錯誤，
  以及結束代碼。
- **後續調整**：如果結果不符合您的期望，可以在同一個對話中回覆並提出修正。
  agent 會保留先前的內容脈絡，並針對相同的檔案進行迭代修改。

例如，如果測試沒有印出預期的問候訊息，可以回覆：

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

agent 會重新讀取檔案、執行指令、診斷問題，並再次編輯該檔案——全部都在
同一個對話中完成。
## 疑難排解

<!-- @os:linux -->
- **`agent-canvas` 未加入 PATH：** 請重新安裝
  `npm install -g @openhands/agent-canvas`，並確認 npm 全域二進位檔目錄
  已加入 PATH，才能在新的終端機中啟動 `agent-canvas`。
- **`npm install -g` 因權限錯誤而失敗：** 請設定一個由使用者擁有的
  全域 npm 目錄，然後重新開啟終端機並再次安裝 Agent Canvas。

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **缺少 `uv`：** 請依照
  [uv 安裝指南](https://docs.astral.sh/uv/getting-started/installation/) 進行安裝。
  Agent Canvas 使用 `uv` 來管理代理伺服器的 Python 環境。
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` 或 `docker run` 無法連線：** 請確認 Docker Desktop
  正在執行中（其鯨魚圖示會出現在系統匣中），並確認引擎已完成啟動。
  `docker version` 應會同時印出 Client 和 Server 兩個區段。
- **容器啟動後，後端一直未變成健康狀態：** 第一次啟動時會在容器內初始化
  Agent Server，請等待一兩分鐘，然後檢查 `docker logs <container>` 是否有錯誤訊息。
- **容器無法連線到 Lemonade：** 容器是透過
  `host.docker.internal` 連線到主機的。請確認 Lemonade 是否在 Windows 主機上以
  `lemonade status` 提供服務，並在設定 LLM 時使用
  `http://host.docker.internal:13305/api/v1` 作為 Base URL。
<!-- @os:end -->

- **UI 已載入但後端顯示不健康：** 請等待一兩分鐘，讓代理伺服器完成啟動，
  然後重新整理頁面。若仍然不健康，請重新啟動整個堆疊並檢查記錄檔中的錯誤。
- **Lemonade 對話請求因連線錯誤而失敗：** 請確認
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` 執行成功，並確認
  Lemonade 是否仍以 `lemonade status` 提供模型服務。
- **代理程式出現與內容長度或權杖限制相關的錯誤訊息：** 請開始一個新的對話，
  以免代理程式攜帶過大的歷史紀錄。若情況持續發生，請以比預設值 65536 更大的
  `ctx_size`（例如 `ctx_size=131072`）重新啟動 Lemonade，前提是記憶體足夠。
- **代理程式產出的編輯品質不佳或不完整：** 請切換到 Lemonade 中較大的模型，
  或給代理程式一個較小、更具體的任務，讓它完成後再要求下一項變更。

## 後續步驟

- 在相同的工作區中嘗試更大型的任務，例如新增單元測試檔案或修復已知的錯誤，
  並在保留變更之前先檢視代理程式的差異內容。
- 在 **Customize** 下連接 MCP 伺服器（例如 GitHub 或 Slack），
  讓代理程式在工作時能夠讀取問題或發佈更新。
- 儲存多個 LLM 設定檔（例如一個快速的小型模型和一個效能更強的大型模型），
  並在對話過程中使用 `/model` 進行切換。
- 接下來可前往 [OpenHands automations](https://docs.openhands.dev/openhands/usage/automations/overview)，
  將重複性的開發流程轉換為排程或事件觸發的代理程式執行作業。

## 資源

- [OpenHands 文件](https://docs.openhands.dev/)
- [Agent Canvas 總覽](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Agent Canvas 設定](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM 設定檔與模型設定](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Lemonade Server 文件](https://lemonade-server.ai/docs)

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