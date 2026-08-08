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
> Dieses Playbook erfordert mindestens **32GB** Arbeitsspeicher.
<!-- @device:end -->

## Übersicht

[Open WebUI](https://docs.openwebui.com) ist eine selbst gehostete, browserbasierte Oberfläche, die ein vertrautes Chatbot-Erlebnis bietet und gleichzeitig als Frontend für einen oder mehrere KI-Modellserver fungiert. Anstatt an einen einzigen Anbieter gebunden zu sein, kann Open WebUI eine Verbindung zu **jedem Backend herstellen, das eine OpenAI-kompatible API bereitstellt**, sodass Sie Modelle und Funktionen austauschen können, ohne die Benutzeroberfläche zu wechseln.

In diesem Playbook verwenden wir [**Lemonade**](https://lemonade-server.ai) als Backend, da es einen **einheitlichen, OpenAI-kompatiblen Endpunkt** bereitstellt, der mehrere Modalitäten unterstützt:
- **Large Language Models (LLMs)** für Textgenerierung
- **Vision-Modelle** für Bildverständnis
- **Stable Diffusion** für Bildgenerierung
- **Audio-Transkriptionsmodelle** für Sprache-zu-Text

Dieses Setup ermöglicht es Ihnen, den **kompletten multimodalen Workflow von Anfang bis Ende** zu erkunden.

---

## Was Sie lernen werden

Am Ende können Sie:

- Open WebUI mit einem lokalen, OpenAI-kompatiblen Backend (Lemonade) verbinden
- Mit einem lokalen LLM über Ihren Browser chatten
- Ein Bild hochladen und einem Vision-Modell Fragen dazu stellen
- Bilder aus Textprompts mithilfe von Stable-Diffusion-Modellen (SDXL-Turbo / SDXL) generieren
- Das mentale Modell verstehen, sodass Sie auch andere Backends (Ollama, vLLM, llama.cpp server usw.) verwenden können

---

## Kernkonzepte (Mentales Modell)

### Die drei Komponenten

| Komponente | Was sie tut | Beispiele |
|---|---|---|
| Frontend (UI) | Die Web-App, mit der Sie interagieren | Open WebUI |
| Backend (Modellserver) | Hostet Modelle und stellt HTTP-Endpunkte bereit | Lemonade, Ollama, vLLM, llama.cpp server, OpenAI-kompatible Server |
| Modelle | Die eigentlichen LLM-/Vision-/Diffusion-/Audio-Modelle | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### Warum „OpenAI-kompatible API“ wichtig ist

Open WebUI basiert auf standardisierten OpenAI-Endpunkten, wie zum Beispiel:
  - Chat: `/chat/completions`
  - Modellliste: `/models`
  - Bildgenerierung: `/images/generations`
  - Audio-Transkription: `/audio/transcriptions`

Lemonade stellt diese unter `http://localhost:13305/api/v1/...` bereit.

Wenn ein Backend diese Endpunkte unterstützt, kann Open WebUI mit minimalem Konfigurationsaufwand mit ihm kommunizieren. Deshalb können wir Backends wechseln, ohne unseren Workflow zu ändern.

#### Zwei Dienste, zwei Ports

Im Verlauf dieses Playbooks arbeiten Sie mit zwei separaten Diensten:

| Dienst | URL | Was Sie dort tun |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | Modelle durchsuchen, herunterladen und verwalten |
| **Open WebUI** | `http://localhost:8080` | Chatten, Bilder hochladen, Bilder generieren — die benutzerseitige Oberfläche |

Lemonade führt die Modelle aus; Open WebUI ist die Oberfläche, mit der Sie interagieren. Verwenden Sie zunächst die Lemonade-GUI, um Ihre Modelle herunterzuladen, und nutzen Sie sie anschließend über Open WebUI.

---

## Konfigurieren des Arbeitsspeichers

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Auf Software-Updates prüfen

<!-- @require:software-update -->
<!-- @device:end -->

## Einmalige Einrichtung

Für dieses Playbook muss Lemonade als Backend laufen und unter Linux eine Container-Engine (Podman) vorhanden sein, um Open WebUI auszuführen. Richten Sie diese ein, bevor Sie Open WebUI installieren.

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

## Herunterladen von Modellen in Lemonade

Bevor Sie Open WebUI installieren, stellen Sie sicher, dass die Modelle, die Sie verwenden möchten, in Lemonade heruntergeladen und einsatzbereit sind.

1. Öffnen Sie die Lemonade-GUI unter `http://localhost:13305`.
2. Durchsuchen Sie die verfügbaren Modelle und laden Sie die gewünschten herunter (z. B. ein LLM für den Chat, ein Vision-Modell und/oder ein Stable-Diffusion-Modell für die Bildgenerierung).
3. Bestätigen Sie, dass die API erreichbar ist, indem Sie `http://localhost:13305/api/v1/models` in Ihrem Browser aufrufen — Sie sollten dort Ihre heruntergeladenen Modelle sehen.

> Modelle müssen in **Lemonade** (`localhost:13305`) heruntergeladen werden, bevor sie in **Open WebUI** (`localhost:8080`) erscheinen können. Wenn ein Modell später nicht in Open WebUI angezeigt wird, kommen Sie hierher zurück und überprüfen Sie zuerst Lemonade.


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

## Installieren von Open WebUI

<!-- @os:windows -->
### 1. Python 3.12 installieren

Open WebUI erfordert **Python 3.12** — es lässt sich nicht unter Python 3.13+ installieren. Mit dem Windows Python Launcher (`py`) können Sie 3.12 parallel zu einer bereits vorhandenen Python-Version installieren, ohne Konflikte zu verursachen.

```powershell
winget install Python.Python.3.12
```

Schließen Sie nach der Installation Ihr Terminal und öffnen Sie es erneut, um dann Folgendes zu überprüfen:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Hinweis:** Auf Ihrem System ist bereits Python 3.13 vorinstalliert. Die Installation von 3.12 hat darauf keinen Einfluss — `python` verwendet weiterhin 3.13, und `py -3.12` verwendet 3.12 nur dann, wenn Sie es benötigen.
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

> **Tipp**: Open WebUI bietet auf [GitHub](https://github.com/open-webui/open-webui) auch weitere Installationsmöglichkeiten.
## Starten des Open WebUI-Servers

<!-- @os:windows -->
- Führen Sie den folgenden Befehl aus, um den Open WebUI-HTTP-Server zu starten:
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
> Der Container läuft im Hintergrund. Verwalten Sie ihn aus dem Verzeichnis, das die `compose.yml` enthält, mit `podman compose down` (Stoppen) und `podman compose up -d` (Starten). Ihre Konten und Einstellungen bleiben im Volume `open_webui_data` erhalten.
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

Da nun beide Dienste ausgeführt werden – Lemonade unter `localhost:13305` und Open WebUI unter `localhost:8080` – verbinden Sie diese, damit Open WebUI die Modelle von Lemonade verwenden kann.

Gehen Sie in Open WebUI wie folgt vor:

1. Klicken Sie oben rechts auf das **Benutzerprofilsymbol** und wählen Sie dann **Einstellungen** aus.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. Klicken Sie im Einstellungsbereich unten links auf **Admin-Einstellungen**.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. Klicken Sie in der Seitenleiste der Admin-Einstellungen auf **Verbindungen** (oder navigieren Sie direkt zu `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. Fügen Sie unter **OpenAI API** eine neue Verbindung hinzu:
   - **Basis-URL:** `http://localhost:13305/api/v1`
   - **API-Schlüssel:** `-` (ein einzelner Bindestrich funktioniert lokal)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. Stellen Sie sicher, dass unter **„OpenAI-API-Verbindungen verwalten“** nur `http://localhost:13305/api/v1` aktiviert ist. Deaktivieren Sie alle anderen Verbindungen (z. B. die standardmäßige OpenAI-Verbindung).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. Klicken Sie auf **Speichern**.

7. **(Empfohlen)** Deaktivieren Sie automatische Generierungsfunktionen, damit Open WebUI mit lokalen LLMs reaktionsschnell bleibt. Gehen Sie zu **Admin-Einstellungen → Einstellungen → Oberfläche** und deaktivieren Sie:
   - Titelgenerierung
   - Follow-up-Generierung
   - Tag-Generierung

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. Klicken Sie auf **Speichern** und kehren Sie dann zu `http://localhost:8080` zurück.
9. Klicken Sie auf das Modell-Dropdown-Menü — Sie sollten die von Lemonade heruntergeladenen Modelle sehen.

---

## Hauptaktivitäten

Jetzt sind Sie vollständig eingerichtet. Sehen wir uns drei interessante Dinge an, die Sie tun können.

---

### Aktivität 1: Chatten mit einem lokalen LLM
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Klicken Sie auf das Dropdown-Menü oben links in der Oberfläche. Dort werden die installierten Lemonade-Modelle angezeigt. Wählen Sie eines aus, um fortzufahren (Beispiel: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. Geben Sie eine Nachricht an das LLM ein und klicken Sie auf Senden (oder drücken Sie die Eingabetaste). Das LLM benötigt einige Sekunden, um in den Speicher geladen zu werden, danach sehen Sie die Antwort als Stream eintreffen.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Klicken Sie auf das Dropdown-Menü oben links in der Oberfläche. Dort werden die installierten Lemonade-Modelle angezeigt. Wählen Sie eines aus, um fortzufahren (Beispiel: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Geben Sie eine Nachricht an das LLM ein und klicken Sie auf Senden (oder drücken Sie die Eingabetaste). Das LLM benötigt einige Sekunden, um in den Speicher geladen zu werden, danach sehen Sie die Antwort als Stream eintreffen.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. Das Modell antwortet im Chat.

4. Öffnen Sie zu diesem Zeitpunkt den `Task Manager` auf Ihrem System. Sie sehen eine **hohe GPU- oder NPU-Auslastung**, je nachdem, ob das ausgewählte Modell **Hybrid** bzw. **NPU** ist. Mithilfe des Task-Managers können Sie bestätigen, dass Sie das Modell lokal ausführen.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Klicken Sie auf das Dropdown-Menü oben links in der Oberfläche. Dort werden die installierten Lemonade-Modelle angezeigt. Wählen Sie eines aus, um fortzufahren (Beispiel: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Geben Sie eine Nachricht an das LLM ein und klicken Sie auf Senden (oder drücken Sie die Eingabetaste). Das LLM benötigt einige Sekunden, um in den Speicher geladen zu werden, danach sehen Sie die Antwort als Stream eintreffen.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. Das Modell antwortet im Chat.
<!-- @os:end -->

Dies bestätigt, dass Open WebUI Anfragen über den OpenAI-kompatiblen Chat-Endpunkt an Lemonade senden kann.

---

### Aktivität 2: Ein Bild hochladen und Fragen dazu stellen (Vision)

Dafür ist ein Modell erforderlich, das Bildeingaben unterstützt (ein Vision- oder Multimodal-Modell).

1. Klicken Sie auf das Filtersymbol, wählen Sie „Nach Kategorie“ und wählen Sie dann ein Modell aus dem Bereich **Vision** aus (z. B. `Qwen3.5-4B-GGUF`)

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
### Aktivität 3: Ein Bild aus einer Textaufforderung generieren (Stable Diffusion)

Stable-Diffusion-Modelle unterstützen keine Textgenerierung, sie generieren nur Bilder über die Images API. 

#### Schritt 1: Bildgenerierung in Open WebUI konfigurieren

1. Suchen Sie in der Lemonade-GUI (`http://localhost:13305`) nach `SDXL-Turbo` (schnell) oder `SDXL-Base-1.0` (höhere Qualität) und laden Sie es herunter.
2. Gehen Sie zu **Admin-Einstellungen → Bilder** (http://localhost:8080/admin/settings/images)
3. Legen Sie Folgendes fest:
   - **Bildgenerierung:** EIN
   - **Bildgenerierungs-Engine:** Standard (OpenAI)
   - **OpenAI-API-Basis-URL:** `http://localhost:13305/api/v1`
   - **OpenAI-API-Schlüssel:** `-`
   - **Modell:** `SDXL-Turbo` oder `SDXL-Base-1.0`
4. Wenn Sie weitere Parameter hinzufügen möchten, fügen Sie diese als JSON in das Textfeld ein. Zum Beispiel: `{ "steps": 4, "cfg_scale": 1 }`. Verfügbare Parameter finden Sie unter [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Speichern
#### Schritt 2: Bilderzeugung für das Modell aktivieren
Dieser Schritt stellt sicher, dass Sie Bilderzeugung als Fähigkeit für Ihr Modell aktivieren.
1. Gehen Sie zu **Admin Settings → Models** (http://localhost:8080/admin/settings/models) und wählen Sie Ihr Modell aus
2. Schalten Sie `Image Generation` ein

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Schritt 3: Ein Bild über den Chat-Bildschirm generieren

1. Gehen Sie zurück zum Chat unter `http://localhost:8080`.
2. Wählen Sie ein **Text Generation LLM** im Modell-Dropdown aus (Beispiel: Qwen, Llama). **Wählen Sie kein Stable-Diffusion-Modell**, da dies ein Chat-Modell-Selektor ist.
3. Klicken Sie im Nachrichtenbereich auf **Integrations** und schalten Sie **Image** EIN.
4. Verwenden Sie einen Prompt wie: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Ein Bild wird generiert und erscheint im Chat.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Dies zeigt, dass Open WebUI einen „zweiteiligen“ Workflow koordinieren kann:
  - Das LLM hilft dabei, den Prompt zu verfeinern
  - Das Bild wird über den Images-Endpunkt von Lemonade mithilfe von Stable Diffusion generiert
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Aktivität 3: Ein Bild aus einem Text-Prompt generieren (Stable Diffusion)

Stable-Diffusion-Modelle unterstützen keine Textgenerierung, sie generieren Bilder nur über die Images-API.

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


#### Schritt 2: Bilderzeugung für das Modell aktivieren
Dieser Schritt stellt sicher, dass Sie Bilderzeugung als Fähigkeit für Ihr Modell aktivieren.
1. Gehen Sie zu **Admin Settings → Models** (http://localhost:8080/admin/settings/models) und wählen Sie Ihr Modell aus
2. Schalten Sie `Image Generation` ein

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Schritt 3: Ein Bild über den Chat-Bildschirm generieren

1. Gehen Sie zurück zum Chat unter `http://localhost:8080`.
2. Wählen Sie ein **Text Generation LLM** im Modell-Dropdown aus (Beispiel: Qwen, Llama). **Wählen Sie kein Stable-Diffusion-Modell**, da dies ein Chat-Modell-Selektor ist.
3. Klicken Sie im Nachrichtenbereich auf **Integrations** und schalten Sie **Image** EIN.
4. Verwenden Sie einen Prompt wie: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Ein Bild wird generiert und erscheint im Chat.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Dies zeigt, dass Open WebUI einen „zweiteiligen“ Workflow koordinieren kann:
  - Das LLM hilft dabei, den Prompt zu verfeinern
  - Das Bild wird über den Images-Endpunkt von Lemonade mithilfe von Stable Diffusion generiert
<!-- @device:end -->
<!-- @os:end -->

---

## Fehlerbehebung

### „Keine Modelle werden in Open WebUI angezeigt“
- Überprüfen Sie zunächst Lemonade: Öffnen Sie `http://localhost:13305/api/v1/models` in einem Browser und bestätigen Sie, dass Ihre Modelle aufgelistet und heruntergeladen sind
- Überprüfen Sie anschließend die Open-WebUI-Verbindung: Gehen Sie zu **Admin Settings → Connections** unter `http://localhost:8080/admin/settings/connections` und stellen Sie sicher, dass die Base URL `http://localhost:13305/api/v1` lautet

### Fehlermeldung „This model does not support chat completion“
- Sie haben ein Bildmodell (SDXL-Turbo / SDXL-Base-1.0) im Chat-Modell-Dropdown ausgewählt.
- **Lösung**: Wählen Sie für den Chat ein LLM aus und verwenden Sie den Image-Umschalter + die Images-Einstellungen zur Generierung.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Fehler/Zeitüberschreitungen bei der Bilderzeugung
- Beginnen Sie zunächst mit `SDXL-Turbo` (schnell, weniger Schritte)
- Sobald es funktioniert, wechseln Sie für höhere Qualität zum Bildmodell `SDXL-Base-1.0`

---

## Nächste Schritte

Sie verfügen nun über einen funktionierenden **„lokalen KI-Stack“**, eine einzige Benutzeroberfläche, die mehrere Modelltypen über eine Standard-API steuert.

Hier sind drei Erweiterungen, die völlig neue Workflows ermöglichen:

### 1. Sprache-zu-Text mit Whisper

Probieren Sie aus, Audio mithilfe eines Whisper-Modells in Text umzuwandeln und diesen dann in ein LLM zur Zusammenfassung, für Aufgabenlisten oder zum Umschreiben einzuspeisen. Dies bildet die Grundlage für Meeting-Notizen und sprachgesteuerte Assistenten.

### 2. Python-Programmierung in Open WebUI

Nutzen Sie die integrierte Code-Ausführungsfunktion von Open WebUI, um Python-Snippets auszuführen, Ausgaben zu überprüfen und schneller zu iterieren – ohne die Benutzeroberfläche zu verlassen. [Referenz](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. HTML-Rendering in Open WebUI

Rendern Sie HTML-Ausgaben direkt in der Benutzeroberfläche. Dies ist überraschend leistungsstark zum Erstellen schneller Prototypen, formatierter Berichte und interaktiver Snippets. [Referenz](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## Referenzen

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Lemonade Server Dokumentation](https://lemonade-server.ai/docs)
- [Lemonade Server CLI](https://lemonade-server.ai/docs/lemonade-cli/)
- [Lemonade ↔ Open WebUI Integrationsleitfaden](https://lemonade-server.ai/docs/server/apps/open-webui)
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