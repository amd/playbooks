<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinöversättning.** Den här sidan har automatiskt översatts från engelska och har inte granskats av en människa. Den kan innehålla fel, och vissa instruktioner, kommandon, nedladdningar, produkttillgänglighet eller annat innehåll kan variera beroende på språk eller region. Vid eventuella motsägelser eller avvikelser är det den ursprungliga engelska versionen av playbook som gäller och har företräde.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Denna spelbok kräver minst **32 GB** systemminne.
<!-- @device:end -->

## Översikt

[Open WebUI](https://docs.openwebui.com) är ett självhostat, webbläsarbaserat gränssnitt som ger en bekant chattbotupplevelse samtidigt som det fungerar som ett frontend för en eller flera AI-modellservrar. Istället för att vara bunden till en leverantör kan Open WebUI ansluta till **vilken backend som helst som exponerar ett OpenAI-kompatibelt API**, så att du kan byta modeller och funktioner utan att byta gränssnitt.

I den här spelboken använder vi [**Lemonade**](https://lemonade-server.ai) som backend eftersom den exponerar en **enhetlig OpenAI-kompatibel slutpunkt** som stödjer flera modaliteter:
- **Stora språkmodeller (LLM)** för textgenerering
- **Visionsmodeller** för bildförståelse
- **Stable Diffusion** för bildgenerering
- **Ljudtranskriberingsmodeller** för tal-till-text

Denna konfiguration gör att du kan utforska hela **det multimodala arbetsflödet från början till slut**.

---

## Vad du kommer att lära dig

När du är klar kommer du att kunna:

- Ansluta Open WebUI till en lokal OpenAI-kompatibel backend (Lemonade)
- Chatta med en lokal LLM från din webbläsare
- Ladda upp en bild och ställa frågor till en visionsmodell om den
- Generera bilder från textprompter med Stable Diffusion-modeller (SDXL-Turbo / SDXL)
- Förstå den mentala modellen så att du kan använda andra backends (Ollama, vLLM, llama.cpp server, osv.)

---

## Grundläggande begrepp (mental modell)

### De tre komponenterna

| Del | Vad den gör | Exempel |
|---|---|---|
| Frontend (gränssnitt) | Webbappen du interagerar med | Open WebUI |
| Backend (modellserver) | Hostar modeller och exponerar HTTP-slutpunkter | Lemonade, Ollama, vLLM, llama.cpp server, OpenAI-kompatibla servrar |
| Modeller | De faktiska LLM-/Vision-/Diffusion-/ljudmodellerna | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### Varför "OpenAI-kompatibelt API" är viktigt

Open WebUI är byggt kring standard OpenAI-liknande slutpunkter, till exempel:
  - Chatt: `/chat/completions`
  - Modellista: `/models`
  - Bildgenerering: `/images/generations`
  - Ljudtranskribering: `/audio/transcriptions`

Lemonade exponerar dessa under `http://localhost:13305/api/v1/...`

Om en backend stödjer dessa slutpunkter kan Open WebUI kommunicera med den med minimal konfiguration. Det är därför vi kan byta backend utan att ändra vårt arbetsflöde.

#### Två tjänster, två portar

Genom hela denna spelbok kommer du att arbeta med två separata tjänster:

| Tjänst | URL | Vad du gör där |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | Bläddra, ladda ner och hantera modeller |
| **Open WebUI** | `http://localhost:8080` | Chatta, ladda upp bilder, generera bilder — det användarvända gränssnittet |

Lemonade kör modellerna; Open WebUI är gränssnittet du interagerar med. Använd Lemonade-GUI:t för att ladda ner dina modeller först, och använd dem sedan från Open WebUI.

---

## Ställa in minneskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrollera programvaruuppdateringar

<!-- @require:software-update -->
<!-- @device:end -->

## Engångskonfiguration

Denna spelbok kräver att Lemonade körs som backend och, på Linux, en containermotor (Podman) för att köra Open WebUI. Ställ in dessa innan du installerar Open WebUI.

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

## Ladda ner modeller i Lemonade

Innan du installerar Open WebUI, se till att de modeller du vill använda är nedladdade och redo i Lemonade.

1. Öppna Lemonade-GUI:t på `http://localhost:13305`.
2. Bläddra bland de tillgängliga modellerna och ladda ner de du vill använda (t.ex. en LLM för chatt, en visionsmodell och/eller en Stable Diffusion-modell för bildgenerering).
3. Bekräfta att API:et är nåbart genom att besöka `http://localhost:13305/api/v1/models` i din webbläsare — du bör se dina nedladdade modeller listade.

> Modeller måste laddas ner i **Lemonade** (`localhost:13305`) innan de kan visas i **Open WebUI** (`localhost:8080`). Om en modell inte visas i Open WebUI senare, kom tillbaka hit och kontrollera Lemonade först.


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

## Installera Open WebUI

<!-- @os:windows -->
### 1. Installera Python 3.12

Open WebUI kräver **Python 3.12** — det installeras inte på Python 3.13+. Windows Python Launcher (`py`) låter dig installera 3.12 sida vid sida med en befintlig Python-version utan konflikter.

```powershell
winget install Python.Python.3.12
```

Stäng och öppna om din terminal efter installationen, verifiera sedan:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Obs:** Ditt system levereras med Python 3.13 förinstallerat. Installation av 3.12 påverkar inte detta — `python` fortsätter att använda 3.13, och `py -3.12` riktar sig mot 3.12 endast när du behöver det.
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

### 2. Skapa en virtuell miljö och installera Open WebUI

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
Vi ska nu använda Podman-tjänsten för att containerisera vår Open WebUI-installation.

Ladda ner följande till en katalog du väljer: [compose.yml](assets/compose.yml)

Kör följande kommando i den katalogen:

```bash
podman compose up -d
```

Detta hämtar Open WebUI-avbildningen och skriver till persistent lagring.

Starta Open WebUI genom att skriva `localhost:8080` i din webbläsares adressfält.

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

> **Tips**: Open WebUI erbjuder även andra installationsalternativ på deras [GitHub](https://github.com/open-webui/open-webui).
## Starting Open WebUI Server

<!-- @os:windows -->
- Kör följande kommando för att starta Open WebUI HTTP-servern:
```bash
open-webui serve
```
<!-- @os:end -->

- Navigera till `http://localhost:8080` i en webbläsare.
- Open WebUI kommer att be dig skapa ett lokalt administratörskonto. När du är inloggad ser du chattgränssnittet.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> Håll terminalfönstret öppet. Om du stänger det stoppas Open WebUI.
<!-- @os:end -->

<!-- @os:linux -->
> Containern körs i bakgrunden. Från katalogen som innehåller `compose.yml` kan du hantera den med `podman compose down` (stoppa) och `podman compose up -d` (starta). Dina konton och inställningar sparas i volymen `open_webui_data`.
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

## Ansluta Open WebUI till Lemonade

Nu när båda tjänsterna körs — Lemonade på `localhost:13305` och Open WebUI på `localhost:8080` — kan du ansluta dem så att Open WebUI kan använda Lemonades modeller.

I Open WebUI:

1. Klicka på **användarprofilikonen** i det övre högra hörnet och välj sedan **Settings**.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. Klicka på **Admin Settings** längst ned till vänster i inställningspanelen.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. Klicka på **Connections** i sidopanelen för Admin Settings (eller navigera direkt till `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. Under **OpenAI API**, lägg till en ny anslutning:
   - **Base URL:** `http://localhost:13305/api/v1`
   - **API Key:** `-` (ett enda bindestreck fungerar lokalt)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. Se till att endast `http://localhost:13305/api/v1` är aktiverad under **"Manage OpenAI API Connections"**. Inaktivera eventuella andra anslutningar (t.ex. standardanslutningen till OpenAI).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. Klicka på **Save**.

7. **(Rekommenderas)** Inaktivera funktioner för automatisk generering för att hålla Open WebUI responsivt med lokala LLM:er. Gå till **Admin Settings → Settings → Interface** och stäng av:
   - Title Generation
   - Follow Up Generation
   - Tags Generation

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. Klicka på **Save** och gå sedan tillbaka till `http://localhost:8080`.
9. Klicka på modellrullgardinsmenyn — du bör nu se de modeller du laddat ned från Lemonade.

---

## Huvudaktiviteter

Nu är allt klart. Låt oss titta på tre intressanta saker att göra.

---

### Aktivitet 1: Chatta med en lokal LLM
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Klicka på rullgardinsmenyn längst upp till vänster i gränssnittet. Den visar de Lemonade-modeller du har installerat. Välj en för att fortsätta. (exempel: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. Skriv ett meddelande till LLM:en och klicka på skicka (eller tryck Enter). LLM:en tar några sekunder att laddas in i minnet och sedan ser du svaret strömma in.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Klicka på rullgardinsmenyn längst upp till vänster i gränssnittet. Den visar de Lemonade-modeller du har installerat. Välj en för att fortsätta. (exempel: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Skriv ett meddelande till LLM:en och klicka på skicka (eller tryck Enter). LLM:en tar några sekunder att laddas in i minnet och sedan ser du svaret strömma in.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. Modellen kommer att svara i chatten.

4. Öppna nu `Task Manager` på ditt system. Du kommer att se **hög GPU- eller NPU-användning** beroende på om modellen du valt är **Hybrid** respektive **NPU**. Med hjälp av aktivitetshanteraren kan du bekräfta att du kör modellen lokalt.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Klicka på rullgardinsmenyn längst upp till vänster i gränssnittet. Den visar de Lemonade-modeller du har installerat. Välj en för att fortsätta. (exempel: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Skriv ett meddelande till LLM:en och klicka på skicka (eller tryck Enter). LLM:en tar några sekunder att laddas in i minnet och sedan ser du svaret strömma in.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. Modellen kommer att svara i chatten.
<!-- @os:end -->

Detta bekräftar att Open WebUI kan skicka förfrågningar till Lemonade med hjälp av den OpenAI-kompatibla chattändpunkten.

---

### Aktivitet 2: Ladda upp en bild och ställ frågor (Vision)

Detta kräver en modell som stöder bildinmatning (en Vision- eller multimodal modell).

1. Klicka på filterikonen, välj "By Category," och välj sedan en modell från avsnittet **Vision** (t.ex. `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. Klicka på **`+`**-knappen i meddelanderutan och ladda upp en bild
3. Ställ en fråga som kräver verklig bildförståelse: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. Modellen svarar utifrån bildens innehåll, inte generisk text.

Detta visar att Open WebUI kan skicka multimodala förfrågningar (text + bild) via backend (Lemonade) till en Vision-modell.

---

<!-- @os:windows -->
### Aktivitet 3: Generera en bild från en textprompt (Stable Diffusion)

Stable Diffusion-modeller stöder inte textgenerering, de genererar endast bilder via Images API. 

#### Steg 1: Konfigurera bildgenerering i Open WebUI

1. Sök i Lemonade-gränssnittet (`http://localhost:13305`) efter `SDXL-Turbo` (snabb) eller `SDXL-Base-1.0` (högre kvalitet) och ladda ned den.
2. Gå till **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Ställ in:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` eller `SDXL-Base-1.0`
4. Om du vill lägga till fler parametrar, lägg till dem i textfältet som JSON. Till exempel: `{ "steps": 4, "cfg_scale": 1 }`. Se tillgängliga parametrar på [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Spara
#### Steg 2: Tillåt bildgenerering för modellen
Detta steg säkerställer att du aktiverar Bildgenerering som en funktion för din modell.
1. Gå till **Admin Settings → Models** (http://localhost:8080/admin/settings/models) och välj din modell
2. Aktivera `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Steg 3: Generera en bild från chattskärmen

1. Gå tillbaka till chatten på `http://localhost:8080`.
2. Välj en **Text Generation LLM** i modellmenyn (exempel: Qwen, Llama). **Välj inte en Stable Diffusion-modell** eftersom detta är en väljare för chattmodeller.
3. Klicka på **Integrations** i meddelandeområdet och slå PÅ **Image**.
4. Använd en prompt som: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. En bild genereras och visas i chatten.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Detta visar att Open WebUI kan koordinera ett arbetsflöde i "två delar":
  - LLM:en hjälper till att förfina prompten
  - Bilden genereras via Lemonades Images-slutpunkt med Stable Diffusion
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Aktivitet 3: Generera en bild från en textprompt (Stable Diffusion)

Stable Diffusion-modeller stöder inte textgenerering, de genererar endast bilder via Images-API:et.

#### Steg 1: Konfigurera bildgenerering i Open WebUI

1. I Lemonade-GUI:t (`http://localhost:13305`), sök efter `SDXL-Turbo` (snabb) eller `SDXL-Base-1.0` (högre kvalitet) och ladda ner den.
2. Gå till **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Ställ in:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` eller `SDXL-Base-1.0`
4. Om du vill lägga till fler parametrar, lägg till dem i textfältet som JSON. Till exempel: `{ "steps": 4, "cfg_scale": 1 }`. Se tillgängliga parametrar på [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Spara


#### Steg 2: Tillåt bildgenerering för modellen
Detta steg säkerställer att du aktiverar Bildgenerering som en funktion för din modell.
1. Gå till **Admin Settings → Models** (http://localhost:8080/admin/settings/models) och välj din modell
2. Aktivera `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Steg 3: Generera en bild från chattskärmen

1. Gå tillbaka till chatten på `http://localhost:8080`.
2. Välj en **Text Generation LLM** i modellmenyn (exempel: Qwen, Llama). **Välj inte en Stable Diffusion-modell** eftersom detta är en väljare för chattmodeller.
3. Klicka på **Integrations** i meddelandeområdet och slå PÅ **Image**.
4. Använd en prompt som: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. En bild genereras och visas i chatten.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Detta visar att Open WebUI kan koordinera ett arbetsflöde i "två delar":
  - LLM:en hjälper till att förfina prompten
  - Bilden genereras via Lemonades Images-slutpunkt med Stable Diffusion
<!-- @device:end -->
<!-- @os:end -->

---

## Felsökning

### "Inga modeller visas i Open WebUI"
- Kontrollera först Lemonade: öppna `http://localhost:13305/api/v1/models` i en webbläsare och bekräfta att dina modeller finns listade och nedladdade
- Kontrollera sedan Open WebUI-anslutningen: gå till **Admin Settings → Connections** på `http://localhost:8080/admin/settings/connections` och verifiera att Base URL är `http://localhost:13305/api/v1`

### Felmeddelandet "This model does not support chat completion"
- Du valde en bildmodell (SDXL-Turbo / SDXL-Base-1.0) i chattmodellens meny.
- **Åtgärd**: välj en LLM för chatt, och använd bildväxlaren + Images-inställningarna för generering.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Fel/timeout vid bildgenerering
- Börja med `SDXL-Turbo` först (snabb, färre steg)
- När det fungerar, byt bildmodell till `SDXL-Base-1.0` för kvalitet

---

## Nästa steg

Du har nu en fungerande **"lokal AI-stack"**, ett enda gränssnitt som styr flera modelltyper via ett standard-API.

Här är tre utökningar som öppnar upp helt nya arbetsflöden:

### 1. Tal till text med Whisper

Prova att omvandla ljud till text med en Whisper-modell, och mata sedan in det i en LLM för sammanfattning, åtgärdspunkter eller omskrivning. Detta är grunden för mötesanteckningar och röststyrda assistenter.

### 2. Python-kodning inuti Open WebUI

Använd Open WebUIs inbyggda kodkörningsupplevelse för att köra Python-snuttar, inspektera utdata och iterera snabbare — utan att lämna gränssnittet. [Referens](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. HTML-rendering inuti Open WebUI

Rendera HTML-utdata direkt i gränssnittet. Detta är förvånansvärt kraftfullt för att bygga snabba prototyper, formaterade rapporter och interaktiva snuttar. [Referens](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## Referenser

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Lemonade Server docs](https://lemonade-server.ai/docs)
- [Lemonade Server CLI](https://lemonade-server.ai/docs/lemonade-cli/)
- [Lemonade ↔ Open WebUI-integrationsguide](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Lemonade Server API-specifikation (slutpunkter)](https://lemonade-server.ai/docs/server/server_spec)
- [Videogenomgång (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [Videogenomgång (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)

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