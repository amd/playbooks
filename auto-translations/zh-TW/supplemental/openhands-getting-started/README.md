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

[OpenHands](https://github.com/All-Hands-AI/OpenHands) 是一款 AI 軟體代理程式，
能夠在真實的工作區中撰寫程式碼、執行命令、瀏覽網頁並編輯檔案。您不必再從聊天視窗中
複製建議，而是直接將代理程式指向一個專案資料夾，讓它完成實際工作：實作功能、修正
錯誤、撰寫測試，或解說程式碼庫。

[Agent Canvas](https://github.com/OpenHands/agent-canvas) 是執行 OpenHands 建議
採用的瀏覽器使用者介面。單一 `agent-canvas` 指令即可同時啟動代理伺服器、自動化後端
與網頁前端，讓您能夠透過瀏覽器與代理程式進行對話互動。

為了讓一切都保留在您的 AMD 系統上，代理程式會與由 Lemonade Server 提供服務的本機
模型對話。Lemonade 以相容於 OpenAI 的 API 公開該模型，因此 Agent Canvas 可以像
設定其他 OpenAI 風格的端點一樣設定它，同時模型、您的程式碼與對話內容都會保留在您
的機器上。

在本實作手冊中，您將啟動一個本機模型、啟動 Agent Canvas、將其指向該模型，並針對
一個真實的專案資料夾執行您的第一個程式撰寫任務。

## 您將學到什麼

- 如何啟動 Lemonade Server，並確認本機模型能夠回應聊天請求
- 如何從 npm 套件安裝並啟動 Agent Canvas
- 如何設定 Agent Canvas，使其以本機 Lemonade 模型作為 LLM
- 如何開始一場 OpenHands 對話，並觀察代理程式在工作區中編輯檔案與執行命令
- 如何檢視代理程式所做的變更，並以後續訊息引導它

## 核心概念

| 概念 | 內容 | 在本實作手冊中的定位 |
| --- | --- | --- |
| Lemonade Server | 為 AMD 硬體打造的本機 LLM 服務平台，提供相容於 OpenAI 的 API。您的資料永遠不會離開您的機器。 | 執行驅動代理程式所用的模型。 |
| OpenHands | 一款 AI 軟體代理程式，能在工作區內讀取並編輯檔案、執行 shell 命令，以及瀏覽網頁。 | 您在聊天中驅動的代理程式。 |
| Agent Canvas | 執行 OpenHands 對話的瀏覽器使用者介面與後端，並顯示工具呼叫與檔案變更。 | 啟動整套堆疊並承載您的對話。 |
| 工作區 | 允許代理程式讀取與修改的專案資料夾。 | 代理程式編輯與執行命令的目標。 |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> 程式碼撰寫代理程式的工作流程，受益於較大的模型與內容視窗。請使用至少 32 GB 的
> 系統記憶體，若要使用較大的 GGUF 模型，建議使用 64 GB 或以上。
<!-- @device:end -->

## 設定記憶體配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 檢查軟體更新

<!-- @require:software-update -->
<!-- @device:end -->

## 先決條件


<!-- @os:linux -->
<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here.
     lemonade-chat-windows asserts the model is already downloaded. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

您需要：

- 已安裝且能夠提供以下模型服務的 Lemonade Server。

<!-- @os:linux -->
- Node.js 22.12 或更新版本，以及 `npm`（供 `agent-canvas` CLI 使用）。
- `uv`，一個 Agent Canvas 用來管理代理伺服器環境的 Python 套件管理工具。若您的
  系統尚未安裝此工具，請在啟動 Agent Canvas 之前先依照
  [uv 安裝指南](https://docs.astral.sh/uv/getting-started/installation/) 完成安裝。
<!-- @os:end -->

<!-- @os:windows -->
- [適用於 Windows 的 Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)，
  需已安裝並處於執行狀態。在 Windows 上，Agent Canvas 堆疊是透過已發佈的 Docker
  映像檔執行，該映像檔已內建 Node.js、`uv` 與 `@openhands/agent-canvas` 套件，
  因此您不需要在主機上另行安裝這些項目。
<!-- @os:end -->

- 一個供您作業用的專案資料夾。這可以是任何本機 git 儲存庫，或是您想讓代理程式
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

> **選擇適合您硬體的模型。** `Qwen3.6-35B-A3B-GGUF`（約 20 GB）是一款出色的程式
> 撰寫模型，但需要龐大的記憶體池。若您的裝置記憶體或 GPU VRAM 有限，請改從
> Lemonade 模型庫中選擇較小的 GGUF 模型，並在本實作手冊中全程使用該模型 ID。

> **注意：** 第一次執行 `lemonade run` 時，若模型尚未存在，系統會自動下載該模型，
> 視模型大小與您的網路連線速度，這可能需要一些時間。

Lemonade 會在以下位置公開一個相容於 OpenAI 的 API：

```text
http://127.0.0.1:13305/api/v1
```

## 2. 驗證本機模型

確認 Lemonade 能夠提供所選模型的服務：

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

接著傳送一個簡短的聊天請求：

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

若回傳結果包含一個 `choices` 陣列，表示 Lemonade 已準備好供 Agent Canvas 使用。

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
全域安裝已發佈的 Agent Canvas 套件：

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

接著從終端機啟動完整堆疊：

```bash
agent-canvas
```

預設情況下，Agent Canvas 會在 `http://localhost:8000` 啟動。請在瀏覽器中開啟該
網址。此連接埠並無特別之處——如果 8000 已被使用，啟動 Agent Canvas 時可使用
`--port`（或 `-p`）指定任何空閒的連接埠：

```bash
agent-canvas --port 3000
```

然後改為開啟 `http://localhost:3000`。預設的本機後端應會在首頁顯示為健康狀態。

`agent-canvas` 指令會一併啟動代理伺服器、自動化後端，以及網頁前端。你只需要這
一個指令即可在本機執行 OpenHands。

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
在 Windows 上，請使用 Docker Desktop 執行已發佈的 Agent Canvas 容器映像。該映
像已包含 Agent Server、自動化後端與網頁前端，因此你不需要在主機上安裝
Node.js、`uv` 或 CLI。

首先，建立容器要掛載的設定與工作區資料夾：

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

提取已發佈的映像（它是公開的，不需要登入）：

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

在瀏覽器中開啟 `http://localhost:8000/canvas`。如果 8000 連接埠已被使用，請對
應至不同的主機連接埠，例如 `-p 8080:8000`，然後改為開啟
`http://localhost:8080/canvas`。

> **注意：** 第一次啟動時會在容器內初始化 Agent Server，因此後端可能需要一兩
> 分鐘才會回報為健康狀態。

`.openhands` 掛載會在容器重新啟動後持續保留你的 LLM 設定檔與設定。本手冊其餘
部分將透過瀏覽器中的 Agent Canvas 使用者介面完成所有設定。

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

首次啟動時，Agent Canvas 會開啟引導流程。在該流程中：

1. 保持代理選擇為 **OpenHands**，然後點擊 **Next**。
2. 在 **Set up your LLM** 畫面中，選擇 **Advanced**。
3. 將 **Authentication** 保持設定為 **API key**。
4. 將 **Custom Model** 設定為 `openai/Qwen3.6-35B-A3B-GGUF`。
5. 將 **Base URL** 設定為 `http://127.0.0.1:13305/api/v1`。
   <!-- @os:windows -->
   > 在 Windows 上，此堆疊是在容器中執行，因此無法透過 `127.0.0.1` 連線至主
   > 機。請改用 `http://host.docker.internal:13305/api/v1`，讓容器化的代理
   > 可以連線到在 Windows 主機上執行的 Lemonade。
   <!-- @os:end -->
6. 在 **API Key** 欄位中，輸入任何非空的佔位值，例如 `lemonade-local`。
   Lemonade 不需要真實金鑰，但 OpenHands 用戶端需要傳送一個值。
7. 點擊 **Next**。

完成後的 Advanced 設定應如下所示。API 金鑰欄位會由介面進行遮蔽。

![Agent Canvas 首次使用的 LLM Advanced 設定，搭配 Lemonade 模型與本機 Base URL](assets/01-llm-advanced-settings.png)

Agent Canvas 會將這些值儲存為 LLM 設定檔。如果你的版本要求為該設定檔命名，請
使用不含空格的名稱，例如 `lemonade-local`。如果之後要變更模型，請開啟
**Settings > LLM** 並更新相同的 Advanced 欄位。你可以在聊天輸入框中使用
`/model` 指令切換已儲存的設定檔。

## 5. 開啟工作區

代理只能讀取並修改你所選工作區內的檔案。在開始任務之前，請將 Agent Canvas 指
向你的專案資料夾：

1. 從首頁選擇 **Open Workspace**。
2. 選取包含你專案的資料夾（例如，你希望代理處理的 git 版本庫）。
3. 在該工作區中開始新的對話。

代理所做的一切——讀取檔案、執行指令、編輯程式碼——都限定在該工作區範圍內。

![引導流程完成後的 Agent Canvas 首頁](assets/02-agent-canvas-home.png)

## 6. 執行你的第一個程式撰寫任務

在開啟工作區並選取本機 LLM 後，於聊天中輸入一個具體的任務。一個好的第一個任
務應該是小而可驗證的，例如：

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

觀察對話時間軸。OpenHands 將會：

- 讀取工作區以了解其結構。
- 建立包含所要求函式與測試區塊的 `hello.py`。
- 選擇性地執行 `python3 hello.py` 以驗證輸出結果。
- 在聊天中回報它所做的事以及任何指令輸出結果。

你應該會看到新檔案出現在工作區中，而代理最後的訊息應該會描述它所做的變更。
這是成果展現的時刻：代理在你的專案資料夾中撰寫並執行了真正的程式碼。

## 7. 審查並引導代理

當代理完成一個步驟後，請先審查其工作成果，再接受下一步：

- **檔案變更**：使用工作區檔案瀏覽器或代理的差異檢視，確切了解新增、變更或
  刪除了哪些內容。
- **指令輸出**：展開代理執行的任何指令，以查看標準輸出（stdout）、標準錯誤
  （stderr）以及結束代碼。
- **後續追蹤**：如果結果不是你想要的，可在同一對話中回覆進行修正。代理會保
  留先前的上下文，並針對相同檔案進行迭代。

例如，如果測試沒有印出預期的問候語，可以回覆：

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

代理會重新讀取該檔案、執行指令、診斷問題，並再次編輯該檔案——全部都在同一個
對話中完成。
## 疑難排解

<!-- @os:linux -->
- **`agent-canvas` 不在 PATH 中：** 請重新安裝
  `npm install -g @openhands/agent-canvas`，並在能夠從新的終端機啟動
  `agent-canvas` 之前，確認 npm 全域二進位目錄已加入 PATH。
- **`npm install -g` 因權限錯誤而失敗：** 設定一個使用者擁有的全域 npm 目錄，
  然後重新開啟終端機並再次安裝 Agent Canvas。

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **缺少 `uv`：** 請從
  [uv 安裝指南](https://docs.astral.sh/uv/getting-started/installation/)安裝。
  Agent Canvas 使用 `uv` 來管理代理伺服器的 Python 環境。
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` 或 `docker run` 無法連線：** 請確認 Docker Desktop
  正在執行（系統匣中會有鯨魚圖示），且引擎已完成啟動。
  `docker version` 應該會同時印出 Client 與 Server 區段。
- **容器已啟動但後端一直無法進入健康狀態：** 首次啟動時會在容器內初始化
  Agent Server，請給它一兩分鐘時間，然後檢查 `docker logs <container>`
  是否有錯誤。
- **容器無法連線到 Lemonade：** 容器透過 `host.docker.internal`
  連線到主機。請以 `lemonade status` 確認 Lemonade 正在 Windows 主機上提供服務，
  並在設定 LLM 時使用 `http://host.docker.internal:13305/api/v1` 作為 Base URL。
<!-- @os:end -->

- **UI 已載入但後端顯示不健康：** 請等待一兩分鐘，讓代理伺服器完成啟動，
  然後重新整理。如果仍然不健康，請重新啟動整個堆疊並檢查記錄中的錯誤。
- **Lemonade 聊天請求因連線錯誤而失敗：** 確認
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` 執行成功，
  且 Lemonade 仍以 `lemonade status` 顯示正在提供模型服務。
- **代理出現內容長度或權杖限制錯誤：** 開始一段新的對話，避免代理攜帶過大的歷史紀錄。
  如果問題持續發生，請在記憶體允許的情況下，以比預設 65536 更大的
  `ctx_size`（例如 `ctx_size=131072`）重新啟動 Lemonade。
- **代理產生的編輯品質不佳或不完整：** 請改用 Lemonade 中較大的模型，
  或給代理一個較小且更具體的任務，讓它先完成後再要求下一個變更。

## 後續步驟

- 在相同的工作區中嘗試一個較大的任務，例如新增單元測試檔案或修復已知的錯誤，
  並在保留變更之前先檢視代理的差異內容。
- 在 **Customize** 底下連接 MCP 伺服器（例如 GitHub 或 Slack），
  讓代理在工作時能讀取議題或發佈更新。
- 儲存多個 LLM 設定檔（一個快速的小型模型和一個更強大的大型模型），
  並在對話過程中以 `/model` 在它們之間切換。
- 前往[OpenHands automations](https://docs.openhands.dev/openhands/usage/automations/overview)，
  將重複性的開發循環轉換為排程或事件觸發的代理執行。

## 資源

- [OpenHands 文件](https://docs.openhands.dev/)
- [Agent Canvas 概覽](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Agent Canvas 設定](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM 設定檔與模型配置](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
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