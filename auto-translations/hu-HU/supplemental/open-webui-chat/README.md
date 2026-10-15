<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ehhez a playbookhoz legalább **32 GB** rendszermemória szükséges.
<!-- @device:end -->

## Áttekintés

Az [Open WebUI](https://docs.openwebui.com) egy önhosztolt, böngészőalapú felület, amely ismerős chatbot-élményt nyújt, miközben egy vagy több AI modellkiszolgáló frontendjeként működik. Ahelyett, hogy egyetlen szolgáltatóhoz lenne kötve, az Open WebUI **bármilyen, OpenAI-kompatibilis API-t kínáló backendhez** csatlakozhat, így modelleket és képességeket cserélhetsz anélkül, hogy felületet kellene váltanod.

Ebben a playbookban a [**Lemonade**](https://lemonade-server.ai) szolgál backendként, mivel egy **egységes, OpenAI-kompatibilis végpontot** biztosít, amely több modalitást is támogat:
- **Nagy nyelvi modellek (LLM-ek)** szöveggeneráláshoz
- **Vizuális modellek** képértelmezéshez
- **Stable Diffusion** képgeneráláshoz
- **Hangátírási modellek** beszéd-szöveg átalakításhoz

Ez a beállítás lehetővé teszi, hogy a **teljes multimodális munkafolyamatot végigkövesd**.

---

## Amit tanulni fogsz

A végére képes leszel:

- Az Open WebUI összekapcsolására egy helyi, OpenAI-kompatibilis backenddel (Lemonade)
- Csevegésre egy helyi LLM-mel a böngésződből
- Kép feltöltésére és kérdések feltevésére egy vizuális modellnek a képpel kapcsolatban
- Képek generálására szöveges promptokból Stable Diffusion modellek segítségével (SDXL-Turbo / SDXL)
- A gondolati modell megértésére, hogy más backendeket is használhass (Ollama, vLLM, llama.cpp server stb.)

---

## Alapfogalmak (gondolati modell)

### A három összetevő

| Elem | Mit csinál | Példák |
|---|---|---|
| Frontend (felhasználói felület) | A webalkalmazás, amellyel interakcióba lépsz | Open WebUI |
| Backend (modellkiszolgáló) | Modelleket hosztol és HTTP végpontokat biztosít | Lemonade, Ollama, vLLM, llama.cpp server, OpenAI-kompatibilis szerverek |
| Modellek | A tényleges LLM / vizuális / diffúziós / hangmodellek | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### Miért fontos az „OpenAI-kompatibilis API"

Az Open WebUI szabványos, OpenAI-stílusú végpontokra épül, például:
  - Chat: `/chat/completions`
  - Modellek listája: `/models`
  - Képgenerálás: `/images/generations`
  - Hangátírás: `/audio/transcriptions`

A Lemonade ezeket a `http://localhost:13305/api/v1/...` alatt teszi elérhetővé.

Ha egy backend támogatja ezeket a végpontokat, az Open WebUI minimális beállítással tud vele kommunikálni. Ezért tudunk backendet váltani anélkül, hogy a munkafolyamatunkat módosítanánk.

#### Két szolgáltatás, két port

Ebben a playbookban két különálló szolgáltatással fogsz dolgozni:

| Szolgáltatás | URL | Mit csinálsz ott |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | Modellek böngészése, letöltése és kezelése |
| **Open WebUI** | `http://localhost:8080` | Csevegés, képek feltöltése, képek generálása — a felhasználó felé néző felület |

A Lemonade futtatja a modelleket; az Open WebUI az a felület, amellyel interakcióba lépsz. Először a Lemonade GUI-ban töltsd le a modelleket, majd használd őket az Open WebUI-ból.

---

<!-- @device:halo_box,halo,stx,krk -->
## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->

## Egyszeri beállítás

Ehhez a playbookhoz a Lemonade-nek backendként kell futnia, illetve Linuxon egy konténermotorra (Podman) van szükség az Open WebUI futtatásához. Ezeket állítsd be az Open WebUI telepítése előtt.

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

Az Open WebUI telepítése előtt győződj meg róla, hogy a használni kívánt modellek le vannak töltve, és készen állnak a Lemonade-ben.

1. Nyisd meg a Lemonade GUI-t a `http://localhost:13305` címen.
2. Böngészd az elérhető modelleket, és töltsd le azokat, amelyeket használni szeretnél (pl. egy LLM-et csevegéshez, egy vizuális modellt, és/vagy egy Stable Diffusion modellt képgeneráláshoz).
3. Ellenőrizd, hogy az API elérhető-e a `http://localhost:13305/api/v1/models` cím böngészőben történő megnyitásával — a letöltött modelleknek meg kell jelenniük a listában.

> A modelleket a **Lemonade**-ben (`localhost:13305`) kell letölteni, mielőtt megjelenhetnének az **Open WebUI**-ban (`localhost:8080`). Ha egy modell később nem jelenik meg az Open WebUI-ban, térj vissza ide, és ellenőrizd először a Lemonade-et.


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

## Az Open WebUI telepítése

<!-- @os:windows -->
### 1. A Python 3.12 telepítése

Az Open WebUI-hoz **Python 3.12** szükséges — nem telepíthető Python 3.13+ verzióra. A Windows Python Launcher (`py`) lehetővé teszi, hogy a 3.12-t bármely már meglévő Python-verzió mellett, konfliktusmentesen telepítsd.

```powershell
winget install Python.Python.3.12
```

A telepítés után zárd be, majd nyisd meg újra a terminált, és ellenőrizd:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Megjegyzés:** A rendszereden előre telepítve van a Python 3.13. A 3.12 telepítése ezt nem befolyásolja — a `python` továbbra is a 3.13-at használja, a `py -3.12` pedig csak akkor a 3.12-t célozza meg, ha szükséged van rá.
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

### 2. Virtuális környezet létrehozása és az Open WebUI telepítése

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

Kérjük, töltsd le a következőt egy általad választott könyvtárba: [compose.yml](assets/compose.yml)

Abban a könyvtárban futtasd a következő parancsot:

```bash
podman compose up -d
```

Ez letölti az Open WebUI image-et, és perzisztens tárolóba írja.

Indítsd el az Open WebUI-t a `localhost:8080` böngésző címsorba történő beírásával.

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

> **Tipp**: Az Open WebUI más telepítési lehetőségeket is kínál a [GitHub](https://github.com/open-webui/open-webui) oldalán.
## Open WebUI szerver indítása

<!-- @os:windows -->
- Az alábbi parancs futtatásával indítsd el az Open WebUI HTTP szervert:
```bash
open-webui serve
```
<!-- @os:end -->

- Egy böngészőben navigálj a `http://localhost:8080` címre.
- Az Open WebUI kérni fogja, hogy hozz létre egy helyi rendszergazdai fiókot. Miután bejelentkeztél, meg fog jelenni a csevegőfelület.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> Hagyd nyitva a terminálablakot. Ha bezárod, leáll az Open WebUI.
<!-- @os:end -->

<!-- @os:linux -->
> A konténer a háttérben fut. A `compose.yml` fájlt tartalmazó könyvtárból a `podman compose down` (leállítás) és a `podman compose up -d` (indítás) parancsokkal kezelheted. A fiókjaid és beállításaid megmaradnak az `open_webui_data` kötetben.
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

## Az Open WebUI csatlakoztatása a Lemonade-hez

Most, hogy mindkét szolgáltatás fut — a Lemonade a `localhost:13305` címen, az Open WebUI pedig a `localhost:8080` címen —, kapcsold össze őket, hogy az Open WebUI használhassa a Lemonade modelljeit.

Az Open WebUI-ban:

1. Kattints a **felhasználói profil ikonra** a jobb felső sarokban, majd válaszd a **Settings** (Beállítások) menüpontot.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. A Beállítások panelen kattints az **Admin Settings** (Rendszergazdai beállítások) menüpontra a bal alsó sarokban.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. A rendszergazdai beállítások oldalsávjában kattints a **Connections** (Kapcsolatok) menüpontra (vagy navigálj közvetlenül a `http://localhost:8080/admin/settings/connections` címre).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. Az **OpenAI API** alatt adj hozzá egy új kapcsolatot:
   - **Base URL:** `http://localhost:13305/api/v1`
   - **API Key:** `-` (helyi használatra egyetlen kötőjel is megfelelő)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. Győződj meg róla, hogy a **"Manage OpenAI API Connections"** alatt kizárólag a `http://localhost:13305/api/v1` kapcsolat van engedélyezve. Kapcsold ki az összes többi kapcsolatot (pl. az alapértelmezett OpenAI kapcsolatot).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. Kattints a **Save** (Mentés) gombra.

7. **(Ajánlott)** Kapcsold ki az automatikus generálási funkciókat, hogy az Open WebUI reszponzív maradjon a helyi LLM-ekkel. Menj az **Admin Settings → Settings → Interface** menübe, és kapcsold ki a következőket:
   - Title Generation
   - Follow Up Generation
   - Tags Generation

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. Kattints a **Save** (Mentés) gombra, majd térj vissza a `http://localhost:8080` címre.
9. Kattints a modellválasztó legördülő menüre — itt látnod kell a Lemonade-ből letöltött modelleket.

---

## Fő tevékenységek

Most már minden készen áll. Nézzünk meg három érdekes dolgot, amit kipróbálhatsz.

---

### 1. tevékenység: Csevegés egy helyi LLM-mel
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Kattints a felület bal felső sarkában található legördülő menüre. Ez megjeleníti a telepített Lemonade modelleket. Válassz ki egyet a folytatáshoz. (példa: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. Írj be egy üzenetet az LLM-nek, majd kattints a küldés gombra (vagy nyomd meg az Entert). Az LLM betöltése a memóriába néhány másodpercet vesz igénybe, majd megjelenik a válasz folyamatos megjelenítéssel.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Kattints a felület bal felső sarkában található legördülő menüre. Ez megjeleníti a telepített Lemonade modelleket. Válassz ki egyet a folytatáshoz. (példa: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Írj be egy üzenetet az LLM-nek, majd kattints a küldés gombra (vagy nyomd meg az Entert). Az LLM betöltése a memóriába néhány másodpercet vesz igénybe, majd megjelenik a válasz folyamatos megjelenítéssel.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. A modell válaszolni fog a csevegésben.

4. Ekkor nyisd meg a `Task Manager` (Feladatkezelő) alkalmazást a rendszereden. **Magas GPU- vagy NPU-kihasználtságot** fogsz látni attól függően, hogy a kiválasztott modell **Hybrid** vagy **NPU** típusú-e. A feladatkezelő segítségével megbizonyosodhatsz arról, hogy a modellt helyileg futtatod.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Kattints a felület bal felső sarkában található legördülő menüre. Ez megjeleníti a telepített Lemonade modelleket. Válassz ki egyet a folytatáshoz. (példa: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Írj be egy üzenetet az LLM-nek, majd kattints a küldés gombra (vagy nyomd meg az Entert). Az LLM betöltése a memóriába néhány másodpercet vesz igénybe, majd megjelenik a válasz folyamatos megjelenítéssel.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. A modell válaszolni fog a csevegésben.
<!-- @os:end -->

Ez igazolja, hogy az Open WebUI kérést tud küldeni a Lemonade-nek az OpenAI-kompatibilis csevegési végpont használatával.

---

### 2. tevékenység: Kép feltöltése és kérdések feltevése (Vision)

Ehhez egy olyan modell szükséges, amely támogatja a képbemenetet (Vision vagy Multimodal modell).

1. Kattints a szűrő ikonra, válaszd a "By Category" (Kategória szerint) lehetőséget, majd válassz egy modellt a **Vision** szekcióból (pl. `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. Kattints a **`+`** gombra az üzenetmezőben, és tölts fel egy képet
3. Tegyél fel egy olyan kérdést, amely valódi képértelmezést igényel: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. A modell a kép tartalma alapján válaszol, nem pedig általános szöveggel.

Ez azt mutatja, hogy az Open WebUI multimodális kéréseket (szöveg + kép) tud küldeni a háttérrendszeren (Lemonade) keresztül egy vision modellnek.

---

<!-- @os:windows -->
### 3. tevékenység: Kép generálása szöveges promptból (Stable Diffusion)

A Stable Diffusion modellek nem támogatják a szöveggenerálást, kizárólag képeket generálnak az Images API-n keresztül. 

#### 1. lépés: Képgenerálás beállítása az Open WebUI-ban

1. A Lemonade GUI-ban (`http://localhost:13305`) keresd meg az `SDXL-Turbo` (gyors) vagy az `SDXL-Base-1.0` (magasabb minőség) modellt, és töltsd le.
2. Menj az **Admin Settings → Images** menübe (http://localhost:8080/admin/settings/images)
3. Állítsd be:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` vagy `SDXL-Base-1.0`
4. Ha további paramétereket szeretnél hozzáadni, add meg őket a szövegmezőben JSON formátumban. Például: `{ "steps": 4, "cfg_scale": 1 }`. Az elérhető paramétereket lásd itt: [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Mentés
#### 2. lépés: Kép generálásának engedélyezése a modellhez
Ez a lépés biztosítja, hogy engedélyezd a Kép generálását mint képességet a modelledhez.
1. Menj az **Admin Settings → Models** (http://localhost:8080/admin/settings/models) menüpontba, és válaszd ki a modelledet
2. Kapcsold be az `Image Generation` opciót

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### 3. lépés: Kép generálása a chat képernyőről

1. Menj vissza a chathez a `http://localhost:8080` címen.
2. Válassz egy **szöveggeneráló LLM-et** a modell legördülő menüben (például: Qwen, Llama). **Ne válassz Stable Diffusion modellt**, mivel ez egy chatmodell-választó.
3. Az üzenetterületen kattints az **Integrations** menüpontra, és kapcsold BE az **Image** opciót.
4. Használj egy ehhez hasonló promptot: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Egy kép generálódik, és megjelenik a chatben.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Ez igazolja, hogy az Open WebUI képes koordinálni egy "kétrészes" munkafolyamatot:
  - Az LLM segít finomítani a promptot
  - A kép a Lemonade Images végpontján keresztül generálódik Stable Diffusion segítségével
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### 3. tevékenység: Kép generálása szöveges promptból (Stable Diffusion)

A Stable Diffusion modellek nem támogatják a szöveggenerálást, csak a Images API-n keresztül generálnak képeket.

#### 1. lépés: Kép generálásának konfigurálása az Open WebUI-ban

1. A Lemonade GUI-ban (`http://localhost:13305`) keress rá az `SDXL-Turbo` (gyors) vagy az `SDXL-Base-1.0` (jobb minőség) modellre, és töltsd le.
2. Menj az **Admin Settings → Images** (http://localhost:8080/admin/settings/images) menüpontba
3. Állítsd be:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` vagy `SDXL-Base-1.0`
4. Ha további paramétereket szeretnél hozzáadni, add meg őket a szövegmezőben JSON formátumban. Például: `{ "steps": 4, "cfg_scale": 1 }`. Az elérhető paraméterek itt találhatók: [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Mentés


#### 2. lépés: Kép generálásának engedélyezése a modellhez
Ez a lépés biztosítja, hogy engedélyezd a Kép generálását mint képességet a modelledhez.
1. Menj az **Admin Settings → Models** (http://localhost:8080/admin/settings/models) menüpontba, és válaszd ki a modelledet
2. Kapcsold be az `Image Generation` opciót

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### 3. lépés: Kép generálása a chat képernyőről

1. Menj vissza a chathez a `http://localhost:8080` címen.
2. Válassz egy **szöveggeneráló LLM-et** a modell legördülő menüben (például: Qwen, Llama). **Ne válassz Stable Diffusion modellt**, mivel ez egy chatmodell-választó.
3. Az üzenetterületen kattints az **Integrations** menüpontra, és kapcsold BE az **Image** opciót.
4. Használj egy ehhez hasonló promptot: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Egy kép generálódik, és megjelenik a chatben.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Ez igazolja, hogy az Open WebUI képes koordinálni egy "kétrészes" munkafolyamatot:
  - Az LLM segít finomítani a promptot
  - A kép a Lemonade Images végpontján keresztül generálódik Stable Diffusion segítségével
<!-- @device:end -->
<!-- @os:end -->

---

## Hibaelhárítás

### "Nem jelennek meg modellek az Open WebUI-ban"
- Először ellenőrizd a Lemonade-et: nyisd meg a `http://localhost:13305/api/v1/models` címet a böngészőben, és győződj meg róla, hogy a modelljeid szerepelnek a listán és le vannak töltve
- Ezután ellenőrizd az Open WebUI kapcsolatot: menj az **Admin Settings → Connections** menüpontba a `http://localhost:8080/admin/settings/connections` címen, és ellenőrizd, hogy az alap URL a `http://localhost:13305/api/v1`

### "This model does not support chat completion" hibaüzenet
- Egy képmodellt (SDXL-Turbo / SDXL-Base-1.0) választottál ki a chatmodell legördülő menüben.
- **Megoldás**: válassz egy LLM-et a chathez, és használd a Kép kapcsolót + a Kép beállításokat a generáláshoz.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Képgenerálási hibák/időtúllépések
- Kezdd az `SDXL-Turbo` modellel (gyors, kevesebb lépés)
- Ha ez működik, válts át `SDXL-Base-1.0` modellre a jobb minőségért

---

## Következő lépések

Mostantól rendelkezel egy működő **„helyi AI stackkel”**, egyetlen felülettel, amely több modelltípust vezérel egy szabványos API-n keresztül.

Íme három kiterjesztési lehetőség, amelyek teljesen új munkafolyamatokat nyitnak meg:

### 1. Beszéd-szöveg átalakítás Whisperrel

Próbáld ki, hogyan alakítható hang szöveggé egy Whisper modell segítségével, majd add tovább egy LLM-nek összefoglaláshoz, teendők kigyűjtéséhez vagy átfogalmazáshoz. Ez az alapja a jegyzőkönyveknek és a hangvezérelt asszisztenseknek.

### 2. Python kódolás az Open WebUI-ban

Használd az Open WebUI beépített kódfuttatási élményét Python-kódrészletek futtatásához, a kimenetek megtekintéséhez és a gyorsabb iterációhoz – anélkül, hogy elhagynád a felületet. [Referencia](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. HTML megjelenítés az Open WebUI-ban

Jelenítsd meg a HTML kimeneteket közvetlenül a felületen. Ez meglepően hasznos gyors prototípusok, formázott jelentések és interaktív részletek készítéséhez. [Referencia](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

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