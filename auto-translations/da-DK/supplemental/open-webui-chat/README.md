<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversættelse.** Denne side er automatisk oversat fra engelsk og er ikke blevet gennemgået af et menneske. Den kan indeholde fejl, og visse instruktioner, kommandoer, downloads, produkttilgængelighed eller andet indhold kan variere afhængigt af sprog eller region. I tilfælde af uoverensstemmelse eller afvigelse er den oprindelige engelske version af playbook'en gældende og har forrang.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Denne playbook kræver mindst **32GB** systemhukommelse.
<!-- @device:end -->

## Oversigt

[Open WebUI](https://docs.openwebui.com) er en selv-hostet, browserbaseret grænseflade, der giver en velkendt chatbot-oplevelse, samtidig med at den fungerer som frontend for én eller flere AI-modelservere. I stedet for at være bundet til én udbyder kan Open WebUI oprette forbindelse til **enhver backend, der eksponerer en OpenAI-kompatibel API**, så du kan skifte mellem modeller og funktioner uden at skifte brugergrænseflade.

I denne playbook bruger vi [**Lemonade**](https://lemonade-server.ai) som backend, fordi den eksponerer et **samlet OpenAI-kompatibelt endpoint**, der understøtter flere modaliteter:
- **Large Language Models (LLM'er)** til tekstgenerering
- **Vision-modeller** til billedforståelse
- **Stable Diffusion** til billedgenerering
- **Lydtranskriptionsmodeller** til tale-til-tekst

Denne opsætning gør det muligt at udforske det **komplette multimodale workflow fra ende til anden**.

---

## Hvad du vil lære

Når du er færdig, vil du kunne:

- Forbinde Open WebUI til en lokal OpenAI-kompatibel backend (Lemonade)
- Chatte med en lokal LLM fra din browser
- Uploade et billede og stille en vision-model spørgsmål om det
- Generere billeder fra tekstprompts ved hjælp af Stable Diffusion-modeller (SDXL-Turbo / SDXL)
- Forstå den mentale model, så du kan bruge andre backends (Ollama, vLLM, llama.cpp server osv.)

---

## Kernebegreber (mental model)

### De tre komponenter

| Del | Hvad den gør | Eksempler |
|---|---|---|
| Frontend (brugergrænseflade) | Webapplikationen, du interagerer med | Open WebUI |
| Backend (modelserver) | Hoster modeller og eksponerer HTTP-endpoints | Lemonade, Ollama, vLLM, llama.cpp server, OpenAI-kompatible servere |
| Modeller | De faktiske LLM-/Vision-/Diffusion-/Lydmodeller | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### Hvorfor "OpenAI-kompatibel API" har betydning

Open WebUI er bygget omkring standard OpenAI-lignende endpoints, såsom:
  - Chat: `/chat/completions`
  - Modelliste: `/models`
  - Billedgenerering: `/images/generations`
  - Lydtranskription: `/audio/transcriptions`

Lemonade eksponerer disse under `http://localhost:13305/api/v1/...`

Hvis en backend understøtter disse endpoints, kan Open WebUI kommunikere med den med minimal opsætning. Det er derfor, vi kan skifte backends uden at ændre vores workflow.

#### To tjenester, to porte

Gennem denne playbook vil du arbejde med to separate tjenester:

| Tjeneste | URL | Hvad du gør der |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | Gennemse, download og administrer modeller |
| **Open WebUI** | `http://localhost:8080` | Chat, upload billeder, generer billeder — den brugervendte grænseflade |

Lemonade kører modellerne; Open WebUI er den grænseflade, du interagerer med. Brug Lemonade GUI'en til først at downloade dine modeller, og brug dem derefter fra Open WebUI.

---

## Indstilling af hukommelseskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tjek for softwareopdateringer

<!-- @require:software-update -->
<!-- @device:end -->

## Engangsopsætning

Denne playbook kræver, at Lemonade kører som backend, og på Linux kræver den en containermotor (Podman) for at køre Open WebUI. Sæt disse op, før du installerer Open WebUI.

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

## Download af modeller i Lemonade

Før du installerer Open WebUI, skal du sikre dig, at de modeller, du vil bruge, er downloadet og klar i Lemonade.

1. Åbn Lemonade GUI'en på `http://localhost:13305`.
2. Gennemse de tilgængelige modeller, og download dem, du vil bruge (f.eks. en LLM til chat, en vision-model og/eller en Stable Diffusion-model til billedgenerering).
3. Bekræft, at API'et er tilgængeligt ved at besøge `http://localhost:13305/api/v1/models` i din browser — du bør se dine downloadede modeller på listen.

> Modeller skal downloades i **Lemonade** (`localhost:13305`), før de kan vises i **Open WebUI** (`localhost:8080`). Hvis en model ikke vises i Open WebUI senere, så kom tilbage hertil og tjek Lemonade først.


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

## Installation af Open WebUI

<!-- @os:windows -->
### 1. Installer Python 3.12

Open WebUI kræver **Python 3.12** — det installeres ikke på Python 3.13+. Windows Python Launcher (`py`) lader dig installere 3.12 side om side med enhver eksisterende Python-version uden konflikter.

```powershell
winget install Python.Python.3.12
```

Luk og genåbn din terminal efter installationen, og bekræft derefter:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Bemærk:** Dit system leveres med Python 3.13 forudinstalleret. Installation af 3.12 påvirker ikke denne — `python` fortsætter med at bruge 3.13, og `py -3.12` målretter kun mod 3.12, når du har brug for det.
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

### 2. Opret et virtuelt miljø og installer Open WebUI

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
Vi vil nu bruge Podman-tjenesten til at containerisere vores Open WebUI-installation.

Download venligst følgende til en mappe efter eget valg: [compose.yml](assets/compose.yml)

I den mappe skal du køre følgende kommando:

```bash
podman compose up -d
```

Dette henter Open WebUI-billedet og skriver til persistent lagring.

Start Open WebUI ved at skrive `localhost:8080` i din browsers adresselinje.

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

> **Tip**: Open WebUI tilbyder også andre installationsmuligheder på deres [GitHub](https://github.com/open-webui/open-webui).
## Starting Open WebUI Server

<!-- @os:windows -->
- Kør følgende kommando for at starte Open WebUI HTTP-serveren:
```bash
open-webui serve
```
<!-- @os:end -->

- Åbn `http://localhost:8080` i en browser.
- Open WebUI vil bede dig om at oprette en lokal administratorkonto. Når du er logget ind, ser du chatgrænsefladen.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> Lad terminalvinduet være åbent. Hvis du lukker det, stopper Open WebUI.
<!-- @os:end -->

<!-- @os:linux -->
> Containeren kører i baggrunden. Fra mappen, der indeholder `compose.yml`, kan du administrere den med `podman compose down` (stop) og `podman compose up -d` (start). Dine konti og indstillinger bevares i volumenet `open_webui_data`.
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

## Forbindelse mellem Open WebUI og Lemonade

Nu hvor begge tjenester kører — Lemonade på `localhost:13305` og Open WebUI på `localhost:8080` — skal de forbindes, så Open WebUI kan bruge Lemonades modeller.

I Open WebUI:

1. Klik på **brugerprofilikonet** i øverste højre hjørne, og vælg derefter **Settings**.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. I panelet Settings skal du klikke på **Admin Settings** nederst til venstre.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. I sidebjælken for Admin Settings skal du klikke på **Connections** (eller gå direkte til `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. Under **OpenAI API** skal du tilføje en ny forbindelse:
   - **Base URL:** `http://localhost:13305/api/v1`
   - **API Key:** `-` (en enkelt bindestreg fungerer lokalt)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. Sørg for, at kun `http://localhost:13305/api/v1` er aktiveret under **"Manage OpenAI API Connections"**. Deaktiver alle andre forbindelser (f.eks. den standardmæssige OpenAI-forbindelse).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. Klik på **Save**.

7. **(Anbefalet)** Deaktiver funktioner til automatisk generering for at holde Open WebUI responsivt med lokale LLM'er. Gå til **Admin Settings → Settings → Interface**, og slå følgende fra:
   - Title Generation
   - Follow Up Generation
   - Tags Generation

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. Klik på **Save**, og vend derefter tilbage til `http://localhost:8080`.
9. Klik på modeldropdown-menuen — du bør nu se de modeller, du har downloadet fra Lemonade.

---

## Vigtigste aktiviteter

Nu er alt sat op. Lad os se på tre interessante ting, du kan gøre.

---

### Aktivitet 1: Chat med en lokal LLM
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Klik på dropdown-menuen øverst til venstre i grænsefladen. Denne viser de Lemonade-modeller, du har installeret. Vælg en for at fortsætte (eksempel: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. Skriv en besked til LLM'en, og klik på send (eller tryk på Enter). LLM'en vil tage nogle sekunder om at blive indlæst i hukommelsen, hvorefter du vil se svaret blive streamet ind.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Klik på dropdown-menuen øverst til venstre i grænsefladen. Denne viser de Lemonade-modeller, du har installeret. Vælg en for at fortsætte (eksempel: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Skriv en besked til LLM'en, og klik på send (eller tryk på Enter). LLM'en vil tage nogle sekunder om at blive indlæst i hukommelsen, hvorefter du vil se svaret blive streamet ind.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. Modellen svarer i chatten.

4. Åbn `Task Manager` på dit system på dette tidspunkt. Du vil se **høj GPU- eller NPU-udnyttelse** afhængigt af, om den valgte model er henholdsvis **Hybrid** eller **NPU**. Ved hjælp af jobliste (Task Manager) kan du bekræfte, at du kører modellen lokalt.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Klik på dropdown-menuen øverst til venstre i grænsefladen. Denne viser de Lemonade-modeller, du har installeret. Vælg en for at fortsætte (eksempel: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Skriv en besked til LLM'en, og klik på send (eller tryk på Enter). LLM'en vil tage nogle sekunder om at blive indlæst i hukommelsen, hvorefter du vil se svaret blive streamet ind.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. Modellen svarer i chatten.
<!-- @os:end -->

Dette bekræfter, at Open WebUI kan sende anmodninger til Lemonade via det OpenAI-kompatible chat-endpoint.

---

### Aktivitet 2: Upload et billede og stil spørgsmål (Vision)

Dette kræver en model, der understøtter billedinput (en Vision- eller Multimodal-model).

1. Klik på filterikonet, vælg "By Category," og vælg derefter en model fra sektionen **Vision** (f.eks. `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. Klik på **`+`**-knappen i beskedfeltet, og upload et billede
3. Stil et spørgsmål, der kræver reel billedforståelse: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. Modellen svarer baseret på billedindholdet, ikke generisk tekst.

Dette demonstrerer, at Open WebUI kan sende multimodale anmodninger (tekst + billede) gennem backend'en (Lemonade) til en vision-model.

---

<!-- @os:windows -->
### Aktivitet 3: Generer et billede ud fra en tekstprompt (Stable Diffusion)

Stable Diffusion-modeller understøtter ikke tekstgenerering, de genererer kun billeder via Images API. 

#### Trin 1: Konfigurer billedgenerering i Open WebUI

1. Søg efter `SDXL-Turbo` (hurtig) eller `SDXL-Base-1.0` (højere kvalitet) i Lemonade GUI'en (`http://localhost:13305`), og download den.
2. Gå til **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Indstil:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` eller `SDXL-Base-1.0`
4. Hvis du vil tilføje flere parametre, kan du tilføje dem i tekstfeltet som JSON. For eksempel: `{ "steps": 4, "cfg_scale": 1 }`. Se de tilgængelige parametre på [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Gem
#### Trin 2: Tillad billedgenerering for modellen
Dette trin sikrer, at du aktiverer billedgenerering som en funktion for din model.
1. Gå til **Admin Settings → Models** (http://localhost:8080/admin/settings/models) og vælg din model
2. Slå `Image Generation` til

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Trin 3: Generér et billede fra chatskærmen

1. Gå tilbage til chatten på `http://localhost:8080`.
2. Vælg en **Text Generation LLM** i model-dropdown'en (eksempel: Qwen, Llama). **Vælg ikke en Stable Diffusion-model**, da dette er en chatmodel-vælger.
3. I beskedområdet skal du klikke på **Integrations** og slå **Image** TIL.
4. Brug en prompt som: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Der genereres et billede, som vises i chatten.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Dette fastslår, at Open WebUI kan koordinere en "todelt" arbejdsgang:
  - LLM'en hjælper med at forfine prompten
  - Billedet genereres via Lemonades Images-endpoint ved brug af Stable Diffusion
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Aktivitet 3: Generér et billede ud fra en tekstprompt (Stable Diffusion)

Stable Diffusion-modeller understøtter ikke tekstgenerering, de genererer kun billeder via Images API'en.

#### Trin 1: Konfigurér billedgenerering i Open WebUI

1. I Lemonade GUI'et (`http://localhost:13305`) skal du søge efter `SDXL-Turbo` (hurtig) eller `SDXL-Base-1.0` (højere kvalitet) og downloade den.
2. Gå til **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Indstil:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` eller `SDXL-Base-1.0`
4. Hvis du vil tilføje flere parametre, skal du tilføje dem i tekstfeltet som JSON. For eksempel: `{ "steps": 4, "cfg_scale": 1 }`. Se tilgængelige parametre under [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Gem


#### Trin 2: Tillad billedgenerering for modellen
Dette trin sikrer, at du aktiverer billedgenerering som en funktion for din model.
1. Gå til **Admin Settings → Models** (http://localhost:8080/admin/settings/models) og vælg din model
2. Slå `Image Generation` til

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Trin 3: Generér et billede fra chatskærmen

1. Gå tilbage til chatten på `http://localhost:8080`.
2. Vælg en **Text Generation LLM** i model-dropdown'en (eksempel: Qwen, Llama). **Vælg ikke en Stable Diffusion-model**, da dette er en chatmodel-vælger.
3. I beskedområdet skal du klikke på **Integrations** og slå **Image** TIL.
4. Brug en prompt som: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Der genereres et billede, som vises i chatten.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Dette fastslår, at Open WebUI kan koordinere en "todelt" arbejdsgang:
  - LLM'en hjælper med at forfine prompten
  - Billedet genereres via Lemonades Images-endpoint ved brug af Stable Diffusion
<!-- @device:end -->
<!-- @os:end -->

---

## Fejlfinding

### "Ingen modeller vises i Open WebUI"
- Tjek først Lemonade: åbn `http://localhost:13305/api/v1/models` i en browser, og bekræft, at dine modeller er angivet og downloadet
- Tjek derefter Open WebUI-forbindelsen: gå til **Admin Settings → Connections** på `http://localhost:8080/admin/settings/connections`, og bekræft, at Base URL er `http://localhost:13305/api/v1`

### Fejlmeddelelsen "This model does not support chat completion"
- Du har valgt en billedmodel (SDXL-Turbo / SDXL-Base-1.0) i chatmodel-dropdown'en.
- **Løsning**: vælg en LLM til chat, og brug Image-kontakten + Images-indstillingerne til generering.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Fejl/timeouts ved billedgenerering
- Start først med `SDXL-Turbo` (hurtig, færre trin)
- Når det fungerer, skal du skifte billedmodellen til `SDXL-Base-1.0` for bedre kvalitet

---

## Næste trin

Du har nu en fungerende **"lokal AI-stak"**, en enkelt brugerflade der styrer flere modeltyper gennem en standard-API.

Her er tre udvidelser, der låser op for helt nye arbejdsgange:

### 1. Tale-til-tekst med Whisper

Prøv at omdanne lyd til tekst ved hjælp af en Whisper-model, og send det derefter til en LLM til opsummering, actionpunkter eller omskrivning. Dette er grundlaget for mødenotater og stemmestyrede assistenter.

### 2. Python-kodning i Open WebUI

Brug Open WebUI's indbyggede kodeeksekveringsoplevelse til at køre Python-snippets, inspicere output og iterere hurtigere—uden at forlade brugerfladen. [Reference](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. HTML-rendering i Open WebUI

Render HTML-output direkte i grænsefladen. Dette er overraskende kraftfuldt til at bygge hurtige prototyper, formaterede rapporter og interaktive snippets. [Reference](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## Referencer

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Lemonade Server-dokumentation](https://lemonade-server.ai/docs)
- [Lemonade Server CLI](https://lemonade-server.ai/docs/lemonade-cli/)
- [Lemonade ↔ Open WebUI-integrationsguide](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Lemonade Server API-specifikation (endpoints)](https://lemonade-server.ai/docs/server/server_spec)
- [Videogennemgang (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [Videogennemgang (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)

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