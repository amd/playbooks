<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **机器翻译。**本页面由英文自动翻译，未经人工审核。其中可能包含错误，某些说明、命令、下载内容、产品可用性或其他内容可能因语言或地区而异。如内容存在任何不一致或差异，应以英文原版 playbook 为准。
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> 本手册要求系统内存至少为 **32GB**。
<!-- @device:end -->

## 概述

[Open WebUI](https://docs.openwebui.com) 是一款自托管、基于浏览器的界面，提供熟悉的聊天机器人体验，同时作为一个或多个 AI 模型服务器的前端。它并不绑定于某一个提供商，Open WebUI 可以连接到**任何公开 OpenAI 兼容 API 的后端**，因此你可以在不更换 UI 的情况下切换模型和功能。

在本手册中，我们使用 [**Lemonade**](https://lemonade-server.ai) 作为后端，因为它公开了一个**统一的 OpenAI 兼容端点**，支持多种模态：
- **大语言模型（LLM）**，用于文本生成
- **视觉模型**，用于图像理解
- **Stable Diffusion**，用于图像生成
- **音频转录模型**，用于语音转文本

此设置使你能够端到端地探索**完整的多模态工作流**。

---

## 你将学到什么

学完本手册后，你将能够：

- 将 Open WebUI 连接到本地的 OpenAI 兼容后端（Lemonade）
- 在浏览器中与本地 LLM 聊天
- 上传图片并向视觉模型提问
- 使用 Stable Diffusion 模型（SDXL-Turbo / SDXL）根据文本提示生成图像
- 理解其中的思维模型，从而能够使用其他后端（Ollama、vLLM、llama.cpp server 等）

---

## 核心概念（思维模型）

### 三个组成部分

| 部分 | 作用 | 示例 |
|---|---|---|
| 前端（UI） | 你所交互的 Web 应用 | Open WebUI |
| 后端（模型服务器） | 承载模型并公开 HTTP 端点 | Lemonade、Ollama、vLLM、llama.cpp server、OpenAI 兼容服务器 |
| 模型 | 实际的 LLM / 视觉 / 扩散 / 音频模型 | CodeLlama、DeepSeek、Gemma-MM、SDXL、SD-Turbo、Whisper |

#### 为什么“OpenAI 兼容 API”很重要

Open WebUI 基于标准的 OpenAI 风格端点构建，例如：
  - 聊天：`/chat/completions`
  - 模型列表：`/models`
  - 图像生成：`/images/generations`
  - 音频转录：`/audio/transcriptions`

Lemonade 在 `http://localhost:13305/api/v1/...` 下公开了这些端点。

只要后端支持这些端点，Open WebUI 就能以最少的配置与其通信。这就是为什么我们可以在不改变工作流的情况下切换后端。

#### 两个服务，两个端口

在本手册中，你将使用两个独立的服务：

| 服务 | URL | 你在这里做什么 |
|---|---|---|
| **Lemonade**（GUI） | `http://localhost:13305` | 浏览、下载和管理模型 |
| **Open WebUI** | `http://localhost:8080` | 聊天、上传图片、生成图像——面向用户的 UI |

Lemonade 负责运行模型；Open WebUI 是你所交互的界面。请先使用 Lemonade GUI 下载所需模型，然后从 Open WebUI 中使用它们。

---

## 设置内存配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 检查软件更新

<!-- @require:software-update -->
<!-- @device:end -->

## 一次性设置

本手册需要将 Lemonade 作为后端运行，并且在 Linux 上，还需要容器引擎（Podman）来运行 Open WebUI。请在安装 Open WebUI 之前完成这些设置。

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

在安装 Open WebUI 之前，请确保你要使用的模型已在 Lemonade 中下载完成并准备就绪。

1. 在 `http://localhost:13305` 打开 Lemonade GUI。
2. 浏览可用模型，并下载你想使用的模型（例如，用于聊天的 LLM、视觉模型和/或用于图像生成的 Stable Diffusion 模型）。
3. 在浏览器中访问 `http://localhost:13305/api/v1/models`，确认 API 可以访问——你应该能看到已下载的模型列表。

> 模型必须先在 **Lemonade**（`localhost:13305`）中下载完成，然后才能出现在 **Open WebUI**（`localhost:8080`）中。如果之后某个模型没有在 Open WebUI 中显示出来，请先回到这里检查 Lemonade。


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

Open WebUI 需要 **Python 3.12**——它无法在 Python 3.13+ 上安装。Windows Python 启动器（`py`）让你能够将 3.12 与任何现有的 Python 版本并行安装，而不会产生冲突。

```powershell
winget install Python.Python.3.12
```

安装完成后关闭并重新打开终端，然后进行验证：

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **注意：** 你的系统预装了 Python 3.13。安装 3.12 不会影响它——`python` 仍然使用 3.13，而 `py -3.12` 仅在你需要时才指向 3.12。
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
现在，我们将使用 Podman 服务来容器化我们的 Open WebUI 安装。

请将以下文件下载到你选择的目录中：[compose.yml](assets/compose.yml)

在该目录中，运行以下命令：

```bash
podman compose up -d
```

这将拉取 Open WebUI 镜像并写入持久存储。

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
- Open WebUI 会要求你创建一个本地管理员账户。登录后，你将看到聊天界面。

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> 请保持终端窗口打开。关闭它会停止 Open WebUI。
<!-- @os:end -->

<!-- @os:linux -->
> 该容器在后台运行。在包含 `compose.yml` 的目录下，可以使用 `podman compose down`（停止）和 `podman compose up -d`（启动）来管理它。你的账户和设置会保存在 `open_webui_data` 卷中。
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

现在两个服务都已运行——Lemonade 位于 `localhost:13305`，Open WebUI 位于 `localhost:8080`——将它们连接起来，以便 Open WebUI 能够使用 Lemonade 的模型。

在 Open WebUI 中：

1. 点击右上角的**用户头像图标**，然后选择**Settings**。

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. 在设置面板中，点击左下角的**Admin Settings**。

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. 在 Admin Settings 侧边栏中，点击**Connections**（或直接导航到 `http://localhost:8080/admin/settings/connections`）。

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. 在**OpenAI API**下，添加一个新连接：
   - **Base URL：** `http://localhost:13305/api/v1`
   - **API Key：** `-`（本地使用单个短横线即可）

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. 确保在**“Manage OpenAI API Connections”**下，只有 `http://localhost:13305/api/v1` 处于启用状态。禁用其他所有连接（例如默认的 OpenAI 连接）。

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. 点击**Save**。

7. **（推荐）** 禁用自动生成功能，以保持 Open WebUI 在使用本地 LLM 时的响应速度。前往**Admin Settings → Settings → Interface**，关闭以下选项：
   - Title Generation
   - Follow Up Generation
   - Tags Generation

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. 点击**Save**，然后返回 `http://localhost:8080`。
9. 点击模型下拉菜单——你应该能看到从 Lemonade 下载的模型。

---

## 主要活动

现在，你已经完成了所有设置。让我们来看三个有趣的活动。

---

### 活动 1：与本地 LLM 聊天
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. 点击界面左上角的下拉菜单。这将显示你已安装的 Lemonade 模型。选择一个以继续（示例：`Qwen3-4B-Hybrid`）。

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. 向 LLM 输入一条消息，点击发送（或按 Enter 键）。LLM 需要几秒钟加载到内存中，然后你将看到响应流式呈现。

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. 点击界面左上角的下拉菜单。这将显示你已安装的 Lemonade 模型。选择一个以继续（示例：`Qwen3.5-4B-GGUF`）。

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. 向 LLM 输入一条消息，点击发送（或按 Enter 键）。LLM 需要几秒钟加载到内存中，然后你将看到响应流式呈现。

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. 模型将在聊天中做出响应。

4. 此时，打开系统上的 `Task Manager`。你将看到**GPU 或 NPU 利用率较高**，具体取决于你所选择的模型是 **Hybrid** 还是 **NPU** 模型。通过任务管理器，你可以确认你正在本地运行该模型。

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. 点击界面左上角的下拉菜单。这将显示你已安装的 Lemonade 模型。选择一个以继续（示例：`Qwen3.5-4B-GGUF`）。

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. 向 LLM 输入一条消息，点击发送（或按 Enter 键）。LLM 需要几秒钟加载到内存中，然后你将看到响应流式呈现。

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. 模型将在聊天中做出响应。
<!-- @os:end -->

这验证了 Open WebUI 能够通过 OpenAI 兼容的聊天端点向 Lemonade 发送请求。

---

### 活动 2：上传图片并提问（视觉）

这需要一个支持图像输入的模型（视觉或多模态模型）。

1. 点击过滤器图标，选择“By Category”，然后从**Vision**部分选择一个模型（例如 `Qwen3.5-4B-GGUF`）

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. 点击消息框中的**`+`**按钮并上传一张图片
3. 提出一个需要真正理解图像的问题：`Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. 模型会根据图像内容作答，而不是泛泛的文本回答。

这证明了 Open WebUI 能够通过后端（Lemonade）向视觉模型发送多模态请求（文本 + 图像）。

---

<!-- @os:windows -->
### 活动 3：根据文本提示生成图像（Stable Diffusion）

Stable Diffusion 模型不支持文本生成，它们只能通过 Images API 生成图像。

#### 步骤 1：在 Open WebUI 中配置图像生成

1. 在 Lemonade GUI（`http://localhost:13305`）中，搜索 `SDXL-Turbo`（快速）或 `SDXL-Base-1.0`（更高质量）并下载。
2. 前往**Admin Settings → Images**（http://localhost:8080/admin/settings/images）
3. 设置：
   - **Image Generation：** ON
   - **Image Generation Engine：** Default (OpenAI)
   - **OpenAI API Base URL：** `http://localhost:13305/api/v1`
   - **OpenAI API Key：** `-`
   - **Model：** `SDXL-Turbo` 或 `SDXL-Base-1.0`
4. 如果你想添加更多参数，请将它们以 JSON 格式添加到文本字段中。例如：`{ "steps": 4, "cfg_scale": 1 }`。可用参数请参见 [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html)。

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. 保存
#### 步骤 2：为该模型启用图像生成
此步骤将确保您为模型启用图像生成能力。
1. 前往 **Admin Settings → Models**（http://localhost:8080/admin/settings/models）并选择您的模型
2. 打开 `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### 步骤 3：从聊天界面生成图像

1. 返回 `http://localhost:8080` 的聊天界面。
2. 在模型下拉列表中选择一个**文本生成 LLM**（例如：Qwen、Llama）。**请勿选择 Stable Diffusion 模型**，因为这是一个聊天模型选择器。
3. 在消息区域，点击 **Integrations**，并将 **Image** 开关打开。
4. 使用类似这样的提示词：`A cinematic photo of heavy traffic at sunset, ultra detailed`。
5. 系统将生成一张图像并显示在聊天中。

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

这说明 Open WebUI 可以协调一个“两部分”工作流：
  - LLM 帮助完善提示词
  - 图像通过 Lemonade 的 Images 接口使用 Stable Diffusion 生成
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### 活动 3：根据文本提示词生成图像（Stable Diffusion）

Stable Diffusion 模型不支持文本生成，它们仅通过 Images API 生成图像。

#### 步骤 1：在 Open WebUI 中配置图像生成

1. 在 Lemonade GUI（`http://localhost:13305`）中，搜索 `SDXL-Turbo`（速度快）或 `SDXL-Base-1.0`（质量更高）并下载。
2. 前往 **Admin Settings → Images**（http://localhost:8080/admin/settings/images）
3. 设置：
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` 或 `SDXL-Base-1.0`
4. 如果您想添加更多参数，请将其以 JSON 格式添加到文本字段中。例如：`{ "steps": 4, "cfg_scale": 1 }`。可用参数请参见 [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html)。

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. 保存


#### 步骤 2：为该模型启用图像生成
此步骤将确保您为模型启用图像生成能力。
1. 前往 **Admin Settings → Models**（http://localhost:8080/admin/settings/models）并选择您的模型
2. 打开 `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### 步骤 3：从聊天界面生成图像

1. 返回 `http://localhost:8080` 的聊天界面。
2. 在模型下拉列表中选择一个**文本生成 LLM**（例如：Qwen、Llama）。**请勿选择 Stable Diffusion 模型**，因为这是一个聊天模型选择器。
3. 在消息区域，点击 **Integrations**，并将 **Image** 开关打开。
4. 使用类似这样的提示词：`A cinematic photo of heavy traffic at sunset, ultra detailed`。
5. 系统将生成一张图像并显示在聊天中。

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

这说明 Open WebUI 可以协调一个“两部分”工作流：
  - LLM 帮助完善提示词
  - 图像通过 Lemonade 的 Images 接口使用 Stable Diffusion 生成
<!-- @device:end -->
<!-- @os:end -->

---

## 故障排除

### “Open WebUI 中未显示任何模型”
- 首先，检查 Lemonade：在浏览器中打开 `http://localhost:13305/api/v1/models`，确认您的模型已列出并已下载
- 然后，检查 Open WebUI 的连接：前往 `http://localhost:8080/admin/settings/connections` 的 **Admin Settings → Connections**，并验证 Base URL 是否为 `http://localhost:13305/api/v1`

### “This model does not support chat completion” 错误提示
- 您在聊天模型下拉列表中选择了图像模型（SDXL-Turbo / SDXL-Base-1.0）。
- **解决方法**：为聊天选择一个 LLM，并使用 Image 开关 + Images 设置进行图像生成。
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### 图像生成错误/超时
- 先从 `SDXL-Turbo` 开始（速度快、步数少）
- 运行正常后，再将图像模型切换为 `SDXL-Base-1.0` 以获得更高质量

---

## 后续步骤

现在您已拥有一个可正常运行的**“本地 AI 技术栈”**——通过标准 API，用单一界面控制多种模型类型。

以下是三项可解锁全新工作流的扩展：

### 1. 使用 Whisper 进行语音转文本

尝试使用 Whisper 模型将音频转换为文本，然后将其输入 LLM 进行摘要、生成待办事项或改写。这是会议记录和语音驱动助手的基础。

### 2. 在 Open WebUI 中进行 Python 编程

使用 Open WebUI 内置的代码执行功能来运行 Python 代码片段、查看输出，并更快地迭代——无需离开该界面。[参考资料](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. 在 Open WebUI 中渲染 HTML

直接在界面中渲染 HTML 输出。这在构建快速原型、格式化报告和交互式代码片段方面出乎意料地强大。[参考资料](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## 参考资料

- [Open WebUI（GitHub）](https://github.com/open-webui/open-webui)
- [Lemonade（GitHub）](https://github.com/lemonade-sdk/lemonade)
- [Lemonade Server 文档](https://lemonade-server.ai/docs)
- [Lemonade Server CLI](https://lemonade-server.ai/docs/lemonade-cli/)
- [Lemonade ↔ Open WebUI 集成指南](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Lemonade Server API 规范（接口）](https://lemonade-server.ai/docs/server/server_spec)
- [视频演示（Lemonade）](https://www.youtube.com/watch?v=mcf7dDybUco)
- [视频演示（Open WebUI + Lemonade）](https://www.youtube.com/watch?v=yZs-Yzl736E)

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