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

## Огляд

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) — це орієнтований на ефективність варіант родини DeepSeek V4: модель Mixture of Experts із 284 мільярдами параметрів, із яких 13 мільярдів є активними. Згідно з [технічним звітом DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash), вона набирає 79% на SWE-bench Verified і 91,6% на LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) — це спеціалізований інференс-рушій, створений саме для цієї архітектури моделі. Замість універсального середовища виконання ds4 орієнтується безпосередньо на родину DeepSeek V4, використовуючи специфічні для архітектури оптимізації ядер для програмного забезпечення AMD ROCm™. Наразі це одна з найпродуктивніших реалізацій DeepSeek V4 Flash на Strix Halo.

У цьому посібнику показано, як використовувати `ai-toolbox-cockpit`, термінальний інтерфейс користувача, щоб налаштувати ds4, завантажити ваги моделі та запустити локальне обслуговування DeepSeek V4 Flash на платформі AMD Ryzen™ AI Halo Developer Platform.

## Що ви дізнаєтеся

- Як встановити та запустити термінальний інтерфейс `ai-toolbox-cockpit`
- Як створити контейнер-тулбокс ds4 ROCm
- Завантаження рекомендованого квантування для одного вузла Halo
- Запуск сервера інференсу ds4 та надання доступу до сумісної з OpenAI кінцевої точки
- Підключення веб-інтерфейсу або агента для кодування до локального сервера

## Налаштування конфігурації пам'яті

<!-- @require:memory-config -->

## Встановлення програмних передумов

> **Системні вимоги для цієї конфігурації (одновузлова IQ2_XXS із контекстом 126k):**
> - Система Strix Halo з **щонайменше 128 ГБ уніфікованої пам'яті**.
> - **Виділена відеопам'ять BIOS (UMA frame buffer) встановлена на мінімум**, щоб пул спільної пам'яті міг бути якомога більшим.
> - **Пул спільної пам'яті GPU встановлено щонайменше на 110 ГБ**: виконайте `amd-ttm --set 110` (див. крок налаштування пам'яті вище) і перезавантажте систему. Менші значення можуть призвести до нестачі пам'яті під час завантаження моделі з контекстом 126k. Якщо у вашій системі менше доступної пам'яті, замість цього знизьте значення **Context** у режимі Server Mode.
>
> **Примітка:** Спробуйте спочатку встановити **пул спільної пам'яті GPU** на **110 ГБ**. Якщо виникають помилки нестачі пам'яті, збільшіть пул спільної пам'яті або зменшіть розмір контексту.

ai-toolbox-cockpit використовує контейнерні тулбокси для запуску рушія ds4. Встановіть `podman`, `distrobox` і `pipx`:

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

## Доступні квантування

Автор ds4 надає кілька квантованих версій DeepSeek V4 Flash у форматі GGUF. Усі моделі нижче використовують калібрування матрицею важливості (imatrix), яке зберігає вищу точність у тих частинах моделі, що найбільше впливають на завдання кодування та міркування.

| Квантування | Розмір | Опис |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 ГБ | Рекомендовано для одного вузла з 128 ГБ |
| [Гібрид Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 ГБ | Зберігає шари 37–42 з точністю Q4 для кращої точності. Вміщується в 128 ГБ, але залишає менше місця для контексту |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 ГБ | Вища якість. Потребує два вузли Halo через кластеризацію з кількома вузлами |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 ГБ | Додатковий модуль для спекулятивного декодування, що покращує швидкість генерації |

Модель **IQ2_XXS imatrix** — гарна відправна точка. Вона комфортно вміщується на одному вузлі й залишає достатньо пам'яті для розумного вікна контексту.

## Встановлення ai-toolbox-cockpit

[ai-toolbox-cockpit](https://github.com/kyuz0/ai-toolbox-cockpit) — це легкий термінальний інтерфейс, який спрощує встановлення різних бекендів ШІ. Ми використаємо його для створення нашого контейнера ds4, завантаження ваг моделі та запуску серверів. Встановіть його за допомогою `pipx`:

<!-- @test:id=ds4-cockpit-install-linux timeout=300 -->
```bash
pipx install git+https://github.com/kyuz0/ai-toolbox-cockpit.git
```
<!-- @test:end -->

Запустіть cockpit:
```bash
ai-toolbox-cockpit
```

<!-- @test:id=ds4-cockpit-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
# Verify the pipx-installed cockpit entry point is on PATH (do NOT launch the TUI).
command -v ai-toolbox-cockpit
echo "OK: ai-toolbox-cockpit is installed and on PATH"
```
<!-- @test:end -->

## Крок 1: Створення тулбокса

На вкладці **Interactive Toolboxes** виберіть останній доступний/стабільний тулбокс для ds4 (наприклад, `ds4-rocm-10.0`) і натисніть **Create/Update**. Це завантажить образ контейнера та створить середовище тулбокса.


<p align="center">
  <img src="assets/ai-toolbox-cockpit-toolboxes.png" alt="Selecting the ds4 toolbox in ai-toolbox-cockpit" width="800"/>
</p>

<!-- @test:id=ds4-toolbox-image-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# The toolbox version changes over time, so match the image family, not a fixed tag.
if ! podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ai-toolbox-cockpit (Interactive Toolboxes tab) first."
  exit 1
fi
echo "OK: ds4 toolbox container image is present"
```
<!-- @test:end -->

## Крок 2: Завантаження моделі

Перейдіть на вкладку **Models**. Спочатку виберіть бекенд (ds4). Потім виберіть **IQ2_XXS imatrix (~80,8 ГБ)** зі спадного списку та натисніть **Download**. Файли моделі буде збережено в `~/ds4` за замовчуванням (шлях зберігання можна змінити).

> **Примітка:** Модель IQ2_XXS має розмір приблизно 80 ГБ, тож завантаження може зайняти деякий час залежно від вашого з'єднання. Ви можете продовжити після завершення.

<p align="center">
  <img src="assets/ai-toolbox-cockpit-models.png" alt="Selecting and downloading the IQ2_XXS model" width="800"/>
</p>

<!-- @test:id=ds4-model-downloaded-linux timeout=60 hidden=True -->
```bash
set -euo pipefail

# ai-toolbox-cockpit saves model weights to ~/ds4 by default
model_dir="$HOME/ds4"

if [ ! -d "$model_dir" ]; then
  echo "Model directory $model_dir does not exist. Download the model in ai-toolbox-cockpit (Model Manager tab) first."
  exit 1
fi

if ! find "$model_dir" -maxdepth 2 -iname '*.gguf' | grep -q .; then
  echo "No .gguf model files found under $model_dir. Download the IQ2_XXS imatrix model in ai-toolbox-cockpit first."
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

## Крок 3: Запуск сервера

Перейдіть на вкладку **Server Mode**. Виберіть завантажену модель і тулбокс, потім налаштуйте розмір контексту, хост і порт. Коли будете готові, натисніть **Start ds4-server**.

> **Порада:** Розмір контексту `126000` — це розумне початкове значення, яке має вміститися на одному вузлі; ви можете встановити вище значення, якщо у вас є запас пам'яті, або нижче — якщо виникають помилки нестачі пам'яті. Порт (`8000` у цьому посібнику) обрано довільно; можете обрати будь-який вільний порт.

> **Дисковий кеш KV (опціонально).** Увімкнення **KV Disk Cache** вивантажує кеш KV на диск (у **Host Cache Dir**, за замовчуванням `~/.cache/ds4-kv`), щоб повторювані системні промпти відновлювалися з SSD замість повторного обчислення. Це оптимізація продуктивності для робочих процесів агентів кодування з довгими, повторюваними промптами, і вона **не є обов'язковою** для запуску сервера.

<p align="center">
  <img src="assets/ai-toolbox-cockpit-server.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Сервер запуститься та слухатиме порт 8000, надаючи доступ до сумісної з OpenAI кінцевої точки API за адресою `http://localhost:8000/v1`.

**Швидкий тест:**
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
  echo "No .gguf model found under $MODEL_DIR. Download it in ai-toolbox-cockpit first."
  exit 1
fi
model_name="$(basename "$model_file")"

# Pick the toolbox image (version-agnostic).
image="$(podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox' | head -1)"
if [ -z "$image" ]; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ai-toolbox-cockpit first."
  exit 1
fi

# Always stop/remove the server on exit so it never holds GPU memory afterwards.
cleanup() {
  podman stop -t 10 "$CONTAINER" >/dev/null 2>&1 || true
  podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# keep-id maps the calling user into the container. Root does not need it, and as root it cannot
# be combined with --ipc=host (crun fails to mount /dev/mqueue), so root keeps the host user namespace.
userns=keep-id
if [ "$(id -u)" -eq 0 ]; then
  userns=host
fi

# Remove any stale instance, then start ds4-server detached (same flags ai-toolbox-cockpit uses, with -d instead of -it).
podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
podman run -d --name "$CONTAINER" \
  --device /dev/dri --device /dev/kfd \
  --group-add keep-groups \
  --security-opt seccomp=unconfined \
  --ipc=host \
  --cap-add=SYS_PTRACE \
  --security-opt label=disable \
  --userns="$userns" \
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
## Підключення веб-інтерфейсу

Ви можете підключити будь-який чат-інтерфейс, який підтримує формат OpenAI API. Наприклад, щоб використовувати HuggingFace ChatUI:

```bash
docker run --network=host \
  -e PORT=3000 \
  -e OPENAI_BASE_URL=http://localhost:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Відкрийте `http://localhost:3000` у своєму браузері, щоб почати спілкування.

> **Примітка:** `--network=host` розміщує веб-інтерфейс у мережі хоста, щоб він міг напряму звертатися до сервера ds4 на `localhost`. Це дозволяє серверу ds4 залишатися прив'язаним до loopback (йому не потрібно бути доступним на інших інтерфейсах).

> **Порада:** Порт веб-інтерфейсу (тут `3000`, встановлений через `PORT`) є довільним — виберіть будь-який вільний порт, якщо `3000` вже зайнятий, і відкрийте цей порт у своєму браузері замість нього. Переконайтеся, що порт у `OPENAI_BASE_URL` збігається з портом, на якому працює ваш сервер ds4.

## Підключення агента кодування

Сервер ds4 надає як OpenAI-, так і Anthropic-сумісні кінцеві точки, тому більшість агентів кодування можуть підключатися до нього безпосередньо. Наприклад, щоб додати його до агента кодування `pi`, додайте наступний блок до `~/.pi/agent/models.json`:

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

> **Порада**: Якщо ваш агент кодування або веб-інтерфейс працює на іншій машині, ніж платформа Halo, вам потрібно буде перенаправити порт сервера (тут `8000`) через SSH:
> ```bash
> ssh -L 8000:localhost:8000 <halo-host-ip>
> ```

## Наступні кроки

- **Багатовузлова кластеризація**: Якщо у вас є два пристрої Halo, ds4 підтримує розподіл моделі Q4 (~153 ГБ) між обома машинами за допомогою конвеєрного паралелізму. Дивіться [документацію ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) для інструкцій з налаштування.
- **Спекулятивне декодування (MTP)**: Завантажте ваги MTP (~3.6 ГБ) і передайте `--mtp` серверу для швидшої генерації.
- **Вивантаження кешу KV на диск**: Для робочих процесів агентів кодування увімкніть `--kv-disk-dir`, щоб повторювані системні промпти відновлювалися з SSD замість повторного обчислення щоразу.

Для отримання додаткової інформації дивіться [репозиторій ds4](https://github.com/antirez/ds4) та [набір інструментів ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox).