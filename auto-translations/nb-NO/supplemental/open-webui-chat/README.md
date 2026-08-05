<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversettelse.** Denne siden ble automatisk oversatt fra engelsk og har ikke blitt gjennomgått av et menneske. Den kan inneholde feil, og enkelte instruksjoner, kommandoer, nedlastinger, produkttilgjengelighet eller annet innhold kan variere etter språk eller region. Ved eventuelle uoverensstemmelser eller avvik er den opprinnelige engelske versjonen av playbook-en gjeldende.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Denne oppskriften krever minst **32 GB** systemminne.
<!-- @device:end -->

## Oversikt

[Open WebUI](https://docs.openwebui.com) er et selvhostet, nettleserbasert grensesnitt som gir en kjent chatbot-opplevelse samtidig som det fungerer som et frontend for én eller flere AI-modellservere. I stedet for å være bundet til én leverandør, kan Open WebUI kobles til **enhver backend som eksponerer et OpenAI-kompatibelt API**, slik at du kan bytte modeller og funksjonalitet uten å bytte brukergrensesnitt.

I denne oppskriften bruker vi [**Lemonade**](https://lemonade-server.ai) som backend fordi den eksponerer et **samlet OpenAI-kompatibelt endepunkt** som støtter flere modaliteter:
- **Store språkmodeller (LLM-er)** for tekstgenerering
- **Synsmodeller** for bildeforståelse
- **Stable Diffusion** for bildegenerering
- **Modeller for lydtranskripsjon** for tale-til-tekst

Dette oppsettet lar deg utforske **hele den multimodale arbeidsflyten fra ende til ende**.

---

## Hva du vil lære

Når du er ferdig, vil du kunne:

- Koble Open WebUI til en lokal OpenAI-kompatibel backend (Lemonade)
- Chatte med en lokal LLM fra nettleseren din
- Laste opp et bilde og stille en synsmodell spørsmål om det
- Generere bilder fra tekstmeldinger ved hjelp av Stable Diffusion-modeller (SDXL-Turbo / SDXL)
- Forstå den mentale modellen slik at du kan bruke andre backends (Ollama, vLLM, llama.cpp server, osv.)

---

## Kjernebegreper (mental modell)

### De tre komponentene

| Del | Hva den gjør | Eksempler |
|---|---|---|
| Frontend (UI) | Nettappen du samhandler med | Open WebUI |
| Backend (modellserver) | Er vert for modeller og eksponerer HTTP-endepunkter | Lemonade, Ollama, vLLM, llama.cpp server, OpenAI-kompatible servere |
| Modeller | De faktiske LLM-/syns-/diffusjons-/lydmodellene | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### Hvorfor "OpenAI-kompatibelt API" er viktig

Open WebUI er bygget rundt standard OpenAI-stil endepunkter, som:
  - Chat: `/chat/completions`
  - Modelliste: `/models`
  - Bildegenerering: `/images/generations`
  - Lydtranskripsjon: `/audio/transcriptions`

Lemonade eksponerer disse under `http://localhost:13305/api/v1/...`

Hvis en backend støtter disse endepunktene, kan Open WebUI kommunisere med den med minimalt oppsett. Det er derfor vi kan bytte backend uten å endre arbeidsflyten vår.

#### To tjenester, to porter

Gjennom denne oppskriften vil du jobbe med to separate tjenester:

| Tjeneste | URL | Hva du gjør der |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | Bla gjennom, last ned og administrer modeller |
| **Open WebUI** | `http://localhost:8080` | Chat, last opp bilder, generer bilder — brukergrensesnittet |

Lemonade kjører modellene; Open WebUI er grensesnittet du samhandler med. Bruk Lemonade GUI til å laste ned modellene dine først, og bruk dem deretter fra Open WebUI.

---

## Angi minnekonfigurasjonen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sjekk om det finnes programvareoppdateringer

<!-- @require:software-update -->
<!-- @device:end -->

## Engangsoppsett

Denne oppskriften krever at Lemonade kjører som backend, og på Linux trengs det en containerløsning (Podman) for å kjøre Open WebUI. Sett opp disse før du installerer Open WebUI.

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

## Laste ned modeller i Lemonade

Før du installerer Open WebUI, må du sørge for at modellene du vil bruke er lastet ned og klare i Lemonade.

1. Åpne Lemonade GUI på `http://localhost:13305`.
2. Bla gjennom de tilgjengelige modellene og last ned de du vil bruke (f.eks. en LLM for chat, en synsmodell og/eller en Stable Diffusion-modell for bildegenerering).
3. Bekreft at API-et er tilgjengelig ved å besøke `http://localhost:13305/api/v1/models` i nettleseren din — du bør se de nedlastede modellene dine oppført der.

> Modeller må lastes ned i **Lemonade** (`localhost:13305`) før de kan vises i **Open WebUI** (`localhost:8080`). Hvis en modell ikke dukker opp i Open WebUI senere, kom tilbake hit og sjekk Lemonade først.


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

## Installere Open WebUI

<!-- @os:windows -->
### 1. Installer Python 3.12

Open WebUI krever **Python 3.12** — den installeres ikke på Python 3.13+. Windows Python Launcher (`py`) lar deg installere 3.12 side om side med en eksisterende Python-versjon uten konflikter.

```powershell
winget install Python.Python.3.12
```

Lukk og åpne terminalen på nytt etter installasjonen, og verifiser deretter:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Merk:** Systemet ditt kommer med Python 3.13 forhåndsinstallert. Å installere 3.12 påvirker ikke dette — `python` bruker fortsatt 3.13, og `py -3.12` retter seg mot 3.12 kun når du trenger det.
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

### 2. Opprett et virtuelt miljø og installer Open WebUI

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
Vi skal nå bruke Podman-tjenesten til å containerisere Open WebUI-installasjonen vår.

Last ned følgende til en mappe etter eget valg: [compose.yml](assets/compose.yml)

I den mappen kjører du følgende kommando:

```bash
podman compose up -d
```

Dette henter Open WebUI-bildet og skriver til vedvarende lagring.

Start Open WebUI ved å skrive `localhost:8080` i nettleserens adresselinje.

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

> **Tips**: Open WebUI tilbyr også andre installasjonsalternativer på [GitHub](https://github.com/open-webui/open-webui).
## Starter Open WebUI-server

<!-- @os:windows -->
- Kjør følgende kommando for å starte Open WebUI HTTP-serveren:
```bash
open-webui serve
```
<!-- @os:end -->

- Naviger til `http://localhost:8080` i en nettleser.
- Open WebUI vil be deg om å opprette en lokal administratorkonto. Når du er logget inn, ser du chat-grensesnittet.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> Hold terminalvinduet åpent. Hvis du lukker det, stopper Open WebUI.
<!-- @os:end -->

<!-- @os:linux -->
> Containeren kjører i bakgrunnen. Fra katalogen som inneholder `compose.yml`, administrerer du den med `podman compose down` (stopp) og `podman compose up -d` (start). Kontoene og innstillingene dine lagres i `open_webui_data`-volumet.
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

## Koble Open WebUI til Lemonade

Nå som begge tjenestene kjører — Lemonade på `localhost:13305` og Open WebUI på `localhost:8080` — kobler du dem sammen slik at Open WebUI kan bruke Lemonades modeller.

I Open WebUI:

1. Klikk på **brukerprofil-ikonet** øverst til høyre, og velg deretter **Settings**.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. I innstillingspanelet klikker du på **Admin Settings** nederst til venstre.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. I sidepanelet for Admin Settings klikker du på **Connections** (eller navigerer direkte til `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. Under **OpenAI API** legger du til en ny tilkobling:
   - **Base URL:** `http://localhost:13305/api/v1`
   - **API Key:** `-` (en enkelt bindestrek fungerer for lokal bruk)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. Sørg for at kun `http://localhost:13305/api/v1` er aktivert under **"Manage OpenAI API Connections"**. Deaktiver eventuelle andre tilkoblinger (f.eks. standard OpenAI-tilkoblingen).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. Klikk **Save**.

7. **(Anbefalt)** Deaktiver automatiske genereringsfunksjoner for å holde Open WebUI responsiv med lokale LLM-er. Gå til **Admin Settings → Settings → Interface** og slå av:
   - Title Generation
   - Follow Up Generation
   - Tags Generation

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. Klikk **Save**, og gå deretter tilbake til `http://localhost:8080`.
9. Klikk på modell-nedtrekksmenyen — du bør se modellene du lastet ned fra Lemonade.

---

## Hovedaktiviteter

Nå er alt klart. La oss se på tre interessante ting du kan gjøre.

---

### Aktivitet 1: Chat med en lokal LLM
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Klikk på nedtrekksmenyen øverst til venstre i grensesnittet. Denne viser Lemonade-modellene du har installert. Velg en for å fortsette. (eksempel: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. Skriv inn en melding til LLM-en og klikk på send (eller trykk Enter). LLM-en vil bruke noen sekunder på å laste inn i minnet, og deretter ser du svaret strømme inn.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Klikk på nedtrekksmenyen øverst til venstre i grensesnittet. Denne viser Lemonade-modellene du har installert. Velg en for å fortsette. (eksempel: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Skriv inn en melding til LLM-en og klikk på send (eller trykk Enter). LLM-en vil bruke noen sekunder på å laste inn i minnet, og deretter ser du svaret strømme inn.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. Modellen vil svare i chatten.

4. På dette tidspunktet åpner du `Task Manager` på systemet ditt. Du vil se **høy GPU- eller NPU-utnyttelse**, avhengig av om modellen du valgte er **Hybrid** eller **NPU**. Ved hjelp av oppgavebehandlingen kan du bekrefte at du kjører modellen lokalt.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Klikk på nedtrekksmenyen øverst til venstre i grensesnittet. Denne viser Lemonade-modellene du har installert. Velg en for å fortsette. (eksempel: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Skriv inn en melding til LLM-en og klikk på send (eller trykk Enter). LLM-en vil bruke noen sekunder på å laste inn i minnet, og deretter ser du svaret strømme inn.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. Modellen vil svare i chatten.
<!-- @os:end -->

Dette bekrefter at Open WebUI kan sende forespørsler til Lemonade ved hjelp av det OpenAI-kompatible chat-endepunktet.

---

### Aktivitet 2: Last opp et bilde og still spørsmål (Vision)

Dette krever en modell som støtter bildeinndata (en Vision- eller Multimodal-modell).

1. Klikk på filterikonet, velg "By Category," og velg deretter en modell fra **Vision**-seksjonen (f.eks. `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. Klikk på **`+`**-knappen i meldingsboksen og last opp et bilde
3. Still et spørsmål som krever ekte bildeforståelse: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. Modellen svarer basert på bildeinnholdet, ikke generisk tekst.

Dette viser at Open WebUI kan sende multimodale forespørsler (tekst + bilde) gjennom backend (Lemonade) til en vision-modell.

---

<!-- @os:windows -->
### Aktivitet 3: Generer et bilde fra en tekstprompt (Stable Diffusion)

Stable Diffusion-modeller støtter ikke tekstgenerering, de genererer kun bilder via Images API. 

#### Trinn 1: Konfigurer bildegenerering i Open WebUI

1. I Lemonade-GUI-et (`http://localhost:13305`) søker du etter `SDXL-Turbo` (rask) eller `SDXL-Base-1.0` (høyere kvalitet) og laster den ned.
2. Gå til **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Angi:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` eller `SDXL-Base-1.0`
4. Hvis du ønsker å legge til flere parametere, legger du dem til i tekstfeltet som JSON. For eksempel: `{ "steps": 4, "cfg_scale": 1 }`. Se tilgjengelige parametere på [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Lagre
#### Steg 2: Tillat bildegenerering for modellen
Dette steget sørger for at du aktiverer bildegenerering som en funksjon for modellen din.
1. Gå til **Admin Settings → Models** (http://localhost:8080/admin/settings/models) og velg modellen din
2. Slå på `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Steg 3: Generer et bilde fra chatskjermen

1. Gå tilbake til chatten på `http://localhost:8080`.
2. Velg en **Text Generation LLM** i modellnedtrekksmenyen (eksempel: Qwen, Llama). **Ikke velg en Stable Diffusion-modell** siden dette er en velger for chatmodeller.
3. I meldingsområdet klikker du på **Integrations**, og slår **Image** PÅ.
4. Bruk en ledetekst som: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Et bilde genereres og vises i chatten.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Dette viser at Open WebUI kan koordinere en "todelt" arbeidsflyt:
  - LLM-en hjelper til med å forbedre ledeteksten
  - Bildet genereres via Lemonades Images-endepunkt ved hjelp av Stable Diffusion
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Aktivitet 3: Generer et bilde fra en tekstledetekst (Stable Diffusion)

Stable Diffusion-modeller støtter ikke tekstgenerering, de genererer kun bilder gjennom Images API-et. 

#### Steg 1: Konfigurer bildegenerering i Open WebUI

1. I Lemonade GUI (`http://localhost:13305`) søker du etter `SDXL-Turbo` (rask) eller `SDXL-Base-1.0` (høyere kvalitet) og laster den ned.
2. Gå til **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Sett:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` eller `SDXL-Base-1.0`
4. Hvis du vil legge til flere parametere, legger du dem til i tekstfeltet som JSON. For eksempel: `{ "steps": 4, "cfg_scale": 1 }`. Se tilgjengelige parametere på [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Lagre


#### Steg 2: Tillat bildegenerering for modellen
Dette steget sørger for at du aktiverer bildegenerering som en funksjon for modellen din.
1. Gå til **Admin Settings → Models** (http://localhost:8080/admin/settings/models) og velg modellen din
2. Slå på `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Steg 3: Generer et bilde fra chatskjermen

1. Gå tilbake til chatten på `http://localhost:8080`.
2. Velg en **Text Generation LLM** i modellnedtrekksmenyen (eksempel: Qwen, Llama). **Ikke velg en Stable Diffusion-modell** siden dette er en velger for chatmodeller.
3. I meldingsområdet klikker du på **Integrations**, og slår **Image** PÅ.
4. Bruk en ledetekst som: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Et bilde genereres og vises i chatten.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Dette viser at Open WebUI kan koordinere en "todelt" arbeidsflyt:
  - LLM-en hjelper til med å forbedre ledeteksten
  - Bildet genereres via Lemonades Images-endepunkt ved hjelp av Stable Diffusion
<!-- @device:end -->
<!-- @os:end -->

---

## Feilsøking

### "Ingen modeller vises i Open WebUI"
- Sjekk først Lemonade: åpne `http://localhost:13305/api/v1/models` i en nettleser og bekreft at modellene dine er oppført og lastet ned
- Sjekk deretter Open WebUI-tilkoblingen: gå til **Admin Settings → Connections** på `http://localhost:8080/admin/settings/connections` og kontroller at Base URL er `http://localhost:13305/api/v1`

### Feilmeldingen "This model does not support chat completion"
- Du valgte en bildemodell (SDXL-Turbo / SDXL-Base-1.0) i modellnedtrekksmenyen for chat.
- **Løsning**: velg en LLM for chat, og bruk Image-bryteren + Images-innstillingene for generering.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Feil/tidsavbrudd ved bildegenerering
- Start med `SDXL-Turbo` først (rask, færre steg)
- Når det fungerer, bytt bildemodellen til `SDXL-Base-1.0` for bedre kvalitet

---

## Neste steg

Du har nå en fungerende **«lokal AI-stack»**, et enkelt brukergrensesnitt som styrer flere modelltyper gjennom et standard-API.

Her er tre utvidelser som åpner for helt nye arbeidsflyter:

### 1. Tale-til-tekst med Whisper

Prøv å gjøre lyd om til tekst ved hjelp av en Whisper-modell, og mat den deretter inn i en LLM for oppsummering, oppgavepunkter eller omskriving. Dette er grunnlaget for møtenotater og talestyrte assistenter.

### 2. Python-koding inne i Open WebUI

Bruk Open WebUIs innebygde kodekjøringsopplevelse til å kjøre Python-utdrag, inspisere resultater og iterere raskere - uten å forlate brukergrensesnittet. [Referanse](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. HTML-rendering inne i Open WebUI

Render HTML-utdata direkte i grensesnittet. Dette er overraskende kraftig for å bygge raske prototyper, formaterte rapporter og interaktive utdrag. [Referanse](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## Referanser

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Lemonade Server-dokumentasjon](https://lemonade-server.ai/docs)
- [Lemonade Server CLI](https://lemonade-server.ai/docs/lemonade-cli/)
- [Integrasjonsveiledning for Lemonade ↔ Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Lemonade Server API-spesifikasjon (endepunkter)](https://lemonade-server.ai/docs/server/server_spec)
- [Videogjennomgang (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [Videogjennomgang (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)

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