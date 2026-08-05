<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинный перевод.** Эта страница была автоматически переведена с английского языка и не прошла проверку человеком. Она может содержать ошибки, а некоторые инструкции, команды, файлы для загрузки, сведения о доступности продуктов или иное содержимое могут отличаться в зависимости от языка или региона. В случае каких-либо несоответствий или расхождений преимущественную силу имеет оригинальная версия playbook на английском языке.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Для этого руководства требуется минимум **32 ГБ** оперативной памяти.
<!-- @device:end -->

## Обзор

[Open WebUI](https://docs.openwebui.com) — это самостоятельно размещаемый интерфейс на основе браузера, который обеспечивает привычный опыт чат-бота, выступая при этом фронтендом для одного или нескольких серверов ИИ-моделей. Вместо привязки к одному поставщику Open WebUI может подключаться к **любому бэкенду, предоставляющему API, совместимый с OpenAI**, поэтому вы можете менять модели и возможности, не переключаясь между интерфейсами.

В этом руководстве в качестве бэкенда используется [**Lemonade**](https://lemonade-server.ai), поскольку он предоставляет **единую конечную точку, совместимую с OpenAI**, поддерживающую несколько модальностей:
- **Большие языковые модели (LLM)** для генерации текста
- **Модели зрения** для понимания изображений
- **Stable Diffusion** для генерации изображений
- **Модели транскрипции аудио** для преобразования речи в текст

Такая настройка позволяет изучить **полный мультимодальный рабочий процесс от начала до конца**.

---

## Чему вы научитесь

К концу руководства вы сможете:

- Подключить Open WebUI к локальному бэкенду, совместимому с OpenAI (Lemonade)
- Общаться с локальной LLM через браузер
- Загружать изображение и задавать вопросы о нём модели зрения
- Генерировать изображения по текстовым запросам с помощью моделей Stable Diffusion (SDXL-Turbo / SDXL)
- Понять ментальную модель, чтобы использовать другие бэкенды (Ollama, vLLM, сервер llama.cpp и т. д.)

---

## Базовые концепции (ментальная модель)

### Три компонента

| Компонент | Что делает | Примеры |
|---|---|---|
| Фронтенд (интерфейс) | Веб-приложение, с которым вы взаимодействуете | Open WebUI |
| Бэкенд (сервер моделей) | Размещает модели и предоставляет HTTP-эндпоинты | Lemonade, Ollama, vLLM, сервер llama.cpp, серверы, совместимые с OpenAI |
| Модели | Собственно модели LLM / зрения / диффузии / аудио | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### Почему важен «API, совместимый с OpenAI»

Open WebUI построен на основе стандартных эндпоинтов в стиле OpenAI, таких как:
  - Чат: `/chat/completions`
  - Список моделей: `/models`
  - Генерация изображений: `/images/generations`
  - Транскрипция аудио: `/audio/transcriptions`

Lemonade предоставляет их по адресу `http://localhost:13305/api/v1/...`

Если бэкенд поддерживает эти эндпоинты, Open WebUI может взаимодействовать с ним при минимальной настройке. Именно поэтому мы можем переключать бэкенды, не меняя рабочий процесс.

#### Две службы, два порта

На протяжении этого руководства вы будете работать с двумя отдельными службами:

| Служба | URL | Что вы там делаете |
|---|---|---|
| **Lemonade** (графический интерфейс) | `http://localhost:13305` | Просмотр, загрузка и управление моделями |
| **Open WebUI** | `http://localhost:8080` | Чат, загрузка изображений, генерация изображений — пользовательский интерфейс |

Lemonade запускает модели; Open WebUI — это интерфейс, с которым вы взаимодействуете. Сначала используйте графический интерфейс Lemonade для загрузки моделей, а затем используйте их из Open WebUI.

---

## Настройка конфигурации памяти

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Проверка обновлений ПО

<!-- @require:software-update -->
<!-- @device:end -->

## Единоразовая настройка

Для этого руководства требуется, чтобы Lemonade был запущен в качестве бэкенда, а в Linux — также механизм контейнеризации (Podman) для запуска Open WebUI. Настройте это перед установкой Open WebUI.

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

Перед установкой Open WebUI убедитесь, что нужные вам модели загружены и готовы к использованию в Lemonade.

1. Откройте графический интерфейс Lemonade по адресу `http://localhost:13305`.
2. Просмотрите доступные модели и загрузите те, которые вы хотите использовать (например, LLM для чата, модель зрения и/или модель Stable Diffusion для генерации изображений).
3. Убедитесь, что API доступен, перейдя по адресу `http://localhost:13305/api/v1/models` в браузере — вы должны увидеть список загруженных моделей.

> Модели должны быть загружены в **Lemonade** (`localhost:13305`), прежде чем они появятся в **Open WebUI** (`localhost:8080`). Если позже модель не отображается в Open WebUI, вернитесь сюда и сначала проверьте Lemonade.


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

Для Open WebUI требуется **Python 3.12** — он не устанавливается на Python 3.13+. Средство запуска Python для Windows (`py`) позволяет установить версию 3.12 параллельно с любой существующей версией Python без конфликтов.

```powershell
winget install Python.Python.3.12
```

Закройте и снова откройте терминал после установки, затем проверьте:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Примечание:** В вашей системе уже предустановлен Python 3.13. Установка версии 3.12 не влияет на него — `python` продолжает использовать 3.13, а `py -3.12` обращается к версии 3.12 только тогда, когда это необходимо.
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
Теперь мы используем службу Podman для контейнеризации установки Open WebUI.

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

> **Совет**: Open WebUI также предлагает другие варианты установки на своей странице [GitHub](https://github.com/open-webui/open-webui).
## Запуск сервера Open WebUI

<!-- @os:windows -->
- Выполните следующую команду, чтобы запустить HTTP-сервер Open WebUI:
```bash
open-webui serve
```
<!-- @os:end -->

- В браузере перейдите по адресу `http://localhost:8080`.
- Open WebUI предложит вам создать локальную учётную запись администратора. После входа вы увидите интерфейс чата.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> Не закрывайте окно терминала. Его закрытие остановит Open WebUI.
<!-- @os:end -->

<!-- @os:linux -->
> Контейнер работает в фоновом режиме. Из каталога, содержащего `compose.yml`, управляйте им с помощью `podman compose down` (остановить) и `podman compose up -d` (запустить). Ваши учётные записи и настройки сохраняются в томе `open_webui_data`.
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

1. Нажмите значок **профиля пользователя** в правом верхнем углу, затем выберите **Settings**.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. На панели Settings нажмите **Admin Settings** в левом нижнем углу.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. На боковой панели Admin Settings нажмите **Connections** (или перейдите напрямую по адресу `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. В разделе **OpenAI API** добавьте новое подключение:
   - **Base URL:** `http://localhost:13305/api/v1`
   - **API Key:** `-` (для локального использования подойдёт одиночный дефис)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. Убедитесь, что в разделе **"Manage OpenAI API Connections"** включён только `http://localhost:13305/api/v1`. Отключите остальные подключения (например, стандартное подключение OpenAI).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. Нажмите **Save**.

7. **(Рекомендуется)** Отключите функции автоматической генерации, чтобы Open WebUI оставался отзывчивым при работе с локальными LLM. Перейдите в **Admin Settings → Settings → Interface** и отключите:
   - Title Generation
   - Follow Up Generation
   - Tags Generation

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. Нажмите **Save**, затем вернитесь на `http://localhost:8080`.
9. Нажмите на выпадающий список моделей — вы должны увидеть модели, загруженные из Lemonade.

---

## Основные действия

Теперь всё готово. Рассмотрим три интересных сценария использования.

---

### Действие 1: Общение с локальной LLM
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Нажмите на выпадающее меню в верхнем левом углу интерфейса. Отобразятся установленные вами модели Lemonade. Выберите одну, чтобы продолжить. (пример: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. Введите сообщение для LLM и нажмите отправить (или клавишу Enter). Загрузка LLM в память займёт несколько секунд, после чего вы увидите потоковый вывод ответа.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Нажмите на выпадающее меню в верхнем левом углу интерфейса. Отобразятся установленные вами модели Lemonade. Выберите одну, чтобы продолжить. (пример: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Введите сообщение для LLM и нажмите отправить (или клавишу Enter). Загрузка LLM в память займёт несколько секунд, после чего вы увидите потоковый вывод ответа.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. Модель ответит в чате.

4. В этот момент откройте `Task Manager` в вашей системе. Вы увидите **высокую загрузку GPU или NPU** в зависимости от того, является ли выбранная вами модель **Hybrid** или **NPU** соответственно. С помощью диспетчера задач вы можете убедиться, что модель работает локально.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Нажмите на выпадающее меню в верхнем левом углу интерфейса. Отобразятся установленные вами модели Lemonade. Выберите одну, чтобы продолжить. (пример: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Введите сообщение для LLM и нажмите отправить (или клавишу Enter). Загрузка LLM в память займёт несколько секунд, после чего вы увидите потоковый вывод ответа.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. Модель ответит в чате.
<!-- @os:end -->

Это подтверждает, что Open WebUI может отправлять запросы в Lemonade через совместимую с OpenAI конечную точку чата.

---

### Действие 2: Загрузка изображения и вопросы по нему (Vision)

Для этого требуется модель с поддержкой ввода изображений (модель Vision или Multimodal).

1. Нажмите значок фильтра, выберите "By Category", затем выберите модель из раздела **Vision** (например, `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. Нажмите кнопку **`+`** в поле сообщения и загрузите изображение
3. Задайте вопрос, требующий подлинного понимания изображения: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. Модель отвечает на основе содержимого изображения, а не общего текста.

Это демонстрирует, что Open WebUI может отправлять мультимодальные запросы (текст + изображение) через бэкенд (Lemonade) в модель Vision.

---

<!-- @os:windows -->
### Действие 3: Генерация изображения по текстовому запросу (Stable Diffusion)

Модели Stable Diffusion не поддерживают генерацию текста, они только генерируют изображения через Images API.

#### Шаг 1: Настройка генерации изображений в Open WebUI

1. В графическом интерфейсе Lemonade (`http://localhost:13305`) найдите `SDXL-Turbo` (быстрая) или `SDXL-Base-1.0` (более высокое качество) и загрузите её.
2. Перейдите в **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Установите:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` или `SDXL-Base-1.0`
4. Если вы хотите добавить дополнительные параметры, добавьте их в текстовое поле в формате JSON. Например: `{ "steps": 4, "cfg_scale": 1 }`. Список доступных параметров см. в [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Сохраните
#### Шаг 2: Разрешите генерацию изображений для модели
Этот шаг гарантирует, что вы включите генерацию изображений как возможность вашей модели.
1. Перейдите в **Admin Settings → Models** (http://localhost:8080/admin/settings/models) и выберите свою модель
2. Включите `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Шаг 3: Сгенерируйте изображение с экрана чата

1. Вернитесь в чат по адресу `http://localhost:8080`.
2. Выберите **LLM для генерации текста** в выпадающем списке моделей (например, Qwen, Llama). **Не выбирайте модель Stable Diffusion**, так как это селектор моделей для чата.
3. В области сообщения нажмите на **Integrations** и включите переключатель **Image**.
4. Используйте промпт наподобие: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Изображение будет сгенерировано и появится в чате.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Это подтверждает, что Open WebUI может координировать «двухчастный» рабочий процесс:
  - LLM помогает уточнить промпт
  - Изображение генерируется через конечную точку Images Lemonade с использованием Stable Diffusion
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Активность 3: Сгенерируйте изображение из текстового промпта (Stable Diffusion)

Модели Stable Diffusion не поддерживают генерацию текста, они генерируют изображения только через Images API. 

#### Шаг 1: Настройте генерацию изображений в Open WebUI

1. В графическом интерфейсе Lemonade (`http://localhost:13305`) найдите `SDXL-Turbo` (быстрая) или `SDXL-Base-1.0` (более высокое качество) и загрузите её.
2. Перейдите в **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Установите:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` или `SDXL-Base-1.0`
4. Если хотите добавить дополнительные параметры, добавьте их в текстовое поле в формате JSON. Например: `{ "steps": 4, "cfg_scale": 1 }`. Доступные параметры смотрите на странице [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Сохраните


#### Шаг 2: Разрешите генерацию изображений для модели
Этот шаг гарантирует, что вы включите генерацию изображений как возможность вашей модели.
1. Перейдите в **Admin Settings → Models** (http://localhost:8080/admin/settings/models) и выберите свою модель
2. Включите `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Шаг 3: Сгенерируйте изображение с экрана чата

1. Вернитесь в чат по адресу `http://localhost:8080`.
2. Выберите **LLM для генерации текста** в выпадающем списке моделей (например, Qwen, Llama). **Не выбирайте модель Stable Diffusion**, так как это селектор моделей для чата.
3. В области сообщения нажмите на **Integrations** и включите переключатель **Image**.
4. Используйте промпт наподобие: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Изображение будет сгенерировано и появится в чате.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Это подтверждает, что Open WebUI может координировать «двухчастный» рабочий процесс:
  - LLM помогает уточнить промпт
  - Изображение генерируется через конечную точку Images Lemonade с использованием Stable Diffusion
<!-- @device:end -->
<!-- @os:end -->

---

## Устранение неполадок

### «В Open WebUI не отображаются модели»
- Сначала проверьте Lemonade: откройте `http://localhost:13305/api/v1/models` в браузере и убедитесь, что ваши модели указаны в списке и загружены
- Затем проверьте подключение Open WebUI: перейдите в **Admin Settings → Connections** по адресу `http://localhost:8080/admin/settings/connections` и убедитесь, что Base URL указан как `http://localhost:13305/api/v1`

### Сообщение об ошибке «This model does not support chat completion»
- Вы выбрали модель для изображений (SDXL-Turbo / SDXL-Base-1.0) в выпадающем списке моделей чата.
- **Решение**: выберите LLM для чата и используйте переключатель Image + настройки Images для генерации.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Ошибки/тайм-ауты генерации изображений
- Начните сначала с `SDXL-Turbo` (быстрая, меньше шагов)
- Когда всё заработает, переключитесь на модель изображений `SDXL-Base-1.0` для повышения качества

---

## Дальнейшие шаги

Теперь у вас есть работающий **«локальный стек ИИ»** — единый интерфейс, управляющий несколькими типами моделей через стандартный API.

Вот три расширения, которые открывают совершенно новые рабочие процессы:

### 1. Преобразование речи в текст с помощью Whisper

Попробуйте преобразовать аудио в текст с помощью модели Whisper, а затем передать его в LLM для суммаризации, выделения пунктов действий или переформулирования. Это основа для заметок со встреч и голосовых ассистентов.

### 2. Программирование на Python внутри Open WebUI

Используйте встроенную возможность выполнения кода в Open WebUI для запуска фрагментов Python, просмотра вывода и более быстрой итерации — не покидая интерфейс. [Справка](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. Рендеринг HTML внутри Open WebUI

Отображайте вывод HTML прямо в интерфейсе. Это на удивление мощная возможность для создания быстрых прототипов, форматированных отчётов и интерактивных фрагментов. [Справка](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## Ссылки

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Документация Lemonade Server](https://lemonade-server.ai/docs)
- [CLI Lemonade Server](https://lemonade-server.ai/docs/lemonade-cli/)
- [Руководство по интеграции Lemonade ↔ Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Спецификация API Lemonade Server (конечные точки)](https://lemonade-server.ai/docs/server/server_spec)
- [Видеообзор (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [Видеообзор (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)

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