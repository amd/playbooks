<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Tato příručka vyžaduje minimálně **32GB** systémové paměti.
<!-- @device:end -->

## Přehled

[Open WebUI](https://docs.openwebui.com) je samostatně hostované, prohlížečové rozhraní, které poskytuje známý zážitek z chatbotu a zároveň funguje jako frontend pro jeden nebo více serverů s AI modely. Namísto vazby na jednoho poskytovatele se Open WebUI dokáže připojit k **jakémukoli backendu, který vystavuje API kompatibilní s OpenAI**, takže můžete přepínat modely a funkce bez nutnosti měnit uživatelské rozhraní.

V této příručce používáme jako backend [**Lemonade**](https://lemonade-server.ai), protože poskytuje **jednotný koncový bod kompatibilní s OpenAI**, který podporuje více modalit:
- **Velké jazykové modely (LLM)** pro generování textu
- **Vizuální modely** pro porozumění obrázkům
- **Stable Diffusion** pro generování obrázků
- **Modely pro přepis zvuku** pro převod řeči na text

Toto nastavení vám umožní prozkoumat **kompletní multimodální pracovní postup od začátku do konce**.

---

## Co se naučíte

Na konci budete schopni:

- Připojit Open WebUI k lokálnímu backendu kompatibilnímu s OpenAI (Lemonade)
- Chatovat s lokálním LLM přímo z prohlížeče
- Nahrát obrázek a klást vizuálnímu modelu otázky týkající se jeho obsahu
- Generovat obrázky z textových promptů pomocí modelů Stable Diffusion (SDXL-Turbo / SDXL)
- Pochopit mentální model, abyste mohli používat i jiné backendy (Ollama, vLLM, llama.cpp server atd.)

---

## Základní koncepty (mentální model)

### Tři součásti

| Součást | Co dělá | Příklady |
|---|---|---|
| Frontend (UI) | Webová aplikace, se kterou pracujete | Open WebUI |
| Backend (server modelů) | Hostuje modely a vystavuje HTTP koncové body | Lemonade, Ollama, vLLM, llama.cpp server, servery kompatibilní s OpenAI |
| Modely | Skutečné LLM / vizuální / difuzní / zvukové modely | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### Proč záleží na „API kompatibilním s OpenAI“

Open WebUI je postaveno na standardních koncových bodech ve stylu OpenAI, například:
  - Chat: `/chat/completions`
  - Seznam modelů: `/models`
  - Generování obrázků: `/images/generations`
  - Přepis zvuku: `/audio/transcriptions`

Lemonade tyto koncové body vystavuje pod adresou `http://localhost:13305/api/v1/...`

Pokud backend tyto koncové body podporuje, dokáže s ním Open WebUI komunikovat s minimálním nastavením. Právě proto můžeme backendy přepínat, aniž bychom museli měnit náš pracovní postup.

#### Dvě služby, dva porty

V rámci této příručky budete pracovat se dvěma samostatnými službami:

| Služba | URL | Co zde děláte |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | Procházení, stahování a správa modelů |
| **Open WebUI** | `http://localhost:8080` | Chatování, nahrávání obrázků, generování obrázků — uživatelské rozhraní |

Lemonade spouští modely; Open WebUI je rozhraní, se kterým pracujete vy. Nejprve použijte GUI Lemonade ke stažení modelů a poté je používejte z Open WebUI.

---

## Nastavení konfigurace paměti

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru

<!-- @require:software-update -->
<!-- @device:end -->

## Jednorázové nastavení

Tato příručka vyžaduje spuštěný Lemonade jako backend a v systému Linux také kontejnerový engine (Podman) pro spuštění Open WebUI. Než nainstalujete Open WebUI, nastavte nejprve toto.

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

## Stahování modelů v Lemonade

Než nainstalujete Open WebUI, ujistěte se, že modely, které chcete používat, jsou v Lemonade stažené a připravené k použití.

1. Otevřete GUI Lemonade na adrese `http://localhost:13305`.
2. Projděte si dostupné modely a stáhněte ty, které chcete používat (např. LLM pro chat, vizuální model a/nebo model Stable Diffusion pro generování obrázků).
3. Ověřte, že je API dostupné, tím, že navštívíte `http://localhost:13305/api/v1/models` ve svém prohlížeči — měli byste vidět seznam stažených modelů.

> Modely musí být stažené v **Lemonade** (`localhost:13305`), než se mohou objevit v **Open WebUI** (`localhost:8080`). Pokud se model v Open WebUI později nezobrazí, vraťte se sem a nejprve zkontrolujte Lemonade.


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

## Instalace Open WebUI

<!-- @os:windows -->
### 1. Instalace Python 3.12

Open WebUI vyžaduje **Python 3.12** — na Python 3.13+ se neinstaluje. Windows Python Launcher (`py`) umožňuje nainstalovat verzi 3.12 vedle jakékoli existující verze Pythonu bez konfliktů.

```powershell
winget install Python.Python.3.12
```

Po instalaci terminál zavřete a znovu otevřete a poté proveďte ověření:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Poznámka:** Váš systém je předinstalovaný s Pythonem 3.13. Instalace verze 3.12 na to nemá vliv — `python` nadále používá verzi 3.13 a `py -3.12` cílí na verzi 3.12 pouze tehdy, když ji potřebujete.
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

### 2. Vytvoření virtuálního prostředí a instalace Open WebUI

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
Nyní použijeme službu Podman k containerizaci naší instalace Open WebUI.

Stáhněte prosím následující soubor do adresáře dle vlastního výběru: [compose.yml](assets/compose.yml)

V tomto adresáři spusťte následující příkaz:

```bash
podman compose up -d
```

Tím se stáhne obraz Open WebUI a data se zapíší do trvalého úložiště.

Spusťte Open WebUI zadáním `localhost:8080` do adresního řádku prohlížeče.

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

> **Tip**: Open WebUI nabízí na svém [GitHub](https://github.com/open-webui/open-webui) i další možnosti instalace.
## Spuštění serveru Open WebUI

<!-- @os:windows -->
- Spusťte následující příkaz pro spuštění HTTP serveru Open WebUI:
```bash
open-webui serve
```
<!-- @os:end -->

- V prohlížeči přejděte na `http://localhost:8080`.
- Open WebUI vás vyzve k vytvoření lokálního administrátorského účtu. Jakmile se přihlásíte, uvidíte rozhraní chatu.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> Ponechte okno terminálu otevřené. Jeho zavřením se Open WebUI zastaví.
<!-- @os:end -->

<!-- @os:linux -->
> Kontejner běží na pozadí. Z adresáře obsahujícího `compose.yml` jej spravujte pomocí `podman compose down` (zastavení) a `podman compose up -d` (spuštění). Vaše účty a nastavení se uchovávají ve svazku `open_webui_data`.
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

## Propojení Open WebUI s Lemonade

Nyní, když obě služby běží — Lemonade na `localhost:13305` a Open WebUI na `localhost:8080` — je propojte, aby Open WebUI mohlo využívat modely Lemonade.

V Open WebUI:

1. Klikněte na **ikonu uživatelského profilu** v pravém horním rohu a poté vyberte **Nastavení**.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. V panelu Nastavení klikněte na **Administrátorské nastavení** vlevo dole.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. V postranním panelu Administrátorské nastavení klikněte na **Připojení** (nebo přejděte přímo na `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. V sekci **OpenAI API** přidejte nové připojení:
   - **Základní URL:** `http://localhost:13305/api/v1`
   - **API klíč:** `-` (pro lokální použití funguje jedna pomlčka)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. Ujistěte se, že v sekci **„Spravovat připojení OpenAI API“** je povoleno pouze `http://localhost:13305/api/v1`. Zakažte všechna ostatní připojení (např. výchozí připojení OpenAI).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. Klikněte na **Uložit**.

7. **(Doporučeno)** Zakažte funkce automatického generování, aby Open WebUI zůstalo responzivní při použití lokálních LLM. Přejděte na **Administrátorské nastavení → Nastavení → Rozhraní** a vypněte:
   - Generování názvu
   - Generování navazujících otázek
   - Generování štítků

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. Klikněte na **Uložit** a poté se vraťte na `http://localhost:8080`.
9. Klikněte na rozbalovací nabídku modelů — měli byste vidět modely, které jste stáhli z Lemonade.

---

## Hlavní činnosti

Nyní máte vše nastaveno. Pojďme se podívat na tři zajímavé věci, které lze dělat.

---

### Aktivita 1: Chat s lokálním LLM
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Klikněte na rozbalovací nabídku v levém horním rohu rozhraní. Zobrazí se nainstalované modely Lemonade. Vyberte jeden z nich (příklad: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. Zadejte zprávu pro LLM a klikněte na odeslání (nebo stiskněte Enter). Načtení LLM do paměti bude trvat několik sekund a poté uvidíte postupně přicházející odpověď.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Klikněte na rozbalovací nabídku v levém horním rohu rozhraní. Zobrazí se nainstalované modely Lemonade. Vyberte jeden z nich (příklad: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Zadejte zprávu pro LLM a klikněte na odeslání (nebo stiskněte Enter). Načtení LLM do paměti bude trvat několik sekund a poté uvidíte postupně přicházející odpověď.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. Model odpoví v chatu.

4. V tuto chvíli otevřete ve svém systému `Správce úloh`. Uvidíte **vysoké využití GPU nebo NPU** podle toho, zda je vybraný model **Hybrid**, nebo **NPU**. Pomocí správce úloh můžete potvrdit, že model spouštíte lokálně.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Klikněte na rozbalovací nabídku v levém horním rohu rozhraní. Zobrazí se nainstalované modely Lemonade. Vyberte jeden z nich (příklad: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Zadejte zprávu pro LLM a klikněte na odeslání (nebo stiskněte Enter). Načtení LLM do paměti bude trvat několik sekund a poté uvidíte postupně přicházející odpověď.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. Model odpoví v chatu.
<!-- @os:end -->

Tím se ověří, že Open WebUI dokáže odesílat požadavky do Lemonade pomocí koncového bodu chatu kompatibilního s OpenAI.

---

### Aktivita 2: Nahrání obrázku a kladení otázek (Vision)

Toto vyžaduje model, který podporuje vstup obrázků (model Vision nebo Multimodal).

1. Klikněte na ikonu filtru, vyberte „Podle kategorie“ a poté zvolte model ze sekce **Vision** (např. `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. Klikněte na tlačítko **`+`** v poli pro zprávu a nahrajte obrázek
3. Zeptejte se na něco, co vyžaduje skutečné porozumění obrázku: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. Model odpoví na základě obsahu obrázku, nikoli obecným textem.

Tím se prokáže, že Open WebUI dokáže odesílat multimodální požadavky (text + obrázek) přes backend (Lemonade) do modelu Vision.

---

<!-- @os:windows -->
### Aktivita 3: Generování obrázku z textového promptu (Stable Diffusion)

Modely Stable Diffusion nepodporují generování textu, generují pouze obrázky pomocí Images API. 

#### Krok 1: Konfigurace generování obrázků v Open WebUI

1. V grafickém rozhraní Lemonade (`http://localhost:13305`) vyhledejte `SDXL-Turbo` (rychlý) nebo `SDXL-Base-1.0` (vyšší kvalita) a stáhněte jej.
2. Přejděte na **Administrátorské nastavení → Obrázky** (http://localhost:8080/admin/settings/images)
3. Nastavte:
   - **Generování obrázků:** ZAPNUTO
   - **Engine generování obrázků:** Výchozí (OpenAI)
   - **Základní URL OpenAI API:** `http://localhost:13305/api/v1`
   - **API klíč OpenAI:** `-`
   - **Model:** `SDXL-Turbo` nebo `SDXL-Base-1.0`
4. Pokud chcete přidat další parametry, vložte je do textového pole ve formátu JSON. Například: `{ "steps": 4, "cfg_scale": 1 }`. Dostupné parametry najdete na stránce [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Uložit
#### Krok 2: Povolení generování obrázků pro model
Tento krok zajistí, že pro váš model povolíte generování obrázků jako schopnost.
1. Přejděte do **Admin Settings → Models** (http://localhost:8080/admin/settings/models) a vyberte svůj model
2. Zapněte `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Krok 3: Generování obrázku z obrazovky chatu

1. Vraťte se zpět do chatu na `http://localhost:8080`.
2. V rozbalovací nabídce modelů vyberte **LLM pro generování textu** (například Qwen, Llama). **Nevybírejte model Stable Diffusion**, protože se jedná o výběr chatovacího modelu.
3. V oblasti zprávy klikněte na **Integrations** a přepněte **Image** na ON.
4. Použijte prompt jako: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Vygeneruje se obrázek a zobrazí se v chatu.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Tím se prokáže, že Open WebUI dokáže koordinovat "dvoudílný" pracovní postup:
  - LLM pomáhá zpřesnit prompt
  - Obrázek se generuje přes koncový bod Images v Lemonade pomocí Stable Diffusion
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Aktivita 3: Generování obrázku z textového promptu (Stable Diffusion)

Modely Stable Diffusion nepodporují generování textu, generují obrázky pouze prostřednictvím API Images. 

#### Krok 1: Konfigurace generování obrázků v Open WebUI

1. V grafickém rozhraní Lemonade (`http://localhost:13305`) vyhledejte `SDXL-Turbo` (rychlý) nebo `SDXL-Base-1.0` (vyšší kvalita) a stáhněte jej.
2. Přejděte do **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Nastavte:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` nebo `SDXL-Base-1.0`
4. Pokud chcete přidat další parametry, přidejte je do textového pole ve formátu JSON. Například: `{ "steps": 4, "cfg_scale": 1 }`. Dostupné parametry naleznete na stránce [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Uložte


#### Krok 2: Povolení generování obrázků pro model
Tento krok zajistí, že pro váš model povolíte generování obrázků jako schopnost.
1. Přejděte do **Admin Settings → Models** (http://localhost:8080/admin/settings/models) a vyberte svůj model
2. Zapněte `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Krok 3: Generování obrázku z obrazovky chatu

1. Vraťte se zpět do chatu na `http://localhost:8080`.
2. V rozbalovací nabídce modelů vyberte **LLM pro generování textu** (například Qwen, Llama). **Nevybírejte model Stable Diffusion**, protože se jedná o výběr chatovacího modelu.
3. V oblasti zprávy klikněte na **Integrations** a přepněte **Image** na ON.
4. Použijte prompt jako: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Vygeneruje se obrázek a zobrazí se v chatu.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Tím se prokáže, že Open WebUI dokáže koordinovat "dvoudílný" pracovní postup:
  - LLM pomáhá zpřesnit prompt
  - Obrázek se generuje přes koncový bod Images v Lemonade pomocí Stable Diffusion
<!-- @device:end -->
<!-- @os:end -->

---

## Řešení problémů

### "V Open WebUI se nezobrazují žádné modely"
- Nejprve zkontrolujte Lemonade: otevřete `http://localhost:13305/api/v1/models` v prohlížeči a ověřte, že jsou vaše modely uvedeny v seznamu a stažené
- Poté zkontrolujte připojení Open WebUI: přejděte do **Admin Settings → Connections** na `http://localhost:8080/admin/settings/connections` a ověřte, že Base URL je `http://localhost:13305/api/v1`

### Chybová zpráva "This model does not support chat completion"
- V rozbalovací nabídce chatovacího modelu jste vybrali obrazový model (SDXL-Turbo / SDXL-Base-1.0).
- **Řešení**: vyberte pro chat LLM a pro generování použijte přepínač Image a nastavení Images.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Chyby/timeouty při generování obrázků
- Nejprve začněte s `SDXL-Turbo` (rychlé, méně kroků)
- Jakmile to funguje, přepněte obrazový model na `SDXL-Base-1.0` kvůli kvalitě

---

## Další kroky

Nyní máte funkční **„lokální AI stack“**, jednotné uživatelské rozhraní ovládající více typů modelů prostřednictvím standardního API.

Zde jsou tři rozšíření, která odemykají zcela nové pracovní postupy:

### 1. Převod řeči na text pomocí Whisper

Zkuste převést zvuk na text pomocí modelu Whisper a poté jej vložit do LLM pro shrnutí, seznam úkolů nebo přepsání. To je základ pro poznámky ze schůzek a hlasem řízené asistenty.

### 2. Programování v Pythonu uvnitř Open WebUI

Použijte vestavěné prostředí pro spouštění kódu v Open WebUI ke spouštění úryvků kódu v Pythonu, kontrole výstupů a rychlejší iteraci — bez opuštění uživatelského rozhraní. [Odkaz](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. Vykreslování HTML uvnitř Open WebUI

Vykreslujte výstupy HTML přímo v rozhraní. To je překvapivě užitečné pro vytváření rychlých prototypů, formátovaných zpráv a interaktivních úryvků. [Odkaz](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## Odkazy

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Dokumentace Lemonade Server](https://lemonade-server.ai/docs)
- [CLI pro Lemonade Server](https://lemonade-server.ai/docs/lemonade-cli/)
- [Průvodce integrací Lemonade ↔ Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Specifikace API Lemonade Server (koncové body)](https://lemonade-server.ai/docs/server/server_spec)
- [Video návod (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [Video návod (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)

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