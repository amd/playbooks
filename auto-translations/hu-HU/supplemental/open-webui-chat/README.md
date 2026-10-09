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

Az [Open WebUI](https://docs.openwebui.com) egy önállóan üzemeltethető, böngészőalapú felület, amely ismerős chatbot élményt nyújt, miközben egy vagy több AI modellkiszolgáló frontendjeként működik. Ahelyett, hogy egyetlen szolgáltatóhoz lenne kötve, az Open WebUI **bármilyen, OpenAI-kompatibilis API-t megjelenítő backendhez** kapcsolódhat, így modelleket és funkciókat cserélhetsz anélkül, hogy a felületet le kellene cserélned.

Ebben a playbookban a [**Lemonade**](https://lemonade-server.ai) szolgál backendként, mivel ez egy **egységes, OpenAI-kompatibilis végpontot** biztosít, amely több modalitást is támogat:
- **Nagy nyelvi modellek (LLM-ek)** szöveggeneráláshoz
- **Látásmodellek (vision models)** képek értelmezéséhez
- **Stable Diffusion** képgeneráláshoz
- **Hangfelismerő modellek** beszéd-szöveg átalakításhoz

Ez a beállítás lehetővé teszi, hogy **a teljes multimodális munkafolyamatot végigjárd**.

---

## Amit meg fogsz tanulni

A végére képes leszel:

- Az Open WebUI összekapcsolására egy helyi, OpenAI-kompatibilis backenddel (Lemonade)
- Csevegésre egy helyi LLM-mel a böngésződből
- Kép feltöltésére és kérdések feltevésére egy látásmodellnek a képpel kapcsolatban
- Képek generálására szöveges promptok alapján Stable Diffusion modellekkel (SDXL-Turbo / SDXL)
- A gondolkodási modell megértésére, hogy más backendeket is tudj használni (Ollama, vLLM, llama.cpp server stb.)

---

## Alapfogalmak (gondolkodási modell)

### A három összetevő

| Elem | Mit csinál | Példák |
|---|---|---|
| Frontend (UI) | A webalkalmazás, amellyel interakcióba lépsz | Open WebUI |
| Backend (modellkiszolgáló) | Modelleket üzemeltet és HTTP végpontokat biztosít | Lemonade, Ollama, vLLM, llama.cpp server, OpenAI-kompatibilis szerverek |
| Modellek | A tényleges LLM / vision / diffúziós / hang modellek | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### Miért számít az „OpenAI-kompatibilis API”

Az Open WebUI szabványos, OpenAI-stílusú végpontokra épül, például:
  - Chat: `/chat/completions`
  - Modellek listája: `/models`
  - Képgenerálás: `/images/generations`
  - Hangátirat: `/audio/transcriptions`

A Lemonade ezeket a `http://localhost:13305/api/v1/...` cím alatt teszi elérhetővé.

Ha egy backend támogatja ezeket a végpontokat, az Open WebUI minimális beállítással képes kommunikálni vele. Emiatt tudunk backendeket cserélni anélkül, hogy a munkafolyamatunkat módosítanánk.

#### Két szolgáltatás, két port

Ebben a playbookban két külön szolgáltatással fogsz dolgozni:

| Szolgáltatás | URL | Mit csinálsz ott |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | Modellek böngészése, letöltése és kezelése |
| **Open WebUI** | `http://localhost:8080` | Csevegés, képfeltöltés, képgenerálás — a felhasználói felület |

A Lemonade futtatja a modelleket; az Open WebUI az a felület, amellyel interakcióba lépsz. Először a Lemonade GUI segítségével töltsd le a modelljeidet, majd használd azokat az Open WebUI-ból.

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

Ehhez a playbookhoz szükséges a Lemonade futtatása backendként, valamint Linuxon egy konténer-futtatókörnyezet (Podman) az Open WebUI futtatásához. Ezeket az Open WebUI telepítése előtt állítsd be.

<!-- @os:windows -->
<!-- @device:halo_box,halo,stx,krk -->
<!-- @require:lemonade -->
<!-- @prereq:lemonade -->
<!-- @device:end -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver,lemonade -->
<!-- @device:end -->
<!-- @prereq:hf-models-all-minilm-l6-v2 -->
---
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
<!-- @require:lemonade,podman -->
<!-- @prereq:podman -->
<!-- @device:end -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver,lemonade,podman -->
<!-- @device:end -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
---
<!-- @device:end -->
<!-- @os:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @prereq:lemonade-models-qwen3-5-4b,lemonade-models-sdxl-turbo -->

<!-- @test:id=lemonade-cli-verify timeout=30 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end --> 

## Modellek letöltése Lemonade-ben

Az Open WebUI telepítése előtt győződj meg róla, hogy a használni kívánt modellek letöltve és készen állnak a Lemonade-ben.

1. Nyisd meg a Lemonade GUI-t a `http://localhost:13305` címen.
2. Böngészd az elérhető modelleket, és töltsd le azokat, amelyeket használni szeretnél (pl. egy LLM-et csevegéshez, egy látásmodellt, és/vagy egy Stable Diffusion modellt képgeneráláshoz).
3. Győződj meg róla, hogy az API elérhető: nyisd meg a böngésződben a `http://localhost:13305/api/v1/models` címet — a letöltött modelleknek meg kell jelenniük a listában.

> A modelleket a **Lemonade**-ben (`localhost:13305`) kell letölteni, mielőtt megjelenhetnének az **Open WebUI**-ban (`localhost:8080`). Ha egy modell később nem jelenik meg az Open WebUI-ban, térj vissza ide, és először itt ellenőrizd a Lemonade-et.


<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
<!-- @prereq:lemonade-models-qwen3-4b-hybrid -->
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
### 1. Python 3.12 telepítése

Az Open WebUI **Python 3.12**-t igényel — Python 3.13+ verzióval nem telepíthető. A Windows Python Launcher (`py`) lehetővé teszi, hogy a 3.12-es verziót a meglévő Python verzióid mellett, ütközés nélkül telepítsd.

```powershell
winget install Python.Python.3.12
```

A telepítés után zárd be, majd nyisd meg újra a terminált, és ellenőrizd:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Megjegyzés:** A rendszereden előre telepítve van a Python 3.13. A 3.12 telepítése ezt nem befolyásolja — a `python` továbbra is a 3.13-at használja, a `py -3.12` pedig csak akkor a 3.12-t célozza, amikor szükséged van rá.
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

Töltsd le a következőt egy általad választott könyvtárba: [compose.yml](assets/compose.yml)

Abban a könyvtárban futtasd a következő parancsot:

```bash
podman compose up -d
```

Ez lehúzza az Open WebUI image-et, és állandó tárolóba írja.

Indítsd el az Open WebUI-t a `localhost:8080` cím böngésződ címsorába történő beírásával.

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

> **Tipp**: Az Open WebUI más telepítési lehetőségeket is kínál a [GitHub](https://github.com/open-webui/open-webui) oldalukon.
## Open WebUI szerver elindítása

<!-- @os:windows -->
- Futtasd a következő parancsot az Open WebUI HTTP szerver elindításához:
```bash
open-webui serve
```
<!-- @os:end -->

- Egy böngészőben navigálj a `http://localhost:8080` címre.
- Az Open WebUI arra kér, hogy hozz létre egy helyi rendszergazdai fiókot. Miután bejelentkeztél, megjelenik a chat felület.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> Hagyd nyitva a terminálablakot. Ha bezárod, az Open WebUI leáll.
<!-- @os:end -->

<!-- @os:linux -->
> A konténer a háttérben fut. Abból a könyvtárból, amely a `compose.yml` fájlt tartalmazza, a `podman compose down` (leállítás) és `podman compose up -d` (indítás) parancsokkal kezelheted. A fiókjaid és beállításaid megmaradnak az `open_webui_data` kötetben.
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

## Open WebUI csatlakoztatása a Lemonade-hez

Most, hogy mindkét szolgáltatás fut — a Lemonade a `localhost:13305`-ön, az Open WebUI pedig a `localhost:8080`-on —, kösd össze őket, hogy az Open WebUI használhassa a Lemonade modelljeit.

Az Open WebUI-ban:

1. Kattints a **felhasználói profil ikonra** a jobb felső sarokban, majd válaszd a **Settings** opciót.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. A Settings panelen kattints az **Admin Settings** gombra a bal alsó sarokban.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. Az Admin Settings oldalsávban kattints a **Connections** menüpontra (vagy navigálj közvetlenül a `http://localhost:8080/admin/settings/connections` címre).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. Az **OpenAI API** alatt adj hozzá egy új kapcsolatot:
   - **Base URL:** `http://localhost:13305/api/v1`
   - **API Key:** `-` (egyetlen kötőjel is megfelel helyi használatra)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. Győződj meg róla, hogy a **"Manage OpenAI API Connections"** alatt kizárólag a `http://localhost:13305/api/v1` van engedélyezve. Tiltsd le az összes többi kapcsolatot (pl. az alapértelmezett OpenAI-t).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. Kattints a **Save** gombra.

7. **(Ajánlott)** Tiltsd le az automatikus generálási funkciókat, hogy az Open WebUI reszponzív maradjon a helyi LLM-ekkel. Navigálj az **Admin Settings → Settings → Interface** menüpontba, és kapcsold ki:
   - Title Generation
   - Follow Up Generation
   - Tags Generation

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. Kattints a **Save** gombra, majd térj vissza a `http://localhost:8080` címre.
9. Kattints a modell legördülő menüre — itt megjelennek a Lemonade-ről letöltött modelljeid.

---

## Fő tevékenységek

Most már minden be van állítva. Nézzünk meg három érdekes dolgot, amit kipróbálhatsz.

---

### 1. tevékenység: Csevegés egy helyi LLM-mel
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Kattints a felület bal felső sarkában lévő legördülő menüre. Ez megjeleníti a telepített Lemonade modelleket. Válassz ki egyet a folytatáshoz. (példa: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. Írj be egy üzenetet az LLM-nek, és kattints a küldésre (vagy nyomj Entert). Az LLM-nek néhány másodpercre lesz szüksége, hogy betöltődjön a memóriába, majd megjelenik a válasz folyamatosan beérkezve.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Kattints a felület bal felső sarkában lévő legördülő menüre. Ez megjeleníti a telepített Lemonade modelleket. Válassz ki egyet a folytatáshoz. (példa: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Írj be egy üzenetet az LLM-nek, és kattints a küldésre (vagy nyomj Entert). Az LLM-nek néhány másodpercre lesz szüksége, hogy betöltődjön a memóriába, majd megjelenik a válasz folyamatosan beérkezve.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. A modell válaszol a chatben.

4. Ekkor nyisd meg a `Task Manager` alkalmazást a rendszereden. Attól függően, hogy a kiválasztott modell **Hybrid** vagy **NPU** típusú, **magas GPU- vagy NPU-kihasználtságot** fogsz látni. A Feladatkezelő segítségével megerősítheted, hogy a modellt valóban helyben futtatod.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Kattints a felület bal felső sarkában lévő legördülő menüre. Ez megjeleníti a telepített Lemonade modelleket. Válassz ki egyet a folytatáshoz. (példa: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Írj be egy üzenetet az LLM-nek, és kattints a küldésre (vagy nyomj Entert). Az LLM-nek néhány másodpercre lesz szüksége, hogy betöltődjön a memóriába, majd megjelenik a válasz folyamatosan beérkezve.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. A modell válaszol a chatben.
<!-- @os:end -->

Ez igazolja, hogy az Open WebUI képes kéréseket küldeni a Lemonade-nek az OpenAI-kompatibilis chat végponton keresztül.

---

### 2. tevékenység: Kép feltöltése és kérdések feltevése (Vision)

Ehhez egy olyan modell szükséges, amely támogatja a képbemenetet (Vision vagy Multimodal modell).

1. Kattints a szűrő ikonra, válaszd a "By Category" opciót, majd válassz egy modellt a **Vision** kategóriából (pl. `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. Kattints a **`+`** gombra az üzenetmezőben, és tölts fel egy képet
3. Tegyél fel egy olyan kérdést, amely valódi képértelmezést igényel: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. A modell a kép tartalma alapján válaszol, nem általános szöveg alapján.

Ez bizonyítja, hogy az Open WebUI képes multimodális kéréseket (szöveg + kép) küldeni a backendnek (Lemonade) egy vision modellhez.

---

<!-- @os:windows -->
### 3. tevékenység: Kép generálása szöveges prompt alapján (Stable Diffusion)

A Stable Diffusion modellek nem támogatják a szöveggenerálást, kizárólag képeket generálnak az Images API-n keresztül.

#### 1. lépés: Képgenerálás konfigurálása az Open WebUI-ban

1. A Lemonade GUI-ban (`http://localhost:13305`) keresd meg az `SDXL-Turbo` (gyors) vagy `SDXL-Base-1.0` (jobb minőségű) modellt, és töltsd le.
2. Navigálj az **Admin Settings → Images** menüpontba (http://localhost:8080/admin/settings/images)
3. Állítsd be:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` vagy `SDXL-Base-1.0`
4. Ha további paramétereket szeretnél hozzáadni, add meg őket a szövegmezőben JSON formátumban. Például: `{ "steps": 4, "cfg_scale": 1 }`. Az elérhető paramétereket itt találod: [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Mentés
#### 2. lépés: Engedélyezd a képgenerálást a modellhez
Ez a lépés biztosítja, hogy a Képgenerálás képességet engedélyezd a modellednél.
1. Menj az **Admin Settings → Models** (http://localhost:8080/admin/settings/models) oldalra, és válaszd ki a modelledet
2. Kapcsold be az `Image Generation` funkciót

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### 3. lépés: Generálj egy képet a chat képernyőről

1. Menj vissza a chathez a `http://localhost:8080` címen.
2. Válassz egy **szöveggeneráló LLM-et** a modell legördülő menüjéből (például: Qwen, Llama). **Ne válassz Stable Diffusion modellt**, mivel ez egy chat modell választó.
3. Az üzenetmezőben kattints az **Integrations** gombra, és kapcsold BE az **Image** opciót.
4. Használj egy olyan promptot, mint: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Egy kép generálódik, és megjelenik a chatben.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Ez igazolja, hogy az Open WebUI képes koordinálni egy "kétrészes" munkafolyamatot:
  - Az LLM segít finomítani a promptot
  - A kép a Lemonade Images végpontján keresztül, Stable Diffusion használatával generálódik
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### 3. tevékenység: Kép generálása szöveges promptból (Stable Diffusion)

A Stable Diffusion modellek nem támogatják a szöveggenerálást, kizárólag a Images API-n keresztül generálnak képeket.

#### 1. lépés: Képgenerálás konfigurálása az Open WebUI-ban

1. A Lemonade GUI-ban (`http://localhost:13305`), keresd meg az `SDXL-Turbo` (gyors) vagy az `SDXL-Base-1.0` (jobb minőségű) modellt, és töltsd le.
2. Menj az **Admin Settings → Images** (http://localhost:8080/admin/settings/images) oldalra
3. Állítsd be:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` vagy `SDXL-Base-1.0`
4. Ha további paramétereket szeretnél hozzáadni, add meg őket JSON formátumban a szövegmezőben. Például: `{ "steps": 4, "cfg_scale": 1 }`. Az elérhető paraméterekért lásd: [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Mentsd el

#### 2. lépés: Engedélyezd a képgenerálást a modellhez
Ez a lépés biztosítja, hogy a Képgenerálás képességet engedélyezd a modellednél.
1. Menj az **Admin Settings → Models** (http://localhost:8080/admin/settings/models) oldalra, és válaszd ki a modelledet
2. Kapcsold be az `Image Generation` funkciót

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### 3. lépés: Generálj egy képet a chat képernyőről

1. Menj vissza a chathez a `http://localhost:8080` címen.
2. Válassz egy **szöveggeneráló LLM-et** a modell legördülő menüjéből (például: Qwen, Llama). **Ne válassz Stable Diffusion modellt**, mivel ez egy chat modell választó.
3. Az üzenetmezőben kattints az **Integrations** gombra, és kapcsold BE az **Image** opciót.
4. Használj egy olyan promptot, mint: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Egy kép generálódik, és megjelenik a chatben.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Ez igazolja, hogy az Open WebUI képes koordinálni egy "kétrészes" munkafolyamatot:
  - Az LLM segít finomítani a promptot
  - A kép a Lemonade Images végpontján keresztül, Stable Diffusion használatával generálódik
<!-- @device:end -->
<!-- @os:end -->

---

## Hibaelhárítás

### "Nem jelennek meg modellek az Open WebUI-ban"
- Először ellenőrizd a Lemonade-et: nyisd meg a `http://localhost:13305/api/v1/models` címet böngészőben, és győződj meg róla, hogy a modelljeid szerepelnek a listában és le vannak töltve
- Ezután ellenőrizd az Open WebUI kapcsolatot: menj az **Admin Settings → Connections** oldalra a `http://localhost:8080/admin/settings/connections` címen, és győződj meg róla, hogy az Alap URL `http://localhost:13305/api/v1`

### "This model does not support chat completion" hibaüzenet
- Egy képmodellt (SDXL-Turbo / SDXL-Base-1.0) választottál ki a chat modell legördülő menüjében.
- **Megoldás**: válassz egy LLM-et a chatelgetéshez, és használd a Image kapcsolót + a Images beállításokat a generáláshoz.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Képgenerálási hibák/időtúllépések
- Kezdd az `SDXL-Turbo`-val (gyors, kevesebb lépés)
- Ha ez működik, válts az `SDXL-Base-1.0` képmodellre a jobb minőségért

---

## Következő lépések

Most már rendelkezel egy működő **„helyi AI stack”-kel**, egyetlen felhasználói felülettel, amely több modelltípust vezérel egy szabványos API-n keresztül.

Íme három bővítési lehetőség, amelyek teljesen új munkafolyamatokat nyitnak meg:

### 1. Beszéd-szöveg átalakítás Whisperrel

Próbáld meg hangot szöveggé alakítani egy Whisper modell segítségével, majd add be egy LLM-nek összefoglalásra, feladatlistákhoz vagy átfogalmazáshoz. Ez az alapja a megbeszélés-jegyzeteknek és a hangvezérelt asszisztenseknek.

### 2. Python kódolás az Open WebUI-ban

Használd az Open WebUI beépített kódfuttatási élményét Python kódrészletek futtatásához, a kimenetek vizsgálatához és a gyorsabb iterációhoz – anélkül, hogy elhagynád a felületet. [Hivatkozás](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. HTML renderelés az Open WebUI-ban

Jeleníts meg HTML kimeneteket közvetlenül a felületen. Ez meglepően hasznos gyors prototípusok, formázott jelentések és interaktív kódrészletek készítéséhez. [Hivatkozás](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

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