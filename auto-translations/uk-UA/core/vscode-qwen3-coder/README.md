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

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Цей посібник вимагає щонайменше **32 ГБ** системної пам'яті.
<!-- @device:end -->

## Огляд

Агенти з кодування — це потужні інструменти, які розширюють можливості розробників завдяки співпраці з AI-агентами на основі великих мовних моделей (LLM). Їх можна вбудовувати в середовище розробки, наприклад у термінал або VS Code, що дозволяє безперешкодно інтегрувати їх у робочий процес розробника.

У цьому підручнику показано, як використовувати Cline, VS Code та LM Studio для запуску агента з кодування повністю на вашому локальному комп'ютері.

## Що ви дізнаєтеся

* Як запустити VS Code з агентом з кодування Cline для допомоги у виконанні завдань програмної інженерії.
* Як налаштувати Cline для взаємодії з LM Studio для локального інференсу агентів з кодування.
* Як використовувати локальних агентів з кодування для вирішення реальних завдань програмної інженерії.

<!-- @device:halo_box,halo,stx,krk -->
## Налаштування конфігурації пам'яті

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Перевірка оновлень програмного забезпечення
> **Примітка**: Якщо VS Code не встановлено, ви можете встановити його за допомогою Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Встановлення необхідного програмного забезпечення

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lmstudio,vscode -->
<!-- @prereq:lmstudio-models-qwen3-coder-30b -->

## Запуск і налаштування LM Studio

Ми використаємо LM Studio для обслуговування LLM, що живить агента з кодування.

- У рядку пошуку знайдіть `LM Studio` і запустіть застосунок. Вас привітає наступна сторінка.

![Початковий екран LM Studio](assets/initial-lm-studio.png)

Далі нам потрібно завантажити LLM у систему. Ми будемо використовувати модель `Qwen3-Coder-30B-A3B` з великою довжиною контексту. (Використовуйте вкладку Model, щоб встановити її, якщо ви цього ще не зробили).
- Клацніть на рядок пошуку у верхній частині вікна LM Studio або натисніть `CTRL+L`. Клацніть перемикач `Manually choose model load parameters`, а потім клацніть на модель Qwen3-Coder-30B-A3B.
- Змініть довжину контексту з `4096` на `32768` і переконайтеся, що `GPU Offload` встановлено на максимум. Потім клацніть `Load Model`

![Вибір моделі](assets/model-list-zoomed.png)

Ми використовуємо велику довжину контексту, щоб агент міг обробляти великі кодові бази та пам'ятати внесені зміни.

![Налаштування моделі](assets/selecting-model-zoomed.png)

Далі нам потрібно увімкнути сервер LM Studio.
- Клацніть на вкладку Developer або натисніть `CTRL+2` у LM Studio зліва.
- Перевірте перемикач статусу та переконайтеся, що він встановлений на `Running`.

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
<!-- @test:id=lmstudio-select-gpu-runtime-windows timeout=120 hidden=True -->
```powershell
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
$rt = ((lms runtime ls) -match 'vulkan' | Select-Object -First 1)
if ($rt) {
  lms runtime select (($rt.Trim() -split '\s+')[0])
  lms runtime ls | Select-String 'ENGINE|✓'
} else {
  Write-Output "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y }
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-select-gpu-runtime-linux timeout=120 hidden=True -->
```bash
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
GPU_RT="$(lms runtime ls 2>/dev/null | awk '/vulkan/{print $1; exit}')"
if [ -n "$GPU_RT" ]; then
  lms runtime select "$GPU_RT"
  lms runtime ls | grep -E 'ENGINE|✓'
else
  echo "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
fi
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
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y; }
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## Запуск і налаштування VS Code

Ми встановимо розширення Cline у VS Code та підключимо його до сервера LM Studio, який ми щойно створили.
- У рядку пошуку знайдіть `VS Code` і запустіть застосунок.
- Клацніть на піктограму `Extensions` у лівій колонці VS Code та знайдіть `Cline`. Потім клацніть кнопку `Install`.

![Встановлення розширення Cline](assets/installing-cline-vscode-extension.png)

- Зліва має з'явитися піктограма Cline. Клацніть на неї, щоб відкрити Cline. З'явиться вікно з запитанням `How will you use Cline?`. Оскільки ми будемо використовувати локальну LLM, що працює через LM Studio, виберіть `Bring my own API Key` і натисніть `Continue`.

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

Далі нам потрібно налаштувати Cline для взаємодії з сервером LM Studio, який ми щойно налаштували.
- Встановіть API Provider на `LM Studio`, а модель на `Qwen3-Coder-30B-A3B-GGUF`.

>**Порада**: Можуть бути доступні новіші моделі. За бажанням розгляньте можливість завантаження та переходу на моделі Qwen3.6.


![Налаштування моделі](assets/cline-model-configuration-zoomed.png)

## Створення вашого першого проєкту

Використаємо нашого локального агента для створення вебсайту! Відкрийте VSCode у довільному каталозі, де Cline створюватиме файли.
- Для цього перейдіть до `File -> Open Folder` у верхньому лівому куті VS Code та оберіть папку, наприклад `Documents`.

![Порожня папка VS Code](assets/open-cline-test.png)

Тепер ми готові дати запит локальному агенту з кодування.
- Клацніть на розширення Cline у лівій колонці та введіть запит, щоб запустити агента. Наприклад, скористаймося таким запитом:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Потім агент почне створювати файли відповідно до запиту. Як користувач, ви можете спостерігати за генерацією коду у VS Code, як показано нижче. Можливо, вам доведеться клацати `Save` щоразу, коли Cline хоче створити файл.

![Генерація коду Cline](assets/cline-code-generation.png)

Після генерації програмного забезпечення агент завершує роботу, і ви можете запустити застосунок. У цьому випадку агент записав у три файли: `index.html`, `script.js` і `styles.css`. Просто двічі клацнувши на HTML-файл, ми можемо завантажити та взаємодіяти зі згенерованим вебсайтом.

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
        "max_tokens": 64
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
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
        "max_tokens": 64
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
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

Після створення вебсайту ви можете продовжити роботу з Cline для його вдосконалення. Два можливі покращення:

- **Документація**: Достатньо дати агенту запит `Add a README`, щоб він згенерував файл `README.md`, що документує вебсайт.
- **Анімація**: Дайте моделі запит `Add an animation that visually represents a large language model running on a laptop.`, щоб додати анімацію до вебсайту.

Ми заохочуємо читача спробувати створити інші застосунки за допомогою цього налаштування. Нижче наведено кілька цікавих прикладів, які ми спробували:

- **Ретро-аркадні ігри**: Спробуйте інші запити. Агенту також може бути цікаво створювати ретро-ігри на Python за допомогою пакета `PyGame` з таким запитом:

```code
Create a simple pong game using the PyGame python package.
```

- **Аналіз даних**: Однією з областей, де агенти з кодування особливо корисні, є написання скриптів і аналіз даних. Ось запит, що демонструє здатність локальної моделі генерувати програмне забезпечення для аналізу даних з візуалізації цін на акції:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Ресурси

Нижче наведено деякі додаткові ресурси, щоб дізнатися більше про Coding Agents, Cline та запуск робочих навантажень на 

* Додаткова інформація про партнерство та інтеграцію AMD LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* Блог AMD із покроковим описом запуску Cline на відеокартах AMD Ryzen™ AI та Radeon™: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Блог Cline про локальний запуск агентів кодування на ПК з ШІ: https://cline.bot/blog/local-models-amd