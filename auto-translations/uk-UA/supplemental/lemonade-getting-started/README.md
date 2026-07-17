<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Огляд

🍋 **Lemonade** — це локальний AI-сервер з відкритим вихідним кодом, який дозволяє запускати великі мовні моделі (LLM), генератори зображень та аудіомоделі безпосередньо на власному обладнанні. Він надає доступ до моделей через стандартний **OpenAI API**, тому будь-який застосунок, що працює з OpenAI, може миттєво працювати з Lemonade. Після завершення цього посібника ви зможете використовувати Lemonade для локального запуску моделей на своєму комп'ютері.

## Що ви дізнаєтесь

Після завершення цього посібника ви зможете:

* **Встановити Lemonade Server** та перевірити його роботу.
* **Завантажити LLM та спілкуватися з нею** за допомогою однієї команди.
* **Дослідити веб-інтерфейс** та спробувати різні модальності, такі як розпізнавання зображень, перетворення мовлення на текст і генерація зображень.
* **Перемикати GPU-бекенди** між Vulkan та AMD ROCm™ software.
* **Створити Python-застосунок**, що працює на основі локальної LLM з використанням OpenAI-сумісного API.
<!-- @device:halo_box,halo,stx,krk -->
* **Запускати моделі на AMD Neural Processing Unit (NPU)** з використанням режимів виконання Hybrid та FLM на обладнанні AMD Ryzen™ AI.
<!-- @device:end -->

## Налаштування конфігурації пам'яті

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Перевірка оновлень програмного забезпечення

<!-- @require:software-update -->
<!-- @device:end -->

## Встановлення необхідного програмного забезпечення

Перш ніж почати, переконайтеся, що у вас є:

- ПК під керуванням **Windows 11** або підтримуваного дистрибутива **Linux** (Ubuntu 24.04+, Fedora, Debian)
- **16 ГБ оперативної пам'яті** рекомендовано для моделі, що використовується в кроках 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 ГБ). **32 ГБ+** рекомендовано, якщо ви хочете використовувати більшу модель для генерації коду в кроці 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 ГБ).
- **~4–30 ГБ вільного місця на диску**, залежно від моделей, які ви завантажуєте. Найбільша модель у цьому посібнику займає близько 20 ГБ.
- **Python 3.10–3.13** (використовується в розділі про Python-застосунок)
- Підключення до інтернету (дротове або бездротове)
<!-- @device:halo_box,halo,stx,krk -->
- [Необов'язково] AMD XDNA 2 NPU (Ryzen AI 300/400/Max 300 series або Z2 Extreme) з останнім встановленим драйвером з [Ryzen AI Software Installation Instructions](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers), якщо ви хочете запускати модель на NPU.
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

## Основні концепції — як працюють локальні AI-сервери

Перш ніж запускати модель, варто зрозуміти *чому* все налаштовано саме так. Lemonade — це **локальний сервер моделей**, процес, який завантажує AI-моделі в пам'ять і надає до них доступ для застосунків через HTTP, так само як це робить хмарний AI-сервіс.

### Навіщо потрібен сервер?

| Перевага | Що це означає для вас |
|---------|----------------------|
| **Спрощена інтеграція** | Застосунки звертаються до одного HTTP API замість того, щоб мати справу з апаратно-специфічними бібліотеками C++ або Python. |
| **Спільні моделі** | Одна завантажена модель може обслуговувати кілька застосунків одночасно, без дублікатів, що з'їдають вашу оперативну пам'ять. |
| **Перенесення з хмари на локальне середовище** | Код, написаний для хмарного API OpenAI, працює з Lemonade після зміни одного URL. |
| **Розподіл відповідальності** | Управління моделями, потокова передача та відмовостійкість обробляються сервером, щоб розробники могли зосередитися на своєму застосунку. |

### Стандарт OpenAI API

Lemonade реалізує **OpenAI API** — той самий інтерфейс, що використовується ChatGPT, Azure OpenAI та десятками інших сервісів. Модель розмови проста:

| Роль | Хто говорить |
|------|---------------|
| **system** | Інструкції для моделі (персонаж, обмеження, доступні інструменти) |
| **user** | Повідомлення від людини (або застосунку) до моделі |
| **assistant** | Відповіді, згенеровані моделлю |

Це означає, що будь-яка бібліотека або застосунок, що підтримує OpenAI, може спілкуватися з Lemonade, вказавши адресу `http://localhost:13305/api/v1` під час роботи Lemonade Server.

## Основне завдання — ваш перший локальний AI-чат

Давайте завантажимо LLM та поспілкуємося з нею, запускаючи AI повністю на вашому власному комп'ютері.

### Крок 1: Завантаження та запуск моделі

Lemonade постачається з кураторською бібліотекою моделей. Почнемо з **Gemma-4-E2B-it** — потужної та компактної моделі з підтримкою розпізнавання зображень. Відкрийте термінал і виконайте:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Ця єдина команда виконує три дії:

1. **Завантажує** модель (~3 ГБ) з Hugging Face, якщо вона ще не завантажена. (Може зайняти деякий час)
2. **Запускає** процес Lemonade Server на порту 13305.
3. **Відкриває Lemonade App**, щоб ви могли почати спілкування з моделлю.


<!-- @os:windows -->
На Windows Lemonade App запускається автоматично, і ви можете одразу почати спілкування. Якщо ви встановили пакет `minimal.msi`, застосунок не включено. Щоб почати спілкування, відкрийте веб-браузер і перейдіть за адресою `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
На Linux відкрийте браузер і перейдіть за адресою `http://localhost:13305` для доступу до веб-застосунку.
<!-- @os:end -->

Спробуйте ввести запитання:

```
What are three fun facts about lemons?
```

Модель відповість безпосередньо у вікні чату. **Вітаємо! Ви запускаєте велику мовну модель локально.**

![Lemonade App з відображеними журналами](../../dependencies/assets/ChatwithLogs.png)

На панелі журналів сервера в Lemonade App ви можете знайти телеметричні дані про продуктивність моделі після кожної відповіді. Наприклад:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Крок 2: Дослідження веб-інтерфейсу та різних модальностей

Lemonade включає вбудований веб-інтерфейс, де ви можете:

- **Взаємодіяти** із завантаженою моделлю у звичному вікні чату
- **Переглядати моделі** на вкладці Model Manager
- **Завантажувати нові моделі** одним кліком

Спробуйте перемикатися між різними модальностями за допомогою вкладки **Model Manager** у веб-інтерфейсі, де можна переглядати моделі за рецептом або категорією:

1. **Розпізнавання зображень:** Модель `Gemma-4-E2B-it-GGUF`, яку ви вже завантажили, підтримує розпізнавання зображень. Вставте зображення у поле чату та попросіть модель описати його.
2. **Генерація зображень:** У категорії Image завантажте модель зображень, наприклад `SDXL-Turbo`, з Model Manager, а потім скористайтеся Lemonade Image Generator, щоб ввести підказку та згенерувати зображення локально.
3. **Аудіо:** У категорії Audio завантажте аудіомодель, наприклад `Whisper-Tiny`, яка може виконувати перетворення мовлення на текст. Надайте аудіозапис для його локальної транскрипції. Для перетворення тексту на мовлення спробуйте одну з моделей у категорії Speech, наприклад `kokoro-v1`.

![Мультимодальність з Lemonade](../../dependencies/assets/multi_modality.png)

### Крок 3: Спробуйте модель з іншим бекендом

Якщо навести курсор на модель у Lemonade App, з'явиться значок шестерні. Натиснувши на нього, можна вибрати параметри моделі, зокрема бажаний бекенд.

За замовчуванням Lemonade використовує Vulkan для GPU-прискорення. Якщо у вас є підтримувана дискретна AMD GPU, ви можете перейти на ROCm.

![Вибір бекенду в Lemonade](../../dependencies/assets/lemonademodeloptions.png)

Для керування встановленими бекендами натисніть кнопку бекенду в крайньому лівому стовпці.

Крім того, ви можете вказати бекенд за допомогою такої команди:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Ви також можете встановити бекенд за замовчуванням за допомогою змінної середовища `LEMONADE_LLAMACPP` зі значеннями: `vulkan`, `rocm` або `cpu`.

---

## Поглиблення — створення AI-застосунку на Python

Справжня потужність локального AI-сервера полягає в тому, що будь-який застосунок може підключитися до нього за допомогою лише кількох рядків коду. Щоб довести це, давайте створимо невеликий, але функціональний **генератор навчальних флеш-карток**: ви задаєте тему, він генерує флеш-картки, і ви можете інтерактивно перевіряти себе.

### Крок 4: Запуск сервера

Переконайтеся, що сервер Lemonade запущено. Зазвичай він запускається автоматично у фоновому режимі після встановлення. Для перевірки виконайте:

```
lemonade status
```

Ви повинні побачити повідомлення на кшталт: `Server is running on port 13305`.

Якщо сервер не запущено, запустіть його, відкривши застосунок Lemonade. Використовуйте порт за замовчуванням **13305** (ви можете підтвердити або вибрати його з піктограми в системному треї).

### Крок 5: Встановлення клієнта OpenAI для Python

У терміналі створіть venv та встановіть клієнт OpenAI для Python за допомогою таких команд:
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

### Крок 6: Створення застосунку з флеш-картками

Давайте завантажимо іншу модель для генерації коду: `Qwen3.5-35B-A3B-GGUF`. Це велика (~20 ГБ) та продуктивна модель, найкраще підходить для систем з 32 ГБ+ оперативної пам'яті. Якщо у вас менше оперативної пам'яті, спробуйте `Qwen3.5-9B-GGUF` (~6 ГБ).

Ви можете завантажити її з інтерфейсу або виконати таку команду:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Введіть наступний запит у Lemonade Chat UI для генерації коду простого застосунку з флеш-картками.

Ми використаємо Qwen3.5-35B-A3B-GGUF (більшу модель, краще пристосовану для написання коду) для генерації нашого Python-застосунку, а сам застосунок під час виконання буде звертатися до Gemma-4-E2B-it-GGUF (меншої моделі, яку ви вже завантажили). Потім код можна скопіювати до файлу на ваш вибір для запуску в Python.

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

> **Порада**: Ми дотримувалися стандартних інженерних практик завдяки ретельному складанню запитів та використанню системи з двох моделей для оптимізації ресурсів і швидкості.

Для вашої зручності ми надали приклад виводу у файлі [`flashcards.py`](assets/flashcards.py). Завантажте його до свого каталогу. У будь-якому разі у вас тепер повинен бути Python-файл, готовий до запуску.

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


### Крок 7: Запуск згенерованого коду

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**Ось що ви повинні побачити:**

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

Приблизно в 150 рядках коду ви створили повністю функціональний навчальний інструмент на основі локальної LLM. Немає API-ключа для управління, немає витрат на використання, і жодні дані не покидають ваш комп'ютер.

> **Ключове спостереження:** Зверніть увагу, що рядок `client = OpenAI(base_url=...) ` — це *єдине*, що прив'язує цей застосунок до Lemonade замість хмари OpenAI. Решта коду ідентична тому, що ви б написали для будь-якого OpenAI-сумісного сервісу. Якщо ви коли-небудь використовували бібліотеку OpenAI для Python, ви вже знаєте, як створювати застосунки з Lemonade.

### Що це демонструє

Цей невеликий застосунок реалізує кілька реальних шаблонів інтеграції:

| Шаблон | Де застосовується |
|---------|-----------------|
| **Системні підказки** | Повідомлення `"system"` вказує LLM виводити структурований JSON |
| **Структурований вивід** | Застосунок розбирає відповідь LLM як JSON для побудови флеш-карток |
| **Запити без збереження стану** | Кожен виклик `generate_flashcards()` є незалежним |
| **Обробка помилок** | Блок `try/except` коректно обробляє випадки, коли вивід LLM не є валідним JSON |

Ці самі шаблони масштабуються до будь-якого застосунку: чат-боти, помічники з коду, генератори контенту, інструменти автоматизації.

#### Додаткове завдання

* Для додаткового виклику спробуйте оновити застосунок так, щоб флеш-картки зачитувалися користувачу, звернувшись до прикладу, наведеного [тут](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## Запуск моделей на NPU (необов'язково)

Якщо у вас є Ryzen AI 300/400/Max 300 series або Z2 Extreme, ваш пристрій має вбудований **Neural Processing Unit (NPU)** — спеціалізований чіп, розроблений спеціально для AI-навантажень. Запуск моделей на NPU є більш енергоефективним, ніж використання GPU, що робить його ідеальним для фонових AI-завдань, тривалих сесій та використання від акумулятора.

Lemonade підтримує три режими виконання на NPU, всі прозорі за тим самим OpenAI API:

| Режим | Як працює | Рецепт | Приклади моделей |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | NPU обробляє запит, iGPU генерує токени | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Тільки NPU** | Весь процес виведення виконується на NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Використовує рушій FastFlowLM на NPU, оптимізований для AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Вимоги

- Процесор **AMD Ryzen AI 300/400 series або Z2 series**
- Для моделей **FLM**: середовище виконання FLM можна встановити з застосунку Lemonade, або Lemonade автоматично встановить середовище виконання FLM під час запуску моделі FLM. Щоб дізнатися більше про FastFlowLM, перейдіть [сюди](https://fastflowlm.com/docs/).


### Крок 8: Запуск гібридної моделі

Гібридні моделі розподіляють роботу між NPU та iGPU для досягнення хорошого балансу між швидкістю та ефективністю. У Lemonade App виберіть модель зі списку `Ryzen AI LLM`, наприклад `Qwen3-4B-Hybrid`, або запустіть її за допомогою такої команди:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade автоматично виявляє ваш NPU та встановлює бекенд **Ryzen AI LLM**.

> **Що відбувається під капотом?** Коли ви надсилаєте повідомлення, NPU паралельно обробляє весь ваш запит (це називається "prefill"). Потім iGPU бере на себе генерацію відповіді по одному токену за раз (це називається "decode"). Такий гібридний підхід використовує сильні сторони кожного чіпа.

### Крок 9: Запуск моделі FLM

Моделі FastFlowLM (FLM) спеціально оптимізовані для архітектури NPU AMD XDNA2 і можуть бути дуже швидкими для свого розміру. Наприклад, виберіть `qwen3.5-4b-FLM` зі списку `FastFlowLM NPU` або скористайтеся такою командою:

<!-- @os:windows -->
Щоб увімкнути `FastFlowLM` на Windows:

* Відкрийте меню `Backends Manager`.
* Знайдіть категорію бекенду `FastFlowLM NPU`.
* Натисніть Install NPU.
* Після завершення встановлення у спадному меню FFLM буде доступно ~36 моделей за замовчуванням.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
Коли застосунок `Lemonade` запускається вперше, бекенд `FastFlowNPU` не увімкнено за замовчуванням.
Локальний застосунок відкриє сторінку встановлення для керівництва вами через налаштування.

Щоб увімкнути `FastFlowLM` на Linux:

* Відкрийте застосунок `Lemonade`.
* Відвідайте [офіційну документацію FLM](https://lemonade-server.ai/flm_npu_linux.html) та дотримуйтесь кроків встановлення FLM, вибравши свій дистрибутив Linux.
* Увімкніть backports відповідно до інструкцій на сторінці встановлення.
* Завантажте останній реліз `v0.9.x` зі [сторінки тегів](https://github.com/FastFlowLM/FastFlowLM/tags).
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
Для AMD Halo Developer Platform обов'язково виберіть Debian 13.
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
* Рекомендовано: закрийте `Lemonade App` та відкрийте його знову, щоб зміни були виявлені.
* Рекомендовано: відкрийте `Backends Manager` та натисніть Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
Після успішного встановлення ви повинні побачити, що `flm:npu` завершено в **Download Manager** всередині **Lemonade Desktop App**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
Потім ви можете вибрати будь-яку з доступних моделей FFLM та почати використовувати бекенд NPU.

Для конкретної моделі завантажте бажану модель зі [сторінки моделей](https://fastflowlm.com/docs/models/qwen/) та перевірте її за допомогою команди Shell, наведеної в документації.
```
flm run qwen3.5-4b-FLM
```
або через 
```
lemonade run qwen3.5-4b-FLM
```

Моделі FLM включають деякі з найпопулярніших архітектур (Gemma 3, Qwen 3, Llama 3 та DeepSeek R1) і варіюються від менш ніж 1 ГБ до понад 13 ГБ.
Lemonade автоматично виявляє ваш NPU та встановлює бекенд **FastFlowLM NPU**.

<!-- @os:windows -->
> **Порада:** Для найкращої продуктивності NPU увімкніть режим turbo:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Перемикання моделей

Застосунок з флеш-картками з кроку 6 також працює з моделями NPU — просто змініть назву моделі:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Наступні кроки

У вас є локальний AI-сервер, що працює на вашому власному обладнанні — ось куди рухатися далі:

1. **Підключіть улюблені застосунки**: Lemonade працює з коробки з [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) та [багатьма іншими](https://lemonade-server.ai/marketplace).

2. **Перегляньте більше моделей**: Дослідіть повну [бібліотеку моделей](https://lemonade-server.ai/docs/server/server_models/), щоб знайти моделі, оптимізовані для написання коду, міркування, розпізнавання зображень тощо. Використовуйте Lemonade App або `lemonade list`, щоб побачити, що доступно.

3. **Розблокуйте GPU-прискорення ROCm**: Якщо у вас є підтримувана AMD GPU, перейдіть на бекенд ROCm: `lemonade config set llamacpp.backend=rocm`. Перегляньте [підтримувані AMD GPU](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Ознайомтеся з повною специфікацією API**: Lemonade підтримує завершення чату, вбудовування, транскрипцію аудіо, генерацію зображень, перетворення тексту на мовлення тощо. Перегляньте [специфікацію сервера](https://lemonade-server.ai/docs/server/server_spec/) для кожного ендпоінту.

5. **Зробіть внесок**: Lemonade є відкритим вихідним кодом. Ознайомтеся з [посібником зі внесків](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) та шукайте [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).