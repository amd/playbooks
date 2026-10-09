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

[OpenHands](https://github.com/All-Hands-AI/OpenHands) — це ШІ-агент для
розробки програмного забезпечення, який може писати код, виконувати команди,
переглядати веб-сторінки та редагувати файли у реальному робочому просторі.
Замість того, щоб копіювати пропозиції з вікна чату, ви вказуєте агенту на
папку проєкту й дозволяєте йому виконати роботу: реалізувати функцію,
виправити помилку, написати тести або пояснити кодову базу.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) — це рекомендований
браузерний інтерфейс для запуску OpenHands. Єдина команда `agent-canvas`
запускає сервер агента, бекенд автоматизації та веб-фронтенд разом, тож ви
можете вести діалог з агентом прямо з браузера.

Щоб усе залишалося на вашій системі AMD, агент спілкується з локальною
моделлю, яку обслуговує Lemonade Server. Lemonade надає доступ до цієї моделі
через API, сумісний з OpenAI, тож Agent Canvas може налаштувати її так само,
як і будь-яку іншу кінцеву точку у стилі OpenAI, при цьому модель, ваш код і
контекст розмови залишаються на вашому комп’ютері.

У цьому посібнику ви запустите локальну модель, запустите Agent Canvas,
налаштуєте її на цю модель і виконаєте своє перше завдання з кодування для
реальної папки проєкту.

## Що ви дізнаєтеся

- Як запустити Lemonade Server і переконатися, що локальна модель відповідає
  на запити чату
- Як встановити та запустити Agent Canvas з пакета npm
- Як налаштувати Agent Canvas на використання локальної моделі Lemonade як LLM
- Як розпочати розмову OpenHands і спостерігати, як агент редагує файли та
  виконує команди в робочому просторі
- Як переглянути, що саме змінив агент, і скеровувати його подальшими
  повідомленнями

## Основні поняття

| Поняття | Що це таке | Де застосовується в цьому посібнику |
| --- | --- | --- |
| Lemonade Server | Платформа для локального обслуговування LLM, створена для апаратного забезпечення AMD, яка надає API, сумісний з OpenAI. Ваші дані ніколи не покидають ваш комп’ютер. | Запускає модель, яка живить агента. |
| OpenHands | ШІ-агент для розробки ПЗ, який читає й редагує файли, виконує команди оболонки та переглядає веб-сторінки в робочому просторі. | Агент, яким ви керуєте через чат. |
| Agent Canvas | Браузерний інтерфейс і бекенд, що запускає розмови OpenHands та показує виклики інструментів і зміни файлів. | Запускає весь стек і приймає вашу розмову. |
| Робочий простір | Папка проєкту, яку агенту дозволено читати та змінювати. | Ціль редагувань і команд агента. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Робочі процеси агента кодування виграють від більшої моделі та більшого
> вікна контексту. Використовуйте щонайменше 32 ГБ системної пам’яті і
> віддавайте перевагу 64 ГБ або більше для великих GGUF-моделей.
<!-- @device:end -->

## Налаштування конфігурації пам’яті

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Перевірка оновлень програмного забезпечення

<!-- @require:software-update -->
<!-- @device:end -->

## Передумови


<!-- @os:linux -->
<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-6-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so the host needs only Docker and the model.
     lemonade-chat-windows asserts the model is already downloaded. -->
<!-- @prereq:docker,lemonade-models-qwen3-6-35b-a3b -->
<!-- @os:end -->

Вам потрібні:

- Встановлений Lemonade Server, здатний обслуговувати наведену нижче модель.

<!-- @os:linux -->
- Node.js 22.12 або новішої версії та `npm` (використовуються CLI
  `agent-canvas`).
- `uv` — менеджер пакетів Python, який Agent Canvas використовує для
  керування середовищем сервера агента. Якщо у вашій системі його ще немає,
  встановіть його з
  [посібника з встановлення uv](https://docs.astral.sh/uv/getting-started/installation/)
  перед запуском Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  встановлений і запущений. У Windows стек Agent Canvas працює з
  опублікованого образу Docker, який включає Node.js, `uv` та пакет
  `@openhands/agent-canvas`, тож встановлювати їх на хост не потрібно.
<!-- @os:end -->

- Папка проєкту для роботи. Це може бути будь-який локальний git-репозиторій
  або каталог з кодом, над яким ви хочете, щоб працював агент.

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

> **Виберіть модель, яка відповідає вашому апаратному забезпеченню.**
> `Qwen3.6-35B-A3B-GGUF` (~20 ГБ) — потужна модель для кодування, але потребує
> великого пулу пам’яті. Якщо на вашому пристрої обмежена пам’ять або обсяг
> VRAM GPU, оберіть меншу GGUF-модель з бібліотеки моделей Lemonade і
> використовуйте цей ідентифікатор моделі протягом усього посібника.

> **Примітка:** перший виклик `lemonade run` завантажує модель, якщо її ще
> немає, що може зайняти певний час залежно від розміру моделі та швидкості
> вашого з’єднання.

Lemonade надає API, сумісний з OpenAI, за адресою:

```text
http://127.0.0.1:13305/api/v1
```

## 2. Перевірка локальної моделі

Переконайтеся, що Lemonade може обслуговувати вибрану модель:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Потім надішліть невеликий запит до чату:

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

Якщо у відповідь повертається масив `choices`, Lemonade готовий для Agent
Canvas.

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

За замовчуванням Agent Canvas запускається за адресою `http://localhost:8000`. Відкрийте цю URL-адресу у
своєму браузері. Порт не є особливим — якщо порт 8000 вже використовується, вкажіть будь-який
вільний порт за допомогою `--port` (або `-p`) під час запуску Agent Canvas:

```bash
agent-canvas --port 3000
```

Потім відкрийте натомість `http://localhost:3000`. Типовий локальний бекенд має відображатися
як справний на головному екрані.

Команда `agent-canvas` запускає сервер агента, бекенд автоматизації та
веб-фронтенд разом. Вам потрібна лише ця одна команда, щоб запустити OpenHands
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
У Windows запустіть опубліковаий образ контейнера Agent Canvas за допомогою Docker Desktop.
Образ містить Agent Server, бекенд автоматизації та веб-фронтенд, тож
встановлювати Node.js, `uv` або CLI на хості не потрібно.

Спочатку створіть теки конфігурації та робочого простору, які монтуватиме контейнер:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Завантажте опублікований образ (він публічний, тож вхід у систему не потрібен):

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

Відкрийте `http://localhost:8000/canvas` у своєму браузері. Якщо порт 8000 вже
використовується, призначте інший порт хоста, наприклад `-p 8080:8000`, і відкрийте натомість
`http://localhost:8080/canvas`.

> **Примітка:** Перший запуск ініціалізує Agent Server всередині контейнера,
> тому може знадобитися хвилина чи дві, перш ніж бекенд повідомить про справний стан.

Монтування `.openhands` зберігає ваш профіль LLM та налаштування між
перезапусками контейнера. Решта цього посібника налаштовує все через інтерфейс Agent
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
4. Встановіть для **Custom Model** значення `openai/Qwen3.6-35B-A3B-GGUF`.
5. Встановіть для **Base URL** значення `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > У Windows стек запускається в контейнері, який не може звернутися до хоста за адресою
   > `127.0.0.1`. Натомість використовуйте `http://host.docker.internal:13305/api/v1`, щоб
   > контейнеризований агент міг звернутися до Lemonade, що працює на хості Windows.
   <!-- @os:end -->
6. У полі **API Key** введіть будь-який непорожній заповнювач, наприклад `lemonade-local`.
   Lemonade не вимагає реального ключа, але клієнту OpenHands потрібне якесь значення
   для надсилання.
7. Натисніть **Next**.

Заповнені розширені налаштування мають виглядати так. Поле з ключем API
приховане інтерфейсом.

![Розширені налаштування LLM Agent Canvas під час першого використання з моделлю Lemonade та локальною базовою URL-адресою](assets/01-llm-advanced-settings.png)

Agent Canvas зберігає ці значення як профіль LLM. Якщо ваша версія просить вас
назвати цей профіль, використовуйте ім'я без пробілів, наприклад `lemonade-local`. Якщо ви
пізніше зміните моделі, відкрийте **Settings > LLM** і оновіть ті самі розширені поля. Ви
можете перемикати збережені профілі з поля введення чату за допомогою команди `/model`.

## 5. Відкриття робочого простору

Агент може читати та змінювати файли лише в межах вибраного вами робочого простору. Перш ніж
розпочати завдання, вкажіть Agent Canvas на вашу теку проєкту:

1. На головному екрані виберіть **Open Workspace**.
2. Виберіть теку, що містить ваш проєкт (наприклад, git-репозиторій,
   над яким ви хочете, щоб працював агент).
3. Розпочніть нову розмову в цьому робочому просторі.

Усе, що робить агент — читання файлів, виконання команд, редагування коду — обмежено
цим робочим простором.

![Головний екран Agent Canvas після початкового налаштування](assets/02-agent-canvas-home.png)

## 6. Виконання вашого першого завдання з кодування

Коли робочий простір відкрито, а локальну LLM вибрано, введіть конкретне завдання в
чат. Хороше перше завдання — невелике і таке, що легко перевірити, наприклад:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Спостерігайте за хронологією розмови. OpenHands:

- Прочитає робочий простір, щоб зрозуміти його структуру.
- Створить `hello.py` із запитаною функцією та блоком тестування.
- За потреби виконає `python3 hello.py`, щоб перевірити результат.
- Повідомить, що він зробив, та будь-який вивід команди в чаті.

Ви повинні побачити, як у робочому просторі з'явиться новий файл, а в останньому повідомленні агента
має бути описана внесена зміна. Це і є ключовий момент: агент
написав та виконав реальний код у вашій теці проєкту.

## 7. Перегляд результатів роботи агента та керування ним

Після того, як агент завершить крок, перегляньте його роботу, перш ніж прийняти наступний крок:

- **Зміни файлів**: скористайтеся переглядачем файлів робочого простору або переглядом різниць (diff)
  агента, щоб точно побачити, що було додано, змінено або видалено.
- **Вивід команд**: розгорніть будь-яку команду, яку виконав агент, щоб побачити stdout, stderr
  та код виходу.
- **Подальші дії**: якщо результат не такий, яким ви його очікували, відповідайте в тій самій
  розмові з виправленням. Агент зберігає попередній контекст та
  продовжує роботу з тими самими файлами.

Наприклад, якщо тест не вивів очікуване привітання, відповідайте:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Агент повторно прочитає файл, виконає команду, діагностує проблему та знову відредагує
файл — усе в тій самій розмові.
## Усунення несправностей

<!-- @os:linux -->
- **`agent-canvas` відсутній у PATH:** перевстановіть за допомогою
  `npm install -g @openhands/agent-canvas` і переконайтеся, що каталог глобальних бінарних файлів npm
  додано до PATH, перш ніж `agent-canvas` можна буде запустити з нового
  термінала.
- **`npm install -g` завершується помилкою доступу:** налаштуйте глобальний каталог npm, що належить
  поточному користувачу, потім знову відкрийте термінал і встановіть Agent Canvas ще раз.

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
- **`docker pull` або `docker run` не вдається підключитися:** переконайтеся, що Docker Desktop
  запущено (його значок у вигляді кита відображається в треї) і що рушій уже
  завершив запуск. Команда `docker version` повинна вивести розділи Client і Server.
- **Контейнер запускається, але бекенд ніколи не стає працездатним:** під час першого
  запуску в контейнері ініціалізується Agent Server; зачекайте хвилину чи
  дві, потім перевірте `docker logs <container>` на наявність помилок.
- **Контейнер не може з'єднатися з Lemonade:** контейнер звертається до хоста через
  `host.docker.internal`. Переконайтеся, що Lemonade обслуговує запити на хості Windows, за допомогою
  `lemonade status`, і використовуйте `http://host.docker.internal:13305/api/v1` як
  Base URL під час налаштування LLM.
<!-- @os:end -->

- **Інтерфейс завантажується, але бекенд позначено як непрацездатний:** зачекайте хвилину чи дві,
  поки сервер агента завершить запуск, потім оновіть сторінку. Якщо він залишається непрацездатним, перезапустіть
  стек і перевірте журнали на наявність помилок.
- **Запити чату Lemonade завершуються помилкою з'єднання:** переконайтеся, що
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` виконується успішно і що
  Lemonade все ще обслуговує модель, за допомогою `lemonade status`.
- **Агент видає помилку про довжину контексту або ліміт токенів:** почніть
  нову розмову, щоб агент не переносив надто велику історію. Якщо це
  продовжує траплятися, перезапустіть Lemonade з більшим значенням `ctx_size`, ніж стандартне
  65536 (наприклад, `ctx_size=131072`), якщо дозволяє пам'ять.
- **Агент створює правки низької якості або неповні:** переключіться на більшу
  модель у Lemonade або дайте агенту менше й конкретніше завдання та дочекайтеся його
  завершення, перш ніж запитувати наступну зміну.

## Подальші кроки

- Спробуйте складніше завдання в тому самому робочому просторі, наприклад додайте файл модульного тесту або
  виправте відому помилку, і перегляньте diff агента, перш ніж зберегти зміну.
- Підключіть MCP-сервер, наприклад GitHub або Slack, у розділі **Customize**, щоб
  агент міг читати задачі (issues) або публікувати оновлення під час роботи.
- Збережіть кілька профілів LLM (швидку малу модель і потужнішу велику модель) і
  перемикайтеся між ними командою `/model` просто під час розмови.
- Перейдіть до [автоматизацій OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview), щоб
  перетворити повторювані цикли розробки на заплановані або запущені подіями прогони агента.

## Ресурси

- [Документація OpenHands](https://docs.openhands.dev/)
- [Огляд Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Налаштування Agent Canvas](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [Профілі LLM та налаштування моделей](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
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