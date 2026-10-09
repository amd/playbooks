<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинний переклад.** Цю сторінку було автоматично перекладено з англійської мови, і вона не була перевірена людиною. Вона може містити помилки, а певні інструкції, команди, завантаження, доступність продукту чи інший вміст можуть відрізнятися залежно від мови чи регіону. У разі будь-яких невідповідностей чи розбіжностей переважну силу має оригінальна англомовна версія playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Для цього посібника потрібно щонайменше **32 ГБ** оперативної пам'яті системи.
<!-- @device:end -->

## Огляд

[Open WebUI](https://docs.openwebui.com) — це розміщений локально, браузерний інтерфейс, який забезпечує звичний досвід чат-бота, виступаючи фронтендом для одного або кількох серверів моделей ШІ. Замість прив'язки до одного постачальника, Open WebUI може підключатися до **будь-якого бекенду, що надає API, сумісний з OpenAI**, тож ви можете змінювати моделі та можливості без зміни інтерфейсу.

У цьому посібнику ми використовуємо [**Lemonade**](https://lemonade-server.ai) як бекенд, оскільки він надає **уніфіковану кінцеву точку, сумісну з OpenAI**, що підтримує кілька модальностей:
- **Великі мовні моделі (LLM)** для генерації тексту
- **Моделі бачення** для розуміння зображень
- **Stable Diffusion** для генерації зображень
- **Моделі транскрипції аудіо** для перетворення мовлення в текст

Це налаштування дозволяє вам дослідити **повний мультимодальний робочий процес від початку до кінця**.

---

## Що ви дізнаєтеся

Наприкінці ви зможете:

- Підключити Open WebUI до локального бекенду, сумісного з OpenAI (Lemonade)
- Спілкуватися з локальною LLM з вашого браузера
- Завантажити зображення та ставити моделі бачення запитання про нього
- Генерувати зображення з текстових запитів за допомогою моделей Stable Diffusion (SDXL-Turbo / SDXL)
- Зрозуміти ментальну модель, щоб ви могли використовувати інші бекенди (Ollama, vLLM, llama.cpp server тощо)

---

## Основні концепції (ментальна модель)

### Три компоненти

| Компонент | Що він робить | Приклади |
|---|---|---|
| Фронтенд (UI) | Веб-застосунок, з яким ви взаємодієте | Open WebUI |
| Бекенд (сервер моделей) | Розміщує моделі та надає HTTP-кінцеві точки | Lemonade, Ollama, vLLM, llama.cpp server, сервери, сумісні з OpenAI |
| Моделі | Фактичні моделі LLM / бачення / дифузії / аудіо | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### Чому важливий "API, сумісний з OpenAI"

Open WebUI побудовано на основі стандартних кінцевих точок у стилі OpenAI, таких як:
  - Чат: `/chat/completions`
  - Список моделей: `/models`
  - Генерація зображень: `/images/generations`
  - Транскрипція аудіо: `/audio/transcriptions`

Lemonade надає їх за адресою `http://localhost:13305/api/v1/...`

Якщо бекенд підтримує ці кінцеві точки, Open WebUI може взаємодіяти з ним з мінімальним налаштуванням. Саме тому ми можемо перемикати бекенди без зміни нашого робочого процесу.

#### Дві служби, два порти

Протягом цього посібника ви будете працювати з двома окремими службами:

| Служба | URL | Що ви там робите |
|---|---|---|
| **Lemonade** (GUI) | `http://localhost:13305` | Переглядайте, завантажуйте та керуйте моделями |
| **Open WebUI** | `http://localhost:8080` | Спілкуйтеся, завантажуйте зображення, генеруйте зображення — інтерфейс, орієнтований на користувача |

Lemonade запускає моделі; Open WebUI — це інтерфейс, з яким ви взаємодієте. Спочатку використовуйте GUI Lemonade, щоб завантажити свої моделі, а потім використовуйте їх з Open WebUI.

---

<!-- @device:halo_box,halo,stx,krk -->
## Налаштування конфігурації пам'яті

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Перевірка оновлень програмного забезпечення

<!-- @require:software-update -->
<!-- @device:end -->

## Одноразове налаштування

Для цього посібника потрібен Lemonade, запущений як бекенд, а в Linux — також рушій контейнерів (Podman) для запуску Open WebUI. Налаштуйте це перед встановленням Open WebUI.

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

## Завантаження моделей у Lemonade

Перед встановленням Open WebUI переконайтеся, що моделі, які ви хочете використовувати, завантажені та готові в Lemonade.

1. Відкрийте GUI Lemonade за адресою `http://localhost:13305`.
2. Перегляньте доступні моделі та завантажте ті, які хочете використовувати (наприклад, LLM для чату, модель бачення та/або модель Stable Diffusion для генерації зображень).
3. Переконайтеся, що API доступний, відвідавши `http://localhost:13305/api/v1/models` у вашому браузері — ви повинні побачити список завантажених моделей.

> Моделі потрібно завантажити в **Lemonade** (`localhost:13305`), перш ніж вони зможуть з'явитися в **Open WebUI** (`localhost:8080`). Якщо модель пізніше не з'являється в Open WebUI, поверніться сюди та спочатку перевірте Lemonade.


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

## Встановлення Open WebUI

<!-- @os:windows -->
### 1. Встановлення Python 3.12

Open WebUI вимагає **Python 3.12** — він не встановлюється на Python 3.13+. Засіб запуску Python для Windows (`py`) дозволяє встановити 3.12 паралельно з будь-якою наявною версією Python без конфліктів.

```powershell
winget install Python.Python.3.12
```

Закрийте та знову відкрийте термінал після встановлення, потім перевірте:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **Примітка:** Ваша система постачається з попередньо встановленим Python 3.13. Встановлення 3.12 не впливає на нього — `python` продовжує використовувати 3.13, а `py -3.12` націлюється лише на 3.12, коли вам це потрібно.
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

### 2. Створення віртуального середовища та встановлення Open WebUI

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
Тепер ми будемо використовувати службу Podman для контейнеризації нашого встановлення Open WebUI.

Будь ласка, завантажте наступне в каталог на свій вибір: [compose.yml](assets/compose.yml)

У цьому каталозі виконайте наступну команду:

```bash
podman compose up -d
```

Це завантажить образ Open WebUI та запише дані в постійне сховище.

Запустіть Open WebUI, ввівши `localhost:8080` в адресному рядку браузера.

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

> **Порада**: Open WebUI також пропонує інші варіанти встановлення на своєму [GitHub](https://github.com/open-webui/open-webui).
## Запуск сервера Open WebUI

<!-- @os:windows -->
- Виконайте наведену нижче команду, щоб запустити HTTP-сервер Open WebUI:
```bash
open-webui serve
```
<!-- @os:end -->

- У браузері перейдіть за адресою `http://localhost:8080`.
- Open WebUI запропонує створити локальний обліковий запис адміністратора. Після входу ви побачите інтерфейс чату.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> Не закривайте вікно терміналу. Його закриття зупинить роботу Open WebUI.
<!-- @os:end -->

<!-- @os:linux -->
> Контейнер працює у фоновому режимі. З каталогу, що містить `compose.yml`, керуйте ним за допомогою команд `podman compose down` (зупинити) та `podman compose up -d` (запустити). Ваші облікові записи та налаштування зберігаються в томі `open_webui_data`.
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

## Підключення Open WebUI до Lemonade

Тепер, коли обидва сервіси запущені — Lemonade за адресою `localhost:13305` і Open WebUI за адресою `localhost:8080` — з’єднайте їх, щоб Open WebUI міг використовувати моделі Lemonade.

В Open WebUI:

1. Натисніть піктограму **профілю користувача** у верхньому правому куті, потім виберіть **Settings**.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. На панелі Settings натисніть **Admin Settings** у нижньому лівому куті.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. На бічній панелі Admin Settings натисніть **Connections** (або перейдіть безпосередньо за адресою `http://localhost:8080/admin/settings/connections`).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. У розділі **OpenAI API** додайте нове з’єднання:
   - **Base URL:** `http://localhost:13305/api/v1`
   - **API Key:** `-` (для локального використання підійде одне тире)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. Переконайтеся, що в розділі **"Manage OpenAI API Connections"** увімкнено лише `http://localhost:13305/api/v1`. Вимкніть усі інші з’єднання (наприклад, стандартне з’єднання OpenAI).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. Натисніть **Save**.

7. **(Рекомендовано)** Вимкніть функції автоматичної генерації, щоб Open WebUI залишався чуйним під час роботи з локальними LLM. Перейдіть до **Admin Settings → Settings → Interface** і вимкніть:
   - Title Generation
   - Follow Up Generation
   - Tags Generation

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. Натисніть **Save**, після чого поверніться на `http://localhost:8080`.
9. Натисніть на випадаючий список моделей — ви маєте побачити моделі, завантажені з Lemonade.

---

## Основні дії

Тепер усе налаштовано. Розглянемо три цікаві сценарії використання.

---

### Дія 1: Спілкування з локальною LLM
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. Натисніть на випадаюче меню у верхньому лівому куті інтерфейсу. Відобразяться встановлені вами моделі Lemonade. Виберіть одну з них, щоб продовжити. (приклад: `Qwen3-4B-Hybrid`).

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. Введіть повідомлення для LLM і натисніть кнопку надсилання (або клавішу Enter). LLM завантажиться в пам’ять протягом кількох секунд, після чого ви побачите потокову відповідь.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. Натисніть на випадаюче меню у верхньому лівому куті інтерфейсу. Відобразяться встановлені вами моделі Lemonade. Виберіть одну з них, щоб продовжити. (приклад: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Введіть повідомлення для LLM і натисніть кнопку надсилання (або клавішу Enter). LLM завантажиться в пам’ять протягом кількох секунд, після чого ви побачите потокову відповідь.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. Модель відповість у чаті.

4. У цей момент відкрийте `Task Manager` у вашій системі. Ви побачите **високе завантаження GPU або NPU** залежно від того, чи вибрана вами модель є **Hybrid**, чи **NPU** відповідно. За допомогою диспетчера завдань ви можете підтвердити, що модель виконується локально.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. Натисніть на випадаюче меню у верхньому лівому куті інтерфейсу. Відобразяться встановлені вами моделі Lemonade. Виберіть одну з них, щоб продовжити. (приклад: `Qwen3.5-4B-GGUF`).

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. Введіть повідомлення для LLM і натисніть кнопку надсилання (або клавішу Enter). LLM завантажиться в пам’ять протягом кількох секунд, після чого ви побачите потокову відповідь.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. Модель відповість у чаті.
<!-- @os:end -->

Це підтверджує, що Open WebUI може надсилати запити до Lemonade через OpenAI-сумісну кінцеву точку чату.

---

### Дія 2: Завантаження зображення та постановка запитань (Vision)

Для цього потрібна модель, яка підтримує введення зображень (модель Vision або Multimodal).

1. Натисніть піктограму фільтра, виберіть "By Category", а потім оберіть модель із розділу **Vision** (наприклад, `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. Натисніть кнопку **`+`** у полі повідомлення та завантажте зображення
3. Поставте запитання, яке вимагає справжнього розуміння зображення: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. Модель відповідає на основі вмісту зображення, а не загального тексту.

Це демонструє, що Open WebUI може надсилати мультимодальні запити (текст + зображення) через бекенд (Lemonade) до моделі Vision.

---

<!-- @os:windows -->
### Дія 3: Генерація зображення з текстового запиту (Stable Diffusion)

Моделі Stable Diffusion не підтримують генерацію тексту, вони лише генерують зображення через Images API. 

#### Крок 1: Налаштування генерації зображень в Open WebUI

1. У графічному інтерфейсі Lemonade (`http://localhost:13305`) знайдіть `SDXL-Turbo` (швидка) або `SDXL-Base-1.0` (вища якість) та завантажте її.
2. Перейдіть до **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Встановіть:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` або `SDXL-Base-1.0`
4. Якщо потрібно додати більше параметрів, додайте їх у текстове поле у форматі JSON. Наприклад: `{ "steps": 4, "cfg_scale": 1 }`. Перелік доступних параметрів дивіться на сторінці [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Збережіть
#### Крок 2: Дозвольте генерацію зображень для моделі
Цей крок гарантує, що ви увімкнете генерацію зображень як можливість для вашої моделі.
1. Перейдіть у **Admin Settings → Models** (http://localhost:8080/admin/settings/models) і виберіть свою модель
2. Увімкніть `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Крок 3: Згенеруйте зображення з екрана чату

1. Поверніться до чату за адресою `http://localhost:8080`.
2. Виберіть **Text Generation LLM** у випадному списку моделей (наприклад: Qwen, Llama). **Не вибирайте модель Stable Diffusion**, оскільки це селектор моделі для чату.
3. В області повідомлення натисніть **Integrations** і увімкніть перемикач **Image**.
4. Використайте підказку на кшталт: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Зображення згенероване та з'являється в чаті.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Це демонструє, що Open WebUI може координувати "двоетапний" робочий процес:
  - LLM допомагає вдосконалити підказку
  - Зображення генерується через ендпоінт Images Lemonade за допомогою Stable Diffusion
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### Активність 3: Згенеруйте зображення з текстової підказки (Stable Diffusion)

Моделі Stable Diffusion не підтримують генерацію тексту, вони генерують лише зображення через Images API.

#### Крок 1: Налаштуйте генерацію зображень в Open WebUI

1. У графічному інтерфейсі Lemonade (`http://localhost:13305`) знайдіть `SDXL-Turbo` (швидкий) або `SDXL-Base-1.0` (вища якість) і завантажте його.
2. Перейдіть у **Admin Settings → Images** (http://localhost:8080/admin/settings/images)
3. Встановіть:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` або `SDXL-Base-1.0`
4. Якщо ви хочете додати більше параметрів, додайте їх у текстове поле у форматі JSON. Наприклад: `{ "steps": 4, "cfg_scale": 1 }`. Перегляньте доступні параметри за посиланням [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html).

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. Збережіть


#### Крок 2: Дозвольте генерацію зображень для моделі
Цей крок гарантує, що ви увімкнете генерацію зображень як можливість для вашої моделі.
1. Перейдіть у **Admin Settings → Models** (http://localhost:8080/admin/settings/models) і виберіть свою модель
2. Увімкніть `Image Generation`

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### Крок 3: Згенеруйте зображення з екрана чату

1. Поверніться до чату за адресою `http://localhost:8080`.
2. Виберіть **Text Generation LLM** у випадному списку моделей (наприклад: Qwen, Llama). **Не вибирайте модель Stable Diffusion**, оскільки це селектор моделі для чату.
3. В області повідомлення натисніть **Integrations** і увімкніть перемикач **Image**.
4. Використайте підказку на кшталт: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. Зображення згенероване та з'являється в чаті.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

Це демонструє, що Open WebUI може координувати "двоетапний" робочий процес:
  - LLM допомагає вдосконалити підказку
  - Зображення генерується через ендпоінт Images Lemonade за допомогою Stable Diffusion
<!-- @device:end -->
<!-- @os:end -->

---

## Усунення несправностей

### "У Open WebUI не відображаються моделі"
- Спочатку перевірте Lemonade: відкрийте `http://localhost:13305/api/v1/models` у браузері та підтвердіть, що ваші моделі перелічені та завантажені
- Потім перевірте з'єднання Open WebUI: перейдіть у **Admin Settings → Connections** за адресою `http://localhost:8080/admin/settings/connections` і переконайтеся, що Base URL — це `http://localhost:13305/api/v1`

### Повідомлення про помилку "This model does not support chat completion"
- Ви вибрали модель зображення (SDXL-Turbo / SDXL-Base-1.0) у випадному списку моделей чату.
- **Виправлення**: виберіть LLM для чату, а для генерації використовуйте перемикач Image та налаштування Images.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### Помилки/тайм-аути генерації зображень
- Спочатку спробуйте `SDXL-Turbo` (швидко, менше кроків)
- Після того, як усе запрацює, перейдіть на модель зображення `SDXL-Base-1.0` для якості

---

## Наступні кроки

Тепер у вас є працюючий **"локальний стек ШІ"** — єдиний інтерфейс, що керує кількома типами моделей через стандартний API.

Ось три розширення, які відкривають абсолютно нові робочі процеси:

### 1. Перетворення мовлення на текст за допомогою Whisper

Спробуйте перетворити аудіо на текст за допомогою моделі Whisper, а потім подайте його в LLM для підсумовування, визначення завдань або перефразування. Це основа для нотаток зустрічей та голосових асистентів.

### 2. Програмування на Python у Open WebUI

Використовуйте вбудовану можливість виконання коду Open WebUI, щоб запускати фрагменти Python, переглядати результати та швидше ітерувати — не виходячи з інтерфейсу. [Довідка](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. Рендеринг HTML у Open WebUI

Відображайте вихідні дані HTML безпосередньо в інтерфейсі. Це напрочуд потужна можливість для створення швидких прототипів, форматованих звітів та інтерактивних фрагментів. [Довідка](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## Посилання

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Документація Lemonade Server](https://lemonade-server.ai/docs)
- [CLI Lemonade Server](https://lemonade-server.ai/docs/lemonade-cli/)
- [Посібник з інтеграції Lemonade ↔ Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Специфікація API Lemonade Server (ендпоінти)](https://lemonade-server.ai/docs/server/server_spec)
- [Відеоогляд (Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [Відеоогляд (Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)

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