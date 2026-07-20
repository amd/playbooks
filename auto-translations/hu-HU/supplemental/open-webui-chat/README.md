<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ez a playbook olyan speciális címkéket használ, amelyeket a GitHub nem tud megjeleníteni. Az oldal helyes előnézetéhez látogasson el a [amd.com/playbooks](https://amd.com/playbooks) oldalra.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ez a playbook legalább **32 GB** rendszermemóriát igényel.
<!-- @device:end -->

## Áttekintés

Az [Open WebUI](https://docs.openwebui.com) egy önállóan üzemeltethető, böngészőalapú felület, amely ismerős chatbot élményt nyújt, miközben egy vagy több AI modellszerver frontendjeként működik. Ahelyett, hogy egyetlen szolgáltatóhoz lenne kötve, az Open WebUI **bármilyen, OpenAI-kompatibilis API-t biztosító háttérrendszerhez** képes csatlakozni, így modelleket és funkciókat válthat anélkül, hogy felületet kellene váltania.

Ebben a playbookban a [**Lemonade**](https://lemonade-server.ai) szolgáltatást használjuk háttérrendszerként, mivel az egy **egységes, OpenAI-kompatibilis végpontot** biztosít, amely több modalitást is támogat:
- **Nagy nyelvi modellek (LLM-ek)** szöveggeneráláshoz
- **Vizuális modellek** képértelmezéshez
- **Stable Diffusion** képgeneráláshoz
- **Hangátírási modellek** beszéd szöveggé alakításához

Ez a beállítás lehetővé teszi, hogy **végigjárja a teljes multimodális munkafolyamatot**.

---

## Amit tanulni fog

A végére képes lesz:

- Az Open WebUI csatlakoztatására egy helyi, OpenAI-kompatibilis háttérrendszerhez (Lemonade)
- Csevegésre egy helyi LLM-mel a böngészőjéből
- Kép feltöltésére és kérdések feltevésére egy vizuális modellnek a képpel kapcsolatban
- Képek generálására szöveges promptokból Stable Diffusion modellek (SDXL-Turbo / SDXL) segítségével
- A gondolkodási modell megértésére, hogy más háttérrendszereket is használhasson (Ollama, vLLM, llama.cpp server stb.)

---

## Alapfogalmak (gondolkodási modell)

### A három összetevő

| Elem | Mit csinál | Példák |
|---|---|---|
| Frontend (felhasználói felület) | A webalkalmazás, amellyel interakcióba lép | Open WebUI |
| Backend (modellszerver) | Modelleket hostol és HTTP végpontokat biztosít | Lemonade, Ollama, vLLM, llama.cpp server, OpenAI-kompatibilis szerverek |
| Modellek | A tényleges LLM / vizuális / diffúziós / hang modellek | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### Miért számít az „OpenAI-kompatibilis API”

Az Open WebUI szabványos OpenAI-stílusú végpontokra épül, például:
  - Csevegés: `/chat/completions`
  - Modelllista: `/models`
  - Képgenerálás: `/images/generations`
  - Hangátírás: `/audio/transcriptions`

A Lemonade ezeket a `http://localhost:13305/api/v1/...` alatt teszi elérhetővé.

Ha egy háttérrendszer támogatja ezeket a végpontokat, az Open WebUI minimális beállítással tud kommunikálni vele. Ezért tudunk háttérrendszert váltani a munkafolyamat módosítása nélkül.

#### Két szolgáltatás, két port

Ebben a playbookban két különálló szolgáltatással fog dolgozni:

| Szolgáltatás | URL | Mit csinál ott |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | Modellek böngészése, letöltése és kezelése |
| **Open WebUI** | `http://localhost:8080` | Csevegés, képek feltöltése, képek generálása — a felhasználó felé néző felület |

A Lemonade futtatja a modelleket; az Open WebUI az a felület, amellyel Ön interakcióba lép. Először a Lemonade GUI-t használja a modellek letöltéséhez, majd ezeket az Open WebUI-ból használja.

---

## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->

## Egyszeri beállítás

Ehhez a playbookhoz szükséges a Lemonade háttérrendszerként való futtatása, valamint Linux esetén egy konténermotor (Podman) az Open WebUI futtatásához. Ezeket állítsa be, mielőtt telepítené az Open WebUI-t.

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

## Modellek letöltése a Lemonade-ben

Az Open WebUI telepítése előtt győződjön meg arról, hogy a használni kívánt modellek le vannak töltve és készen állnak a Lemonade-ben.

1. Nyissa meg a Lemonade GUI-t a `http://localhost:13305` címen.
2. Böngéssze az elérhető modelleket, és töltse le azokat, amelyeket használni szeretne (pl. egy LLM-et csevegéshez, egy vizuális modellt, és/vagy egy Stable Diffusion modellt képgeneráláshoz).
3. Ellenőrizze, hogy az API elérhető-e a `http://localhost:13305/api/v1/models` böngészőben történő megnyitásával — ekkor meg kell jelennie a letöltött modellek listájának.

> A modelleket a **Lemonade**-ben (`localhost:13305`) kell letölteni, mielőtt megjelennének az **Open WebUI**-ban (`localhost:8080`). Ha később egy modell nem jelenik meg az Open WebUI-ban, először itt, a Lemonade-nél ellenőrizze.


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

## Az Open WebUI telepítése

<!-- @os:windows -->
### 1. Telepítse a Python 3.12-t

Az Open WebUI-hoz **Python 3.12** szükséges — Python 3.13+ verzión nem telepíthető. A Windows Python Launcher (`py`) lehetővé teszi a 3.12 telepítését a már meglévő Python verzió mellett, konfliktusok nélkül.

```powershell
winget install Python.Python.3.12
```

Telepítés után zárja be, majd nyissa meg újra a terminált, majd ellenőrizze:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Megjegyzés:** A rendszerén előre telepített Python 3.13 található. A 3.12 telepítése ezt nem érinti — a `python` továbbra is a 3.13-at használja, a `py -3.12` pedig csak akkor célozza meg a 3.12-t, amikor szüksége van rá.
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

### 2. Hozzon létre egy virtuális környezetet és telepítse az Open WebUI-t

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
Most a Podman szolgáltatást fogjuk használni az Open WebUI telepítésének konténerizálásához.

Kérjük, töltse le a következőt egy tetszőleges könyvtárba: [compose.yml](assets/compose.yml)

Ebben a könyvtárban futtassa a következő parancsot:

```bash
podman compose up -d
```

Ez letölti az Open WebUI image-et, és a tartós tárolóba írja.

Indítsa el az Open WebUI-t a `localhost:8080` böngésző címsorába való beírásával.

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

> **Tipp**: Az Open WebUI további telepítési lehetőségeket is biztosít a [GitHub](https://github.com/open-webui/open-webui) oldalán.
## Open WebUI Szerver Indítása

<!-- @os:windows -->
- Futtassa a következő parancsot az Open WebUI HTTP szerver elindításához:
```bash
open-webui serve
```
<!-- @os:end -->

- Böngészőben nyissa meg a következő címet: `http://localhost:8080`.
- Az Open WebUI kérni fogja, hogy hozzon létre egy helyi rendszergazdai fiókot. Miután bejelentkezett, megjelenik a csevegési felület.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> Hagyja nyitva a terminálablakot. Ha bezárja, az Open WebUI leáll.
<!-- @os:end -->

<!-- @os:linux -->
> A konténer a háttérben fut. A `compose.yml` fájlt tartalmazó könyvtárból a `podman compose down` (leállítás) és a `podman compose up -d` (indítás) parancsokkal kezelheti. A fiókjai és beállításai az `open_webui_data` kötetben maradnak meg.
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

## Az Open WebUI Csatlakoztatása a Lemonade-hoz

Most, hogy mindkét szolgáltatás fut — a Lemonade a `localhost:13305`, az Open WebUI pedig a `localhost:8080` címen —, kösse össze őket, hogy az Open WebUI használhassa a Lemonade modelljeit.

Az Open WebUI-ban:

1. Kattintson a **felhasználói profil ikonra** a jobb felső sarokban, majd válassza a **Settings** lehetőséget.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. A Settings panelen kattintson az **Admin Settings** lehetőségre a bal alsó sarokban.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. Az Admin Settings oldalsávban kattintson a **Connections** lehetőségre (vagy navigáljon közvetlenül a `http://localhost:8080/admin/settings/connections` címre).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. Az **OpenAI API** alatt adjon hozzá egy új kapcsolatot:
   - **Base URL:** `http://localhost:13305/api/v1`
   - **API Key:** `-` (helyi használatra egy kötőjel is megfelel)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. Győződjön meg róla, hogy a **"Manage OpenAI API Connections"** alatt csak a `http://localhost:13305/api/v1` van engedélyezve. Tiltson le minden más kapcsolatot (pl. az alapértelmezett OpenAI-t).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. Kattintson a **Save** gombra.

7. **(Ajánlott)** Tiltsa le az automatikus generálási funkciókat, hogy az Open WebUI reszponzív maradjon a helyi LLM-ekkel. Menjen az **Admin Settings → Settings → Interface** menübe, és kapcsolja ki a következőket:
   - Title Generation
   - Follow Up Generation
   - Tags Generation

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. Kattintson a **Save** gombra, majd térjen vissza a `http://localhost:8080` címre.
9. Kattintson a modell legördülő menüre — meg kell jelenniük a Lemonade-ből letöltött modelleknek.

---

## Fő Tevékenységek

Most már minden be van állítva. Nézzünk meg három érdekes dolgot, amit kipróbálhat.

---

### 1. Tevékenység: Csevegés Egy Helyi LLM-mel
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Kattintson a legördülő menüre a felület bal felső sarkában. Ez megjeleníti a telepített Lemonade modelleket. Válasszon egyet a folytatáshoz. (példa: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. Írjon be egy üzenetet az LLM-nek, és kattintson a küldésre (vagy nyomja meg az Entert). Az LLM-nek néhány másodpercbe telik betöltődni a memóriába, majd megjelenik a válasz folyamatosan érkezve.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Kattintson a legördülő menüre a felület bal felső sarkában. Ez megjeleníti a telepített Lemonade modelleket. Válasszon egyet a folytatáshoz. (példa: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Írjon be egy üzenetet az LLM-nek, és kattintson a küldésre (vagy nyomja meg az Entert). Az LLM-nek néhány másodpercbe telik betöltődni a memóriába, majd megjelenik a válasz folyamatosan érkezve.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. A modell válaszol a csevegésben.

4. Ekkor nyissa meg a `Task Manager` alkalmazást a rendszerén. **Magas GPU- vagy NPU-kihasználtságot** fog látni attól függően, hogy a kiválasztott modell **Hybrid** vagy **NPU** típusú-e. A Task Manager segítségével megerősítheti, hogy a modellt helyben futtatja.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Kattintson a legördülő menüre a felület bal felső sarkában. Ez megjeleníti a telepített Lemonade modelleket. Válasszon egyet a folytatáshoz. (példa: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Írjon be egy üzenetet az LLM-nek, és kattintson a küldésre (vagy nyomja meg az Entert). Az LLM-nek néhány másodpercbe telik betöltődni a memóriába, majd megjelenik a válasz folyamatosan érkezve.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. A modell válaszol a csevegésben.
<!-- @os:end -->

Ez igazolja, hogy az Open WebUI képes kéréseket küldeni a Lemonade-nek az OpenAI-kompatibilis chat végponton keresztül.

---

### 2. Tevékenység: Kép Feltöltése és Kérdések Feltevése (Vision)

Ehhez olyan modellre van szükség, amely támogatja a képbevitelt (Vision vagy Multimodal modell).

1. Kattintson a szűrő ikonra, válassza a "By Category" lehetőséget, majd válasszon egy modellt a **Vision** kategóriából (pl. `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. Kattintson a **`+`** gombra az üzenetmezőben, és töltsön fel egy képet
3. Tegyen fel valamit, ami valódi képmegértést igényel: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. A modell a kép tartalma alapján válaszol, nem pedig általános szöveggel.

Ez bizonyítja, hogy az Open WebUI multimodális kéréseket (szöveg + kép) tud küldeni a háttérrendszeren (Lemonade) keresztül egy vision modellnek.

---

<!-- @os:windows -->
### 3. Tevékenység: Kép Generálása Szöveges Prompt Alapján (Stable Diffusion)

A Stable Diffusion modellek nem támogatják a szöveggenerálást, kizárólag képeket generálnak az Images API-n keresztül. 

#### 1. Lépés: Kép Generálás Konfigurálása az Open WebUI-ban

1. A Lemonade GUI-ban (`http://localhost:13305`) keresse meg az `SDXL-Turbo` (gyors) vagy az `SDXL-Base-1.0` (jobb minőségű) modellt, és töltse le.
2. Menjen az **Admin Settings → Images** menübe (http://localhost:8080/admin/settings/images)
3. Állítsa be:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` vagy `SDXL-Base-1.0`
4. Ha további paramétereket szeretne hozzáadni, adja hozzá őket a szövegmezőhöz JSON formátumban. Például: `{ "steps": 4, "cfg_scale": 1 }`. Az elérhető paraméterekért lásd: [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Mentés
#### 2. lépés: Kép generálásának engedélyezése a modellhez
Ez a lépés biztosítja, hogy engedélyezze a Kép generálását mint képességet a modelljéhez.
1. Menjen a **Admin Settings → Models** (http://localhost:8080/admin/settings/models) oldalra, és válassza ki a modelljét
2. Kapcsolja be a `Image Generation` opciót

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### 3. lépés: Kép generálása a csevegési képernyőről

1. Menjen vissza a csevegéshez a `http://localhost:8080` címen.
2. Válasszon egy **szöveggeneráló LLM-et** a modell legördülő menüben (például: Qwen, Llama). **Ne válasszon Stable Diffusion modellt**, mivel ez egy csevegési modellválasztó.
3. Az üzenetmezőben kattintson az **Integrations** gombra, és kapcsolja BE az **Image** opciót.
4. Használjon egy ehhez hasonló promptot: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Egy kép generálódik, és megjelenik a csevegésben.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Ez igazolja, hogy az Open WebUI képes koordinálni egy „kétrészes” munkafolyamatot:
  - Az LLM segít finomítani a promptot
  - A kép a Lemonade Images végpontján keresztül generálódik Stable Diffusion segítségével
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### 3. tevékenység: Kép generálása szöveges promptból (Stable Diffusion)

A Stable Diffusion modellek nem támogatják a szöveggenerálást, csak az Images API-n keresztül generálnak képeket.

#### 1. lépés: Kép generálás konfigurálása az Open WebUI-ban

1. A Lemonade GUI-ban (`http://localhost:13305`) keressen rá az `SDXL-Turbo` (gyors) vagy `SDXL-Base-1.0` (magasabb minőség) modellre, és töltse le.
2. Menjen a **Admin Settings → Images** (http://localhost:8080/admin/settings/images) oldalra
3. Állítsa be:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` vagy `SDXL-Base-1.0`
4. Ha további paramétereket szeretne hozzáadni, adja hozzá őket a szövegmezőhöz JSON formátumban. Például: `{ "steps": 4, "cfg_scale": 1 }`. Az elérhető paraméterek itt találhatók: [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Mentés


#### 2. lépés: Kép generálásának engedélyezése a modellhez
Ez a lépés biztosítja, hogy engedélyezze a Kép generálását mint képességet a modelljéhez.
1. Menjen a **Admin Settings → Models** (http://localhost:8080/admin/settings/models) oldalra, és válassza ki a modelljét
2. Kapcsolja be a `Image Generation` opciót

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### 3. lépés: Kép generálása a csevegési képernyőről

1. Menjen vissza a csevegéshez a `http://localhost:8080` címen.
2. Válasszon egy **szöveggeneráló LLM-et** a modell legördülő menüben (például: Qwen, Llama). **Ne válasszon Stable Diffusion modellt**, mivel ez egy csevegési modellválasztó.
3. Az üzenetmezőben kattintson az **Integrations** gombra, és kapcsolja BE az **Image** opciót.
4. Használjon egy ehhez hasonló promptot: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Egy kép generálódik, és megjelenik a csevegésben.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Ez igazolja, hogy az Open WebUI képes koordinálni egy „kétrészes” munkafolyamatot:
  - Az LLM segít finomítani a promptot
  - A kép a Lemonade Images végpontján keresztül generálódik Stable Diffusion segítségével
<!-- @device:end -->
<!-- @os:end -->

---

## Hibaelhárítás

### „Nem jelennek meg modellek az Open WebUI-ban”
- Először ellenőrizze a Lemonade-et: nyissa meg a `http://localhost:13305/api/v1/models` címet egy böngészőben, és győződjön meg róla, hogy a modelljei szerepelnek a listán és le vannak töltve
- Ezután ellenőrizze az Open WebUI kapcsolatot: menjen a **Admin Settings → Connections** oldalra a `http://localhost:8080/admin/settings/connections` címen, és ellenőrizze, hogy a Base URL `http://localhost:13305/api/v1`

### „Ez a modell nem támogatja a csevegés-kiegészítést” hibaüzenet
- Kép modellt (SDXL-Turbo / SDXL-Base-1.0) választott ki a csevegési modell legördülő menüben.
- **Megoldás**: válasszon egy LLM-et a csevegéshez, és használja az Image kapcsolót + az Images beállításokat a generáláshoz.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Kép generálási hibák/időtúllépések
- Kezdje az `SDXL-Turbo` modellel (gyors, kevesebb lépés)
- Ha ez működik, váltson az `SDXL-Base-1.0` modellre a jobb minőség érdekében

---

## Következő lépések

Most már rendelkezik egy működő **„helyi AI-stackkel”**, egy olyan egységes felülettel, amely több modelltípust vezérel egy szabványos API-n keresztül.

Íme három bővítési lehetőség, amelyek teljesen új munkafolyamatokat tesznek lehetővé:

### 1. Beszéd-szöveg átalakítás Whisperrel

Próbálja meg hangot szöveggé alakítani egy Whisper modell segítségével, majd táplálja be egy LLM-be összefoglaláshoz, teendők kiemeléséhez vagy átíráshoz. Ez az alapja a megbeszélési jegyzeteknek és a hangvezérelt asszisztenseknek.

### 2. Python kódolás az Open WebUI-ban

Használja az Open WebUI beépített kódfuttatási élményét Python-kódrészletek futtatásához, kimenetek megtekintéséhez és gyorsabb iterációhoz — anélkül, hogy elhagyná a felületet. [Referencia](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. HTML renderelés az Open WebUI-ban

HTML-kimenetek közvetlen renderelése a felületen. Ez meglepően hasznos gyors prototípusok, formázott jelentések és interaktív részletek létrehozásához. [Referencia](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## Hivatkozások

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Lemonade Server dokumentáció](https://lemonade-server.ai/docs)
- [Lemonade Server CLI](https://lemonade-server.ai/docs/lemonade-cli/)
- [Lemonade ↔ Open WebUI integrációs útmutató](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Lemonade Server API specifikáció (végpontok)](https://lemonade-server.ai/docs/server/server_spec)
- [Videós bemutató (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [Videós bemutató (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)