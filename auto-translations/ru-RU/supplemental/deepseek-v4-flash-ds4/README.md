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

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) — это ориентированный на эффективность вариант семейства DeepSeek V4 — модель Mixture of Experts с 284 миллиардами параметров и 13 миллиардами активных параметров. Согласно [техническому отчёту DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash), она набирает 79% на SWE-bench Verified и 91.6% на LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) — это специализированный движок вывода, созданный именно для этой архитектуры модели. Вместо универсального рантайма ds4 нацелен непосредственно на семейство DeepSeek V4, используя оптимизации ядер, специфичные для архитектуры, для AMD ROCm™ software. В настоящее время это одна из наиболее производительных реализаций DeepSeek V4 Flash на Strix Halo.

В этом руководстве показано, как использовать `ds4-cockpit`, терминальный интерфейс, для настройки ds4, загрузки весов модели и запуска локального обслуживания DeepSeek V4 Flash на платформе AMD Ryzen™ AI Halo Developer Platform.

## Чему вы научитесь

- Как установить и запустить терминальный интерфейс `ds4-cockpit`
- Как создать контейнер-тулбокс ds4 ROCm
- Загрузка рекомендуемой квантизации для одного узла Halo
- Запуск сервера вывода ds4 и предоставление конечной точки, совместимой с OpenAI
- Подключение веб-интерфейса или агента для написания кода к локальному серверу

## Настройка конфигурации памяти

<!-- @require:memory-config -->

## Установка необходимого программного обеспечения

> **Системные требования для этой конфигурации (однонодовая IQ2_XXS с контекстом 126k):**
> - Система Strix Halo с **не менее 128 ГБ унифицированной памяти**.
> - **Выделенная видеопамять (UMA frame buffer) в BIOS должна быть установлена на минимум**, чтобы пул общей памяти мог быть как можно больше.
> - **Пул общей памяти GPU должен быть установлен на не менее 110 ГБ**: выполните `amd-ttm --set 110` (см. шаг настройки памяти выше) и перезагрузите систему. При меньших значениях может возникнуть ошибка нехватки памяти при загрузке модели с контекстом 126k. Если в вашей системе доступно меньше памяти, вместо этого снизьте значение **Context** в режиме сервера (Server Mode).
>
> **Примечание:** В качестве отправной точки попробуйте установить **пул общей памяти GPU** на **110 ГБ**. Если возникают ошибки нехватки памяти, увеличьте пул общей памяти или уменьшите размер контекста.

ds4-cockpit использует контейнеры-тулбоксы для запуска движка ds4. Установите `podman`, `distrobox` и `pipx`:

```bash
sudo apt update
sudo apt install -y podman distrobox pipx
```

<!-- @test:id=ds4-prereqs-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
podman --version
distrobox version 2>/dev/null || distrobox --version
pipx --version
echo "OK: podman, distrobox, and pipx are installed"
```
<!-- @test:end -->

## Доступные квантизации

Автор ds4 предоставляет несколько квантизированных версий DeepSeek V4 Flash в формате GGUF. Все модели ниже используют калибровку по матрице важности (imatrix), которая сохраняет более высокую точность для тех частей модели, которые наиболее важны для задач написания кода и логического рассуждения.

| Квантизация | Размер | Описание |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 ГБ | Рекомендуется для одного узла с 128 ГБ памяти |
| [Гибрид Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 ГБ | Сохраняет слои 37–42 с точностью Q4 для лучшей точности. Помещается в 128 ГБ, но оставляет меньше места под контекст |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 ГБ | Более высокое качество. Требует два узла Halo с многоузловой кластеризацией |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 ГБ | Опциональное дополнение для спекулятивного декодирования, повышающее скорость генерации |

Модель **IQ2_XXS imatrix** — хорошая отправная точка. Она комфортно помещается на одном узле и оставляет достаточно памяти для приемлемого размера окна контекста.

## Установка ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) — это лёгкий терминальный интерфейс, упрощающий начало работы с ds4 на Strix Halo. Он берёт на себя создание контейнеров-тулбоксов, загрузку весов модели и запуск серверов. Установите его с помощью `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

Запустите cockpit:
```bash
ds4-cockpit
```

<!-- @test:id=ds4-cockpit-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
# Verify the pipx-installed cockpit entry point is on PATH (do NOT launch the TUI).
command -v ds4-cockpit
echo "OK: ds4-cockpit is installed and on PATH"
```
<!-- @test:end -->

## Создание тулбокса

На вкладке **Interactive Toolboxes** выберите последний доступный/стабильный тулбокс (например, `ds4-rocm-7.2.4`) и нажмите **Create/Update**. Это загрузит образ контейнера и создаст среду тулбокса.


<p align="center">
  <img src="assets/ds4-cockpit-toolboxes.png" alt="Selecting the ds4 toolbox in ds4-cockpit" width="800"/>
</p>

<!-- @test:id=ds4-toolbox-image-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# The toolbox version changes over time, so match the image family, not a fixed tag.
if ! podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ds4-cockpit (Interactive Toolboxes tab) first."
  exit 1
fi
echo "OK: ds4 toolbox container image is present"
```
<!-- @test:end -->

## Загрузка модели

Перейдите на вкладку **Model Manager**. Выберите **IQ2_XXS imatrix (~80.8 GB)** из выпадающего списка и нажмите **Download**. Файлы модели по умолчанию будут сохранены в `~/ds4` (путь хранения можно изменить).

> **Примечание:** Модель IQ2_XXS занимает примерно 80 ГБ, поэтому загрузка может занять некоторое время в зависимости от вашего подключения. Вы можете продолжить после её завершения.

<p align="center">
  <img src="assets/ds4-cockpit-model-manager.png" alt="Selecting and downloading the IQ2_XXS model" width="800"/>
</p>

<!-- @test:id=ds4-model-downloaded-linux timeout=60 hidden=True -->
```bash
set -euo pipefail

# ds4-cockpit saves model weights to ~/ds4 by default
model_dir="$HOME/ds4"

if [ ! -d "$model_dir" ]; then
  echo "Model directory $model_dir does not exist. Download the model in ds4-cockpit (Model Manager tab) first."
  exit 1
fi

if ! find "$model_dir" -maxdepth 2 -iname '*.gguf' | grep -q .; then
  echo "No .gguf model files found under $model_dir. Download the IQ2_XXS imatrix model in ds4-cockpit first."
  exit 1
fi

# Prefer to confirm the recommended IQ2_XXS imatrix quantization is present.
if find "$model_dir" -maxdepth 2 -iname '*IQ2*imatrix*.gguf' | grep -q .; then
  echo "OK: IQ2_XXS imatrix model is downloaded"
else
  echo "OK: a GGUF model is present (recommended IQ2_XXS imatrix file not detected by name)"
fi
```
<!-- @test:end -->

## Запуск сервера

Перейдите на вкладку **Server Mode**. Выберите загруженную модель и тулбокс, затем настройте размер контекста, хост и порт. Когда всё готово, нажмите **Start ds4-server**.

> **Совет** Размер контекста `126000` — разумное начальное значение, которое должно поместиться на одном узле — вы можете установить его выше, если у вас есть запас памяти, или ниже, если вы столкнётесь с ошибками нехватки памяти. Порт (`8000` в этом руководстве) выбран произвольно; выберите любой свободный порт.

> **KV Disk Cache (опционально).** Включение **KV Disk Cache** переносит KV-кэш на диск (в **Host Cache Dir**, по умолчанию `~/.cache/ds4-kv`), так что повторяющиеся системные подсказки восстанавливаются с SSD вместо повторного вычисления. Это оптимизация производительности для рабочих процессов агентов написания кода с длинными, повторяющимися подсказками и **не требуется** для запуска сервера.

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Сервер запустится и будет прослушивать порт 8000, предоставляя конечную точку API, совместимую с OpenAI, по адресу `http://localhost:8000/v1`.

**Быстрая проверка:**
```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "deepseek-v4-flash",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": false
  }'
```

<!-- @test:id=ds4-server-chat-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

# This runner is shared with other playbooks, and ds4 at a 126k context consumes almost the entire GPU memory pool.
# So rather than keeping ds4 resident, CI starts the server, verifies a chat completion, then stops it again.
# This frees the memory for the next job.
# ds4 has no separate "unload"; stopping the server process is what releases the ~80 GB model.

CONTAINER="ds4-ci-server"
MODEL_DIR="$HOME/ds4"

# Locate the downloaded model (prefer the recommended IQ2_XXS imatrix file).
model_file="$(find "$MODEL_DIR" -maxdepth 2 -iname '*IQ2*imatrix*.gguf' 2>/dev/null | head -1)"
if [ -z "$model_file" ]; then
  model_file="$(find "$MODEL_DIR" -maxdepth 2 -iname '*.gguf' 2>/dev/null | head -1)"
fi
if [ -z "$model_file" ]; then
  echo "No .gguf model found under $MODEL_DIR. Download it in ds4-cockpit first."
  exit 1
fi
model_name="$(basename "$model_file")"

# Pick the toolbox image (version-agnostic).
image="$(podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox' | head -1)"
if [ -z "$image" ]; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ds4-cockpit first."
  exit 1
fi

# Always stop/remove the server on exit so it never holds GPU memory afterwards.
cleanup() {
  podman stop -t 10 "$CONTAINER" >/dev/null 2>&1 || true
  podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# Remove any stale instance, then start ds4-server detached (same flags ds4-cockpit uses, with -d instead of -it).
podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
podman run -d --name "$CONTAINER" \
  --device /dev/dri --device /dev/kfd \
  --group-add keep-groups \
  --security-opt seccomp=unconfined \
  --ipc=host \
  --cap-add=SYS_PTRACE \
  --security-opt label=disable \
  --userns=keep-id \
  -p 127.0.0.1:8000:8000 \
  -v "$MODEL_DIR":/models:ro \
  "$image" \
  ds4-server -m "/models/$model_name" --ctx 126000 --host 0.0.0.0 --port 8000

# Wait for readiness; the ~80 GB model can take a few minutes to load.
up=false
for i in $(seq 1 240); do
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 http://127.0.0.1:8000/v1/models || true)"
  if [ -n "$code" ] && [ "$code" != "000" ]; then
    up=true
    break
  fi
  if ! podman inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null | grep -q true; then
    echo "ds4-server container exited during startup:"
    podman logs "$CONTAINER" 2>&1 | tail -40 || true
    exit 1
  fi
  sleep 2
done

if [ "$up" != "true" ]; then
  echo "ds4 server did not become ready on http://127.0.0.1:8000"
  podman logs "$CONTAINER" 2>&1 | tail -40 || true
  exit 1
fi
echo "OK: ds4 server is responding on :8000"

body='{
  "model": "deepseek-v4-flash",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32,
  "stream": false
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from ds4 /v1/chat/completions"
  exit 1
fi

export DS4_OUT="$out"
python3 - <<'PY'
import json, os, sys

data = json.loads(os.environ["DS4_OUT"])
choices = data.get("choices")
if not choices:
    print("Response has no 'choices':")
    print(json.dumps(data, indent=2)[:2000])
    sys.exit(1)

message = choices[0].get("message", {}) or {}
content = message.get("content") or message.get("reasoning_content")
if not content:
    print("Response choice has empty content:")
    print(json.dumps(data, indent=2)[:2000])
    sys.exit(1)

print("OK: ds4 chat/completions returned content")
PY

echo "OK: ds4 server test complete; server stopped and GPU memory released"
```
<!-- @test:end -->

## Подключение веб-интерфейса

Вы можете подключить любой чат-интерфейс, поддерживающий формат OpenAI API. Например, чтобы использовать HuggingFace ChatUI:

```bash
docker run -p 3000:3000 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Откройте `http://localhost:3000` в браузере, чтобы начать общение.
## Подключение агента кодирования

Сервер ds4 предоставляет совместимые конечные точки как OpenAI, так и Anthropic, поэтому большинство агентов кодирования могут подключаться к нему напрямую. Например, чтобы добавить его в агент кодирования `pi`, добавьте следующий блок в `~/.pi/agent/models.json`:

```json
"ds4": {
  "name": "ds4.c local",
  "baseUrl": "http://localhost:8000/v1",
  "api": "openai-completions",
  "apiKey": "dsv4-local",
  "compat": {
    "supportsStore": false,
    "supportsDeveloperRole": false,
    "supportsReasoningEffort": true,
    "supportsUsageInStreaming": true,
    "maxTokensField": "max_tokens",
    "supportsStrictMode": false,
    "thinkingFormat": "deepseek",
    "requiresReasoningContentOnAssistantMessages": true
  },
  "models": [
    {
      "id": "deepseek-v4-flash",
      "name": "DeepSeek V4 Flash (ds4.c local)",
      "reasoning": true,
      "thinkingLevelMap": {
        "off": null,
        "minimal": "low",
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "xhigh"
      },
      "input": ["text"],
      "contextWindow": 131072,
      "maxTokens": 65536,
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 }
    }
  ]
}
```

> **Совет**: Если ваш агент кодирования или веб-интерфейс работает на другой машине, отличной от платформы Halo, вам нужно перенаправить порт 8000 через SSH:
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```

## Дальнейшие шаги

- **Многоузловая кластеризация**: Если у вас есть два устройства Halo, ds4 поддерживает распределение модели Q4 (~153 ГБ) между обеими машинами с помощью конвейерного параллелизма. Инструкции по настройке см. в [документации ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism).
- **Спекулятивное декодирование (MTP)**: Загрузите веса MTP (~3,6 ГБ) и передайте `--mtp` серверу для более высокой скорости генерации.
- **Выгрузка кэша KV на диск**: Для рабочих процессов агента кодирования включите `--kv-disk-dir`, чтобы повторяющиеся системные подсказки восстанавливались с SSD, а не пересчитывались каждый раз.

Дополнительную информацию см. в [репозитории ds4](https://github.com/antirez/ds4) и [наборе инструментов ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox).