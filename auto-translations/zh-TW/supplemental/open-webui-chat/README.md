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
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> 此手冊至少需要 **32GB** 的系統記憶體。
<!-- @device:end -->

## 概觀

[Open WebUI](https://docs.openwebui.com) 是一個自架、以瀏覽器為基礎的介面，提供熟悉的聊天機器人體驗，同時作為一個或多個 AI 模型伺服器的前端。Open WebUI 不受限於單一供應商，而是可以連接到**任何提供 OpenAI 相容 API 的後端**，因此你可以在不切換 UI 的情況下更換模型與功能。

在此手冊中，我們使用 [**Lemonade**](https://lemonade-server.ai) 作為後端，因為它提供了**統一的 OpenAI 相容端點**，支援多種模態：
- **大型語言模型 (LLMs)** 用於文字生成
- **視覺模型** 用於圖像理解
- **Stable Diffusion** 用於圖像生成
- **語音轉錄模型** 用於語音轉文字

此設定讓你能夠端到端地探索**完整的多模態工作流程**。

---

## 你將學到什麼

完成後，你將能夠：

- 將 Open WebUI 連接到本地的 OpenAI 相容後端 (Lemonade)
- 透過瀏覽器與本地 LLM 對話
- 上傳圖像並向視覺模型詢問相關問題
- 使用 Stable Diffusion 模型（SDXL-Turbo / SDXL）從文字提示生成圖像
- 理解其運作模式，以便你能使用其他後端（Ollama、vLLM、llama.cpp server 等）

---

## 核心概念（運作模式）

### 三個組成部分

| 部分 | 作用 | 範例 |
|---|---|---|
| 前端 (UI) | 你互動的網頁應用程式 | Open WebUI |
| 後端（模型伺服器） | 託管模型並公開 HTTP 端點 | Lemonade、Ollama、vLLM、llama.cpp server、OpenAI 相容伺服器 |
| 模型 | 實際的 LLM／視覺／擴散／音訊模型 | CodeLlama、DeepSeek、Gemma-MM、SDXL、SD-Turbo、Whisper |

#### 為什麼「OpenAI 相容 API」很重要

Open WebUI 是圍繞標準的 OpenAI 風格端點所建構的，例如：
  - 聊天：`/chat/completions`
  - 模型清單：`/models`
  - 圖像生成：`/images/generations`
  - 語音轉錄：`/audio/transcriptions`

Lemonade 在 `http://localhost:13305/api/v1/...` 下公開這些端點

如果後端支援這些端點，Open WebUI 就能以最少的設定與其溝通。這就是為什麼我們可以在不改變工作流程的情況下切換後端。

#### 兩個服務，兩個埠

在此手冊中，你將使用兩個獨立的服務：

| 服務 | URL | 你在此做什麼 |
|---|---|---|
| **Lemonade**（GUI） | `http://localhost:13305` | 瀏覽、下載並管理模型 |
| **Open WebUI** | `http://localhost:8080` | 聊天、上傳圖像、生成圖像——面向使用者的 UI |

Lemonade 執行模型；Open WebUI 是你互動的介面。請先使用 Lemonade GUI 下載你的模型，然後從 Open WebUI 中使用它們。

---

## 設定記憶體配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 檢查軟體更新

<!-- @require:software-update -->
<!-- @device:end -->

## 一次性設定

此手冊需要 Lemonade 作為後端執行，在 Linux 上還需要容器引擎（Podman）來執行 Open WebUI。請先完成這些設定，再安裝 Open WebUI。

<!-- @os:windows -->
<!-- @device:halo_box,halo,stx,krk -->
<!-- @require:lemonade -->
<!-- @device:end -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver,lemonade -->
<!-- @device:end -->
---
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
<!-- @require:lemonade,podman -->
<!-- @device:end -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver,lemonade,podman -->
<!-- @device:end -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
---
<!-- @device:end -->
<!-- @os:end -->

<!-- @test:id=lemonade-cli-verify timeout=30 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end --> 

## 在 Lemonade 中下載模型

在安裝 Open WebUI 之前，請確認你想使用的模型已在 Lemonade 中下載並準備就緒。

1. 在 `http://localhost:13305` 開啟 Lemonade GUI。
2. 瀏覽可用的模型，並下載你想使用的模型（例如：用於聊天的 LLM、視覺模型，和/或用於圖像生成的 Stable Diffusion 模型）。
3. 在瀏覽器中造訪 `http://localhost:13305/api/v1/models`，確認 API 可正常連線——你應該會看到已下載的模型列表。

> 模型必須先在 **Lemonade**（`localhost:13305`）中下載，才能出現在 **Open WebUI**（`localhost:8080`）中。如果之後某個模型未出現在 Open WebUI 中，請先回到這裡檢查 Lemonade。


<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
<!-- @test:id=openwebui-lemonade-multimodal-smoke-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$tmpChat = $null
$tmpVision = $null
$tmpImg = $null

try {
  # Wait for /models
  $modelsJson = $null
  for ($i=0; $i -lt 120; $i++) {
    $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
    if ($modelsJson) { break }
    Start-Sleep -Seconds 1
  }
  if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
  Write-Host "OK: Lemonade server is responding"
  
  # Verify required models are present + downloaded
  $parsed = $modelsJson | ConvertFrom-Json
  $required = @(
    "Qwen3-4B-Hybrid",
    "Qwen3.5-4B-GGUF",
    "SDXL-Turbo"
  )
  foreach ($mid in $required) {
    $entry = $parsed.data | Where-Object { $_.id -eq $mid } | Select-Object -First 1
    if (-not $entry) { throw "Model $mid is not present in /api/v1/models. Please download it." }
    if (-not $entry.downloaded) { throw "Model $mid is present but not downloaded. Please download it." }
    Write-Host "OK: $mid is downloaded"
  }

  # Chat completion smoke test (LLM)
  $chatBody = @{
    model = "Qwen3-4B-Hybrid"
    messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
    temperature = 0
    max_tokens = 500
    stream = $false
  } | ConvertTo-Json -Depth 6
  $tmpChat = Join-Path $env:TEMP "chat-body.json"
  [System.IO.File]::WriteAllText($tmpChat, $chatBody, [System.Text.UTF8Encoding]::new($false))
  $chatOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer -" `
    --data-binary "@$tmpChat"
  if (-not $chatOut) { throw "Empty response from chat/completions" }
  $chatParsed = $chatOut | ConvertFrom-Json
  $chatText = $chatParsed.choices[0].message.content
  if ($chatText -notmatch "\bOK\b") { throw "LLM chat test failed. Got: $chatText" }
  Write-Host "OK: LLM chat works"

  # Vision smoke test (OpenAI-style image_url)
  $png1x1 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO8p+S4AAAAASUVORK5CYII="
  $dataUrl = "data:image/png;base64,$png1x1"
  $visionBody = @{
    model = "Qwen3.5-4B-GGUF"
    messages = @(@{
      role = "user"
      content = @(
        @{ type = "text"; text = "If you can see an image input, reply with exactly: OK" },
        @{ type = "image_url"; image_url = @{ url = $dataUrl } }
      )
    })
    temperature = 0
    max_tokens = 256
  } | ConvertTo-Json -Depth 10
  $tmpVision = Join-Path $env:TEMP "vision-body.json"
  [System.IO.File]::WriteAllText($tmpVision, $visionBody, [System.Text.UTF8Encoding]::new($false))
  $visionOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer -" `
    --data-binary "@$tmpVision"
  if (-not $visionOut) { throw "Empty response from vision chat/completions" }
  $visionParsed = $visionOut | ConvertFrom-Json
  if (-not $visionParsed.choices -or $visionParsed.choices.Count -lt 1) { throw "Unexpected vision response (no choices). Raw response: $visionOut" }
  $visionText = $visionParsed.choices[0].message.content
  if ([string]::IsNullOrWhiteSpace($visionText)) { throw "Vision returned empty content. Raw response: $visionOut" }
  if ($visionText -notmatch "\bOK\b") { throw "Vision test failed. Got: $visionText. Raw response: $visionOut" }
  Write-Host "OK: Vision chat works"

  # Image generation smoke test
  $imgBody = @{
    model  = "SDXL-Turbo"
    prompt = "A simple red cube on a white table, studio lighting"
    size   = "256x256"
    steps  = 4
    response_format = "b64_json"
  } | ConvertTo-Json -Depth 6
  $tmpImg = Join-Path $env:TEMP "img-body.json"
  [System.IO.File]::WriteAllText($tmpImg, $imgBody, [System.Text.UTF8Encoding]::new($false))
  $imgOut = curl.exe -sS --fail-with-body --max-time 900 http://127.0.0.1:13305/api/v1/images/generations `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer -" `
    --data-binary "@$tmpImg"
  if (-not $imgOut) { throw "Empty response from images/generations" }
  $imgParsed = $imgOut | ConvertFrom-Json
  if (-not $imgParsed.data -or -not $imgParsed.data[0].b64_json) { throw "Image generation did not return data[0].b64_json. Raw response: $imgOut" }
  Write-Host "OK: Image generation works"
}
finally {
  @($tmpChat, $tmpVision, $tmpImg) |
  Where-Object { $_ } |
  ForEach-Object { Remove-Item $_ -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=openwebui-lemonade-multimodal-smoke-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$tmpChat = $null
$tmpVision = $null
$tmpImg = $null

try {
  # Wait for /models
  $modelsJson = $null
  for ($i=0; $i -lt 120; $i++) {
    $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
    if ($modelsJson) { break }
    Start-Sleep -Seconds 1
  }
  if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
  Write-Host "OK: Lemonade server is responding"
  
  # Verify required models are present + downloaded
  $parsed = $modelsJson | ConvertFrom-Json
  $required = @(
    "Qwen3.5-4B-GGUF",
    "SDXL-Turbo"
  )
  foreach ($mid in $required) {
    $entry = $parsed.data | Where-Object { $_.id -eq $mid } | Select-Object -First 1
    if (-not $entry) { throw "Model $mid is not present in /api/v1/models. Please download it." }
    if (-not $entry.downloaded) { throw "Model $mid is present but not downloaded. Please download it." }
    Write-Host "OK: $mid is downloaded"
  }

  # Chat completion smoke test (LLM)
  $chatBody = @{
    model = "Qwen3.5-4B-GGUF"
    messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
    temperature = 0
    max_tokens = 500
    stream = $false
  } | ConvertTo-Json -Depth 6
  $tmpChat = Join-Path $env:TEMP "chat-body.json"
  [System.IO.File]::WriteAllText($tmpChat, $chatBody, [System.Text.UTF8Encoding]::new($false))
  $chatOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer -" `
    --data-binary "@$tmpChat"
  if (-not $chatOut) { throw "Empty response from chat/completions" }
  $chatParsed = $chatOut | ConvertFrom-Json
  $chatText = $chatParsed.choices[0].message.content
  if ($chatText -notmatch "\bOK\b") { throw "LLM chat test failed. Got: $chatText" }
  Write-Host "OK: LLM chat works"

  # Vision smoke test (OpenAI-style image_url)
  $png1x1 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO8p+S4AAAAASUVORK5CYII="
  $dataUrl = "data:image/png;base64,$png1x1"
  $visionBody = @{
    model = "Qwen3.5-4B-GGUF"
    messages = @(@{
      role = "user"
      content = @(
        @{ type = "text"; text = "If you can see an image input, reply with exactly: OK" },
        @{ type = "image_url"; image_url = @{ url = $dataUrl } }
      )
    })
    temperature = 0
    max_tokens = 256
  } | ConvertTo-Json -Depth 10
  $tmpVision = Join-Path $env:TEMP "vision-body.json"
  [System.IO.File]::WriteAllText($tmpVision, $visionBody, [System.Text.UTF8Encoding]::new($false))
  $visionOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer -" `
    --data-binary "@$tmpVision"
  if (-not $visionOut) { throw "Empty response from vision chat/completions" }
  $visionParsed = $visionOut | ConvertFrom-Json
  if (-not $visionParsed.choices -or $visionParsed.choices.Count -lt 1) { throw "Unexpected vision response (no choices). Raw response: $visionOut" }
  $visionText = $visionParsed.choices[0].message.content
  if ([string]::IsNullOrWhiteSpace($visionText)) { throw "Vision returned empty content. Raw response: $visionOut" }
  if ($visionText -notmatch "\bOK\b") { throw "Vision test failed. Got: $visionText. Raw response: $visionOut" }
  Write-Host "OK: Vision chat works"

  # Image generation smoke test
  $imgBody = @{
    model  = "SDXL-Turbo"
    prompt = "A simple red cube on a white table, studio lighting"
    size   = "256x256"
    steps  = 4
    response_format = "b64_json"
  } | ConvertTo-Json -Depth 6
  $tmpImg = Join-Path $env:TEMP "img-body.json"
  [System.IO.File]::WriteAllText($tmpImg, $imgBody, [System.Text.UTF8Encoding]::new($false))
  $imgOut = curl.exe -sS --fail-with-body --max-time 900 http://127.0.0.1:13305/api/v1/images/generations `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer -" `
    --data-binary "@$tmpImg"
  if (-not $imgOut) { throw "Empty response from images/generations" }
  $imgParsed = $imgOut | ConvertFrom-Json
  if (-not $imgParsed.data -or -not $imgParsed.data[0].b64_json) { throw "Image generation did not return data[0].b64_json. Raw response: $imgOut" }
  Write-Host "OK: Image generation works"
}
finally {
  @($tmpChat, $tmpVision, $tmpImg) |
  Where-Object { $_ } |
  ForEach-Object { Remove-Item $_ -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end -->
<!-- @device:end -->
<!-- @os:end --> 

<!-- @os:linux --> 
<!-- @test:id=openwebui-lemonade-multimodal-smoke-linux timeout=1800 hidden=True -->
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
import base64, json, os, sys, urllib.request

data = json.loads(os.environ["MODELS_JSON"])
required = [
  "Qwen3.5-4B-GGUF",
  "SDXL-Turbo",
]

by_id = {m.get("id"): m for m in data.get("data", [])}
for mid in required:
  m = by_id.get(mid)
  if not m:
    print(f"Model {mid} is not present in /api/v1/models. Please download it.")
    sys.exit(1)
  if not m.get("downloaded", False):
    print(f"Model {mid} is present but not downloaded. Please download it.")
    sys.exit(1)
  print(f"OK: {mid} is downloaded")

def post_json(url, payload, timeout=300):
  req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={
      "Content-Type": "application/json",
      "Authorization": "Bearer -",
    },
    method="POST",
  )
  try:
    with urllib.request.urlopen(req, timeout=timeout) as r:
      return json.loads(r.read().decode("utf-8"))
  except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", errors="replace")
    raise SystemExit(f"POST {url} failed with HTTP {e.code}. Response body:\n{body}")

# LLM chat smoke test
chat = post_json("http://127.0.0.1:13305/api/v1/chat/completions", {
  "model": "Qwen3.5-4B-GGUF",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 500,
  "stream": False,
}, timeout=300)
text = chat["choices"][0]["message"]["content"]
if "OK" not in text:
  raise SystemExit(f"LLM chat test failed. Got: {text}")
print("OK: LLM chat works")

# Vision smoke test (OpenAI image_url format)
png1x1 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO8p+S4AAAAASUVORK5CYII="
data_url = "data:image/png;base64," + png1x1
vision = post_json("http://127.0.0.1:13305/api/v1/chat/completions", {
  "model": "Qwen3.5-4B-GGUF",
  "messages": [{
    "role": "user",
    "content": [
      {"type": "text", "text": "If you can see an image input, reply with exactly: OK"},
      {"type": "image_url", "image_url": {"url": data_url}},
    ],
  }],
  "temperature": 0,
  "max_tokens": 256,
}, timeout=300)
if not vision.get("choices"):
  raise SystemExit(f"Unexpected vision response (no choices). Raw response:\n{json.dumps(vision, indent=2)}")
vtext = vision["choices"][0]["message"].get("content", "")
if not vtext.strip():
  raise SystemExit(f"Vision returned empty content. Raw response:\n{json.dumps(vision, indent=2)}")
if "OK" not in vtext:
  raise SystemExit(f"Vision test failed. Got: {vtext}\nRaw response:\n{json.dumps(vision, indent=2)}")
print("OK: Vision chat works")

# Image generation smoke test
img = post_json("http://127.0.0.1:13305/api/v1/images/generations", {
  "model": "SDXL-Turbo",
  "prompt": "A simple red cube on a white table, studio lighting",
  "size": "256x256",
  "steps": 4,
  "response_format": "b64_json",
}, timeout=900)
b64 = img.get("data", [{}])[0].get("b64_json")
if not b64:
  raise SystemExit("Image generation did not return data[0].b64_json")
print("OK: Image generation works")
PY
```
<!-- @test:end --> 
<!-- @os:end --> 

## 安裝 Open WebUI

<!-- @os:windows -->
### 1. 安裝 Python 3.12

Open WebUI 需要 **Python 3.12**——它無法在 Python 3.13+ 上安裝。Windows Python 啟動器（`py`）讓你可以在不與現有 Python 版本衝突的情況下並行安裝 3.12。

```powershell
winget install Python.Python.3.12
```

安裝後請關閉並重新開啟終端機，然後驗證：

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **注意：** 你的系統已預先安裝 Python 3.13。安裝 3.12 不會影響它——`python` 會繼續使用 3.13，而 `py -3.12` 只有在你需要時才會指向 3.12。
<!-- @device:end -->

<!-- @test:id=python-env-check-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$v = (& py -3.12 --version) 2>&1
if ($LASTEXITCODE -ne 0) { throw "Python 3.12 was not found. Install it with: winget install Python.Python.3.12" }
if ($v -notmatch "Python 3\.12\.") { throw "Expected Python 3.12.x but got: $v" }

Write-Host "OK: $v"
```
<!-- @test:end --> 

### 2. 建立虛擬環境並安裝 Open WebUI

```powershell
mkdir openwebui
cd openwebui
py -3.12 -m venv openwebui-venv
.\openwebui-venv\Scripts\activate
pip install open-webui beautifulsoup4
```

<!-- @test:id=openwebui-install-venv-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$work = Join-Path (Get-Location) "openwebui"
if (Test-Path $work) { Remove-Item -Recurse -Force $work }
New-Item -ItemType Directory -Force -Path $work | Out-Null

Push-Location $work
try {
  py -3.12 -m venv openwebui-venv
  $py = Join-Path $work "openwebui-venv\Scripts\python.exe"

  & $py -m pip install --upgrade pip
  if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed" }

  & $py -m pip install open-webui beautifulsoup4
  if ($LASTEXITCODE -ne 0) { throw "pip install open-webui beautifulsoup4 failed" }

  Write-Host "OK: open-webui installed in venv"
}
finally {
  Pop-Location
}
```
<!-- @test:end --> 

<!-- @test:id=openwebui-install-check-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$work = Join-Path (Get-Location) "openwebui"
$venv = Join-Path $work "openwebui-venv"
$py = Join-Path $venv "Scripts\python.exe"

& $py -c "import open_webui; print('OK: import open_webui')"
& $py -c "import bs4; print('OK: bs4 import')"
```
<!-- @test:end --> 

<!-- @test:id=openwebui-cli-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$work = Join-Path (Get-Location) "openwebui"
$venv = Join-Path $work "openwebui-venv"
$ow = Join-Path $venv "Scripts\open-webui.exe"

if (-not (Test-Path $ow)) { throw "open-webui.exe not found at $ow" }

& $ow --help | Out-Null
Write-Host "OK: open-webui CLI is available"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
我們現在要使用 Podman 服務將 Open WebUI 安裝進行容器化。

請將以下檔案下載到你選擇的目錄中：[compose.yml](assets/compose.yml)

在該目錄中，執行以下指令：

```bash
podman compose up -d
```

這會拉取 Open WebUI 映像檔並寫入持久化儲存空間。

在瀏覽器網址列輸入 `localhost:8080` 以啟動 Open WebUI。

<!-- @test:id=openwebui-podman-prereq-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PODMAN_COMPOSE_PROVIDER="$(command -v podman-compose)"
export PODMAN_COMPOSE_WARNING_LOGS=false

podman --version
podman compose version
podman info >/dev/null

if [ ! -f compose.yml ]; then
  echo "compose.yml not found in current working directory (playbooks/supplemental/open-webui-chat/assets)"
  exit 1
fi

echo "OK: Podman, Podman Compose, and compose.yml are available"
```
<!-- @test:end -->

<!-- @test:id=openwebui-compose-validate-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path
import sys
import yaml

path = Path("compose.yml")
if not path.exists():
    raise SystemExit("compose.yml not found")

data = yaml.safe_load(path.read_text())
svc = data.get("services", {}).get("open-webui")
if not svc:
    raise SystemExit("compose.yml does not define services.open-webui")

expected_image = "ghcr.io/open-webui/open-webui:main"
if svc.get("image") != expected_image:
    raise SystemExit(f"Expected image {expected_image}, got {svc.get('image')}")

if svc.get("container_name") != "open-webui":
    raise SystemExit("Expected container_name: open-webui")

if svc.get("network_mode") != "host":
    raise SystemExit("Expected network_mode: host")

volumes = svc.get("volumes", [])
if "open_webui_data:/app/backend/data" not in volumes:
    raise SystemExit("Expected open_webui_data:/app/backend/data volume mount")

if "open_webui_data" not in data.get("volumes", {}):
    raise SystemExit("Expected top-level open_webui_data volume")

print("OK: compose.yml matches the Open WebUI Podman setup")
PY

podman compose -f compose.yml config >/dev/null

echo "OK: podman compose can parse compose.yml"
```
<!-- @test:end -->
<!-- @os:end -->

> **提示**：Open WebUI 也在其 [GitHub](https://github.com/open-webui/open-webui) 上提供其他安裝選項。
## 啟動 Open WebUI 伺服器

<!-- @os:windows -->
- 執行以下命令以啟動 Open WebUI HTTP 伺服器：
```bash
open-webui serve
```
<!-- @os:end -->

- 在瀏覽器中，前往 `http://localhost:8080`。
- Open WebUI 會要求您建立一個本機管理員帳戶。登入後，您會看到聊天介面。

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> 請保持終端機視窗開啟。關閉它會停止 Open WebUI。
<!-- @os:end -->

<!-- @os:linux -->
> 該容器會在背景中執行。從包含 `compose.yml` 的目錄中，可使用 `podman compose down`（停止）和 `podman compose up -d`（啟動）來管理它。您的帳戶與設定會保存在 `open_webui_data` 資料卷中。
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openwebui-server-smoke-windows timeout=900 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$work = Join-Path (Get-Location) "openwebui"
$venv = Join-Path $work "openwebui-venv"
$ow = Join-Path $venv "Scripts\open-webui.exe"
if (-not (Test-Path $ow)) { throw "open-webui not found. Run openwebui-install-venv-windows first." }

# Fresh data dir so auth mode/config isn't polluted by previous runs
$dataDir = Join-Path $work "openwebui-data-ci"
if (Test-Path $dataDir) { Remove-Item -Recurse -Force $dataDir }
New-Item -ItemType Directory -Force -Path $dataDir | Out-Null

$env:DATA_DIR = $dataDir
$env:WEBUI_AUTH = "False" # Disable auth for CI
$env:ENABLE_PERSISTENT_CONFIG = "False" # Ensure environment-variable config applies for the run and isn't overridden by persistent settings

$logOut = Join-Path $work "openwebui-ci-out.log"
$logErr = Join-Path $work "openwebui-ci-err.log"
$p = Start-Process -FilePath $ow -ArgumentList "serve --port 8080" -NoNewWindow -PassThru -RedirectStandardOutput $logOut -RedirectStandardError $logErr
try {
  $ok = $false
  for ($i=0; $i -lt 90; $i++) {
    $health = curl.exe -s --max-time 2 http://127.0.0.1:8080/health
    if ($health) { $ok = $true; break }
    Start-Sleep -Seconds 1
  }
  if (-not $ok) { throw "Open WebUI not ready on http://127.0.0.1:8080" }
  Write-Host "OK: Open WebUI is responding on /health"
}
finally {
  if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end --> 
<!-- @os:end --> 

<!-- @os:linux -->
<!-- @test:id=openwebui-podman-server-smoke-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

export PODMAN_COMPOSE_PROVIDER="$(command -v podman-compose)"
export PODMAN_COMPOSE_WARNING_LOGS=false

cleanup() {
  podman compose -f compose.yml down >/dev/null 2>&1 || true
}
trap cleanup EXIT

# Clean up a stale container from a previous failed run.
podman rm -f open-webui >/dev/null 2>&1 || true

podman compose -f compose.yml up -d

health=""
for i in $(seq 1 180); do
  health="$(curl -fsS --max-time 2 http://127.0.0.1:8080/health || true)"
  if [ -n "$health" ]; then
    break
  fi
  sleep 1
done

if [ -z "$health" ]; then
  echo "Open WebUI did not become ready on http://127.0.0.1:8080/health"
  echo "Container status:"
  podman ps -a || true
  echo "Open WebUI logs:"
  podman logs --tail 200 open-webui || true
  exit 1
fi

echo "OK: Open WebUI container is responding on /health"

# Verify that the Open WebUI container can reach Lemonade through host networking.
podman exec open-webui sh -lc 'python -c "import json, urllib.request; data=json.load(urllib.request.urlopen(\"http://127.0.0.1:13305/api/v1/models\", timeout=10)); assert \"data\" in data; print(\"OK: Open WebUI container can reach Lemonade models endpoint\")"'
```
<!-- @test:end --> 
<!-- @os:end --> 

## 將 Open WebUI 連接至 Lemonade

現在兩項服務都已在執行——Lemonade 於 `localhost:13305`，Open WebUI 於 `localhost:8080`——請將它們連接起來，讓 Open WebUI 能夠使用 Lemonade 的模型。

在 Open WebUI 中：

1. 點擊右上角的**使用者個人檔案圖示**，然後選擇**設定**。

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. 在設定面板中，點擊左下角的**管理員設定**。

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. 在管理員設定側邊欄中，點擊**連線**（或直接前往 `http://localhost:8080/admin/settings/connections`）。

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. 在 **OpenAI API** 下方，新增一個連線：
   - **Base URL：** `http://localhost:13305/api/v1`
   - **API Key：** `-`（本機使用只需輸入一個破折號）

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. 請確保在**「管理 OpenAI API 連線」**下，僅啟用 `http://localhost:13305/api/v1`。停用其他所有連線（例如預設的 OpenAI 連線）。

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. 點擊**儲存**。

7. **（建議）** 停用自動生成功能，以保持 Open WebUI 在使用本機 LLM 時的回應速度。前往**管理員設定 → 設定 → 介面**，然後關閉：
   - 標題生成
   - 後續問題生成
   - 標籤生成

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. 點擊**儲存**，然後返回 `http://localhost:8080`。
9. 點擊模型下拉選單——您應該會看到從 Lemonade 下載的模型。

---

## 主要活動

現在，一切都已設定完成。讓我們來看看三個有趣的操作。

---

### 活動一：與本機 LLM 聊天
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. 點擊介面左上角的下拉選單。這會顯示您已安裝的 Lemonade 模型。選擇其中一個繼續操作（範例：`Qwen3-4B-Hybrid`）。

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. 向 LLM 輸入訊息並點擊傳送（或按下 Enter）。LLM 需要幾秒鐘載入到記憶體中，之後您將看到回應以串流方式呈現。

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. 點擊介面左上角的下拉選單。這會顯示您已安裝的 Lemonade 模型。選擇其中一個繼續操作（範例：`Qwen3.5-4B-GGUF`）。

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. 向 LLM 輸入訊息並點擊傳送（或按下 Enter）。LLM 需要幾秒鐘載入到記憶體中，之後您將看到回應以串流方式呈現。

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. 模型將在聊天中回應。

4. 此時，開啟系統上的 `Task Manager`（工作管理員）。根據您所選模型是 **Hybrid** 還是 **NPU**，您將分別看到**高 GPU 或 NPU 使用率**。透過工作管理員，您可以確認自己正在本機執行該模型。

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. 點擊介面左上角的下拉選單。這會顯示您已安裝的 Lemonade 模型。選擇其中一個繼續操作（範例：`Qwen3.5-4B-GGUF`）。

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. 向 LLM 輸入訊息並點擊傳送（或按下 Enter）。LLM 需要幾秒鐘載入到記憶體中，之後您將看到回應以串流方式呈現。

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. 模型將在聊天中回應。
<!-- @os:end -->

這驗證了 Open WebUI 能夠使用相容於 OpenAI 的聊天端點，向 Lemonade 傳送請求。

---

### 活動二：上傳圖片並提問（視覺功能）

此功能需要一個支援圖片輸入的模型（視覺或多模態模型）。

1. 點擊篩選圖示，選擇「依類別」，然後從**視覺（Vision）**區段中選擇一個模型（例如：`Qwen3.5-4B-GGUF`）

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. 點擊訊息輸入框中的 **`+`** 按鈕並上傳一張圖片
3. 提出需要真正理解圖片內容的問題：`Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. 模型會根據圖片內容回答，而非泛泛的文字內容。

這證明了 Open WebUI 能夠透過後端（Lemonade）將多模態請求（文字＋圖片）傳送給視覺模型。

---

<!-- @os:windows -->
### 活動三：根據文字提示生成圖片（Stable Diffusion）

Stable Diffusion 模型不支援文字生成，它們僅透過 Images API 生成圖片。

#### 步驟一：在 Open WebUI 中設定圖片生成

1. 在 Lemonade GUI（`http://localhost:13305`）中，搜尋 `SDXL-Turbo`（速度較快）或 `SDXL-Base-1.0`（品質較高）並下載。
2. 前往**管理員設定 → 圖片**（http://localhost:8080/admin/settings/images）
3. 設定：
   - **圖片生成：** 開啟
   - **圖片生成引擎：** 預設（OpenAI）
   - **OpenAI API Base URL：** `http://localhost:13305/api/v1`
   - **OpenAI API Key：** `-`
   - **模型：** `SDXL-Turbo` 或 `SDXL-Base-1.0`
4. 如果您想新增更多參數，請以 JSON 格式將其加入文字欄位中。例如：`{ "steps": 4, "cfg_scale": 1 }`。可用參數請參閱 [圖片生成（Stable Diffusion CPP）](https://lemonade-server.ai/models.html)。

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. 儲存
#### 步驟 2:允許模型進行圖片生成
此步驟可確保您為模型啟用圖片生成功能。
1. 前往 **Admin Settings → Models**(http://localhost:8080/admin/settings/models)並選擇您的模型
2. 開啟 `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### 步驟 3:從聊天畫面生成圖片

1. 返回聊天畫面 `http://localhost:8080`。
2. 在模型下拉選單中選擇一個**文字生成 LLM**(例如:Qwen、Llama)。**請勿選擇 Stable Diffusion 模型**,因為這是聊天模型選擇器。
3. 在訊息區域中,點擊 **Integrations**,並將 **Image** 切換為 ON。
4. 使用類似以下的提示詞:`A cinematic photo of heavy traffic at sunset, ultra detailed`。
5. 系統會生成一張圖片並顯示在聊天中。

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

這確立了 Open WebUI 可以協調一個「兩部分」的工作流程:
  - LLM 協助改善提示詞
  - 圖片是透過 Lemonade 的 Images 端點使用 Stable Diffusion 生成的
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### 活動 3:從文字提示詞生成圖片(Stable Diffusion)

Stable Diffusion 模型不支援文字生成,它們僅透過 Images API 生成圖片。

#### 步驟 1:在 Open WebUI 中設定圖片生成

1. 在 Lemonade GUI 中(`http://localhost:13305`),搜尋 `SDXL-Turbo`(快速)或 `SDXL-Base-1.0`(更高品質)並下載。
2. 前往 **Admin Settings → Images**(http://localhost:8080/admin/settings/images)
3. 設定:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` 或 `SDXL-Base-1.0`
4. 如果您想新增更多參數,請以 JSON 格式將其新增至文字欄位。例如:`{ "steps": 4, "cfg_scale": 1 }`。請參閱 [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html) 以取得可用參數。

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. 儲存


#### 步驟 2:允許模型進行圖片生成
此步驟可確保您為模型啟用圖片生成功能。
1. 前往 **Admin Settings → Models**(http://localhost:8080/admin/settings/models)並選擇您的模型
2. 開啟 `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### 步驟 3:從聊天畫面生成圖片

1. 返回聊天畫面 `http://localhost:8080`。
2. 在模型下拉選單中選擇一個**文字生成 LLM**(例如:Qwen、Llama)。**請勿選擇 Stable Diffusion 模型**,因為這是聊天模型選擇器。
3. 在訊息區域中,點擊 **Integrations**,並將 **Image** 切換為 ON。
4. 使用類似以下的提示詞:`A cinematic photo of heavy traffic at sunset, ultra detailed`。
5. 系統會生成一張圖片並顯示在聊天中。

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

這確立了 Open WebUI 可以協調一個「兩部分」的工作流程:
  - LLM 協助改善提示詞
  - 圖片是透過 Lemonade 的 Images 端點使用 Stable Diffusion 生成的
<!-- @device:end -->
<!-- @os:end -->

---

## 疑難排解

### 「Open WebUI 中未顯示任何模型」
- 首先,檢查 Lemonade:在瀏覽器中開啟 `http://localhost:13305/api/v1/models`,確認您的模型已列出且已下載
- 接著,檢查 Open WebUI 連線:前往 `http://localhost:8080/admin/settings/connections` 的 **Admin Settings → Connections**,並確認 Base URL 為 `http://localhost:13305/api/v1`

### 出現「This model does not support chat completion」錯誤訊息
- 您在聊天模型下拉選單中選擇了圖片模型(SDXL-Turbo / SDXL-Base-1.0)。
- **解決方法**:選擇一個用於聊天的 LLM,並使用 Image 切換開關和 Images 設定來進行生成。
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### 圖片生成錯誤/逾時
- 先從 `SDXL-Turbo` 開始嘗試(速度快、步驟少)
- 運作正常後,再將圖片模型切換為 `SDXL-Base-1.0` 以獲得更高品質

---

## 後續步驟

您現在擁有一個可運作的**「本地 AI 堆疊」**,即透過標準 API 以單一 UI 控制多種模型類型。

以下三種擴充功能可解鎖全新的工作流程:

### 1. 使用 Whisper 進行語音轉文字

嘗試使用 Whisper 模型將音訊轉換為文字,然後將其輸入 LLM 進行摘要、行動項目提取或改寫。這是會議記錄和語音驅動助理的基礎。

### 2. 在 Open WebUI 中進行 Python 編碼

使用 Open WebUI 內建的程式碼執行體驗來執行 Python 程式碼片段、檢視輸出結果,並更快速地進行迭代——完全不需要離開 UI。[參考資料](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. 在 Open WebUI 中進行 HTML 渲染

直接在介面中渲染 HTML 輸出結果。這對於建立快速原型、格式化報告和互動式程式碼片段來說,功能出奇強大。[參考資料](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## 參考資料

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Lemonade Server 文件](https://lemonade-server.ai/docs)
- [Lemonade Server CLI](https://lemonade-server.ai/docs/lemonade-cli/)
- [Lemonade ↔ Open WebUI 整合指南](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Lemonade Server API 規範(端點)](https://lemonade-server.ai/docs/server/server_spec)
- [影片操作說明(Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [影片操作說明(Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)

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