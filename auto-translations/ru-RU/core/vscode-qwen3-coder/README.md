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

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Для этого руководства требуется минимум **32 ГБ** оперативной памяти системы.
<!-- @device:end -->

## Обзор

Агенты программирования — это мощные инструменты, которые расширяют возможности разработчиков благодаря совместной работе с ИИ-агентами на базе больших языковых моделей (LLM). Их можно встраивать прямо в среду разработки, например в терминал или VS Code, обеспечивая бесшовную интеграцию в рабочий процесс разработчика.

В этом руководстве показано, как использовать Cline, VS Code и LM Studio для запуска агента программирования полностью на локальном компьютере.

## Что вы узнаете

* Как запустить VS Code с агентом программирования Cline для помощи в задачах разработки ПО.
* Как настроить Cline для взаимодействия с LM Studio для локального инференса агентов программирования.
* Как использовать локальных агентов программирования для решения реальных задач разработки ПО.

<!-- @device:halo_box,halo,stx,krk -->
## Настройка конфигурации памяти

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Проверка обновлений ПО
> **Примечание**: Если VS Code не установлен, вы можете установить его с помощью Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Установка необходимого ПО

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lmstudio,vscode -->
<!-- @prereq:lmstudio-models-qwen3-coder-30b -->

## Запуск и настройка LM Studio

Мы будем использовать LM Studio для обслуживания LLM, которая обеспечивает работу агента программирования.

- В строке поиска введите `LM Studio` и запустите приложение. Вы увидите следующую страницу.

![Начальный экран LM Studio](assets/initial-lm-studio.png)

Далее нам нужно загрузить LLM в систему. Мы будем использовать модель `Qwen3-Coder-30B-A3B` с большой длиной контекста. (Используйте вкладку Model, чтобы установить её, если вы ещё этого не сделали).
- Нажмите на строку поиска в верхней части окна LM Studio или нажмите `CTRL+L`. Нажмите переключатель `Manually choose model load parameters`, а затем выберите модель Qwen3-Coder-30B-A3B.
- Измените длину контекста с `4096` на `32768` и убедитесь, что `GPU Offload` установлен на максимум. Затем нажмите `Load Model`

![Выбор модели](assets/model-list-zoomed.png)

Мы используем большую длину контекста, чтобы агент мог обрабатывать большие кодовые базы и помнить внесённые изменения.

![Настройка модели](assets/selecting-model-zoomed.png)

Далее нам нужно включить сервер LM Studio.
- Нажмите вкладку Developer или нажмите `CTRL+2` в LM Studio слева.
- Проверьте переключатель статуса и убедитесь, что он установлен в `Running`.

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

## Запуск и настройка VS Code

Мы установим расширение Cline в VS Code и подключим его к серверу LM Studio, который мы только что создали.
- В строке поиска введите `VS Code` и запустите приложение.
- Нажмите на значок `Extensions` в левой колонке VS Code и найдите `Cline`. Затем нажмите кнопку `Install`.

![Установка расширения Cline](assets/installing-cline-vscode-extension.png)

- Слева должен появиться значок Cline. Нажмите на него, чтобы открыть Cline. Появится окно с вопросом `How will you use Cline?` Поскольку мы будем использовать локальную LLM, работающую через LM Studio, выберите `Bring my own API Key` и нажмите `Continue`.

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

![Создание учётной записи](assets/cline-how-will-you-use-cline-zoomed.png)

Далее нам нужно настроить Cline для взаимодействия с сервером LM Studio, который мы настроили.
- Установите API Provider на `LM Studio`, а модель на `Qwen3-Coder-30B-A3B-GGUF`.

>**Совет**: Могут быть доступны более новые модели. При желании рассмотрите возможность загрузки и переключения на модели Qwen3.6.


![Настройка модели](assets/cline-model-configuration-zoomed.png)

## Создание вашего первого проекта

Давайте используем нашего локального агента для создания веб-сайта! Откройте VSCode в папке по вашему выбору, где Cline создаст файлы.
- Для этого перейдите в `File -> Open Folder` в верхнем левом углу VS Code и выберите папку, например `Documents`.

![Пустая папка VS Code](assets/open-cline-test.png)

Теперь мы готовы отправить запрос локальному агенту программирования.
- Нажмите на расширение Cline в левой колонке и введите запрос, чтобы запустить агента. В качестве примера воспользуемся следующим запросом:
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

Затем агент начнёт создавать файлы в соответствии с запросом. Как пользователь, вы можете наблюдать за генерацией кода в VS Code, как показано ниже. Возможно, вам потребуется нажимать `Save` каждый раз, когда Cline захочет создать файл.

![Генерация кода Cline](assets/cline-code-generation.png)

После генерации ПО работа агента завершена, и вы можете запустить приложение. В данном случае агент записал три файла: `index.html`, `script.js` и `styles.css`. Просто дважды щёлкнув по HTML-файлу, мы можем загрузить сгенерированный веб-сайт и взаимодействовать с ним.

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

## Дальнейшие шаги

После создания веб-сайта вы можете продолжить работу с Cline, чтобы улучшить его. Вот два возможных улучшения:

- **Документация**: Достаточно отправить агенту запрос `Add a README`, чтобы агент сгенерировал файл `README.md`, документирующий веб-сайт.
- **Анимация**: Отправьте модели запрос `Add an animation that visually represents a large language model running on a laptop.`, чтобы добавить на сайт анимацию.

Мы призываем читателя попробовать сгенерировать другие приложения, используя эту настройку. Ниже приведены несколько интересных примеров, которые мы опробовали:

- **Ретро-аркадные игры**: Попробуйте другие запросы. Агенту также может быть интересно создавать ретро-игры на Python с использованием пакета `PyGame` по следующему запросу:

```code
Create a simple pong game using the PyGame python package.
```

- **Анализ данных**: Одна из областей, где агенты программирования особенно полезны, — это написание скриптов и анализ данных. Вот запрос, демонстрирующий способность локальной модели генерировать ПО для анализа данных для визуализации цен на акции:

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## Ресурсы

Ниже приведены дополнительные ресурсы, где можно узнать больше о кодирующих агентах, Cline и запуске рабочих нагрузок на 

* Дополнительная информация о партнёрстве и интеграции AMD с LM Studio: https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* Блог AMD с описанием запуска Cline на видеокартах AMD Ryzen™ AI и Radeon™: https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Блог Cline о локальном запуске кодирующих агентов на AI ПК: https://cline.bot/blog/local-models-amd