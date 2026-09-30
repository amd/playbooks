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
## Огляд

🍋 **Lemonade** — це серверне рішення для локального штучного інтелекту з відкритим кодом, яке дає змогу запускати великі мовні моделі (LLM), генератори зображень і аудіомоделі безпосередньо на вашому власному обладнанні. Воно надає доступ до моделей через галузевий стандарт **OpenAI API**, тож будь-який додаток, що працює з OpenAI, миттєво зможе працювати з Lemonade. Наприкінці цього посібника ви вже використовуватимете Lemonade для локального запуску моделей на своєму комп'ютері.

## Чого ви навчитеся

Наприкінці цього посібника ви зможете:

* **Встановити Lemonade Server** і перевірити його роботу.
* **Завантажити LLM і почати спілкування з нею** за допомогою однієї команди.
* **Дослідити веб-інтерфейс** і спробувати різні режими роботи, як-от розпізнавання зображень, перетворення мовлення на текст і генерацію зображень.
* **Перемикатися між бекендами GPU** — Vulkan та ПЗ AMD ROCm™.
* **Створити застосунок на Python**, що працює на основі локальної LLM, використовуючи API, сумісний з OpenAI.
<!-- @device:halo_box,halo,stx,krk -->
* **Запускайте моделі на нейронному процесорі (NPU) AMD**, використовуючи режими виконання Hybrid і FLM на апаратному забезпеченні AMD Ryzen™ AI.
<!-- @device:end -->

<!-- @device:halo_box,halo,stx,krk -->
## Налаштування конфігурації пам'яті
<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Перевірка наявності оновлень програмного забезпечення
<!-- @require:software-update -->
<!-- @device:end -->
## Встановлення необхідного програмного забезпечення

Перш ніж почати, переконайтеся, що у вас є:

- ПК під керуванням **Windows 11** або підтримуваного дистрибутива **Linux** (Ubuntu 24.04+, Fedora, Debian)
- Рекомендовано **16 ГБ оперативної пам’яті** для моделі середовища виконання, яка використовується в кроках 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 ГБ). Рекомендовано **32 ГБ+**, якщо ви хочете використовувати більшу модель для генерації коду в кроці 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 ГБ).
- **~4–30 ГБ вільного місця на диску**, залежно від моделей, які ви завантажите. Найбільша модель у цьому посібнику важить близько 20 ГБ.
- **Python 3.10–3.13** (використовується в розділі про Python-застосунок)
- Підключення до інтернету (дротове або бездротове)
<!-- @device:halo_box,halo,stx,krk -->
- [Необов'язково] NPU AMD XDNA 2 (Ryzen AI 300/400/Max 300 series або Z2 Extreme) з останнім установленим драйвером із [Інструкцій із встановлення програмного забезпечення Ryzen AI](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers), якщо ви хочете запускати модель на NPU.
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-update-windows timeout=120 hidden=True -->
```powershell
winget upgrade -e --id AMD.LemonadeServer
lemonade --version

# Upgrading runs the Lemonade Server installer, which stops the running server
# to replace its files and does not start it again. Relaunch it so the local API
# on port 13305 is available for the next steps.
if (-not (Get-Process LemonadeServer -ErrorAction SilentlyContinue)) {
  Start-Process "$env:LOCALAPPDATA\lemonade_server\bin\LemonadeServer.exe"
}
```
<!-- @test:end -->

<!-- @test:id=lemonade-chat-gemma-windows timeout=1200 hidden=True -->
```powershell

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade(robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "Gemma-4-E2B-it-GGUF" } | Select-Object -First 1
if (-not $entry) { throw "Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "Gemma-4-E2B-it-GGUF"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 500
} | ConvertTo-Json -Depth 5
$out = curl.exe -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions -H "Content-Type: application/json" -d $body
if (-not $out) { throw "Empty response from Lemonade chat/completions" }
Write-Host "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-update-linux timeout=120 hidden=True -->
```bash
sudo apt update
sudo apt install --only-upgrade lemonade-server
lemonade --version
```
<!-- @test:end -->

<!-- @test:id=lemonade-chat-gemma-linux timeout=1200 hidden=True -->
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
    if item.get("id") == "Gemma-4-E2B-it-GGUF":
        entry = item
        break

if entry is None:
    print("Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade")
PY

body='{
  "model": "Gemma-4-E2B-it-GGUF",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 500
}'

out="$(curl -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->
---

## Основні концепції — як працюють локальні сервери ШІ

Перед тим, як запускати модель, варто зрозуміти, *чому* все влаштовано саме так. Lemonade — це **локальний сервер моделей**, процес, який завантажує моделі ШІ в пам'ять і надає до них доступ застосункам через HTTP, так само як це робив би хмарний сервіс ШІ.

### Навіщо потрібен сервер?

| Перевага | Що це означає для вас |
|---------|----------------------|
| **Спрощена інтеграція** | Застосунки взаємодіють з одним HTTP API замість роботи з апаратно-специфічними бібліотеками C++ або Python. |
| **Спільні моделі** | Одна завантажена модель може обслуговувати кілька застосунків одночасно, без дублювання копій, що з'їдають вашу оперативну пам'ять. |
| **Портативність із хмари в локальне середовище** | Код, написаний для хмарного API OpenAI, працює з Lemonade після зміни лише однієї URL-адреси. |
| **Розділення відповідальності** | Керування моделями, потокова передача та відмовостійкість обробляються сервером, тож розробники можуть зосередитися на своєму застосунку. |

### Стандарт OpenAI API

Lemonade реалізує **OpenAI API** — той самий інтерфейс, що використовується ChatGPT, Azure OpenAI та десятками інших сервісів. Модель розмови проста:

| Роль | Хто говорить |
|------|---------------|
| **system** | Інструкції для моделі (персона, обмеження, доступні інструменти) |
| **user** | Повідомлення від людини (або застосунку) до моделі |
| **assistant** | Відповіді, згенеровані моделлю |

Це означає, що будь-яка бібліотека чи застосунок, який підтримує OpenAI, може взаємодіяти з Lemonade, вказавши на `http://localhost:13305/api/v1`, поки Lemonade Server працює.

## Основна діяльність — ваш перший локальний чат зі ШІ

Завантажмо LLM і поспілкуємося з нею, запустивши ШІ повністю на власній машині.

### Крок 1: Завантаження та запуск моделі

Lemonade постачається з добірною бібліотекою моделей. Почнімо з **Gemma-4-E2B-it** — потужної та компактної моделі з підтримкою розпізнавання зображень. Відкрийте термінал і виконайте:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Ця одна команда виконує три дії:

1. **Завантажує** модель (~3 ГБ) з Hugging Face, якщо вона ще не завантажена. (Може зайняти певний час)
2. **Запускає** процес Lemonade Server на порту 13305.
3. **Відкриває Lemonade App**, щоб ви могли почати спілкування з моделлю.
<!-- @os:windows -->
На Windows додаток Lemonade App запускається автоматично, і ви можете одразу почати спілкування. Якщо ви встановили пакет `minimal.msi`, цей додаток не входить до складу. Щоб почати спілкування, відкрийте веб-браузер і перейдіть за адресою `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
На Linux відкрийте браузер і перейдіть за адресою `http://localhost:13305`, щоб отримати доступ до веб-застосунку.
<!-- @os:end -->
Спробуйте ввести запитання:

```
What are three fun facts about lemons?
```

Модель відповість безпосередньо у вікні чату. **Вітаємо! Ви запустили велику мовну модель локально.**

![Lemonade App з відображеними журналами](../../dependencies/assets/ChatwithLogs.png)

На панелі журналів сервера (Server Logs) у Lemonade App ви можете знайти дані телеметрії про продуктивність моделі після кожної відповіді. Наприклад:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Крок 2: Дослідіть веб-інтерфейс і різні модальності

Lemonade містить вбудований веб-інтерфейс, у якому ви можете:

- **Взаємодіяти** із завантаженою моделлю у звичному вікні чату
- **Переглядати моделі** на вкладці Model Manager
- **Завантажувати нові моделі** одним натисканням

Спробуйте перемикатися між різними модальностями за допомогою вкладки **Model Manager** у веб-інтерфейсі, де можна переглядати моделі за Recipe або за Category:

1. **Vision:** Модель `Gemma-4-E2B-it-GGUF`, яку ви вже завантажили, підтримує vision. Вставте зображення у поле чату та попросіть модель описати його.
2. **Генерація зображень:** У категорії Image завантажте модель для зображень, наприклад `SDXL-Turbo`, у Model Manager, а потім скористайтеся Lemonade Image Generator, щоб ввести підказку та згенерувати зображення локально.
3. **Аудіо:** У категорії Audio завантажте аудіомодель, наприклад `Whisper-Tiny`, яка вміє перетворювати мовлення на текст. Надайте аудіозапис для локальної транскрипції. Для перетворення тексту на мовлення спробуйте одну з моделей у категорії Speech, наприклад `kokoro-v1`.

![Мультимодальність з Lemonade](../../dependencies/assets/multi_modality.png)

### Крок 3: Спробуйте модель з іншим бекендом

Якщо навести курсор на модель у Lemonade App, з'явиться значок шестерні. Натиснувши на нього, ви можете вибрати параметри для моделі, зокрема обрати потрібний бекенд.

За замовчуванням Lemonade використовує Vulkan для прискорення на GPU. Якщо у вас є підтримуваний дискретний GPU AMD, ви можете переключитися на ROCm.

![Вибір бекенду Lemonade](../../dependencies/assets/lemonademodeloptions.png)

Щоб керувати встановленими бекендами, натисніть кнопку бекенду в крайньому лівому стовпці.

Крім того, ви можете вказати бекенд за допомогою такої команди:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Ви також можете встановити бекенд за замовчуванням за допомогою змінної середовища `LEMONADE_LLAMACPP` зі значеннями: `vulkan`, `rocm` або `cpu`.

---

## Йдемо далі — створюємо застосунок на основі ШІ за допомогою Python

Справжня сила локального AI-сервера полягає в тому, що будь-який застосунок може підключитися до нього за допомогою лише кількох рядків коду. Щоб це довести, давайте створимо невеликий, але функціональний **генератор навчальних карток**, якому ви задаєте тему, він генерує картки, а ви можете перевіряти себе в інтерактивному режимі.

### Крок 4: Запустіть сервер

Переконайтеся, що сервер Lemonade запущено. Зазвичай він запускається автоматично у фоновому режимі після встановлення. Щоб перевірити це, виконайте:

```
lemonade status
```

Ви маєте побачити повідомлення на кшталт: `Server is running on port 13305`.

Якщо сервер не запущено, запустіть його, відкривши застосунок Lemonade. Використовуйте порт за замовчуванням **13305** (це можна підтвердити або вибрати через значок у треї).

### Крок 5: Встановіть клієнт OpenAI Python

У терміналі створіть venv і встановіть клієнт OpenAI Python за допомогою наведених нижче команд:
<!-- @os:linux -->
```bash
# Your specific version of Linux may have different commands
sudo apt update
sudo apt install -y python3-venv
python3 -m venv lemonade-env
source lemonade-env/bin/activate
pip install openai
```
<!-- @os:end -->
<!-- @os:windows -->
```powershell
python -m venv lemonade-env
lemonade-env\Scripts\activate
pip install openai
```
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=env-check-windows timeout=300 hidden=True -->
```powershell
python --version
where.exe python
where.exe pip
python -c "import sys; print(sys.executable)"
python -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=env-check-linux timeout=300 hidden=True -->
```bash
python3 --version
which python3
which pip3
python3 -c "import sys; print(sys.executable)"
python3 -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=pip-install-openai-windows timeout=300 hidden=True -->
```powershell
python -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=pip-install-openai-linux timeout=300 hidden=True -->
```bash
python3 -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-openai-import-windows timeout=120 hidden=True -->
```powershell
python -m pip show openai
python -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=python-openai-import-linux timeout=120 hidden=True -->
```bash
python3 -m pip show openai
python3 -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

### Крок 6: Створіть застосунок для карток

Завантажимо іншу модель для генерації коду: `Qwen3.5-35B-A3B-GGUF`. Це велика (~20 ГБ) і продуктивна модель, найкраще підходить для систем із 32 ГБ+ оперативної пам'яті. Якщо у вас менше доступної пам'яті, спробуйте замість неї `Qwen3.5-9B-GGUF` (~6 ГБ).

Ви можете завантажити її через інтерфейс користувача або виконати таку команду:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Введіть наступну підказку в Lemonade Chat UI, щоб згенерувати код простого застосунку для карток.

Ми використаємо Qwen3.5-35B-A3B-GGUF (більшу модель, краще пристосовану для написання коду) для генерації нашого застосунку на Python, а сам застосунок під час виконання викликатиме Gemma-4-E2B-it-GGUF (меншу модель, яку ви вже завантажили). Отриманий код можна скопіювати у файл на свій вибір і запустити на Python.

```
Generate a Python script that uses the OpenAI Python library to call a local LLM and create an interactive flashcard study tool.

Connection details:
- Base URL: http://localhost:13305/api/v1
- API key: "lemonade"
- Model to use: "Gemma-4-E2B-it-GGUF"

Structure:

1. A `generate_flashcards(topic, count=5)` function that:
   - Sends a system message instructing the LLM to return ONLY a JSON array of objects with "question" and "answer" fields.
   - Handles malformed JSON gracefully.
   - Returns the parsed list of cards, or an empty list if parsing fails.

2. A `quiz(cards)` function that shuffles the cards and, for each card:
   - Prints `--- Card i/N ---`.
   - Prints `Q: <question>`.
   - Waits for the user to press Enter ("Press Enter to reveal the answer...").
   - Prints `A: <answer>`.
   - Asks "Did you get it right? (y/n): " and tracks the score.
   - At the end, prints `🏆 Score: <score>/<total>`.

3. A main loop that:
   - Prints a `🍋 Lemonade Flashcard Generator` banner on startup.
   - Asks the user for a topic (typing "quit" exits).
   - Prints `✨ Generating N flashcards on: <topic>`.
   - Calls `generate_flashcards` and lists the generated questions as an indented numbered list (`  1. ...`).
   - Offers to start the quiz.
```

> **Порада**: Ми дотримувалися стандартних інженерних практик, ретельно створивши підказку та використавши систему з двох моделей для оптимізації ресурсів і швидкості.

Для вашої зручності ми надали приклад результату у файлі [`flashcards.py`](assets/flashcards.py). Не соромтеся завантажити його у свою директорію. У будь-якому разі тепер у вас має бути файл Python, який можна запустити.

<!-- @os:windows -->
<!-- @test:id=lemonade-python-smoke-windows timeout=900 hidden=True -->
```powershell
# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

Start-Sleep -Seconds 5
python lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-python-smoke-linux timeout=600 hidden=True -->
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

sleep 5
python3 lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


### Крок 7: Запустіть згенерований код

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**Ось що ви маєте побачити:**

```
🍋 Lemonade Flashcard Generator
================================
Powered by a local LLM running on your own hardware.

Enter a topic (or "quit" to exit): the solar system

✨ Generating 5 flashcards on: the solar system

Generated 5 cards!

  1. Which planet is closest to the Sun?
  2. What is the largest planet in our solar system?
  3. Which planet is known as the "Red Planet"?
  4. How many moons does Earth have?
  5. What separates the inner planets from the outer planets?

Start quiz? (y/n): y

--- Card 1/5 ---
Q: What is the largest planet in our solar system?

Press Enter to reveal the answer...
A: Jupiter is the largest planet, with a diameter of about 139,820 km.

Did you get it right? (y/n): y

...

🏆 Score: 4/5
```

Приблизно у 150 рядках коду ви створили повністю функціональний навчальний інструмент на основі локальної LLM. Немає жодного API-ключа, яким потрібно керувати, немає витрат на використання, і жодні дані не залишають вашу машину.

> **Ключовий момент:** Зверніть увагу, що рядок `client = OpenAI(base_url=...) ` — це *єдине*, що пов'язує цей застосунок із Lemonade замість хмари OpenAI. Решта коду ідентична тому, що ви б написали для будь-якого сервісу, сумісного з OpenAI. Якщо ви коли-небудь використовували бібліотеку OpenAI Python, ви вже знаєте, як створювати застосунки з Lemonade.

### Що це демонструє

Цей невеликий застосунок демонструє кілька реальних патернів інтеграції:

| Патерн | Де зустрічається |
|---------|-----------------|
| **Системні підказки** | Повідомлення `"system"` вказує LLM виводити структурований JSON |
| **Структурований вивід** | Застосунок розбирає відповідь LLM як JSON для створення карток |
| **Запити без стану** | Кожен виклик `generate_flashcards()` є незалежним |
| **Обробка помилок** | `try/except` коректно обробляє випадки, коли вивід LLM не є валідним JSON |

Ці ж патерни масштабуються на будь-який застосунок, наприклад чат-боти, помічники з кодування, генератори контенту, інструменти автоматизації.

#### Додаткове завдання

* Для додаткового виклику спробуйте оновити застосунок так, щоб картки зачитувалися користувачу, скориставшись прикладом, наведеним [тут](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## Запуск моделей на NPU (Опціонально)

Якщо у вас Ryzen AI 300/400/Max 300 series або Z2 Extreme, ваш пристрій має вбудований **Neural Processing Unit (NPU)** — спеціалізований чіп, розроблений спеціально для AI-навантажень. Запуск моделей на NPU є більш енергоефективним, ніж використання GPU, що робить його ідеальним для фонових AI-завдань, довших сесій та роботи від акумулятора.

Lemonade підтримує три режими виконання на NPU, усі прозорі за тим самим OpenAI API:

| Режим | Як це працює | Рецепт | Приклади моделей |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | NPU обробляє промпт, iGPU генерує токени | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **NPU-only** | Весь інференс виконується на NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Використовує рушій FastFlowLM на NPU, оптимізований для AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Вимоги

- Процесор **AMD Ryzen AI 300/400 series або Z2 series**
- Для моделей **FLM**: середовище виконання FLM можна встановити безпосередньо з додатка Lemonade, або Lemonade автоматично встановить середовище виконання FLM під час запуску моделі FLM. Щоб дізнатися більше про FastFlowLM, дивіться [тут](https://fastflowlm.com/docs/).


### Крок 8: Запуск гібридної моделі

Гібридні моделі розподіляють роботу між NPU та iGPU для гарного балансу швидкості й ефективності. У додатку Lemonade оберіть модель зі списку `Ryzen AI LLM`, наприклад, `Qwen3-4B-Hybrid`, або запустіть її за допомогою наступної команди:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade автоматично виявляє ваш NPU та встановлює бекенд **Ryzen AI LLM**.

> **Що відбувається "під капотом"?** Коли ви надсилаєте повідомлення, NPU обробляє весь ваш промпт паралельно (це називається "prefill"). Потім iGPU бере на себе генерацію відповіді по одному токену за раз (це називається "decode"). Такий гібридний підхід використовує сильні сторони кожного чіпа.

### Крок 9: Запуск моделі FLM

Моделі FastFlowLM (FLM) спеціально оптимізовані для архітектури AMD XDNA2 NPU і можуть бути дуже швидкими для свого розміру. Наприклад, оберіть `qwen3.5-4b-FLM` зі списку `FastFlowLM NPU` або скористайтеся наступною командою:

<!-- @os:windows -->
Щоб увімкнути `FastFlowLM` у Windows:

* Відкрийте меню `Backends Manager`.
* Знайдіть категорію бекенду `FastFlowLM NPU`.
* Натисніть Install NPU.
* Після завершення встановлення в меню FFLM буде доступно приблизно 36 стандартних моделей.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Коли додаток `Lemonade` запускається вперше, бекенд `FastFlowNPU` за замовчуванням не увімкнений. 
Локальний додаток відкриє сторінку встановлення, щоб провести вас через налаштування.

Щоб увімкнути `FastFlowLM` у Linux:

* Відкрийте додаток `Lemonade`.
* Відвідайте [офіційну документацію FLM](https://lemonade-server.ai/flm_npu_linux.html) та дотримуйтесь кроків встановлення FLM, обравши свій дистрибутив Linux.
* Увімкніть backports, як зазначено на сторінці встановлення.
* Завантажте останній реліз `v0.9.x` зі [сторінки тегів](https://github.com/FastFlowLM/FastFlowLM/tags).'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
Для AMD Halo Developer Platform обов'язково оберіть Debian 13.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* Встановіть завантажений пакет `.deb`.
* Рекомендовано: закрийте додаток `Lemonade App` і відкрийте його знову, щоб зміни були виявлені.
* Рекомендовано: відкрийте `Backends Manager` та натисніть Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Після успішного встановлення ви повинні побачити, що `flm:npu` завершено в **Download Manager** усередині **Lemonade Desktop App**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Потім ви можете обрати будь-яку з доступних моделей FFLM та почати використовувати бекенд NPU.

Для конкретної моделі завантажте бажану модель зі [сторінки моделей](https://fastflowlm.com/docs/models/qwen/) та перевірте її за допомогою команди Shell, наведеної в документації.
```
flm run qwen3.5-4b-FLM
```
або через 
```
lemonade run qwen3.5-4b-FLM
```

Моделі FLM включають деякі з найпопулярніших архітектур (Gemma 3, Qwen 3, Llama 3 та DeepSeek R1) і мають розмір від менше 1 ГБ до понад 13 ГБ.
Lemonade автоматично виявляє ваш NPU та встановлює бекенд **FastFlowLM NPU**.

<!-- @os:windows -->
> **Порада:** Для найкращої продуктивності NPU увімкніть турборежим:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Перемикання моделей

Додаток флеш-карток із кроку 6 також працює з моделями NPU, просто змініть назву моделі:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Наступні кроки

Тепер у вас є локальний AI-сервер, що працює на вашому власному обладнанні. Ось куди можна рухатися далі:

1. **Підключіть свої улюблені додатки**: Lemonade працює "з коробки" з [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) та [багатьма іншими](https://lemonade-server.ai/marketplace).

2. **Перегляньте більше моделей**: Дослідіть повну [бібліотеку моделей](https://lemonade-server.ai/docs/server/server_models/), щоб знайти моделі, оптимізовані для кодування, міркування, зору та іншого. Скористайтеся додатком Lemonade або командою `lemonade list`, щоб побачити, що доступно.

3. **Розблокуйте прискорення ROCm GPU**: Якщо у вас є підтримуваний GPU AMD, перемкніться на бекенд ROCm: `lemonade config set llamacpp.backend=rocm`. Дивіться [підтримувані AMD GPU](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Прочитайте повну специфікацію API**: Lemonade підтримує завершення чату, вбудовування, транскрипцію аудіо, генерацію зображень, синтез мовлення та інше. Дивіться [Специфікацію сервера](https://lemonade-server.ai/docs/server/server_spec/) для всіх ендпоінтів.

5. **Зробіть свій внесок**: Lemonade — це проєкт з відкритим кодом. Ознайомтеся з [посібником для контриб'юторів](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) та зверніть увагу на [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

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