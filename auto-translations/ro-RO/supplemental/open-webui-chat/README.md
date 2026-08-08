<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din limba engleză și nu a fost revizuită de o persoană. Aceasta poate conține erori, iar anumite instrucțiuni, comenzi, descărcări, disponibilitatea produselor sau alt conținut pot varia în funcție de limbă sau regiune. În cazul oricărei neconcordanțe sau discrepanțe, versiunea originală în limba engleză a playbook-ului prevalează.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Acest playbook necesită un minimum de **32GB** de memorie de sistem.
<!-- @device:end -->

## Prezentare generală

[Open WebUI](https://docs.openwebui.com) este o interfață auto-găzduită, bazată pe browser, care oferă o experiență familiară de tip chatbot, acționând în același timp ca frontend pentru unul sau mai multe servere de modele AI. În loc să fie legat de un singur furnizor, Open WebUI se poate conecta la **orice backend care expune un API compatibil OpenAI**, astfel încât puteți schimba modelele și capabilitățile fără a schimba interfața.

În acest playbook, folosim [**Lemonade**](https://lemonade-server.ai) ca backend deoarece expune un **endpoint unificat compatibil OpenAI** care acceptă mai multe modalități:
- **Modele de limbaj de mari dimensiuni (LLM)** pentru generarea de text
- **Modele de viziune** pentru înțelegerea imaginilor
- **Stable Diffusion** pentru generarea de imagini
- **Modele de transcriere audio** pentru conversia vorbirii în text

Această configurație vă permite să explorați **întregul flux de lucru multimodal, de la un capăt la altul**.

---

## Ce veți învăța

La final, veți putea:

- Conecta Open WebUI la un backend local compatibil OpenAI (Lemonade)
- Discuta cu un LLM local din browser
- Încărca o imagine și adresa întrebări despre ea unui model de viziune
- Genera imagini din prompturi text folosind modele Stable Diffusion (SDXL-Turbo / SDXL)
- Înțelege modelul mental, astfel încât să puteți folosi și alte backend-uri (Ollama, vLLM, llama.cpp server etc.)

---

## Concepte de bază (model mental)

### Cele trei componente

| Componentă | Ce face | Exemple |
|---|---|---|
| Frontend (UI) | Aplicația web cu care interacționați | Open WebUI |
| Backend (server de modele) | Găzduiește modelele și expune endpoint-uri HTTP | Lemonade, Ollama, vLLM, llama.cpp server, servere compatibile OpenAI |
| Modele | Modelele LLM / Viziune / Difuzie / Audio propriu-zise | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### De ce contează „API compatibil OpenAI”

Open WebUI este construit în jurul unor endpoint-uri standard de tip OpenAI, precum:
  - Chat: `/chat/completions`
  - Listă de modele: `/models`
  - Generare de imagini: `/images/generations`
  - Transcriere audio: `/audio/transcriptions`

Lemonade expune aceste endpoint-uri sub `http://localhost:13305/api/v1/...`

Dacă un backend acceptă acele endpoint-uri, Open WebUI poate comunica cu el cu o configurare minimă. De aceea putem schimba backend-urile fără a modifica fluxul de lucru.

#### Două servicii, două porturi

Pe parcursul acestui playbook veți lucra cu două servicii separate:

| Serviciu | URL | Ce faceți acolo |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | Răsfoiți, descărcați și gestionați modele |
| **Open WebUI** | `http://localhost:8080` | Discutați, încărcați imagini, generați imagini — interfața destinată utilizatorului |

Lemonade rulează modelele; Open WebUI este interfața cu care interacționați. Folosiți mai întâi interfața grafică Lemonade pentru a descărca modelele, apoi utilizați-le din Open WebUI.

---

## Configurarea memoriei

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificați actualizările de software

<!-- @require:software-update -->
<!-- @device:end -->

## Configurare inițială (o singură dată)

Acest playbook necesită Lemonade rulând ca backend și, pe Linux, un motor de containere (Podman) pentru a rula Open WebUI. Configurați acestea înainte de a instala Open WebUI.

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

## Descărcarea modelelor în Lemonade

Înainte de a instala Open WebUI, asigurați-vă că modelele pe care doriți să le utilizați sunt descărcate și gata de utilizare în Lemonade.

1. Deschideți interfața grafică Lemonade la `http://localhost:13305`.
2. Răsfoiți modelele disponibile și descărcați-le pe cele pe care doriți să le utilizați (de exemplu, un LLM pentru chat, un model de viziune și/sau un model Stable Diffusion pentru generarea de imagini).
3. Confirmați că API-ul este accesibil vizitând `http://localhost:13305/api/v1/models` în browser — ar trebui să vedeți listate modelele descărcate.

> Modelele trebuie descărcate în **Lemonade** (`localhost:13305`) înainte de a putea apărea în **Open WebUI** (`localhost:8080`). Dacă un model nu apare mai târziu în Open WebUI, reveniți aici și verificați mai întâi Lemonade.


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

## Instalarea Open WebUI

<!-- @os:windows -->
### 1. Instalați Python 3.12

Open WebUI necesită **Python 3.12** — nu se instalează pe Python 3.13+. Lansatorul Python pentru Windows (`py`) vă permite să instalați versiunea 3.12 în paralel cu orice versiune Python existentă, fără conflicte.

```powershell
winget install Python.Python.3.12
```

Închideți și redeschideți terminalul după instalare, apoi verificați:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Notă:** Sistemul dumneavoastră vine cu Python 3.13 preinstalat. Instalarea versiunii 3.12 nu îl afectează — `python` continuă să folosească 3.13, iar `py -3.12` vizează doar versiunea 3.12 atunci când aveți nevoie de ea.
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

### 2. Creați un mediu virtual și instalați Open WebUI

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
Vom folosi acum serviciul Podman pentru a containeriza instalarea noastră de Open WebUI.

Vă rugăm să descărcați următorul fișier într-un director la alegere: [compose.yml](assets/compose.yml)

În acel director, rulați următoarea comandă:

```bash
podman compose up -d
```

Aceasta descarcă imaginea Open WebUI și scrie în stocarea persistentă.

Lansați Open WebUI tastând `localhost:8080` în bara de adrese a browserului.

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

> **Sfat**: Open WebUI oferă și alte opțiuni de instalare pe [GitHub](https://github.com/open-webui/open-webui).
## Pornirea serverului Open WebUI

<!-- @os:windows -->
- Rulați următoarea comandă pentru a lansa serverul HTTP Open WebUI:
```bash
open-webui serve
```
<!-- @os:end -->

- Într-un browser, navigați la `http://localhost:8080`.
- Open WebUI vă va solicita să creați un cont local de administrator. Odată ce v-ați autentificat, veți vedea interfața de chat.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> Păstrați fereastra terminalului deschisă. Închiderea acesteia oprește Open WebUI.
<!-- @os:end -->

<!-- @os:linux -->
> Containerul rulează în fundal. Din directorul care conține `compose.yml`, gestionați-l cu `podman compose down` (oprire) și `podman compose up -d` (pornire). Conturile și setările dvs. persistă în volumul `open_webui_data`.
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

## Conectarea Open WebUI la Lemonade

Acum că ambele servicii rulează — Lemonade pe `localhost:13305` și Open WebUI pe `localhost:8080` — conectați-le astfel încât Open WebUI să poată utiliza modelele Lemonade.

În Open WebUI:

1. Faceți clic pe **pictograma de profil utilizator** din colțul din dreapta sus, apoi selectați **Settings**.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. În panoul Settings, faceți clic pe **Admin Settings** în colțul din stânga jos.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. În bara laterală Admin Settings, faceți clic pe **Connections** (sau navigați direct la `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. Sub **OpenAI API**, adăugați o conexiune nouă:
   - **Base URL:** `http://localhost:13305/api/v1`
   - **API Key:** `-` (o singură liniuță funcționează pentru local)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. Asigurați-vă că sub **"Manage OpenAI API Connections"**, este activată doar `http://localhost:13305/api/v1`. Dezactivați orice altă conexiune (de exemplu, cea implicită OpenAI).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. Faceți clic pe **Save**.

7. **(Recomandat)** Dezactivați funcțiile de generare automată pentru a menține Open WebUI receptiv cu LLM-uri locale. Accesați **Admin Settings → Settings → Interface** și dezactivați:
   - Title Generation
   - Follow Up Generation
   - Tags Generation

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. Faceți clic pe **Save**, apoi reveniți la `http://localhost:8080`.
9. Faceți clic pe meniul derulant al modelelor — ar trebui să vedeți modelele pe care le-ați descărcat din Lemonade.

---

## Activități principale

Acum totul este configurat. Să analizăm trei lucruri interesante de făcut.

---

### Activitatea 1: Discutați cu un LLM local
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Faceți clic pe meniul derulant din partea stângă sus a interfeței. Acesta va afișa modelele Lemonade pe care le-ați instalat. Selectați unul pentru a continua. (exemplu: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. Introduceți un mesaj pentru LLM și faceți clic pe trimitere (sau apăsați Enter). LLM-ul va avea nevoie de câteva secunde pentru a se încărca în memorie, apoi veți vedea răspunsul apărând treptat.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Faceți clic pe meniul derulant din partea stângă sus a interfeței. Acesta va afișa modelele Lemonade pe care le-ați instalat. Selectați unul pentru a continua. (exemplu: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Introduceți un mesaj pentru LLM și faceți clic pe trimitere (sau apăsați Enter). LLM-ul va avea nevoie de câteva secunde pentru a se încărca în memorie, apoi veți vedea răspunsul apărând treptat.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. Modelul va răspunde în chat.

4. În acest moment, deschideți `Task Manager` pe sistemul dvs. Veți vedea o **utilizare ridicată a GPU sau NPU** în funcție de faptul dacă modelul selectat este **Hybrid** sau **NPU**. Folosind managerul de sarcini, puteți confirma că rulați modelul local.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Faceți clic pe meniul derulant din partea stângă sus a interfeței. Acesta va afișa modelele Lemonade pe care le-ați instalat. Selectați unul pentru a continua. (exemplu: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Introduceți un mesaj pentru LLM și faceți clic pe trimitere (sau apăsați Enter). LLM-ul va avea nevoie de câteva secunde pentru a se încărca în memorie, apoi veți vedea răspunsul apărând treptat.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. Modelul va răspunde în chat.
<!-- @os:end -->

Aceasta validează faptul că Open WebUI poate trimite solicitări către Lemonade folosind punctul final de chat compatibil cu OpenAI.

---

### Activitatea 2: Încărcați o imagine și puneți întrebări (Vision)

Acest lucru necesită un model care acceptă intrare de imagine (un model Vision sau Multimodal).

1. Faceți clic pe pictograma de filtrare, selectați „By Category", apoi alegeți un model din secțiunea **Vision** (de exemplu, `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. Faceți clic pe butonul **`+`** din caseta de mesaje și încărcați o imagine
3. Puneți o întrebare care necesită o înțelegere reală a imaginii: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. Modelul răspunde pe baza conținutului imaginii, nu cu text generic.

Aceasta demonstrează că Open WebUI poate trimite solicitări multimodale (text + imagine) prin intermediul backend-ului (Lemonade) către un model de tip vision.

---

<!-- @os:windows -->
### Activitatea 3: Generați o imagine dintr-un prompt text (Stable Diffusion)

Modelele Stable Diffusion nu acceptă generarea de text, ele generează doar imagini prin intermediul API-ului Images.

#### Pasul 1: Configurați generarea de imagini în Open WebUI

1. În interfața grafică Lemonade (`http://localhost:13305`), căutați `SDXL-Turbo` (rapid) sau `SDXL-Base-1.0` (calitate superioară) și descărcați-l.
2. Accesați **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Setați:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` sau `SDXL-Base-1.0`
4. Dacă doriți să adăugați mai mulți parametri, adăugați-i în câmpul de text sub formă de JSON. De exemplu: `{ "steps": 4, "cfg_scale": 1 }`. Consultați parametrii disponibili la [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Salvați
#### Pasul 2: Permiteți Generarea de Imagini pentru model
Acest pas asigură activarea Generării de Imagini ca o capabilitate a modelului dvs.
1. Accesați **Admin Settings → Models** (http://localhost:8080/admin/settings/models) și alegeți modelul dvs.
2. Activați `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Pasul 3: Generați o imagine din ecranul de chat

1. Reveniți la chat la `http://localhost:8080`.
2. Selectați un **LLM de Generare de Text** din meniul derulant de modele (exemplu: Qwen, Llama). **Nu selectați un model Stable Diffusion**, deoarece acesta este un selector de model pentru chat.
3. În zona de mesaje, faceți clic pe **Integrations** și comutați **Image** pe ON.
4. Folosiți un prompt precum: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. O imagine este generată și apare în chat.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Acest lucru demonstrează că Open WebUI poate coordona un flux de lucru „în două părți”:
  - LLM-ul ajută la rafinarea prompt-ului
  - Imaginea este generată prin endpoint-ul Images al Lemonade, folosind Stable Diffusion
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Activitatea 3: Generați o Imagine dintr-un Prompt de Text (Stable Diffusion)

Modelele Stable Diffusion nu suportă generarea de text, ele generează imagini doar prin API-ul Images.

#### Pasul 1: Configurați Generarea de Imagini în Open WebUI

1. În interfața grafică Lemonade (`http://localhost:13305`), căutați `SDXL-Turbo` (rapid) sau `SDXL-Base-1.0` (calitate superioară) și descărcați-l.
2. Accesați **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Setați:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` sau `SDXL-Base-1.0`
4. Dacă doriți să adăugați mai mulți parametri, adăugați-i în câmpul de text sub formă de JSON. De exemplu: `{ "steps": 4, "cfg_scale": 1 }`. Consultați parametrii disponibili la [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Salvați


#### Pasul 2: Permiteți Generarea de Imagini pentru model
Acest pas asigură activarea Generării de Imagini ca o capabilitate a modelului dvs.
1. Accesați **Admin Settings → Models** (http://localhost:8080/admin/settings/models) și alegeți modelul dvs.
2. Activați `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Pasul 3: Generați o imagine din ecranul de chat

1. Reveniți la chat la `http://localhost:8080`.
2. Selectați un **LLM de Generare de Text** din meniul derulant de modele (exemplu: Qwen, Llama). **Nu selectați un model Stable Diffusion**, deoarece acesta este un selector de model pentru chat.
3. În zona de mesaje, faceți clic pe **Integrations** și comutați **Image** pe ON.
4. Folosiți un prompt precum: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. O imagine este generată și apare în chat.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Acest lucru demonstrează că Open WebUI poate coordona un flux de lucru „în două părți”:
  - LLM-ul ajută la rafinarea prompt-ului
  - Imaginea este generată prin endpoint-ul Images al Lemonade, folosind Stable Diffusion
<!-- @device:end -->
<!-- @os:end -->

---

## Depanare

### „Niciun model nu apare în Open WebUI"
- Mai întâi, verificați Lemonade: deschideți `http://localhost:13305/api/v1/models` într-un browser și confirmați că modelele dvs. sunt listate și descărcate
- Apoi, verificați conexiunea Open WebUI: accesați **Admin Settings → Connections** la `http://localhost:8080/admin/settings/connections` și verificați că Base URL este `http://localhost:13305/api/v1`

### Mesajul de eroare „This model does not support chat completion"
- Ați selectat un model de imagine (SDXL-Turbo / SDXL-Base-1.0) în meniul derulant de model pentru chat.
- **Soluție**: selectați un LLM pentru chat și folosiți comutatorul Image + setările Images pentru generare.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Erori/timeout-uri la generarea de imagini
- Începeți mai întâi cu `SDXL-Turbo` (rapid, mai puțini pași)
- Odată ce funcționează, treceți modelul de imagine la `SDXL-Base-1.0` pentru calitate

---

## Pași următori

Aveți acum o stivă locală de AI funcțională, o singură interfață care controlează mai multe tipuri de modele printr-un API standard.

Iată trei extinderi care deblochează fluxuri de lucru complet noi:

### 1. Conversie Vorbire-în-Text cu Whisper

Încercați să transformați audio în text folosind un model Whisper, apoi introduceți-l într-un LLM pentru rezumare, elemente de acțiune sau rescriere. Aceasta este fundația pentru notițe de întâlniri și asistenți controlați prin voce.

### 2. Programare Python în Open WebUI

Folosiți experiența integrată de execuție de cod din Open WebUI pentru a rula fragmente Python, a inspecta rezultatele și a itera mai rapid—fără a părăsi interfața. [Referință](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. Randare HTML în Open WebUI

Randați rezultate HTML direct în interfață. Acest lucru este surprinzător de puternic pentru construirea de prototipuri rapide, rapoarte formatate și fragmente interactive. [Referință](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## Referințe

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Documentația Lemonade Server](https://lemonade-server.ai/docs)
- [CLI Lemonade Server](https://lemonade-server.ai/docs/lemonade-cli/)
- [Ghid de integrare Lemonade ↔ Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Specificația API Lemonade Server (endpoint-uri)](https://lemonade-server.ai/docs/server/server_spec)
- [Prezentare video (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [Prezentare video (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)

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