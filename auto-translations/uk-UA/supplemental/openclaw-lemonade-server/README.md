<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинний переклад.** Цю сторінку було автоматично перекладено з англійської мови, і вона не була перевірена людиною. Вона може містити помилки, а певні інструкції, команди, завантаження, доступність продукту чи інший вміст можуть відрізнятися залежно від мови чи регіону. У разі будь-яких невідповідностей чи розбіжностей переважну силу має оригінальна англомовна версія playbook.
<!-- auto-translated-disclaimer:end -->

# Запуск OpenClaw із Lemonade Server як бекенд

## Огляд

[**OpenClaw**](https://openclaw.ai/) — це автономний AI-агент, який може писати та виконувати код, керувати файлами та виконувати складні багатоетапні завдання від вашого імені. На відміну від чат-асистента, який лише відповідає на запитання, OpenClaw виконує реальні дії у вашій системі, а це означає, що йому потрібен швидкий, потужний AI-бекенд, здатний встигати за вимогливим циклом роботи агента.

[**Lemonade Server**](https://lemonade-server.ai/) — саме такий бекенд. Це локальний сервер інференсу з відкритим кодом, який запускає GenAI-моделі безпосередньо на вашому обладнанні та надає до них доступ через стандартний для галузі API OpenAI.

Разом вони утворюють повністю локальний стек AI-агента: Lemonade обробляє інференс моделі, а OpenClaw забезпечує цикл роботи агента, який перетворює результати моделі на реальні дії.

> **Перш ніж продовжити:** OpenClaw — це високоавтономний AI-агент. Надання будь-якому AI-агенту доступу до вашої системи може призвести до непередбачуваних або небажаних наслідків. Продовжуйте, лише якщо ви розумієте ризики та готові до того, що автономне програмне забезпечення діятиме від вашого імені.

---

## Що ви дізнаєтесь

Наприкінці цього посібника ви зможете:

- Дізнатися про **Lemonade Server**
- **Встановити OpenClaw** та **налаштувати його на Lemonade Server** як AI-бекенд.
- **Запустити шлюз OpenClaw** і переконатися, що ваш агент готовий до роботи.
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
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (необов'язково, для пісочниці OpenClaw)
- **~10–30 ГБ вільного місця на диску** для ваг моделі
<!-- @os:end -->

<!-- @os:windows -->
- ПК з **Windows 10/11**
- Щонайменше **12 ГБ оперативної пам'яті** (рекомендовано 64 ГБ+ для більших моделей)
- **~10–30 ГБ вільного місця на диску** для ваг моделі
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (необов'язково, для пісочниці OpenClaw)
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

Рекомендованою моделлю для цього посібника є **Qwen3.6-35B-A3B-GGUF** від Unsloth — потужна MoE-модель з вікном контексту у 263 тисячі токенів, яка добре підходить для агентних навантажень. Ця модель використовує квантування UD-Q4_K_XL. Завантажте її зараз:

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

Модель має типову довжину контексту 262 144 токени. Якщо ви стикаєтеся з помилками нестачі пам'яті (OOM), розгляньте можливість зменшення вікна контексту. Однак, оскільки Qwen3.6 використовує розширений контекст для складних завдань, ми рекомендуємо підтримувати довжину контексту щонайменше 128К токенів, щоб зберегти можливості мислення.

> **Порада: вимкніть режим мислення для швидших відповідей агента:** Qwen3.6-35B-A3B за замовчуванням працює в режимі мислення, що додає затримку перед кожною відповіддю. Для циклів роботи агента ця затримка швидко накопичується. Репозиторій [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) містить готову конфігурацію, яка вимикає мислення. Щоб її використати, завантажте файл та імпортуйте його:
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

Ми запускаємо OpenClaw всередині WSL (рекомендовано) і підключаємо його до Lemonade, що працює нативно на Windows. Це надає вам середовище оболонки Linux для OpenClaw, зберігаючи GPU-прискорення Lemonade на стороні Windows.

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

Вийдіть із WSL і перезапустіть його:

```powershell
exit
wsl --shutdown
wsl
```

### З'єднання Lemonade з Windows у WSL

WSL2 працює у віртуальній мережі. Lemonade на Windows прив'язується до `127.0.0.1`, до якого WSL не може напряму отримати доступ. Проксі-порт Windows перенаправляє трафік з IP-адреси шлюзу WSL на локальний хост Windows.

**Знайдіть IP-адресу шлюзу WSL** (виконайте всередині WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Додайте проксі-порт** (виконайте в PowerShell від імені адміністратора, замінивши `<WSL-Gateway-IP>` на вашу IP-адресу шлюзу WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Примітка: якщо ви стикаєтесь із помилкою `netsh: command not found`, спробуйте використати явну назву виконуваного файлу — `netsh.exe`

**Додайте правило брандмауера** (у тому ж PowerShell з правами адміністратора):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Перевірте з WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Якщо ви вже завантажили модель Qwen3.6-35B-A3B-GGUF на попередньому кроці, ви маєте побачити вивід JSON на кшталт цього:

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

#### Підтримка роботи мосту після перезапуску

Правило `netsh portproxy` зберігається після перезавантаження, але IP-адреса шлюзу WSL може змінюватися після `wsl --shutdown` або перезавантаження. Коли це відбувається, проксі все ще вказує на стару IP-адресу, і Lemonade стає недоступним із WSL. Якщо це сталося, скористайтеся одним із варіантів нижче.

**Варіант 1 (рекомендовано) — Автоматичне відновлення мосту.** Щоб уникнути виконання цього вручну щоразу, використовуйте заплановане завдання, яке перевіряє міст під час кожного запуску та входу в систему й перебудовує його лише тоді, коли IP-адреса шлюзу змінилася. Див. [посібник з автоматичного відновлення мосту Lemonade WSL](assets/RepairLemonadeWslBridge.md).


**Варіант 2 — Ручне відновлення мосту.** Спочатку отримайте поточну IP-адресу шлюзу WSL, виконавши цю команду всередині WSL:

```bash
ip route show default | awk '{print $3}' | head -1
```

Скопіюйте це значення; ви використаєте його замість `<new-WSL-Gateway-IP>` нижче.

Потім у **PowerShell із підвищеними правами** (запустіть від імені адміністратора) перелічіть наявні правила, видаліть лише застаріле правило Lemonade та додайте нове з поточною IP-адресою:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

У виведенні `show all` застаріле правило Lemonade — це запис, адреса підключення якого `127.0.0.1` на порту `13305`; його адреса прослуховування — це ваша `<old-WSL-Gateway-IP>`. Видалення за цією адресою прибирає лише це правило, залишаючи будь-які інші правила port-proxy на вашому комп'ютері незмінними.

Правило брандмауера, яке ви додали під час налаштування, прив'язане до порту `13305` (а не до IP-адреси), тому воно продовжує працювати і не потребує повторного створення.

> **Рекомендація:** Щоб уникнути проблем зі шлюзом, ми настійно рекомендуємо таку конфігурацію оболонки:
> - **Команди Windows** слід виконувати в **PowerShell**
> - **Команди дистрибутива WSL** слід виконувати в **командному рядку** (запущеному від імені **адміністратора**)

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
> Виконуйте команди в цьому розділі всередині вашого **терміналу WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Прапорець `--no-onboard` пропускає інтерактивний майстер налаштування, ви налаштуєте бекенд моделі вручну на наступному кроці, що дає вам точний контроль над тим, яка модель і сервер використовуються.

Відкрийте новий термінал і підтвердіть встановлення:

```bash
openclaw --version
```

> **Порада:** Якщо після встановлення ви бачите `command not found`, додайте глобальний каталог bin npm до вашого PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Щоб зробити це постійним, додайте рядок вище до вашого файлу `~/.bashrc` або `~/.zshrc`.

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

Запустіть неінтерактивне налаштування OpenClaw.
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

Ця команда записує конфігурацію OpenClaw у `~/.openclaw/openclaw.json`.

> **Розмір контекстного вікна OpenClaw:** Стиснення (compaction) OpenClaw запускається, коли `contextTokens > contextWindow − reserveTokens`. Стандартне значення `reserveTokensFloor` становить 20 000 токенів — це нижня межа, яка перевизначає `reserveTokens`, коли воно нижче, тому будь-яке контекстне вікно моделі менше ~37k спричинить нескінченний цикл стиснення. Встановіть низький резерв і вимкніть нижню межу один раз у вашій конфігурації, і це застосовуватиметься до кожної моделі, налаштування для кожної моделі окремо не потрібне:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` — це *нижня межа* (мінімальна гарантія), а не сам резерв, встановлення лише нижньої межі не має ефекту. `reserveTokensFloor: 0` вимикає гарантію, тому нижче значення `reserveTokens` приймається.
>
> **Коли це застосовувати:** Використовуйте цю конфігурацію, якщо ефективне контекстне вікно вашої моделі менше ~37k, чи то тому, що модель мала (наприклад, 8k, 16k, 32k), чи то тому, що ви навмисно обмежили його нижчим значенням (наприклад, завантажили модель на 128k, але встановили контекст 16k у Lemonade). Без цього OpenClaw входить у нескінченний цикл стиснення під час запуску.
>
> **Моделі з великим контекстом на повному контексті:** Ви можете повністю пропустити це. Стандартні значення працюють добре, стиснення спрацює задовго до заповнення вікна, і модель має достатньо простору для генерації довгих відповідей. Якщо ви все ж застосуєте це, майте на увазі, що `reserveTokens: 4096` обмежує довжину відповіді приблизно 4k токенів, що може обрізати генерацію довгих файлів або детальні плани.
>
> **Куди це додати:** Розмістіть блок `compaction` всередині `agents.defaults` у вашому `openclaw.json` (зазвичай за адресою `~/.openclaw/openclaw.json`):
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
> Решта вашої конфігурації (gateway, канали, моделі тощо) залишається незмінною, потрібно додати лише ключ `compaction`.
### (Рекомендовано) Увімкнення пісочниці Docker

OpenClaw може спрямовувати всі файлові та кодові операції агента через ізольований контейнер Docker, а не виконувати їх безпосередньо на вашому хості. Це обмежує радіус впливу будь-якої ненавмисної дії лише пісочницею, залишаючи файлову систему та мережу вашого хоста недоторканими.

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

Виконайте це, щоб додати ключ `sandbox` всередині наявного блоку `agents.defaults` у файлі `~/.openclaw/openclaw.json`:

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

Контейнери пісочниці **не мають доступу до мережі** за замовчуванням. Дивіться [довідку щодо пісочниць](https://docs.openclaw.ai/gateway/sandboxing) для монтування каталогів та перевизначення мережевих параметрів.

> #### Усунення несправностей: Docker Permission Denied
> 
> Якщо ви отримуєте помилку "permission denied" під час виконання команд Docker:
> 
> **Крок 1: Додайте свого користувача до групи docker**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **Крок 2: Якщо помилка не зникає, застосуйте постійне виправлення**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Потім **перезавантажте** свою систему.
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

<!-- @os:linux -->
## (Рекомендовано) Інтеграція OpenClaw з сервісами Firecrawl

[Firecrawl](https://docs.firecrawl.dev/introduction) надає самостійно розміщувану службу веб-краулінгу та вилучення контенту, яка може обійти ці обмеження та розкрити весь потенціал автоматизації OpenClaw. 

У цьому налаштуванні OpenClaw працює як набір контейнерів Docker, керованих за допомогою Podman. Щоб спростити керування життєвим циклом та автоматичний запуск, ми реєструємо Firecrawl як службу `systemd` рівня користувача, яка керує базовим стеком Podman Compose. Це дозволяє OpenClaw запускати шлюз, зупиняти та перевіряти службу Firecrawl за допомогою стандартних команд `systemctl --user` замість безпосередньої взаємодії з контейнерами. 

Щоб усе було просто, ми розбили весь процес на чотири кроки:

---

### 1. Реєстрація системної служби
Перейдіть до каталогу конфігурації користувача systemd:
```bash
cd ~/.config/systemd/user
```
Створіть та відкрийте новий файл під назвою `firecrawl.service`.
```bash
nano firecrawl.service
```
Скопіюйте та вставте наступну конфігурацію:
```bash
[Unit]
Description=OpenClaw Firecrawl Service
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=%h/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman compose -f openclaw-compose.yaml config --quiet

# Generate token and write to .env file
ExecStartPre=/bin/bash -c 'chmod 644 %h/firecrawl/.env && echo "OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 32)" > %h/firecrawl/.env'

# Step 1: Start containers in detached mode
ExecStart=/usr/bin/podman compose -f openclaw-compose.yaml up -d --remove-orphans

# Step 2: Wait for container to be healthy/ready
ExecStartPost=/bin/sleep 5

# Step 3: Run onboarding inside container in detached mode
ExecStartPost=/usr/bin/podman exec -d openclaw_gateway /bin/bash -c "openclaw onboard \
    --non-interactive \
    --accept-risk \
    --mode local \
    --auth-choice skip \
    --gateway-auth token \
    --gateway-token "$OPENCLAW_GATEWAY_TOKEN" "

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f openclaw-compose.yaml down

[Install]
WantedBy=default.target
```
На цьому етапі службу вже визначено, але ще не зареєстровано в `systemd`. 
Переконайтеся, що назва файлу точно відповідає тій, яку ви створили вище, потім виконайте:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
Якщо все пройшло успішно, ви побачите наступне виведення:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` містить символічні посилання на служби, налаштовані на автоматичний запуск.

### 2. Налаштування Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) ідеально підходить для тих, кому потрібен повний контроль над середовищами скрапінгу та обробки даних, але має компроміс у вигляді додаткових зусиль на обслуговування та налаштування.

Почніть з клонування репозиторію:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Створіть `.env` у кореневому каталозі `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Розгортання OpenClaw за допомогою Podman Compose

Перш ніж продовжити, переконайтеся, що ви завантажили останній образ Docker для OpenClaw:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
Після цього завантажте файл Compose для OpenClaw [openclaw-compose.yaml](assets/openclaw-compose.yaml) та розмістіть його в кореневому каталозі `/firecrawl`:

> Ця угода необхідна для того, щоб `systemd` міг коректно знайти та запустити службу, як зазначено в `WorkingDirectory=${HOME}/firecrawl`.

> Ви завжди можете розширити стек, додаючи додаткові служби Firecrawl за потреби. Повний список доступних служб можна знайти в офіційному файлі [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Запуск служби OpenClaw через Firecrawl 

Перш ніж передати контроль `systemd`, перевірте, що все працює правильно, запустивши стек вручну:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Якщо все налаштовано правильно, ви побачите, що контейнер OpenClaw піднявся, і виведення командного рядка має виглядати приблизно так:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Після перевірки зупиніть стек, перш ніж продовжити:
```bash
podman compose -f openclaw-compose.yaml down
```
Перш ніж запускати службу, необхідно переконатися, що для каталогу `firecrawl` та його файлу `.env` встановлено правильного власника та дозволи. 
Це важливо для того, щоб служба могла записати ваші облікові дані під час запуску.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Тепер, коли все перевірено, запустіть службу через `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Дії OpenClaw](https://docs.openclaw.ai/) доступні зсередини інтерактивного контейнера, а веб-панель доступна на тому самому хості та порту за адресою http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Отримання вашого `OPENCLAW_GATEWAY_TOKEN`

Щойно служба запуститься та запрацює, ви побачите, що у вашій домашній теці створено новий каталог `.openclaw` (~/.openclaw). Цей каталог за замовчуванням заблоковано, тому вам потрібно розблокувати його, щоб отримати токен шлюзу.

1. Надайте доступ до каталогу:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Прочитайте свій токен шлюзу:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Знайдіть значення `OPENCLAW_GATEWAY_TOKEN` у виведенні.

3. Відкрийте панель шлюзу у своєму браузері за адресою http://127.0.0.1:18789. Вставте свій токен, коли з'явиться запит на автентифікацію.

Щоб зупинити службу, виконайте:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Запуск шлюзу OpenClaw (OpenClaw Gateway)

Шлюз — це процес OpenClaw, який керує циклом агента та обслуговує панель керування:

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

Щоб відкрити панель керування, виконайте це у другому терміналі, поки шлюз усе ще працює:

```bash
openclaw dashboard
```

Оскільки шлюз прив’язується до loopback, панель керування автоматично автентифікується при відкритті з того самого пристрою — введення токена чи схвалення пристрою для локального доступу не потрібне. Ви маєте побачити панель керування OpenClaw, де ваша модель Lemonade вказана як активний бекенд.

> Якщо ви увімкнули пісочницю (sandboxing), перевірити її роботу можна, попросивши агента виконати `run hostname` з панелі керування. Якщо замість імені хосту вашого пристрою ви бачите короткий ID контейнера, пісочниця працює.

**Вітаємо, ви створили повністю локальний стек AI-агента з нуля.**

> **Потрібен токен шлюзу?** Виконайте `openclaw dashboard --no-open`, щоб вивести URL панелі керування з вбудованим токеном (також буде здійснена спроба скопіювати його в буфер обміну). Крім того, токен зберігається у `gateway.auth.token` у файлі `~/.openclaw/openclaw.json`.

**Доступ до панелі керування з іншого пристрою (через SSH-тунель)**

Якщо OpenClaw працює на віддаленому пристрої, ви можете отримати доступ до його панелі керування зі свого локального пристрою через SSH-тунель. Тунель перенаправляє порт шлюзу (`18789`), щоб ваш локальний браузер міг спілкуватися з віддаленим шлюзом через `127.0.0.1`.

1. На своєму **локальному пристрої** підключіться до віддаленого пристрою один раз і підтвердьте запит на відбиток ключа, щоб хост додався до списку відомих хостів:

   ```bash
   ssh user@<host-ip>
   ```

2. Далі на своєму **локальному пристрої** відкрийте SSH-тунель:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Примітка:** після введення пароля термінал не показує жодного виводу і виглядає так, ніби завис. Це очікувана поведінка: прапорець `-N` вказує SSH не виконувати жодних віддалених команд, тому він просто утримує тунель відкритим. Залиште цей термінал працювати.

3. На своєму **локальному пристрої** відкрийте браузер і перейдіть за адресою `http://127.0.0.1:18789`.

4. На **віддаленому пристрої** виведіть токен шлюзу та вставте його в браузер для входу:

   ```bash
   openclaw dashboard --no-open
   ```

   Ця команда виводить URL панелі керування з вбудованим токеном; скопіюйте токен для входу. (Токен також зберігається у `gateway.auth.token` у файлі `~/.openclaw/openclaw.json`.)

> **Схвалення віддаленого пристрою:** коли ви відкриваєте панель керування з іншого пристрою чи телефону, браузер може показати ID запиту. На **віддаленому пристрої** перегляньте список запитів, що очікують на схвалення:
> ```bash
> openclaw devices list
> ```
> Потім схваліть відповідний запит:
> ```bash
> openclaw devices approve <requestId>
> ```
> Це потрібно лише для віддалених або додаткових пристроїв; доступ через loopback з того самого пристрою автентифікується автоматично. Детальніше див. у документації [Remote Access](https://docs.openclaw.ai/gateway/remote).

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Додатково: підключення каналу зв’язку

Після запуску шлюзу ви можете отримати доступ до свого локального агента з будь-якого пристрою. Виберіть варіант, що підходить для вашої конфігурації. OpenClaw підтримує [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) та інші канали — повний список див. на [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Варіант A: Discord

Для Discord потрібен сервер, на якому **ви маєте права адміністратора**, щоб додати бота. Якщо ви є учасником спільних серверів, але не володієте жодним з них, скористайтеся варіантом B (Telegram).

#### Створення облікового запису та сервера Discord

Якщо у вас немає облікового запису Discord, зареєструйтеся на [discord.com](https://discord.com). Вам також потрібен сервер, на якому ви є адміністратором — створіть його, натиснувши іконку **+** на бічній панелі Discord і вибравши **Create My Own**. Приватний сервер цілком підійде.

#### Створення застосунку та бота Discord

1. Перейдіть до [Discord Developer Portal](https://discord.com/developers/applications) і натисніть **New Application**. Дайте йому назву (наприклад, «openclaw-bot»).
2. На бічній панелі натисніть **Bot**. Задайте ім’я користувача для бота.
3. Не покидаючи сторінку Bot, прокрутіть до **Privileged Gateway Intents** і увімкніть:
   - **Message Content Intent** (обов’язково)
   - **Server Members Intent** (рекомендовано)
4. Прокрутіть назад догори та натисніть **Reset Token**, щоб згенерувати токен бота. Скопіюйте його.

#### Додавання бота на ваш сервер

1. На бічній панелі натисніть **OAuth2/ URL Generator**.
2. У розділі **Scopes** увімкніть `bot` та `applications.commands`.
3. У розділі **Bot Permissions** увімкніть: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Скопіюйте згенерований URL, вставте його у браузер, виберіть свій сервер і підтвердьте. Бот має з’явитися у списку учасників вашого сервера.

#### Збір ваших ID

Увімкніть режим розробника в Discord (**User Settings/ Advanced/ Developer Mode**), потім:
- Клацніть правою кнопкою миші на іконці сервера: **Copy Server ID**
- Клацніть правою кнопкою миші на своєму аватарі: **Copy User ID**

#### Дозвіл на особисті повідомлення від учасників сервера

Клацніть правою кнопкою миші на іконці сервера / **Privacy Settings** / увімкніть перемикач **Direct Messages**. Це дозволить боту надсилати вам особисті повідомлення, що необхідно для етапу пов’язування (pairing).

#### Налаштування OpenClaw для Discord

Збережіть токен вашого бота як змінну середовища, а потім створіть єдиний файл-патч, який вмикає Discord, посилається на токен і додає ваш сервер до дозволеного списку. Замініть `<server_id>` та `<user_id>` на ID, зібрані вище.

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

> **Не покладайтеся на прохання до агента налаштувати це.** Коли увімкнено пісочницю, агент не може записувати у `~/.openclaw/openclaw.json` зсередини пісочниці — натомість використовуйте наведені вище команди CLI на хості.

Перезапустіть шлюз, щоб застосувати нову конфігурацію каналу:

```bash
openclaw gateway run --bind loopback --port 18789
```

Протягом кількох секунд у виводі шлюзу ви маєте побачити `logged in to discord as <bot-name>`.
#### Прив'яжіть свій обліковий запис Discord

Напишіть боту в Discord. Він відповість коротким кодом прив'язки.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Підтвердіть це на машині, що виконує OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Коди прив'язки діють протягом однієї години.

Тепер ви можете спілкуватися зі своїм агентом безпосередньо з Discord і передавати завдання на власне обладнання.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Варіант B: Telegram

Telegram простіший за Discord для більшості користувачів — він не вимагає ані сервера, ані прав адміністратора.

#### Створення бота Telegram

1. Відкрийте Telegram і напишіть **@BotFather**.
2. Надішліть `/newbot` і дотримуйтеся підказок. Збережіть токен бота, який він видасть.

#### Налаштування OpenClaw для Telegram

Збережіть токен як змінну середовища:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Додайте конфігурацію каналу до `~/.openclaw/openclaw.json` (або внесіть зміни через панель керування):

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

Перезапустіть шлюз, потім надішліть боту будь-яке повідомлення в Telegram. Підтвердіть прив'язку:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Коди прив'язки діють протягом однієї години. Тепер ви можете спілкуватися зі своїм агентом через особисті повідомлення в Telegram.

---

## Наступні кроки

Тепер, коли ваш агент може отримувати команди з телефону та виконувати дії на вашій локальній машині, ось три напрямки, які варто дослідити:

1. **Узагальнювач фондового ринку**: Налаштуйте OpenClaw на отримання даних з фінансових API з фіксованим інтервалом, узагальнення денних рухів за допомогою вашої локальної моделі та надсилання дайджесту на ваш телефон щоранку через обраний вами канал.

2. **Монітор донавчання**: Запустіть завдання навчання віддалено через Telegram або Discord, а потім нехай агент відстежує журнал навчання та періодично повідомляє про значення втрат, використання GPU та дискового простору на ваш телефон. Якщо процес зупиняється або відбувається сплеск використання VRAM, ви дізнаєтесь про це негайно, не перебуваючи біля машини.

3. **IOT з локальною VLM**: Направте камеру на вхідні двері, запустіть модель зору на Lemonade і нехай OpenClaw аналізує кадри на вимогу або за тригером. Запитайте "чи прийшли сьогодні якісь посилки?" зі свого телефону та отримайте пряму відповідь від власного обладнання.

<!-- @os:linux -->
<!-- @test:id=lemonade-unload-linux timeout=60 hidden=True -->
```bash
# CI cleanup: unload the model so the GPU pool is free
lemonade unload || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-unload-windows timeout=60 hidden=True -->
```powershell
# CI cleanup: unload the model so the GPU pool is free
lemonade unload
exit 0
```
<!-- @test:end -->
<!-- @os:end -->