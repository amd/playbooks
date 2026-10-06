<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Machinevertaling.** Deze pagina is automatisch vertaald vanuit het Engels en is niet door een mens gecontroleerd. Deze pagina kan fouten bevatten en bepaalde instructies, opdrachten, downloads, productbeschikbaarheid of andere inhoud kan per taal of regio verschillen. In geval van tegenstrijdigheid of discrepantie is de oorspronkelijke Engelse versie van de playbook doorslaggevend en prevaleert deze.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Voor dit playbook is minimaal **32GB** systeemgeheugen vereist.
<!-- @device:end -->

## Overzicht

[Open WebUI](https://docs.openwebui.com) is een zelf-gehoste, browsergebaseerde interface die een vertrouwde chatbotervaring biedt terwijl het fungeert als frontend voor een of meerdere AI-modelservers. In plaats van gebonden te zijn aan één provider, kan Open WebUI verbinding maken met **elke backend die een OpenAI-compatibele API blootstelt**, zodat je modellen en mogelijkheden kunt verwisselen zonder van UI te hoeven wisselen.

In dit playbook gebruiken we [**Lemonade**](https://lemonade-server.ai) als backend omdat het een **uniform OpenAI-compatibel endpoint** blootstelt dat meerdere modaliteiten ondersteunt:
- **Large Language Models (LLM's)** voor tekstgeneratie
- **Vision-modellen** voor beeldbegrip
- **Stable Diffusion** voor beeldgeneratie
- **Audiotranscriptiemodellen** voor spraak-naar-tekst

Deze opzet stelt je in staat om de **complete multimodale workflow van begin tot eind** te verkennen.

---

## Wat je gaat leren

Aan het einde ben je in staat om:

- Open WebUI te verbinden met een lokale OpenAI-compatibele backend (Lemonade)
- Vanuit je browser te chatten met een lokale LLM
- Een afbeelding te uploaden en een vision-model er vragen over te stellen
- Afbeeldingen te genereren vanuit tekstprompts met Stable Diffusion-modellen (SDXL-Turbo / SDXL)
- Het mentale model te begrijpen zodat je ook andere backends kunt gebruiken (Ollama, vLLM, llama.cpp server, enz.)

---

## Kernconcepten (mentaal model)

### De drie onderdelen

| Onderdeel | Wat het doet | Voorbeelden |
|---|---|---|
| Frontend (UI) | De webapp waarmee je werkt | Open WebUI |
| Backend (Modelserver) | Host modellen en stelt HTTP-endpoints beschikbaar | Lemonade, Ollama, vLLM, llama.cpp server, OpenAI-compatibele servers |
| Modellen | De daadwerkelijke LLM-/Vision-/Diffusion-/Audio-modellen | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### Waarom "OpenAI-compatibele API" belangrijk is

Open WebUI is opgebouwd rond standaard OpenAI-stijl endpoints, zoals:
  - Chat: `/chat/completions`
  - Modellenlijst: `/models`
  - Beeldgeneratie: `/images/generations`
  - Audiotranscriptie: `/audio/transcriptions`

Lemonade stelt deze beschikbaar onder `http://localhost:13305/api/v1/...`

Als een backend deze endpoints ondersteunt, kan Open WebUI er met minimale configuratie mee communiceren. Daarom kunnen we van backend wisselen zonder onze workflow te wijzigen.

#### Twee services, twee poorten

Tijdens dit playbook werk je met twee afzonderlijke services:

| Service | URL | Wat je daar doet |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | Modellen bladeren, downloaden en beheren |
| **Open WebUI** | `http://localhost:8080` | Chatten, afbeeldingen uploaden, afbeeldingen genereren — de gebruikersinterface |

Lemonade draait de modellen; Open WebUI is de interface waarmee je werkt. Gebruik eerst de Lemonade GUI om je modellen te downloaden en gebruik ze daarna vanuit Open WebUI.

---

<!-- @device:halo_box,halo,stx,krk -->
## De geheugenconfiguratie instellen

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Controleren op software-updates

<!-- @require:software-update -->
<!-- @device:end -->

## Eenmalige installatie

Voor dit playbook moet Lemonade als backend draaien en, op Linux, een containerengine (Podman) om Open WebUI uit te voeren. Stel deze eerst in voordat je Open WebUI installeert.

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

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @prereq:lemonade-models-qwen3-4b,lemonade-models-sdxl-turbo -->

<!-- @test:id=lemonade-cli-verify timeout=30 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end --> 

## Modellen downloaden in Lemonade

Zorg ervoor dat de modellen die je wilt gebruiken zijn gedownload en klaar staan in Lemonade voordat je Open WebUI installeert.

1. Open de Lemonade GUI op `http://localhost:13305`.
2. Blader door de beschikbare modellen en download degene die je wilt gebruiken (bijvoorbeeld een LLM voor chat, een vision-model en/of een Stable Diffusion-model voor beeldgeneratie).
3. Controleer of de API bereikbaar is door naar `http://localhost:13305/api/v1/models` in je browser te gaan — je zou je gedownloade modellen vermeld moeten zien.

> Modellen moeten worden gedownload in **Lemonade** (`localhost:13305`) voordat ze kunnen verschijnen in **Open WebUI** (`localhost:8080`). Als een model later niet verschijnt in Open WebUI, kom dan hier terug en controleer eerst Lemonade.


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

## Open WebUI installeren

<!-- @os:windows -->
### 1. Python 3.12 installeren

Open WebUI vereist **Python 3.12** — het installeert niet op Python 3.13+. Met de Windows Python Launcher (`py`) kun je 3.12 naast elke bestaande Python-versie installeren zonder conflicten.

```powershell
winget install Python.Python.3.12
```

Sluit je terminal na installatie en open deze opnieuw, controleer vervolgens:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Opmerking:** Je systeem wordt geleverd met Python 3.13 vooraf geïnstalleerd. Het installeren van 3.12 heeft hier geen invloed op — `python` blijft 3.13 gebruiken, en `py -3.12` richt zich alleen op 3.12 wanneer je dat nodig hebt.
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

### 2. Een virtuele omgeving aanmaken en Open WebUI installeren

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
We gaan nu de Podman-service gebruiken om onze Open WebUI-installatie te containeriseren.

Download het volgende naar een map naar keuze: [compose.yml](assets/compose.yml)

Voer in die map het volgende commando uit:

```bash
podman compose up -d
```

Dit haalt de Open WebUI-image op en schrijft naar persistente opslag.

Start Open WebUI door `localhost:8080` in je browseradresbalk te typen.

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

> **Tip**: Open WebUI biedt ook andere installatieopties op hun [GitHub](https://github.com/open-webui/open-webui).
## Starting Open WebUI Server

<!-- @os:windows -->
- Voer de volgende opdracht uit om de Open WebUI HTTP-server te starten:
```bash
open-webui serve
```
<!-- @os:end -->

- Navigeer in een browser naar `http://localhost:8080`.
- Open WebUI zal u vragen een lokaal beheerdersaccount aan te maken. Zodra u bent ingelogd, ziet u de chatinterface.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> Houd het terminalvenster open. Als u het sluit, stopt Open WebUI.
<!-- @os:end -->

<!-- @os:linux -->
> De container draait op de achtergrond. Vanuit de map die `compose.yml` bevat, kunt u deze beheren met `podman compose down` (stoppen) en `podman compose up -d` (starten). Uw accounts en instellingen blijven bewaard in het `open_webui_data`-volume.
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

## Open WebUI verbinden met Lemonade

Nu beide services draaien — Lemonade op `localhost:13305` en Open WebUI op `localhost:8080` — verbindt u ze zodat Open WebUI de modellen van Lemonade kan gebruiken.

In Open WebUI:

1. Klik op het **gebruikersprofielpictogram** in de rechterbovenhoek en selecteer vervolgens **Settings**.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. Klik in het Settings-paneel linksonder op **Admin Settings**.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. Klik in de zijbalk van Admin Settings op **Connections** (of navigeer rechtstreeks naar `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. Voeg onder **OpenAI API** een nieuwe verbinding toe:
   - **Base URL:** `http://localhost:13305/api/v1`
   - **API Key:** `-` (een enkel streepje volstaat voor lokaal gebruik)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. Zorg ervoor dat onder **"Manage OpenAI API Connections"** alleen `http://localhost:13305/api/v1` is ingeschakeld. Schakel eventuele andere verbindingen uit (bijvoorbeeld de standaard OpenAI-verbinding).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. Klik op **Save**.

7. **(Aanbevolen)** Schakel automatische generatiefuncties uit om Open WebUI responsief te houden bij gebruik van lokale LLM's. Ga naar **Admin Settings → Settings → Interface** en schakel het volgende uit:
   - Title Generation
   - Follow Up Generation
   - Tags Generation

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. Klik op **Save** en keer terug naar `http://localhost:8080`.
9. Klik op de modeldropdown — u zou de modellen moeten zien die u van Lemonade hebt gedownload.

---

## Belangrijkste activiteiten

U bent nu helemaal klaar. Laten we eens kijken naar drie interessante dingen om te doen.

---

### Activiteit 1: Chatten met een lokale LLM
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Klik op het dropdownmenu linksboven in de interface. Hierin worden de Lemonade-modellen weergegeven die u hebt geïnstalleerd. Selecteer er een om verder te gaan. (voorbeeld: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. Voer een bericht in voor de LLM en klik op verzenden (of druk op Enter). Het laden van de LLM in het geheugen duurt een paar seconden, waarna u het antwoord ziet binnenstromen.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Klik op het dropdownmenu linksboven in de interface. Hierin worden de Lemonade-modellen weergegeven die u hebt geïnstalleerd. Selecteer er een om verder te gaan. (voorbeeld: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Voer een bericht in voor de LLM en klik op verzenden (of druk op Enter). Het laden van de LLM in het geheugen duurt een paar seconden, waarna u het antwoord ziet binnenstromen.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. Het model reageert in de chat.

4. Open op dit moment `Task Manager` op uw systeem. U ziet **hoge GPU- of NPU-benutting**, afhankelijk van of het geselecteerde model **Hybrid** of **NPU** is. Met behulp van Taakbeheer kunt u bevestigen dat u het model lokaal uitvoert.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Klik op het dropdownmenu linksboven in de interface. Hierin worden de Lemonade-modellen weergegeven die u hebt geïnstalleerd. Selecteer er een om verder te gaan. (voorbeeld: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Voer een bericht in voor de LLM en klik op verzenden (of druk op Enter). Het laden van de LLM in het geheugen duurt een paar seconden, waarna u het antwoord ziet binnenstromen.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. Het model reageert in de chat.
<!-- @os:end -->

Dit bevestigt dat Open WebUI verzoeken naar Lemonade kan sturen via het OpenAI-compatibele chat-eindpunt.

---

### Activiteit 2: Een afbeelding uploaden en vragen stellen (Vision)

Hiervoor is een model nodig dat afbeeldingsinvoer ondersteunt (een Vision- of Multimodal-model).

1. Klik op het filterpictogram, selecteer "By Category" en kies vervolgens een model uit de sectie **Vision** (bijvoorbeeld `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. Klik op de knop **`+`** in het berichtvak en upload een afbeelding
3. Stel een vraag die echt beeldbegrip vereist: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. Het model antwoordt op basis van de inhoud van de afbeelding, niet met generieke tekst.

Dit toont aan dat Open WebUI multimodale verzoeken (tekst + afbeelding) via de backend (Lemonade) naar een vision-model kan sturen.

---

<!-- @os:windows -->
### Activiteit 3: Een afbeelding genereren vanuit een tekstprompt (Stable Diffusion)

Stable Diffusion-modellen ondersteunen geen tekstgeneratie; ze genereren alleen afbeeldingen via de Images API.

#### Stap 1: Afbeeldingsgeneratie configureren in Open WebUI

1. Zoek in de Lemonade GUI (`http://localhost:13305`) naar `SDXL-Turbo` (snel) of `SDXL-Base-1.0` (hogere kwaliteit) en download deze.
2. Ga naar **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Stel het volgende in:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` of `SDXL-Base-1.0`
4. Als u meer parameters wilt toevoegen, voeg deze dan toe aan het tekstveld als JSON. Bijvoorbeeld: `{ "steps": 4, "cfg_scale": 1 }`. Zie de beschikbare parameters op [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Opslaan
#### Stap 2: Beeldgeneratie inschakelen voor het model
Deze stap zorgt ervoor dat u Beeldgeneratie inschakelt als een mogelijkheid voor uw model.
1. Ga naar **Admin Settings → Models** (http://localhost:8080/admin/settings/models) en kies uw model
2. Schakel `Image Generation` in

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Stap 3: Een afbeelding genereren vanaf het chatscherm

1. Ga terug naar de chat op `http://localhost:8080`.
2. Selecteer een **Text Generation LLM** in de modeldropdown (voorbeeld: Qwen, Llama). **Selecteer geen Stable Diffusion-model**, aangezien dit een chatmodelselector is.
3. Klik in het berichtveld op **Integrations** en zet **Image** AAN.
4. Gebruik een prompt zoals: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Er wordt een afbeelding gegenereerd en weergegeven in de chat.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Dit laat zien dat Open WebUI een "tweedelige" workflow kan coördineren:
  - De LLM helpt bij het verfijnen van de prompt
  - De afbeelding wordt gegenereerd via Lemonade's Images-endpoint met Stable Diffusion
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Activiteit 3: Een afbeelding genereren vanuit een tekstprompt (Stable Diffusion)

Stable Diffusion-modellen ondersteunen geen tekstgeneratie, ze genereren alleen afbeeldingen via de Images API.

#### Stap 1: Beeldgeneratie configureren in Open WebUI

1. Zoek in de Lemonade GUI (`http://localhost:13305`) naar `SDXL-Turbo` (snel) of `SDXL-Base-1.0` (hogere kwaliteit) en download het.
2. Ga naar **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Stel in:
   - **Image Generation:** AAN
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` of `SDXL-Base-1.0`
4. Als u meer parameters wilt toevoegen, voeg deze dan toe aan het tekstveld als JSON. Bijvoorbeeld: `{ "steps": 4, "cfg_scale": 1 }`. Zie beschikbare parameters op [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Opslaan


#### Stap 2: Beeldgeneratie inschakelen voor het model
Deze stap zorgt ervoor dat u Beeldgeneratie inschakelt als een mogelijkheid voor uw model.
1. Ga naar **Admin Settings → Models** (http://localhost:8080/admin/settings/models) en kies uw model
2. Schakel `Image Generation` in

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Stap 3: Een afbeelding genereren vanaf het chatscherm

1. Ga terug naar de chat op `http://localhost:8080`.
2. Selecteer een **Text Generation LLM** in de modeldropdown (voorbeeld: Qwen, Llama). **Selecteer geen Stable Diffusion-model**, aangezien dit een chatmodelselector is.
3. Klik in het berichtveld op **Integrations** en zet **Image** AAN.
4. Gebruik een prompt zoals: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Er wordt een afbeelding gegenereerd en weergegeven in de chat.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Dit laat zien dat Open WebUI een "tweedelige" workflow kan coördineren:
  - De LLM helpt bij het verfijnen van de prompt
  - De afbeelding wordt gegenereerd via Lemonade's Images-endpoint met Stable Diffusion
<!-- @device:end -->
<!-- @os:end -->

---

## Probleemoplossing

### "Er verschijnen geen modellen in Open WebUI"
- Controleer eerst Lemonade: open `http://localhost:13305/api/v1/models` in een browser en bevestig dat uw modellen worden weergegeven en gedownload
- Controleer vervolgens de Open WebUI-verbinding: ga naar **Admin Settings → Connections** op `http://localhost:8080/admin/settings/connections` en controleer of de Base URL `http://localhost:13305/api/v1` is

### Foutmelding "This model does not support chat completion"
- U hebt een beeldmodel (SDXL-Turbo / SDXL-Base-1.0) geselecteerd in de chatmodeldropdown.
- **Oplossing**: selecteer een LLM voor chat en gebruik de Image-schakelaar + Images-instellingen voor generatie.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Fouten/time-outs bij beeldgeneratie
- Begin eerst met `SDXL-Turbo` (snel, minder stappen)
- Schakel, zodra het werkt, over naar `SDXL-Base-1.0` voor kwaliteit

---

## Volgende stappen

U beschikt nu over een werkende **'lokale AI-stack'**, één UI die meerdere modeltypes aanstuurt via een standaard-API.

Hier zijn drie uitbreidingen die volledig nieuwe workflows mogelijk maken:

### 1. Spraak-naar-tekst met Whisper

Probeer audio om te zetten in tekst met behulp van een Whisper-model, en voer dit vervolgens in een LLM in voor samenvatting, actiepunten of herschrijving. Dit is de basis voor vergadernotities en spraakgestuurde assistenten.

### 2. Python-programmeren binnen Open WebUI

Gebruik de ingebouwde code-uitvoeringservaring van Open WebUI om Python-codefragmenten uit te voeren, uitvoer te inspecteren en sneller te itereren—zonder de UI te verlaten. [Referentie](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. HTML-weergave binnen Open WebUI

Render HTML-uitvoer rechtstreeks in de interface. Dit is verrassend krachtig voor het bouwen van snelle prototypes, opgemaakte rapporten en interactieve codefragmenten. [Referentie](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## Referenties

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Lemonade Server-documentatie](https://lemonade-server.ai/docs)
- [Lemonade Server CLI](https://lemonade-server.ai/docs/lemonade-cli/)
- [Integratiehandleiding Lemonade ↔ Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Lemonade Server API-specificatie (endpoints)](https://lemonade-server.ai/docs/server/server_spec)
- [Video-doorloop (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [Video-doorloop (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)

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