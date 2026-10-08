<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинный перевод.** Эта страница была автоматически переведена с английского языка и не прошла проверку человеком. Она может содержать ошибки, а некоторые инструкции, команды, файлы для загрузки, сведения о доступности продуктов или иное содержимое могут отличаться в зависимости от языка или региона. В случае каких-либо несоответствий или расхождений преимущественную силу имеет оригинальная версия playbook на английском языке.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Обзор

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Для работы с этим руководством требуется минимум **32 ГБ** системной памяти.
<!-- @device:end -->

n8n — это платформа автоматизации рабочих процессов, которая позволяет соединять приложения и сервисы с помощью визуального редактора на основе узлов.

Это руководство научит вас настраивать ИИ-инструмент для суммаризации финансовых новостей, который извлекает последние деловые заголовки из RSS-ленты новостей и использует локальную LLM, работающую на вашей системе, для создания сводки, ориентированной на инвесторов.

## Что вы узнаете

- Как установить и запустить n8n
- Импорт и настройка готового рабочего процесса
- Подключение к Lemonade с использованием встроенной интеграции n8n
- Понимание узлов рабочего процесса и потока данных

## Что такое Lemonade?

[Lemonade](https://lemonade-server.ai) — это платформа для локального обслуживания LLM, созданная для оборудования AMD. Она предоставляет API, совместимый с OpenAI, который работает полностью на вашем компьютере — ваши данные никогда не покидают устройство.

В этом руководстве мы используем Lemonade для обслуживания локальной LLM, к которой подключается n8n для выполнения задач на основе ИИ.

n8n включает **встроенный узел Lemonade** (`Lemonade Chat Model`), который обеспечивает полноценную интеграцию — без необходимости ручной настройки. Это упрощает подключение вашей локальной LLM к рабочим процессам автоматизации.

<!-- @device:halo_box,halo,stx,krk -->
## Настройка конфигурации памяти

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Проверка обновлений программного обеспечения

<!-- @require:software-update -->
<!-- @device:end -->

## Установка необходимого программного обеспечения
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:n8n,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- Linux runs n8n as a Podman container (see compose.yml below), so Node.js and a host n8n install are not required; podman is the only extra prerequisite. -->
<!-- @require:lemonade,podman -->
<!-- @prereq:podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @prereq:lemonade-models-gpt-oss-120b -->
<!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @prereq:lemonade-models-gpt-oss-20b -->
<!-- @var:id=lemonade_model value="gpt-oss-20b-mxfp4-GGUF" -->
<!-- @device:end -->


<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade (robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1
if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
  -H "Content-Type: application/json" `
  --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
}
finally {
  Remove-Item  $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->


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
  "max_tokens": 32
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
<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->
<!-- @os:end -->

## Установка n8n
<!-- @os:windows -->
Установите n8n глобально с помощью npm.

> **Примечание**: Вы можете увидеть предупреждения npm. Это ожидаемо.

```bash
npm install -g n8n
```

<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **Совет**: Пользователям Windows может потребоваться изменить политику выполнения PowerShell (например,
> установить её на RemoteSigned или Unrestricted) перед запуском некоторых команд Powershell.
<!-- @os:end -->


<!-- @os:windows -->
> **Проблема с PATH**: Если `n8n --version` сообщает, что команда не найдена, убедитесь, что каталог глобальных бинарных файлов npm указан в пользовательской переменной `PATH`. Обычный путь установки: `C:\Users\<username>\AppData\Roaming\npm`. 
> Добавьте его в пользовательский путь (Изменить системные переменные среды > Переменные среды > Изменить путь пользователя) и перезапустите терминал. 

<!-- @os:end -->

<!-- @os:linux -->
Теперь мы будем использовать сервис Podman для контейнеризации нашей установки n8n.

Скачайте следующий файл в выбранную вами директорию: [compose.yml](assets/compose.yml)

В этой директории выполните следующую команду:
```bash
podman compose up -d
```

Это должно установить n8n и записать данные в постоянное хранилище.

Запустите n8n, введя `localhost:5678` в адресной строке браузера.
<!-- @os:end -->

<!-- @os:windows -->
## Запуск n8n

Запустите n8n из терминала:

```bash
n8n start
```

<!-- @test:id=n8n-start-windows timeout=300 hidden=True -->
```powershell
$N8N_CMD = "$env:APPDATA\npm\n8n.cmd"
$p = Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$N8N_CMD`" start" -NoNewWindow -PassThru
try {
  $ok = $false
  for ($i=0; $i -lt 120; $i++) {
    # Check HTTP status code only (body may be empty)
    $code = curl.exe -s -o NUL -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz
    if ($LASTEXITCODE -eq 0 -and $code -eq "200") { $ok = $true; break }
    Start-Sleep -Seconds 1
  }
  if (-not $ok) { throw "n8n not ready on http://127.0.0.1:5678/healthz" }
  Write-Host "OK: n8n server is responding"
} finally {
  # Kill the process actually listening on 5678
  $conn = Get-NetTCPConnection -LocalPort 5678 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($conn) { Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue }
  # Also kill wrapper pid just in case
  if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-start-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PODMAN_COMPOSE_PROVIDER="$(command -v podman-compose)"
cleanup() {
  podman compose -f compose.yml down >/dev/null 2>&1 || true
}
trap cleanup EXIT

podman rm -f n8n >/dev/null 2>&1 || true
podman compose -f compose.yml up -d

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "n8n not ready on http://127.0.0.1:5678/healthz"
  podman ps -a || true
  podman logs n8n 2>&1 | tail -30 || true
  exit 1
fi

echo "OK: n8n server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
n8n запускает локальный веб-сервер. Нажмите `'o'` или откройте браузер по адресу `http://localhost:5678`, чтобы получить доступ к редактору.
<!-- @os:end -->


> **Совет**: Держите окно терминала открытым во время использования n8n. Его закрытие может остановить сервер.

## Запуск Lemonade

Lemonade — это локальный сервер, который будет запускать модель и подключаться к n8n.

<!-- @os:linux -->
Откройте графический интерфейс Lemonade, нажав на значок Lemonade на панели задач. Здесь вы можете просматривать модели, бэкенды и загружать предустановленные модели.
<!-- @os:end -->

<!-- @os:windows -->
Откройте графический интерфейс Lemonade, нажав на значок Lemonade. Щёлкните правой кнопкой мыши по значку в трее, чтобы открыть приложение. Затем вы можете добавлять модели, бэкенды и загружать предустановленные модели.
<!-- @os:end -->

>**Совет**: После запуска графический интерфейс Lemonade также доступен по адресу http://localhost:13305

В качестве альтернативы вы можете открыть терминал и выполнить `lemonade list`, чтобы увидеть установленные модели. Затем выполните:

<!-- @device:halo_box -->
<!-- @os:linux -->
```bash
lemonade run gpt-oss-120b-Q4_K_M --llamacpp vulkan
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo -->
```bash
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
```bash
lemonade run gpt-oss-20b-GGUF --llamacpp vulkan
```
<!-- @device:end -->


## Настройка рабочего процесса

### Шаг 1: Регистрация или вход в n8n

При первом открытии n8n вам будет предложено создать учётную запись или войти в систему:

1. Откройте `http://localhost:5678` в браузере
2. Создайте новую локальную учётную запись, указав свой email, или войдите, если у вас уже есть аккаунт
3. После входа вы увидите панель управления n8n

> **Совет**: Если вы заблокированы в своей учётной записи, попробуйте выполнить `n8n user-management:reset`

### Шаг 2: Импорт рабочего процесса

Мы предоставили готовый рабочий процесс, который вы можете импортировать напрямую:

1. Скачайте следующий файл рабочего процесса: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Нажмите **Start from Scratch**, чтобы открыть редактор рабочих процессов. Либо нажмите кнопку + в левом верхнем углу, а затем **Add workflow**.
3. Нажмите меню **...** (три точки) в верхней правой панели и выберите **Import from file**
4. Выберите скачанный файл `financial-news-workflow.json`
5. Рабочий процесс появится на холсте
### Шаг 3: Знакомство с workflow

Импортированный workflow содержит 8 связанных узлов:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Узел | Назначение |
|------|---------|
| **When clicking 'Execute workflow'** | Ручной триггер для запуска workflow |
| **Fetch Financial News Feed** | Узел RSS Read, который получает последние деловые заголовки из RSS-ленты (по умолчанию используется лента NYT Business, API-ключ не требуется) |
| **Aggregate Headlines** | Узел Aggregate, который собирает заголовки и описания из всех элементов ленты в единый список |
| **Clean Extracted News Data** | Узел Set, который объединяет все заголовки в одно текстовое поле |
| **AI Financial News Summarizer** | AI Agent, обрабатывающий новости с системным промптом финансового аналитика |
| **Lemonade Chat Model** | Подключается к вашему локальному серверу Lemonade, на котором работает LLM |
| **Structured Output Parser** | Форматирует вывод модели в структурированный JSON |
| **Convert to File** | Преобразует сводку в файл для скачивания |

> **Совет**: чтобы использовать другой источник новостей, дважды щёлкните узел **Fetch Financial News Feed** и замените URL на любую другую бизнес- или рыночную RSS-ленту по вашему выбору.

### Шаг 4: Настройка учётных данных Lemonade

Перед запуском workflow необходимо подключить его к локальному серверу Lemonade:

1. Дважды щёлкните узел **Lemonade Chat Model** в n8n
2. В выпадающем меню **Credential to connect with** выберите **Create New Credential**
3. Введите значения из таблицы ниже и нажмите сохранить.
4. Выберите нужную модель, загруженную в Lemonade Server.

  | Поле | Значение |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Примечание**: перед тестированием выполните в терминале команду `lemonade status`, чтобы убедиться, что сервер Lemonade запущен.
<!-- @device:halo_box -->
> Этот workflow использует GPT-OSS-120B, которая предустановлена в Lemonade. Вы можете изменить её на другую загруженную модель в настройках узла Lemonade Chat Model.
<!-- @device:end -->

### Шаг 5: Тестирование workflow

1. Убедитесь, что Lemonade запущен с загруженной моделью
2. Нажмите **Execute workflow** внизу по центру холста
3. Наблюдайте, как каждый узел выполняется слева направо — по завершении они становятся зелёными
4. Дважды щёлкните узел **AI Financial News Summarizer**, чтобы увидеть сгенерированную сводку в нижней панели.
5. Дважды щёлкните узел **Convert to File**, чтобы скачать соответствующий текстовый файл в нижней панели.

## Знакомство с AI Agent

AI Financial News Summarizer использует системный промпт, разработанный для финансового анализа:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Агент получает очищенные данные новостей и выводит структурированную сводку с настроением рынка.

### Сохранение workflow

Нажмите на название workflow вверху и при необходимости переименуйте его. Workflow автоматически сохраняется по мере работы.

## Дальнейшие шаги

- **Настройка автоматизации по расписанию**: замените Manual Trigger на **Schedule Trigger**, чтобы выполнять workflow ежедневно
- **Отправка уведомлений**: добавьте узел **Discord**, **Slack** или **Email**, чтобы получать сводки
- **Пробуйте разные модели**: измените модель в узле Lemonade Chat Model, чтобы поэкспериментировать с различными LLM
- **Измените источник новостей**: укажите в узле **Fetch Financial News Feed** другую RSS-ленту, чтобы отслеживать другие разделы или издания
- **Пробуйте разные бэкенды**: n8n также поддерживает [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio и другие локальные бэкенды LLM

### Изучите шаблоны n8n

n8n предлагает сотни готовых шаблонов workflow. Просмотрите официальную библиотеку шаблонов по ссылке:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Выполните поиск по словам "AI", "LLM" или "automation", чтобы найти workflow, которые можно импортировать и настроить под себя.

Дополнительную информацию можно найти в [документации n8n](https://docs.n8n.io/).

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