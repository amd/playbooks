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
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Обзор

Разработчики тратят много времени на небольшие повторяющиеся циклы: проверку помеченных pull request'ов, ответы на комментарии в GitHub, разбор новых issue, превращение цепочек сообщений в Slack в заметки для стендапа или послеинцидентные отчёты, а также отслеживание сигналов о релизах и исследованиях.
Каждый такой цикл знаком, но всё же требует суждения: собрать нужный контекст, решить, что важно, и опубликовать понятное обновление там, где команда уже работает.

[Автоматизации OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) превращают эти циклы в запланированные или событийные диалоги агента: запуски, во время которых ИИ-агент может читать контекст, вызывать инструменты и формировать обновление.
Общие шаблоны автоматизации в каталоге расширений OpenHands следуют этому шаблону для проверки pull request'ов в GitHub, мониторинга репозиториев, триажа issue в Linear, послеинцидентных ретроспектив, дайджестов стендапов в Slack и исследовательских обзоров: автоматизация активируется, использует настроенные интеграции, такие как GitHub или Slack, для получения контекста, обрабатывает этот контекст с помощью большой языковой модели (LLM) и записывает результат обратно.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) — это локальная управляющая платформа для создания и тестирования таких автоматизаций.
В этом руководстве она запускает OpenHands Agent Server — серверный процесс, выполняющий диалоги агента, — и подключает агента к внешним сервисам, таким как GitHub и Slack.

Чтобы рабочий процесс оставался на вашей системе AMD, агент обращается к локальной модели, обслуживаемой Lemonade Server.
Lemonade предоставляет доступ к этой модели через API, совместимый с OpenAI, поэтому Agent Canvas может настроить её как удалённую конечную точку в стиле OpenAI, в то время как сама модель, подсказка (prompt) и контекст рабочего процесса остаются локальными.

В этом руководстве вы создадите одну конкретную автоматизацию: запланированный дайджест разработки из GitHub в Slack.
Она использует GitHub для проверки недавней активности в репозитории, Slack для публикации дайджеста, вызовы API Agent Canvas для настройки и тестирования автоматизации, а также Lemonade для локального запуска LLM.

![Диаграмма архитектуры, показывающая GitHub MCP, автоматизацию OpenHands, Lemonade Server и Slack MCP](assets/00-architecture-overview.png)

## Чему вы научитесь

- Как запустить Lemonade Server и убедиться, что локальная модель отвечает на запросы чата
- Как запустить Agent Canvas и настроить его Agent Server на работу с локальной LLM
- Как установить MCP-серверы (Model Context Protocol) для GitHub и Slack через API Agent Server
- Как создать и запустить запланированную автоматизацию OpenHands, публикующую дайджест разработки в Slack
- Как устранять наиболее распространённые сбои локальной модели и автоматизации

## Основные понятия

| Понятие | Что это такое | Где применяется в этом руководстве |
| --- | --- | --- |
| Lemonade Server | Локальная платформа обслуживания LLM, созданная для оборудования AMD и предоставляющая API, совместимый с OpenAI. Ваши данные никогда не покидают ваш компьютер. | Запускает модель, которая обеспечивает работу агента. |
| OpenHands Agent Server | Серверный процесс, выполняющий диалоги агента OpenHands. | Размещает агента, его профиль LLM и его MCP-серверы. |
| Agent Canvas | Локальная управляющая платформа для OpenHands, которая запускает Agent Server и интерфейс для просмотра запусков агента. | Запускает бэкенды и предоставляет API, который вы вызываете. |
| MCP-сервер | Сервер Model Context Protocol, предоставляющий агенту инструменты для внешнего сервиса, такого как GitHub или Slack. | Позволяет агенту читать GitHub и писать в Slack. |
| Автоматизация OpenHands | Запланированный или событийный диалог агента, который получает контекст, обрабатывает его и записывает результат куда-либо. | Дайджест из GitHub в Slack, который вы создаёте здесь. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Рабочие процессы агента для написания кода выигрывают от более крупной модели и большего окна контекста.
> Используйте не менее 32 ГБ оперативной памяти, а для более крупных моделей GGUF предпочтительно 64 ГБ или больше.
<!-- @device:end -->

## Настройка конфигурации памяти

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Проверка обновлений программного обеспечения

<!-- @require:software-update -->
<!-- @device:end -->

## Предварительные требования

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-6-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas); host npm is only used by CI to resolve the MCP packages. -->
<!-- @prereq:docker,nodejs,lemonade-models-qwen3-6-35b-a3b -->
<!-- @os:end -->

Вам потребуется:

- Lemonade Server, установленный согласно стандартному [руководству по установке Lemonade](https://lemonade-server.ai/docs/guide/install/).

<!-- @os:linux -->
- Node.js 22.12 или более поздней версии и `npm`, используемые для установки опубликованного CLI Agent Canvas и запуска MCP-серверов с помощью `npx`.
- `uv` — менеджер пакетов Python, который Agent Canvas использует для построения среды Agent Server. Если он ещё не установлен, установите его из [руководства по установке uv](https://docs.astral.sh/uv/getting-started/installation/).
- Недавно опубликованный пакет `@openhands/agent-canvas` со схемно-ориентированными настройками агента, `LLMSummarizingCondenserSettings.max_tokens` и поддержкой `custom_tokenizer` для LLM.
- Пакет Python `transformers`, доступный в среде Agent Server. Он необходим для подсчёта токенов по шаблону чата, когда задан `custom_tokenizer`.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop для Windows](https://docs.docker.com/desktop/setup/install/windows-install/), установленный и запущенный. В Windows стек Agent Canvas запускается из опубликованного образа Docker, который включает в себя Node.js, `uv`, `transformers` и пакет `@openhands/agent-canvas`, поэтому устанавливать их на хосте не нужно.
<!-- @os:end -->

- Токен GitHub с доступом на чтение к репозиторию, который вы хотите резюмировать.
- Токен бота Slack (`xoxb-...`) с правами `chat:write` и доступом на чтение канала.
- Идентификатор команды Slack (`T...`).
- Идентификатор канала Slack (`C...`), в который должен публиковаться дайджест.

Пригласите приложение Slack в целевой канал перед тестированием автоматизации.
## Переменные, используемые в этом плейбуке

<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @os:linux -->
```bash
export LEMONADE_BASE_URL="http://127.0.0.1:13305/api/v1"
export LEMONADE_MODEL="Qwen3.6-35B-A3B-GGUF"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
$env:LEMONADE_BASE_URL = "http://127.0.0.1:13305/api/v1"
$env:LEMONADE_MODEL = "Qwen3.6-35B-A3B-GGUF"
```
<!-- @os:end -->

Эти две переменные используются командами проверки ниже.
Модель, токенизатор и другие настройки LLM вводятся непосредственно в пользовательском интерфейсе Agent Canvas на последующих шагах, поэтому их буквальные значения приводятся инлайн там, где они нужны.

Следующие значения вводятся в пользовательский интерфейс Agent Canvas на последующих шагах.
Задайте их здесь, чтобы потом скопировать:

<!-- @os:linux -->
```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
$env:GITHUB_REPO_FILTER = "your-org/your-repo"
$env:SLACK_DIGEST_CHANNEL = "C0123456789"
$env:DIGEST_TIMEZONE = "America/New_York"
```
<!-- @os:end -->

Используйте явное значение `owner/repo` для `GITHUB_REPO_FILTER`.
Широкие маски по организации могут возвращать слишком много контекста MCP для локальных моделей.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Запуск Lemonade Server

Запустите модель из CLI Lemonade:

<!-- @os:linux -->
```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "$env:LEMONADE_MODEL"
```
<!-- @os:end -->

> **Выберите модель, подходящую под ваше оборудование.** `Qwen3.6-35B-A3B-GGUF` (~20 ГБ) — мощная модель для этого workflow, но ей требуется большой пул памяти.
> Если на вашем устройстве ограниченный объём памяти или видеопамяти GPU, выберите модель GGUF меньшего размера из библиотеки моделей Lemonade и используйте этот идентификатор модели (и соответствующий ему токенизатор) на протяжении всего этого плейбука.

> **Примечание:** первый запуск `lemonade run` загружает модель, если она ещё не скачана, что может занять некоторое время в зависимости от размера модели и скорости вашего соединения.

Lemonade предоставляет API, совместимый с OpenAI, по адресу:

```text
http://127.0.0.1:13305/api/v1
```

Опционально: если Agent Canvas или исполнитель автоматизации находятся не на той же машине, опубликуйте конечную точку Lemonade через защищённый туннель и используйте HTTPS-URL в качестве базового URL LLM.
[ngrok](https://ngrok.com/) предоставляет доступ к локальному порту через интернет по защищённому HTTPS-URL; для этого требуется бесплатный аккаунт ngrok, а `YOUR_NGROK_DOMAIN.ngrok-free.dev` нужно заменить на ваш собственный зарезервированный домен:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Проверка локальной модели

Убедитесь, что Lemonade может обслуживать выбранную модель:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Затем отправьте небольшой запрос чата:

```bash
curl -sS "${LEMONADE_BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"${LEMONADE_MODEL}"'",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
curl.exe -s "$env:LEMONADE_BASE_URL/models"
```

Затем отправьте небольшой запрос чата:

```powershell
$body = @{
  model    = "$env:LEMONADE_MODEL"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens  = 64
} | ConvertTo-Json -Depth 5
curl.exe -sS "$env:LEMONADE_BASE_URL/chat/completions" -H "Content-Type: application/json" -d $body
```
<!-- @os:end -->

Если в ответ возвращается массив `choices`, значит Lemonade готов к работе с Agent Canvas.

<!-- @os:linux -->
<!-- @test:id=lemonade-chat-linux timeout=1200 hidden=True -->
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
import json
import os
import sys

data = json.loads(os.environ["MODELS_JSON"])
entry = None
for item in data.get("data", []):
    if item.get("id") == "${lemonade_model}":
        entry = item
        break

if entry is None:
    print("Model ${lemonade_model} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: ${lemonade_model} model is downloaded in Lemonade")
PY

body='{
  "model": "${lemonade_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 64
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$modelsJson = $null
for ($i = 0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}

if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1

if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

$body = @{
  model    = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens  = 64
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "digest-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->
<!-- @os:end -->

## 3. Запуск Agent Canvas

<!-- @os:linux -->
Установите опубликованный пакет Agent Canvas и запустите полный стек:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Если глобальная установка npm завершается с ошибкой прав доступа, см. раздел по устранению неполадок с правами npm ниже.

По умолчанию Agent Canvas запускается по адресу `http://localhost:8000`.
Откройте этот URL в браузере.
Порт не имеет особого значения — если 8000 уже занят, укажите любой свободный порт с помощью `--port` (или `-p`).
Локальный бэкенд по умолчанию должен отображаться как исправный (healthy) на главном экране.

> **Примечание:** при первом запуске выполняется сборка управляемого `uv` окружения Python для Agent Server, поэтому может пройти несколько минут, прежде чем бэкенд сообщит о своей готовности.

Команда `agent-canvas` запускает agent-сервер, бэкенд автоматизации и веб-фронтенд вместе.
Для локального запуска OpenHands вам понадобится всего одна эта команда.
Остальная часть этого плейбука настраивает всё через пользовательский интерфейс Agent Canvas в вашем браузере.
<!-- @os:end -->

<!-- @os:windows -->
В Windows запустите опубликованный образ контейнера Agent Canvas с помощью Docker Desktop.
Образ включает в себя Agent Server, бэкенд автоматизации и веб-фронтенд, поэтому вам не нужно устанавливать Node.js, `uv` или CLI на хост-машине.

Сначала создайте папки конфигурации и рабочего пространства, которые будут смонтированы в контейнер:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Загрузите опубликованный образ (около 6 ГБ; он публичный, поэтому вход в систему не требуется):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Затем запустите стек:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Откройте `http://localhost:8000/canvas` в браузере.
Если порт 8000 уже занят, сопоставьте другой порт хоста, например `-p 8080:8000`, и вместо этого откройте `http://localhost:8080/canvas`.

> **Примечание:** при первом запуске окружение Agent Server собирается внутри контейнера, поэтому может пройти несколько минут, прежде чем бэкенд сообщит о своей готовности.

Точка монтирования `.openhands` сохраняет ваш профиль LLM, серверы MCP и автоматизации между перезапусками контейнера.
Остальная часть этого плейбука настраивает всё через пользовательский интерфейс Agent Canvas в вашем браузере по адресу `http://localhost:8000/canvas`.
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=uv-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->

<!-- @test:id=agent-canvas-version timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
# Prefer --version; fall back to --help if this build has no --version flag.
agent-canvas --version || agent-canvas --help
echo "OK: agent-canvas CLI is on PATH"
```
<!-- @test:end -->

<!-- @test:id=agent-canvas-start timeout=1200 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
log="/tmp/agent-canvas-test.log"
p=""
cleanup() {
  set +e
  for port in 8000 18000 18001 3001; do
    pid="$(ss -ltnp 2>/dev/null | grep ":$port " | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2)"
    [ -n "$pid" ] && kill "$pid" 2>/dev/null
  done
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null
    sleep 2
    kill -9 "$p" 2>/dev/null
  fi
}
# Preserve the real exit code; cleanup must never flip a pass to a fail (or vice versa).
trap 'rc=$?; cleanup; exit $rc' EXIT

# First launch builds the agent server's uv-managed Python env, so allow a generous startup window.
agent-canvas >"$log" 2>&1 &
p=$!

# Probe the agent-server backend health (18000/server_info), NOT just the 8000 ingress root:
# the ingress serves the static frontend and returns 200 for / even when the agent-server is down.
ok=false
for i in $(seq 1 300); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18000/server_info || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  if ! kill -0 "$p" 2>/dev/null; then
    echo "agent-canvas process exited before it finished starting"
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "agent-server not ready on http://127.0.0.1:18000/server_info"
  cat "$log" || true
  exit 1
fi

echo "OK: agent-canvas agent-server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=agent-canvas-docker-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$image    = "ghcr.io/openhands/agent-canvas:1.14.0"
$name     = "digest-agent-canvas-ci"
$hostPort = 18080

# Pull the image if the runner doesn't already have it. The published image is
# public, so no login is needed. A non-interactive session can trip over a
# configured Docker credential helper (ghcr is unauthenticated here), so pull
# with an isolated, empty Docker config that has no credsStore/credHelpers.
# TODO: remove this self-provisioning once the runners ship the image by default.
$imgId = docker images -q $image
if (-not $imgId) {
  Write-Host "Image $image not present; pulling..."
  $dockerCfg = Join-Path $env:TEMP "digest-docker-cfg"
  New-Item -ItemType Directory -Force -Path $dockerCfg | Out-Null
  '{}' | Set-Content -Path (Join-Path $dockerCfg "config.json") -Encoding ascii
  docker --config $dockerCfg pull $image
  if ($LASTEXITCODE -ne 0) { throw "docker pull failed for $image" }
}
Write-Host "OK: $image is present"

if (docker ps -aq -f "name=$name") { docker rm -f $name | Out-Null }

try {
  docker run -d --name $name -p "${hostPort}:8000" $image | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "docker run failed for $image" }

  # Probe the agent-server backend health through the container proxy
  # (/server_info -> agent-server on 18000 inside the container), not just the
  # /canvas static UI, which can return 200 while the backend is still down.
  $ok = $false
  for ($i = 0; $i -lt 300; $i++) {
    $canvas = try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:${hostPort}/canvas").StatusCode } catch { 0 }
    $info   = try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:${hostPort}/server_info").StatusCode } catch { 0 }
    if ($canvas -eq 200 -and $info -eq 200) { $ok = $true; break }
    $state = docker inspect -f "{{.State.Status}}" $name 2>$null
    if ($state -ne "running") { throw "Container $name exited before it finished starting" }
    Start-Sleep -Seconds 2
  }

  if (-not $ok) {
    docker logs --tail 40 $name
    throw "agent-canvas backend not healthy on http://localhost:${hostPort}/server_info"
  }
  Write-Host "OK: agent-canvas Docker stack is healthy (/canvas and /server_info return 200)"
}
finally {
  if (docker ps -aq -f "name=$name") { docker rm -f $name | Out-Null }
}
```
<!-- @test:end -->
<!-- @os:end -->
## 4. Настройка локальной LLM в интерфейсе

При первом запуске Agent Canvas открывается процесс первоначальной настройки.
В этом процессе:

1. Оставьте **OpenHands** выбранным в качестве агента и нажмите **Next**.
2. На экране **Set up your LLM** выберите **Advanced**.
3. Оставьте для **Authentication** значение **API key**.
4. Установите **Custom Model** в `openai/Qwen3.6-35B-A3B-GGUF`.
5. Установите **Base URL** в `http://127.0.0.1:13305/api/v1`.
6. В поле **API Key** введите любой непустой заполнитель, например `lemonade-local`. Lemonade не требует реального ключа, но клиенту OpenHands необходимо какое-то значение для отправки.

<!-- @os:windows -->
> **Windows (Docker):** сервер агента запускается внутри контейнера, поэтому в качестве **Base URL** укажите `http://host.docker.internal:13305/api/v1` вместо `http://127.0.0.1:13305/api/v1`.
> Изнутри контейнера `127.0.0.1` указывает на сам контейнер; `host.docker.internal` позволяет обратиться к Lemonade, работающему на хосте Windows, и это имя хоста автоматически предоставляется Docker Desktop.
<!-- @os:end -->

Поля подключения должны выглядеть следующим образом.
Поле API-ключа маскируется интерфейсом.

![Расширенные настройки LLM при первом использовании Agent Canvas с моделью Lemonade и локальным базовым URL-адресом](assets/01-llm-advanced-settings.png)

Затем выберите **All** и задайте дополнительные поля для локальной модели:

1. Прокрутите до **Custom Tokenizer** и установите значение `Qwen/Qwen3.6-35B-A3B`.
2. Прокрутите до **LiteLLM Extra Body** и установите значение `{"enable_thinking": true}`.
3. Нажмите **Next**.

![Вкладка All настроек LLM при первом использовании Agent Canvas с пользовательским токенизатором Qwen](assets/02-llm-all-tokenizer-settings.png)

![Вкладка All настроек LLM при первом использовании Agent Canvas с настроенным дополнительным телом запроса LiteLLM](assets/03-llm-all-extra-body-settings.png)

Настройки LLM должны отображать:

| Поле | Значение |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Префикс `openai/` указывает LiteLLM использовать формат запросов, совместимый с OpenAI, при обращении к конечной точке Lemonade.
Пользовательский токенизатор — это оригинальный токенизатор Hugging Face для модели GGUF; он позволяет OpenHands подсчитывать те же токены шаблона чата, которые видит локальный сервер модели.
Текущая форма LLM для первого использования не показывает настройки конденсера.
Если в вашей сборке Agent Canvas позже появятся настройки конденсера в разделе **Settings > LLM**, используйте `llm_summarizing` и установите максимальное количество токенов ниже контекстного окна Lemonade, например `56000`.

## 5. Установка серверов MCP для GitHub и Slack

В интерфейсе Agent Canvas откройте **Customize** (или **Settings > MCP**), чтобы добавить серверы MCP, предоставляющие агенту инструменты для работы с GitHub и Slack.
Значения токенов отправляются только на ваш локальный сервер агента и сохраняются в виде зашифрованных настроек.

<!-- @os:windows -->
> **Windows (Docker):** приведённые ниже команды MCP-сервера `npx` выполняются внутри контейнера, в который уже включён Node.js, поэтому на хосте ничего дополнительно устанавливать не требуется.
> Поскольку каталог `.openhands` смонтирован, серверы MCP и их токены сохраняются между перезапусками контейнера.
<!-- @os:end -->

### MCP-сервер GitHub

Добавьте новый MCP-сервер со следующими настройками:

| Поле | Значение |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = ваш токен GitHub |

Используйте токен GitHub с доступом на чтение к репозиторию, для которого нужна сводка.

### MCP-сервер Slack

Добавьте второй MCP-сервер со следующими настройками:

| Поле | Значение |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = ID вашего канала для сводки |

Установите в `SLACK_CHANNEL_IDS` ID канала для сводки (то же значение, что и `SLACK_DIGEST_CHANNEL`), чтобы агенту не нужно было просматривать каждый канал Slack.

После добавления обоих серверов воспользуйтесь кнопкой **Test** для каждого из них, чтобы убедиться, что подключение установлено и инструменты доступны.
Сервер GitHub должен отображать список инструментов GitHub, а сервер Slack — список инструментов Slack.

![Страница MCP Agent Canvas с установленными серверами GitHub и Slack](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. Создание автоматизации сводки

В интерфейсе Agent Canvas откройте страницу **Automations** и создайте новую автоматизацию:

1. Выберите **Create automation** и тип **Prompt preset**.
2. Установите **Name** в значение `GitHub Development Digest to Slack`.
3. Установите **Prompt** в следующий текст, заменив заполнители репозитория и канала своими значениями:

   ```text
   Use the GitHub MCP server for exactly one repository: your-org/your-repo.
   Inspect recent development activity since the previous weekday, including
   merged pull requests, newly opened or reopened pull requests, notable
   commits pushed to main or release branches, new issues, important issue
   updates, releases, risks, blockers, and review requests. Keep GitHub
   lookups small: inspect the latest 3 to 5 commits, pull requests, issues,
   and releases. Use the Slack MCP server to post directly to channel ID
   C0123456789. Keep the Slack message concise: title with date range, 3 to 7
   bullets, links back to GitHub, and a Needs attention section only if
   needed. End with: This digest was generated by an AI agent (OpenHands) on
   behalf of the user. Do not include secrets, raw tokens, private
   environment variables, or unrelated Slack messages.
   ```

4. Установите **Trigger** в значение **Cron** с расписанием `0 9 * * 1-5` (9 утра по будням) и укажите **Timezone**, соответствующий вашему часовому поясу, например `America/New_York`.
5. Установите **Timeout** в значение `900` секунд.
6. Сохраните автоматизацию.

Страница сведений об автоматизации показывает новую автоматизацию с её cron-триггером и сгенерированной точкой входа prompt-preset.

![Страница сведений об автоматизации Agent Canvas после создания](assets/05-automation-created.png)
## 7. Протестируйте автоматизацию

На странице сведений об автоматизации в Agent Canvas UI:

1. Нажмите **Run now** (или **Dispatch**), чтобы немедленно запустить автоматизацию один раз.
2. Следите за списком запусков на той же странице. Последний запуск должен перейти в состояние `COMPLETED`.
3. Откройте целевой канал Slack. В нём должен появиться сгенерированный дайджест.

Вам не нужно ждать срабатывания расписания cron — **Run now** запускает выполнение по требованию, что позволяет убедиться в корректности промпта, подключений MCP и публикации в Slack ещё до того, как вы будете полагаться на расписание.

![Автоматизация в Agent Canvas успешно завершила выполнение](assets/06-automation-run-completed.png)

![Канал Slack с сгенерированным дайджестом OpenHands](assets/07-slackbot-message.png)

## Устранение неполадок

<!-- @os:windows -->
- **Порт Docker 8000 уже используется:** сопоставьте другой порт хоста, например `docker run ... -p 8080:8000 ...`, и откройте `http://localhost:8080/canvas`.
- **`docker pull` завершается с ошибкой учётных данных** (например, "A specified logon session does not exist"): выполните pull из интерактивного сеанса Windows или предварительно загрузите образ. Образ публичный, поэтому `docker login` не требуется.
- **Интерфейс загружается, но бэкенд неисправен:** при первом запуске внутри контейнера строится окружение Agent Server. Подождите минуту и обновите страницу, затем проверьте прогресс командой `docker logs <container>`.
- **Agent Canvas не может подключиться к Lemonade из контейнера:** установите **Base URL** для LLM равным `http://host.docker.internal:13305/api/v1` (а не `127.0.0.1`), и убедитесь, что Lemonade запущен на хосте Windows.
<!-- @os:end -->

- **Lemonade не запущен:** перезапустите его командой `lemonade run "${LEMONADE_MODEL}"` из шага 1, затем повторите проверку работоспособности.
- **`npm install -g` завершается с ошибкой доступа:** в Linux или WSL настройте глобальный каталог npm, принадлежащий пользователю, добавьте его в файл инициализации вашей оболочки, затем снова установите Agent Canvas:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Если вы используете `zsh`, добавьте ту же строку `export PATH=...` в `~/.zshrc` вместо `~/.bashrc`.
- **Agent Canvas отклоняет настройки LLM после установки `custom_tokenizer`:** установите `transformers` в окружении Python Agent Server, при необходимости перезапустите Agent Canvas и повторите попытку сохранения настроек LLM. OpenHands требует Transformers для загрузки шаблона чата токенизатора, когда задан `custom_tokenizer`.
- **Agent Canvas не может подключиться к Lemonade:** проверьте `curl -fsS "${LEMONADE_BASE_URL}/health"` и убедитесь, что базовый URL, введённый в форме LLM при первом использовании или в **Settings > LLM**, совпадает с работающей локальной конечной точкой или HTTPS-туннелем.
- **Настройки LLM не сохранились:** убедитесь, что вы нажали **Next** после ввода значений. Повторно откройте **Settings > LLM**, чтобы проверить, сохранились ли значения.
- **GitHub MCP не видит приватные репозитории:** убедитесь, что токен GitHub имеет доступ на чтение к целевому репозиторию и что кнопка **Test** MCP в разделе **Customize** показывает доступные инструменты GitHub.
- **Slack может читать каналы, но не может публиковать сообщения:** пригласите приложение Slack в целевой канал и убедитесь, что у бота есть разрешение `chat:write`.
- **Автоматизация показывает слишком много каналов Slack:** используйте идентификатор канала Slack и задайте `SLACK_CHANNEL_IDS` на сервере Slack MCP в разделе **Customize**.
- **Запуск автоматизации завершается ошибкой или превышает контекст:** убедитесь, что Lemonade был запущен с `ctx_size=65536`, что у LLM OpenHands задан `custom_tokenizer`, и используйте явно указанный репозиторий с ограничением наборов результатов GitHub до 3–5 элементов. Если ваша сборка Agent Canvas предоставляет настройки конденсора, установите максимальное количество токенов конденсора ниже контекстного окна Lemonade.

## Дальнейшие шаги

- Добавьте еженедельный дайджест только по релизам.
- Добавьте автоматизацию, запускаемую по событиям GitHub, для более быстрых оповещений о PR или push.
- Направьте тот же дайджест в Notion, Linear или другой инструмент на базе MCP.

## Ресурсы

- [Плейбуки AMD AI](https://developer.amd.com/playbooks/)
- [Документация Lemonade Server](https://lemonade-server.ai/docs)
- [Репозиторий расширений OpenHands](https://github.com/OpenHands/extensions)
- [Серверы Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Пакет Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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
try { lemonade unload } catch {}
```
<!-- @test:end -->
<!-- @os:end -->