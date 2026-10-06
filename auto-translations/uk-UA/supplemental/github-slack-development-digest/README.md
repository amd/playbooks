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
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Огляд

Розробники витрачають багато часу на невеликі повторювані цикли: перегляд позначених pull request'ів, відповіді на коментарі GitHub, сортування нових issue, перетворення гілок Slack на нотатки для стендапів або подальші дії після інцидентів, а також відстеження сигналів щодо релізів чи досліджень.
Кожен такий цикл знайомий, але все одно потребує судження: зібрати потрібний контекст, вирішити, що важливо, і опублікувати чітке оновлення там, де команда вже працює.

[Автоматизації OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview) перетворюють ці цикли на заплановані або запущені за подією діалоги агента: запуски, під час яких AI-агент програмного забезпечення може читати контекст, викликати інструменти та готувати оновлення.
Спільні шаблони автоматизації в каталозі розширень OpenHands дотримуються цього шаблону для перегляду pull request'ів GitHub, моніторингу репозиторіїв, сортування issue в Linear, ретроспектив інцидентів, дайджестів стендапів у Slack і дослідницьких оглядів: автоматизація прокидається, використовує налаштовані інтеграції, такі як GitHub або Slack, для отримання контексту, аналізує цей контекст за допомогою великої мовної моделі (LLM) і записує результат назад.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) — це локальна площина керування для створення й тестування цих автоматизацій.
У цьому посібнику вона запускає OpenHands Agent Server, фоновий процес, що виконує діалоги агента, і з'єднує агента з зовнішніми сервісами, такими як GitHub і Slack.

Щоб залишити робочий процес у межах вашої AMD-системи, агент спілкується з локальною моделлю, яку обслуговує Lemonade Server.
Lemonade надає цю модель через API, сумісний з OpenAI, тож Agent Canvas може налаштувати її як віддалену точку доступу у стилі OpenAI, тоді як модель, промпт і контекст робочого процесу залишаються локальними.

У цьому посібнику ви створите одну конкретну автоматизацію: запланований дайджест розробки з GitHub у Slack.
Вона використовує GitHub для перевірки недавньої активності в репозиторії, Slack для публікації дайджесту, виклики API Agent Canvas для налаштування та тестування автоматизації, а також Lemonade для локального запуску LLM.

![Діаграма архітектури, що показує GitHub MCP, автоматизацію OpenHands, Lemonade Server і Slack MCP](assets/00-architecture-overview.png)

## Що ви дізнаєтеся

- Як запустити Lemonade Server і перевірити, що локальна модель відповідає на запити чату
- Як запустити Agent Canvas і спрямувати його Agent Server на локальну LLM
- Як встановити сервери GitHub і Slack Model Context Protocol (MCP) через API Agent Server
- Як створити та запустити заплановану автоматизацію OpenHands, яка публікує дайджест розробки в Slack
- Як усунути найпоширеніші збої локальної моделі та автоматизації

## Основні концепції

| Концепція | Що це таке | Де вона застосовується в цьому посібнику |
| --- | --- | --- |
| Lemonade Server | Локальна платформа обслуговування LLM, створена для апаратного забезпечення AMD, яка надає API, сумісний з OpenAI. Ваші дані ніколи не залишають ваш комп'ютер. | Запускає модель, що живить агента. |
| OpenHands Agent Server | Фоновий процес, що виконує діалоги агента OpenHands. | Розміщує агента, його профіль LLM та його сервери MCP. |
| Agent Canvas | Локальна площина керування для OpenHands, яка запускає Agent Server та інтерфейс для перегляду запусків агента. | Запускає бекенди та надає API, який ви викликаєте. |
| MCP-сервер | Сервер Model Context Protocol, який надає агенту інструменти для зовнішнього сервісу, такого як GitHub чи Slack. | Дозволяє агенту читати GitHub і писати в Slack. |
| Автоматизація OpenHands | Запланований або запущений за подією діалог агента, який отримує контекст, аналізує його та записує результат десь. | Дайджест з GitHub у Slack, який ви створюєте тут. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Робочі процеси агента кодування виграють від більшої моделі та більшого контекстного вікна.
> Використовуйте щонайменше 32 ГБ системної пам'яті, і надавайте перевагу 64 ГБ або більше для більших GGUF-моделей.
<!-- @device:end -->

## Налаштування конфігурації пам'яті

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Перевірка оновлень програмного забезпечення

<!-- @require:software-update -->
<!-- @device:end -->

## Передумови

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

Вам знадобиться:

- Lemonade Server, встановлений за стандартним [посібником зі встановлення Lemonade](https://lemonade-server.ai/docs/guide/install/).

<!-- @os:linux -->
- Node.js 22.12 або новіший та `npm`, що використовуються для встановлення опублікованого CLI Agent Canvas і запуску MCP-серверів за допомогою `npx`.
- `uv`, менеджер пакетів Python, який Agent Canvas використовує для побудови середовища Agent Server. Якщо його ще не встановлено, встановіть його за [посібником зі встановлення uv](https://docs.astral.sh/uv/getting-started/installation/).
- Нещодавно опублікований пакет `@openhands/agent-canvas` з налаштуваннями агента на основі схеми, `LLMSummarizingCondenserSettings.max_tokens` та підтримкою `custom_tokenizer` для LLM.
- Пакет Python `transformers`, доступний у середовищі Agent Server. Він потрібен для підрахунку токенів шаблону чату, коли встановлено `custom_tokenizer`.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop для Windows](https://docs.docker.com/desktop/setup/install/windows-install/), встановлений і запущений. У Windows стек Agent Canvas працює з опублікованого Docker-образу, який включає Node.js, `uv`, `transformers` і пакет `@openhands/agent-canvas`, тож вам не потрібно встановлювати їх на хості.
<!-- @os:end -->

- Токен GitHub з правами читання для репозиторію, який потрібно підсумувати.
- Токен бота Slack (`xoxb-...`) з правами `chat:write` і доступом до читання каналу.
- ID команди Slack (`T...`).
- ID каналу Slack (`C...`), куди слід публікувати дайджест.

Запросіть застосунок Slack до цільового каналу перед тестуванням автоматизації.
## Змінні, що використовуються в цьому посібнику

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

Ці дві змінні використовуються у наведених нижче командах перевірки.
Модель, токенізатор та інші налаштування LLM вводяться безпосередньо в інтерфейсі Agent Canvas на пізніших кроках, тому їхні буквальні значення наведено там, де вони потрібні.

Наступні значення вводяться в інтерфейс Agent Canvas на пізніших кроках.
Встановіть їх тут, щоб потім скопіювати:

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

Використовуйте явне значення `owner/repo` для `GITHUB_REPO_FILTER`.
Широкі підстановочні знаки для організацій можуть повертати занадто великий контекст MCP для локальних моделей.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Запуск Lemonade Server

Запустіть модель за допомогою Lemonade CLI:

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

> **Виберіть модель, яка підходить для вашого обладнання.** `Qwen3.6-35B-A3B-GGUF` (~20 ГБ) — потужна модель для цього робочого процесу, але вона потребує великого пулу пам'яті.
> Якщо ваш пристрій має обмежену пам'ять або обсяг відеопам'яті GPU, виберіть меншу модель GGUF з бібліотеки моделей Lemonade та використовуйте цей ідентифікатор моделі (і відповідний токенізатор) протягом усього цього посібника.

> **Примітка.** Перший запуск `lemonade run` завантажує модель, якщо її ще немає, що може зайняти певний час залежно від розміру моделі та швидкості з'єднання.

Lemonade надає сумісний з OpenAI API за адресою:

```text
http://127.0.0.1:13305/api/v1
```

Додатково: якщо Agent Canvas або програма автоматизації не знаходяться на тому ж пристрої, опублікуйте кінцеву точку Lemonade через захищений тунель і використовуйте URL-адресу HTTPS як базову URL-адресу LLM.
[ngrok](https://ngrok.com/) надає доступ до локального порту з інтернету через захищену URL-адресу HTTPS; для цього потрібен безкоштовний обліковий запис ngrok, а `YOUR_NGROK_DOMAIN.ngrok-free.dev` слід замінити власним зарезервованим доменом:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Перевірка локальної моделі

Переконайтеся, що Lemonade може обслуговувати обрану модель:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Потім надішліть невеликий запит чату:

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

Потім надішліть невеликий запит чату:

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

Якщо у відповідь повертається масив `choices`, Lemonade готовий до роботи з Agent Canvas.

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
Встановіть опублікований пакет Agent Canvas та запустіть повний стек:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Якщо глобальне встановлення npm завершується помилкою доступу, див. розділ про усунення несправностей з правами доступу npm нижче.

За замовчуванням Agent Canvas запускається за адресою `http://localhost:8000`.
Відкрийте цю URL-адресу у браузері.
Порт не є особливим — якщо 8000 вже зайнятий, вкажіть будь-який вільний порт за допомогою `--port` (або `-p`).
Типовий локальний бекенд повинен відображатися як справний на головному екрані.

> **Примітка.** Перший запуск створює керовsomande середовище Python для Agent Server, тому може знадобитися кілька хвилин, перш ніж бекенд повідомить про справний стан.

Команда `agent-canvas` одночасно запускає агентський сервер, бекенд автоматизації та веб-фронтенд.
Вам потрібна лише ця одна команда, щоб запустити OpenHands локально.
Решта цього посібника налаштовує все через інтерфейс Agent Canvas у вашому браузері.
<!-- @os:end -->

<!-- @os:windows -->
У Windows запустіть опублікований образ контейнера Agent Canvas за допомогою Docker Desktop.
Образ містить Agent Server, бекенд автоматизації та веб-фронтенд, тому вам не потрібно встановлювати Node.js, `uv` чи CLI на хост.

Спочатку створіть папки конфігурації та робочого простору, які монтує контейнер:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Завантажте опублікований образ (приблизно 6 ГБ; він публічний, тому вхід не потрібен):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Потім запустіть стек:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Відкрийте `http://localhost:8000/canvas` у браузері.
Якщо порт 8000 вже зайнятий, зіставте інший порт хоста, наприклад `-p 8080:8000`, і замість цього відкрийте `http://localhost:8080/canvas`.

> **Примітка.** Перший запуск створює середовище Agent Server всередині контейнера, тому може знадобитися кілька хвилин, перш ніж бекенд повідомить про справний стан.

Монтування `.openhands` зберігає ваш профіль LLM, сервери MCP та автоматизації між перезапусками контейнера.
Решта цього посібника налаштовує все через інтерфейс Agent Canvas у вашому браузері за адресою `http://localhost:8000/canvas`.
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
## 4. Налаштування локального LLM в інтерфейсі

Під час першого запуску Agent Canvas відкриває процес початкового налаштування.
У цьому процесі:

1. Залиште **OpenHands** вибраним як агента та натисніть **Next**.
2. На екрані **Set up your LLM** виберіть **Advanced**.
3. Залиште **Authentication** зі значенням **API key**.
4. Встановіть **Custom Model** на `openai/Qwen3.6-35B-A3B-GGUF`.
5. Встановіть **Base URL** на `http://127.0.0.1:13305/api/v1`.
6. У полі **API Key** введіть будь-яке непорожнє значення-заповнювач, наприклад `lemonade-local`. Lemonade не вимагає справжнього ключа, але клієнту OpenHands потрібне якесь значення для надсилання.

<!-- @os:windows -->
> **Windows (Docker):** Agent Server працює всередині контейнера, тому встановіть **Base URL** на `http://host.docker.internal:13305/api/v1` замість `http://127.0.0.1:13305/api/v1`.
> Зсередини контейнера `127.0.0.1` означає сам контейнер; `host.docker.internal` звертається до Lemonade, що працює на хості Windows, і Docker Desktop надає це ім’я хоста автоматично.
<!-- @os:end -->

Поля підключення мають виглядати так.
Поле API-ключа приховане інтерфейсом.

![Налаштування Advanced LLM під час першого запуску Agent Canvas з моделлю Lemonade та локальною базовою URL-адресою](assets/01-llm-advanced-settings.png)

Потім виберіть **All** і налаштуйте додаткові поля локальної моделі:

1. Прокрутіть до **Custom Tokenizer** і встановіть значення `Qwen/Qwen3.6-35B-A3B`.
2. Прокрутіть до **LiteLLM Extra Body** і встановіть значення `{"enable_thinking": true}`.
3. Натисніть **Next**.

![Вкладка All налаштувань LLM під час першого запуску Agent Canvas з користувацьким токенізатором Qwen](assets/02-llm-all-tokenizer-settings.png)

![Вкладка All налаштувань LLM під час першого запуску Agent Canvas з налаштованим LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

Налаштування LLM мають показувати:

| Поле | Значення |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Префікс `openai/` вказує LiteLLM використовувати форматування запитів, сумісне з OpenAI, для кінцевої точки Lemonade.
Користувацький токенізатор — це оригінальний токенізатор Hugging Face для моделі GGUF; він дозволяє OpenHands рахувати ті самі токени шаблону чату, які бачить локальний сервер моделі.
Поточна форма LLM для першого запуску не показує налаштування кондесера (condenser).
Якщо у вашій збірці Agent Canvas пізніше з’являться налаштування кондесера в **Settings > LLM**, використовуйте `llm_summarizing` і встановіть максимальну кількість токенів нижче контекстного вікна Lemonade, наприклад `56000`.

## 5. Встановлення MCP-серверів GitHub та Slack

В інтерфейсі Agent Canvas відкрийте **Customize** (або **Settings > MCP**), щоб додати MCP-сервери, які надають агенту інструменти для GitHub та Slack.
Значення токенів надсилаються лише до вашого локального Agent Server і зберігаються як зашифровані налаштування.

<!-- @os:windows -->
> **Windows (Docker):** наведені нижче команди MCP-серверів `npx` виконуються всередині контейнера, який вже включає Node.js, тому на хості нічого додатково не встановлюється.
> Оскільки `.openhands` змонтовано, MCP-сервери та їхні токени зберігаються між перезапусками контейнера.
<!-- @os:end -->

### MCP-сервер GitHub

Додайте новий MCP-сервер з такими налаштуваннями:

| Поле | Значення |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = ваш токен GitHub |

Використовуйте токен GitHub з правами читання для репозиторію, для якого потрібно створювати огляди.

### MCP-сервер Slack

Додайте другий MCP-сервер з такими налаштуваннями:

| Поле | Значення |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = ідентифікатор вашого каналу для дайджестів |

Встановіть `SLACK_CHANNEL_IDS` на ідентифікатор каналу для дайджестів (те саме значення, що й `SLACK_DIGEST_CHANNEL`), щоб агенту не потрібно було переглядати кожен канал Slack.

Після додавання обох серверів скористайтеся кнопкою **Test** для кожного з них, щоб підтвердити підключення та доступність інструментів.
Сервер GitHub має показати список інструментів GitHub, а сервер Slack — список інструментів Slack.

![Сторінка MCP в Agent Canvas зі встановленими серверами GitHub та Slack](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. Створення автоматизації дайджесту

В інтерфейсі Agent Canvas відкрийте сторінку **Automations** і створіть нову автоматизацію:

1. Виберіть **Create automation** і тип **Prompt preset**.
2. Встановіть **Name** на `GitHub Development Digest to Slack`.
3. Встановіть **Prompt** на наступний текст, замінивши заповнювачі репозиторію та каналу вашими значеннями:

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

4. Встановіть **Trigger** на **Cron** із розкладом `0 9 * * 1-5` (9 ранку у будні дні) та встановіть **Timezone** на ваш часовий пояс, наприклад `America/New_York`.
5. Встановіть **Timeout** на `900` секунд.
6. Збережіть автоматизацію.

Сторінка деталей автоматизації показує нову автоматизацію з її cron-тригером та згенерованою точкою входу prompt-preset.

![Сторінка деталей автоматизації в Agent Canvas після створення](assets/05-automation-created.png)
## 7. Протестуйте автоматизацію

На сторінці деталей автоматизації в Agent Canvas UI:

1. Натисніть **Run now** (або **Dispatch**), щоб запустити автоматизацію негайно один раз.
2. Слідкуйте за списком запусків на цій же сторінці. Останній запуск повинен перейти в стан `COMPLETED`.
3. Відкрийте цільовий Slack-канал. Він повинен містити згенерований дайджест.

Не потрібно чекати спрацювання розкладу cron — **Run now** запускає виконання на вимогу, щоб ви могли переконатися, що промпт, MCP-з'єднання та публікація в Slack працюють, перш ніж покладатися на розклад.

![Автоматизація Agent Canvas успішно завершила запуск](assets/06-automation-run-completed.png)

![Slack-канал, що показує згенерований дайджест OpenHands](assets/07-slackbot-message.png)

## Усунення несправностей

<!-- @os:windows -->
- **Порт Docker 8000 вже використовується:** призначте інший порт хоста, наприклад `docker run ... -p 8080:8000 ...`, і відкрийте `http://localhost:8080/canvas`.
- **`docker pull` завершується з помилкою облікових даних** (наприклад, "A specified logon session does not exist"): виконайте pull з інтерактивної сесії Windows або заздалегідь завантажте образ. Образ є публічним, тому `docker login` не потрібен.
- **Інтерфейс завантажується, але бекенд нездоровий:** під час першого запуску в контейнері формується середовище Agent Server. Зачекайте хвилину та оновіть сторінку, потім перевірте прогрес у `docker logs <container>`.
- **Agent Canvas не може підключитися до Lemonade з контейнера:** встановіть **Base URL** для LLM на `http://host.docker.internal:13305/api/v1` (не `127.0.0.1`) і переконайтеся, що Lemonade запущено на хості Windows.
<!-- @os:end -->

- **Lemonade не працює:** перезапустіть його за допомогою команди `lemonade run "${LEMONADE_MODEL}"` з кроку 1, потім повторно виконайте перевірку стану.
- **`npm install -g` завершується з помилкою доступу:** у Linux або WSL налаштуйте глобальний каталог npm, що належить користувачу, додайте його до файлу запуску вашої оболонки, потім знову встановіть Agent Canvas:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

Якщо ви використовуєте `zsh`, додайте той самий рядок `export PATH=...` до `~/.zshrc` замість `~/.bashrc`.
- **Agent Canvas відхиляє налаштування LLM після встановлення `custom_tokenizer`:** встановіть `transformers` у середовищі Python Agent Server, за потреби перезапустіть Agent Canvas і повторіть спробу збереження налаштувань LLM. OpenHands потребує Transformers для завантаження шаблону чату токенізатора, коли встановлено `custom_tokenizer`.
- **Agent Canvas не може підключитися до Lemonade:** перевірте `curl -fsS "${LEMONADE_BASE_URL}/health"` і переконайтеся, що базова URL-адреса, введена у формі LLM при першому використанні або в **Settings > LLM**, відповідає запущеному локальному кінцевому точці або HTTPS-тунелю.
- **Налаштування LLM не збереглися:** переконайтеся, що ви натиснули **Next** після введення значень. Відкрийте знову **Settings > LLM**, щоб переконатися, що значення збереглися.
- **GitHub MCP не бачить приватні репозиторії:** переконайтеся, що GitHub-токен має доступ на читання до цільового репозиторію та що кнопка **Test** MCP у **Customize** показує інструменти GitHub.
- **Slack може читати канали, але не може публікувати:** запросіть Slack-додаток у цільовий канал і переконайтеся, що бот має право `chat:write`.
- **Автоматизація показує забагато Slack-каналів:** використовуйте ідентифікатор Slack-каналу та встановіть `SLACK_CHANNEL_IDS` на сервері Slack MCP у **Customize**.
- **Запуск автоматизації завершується невдачею або перевищує контекст:** переконайтеся, що Lemonade було запущено з `ctx_size=65536`, переконайтеся, що для LLM OpenHands встановлено `custom_tokenizer`, і використовуйте конкретний репозиторій з результатами GitHub, обмеженими 3-5 елементами. Якщо ваша збірка Agent Canvas надає налаштування condenser, встановіть максимальну кількість токенів condenser нижче вікна контексту Lemonade.

## Наступні кроки

- Додайте щотижневий дайджест лише для релізів.
- Додайте автоматизацію, що запускається за подіями GitHub, для швидших сповіщень про PR або push.
- Направте той самий дайджест у Notion, Linear або інший інструмент на базі MCP.

## Ресурси

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Документація Lemonade Server](https://lemonade-server.ai/docs)
- [Репозиторій розширень OpenHands](https://github.com/OpenHands/extensions)
- [Сервери Model Context Protocol](https://github.com/modelcontextprotocol/servers)
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