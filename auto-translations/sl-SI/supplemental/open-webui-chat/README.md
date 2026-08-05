<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ta vodnik zahteva vsaj **32 GB** sistemskega pomnilnika.
<!-- @device:end -->

## Pregled

[Open WebUI](https://docs.openwebui.com) je samostojno gostovan vmesnik, ki deluje v brskalniku in ponuja znano izkušnjo klepetalnega robota, hkrati pa deluje kot vmesnik za enega ali več strežnikov modelov AI. Namesto da bi bil vezan na enega ponudnika, se lahko Open WebUI poveže z **vsakim zalednim sistemom, ki izpostavlja API, združljiv z OpenAI**, tako da lahko menjate modele in zmogljivosti brez menjave uporabniškega vmesnika.

V tem vodniku uporabljamo [**Lemonade**](https://lemonade-server.ai) kot zaledni sistem, ker izpostavlja **enotno končno točko, združljivo z OpenAI**, ki podpira več modalnosti:
- **Velike jezikovne modele (LLM)** za generiranje besedila
- **Vizualne modele** za razumevanje slik
- **Stable Diffusion** za generiranje slik
- **Modele za prepis zvoka** za pretvorbo govora v besedilo

Ta nastavitev vam omogoča raziskovanje **celotnega večmodalnega poteka dela od začetka do konca**.

---

## Kaj se boste naučili

Ob koncu boste znali:

- Povezati Open WebUI z lokalnim zalednim sistemom, združljivim z OpenAI (Lemonade)
- Klepetati z lokalnim LLM iz svojega brskalnika
- Naložiti sliko in postavljati vprašanja o njej vizualnemu modelu
- Generirati slike iz besedilnih pozivov z uporabo modelov Stable Diffusion (SDXL-Turbo / SDXL)
- Razumeti miselni model, da boste lahko uporabljali tudi druge zaledne sisteme (Ollama, vLLM, strežnik llama.cpp itd.)

---

## Osnovni koncepti (miselni model)

### Trije sestavni deli

| Del | Kaj počne | Primeri |
|---|---|---|
| Uporabniški vmesnik (UI) | Spletna aplikacija, s katero komunicirate | Open WebUI |
| Zaledni sistem (strežnik modelov) | Gosti modele in izpostavlja HTTP končne točke | Lemonade, Ollama, vLLM, strežnik llama.cpp, strežniki, združljivi z OpenAI |
| Modeli | Dejanski modeli LLM/vizualni/difuzijski/zvočni | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### Zakaj je pomemben »API, združljiv z OpenAI«

Open WebUI je zgrajen okoli standardnih končnih točk v slogu OpenAI, kot so:
  - Klepet: `/chat/completions`
  - Seznam modelov: `/models`
  - Generiranje slik: `/images/generations`
  - Prepis zvoka: `/audio/transcriptions`

Lemonade te izpostavlja pod `http://localhost:13305/api/v1/...`

Če zaledni sistem podpira te končne točke, lahko Open WebUI z njim komunicira ob minimalni nastavitvi. Zato lahko zaledne sisteme menjamo brez spreminjanja poteka dela.

#### Dve storitvi, dva vrat

Skozi ta vodnik boste delali z dvema ločenima storitvama:

| Storitev | URL | Kaj tam počnete |
|---|---|---|
| **Lemonade** (grafični vmesnik) | `http://localhost:13305` | Brskanje, prenos in upravljanje modelov |
| **Open WebUI** | `http://localhost:8080` | Klepet, nalaganje slik, generiranje slik — uporabniški vmesnik |

Lemonade poganja modele; Open WebUI je vmesnik, s katerim komunicirate. Najprej uporabite grafični vmesnik Lemonade za prenos modelov, nato jih uporabite iz Open WebUI.

---

## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme

<!-- @require:software-update -->
<!-- @device:end -->

## Enkratna nastavitev

Ta vodnik potrebuje zagnan Lemonade kot zaledni sistem, na Linuxu pa tudi kontejnerski pogon (Podman) za zagon Open WebUI. Pred namestitvijo Open WebUI nastavite to.

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

## Prenos modelov v Lemonade

Pred namestitvijo Open WebUI se prepričajte, da so modeli, ki jih želite uporabljati, preneseni in pripravljeni v Lemonade.

1. Odprite grafični vmesnik Lemonade na `http://localhost:13305`.
2. Prebrskajte razpoložljive modele in prenesite tiste, ki jih želite uporabljati (npr. LLM za klepet, vizualni model in/ali model Stable Diffusion za generiranje slik).
3. Potrdite, da je API dosegljiv tako, da v brskalniku obiščete `http://localhost:13305/api/v1/models` — videti bi morali seznam prenesenih modelov.

> Modeli morajo biti preneseni v **Lemonade** (`localhost:13305`), preden se lahko pojavijo v **Open WebUI** (`localhost:8080`). Če se model kasneje ne prikaže v Open WebUI, se vrnite sem in najprej preverite Lemonade.


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

## Namestitev Open WebUI

<!-- @os:windows -->
### 1. Namestite Python 3.12

Open WebUI zahteva **Python 3.12** — ne namesti se na Python 3.13+. Zaganjalnik za Windows Python (`py`) omogoča namestitev različice 3.12 vzporedno z morebitno obstoječo različico Pythona brez konfliktov.

```powershell
winget install Python.Python.3.12
```

Po namestitvi zaprite in ponovno odprite terminal, nato preverite:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Opomba:** Vaš sistem ima vnaprej nameščen Python 3.13. Namestitev različice 3.12 nanj ne vpliva — `python` še naprej uporablja 3.13, `py -3.12` pa cilja na 3.12 samo takrat, ko jo potrebujete.
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

### 2. Ustvarite navidezno okolje in namestite Open WebUI

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
Zdaj bomo uporabili storitev Podman za kontejnerizacijo naše namestitve Open WebUI.

Prenesite naslednje v mapo po vaši izbiri: [compose.yml](assets/compose.yml)

V tej mapi zaženite naslednji ukaz:

```bash
podman compose up -d
```

S tem se prenese slika Open WebUI in zapiše v trajno shrambo.

Zaženite Open WebUI tako, da v naslovno vrstico brskalnika vnesete `localhost:8080`.

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

> **Nasvet**: Open WebUI ponuja tudi druge možnosti namestitve na svojem [GitHub](https://github.com/open-webui/open-webui).
## Zaganjanje strežnika Open WebUI

<!-- @os:windows -->
- Zaženite naslednji ukaz, da zaženete strežnik HTTP Open WebUI:
```bash
open-webui serve
```
<!-- @os:end -->

- V brskalniku pojdite na `http://localhost:8080`.
- Open WebUI vas bo pozval, da ustvarite lokalni skrbniški račun. Ko boste prijavljeni, boste videli klepetalni vmesnik.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> Okno terminala pustite odprto. Če ga zaprete, se Open WebUI ustavi.
<!-- @os:end -->

<!-- @os:linux -->
> Vsebnik teče v ozadju. V mapi, ki vsebuje `compose.yml`, ga upravljate z ukazoma `podman compose down` (ustavitev) in `podman compose up -d` (zagon). Vaši računi in nastavitve so shranjeni v obsegu `open_webui_data`.
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

## Povezovanje Open WebUI z Lemonade

Zdaj, ko obe storitvi tečeta — Lemonade na `localhost:13305` in Open WebUI na `localhost:8080` — ju povežite, da bo Open WebUI lahko uporabljal modele iz Lemonade.

V Open WebUI:

1. Kliknite ikono **uporabniškega profila** v zgornjem desnem kotu, nato izberite **Settings**.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. V plošči Settings kliknite **Admin Settings** v spodnjem levem kotu.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. V stranski vrstici Admin Settings kliknite **Connections** (ali pojdite neposredno na `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. Pod **OpenAI API** dodajte novo povezavo:
   - **Base URL:** `http://localhost:13305/api/v1`
   - **API Key:** `-` (za lokalno uporabo zadostuje en pomišljaj)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. Prepričajte se, da je pod **"Manage OpenAI API Connections"** omogočena samo povezava `http://localhost:13305/api/v1`. Onemogočite vse druge povezave (npr. privzeto povezavo OpenAI).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. Kliknite **Save**.

7. **(Priporočeno)** Onemogočite funkcije samodejnega ustvarjanja, da Open WebUI ostane odziven pri delu z lokalnimi jezikovnimi modeli (LLM). Pojdite na **Admin Settings → Settings → Interface** in izklopite:
   - Title Generation
   - Follow Up Generation
   - Tags Generation

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. Kliknite **Save**, nato se vrnite na `http://localhost:8080`.
9. Kliknite spustni meni z modeli — videti bi morali modele, ki ste jih prenesli iz Lemonade.

---

## Glavne dejavnosti

Zdaj je vse pripravljeno. Oglejmo si tri zanimive dejavnosti.

---

### Dejavnost 1: Pogovor z lokalnim jezikovnim modelom (LLM)
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Kliknite spustni meni v zgornjem levem kotu vmesnika. Prikazani bodo modeli Lemonade, ki jih imate nameščene. Izberite enega za nadaljevanje. (primer: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. Vnesite sporočilo za LLM in kliknite pošlji (ali pritisnite Enter). LLM bo potreboval nekaj sekund, da se naloži v pomnilnik, nato pa boste videli odgovor, ki se sprotno izpisuje.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Kliknite spustni meni v zgornjem levem kotu vmesnika. Prikazani bodo modeli Lemonade, ki jih imate nameščene. Izberite enega za nadaljevanje. (primer: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Vnesite sporočilo za LLM in kliknite pošlji (ali pritisnite Enter). LLM bo potreboval nekaj sekund, da se naloži v pomnilnik, nato pa boste videli odgovor, ki se sprotno izpisuje.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. Model se bo odzval v klepetu.

4. Med tem odprite `Task Manager` v sistemu. Videli boste **visoko izkoriščenost GPU ali NPU**, odvisno od tega, ali je izbrani model **Hybrid** ali **NPU**. S pomočjo upravitelja opravil lahko potrdite, da model dejansko izvajate lokalno.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Kliknite spustni meni v zgornjem levem kotu vmesnika. Prikazani bodo modeli Lemonade, ki jih imate nameščene. Izberite enega za nadaljevanje. (primer: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Vnesite sporočilo za LLM in kliknite pošlji (ali pritisnite Enter). LLM bo potreboval nekaj sekund, da se naloži v pomnilnik, nato pa boste videli odgovor, ki se sprotno izpisuje.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. Model se bo odzval v klepetu.
<!-- @os:end -->

To potrjuje, da lahko Open WebUI pošilja zahteve Lemonade prek klepetalne končne točke, združljive z OpenAI.

---

### Dejavnost 2: Naložite sliko in postavljajte vprašanja (vid)

To zahteva model, ki podpira vhod slike (model za vid ali multimodalni model).

1. Kliknite ikono filtra, izberite »By Category«, nato izberite model iz razdelka **Vision** (npr. `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. Kliknite gumb **`+`** v polju za sporočilo in naložite sliko
3. Postavite vprašanje, ki zahteva pravo razumevanje slike: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. Model odgovori na podlagi vsebine slike, ne na podlagi splošnega besedila.

To dokazuje, da lahko Open WebUI pošilja multimodalne zahteve (besedilo + slika) prek zaledja (Lemonade) modelu za vid.

---

<!-- @os:windows -->
### Dejavnost 3: Ustvarite sliko iz besedilnega poziva (Stable Diffusion)

Modeli Stable Diffusion ne podpirajo ustvarjanja besedila, ustvarjajo samo slike prek API-ja Images.

#### Korak 1: Konfiguracija ustvarjanja slik v Open WebUI

1. V grafičnem vmesniku Lemonade (`http://localhost:13305`) poiščite `SDXL-Turbo` (hitro) ali `SDXL-Base-1.0` (višja kakovost) in ga prenesite.
2. Pojdite na **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Nastavite:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` ali `SDXL-Base-1.0`
4. Če želite dodati več parametrov, jih dodajte v besedilno polje v obliki JSON. Na primer: `{ "steps": 4, "cfg_scale": 1 }`. Razpoložljive parametre si oglejte na [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Shranite
#### Korak 2: Omogočite generiranje slik za model
Ta korak zagotovi, da omogočite generiranje slik kot zmožnost za vaš model.
1. Pojdite v **Admin Settings → Models** (http://localhost:8080/admin/settings/models) in izberite svoj model
2. Vklopite `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Korak 3: Ustvarite sliko z zaslona klepeta

1. Pojdite nazaj v klepet na `http://localhost:8080`.
2. Izberite **Text Generation LLM** v spustnem meniju modela (na primer: Qwen, Llama). **Ne izberite modela Stable Diffusion**, saj je to izbirnik modela za klepet.
3. V območju sporočila kliknite na **Integrations** in preklopite **Image** na ON.
4. Uporabite poziv, kot je: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Slika je ustvarjena in se prikaže v klepetu.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

To potrjuje, da lahko Open WebUI usklajuje "dvodelni" potek dela:
  - LLM pomaga izpopolniti poziv
  - Slika se ustvari prek Lemonadove končne točke za slike (Images) z uporabo Stable Diffusion
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Aktivnost 3: Ustvarite sliko iz besedilnega poziva (Stable Diffusion)

Modeli Stable Diffusion ne podpirajo generiranja besedila, ustvarjajo samo slike prek API-ja Images. 

#### Korak 1: Konfigurirajte generiranje slik v Open WebUI

1. V grafičnem vmesniku Lemonade (`http://localhost:13305`) poiščite `SDXL-Turbo` (hitro) ali `SDXL-Base-1.0` (višja kakovost) in ga prenesite.
2. Pojdite v **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Nastavite:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` ali `SDXL-Base-1.0`
4. Če želite dodati več parametrov, jih dodajte v besedilno polje kot JSON. Na primer: `{ "steps": 4, "cfg_scale": 1 }`. Razpoložljive parametre si oglejte na [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Shranite


#### Korak 2: Omogočite generiranje slik za model
Ta korak zagotovi, da omogočite generiranje slik kot zmožnost za vaš model.
1. Pojdite v **Admin Settings → Models** (http://localhost:8080/admin/settings/models) in izberite svoj model
2. Vklopite `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Korak 3: Ustvarite sliko z zaslona klepeta

1. Pojdite nazaj v klepet na `http://localhost:8080`.
2. Izberite **Text Generation LLM** v spustnem meniju modela (na primer: Qwen, Llama). **Ne izberite modela Stable Diffusion**, saj je to izbirnik modela za klepet.
3. V območju sporočila kliknite na **Integrations** in preklopite **Image** na ON.
4. Uporabite poziv, kot je: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Slika je ustvarjena in se prikaže v klepetu.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

To potrjuje, da lahko Open WebUI usklajuje "dvodelni" potek dela:
  - LLM pomaga izpopolniti poziv
  - Slika se ustvari prek Lemonadove končne točke za slike (Images) z uporabo Stable Diffusion
<!-- @device:end -->
<!-- @os:end -->

---

## Odpravljanje težav

### »V Open WebUI se ne prikaže noben model«
- Najprej preverite Lemonade: odprite `http://localhost:13305/api/v1/models` v brskalniku in potrdite, da so vaši modeli navedeni in preneseni
- Nato preverite povezavo Open WebUI: pojdite v **Admin Settings → Connections** na `http://localhost:8080/admin/settings/connections` in preverite, ali je Base URL nastavljen na `http://localhost:13305/api/v1`

### Sporočilo o napaki »This model does not support chat completion«
- V spustnem meniju modela za klepet ste izbrali model za slike (SDXL-Turbo / SDXL-Base-1.0).
- **Rešitev**: izberite LLM za klepet, za generiranje pa uporabite preklop Image in nastavitve Images.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Napake/časovne omejitve pri generiranju slik
- Najprej začnite z `SDXL-Turbo` (hitro, manj korakov)
- Ko deluje, preklopite model za slike na `SDXL-Base-1.0` za boljšo kakovost

---

## Naslednji koraki

Zdaj imate delujoč **'lokalni AI sklad'**, en sam uporabniški vmesnik, ki upravlja več vrst modelov prek standardnega API-ja.

Tukaj so tri razširitve, ki odklenejo popolnoma nove poteke dela:

### 1. Pretvorba govora v besedilo z Whisper

Poskusite pretvoriti zvok v besedilo z uporabo modela Whisper, nato pa ga podajte v LLM za povzemanje, sezname opravil ali preoblikovanje. To je osnova za zapiske s sestankov in glasovno vodene asistente.

### 2. Kodiranje v Pythonu znotraj Open WebUI

Uporabite vgrajeno izkušnjo izvajanja kode v Open WebUI za zagon odlomkov kode v Pythonu, pregled izhodov in hitrejše iteriranje – ne da bi zapustili uporabniški vmesnik. [Referenca](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. Upodabljanje HTML znotraj Open WebUI

Neposredno upodobite izhode HTML v vmesniku. To je presenetljivo zmogljivo za izdelavo hitrih prototipov, oblikovanih poročil in interaktivnih odlomkov. [Referenca](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## Reference

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Dokumentacija Lemonade Server](https://lemonade-server.ai/docs)
- [Lemonade Server CLI](https://lemonade-server.ai/docs/lemonade-cli/)
- [Vodnik za integracijo Lemonade ↔ Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Specifikacija API-ja Lemonade Server (končne točke)](https://lemonade-server.ai/docs/server/server_spec)
- [Videopredstavitev (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [Videopredstavitev (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)

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