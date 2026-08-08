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
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Обзор

🍋 **Lemonade** — это локальный AI-сервер с открытым исходным кодом, который позволяет запускать большие языковые модели (LLM), генераторы изображений и аудиомодели прямо на вашем собственном оборудовании. Он предоставляет доступ к моделям через отраслевой стандарт **OpenAI API**, поэтому любое приложение, работающее с OpenAI, сразу же сможет работать с Lemonade. К концу этого плейбука вы будете использовать Lemonade для локального запуска моделей на своей машине.

## Чему вы научитесь

К концу этого плейбука вы сможете:

* **Установить Lemonade Server** и убедиться, что он работает.
* **Скачать LLM и начать с ней диалог** одной командой.
* **Изучить веб-интерфейс** и опробовать различные модальности, такие как распознавание изображений, преобразование речи в текст и генерация изображений.
* **Переключать GPU-бэкенды** между Vulkan и AMD ROCm™.
* **Создать приложение на Python** на основе локальной LLM с использованием API, совместимого с OpenAI.
<!-- @device:halo_box,halo,stx,krk -->
* **Запускать модели на нейронном процессоре AMD (NPU)** с использованием режимов выполнения Hybrid и FLM на оборудовании AMD Ryzen™ AI.
<!-- @device:end -->

## Настройка конфигурации памяти

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Проверка обновлений программного обеспечения

<!-- @require:software-update -->
<!-- @device:end -->

## Установка необходимого программного обеспечения

Прежде чем начать, убедитесь, что у вас есть:

- ПК с **Windows 11** или поддерживаемым дистрибутивом **Linux** (Ubuntu 24.04+, Fedora, Debian)
- Рекомендуется **16 ГБ ОЗУ** для рабочей модели, используемой в шагах 1–7 (`Gemma-4-E2B-it-GGUF`, ~3 ГБ). Рекомендуется **32 ГБ и более**, если вы хотите использовать более крупную модель генерации кода в шаге 6 (`Qwen3.5-35B-A3B-GGUF`, ~20 ГБ).
- **~4–30 ГБ свободного места на диске**, в зависимости от загружаемых моделей. Самая крупная модель в этом руководстве занимает около 20 ГБ.
- **Python 3.10–3.13** (используется в разделе с Python-приложением)
- Подключение к интернету (проводное или беспроводное)
<!-- @device:halo_box,halo,stx,krk -->
- [Опционально] NPU AMD XDNA 2 (серии Ryzen AI 300/400/Max 300 или Z2 Extreme) с последним установленным драйвером из [инструкций по установке ПО Ryzen AI](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers), если вы хотите запускать модель на NPU.
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
```bash
winget upgrade -e --id AMD.LemonadeServer
lemonade --version
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

## Основные концепции — как работают локальные AI-серверы

Прежде чем запускать модель, стоит понять, *почему* всё устроено именно так. Lemonade — это **локальный сервер моделей**, процесс, который загружает AI-модели в память и предоставляет к ним доступ приложениям по HTTP, точно так же, как это делал бы облачный AI-сервис.

### Зачем нужен сервер?

| Преимущество | Что это значит для вас |
|---------|----------------------|
| **Упрощённая интеграция** | Приложения взаимодействуют с одним HTTP API вместо работы со специфичными для оборудования библиотеками C++ или Python. |
| **Общие модели** | Одна загруженная модель может обслуживать несколько приложений одновременно, без дублирующихся копий, съедающих вашу оперативную память. |
| **Переносимость между облаком и локальной средой** | Код, написанный для облачного API OpenAI, работает с Lemonade после изменения всего одного URL. |
| **Разделение обязанностей** | Управление моделями, потоковая передача данных и отказоустойчивость обрабатываются сервером, поэтому разработчики могут сосредоточиться на своём приложении. |

### Стандарт OpenAI API

Lemonade реализует **OpenAI API** — тот же интерфейс, который используется в ChatGPT, Azure OpenAI и десятках других сервисов. Модель диалога проста:

| Роль | Кто говорит |
|------|---------------|
| **system** | Инструкции для модели (персона, ограничения, доступные инструменты) |
| **user** | Сообщения от человека (или приложения) к модели |
| **assistant** | Ответы, сгенерированные моделью |

Это означает, что любая библиотека или приложение, поддерживающее OpenAI, может взаимодействовать с Lemonade, направив запросы на `http://localhost:13305/api/v1` при запущенном Lemonade Server.

## Основная часть — ваш первый локальный AI-чат

Давайте скачаем LLM и пообщаемся с ней, запустив AI полностью на вашей собственной машине.

### Шаг 1: Скачивание и запуск модели

Lemonade поставляется с подобранной библиотекой моделей. Начнём с **Gemma-4-E2B-it** — компактной и функциональной модели с поддержкой распознавания изображений. Откройте терминал и выполните:

```
lemonade run Gemma-4-E2B-it-GGUF
```

Эта единственная команда выполняет три действия:

1. **Скачивает** модель (~3 ГБ) с Hugging Face, если она ещё не загружена. (Может занять некоторое время)
2. **Запускает** процесс Lemonade Server на порту 13305.
3. **Открывает Lemonade App**, чтобы вы могли начать общение с моделью.


<!-- @os:windows -->
В Windows Lemonade App запускается автоматически, и вы можете сразу начать общение. Если вы установили пакет `minimal.msi`, приложение не включено. Чтобы начать общение, откройте веб-браузер и перейдите по адресу `http://localhost:13305`.
<!-- @os:end -->

<!-- @os:linux -->
В Linux откройте браузер и перейдите по адресу `http://localhost:13305`, чтобы получить доступ к веб-приложению.
<!-- @os:end -->

Попробуйте ввести вопрос:

```
What are three fun facts about lemons?
```

Модель ответит непосредственно в окне чата. **Поздравляем! Вы запустили большую языковую модель локально.**

![Приложение Lemonade с отображёнными журналами](../../dependencies/assets/ChatwithLogs.png)

В панели журналов сервера (Server Logs) в Lemonade App вы можете найти данные телеметрии о производительности модели после каждого ответа. Например:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### Шаг 2: Изучите веб-интерфейс и различные модальности

Lemonade включает встроенный веб-интерфейс, в котором вы можете:

- **Взаимодействовать** с загруженной моделью в привычном окне чата
- **Просматривать модели** на вкладке Model Manager
- **Скачивать новые модели** одним щелчком мыши

Попробуйте переключаться между разными модальностями с помощью вкладки **Model Manager** в веб-интерфейсе, где можно просматривать модели по рецепту (Recipe) или по категории (Category):

1. **Изображения (Vision):** Уже загруженная у вас модель `Gemma-4-E2B-it-GGUF` поддерживает работу с изображениями. Вставьте изображение в поле чата и попросите модель описать его.
2. **Генерация изображений:** В категории Image скачайте модель для генерации изображений, например `SDXL-Turbo`, из Model Manager, а затем используйте Lemonade Image Generator, чтобы ввести запрос и локально сгенерировать изображение.
3. **Аудио:** В категории Audio скачайте аудиомодель, например `Whisper-Tiny`, которая умеет преобразовывать речь в текст. Предоставьте аудиозапись, чтобы локально её транскрибировать. Для преобразования текста в речь попробуйте одну из моделей в категории Speech, например `kokoro-v1`.

![Мультимодальность с Lemonade](../../dependencies/assets/multi_modality.png)

### Шаг 3: Попробуйте модель с другим бэкендом

Наведя курсор на модель в приложении Lemonade, вы увидите значок шестерёнки. Нажав на него, можно выбрать параметры модели, включая нужный бэкенд.

По умолчанию Lemonade использует Vulkan для ускорения на GPU. Если у вас есть поддерживаемый дискретный GPU AMD, вы можете переключиться на ROCm.

![Выбор бэкенда в Lemonade](../../dependencies/assets/lemonademodeloptions.png)

Чтобы управлять установленными бэкендами, нажмите кнопку бэкенда в крайнем левом столбце.

Также можно указать бэкенд с помощью следующей команды:

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

Кроме того, можно задать бэкенд по умолчанию с помощью переменной окружения `LEMONADE_LLAMACPP` со значениями: `vulkan`, `rocm` или `cpu`.

---

## Идём дальше — создаём приложение с ИИ на Python

Настоящая сила локального сервера ИИ заключается в том, что любое приложение может подключиться к нему всего за несколько строк кода. Чтобы это доказать, давайте создадим небольшое, но функциональное **приложение для генерации учебных карточек**, которому вы задаёте тему, оно генерирует карточки, а вы можете интерактивно проверять свои знания.

### Шаг 4: Запустите сервер

Убедитесь, что сервер Lemonade запущен. Обычно он запускается автоматически в фоновом режиме после установки. Чтобы проверить это, выполните:

```
lemonade status
```

Вы должны увидеть сообщение вроде: `Server is running on port 13305`.

Если сервер не запущен, запустите его, открыв приложение Lemonade. Используйте порт по умолчанию **13305** (его можно подтвердить или выбрать из значка в трее).

### Шаг 5: Установите клиент OpenAI Python

В терминале создайте venv и установите клиент OpenAI Python с помощью следующих команд:
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

### Шаг 6: Создайте приложение для карточек

Скачаем другую модель для генерации кода: `Qwen3.5-35B-A3B-GGUF`. Это большая (~20 ГБ) и производительная модель, которая лучше всего подходит для систем с 32 ГБ+ ОЗУ. Если у вас меньше доступной ОЗУ, попробуйте вместо неё `Qwen3.5-9B-GGUF` (~6 ГБ).

Скачать её можно из интерфейса или выполнив следующую команду:
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

Введите следующий запрос в чат Lemonade Chat UI, чтобы сгенерировать код простого приложения для карточек.

Мы будем использовать Qwen3.5-35B-A3B-GGUF (более крупную модель, лучше справляющуюся с написанием кода) для генерации нашего Python-приложения, а само приложение во время выполнения будет обращаться к Gemma-4-E2B-it-GGUF (меньшей модели, которую вы уже скачали). Затем код можно скопировать в файл по вашему выбору и запустить в Python.

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

> **Совет**: Мы следовали стандартным инженерным практикам благодаря тщательной проработке запроса и использованию системы с двумя моделями для оптимизации ресурсов и скорости.

Для вашего удобства мы предоставили пример вывода в файле [`flashcards.py`](assets/flashcards.py). Вы можете скачать его в свой каталог. В любом случае у вас теперь должен быть Python-файл, готовый к запуску.

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


### Шаг 7: Запустите сгенерированный код

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**Вот что вы должны увидеть:**

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

Всего примерно за 150 строк кода вы создали полностью функциональный инструмент для обучения на основе локальной LLM. Не нужно управлять API-ключом, нет расходов на использование, и никакие данные никогда не покидают вашу машину.

> **Ключевой момент:** Обратите внимание, что строка `client = OpenAI(base_url=...) ` — это *единственное*, что связывает это приложение с Lemonade вместо облака OpenAI. Остальной код полностью идентичен тому, что вы бы написали для любого сервиса, совместимого с OpenAI. Если вы когда-либо использовали библиотеку OpenAI Python, вы уже знаете, как создавать приложения с Lemonade.

### Что это демонстрирует

Это небольшое приложение демонстрирует несколько реальных паттернов интеграции:

| Паттерн | Где встречается |
|---------|-----------------|
| **Системные запросы** | Сообщение `"system"` указывает LLM выводить структурированный JSON |
| **Структурированный вывод** | Приложение анализирует ответ LLM как JSON для создания карточек |
| **Запросы без сохранения состояния** | Каждый вызов `generate_flashcards()` независим |
| **Обработка ошибок** | Конструкция `try/except` корректно обрабатывает случаи, когда вывод LLM не является допустимым JSON |

Эти же паттерны масштабируются на любые приложения, такие как чат-боты, помощники по коду, генераторы контента, инструменты автоматизации.

#### Дополнительное задание

* Для дополнительного вызова попробуйте обновить приложение так, чтобы карточки зачитывались пользователю, взяв за основу пример, приведённый [здесь](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py).

---

<!-- @device:halo_box,halo,stx,krk -->
## Запуск моделей на NPU (опционально)

Если у вас Ryzen AI 300/400/Max 300 series или Z2 Extreme, ваше устройство оснащено встроенным **Neural Processing Unit (NPU)** — специализированным чипом, разработанным специально для рабочих нагрузок ИИ. Запуск моделей на NPU более энергоэффективен, чем использование GPU, что делает его идеальным для фоновых задач ИИ, длительных сеансов работы и использования от батареи.

Lemonade поддерживает три режима выполнения на NPU, все они прозрачно работают через один и тот же OpenAI API:

| Режим | Как это работает | Рецепт | Примеры моделей |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | NPU обрабатывает промпт, iGPU генерирует токены | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **Только NPU** | Весь вывод выполняется на NPU | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | Использует движок FastFlowLM на NPU, оптимизированный для AMD XDNA2 | FLM (`flm`) | qwen3.5-4b-FLM |

### Требования

- Процессор **AMD Ryzen AI серии 300/400 или серии Z2**
- Для моделей **FLM**: среду выполнения FLM можно установить прямо из приложения Lemonade, либо Lemonade автоматически установит среду выполнения FLM при запуске модели FLM. Подробнее о FastFlowLM см. [здесь](https://fastflowlm.com/docs/).


### Шаг 8: Запуск гибридной модели

Гибридные модели распределяют работу между NPU и iGPU, обеспечивая хороший баланс между скоростью и эффективностью. В приложении Lemonade выберите модель из списка `Ryzen AI LLM`, например `Qwen3-4B-Hybrid`, или запустите её с помощью следующей команды:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade автоматически определяет ваш NPU и устанавливает бэкенд **Ryzen AI LLM**.

> **Что происходит «под капотом»?** Когда вы отправляете сообщение, NPU параллельно обрабатывает весь ваш промпт (это называется «prefill»). Затем iGPU берёт на себя генерацию ответа по одному токену за раз (это называется «decode»). Такой гибридный подход использует сильные стороны каждого чипа.

### Шаг 9: Запуск модели FLM

Модели FastFlowLM (FLM) специально оптимизированы для архитектуры NPU AMD XDNA2 и могут работать очень быстро для своего размера. Например, выберите `qwen3.5-4b-FLM` из списка `FastFlowLM NPU` или используйте следующую команду:

<!-- @os:windows -->
Чтобы включить `FastFlowLM` в Windows:

* Откройте меню `Backends Manager`.
* Найдите категорию бэкенда `FastFlowLM NPU`.
* Нажмите Install NPU.
* После завершения установки в выпадающем меню FFLM станет доступно около 36 моделей по умолчанию.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
При первом запуске приложения `Lemonade` бэкенд `FastFlowNPU` не включён по умолчанию.
Локальное приложение откроет страницу установки, чтобы провести вас через настройку.

Чтобы включить `FastFlowLM` в Linux:

* Откройте приложение `Lemonade`.
* Посетите [официальную документацию FLM](https://lemonade-server.ai/flm_npu_linux.html) и следуйте инструкциям по установке FLM, выбрав свой дистрибутив Linux.
* Включите backports, как указано на странице установки.
* Загрузите последний выпуск `v0.9.x` со [страницы тегов](https://github.com/FastFlowLM/FastFlowLM/tags).'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
Для AMD Halo Developer Platform обязательно выберите Debian 13.
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* Установите загруженный пакет `.deb`.
* Рекомендуется: закройте приложение `Lemonade App` и откройте его снова, чтобы изменения были обнаружены.
* Рекомендуется: откройте `Backends Manager` и нажмите Install `FastFlowNPU` Backend.
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
После успешной установки вы должны увидеть, что `flm:npu` завершён в **Download Manager** внутри **Lemonade Desktop App**.
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
После этого вы можете выбрать любую из доступных моделей FFLM и начать использовать бэкенд NPU.

Для конкретной модели скачайте нужную модель со [страницы моделей](https://fastflowlm.com/docs/models/qwen/) и проверьте её с помощью команды Shell, указанной в документации.
```
flm run qwen3.5-4b-FLM
```
или через 
```
lemonade run qwen3.5-4b-FLM
```

Модели FLM включают некоторые из самых популярных архитектур (Gemma 3, Qwen 3, Llama 3 и DeepSeek R1) и варьируются по размеру от менее 1 ГБ до более 13 ГБ.
Lemonade автоматически определяет ваш NPU и устанавливает бэкенд **FastFlowLM NPU**.

<!-- @os:windows -->
> **Совет:** Для максимальной производительности NPU включите режим turbo:
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### Переключение моделей

Приложение с флеш-карточками из шага 6 также работает с моделями на NPU, просто измените имя модели:

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## Дальнейшие шаги

У вас есть локальный сервер ИИ, работающий на вашем собственном оборудовании, вот куда двигаться дальше:

1. **Подключите ваши любимые приложения**: Lemonade работает «из коробки» с [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk), [Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/), [Continue](https://lemonade-server.ai/docs/server/apps/continue/), [n8n](https://n8n.io/integrations/lemonade-model/) и [многими другими](https://lemonade-server.ai/marketplace).

2. **Изучите больше моделей**: Ознакомьтесь с полной [библиотекой моделей](https://lemonade-server.ai/docs/server/server_models/), чтобы найти модели, оптимизированные для программирования, рассуждений, работы с изображениями и многого другого. Используйте приложение Lemonade или команду `lemonade list`, чтобы увидеть, что доступно.

3. **Разблокируйте ускорение GPU через ROCm**: Если у вас есть поддерживаемый GPU AMD, переключитесь на бэкенд ROCm: `lemonade config set llamacpp.backend=rocm`. См. [поддерживаемые GPU AMD](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations).

4. **Изучите полную спецификацию API**: Lemonade поддерживает завершение чата, эмбеддинги, транскрипцию аудио, генерацию изображений, преобразование текста в речь и многое другое. См. [спецификацию сервера](https://lemonade-server.ai/docs/server/server_spec/) для всех конечных точек.

5. **Внесите свой вклад**: Lemonade — это проект с открытым исходным кодом. Ознакомьтесь с [руководством по внесению вклада](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md) и найдите [подходящие для новичков задачи](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

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