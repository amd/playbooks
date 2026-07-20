<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> 本手册使用了 GitHub 无法渲染的特殊标签。请访问 [amd.com/playbooks](https://amd.com/playbooks) 以正确预览此内容。
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> 本手册最低需要 **32GB** 系统内存。
<!-- @device:end -->

## 概述

[Open WebUI](https://docs.openwebui.com) 是一个自托管、基于浏览器的界面，可提供熟悉的聊天机器人体验，同时作为一个或多个 AI 模型服务器的前端。Open WebUI 不局限于单一提供商，可以连接到**任何暴露 OpenAI 兼容 API 的后端**，因此你可以在不切换界面的情况下更换模型和功能。

在本手册中，我们使用 [**Lemonade**](https://lemonade-server.ai) 作为后端，因为它暴露了一个**统一的 OpenAI 兼容端点**，支持多种模态：
- **大语言模型（LLM）** 用于文本生成
- **视觉模型** 用于图像理解
- **Stable Diffusion** 用于图像生成
- **音频转录模型** 用于语音转文本

此设置使你能够端到端地探索**完整的多模态工作流**。

---

## 你将学到什么

学完之后，你将能够：

- 将 Open WebUI 连接到本地 OpenAI 兼容后端（Lemonade）
- 在浏览器中与本地 LLM 聊天
- 上传图像并向视觉模型提问
- 使用 Stable Diffusion 模型（SDXL-Turbo / SDXL）根据文本提示生成图像
- 理解其中的思维模型，以便使用其他后端（Ollama、vLLM、llama.cpp server 等）

---

## 核心概念（思维模型）

### 三个组成部分

| 组成部分 | 作用 | 示例 |
|---|---|---|
| 前端（UI） | 你交互的网页应用 | Open WebUI |
| 后端（模型服务器） | 托管模型并暴露 HTTP 端点 | Lemonade、Ollama、vLLM、llama.cpp server、OpenAI 兼容服务器 |
| 模型 | 实际的 LLM / 视觉 / 扩散 / 音频模型 | CodeLlama、DeepSeek、Gemma-MM、SDXL、SD-Turbo、Whisper |

#### 为什么“OpenAI 兼容 API”很重要

Open WebUI 是围绕标准 OpenAI 风格端点构建的，例如：
  - 聊天：`/chat/completions`
  - 模型列表：`/models`
  - 图像生成：`/images/generations`
  - 音频转录：`/audio/transcriptions`

Lemonade 在 `http://localhost:13305/api/v1/...` 下暴露这些端点。

如果一个后端支持这些端点，Open WebUI 就可以以最少的配置与之通信。这就是我们可以在不改变工作流的情况下切换后端的原因。

#### 两个服务，两个端口

在本手册中，你将使用两个独立的服务：

| 服务 | URL | 你在此进行的操作 |
|---|---|---|
| **Lemonade**（图形界面） | `http://localhost:13305` | 浏览、下载和管理模型 |
| **Open WebUI** | `http://localhost:8080` | 聊天、上传图像、生成图像 —— 面向用户的界面 |

Lemonade 运行模型；Open WebUI 是你交互的界面。请先使用 Lemonade 图形界面下载模型，然后在 Open WebUI 中使用它们。

---

## 设置内存配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 检查软件更新

<!-- @require:software-update -->
<!-- @device:end -->

## 一次性设置

本手册需要 Lemonade 作为后端运行，并且在 Linux 上，还需要一个容器引擎（Podman）来运行 Open WebUI。请在安装 Open WebUI 之前完成这些设置。

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

## 在 Lemonade 中下载模型

在安装 Open WebUI 之前，请确保你想使用的模型已在 Lemonade 中下载并就绪。

1. 在 `http://localhost:13305` 打开 Lemonade 图形界面。
2. 浏览可用模型，并下载你想使用的模型（例如，用于聊天的 LLM、视觉模型和/或用于图像生成的 Stable Diffusion 模型）。
3. 在浏览器中访问 `http://localhost:13305/api/v1/models` 以确认 API 可访问 —— 你应该能看到已下载的模型列表。

> 模型必须先在 **Lemonade**（`localhost:13305`）中下载，才能出现在 **Open WebUI**（`localhost:8080`）中。如果之后某个模型未在 Open WebUI 中显示，请返回此处先检查 Lemonade。


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

## 安装 Open WebUI

<!-- @os:windows -->
### 1. 安装 Python 3.12

Open WebUI 需要 **Python 3.12** —— 它无法在 Python 3.13+ 上安装。Windows Python 启动器（`py`）可让你在不与现有 Python 版本冲突的情况下并行安装 3.12。

```powershell
winget install Python.Python.3.12
```

安装后请关闭并重新打开终端，然后进行验证：

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **注意：** 你的系统预装了 Python 3.13。安装 3.12 不会影响它 —— `python` 仍然使用 3.13，而 `py -3.12` 仅在你需要时才指向 3.12。
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

### 2. 创建虚拟环境并安装 Open WebUI

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
我们现在将使用 Podman 服务来容器化我们的 Open WebUI 安装。

请将以下文件下载到你选择的目录中：[compose.yml](assets/compose.yml)

在该目录中，运行以下命令：

```bash
podman compose up -d
```

这会拉取 Open WebUI 镜像并写入持久化存储。

在浏览器地址栏中输入 `localhost:8080` 以启动 Open WebUI。

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

> **提示**：Open WebUI 还在其 [GitHub](https://github.com/open-webui/open-webui) 上提供了其他安装选项。
## 启动 Open WebUI 服务器

<!-- @os:windows -->
- 运行以下命令以启动 Open WebUI HTTP 服务器：
```bash
open-webui serve
```
<!-- @os:end -->

- 在浏览器中，导航到 `http://localhost:8080`。
- Open WebUI 会要求您创建一个本地管理员账户。登录后，您将看到聊天界面。

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> 请保持终端窗口打开。关闭它会停止 Open WebUI。
<!-- @os:end -->

<!-- @os:linux -->
> 该容器在后台运行。在包含 `compose.yml` 的目录下，使用 `podman compose down`（停止）和 `podman compose up -d`（启动）来管理它。您的账户和设置会保存在 `open_webui_data` 卷中。
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

## 将 Open WebUI 连接到 Lemonade

现在两项服务都已运行——Lemonade 位于 `localhost:13305`，Open WebUI 位于 `localhost:8080`——将它们连接起来，以便 Open WebUI 可以使用 Lemonade 的模型。

在 Open WebUI 中：

1. 点击右上角的**用户头像图标**，然后选择**设置**。

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. 在设置面板中，点击左下角的**管理员设置**。

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. 在管理员设置侧边栏中，点击**连接**（或直接导航到 `http://localhost:8080/admin/settings/connections`）。

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. 在 **OpenAI API** 下，添加一个新连接：
   - **Base URL：** `http://localhost:13305/api/v1`
   - **API Key：** `-`（本地使用时输入一个短横线即可）

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. 确保在**“管理 OpenAI API 连接”**下，仅启用 `http://localhost:13305/api/v1`。禁用其他所有连接（例如默认的 OpenAI 连接）。

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. 点击**保存**。

7. **（推荐）** 禁用自动生成功能，以保持 Open WebUI 在使用本地 LLM 时的响应速度。前往**管理员设置 → 设置 → 界面**，关闭以下选项：
   - 标题生成
   - 后续问题生成
   - 标签生成

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. 点击**保存**，然后返回 `http://localhost:8080`。
9. 点击模型下拉菜单——您应该能看到从 Lemonade 下载的模型。

---

## 主要活动

现在，一切都已设置完成。让我们来看看三件有趣的事情。

---

### 活动 1：与本地 LLM 聊天
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. 点击界面左上角的下拉菜单。这将显示您已安装的 Lemonade 模型。选择一个继续（例如：`Qwen3-4B-Hybrid`）。

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. 向 LLM 输入一条消息并点击发送（或按 Enter 键）。LLM 需要几秒钟加载到内存中，然后您将看到响应以流式方式呈现。

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. 点击界面左上角的下拉菜单。这将显示您已安装的 Lemonade 模型。选择一个继续（例如：`Qwen3.5-4B-GGUF`）。

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. 向 LLM 输入一条消息并点击发送（或按 Enter 键）。LLM 需要几秒钟加载到内存中，然后您将看到响应以流式方式呈现。

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. 模型将在聊天中做出回复。

4. 此时，打开系统上的 `Task Manager`。根据您选择的模型是 **Hybrid** 还是 **NPU** 模式，您将分别看到 **GPU 或 NPU 使用率较高**。通过任务管理器，您可以确认自己正在本地运行该模型。

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. 点击界面左上角的下拉菜单。这将显示您已安装的 Lemonade 模型。选择一个继续（例如：`Qwen3.5-4B-GGUF`）。

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. 向 LLM 输入一条消息并点击发送（或按 Enter 键）。LLM 需要几秒钟加载到内存中，然后您将看到响应以流式方式呈现。

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. 模型将在聊天中做出回复。
<!-- @os:end -->

这验证了 Open WebUI 可以使用 OpenAI 兼容的聊天端点向 Lemonade 发送请求。

---

### 活动 2：上传图片并提问（视觉能力）

这需要一个支持图像输入的模型（视觉或多模态模型）。

1. 点击筛选图标，选择“按类别”，然后从**视觉（Vision）**部分选择一个模型（例如 `Qwen3.5-4B-GGUF`）

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. 点击消息框中的 **`+`** 按钮并上传一张图片
3. 提出一个需要真正理解图像内容的问题：`Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. 模型会根据图像内容作答，而不是给出通用的文字回复。

这展示了 Open WebUI 可以通过后端（Lemonade）向视觉模型发送多模态请求（文本 + 图像）。

---

<!-- @os:windows -->
### 活动 3：根据文本提示生成图像（Stable Diffusion）

Stable Diffusion 模型不支持文本生成，它们仅通过图像 API 生成图像。

#### 步骤 1：在 Open WebUI 中配置图像生成

1. 在 Lemonade GUI（`http://localhost:13305`）中，搜索 `SDXL-Turbo`（速度快）或 `SDXL-Base-1.0`（质量更高）并下载。
2. 前往**管理员设置 → 图像**（http://localhost:8080/admin/settings/images）
3. 设置：
   - **图像生成：** 开启
   - **图像生成引擎：** 默认（OpenAI）
   - **OpenAI API Base URL：** `http://localhost:13305/api/v1`
   - **OpenAI API Key：** `-`
   - **模型：** `SDXL-Turbo` 或 `SDXL-Base-1.0`
4. 如果您想添加更多参数，请以 JSON 格式将它们添加到文本字段中。例如：`{ "steps": 4, "cfg_scale": 1 }`。可用参数请参见 [图像生成（Stable Diffusion CPP）](https://lemonade-server.ai/models.html)。

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. 保存
#### 步骤 2：为模型启用图像生成
此步骤确保您为模型启用图像生成功能。
1. 进入 **Admin Settings → Models**（http://localhost:8080/admin/settings/models）并选择您的模型
2. 打开 `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### 步骤 3：从聊天界面生成图像

1. 返回 `http://localhost:8080` 的聊天界面。
2. 在模型下拉菜单中选择一个**文本生成 LLM**（例如：Qwen、Llama）。**请勿选择 Stable Diffusion 模型**，因为这里是聊天模型选择器。
3. 在消息区域，点击 **Integrations**，并将 **Image** 开关打开。
4. 使用类似这样的提示词：`A cinematic photo of heavy traffic at sunset, ultra detailed`。
5. 系统会生成一张图像并显示在聊天中。

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

这说明 Open WebUI 可以协调一个“两部分”工作流：
  - LLM 帮助优化提示词
  - 图像通过 Lemonade 的 Images 端点使用 Stable Diffusion 生成
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### 活动 3：根据文本提示生成图像（Stable Diffusion）

Stable Diffusion 模型不支持文本生成，它们只能通过 Images API 生成图像。

#### 步骤 1：在 Open WebUI 中配置图像生成

1. 在 Lemonade GUI（`http://localhost:13305`）中，搜索 `SDXL-Turbo`（速度快）或 `SDXL-Base-1.0`（质量更高）并下载。
2. 进入 **Admin Settings → Images**（http://localhost:8080/admin/settings/images）
3. 设置：
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` 或 `SDXL-Base-1.0`
4. 如果您想添加更多参数，可将它们以 JSON 格式添加到文本字段中。例如：`{ "steps": 4, "cfg_scale": 1 }`。可用参数请参见 [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html)。

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. 保存


#### 步骤 2：为模型启用图像生成
此步骤确保您为模型启用图像生成功能。
1. 进入 **Admin Settings → Models**（http://localhost:8080/admin/settings/models）并选择您的模型
2. 打开 `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### 步骤 3：从聊天界面生成图像

1. 返回 `http://localhost:8080` 的聊天界面。
2. 在模型下拉菜单中选择一个**文本生成 LLM**（例如：Qwen、Llama）。**请勿选择 Stable Diffusion 模型**，因为这里是聊天模型选择器。
3. 在消息区域，点击 **Integrations**，并将 **Image** 开关打开。
4. 使用类似这样的提示词：`A cinematic photo of heavy traffic at sunset, ultra detailed`。
5. 系统会生成一张图像并显示在聊天中。

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

这说明 Open WebUI 可以协调一个“两部分”工作流：
  - LLM 帮助优化提示词
  - 图像通过 Lemonade 的 Images 端点使用 Stable Diffusion 生成
<!-- @device:end -->
<!-- @os:end -->

---

## 故障排查

### “Open WebUI 中未显示任何模型”
- 首先检查 Lemonade：在浏览器中打开 `http://localhost:13305/api/v1/models`，确认您的模型已列出并已下载
- 然后检查 Open WebUI 连接：进入 `http://localhost:8080/admin/settings/connections` 的 **Admin Settings → Connections**，并确认 Base URL 为 `http://localhost:13305/api/v1`

### “This model does not support chat completion” 错误提示
- 您在聊天模型下拉菜单中选择了图像模型（SDXL-Turbo / SDXL-Base-1.0）。
- **解决方法**：选择一个用于聊天的 LLM，并使用 Image 开关和 Images 设置进行图像生成。
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### 图像生成错误/超时
- 首先尝试使用 `SDXL-Turbo`（速度快，步数少）
- 运行正常后，可将图像模型切换为 `SDXL-Base-1.0` 以获得更高质量

---

## 后续步骤

现在您已经拥有一个可正常运行的**“本地 AI 技术栈”**，通过一个统一的界面，借助标准 API 控制多种类型的模型。

以下三项扩展功能可解锁全新的工作流：

### 1. 使用 Whisper 进行语音转文本

尝试使用 Whisper 模型将音频转换为文本，然后将其输入 LLM 进行摘要、生成待办事项或改写。这是会议记录和语音驱动助手的基础。

### 2. 在 Open WebUI 中进行 Python 编程

使用 Open WebUI 内置的代码执行体验来运行 Python 代码片段、查看输出并快速迭代——无需离开界面。[参考](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. 在 Open WebUI 中渲染 HTML

直接在界面中渲染 HTML 输出。这在构建快速原型、格式化报告和交互式代码片段方面出乎意料地强大。[参考](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## 参考资料

- [Open WebUI（GitHub）](https://github.com/open-webui/open-webui)
- [Lemonade（GitHub）](https://github.com/lemonade-sdk/lemonade)
- [Lemonade Server 文档](https://lemonade-server.ai/docs)
- [Lemonade Server CLI](https://lemonade-server.ai/docs/lemonade-cli/)
- [Lemonade 与 Open WebUI 集成指南](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Lemonade Server API 规范（端点）](https://lemonade-server.ai/docs/server/server_spec)
- [视频演示（Lemonade）](https://www.youtube.com/watch?v=mcf7dDybUco)
- [视频演示（Open WebUI + Lemonade）](https://www.youtube.com/watch?v=yZs-Yzl736E)