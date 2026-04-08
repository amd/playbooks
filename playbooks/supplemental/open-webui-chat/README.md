<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# How to Chat with LLMs in Open WebUI

## Overview

Open WebUI is a self-hosted, browser-based interface that provides a familiar chatbot experience while acting as a frontend for one or more AI model servers. Instead of being tied to one provider, Open WebUI can connect to **any backend that exposes an OpenAI-compatible API**, so you can swap models and capabilities without switching UIs.

In this playbook, we use **Lemonade** as the backend because it exposes a **unified OpenAI-compatible endpoint** supporting multiple modalities:
- **LLMs** for text generation
- **Vision models** for image understanding
- **Stable Diffusion** for image generation
- **Audio transcription models** for speech-to-text

This setup enables you to explore the **complete multimodal workflow end-to-end**.

---

## Learning Objectives

By the end, you’ll be able to:

- Connect Open WebUI to a local OpenAI-compatible backend (Lemonade)
- Chat with a local LLM from your browser
- Upload an image and ask a vision model questions about it
- Generate images from text prompts using Stable Diffusion models (SD-Turbo / SDXL)
- Understand the mental model so you can swap in other backends later (Ollama, vLLM, llama.cpp server, etc.)

---

## Core Concepts (Mental Model)

### The Three Components

| Piece | What it does | Examples |
|---|---|---|
| Frontend (UI) | The web app you interact with | Open WebUI |
| Backend (Model Server) | Hosts models and exposes HTTP endpoints | Lemonade, Ollama, vLLM, llama.cpp server, OpenAI-compatible servers |
| Models | The actual LLM / vision / diffusion / audio models | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### Why “OpenAI-compatible API” matters

Open WebUI is built around standard OpenAI-style endpoints, like: 
  - Chat: `/chat/completions`
  - Models list: `/models`
  - Image generation: `/images/generations`
  - Audio transcription: `/audio/transcriptions`

Lemonade exposes these under `http://localhost:8000/api/v1/...`

If a backend supports those endpoints, Open WebUI can talk to it with minimal setup. That’s why we can switch backends without changing our workflow.

---

## One-Time Setup

This section establishes a stable local environment: Lemonade running, Open WebUI running, and a working connection between them.

### 1) Install Lemonade, Start Lemonade Server, and Download Models

<!-- @os:windows -->
- Install Lemonade (App + Server) using the `.msi` installer from the [official documentation page](https://lemonade-server.ai/install_options.html).
<!-- @os:end -->
<!-- @os:linux -->
- Install Lemonade (App + Server) by following the Linux distribution-specific package manager instructions on the [official documentation page](https://lemonade-server.ai/install_options.html).
<!-- @os:end -->
- Start the Lemonade server:
  -  Open Powershell
  -  Run the command: `lemonade-server serve`
- Verify server status:
  - In the same Powershell terminal, run: `lemonade-server status`
  - Expect to see `Server is running on port 8000`
  - Open the Lemonade Server app and download required models from the `Model Manager` tab

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Server App" width="600"/>
</p>

- Confirm the API is reachable:
  - Open `http://localhost:8000/api/v1/models` in your web browser.
  - You should see a JSON list of models downloaded in Lemonade

> If you don’t see your models in `http://localhost:8000/api/v1/models`, Open WebUI won’t be able to select them later.

<!-- @test:id=lemonade-cli-verify timeout=30 hidden=True -->
```bash
lemonade-server --version
```
<!-- @test:end --> 


<!-- @os:windows -->
<!-- @test:id=openwebui-lemonade-multimodal-smoke-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# Stop any stale server (safe if none running)
& lemonade-server stop 2>$null | Out-Null
Start-Sleep -Seconds 2

# Start server
$logOut = "$PWD\lemonade-openwebui-ci-out.log"
$logErr = "$PWD\lemonade-openwebui-ci-err.log"
$p = Start-Process -FilePath "lemonade-server" -ArgumentList "serve --no-tray --host 127.0.0.1 --port 8000" -NoNewWindow -PassThru `
  -RedirectStandardOutput $logOut -RedirectStandardError $logErr

try {
  # Wait for /models
  $modelsJson = $null
  for ($i=0; $i -lt 120; $i++) {
    $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:8000/api/v1/models
    if ($modelsJson) { break }
    Start-Sleep -Seconds 1
  }
  if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:8000" }
  Write-Host "OK: Lemonade server is responding"
  
  # Verify required models are present + downloaded
  $parsed = $modelsJson | ConvertFrom-Json
  $required = @(
    "Llama-3.2-1B-Instruct-Hybrid",
    "Gemma-3-4b-it-GGUF",
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
    model = "Llama-3.2-1B-Instruct-Hybrid"
    messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
    temperature = 0
    max_tokens = 50
    stream = $false
  } | ConvertTo-Json -Depth 6
  $tmpChat = Join-Path $env:TEMP "chat-body.json"
  [System.IO.File]::WriteAllText($tmpChat, $chatBody, [System.Text.UTF8Encoding]::new($false))
  $chatOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:8000/api/v1/chat/completions `
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
    model = "Gemma-3-4b-it-GGUF"
    messages = @(@{
      role = "user"
      content = @(
        @{ type = "text"; text = "If you can see an image input, reply with exactly: OK" },
        @{ type = "image_url"; image_url = @{ url = $dataUrl } }
      )
    })
    temperature = 0
    max_tokens = 32
  } | ConvertTo-Json -Depth 10
  $tmpVision = Join-Path $env:TEMP "vision-body.json"
  [System.IO.File]::WriteAllText($tmpVision, $visionBody, [System.Text.UTF8Encoding]::new($false))
  $visionOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:8000/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer -" `
    --data-binary "@$tmpVision"
  if (-not $visionOut) { throw "Empty response from vision chat/completions" }
  $visionParsed = $visionOut | ConvertFrom-Json
  $visionText = $visionParsed.choices[0].message.content
  if ($visionText -notmatch "\bOK\b") { throw "Vision test failed. Got: $visionText" }
  Write-Host "OK: Vision chat works"

  # Image generation smoke test
  $imgBody = @{
    model  = "SDXL-Turbo"
    prompt = "A simple red cube on a white table, studio lighting"
    size   = "256x256"
  } | ConvertTo-Json -Depth 6
  $tmpImg = Join-Path $env:TEMP "img-body.json"
  [System.IO.File]::WriteAllText($tmpImg, $imgBody, [System.Text.UTF8Encoding]::new($false))
  $imgOut = curl.exe -sS --fail-with-body --max-time 900 http://127.0.0.1:8000/api/v1/images/generations `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer -" `
    --data-binary "@$tmpImg"
  if (-not $imgOut) { throw "Empty response from images/generations" }
  $imgParsed = $imgOut | ConvertFrom-Json
  if (-not $imgParsed.data -or -not $imgParsed.data[0].b64_json) { throw "Image generation did not return data[0].b64_json" }
  Write-Host "OK: Image generation works"
}
finally {
  Remove-Item $tmpChat, $tmpVision, $tmpImg -Force -ErrorAction SilentlyContinue
  & lemonade-server stop 2>$null | Out-Null
  Start-Sleep -Seconds 2
  if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
  Write-Host "OK: Lemonade Server stopped successfully"
}
```
<!-- @test:end --> 
<!-- @os:end --> 

<!-- @os:linux --> 
<!-- @test:id=openwebui-lemonade-multimodal-smoke-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

lemonade-server stop >/dev/null 2>&1 || true
sleep 2

p=""
cleanup() {
  lemonade-server stop >/dev/null 2>&1 || true
  sleep 2
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

lemonade-server serve --host 127.0.0.1 --port 8000 >./lemonade-openwebui-ci.log 2>&1 &
p=$!

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:8000/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:8000"
  exit 1
fi
echo "OK: Lemonade server is responding"

export MODELS_JSON="$models_json"
python3 - <<'PY'
import base64, json, os, sys, urllib.request

data = json.loads(os.environ["MODELS_JSON"])
required = [
  "Llama-3.2-1B-Instruct-GGUF",
  "Gemma-3-4b-it-GGUF",
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
  with urllib.request.urlopen(req, timeout=timeout) as r:
    return json.loads(r.read().decode("utf-8"))

# LLM chat smoke test
chat = post_json("http://127.0.0.1:8000/api/v1/chat/completions", {
  "model": "Llama-3.2-1B-Instruct-GGUF",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 50,
}, timeout=300)
text = chat["choices"][0]["message"]["content"]
if "OK" not in text:
  raise SystemExit(f"LLM chat test failed. Got: {text}")
print("OK: LLM chat works")

# Vision smoke test (OpenAI image_url format)
png1x1 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO8p+S4AAAAASUVORK5CYII="
data_url = "data:image/png;base64," + png1x1
vision = post_json("http://127.0.0.1:8000/api/v1/chat/completions", {
  "model": "Gemma-3-4b-it-GGUF",
  "messages": [{
    "role": "user",
    "content": [
      {"type": "text", "text": "If you can see an image input, reply with exactly: OK"},
      {"type": "image_url", "image_url": {"url": data_url}},
    ],
  }],
  "temperature": 0,
  "max_tokens": 32,
}, timeout=300)
vtext = vision["choices"][0]["message"]["content"]
if "OK" not in vtext:
  raise SystemExit(f"Vision test failed. Got: {vtext}")
print("OK: Vision chat works")

# Image generation smoke test
img = post_json("http://127.0.0.1:8000/api/v1/images/generations", {
  "model": "SDXL-Turbo",
  "prompt": "A simple red cube on a white table, studio lighting",
  "size": "256x256",
}, timeout=900)
b64 = img.get("data", [{}])[0].get("b64_json")
if not b64:
  raise SystemExit("Image generation did not return data[0].b64_json")
print("OK: Image generation works")
PY
```
<!-- @test:end --> 
<!-- @os:end --> 


### 2) Install Open WebUI

<!-- @os:windows -->
Open PowerShell and create a fresh virtual environment:

```bash
# Install open-webui into a venv [Windows]
python -m venv openwebui-venv
.\openwebui-venv\Scripts\activate
python -m pip install --upgrade pip
pip install open-webui
```
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-env-check-windows timeout=1200 hidden=True -->
```powershell
python --version
where.exe python
python -c "import sys; print(sys.executable)"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openwebui-install-venv-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$venv = "$PWD\openwebui-venv-ci"
if (Test-Path $venv) { Remove-Item -Recurse -Force $venv }

python -m venv $venv
$py = Join-Path $venv "Scripts\python.exe"

& $py -m pip install --upgrade pip
& $py -m pip install open-webui
& $py -m pip install beautifulsoup4

if ($LASTEXITCODE -ne 0) { throw "pip install open-webui failed" }
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openwebui-install-check-windows timeout=1200 hidden=True -->
```powershell
$venv = "$PWD\openwebui-venv-ci"
$py = Join-Path $venv "Scripts\python.exe"
& $py -c "import open_webui; print('OK: import open_webui')"
& $py -c "import bs4; print('OK: bs4 import')"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openwebui-cli-windows timeout=1200 hidden=True -->
```powershell
$venv = "$PWD\openwebui-venv-ci"
$ow = Join-Path $venv "Scripts\open-webui.exe"

& $ow --help | Out-Null
Write-Host "OK: open-webui installed in venv"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
Open a terminal and create a fresh virtual environment:

```bash
# Install open-webui into a venv [Linux]
python3 -m venv openwebui-venv
source openwebui-venv/bin/activate
python -m pip install --upgrade pip
pip install open-webui
```
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=python-env-check-linux timeout=300 hidden=True -->
```bash
python3 --version
python3 -m pip --version
which python3
which pip3
python3 -c "import sys; print(sys.executable)"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux --> 
<!-- @test:id=openwebui-install-venv-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

venv="./openwebui-venv-ci"
rm -rf "$venv"
python3 -m venv "$venv"
py="$venv/bin/python"
ow="$venv/bin/open-webui"

"$py" -m pip install --upgrade pip
"$py" -m pip install open-webui
"$py" -m pip install beautifulsoup4
"$py" -c "import open_webui; print('OK: import open_webui')"
"$py" -c "import bs4; print('OK: bs4 import')"
"$ow" --help

echo "OK: open-webui installed in venv"
```
<!-- @test:end --> 
<!-- @os:end -->

> Note: Open WebUI also provides a variety of other installation options, such as Docker, on their GitHub.

### 3) Start Open WebUI Server

- Run this command to launch the Open WebUI HTTP server:
```bash
open-webui serve
```
- In a browser, navigate to `http://localhost:8080`.
- Open WebUI will ask you to create a local administrator account. Once you are signed in, you will see the chat interface.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>
  
> Keep the terminal window open. Closing it stops Open WebUI.


<!-- @os:windows -->
<!-- @test:id=openwebui-server-smoke-windows timeout=900 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$venv = "$PWD\openwebui-venv-ci"
$ow = Join-Path $venv "Scripts\open-webui.exe"
if (-not (Test-Path $ow)) { throw "open-webui not found. Run openwebui-install-venv-windows first." }

# Fresh data dir so auth mode/config isn't polluted by previous runs
$dataDir = "$PWD\openwebui-data-ci"
if (Test-Path $dataDir) { Remove-Item -Recurse -Force $dataDir }
New-Item -ItemType Directory -Force -Path $dataDir | Out-Null

$env:DATA_DIR = $dataDir
$env:WEBUI_AUTH = "False" # Disable auth for CI
$env:ENABLE_PERSISTENT_CONFIG = "False" # Ensure environment-variable config applies for the run and isn't overridden by persistent settings

$logOut = "$PWD\openwebui-ci-out.log"
$logErr = "$PWD\openwebui-ci-err.log" 
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
<!-- @test:id=openwebui-server-smoke-linux timeout=900 hidden=True -->
```bash
set -euo pipefail

venv="./openwebui-venv-ci"
ow="$venv/bin/open-webui"
if [ ! -x "$ow" ]; then
  echo "open-webui not found. Run openwebui-install-venv-linux first."
  exit 1
fi

data_dir="./openwebui-data-ci"
rm -rf "$data_dir"
mkdir -p "$data_dir"

export DATA_DIR="$data_dir"
export WEBUI_AUTH=False
export ENABLE_PERSISTENT_CONFIG=False

p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

"$ow" serve --port 8080 >./openwebui-ci.log 2>&1 &
p=$!

ok=""
for i in $(seq 1 90); do
  ok="$(curl -s --max-time 2 http://127.0.0.1:8080/health || true)"
  if [ -n "$ok" ]; then break; fi
  sleep 1
done

if [ -z "$ok" ]; then
  echo "Open WebUI not ready on http://127.0.0.1:8080"
  exit 1
fi

echo "OK: Open WebUI is responding on /health"
```
<!-- @test:end --> 
<!-- @os:end --> 


### 4) Connect Open WebUI to Lemonade

In Open WebUI:

1. Go to **Admin Settings → Connections**

<p align="center">
  <img src="assets/open_settings.png" alt="Open WebUI Settings page" width="200"/>
</p>
<p align="center">
  <img src="assets/connection_settings.png" alt="Navigating to the connection settings" width="500"/>
</p>

2. Under **OpenAI API**, add a new connection:
   - **Base URL:** `http://localhost:8000/api/v1`
   - **API Key:** `-` (a single dash works for local)
<p align="center">
  <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="500"/>
</p>

3. Save
4. Apply the following suggested settings. These help Open WebUI to be more responsive with local LLMs.
   - Click the user profile button again, and choose "Admin Settings".
   - Click the "Settings" tab at the top, then "Interface" (which will be on the top or the left, depending on your window size), then disable the following:
      - Title Generation
      - Follow Up Generation
      - Tags Generation
<p align="center">
  <img src="assets/admin_settings.png" alt="Admin Settings" width="600"/>
</p>

5. Click the **"Save"** button in the bottom right of the page, then return to `http://localhost:8080`.
6. Click the model dropdown and expect to see all the models that you have downloaded from Lemonade!

---

## Main Activities

Now you’re all set up. Let's look at three interesting things to do.

---

### Activity 1: Chat with a Local LLM

1. Click the dropdown menu in the top-left of the interface. This will display all of the Lemonade models you have installed. Select one to proceed. (example: `Llama-3.2-1B-Instruct-Hybrid`).
<p align="center">
  <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
</p>

2. Enter a message to the LLM and click send (or hit Enter). The LLM will take a few seconds to load into memory and then you will see the response stream in.
<p align="center">
  <img src="assets/sending_a_message.png" alt="Sending a message" width="53%"/>
  <img src="assets/llm_response.png" alt="LLM Response" width="40%"/>
</p>

3. The model will respond in the chat.
<!-- @os:windows -->
4. At this time, open `Task Manager` on your system. You will see **high GPU/NPU utilization** based on whether the model you selected is **Hybrid** or **NPU** respectively. That clearly shows you’re running locally.
<p align="center">
  <img src="assets/npu_utilization.png" alt="Task Manager NPU utilization" width="600"/>
</p>
<!-- @os:end -->
This validates that Open WebUI can send requests to Lemonade using the OpenAI-compatible chat endpoint.

---

### Activity 2: Upload an Image and Ask Questions (Vision)

This requires a model that supports image input (a vision / multimodal model).

1. Select a vision-capable model (example: `Gemma-3-4b-it-GGUF`, or any model labeled for vision in Lemonade)
<p align="center">
  <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
</p>

2. Click the **`+`** button in the message box and upload an image
3. Ask something that forces true image understanding: `Do you think this is a well-designed UI?`
<p align="center">
  <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="46%"/>
  <img src="assets/vlm_response.png" alt="VLM Response" width="47%"/>
</p>

4. The model answers based on the image content, not generic text.

This demonstrates that Open WebUI can send multimodal requests (text + image) through the backend (Lemonade) to a vision model.

---

### Activity 3: Generate an Image from a Text Prompt (Stable Diffusion)

Stable Diffusion models don't support text generation, they only generate images through the Images API. 

#### Step 1: Configure Image Generation in Open WebUI

1. Go to **Admin Settings → Images**
2. Set:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:8000/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SD-Turbo` (fast) or `SDXL-Base-1.0` (higher quality)
3. If you want to add more parameters, add them to the text field as JSON. For example: `{ "steps": 4, "cfg_scale": 1 }`. See available parameters at [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).
<p align="center">
  <img src="assets/images_settings.png" alt="Lemonade VLM's" width="600"/>
</p>
4. Save


#### Step 2: Allow Image Generation for the model
This step ensures that you enable Image Generation as a capability for your model.
1. Go to **Admin Settings → Models** and choose your model
2. Turn on `Image Generation`
<p align="center">
  <img src="assets/model_settings.png" alt="Model Settings" width="47%"/>
  <img src="assets/edit_model.png" alt="Edit Model" width="45%"/>
</p>

#### Step 3: Generate an image from the chat screen

1. Go back to chat at `http://localhost:8080`.
2. Select a **Text Generation LLM** in the model dropdown (example: DeepSeek, CodeLlama).  **Do not select a Stable Diffusion model** as this is a chat model selector.
3. In the message area, toggle **Image** ON.
4. Use a prompt like: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. An image is generated and appears in the chat.
<p align="center">
  <img src="assets/image_generation.png" alt="Image Generation" width="600"/>
</p>

This establishes that Open WebUI can coordinate a “two-part” workflow:
  - The LLM helps refine the prompt
  - The image is generated via Lemonade’s Images endpoint using Stable Diffusion

---

## Troubleshooting

### “No models show up”
- Confirm `http://localhost:8000/api/v1/models` loads in a browser
- Re-check Open WebUI connection Base URL: `http://localhost:8000/api/v1`

### “This model does not support chat completion” error message
- You selected an image model (SD-Turbo / SDXL) in the chat model dropdown.
- **Fix**: select an LLM for chat, and use the Image toggle + Images settings for generation.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Image generation errors/timeouts
- Start with `SD-Turbo` first (fast, fewer steps)
- Once working, switch the image model to `SDXL-Base-1.0` for quality

---

## Next Steps

You now have a working **“local AI stack”**, a single UI controlling multiple model types through a standard API.

Here are three expansions that unlock entirely new workflows:

### 1) Speech-to-Text with Whisper
Try turning audio into text using a Whisper model, then feed it into an LLM for summarization, action items, or rewriting. This is the foundation for meeting notes and voice-driven assistants.

### 2) Python Coding inside Open WebUI
Use Open WebUI’s built-in code execution experience to run Python snippets, inspect outputs, and iterate faster—without leaving the UI. [Reference](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3) HTML Rendering inside Open WebUI
Render HTML outputs directly in the interface. This is surprisingly powerful for building quick prototypes, formatted reports, and interactive snippets. [Reference](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## References

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Lemonade Server docs](https://lemonade-server.ai/docs)
- [Lemonade ↔ Open WebUI integration guide](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Lemonade Server API spec (endpoints)](https://lemonade-server.ai/docs/server/server_spec)
- [Video walkthrough (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [Video walkthrough (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)
