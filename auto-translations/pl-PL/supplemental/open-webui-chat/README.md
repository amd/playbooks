<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ten przewodnik wykorzystuje specjalne znaczniki, których GitHub nie potrafi wyrenderować. Odwiedź stronę [amd.com/playbooks](https://amd.com/playbooks), aby poprawnie wyświetlić tę treść.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Ten przewodnik wymaga co najmniej **32GB** pamięci systemowej.
<!-- @device:end -->

## Przegląd

[Open WebUI](https://docs.openwebui.com) to samodzielnie hostowany interfejs działający w przeglądarce, który zapewnia znajome doświadczenie chatbota, pełniąc jednocześnie rolę frontendu dla jednego lub wielu serwerów modeli AI. Zamiast być związanym z jednym dostawcą, Open WebUI może łączyć się z **dowolnym backendem udostępniającym API kompatybilne z OpenAI**, dzięki czemu możesz zmieniać modele i funkcje bez zmiany interfejsu.

W tym przewodniku jako backend wykorzystujemy [**Lemonade**](https://lemonade-server.ai), ponieważ udostępnia on **ujednolicony punkt końcowy kompatybilny z OpenAI**, obsługujący wiele modalności:
- **Duże modele językowe (LLM)** do generowania tekstu
- **Modele wizyjne** do rozumienia obrazów
- **Stable Diffusion** do generowania obrazów
- **Modele transkrypcji audio** do zamiany mowy na tekst

Taka konfiguracja pozwala na poznanie **całego, wielomodalnego przepływu pracy od początku do końca**.

---

## Czego się nauczysz

Po ukończeniu tego przewodnika będziesz potrafić:

- Połączyć Open WebUI z lokalnym backendem kompatybilnym z OpenAI (Lemonade)
- Prowadzić rozmowę z lokalnym modelem LLM z poziomu przeglądarki
- Przesłać obraz i zadawać modelowi wizyjnemu pytania na jego temat
- Generować obrazy na podstawie tekstowych promptów za pomocą modeli Stable Diffusion (SDXL-Turbo / SDXL)
- Zrozumieć model koncepcyjny, dzięki czemu będziesz mógł korzystać z innych backendów (Ollama, vLLM, llama.cpp server itd.)

---

## Kluczowe pojęcia (model koncepcyjny)

### Trzy komponenty

| Element | Co robi | Przykłady |
|---|---|---|
| Frontend (UI) | Aplikacja webowa, z którą wchodzisz w interakcję | Open WebUI |
| Backend (serwer modeli) | Hostuje modele i udostępnia punkty końcowe HTTP | Lemonade, Ollama, vLLM, llama.cpp server, serwery kompatybilne z OpenAI |
| Modele | Właściwe modele LLM / wizyjne / dyfuzyjne / audio | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### Dlaczego "API kompatybilne z OpenAI" ma znaczenie

Open WebUI został zbudowany wokół standardowych punktów końcowych w stylu OpenAI, takich jak:
  - Czat: `/chat/completions`
  - Lista modeli: `/models`
  - Generowanie obrazów: `/images/generations`
  - Transkrypcja audio: `/audio/transcriptions`

Lemonade udostępnia je pod adresem `http://localhost:13305/api/v1/...`

Jeśli backend obsługuje te punkty końcowe, Open WebUI może się z nim komunikować przy minimalnej konfiguracji. Dlatego możemy zmieniać backendy bez konieczności zmiany naszego przepływu pracy.

#### Dwie usługi, dwa porty

W trakcie tego przewodnika będziesz korzystać z dwóch osobnych usług:

| Usługa | URL | Co tam robisz |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | Przeglądaj, pobieraj i zarządzaj modelami |
| **Open WebUI** | `http://localhost:8080` | Prowadź rozmowy, przesyłaj obrazy, generuj obrazy — interfejs użytkownika |

Lemonade uruchamia modele; Open WebUI to interfejs, z którym wchodzisz w interakcję. Najpierw użyj GUI Lemonade, aby pobrać swoje modele, a następnie korzystaj z nich w Open WebUI.

---

## Ustawianie konfiguracji pamięci

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania

<!-- @require:software-update -->
<!-- @device:end -->

## Konfiguracja jednorazowa

Ten przewodnik wymaga uruchomienia Lemonade jako backendu, a w systemie Linux — silnika kontenerów (Podman) do uruchomienia Open WebUI. Skonfiguruj je przed instalacją Open WebUI.

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

## Pobieranie modeli w Lemonade

Przed instalacją Open WebUI upewnij się, że modele, których chcesz używać, zostały pobrane i są gotowe w Lemonade.

1. Otwórz GUI Lemonade pod adresem `http://localhost:13305`.
2. Przeglądaj dostępne modele i pobierz te, których chcesz użyć (np. model LLM do rozmów, model wizyjny i/lub model Stable Diffusion do generowania obrazów).
3. Potwierdź, że API jest dostępne, odwiedzając `http://localhost:13305/api/v1/models` w przeglądarce — powinieneś zobaczyć listę pobranych modeli.

> Modele muszą zostać pobrane w **Lemonade** (`localhost:13305`), zanim będą mogły pojawić się w **Open WebUI** (`localhost:8080`). Jeśli model nie pojawi się później w Open WebUI, wróć tutaj i sprawdź najpierw Lemonade.


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

## Instalacja Open WebUI

<!-- @os:windows -->
### 1. Instalacja Python 3.12

Open WebUI wymaga **Pythona 3.12** — nie instaluje się na Pythonie 3.13+. Windowsowy launcher Pythona (`py`) pozwala zainstalować wersję 3.12 obok już istniejącej wersji Pythona bez konfliktów.

```powershell
winget install Python.Python.3.12
```

Zamknij i ponownie otwórz terminal po instalacji, a następnie zweryfikuj:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Uwaga:** Twój system ma wstępnie zainstalowanego Pythona 3.13. Instalacja wersji 3.12 nie wpływa na niego — `python` nadal korzysta z 3.13, a `py -3.12` odwołuje się do wersji 3.12 tylko wtedy, gdy jej potrzebujesz.
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

### 2. Utworzenie środowiska wirtualnego i instalacja Open WebUI

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
Wykorzystamy teraz usługę Podman, aby skonteneryzować naszą instalację Open WebUI.

Pobierz poniższy plik do wybranego katalogu: [compose.yml](assets/compose.yml)

W tym katalogu uruchom następujące polecenie:

```bash
podman compose up -d
```

Spowoduje to pobranie obrazu Open WebUI i zapisanie danych w pamięci trwałej.

Uruchom Open WebUI, wpisując `localhost:8080` w pasku adresu przeglądarki.

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

> **Wskazówka**: Open WebUI oferuje również inne opcje instalacji, dostępne na ich [GitHub](https://github.com/open-webui/open-webui).
## Uruchamianie serwera Open WebUI

<!-- @os:windows -->
- Uruchom następujące polecenie, aby uruchomić serwer HTTP Open WebUI:
```bash
open-webui serve
```
<!-- @os:end -->

- W przeglądarce przejdź do `http://localhost:8080`.
- Open WebUI poprosi Cię o utworzenie lokalnego konta administratora. Po zalogowaniu zobaczysz interfejs czatu.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> Zostaw okno terminala otwarte. Zamknięcie go zatrzyma Open WebUI.
<!-- @os:end -->

<!-- @os:linux -->
> Kontener działa w tle. Z katalogu zawierającego `compose.yml`, zarządzaj nim za pomocą `podman compose down` (zatrzymanie) i `podman compose up -d` (uruchomienie). Twoje konta i ustawienia są zachowywane w woluminie `open_webui_data`.
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

## Łączenie Open WebUI z Lemonade

Teraz, gdy oba usługi są uruchomione — Lemonade na `localhost:13305` i Open WebUI na `localhost:8080` — połącz je, aby Open WebUI mogło korzystać z modeli Lemonade.

W Open WebUI:

1. Kliknij ikonę **profilu użytkownika** w prawym górnym rogu, a następnie wybierz **Ustawienia**.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. W panelu Ustawień kliknij **Ustawienia administratora** w lewym dolnym rogu.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. Na pasku bocznym Ustawień administratora kliknij **Połączenia** (lub przejdź bezpośrednio do `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. W sekcji **OpenAI API** dodaj nowe połączenie:
   - **Base URL:** `http://localhost:13305/api/v1`
   - **API Key:** `-` (pojedynczy myślnik działa lokalnie)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. Upewnij się, że w sekcji **„Manage OpenAI API Connections”** włączone jest tylko `http://localhost:13305/api/v1`. Wyłącz wszystkie inne połączenia (np. domyślne połączenie OpenAI).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. Kliknij **Zapisz**.

7. **(Zalecane)** Wyłącz funkcje automatycznego generowania, aby Open WebUI działało responsywnie z lokalnymi modelami LLM. Przejdź do **Ustawienia administratora → Ustawienia → Interfejs** i wyłącz:
   - Generowanie tytułu
   - Generowanie kontynuacji
   - Generowanie tagów

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. Kliknij **Zapisz**, a następnie wróć do `http://localhost:8080`.
9. Kliknij listę rozwijaną modeli — powinieneś zobaczyć modele pobrane z Lemonade.

---

## Główne działania

Teraz wszystko jest gotowe. Przyjrzyjmy się trzem interesującym rzeczom do zrobienia.

---

### Aktywność 1: Czat z lokalnym modelem LLM
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Kliknij menu rozwijane w lewym górnym rogu interfejsu. Wyświetli ono modele Lemonade, które masz zainstalowane. Wybierz jeden, aby kontynuować (przykład: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. Wpisz wiadomość do modelu LLM i kliknij wyślij (lub naciśnij Enter). Model LLM będzie się ładował do pamięci przez kilka sekund, a następnie zobaczysz strumień odpowiedzi.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Kliknij menu rozwijane w lewym górnym rogu interfejsu. Wyświetli ono modele Lemonade, które masz zainstalowane. Wybierz jeden, aby kontynuować (przykład: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Wpisz wiadomość do modelu LLM i kliknij wyślij (lub naciśnij Enter). Model LLM będzie się ładował do pamięci przez kilka sekund, a następnie zobaczysz strumień odpowiedzi.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. Model odpowie w czacie.

4. W tym momencie otwórz `Menedżer zadań` w swoim systemie. Zobaczysz **wysokie wykorzystanie GPU lub NPU**, w zależności od tego, czy wybrany model jest **Hybrydowy** czy **NPU**. Za pomocą menedżera zadań możesz potwierdzić, że model działa lokalnie.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Kliknij menu rozwijane w lewym górnym rogu interfejsu. Wyświetli ono modele Lemonade, które masz zainstalowane. Wybierz jeden, aby kontynuować (przykład: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Wpisz wiadomość do modelu LLM i kliknij wyślij (lub naciśnij Enter). Model LLM będzie się ładował do pamięci przez kilka sekund, a następnie zobaczysz strumień odpowiedzi.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. Model odpowie w czacie.
<!-- @os:end -->

To potwierdza, że Open WebUI może wysyłać żądania do Lemonade za pomocą punktu końcowego czatu zgodnego z OpenAI.

---

### Aktywność 2: Prześlij obraz i zadaj pytania (Wizja)

Wymaga to modelu obsługującego wejście obrazu (model Wizji lub Multimodalny).

1. Kliknij ikonę filtra, wybierz „Według kategorii”, a następnie wybierz model z sekcji **Wizja** (np. `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. Kliknij przycisk **`+`** w polu wiadomości i prześlij obraz
3. Zadaj pytanie wymuszające prawdziwe zrozumienie obrazu: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. Model odpowiada na podstawie zawartości obrazu, a nie ogólnego tekstu.

To pokazuje, że Open WebUI może wysyłać żądania multimodalne (tekst + obraz) przez backend (Lemonade) do modelu wizji.

---

<!-- @os:windows -->
### Aktywność 3: Generowanie obrazu na podstawie polecenia tekstowego (Stable Diffusion)

Modele Stable Diffusion nie obsługują generowania tekstu, generują jedynie obrazy poprzez API Images.

#### Krok 1: Konfiguracja generowania obrazów w Open WebUI

1. W GUI Lemonade (`http://localhost:13305`), wyszukaj `SDXL-Turbo` (szybszy) lub `SDXL-Base-1.0` (wyższa jakość) i pobierz go.
2. Przejdź do **Ustawienia administratora → Obrazy** (http://localhost:8080/admin/settings/images)
3. Ustaw:
   - **Generowanie obrazów:** WŁ.
   - **Silnik generowania obrazów:** Domyślny (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` lub `SDXL-Base-1.0`
4. Jeśli chcesz dodać więcej parametrów, dodaj je do pola tekstowego w formacie JSON. Na przykład: `{ "steps": 4, "cfg_scale": 1 }`. Dostępne parametry znajdziesz w [Generowanie obrazów (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Zapisz
#### Krok 2: Zezwól na generowanie obrazów dla modelu
Ten krok zapewnia włączenie generowania obrazów jako możliwości Twojego modelu.
1. Przejdź do **Admin Settings → Models** (http://localhost:8080/admin/settings/models) i wybierz swój model
2. Włącz `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Krok 3: Wygeneruj obraz z poziomu ekranu czatu

1. Wróć do czatu pod adresem `http://localhost:8080`.
2. Wybierz **Text Generation LLM** z rozwijanej listy modeli (przykład: Qwen, Llama). **Nie wybieraj modelu Stable Diffusion**, ponieważ jest to selektor modelu czatu.
3. W obszarze wiadomości kliknij **Integrations** i włącz przełącznik **Image**.
4. Użyj promptu takiego jak: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Obraz zostaje wygenerowany i pojawia się w czacie.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

To pokazuje, że Open WebUI może koordynować „dwuczęściowy" przepływ pracy:
  - LLM pomaga dopracować prompt
  - Obraz jest generowany za pomocą endpointu Images Lemonade z użyciem Stable Diffusion
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Aktywność 3: Generowanie obrazu z promptu tekstowego (Stable Diffusion)

Modele Stable Diffusion nie obsługują generowania tekstu, generują obrazy wyłącznie za pomocą API Images.

#### Krok 1: Skonfiguruj generowanie obrazów w Open WebUI

1. W GUI Lemonade (`http://localhost:13305`), wyszukaj `SDXL-Turbo` (szybki) lub `SDXL-Base-1.0` (wyższa jakość) i pobierz go.
2. Przejdź do **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Ustaw:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` lub `SDXL-Base-1.0`
4. Jeśli chcesz dodać więcej parametrów, dodaj je do pola tekstowego w formacie JSON. Na przykład: `{ "steps": 4, "cfg_scale": 1 }`. Zobacz dostępne parametry w [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Zapisz


#### Krok 2: Zezwól na generowanie obrazów dla modelu
Ten krok zapewnia włączenie generowania obrazów jako możliwości Twojego modelu.
1. Przejdź do **Admin Settings → Models** (http://localhost:8080/admin/settings/models) i wybierz swój model
2. Włącz `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Krok 3: Wygeneruj obraz z poziomu ekranu czatu

1. Wróć do czatu pod adresem `http://localhost:8080`.
2. Wybierz **Text Generation LLM** z rozwijanej listy modeli (przykład: Qwen, Llama). **Nie wybieraj modelu Stable Diffusion**, ponieważ jest to selektor modelu czatu.
3. W obszarze wiadomości kliknij **Integrations** i włącz przełącznik **Image**.
4. Użyj promptu takiego jak: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Obraz zostaje wygenerowany i pojawia się w czacie.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

To pokazuje, że Open WebUI może koordynować „dwuczęściowy" przepływ pracy:
  - LLM pomaga dopracować prompt
  - Obraz jest generowany za pomocą endpointu Images Lemonade z użyciem Stable Diffusion
<!-- @device:end -->
<!-- @os:end -->

---

## Rozwiązywanie problemów

### „Żadne modele nie pojawiają się w Open WebUI"
- Najpierw sprawdź Lemonade: otwórz `http://localhost:13305/api/v1/models` w przeglądarce i potwierdź, że Twoje modele są wymienione i pobrane
- Następnie sprawdź połączenie Open WebUI: przejdź do **Admin Settings → Connections** pod adresem `http://localhost:8080/admin/settings/connections` i zweryfikuj, że Base URL to `http://localhost:13305/api/v1`

### Komunikat błędu „This model does not support chat completion"
- Wybrano model obrazu (SDXL-Turbo / SDXL-Base-1.0) w rozwijanej liście modeli czatu.
- **Rozwiązanie**: wybierz LLM do czatu i użyj przełącznika Image oraz ustawień Images do generowania.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Błędy/przekroczenia czasu generowania obrazu
- Zacznij od `SDXL-Turbo` (szybki, mniej kroków)
- Gdy działa poprawnie, przełącz model obrazu na `SDXL-Base-1.0` dla wyższej jakości

---

## Kolejne kroki

Masz teraz działający **„lokalny stos AI"**, jeden interfejs kontrolujący wiele typów modeli za pomocą standardowego API.

Oto trzy rozszerzenia, które odblokowują zupełnie nowe przepływy pracy:

### 1. Zamiana mowy na tekst za pomocą Whisper

Spróbuj zamienić dźwięk na tekst za pomocą modelu Whisper, a następnie przekaż go do LLM w celu podsumowania, wyodrębnienia zadań lub przepisania. To podstawa dla notatek ze spotkań i asystentów sterowanych głosem.

### 2. Kodowanie w Pythonie w Open WebUI

Skorzystaj z wbudowanego w Open WebUI środowiska wykonywania kodu, aby uruchamiać fragmenty kodu w Pythonie, sprawdzać wyniki i iterować szybciej — bez opuszczania interfejsu. [Odniesienie](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. Renderowanie HTML w Open WebUI

Renderuj wyniki HTML bezpośrednio w interfejsie. Jest to zaskakująco przydatne przy budowaniu szybkich prototypów, sformatowanych raportów i interaktywnych fragmentów kodu. [Odniesienie](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## Odnośniki

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Dokumentacja Lemonade Server](https://lemonade-server.ai/docs)
- [Lemonade Server CLI](https://lemonade-server.ai/docs/lemonade-cli/)
- [Przewodnik integracji Lemonade ↔ Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Specyfikacja API Lemonade Server (endpointy)](https://lemonade-server.ai/docs/server/server_spec)
- [Przewodnik wideo (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [Przewodnik wideo (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)