<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->

> [!IMPORTANT]
> Данное руководство использует специальные теги, которые GitHub не может отобразить. Пожалуйста, посетите [amd.com/playbooks](https://amd.com/playbooks) для корректного просмотра этого контента.
<!-- @github-only:end -->

## Обзор

LM Studio — это мощная обёртка с графическим интерфейсом для [llama.cpp](https://github.com/ggml-org/llama.cpp), которая также предоставляет [совместимую с OpenAI конечную точку](https://lmstudio.ai/docs/developer/openai-compat) для локального обслуживания моделей. LM Studio предлагает простой, но мощный интерфейс для лёгкой загрузки и развёртывания моделей. LM Studio предлагает как Vulkan, так и AMD ROCm™ бэкенды (называемые runtime) для пользователей AMD.


## Что вы узнаете
- Как настроить и использовать LM Studio для использования вашего локального оборудования
- Тестировать и управлять LLM в полностью автономной среде
- Обслуживать модели через API, совместимый с OpenAI, для работы пользовательских рабочих процессов и приложений


## Настройка конфигурации памяти

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Проверка обновлений программного обеспечения

<!-- @os:linux -->
> **Примечание**: Вы можете установить VS Code через AMD Ryzen™ AI Developer Center. Для LM Studio следуйте инструкциям по установке ниже.
<!-- @os:end -->

<!-- @os:windows -->
> **Примечание**: Если VS Code или LM Studio не установлены, вы можете установить их через AMD Ryzen™ AI Developer Center. 
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Установка необходимого программного обеспечения

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->

## Загрузка моделей

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

## Общение с LLM
Узнайте, как начать общаться с LLM уровня ChatGPT полностью локально.  

1. Откройте LMStudio. 
2. Нажмите `Ctrl + L`, чтобы открыть загрузчик моделей, выберите `Manually choose model load parameters` и нажмите на `${model_name}`
3. Убедитесь, что отмечен пункт "show advanced settings".  
4. Измените `Context Length` по желанию. Более высокая длина контекста означает больше памяти модели, но больше используемой системной памяти. Для этого руководства рекомендуется 4096.
5. Убедитесь, что `GPU Offload` установлен на максимум, а `Flash Attention` включён (Cache Quantizations можно оставить выключенным)
6. Отметьте `Remember settings` и нажмите на `Load Model`.
7. Если вы не в окне чата, нажмите `Ctrl + 1` или нажмите на кнопку 👾 в верхнем левом углу экрана.
8. Отправьте сообщение и начните взаимодействовать с моделью!

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

> **Совет**: Длина контекста относится к памяти модели. Flash attention повышает скорость обработки, снижая использование памяти. GPU Offload переносит вычисления на видеокарту для более быстрых ответов.

## Обслуживание LLM через конечную точку, совместимую с OpenAI

LM Studio также предлагает совместимую с OpenAI конечную точку в виде LM Studio Server. Это уже было продемонстрировано в агентском рабочем процессе программирования с Cline [здесь](../playbooks/vscode-qwen3-coder). Другой распространённый сценарий использования — подключение LM Studio Server к любому веб-приложению (React, Node.js, Python) путём отправки стандартных HTTP-запросов к конечной точке вывода.

Чтобы настроить LM Studio Server, используйте следующие инструкции:

1. С левой стороны нажмите на вкладку `Developer` (значок командной строки) или `Ctrl + 2`, а затем нажмите на `Server Settings`.  
2. (Необязательно): Если вы хотите обслуживать модель по вашей локальной сети, отметьте `Serve on Local Network`. Если вы хотите использовать её с веб-сайтом или для расширенных вызовов внутри VS Code, отметьте `Enable CORS`. 
3. В верхнем левом углу убедитесь, что сервер запущен, нажав на переключатель перед `Status`.
4. Теперь будет запущена конечная точка, совместимая с OpenAI. Адрес обычно http://127.0.0.1:1234  
5. Если модель ещё не загружена, вы можете загрузить её, нажав `Load Model` и следуя ранее указанным шагам. 

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


Теперь эта модель будет доступна через конечную точку LM Studio Server и будет поддерживать конечные точки OpenAI, включая:

| Endpoint | Method | Docs |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### Пример: проверка связи с эндпоинтом
Только что создав OpenAI-совместимый эндпоинт, давайте посмотрим, как интегрировать его в среду разработки Python (например, VSCode) и использовать вашу систему в качестве локального API-провайдера.

1. Создайте виртуальное окружение Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
    В Linux откройте терминал в выбранном каталоге и выполните следующие команды для создания venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Предоставьте своему пользователю доступ к устройствам GPU** (для вступления изменений в силу выйдите из системы и войдите снова):

```bash
sudo usermod -aG render,video $LOGNAME
```

    В Linux откройте терминал в выбранном каталоге и выполните следующие команды для создания venv.
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
    В Windows откройте терминал в выбранном каталоге и выполните следующие команды для создания venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Совет**: пользователям Windows может потребоваться изменить политику выполнения PowerShell (например,
    > установить значение RemoteSigned или Unrestricted) перед выполнением некоторых команд PowerShell.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    В Windows откройте терминал в выбранном каталоге и выполните следующие команды для создания venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Совет**: пользователям Windows может потребоваться изменить политику выполнения PowerShell (например,
    > установить значение RemoteSigned или Unrestricted) перед выполнением некоторых команд PowerShell.

<!-- @device:end -->
<!-- @os:end -->

2. Установите пакет OpenAI
    ```bash
    pip install openai
    ```

3. Выполните следующий скрипт, чтобы проверить связь с только что созданным эндпоинтом.
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

#### (Необязательно): переключение между средами выполнения

1. Нажмите `Ctrl + Shift + R` на клавиатуре. Либо нажмите на вкладку `Discover` (значок лупы) в левой части экрана, а затем нажмите `Runtime` во всплывающем окне.
2. После этого вы увидите раздел `Runtime Selections`, где с помощью раскрывающегося меню можно изменить среду выполнения.


## Дальнейшие шаги

- **Интеграция собственных приложений**: интегрируйте собственные скрипты или приложения на Python, используя локальный OpenAI-совместимый API.
- **Расширенные интерфейсы**: подключите мощные интерфейсы, такие как Open WebUI, к своему серверу для управления историей чата и профилями.

Дополнительную документацию можно найти по адресу: https://lmstudio.ai/docs/developer