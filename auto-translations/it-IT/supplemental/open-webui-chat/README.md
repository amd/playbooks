<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Questo playbook utilizza tag speciali che GitHub non è in grado di visualizzare. Visita [amd.com/playbooks](https://amd.com/playbooks) per visualizzare correttamente questo contenuto.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Questo playbook richiede un minimo di **32GB** di memoria di sistema.
<!-- @device:end -->

## Panoramica

[Open WebUI](https://docs.openwebui.com) è un'interfaccia self-hosted basata su browser che offre una familiare esperienza di chatbot, fungendo da frontend per uno o più server di modelli AI. Invece di essere vincolata a un singolo provider, Open WebUI può connettersi a **qualsiasi backend che esponga un'API compatibile con OpenAI**, consentendo di cambiare modelli e funzionalità senza dover cambiare interfaccia.

In questo playbook utilizziamo [**Lemonade**](https://lemonade-server.ai) come backend perché espone un **endpoint unificato compatibile con OpenAI** che supporta più modalità:
- **Large Language Models (LLM)** per la generazione di testo
- **Modelli vision** per la comprensione delle immagini
- **Stable Diffusion** per la generazione di immagini
- **Modelli di trascrizione audio** per il riconoscimento vocale

Questa configurazione ti permette di esplorare il **flusso di lavoro multimodale completo end-to-end**.

---

## Cosa Imparerai

Al termine, sarai in grado di:

- Connettere Open WebUI a un backend locale compatibile con OpenAI (Lemonade)
- Chattare con un LLM locale dal tuo browser
- Caricare un'immagine e porre domande a un modello vision
- Generare immagini da prompt testuali utilizzando modelli Stable Diffusion (SDXL-Turbo / SDXL)
- Comprendere il modello concettuale per poter utilizzare altri backend (Ollama, vLLM, llama.cpp server, ecc.)

---

## Concetti Fondamentali (Modello Concettuale)

### I Tre Componenti

| Componente | Funzione | Esempi |
|---|---|---|
| Frontend (UI) | L'applicazione web con cui interagisci | Open WebUI |
| Backend (Server Modelli) | Ospita i modelli ed espone endpoint HTTP | Lemonade, Ollama, vLLM, llama.cpp server, server compatibili con OpenAI |
| Modelli | Gli effettivi modelli LLM / Vision / Diffusion / Audio | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### Perché è importante l'"API compatibile con OpenAI"

Open WebUI è costruita attorno agli endpoint standard in stile OpenAI, come:
  - Chat: `/chat/completions`
  - Lista modelli: `/models`
  - Generazione immagini: `/images/generations`
  - Trascrizione audio: `/audio/transcriptions`

Lemonade li espone sotto `http://localhost:13305/api/v1/...`

Se un backend supporta questi endpoint, Open WebUI può comunicare con esso con una configurazione minima. Ecco perché possiamo cambiare backend senza modificare il nostro flusso di lavoro.

#### Due servizi, due porte

In questo playbook lavorerai con due servizi separati:

| Servizio | URL | Cosa fare lì |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | Sfogliare, scaricare e gestire i modelli |
| **Open WebUI** | `http://localhost:8080` | Chattare, caricare immagini, generare immagini — l'interfaccia utente |

Lemonade esegue i modelli; Open WebUI è l'interfaccia con cui interagisci. Usa la GUI di Lemonade per scaricare prima i tuoi modelli, poi utilizzali da Open WebUI.

---

## Impostazione della Configurazione della Memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verifica degli Aggiornamenti Software

<!-- @require:software-update -->
<!-- @device:end -->

## Configurazione Iniziale

Questo playbook richiede Lemonade in esecuzione come backend e, su Linux, un motore di container (Podman) per eseguire Open WebUI. Configura questi elementi prima di installare Open WebUI.

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

## Download dei Modelli in Lemonade

Prima di installare Open WebUI, assicurati che i modelli che desideri utilizzare siano scaricati e pronti in Lemonade.

1. Apri la GUI di Lemonade all'indirizzo `http://localhost:13305`.
2. Sfoglia i modelli disponibili e scarica quelli che vuoi utilizzare (ad es., un LLM per la chat, un modello vision e/o un modello Stable Diffusion per la generazione di immagini).
3. Verifica che l'API sia raggiungibile visitando `http://localhost:13305/api/v1/models` nel tuo browser — dovresti vedere elencati i modelli scaricati.

> I modelli devono essere scaricati in **Lemonade** (`localhost:13305`) prima di poter apparire in **Open WebUI** (`localhost:8080`). Se un modello non compare in Open WebUI in seguito, torna qui e controlla prima Lemonade.


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

## Installazione di Open WebUI

<!-- @os:windows -->
### 1. Installa Python 3.12

Open WebUI richiede **Python 3.12** — non si installa su Python 3.13+. Il Windows Python Launcher (`py`) ti consente di installare la versione 3.12 affiancata a qualsiasi versione Python esistente senza conflitti.

```powershell
winget install Python.Python.3.12
```

Chiudi e riapri il terminale dopo l'installazione, quindi verifica:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Nota:** Il tuo sistema viene fornito con Python 3.13 preinstallato. L'installazione della versione 3.12 non lo influenza — `python` continua a utilizzare la 3.13, e `py -3.12` punta alla 3.12 solo quando necessario.
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

### 2. Crea un ambiente virtuale e installa Open WebUI

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
Utilizzeremo ora il servizio Podman per containerizzare la nostra installazione di Open WebUI.

Scarica il seguente file nella directory di tua scelta: [compose.yml](assets/compose.yml)

In quella directory, esegui il seguente comando:

```bash
podman compose up -d
```

Questo scarica l'immagine di Open WebUI e scrive nella memoria persistente.

Avvia Open WebUI digitando `localhost:8080` nella barra degli indirizzi del browser.

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

> **Suggerimento**: Open WebUI offre anche altre opzioni di installazione sul loro [GitHub](https://github.com/open-webui/open-webui).

## Avvio del Server Open WebUI

<!-- @os:windows -->
- Esegui il seguente comando per avviare il server HTTP di Open WebUI:
```bash
open-webui serve
```
<!-- @os:end -->

- In un browser, naviga su `http://localhost:8080`.
- Open WebUI ti chiederà di creare un account amministratore locale. Una volta effettuato l'accesso, vedrai l'interfaccia di chat.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> Tieni aperta la finestra del terminale. Chiuderla interrompe Open WebUI.
<!-- @os:end -->

<!-- @os:linux -->
> Il container viene eseguito in background. Dalla directory contenente `compose.yml`, gestiscilo con `podman compose down` (arresta) e `podman compose up -d` (avvia). I tuoi account e le impostazioni persistono nel volume `open_webui_data`.
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

## Connessione di Open WebUI a Lemonade

Ora che entrambi i servizi sono in esecuzione — Lemonade su `localhost:13305` e Open WebUI su `localhost:8080` — collegali in modo che Open WebUI possa utilizzare i modelli di Lemonade.

In Open WebUI:

1. Clicca sull'**icona del profilo utente** nell'angolo in alto a destra, quindi seleziona **Impostazioni**.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. Nel pannello Impostazioni, clicca su **Impostazioni Admin** in basso a sinistra.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. Nella barra laterale delle Impostazioni Admin, clicca su **Connessioni** (oppure naviga direttamente su `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. Sotto **OpenAI API**, aggiungi una nuova connessione:
   - **URL Base:** `http://localhost:13305/api/v1`
   - **Chiave API:** `-` (un singolo trattino funziona per uso locale)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. Assicurati che sotto **"Gestisci Connessioni API OpenAI"**, sia abilitato solo `http://localhost:13305/api/v1`. Disabilita qualsiasi altra connessione (ad es., quella predefinita di OpenAI).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. Clicca su **Salva**.

7. **(Consigliato)** Disabilita le funzionalità di generazione automatica per mantenere Open WebUI reattivo con i LLM locali. Vai su **Impostazioni Admin → Impostazioni → Interfaccia** e disattiva:
   - Generazione Titolo
   - Generazione Follow Up
   - Generazione Tag

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. Clicca su **Salva**, poi torna su `http://localhost:8080`.
9. Clicca sul menu a tendina dei modelli — dovresti vedere i modelli che hai scaricato da Lemonade.

---

## Attività Principali

Ora sei pronto. Vediamo tre cose interessanti da fare.

---

### Attività 1: Chatta con un LLM Locale
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Clicca sul menu a tendina in alto a sinistra dell'interfaccia. Verranno visualizzati i modelli Lemonade installati. Selezionane uno per procedere. (esempio: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. Inserisci un messaggio per il LLM e clicca su invia (o premi Invio). Il LLM impiegherà qualche secondo per caricarsi in memoria, poi vedrai la risposta apparire progressivamente.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Clicca sul menu a tendina in alto a sinistra dell'interfaccia. Verranno visualizzati i modelli Lemonade installati. Selezionane uno per procedere. (esempio: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Inserisci un messaggio per il LLM e clicca su invia (o premi Invio). Il LLM impiegherà qualche secondo per caricarsi in memoria, poi vedrai la risposta apparire progressivamente.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. Il modello risponderà nella chat.

4. A questo punto, apri il `Task Manager` sul tuo sistema. Vedrai **un elevato utilizzo della GPU o della NPU** a seconda che il modello selezionato sia rispettivamente **Hybrid** o **NPU**. Utilizzando il task manager, puoi confermare che stai eseguendo il modello localmente.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Clicca sul menu a tendina in alto a sinistra dell'interfaccia. Verranno visualizzati i modelli Lemonade installati. Selezionane uno per procedere. (esempio: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Inserisci un messaggio per il LLM e clicca su invia (o premi Invio). Il LLM impiegherà qualche secondo per caricarsi in memoria, poi vedrai la risposta apparire progressivamente.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. Il modello risponderà nella chat.
<!-- @os:end -->

Questo conferma che Open WebUI è in grado di inviare richieste a Lemonade utilizzando l'endpoint di chat compatibile con OpenAI.

---

### Attività 2: Carica un'Immagine e Fai Domande (Vision)

Questa attività richiede un modello che supporti l'input di immagini (un modello Vision o Multimodale).

1. Clicca sull'icona del filtro, seleziona "Per Categoria", quindi scegli un modello dalla sezione **Vision** (ad es., `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. Clicca sul pulsante **`+`** nella casella del messaggio e carica un'immagine
3. Fai una domanda che richieda una vera comprensione dell'immagine: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. Il modello risponde in base al contenuto dell'immagine, non a testo generico.

Questo dimostra che Open WebUI è in grado di inviare richieste multimodali (testo + immagine) attraverso il backend (Lemonade) a un modello vision.

---

<!-- @os:windows -->
### Attività 3: Genera un'Immagine da un Prompt Testuale (Stable Diffusion)

I modelli Stable Diffusion non supportano la generazione di testo, generano immagini esclusivamente tramite l'API Images.

#### Passaggio 1: Configura la Generazione di Immagini in Open WebUI

1. Nella GUI di Lemonade (`http://localhost:13305`), cerca `SDXL-Turbo` (veloce) o `SDXL-Base-1.0` (qualità superiore) e scaricalo.
2. Vai su **Impostazioni Admin → Immagini** (http://localhost:8080/admin/settings/images)
3. Imposta:
   - **Generazione Immagini:** ON
   - **Motore di Generazione Immagini:** Default (OpenAI)
   - **URL Base API OpenAI:** `http://localhost:13305/api/v1`
   - **Chiave API OpenAI:** `-`
   - **Modello:** `SDXL-Turbo` o `SDXL-Base-1.0`
4. Se vuoi aggiungere ulteriori parametri, inseriscili nel campo di testo come JSON. Ad esempio: `{ "steps": 4, "cfg_scale": 1 }`. Consulta i parametri disponibili su [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Salva


#### Passaggio 2: Abilita la Generazione di Immagini per il modello
Questo passaggio garantisce che tu abiliti la Generazione di Immagini come funzionalità per il tuo modello.
1. Vai su **Impostazioni Admin → Modelli** (http://localhost:8080/admin/settings/models) e scegli il tuo modello
2. Attiva `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Passaggio 3: Genera un'immagine dalla schermata di chat

1. Torna alla chat su `http://localhost:8080`.
2. Seleziona un **LLM per la Generazione di Testo** nel menu a tendina dei modelli (esempio: Qwen, Llama). **Non selezionare un modello Stable Diffusion** poiché questo è un selettore di modelli di chat.
3. Nell'area del messaggio, clicca su **Integrazioni** e attiva **Immagine** su ON.
4. Usa un prompt come: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Un'immagine viene generata e appare nella chat.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Questo dimostra che Open WebUI è in grado di coordinare un flusso di lavoro "in due fasi":
  - Il LLM aiuta a perfezionare il prompt
  - L'immagine viene generata tramite l'endpoint Images di Lemonade utilizzando Stable Diffusion
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Attività 3: Genera un'Immagine da un Prompt Testuale (Stable Diffusion)

I modelli Stable Diffusion non supportano la generazione di testo, generano immagini esclusivamente tramite l'API Images.

#### Passaggio 1: Configura la Generazione di Immagini in Open WebUI

1. Nella GUI di Lemonade (`http://localhost:13305`), cerca `SDXL-Turbo` (veloce) o `SDXL-Base-1.0` (qualità superiore) e scaricalo.
2. Vai su **Impostazioni Admin → Immagini** (http://localhost:8080/admin/settings/images)
3. Imposta:
   - **Generazione Immagini:** ON
   - **Motore di Generazione Immagini:** Default (OpenAI)
   - **URL Base API OpenAI:** `http://localhost:13305/api/v1`
   - **Chiave API OpenAI:** `-`
   - **Modello:** `SDXL-Turbo` o `SDXL-Base-1.0`
4. Se vuoi aggiungere ulteriori parametri, inseriscili nel campo di testo come JSON. Ad esempio: `{ "steps": 4, "cfg_scale": 1 }`. Consulta i parametri disponibili su [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Salva


#### Passaggio 2: Abilita la Generazione di Immagini per il modello
Questo passaggio garantisce che tu abiliti la Generazione di Immagini come funzionalità per il tuo modello.
1. Vai su **Impostazioni Admin → Modelli** (http://localhost:8080/admin/settings/models) e scegli il tuo modello
2. Attiva `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Passaggio 3: Genera un'immagine dalla schermata di chat

1. Torna alla chat su `http://localhost:8080`.
2. Seleziona un **LLM per la Generazione di Testo** nel menu a tendina dei modelli (esempio: Qwen, Llama). **Non selezionare un modello Stable Diffusion** poiché questo è un selettore di modelli di chat.
3. Nell'area del messaggio, clicca su **Integrazioni** e attiva **Immagine** su ON.
4. Usa un prompt come: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Un'immagine viene generata e appare nella chat.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Questo dimostra che Open WebUI è in grado di coordinare un flusso di lavoro "in due fasi":
  - Il LLM aiuta a perfezionare il prompt
  - L'immagine viene generata tramite l'endpoint Images di Lemonade utilizzando Stable Diffusion
<!-- @device:end -->
<!-- @os:end -->

---

## Risoluzione dei Problemi

### "Nessun modello compare in Open WebUI"
- Prima, controlla Lemonade: apri `http://localhost:13305/api/v1/models` in un browser e verifica che i tuoi modelli siano elencati e scaricati
- Poi, controlla la connessione di Open WebUI: vai su **Impostazioni Admin → Connessioni** su `http://localhost:8080/admin/settings/connections` e verifica che l'URL Base sia `http://localhost:13305/api/v1`

### Messaggio di errore "This model does not support chat completion"
- Hai selezionato un modello di immagini (SDXL-Turbo / SDXL-Base-1.0) nel menu a tendina dei modelli di chat.
- **Soluzione**: seleziona un LLM per la chat e usa il toggle Immagine + le impostazioni Immagini per la generazione.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Errori/timeout nella generazione di immagini
- Inizia prima con `SDXL-Turbo` (veloce, meno passaggi)
- Una volta funzionante, passa il modello di immagini a `SDXL-Base-1.0` per la qualità

---

## Passi Successivi

Ora disponi di uno **'stack AI locale'** funzionante, una singola interfaccia che controlla più tipi di modelli attraverso un'API standard.

Ecco tre espansioni che aprono flussi di lavoro completamente nuovi:

### 1. Riconoscimento Vocale con Whisper

Prova a convertire l'audio in testo utilizzando un modello Whisper, poi passalo a un LLM per la sintesi, l'estrazione di azioni o la riscrittura. Questa è la base per le note delle riunioni e gli assistenti vocali.

### 2. Programmazione Python all'interno di Open WebUI

Usa l'esperienza di esecuzione del codice integrata in Open WebUI per eseguire frammenti Python, ispezionare gli output e iterare più velocemente — senza uscire dall'interfaccia. [Riferimento](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. Rendering HTML all'interno di Open WebUI

Visualizza gli output HTML direttamente nell'interfaccia. Questo è sorprendentemente potente per creare prototipi rapidi, report formattati e frammenti interattivi. [Riferimento](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## Riferimenti

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Documentazione Lemonade Server](https://lemonade-server.ai/docs)
- [CLI Lemonade Server](https://lemonade-server.ai/docs/lemonade-cli/)
- [Guida all'integrazione Lemonade ↔ Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Specifiche API Lemonade Server (endpoint)](https://lemonade-server.ai/docs/server/server_spec)
- [Video guida (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [Video guida (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)