<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije proveravana od strane čoveka. Može sadržati greške, a određena uputstva, komande, preuzimanja, dostupnost proizvoda ili drugi sadržaj mogu se razlikovati u zavisnosti od jezika ili regiona. U slučaju bilo kakve nedoslednosti ili neslaganja, merodavna je originalna verzija playbook-a na engleskom jeziku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ovaj priručnik zahteva najmanje **32GB** sistemske memorije.
<!-- @device:end -->

## Pregled

[Open WebUI](https://docs.openwebui.com) je samostalno hostovan interfejs zasnovan na pregledaču koji pruža poznato iskustvo čet-bota dok funkcioniše kao frontend za jedan ili više servera AI modela. Umesto da bude vezan za jednog provajdera, Open WebUI se može povezati na **bilo koji bekend koji izlaže OpenAI-kompatibilan API**, tako da možete menjati modele i mogućnosti bez menjanja UI-ja.

U ovom priručniku koristimo [**Lemonade**](https://lemonade-server.ai) kao bekend jer izlaže **jedinstven OpenAI-kompatibilan endpoint** koji podržava više modaliteta:
- **Velike jezičke modele (LLM)** za generisanje teksta
- **Vizuelne modele** za razumevanje slika
- **Stable Diffusion** za generisanje slika
- **Modele za transkripciju zvuka** za pretvaranje govora u tekst

Ova postavka vam omogućava da istražite **kompletan multimodalni tok rada od početka do kraja**.

---

## Šta ćete naučiti

Na kraju ćete moći da:

- Povežete Open WebUI sa lokalnim OpenAI-kompatibilnim bekendom (Lemonade)
- Ćaskate sa lokalnim LLM-om iz pregledača
- Otpremite sliku i postavljate pitanja vizuelnom modelu o njoj
- Generišete slike iz tekstualnih upita koristeći Stable Diffusion modele (SDXL-Turbo / SDXL)
- Razumete mentalni model kako biste mogli da koristite druge bekende (Ollama, vLLM, llama.cpp server, itd.)

---

## Osnovni koncepti (mentalni model)

### Tri komponente

| Deo | Šta radi | Primeri |
|---|---|---|
| Frontend (UI) | Veb aplikacija sa kojom komunicirate | Open WebUI |
| Bekend (server modela) | Hostuje modele i izlaže HTTP endpoint-e | Lemonade, Ollama, vLLM, llama.cpp server, OpenAI-kompatibilni serveri |
| Modeli | Sami LLM / vizuelni / difuzioni / audio modeli | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### Zašto je "OpenAI-kompatibilan API" bitan

Open WebUI je izgrađen oko standardnih endpoint-a u OpenAI stilu, kao što su:
  - Chat: `/chat/completions`
  - Lista modela: `/models`
  - Generisanje slika: `/images/generations`
  - Transkripcija zvuka: `/audio/transcriptions`

Lemonade izlaže ove endpoint-e pod `http://localhost:13305/api/v1/...`

Ako bekend podržava te endpoint-e, Open WebUI može da komunicira sa njim uz minimalno podešavanje. Zato možemo da menjamo bekende bez izmene toka rada.

#### Dva servisa, dva porta

Kroz ovaj priručnik radićete sa dva odvojena servisa:

| Servis | URL | Šta tamo radite |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | Pregledajte, preuzimajte i upravljajte modelima |
| **Open WebUI** | `http://localhost:8080` | Ćaskajte, otpremajte slike, generišite slike — korisnički interfejs |

Lemonade pokreće modele; Open WebUI je interfejs sa kojim komunicirate. Prvo koristite Lemonade GUI da preuzmete svoje modele, a zatim ih koristite iz Open WebUI.

---

## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Provera ažuriranja softvera

<!-- @require:software-update -->
<!-- @device:end -->

## Jednokratno podešavanje

Ovaj priručnik zahteva da Lemonade radi kao bekend, a na Linux-u i mašinu za kontejnere (Podman) za pokretanje Open WebUI. Podesite ovo pre instaliranja Open WebUI.

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

## Preuzimanje modela u Lemonade

Pre instaliranja Open WebUI, uverite se da su modeli koje želite da koristite preuzeti i spremni u Lemonade.

1. Otvorite Lemonade GUI na `http://localhost:13305`.
2. Pregledajte dostupne modele i preuzmite one koje želite da koristite (npr. LLM za ćaskanje, vizuelni model i/ili Stable Diffusion model za generisanje slika).
3. Potvrdite da je API dostupan tako što ćete posetiti `http://localhost:13305/api/v1/models` u pregledaču — trebalo bi da vidite listu preuzetih modela.

> Modeli moraju biti preuzeti u **Lemonade** (`localhost:13305`) pre nego što se pojave u **Open WebUI** (`localhost:8080`). Ako se model kasnije ne pojavi u Open WebUI, vratite se ovde i prvo proverite Lemonade.


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

## Instaliranje Open WebUI

<!-- @os:windows -->
### 1. Instalirajte Python 3.12

Open WebUI zahteva **Python 3.12** — ne instalira se na Python 3.13+. Windows Python Launcher (`py`) omogućava vam da instalirate 3.12 uporedo sa bilo kojom postojećom verzijom Python-a bez konflikata.

```powershell
winget install Python.Python.3.12
```

Zatvorite i ponovo otvorite terminal nakon instalacije, a zatim proverite:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Napomena:** Vaš sistem dolazi sa unapred instaliranim Python-om 3.13. Instaliranje 3.12 ne utiče na njega — `python` i dalje koristi 3.13, a `py -3.12` cilja na 3.12 samo kada vam je to potrebno.
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

### 2. Kreirajte virtuelno okruženje i instalirajte Open WebUI

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
Sada ćemo koristiti Podman servis da kontejnerizujemo našu Open WebUI instalaciju.

Preuzmite sledeće u direktorijum po vašem izboru: [compose.yml](assets/compose.yml)

U tom direktorijumu pokrenite sledeću komandu:

```bash
podman compose up -d
```

Ovo preuzima Open WebUI sliku i upisuje u trajno skladište.

Pokrenite Open WebUI tako što ćete uneti `localhost:8080` u adresnu traku pregledača.

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

> **Savet**: Open WebUI takođe nudi druge opcije instalacije na svom [GitHub](https://github.com/open-webui/open-webui) nalogu.
## Pokretanje Open WebUI servera

<!-- @os:windows -->
- Pokrenite sledeću komandu da biste pokrenuli Open WebUI HTTP server:
```bash
open-webui serve
```
<!-- @os:end -->

- U pregledaču otvorite `http://localhost:8080`.
- Open WebUI će od vas tražiti da napravite lokalni administratorski nalog. Kada se prijavite, videćete interfejs za ćaskanje.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> Ostavite prozor terminala otvorenim. Zatvaranjem terminala zaustavlja se Open WebUI.
<!-- @os:end -->

<!-- @os:linux -->
> Kontejner radi u pozadini. Iz direktorijuma koji sadrži `compose.yml`, upravljajte njime pomoću `podman compose down` (zaustavljanje) i `podman compose up -d` (pokretanje). Vaši nalozi i podešavanja se čuvaju u volumenu `open_webui_data`.
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

## Povezivanje Open WebUI sa Lemonade

Sada kada oba servisa rade — Lemonade na `localhost:13305` i Open WebUI na `localhost:8080` — povežite ih kako bi Open WebUI mogao da koristi modele iz Lemonade.

U Open WebUI:

1. Kliknite na **ikonicu korisničkog profila** u gornjem desnom uglu, a zatim izaberite **Settings**.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. U panelu Settings, kliknite na **Admin Settings** u donjem levom uglu.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. U bočnoj traci Admin Settings kliknite na **Connections** (ili direktno otvorite `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. U sekciji **OpenAI API**, dodajte novu vezu:
   - **Base URL:** `http://localhost:13305/api/v1`
   - **API Key:** `-` (jedna crtica je dovoljna za lokalno korišćenje)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. Proverite da je pod **"Manage OpenAI API Connections"** omogućena samo veza `http://localhost:13305/api/v1`. Onemogućite sve ostale veze (npr. podrazumevanu OpenAI vezu).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. Kliknite na **Save**.

7. **(Preporučeno)** Onemogućite funkcije automatskog generisanja kako bi Open WebUI ostao responzivan sa lokalnim LLM-ovima. Idite na **Admin Settings → Settings → Interface** i isključite:
   - Title Generation
   - Follow Up Generation
   - Tags Generation

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. Kliknite na **Save**, a zatim se vratite na `http://localhost:8080`.
9. Kliknite na padajući meni sa modelima — trebalo bi da vidite modele koje ste preuzeli iz Lemonade.

---

## Glavne aktivnosti

Sada je sve spremno. Pogledajmo tri zanimljive stvari koje možete da uradite.

---

### Aktivnost 1: Ćaskanje sa lokalnim LLM-om
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Kliknite na padajući meni u gornjem levom uglu interfejsa. Ovo će prikazati Lemonade modele koje imate instalirane. Izaberite jedan da biste nastavili. (primer: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. Unesite poruku za LLM i kliknite na dugme za slanje (ili pritisnite Enter). LLM-u je potrebno nekoliko sekundi da se učita u memoriju, a zatim ćete videti da odgovor stiže u vidu toka.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Kliknite na padajući meni u gornjem levom uglu interfejsa. Ovo će prikazati Lemonade modele koje imate instalirane. Izaberite jedan da biste nastavili. (primer: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Unesite poruku za LLM i kliknite na dugme za slanje (ili pritisnite Enter). LLM-u je potrebno nekoliko sekundi da se učita u memoriju, a zatim ćete videti da odgovor stiže u vidu toka.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. Model će odgovoriti u ćaskanju.

4. U ovom trenutku otvorite `Task Manager` na svom sistemu. Videćete **veliku iskorišćenost GPU-a ili NPU-a**, u zavisnosti od toga da li je izabrani model **Hybrid** ili **NPU**. Pomoću menadžera zadataka možete potvrditi da model zaista pokrećete lokalno.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Kliknite na padajući meni u gornjem levom uglu interfejsa. Ovo će prikazati Lemonade modele koje imate instalirane. Izaberite jedan da biste nastavili. (primer: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Unesite poruku za LLM i kliknite na dugme za slanje (ili pritisnite Enter). LLM-u je potrebno nekoliko sekundi da se učita u memoriju, a zatim ćete videti da odgovor stiže u vidu toka.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. Model će odgovoriti u ćaskanju.
<!-- @os:end -->

Ovim se potvrđuje da Open WebUI može da šalje zahteve ka Lemonade koristeći OpenAI-kompatibilnu chat krajnju tačku.

---

### Aktivnost 2: Otpremanje slike i postavljanje pitanja (Vision)

Za ovo je potreban model koji podržava unos slika (Vision ili multimodalni model).

1. Kliknite na ikonicu filtera, izaberite "By Category", a zatim izaberite model iz sekcije **Vision** (npr. `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. Kliknite na dugme **`+`** u polju za poruku i otpremite sliku
3. Postavite pitanje koje zahteva pravo razumevanje slike: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. Model odgovara na osnovu sadržaja slike, a ne generičkog teksta.

Ovo pokazuje da Open WebUI može da šalje multimodalne zahteve (tekst + slika) kroz backend (Lemonade) ka vision modelu.

---

<!-- @os:windows -->
### Aktivnost 3: Generisanje slike na osnovu tekstualnog upita (Stable Diffusion)

Stable Diffusion modeli ne podržavaju generisanje teksta, oni samo generišu slike putem Images API-ja. 

#### Korak 1: Konfigurisanje generisanja slika u Open WebUI

1. U Lemonade GUI (`http://localhost:13305`), pretražite `SDXL-Turbo` (brže) ili `SDXL-Base-1.0` (veći kvalitet) i preuzmite ga.
2. Idite na **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Podesite:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` ili `SDXL-Base-1.0`
4. Ako želite da dodate više parametara, dodajte ih u tekstualno polje u JSON formatu. Na primer: `{ "steps": 4, "cfg_scale": 1 }`. Dostupne parametre pogledajte na [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Sačuvajte
#### Korak 2: Omogućite generisanje slika za model
Ovaj korak obezbeđuje da omogućite generisanje slika kao mogućnost za vaš model.
1. Idite na **Admin Settings → Models** (http://localhost:8080/admin/settings/models) i izaberite svoj model
2. Uključite `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Korak 3: Generišite sliku sa ekrana za ćaskanje

1. Vratite se na ćaskanje na `http://localhost:8080`.
2. Izaberite **Text Generation LLM** u padajućem meniju modela (primer: Qwen, Llama). **Nemojte birati Stable Diffusion model** jer je ovo selektor modela za ćaskanje.
3. U oblasti za poruke kliknite na **Integrations**, i uključite **Image**.
4. Koristite podsticaj poput: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Slika se generiše i pojavljuje se u ćaskanju.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Ovim se utvrđuje da Open WebUI može da koordiniše „dvodelni“ radni tok:
  - LLM pomaže u usavršavanju podsticaja
  - Slika se generiše preko Lemonade Images krajnje tačke koristeći Stable Diffusion
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Aktivnost 3: Generisanje slike iz tekstualnog podsticaja (Stable Diffusion)

Stable Diffusion modeli ne podržavaju generisanje teksta, oni generišu slike samo preko Images API-ja.

#### Korak 1: Konfigurišite generisanje slika u Open WebUI

1. U Lemonade GUI-ju (`http://localhost:13305`), pretražite `SDXL-Turbo` (brže) ili `SDXL-Base-1.0` (viši kvalitet) i preuzmite ga.
2. Idite na **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Podesite:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` ili `SDXL-Base-1.0`
4. Ako želite da dodate više parametara, dodajte ih u tekstualno polje kao JSON. Na primer: `{ "steps": 4, "cfg_scale": 1 }`. Pogledajte dostupne parametre na [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Sačuvajte


#### Korak 2: Omogućite generisanje slika za model
Ovaj korak obezbeđuje da omogućite generisanje slika kao mogućnost za vaš model.
1. Idite na **Admin Settings → Models** (http://localhost:8080/admin/settings/models) i izaberite svoj model
2. Uključite `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Korak 3: Generišite sliku sa ekrana za ćaskanje

1. Vratite se na ćaskanje na `http://localhost:8080`.
2. Izaberite **Text Generation LLM** u padajućem meniju modela (primer: Qwen, Llama). **Nemojte birati Stable Diffusion model** jer je ovo selektor modela za ćaskanje.
3. U oblasti za poruke kliknite na **Integrations**, i uključite **Image**.
4. Koristite podsticaj poput: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Slika se generiše i pojavljuje se u ćaskanju.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Ovim se utvrđuje da Open WebUI može da koordiniše „dvodelni“ radni tok:
  - LLM pomaže u usavršavanju podsticaja
  - Slika se generiše preko Lemonade Images krajnje tačke koristeći Stable Diffusion
<!-- @device:end -->
<!-- @os:end -->

---

## Rešavanje problema

### „Nijedan model se ne prikazuje u Open WebUI“
- Prvo, proverite Lemonade: otvorite `http://localhost:13305/api/v1/models` u pregledaču i potvrdite da su vaši modeli navedeni i preuzeti
- Zatim proverite Open WebUI konekciju: idite na **Admin Settings → Connections** na `http://localhost:8080/admin/settings/connections` i proverite da li je Base URL `http://localhost:13305/api/v1`

### Poruka o grešci „This model does not support chat completion“
- Izabrali ste model za slike (SDXL-Turbo / SDXL-Base-1.0) u padajućem meniju modela za ćaskanje.
- **Rešenje**: izaberite LLM za ćaskanje, a za generisanje koristite prekidač Image + podešavanja Images.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Greške/isteci vremena pri generisanju slika
- Počnite prvo sa `SDXL-Turbo` (brže, manje koraka)
- Kada proradi, prebacite model za slike na `SDXL-Base-1.0` radi kvaliteta

---

## Sledeći koraci

Sada imate funkcionalan **„lokalni AI paket“**, jedan korisnički interfejs koji kontroliše više tipova modela preko standardnog API-ja.

Evo tri proširenja koja otključavaju potpuno nove radne tokove:

### 1. Pretvaranje govora u tekst pomoću Whisper-a

Probajte da pretvorite audio u tekst koristeći Whisper model, a zatim ga prosledite LLM-u radi sažimanja, izdvajanja akcionih stavki ili preformulisanja. Ovo je osnova za beleške sa sastanaka i asistente vođene glasom.

### 2. Python programiranje unutar Open WebUI

Koristite ugrađeno iskustvo izvršavanja koda u Open WebUI da pokrenete Python isečke, pregledate izlaze i iterirate brže — bez napuštanja korisničkog interfejsa. [Referenca](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. HTML prikazivanje unutar Open WebUI

Prikazujte HTML izlaze direktno u interfejsu. Ovo je iznenađujuće moćno za izradu brzih prototipova, formatiranih izveštaja i interaktivnih isečaka. [Referenca](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## Reference

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Lemonade Server dokumentacija](https://lemonade-server.ai/docs)
- [Lemonade Server CLI](https://lemonade-server.ai/docs/lemonade-cli/)
- [Vodič za integraciju Lemonade ↔ Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Lemonade Server API specifikacija (krajnje tačke)](https://lemonade-server.ai/docs/server/server_spec)
- [Video pregled (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [Video pregled (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)

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