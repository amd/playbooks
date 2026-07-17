<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> This playbook requires a minimum of **32GB** of system memory.
<!-- @device:end -->

## Обзор

[Open WebUI](https://docs.openwebui.com) — это самостоятельно размещаемый браузерный интерфейс, предоставляющий привычный опыт работы с чат-ботом и выступающий в роли фронтенда для одного или нескольких серверов AI-моделей. Вместо привязки к одному провайдеру Open WebUI может подключаться к **любому бэкенду, предоставляющему OpenAI-совместимый API**, что позволяет менять модели и возможности без смены интерфейса.

В этом руководстве мы используем [**Lemonade**](https://lemonade-server.ai) в качестве бэкенда, поскольку он предоставляет **единую OpenAI-совместимую конечную точку**, поддерживающую несколько модальностей:
- **Большие языковые модели (LLM)** для генерации текста
- **Модели зрения** для понимания изображений
- **Stable Diffusion** для генерации изображений
- **Модели транскрипции аудио** для преобразования речи в текст

Эта конфигурация позволяет изучить **полный мультимодальный рабочий процесс от начала до конца**.

---

## Чему вы научитесь

По завершении вы сможете:

- Подключить Open WebUI к локальному OpenAI-совместимому бэкенду (Lemonade)
- Общаться с локальной LLM через браузер
- Загружать изображения и задавать вопросы модели зрения о них
- Генерировать изображения по текстовым подсказкам с помощью моделей Stable Diffusion (SDXL-Turbo / SDXL)
- Понять концептуальную модель, чтобы использовать другие бэкенды (Ollama, vLLM, llama.cpp server и др.)

---

## Основные концепции (концептуальная модель)

### Три компонента

| Компонент | Что делает | Примеры |
|---|---|---|
| Фронтенд (UI) | Веб-приложение, с которым вы взаимодействуете | Open WebUI |
| Бэкенд (сервер моделей) | Размещает модели и предоставляет HTTP-конечные точки | Lemonade, Ollama, vLLM, llama.cpp server, OpenAI-совместимые серверы |
| Модели | Фактические LLM / модели зрения / диффузии / аудио | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### Почему важен «OpenAI-совместимый API»

Open WebUI построен вокруг стандартных конечных точек в стиле OpenAI, таких как:
  - Чат: `/chat/completions`
  - Список моделей: `/models`
  - Генерация изображений: `/images/generations`
  - Транскрипция аудио: `/audio/transcriptions`

Lemonade предоставляет их по адресу `http://localhost:13305/api/v1/...`

Если бэкенд поддерживает эти конечные точки, Open WebUI может взаимодействовать с ним при минимальной настройке. Именно поэтому мы можем менять бэкенды, не изменяя рабочий процесс.

#### Два сервиса, два порта

На протяжении всего руководства вы будете работать с двумя отдельными сервисами:

| Сервис | URL | Что вы там делаете |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | Просматриваете, загружаете и управляете моделями |
| **Open WebUI** | `http://localhost:8080` | Общаетесь в чате, загружаете изображения, генерируете изображения — пользовательский интерфейс |

Lemonade запускает модели; Open WebUI — это интерфейс, с которым вы взаимодействуете. Используйте GUI Lemonade для загрузки моделей, а затем работайте с ними через Open WebUI.

---

## Настройка конфигурации памяти

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Проверка обновлений программного обеспечения

<!-- @require:software-update -->
<!-- @device:end -->

## Первоначальная настройка

Для этого руководства необходимо, чтобы Lemonade работал в качестве бэкенда, а в Linux — контейнерный движок (Podman) для запуска Open WebUI. Настройте их перед установкой Open WebUI.

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

## Загрузка моделей в Lemonade

Перед установкой Open WebUI убедитесь, что нужные модели загружены и готовы в Lemonade.

1. Откройте GUI Lemonade по адресу `http://localhost:13305`.
2. Просмотрите доступные модели и загрузите те, которые хотите использовать (например, LLM для чата, модель зрения и/или модель Stable Diffusion для генерации изображений).
3. Убедитесь, что API доступен, открыв `http://localhost:13305/api/v1/models` в браузере — вы должны увидеть список загруженных моделей.

> Модели должны быть загружены в **Lemonade** (`localhost:13305`), прежде чем они смогут появиться в **Open WebUI** (`localhost:8080`). Если модель не отображается в Open WebUI, вернитесь сюда и сначала проверьте Lemonade.


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

## Установка Open WebUI

<!-- @os:windows -->
### 1. Установите Python 3.12

Open WebUI требует **Python 3.12** — он не устанавливается на Python 3.13+. Лаунчер Python для Windows (`py`) позволяет установить 3.12 параллельно с любой существующей версией Python без конфликтов.

```powershell
winget install Python.Python.3.12
```

Закройте и снова откройте терминал после установки, затем проверьте:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Примечание:** В вашей системе предустановлен Python 3.13. Установка 3.12 не влияет на него — `python` продолжает использовать 3.13, а `py -3.12` обращается к 3.12 только когда это необходимо.
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

### 2. Создайте виртуальное окружение и установите Open WebUI

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
Теперь мы воспользуемся сервисом Podman для контейнеризации нашей установки Open WebUI.

Пожалуйста, загрузите следующий файл в выбранный вами каталог: [compose.yml](assets/compose.yml)

В этом каталоге выполните следующую команду:

```bash
podman compose up -d
```

Это загрузит образ Open WebUI и запишет данные в постоянное хранилище.

Запустите Open WebUI, введя `localhost:8080` в адресную строку браузера.

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

> **Совет**: Open WebUI также предоставляет другие варианты установки на своём [GitHub](https://github.com/open-webui/open-webui).

## Запуск сервера Open WebUI

<!-- @os:windows -->
- Выполните следующую команду для запуска HTTP-сервера Open WebUI:
```bash
open-webui serve
```
<!-- @os:end -->

- В браузере перейдите по адресу `http://localhost:8080`.
- Open WebUI предложит вам создать локальную учётную запись администратора. После входа в систему вы увидите интерфейс чата.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> Не закрывайте окно терминала. Его закрытие остановит Open WebUI.
<!-- @os:end -->

<!-- @os:linux -->
> Контейнер работает в фоновом режиме. Из каталога, содержащего `compose.yml`, управляйте им с помощью `podman compose down` (остановка) и `podman compose up -d` (запуск). Ваши учётные записи и настройки сохраняются в томе `open_webui_data`.
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

## Подключение Open WebUI к Lemonade

Теперь, когда оба сервиса запущены — Lemonade на `localhost:13305` и Open WebUI на `localhost:8080` — подключите их, чтобы Open WebUI мог использовать модели Lemonade.

В Open WebUI:

1. Нажмите **значок профиля пользователя** в правом верхнем углу, затем выберите **Настройки**.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. На панели настроек нажмите **Настройки администратора** в нижнем левом углу.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. На боковой панели настроек администратора нажмите **Подключения** (или перейдите напрямую по адресу `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. В разделе **OpenAI API** добавьте новое подключение:
   - **Базовый URL:** `http://localhost:13305/api/v1`
   - **Ключ API:** `-` (одиночный дефис работает для локального подключения)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. Убедитесь, что в разделе **«Управление подключениями OpenAI API»** включён только `http://localhost:13305/api/v1`. Отключите все остальные подключения (например, стандартное подключение к OpenAI).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. Нажмите **Сохранить**.

7. **(Рекомендуется)** Отключите функции автоматической генерации, чтобы Open WebUI оставался отзывчивым при работе с локальными LLM. Перейдите в **Настройки администратора → Настройки → Интерфейс** и отключите:
   - Генерацию заголовков
   - Генерацию продолжений
   - Генерацию тегов

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. Нажмите **Сохранить**, затем вернитесь на `http://localhost:8080`.
9. Нажмите на выпадающий список моделей — вы должны увидеть модели, загруженные из Lemonade.

---

## Основные задания

Теперь всё готово. Давайте рассмотрим три интересных варианта использования.

---

### Задание 1: Общение с локальной LLM
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Нажмите на выпадающее меню в верхнем левом углу интерфейса. Отобразятся установленные модели Lemonade. Выберите одну для продолжения (например: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. Введите сообщение для LLM и нажмите «Отправить» (или Enter). LLM потребуется несколько секунд для загрузки в память, после чего вы увидите потоковый вывод ответа.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Нажмите на выпадающее меню в верхнем левом углу интерфейса. Отобразятся установленные модели Lemonade. Выберите одну для продолжения (например: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Введите сообщение для LLM и нажмите «Отправить» (или Enter). LLM потребуется несколько секунд для загрузки в память, после чего вы увидите потоковый вывод ответа.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. Модель ответит в чате.

4. Сейчас откройте `Диспетчер задач` на вашей системе. Вы увидите **высокую загрузку GPU или NPU** в зависимости от того, является ли выбранная модель **Hybrid** или **NPU** соответственно. С помощью диспетчера задач вы можете убедиться, что модель работает локально.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Нажмите на выпадающее меню в верхнем левом углу интерфейса. Отобразятся установленные модели Lemonade. Выберите одну для продолжения (например: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Введите сообщение для LLM и нажмите «Отправить» (или Enter). LLM потребуется несколько секунд для загрузки в память, после чего вы увидите потоковый вывод ответа.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. Модель ответит в чате.
<!-- @os:end -->

Это подтверждает, что Open WebUI может отправлять запросы в Lemonade через OpenAI-совместимую конечную точку чата.

---

### Задание 2: Загрузка изображения и вопросы к нему (зрение)

Для этого требуется модель, поддерживающая ввод изображений (модель зрения или мультимодальная модель).

1. Нажмите на значок фильтра, выберите «По категории», затем выберите модель из раздела **Зрение** (например, `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. Нажмите кнопку **`+`** в поле сообщения и загрузите изображение
3. Задайте вопрос, требующий истинного понимания изображения: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. Модель отвечает на основе содержимого изображения, а не общего текста.

Это демонстрирует, что Open WebUI может отправлять мультимодальные запросы (текст + изображение) через бэкенд (Lemonade) в модель зрения.

---

<!-- @os:windows -->
### Задание 3: Генерация изображения по текстовой подсказке (Stable Diffusion)

Модели Stable Diffusion не поддерживают генерацию текста — они генерируют только изображения через Images API.

#### Шаг 1: Настройка генерации изображений в Open WebUI

1. В GUI Lemonade (`http://localhost:13305`) найдите `SDXL-Turbo` (быстрый) или `SDXL-Base-1.0` (более высокое качество) и загрузите его.
2. Перейдите в **Настройки администратора → Изображения** (http://localhost:8080/admin/settings/images)
3. Установите:
   - **Генерация изображений:** ВКЛ
   - **Движок генерации изображений:** По умолчанию (OpenAI)
   - **Базовый URL OpenAI API:** `http://localhost:13305/api/v1`
   - **Ключ OpenAI API:** `-`
   - **Модель:** `SDXL-Turbo` или `SDXL-Base-1.0`
4. Если вы хотите добавить дополнительные параметры, введите их в текстовое поле в формате JSON. Например: `{ "steps": 4, "cfg_scale": 1 }`. Доступные параметры см. на странице [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Сохраните


#### Шаг 2: Разрешите генерацию изображений для модели
Этот шаг обеспечивает включение генерации изображений как возможности для вашей модели.
1. Перейдите в **Настройки администратора → Модели** (http://localhost:8080/admin/settings/models) и выберите свою модель
2. Включите `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Шаг 3: Сгенерируйте изображение из экрана чата

1. Вернитесь в чат по адресу `http://localhost:8080`.
2. Выберите **LLM для генерации текста** в выпадающем списке моделей (например: Qwen, Llama). **Не выбирайте модель Stable Diffusion** — это селектор модели чата.
3. В области сообщений нажмите **Интеграции** и включите **Изображение**.
4. Используйте подсказку вроде: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Изображение будет сгенерировано и появится в чате.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Это демонстрирует, что Open WebUI может координировать «двухэтапный» рабочий процесс:
  - LLM помогает уточнить подсказку
  - Изображение генерируется через конечную точку Images в Lemonade с использованием Stable Diffusion
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Задание 3: Генерация изображения по текстовой подсказке (Stable Diffusion)

Модели Stable Diffusion не поддерживают генерацию текста — они генерируют только изображения через Images API.

#### Шаг 1: Настройка генерации изображений в Open WebUI

1. В GUI Lemonade (`http://localhost:13305`) найдите `SDXL-Turbo` (быстрый) или `SDXL-Base-1.0` (более высокое качество) и загрузите его.
2. Перейдите в **Настройки администратора → Изображения** (http://localhost:8080/admin/settings/images)
3. Установите:
   - **Генерация изображений:** ВКЛ
   - **Движок генерации изображений:** По умолчанию (OpenAI)
   - **Базовый URL OpenAI API:** `http://localhost:13305/api/v1`
   - **Ключ OpenAI API:** `-`
   - **Модель:** `SDXL-Turbo` или `SDXL-Base-1.0`
4. Если вы хотите добавить дополнительные параметры, введите их в текстовое поле в формате JSON. Например: `{ "steps": 4, "cfg_scale": 1 }`. Доступные параметры см. на странице [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Сохраните


#### Шаг 2: Разрешите генерацию изображений для модели
Этот шаг обеспечивает включение генерации изображений как возможности для вашей модели.
1. Перейдите в **Настройки администратора → Модели** (http://localhost:8080/admin/settings/models) и выберите свою модель
2. Включите `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Шаг 3: Сгенерируйте изображение из экрана чата

1. Вернитесь в чат по адресу `http://localhost:8080`.
2. Выберите **LLM для генерации текста** в выпадающем списке моделей (например: Qwen, Llama). **Не выбирайте модель Stable Diffusion** — это селектор модели чата.
3. В области сообщений нажмите **Интеграции** и включите **Изображение**.
4. Используйте подсказку вроде: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Изображение будет сгенерировано и появится в чате.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Это демонстрирует, что Open WebUI может координировать «двухэтапный» рабочий процесс:
  - LLM помогает уточнить подсказку
  - Изображение генерируется через конечную точку Images в Lemonade с использованием Stable Diffusion
<!-- @device:end -->
<!-- @os:end -->

---

## Устранение неполадок

### «В Open WebUI не отображаются модели»
- Сначала проверьте Lemonade: откройте `http://localhost:13305/api/v1/models` в браузере и убедитесь, что ваши модели перечислены и загружены
- Затем проверьте подключение Open WebUI: перейдите в **Настройки администратора → Подключения** по адресу `http://localhost:8080/admin/settings/connections` и убедитесь, что базовый URL указан как `http://localhost:13305/api/v1`

### Сообщение об ошибке «This model does not support chat completion»
- Вы выбрали модель изображений (SDXL-Turbo / SDXL-Base-1.0) в выпадающем списке моделей чата.
- **Решение**: выберите LLM для чата, а для генерации используйте переключатель «Изображение» и настройки Images.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Ошибки/тайм-ауты при генерации изображений
- Начните с `SDXL-Turbo` (быстрый, меньше шагов)
- После успешной работы переключите модель изображений на `SDXL-Base-1.0` для повышения качества

---

## Дальнейшие шаги

Теперь у вас есть рабочий **«локальный AI-стек»** — единый интерфейс, управляющий несколькими типами моделей через стандартный API.

Вот три расширения, открывающие совершенно новые рабочие процессы:

### 1. Преобразование речи в текст с помощью Whisper

Попробуйте преобразовать аудио в текст с помощью модели Whisper, а затем передать его в LLM для создания резюме, списка задач или переработки. Это основа для заметок о встречах и голосовых помощников.

### 2. Написание кода на Python внутри Open WebUI

Используйте встроенную среду выполнения кода Open WebUI для запуска фрагментов Python, проверки результатов и более быстрой итерации — не покидая интерфейс. [Справочник](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. Рендеринг HTML внутри Open WebUI

Отображайте HTML-вывод непосредственно в интерфейсе. Это удивительно мощный инструмент для быстрого создания прототипов, форматированных отчётов и интерактивных фрагментов. [Справочник](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## Ссылки

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Документация Lemonade Server](https://lemonade-server.ai/docs)
- [Lemonade Server CLI](https://lemonade-server.ai/docs/lemonade-cli/)
- [Руководство по интеграции Lemonade ↔ Open WebUI](https://lemonade-server.ai