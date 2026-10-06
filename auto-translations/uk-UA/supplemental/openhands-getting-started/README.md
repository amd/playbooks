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
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Огляд

[OpenHands](https://github.com/All-Hands-AI/OpenHands) — це AI-агент для написання програмного забезпечення, який може писати код, виконувати команди, переглядати веб-сторінки та редагувати файли в реальному робочому середовищі. Замість того, щоб копіювати пропозиції з вікна чату, ви спрямовуєте агента на папку проєкту та дозволяєте йому виконувати роботу: реалізувати функцію, виправити помилку, написати тести або пояснити кодову базу.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) — це рекомендований інтерфейс браузера для запуску OpenHands. Єдина команда `agent-canvas` запускає сервер агента, бекенд автоматизації та веб-фронтенд разом, тож ви можете вести розмову з агентом прямо у браузері.

Щоб усе залишалося на вашій системі AMD, агент спілкується з локальною моделлю, яку обслуговує Lemonade Server. Lemonade надає доступ до цієї моделі через API, сумісний з OpenAI, тож Agent Canvas може налаштувати її так само, як будь-яку іншу кінцеву точку у стилі OpenAI, тоді як модель, ваш код і контекст розмови залишаються на вашій машині.

У цьому посібнику ви запустите локальну модель, запустите Agent Canvas, спрямуєте його на цю модель і виконаєте своє перше завдання з кодування над реальною папкою проєкту.

## Що ви дізнаєтеся

- Як запустити Lemonade Server і переконатися, що локальна модель відповідає на запити чату
- Як встановити та запустити Agent Canvas з npm-пакета
- Як налаштувати Agent Canvas для використання локальної моделі Lemonade як LLM
- Як розпочати розмову OpenHands і спостерігати, як агент редагує файли та виконує команди в робочому середовищі
- Як переглянути, що змінив агент, і скеровувати його подальшими повідомленнями

## Основні поняття

| Поняття | Що це таке | Де це застосовується в цьому посібнику |
| --- | --- | --- |
| Lemonade Server | Локальна платформа для обслуговування LLM, створена для апаратного забезпечення AMD, яка надає API, сумісний з OpenAI. Ваші дані ніколи не покидають вашу машину. | Запускає модель, яка живить агента. |
| OpenHands | AI-агент для програмного забезпечення, який читає та редагує файли, виконує команди оболонки та переглядає веб у робочому середовищі. | Агент, яким ви керуєте з чату. |
| Agent Canvas | Інтерфейс браузера та бекенд, який запускає розмови OpenHands і показує виклики інструментів та зміни файлів. | Запускає стек і розміщує вашу розмову. |
| Робоче середовище (Workspace) | Папка проєкту, яку агенту дозволено читати та змінювати. | Ціль редагувань і команд агента. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Робочі процеси агента для кодування виграють від більшої моделі та більшого контекстного вікна. Використовуйте щонайменше 32 ГБ системної пам'яті, а для більших моделей GGUF надавайте перевагу 64 ГБ або більше.
<!-- @device:end -->

## Налаштування конфігурації пам'яті

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Перевірка оновлень програмного забезпечення

<!-- @require:software-update -->
<!-- @device:end -->

## Передумови


<!-- @os:linux -->
<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here.
     lemonade-chat-windows asserts the model is already downloaded. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

Вам потрібно:

- Lemonade Server встановлено та готовий обслуговувати наведену нижче модель.

<!-- @os:linux -->
- Node.js версії 22.12 або новіше та `npm` (використовуються CLI `agent-canvas`).
- `uv` — менеджер пакетів Python, який Agent Canvas використовує для керування середовищем сервера агента. Якщо у вашій системі його ще немає, встановіть його за [посібником зі встановлення uv](https://docs.astral.sh/uv/getting-started/installation/) перед запуском Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  встановлено та запущено. У Windows стек Agent Canvas запускається з опублікованого образу Docker, який включає Node.js, `uv` та пакет
  `@openhands/agent-canvas`, тож вам не потрібно встановлювати їх на хості.
<!-- @os:end -->

- Папка проєкту для роботи. Це може бути будь-який локальний git-репозиторій або каталог з кодом, над яким ви хочете, щоб агент працював.

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

Запустіть модель з CLI Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Виберіть модель, яка відповідає вашому обладнанню.** `Qwen3.6-35B-A3B-GGUF` (~20 ГБ) — потужна модель для кодування, але потребує великого пулу пам'яті. Якщо ваш пристрій має обмежену пам'ять або обсяг відеопам'яті GPU, виберіть меншу модель GGUF з бібліотеки моделей Lemonade і використовуйте цей ідентифікатор моделі протягом усього цього посібника.

> **Примітка:** Перший запуск `lemonade run` завантажує модель, якщо її ще немає, що може зайняти певний час залежно від розміру моделі та вашого з'єднання.

Lemonade надає API, сумісний з OpenAI, за адресою:

```text
http://127.0.0.1:13305/api/v1
```

## 2. Перевірка локальної моделі

Переконайтеся, що Lemonade може обслуговувати вибрану модель:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Потім надішліть невеликий запит чату:

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

Якщо це повертає масив `choices`, Lemonade готовий для Agent Canvas.

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
## 3. Встановлення та запуск Agent Canvas

<!-- @os:linux -->
Встановіть опубліковаий пакет Agent Canvas глобально:

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

Потім запустіть повний стек із термінала:

```bash
agent-canvas
```

За замовчуванням Agent Canvas запускається на `http://localhost:8000`. Відкрийте
цю URL-адресу у браузері. Порт не є особливим — якщо 8000 вже зайнятий, передайте
будь-який вільний порт за допомогою `--port` (або `-p`) під час запуску Agent Canvas:

```bash
agent-canvas --port 3000
```

Потім відкрийте `http://localhost:3000` замість цього. Типовий локальний бекенд має
відображатися як справний на домашньому екрані.

Команда `agent-canvas` запускає сервер агента, бекенд автоматизації та
веб-фронтенд разом. Вам потрібна лише ця одна команда для запуску OpenHands
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
У Windows запустіть опублікований образ контейнера Agent Canvas за допомогою Docker Desktop.
Образ містить Agent Server, бекенд автоматизації та веб-фронтенд, тому
вам не потрібно встановлювати Node.js, `uv` чи CLI на хості.

Спочатку створіть папки конфігурації та робочого простору, які монтуватиме контейнер:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Завантажте опублікований образ (він публічний, тож авторизація не потрібна):

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

Відкрийте `http://localhost:8000/canvas` у браузері. Якщо порт 8000 вже
зайнятий, призначте інший порт хоста, наприклад `-p 8080:8000`, і відкрийте
`http://localhost:8080/canvas` замість цього.

> **Примітка:** Під час першого запуску відбувається ініціалізація Agent Server
> усередині контейнера, тому може знадобитися хвилина-дві, перш ніж бекенд
> повідомить про справний стан.

Монтування `.openhands` зберігає ваш профіль LLM і налаштування між перезапусками
контейнера. Решта цього посібника налаштовує все через інтерфейс Agent
Canvas у вашому браузері.

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

## 4. Налаштування локальної LLM

Під час першого запуску Agent Canvas відкриває процес початкового налаштування. У цьому процесі:

1. Залиште **OpenHands** вибраним як агент і натисніть **Next**.
2. На екрані **Set up your LLM** виберіть **Advanced**.
3. Залиште для **Authentication** значення **API key**.
4. Встановіть **Custom Model** на `openai/Qwen3.6-35B-A3B-GGUF`.
5. Встановіть **Base URL** на `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > У Windows стек працює в контейнері, який не може звернутися до хоста за адресою
   > `127.0.0.1`. Натомість використовуйте `http://host.docker.internal:13305/api/v1`, щоб
   > контейнеризований агент міг звернутися до Lemonade, що працює на хості Windows.
   <!-- @os:end -->
6. У полі **API Key** введіть будь-яке непорожнє значення-заповнювач, наприклад `lemonade-local`.
   Lemonade не вимагає справжнього ключа, але клієнту OpenHands потрібне значення
   для надсилання.
7. Натисніть **Next**.

Завершені розширені налаштування мають виглядати так. Поле API-ключа
приховане інтерфейсом.

![Розширені налаштування LLM Agent Canvas при першому використанні з моделлю Lemonade та локальною базовою URL-адресою](assets/01-llm-advanced-settings.png)

Agent Canvas зберігає ці значення як профіль LLM. Якщо ваша версія просить вас
дати цьому профілю назву, використовуйте назву без пробілів, наприклад `lemonade-local`. Якщо ви
пізніше зміните моделі, відкрийте **Settings > LLM** і оновіть ті самі розширені поля. Ви
можете перемикати збережені профілі з поля вводу чату за допомогою команди `/model`.

## 5. Відкриття робочого простору

Агент може читати та змінювати лише файли в робочому просторі, який ви виберете. Перш ніж
розпочати завдання, вкажіть Agent Canvas на папку вашого проєкту:

1. На домашньому екрані виберіть **Open Workspace**.
2. Виберіть папку, що містить ваш проєкт (наприклад, git-репозиторій,
   над яким ви хочете, щоб агент працював).
3. Почніть нову розмову в цьому робочому просторі.

Усе, що робить агент — читання файлів, виконання команд, редагування коду — обмежено
цим робочим простором.

![Домашній екран Agent Canvas після початкового налаштування](assets/02-agent-canvas-home.png)

## 6. Виконання вашого першого завдання з кодування

Коли робочий простір відкрито, а локальну LLM вибрано, введіть конкретне завдання в
чат. Хороше перше завдання є невеликим і перевірюваним, наприклад:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Спостерігайте за хронологією розмови. OpenHands буде:

- Читати робочий простір, щоб зрозуміти його структуру.
- Створювати `hello.py` з потрібною функцією та блоком тестування.
- За потреби виконувати `python3 hello.py` для перевірки виводу.
- Повідомляти про те, що було зроблено, і будь-який вивід команд у чаті.

Ви маєте побачити, як у робочому просторі з'являється новий файл, а в останньому
повідомленні агента описано внесену зміну. Це і є ключовий момент: агент
написав і виконав справжній код у вашій папці проєкту.

## 7. Перевірка та керування роботою агента

Після завершення агентом кроку перевірте його роботу, перш ніж прийняти наступний крок:

- **Зміни файлів**: використовуйте файловий браузер робочого простору або перегляд різниці агента, щоб
  побачити точно, що було додано, змінено або видалено.
- **Вивід команд**: розгорніть будь-яку команду, виконану агентом, щоб побачити stdout, stderr
  та код завершення.
- **Подальші дії**: якщо результат не відповідає вашим очікуванням, відповідайте в тій самій
  розмові з виправленням. Агент зберігає попередній контекст і
  продовжує роботу з тими самими файлами.

Наприклад, якщо тест не вивів очікуване привітання, відповідайте:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Агент повторно прочитає файл, виконає команду, визначить причину проблеми та знову
відредагує файл — усе в тій самій розмові.
## Усунення несправностей

<!-- @os:linux -->
- **`agent-canvas` відсутній у PATH:** перевстановіть за допомогою
  `npm install -g @openhands/agent-canvas` і переконайтеся, що каталог глобальних
  бінарних файлів npm додано до PATH, перш ніж `agent-canvas` можна буде
  запустити з нового термінала.
- **`npm install -g` завершується з помилкою прав доступу:** налаштуйте
  глобальний каталог npm, що належить користувачу, потім знову відкрийте термінал
  і встановіть Agent Canvas ще раз.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **Відсутній `uv`:** встановіть його за допомогою
  [посібника зі встановлення uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas використовує `uv` для керування Python-середовищем сервера агента.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` або `docker run` не вдається підключитися:** переконайтеся,
  що Docker Desktop запущено (його значок у вигляді кита розташований у системному
  треї) і що механізм завершив запуск. Команда `docker version` має вивести
  і розділ Client, і розділ Server.
- **Контейнер запускається, але бекенд ніколи не стає справним:** перший
  запуск ініціалізує Agent Server усередині контейнера; зачекайте хвилину-дві,
  потім перевірте `docker logs <container>` на наявність помилок.
- **Контейнер не може підключитися до Lemonade:** контейнер звертається до
  хоста через `host.docker.internal`. Переконайтеся, що Lemonade обслуговує
  запити на хості Windows за допомогою `lemonade status`, і використовуйте
  `http://host.docker.internal:13305/api/v1` як базову URL-адресу під час
  налаштування LLM.
<!-- @os:end -->

- **Інтерфейс завантажується, але бекенд показує стан несправності:** зачекайте
  хвилину-дві, поки сервер агента завершить запуск, потім оновіть сторінку.
  Якщо стан залишається несправним, перезапустіть стек і перевірте журнали на
  наявність помилок.
- **Запити чату Lemonade завершуються з помилкою підключення:** переконайтеся,
  що `curl -fsS "http://127.0.0.1:13305/api/v1/health"` виконується успішно і
  що Lemonade все ще обслуговує модель, перевіривши за допомогою
  `lemonade status`.
- **Агент видає помилку щодо довжини контексту або ліміту токенів:** почніть
  нову розмову, щоб агент не переносив надмірно велику історію. Якщо проблема
  повторюється, перезапустіть Lemonade з більшим значенням `ctx_size`, ніж
  типове 65536 (наприклад, `ctx_size=131072`), якщо дозволяє обсяг пам'яті.
- **Агент створює низькоякісні або неповні правки:** перейдіть на більшу модель
  у Lemonade або поставте агенту менше й конкретніше завдання та дочекайтеся
  його завершення, перш ніж запитувати наступну зміну.

## Наступні кроки

- Спробуйте більше завдання у тому ж робочому просторі, наприклад додайте файл
  модульного тесту або виправте відому помилку, і перегляньте diff агента, перш
  ніж зберегти зміну.
- Підключіть MCP-сервер, наприклад GitHub або Slack, у розділі **Customize**,
  щоб агент міг читати задачі або публікувати оновлення під час роботи.
- Збережіть кілька профілів LLM (швидку маленьку модель і потужнішу велику
  модель) та перемикайтеся між ними за допомогою `/model` під час розмови.
- Перейдіть до [автоматизацій OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview),
  щоб перетворити повторювані цикли розробки на заплановані або запущені за
  подіями запуски агента.

## Ресурси

- [Документація OpenHands](https://docs.openhands.dev/)
- [Огляд Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Налаштування Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [Профілі LLM та конфігурація моделей](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Документація Lemonade Server](https://lemonade-server.ai/docs)

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