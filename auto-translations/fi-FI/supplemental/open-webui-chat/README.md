<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Tämä playbook käyttää erityisiä tageja, joita GitHub ei pysty renderöimään. Katso sisältö oikein osoitteessa [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Tämä playbook vaatii vähintään **32 Gt** järjestelmämuistia.
<!-- @device:end -->

## Yleiskatsaus

[Open WebUI](https://docs.openwebui.com) on itse isännöity, selainpohjainen käyttöliittymä, joka tarjoaa tutun chatbot-kokemuksen toimien samalla yhden tai useamman tekoälymallipalvelimen käyttöliittymänä. Sen sijaan että olisit sidottu yhteen palveluntarjoajaan, Open WebUI voi muodostaa yhteyden **mihin tahansa taustajärjestelmään, joka tarjoaa OpenAI-yhteensopivan API:n**, joten voit vaihtaa malleja ja ominaisuuksia ilman käyttöliittymän vaihtamista.

Tässä playbookissa käytämme [**Lemonade**](https://lemonade-server.ai)-palvelua taustajärjestelmänä, koska se tarjoaa **yhtenäisen OpenAI-yhteensopivan päätepisteen**, joka tukee useita modaliteetteja:
- **Suuret kielimallit (LLM)** tekstin tuottamiseen
- **Näkömallit** kuvien ymmärtämiseen
- **Stable Diffusion** kuvien luomiseen
- **Äänen transkriptiomallit** puheesta tekstiksi -muunnokseen

Tämä kokoonpano mahdollistaa **täydellisen multimodaalisen työnkulun tutkimisen alusta loppuun**.

---

## Mitä opit

Tämän jälkeen osaat:

- Yhdistää Open WebUI:n paikalliseen OpenAI-yhteensopivaan taustajärjestelmään (Lemonade)
- Keskustella paikallisen LLM:n kanssa selaimestasi
- Ladata kuvan ja esittää näkömallille kysymyksiä siitä
- Luoda kuvia tekstikehotteista Stable Diffusion -mallien avulla (SDXL-Turbo / SDXL)
- Ymmärtää toimintamallin, jotta voit käyttää muita taustajärjestelmiä (Ollama, vLLM, llama.cpp server jne.)

---

## Peruskäsitteet (toimintamalli)

### Kolme komponenttia

| Osa | Mitä se tekee | Esimerkkejä |
|---|---|---|
| Käyttöliittymä (UI) | Verkkosovellus, jonka kanssa olet vuorovaikutuksessa | Open WebUI |
| Taustajärjestelmä (mallipalvelin) | Isännöi malleja ja tarjoaa HTTP-päätepisteitä | Lemonade, Ollama, vLLM, llama.cpp server, OpenAI-yhteensopivat palvelimet |
| Mallit | Varsinaiset LLM / näkö / diffuusio / ääni -mallit | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### Miksi "OpenAI-yhteensopiva API" on tärkeä

Open WebUI on rakennettu standardien OpenAI-tyylisten päätepisteiden ympärille, kuten:
  - Chat: `/chat/completions`
  - Mallilista: `/models`
  - Kuvien luominen: `/images/generations`
  - Äänen transkriptio: `/audio/transcriptions`

Lemonade tarjoaa nämä osoitteessa `http://localhost:13305/api/v1/...`

Jos taustajärjestelmä tukee näitä päätepisteitä, Open WebUI voi kommunikoida sen kanssa minimaalisella konfiguroinnilla. Siksi voimme vaihtaa taustajärjestelmiä muuttamatta työnkulkuamme.

#### Kaksi palvelua, kaksi porttia

Tässä playbookissa työskentelet kahden erillisen palvelun kanssa:

| Palvelu | URL | Mitä teet siellä |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | Selaa, lataa ja hallinnoi malleja |
| **Open WebUI** | `http://localhost:8080` | Chattaile, lataa kuvia, luo kuvia — käyttäjälle näkyvä käyttöliittymä |

Lemonade ajaa malleja; Open WebUI on käyttöliittymä, jonka kanssa olet vuorovaikutuksessa. Käytä Lemonade GUI:ta mallien lataamiseen ensin, ja käytä niitä sitten Open WebUI:sta.

---

## Muistikonfiguraation asettaminen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset

<!-- @require:software-update -->
<!-- @device:end -->

## Kertaluonteinen asennus

Tämä playbook tarvitsee Lemonade-palvelun käynnissä taustajärjestelmänä ja Linuxilla konttimoottori (Podman) Open WebUI:n ajamiseen. Asenna nämä ennen Open WebUI:n asentamista.

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

## Mallien lataaminen Lemonadessa

Ennen Open WebUI:n asentamista varmista, että haluamasi mallit on ladattu ja valmiina Lemonadessa.

1. Avaa Lemonade GUI osoitteessa `http://localhost:13305`.
2. Selaa saatavilla olevia malleja ja lataa haluamasi (esim. LLM chattailua varten, näkömalli ja/tai Stable Diffusion -malli kuvien luomiseen).
3. Varmista, että API on saavutettavissa käymällä osoitteessa `http://localhost:13305/api/v1/models` selaimessasi — sinun pitäisi nähdä ladatut mallisi listattuna.

> Mallit täytyy ladata **Lemonadessa** (`localhost:13305`) ennen kuin ne voivat näkyä **Open WebUI:ssa** (`localhost:8080`). Jos malli ei myöhemmin näy Open WebUI:ssa, palaa tähän ja tarkista Lemonade ensin.


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

## Open WebUI:n asentaminen

<!-- @os:windows -->
### 1. Asenna Python 3.12

Open WebUI vaatii **Python 3.12:n** — se ei asennu Python 3.13+:lle. Windowsin Python Launcher (`py`) mahdollistaa 3.12:n asentamisen rinnakkain minkä tahansa olemassa olevan Python-version kanssa ilman ristiriitoja.

```powershell
winget install Python.Python.3.12
```

Sulje ja avaa terminaali uudelleen asennuksen jälkeen, ja tarkista:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Huomio:** Järjestelmässäsi on valmiiksi asennettuna Python 3.13. 3.12:n asentaminen ei vaikuta siihen — `python` käyttää edelleen 3.13:a, ja `py -3.12` kohdistuu 3.12:een vain tarvittaessa.
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

### 2. Luo virtuaaliympäristö ja asenna Open WebUI

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
Käytämme nyt Podman-palvelua Open WebUI -asennuksemme kontittamiseen.

Lataa seuraava valitsemaasi hakemistoon: [compose.yml](assets/compose.yml)

Suorita kyseisessä hakemistossa seuraava komento:

```bash
podman compose up -d
```

Tämä hakee Open WebUI -imagen ja kirjoittaa pysyvään tallennustilaan.

Käynnistä Open WebUI kirjoittamalla `localhost:8080` selaimen osoitepalkkiin.

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

> **Vinkki**: Open WebUI tarjoaa myös muita asennusvaihtoehtoja [GitHub](https://github.com/open-webui/open-webui)-sivullaan.

## Open WebUI -palvelimen käynnistäminen

<!-- @os:windows -->
- Suorita seuraava komento käynnistääksesi Open WebUI HTTP -palvelimen:
```bash
open-webui serve
```
<!-- @os:end -->

- Siirry selaimessa osoitteeseen `http://localhost:8080`.
- Open WebUI pyytää sinua luomaan paikallisen järjestelmänvalvojan tilin. Kun olet kirjautunut sisään, näet chat-käyttöliittymän.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> Pidä terminaali-ikkuna auki. Sen sulkeminen pysäyttää Open WebUI:n.
<!-- @os:end -->

<!-- @os:linux -->
> Kontti toimii taustalla. Hallinnoi sitä `compose.yml`-tiedoston sisältävästä hakemistosta komennoilla `podman compose down` (pysäytä) ja `podman compose up -d` (käynnistä). Tilisi ja asetuksesi säilyvät `open_webui_data`-volyymissa.
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

## Open WebUI:n yhdistäminen Lemonadeen

Nyt kun molemmat palvelut ovat käynnissä — Lemonade osoitteessa `localhost:13305` ja Open WebUI osoitteessa `localhost:8080` — yhdistä ne, jotta Open WebUI voi käyttää Lemonade-malleja.

Open WebUI:ssa:

1. Napsauta **käyttäjäprofiili-kuvaketta** oikeassa yläkulmassa ja valitse **Asetukset**.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. Napsauta Asetukset-paneelissa **Järjestelmänvalvojan asetukset** vasemmassa alakulmassa.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. Napsauta Järjestelmänvalvojan asetukset -sivupalkissa **Yhteydet** (tai siirry suoraan osoitteeseen `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. Lisää **OpenAI API** -kohdassa uusi yhteys:
   - **Perus-URL:** `http://localhost:13305/api/v1`
   - **API-avain:** `-` (yksittäinen viiva toimii paikallisesti)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. Varmista, että **"Hallinnoi OpenAI API -yhteyksiä"** -kohdassa on käytössä vain `http://localhost:13305/api/v1`. Poista muut yhteydet käytöstä (esim. oletusarvoinen OpenAI-yhteys).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. Napsauta **Tallenna**.

7. **(Suositeltavaa)** Poista automaattiset luontiominaisuudet käytöstä pitääksesi Open WebUI:n responsiivisena paikallisten LLM:ien kanssa. Siirry kohtaan **Järjestelmänvalvojan asetukset → Asetukset → Käyttöliittymä** ja poista käytöstä:
   - Otsikon luominen
   - Jatkokysymysten luominen
   - Tagien luominen

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. Napsauta **Tallenna** ja palaa sitten osoitteeseen `http://localhost:8080`.
9. Napsauta mallin pudotusvalikkoa — sinun pitäisi nähdä Lemonadesta lataamasi mallit.

---

## Pääaktiviteetit

Nyt olet valmis. Katsotaan kolmea mielenkiintoista asiaa, joita voit tehdä.

---

### Aktiviteetti 1: Chattaile paikallisen LLM:n kanssa
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Napsauta käyttöliittymän vasemmassa yläkulmassa olevaa pudotusvalikkoa. Tämä näyttää asentamasi Lemonade-mallit. Valitse yksi jatkaaksesi. (esimerkki: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. Kirjoita viesti LLM:lle ja napsauta lähetä (tai paina Enter). LLM latautuu muistiin muutamassa sekunnissa, minkä jälkeen näet vastauksen virtaavan näytölle.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Napsauta käyttöliittymän vasemmassa yläkulmassa olevaa pudotusvalikkoa. Tämä näyttää asentamasi Lemonade-mallit. Valitse yksi jatkaaksesi. (esimerkki: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Kirjoita viesti LLM:lle ja napsauta lähetä (tai paina Enter). LLM latautuu muistiin muutamassa sekunnissa, minkä jälkeen näet vastauksen virtaavan näytölle.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. Malli vastaa chatissa.

4. Avaa tässä vaiheessa järjestelmässäsi `Tehtävienhallinta`. Näet **korkean GPU- tai NPU-käyttöasteen** sen mukaan, onko valitsemasi malli **Hybrid** vai **NPU**. Tehtävienhallinnan avulla voit varmistaa, että ajat mallia paikallisesti.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Napsauta käyttöliittymän vasemmassa yläkulmassa olevaa pudotusvalikkoa. Tämä näyttää asentamasi Lemonade-mallit. Valitse yksi jatkaaksesi. (esimerkki: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Kirjoita viesti LLM:lle ja napsauta lähetä (tai paina Enter). LLM latautuu muistiin muutamassa sekunnissa, minkä jälkeen näet vastauksen virtaavan näytölle.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. Malli vastaa chatissa.
<!-- @os:end -->

Tämä vahvistaa, että Open WebUI voi lähettää pyyntöjä Lemonadelle käyttäen OpenAI-yhteensopivaa chat-päätepistettä.

---

### Aktiviteetti 2: Lataa kuva ja esitä kysymyksiä (näkö)

Tämä vaatii mallin, joka tukee kuvasyötettä (näkö- tai multimodaalinen malli).

1. Napsauta suodatinkuvaketta, valitse "Kategorian mukaan" ja valitse sitten malli **Näkö**-osiosta (esim. `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. Napsauta viestiruudun **`+`**-painiketta ja lataa kuva
3. Esitä kysymys, joka edellyttää todellista kuvan ymmärtämistä: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. Malli vastaa kuvan sisällön perusteella, ei yleisen tekstin perusteella.

Tämä osoittaa, että Open WebUI voi lähettää multimodaalisia pyyntöjä (teksti + kuva) taustajärjestelmän (Lemonade) kautta näkömallille.

---

<!-- @os:windows -->
### Aktiviteetti 3: Luo kuva tekstikehotteesta (Stable Diffusion)

Stable Diffusion -mallit eivät tue tekstin luomista, ne luovat kuvia vain Images API:n kautta.

#### Vaihe 1: Konfiguroi kuvien luominen Open WebUI:ssa

1. Etsi Lemonade GUI:sta (`http://localhost:13305`) `SDXL-Turbo` (nopea) tai `SDXL-Base-1.0` (parempi laatu) ja lataa se.
2. Siirry kohtaan **Järjestelmänvalvojan asetukset → Kuvat** (http://localhost:8080/admin/settings/images)
3. Aseta:
   - **Kuvien luominen:** PÄÄLLÄ
   - **Kuvien luontimoottori:** Oletus (OpenAI)
   - **OpenAI API:n perus-URL:** `http://localhost:13305/api/v1`
   - **OpenAI API-avain:** `-`
   - **Malli:** `SDXL-Turbo` tai `SDXL-Base-1.0`
4. Jos haluat lisätä lisäparametreja, lisää ne tekstikenttään JSON-muodossa. Esimerkiksi: `{ "steps": 4, "cfg_scale": 1 }`. Katso saatavilla olevat parametrit osoitteesta [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Tallenna


#### Vaihe 2: Salli kuvien luominen mallille
Tämä vaihe varmistaa, että otat kuvien luomisen käyttöön mallisi ominaisuutena.
1. Siirry kohtaan **Järjestelmänvalvojan asetukset → Mallit** (http://localhost:8080/admin/settings/models) ja valitse mallisi
2. Ota käyttöön `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Vaihe 3: Luo kuva chat-näytöltä

1. Palaa chattiin osoitteessa `http://localhost:8080`.
2. Valitse **tekstin luomiseen tarkoitettu LLM** mallin pudotusvalikosta (esimerkki: Qwen, Llama). **Älä valitse Stable Diffusion -mallia**, sillä tämä on chat-mallin valitsin.
3. Napsauta viestiruudussa **Integraatiot** ja kytke **Kuva** PÄÄLLE.
4. Käytä kehotetta kuten: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Kuva luodaan ja se näkyy chatissa.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Tämä osoittaa, että Open WebUI voi koordinoida "kaksivaiheisen" työnkulun:
  - LLM auttaa tarkentamaan kehotteen
  - Kuva luodaan Lemonade-palvelun Images-päätepisteen kautta Stable Diffusion -mallilla
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Aktiviteetti 3: Luo kuva tekstikehotteesta (Stable Diffusion)

Stable Diffusion -mallit eivät tue tekstin luomista, ne luovat kuvia vain Images API:n kautta.

#### Vaihe 1: Konfiguroi kuvien luominen Open WebUI:ssa

1. Etsi Lemonade GUI:sta (`http://localhost:13305`) `SDXL-Turbo` (nopea) tai `SDXL-Base-1.0` (parempi laatu) ja lataa se.
2. Siirry kohtaan **Järjestelmänvalvojan asetukset → Kuvat** (http://localhost:8080/admin/settings/images)
3. Aseta:
   - **Kuvien luominen:** PÄÄLLÄ
   - **Kuvien luontimoottori:** Oletus (OpenAI)
   - **OpenAI API:n perus-URL:** `http://localhost:13305/api/v1`
   - **OpenAI API-avain:** `-`
   - **Malli:** `SDXL-Turbo` tai `SDXL-Base-1.0`
4. Jos haluat lisätä lisäparametreja, lisää ne tekstikenttään JSON-muodossa. Esimerkiksi: `{ "steps": 4, "cfg_scale": 1 }`. Katso saatavilla olevat parametrit osoitteesta [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Tallenna


#### Vaihe 2: Salli kuvien luominen mallille
Tämä vaihe varmistaa, että otat kuvien luomisen käyttöön mallisi ominaisuutena.
1. Siirry kohtaan **Järjestelmänvalvojan asetukset → Mallit** (http://localhost:8080/admin/settings/models) ja valitse mallisi
2. Ota käyttöön `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Vaihe 3: Luo kuva chat-näytöltä

1. Palaa chattiin osoitteessa `http://localhost:8080`.
2. Valitse **tekstin luomiseen tarkoitettu LLM** mallin pudotusvalikosta (esimerkki: Qwen, Llama). **Älä valitse Stable Diffusion -mallia**, sillä tämä on chat-mallin valitsin.
3. Napsauta viestiruudussa **Integraatiot** ja kytke **Kuva** PÄÄLLE.
4. Käytä kehotetta kuten: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Kuva luodaan ja se näkyy chatissa.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Tämä osoittaa, että Open WebUI voi koordinoida "kaksivaiheisen" työnkulun:
  - LLM auttaa tarkentamaan kehotteen
  - Kuva luodaan Lemonade-palvelun Images-päätepisteen kautta Stable Diffusion -mallilla
<!-- @device:end -->
<!-- @os:end -->

---

## Vianmääritys

### "Malleja ei näy Open WebUI:ssa"
- Tarkista ensin Lemonade: avaa `http://localhost:13305/api/v1/models` selaimessa ja varmista, että mallisi on listattu ja ladattu
- Tarkista sitten Open WebUI -yhteys: siirry kohtaan **Järjestelmänvalvojan asetukset → Yhteydet** osoitteessa `http://localhost:8080/admin/settings/connections` ja varmista, että perus-URL on `http://localhost:13305/api/v1`

### "This model does not support chat completion" -virheilmoitus
- Valitsit kuvamallin (SDXL-Turbo / SDXL-Base-1.0) chat-mallin pudotusvalikosta.
- **Korjaus**: valitse LLM chattailua varten ja käytä Kuva-kytkintä sekä Kuvat-asetuksia luomiseen.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Kuvien luomisen virheet/aikakatkaisut
- Aloita ensin `SDXL-Turbo`-mallilla (nopea, vähemmän vaiheita)
- Kun se toimii, vaihda kuvamalliksi `SDXL-Base-1.0` laadun parantamiseksi

---

## Seuraavat vaiheet

Sinulla on nyt toimiva **"paikallinen tekoälypino"** — yksi käyttöliittymä, joka ohjaa useita mallityyppejä standardin API:n kautta.

Tässä kolme laajennusta, jotka avaavat täysin uusia työnkulkuja:

### 1. Puheesta tekstiksi Whisper-mallilla

Kokeile äänen muuntamista tekstiksi Whisper-mallilla ja syötä se sitten LLM:lle tiivistämistä, toimintakohtien tunnistamista tai uudelleenkirjoittamista varten. Tämä on kokousmuistiinpanojen ja ääniohjattujen assistenttien perusta.

### 2. Python-koodaus Open WebUI:ssa

Käytä Open WebUI:n sisäänrakennettua koodin suoritusominaisuutta Python-katkelmien ajamiseen, tulosten tarkistamiseen ja nopeampaan iterointiin — poistumatta käyttöliittymästä. [Viite](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. HTML-renderöinti Open WebUI:ssa

Renderöi HTML-tulosteet suoraan käyttöliittymässä. Tämä on yllättävän tehokas tapa rakent