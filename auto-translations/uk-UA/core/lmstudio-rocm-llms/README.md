<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Цей посібник використовує спеціальні теги, які GitHub не може відобразити. Будь ласка, відвідайте [amd.com/playbooks](https://amd.com/playbooks), щоб коректно переглянути цей вміст.
<!-- @github-only:end -->

## Огляд

LM Studio — це потужна обгортка з графічним інтерфейсом для [llama.cpp](https://github.com/ggml-org/llama.cpp), яка також надає [сумісну з OpenAI кінцеву точку](https://lmstudio.ai/docs/developer/openai-compat) для локального обслуговування моделей. LM Studio пропонує простий, але потужний інтерфейс для легкого завантаження та розгортання моделей. LM Studio пропонує бекенди (які називаються середовищами виконання) Vulkan та AMD ROCm™ для користувачів AMD.


## Що ви дізнаєтесь
- Як налаштувати та використовувати LM Studio для використання вашого локального обладнання
- Тестувати та керувати LLM у повністю офлайн-середовищі
- Обслуговувати моделі через сумісний з OpenAI API для роботи власних робочих процесів і застосунків


## Налаштування конфігурації пам'яті

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Перевірка оновлень програмного забезпечення

<!-- @os:linux -->
> **Примітка**: Ви можете встановити VS Code через AMD Ryzen™ AI Developer Center. Для LM Studio дотримуйтесь інструкцій зі встановлення нижче.
<!-- @os:end -->

<!-- @os:windows -->
> **Примітка**: Якщо VS Code або LM Studio не встановлено, ви можете встановити їх через AMD Ryzen™ AI Developer Center. 
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
Дізнайтеся, як почати спілкуватися з LLM рівня ChatGPT повністю локально.  

1. Відкрийте LMStudio. 
2. Натисніть `Ctrl + L`, щоб відкрити завантажувач моделей, виберіть `Manually choose model load parameters` і клацніть на `${model_name}`
3. Переконайтеся, що позначено "show advanced settings".  
4. Змініть `Context Length` за бажанням. Більша довжина контексту означає більше використання пам'яті моделі, але й більше використання системної пам'яті. Для цього посібника рекомендовано 4096.
5. Переконайтеся, що `GPU Offload` встановлено на максимум, а `Flash Attention` увімкнено (Cache Quantizations можна залишити вимкненим)
6. Позначте `Remember settings` і клацніть на `Load Model`.
7. Якщо ви не в чат-вікні, натисніть `Ctrl + 1` або клацніть на кнопку 👾 у верхньому лівому куті екрана.
8. Надішліть повідомлення та почніть взаємодію з моделлю!

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

> **Порада**: Довжина контексту означає пам'ять моделі. Flash attention покращує швидкість обробки, зменшуючи використання пам'яті. GPU Offload перекладає обчислення на графічну карту для швидших відповідей.

## Обслуговування LLM через сумісну з OpenAI кінцеву точку

LM Studio також пропонує сумісну з OpenAI кінцеву точку у вигляді LM Studio Server. Це вже було продемонстровано в агентному робочому процесі кодування з Cline [тут](../playbooks/vscode-qwen3-coder). Інший поширений випадок використання — підключення LM Studio Server до будь-якого веб-застосунку (React, Node.js, Python) шляхом надсилання стандартних HTTP-запитів до кінцевої точки інференсу.

Щоб налаштувати LM Studio Server, скористайтеся наступними інструкціями:

1. Ліворуч клацніть на вкладку `Developer` (іконка командного рядка) або натисніть `Ctrl + 2`, а потім клацніть на `Server Settings`.  
2. (Необов'язково): Якщо ви хочете обслуговувати модель у своїй локальній мережі, позначте `Serve on Local Network`. Якщо ви хочете використовувати з вебсайтом або широким викликом у VS Code, позначте `Enable CORS`. 
3. У верхньому лівому куті переконайтеся, що сервер запущено, клацнувши на перемикач біля `Status`.
4. Тепер буде запущено сумісну з OpenAI кінцеву точку. Адреса зазвичай http://127.0.0.1:1234  
5. Якщо модель ще не завантажена, ви можете завантажити її, клацнувши `Load Model` та виконавши раніше згадані кроки. 

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


Ця модель тепер буде доступна через кінцеву точку LM Studio Server і підтримуватиме кінцеві точки OpenAI, зокрема:

| Кінцева точка | Метод | Документація |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### Приклад: перевірка зʼєднання з ендпоінтом
Щойно створивши OpenAI-сумісний ендпоінт, розгляньмо, як інтегрувати його в середовище розробки Python (наприклад, VSCode) і використовувати вашу систему як локального постачальника API.

1. Створіть віртуальне середовище Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
    У Linux відкрийте термінал у потрібному каталозі та виконайте наведені команди для створення venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Надайте вашому користувачу доступ до пристроїв GPU** (щоб зміни набули чинності, вийдіть із системи та увійдіть знову):

```bash
sudo usermod -aG render,video $LOGNAME
```

    У Linux відкрийте термінал у потрібному каталозі та виконайте наведені команди для створення venv.
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
    У Windows відкрийте термінал у потрібному каталозі та виконайте наведені команди для створення venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Порада**: користувачам Windows може знадобитися змінити політику виконання PowerShell (наприклад,
    > встановивши значення RemoteSigned або Unrestricted) перед виконанням деяких команд PowerShell.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    У Windows відкрийте термінал у потрібному каталозі та виконайте наведені команди для створення venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Порада**: користувачам Windows може знадобитися змінити політику виконання PowerShell (наприклад,
    > встановивши значення RemoteSigned або Unrestricted) перед виконанням деяких команд PowerShell.

<!-- @device:end -->
<!-- @os:end -->

2. Встановіть пакет OpenAI
    ```bash
    pip install openai
    ```

3. Запустіть наступний скрипт, щоб перевірити зʼєднання зі щойно створеним ендпоінтом.
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

#### (Необовʼязково): перемикання між середовищами виконання

1. Натисніть `Ctrl + Shift + R` на клавіатурі. Або натисніть на вкладку `Discover` (значок лупи) ліворуч, а потім клацніть `Runtime` у спливному вікні.
2. Ви побачите `Runtime Selections`, де за допомогою випадного меню можна змінити середовище виконання.


## Наступні кроки

- **Інтеграція власних застосунків**: інтегруйте власні скрипти або застосунки Python за допомогою локального OpenAI-сумісного API.
- **Розширені фронтенди**: підключіть потужні інтерфейси, такі як Open WebUI, до вашого сервера для роботи з історією чату та керування персонами.

Додаткову документацію можна знайти за посиланням: https://lmstudio.ai/docs/developer