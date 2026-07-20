<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# Запуск OpenClaw із Lemonade Server як бекендом

## Огляд

[**OpenClaw**](https://openclaw.ai/) — це автономний AI-агент, який може писати та виконувати код, керувати файлами та виконувати складні багатоетапні завдання від вашого імені. На відміну від чат-асистента, який лише відповідає на запитання, OpenClaw виконує реальні дії у вашій системі, а це означає, що йому потрібен швидкий, потужний AI-бекенд, здатний встигати за вимогливим циклом роботи агента.

[**Lemonade Server**](https://lemonade-server.ai/) — саме такий бекенд. Це локальний сервер інференсу з відкритим кодом, який запускає GenAI-моделі безпосередньо на вашому обладнанні та надає до них доступ через галузевий стандарт OpenAI API.

Разом вони формують повністю локальний стек AI-агента: Lemonade відповідає за інференс моделі, а OpenClaw забезпечує цикл роботи агента, який перетворює вихідні дані моделі на реальні дії.

> **Перш ніж продовжити:** OpenClaw — це високоавтономний AI-агент. Надання будь-якому AI-агенту доступу до вашої системи може призвести до непередбачуваних або небажаних наслідків. Продовжуйте лише якщо ви розумієте ризики та готові до того, що автономне програмне забезпечення діятиме від вашого імені.

---

## Чого ви навчитеся

Наприкінці цього посібника ви зможете:

- Дізнатися про **Lemonade Server**
- **Встановити OpenClaw** та **налаштувати його на роботу з Lemonade Server** як AI-бекендом.
- **Запустити шлюз OpenClaw** та переконатися, що ваш агент готовий до роботи.
- **Підключити канал зв'язку** (Discord або Telegram), щоб спілкуватися зі своїм агентом з будь-якого пристрою.

---

## Налаштування конфігурації пам'яті

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Перевірка оновлень програмного забезпечення

<!-- @require:software-update -->
<!-- @device:end -->

## Встановлення необхідного програмного забезпечення

<!-- @os:linux -->
- ПК з **Ubuntu 24.04+** або сумісним дистрибутивом Linux на основі Debian з `apt-get`
- Щонайменше **12 ГБ оперативної пам'яті** (рекомендовано 64 ГБ+ для більших моделей)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (Необов'язково, для пісочниці OpenClaw)

- **~10–30 ГБ вільного місця на диску** для ваг моделі
<!-- @os:end -->
<!-- @os:windows -->
- ПК з **Windows 10/11**
- Щонайменше **12 ГБ оперативної пам'яті** (рекомендовано 64 ГБ+ для більших моделей)
- **~10–30 ГБ вільного місця на диску** для ваг моделі
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (Необов'язково, для пісочниці OpenClaw)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Завантажте та завантажте рекомендовану модель

Рекомендованою моделлю для цього посібника є **Qwen3.6-35B-A3B-GGUF** від Unsloth, потужна MoE-модель із вікном контексту на 263 тис. токенів, яка добре підходить для навантажень агентів. Ця модель використовує квантизацію UD-Q4_K_XL. Завантажте її зараз:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Потім завантажте її з великим вікном контексту та збережіть це налаштування для майбутніх запусків:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Модель має типову довжину контексту 262 144 токени. Якщо ви зіткнетеся з помилками нестачі пам'яті (OOM), розгляньте можливість зменшення вікна контексту. Однак, оскільки Qwen3.6 використовує розширений контекст для складних завдань, ми радимо підтримувати довжину контексту щонайменше 128 тис. токенів, щоб зберегти можливості мислення.

> **Порада: вимкніть режим мислення для швидших відповідей агента:** Qwen3.6-35B-A3B за замовчуванням працює в режимі мислення, що додає затримку перед кожною відповіддю. У циклах роботи агента ці накладні витрати швидко накопичуються. Репозиторій [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) надає готову конфігурацію, яка вимикає режим мислення. Щоб її використати, завантажте файл та імпортуйте його:
>
> ```bash
> curl -LO https://raw.githubusercontent.com/lemonade-sdk/recipes/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json
> lemonade import Qwen3.6-35B-A3B-NoThinking.json
> ```

---

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$modelsJson = $null
for ($i = 0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}

if (-not $modelsJson) {throw "Lemonade server not ready on http://127.0.0.1:13305"}
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${openclaw_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${openclaw_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${openclaw_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${openclaw_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${openclaw_model} is not saved with ctx_size=262144. Run: lemonade load ${openclaw_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${openclaw_model} is saved with ctx_size=262144"

$body = @{
  model = "${openclaw_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openclaw-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) {throw "Empty response from Lemonade chat/completions"}
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-chat-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

export MODELS_JSON="$models_json"

python3 - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["MODELS_JSON"])
model_id = "${openclaw_model}"

entry = None
for item in data.get("data", []):
    if item.get("id") == model_id:
        entry = item
        break

if entry is None:
    print(f"Model {model_id} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print(f"Model {model_id} is present but not downloaded in Lemonade. Please download it before running CI.")
    sys.exit(1)

print(f"OK: {model_id} model is downloaded in Lemonade")

ctx_size = entry.get("recipe_options", {}).get("ctx_size")
if ctx_size != 262144:
    print(f"Model {model_id} is not saved with ctx_size=262144. Run: lemonade load {model_id} --ctx-size 262144 --save-options")
    sys.exit(1)
print(f"OK: {model_id} is saved with ctx_size=262144")
PY

body='{
  "model": "${openclaw_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Lemonade chat/completions returned a response"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->

## Налаштування WSL

Ми запускаємо OpenClaw усередині WSL (Рекомендовано) та підключаємо його до Lemonade, який працює нативно на Windows. Це надає вам середовище оболонки Linux для OpenClaw, зберігаючи при цьому апаратне прискорення GPU для Lemonade на стороні Windows.

### Встановлення WSL та Ubuntu

Відкрийте PowerShell від імені адміністратора та встановіть ядро WSL:

```powershell
wsl --install --no-distribution
```

Потім встановіть Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Увімкнення systemd у WSL

Виконайте це в терміналі Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Перезапустіть WSL:

```powershell
wsl --shutdown
wsl
```

### Прокидання Lemonade з Windows у WSL

WSL2 працює у віртуальній мережі. Lemonade на Windows прив'язується до `127.0.0.1`, до якого WSL не може отримати прямий доступ. Проксі порту Windows перенаправляє трафік із IP-адреси шлюзу WSL на локальний хост Windows.

**Знайдіть IP-адресу вашого шлюзу WSL** (виконайте всередині WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Додайте проксі порту** (виконайте в PowerShell від імені адміністратора, замінивши `<WSL-Gateway-IP>` на вашу IP-адресу шлюзу WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Додайте правило брандмауера** (той самий елевований PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Перевірте з WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Якщо ви вже завантажили модель Qwen3.6-35B-A3B-GGUF на попередньому кроці, ви маєте побачити вихідні дані JSON, подібні до цього:

```json
{
  "data": [
    {
      "checkpoint": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL",
      "checkpoints": {
        "main": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL"
      },
      "mmproj": "unsloth/Qwen3.6-35B-A3B-GGUF:mmproj-F16.gguf",
      ....
    }
  ],
  "object": "list"
}
```

> Правило `netsh portproxy` зберігається після перезавантаження, але IP-адреса шлюзу WSL може змінюватися після `wsl --shutdown`. Якщо Lemonade стає недоступним із WSL після перезапуску, отримайте оновлену IP-адресу шлюзу та оновіть проксі новою IP-адресою.

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

echo "WSL gateway IP: $WINDOWS_HOST"

models_json="$(curl -fsS --max-time 5 "http://$WINDOWS_HOST:13305/api/v1/models")"

if [ -z "$models_json" ]; then
  echo "Could not reach Lemonade from WSL at http://$WINDOWS_HOST:13305/api/v1/models"
  echo "Check the Windows netsh portproxy and firewall rule from the README."
  exit 1
fi

echo "$models_json" | python3 -m json.tool >/dev/null
echo "OK: WSL can reach native Windows Lemonade through the bridge"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "wsl-lemonade-bridge-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "WSL Lemonade bridge test failed"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 

---
<!-- @os:end -->

## Встановлення та налаштування OpenClaw

### Встановлення OpenClaw
<!-- @os:windows -->
> Виконуйте команди в цьому розділі всередині вашого терміналу **WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Прапорець `--no-onboard` пропускає інтерактивний майстер налаштування; ви налаштуєте бекенд моделі вручну на наступному кроці, що дає вам точний контроль над тим, яка модель і сервер використовуються.

Відкрийте новий термінал і підтвердьте встановлення:

```bash
openclaw --version
```

> **Порада:** Якщо після встановлення ви бачите `command not found`, додайте глобальний каталог bin npm до вашого PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Щоб зробити це постійним, додайте наведений вище рядок до вашого файлу `~/.bashrc` або `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=openclaw-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->
### Налаштування OpenClaw для використання Lemonade

Запустіть неінтерактивне первинне налаштування OpenClaw.
<!-- @os:linux -->
```bash
openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->
<!-- @os:windows -->
```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->

Ця команда записує конфігурацію OpenClaw до `~/.openclaw/openclaw.json`.

> **Розмір контекстного вікна OpenClaw:** ущільнення (compaction) в OpenClaw запускається, коли `contextTokens > contextWindow − reserveTokens`. Значення `reserveTokensFloor` за замовчуванням становить 20 000 токенів — це нижня межа, яка перевизначає `reserveTokens`, якщо воно менше, тому будь-яке контекстне вікно моделі менше ~37 тис. токенів спричинить нескінченний цикл ущільнення. Встановіть у своїй конфігурації низький резерв і вимкніть цю межу один раз — і це застосовуватиметься до кожної моделі без окремого налаштування для кожної з них:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` — це *нижня межа* (мінімальний захист), а не сам резерв, тож встановлення лише цієї межі не матиме ефекту. `reserveTokensFloor: 0` вимикає цей захист, щоб було прийнято менше значення `reserveTokens`.
>
> **Коли це застосовувати:** використовуйте цю конфігурацію, якщо ефективне контекстне вікно вашої моделі менше ~37 тис. токенів — або через те, що модель невелика (наприклад, 8k, 16k, 32k), або через те, що ви навмисно обмежили контекст меншим значенням (наприклад, завантажили модель на 128k, але встановили контекст 16k у Lemonade). Без цього OpenClaw при запуску потрапить у нескінченний цикл ущільнення.
>
> **Моделі з великим контекстом при повному контекстному вікні:** це можна повністю пропустити. Значення за замовчуванням працюють добре, ущільнення спрацює задовго до заповнення вікна, і в моделі буде достатньо простору для генерації довгих відповідей. Якщо ж ви все ж застосуєте це, майте на увазі, що `reserveTokens: 4096` обмежує довжину відповіді приблизно 4 тис. токенів, що може обрізати генерацію довгих файлів або детальних планів.
>
> **Куди це додати:** розмістіть блок `compaction` всередині `agents.defaults` у вашому файлі `openclaw.json` (зазвичай за адресою `~/.openclaw/openclaw.json`):
>
> ```json
> {
>   "agents": {
>     "defaults": {
>       "workspace": "/home/<you>/.openclaw/workspace",
>       "model": {
>         "primary": "lemonade/<your-model-id>"
>       },
>       "compaction": {
>         "reserveTokens": 4096,
>         "reserveTokensFloor": 0
>       }
>     }
>   }
> }
> ```
>
> Решта вашої конфігурації (gateway, channels, models тощо) залишається без змін, потрібно додати лише ключ `compaction`.

### (Рекомендовано) Увімкнути пісочницю Docker

OpenClaw може спрямовувати всі файлові та кодові операції агента через ізольований контейнер Docker, замість того, щоб виконувати їх безпосередньо на вашому хості. Це обмежує радіус впливу будь-якої небажаної дії ізольованим середовищем, залишаючи файлову систему та мережу вашого хоста недоторканими.

Зберіть образ пісочниці один раз (Docker має бути встановлений):

```bash
docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE
```

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Виконайте це, щоб додати ключ `sandbox` всередині наявного блока `agents.defaults` у `~/.openclaw/openclaw.json`:

```bash
cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5
openclaw config patch --file ./sandbox.patch.json5
```

Контейнери пісочниці за замовчуванням **не мають доступу до мережі**. Дивіться [довідник з пісочниць](https://docs.openclaw.ai/gateway/sandboxing) щодо монтування томів та перевизначень мережі.

> #### Усунення несправностей: Docker Permission Denied
> 
> Якщо ви отримуєте помилку "permission denied" під час виконання команд Docker:
> 
> **Крок 1: додайте свого користувача до групи docker**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **Крок 2: якщо помилка не зникає, застосуйте постійне виправлення**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Потім **перезавантажте** систему.
> 
> **Швидке тимчасове виправлення** (скидається після перезавантаження):
> ```bash
> sudo chmod 666 /var/run/docker.sock
> ```

<!-- @os:linux -->
<!-- @test:id=openclaw-onboard-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "127.0.0.1:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written"
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-onboard-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "$WINDOWS_HOST:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-onboard-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw onboarding failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"
$tmp = Join-Path $env:TEMP "openclaw-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox config patch failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

### Запуск Gateway OpenClaw

Gateway — це процес OpenClaw, який керує циклом роботи агента та обслуговує панель приладів:

```bash
openclaw gateway run --bind loopback --port 18789
```

<!-- @os:linux -->
<!-- @test:id=openclaw-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

Щоб відкрити панель приладів, виконайте це в другому терміналі, поки gateway все ще запущений:

```bash
openclaw dashboard
```

Оскільки gateway прив'язується до loopback-адреси, панель приладів автоматично автентифікується при відкритті з того самого пристрою, тож для локального доступу не потрібно вводити токен чи підтверджувати пристрій. Ви маєте побачити панель приладів OpenClaw з вашою моделлю Lemonade, зазначеною як активний бекенд.

> Якщо ви увімкнули пісочницю, ви можете перевірити її, попросивши агента виконати `run hostname` з панелі приладів. Якщо ви бачите короткий ID контейнера замість імені вашого хосту, пісочниця працює правильно.

**Вітаємо, ви побудували повністю локальний стек ШІ-агента з нуля.**

> **Потрібен токен gateway?** Виконайте `openclaw dashboard --no-open`, щоб вивести URL панелі приладів із вбудованим токеном (він також намагається скопіювати його до буфера обміну). Або токен можна знайти за ключем `gateway.auth.token` у `~/.openclaw/openclaw.json`.
>
> **Підтвердження віддаленого пристрою:** коли ви відкриваєте панель приладів з другого пристрою чи телефону, браузер показує ID запиту. Повернувшись на машину, де запущений gateway, виконайте:
> ```bash
> openclaw devices approve <requestId>
> ```
> Це потрібно лише для віддалених або додаткових пристроїв, доступ через loopback з того самого пристрою автентифікується автоматично.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Додатково: підключення каналу зв'язку

Після запуску gateway ви можете отримати доступ до свого локального агента з будь-якого пристрою. Оберіть варіант, що підходить для вашої конфігурації. OpenClaw підтримує [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) та інші канали, повний список дивіться на [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Варіант A: Discord

Discord вимагає сервер, на якому **ви маєте права адміністратора**, щоб додати бота. Якщо ви є учасником спільних серверів, але не володієте жодним із них, скористайтеся варіантом B (Telegram).
#### Створіть обліковий запис і сервер Discord

Якщо у вас немає облікового запису Discord, зареєструйтеся на [discord.com](https://discord.com). Вам також потрібен сервер, на якому ви є адміністратором — створіть його, натиснувши на іконку **+** на бічній панелі Discord і вибравши **Create My Own**. Приватний сервер підійде.

#### Створіть застосунок і бота Discord

1. Перейдіть до [Discord Developer Portal](https://discord.com/developers/applications) та натисніть **New Application**. Дайте йому назву (наприклад, "openclaw-bot").
2. На бічній панелі натисніть **Bot**. Встановіть ім'я користувача для бота.
3. Залишаючись на сторінці Bot, прокрутіть до **Privileged Gateway Intents** і увімкніть:
   - **Message Content Intent** (обов'язково)
   - **Server Members Intent** (рекомендовано)
4. Прокрутіть назад догори та натисніть **Reset Token**, щоб згенерувати токен бота. Скопіюйте його.

#### Додайте бота на ваш сервер

1. На бічній панелі натисніть **OAuth2/ URL Generator**.
2. У розділі **Scopes** увімкніть `bot` і `applications.commands`.
3. У розділі **Bot Permissions** увімкніть: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Скопіюйте згенеровану URL-адресу, вставте її в браузер, виберіть свій сервер і підтвердьте. Бот тепер має з'явитися у списку учасників вашого сервера.

#### Зберіть свої ID

Увімкніть режим розробника в Discord (**User Settings/ Advanced/ Developer Mode**), потім:
- Натисніть правою кнопкою на іконку вашого сервера: **Copy Server ID**
- Натисніть правою кнопкою на свій аватар: **Copy User ID**

#### Дозвольте особисті повідомлення від учасників сервера

Натисніть правою кнопкою на іконку вашого сервера/ **Privacy Settings**/ увімкніть **Direct Messages**. Це дозволить боту надсилати вам особисті повідомлення, що необхідно для етапу з'єднання (pairing).

#### Налаштуйте OpenClaw для Discord

Збережіть токен вашого бота як змінну середовища, потім створіть один патч-файл, який увімкне Discord, посилатиметься на токен і додасть ваш сервер до дозволеного списку. Замініть `<server_id>` та `<user_id>` на ID, зібрані вище.

```bash
export DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN"

cat > discord.patch.json5 <<JSON5
{
  channels: {
    discord: {
      enabled: true,
      token: { source: "env", provider: "default", id: "DISCORD_BOT_TOKEN" },
      dmPolicy: "pairing",
      groupPolicy: "allowlist",
      guilds: {
        "<server_id>": {
          requireMention: false,
          users: ["<user_id>"],
        },
      },
    },
  },
}
JSON5
openclaw config patch --file ./discord.patch.json5
```

> **Не покладайтеся на прохання до агента налаштувати це.** Коли увімкнено пісочницю (sandboxing), агент не може записувати до `~/.openclaw/openclaw.json` зсередини пісочниці, натомість використовуйте наведені вище команди CLI на хості.

Перезапустіть шлюз, щоб він застосував нову конфігурацію каналу:

```bash
openclaw gateway run --bind loopback --port 18789
```

Ви маєте побачити `logged in to discord as <bot-name>` у виведенні шлюзу протягом кількох секунд.

#### З'єднайте свій обліковий запис Discord

Надішліть особисте повідомлення боту в Discord. Він відповість коротким кодом з'єднання.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Підтвердьте це на машині, де запущено OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Коди з'єднання втрачають чинність через годину.

Тепер ви можете спілкуватися зі своїм агентом безпосередньо з Discord і передавати завдання на своє локальне обладнання.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Варіант Б: Telegram

Telegram простіший за Discord для більшості користувачів, він не потребує сервера чи прав адміністратора.

#### Створіть бота Telegram

1. Відкрийте Telegram і напишіть **@BotFather**.
2. Надішліть `/newbot` і дотримуйтесь підказок. Збережіть токен бота, який вам буде надано.

#### Налаштуйте OpenClaw для Telegram

Збережіть токен як змінну середовища:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Додайте конфігурацію каналу до `~/.openclaw/openclaw.json` (або застосуйте патч через дашборд):

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "YOUR_BOT_TOKEN",
      "dmPolicy": "pairing"
    }
  }
}
```

Перезапустіть шлюз, потім надішліть своєму боту будь-яке повідомлення в Telegram. Підтвердьте з'єднання:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Коди з'єднання втрачають чинність через годину. Тепер ви можете спілкуватися зі своїм агентом через особисті повідомлення Telegram.

---

## Наступні кроки

Тепер, коли ваш агент може отримувати команди з вашого телефону та виконувати дії на вашій локальній машині, ось три напрямки, варті вивчення:

1. **Узагальнювач фондового ринку**: Заплануйте OpenClaw для отримання даних з фінансових API з фіксованим інтервалом, підсумовуйте денні рухи за допомогою вашої локальної моделі та надсилайте дайджест на телефон щоранку через обраний вами канал.

2. **Монітор донавчання (fine-tuning)**: Запустіть завдання навчання віддалено через Telegram або Discord, а потім нехай агент відстежує лог навчання та повідомляє періодичні значення втрат, використання GPU та дискового простору на ваш телефон. Якщо процес зупиняється або відбувається сплеск використання VRAM, ви дізнаєтесь про це негайно, не перебуваючи біля машини.

3. **IOT з локальною VLM**: Направте камеру на вхідні двері, запустіть модель зору на Lemonade і нехай OpenClaw аналізує кадри за запитом або тригером. Запитайте "чи прийшли якісь посилки сьогодні?" зі свого телефону та отримайте пряму відповідь від вашого власного обладнання.