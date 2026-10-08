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

LM Studio — это мощная графическая оболочка для [llama.cpp](https://github.com/ggml-org/llama.cpp), которая также предоставляет [совместимую с OpenAI конечную точку](https://lmstudio.ai/docs/developer/openai-compat) для локального обслуживания моделей. LM Studio предлагает простой, но мощный интерфейс для удобной загрузки и развёртывания моделей. Для пользователей AMD LM Studio предлагает как Vulkan, так и бэкенды AMD ROCm™ (называемые средами выполнения).


## Что вы узнаете
- Как настроить и использовать LM Studio для задействования вашего локального оборудования
- Как тестировать и управлять LLM в полностью автономной среде
- Как обслуживать модели через совместимый с OpenAI API для работы пользовательских рабочих процессов и приложений


<!-- @device:halo_box,halo,stx,krk -->
## Настройка конфигурации памяти

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Проверка обновлений ПО

<!-- @os:linux -->
> **Примечание**: VS Code можно установить через AMD Ryzen™ AI Developer Center. Для LM Studio следуйте приведённым ниже инструкциям по установке.
<!-- @os:end -->

<!-- @os:windows -->
> **Примечание**: Если VS Code или LM Studio не установлены, вы можете установить их из AMD Ryzen™ AI Developer Center. 
<!-- @os:end -->

<!-- @require:software-update -->
<!-- @device:end -->

## Установка необходимого ПО

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lmstudio -->
<!-- @prereq:lmstudio -->

## Загрузка моделей

<!-- @var:id=lms_model device=halo,halo_box value="gpt-oss-120b" -->
<!-- @var:id=lms_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="qwen3.5-9b" -->
<!-- @var:id=model_name device=halo,halo_box value="GPT-OSS 120B" -->
<!-- @var:id=model_name device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen3.5 9B" -->

<!-- @device:halo,halo_box -->
<!-- @require:lmstudio-models-gpt-oss-120b -->
<!-- @prereq:lmstudio-models-gpt-oss-120b -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @require:lmstudio-models-qwen3-9b -->
<!-- @prereq:lmstudio-models-qwen3-9b -->
<!-- @device:end -->

## Общение с LLM
Узнайте, как начать общение с LLM уровня ChatGPT полностью в локальной среде.  

1. Откройте LMStudio. 
2. Нажмите `Ctrl + L`, чтобы открыть загрузчик моделей, выберите `Manually choose model load parameters` и щёлкните по `${model_name}`
3. Убедитесь, что флажок «show advanced settings» установлен.  
4. Измените `Context Length` по желанию. Чем выше длина контекста, тем больше памяти требуется модели, но также возрастает расход системной памяти. Для данного руководства рекомендуется значение 4096.
5. Убедитесь, что `GPU Offload` установлен на максимум, а `Flash Attention` включён (Cache Quantizations можно оставить выключенным)
6. Установите флажок `Remember settings` и нажмите `Load Model`.
7. Если вы не находитесь в окне чата, нажмите `Ctrl + 1` или щёлкните по кнопке 👾 в левом верхнем углу экрана.
8. Отправьте сообщение и начните взаимодействовать с моделью!

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
<!-- @test:id=lmstudio-load-model-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "${lms_model}-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
# retry once: large-model loads can transiently fail under memory pressure
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y }
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
<!-- @test:id=lmstudio-load-model-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="${lms_model}-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
# retry once: large-model loads can transiently fail under memory pressure
lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load ${lms_model} --context-length 32768 --gpu max --identifier "$ID" -y; }
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

> **Совет**: длина контекста определяет «память» модели. Flash attention повышает скорость обработки, одновременно снижая расход памяти. GPU Offload переносит вычисления на видеокарту для более быстрых ответов.

## Обслуживание LLM через совместимую с OpenAI конечную точку

LM Studio также предлагает совместимую с OpenAI конечную точку в виде LM Studio Server. Это уже было продемонстрировано в рабочем процессе агентного программирования с Cline [здесь](../playbooks/vscode-qwen3-coder). Ещё один распространённый сценарий использования — подключение LM Studio Server к любому веб-приложению (React, Node.js, Python) путём отправки стандартных HTTP-запросов к конечной точке инференса.

Чтобы настроить LM Studio Server, воспользуйтесь следующими инструкциями:

1. С левой стороны щёлкните по вкладке `Developer` (значок командной строки) или нажмите `Ctrl + 2`, а затем щёлкните по `Server Settings`.  
2. (Необязательно): если вы хотите обслуживать модель в рамках вашей локальной сети, установите флажок `Serve on Local Network`. Если вы хотите использовать её с веб-сайтом или интенсивно вызывать из VS Code, установите флажок `Enable CORS`. 
3. В верхнем левом углу убедитесь, что сервер запущен, щёлкнув по переключателю напротив `Status`.
4. Теперь будет запущена совместимая с OpenAI конечная точка. Обычно её адрес — http://127.0.0.1:1234  
5. Если модель ещё не загружена, вы можете загрузить её, нажав `Load Model` и выполнив ранее описанные шаги. 

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


Теперь эта модель будет доступна через конечную точку LM Studio Server и будет поддерживать следующие конечные точки OpenAI:

| Конечная точка | Метод | Документация |
|------------|----------|----------|
| /v1/models | GET | [Models](https://lmstudio.ai/docs/developer/openai-compat/models) |
| /v1/responses | POST | [Responses](https://lmstudio.ai/docs/developer/openai-compat/responses) |
| /v1/chat/completions | POST |	[Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) |
| /v1/embeddings | POST | [Embeddings](https://lmstudio.ai/docs/developer/openai-compat/embeddings) |
| /v1/completions | POST | [Completions](https://lmstudio.ai/docs/developer/openai-compat/completions) |
#### Пример: пинг вашего эндпоинта
Только что создав эндпоинт, совместимый с OpenAI, давайте посмотрим, как интегрировать его в среду разработки Python (например, VSCode) и использовать вашу систему в качестве локального поставщика API.

1. Создайте виртуальное окружение Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
    В Linux откройте терминал в выбранном каталоге и выполните команды для создания venv.
    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv lmstudio-env --system-site-packages
    source lmstudio-env/bin/activate
    ```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Предоставьте вашему пользователю доступ к устройствам GPU** (для вступления изменений в силу выйдите из системы и войдите снова):

```bash
sudo usermod -aG render,video $LOGNAME
```

    В Linux откройте терминал в выбранном каталоге и выполните команды для создания venv.
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
    В Windows откройте терминал в выбранном каталоге и выполните команды для создания venv.
    ```bash
    python -m venv lmstudio-env --system-site-packages
    lmstudio-env\Scripts\activate
    ```

    > **Совет**: пользователям Windows может потребоваться изменить политику выполнения PowerShell (например,
    > установить значение RemoteSigned или Unrestricted) перед запуском некоторых команд PowerShell.

<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
    В Windows откройте терминал в выбранном каталоге и выполните команды для создания venv.
    ```bash
    python -m venv lmstudio-env
    lmstudio-env\Scripts\activate
    ```

    > **Совет**: пользователям Windows может потребоваться изменить политику выполнения PowerShell (например,
    > установить значение RemoteSigned или Unrestricted) перед запуском некоторых команд PowerShell.

<!-- @device:end -->
<!-- @os:end -->

2. Установите пакет OpenAI
    ```bash
    pip install openai
    ```

3. Запустите следующий скрипт, чтобы пропинговать только что созданный нами эндпоинт.
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

#### (Необязательно): переключение между средами выполнения (Runtimes)

1. Нажмите `Ctrl + Shift + R` на клавиатуре. Либо нажмите на вкладку `Discover` (значок лупы) слева, а затем нажмите `Runtime` во всплывающем окне.
2. После этого вы увидите `Runtime Selections`, где с помощью выпадающего меню можно изменить среду выполнения.


## Следующие шаги

- **Интеграция пользовательских приложений**: интегрируйте собственные скрипты или приложения Python, используя локальный API, совместимый с OpenAI.
- **Продвинутые интерфейсы**: подключите мощные интерфейсы, такие как Open WebUI, к вашему серверу для управления историей чатов и персонами.

Дополнительную документацию см. по адресу: https://lmstudio.ai/docs/developer