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

[OpenHands](https://github.com/All-Hands-AI/OpenHands) — це AI-агент для розробки програмного забезпечення, який може писати код, виконувати команди, переглядати вебсторінки та редагувати файли в реальному робочому просторі. Замість того щоб копіювати пропозиції з вікна чату, ви вказуєте агенту на папку проєкту й дозволяєте йому виконати роботу: реалізувати функцію, виправити помилку, написати тести або пояснити кодову базу.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) — це рекомендований інтерфейс браузера для запуску OpenHands. Одна команда `agent-canvas` запускає сервер агента, бекенд автоматизації та вебфронтенд разом, тож ви можете вести розмову з агентом просто у браузері.

Щоб усе залишалося на вашій системі AMD, агент спілкується з локальною моделлю, яку обслуговує Lemonade Server. Lemonade надає доступ до цієї моделі через API, сумісний з OpenAI, тому Agent Canvas може налаштувати її так само, як і будь-яку іншу кінцеву точку у стилі OpenAI, тоді як модель, ваш код і контекст розмови залишаються на вашому комп'ютері.

У цьому посібнику ви запустите локальну модель, запустите Agent Canvas, налаштуєте його на цю модель і виконаєте своє перше завдання з написання коду в реальній папці проєкту.

## Чого ви навчитеся

- Як запустити Lemonade Server і переконатися, що локальна модель відповідає на запити чату
- Як встановити та запустити Agent Canvas з пакета npm
- Як налаштувати Agent Canvas для використання локальної моделі Lemonade як LLM
- Як розпочати розмову OpenHands і спостерігати, як агент редагує файли та виконує команди в робочому просторі
- Як переглянути зміни, внесені агентом, і скеровувати його наступними повідомленнями

## Основні концепції

| Концепція | Що це таке | Де вона застосовується в цьому посібнику |
| --- | --- | --- |
| Lemonade Server | Локальна платформа обслуговування LLM, створена для апаратного забезпечення AMD, яка надає API, сумісний з OpenAI. Ваші дані ніколи не залишають ваш комп'ютер. | Запускає модель, яка живить агента. |
| OpenHands | AI-агент для розробки програмного забезпечення, який читає й редагує файли, виконує команди оболонки та переглядає вебсторінки в робочому просторі. | Агент, яким ви керуєте з чату. |
| Agent Canvas | Інтерфейс браузера та бекенд, який запускає розмови OpenHands і показує виклики інструментів та зміни файлів. | Запускає весь стек і розміщує вашу розмову. |
| Робочий простір | Папка проєкту, яку агенту дозволено читати й змінювати. | Ціль редагувань і команд агента. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Робочі процеси агента для написання коду виграють від більшої моделі та вікна контексту. Використовуйте щонайменше 32 ГБ системної пам'яті, а для більших моделей GGUF надавайте перевагу 64 ГБ і більше.
<!-- @device:end -->

## Налаштування конфігурації пам'яті

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Перевірка оновлень програмного забезпечення

<!-- @require:software-update -->
<!-- @device:end -->

## Передумови


<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- @os:end -->

Вам потрібні:

- Встановлений Lemonade Server, здатний обслуговувати наведену нижче модель.

<!-- @os:linux -->
- Node.js 22.12 або новіша версія та `npm` (використовується CLI `agent-canvas`).
- `uv`, менеджер пакетів Python, який Agent Canvas використовує для керування середовищем сервера агента. Якщо у вашій системі його ще немає, встановіть його з [посібника зі встановлення uv](https://docs.astral.sh/uv/getting-started/installation/) перед запуском Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop для Windows](https://docs.docker.com/desktop/setup/install/windows-install/), встановлений і запущений. У Windows стек Agent Canvas запускається з опублікованого образу Docker, який містить у собі Node.js, `uv` та пакет `@openhands/agent-canvas`, тож встановлювати їх на хості не потрібно.
<!-- @os:end -->

- Папка проєкту для роботи. Це може бути будь-який локальний git-репозиторій або каталог з кодом, над яким ви хочете, щоб працював агент.

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

> **Виберіть модель, яка відповідає вашому апаратному забезпеченню.** `Qwen3.6-35B-A3B-GGUF` (~20 ГБ) — потужна модель для написання коду, але потребує великого пулу пам'яті. Якщо ваш пристрій має обмежену пам'ять або обсяг відеопам'яті GPU, натомість виберіть меншу модель GGUF з бібліотеки моделей Lemonade і використовуйте цей ідентифікатор моделі протягом усього посібника.

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

Якщо у відповідь повертається масив `choices`, Lemonade готовий для Agent Canvas.

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
Встановіть опубліковану пакет Agent Canvas глобально:

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

Потім запустіть повний стек з терміналу:

```bash
agent-canvas
```

За замовчуванням Agent Canvas запускається за адресою `http://localhost:8000`. Відкрийте цю URL-адресу в
браузері. Порт не має особливого значення — якщо 8000 вже використовується, вкажіть будь-який
вільний порт за допомогою `--port` (або `-p`) під час запуску Agent Canvas:

```bash
agent-canvas --port 3000
```

Потім відкрийте `http://localhost:3000` замість цього. Стандартний локальний бекенд має відображатися
як справний на головному екрані.

Команда `agent-canvas` запускає сервер агента, автоматизаційний бекенд і
веб-фронтенд разом. Вам потрібна лише ця одна команда, щоб запускати OpenHands
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
У Windows запустіть опубліковане образ контейнера Agent Canvas за допомогою Docker Desktop.
Образ включає сервер агента, автоматизаційний бекенд і веб-фронтенд, тому вам
не потрібно встановлювати Node.js, `uv` чи CLI на хості.

Спочатку створіть папки конфігурації та робочого простору, які монтуватиме контейнер:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Завантажте опубліковане зображення (воно публічне, тому вхід не потрібен):

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
використовується, зіставте інший порт хоста, наприклад `-p 8080:8000`, і відкрийте
`http://localhost:8080/canvas` замість цього.

> **Примітка:** Перший запуск ініціалізує сервер агента всередині контейнера,
> тому може пройти хвилина або дві, перш ніж бекенд повідомить, що він справний.

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

Під час першого запуску Agent Canvas відкриває процес адаптації. У цьому процесі:

1. Залиште **OpenHands** вибраним як агент і натисніть **Next**.
2. На екрані **Set up your LLM** виберіть **Advanced**.
3. Залиште **Authentication** встановленим на **API key**.
4. Встановіть **Custom Model** на `openai/Qwen3.6-35B-A3B-GGUF`.
5. Встановіть **Base URL** на `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > На Windows стек працює в контейнері, який не може підключитися до хоста за адресою
   > `127.0.0.1`. Замість цього використовуйте `http://host.docker.internal:13305/api/v1`, щоб
   > контейнеризований агент міг підключитися до Lemonade, що працює на хості Windows.
   <!-- @os:end -->
6. У поле **API Key** введіть будь-який непорожній заповнювач, наприклад `lemonade-local`.
   Lemonade не вимагає справжнього ключа, але клієнту OpenHands потрібне значення
   для надсилання.
7. Натисніть **Next**.

Заповнені розширені налаштування мають виглядати так. Поле API key
приховане інтерфейсом.

![Розширені налаштування LLM Agent Canvas при першому використанні з моделлю Lemonade та локальною базовою URL-адресою](assets/01-llm-advanced-settings.png)

Agent Canvas зберігає ці значення як профіль LLM. Якщо ваша версія просить вас
назвати цей профіль, використовуйте назву без пробілів, наприклад `lemonade-local`. Якщо ви пізніше
зміните моделі, відкрийте **Settings > LLM** і оновіть ті самі розширені поля. Ви
можете перемикати збережені профілі з поля введення чату за допомогою команди `/model`.

## 5. Відкриття робочого простору

Агент може читати та змінювати лише файли всередині обраного вами робочого простору. Перед
початком завдання вкажіть Agent Canvas на папку вашого проєкту:

1. На головному екрані виберіть **Open Workspace**.
2. Виберіть папку, що містить ваш проєкт (наприклад, git-репозиторій,
   з яким має працювати агент).
3. Розпочніть нову розмову в цьому робочому просторі.

Усе, що робить агент — читання файлів, виконання команд, редагування коду — обмежене
цим робочим простором.

![Головний екран Agent Canvas після адаптації](assets/02-agent-canvas-home.png)

## 6. Виконання вашого першого завдання з програмування

Коли робочий простір відкрито, а локальну LLM обрано, введіть конкретне завдання в
чат. Хорошим першим завданням є невелике та таке, що піддається перевірці, наприклад:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Спостерігайте за хронологією розмови. OpenHands буде:

- Читати робочий простір, щоб зрозуміти його структуру.
- Створювати `hello.py` з запитаною функцією та блоком тесту.
- За бажанням запускати `python3 hello.py` для перевірки результату.
- Звітувати про виконані дії та будь-який вивід команд у чаті.

Ви маєте побачити, як у робочому просторі з'являється новий файл, а фінальне повідомлення
агента має описувати внесену зміну. Це той момент результату: агент
написав і виконав реальний код у вашій папці проєкту.

## 7. Перевірка та керування агентом

Після того як агент завершує крок, перегляньте його роботу, перш ніж приймати наступний:

- **Зміни файлів**: використовуйте браузер файлів робочого простору або перегляд змін
  агента, щоб побачити точно, що було додано, змінено чи видалено.
- **Вивід команд**: розгорніть будь-яку команду, яку виконав агент, щоб побачити stdout, stderr
  та код завершення.
- **Подальші дії**: якщо результат не відповідає вашим очікуванням, відповідайте в тій самій
  розмові з виправленням. Агент зберігає попередній контекст і
  ітерує над тими самими файлами.

Наприклад, якщо тест не вивів очікуване привітання, відповідайте:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

Агент повторно прочитає файл, виконає команду, діагностує проблему та знову відредагує
файл — усе в тій самій розмові.
## Усунення несправностей

<!-- @os:linux -->
- **`agent-canvas` немає в PATH:** перевстановіть за допомогою
  `npm install -g @openhands/agent-canvas` і переконайтеся, що каталог глобальних
  бінарних файлів npm вказано в PATH, перш ніж `agent-canvas` можна буде
  запустити з нового термінала.
- **`npm install -g` завершується помилкою прав доступу:** налаштуйте
  глобальний каталог npm, що належить користувачу, потім знову відкрийте
  термінал і повторно встановіть Agent Canvas.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **Відсутній `uv`:** встановіть його за
  [посібником з встановлення uv](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas використовує `uv` для керування Python-середовищем сервера агента.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` або `docker run` не може підключитися:** переконайтеся, що
  Docker Desktop запущено (його значок-кит у системному треї) і що рушій
  завершив запуск. Команда `docker version` має вивести розділи Client і Server.
- **Контейнер запускається, але бекенд ніколи не стає справним:** перший
  запуск ініціалізує сервер агента всередині контейнера; зачекайте хвилину-дві,
  потім перевірте `docker logs <container>` на наявність помилок.
- **Контейнер не може підключитися до Lemonade:** контейнер звертається до
  хоста через `host.docker.internal`. Переконайтеся, що Lemonade обслуговує
  запити на хості Windows за допомогою `lemonade status`, і використовуйте
  `http://host.docker.internal:13305/api/v1` як базову URL-адресу під час
  налаштування LLM.
<!-- @os:end -->

- **Інтерфейс завантажується, але бекенд позначено як несправний:** зачекайте
  хвилину-дві, поки сервер агента завершить запуск, потім оновіть сторінку.
  Якщо стан не змінюється, перезапустіть стек і перевірте журнали на наявність
  помилок.
- **Запити чату Lemonade завершуються помилкою підключення:** переконайтеся, що
  команда `curl -fsS "http://127.0.0.1:13305/api/v1/health"` виконується успішно
  і що Lemonade усе ще обслуговує модель, скориставшись `lemonade status`.
- **Агент видає помилку про довжину контексту або ліміт токенів:** почніть нову
  розмову, щоб агент не переносив надто велику історію. Якщо це повторюється,
  перезапустіть Lemonade з більшим значенням `ctx_size`, ніж стандартне 65536
  (наприклад, `ctx_size=131072`), якщо дозволяє обсяг пам'яті.
- **Агент видає низькоякісні або неповні правки:** перемкніться на більшу
  модель у Lemonade або дайте агенту менше й конкретніше завдання і дочекайтеся
  його завершення, перш ніж просити наступну зміну.

## Наступні кроки

- Спробуйте виконати більше завдання в тому самому робочому просторі,
  наприклад додати файл модульного тесту або виправити відому помилку, і
  перегляньте діф агента, перш ніж зберігати зміну.
- Підключіть сервер MCP, наприклад GitHub або Slack, у розділі **Customize**,
  щоб агент міг читати задачі або публікувати оновлення під час роботи.
- Збережіть кілька профілів LLM (швидку невелику модель і потужнішу велику
  модель) і перемикайтеся між ними за допомогою `/model` під час розмови.
- Перейдіть до [автоматизацій OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview),
  щоб перетворити повторювані цикли розробки на заплановані або керовані
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