<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Táto príručka vyžaduje minimálne **32 GB** systémovej pamäte.
<!-- @device:end -->

## Prehľad

[Open WebUI](https://docs.openwebui.com) je samostatne hosťované, prehliadačové rozhranie, ktoré poskytuje známy zážitok chatbota a zároveň funguje ako frontend pre jeden alebo viacero serverov s AI modelmi. Namiesto viazanosti na jedného poskytovateľa sa Open WebUI dokáže pripojiť k **akémukoľvek backendu, ktorý poskytuje rozhranie API kompatibilné s OpenAI**, takže môžete meniť modely a funkcie bez toho, aby ste museli meniť používateľské rozhranie.

V tejto príručke používame ako backend [**Lemonade**](https://lemonade-server.ai), pretože poskytuje **jednotný koncový bod API kompatibilný s OpenAI**, ktorý podporuje viacero modalít:
- **Veľké jazykové modely (LLM)** na generovanie textu
- **Vizuálne modely** na porozumenie obrázkom
- **Stable Diffusion** na generovanie obrázkov
- **Modely na prepis zvuku** na prevod reči na text

Toto nastavenie vám umožňuje preskúmať **kompletný multimodálny pracovný postup od začiatku do konca**.

---

## Čo sa naučíte

Na konci budete vedieť:

- Pripojiť Open WebUI k lokálnemu backendu kompatibilnému s OpenAI (Lemonade)
- Chatovať s lokálnym LLM priamo z prehliadača
- Nahrať obrázok a klásť vizuálnemu modelu otázky o ňom
- Generovať obrázky z textových výziev pomocou modelov Stable Diffusion (SDXL-Turbo / SDXL)
- Pochopiť mentálny model, aby ste mohli používať aj iné backendy (Ollama, vLLM, llama.cpp server atď.)

---

## Základné pojmy (mentálny model)

### Tri komponenty

| Časť | Čo robí | Príklady |
|---|---|---|
| Frontend (UI) | Webová aplikácia, s ktorou pracujete | Open WebUI |
| Backend (server modelov) | Hostuje modely a poskytuje HTTP koncové body | Lemonade, Ollama, vLLM, llama.cpp server, servery kompatibilné s OpenAI |
| Modely | Skutočné LLM / vizuálne / difúzne / zvukové modely | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### Prečo záleží na „rozhraní API kompatibilnom s OpenAI"

Open WebUI je postavené okolo štandardných koncových bodov v štýle OpenAI, ako napríklad:
  - Chat: `/chat/completions`
  - Zoznam modelov: `/models`
  - Generovanie obrázkov: `/images/generations`
  - Prepis zvuku: `/audio/transcriptions`

Lemonade tieto koncové body poskytuje pod adresou `http://localhost:13305/api/v1/...`

Ak backend tieto koncové body podporuje, Open WebUI s ním dokáže komunikovať s minimálnym nastavením. Preto môžeme meniť backendy bez toho, aby sme museli meniť náš pracovný postup.

#### Dve služby, dva porty

Počas tejto príručky budete pracovať s dvomi samostatnými službami:

| Služba | URL | Čo tam robíte |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | Prehliadanie, sťahovanie a správa modelov |
| **Open WebUI** | `http://localhost:8080` | Chatovanie, nahrávanie obrázkov, generovanie obrázkov — používateľské rozhranie |

Lemonade spúšťa modely; Open WebUI je rozhranie, s ktorým pracujete. Najprv použite Lemonade GUI na stiahnutie modelov a potom ich používajte z Open WebUI.

---

## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizácií softvéru

<!-- @require:software-update -->
<!-- @device:end -->

## Jednorazové nastavenie

Táto príručka vyžaduje, aby bol spustený Lemonade ako backend a v systéme Linux aj kontajnerový engine (Podman) na spustenie Open WebUI. Nastavte tieto komponenty pred inštaláciou Open WebUI.

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

## Sťahovanie modelov v Lemonade

Pred inštaláciou Open WebUI sa uistite, že modely, ktoré chcete používať, sú stiahnuté a pripravené v Lemonade.

1. Otvorte Lemonade GUI na adrese `http://localhost:13305`.
2. Prehliadajte dostupné modely a stiahnite tie, ktoré chcete použiť (napr. LLM na chatovanie, vizuálny model a/alebo model Stable Diffusion na generovanie obrázkov).
3. Overte, či je API dostupné, tak, že v prehliadači otvoríte adresu `http://localhost:13305/api/v1/models` — mali by ste vidieť zoznam stiahnutých modelov.

> Modely musia byť stiahnuté v **Lemonade** (`localhost:13305`), aby sa mohli neskôr zobraziť v **Open WebUI** (`localhost:8080`). Ak sa model neskôr v Open WebUI nezobrazí, vráťte sa sem a najprv skontrolujte Lemonade.


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

## Inštalácia Open WebUI

<!-- @os:windows -->
### 1. Inštalácia Python 3.12

Open WebUI vyžaduje **Python 3.12** — neinštaluje sa na Python 3.13 a vyšší. Windows Python Launcher (`py`) vám umožňuje nainštalovať 3.12 popri akejkoľvek existujúcej verzii Pythonu bez konfliktov.

```powershell
winget install Python.Python.3.12
```

Po inštalácii zatvorte a znova otvorte terminál a overte inštaláciu:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Poznámka:** Váš systém má predinštalovaný Python 3.13. Inštalácia verzie 3.12 to nijako neovplyvní — `python` naďalej používa verziu 3.13 a `py -3.12` sa zameriava len na verziu 3.12, keď ju potrebujete.
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

### 2. Vytvorenie virtuálneho prostredia a inštalácia Open WebUI

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
Teraz použijeme službu Podman na kontajnerizáciu našej inštalácie Open WebUI.

Stiahnite si prosím nasledujúci súbor do priečinka podľa vlastného výberu: [compose.yml](assets/compose.yml)

V danom priečinku spustite nasledujúci príkaz:

```bash
podman compose up -d
```

Tým sa stiahne obraz (image) Open WebUI a zapíše sa do trvalého úložiska.

Spustite Open WebUI zadaním `localhost:8080` do panela s adresou v prehliadači.

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

> **Tip**: Open WebUI ponúka aj ďalšie možnosti inštalácie, ktoré nájdete na ich stránke [GitHub](https://github.com/open-webui/open-webui).
## Spustenie servera Open WebUI

<!-- @os:windows -->
- Spustite nasledujúci príkaz na spustenie HTTP servera Open WebUI:
```bash
open-webui serve
```
<!-- @os:end -->

- V prehliadači prejdite na `http://localhost:8080`.
- Open WebUI vás vyzve na vytvorenie lokálneho účtu správcu. Po prihlásení uvidíte rozhranie chatu.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> Ponechajte okno terminálu otvorené. Jeho zatvorenie zastaví Open WebUI.
<!-- @os:end -->

<!-- @os:linux -->
> Kontajner beží na pozadí. Z adresára obsahujúceho `compose.yml` ho spravujte pomocou `podman compose down` (zastavenie) a `podman compose up -d` (spustenie). Vaše účty a nastavenia zostávajú zachované v zväzku `open_webui_data`.
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

## Pripojenie Open WebUI k Lemonade

Teraz, keď obe služby bežia — Lemonade na `localhost:13305` a Open WebUI na `localhost:8080` — ich prepojíme, aby Open WebUI mohlo používať modely Lemonade.

V Open WebUI:

1. Kliknite na **ikonu profilu používateľa** v pravom hornom rohu a potom vyberte **Settings**.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. V paneli Settings kliknite na **Admin Settings** v ľavom dolnom rohu.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. Na bočnom paneli Admin Settings kliknite na **Connections** (alebo prejdite priamo na `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. V sekcii **OpenAI API** pridajte nové pripojenie:
   - **Base URL:** `http://localhost:13305/api/v1`
   - **API Key:** `-` (pre lokálne použitie stačí jedna pomlčka)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. Uistite sa, že v sekcii **„Manage OpenAI API Connections"** je povolené iba pripojenie `http://localhost:13305/api/v1`. Vypnite všetky ostatné pripojenia (napr. predvolené pripojenie OpenAI).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. Kliknite na **Save**.

7. **(Odporúčané)** Vypnite funkcie automatického generovania, aby Open WebUI zostalo responzívne pri používaní lokálnych LLM. Prejdite na **Admin Settings → Settings → Interface** a vypnite:
   - Title Generation
   - Follow Up Generation
   - Tags Generation

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. Kliknite na **Save** a potom sa vráťte na `http://localhost:8080`.
9. Kliknite na rozbaľovaciu ponuku modelov — mali by ste vidieť modely, ktoré ste si stiahli z Lemonade.

---

## Hlavné aktivity

Teraz máte všetko nastavené. Pozrime sa na tri zaujímavé veci, ktoré môžete vyskúšať.

---

### Aktivita 1: Chatovanie s lokálnym LLM
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Kliknite na rozbaľovaciu ponuku vľavo hore v rozhraní. Zobrazia sa nainštalované modely Lemonade. Vyberte jeden z nich, aby ste mohli pokračovať. (príklad: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. Zadajte správu pre LLM a kliknite na odoslať (alebo stlačte Enter). Načítanie LLM do pamäte bude trvať niekoľko sekúnd a potom uvidíte prichádzajúcu odpoveď.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Kliknite na rozbaľovaciu ponuku vľavo hore v rozhraní. Zobrazia sa nainštalované modely Lemonade. Vyberte jeden z nich, aby ste mohli pokračovať. (príklad: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Zadajte správu pre LLM a kliknite na odoslať (alebo stlačte Enter). Načítanie LLM do pamäte bude trvať niekoľko sekúnd a potom uvidíte prichádzajúcu odpoveď.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. Model odpovie v chate.

4. Následne otvorte na svojom systéme `Task Manager`. Uvidíte **vysoké využitie GPU alebo NPU** podľa toho, či je vybraný model **Hybrid** alebo **NPU**. Pomocou správcu úloh môžete potvrdiť, že model beží lokálne.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Kliknite na rozbaľovaciu ponuku vľavo hore v rozhraní. Zobrazia sa nainštalované modely Lemonade. Vyberte jeden z nich, aby ste mohli pokračovať. (príklad: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Zadajte správu pre LLM a kliknite na odoslať (alebo stlačte Enter). Načítanie LLM do pamäte bude trvať niekoľko sekúnd a potom uvidíte prichádzajúcu odpoveď.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. Model odpovie v chate.
<!-- @os:end -->

Toto potvrdzuje, že Open WebUI dokáže odosielať požiadavky do Lemonade pomocou koncového bodu chatu kompatibilného s OpenAI.

---

### Aktivita 2: Nahranie obrázka a kladenie otázok (Vision)

Toto vyžaduje model, ktorý podporuje vstup obrázkov (model Vision alebo Multimodal).

1. Kliknite na ikonu filtra, vyberte „By Category" a potom zvoľte model zo sekcie **Vision** (napr. `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. Kliknite na tlačidlo **`+`** v poli správy a nahrajte obrázok
3. Položte otázku, ktorá vyžaduje skutočné pochopenie obrázka: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. Model odpovie na základe obsahu obrázka, nie generického textu.

Toto ukazuje, že Open WebUI dokáže odosielať multimodálne požiadavky (text + obrázok) cez backend (Lemonade) do modelu Vision.

---

<!-- @os:windows -->
### Aktivita 3: Generovanie obrázka z textového promptu (Stable Diffusion)

Modely Stable Diffusion nepodporujú generovanie textu, generujú iba obrázky prostredníctvom rozhrania Images API.

#### Krok 1: Konfigurácia generovania obrázkov v Open WebUI

1. V grafickom rozhraní Lemonade (`http://localhost:13305`) vyhľadajte `SDXL-Turbo` (rýchly) alebo `SDXL-Base-1.0` (vyššia kvalita) a stiahnite ho.
2. Prejdite na **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Nastavte:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` alebo `SDXL-Base-1.0`
4. Ak chcete pridať ďalšie parametre, pridajte ich do textového poľa vo formáte JSON. Napríklad: `{ "steps": 4, "cfg_scale": 1 }`. Dostupné parametre nájdete na [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Uložte
#### Krok 2: Povoliť generovanie obrázkov pre model
Tento krok zabezpečí, že povolíte generovanie obrázkov ako schopnosť vášho modelu.
1. Prejdite do **Admin Settings → Models** (http://localhost:8080/admin/settings/models) a vyberte svoj model
2. Zapnite `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Krok 3: Vygenerovanie obrázka z obrazovky chatu

1. Vráťte sa späť do chatu na `http://localhost:8080`.
2. V rozbaľovacej ponuke modelov vyberte **Text Generation LLM** (napríklad Qwen, Llama). **Nevyberajte model Stable Diffusion**, keďže ide o výber modelu pre chat.
3. V oblasti správy kliknite na **Integrations** a prepnite **Image** na ZAPNUTÉ.
4. Použite prompt napríklad: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Obrázok sa vygeneruje a zobrazí sa v chate.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Tým sa potvrdí, že Open WebUI dokáže koordinovať „dvojdielny" pracovný postup:
  - LLM pomáha spresniť prompt
  - Obrázok sa generuje cez koncový bod Images v Lemonade pomocou Stable Diffusion
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Aktivita 3: Vygenerovanie obrázka z textového promptu (Stable Diffusion)

Modely Stable Diffusion nepodporujú generovanie textu, generujú obrázky iba prostredníctvom Images API. 

#### Krok 1: Konfigurácia generovania obrázkov v Open WebUI

1. V grafickom rozhraní Lemonade (`http://localhost:13305`) vyhľadajte `SDXL-Turbo` (rýchly) alebo `SDXL-Base-1.0` (vyššia kvalita) a stiahnite si ho.
2. Prejdite do **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Nastavte:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` alebo `SDXL-Base-1.0`
4. Ak chcete pridať ďalšie parametre, pridajte ich do textového poľa vo formáte JSON. Napríklad: `{ "steps": 4, "cfg_scale": 1 }`. Dostupné parametre nájdete na stránke [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Uložte


#### Krok 2: Povoliť generovanie obrázkov pre model
Tento krok zabezpečí, že povolíte generovanie obrázkov ako schopnosť vášho modelu.
1. Prejdite do **Admin Settings → Models** (http://localhost:8080/admin/settings/models) a vyberte svoj model
2. Zapnite `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Krok 3: Vygenerovanie obrázka z obrazovky chatu

1. Vráťte sa späť do chatu na `http://localhost:8080`.
2. V rozbaľovacej ponuke modelov vyberte **Text Generation LLM** (napríklad Qwen, Llama). **Nevyberajte model Stable Diffusion**, keďže ide o výber modelu pre chat.
3. V oblasti správy kliknite na **Integrations** a prepnite **Image** na ZAPNUTÉ.
4. Použite prompt napríklad: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Obrázok sa vygeneruje a zobrazí sa v chate.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Tým sa potvrdí, že Open WebUI dokáže koordinovať „dvojdielny" pracovný postup:
  - LLM pomáha spresniť prompt
  - Obrázok sa generuje cez koncový bod Images v Lemonade pomocou Stable Diffusion
<!-- @device:end -->
<!-- @os:end -->

---

## Riešenie problémov

### „V Open WebUI sa nezobrazujú žiadne modely"
- Najprv skontrolujte Lemonade: otvorte `http://localhost:13305/api/v1/models` v prehliadači a potvrďte, že vaše modely sú uvedené v zozname a stiahnuté
- Potom skontrolujte pripojenie Open WebUI: prejdite do **Admin Settings → Connections** na `http://localhost:8080/admin/settings/connections` a overte, že Base URL je `http://localhost:13305/api/v1`

### Chybová správa „This model does not support chat completion"
- V rozbaľovacej ponuke modelov pre chat ste vybrali obrazový model (SDXL-Turbo / SDXL-Base-1.0).
- **Riešenie**: pre chat vyberte LLM a na generovanie použite prepínač Image + nastavenia Images.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Chyby/časové limity pri generovaní obrázkov
- Začnite najprv s `SDXL-Turbo` (rýchly, menej krokov)
- Keď to funguje, prepnite obrazový model na `SDXL-Base-1.0` pre vyššiu kvalitu

---

## Ďalšie kroky

Teraz máte funkčný **„lokálny AI stack"** — jedno rozhranie ovládajúce viacero typov modelov prostredníctvom štandardného API.

Tu sú tri rozšírenia, ktoré odomknú úplne nové pracovné postupy:

### 1. Prepis reči na text pomocou Whisper

Vyskúšajte premenu zvuku na text pomocou modelu Whisper a následne ho odovzdajte do LLM na sumarizáciu, vytvorenie zoznamu úloh alebo prepísanie. Toto je základ pre poznámky zo stretnutí a hlasom ovládaných asistentov.

### 2. Programovanie v Pythone priamo v Open WebUI

Použite vstavané prostredie na spúšťanie kódu v Open WebUI na spúšťanie ukážok kódu v Pythone, kontrolu výstupov a rýchlejšie iterácie — bez nutnosti opustiť rozhranie. [Referencia](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. Vykresľovanie HTML v Open WebUI

Vykresľujte HTML výstupy priamo v rozhraní. Toto je prekvapivo výkonná funkcia na vytváranie rýchlych prototypov, formátovaných reportov a interaktívnych ukážok. [Referencia](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## Referencie

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Dokumentácia Lemonade Server](https://lemonade-server.ai/docs)
- [Lemonade Server CLI](https://lemonade-server.ai/docs/lemonade-cli/)
- [Sprievodca integráciou Lemonade ↔ Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Špecifikácia API Lemonade Server (koncové body)](https://lemonade-server.ai/docs/server/server_spec)
- [Videonávod (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [Videonávod (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)

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