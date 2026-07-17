<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> This playbook requires a minimum of **32GB** of system memory.
<!-- @device:end -->

## Огляд

Агенти для написання коду — це потужні інструменти, що розширюють можливості розробників завдяки співпраці з агентами штучного інтелекту на основі великих мовних моделей (LLM). Їх можна вбудовувати у середовище розробки, наприклад у термінал або VS Code, що забезпечує безперешкодну інтеграцію у робочий процес розробника.

У цьому посібнику демонструється, як використовувати Cline, VS Code та LM Studio для запуску агента написання коду повністю на локальній машині.

## Що ви дізнаєтесь

* Як запустити VS Code з агентом написання коду Cline для допомоги у завданнях з розробки програмного забезпечення.
* Як налаштувати Cline для взаємодії з LM Studio для локального виведення агентів написання коду.
* Як використовувати локальні агенти написання коду для вирішення реальних завдань з розробки програмного забезпечення.

## Налаштування конфігурації пам'яті

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Перевірка оновлень програмного забезпечення
> **Примітка**: Якщо VS Code не встановлено, його можна встановити за допомогою Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Встановлення необхідного програмного забезпечення

<!-- @require:lmstudio,vscode -->

## Запуск та налаштування LM Studio

Ми будемо використовувати LM Studio для обслуговування LLM, що керує агентом написання коду.

- У рядку пошуку знайдіть `LM Studio` та запустіть застосунок. Вас зустріне наступна сторінка.

![Початковий екран LM Studio](assets/initial-lm-studio.png)

Далі необхідно завантажити LLM у систему. Ми будемо використовувати модель `Qwen3-Coder-30B-A3B` з великою довжиною контексту. (Скористайтеся вкладкою Model для встановлення, якщо ви ще цього не зробили).
- Натисніть на рядок пошуку у верхній частині вікна LM Studio або натисніть `CTRL+L`. Натисніть перемикач `Manually choose model load parameters`, а потім виберіть модель Qwen3-Coder-30B-A3B.
- Змініть довжину контексту з `4096` на `32768` та переконайтеся, що `GPU Offload` встановлено на максимум. Потім натисніть `Load Model`.

![Вибір моделі](assets/model-list-zoomed.png)

Ми використовуємо велику довжину контексту, щоб агент міг обробляти великі кодові бази та запам'ятовувати внесені зміни.

![Налаштування моделі](assets/selecting-model-zoomed.png)

Далі необхідно увімкнути сервер LM Studio.
- Натисніть вкладку Developer або натисніть `CTRL+2` у LM Studio зліва.
- Перевірте перемикач стану та переконайтеся, що він встановлений у положення `Running`.

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-up-windows timeout=120 hidden=True -->
```powershell
lms server start --port 1234
curl.exe -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-up-linux timeout=120 hidden=True -->
```bash
lms server start --port 1234
curl -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

![Статус сервера](assets/lm-studio-server-status.png)

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-qwen3-coder-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="qwen3coder-32k-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## Запуск та налаштування VS Code

Ми встановимо розширення Cline у VS Code та підключимо його до щойно створеного сервера LM Studio.
- У рядку пошуку знайдіть `VS Code` та запустіть застосунок.
- Натисніть на значок `Extensions` у лівій колонці VS Code та знайдіть `Cline`. Потім натисніть кнопку `Install`.

![Встановлення розширення Cline](assets/installing-cline-vscode-extension.png)

- Зліва має з'явитися значок Cline. Натисніть на нього, щоб відкрити Cline. З'явиться вікно із запитанням `How will you use Cline?` Оскільки ми будемо використовувати локальну LLM, що працює через LM Studio, виберіть `Bring my own API Key` та натисніть `Continue`.

<!-- @os:windows -->
<!-- @test:id=cline-install-and-verify-windows timeout=300 hidden=True -->
```powershell
code --install-extension saoudrizwan.claude-dev
code --list-extensions | Select-String -Pattern "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=cline-install-and-verify-linux timeout=300 hidden=True -->
```bash
code --install-extension saoudrizwan.claude-dev
code --list-extensions | grep -i "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

![Створення облікового запису](assets/cline-how-will-you-use-cline-zoomed.png)

Далі необхідно налаштувати Cline для взаємодії з сервером LM Studio, який ми налаштували.
- Встановіть API Provider на `LM Studio`, а модель — на `Qwen3-Coder-30B-A3B-GGUF`.

>**Порада**: Можуть бути доступні новіші моделі. За бажанням розгляньте можливість завантаження та переходу на моделі Qwen3.6.


![Налаштування моделі](assets/cline-model-configuration-zoomed.png)

## Створення вашого першого проєкту

Давайте використаємо наш локальний агент для створення вебсайту! Відкрийте VSCode у будь-якій директорії на ваш вибір, де Cline створюватиме файли.
- Для цього перейдіть до `File -> Open Folder` у верхньому лівому куті VS Code та виберіть папку, наприклад `Documents`.

![Порожня папка VS Code](assets/open-cline-test.png)

Тепер ми готові надати запит локальному агенту написання коду.
- Натисніть на розширення Cline у лівій колонці та введіть запит для запуску агента. Як приклад, скористаємося наступним запитом:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Після цього агент почне створювати файли відповідно до запиту. Як користувач, ви можете спостерігати за генерацією коду у VS Code, як показано нижче. Можливо, вам доведеться натискати `Save` кожного разу, коли Cline захоче створити файл.

![Генерація коду Cline](assets/cline-code-generation.png)

Після генерації програмного забезпечення агент завершує роботу, і ви можете запустити застосунок. У цьому випадку агент записав три файли: `index.html`, `script.js` та `styles.css`. Просто двічі клацнувши на HTML-файлі, ми можемо завантажити та взаємодіяти зі згенерованим вебсайтом.

<!-- @os:windows -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request
with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()
req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-stop-windows timeout=300 hidden=True -->
```powershell
$ID = Get-Content "$env:TEMP\lmstudio_model_id.txt" -Raw
$ID = $ID.Trim()
lms unload "$ID"
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-stop-linux timeout=300 hidden=True -->
```bash
ID="$(cat /tmp/lmstudio_model_id.txt)"
lms unload "$ID" || true
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

## Наступні кроки

Після генерації вебсайту ви можете продовжити роботу з Cline для його вдосконалення. Два можливих покращення:

- **Документація**: Запит до агента `Add a README` — це все, що потрібно для того, щоб агент згенерував файл `README.md` з документацією до вебсайту.
- **Анімація**: Надайте моделі запит `Add an animation that visually represents a large language model running on a laptop.`, щоб додати анімацію до вебсайту.

Ми заохочуємо читача спробувати генерувати інші застосунки за допомогою цього налаштування. Нижче наведено кілька цікавих прикладів, які ми випробували:

- **Ретро аркадні ігри**: Спробуйте інші запити. Також може бути цікаво попросити агента створити ретро-ігри на Python з використанням пакету `PyGame` за допомогою наступного запиту:

```code
Create a simple pong game using the PyGame python package.
```

- **Аналіз даних**: Одна з областей, де агенти написання коду особливо корисні, — це написання скриптів та аналіз даних. Ось запит для демонстрації здатності локальної моделі генерувати програмне забезпечення для аналізу даних з візуалізацією цін на акції:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Ресурси

Нижче наведено додаткові ресурси для отримання додаткової інформації про агентів написання коду, Cline та запуск робочих навантажень на

* Додаткова інформація про партнерство та інтеграцію AMD з LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* Блог AMD з покроковим описом запуску Cline на AMD Ryzen™ AI та Radeon™ Graphics Cards: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Блог Cline про запуск агентів написання коду локально на AI PC: https://cline.bot/blog/local-models-amd