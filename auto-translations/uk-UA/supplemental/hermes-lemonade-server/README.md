<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинний переклад.** Цю сторінку було автоматично перекладено з англійської мови, і вона не була перевірена людиною. Вона може містити помилки, а певні інструкції, команди, завантаження, доступність продукту чи інший вміст можуть відрізнятися залежно від мови чи регіону. У разі будь-яких невідповідностей чи розбіжностей переважну силу має оригінальна англомовна версія playbook.
<!-- auto-translated-disclaimer:end -->

# Запуск Hermes Agent локально за допомогою Lemonade Server

## Огляд

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) — це самовдосконалюваний AI-агент, створений компанією Nous Research. Він має вбудований цикл навчання, створює навички на основі досвіду, формує постійну пам'ять про вас у різних сесіях і може виконувати заплановані автоматизації від вашого імені. На відміну від простого чат-асистента, Hermes виконує реальні дії: запускає команди оболонки, записує файли, переглядає веб-сторінки та делегує паралельні робочі потоки підагентам.

[**Lemonade Server**](https://lemonade-server.ai/) — це локальний бекенд для інференсу, який живить його роботу. Це сервер з відкритим вихідним кодом, який запускає GenAI-моделі безпосередньо на вашому обладнанні AMD і надає до них доступ через промисловий стандарт OpenAI API.

Разом вони утворюють повністю локальний стек AI-агента: Lemonade обробляє інференс моделі на вашому GPU, а Hermes забезпечує цикл роботи агента, пам'ять, навички та шлюз обміну повідомленнями.

> **Перш ніж продовжити:** Hermes Agent — це високоавтономний AI-агент. Надання будь-якому AI-агенту доступу до вашої системи може призвести до непередбачуваних або небажаних наслідків. Продовжуйте лише в тому разі, якщо ви розумієте ризики та готові до того, що автономне програмне забезпечення діятиме від вашого імені.

---

## Чого ви навчитеся

Наприкінці цього посібника ви зможете:

- **Встановити Hermes Agent** і налаштувати його на використання **Lemonade Server** як AI-бекенда.
- **(Рекомендовано) Увімкнути пісочницю Docker/Podman** для ізоляції дій агента від вашої основної системи.
- **Запустити шлюз Hermes** і переконатися, що ваш агент готовий до роботи.
- **Підключити канал зв'язку** (Discord або Telegram), щоб ви могли спілкуватися з вашим агентом з будь-якого пристрою.

---

<!-- @device:halo_box,halo,stx,krk -->
## Налаштування конфігурації пам'яті

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Перевірка оновлень програмного забезпечення

<!-- @require:software-update -->
<!-- @device:end -->

## Встановлення необхідного програмного забезпечення

<!-- @os:linux -->
- ПК з **Ubuntu 24.04+** або сумісним дистрибутивом Linux на основі Debian з `apt-get`
- Щонайменше **12 ГБ оперативної пам'яті** (рекомендовано 64 ГБ+ для більших моделей)
- **~10–30 ГБ вільного місця на диску** для вагових коефіцієнтів моделі
- [Podman](https://podman.io/docs/installation) (необов'язково, для пісочниці Hermes Agent)
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @os:windows -->
- ПК з **Windows 10/11**
- Щонайменше **12 ГБ оперативної пам'яті** (рекомендовано 64 ГБ+ для більших моделей)
- **~10–30 ГБ вільного місця на диску** для вагових коефіцієнтів моделі
- Podman (необов'язково, для пісочниці Hermes Agent). Встановіть усередині WSL:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman попередньо встановлено на Halo Box, і додаткове налаштування не потрібне
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:hermes,lemonade-models-qwen3-35b-a3b,lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Завантажте та запустіть рекомендовану модель

Рекомендованою моделлю для цього посібника є **Qwen3.6-35B-A3B-GGUF** від Unsloth — потужна MoE-модель з вікном контексту на 263k токенів, яка добре підходить для агентних навантажень. Ця модель використовує квантування UD-Q4_K_XL. Завантажте її зараз:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Потім запустіть її з великим вікном контексту та збережіть це налаштування для майбутніх запусків:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

Модель має типову довжину контексту 262 144 токени. Якщо виникають помилки нестачі пам'яті (OOM), розгляньте можливість зменшення вікна контексту.

> **Порада: вимкніть режим "мислення" для швидших відповідей агента:** Qwen3.6-35B-A3B за замовчуванням працює в режимі "мислення", що додає затримку перед кожною відповіддю. Для циклів роботи агента ця затримка швидко накопичується. Репозиторій [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) надає готову конфігурацію, яка вимикає режим "мислення". Щоб скористатися нею, завантажте файл і імпортуйте його:
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
$entry = $parsed.data | Where-Object { $_.id -eq "${hermes_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${hermes_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${hermes_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${hermes_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${hermes_model} is not saved with ctx_size=262144. Run: lemonade load ${hermes_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${hermes_model} is saved with ctx_size=262144"

$body = @{
  model = "${hermes_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "hermes-lemonade-chat-body.json"
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
model_id = "${hermes_model}"

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
  "model": "${hermes_model}",
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

Ми запускаємо Hermes Agent усередині WSL і підключаємо його до Lemonade, яка працює нативно у Windows. Це надає середовище оболонки Linux для Hermes, зберігаючи при цьому GPU-прискорення Lemonade на боці Windows.

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

WSL2 працює у віртуальній мережі. Lemonade у Windows прив'язується до `127.0.0.1`, до якого WSL не може отримати прямий доступ. Проксі портів Windows перенаправляє трафік з IP-адреси шлюзу WSL на локальний хост Windows.

**Знайдіть IP-адресу шлюзу WSL** (виконайте всередині WSL):

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

Якщо ви вже завантажили модель Qwen3.6-35B-A3B-GGUF на попередньому кроці, ви побачите вивід у форматі JSON із переліком вашої завантаженої моделі.

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

> Правило `netsh portproxy` зберігається після перезавантаження, але IP-адреса шлюзу WSL може змінитися після `wsl --shutdown`. Якщо Lemonade стає недоступним з WSL після перезапуску, отримайте оновлену IP-адресу шлюзу та оновіть проксі з цією новою адресою.

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
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

## Встановлення Hermes Agent

<!-- @os:windows -->
> Виконуйте команди в цьому розділі всередині вашого **терміналу WSL**, якщо не вказано інше.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Прапорець `--skip-setup` пропускає інтерактивний майстер налаштування, щоб ви могли налаштувати бекенд моделі вручну на наступному кроці.

Перезавантажте вашу оболонку:

```bash
source ~/.bashrc
```

Підтвердьте встановлення:

```bash
hermes --version
```

Запустіть самодіагностику для перевірки всіх залежностей:

```bash
hermes doctor
```

> **Порада:** Якщо після встановлення ви бачите `command not found`, додайте Hermes до вашого PATH:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> Щоб зробити це постійним, додайте наведений вище рядок до вашого файлу `~/.bashrc` або `~/.zshrc`.

<!-- @os:linux -->
<!-- @test:id=hermes-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---
## Налаштування Hermes для використання Lemonade

Hermes зберігає конфігурацію моделі у файлі `~/.hermes/config.yaml`. Ви можете скористатися інтерактивним засобом вибору `hermes model` або записати конфігурацію напряму.

### Варіант 1: Інтерактивний засіб вибору

<!-- @os:windows -->
> Виконайте наступне у вашому **терміналі WSL**.
<!-- @os:end -->

<!-- @os:linux -->
```bash
hermes model
```
<!-- @os:end -->

<!-- @os:windows -->
```bash
hermes model
```
<!-- @os:end -->

Коли з'явиться запит:

1. Виберіть **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** скористайтеся IP-адресою шлюзу WSL: виконайте `ip route show default | awk '{print $3}' | head -1` у WSL, щоб отримати її, а потім введіть `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1` (Автовизначення)
5. **Select model:** оберіть `Qwen3.6-35B-A3B-GGUF` зі списку
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade` (або будь-яку назву на ваш розсуд)

`hermes model` зберігає як активний вибір моделі, так і іменований запис `custom_providers`, у якому разом із кінцевою точкою зберігається довжина контексту. Результат у `~/.hermes/config.yaml` виглядає так:

```yaml
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
```

### Варіант 2: Пряме редагування конфігурації

<!-- @os:linux -->

```bash
mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->

У терміналі WSL отримайте IP-адресу хоста Windows та запишіть конфігурацію:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"
if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration (Windows host)"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-lemonade-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes Lemonade config check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---

## (Рекомендовано) Увімкнення пісочниці Podman

Hermes Agent може спрямовувати всі операції агента з оболонкою та файлами через ізольований контейнер замість їх виконання безпосередньо на вашому хості. Це обмежує вплив будь-якої непередбаченої дії лише пісочницею, залишаючи файлову систему та мережу вашого хоста недоторканими.

Створіть легковаговий образ пісочниці:

<!-- @os:linux -->
```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

<!-- @test:id=hermes-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
Увійдіть у ваш термінал WSL:

```powershell
wsl -d Ubuntu-24.04
```

Потім створіть легковаговий образ пісочниці:

```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

<!-- @test:id=hermes-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Потім налаштуйте Hermes на використання Podman як середовища виконання контейнерів та встановіть серверну частину терміналу:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> `terminal.backend` залишається `docker`.
> Саме `HERMES_DOCKER_BINARY` вказує Hermes використовувати Podman як середовище виконання замість Docker.

<!-- @os:linux -->
<!-- @test:id=hermes-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

# The sandbox image must exist before Hermes can use it as the terminal backend.
podman image inspect hermes-sandbox:bookworm-slim >/dev/null

# Point Hermes at Podman as the container runtime (idempotent: drop any prior line first).
mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

# Append the terminal backend block (config.yaml is rewritten fresh by the model-config test each run, so this appends exactly once per run).
cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox config failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Тепер Hermes запустить постійний контейнер-пісочницю та спрямовуватиме всі виклики `terminal` та файлових інструментів через нього. Контейнер існує протягом усього життєвого циклу процесу Hermes, повторно використовується для всіх викликів інструментів і знищується при завершенні роботи Hermes.

> **Перевірка роботи пісочниці:** запустіть Hermes (`hermes`) і попросіть його виконати `run hostname` — ви повинні побачити короткий ідентифікатор контейнера замість імені вашого хосту. Також можна попросити виконати `rm -rf <path-to-a-dummy-file/folder>`: Hermes підтвердить видалення, але папка залишиться на вашому хості. Команда була виконана всередині ізольованого `$HOME` контейнера, а не вашого.

> **Потрібна сильніша ізоляція?** Hermes також надає офіційний образ Docker (`nousresearch/hermes-agent`), який запускає весь процес агента всередині контейнера — шлюз, інструменти і все інше. Докладніше про налаштування див. у [документації Hermes Docker](https://hermes-agent.nousresearch.com/docs/user-guide/docker).

---

<!-- @os:linux -->
## (Рекомендовано) Інтеграція Hermes із сервісами Firecrawl

Hermes може переглядати та видобувати вміст із вебсайтів за допомогою своїх вбудованих вебінструментів. Однак багато сучасних вебсайтів використовують системи виявлення ботів, які блокують прості HTTP-запити та повертають сторінки з перевіркою замість фактичного вмісту. Через це Hermes може не мати можливості надійно видобувати інформацію з таких сайтів.

Щоб подолати це обмеження, [Firecrawl](https://docs.firecrawl.dev/introduction) надає сервіс для самостійного розгортання, який виконує сканування вебсторінок та видобування вмісту та може обходити ці перевірки, розкриваючи повний потенціал автоматизації Hermes.

У цьому налаштуванні Firecrawl працює як набір контейнерів Docker, якими керує Podman. Щоб спростити керування життєвим циклом та автоматичний запуск, ми реєструємо Firecrawl як сервіс `systemd` рівня користувача, який оркеструє базовий стек Podman Compose. Це дозволяє Hermes запускати, зупиняти та перевіряти сервіс Firecrawl за допомогою стандартних команд `systemctl --user` замість безпосередньої взаємодії з контейнерами.

Щоб усе було простіше, ми розбили весь процес на чотири кроки:

---

### 1. Реєстрація системного сервісу
Перейдіть до каталогу конфігурації користувача systemd:
```bash
cd ~/.config/systemd/user
```
Створіть і відкрийте новий файл під назвою `firecrawl.service`.
```bash
nano firecrawl.service
```
Скопіюйте та вставте таку конфігурацію:
```bash
[Unit]
Description=Firecrawl
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${HOME}/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman -f hermes-compose.yaml config --quiet

# Start containers in detached mode
ExecStart=/usr/bin/podman compose -f hermes-compose.yaml up -d --remove-orphans

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f hermes-compose.yaml down

[Install]
WantedBy=default.target

```
На цьому етапі сервіс визначено, але ще не зареєстровано у `systemd`.
Переконайтеся, що назва файлу точно відповідає тій, яку ви створили вище, а потім виконайте:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
У разі успіху ви повинні побачити такий результат:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` містить символьні посилання на сервіси, налаштовані на автоматичний запуск.

### 2. Налаштування Firecrawl для вашого сервісу

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) ідеально підходить для тих, кому потрібен повний контроль над середовищем скрапінгу та обробки даних, але це супроводжується додатковими витратами на обслуговування та налаштування.

Почніть з клонування репозиторію:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Створіть файл `.env` у кореневому каталозі `/firecrawl`:
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY=""

# ===== Proxy =====
# PROXY_SERVER can be a full URL (e.g. http://0.1.2.3:1234) or just an IP and port combo (e.g. 0.1.2.3:1234)
# Do not uncomment PROXY_USERNAME and PROXY_PASSWORD if your proxy is unauthenticated
# PROXY_SERVER=
# PROXY_USERNAME=
# PROXY_PASSWORD=

# This key lets you access the queue admin panel. Change this if your deployment is publicly accessible.
BULL_AUTH_KEY=CHANGEME

# ===== System Resource Configuration =====
# Maximum CPU usage threshold (0.0-1.0). Worker will reject new jobs when CPU usage exceeds this value.
# Default: 0.8 (80%)
# MAX_CPU=0.8

# Maximum RAM usage threshold (0.0-1.0). Worker will reject new jobs when memory usage exceeds this value.
# Default: 0.8 (80%)
# MAX_RAM=0.8
```
> Встановіть для `BULL_AUTH_KEY` надійний секретний ключ, особливо для будь-якого розгортання, доступного з ненадійних мереж.
### 3. Розгортання Hermes через Compose

Перш ніж продовжити, переконайтеся, що ви завантажили останній Docker-образ Hermes:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
Після цього завантажте файл Compose для Hermes [hermes-compose.yaml](assets/hermes-compose.yaml) і помістіть його в кореневий каталог `/firecrawl`:

> Ця домовленість необхідна для того, щоб `systemd` міг знайти та запустити службу коректно, як зазначено в `WorkingDirectory=${HOME}/firecrawl`.

> Ви завжди можете розширити стек, додаючи додаткові служби Firecrawl за потреби. Повний перелік доступних служб можна знайти в офіційному файлі [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Запуск служби Hermes через Firecrawl 

Перш ніж передати керування `systemd`, переконайтеся, що все працює коректно, запустивши стек вручну:
```bash
podman compose -f hermes-compose.yaml up -d
```
Якщо все налаштовано правильно, ви повинні побачити, що контейнер Hermes запустився, а вивід командного рядка має виглядати приблизно так:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

Після перевірки зупиніть стек, перш ніж продовжити:
```bash
podman compose -f hermes-compose.yaml down
```
Тепер, коли все перевірено, запустіть службу через `systemd`:
```bash
systemctl --user start firecrawl.service
```
[API Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) доступний зсередини інтерактивного контейнера, а веб-панель доступна на тому ж хості та порту за адресою http://127.0.0.1:9119.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

Щоб зупинити службу, виконайте:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native

Запустіть інтерактивну CLI-сесію безпосередньо: 

```bash
hermes
```

<!-- @os:linux -->
<!-- @test:id=hermes-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started successfully"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started inside WSL"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

**Вітаємо, ви створили повністю локальний стек ШІ-агента.**

### Веб-панель

Hermes включає веб-інтерфейс у браузері для керування конфігурацією, ключами API, моделями, сесіями, пам'яттю та запланованими завданнями (cron jobs). Відкрийте другий термінал, поки шлюз або CLI працює, і запустіть його за допомогою:

```bash
hermes dashboard
```

Це запускає локальний сервер і відкриває `http://127.0.0.1:9119` у вашому браузері. Дивіться [документацію панелі](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard) для повного опису функцій.
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## Необов'язково: підключення каналу зв'язку

Коли шлюз запущено, ви можете звертатися до свого локального агента з будь-якого пристрою. Hermes підтримує [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) та інші

---

### Discord

Для Discord потрібен сервер, на якому **у вас є права адміністратора**, щоб додати бота. Якщо ви перебуваєте на спільних серверах, але не володієте жодним, скористайтеся Telegram.

#### Створення застосунку та бота Discord

1. Перейдіть на [Discord Developer Portal](https://discord.com/developers/applications) і натисніть **New Application**. Дайте йому назву (наприклад, "hermes-bot").
2. На бічній панелі натисніть **Bot**. Встановіть ім'я користувача для бота.
3. Залишаючись на сторінці Bot, прокрутіть до **Privileged Gateway Intents** і увімкніть:
   - **Message Content Intent** (обов'язково)
   - **Server Members Intent** (рекомендовано)
4. Прокрутіть назад догори та натисніть **Reset Token**, щоб згенерувати токен бота. Скопіюйте його.

#### Додавання бота на ваш сервер

1. На бічній панелі натисніть **OAuth2 / URL Generator**.
2. У розділі **Scopes** увімкніть `bot` і `applications.commands`.
3. У розділі **Bot Permissions** увімкніть: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Скопіюйте згенероване посилання, вставте його у браузер, виберіть свій сервер і підтвердьте.

#### Збір ваших ID та дозвіл на особисті повідомлення

Увімкніть режим розробника в Discord (**User Settings / Advanced / Developer Mode**), потім:
- Клацніть правою кнопкою миші на значку сервера: **Copy Server ID**
- Клацніть правою кнопкою миші на своєму аватарі: **Copy User ID**

Клацніть правою кнопкою миші на значку сервера / **Privacy Settings** / увімкніть **Direct Messages**. Це необхідно для етапу з'єднання (pairing).

#### Налаштування Hermes для Discord

Додайте наступне до `~/.hermes/.env`:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

Потім запустіть шлюз:

```bash
hermes gateway
```

Бот має з'явитися онлайн у Discord протягом кількох секунд. Надішліть йому повідомлення — особисте або в каналі, який він бачить.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Створення бота Telegram

1. Відкрийте Telegram і напишіть **@BotFather**.
2. Надішліть `/newbot` і дотримуйтеся підказок. Збережіть токен бота, який він надасть.

#### Налаштування Hermes для Telegram

Додайте наступне до `~/.hermes/.env`:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **Не знаєте свій ID користувача Telegram?** Напишіть [@userinfobot](https://t.me/userinfobot) у Telegram, і він відповість вашим числовим ID.

Потім запустіть шлюз:

```bash
hermes gateway
```

Надішліть боту будь-яке повідомлення в Telegram для перевірки. Тепер ви можете спілкуватися зі своїм агентом через особисті повідомлення Telegram. Дивіться [повний посібник з налаштування Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) для режиму webhook та додаткових опцій.

---

## Наступні кроки

Тепер, коли ваш агент може отримувати команди з телефону та діяти на вашому локальному комп'ютері, ось три напрямки, варті дослідження:

1. **Автоматизована дослідницька розсилка**: Налаштуйте Hermes на пошук в інтернеті тем, які вас цікавлять, щоранку, узагальнення результатів вашою локальною моделлю та надсилання дайджесту на ваш телефон через Telegram або Discord — все це працює на вашому власному обладнанні без витрат на хмарні сервіси.

2. **Рецензування коду за запитом**: Направте Hermes на репозиторій GitHub, попросіть переглянути відкриті pull requests і опублікувати коментарі або підсумок назад у вашому чаті. Завдяки Docker-бекенду терміналу всі операції git виконуються всередині пісочниці, залишаючи ваш хост чистим.

3. **Локальний файловий помічник**: Надайте Hermes доступ до робочого каталогу та попросіть організовувати, перейменовувати, узагальнювати чи перетворювати файли за запитом з вашого телефону. Оскільки Docker-бекенд терміналу обмежує весь запис простором пісочниці, випадкові руйнівні операції локалізовані.