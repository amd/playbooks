<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maschinelle Übersetzung.** Diese Seite wurde automatisch aus dem Englischen übersetzt und nicht von einem Menschen überprüft. Sie kann Fehler enthalten, und bestimmte Anweisungen, Befehle, Downloads, Produktverfügbarkeiten oder andere Inhalte können je nach Sprache oder Region abweichen. Im Falle von Unstimmigkeiten oder Widersprüchen ist die englische Originalversion des playbook maßgeblich und hat Vorrang.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Dieses Playbook erfordert mindestens **32 GB** Arbeitsspeicher.
<!-- @device:end -->

## Übersicht

[Open WebUI](https://docs.openwebui.com) ist eine selbst gehostete, browserbasierte Oberfläche, die ein vertrautes Chatbot-Erlebnis bietet und dabei als Frontend für einen oder mehrere KI-Modellserver fungiert. Anstatt an einen einzigen Anbieter gebunden zu sein, kann Open WebUI eine Verbindung zu **jedem Backend herstellen, das eine OpenAI-kompatible API bereitstellt**, sodass Sie Modelle und Funktionen wechseln können, ohne die Benutzeroberfläche zu tauschen.

In diesem Playbook verwenden wir [**Lemonade**](https://lemonade-server.ai) als Backend, da es einen **einheitlichen, OpenAI-kompatiblen Endpunkt** bereitstellt, der mehrere Modalitäten unterstützt:
- **Large Language Models (LLMs)** zur Texterzeugung
- **Vision-Modelle** zum Verstehen von Bildern
- **Stable Diffusion** zur Bilderzeugung
- **Audio-Transkriptionsmodelle** für Sprache-zu-Text

Dieses Setup ermöglicht es Ihnen, den **kompletten multimodalen Workflow von Anfang bis Ende** zu erkunden.

---

## Was Sie lernen werden

Am Ende sind Sie in der Lage:

- Open WebUI mit einem lokalen, OpenAI-kompatiblen Backend (Lemonade) zu verbinden
- Über Ihren Browser mit einem lokalen LLM zu chatten
- Ein Bild hochzuladen und einem Vision-Modell Fragen dazu zu stellen
- Bilder aus Textprompts mit Stable-Diffusion-Modellen zu erzeugen (SDXL-Turbo / SDXL)
- Das mentale Modell zu verstehen, sodass Sie auch andere Backends nutzen können (Ollama, vLLM, llama.cpp server usw.)

---

## Grundkonzepte (Mentales Modell)

### Die drei Komponenten

| Komponente | Was sie macht | Beispiele |
|---|---|---|
| Frontend (UI) | Die Web-App, mit der Sie interagieren | Open WebUI |
| Backend (Modellserver) | Hostet Modelle und stellt HTTP-Endpunkte bereit | Lemonade, Ollama, vLLM, llama.cpp server, OpenAI-kompatible Server |
| Modelle | Die eigentlichen LLM-/Vision-/Diffusion-/Audio-Modelle | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### Warum „OpenAI-kompatible API“ wichtig ist

Open WebUI basiert auf standardmäßigen Endpunkten im OpenAI-Stil, wie zum Beispiel:
  - Chat: `/chat/completions`
  - Modellliste: `/models`
  - Bilderzeugung: `/images/generations`
  - Audio-Transkription: `/audio/transcriptions`

Lemonade stellt diese unter `http://localhost:13305/api/v1/...` bereit.

Wenn ein Backend diese Endpunkte unterstützt, kann Open WebUI mit minimalem Konfigurationsaufwand damit kommunizieren. Deshalb können wir Backends wechseln, ohne unseren Workflow zu ändern.

#### Zwei Dienste, zwei Ports

Im Verlauf dieses Playbooks arbeiten Sie mit zwei separaten Diensten:

| Dienst | URL | Was Sie dort tun |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | Modelle durchsuchen, herunterladen und verwalten |
| **Open WebUI** | `http://localhost:8080` | Chatten, Bilder hochladen, Bilder generieren — die Benutzeroberfläche |

Lemonade führt die Modelle aus; Open WebUI ist die Oberfläche, mit der Sie interagieren. Verwenden Sie zuerst die Lemonade-GUI, um Ihre Modelle herunterzuladen, und nutzen Sie sie anschließend über Open WebUI.

---

<!-- @device:halo_box,halo,stx,krk -->
## Einrichten der Speicherkonfiguration

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Nach Software-Updates suchen

<!-- @require:software-update -->
<!-- @device:end -->

## Einmalige Einrichtung

Für dieses Playbook muss Lemonade als Backend laufen und unter Linux zusätzlich eine Container-Engine (Podman), um Open WebUI auszuführen. Richten Sie dies ein, bevor Sie Open WebUI installieren.

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

## Modelle in Lemonade herunterladen

Bevor Sie Open WebUI installieren, stellen Sie sicher, dass die Modelle, die Sie verwenden möchten, in Lemonade heruntergeladen und einsatzbereit sind.

1. Öffnen Sie die Lemonade-GUI unter `http://localhost:13305`.
2. Durchsuchen Sie die verfügbaren Modelle und laden Sie die gewünschten herunter (z. B. ein LLM für den Chat, ein Vision-Modell und/oder ein Stable-Diffusion-Modell zur Bilderzeugung).
3. Bestätigen Sie, dass die API erreichbar ist, indem Sie `http://localhost:13305/api/v1/models` in Ihrem Browser aufrufen — Sie sollten dort Ihre heruntergeladenen Modelle sehen.

> Modelle müssen zunächst in **Lemonade** (`localhost:13305`) heruntergeladen werden, bevor sie in **Open WebUI** (`localhost:8080`) erscheinen können. Wenn ein Modell später nicht in Open WebUI angezeigt wird, kommen Sie hierher zurück und prüfen Sie zuerst Lemonade.


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
  $pngImg = "iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAIAAABLbSncAAAAEUlEQVR42mP4z8CAFTEMLQkAKP8/wc53yE8AAAAASUVORK5CYII="
  $dataUrl = "data:image/png;base64,$pngImg"
  $visionBody = @{
    model = "Qwen3.5-4B-GGUF"
    messages = @(@{
      role = "user"
      content = @(
        @{ type = "text"; text = "What color is this image? Reply with only the color name." },
        @{ type = "image_url"; image_url = @{ url = $dataUrl } }
      )
    })
    temperature = 0
    max_tokens = 512
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
  if ($visionText -notmatch "(?i)red") { throw "Vision test failed. Got: $visionText. Raw response: $visionOut" }
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
  $pngImg = "iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAIAAABLbSncAAAAEUlEQVR42mP4z8CAFTEMLQkAKP8/wc53yE8AAAAASUVORK5CYII="
  $dataUrl = "data:image/png;base64,$pngImg"
  $visionBody = @{
    model = "Qwen3.5-4B-GGUF"
    messages = @(@{
      role = "user"
      content = @(
        @{ type = "text"; text = "What color is this image? Reply with only the color name." },
        @{ type = "image_url"; image_url = @{ url = $dataUrl } }
      )
    })
    temperature = 0
    max_tokens = 512
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
  if ($visionText -notmatch "(?i)red") { throw "Vision test failed. Got: $visionText. Raw response: $visionOut" }
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
png_img = "iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAIAAABLbSncAAAAEUlEQVR42mP4z8CAFTEMLQkAKP8/wc53yE8AAAAASUVORK5CYII="
data_url = "data:image/png;base64," + png_img
vision = post_json("http://127.0.0.1:13305/api/v1/chat/completions", {
  "model": "Qwen3.5-4B-GGUF",
  "messages": [{
    "role": "user",
    "content": [
      {"type": "text", "text": "What color is this image? Reply with only the color name."},
      {"type": "image_url", "image_url": {"url": data_url}},
    ],
  }],
  "temperature": 0,
  "max_tokens": 512,
}, timeout=300)
if not vision.get("choices"):
  raise SystemExit(f"Unexpected vision response (no choices). Raw response:\n{json.dumps(vision, indent=2)}")
vtext = vision["choices"][0]["message"].get("content", "")
if not vtext.strip():
  raise SystemExit(f"Vision returned empty content. Raw response:\n{json.dumps(vision, indent=2)}")
if "red" not in vtext.lower():
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

## Open WebUI installieren

<!-- @os:windows -->
### 1. Python 3.12 installieren

Open WebUI benötigt **Python 3.12** — es lässt sich nicht auf Python 3.13+ installieren. Mit dem Windows Python Launcher (`py`) können Sie 3.12 parallel zu einer bereits vorhandenen Python-Version installieren, ohne Konflikte zu verursachen.

```powershell
winget install Python.Python.3.12
```

Schließen und öffnen Sie Ihr Terminal nach der Installation erneut und überprüfen Sie dann:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Hinweis:** Auf Ihrem System ist bereits Python 3.13 vorinstalliert. Die Installation von 3.12 hat darauf keine Auswirkungen — `python` verwendet weiterhin 3.13, und `py -3.12` richtet sich nur dann gezielt an 3.12, wenn Sie es benötigen.
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

### 2. Eine virtuelle Umgebung erstellen und Open WebUI installieren

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
Wir verwenden nun den Podman-Dienst, um unsere Open-WebUI-Installation zu containerisieren.

Bitte laden Sie Folgendes in ein Verzeichnis Ihrer Wahl herunter: [compose.yml](assets/compose.yml)

Führen Sie in diesem Verzeichnis den folgenden Befehl aus:

```bash
podman compose up -d
```

Dadurch wird das Open-WebUI-Image heruntergeladen und in einen persistenten Speicher geschrieben.

Starten Sie Open WebUI, indem Sie `localhost:8080` in die Adressleiste Ihres Browsers eingeben.

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

> **Tipp**: Open WebUI bietet auf seinem [GitHub](https://github.com/open-webui/open-webui) auch weitere Installationsmöglichkeiten an.
## Starten des Open WebUI Servers

<!-- @os:windows -->
- Führen Sie den folgenden Befehl aus, um den Open WebUI HTTP-Server zu starten:
```bash
open-webui serve
```
<!-- @os:end -->

- Navigieren Sie in einem Browser zu `http://localhost:8080`.
- Open WebUI fordert Sie auf, ein lokales Administratorkonto zu erstellen. Sobald Sie angemeldet sind, sehen Sie die Chat-Oberfläche.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> Lassen Sie das Terminalfenster geöffnet. Wenn Sie es schließen, wird Open WebUI beendet.
<!-- @os:end -->

<!-- @os:linux -->
> Der Container läuft im Hintergrund. Verwalten Sie ihn aus dem Verzeichnis, das `compose.yml` enthält, mit `podman compose down` (stoppen) und `podman compose up -d` (starten). Ihre Konten und Einstellungen bleiben im Volume `open_webui_data` erhalten.
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

## Open WebUI mit Lemonade verbinden

Da nun beide Dienste laufen — Lemonade unter `localhost:13305` und Open WebUI unter `localhost:8080` — verbinden Sie sie, damit Open WebUI die Modelle von Lemonade nutzen kann.

In Open WebUI:

1. Klicken Sie auf das **Benutzerprofil-Symbol** oben rechts und wählen Sie dann **Settings**.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. Klicken Sie im Settings-Bereich unten links auf **Admin Settings**.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. Klicken Sie in der Seitenleiste der Admin Settings auf **Connections** (oder navigieren Sie direkt zu `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. Fügen Sie unter **OpenAI API** eine neue Verbindung hinzu:
   - **Base URL:** `http://localhost:13305/api/v1`
   - **API Key:** `-` (ein einzelner Bindestrich funktioniert für lokale Nutzung)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. Stellen Sie sicher, dass unter **„Manage OpenAI API Connections"** nur `http://localhost:13305/api/v1` aktiviert ist. Deaktivieren Sie alle anderen Verbindungen (z. B. die standardmäßige OpenAI-Verbindung).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. Klicken Sie auf **Save**.

7. **(Empfohlen)** Deaktivieren Sie automatische Generierungsfunktionen, damit Open WebUI mit lokalen LLMs reaktionsschnell bleibt. Gehen Sie zu **Admin Settings → Settings → Interface** und schalten Sie Folgendes aus:
   - Title Generation
   - Follow Up Generation
   - Tags Generation

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. Klicken Sie auf **Save** und kehren Sie dann zu `http://localhost:8080` zurück.
9. Klicken Sie auf das Modell-Dropdown-Menü — Sie sollten die von Lemonade heruntergeladenen Modelle sehen.

---

## Hauptaktivitäten

Jetzt sind Sie vollständig eingerichtet. Schauen wir uns drei interessante Dinge an, die Sie tun können.

---

### Aktivität 1: Chatten mit einem lokalen LLM
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Klicken Sie auf das Dropdown-Menü oben links in der Oberfläche. Dies zeigt die installierten Lemonade-Modelle an. Wählen Sie eines aus, um fortzufahren. (Beispiel: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. Geben Sie eine Nachricht an das LLM ein und klicken Sie auf Senden (oder drücken Sie Enter). Das LLM benötigt einige Sekunden, um in den Speicher geladen zu werden, danach sehen Sie die Antwort als Stream eintreffen.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Klicken Sie auf das Dropdown-Menü oben links in der Oberfläche. Dies zeigt die installierten Lemonade-Modelle an. Wählen Sie eines aus, um fortzufahren. (Beispiel: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Geben Sie eine Nachricht an das LLM ein und klicken Sie auf Senden (oder drücken Sie Enter). Das LLM benötigt einige Sekunden, um in den Speicher geladen zu werden, danach sehen Sie die Antwort als Stream eintreffen.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. Das Modell antwortet im Chat.

4. Öffnen Sie zu diesem Zeitpunkt den `Task Manager` auf Ihrem System. Sie sehen eine **hohe GPU- oder NPU-Auslastung**, je nachdem, ob das ausgewählte Modell **Hybrid** oder **NPU** ist. Mit dem Task-Manager können Sie bestätigen, dass Sie das Modell lokal ausführen.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Klicken Sie auf das Dropdown-Menü oben links in der Oberfläche. Dies zeigt die installierten Lemonade-Modelle an. Wählen Sie eines aus, um fortzufahren. (Beispiel: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Geben Sie eine Nachricht an das LLM ein und klicken Sie auf Senden (oder drücken Sie Enter). Das LLM benötigt einige Sekunden, um in den Speicher geladen zu werden, danach sehen Sie die Antwort als Stream eintreffen.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. Das Modell antwortet im Chat.
<!-- @os:end -->

Dies bestätigt, dass Open WebUI Anfragen über den OpenAI-kompatiblen Chat-Endpunkt an Lemonade senden kann.

---

### Aktivität 2: Ein Bild hochladen und Fragen stellen (Vision)

Dies erfordert ein Modell, das Bildeingaben unterstützt (ein Vision- oder Multimodal-Modell).

1. Klicken Sie auf das Filtersymbol, wählen Sie „By Category“ und wählen Sie dann ein Modell aus dem Abschnitt **Vision** (z. B. `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. Klicken Sie auf die Schaltfläche **`+`** im Nachrichtenfeld und laden Sie ein Bild hoch
3. Stellen Sie eine Frage, die ein echtes Bildverständnis erfordert: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. Das Modell antwortet basierend auf dem Bildinhalt, nicht mit generischem Text.

Dies zeigt, dass Open WebUI multimodale Anfragen (Text + Bild) über das Backend (Lemonade) an ein Vision-Modell senden kann.

---

<!-- @os:windows -->
### Aktivität 3: Ein Bild aus einem Text-Prompt generieren (Stable Diffusion)

Stable-Diffusion-Modelle unterstützen keine Textgenerierung, sie generieren nur Bilder über die Images-API. 

#### Schritt 1: Bildgenerierung in Open WebUI konfigurieren

1. Suchen Sie in der Lemonade-GUI (`http://localhost:13305`) nach `SDXL-Turbo` (schnell) oder `SDXL-Base-1.0` (höhere Qualität) und laden Sie es herunter.
2. Gehen Sie zu **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Legen Sie Folgendes fest:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` oder `SDXL-Base-1.0`
4. Wenn Sie weitere Parameter hinzufügen möchten, fügen Sie diese als JSON in das Textfeld ein. Zum Beispiel: `{ "steps": 4, "cfg_scale": 1 }`. Verfügbare Parameter finden Sie unter [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Speichern
#### Schritt 2: Bilderzeugung für das Modell zulassen
Dieser Schritt stellt sicher, dass Sie Bilderzeugung als Fähigkeit für Ihr Modell aktivieren.
1. Gehen Sie zu **Admin Settings → Models** (http://localhost:8080/admin/settings/models) und wählen Sie Ihr Modell aus
2. Aktivieren Sie `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Schritt 3: Ein Bild über den Chat-Bildschirm generieren

1. Gehen Sie zurück zum Chat unter `http://localhost:8080`.
2. Wählen Sie im Modell-Dropdown ein **Text Generation LLM** aus (Beispiel: Qwen, Llama). **Wählen Sie kein Stable-Diffusion-Modell aus**, da dies ein Auswahlmenü für Chat-Modelle ist.
3. Klicken Sie im Nachrichtenbereich auf **Integrations** und schalten Sie **Image** ein.
4. Verwenden Sie einen Prompt wie: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Ein Bild wird erzeugt und erscheint im Chat.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Dies zeigt, dass Open WebUI einen „zweiteiligen“ Arbeitsablauf koordinieren kann:
  - Das LLM hilft, den Prompt zu verfeinern
  - Das Bild wird über Lemonades Images-Endpunkt mithilfe von Stable Diffusion erzeugt
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Aktivität 3: Ein Bild aus einem Text-Prompt generieren (Stable Diffusion)

Stable-Diffusion-Modelle unterstützen keine Textgenerierung, sie erzeugen Bilder ausschließlich über die Images-API.

#### Schritt 1: Bilderzeugung in Open WebUI konfigurieren

1. Suchen Sie in der Lemonade-GUI (`http://localhost:13305`) nach `SDXL-Turbo` (schnell) oder `SDXL-Base-1.0` (höhere Qualität) und laden Sie es herunter.
2. Gehen Sie zu **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Stellen Sie Folgendes ein:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` oder `SDXL-Base-1.0`
4. Wenn Sie weitere Parameter hinzufügen möchten, fügen Sie diese als JSON in das Textfeld ein. Zum Beispiel: `{ "steps": 4, "cfg_scale": 1 }`. Verfügbare Parameter finden Sie unter [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Speichern


#### Schritt 2: Bilderzeugung für das Modell zulassen
Dieser Schritt stellt sicher, dass Sie Bilderzeugung als Fähigkeit für Ihr Modell aktivieren.
1. Gehen Sie zu **Admin Settings → Models** (http://localhost:8080/admin/settings/models) und wählen Sie Ihr Modell aus
2. Aktivieren Sie `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Schritt 3: Ein Bild über den Chat-Bildschirm generieren

1. Gehen Sie zurück zum Chat unter `http://localhost:8080`.
2. Wählen Sie im Modell-Dropdown ein **Text Generation LLM** aus (Beispiel: Qwen, Llama). **Wählen Sie kein Stable-Diffusion-Modell aus**, da dies ein Auswahlmenü für Chat-Modelle ist.
3. Klicken Sie im Nachrichtenbereich auf **Integrations** und schalten Sie **Image** ein.
4. Verwenden Sie einen Prompt wie: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Ein Bild wird erzeugt und erscheint im Chat.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Dies zeigt, dass Open WebUI einen „zweiteiligen“ Arbeitsablauf koordinieren kann:
  - Das LLM hilft, den Prompt zu verfeinern
  - Das Bild wird über Lemonades Images-Endpunkt mithilfe von Stable Diffusion erzeugt
<!-- @device:end -->
<!-- @os:end -->

---

## Fehlerbehebung

### „In Open WebUI werden keine Modelle angezeigt“
- Überprüfen Sie zuerst Lemonade: Öffnen Sie `http://localhost:13305/api/v1/models` in einem Browser und bestätigen Sie, dass Ihre Modelle aufgelistet und heruntergeladen sind
- Überprüfen Sie anschließend die Open-WebUI-Verbindung: Gehen Sie zu **Admin Settings → Connections** unter `http://localhost:8080/admin/settings/connections` und stellen Sie sicher, dass die Base-URL `http://localhost:13305/api/v1` lautet

### Fehlermeldung „This model does not support chat completion“
- Sie haben ein Bildmodell (SDXL-Turbo / SDXL-Base-1.0) im Chat-Modell-Dropdown ausgewählt.
- **Lösung**: Wählen Sie ein LLM für den Chat aus und verwenden Sie den Image-Umschalter sowie die Images-Einstellungen für die Generierung.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Fehler/Zeitüberschreitungen bei der Bilderzeugung
- Beginnen Sie zunächst mit `SDXL-Turbo` (schnell, weniger Schritte)
- Sobald es funktioniert, wechseln Sie für höhere Qualität zum Bildmodell `SDXL-Base-1.0`

---

## Nächste Schritte

Sie verfügen nun über einen funktionierenden **„lokalen KI-Stack“**, eine einzige Benutzeroberfläche, die mehrere Modelltypen über eine Standard-API steuert.

Hier sind drei Erweiterungen, die völlig neue Arbeitsabläufe eröffnen:

### 1. Sprache-zu-Text mit Whisper

Versuchen Sie, Audio mithilfe eines Whisper-Modells in Text umzuwandeln und diesen dann einem LLM zur Zusammenfassung, für Aktionspunkte oder zum Umformulieren zuzuführen. Dies ist die Grundlage für Besprechungsnotizen und sprachgesteuerte Assistenten.

### 2. Python-Programmierung in Open WebUI

Nutzen Sie die integrierte Code-Ausführungsfunktion von Open WebUI, um Python-Snippets auszuführen, Ausgaben zu prüfen und schneller zu iterieren – ohne die Benutzeroberfläche zu verlassen. [Referenz](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. HTML-Rendering in Open WebUI

Rendern Sie HTML-Ausgaben direkt in der Oberfläche. Dies ist überraschend leistungsstark zum Erstellen schneller Prototypen, formatierter Berichte und interaktiver Snippets. [Referenz](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## Referenzen

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Lemonade Server Dokumentation](https://lemonade-server.ai/docs)
- [Lemonade Server CLI](https://lemonade-server.ai/docs/lemonade-cli/)
- [Lemonade ↔ Open WebUI Integrationsanleitung](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Lemonade Server API-Spezifikation (Endpunkte)](https://lemonade-server.ai/docs/server/server_spec)
- [Video-Anleitung (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [Video-Anleitung (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)

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