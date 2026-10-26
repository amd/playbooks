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
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Обзор

[OpenHands](https://github.com/All-Hands-AI/OpenHands) — это программный ИИ-агент,
который может писать код, выполнять команды, просматривать веб-страницы и редактировать файлы в реальном
рабочем пространстве. Вместо того чтобы копировать подсказки из окна чата, вы направляете
агента на папку проекта и позволяете ему выполнять работу: реализовать функцию, исправить
ошибку, написать тесты или объяснить кодовую базу.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) — рекомендуемый
интерфейс в браузере для запуска OpenHands. Одна команда `agent-canvas` запускает
сервер агента, бэкенд автоматизации и веб-фронтенд вместе, что позволяет
вести беседу с агентом прямо из браузера.

Чтобы всё оставалось на вашей системе AMD, агент взаимодействует с локальной моделью, обслуживаемой
Lemonade Server. Lemonade предоставляет доступ к этой модели через API, совместимый с OpenAI,
поэтому Agent Canvas может настроить её как любую другую конечную точку в стиле OpenAI,
при этом модель, ваш код и контекст беседы остаются на вашем
компьютере.

В этом руководстве вы запустите локальную модель, запустите Agent Canvas, укажете
на эту модель и выполните свою первую задачу по написанию кода в реальной папке проекта.

## Что вы узнаете

- Как запустить Lemonade Server и убедиться, что локальная модель отвечает на запросы чата
- Как установить и запустить Agent Canvas из пакета npm
- Как настроить Agent Canvas на использование локальной модели Lemonade в качестве LLM
- Как начать беседу OpenHands и наблюдать, как агент редактирует файлы и выполняет
  команды в рабочем пространстве
- Как проверить изменения, внесённые агентом, и направлять его последующими сообщениями

## Основные понятия

| Понятие | Что это такое | Место в этом руководстве |
| --- | --- | --- |
| Lemonade Server | Платформа для локального обслуживания LLM, созданная для оборудования AMD, предоставляющая API, совместимый с OpenAI. Ваши данные никогда не покидают ваш компьютер. | Запускает модель, которая обеспечивает работу агента. |
| OpenHands | ИИ-агент для программного обеспечения, который читает и редактирует файлы, выполняет команды оболочки и просматривает веб-страницы внутри рабочего пространства. | Агент, которым вы управляете из чата. |
| Agent Canvas | Интерфейс в браузере и бэкенд, который запускает беседы OpenHands и показывает вызовы инструментов и изменения файлов. | Запускает стек и размещает вашу беседу. |
| Рабочее пространство | Папка проекта, которую агенту разрешено читать и изменять. | Цель правок и команд агента. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Рабочие процессы агента для написания кода выигрывают от более крупной модели и окна контекста. Используйте не
> менее 32 ГБ системной памяти, а для более крупных моделей GGUF предпочтительнее 64 ГБ и более.
<!-- @device:end -->

## Настройка конфигурации памяти

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Проверка обновлений программного обеспечения

<!-- @require:software-update -->
<!-- @device:end -->

## Предварительные требования


<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- @os:end -->

Вам понадобится:

- Установленный Lemonade Server, способный обслуживать указанную ниже модель.

<!-- @os:linux -->
- Node.js 22.12 или более поздней версии и `npm` (используются CLI `agent-canvas`).
- `uv` — менеджер пакетов Python, который Agent Canvas использует для управления
  средой сервера агента. Если в вашей системе его ещё нет, установите его из
  [руководства по установке uv](https://docs.astral.sh/uv/getting-started/installation/),
  прежде чем запускать Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop для Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  установленный и запущенный. В Windows стек Agent Canvas работает из
  опубликованного образа Docker, который включает в себя Node.js, `uv` и
  пакет `@openhands/agent-canvas`, поэтому устанавливать их на хосте не требуется.
<!-- @os:end -->

- Папка проекта для работы. Это может быть любой локальный git-репозиторий или каталог
  с кодом, над которым вы хотите, чтобы агент работал.

<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @os:linux -->
<!-- @test:id=prereq-clis-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

lemonade --version
node -v
npm -v

# uv is a required prerequisite (agent-canvas uses it to build its Python env).
# Install it only if the runner doesn't already have it.
# TODO: remove this self-provisioning once the runners ship uv by default.
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"
uv --version

echo "OK: lemonade, node, npm, and uv are all available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=prereq-clis-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# On Windows the Agent Canvas stack runs from the published Docker image, so the
# only host prerequisites are Lemonade and a running Docker engine. Node.js, uv,
# and agent-canvas are bundled inside the container.
lemonade --version
docker version --format "{{.Server.Version}}"

Write-Host "OK: lemonade and docker are available"
```
<!-- @test:end -->
<!-- @os:end -->

## 1. Запуск Lemonade Server

Запустите модель из Lemonade CLI:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Выберите модель, подходящую для вашего оборудования.** `Qwen3.6-35B-A3B-GGUF` (~20 ГБ) — это мощная модель для написания кода, но ей требуется большой объём памяти. Если на вашем устройстве ограниченный объём памяти или видеопамяти GPU, выберите вместо неё меньшую модель GGUF из библиотеки моделей Lemonade и используйте этот идентификатор модели на протяжении всего руководства.

> **Примечание.** При первом запуске `lemonade run` модель загружается, если она ещё не присутствует в системе, что может занять некоторое время в зависимости от размера модели и скорости вашего соединения.

Lemonade предоставляет API, совместимый с OpenAI, по адресу:

```text
http://127.0.0.1:13305/api/v1
```

## 2. Проверка локальной модели

Убедитесь, что Lemonade может обслуживать выбранную модель:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Затем отправьте небольшой запрос чата:

```bash
curl -sS "http://127.0.0.1:13305/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.6-35B-A3B-GGUF",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

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
model_id = "${lemonade_model}"

entry = None
for item in data.get("data", []):
    if item.get("id") == model_id:
        entry = item
        break

if entry is None:
    print(f"Model {model_id} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print(f"Model {model_id} is present but not downloaded in Lemonade. Please download it before running CI.")
    sys.exit(1)

print(f"OK: {model_id} model is downloaded in Lemonade")
PY

body='{
  "model": "${lemonade_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Lemonade chat/completions returned a response"
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

if (-not $modelsJson) {throw "Lemonade server not ready on http://127.0.0.1:13305"}
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

$body = @{
  model = "${lemonade_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openhands-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) {throw "Empty response from Lemonade chat/completions"}
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->
## 3. Установка и запуск Agent Canvas

<!-- @os:linux -->
Установите опубликованный пакет Agent Canvas глобально:

```bash
npm install -g @openhands/agent-canvas
```

<!-- @test:id=agent-canvas-version-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# agent-canvas is expected to be provisioned on the runner. Fail loudly if it
# isn't, rather than installing it here.
if ! command -v agent-canvas >/dev/null 2>&1; then
  echo "agent-canvas is not on PATH; the runner must provision it before CI runs"
  exit 1
fi

# Prefer --version; fall back to --help if this build has no --version flag.
agent-canvas --version || agent-canvas --help

echo "OK: agent-canvas CLI is on PATH"
```
<!-- @test:end -->

Затем запустите полный стек из терминала:

```bash
agent-canvas
```

По умолчанию Agent Canvas запускается на `http://localhost:8000`. Откройте этот URL
в своём браузере. Порт не имеет особого значения — если 8000 уже занят, укажите
любой свободный порт с помощью `--port` (или `-p`) при запуске Agent Canvas:

```bash
agent-canvas --port 3000
```

Затем откройте `http://localhost:3000`. Локальный бэкенд по умолчанию должен отображаться
как исправный на главном экране.

Команда `agent-canvas` запускает сервер агента, автоматизационный бэкенд и
веб-фронтенд вместе. Вам нужна только эта одна команда для запуска OpenHands
локально.

<!-- @test:id=agent-canvas-server-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

log="/tmp/agent-canvas-ci.log"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

# First launch builds the agent server's uv-managed Python env, so allow a generous startup window.
agent-canvas >"$log" 2>&1 &
p=$!

# Probe the agent-server backend health (18000/server_info), NOT just the 8000
# ingress root: the ingress serves the static frontend and returns 200 for /
# even when the agent-server is down.
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
  echo "---- agent-canvas log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: agent-canvas agent-server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
В Windows запустите опубликованный образ контейнера Agent Canvas с помощью Docker Desktop.
Образ включает Agent Server, автоматизационный бэкенд и веб-фронтенд, поэтому
не нужно устанавливать Node.js, `uv` или CLI на хосте.

Сначала создайте папки конфигурации и рабочего пространства, которые монтирует контейнер:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Загрузите опубликованный образ (он публичный, поэтому вход не требуется):

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

Откройте `http://localhost:8000/canvas` в своём браузере. Если порт 8000 уже
занят, сопоставьте другой порт хоста, например `-p 8080:8000`, и откройте
`http://localhost:8080/canvas` вместо него.

> **Примечание:** первый запуск инициализирует Agent Server внутри контейнера,
> поэтому может пройти минута-две, прежде чем бэкенд сообщит о работоспособности.

Монтирование `.openhands` сохраняет ваш профиль LLM и настройки между перезапусками
контейнера. Остальная часть этого руководства настраивает всё через интерфейс
Agent Canvas в вашем браузере.

<!-- @test:id=agent-canvas-docker-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$image    = "ghcr.io/openhands/agent-canvas:1.14.0"
$name     = "openhands-agent-canvas-ci"
$hostPort = 18080

# The image is expected to be provisioned on the runner. Fail loudly if it
# isn't, rather than pulling it here.
$imgId = docker images -q $image
if (-not $imgId) {
  throw "Image $image is not present; the runner must provision it before CI runs"
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

## 4. Настройка локальной LLM

При первом запуске Agent Canvas открывает процесс первоначальной настройки. В этом процессе:

1. Оставьте **OpenHands** выбранным в качестве агента и нажмите **Next**.
2. На экране **Set up your LLM** выберите **Advanced**.
3. Оставьте **Authentication** установленным на **API key**.
4. Установите **Custom Model** равным `openai/Qwen3.6-35B-A3B-GGUF`.
5. Установите **Base URL** равным `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > В Windows стек работает в контейнере, который не может обратиться к хосту по адресу
   > `127.0.0.1`. Вместо этого используйте `http://host.docker.internal:13305/api/v1`, чтобы
   > контейнеризированный агент мог достучаться до Lemonade, запущенного на хосте Windows.
   <!-- @os:end -->
6. В поле **API Key** введите любой непустой заполнитель, например `lemonade-local`.
   Lemonade не требует реального ключа, но клиенту OpenHands нужно значение
   для отправки.
7. Нажмите **Next**.

Завершённые настройки Advanced должны выглядеть так. Поле API key
скрыто интерфейсом.

![Расширенные настройки LLM при первом использовании Agent Canvas с моделью Lemonade и локальным базовым URL](assets/01-llm-advanced-settings.png)

Agent Canvas сохраняет эти значения как профиль LLM. Если ваша версия просит
назвать этот профиль, используйте имя без пробелов, например `lemonade-local`. Если вы
измените модели позже, откройте **Settings > LLM** и обновите те же поля Advanced. Вы
можете переключать сохранённые профили из поля ввода чата с помощью команды `/model`.

## 5. Открытие рабочего пространства

Агент может читать и изменять только файлы внутри выбранного вами рабочего пространства.
Перед началом задачи укажите Agent Canvas на папку вашего проекта:

1. На главном экране выберите **Open Workspace**.
2. Выберите папку, содержащую ваш проект (например, репозиторий git,
   над которым вы хотите, чтобы агент работал).
3. Начните новую беседу в этом рабочем пространстве.

Всё, что делает агент — чтение файлов, выполнение команд, редактирование кода — ограничено
этим рабочим пространством.

![Домашний экран Agent Canvas после первоначальной настройки](assets/02-agent-canvas-home.png)

## 6. Выполнение вашей первой задачи по программированию

После открытия рабочего пространства и выбора локальной LLM введите конкретную задачу в
чат. Хорошей первой задачей является небольшая и проверяемая, например:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Наблюдайте за временной шкалой беседы. OpenHands будет:

- Читать рабочее пространство, чтобы понять структуру.
- Создавать `hello.py` с запрошенной функцией и тестовым блоком.
- При необходимости запускать `python3 hello.py` для проверки вывода.
- Сообщать о том, что было сделано, и любом выводе команд в чате.

Вы должны увидеть новый файл, появившийся в рабочем пространстве, а итоговое сообщение
агента должно описывать сделанное изменение. Это момент результата: агент
написал и выполнил реальный код в папке вашего проекта.

## 7. Проверка работы агента и управление им

После завершения агентом шага проверьте его работу перед принятием следующего:

- **Изменения файлов**: используйте файловый браузер рабочего пространства или представление
  различий (diff) агента, чтобы увидеть точно, что было добавлено, изменено или удалено.
- **Вывод команд**: разверните любую выполненную агентом команду, чтобы увидеть stdout, stderr
  и код завершения.
- **Дальнейшие действия**: если результат не соответствует ожидаемому, ответьте в той же
  беседе с исправлением. Агент сохраняет предыдущий контекст и
  продолжает работу над теми же файлами.

Например, если тест не вывел ожидаемое приветствие, ответьте:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Агент повторно прочитает файл, выполнит команду, диагностирует проблему и снова отредактирует
файл — всё в той же беседе.
## Устранение неполадок

<!-- @os:linux -->
- **`agent-canvas` отсутствует в PATH:** переустановите с помощью
  `npm install -g @openhands/agent-canvas` и убедитесь, что каталог глобальных
  бинарных файлов npm добавлен в PATH, прежде чем запускать `agent-canvas` из
  нового терминала.
- **`npm install -g` завершается с ошибкой прав доступа:** настройте
  принадлежащий пользователю глобальный каталог npm, затем заново откройте
  терминал и снова установите Agent Canvas.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` отсутствует:** установите его согласно
  [руководству по установке uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas использует `uv` для управления Python-окружением сервера агента.
<!-- @os:end -->

<!-- @os:windows -->
- **Команда `docker pull` или `docker run` не может подключиться:** убедитесь,
  что Docker Desktop запущен (его значок в виде кита отображается в системном
  трее) и что движок завершил запуск. Команда `docker version` должна выводить
  разделы Client и Server.
- **Контейнер запускается, но серверная часть так и не переходит в исправное
  состояние:** при первом запуске внутри контейнера инициализируется Agent
  Server; подождите минуту-другую, затем проверьте ошибки командой
  `docker logs <container>`.
- **Контейнер не может подключиться к Lemonade:** контейнер обращается к хосту
  через `host.docker.internal`. Убедитесь, что Lemonade работает на хосте
  Windows с помощью команды `lemonade status`, и используйте
  `http://host.docker.internal:13305/api/v1` в качестве Base URL при настройке
  LLM.
<!-- @os:end -->

- **Интерфейс загружается, но серверная часть отображается как неисправная:**
  подождите минуту-другую, пока сервер агента завершит запуск, затем обновите
  страницу. Если состояние не меняется, перезапустите стек и проверьте логи на
  наличие ошибок.
- **Запросы чата Lemonade завершаются с ошибкой подключения:** убедитесь, что
  команда `curl -fsS "http://127.0.0.1:13305/api/v1/health"` выполняется
  успешно и что Lemonade по-прежнему обслуживает модель — проверьте это с
  помощью `lemonade status`.
- **Агент выдаёт ошибку о превышении длины контекста или лимита токенов:**
  начните новую беседу, чтобы у агента не накапливалась слишком большая
  история. Если проблема повторяется, перезапустите Lemonade с большим
  значением `ctx_size`, чем стандартное 65536 (например, `ctx_size=131072`),
  если позволяет объём памяти.
- **Агент выдаёт правки низкого качества или неполные:** переключитесь на
  более крупную модель в Lemonade либо поставьте агенту более простую и
  конкретную задачу и дождитесь её завершения, прежде чем запрашивать
  следующее изменение.

## Дальнейшие шаги

- Попробуйте выполнить более крупную задачу в том же рабочем пространстве,
  например добавить файл с модульными тестами или исправить известную ошибку,
  и просмотрите изменения агента перед их сохранением.
- Подключите MCP-сервер, например GitHub или Slack, в разделе **Customize**,
  чтобы агент мог читать issue или публиковать обновления во время работы.
- Сохраните несколько LLM-профилей (быструю небольшую модель и более мощную
  крупную модель) и переключайтесь между ними с помощью `/model` прямо во
  время беседы.
- Перейдите к разделу [автоматизации OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview),
  чтобы превратить повторяющиеся циклы разработки в запуски агента по
  расписанию или по событию.

## Ресурсы

- [Документация OpenHands](https://docs.openhands.dev/)
- [Обзор Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Настройка Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM-профили и настройка моделей](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Документация Lemonade Server](https://lemonade-server.ai/docs)

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