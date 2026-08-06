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

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) — це орієнтований на ефективність варіант родини DeepSeek V4 — модель Mixture of Experts зі 284 мільярдами параметрів, з яких 13 мільярдів активних. Згідно з [технічним звітом DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash), вона показує 79% на SWE-bench Verified та 91.6% на LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) — це спеціалізований інференс-двигун, створений саме для цієї архітектури моделі. На відміну від рушіїв загального призначення, ds4 орієнтований безпосередньо на родину DeepSeek V4 з оптимізаціями ядер, специфічними для архітектури, для програмного забезпечення AMD ROCm™. Наразі це одна з найпродуктивніших реалізацій DeepSeek V4 Flash на Strix Halo.

Цей навчальний посібник показує, як використовувати `ds4-cockpit`, термінальний інтерфейс користувача, для налаштування ds4, завантаження вагових коефіцієнтів моделі та запуску локального обслуговування DeepSeek V4 Flash на платформі розробника AMD Ryzen™ AI Halo.

## Що ви дізнаєтеся

- Як встановити та запустити термінальний інтерфейс `ds4-cockpit`
- Як створити ROCm-контейнер toolbox для ds4
- Завантаження рекомендованого квантування для одного вузла Halo
- Запуск сервера інференсу ds4 та надання доступу до сумісної з OpenAI кінцевої точки
- Підключення веб-інтерфейсу або кодового агента до локального сервера

## Налаштування конфігурації пам'яті

<!-- @require:memory-config -->

## Встановлення необхідного програмного забезпечення

> **Системні вимоги для цієї конфігурації (однодвузлова IQ2_XXS з контекстом 126k):**
> - Система Strix Halo з **щонайменше 128 ГБ уніфікованої пам'яті**.
> - **Виділена VRAM у BIOS (UMA frame buffer) встановлена на мінімум**, щоб пул спільної пам'яті міг бути якомога більшим.
> - Пул спільної пам'яті GPU **встановлений щонайменше на 110 ГБ**: виконайте `amd-ttm --set 110` (див. крок налаштування пам'яті вище) і перезавантажте систему. Менші значення можуть спричинити помилки нестачі пам'яті при завантаженні моделі з контекстом 126k. Якщо у вашій системі менше доступної пам'яті, замість цього зменшіть значення **Context** у режимі сервера.
>
> **Примітка:** Спробуйте встановити **пул спільної пам'яті GPU** на **110 ГБ** як початкове значення. Якщо ви зіткнетеся з помилками нестачі пам'яті, збільшіть пул спільної пам'яті або зменшіть розмір контексту.

ds4-cockpit використовує контейнери toolbox для запуску двигуна ds4. Встановіть `podman`, `distrobox` і `pipx`:

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

Автор ds4 надає кілька квантованих версій DeepSeek V4 Flash у форматі GGUF. Усі моделі нижче використовують калібрування importance matrix (imatrix), яке зберігає вищу точність для тих частин моделі, що найважливіші для завдань програмування та міркування.

| Квантування | Розмір | Опис |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80.8 ГБ | Рекомендовано для одного вузла на 128 ГБ |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 ГБ | Зберігає шари 37–42 з точністю Q4 для кращої якості. Вміщується в 128 ГБ, але залишає менше місця для контексту |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 ГБ | Вища якість. Потребує два вузли Halo через мультивузлову кластеризацію |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3.6 ГБ | Додатковий модуль для спекулятивного декодування, щоб пришвидшити генерацію |

Модель **IQ2_XXS imatrix** — хороша відправна точка. Вона комфортно вміщується на одному вузлі та залишає достатньо пам'яті для розумного розміру контекстного вікна.

## Встановлення ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) — це легкий термінальний інтерфейс, який спрощує запуск та роботу з ds4 на Strix Halo. Він керує створенням контейнерів toolbox, завантаженням вагових коефіцієнтів моделі та запуском серверів. Встановіть його за допомогою `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

Запустіть cockpit:
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

## Створення Toolbox

На вкладці **Interactive Toolboxes** виберіть останній доступний/стабільний toolbox (наприклад, `ds4-rocm-7.2.4`) і натисніть **Create/Update**. Це завантажить образ контейнера та створить середовище toolbox.


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

## Завантаження моделі

Перейдіть на вкладку **Model Manager**. Виберіть **IQ2_XXS imatrix (~80.8 ГБ)** у випадаючому списку та натисніть **Download**. Файли моделі буде збережено в `~/ds4` за замовчуванням (шлях зберігання можна змінити).

> **Примітка:** Модель IQ2_XXS має розмір приблизно 80 ГБ, тому завантаження може тривати деякий час залежно від вашого з'єднання. Продовжите, коли воно завершиться.

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

Перейдіть на вкладку **Server Mode**. Виберіть завантажену модель і toolbox, потім налаштуйте розмір контексту, хост і порт. Коли будете готові, натисніть **Start ds4-server**.

> **Порада** Розмір контексту `126000` є розумним початковим значенням, яке має вміститися на одному вузлі — ви можете встановити більше значення, якщо у вас є запас пам'яті, або зменшити його, якщо виникають помилки нестачі пам'яті. Порт (`8000` у цьому посібнику) довільний; виберіть будь-який вільний порт.

> **KV Disk Cache (опціонально).** Увімкнення **KV Disk Cache** вивантажує KV-кеш на диск (у **Host Cache Dir**, за замовчуванням `~/.cache/ds4-kv`), щоб повторювані системні підказки відновлювалися з SSD замість повторного обчислення. Це оптимізація продуктивності для робочих процесів кодових агентів з довгими, повторюваними підказками, і **не обов'язкова** для запуску сервера.

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

Сервер запуститься та слухатиме порт 8000, надаючи доступ до сумісної з OpenAI кінцевої точки API за адресою `http://localhost:8000/v1`.

**Швидка перевірка:**
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

## Підключення веб-інтерфейсу

Ви можете підключити будь-який чат-інтерфейс, що підтримує формат OpenAI API. Наприклад, щоб використати HuggingFace ChatUI:

```bash
docker run -p 3000:3000 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Відкрийте `http://localhost:3000` у вашому браузері, щоб почати спілкування.
## Підключення агента для кодування

Сервер ds4 надає сумісні кінцеві точки як OpenAI, так і Anthropic, тому більшість агентів для кодування можуть підключатися до нього напряму. Наприклад, щоб додати його до агента для кодування `pi`, додайте наступний блок до `~/.pi/agent/models.json`:

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

> **Порада**: Якщо ваш агент для кодування або Web UI працює на іншій машині, ніж платформа Halo, вам потрібно буде переспрямувати порт 8000 через SSH:
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```

## Наступні кроки

- **Кластеризація з кількох вузлів**: Якщо у вас є два пристрої Halo, ds4 підтримує розподіл моделі Q4 (~153 ГБ) між обома машинами за допомогою пайплайн-паралелізму. Дивіться [документацію ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) для отримання інструкцій із налаштування.
- **Спекулятивне декодування (MTP)**: Завантажте ваги MTP (~3,6 ГБ) і передайте `--mtp` серверу для швидшої швидкості генерації.
- **Вивантаження кешу KV на диск**: Для робочих процесів агентів для кодування увімкніть `--kv-disk-dir`, щоб повторювані системні запити відновлювалися з SSD замість повторного обчислення щоразу.

Для отримання додаткової інформації дивіться [репозиторій ds4](https://github.com/antirez/ds4) та [набір інструментів ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox).