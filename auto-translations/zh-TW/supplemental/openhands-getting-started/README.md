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

## 總覽

[OpenHands](https://github.com/All-Hands-AI/OpenHands) 是一個 AI 軟體代理程式，能夠撰寫程式碼、執行指令、瀏覽網頁，並在實際工作區中編輯檔案。您不再需要從聊天視窗中複製建議，而是直接將代理程式指向一個專案資料夾，讓它去完成工作：實作功能、修復錯誤、撰寫測試，或說明程式碼庫。

[Agent Canvas](https://github.com/OpenHands/agent-canvas) 是執行 OpenHands 建議使用的瀏覽器 UI。單一個 `agent-canvas` 指令即可一起啟動代理程式伺服器、自動化後端與網頁前端，讓您能透過瀏覽器與代理程式進行對話。

為了讓所有東西都保留在您的 AMD 系統上，代理程式會與 Lemonade Server 所提供的本機模型溝通。Lemonade 透過相容於 OpenAI 的 API 公開該模型，因此 Agent Canvas 可以像設定任何其他 OpenAI 風格的端點一樣設定它，同時模型、您的程式碼與對話上下文都會保留在您的機器上。

在此手冊中，您將啟動一個本機模型、啟動 Agent Canvas、將其指向該模型，並針對實際的專案資料夾執行您的第一個程式撰寫任務。

## 您將學到什麼

- 如何啟動 Lemonade Server 並確認本機模型能回應聊天請求
- 如何從 npm 套件安裝並啟動 Agent Canvas
- 如何設定 Agent Canvas 以使用本機的 Lemonade 模型作為 LLM
- 如何啟動 OpenHands 對話，並觀察代理程式在工作區中編輯檔案與執行指令
- 如何檢視代理程式所做的變更，並透過後續訊息來引導它

## 核心概念

| 概念 | 是什麼 | 在此手冊中的定位 |
| --- | --- | --- |
| Lemonade Server | 一個專為 AMD 硬體打造的本機 LLM 服務平台，公開相容於 OpenAI 的 API。您的資料永遠不會離開您的機器。 | 執行驅動代理程式的模型。 |
| OpenHands | 一個 AI 軟體代理程式，能在工作區內讀取與編輯檔案、執行 shell 指令並瀏覽網頁。 | 您透過聊天驅動的代理程式。 |
| Agent Canvas | 執行 OpenHands 對話並顯示工具呼叫與檔案變更的瀏覽器 UI 與後端。 | 啟動整個堆疊並承載您的對話。 |
| 工作區 | 允許代理程式讀取與修改的專案資料夾。 | 代理程式編輯與執行指令的目標。 |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> 程式撰寫代理程式的工作流程受益於較大的模型與內容視窗（context window）。請至少使用 32 GB 的系統記憶體，若要使用較大的 GGUF 模型，建議使用 64 GB 以上。
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

- 已安裝 Lemonade Server，並能夠提供下方的模型服務。

<!-- @os:linux -->
- Node.js 22.12 或更新版本，以及 `npm`（供 `agent-canvas` CLI 使用）。
- `uv`，這是 Agent Canvas 用來管理代理程式伺服器環境的 Python 套件管理工具。若您的系統尚未安裝，請在啟動 Agent Canvas 之前，先從
  [uv 安裝指南](https://docs.astral.sh/uv/getting-started/installation/) 進行安裝。
<!-- @os:end -->

<!-- @os:windows -->
- [適用於 Windows 的 Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)，
  已安裝並正在執行。在 Windows 上，Agent Canvas 堆疊是從已發佈的 Docker 映像檔執行，該映像檔已包含 Node.js、`uv` 與
  `@openhands/agent-canvas` 套件，因此您不需要在主機上另行安裝這些項目。
<!-- @os:end -->

- 一個供您作業的專案資料夾。這可以是任何本機 git 儲存庫，或您希望代理程式進行處理的程式碼目錄。

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

> **選擇適合您硬體的模型。**`Qwen3.6-35B-A3B-GGUF`（約 20 GB）是一個強大的程式撰寫模型，但需要大量的記憶體池。若您的裝置記憶體或 GPU VRAM 有限，請改為從 Lemonade 模型庫中選擇較小的 GGUF 模型，並在本手冊中全程使用該模型 ID。

> **注意：**第一次執行 `lemonade run` 時，若模型尚未存在，就會下載該模型，視模型大小與您的網路連線速度，這可能需要一些時間。

Lemonade 會公開一個相容於 OpenAI 的 API，位址為：

```text
http://127.0.0.1:13305/api/v1
```

## 2. 驗證本機模型

確認 Lemonade 能夠提供所選模型的服務：

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

接著送出一個小型的聊天請求：

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

若此請求回傳一個 `choices` 陣列，代表 Lemonade 已準備好供 Agent Canvas 使用。

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

接著從終端機啟動完整的堆疊：

```bash
agent-canvas
```

預設情況下，Agent Canvas 會在 `http://localhost:8000` 啟動。請在瀏覽器中開啟該
URL。此連接埠並無特殊意義——如果 8000 已被使用，啟動 Agent Canvas 時可透過
`--port`（或 `-p`）傳入任何可用的連接埠：

```bash
agent-canvas --port 3000
```

接著改為開啟 `http://localhost:3000`。首頁畫面上，預設的本機後端應顯示為健康狀態。

`agent-canvas` 指令會一併啟動代理伺服器、自動化後端與網頁前端。您只需要這一個
指令即可在本機執行 OpenHands。

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
在 Windows 上，使用 Docker Desktop 執行已發布的 Agent Canvas 容器映像檔。
該映像檔內含 Agent Server、自動化後端與網頁前端，因此您不需要在主機上安裝
Node.js、`uv` 或 CLI。

首先，建立容器要掛載的設定與工作區資料夾：

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

提取已發布的映像檔（此映像檔為公開，因此不需要登入）：

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

接著啟動堆疊：

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
> 因此後端回報健康狀態前可能需要一兩分鐘。

`.openhands` 掛載可讓您的 LLM 設定檔與設定值在容器重新啟動後仍保持不變。
本操作手冊接下來的內容，都透過瀏覽器中的 Agent Canvas UI 進行設定。

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

首次啟動時，Agent Canvas 會開啟一個入門引導流程。在該流程中：

1. 保持 **OpenHands** 為選定的代理，然後按一下 **Next**。
2. 在 **Set up your LLM** 畫面上，選擇 **Advanced**。
3. 保持 **Authentication** 設定為 **API key**。
4. 將 **Custom Model** 設定為 `openai/Qwen3.6-35B-A3B-GGUF`。
5. 將 **Base URL** 設定為 `http://127.0.0.1:13305/api/v1`。
   <!-- @os:windows -->
   > 在 Windows 上，此堆疊是在容器中執行，無法透過 `127.0.0.1` 存取主機。
   > 請改用 `http://host.docker.internal:13305/api/v1`，讓容器化的代理
   > 可以連線到在 Windows 主機上執行的 Lemonade。
   <!-- @os:end -->
6. 在 **API Key** 欄位，輸入任何非空白的預留值，例如 `lemonade-local`。
   Lemonade 不需要真正的金鑰，但 OpenHands 用戶端需要一個值才能傳送。
7. 按一下 **Next**。

完成後的 Advanced 設定應如下所示。API 金鑰欄位在 UI 中會被遮蔽。

![Agent Canvas 首次使用的 LLM Advanced 設定，包含 Lemonade 模型與本機基礎 URL](assets/01-llm-advanced-settings.png)

Agent Canvas 會將這些值儲存為 LLM 設定檔。如果您的版本要求您為該設定檔命名，
請使用不含空格的名稱，例如 `lemonade-local`。如果之後想更換模型，請開啟
**Settings > LLM** 並更新相同的 Advanced 欄位。您可以在聊天輸入框中使用
`/model` 指令切換已儲存的設定檔。

## 5. 開啟工作區

代理只能讀取與修改您所選工作區內的檔案。在開始工作前，請將 Agent Canvas
指向您的專案資料夾：

1. 在首頁畫面中，選擇 **Open Workspace**。
2. 選取包含您專案的資料夾（例如您想讓代理處理的某個 git 儲存庫）。
3. 在該工作區中開始新的對話。

代理所做的每一件事——讀取檔案、執行指令、編輯程式碼——都僅限於該工作區範圍內。

![完成引導流程後的 Agent Canvas 首頁](assets/02-agent-canvas-home.png)

## 6. 執行您的第一個程式撰寫任務

在工作區開啟且已選定本機 LLM 的狀態下，在聊天視窗中輸入一個具體的任務。
一個好的第一個任務應該規模小且可驗證，例如：

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

觀察對話時間軸。OpenHands 會：

- 讀取工作區以了解其結構。
- 建立包含所要求函式與測試區塊的 `hello.py`。
- 選擇性地執行 `python3 hello.py` 以驗證輸出。
- 在聊天中回報它所做的事以及任何指令輸出。

您應該會看到工作區中出現新檔案，而代理的最終訊息應該會描述它所做的變更。
這是成果展現的時刻：代理在您的專案資料夾中撰寫並執行了真實的程式碼。

## 7. 檢閱並引導代理

代理完成一個步驟後，在接受下一步之前請先檢閱其成果：

- **檔案變更**：使用工作區檔案瀏覽器或代理的差異檢視畫面，查看究竟新增、
  變更或刪除了什麼內容。
- **指令輸出**：展開代理執行過的任何指令，查看標準輸出、標準錯誤與結束代碼。
- **後續調整**：如果結果不符合您的期望，請在同一個對話中回覆修正內容。
  代理會保留先前的內容脈絡，並在相同的檔案上繼續進行。

例如，如果測試沒有印出預期的問候語，請回覆：

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

代理會重新讀取檔案、執行指令、診斷問題，並再次編輯該檔案——所有動作都在
同一個對話中完成。
## 疑難排解

<!-- @os:linux -->
- **`agent-canvas` 不在 PATH 中：** 重新安裝
  `npm install -g @openhands/agent-canvas`，並確認 npm 全域二進位檔目錄
  已加入 PATH，之後才能從新的終端機啟動 `agent-canvas`。
- **`npm install -g` 因權限錯誤而失敗：** 設定一個由使用者擁有的
  npm 全域目錄，然後重新開啟終端機並再次安裝 Agent Canvas。

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **找不到 `uv`：** 請依照
  [uv 安裝指南](https://docs.astral.sh/uv/getting-started/installation/) 進行安裝。
  Agent Canvas 使用 `uv` 來管理代理伺服器的 Python 環境。
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` 或 `docker run` 無法連線：** 請確認 Docker Desktop
  正在執行（其鯨魚圖示會顯示在系統匣中），且引擎已完成啟動。
  `docker version` 應該同時印出 Client 與 Server 兩個區段。
- **容器已啟動但後端一直未變為健康狀態：** 首次啟動時會在容器內
  初始化 Agent Server，請等候一到兩分鐘，然後檢查
  `docker logs <container>` 是否有錯誤。
- **容器無法連上 Lemonade：** 容器是透過
  `host.docker.internal` 連到主機的。請確認 Lemonade 是否正在
  Windows 主機上以 `lemonade status` 提供服務，並在設定 LLM 時
  使用 `http://host.docker.internal:13305/api/v1` 作為 Base URL。
<!-- @os:end -->

- **UI 已載入但後端顯示為不健康：** 請等候一到兩分鐘讓代理伺服器
  完成啟動，然後重新整理。若仍然不健康，請重新啟動整個服務堆疊
  並檢查記錄檔中是否有錯誤。
- **Lemonade 聊天請求因連線錯誤而失敗：** 請確認
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` 執行成功，
  且 Lemonade 仍以 `lemonade status` 提供該模型服務。
- **代理程式回報內容長度或權杖限制錯誤：** 請開始新的對話，
  以免代理程式攜帶過大的歷史紀錄。若情況持續發生，請以大於
  預設值 65536 的 `ctx_size`（例如 `ctx_size=131072`）重新啟動
  Lemonade，前提是記憶體充足。
- **代理程式產生的編輯品質低落或不完整：** 請切換至 Lemonade 中
  較大的模型，或給代理程式一個較小、較具體的任務，等其完成後
  再要求下一項變更。

## 後續步驟

- 在相同的工作區中嘗試更大型的任務，例如新增單元測試檔案或
  修復已知的錯誤，並在保留變更前檢視代理程式的差異內容。
- 在 **Customize** 底下連接 MCP 伺服器（例如 GitHub 或 Slack），
  讓代理程式在運作時能讀取議題或發佈更新。
- 儲存多個 LLM 設定檔（一個快速的小型模型，以及一個能力更強的
  大型模型），並在對話過程中以 `/model` 進行切換。
- 前往 [OpenHands automations](https://docs.openhands.dev/openhands/usage/automations/overview)，
  將重複性的開發流程轉換為排程或事件觸發的代理程式執行作業。

## 資源

- [OpenHands 說明文件](https://docs.openhands.dev/)
- [Agent Canvas 總覽](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Agent Canvas 設定](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM 設定檔與模型組態](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Lemonade Server 說明文件](https://lemonade-server.ai/docs)

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