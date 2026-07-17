<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Огляд

LM Studio — це потужна GUI-оболонка для [llama.cpp](https://github.com/ggml-org/llama.cpp), яка також надає [сумісний з OpenAI ендпоінт](https://lmstudio.ai/docs/developer/openai-compat) для локального обслуговування моделей. LM Studio пропонує простий, але потужний інтерфейс для легкого завантаження та розгортання моделей. Для користувачів AMD LM Studio надає бекенди (так звані середовища виконання) Vulkan та AMD ROCm™.


## Що ви дізнаєтесь
- Як налаштувати та використовувати LM Studio для роботи з локальним обладнанням
- Тестувати та керувати LLM у повністю автономному середовищі
- Обслуговувати моделі через сумісний з OpenAI API для власних робочих процесів і застосунків


## Налаштування конфігурації пам'яті

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Перевірка оновлень програмного забезпечення

<!-- @os:linux -->
> **Примітка**: Ви можете встановити VS Code через AMD Ryzen™ AI Developer Center. Для LM Studio дотримуйтесь інструкцій із встановлення нижче.
<!-- @os:end -->

<!-- @os:windows -->
> **Примітка**: Якщо VS Code або LM Studio не встановлено, ви можете встановити їх з AMD Ryzen™ AI Developer Center.
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Встановлення необхідного програмного забезпечення

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## Завантаження моделей

<!-- @var:id=lms_model device=halo,halo_box value="gpt-oss-120b" -->
<!-- @var:id=lms_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="qwen3.5-9b" -->
<!-- @var:id=model_name device=halo,halo_box value="GPT-OSS 120B" -->
<!-- @var:id=model_name device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen3.5 9B" -->

<!-- @device:halo,halo_box -->
<!-- @require:lmstudio-models-gpt-oss-120b -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @require:lmstudio-models-qwen3-9b -->
<!-- @device:end -->

## Спілкування з LLM
Дізнайтеся, як розпочати спілкування з LLM рівня ChatGPT повністю локально.

1. Відкрийте LMStudio.
2. Натисніть `Ctrl + L`, щоб відкрити завантажувач моделей, виберіть `Manually choose model load parameters` і натисніть на `${model_name}`
3. Переконайтеся, що встановлено прапорець "show advanced settings".
4. Змініть `Context Length` за потреби. Більша довжина контексту означає більше пам'яті для моделі, але більше використання системної пам'яті. Для цього посібника рекомендується значення 4096.
5. Переконайтеся, що `GPU Offload` встановлено на максимум, а `Flash Attention` увімкнено (Cache Quantizations можна залишити вимкненим).
6. Встановіть прапорець `Remember settings` і натисніть `Load Model`.
7. Якщо ви не у вікні чату, натисніть `Ctrl + 1` або клацніть кнопку 👾 у верхньому лівому куті екрана.
8. Надішліть повідомлення та почніть взаємодіяти з моделлю!

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-model-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "${lms_model}-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-model-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="${lms_model}-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<p align="center">
  <img src="assets/chat.png" alt="Chatting with ${model_name} on LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<p align="center">
  <img src="assets/chat_qwen.png" alt="Chatting with ${model_name} on LM Studio" width="600"/>
</p>
<!-- @device:end -->

> **Порада**: Довжина контексту — це пам'ять моделі. Flash attention підвищує швидкість обробки, зменшуючи використання пам'яті. GPU Offload переносить обчислення на відеокарту для швидших відповідей.

## Обслуговування LLM через сумісний з OpenAI ендпоінт

LM Studio також пропонує сумісний з OpenAI ендпоінт у вигляді LM Studio Server. Це вже було продемонстровано в агентному робочому процесі кодування з Cline [тут](../playbooks/vscode-qwen3-coder). Ще одним поширеним варіантом використання є підключення LM Studio Server до будь-якого вебзастосунку (React, Node.js, Python) шляхом надсилання стандартних HTTP-запитів до ендпоінту виведення.

Щоб налаштувати LM Studio Server, дотримуйтесь наступних інструкцій:

1. На лівій панелі натисніть на вкладку `Developer` (іконка командного рядка) або `Ctrl + 2`, а потім натисніть `Server Settings`.
2. (Необов'язково): Якщо ви хочете обслуговувати модель у локальній мережі, встановіть прапорець `Serve on Local Network`. Якщо ви хочете використовувати з вебсайтом або інтенсивними викликами у VS Code, встановіть прапорець `Enable CORS`.
3. У верхньому лівому куті переконайтеся, що сервер запущено, натиснувши перемикач поруч із `Status`.
4. Тепер буде запущено сумісний з OpenAI ендпоінт. Адреса зазвичай: http://127.0.0.1:1234
5. Якщо модель ще не завантажено, ви можете завантажити її, натиснувши `Load Model` і виконавши раніше описані кроки.

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


Ця модель тепер буде доступна через ендпоінт LM Studio Server і підтримуватиме ендпоінти OpenAI, зокрема:

| Ендпоінт | Метод | Документація |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST | [Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |


#### Приклад: Перевірка ендпоінту
Щойно створивши сумісний з OpenAI ендпоінт, розглянемо, як інтегрувати його в середовище розробника Python (наприклад, VSCode) і використовувати вашу систему як локального постачальника API.

1. Створіть віртуальне середовище Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
    На Linux відкрийте термінал у потрібній директорії та виконайте команди для створення venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Надайте вашому користувачу доступ до пристроїв GPU** (вийдіть із системи та увійдіть знову, щоб зміни набули чинності):

```bash
sudo usermod -aG render,video $LOGNAME
```

    На Linux відкрийте термінал у потрібній директорії та виконайте команди для створення venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
    На Windows відкрийте термінал у потрібній директорії та виконайте команди для створення venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Порада**: Користувачам Windows може знадобитися змінити політику виконання PowerShell (наприклад,
    > встановити її на RemoteSigned або Unrestricted) перед виконанням деяких команд Powershell.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    На Windows відкрийте термінал у потрібній директорії та виконайте команди для створення venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Порада**: Користувачам Windows може знадобитися змінити політику виконання PowerShell (наприклад,
    > встановити її на RemoteSigned або Unrestricted) перед виконанням деяких команд Powershell.

<!-- @device:end -->
<!-- @os:end -->

2. Встановіть пакет OpenAI
    ```bash
    pip install openai
    ```

3. Запустіть наступний скрипт для перевірки щойно створеного ендпоінту.
    ```python
    from openai import OpenAI

    # Initialize the client specifically for your local server
    # The API key is required by the library but ignored by LM Studio
    client = OpenAI(
        base_url="http://localhost:1234/v1", 
        api_key="lm-studio"
    )
    print("Attempting to connect to local LM Studio server...")

    try:
        # Create a simple chat completion request
        completion = client.chat.completions.create(
            model="local-model", # The model identifier is optional in local mode
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": "Explain Python decorators in 1 sentence"}
            ],
            temperature=0.7,
        )
        # Print the response
        print("\nConnection Successful! Server Response:\n")
        print(completion.choices[0].message.content)

    except Exception as e:
        print(f"\nConnection Failed: {e}. Ensure LM Studio server is running on port 1234.")
    ```
<!-- @os:windows -->
<!-- @test:id=lmstudio-ping-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
 "http://127.0.0.1:1234/v1/chat/completions",
 data=json.dumps({
   "model": model_id,
   "messages": [{"role":"user","content":"What is 2 + 2? Reply with only the number."}],
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
<!-- @test:id=lmstudio-ping-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request

with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
 "http://127.0.0.1:1234/v1/chat/completions",
 data=json.dumps({
   "model": model_id,
   "messages": [{"role":"user","content":"What is 47 + 42? Reply with only the number in words."}],
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

#### (Необов'язково): Перемикання між середовищами виконання

1. Натисніть `Ctrl + Shift + R` на клавіатурі. Або натисніть на вкладку `Discover` (іконка лупи) на лівій панелі, а потім натисніть `Runtime` у спливаючому вікні.
2. Ви побачите `Runtime Selections`, де за допомогою випадаючого меню можна змінити середовище виконання.


## Наступні кроки

- **Інтеграція власних застосунків**: Інтегруйте власні скрипти або застосунки Python за допомогою локального сумісного з OpenAI API.
- **Розширені інтерфейси**: Підключіть потужні інтерфейси, як-от Open WebUI, до вашого сервера для керування історією чату та персонажами.

Для отримання додаткової документації відвідайте: https://lmstudio.ai/docs/developer