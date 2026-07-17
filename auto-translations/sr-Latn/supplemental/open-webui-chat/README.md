<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ovaj priručnik koristi posebne oznake koje GitHub ne može prikazati. Posetite [amd.com/playbooks](https://amd.com/playbooks) da biste ispravno pregledali ovaj sadržaj.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ovaj priručnik zahteva najmanje **32GB** sistemske memorije.
<!-- @device:end -->

## Pregled

[Open WebUI](https://docs.openwebui.com) je interfejs koji se samostalno hostuje, zasnovan na pregledaču, koji pruža poznato iskustvo čet-bota i istovremeno služi kao frontend za jedan ili više servera AI modela. Umesto da bude vezan za jednog provajdera, Open WebUI se može povezati sa **bilo kojim backendom koji izlaže OpenAI-kompatibilni API**, tako da možete menjati modele i mogućnosti bez promene korisničkog interfejsa.

U ovom priručniku koristimo [**Lemonade**](https://lemonade-server.ai) kao backend jer izlaže **jedinstveni OpenAI-kompatibilni endpoint** koji podržava više modaliteta:
- **Veliki jezički modeli (LLM)** za generisanje teksta
- **Vizuelni modeli** za razumevanje slika
- **Stable Diffusion** za generisanje slika
- **Modeli za transkripciju zvuka** za pretvaranje govora u tekst

Ovo podešavanje vam omogućava da istražite **kompletan multimodalni tok rada od početka do kraja**.

---

## Šta ćete naučiti

Na kraju, bićete u mogućnosti da:

- Povežete Open WebUI sa lokalnim OpenAI-kompatibilnim backendom (Lemonade)
- Čatujete sa lokalnim LLM-om iz svog pregledača
- Otpremite sliku i postavljate pitanja vizuelnom modelu o njoj
- Generišete slike iz tekstualnih upita koristeći Stable Diffusion modele (SDXL-Turbo / SDXL)
- Razumete mentalni model kako biste mogli da koristite druge backende (Ollama, vLLM, llama.cpp server, itd.)

---

## Osnovni koncepti (mentalni model)

### Tri komponente

| Deo | Šta radi | Primeri |
|---|---|---|
| Frontend (UI) | Veb aplikacija sa kojom komunicirate | Open WebUI |
| Backend (server modela) | Hostuje modele i izlaže HTTP endpoint-e | Lemonade, Ollama, vLLM, llama.cpp server, OpenAI-kompatibilni serveri |
| Modeli | Stvarni LLM / vizuelni / difuzni / audio modeli | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### Zašto je „OpenAI-kompatibilni API" važan

Open WebUI je izgrađen oko standardnih OpenAI-stilskih endpoint-a, kao što su:
  - Čet: `/chat/completions`
  - Lista modela: `/models`
  - Generisanje slika: `/images/generations`
  - Transkripcija zvuka: `/audio/transcriptions`

Lemonade ih izlaže pod `http://localhost:13305/api/v1/...`

Ako backend podržava te endpoint-e, Open WebUI može da komunicira sa njim uz minimalno podešavanje. Zato možemo menjati backende bez promene našeg toka rada.

#### Dve usluge, dva porta

Tokom ovog priručnika radićete sa dve odvojene usluge:

| Usluga | URL | Šta tamo radite |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | Pregledajte, preuzimajte i upravljajte modelima |
| **Open WebUI** | `http://localhost:8080` | Čatujte, otpremajte slike, generišete slike — korisnički interfejs |

Lemonade pokreće modele; Open WebUI je interfejs sa kojim komunicirate. Koristite Lemonade GUI da prvo preuzmete modele, a zatim ih koristite iz Open WebUI.

---

## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Proverite ažuriranja softvera

<!-- @require:software-update -->
<!-- @device:end -->

## Jednokratno podešavanje

Ovaj priručnik zahteva da Lemonade radi kao backend i, na Linuxu, engine za kontejnere (Podman) za pokretanje Open WebUI. Podesite ovo pre instalacije Open WebUI.

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

Pre instalacije Open WebUI, uverite se da su modeli koje želite da koristite preuzeti i spremni u Lemonade.

1. Otvorite Lemonade GUI na `http://localhost:13305`.
2. Pregledajte dostupne modele i preuzmite one koje želite da koristite (npr. LLM za čet, vizuelni model i/ili Stable Diffusion model za generisanje slika).
3. Potvrdite da je API dostupan posetom `http://localhost:13305/api/v1/models` u vašem pregledaču — trebalo bi da vidite listu vaših preuzetih modela.

> Modeli moraju biti preuzeti u **Lemonade** (`localhost:13305`) pre nego što mogu da se pojave u **Open WebUI** (`localhost:8080`). Ako se model ne prikazuje u Open WebUI kasnije, vratite se ovde i prvo proverite Lemonade.


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

## Instalacija Open WebUI

<!-- @os:windows -->
### 1. Instalirajte Python 3.12

Open WebUI zahteva **Python 3.12** — ne instalira se na Python 3.13+. Windows Python Launcher (`py`) vam omogućava da instalirate 3.12 paralelno sa bilo kojom postojećom verzijom Pythona bez konflikata.

```powershell
winget install Python.Python.3.12
```

Zatvorite i ponovo otvorite terminal nakon instalacije, a zatim proverite:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Napomena:** Vaš sistem dolazi sa unapred instaliranim Python 3.13. Instaliranje 3.12 ne utiče na njega — `python` nastavlja da koristi 3.13, a `py -3.12` cilja 3.12 samo kada vam je potrebno.
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
Sada ćemo koristiti Podman servis za kontejnerizaciju naše instalacije Open WebUI.

Preuzmite sledeće u direktorijum po vašem izboru: [compose.yml](assets/compose.yml)

U tom direktorijumu pokrenite sledeću komandu:

```bash
podman compose up -d
```

Ovo preuzima Open WebUI sliku i upisuje u trajno skladište.

Pokrenite Open WebUI upisivanjem `localhost:8080` u adresnu traku pregledača.

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

> **Savet**: Open WebUI takođe pruža druge opcije instalacije na njihovom [GitHub](https://github.com/open-webui/open-webui).

## Pokretanje Open WebUI servera

<!-- @os:windows -->
- Pokrenite sledeću komandu da pokrenete Open WebUI HTTP server:
```bash
open-webui serve
```
<!-- @os:end -->

- U pregledaču, idite na `http://localhost:8080`.
- Open WebUI će vas zamoliti da kreirate lokalni administratorski nalog. Kada se prijavite, videćete interfejs za čet.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> Ostavite prozor terminala otvorenim. Zatvaranjem se zaustavlja Open WebUI.
<!-- @os:end -->

<!-- @os:linux -->
> Kontejner radi u pozadini. Iz direktorijuma koji sadrži `compose.yml`, upravljajte njime pomoću `podman compose down` (zaustavljanje) i `podman compose up -d` (pokretanje). Vaši nalozi i podešavanja ostaju sačuvani u `open_webui_data` volumenu.
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

Sada kada obe usluge rade — Lemonade na `localhost:13305` i Open WebUI na `localhost:8080` — povežite ih kako bi Open WebUI mogao da koristi Lemonade-ove modele.

U Open WebUI:

1. Kliknite na **ikonu korisničkog profila** u gornjem desnom uglu, a zatim izaberite **Podešavanja**.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. U panelu Podešavanja, kliknite na **Administratorska podešavanja** u donjem levom uglu.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. U bočnoj traci Administratorskih podešavanja, kliknite na **Veze** (ili idite direktno na `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. Pod **OpenAI API**, dodajte novu vezu:
   - **Osnovna URL adresa:** `http://localhost:13305/api/v1`
   - **API ključ:** `-` (jedna crtica funkcioniše lokalno)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. Uverite se da je pod **„Upravljanje OpenAI API vezama"** omogućena samo `http://localhost:13305/api/v1`. Onemogućite sve ostale veze (npr. podrazumevanu OpenAI vezu).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. Kliknite na **Sačuvaj**.

7. **(Preporučeno)** Onemogućite funkcije automatskog generisanja kako biste Open WebUI održali responzivnim sa lokalnim LLM-ovima. Idite na **Administratorska podešavanja → Podešavanja → Interfejs** i isključite:
   - Generisanje naslova
   - Generisanje nastavka
   - Generisanje oznaka

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. Kliknite na **Sačuvaj**, a zatim se vratite na `http://localhost:8080`.
9. Kliknite na padajući meni modela — trebalo bi da vidite modele koje ste preuzeli iz Lemonade.

---

## Glavne aktivnosti

Sada ste sve podesili. Pogledajmo tri zanimljive stvari koje možete da uradite.

---

### Aktivnost 1: Čet sa lokalnim LLM-om
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Kliknite na padajući meni u gornjem levom uglu interfejsa. Prikazaće se Lemonade modeli koje ste instalirali. Izaberite jedan da nastavite. (primer: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. Unesite poruku LLM-u i kliknite na pošalji (ili pritisnite Enter). LLM će nekoliko sekundi učitavati u memoriju, a zatim ćete videti kako odgovor stiže.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Kliknite na padajući meni u gornjem levom uglu interfejsa. Prikazaće se Lemonade modeli koje ste instalirali. Izaberite jedan da nastavite. (primer: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Unesite poruku LLM-u i kliknite na pošalji (ili pritisnite Enter). LLM će nekoliko sekundi učitavati u memoriju, a zatim ćete videti kako odgovor stiže.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. Model će odgovoriti u četu.

4. U ovom trenutku, otvorite `Task Manager` na vašem sistemu. Videćete **visoku iskorišćenost GPU ili NPU** u zavisnosti od toga da li je model koji ste izabrali **Hybrid** ili **NPU** respektivno. Koristeći task manager, možete potvrditi da pokrećete model lokalno.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Kliknite na padajući meni u gornjem levom uglu interfejsa. Prikazaće se Lemonade modeli koje ste instalirali. Izaberite jedan da nastavite. (primer: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Unesite poruku LLM-u i kliknite na pošalji (ili pritisnite Enter). LLM će nekoliko sekundi učitavati u memoriju, a zatim ćete videti kako odgovor stiže.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. Model će odgovoriti u četu.
<!-- @os:end -->

Ovo potvrđuje da Open WebUI može da šalje zahteve Lemonade koristeći OpenAI-kompatibilni endpoint za čet.

---

### Aktivnost 2: Otpremite sliku i postavljajte pitanja (vizija)

Ovo zahteva model koji podržava unos slika (vizuelni ili multimodalni model).

1. Kliknite na ikonu filtera, izaberite „Po kategoriji", a zatim odaberite model iz odeljka **Vizija** (npr. `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. Kliknite na dugme **`+`** u polju za poruku i otpremite sliku
3. Postavite pitanje koje zahteva stvarno razumevanje slike: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. Model odgovara na osnovu sadržaja slike, a ne generičkog teksta.

Ovo demonstrira da Open WebUI može da šalje multimodalne zahteve (tekst + slika) kroz backend (Lemonade) vizuelnom modelu.

---

<!-- @os:windows -->
### Aktivnost 3: Generišite sliku iz tekstualnog upita (Stable Diffusion)

Stable Diffusion modeli ne podržavaju generisanje teksta, oni samo generišu slike kroz Images API.

#### Korak 1: Konfigurišite generisanje slika u Open WebUI

1. U Lemonade GUI (`http://localhost:13305`), potražite `SDXL-Turbo` (brzo) ili `SDXL-Base-1.0` (viši kvalitet) i preuzmite ga.
2. Idite na **Administratorska podešavanja → Slike** (http://localhost:8080/admin/settings/images)
3. Podesite:
   - **Generisanje slika:** UKLJUČENO
   - **Engine za generisanje slika:** Podrazumevano (OpenAI)
   - **OpenAI API osnovna URL adresa:** `http://localhost:13305/api/v1`
   - **OpenAI API ključ:** `-`
   - **Model:** `SDXL-Turbo` ili `SDXL-Base-1.0`
4. Ako želite da dodate više parametara, dodajte ih u tekstualno polje kao JSON. Na primer: `{ "steps": 4, "cfg_scale": 1 }`. Pogledajte dostupne parametre na [Generisanje slika (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Sačuvajte


#### Korak 2: Dozvolite generisanje slika za model
Ovaj korak osigurava da omogućite generisanje slika kao mogućnost za vaš model.
1. Idite na **Administratorska podešavanja → Modeli** (http://localhost:8080/admin/settings/models) i odaberite vaš model
2. Uključite `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Korak 3: Generišite sliku sa ekrana četa

1. Vratite se na čet na `http://localhost:8080`.
2. Izaberite **LLM za generisanje teksta** u padajućem meniju modela (primer: Qwen, Llama). **Nemojte birati Stable Diffusion model** jer je ovo selektor modela za čet.
3. U oblasti za poruke, kliknite na **Integracije** i uključite **Sliku**.
4. Koristite upit poput: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Slika se generiše i pojavljuje u četu.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Ovo potvrđuje da Open WebUI može da koordinira tok rada u „dva dela":
  - LLM pomaže u preciziranju upita
  - Slika se generiše putem Lemonade-ovog Images endpoint-a koristeći Stable Diffusion
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Aktivnost 3: Generišite sliku iz tekstualnog upita (Stable Diffusion)

Stable Diffusion modeli ne podržavaju generisanje teksta, oni samo generišu slike kroz Images API.

#### Korak 1: Konfigurišite generisanje slika u Open WebUI

1. U Lemonade GUI (`http://localhost:13305`), potražite `SDXL-Turbo` (brzo) ili `SDXL-Base-1.0` (viši kvalitet) i preuzmite ga.
2. Idite na **Administratorska podešavanja → Slike** (http://localhost:8080/admin/settings/images)
3. Podesite:
   - **Generisanje slika:** UKLJUČENO
   - **Engine za generisanje slika:** Podrazumevano (OpenAI)
   - **OpenAI API osnovna URL adresa:** `http://localhost:13305/api/v1`
   - **OpenAI API ključ:** `-`
   - **Model:** `SDXL-Turbo` ili `SDXL-Base-1.0`
4. Ako želite da dodate više parametara, dodajte ih u tekstualno polje kao JSON. Na primer: `{ "steps": 4, "cfg_scale": 1 }`. Pogledajte dostupne parametre na [Generisanje slika (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Sačuvajte


#### Korak 2: Dozvolite generisanje slika za model
Ovaj korak osigurava da omogućite generisanje slika kao mogućnost za vaš model.
1. Idite na **Administratorska podešavanja → Modeli** (http://localhost:8080/admin/settings/models) i odaberite vaš model
2. Uključite `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Korak 3: Generišite sliku sa ekrana četa

1. Vratite se na čet na `http://localhost:8080`.
2. Izaberite **LLM za generisanje teksta** u padajućem meniju modela (primer: Qwen, Llama). **Nemojte birati Stable Diffusion model** jer je ovo selektor modela za čet.
3. U oblasti za poruke, kliknite na **Integracije** i uključite **Sliku**.
4. Koristite upit poput: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Slika se generiše i pojavljuje u četu.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Ovo potvrđuje da Open WebUI može da koordinira tok rada u „dva dela":
  - LLM pomaže u preciziranju upita
  - Slika se generiše putem Lemonade-ovog Images endpoint-a koristeći Stable Diffusion
<!-- @device:end -->
<!-- @os:end -->

---

## Rešavanje problema

### „Nijedan model se ne prikazuje u Open WebUI"
- Prvo proverite Lemonade: otvorite `http://localhost:13305/api/v1/models` u pregledaču i potvrdite da su vaši modeli navedeni i preuzeti
- Zatim proverite vezu Open WebUI: idite na **Administratorska podešavanja → Veze** na `http://localhost:8080/admin/settings/connections` i proverite da li je osnovna URL adresa `http://localhost:13305/api/v1`

### Poruka o grešci „Ovaj model ne podržava dovršavanje četa"
- Izabrali ste model slike (SDXL-Turbo / SDXL-Base-1.0) u padajućem meniju modela za čet.
- **Rešenje**: izaberite LLM za čet, a koristite prekidač za slike i podešavanja slika za generisanje.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Greške/prekoračenja vremena pri generisanju slika
- Počnite sa `SDXL-Turbo` (brzo, manje koraka)
- Kada to proradí, prebacite model slike na `SDXL-Base-1.0` za kvalitet

---

## Sledeći koraci

Sada imate funkcionalan **„lokalni AI stek"** — jedan UI koji kontroliše više tipova modela kroz standardni API.

Evo tri proširenja koja otključavaju potpuno nove tokove rada:

### 1. Govor u tekst sa Whisper

Pokušajte da pretvorite zvuk u tekst koristeći Whisper model, a zatim ga prosledite LLM-u za sažimanje, akcione stavke ili prepisivanje. Ovo je osnova za beleške sa sastanaka i glasovne asistente.

### 2. Python kodiranje unutar Open WebUI

Koristite ugrađeno iskustvo izvršavanja koda u Open WebUI za pokretanje Python isečaka, pregled izlaza i brže iteracije — bez napuštanja korisničkog interfejsa. [Referenca](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. HTML renderovanje unutar Open WebUI

Renderujte HTML izlaze direktno u interfejsu. Ovo je iznenađujuće moćno za brzo pravljenje prototipova, formatiranih izveštaja i interaktivnih isečaka. [Referenca](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## Reference

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Dokumentacija Lemonade servera](https://lemonade-server.ai/docs)
- [Lemonade Server CLI](https://lemonade-server.ai/docs/lemonade-cli/)
- [Vodič za integraciju Lemonade ↔ Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Specifikacija Lemonade Server API-ja (endpoint-i)](https://lemonade-server.ai/docs/server/server_spec)
- [Video vodič (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [Video vodič (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)