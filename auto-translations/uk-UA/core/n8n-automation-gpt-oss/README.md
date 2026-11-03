<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинний переклад.** Цю сторінку було автоматично перекладено з англійської мови, і вона не була перевірена людиною. Вона може містити помилки, а певні інструкції, команди, завантаження, доступність продукту чи інший вміст можуть відрізнятися залежно від мови чи регіону. У разі будь-яких невідповідностей чи розбіжностей переважну силу має оригінальна англомовна версія playbook.
<!-- auto-translated-disclaimer:end -->

### Огляд

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Огляд

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Для цього посібника потрібно щонайменше **32 ГБ** оперативної пам'яті системи.
<!-- @device:end -->

n8n — це платформа автоматизації робочих процесів, яка дозволяє з'єднувати додатки та сервіси за допомогою візуального редактора на основі вузлів.

Цей посібник навчить вас налаштовувати сумаризатор фінансових новин на основі ШІ, який отримує останні бізнес-заголовки з RSS-стрічки новин і використовує локальну LLM, що працює на вашій системі, для створення підсумку, орієнтованого на інвесторів.

## Що ви дізнаєтеся

- Як встановити та запустити n8n
- Імпортування та налаштування готового робочого процесу
- Підключення до Lemonade за допомогою нативної інтеграції n8n
- Розуміння вузлів робочого процесу та потоку даних

## Що таке Lemonade?

[Lemonade](https://lemonade-server.ai) — це платформа для локального обслуговування LLM, створена для апаратного забезпечення AMD. Вона надає сумісний з OpenAI API, який повністю працює на вашому пристрої — ваші дані ніколи не залишають ваш пристрій.

У цьому посібнику ми використовуємо Lemonade для обслуговування локальної LLM, до якої підключається n8n для виконання завдань на основі ШІ.

n8n включає **нативний вузол Lemonade** (`Lemonade Chat Model`), який забезпечує повноцінну інтеграцію - не потрібне ручне налаштування. Це робить підключення вашої локальної LLM до автоматизованих робочих процесів простим.

<!-- @device:halo_box,halo,stx,krk -->
## Налаштування конфігурації пам'яті

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Перевірка оновлень програмного забезпечення

<!-- @require:software-update -->
<!-- @device:end -->

## Встановлення необхідного програмного забезпечення
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @require:lemonade,podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
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

<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->

## Встановлення n8n
<!-- @os:windows -->
Встановіть n8n глобально за допомогою npm.

> **Примітка**: Ви можете побачити деякі попередження npm. Це очікувано.

```bash
npm install -g n8n
```

<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **Порада**: Користувачам Windows може знадобитися змінити політику виконання PowerShell (наприклад,
> встановивши її на RemoteSigned або Unrestricted) перед запуском деяких команд PowerShell.
<!-- @os:end -->


<!-- @os:windows -->
> **Проблема з PATH**: Якщо `n8n --version` видає повідомлення про те, що команду не знайдено, переконайтеся, що каталог глобального bin npm знаходиться у користувацькому `PATH`. Звичайний шлях встановлення — `C:\Users\<username>\AppData\Roaming\npm`.
> Додайте це до користувацького шляху (Змінити системні змінні середовища > Змінні середовища > Змінити User Path) і перезавантажте термінал.

<!-- @os:end -->

<!-- @os:linux -->
Тепер ми будемо використовувати сервіс Podman для контейнеризації нашого встановлення n8n.

Будь ласка, завантажте наступне у вибраний вами каталог: [compose.yml](assets/compose.yml)

У цьому каталозі виконайте наступну команду:
```bash
podman compose up -d
```

Це має встановити n8n і записати дані у постійне сховище.

Запустіть n8n, ввівши `localhost:5678` в адресний рядок браузера.
<!-- @os:end -->

<!-- @os:windows -->
## Запуск n8n

Запустіть n8n з терміналу:

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

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

n8n start >/tmp/n8n-test.log 2>&1 &
p=$!

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
  exit 1
fi

echo "OK: n8n server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
n8n запускає локальний веб-сервер. Натисніть `'o'` або відкрийте браузер за адресою `http://localhost:5678`, щоб отримати доступ до редактора.
<!-- @os:end -->


> **Порада**: Не закривайте вікно терміналу під час використання n8n. Закриття може зупинити сервер.

## Запуск Lemonade

Lemonade — це локальний сервер, який запускатиме модель і підключатиметься до n8n.

<!-- @os:linux -->
Відкрийте графічний інтерфейс Lemonade, натиснувши на іконку Lemonade на панелі завдань. Тут ви можете переглядати моделі, бекенди та завантажувати попередньо встановлені моделі.
<!-- @os:end -->

<!-- @os:windows -->
Відкрийте графічний інтерфейс Lemonade, натиснувши на іконку Lemonade. Клацніть правою кнопкою миші на іконці в треї, щоб відкрити додаток. Потім ви можете додавати моделі, бекенди та завантажувати попередньо встановлені моделі.
<!-- @os:end -->

>**Порада**: Після запуску графічний інтерфейс Lemonade також доступний за адресою http://localhost:13305

Альтернативно, ви можете відкрити термінал і виконати команду `lemonade list`, щоб побачити, які моделі встановлені. Потім виконайте:

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


## Налаштування робочого процесу

### Крок 1: Реєстрація або вхід в n8n

Коли ви вперше відкриваєте n8n, вам буде запропоновано створити обліковий запис або увійти:

1. Відкрийте `http://localhost:5678` у браузері
2. Створіть новий локальний обліковий запис за допомогою вашої електронної пошти або увійдіть, якщо у вас вже є обліковий запис
3. Після входу ви побачите панель керування n8n

> **Порада**: Якщо ви заблоковані у своєму обліковому записі, спробуйте `n8n user-management:reset`

### Крок 2: Імпортування робочого процесу

Ми надали готовий робочий процес, який ви можете імпортувати безпосередньо:

1. Завантажте наступний файл робочого процесу: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Натисніть **Start from Scratch**, щоб відкрити редактор робочого процесу. Альтернативно, натисніть кнопку + у верхньому лівому куті, а потім **Add workflow**.
3. Натисніть меню **...** (три крапки) у верхній правій панелі та виберіть **Import from file**
4. Виберіть завантажений файл `financial-news-workflow.json`
5. Робочий процес з'явиться на полотні
### Крок 3: Розуміння робочого процесу

Імпортований робочий процес містить 8 з'єднаних вузлів:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Вузол | Призначення |
|------|---------|
| **When clicking 'Execute workflow'** | Ручний тригер для запуску робочого процесу |
| **Fetch Financial News Feed** | Вузол RSS Read, що отримує останні бізнес-заголовки з RSS-каналу (за замовчуванням використовується канал NYT Business, API-ключ не потрібен) |
| **Aggregate Headlines** | Вузол Aggregate, що збирає заголовки та резюме з кожного елемента каналу в єдиний список |
| **Clean Extracted News Data** | Вузол Set, що об'єднує всі заголовки в єдине текстове поле |
| **AI Financial News Summarizer** | AI Agent, що обробляє новини за допомогою системного запиту фінансового аналітика |
| **Lemonade Chat Model** | Підключається до вашого локального сервера Lemonade, на якому запущено LLM |
| **Structured Output Parser** | Форматує вихідні дані ШІ у структурований JSON |
| **Convert to File** | Перетворює резюме на файл, доступний для завантаження |

> **Порада**: щоб використати інше джерело новин, двічі клацніть вузол **Fetch Financial News Feed** і замініть URL-адресу на будь-який бажаний RSS-канал про бізнес чи ринки.

### Крок 4: Налаштування облікових даних Lemonade

Перш ніж запускати робочий процес, потрібно підключити його до вашого локального сервера Lemonade:

1. Двічі клацніть вузол **Lemonade Chat Model** у n8n
2. У випадному меню **Credential to connect with** виберіть **Create New Credential**
3. Введіть значення з наведеної нижче таблиці та натисніть save.
4. Виберіть відповідну модель, яку ви завантажили в Lemonade Server.

  | Поле | Значення |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Примітка**: перед тестуванням виконайте `lemonade status` у терміналі, щоб переконатися, що сервер Lemonade запущено.
<!-- @device:halo_box -->
> Цей робочий процес використовує GPT-OSS-120B, яка попередньо встановлена в Lemonade. Ви можете змінити це на інші завантажені моделі в налаштуваннях вузла Lemonade Chat Model.
<!-- @device:end -->

### Крок 5: Тестування робочого процесу

1. Переконайтеся, що Lemonade запущено із завантаженою моделлю
2. Натисніть **Execute workflow** внизу по центру полотна
3. Спостерігайте, як кожен вузол виконується зліва направо — вони стають зеленими після завершення
4. Двічі клацніть вузол **AI Financial News Summarizer**, щоб побачити згенероване резюме на нижній панелі.
5. Двічі клацніть вузол **Convert to File**, щоб завантажити відповідний текстовий файл на нижній панелі.

## Розуміння AI Agent

AI Financial News Summarizer використовує системний запит, розроблений для фінансового аналізу:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

Агент отримує очищені дані новин і видає структуроване резюме з ринковими настроями.

### Збереження робочого процесу

Клацніть на назву робочого процесу вгорі та за бажанням перейменуйте її. Робочі процеси зберігаються автоматично під час роботи.

## Наступні кроки

- **Автоматизація за розкладом**: замініть Manual Trigger на **Schedule Trigger**, щоб запускати процес щодня
- **Надсилання сповіщень**: додайте вузол **Discord**, **Slack** або **Email**, щоб отримувати резюме
- **Спробуйте інші моделі**: змініть модель у вузлі Lemonade Chat Model, щоб поекспериментувати з різними LLM
- **Змініть джерело новин**: спрямуйте вузол **Fetch Financial News Feed** на інший RSS-канал, щоб стежити за іншими розділами чи виданнями
- **Спробуйте інші бекенди**: n8n також підтримує [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio та інші локальні бекенди LLM

### Дослідіть шаблони n8n

n8n має сотні готових шаблонів робочих процесів. Перегляньте офіційну бібліотеку шаблонів за адресою:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Виконайте пошук за словами "AI", "LLM" або "automation", щоб знайти робочі процеси, які можна імпортувати та налаштувати.

Для отримання додаткової інформації перегляньте [Документацію n8n](https://docs.n8n.io/).

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