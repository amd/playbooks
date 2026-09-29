<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинний переклад.** Цю сторінку було автоматично перекладено з англійської мови, і вона не була перевірена людиною. Вона може містити помилки, а певні інструкції, команди, завантаження, доступність продукту чи інший вміст можуть відрізнятися залежно від мови чи регіону. У разі будь-яких невідповідностей чи розбіжностей переважну силу має оригінальна англомовна версія playbook.
<!-- auto-translated-disclaimer:end -->

# Запустіть OpenClaw із Lemonade Server як бекенд

## Огляд

[**OpenClaw**](https://openclaw.ai/) — це автономний AI-агент, який може писати та виконувати код, керувати файлами та виконувати складні багатоетапні завдання від вашого імені. На відміну від чат-асистента, який лише відповідає на запитання, OpenClaw виконує реальні дії у вашій системі, а це означає, що йому потрібен швидкий і потужний AI-бекенд, здатний встигати за вимогливим циклом роботи агента.

[**Lemonade Server**](https://lemonade-server.ai/) — це саме такий бекенд. Це проривний сервер локального інференсу з відкритим кодом, який запускає GenAI-моделі безпосередньо на вашому обладнанні та надає до них доступ через промисловий стандарт OpenAI API.

Разом вони формують повністю локальний AI-стек агента: Lemonade відповідає за інференс моделі, а OpenClaw надає цикл роботи агента, який перетворює вихідні дані моделі на реальні дії.

> **Перш ніж продовжити:** OpenClaw — це надзвичайно автономний AI-агент. Надання будь-якому AI-агенту доступу до вашої системи може призвести до непередбачуваних або небажаних результатів. Продовжуйте лише в тому разі, якщо ви розумієте ризики та вам комфортно з тим, що автономне програмне забезпечення діятиме від вашого імені.

---

## Що ви дізнаєтесь

Після завершення роботи з цим посібником ви зможете:

- Дізнатись більше про **Lemonade Server**
- **Встановити OpenClaw** та **налаштувати його на Lemonade Server** як AI-бекенд.
- **Запустити шлюз OpenClaw** та переконатися, що ваш агент готовий до роботи.
- **Підключити канал зв’язку** (Discord або Telegram), щоб спілкуватися з агентом з будь-якого пристрою.

---

<!-- @device:halo_box,halo,stx,krk -->
## Налаштування конфігурації пам’яті

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Перевірка оновлень програмного забезпечення

<!-- @require:software-update -->
<!-- @device:end -->

## Встановлення необхідного програмного забезпечення

<!-- @os:linux -->
- ПК з **Ubuntu 24.04+** або сумісним дистрибутивом Linux на основі Debian з `apt-get`
- Щонайменше **12 ГБ оперативної пам’яті** (рекомендовано 64 ГБ+ для більших моделей)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (опційно, для пісочниці OpenClaw)
- **~10–30 ГБ вільного місця на диску** для ваг моделі
<!-- @os:end -->

<!-- @os:windows -->
- ПК з **Windows 10/11**
- Щонайменше **12 ГБ оперативної пам’яті** (рекомендовано 64 ГБ+ для більших моделей)
- **~10–30 ГБ вільного місця на диску** для ваг моделі
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (опційно, для пісочниці OpenClaw)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Завантаження та запуск рекомендованої моделі

Рекомендованою моделлю для цього посібника є **Qwen3.6-35B-A3B-GGUF** від Unsloth — потужна MoE-модель із вікном контексту у 263 тисячі токенів, яка добре підходить для навантажень агентів. Ця модель використовує квантизацію UD-Q4_K_XL. Завантажте її зараз:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Потім завантажте її з великим вікном контексту та збережіть це налаштування для майбутніх запусків:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Модель має типову довжину контексту 262 144 токени. Якщо ви зіткнетеся з помилками нестачі пам’яті (OOM), розгляньте можливість зменшення вікна контексту. Однак, оскільки Qwen3.6 використовує розширений контекст для складних завдань, ми рекомендуємо підтримувати довжину контексту щонайменше 128K токенів, щоб зберегти можливості мислення.

> **Порада: вимкніть мислення для швидших відповідей агента:** Qwen3.6-35B-A3B за замовчуванням працює в режимі мислення, що додає затримку перед кожною відповіддю. Для циклів роботи агента ці накладні витрати швидко накопичуються. Репозиторій [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) надає готову конфігурацію, яка вимикає мислення. Щоб використати її, завантажте файл та імпортуйте його:
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

Ми запускаємо OpenClaw всередині WSL (рекомендовано) та підключаємо його до Lemonade, що працює нативно у Windows. Це дає вам середовище оболонки Linux для OpenClaw, зберігаючи при цьому GPU-прискорення Lemonade на стороні Windows.

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

Вийдіть з WSL та перезапустіть його:

```powershell
exit
wsl --shutdown
wsl
```

### Прокладання мосту від Lemonade у Windows до WSL

WSL2 працює у віртуальній мережі. Lemonade у Windows прив’язується до `127.0.0.1`, до якого WSL не може отримати прямий доступ. Проксі-порт Windows пересилає трафік із шлюзної IP-адреси WSL на локальний хост Windows.

**Знайдіть свою шлюзну IP-адресу WSL** (виконайте всередині WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Додайте проксі-порт** (виконайте в PowerShell від імені адміністратора, замінивши `<WSL-Gateway-IP>` на вашу шлюзну IP-адресу WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Примітка: якщо ви зіткнетесь із помилкою `netsh: command not found`, спробуйте використати явну назву виконуваного файлу — `netsh.exe`

**Додайте правило брандмауера** (у тому ж елевованому PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Перевірте з WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Якщо ви вже завантажили модель Qwen3.6-35B-A3B-GGUF на попередньому кроці, ви маєте побачити вихід JSON, подібний до цього:

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

#### Підтримання роботи мосту після перезапуску

Правило `netsh portproxy` зберігається після перезавантажень, але IP-адреса шлюзу WSL може змінитися після `wsl --shutdown` або перезавантаження. Коли це станеться, проксі все ще вказуватиме на стару IP-адресу, і Lemonade стане недоступним із WSL. Якщо це трапиться, скористайтеся одним із варіантів нижче.

**Варіант 1 (рекомендовано) — Автоматичне відновлення мосту.** Щоб уникнути повторення цих дій вручну щоразу, використовуйте заплановане завдання, яке перевіряє міст під час кожного запуску та входу в систему й перебудовує його лише тоді, коли IP-адреса шлюзу змінилася. Див. [посібник з автоматичного відновлення мосту Lemonade WSL](assets/RepairLemonadeWslBridge.md).


**Варіант 2 — Відновлення мосту вручну.** Спочатку отримайте поточну IP-адресу шлюзу WSL, виконавши в WSL таку команду:

```bash
ip route show default | awk '{print $3}' | head -1
```

Скопіюйте це значення; ви використаєте його замість `<new-WSL-Gateway-IP>` нижче.

Потім у **PowerShell із підвищеними правами** (запустити від імені адміністратора) виведіть список наявних правил, видаліть лише застаріле правило Lemonade та додайте нове з поточною IP-адресою:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

У виведенні команди `show all` застаріле правило Lemonade — це запис, у якого адреса підключення `127.0.0.1` на порту `13305`; його адреса прослуховування — це ваша `<old-WSL-Gateway-IP>`. Видалення за цією адресою прибирає лише це правило, залишаючи всі інші правила port-proxy на вашому комп'ютері недоторканими.

Правило брандмауера, яке ви додали під час налаштування, прив'язане до порту `13305` (а не до IP-адреси), тому воно продовжує працювати і не потребує повторного створення.

> **Рекомендація:** Щоб уникнути проблем зі шлюзом, ми настійно радимо таку конфігурацію оболонки:
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
> Виконуйте команди в цьому розділі всередині свого **терміналу WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Прапорець `--no-onboard` пропускає інтерактивний майстер налаштування, ви налаштуєте бекенд моделі вручну на наступному кроці, що дає точний контроль над тим, яка модель і сервер використовуються.

Відкрийте новий термінал і підтвердьте встановлення:

```bash
openclaw --version
```

> **Порада:** Якщо після встановлення ви бачите `command not found`, додайте глобальний bin-каталог npm до PATH:
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

Запустіть неінтерактивне встановлення OpenClaw.
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

Ця команда записує конфігурацію OpenClaw у файл `~/.openclaw/openclaw.json`.

> **Розмір контекстного вікна OpenClaw:** Стиснення OpenClaw спрацьовує, коли `contextTokens > contextWindow − reserveTokens`. Значення `reserveTokensFloor` за замовчуванням становить 20 000 токенів — це нижня межа, яка перевизначає `reserveTokens`, якщо він менший, тому будь-який контекст моделі нижче приблизно 37 тис. токенів спричинить нескінченний цикл стиснення. Встановіть низький резерв і вимкніть цю нижню межу один раз у своїй конфігурації, і це застосовуватиметься до кожної моделі — без окремого налаштування для кожної моделі:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` — це *нижня межа* (мінімальна гарантія), а не сам резерв, тому налаштування лише нижньої межі не матиме ефекту. `reserveTokensFloor: 0` вимикає цю гарантію, тому менше значення `reserveTokens` приймається.
>
> **Коли застосовувати це:** Використовуйте цю конфігурацію, якщо ефективне контекстне вікно вашої моделі менше приблизно 37 тис. токенів — або тому, що модель невелика (наприклад, 8 тис., 16 тис., 32 тис.), або тому, що ви навмисно обмежили його меншим значенням (наприклад, завантажили модель на 128 тис., але встановили контекст 16 тис. у Lemonade). Без цього OpenClaw входить у нескінченний цикл стиснення під час запуску.
>
> **Моделі з великим контекстом за повного контексту:** Це можна повністю пропустити. Значення за замовчуванням працюють добре, стиснення спрацює задовго до заповнення вікна, і в моделі буде достатньо простору для генерації довгих відповідей. Якщо ви все ж застосуєте це, майте на увазі, що `reserveTokens: 4096` обмежує довжину відповіді приблизно 4 тис. токенів, що може обрізати генерацію довгих файлів або детальних планів.
>
> **Куди це додати:** Розмістіть блок `compaction` всередині `agents.defaults` у вашому файлі `openclaw.json` (зазвичай за шляхом `~/.openclaw/openclaw.json`):
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
> Решта вашої конфігурації (шлюз, канали, моделі тощо) залишається незмінною, потрібно додати лише ключ `compaction`.
### (Рекомендовано) Увімкнення пісочниці Docker

OpenClaw може направляти всі операції агента з файлами та кодом через ізольований контейнер Docker, а не виконувати їх безпосередньо на вашому хості. Це обмежує зону впливу будь-якої небажаної дії лише пісочницею, залишаючи вашу файлову систему та мережу хоста незмінними.

Зберіть образ пісочниці один раз (Docker має бути встановлено):

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

# Docker Desktop injects its WSL cli-tools a few seconds after the distro boots.
for i in $(seq 1 30); do
  docker version >/dev/null 2>&1 && break
  sleep 2
done
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

Виконайте це, щоб додати ключ `sandbox` всередину наявного блоку `agents.defaults` у файлі `~/.openclaw/openclaw.json`:

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

Контейнери пісочниці за замовчуванням **не мають доступу до мережі**. Дивіться [довідник з пісочниці](https://docs.openclaw.ai/gateway/sandboxing) щодо прив'язки томів (bind mounts) та перевизначень мережі.

> #### Усунення несправностей: Docker Permission Denied
> 
> Якщо ви отримуєте повідомлення "permission denied" під час виконання команд Docker:
> 
> **Крок 1: Додайте вашого користувача до групи docker**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **Крок 2: Якщо помилка залишається, застосуйте постійне виправлення**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Потім **перезавантажте** вашу систему.
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
## (Рекомендовано) Інтеграція OpenClaw зі службами Firecrawl

[Firecrawl](https://docs.firecrawl.dev/introduction) надає самостійно розміщувану службу веб-сканування та вилучення контенту, яка може обійти ці труднощі та розкрити повний потенціал автоматизації OpenClaw. 

У цій конфігурації OpenClaw працює як набір контейнерів Docker, керованих за допомогою Podman. Щоб спростити керування життєвим циклом та автоматичний запуск, ми реєструємо Firecrawl як службу `systemd` рівня користувача, яка оркеструє базовий стек Podman Compose. Це дозволяє OpenClaw запускати шлюз, зупиняти та перевіряти службу Firecrawl за допомогою стандартних команд `systemctl --user`, замість того, щоб взаємодіяти з контейнерами напряму. 

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
На цьому етапі службу визначено, але ще не зареєстровано в `systemd`. 
Переконайтеся, що назва файлу точно відповідає тій, яку ви створили вище, потім виконайте:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
У разі успіху ви маєте побачити наступний вивід:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` містить символічні посилання на служби, налаштовані для автоматичного запуску.

### 2. Налаштування Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) є ідеальним варіантом для тих, кому потрібен повний контроль над середовищами скрапінгу та обробки даних, але це супроводжується додатковими зусиллями з обслуговування та налаштування.

Почніть з клонування репозиторію:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Створіть файл `.env` у каталозі `/firecrawl`: 
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
Після цього завантажте файл Compose для OpenClaw [openclaw-compose.yaml](assets/openclaw-compose.yaml) і розмістіть його в кореневому каталозі `/firecrawl`:

> Ця угода необхідна для того, щоб `systemd` міг знайти та правильно запустити службу, як зазначено в `WorkingDirectory=${HOME}/firecrawl`.

> Ви завжди можете розширити стек, додаючи додаткові служби Firecrawl за потреби. Повний список доступних служб можна знайти в офіційному файлі [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Запуск служби OpenClaw через Firecrawl 

Перш ніж передати керування `systemd`, перевірте, що все працює правильно, запустивши стек вручну:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Якщо все налаштовано правильно, ви маєте побачити, як запускається контейнер OpenClaw, а вивід командного рядка має виглядати приблизно так:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

Після перевірки зупиніть стек, перш ніж продовжити:
```bash
podman compose -f openclaw-compose.yaml down
```
Перш ніж запускати службу, потрібно переконатися, що для каталогу `firecrawl` та його файлу `.env` встановлено правильного власника та дозволи. 
Це необхідно для того, щоб служба могла записувати ваші облікові дані під час запуску.
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

Щойно служба запуститься та почне працювати, ви помітите новий каталог `.openclaw`, створений у вашій домашній папці (~/.openclaw). Цей каталог за замовчуванням заблоковано, тож вам потрібно розблокувати його, щоб отримати ваш токен шлюзу.

1. Надайте доступ до каталогу:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Зчитайте свій токен шлюзу:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Знайдіть значення `OPENCLAW_GATEWAY_TOKEN` у виводі.

3. Відкрийте панель шлюзу у вашому браузері за адресою http://127.0.0.1:18789. Вставте свій токен, коли з'явиться запит на автентифікацію.

Щоб зупинити службу, виконайте:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Запуск шлюзу OpenClaw

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

Щоб відкрити панель керування, виконайте це у другому терміналі, доки шлюз усе ще працює:

```bash
openclaw dashboard
```

Оскільки шлюз прив’язується до loopback-адреси, панель керування автоматично проходить автентифікацію при відкритті з того самого пристрою — введення токена або підтвердження пристрою для локального доступу не потрібне. Ви маєте побачити панель керування OpenClaw з вашою моделлю Lemonade у списку як активний бекенд.

> Якщо ви ввімкнули пісочницю (sandboxing), перевірити її можна, попросивши агента виконати `run hostname` з панелі керування. Якщо замість імені хосту вашого пристрою ви бачите короткий ідентифікатор контейнера, пісочниця працює.

**Вітаємо, ви створили повністю локальний стек ШІ-агента з нуля.**

> **Потрібен токен шлюзу?** Виконайте `openclaw dashboard --no-open`, щоб вивести URL-адресу панелі керування з убудованим токеном (також буде здійснено спробу скопіювати його в буфер обміну). Крім того, токен зберігається за шляхом `gateway.auth.token` у файлі `~/.openclaw/openclaw.json`.

**Доступ до панелі керування з іншого пристрою (через SSH-тунель)**

Якщо OpenClaw працює на віддаленому пристрої, ви можете отримати доступ до його панелі керування з локального пристрою через SSH-тунель. Тунель перенаправляє порт шлюзу (`18789`), щоб ваш локальний браузер міг спілкуватися з віддаленим шлюзом через `127.0.0.1`.

1. На вашому **локальному пристрої** підключіться до віддаленого пристрою один раз і підтвердьте запит на відбиток ключа, щоб хост додався до списку відомих хостів:

   ```bash
   ssh user@<host-ip>
   ```

2. Ще на **локальному пристрої** відкрийте SSH-тунель:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Примітка:** Після введення пароля термінал не показує жодного виведення й виглядає так, ніби зависнув. Це нормально: прапорець `-N` вказує SSH не виконувати жодної віддаленої команди, тому він просто утримує тунель відкритим. Залиште цей термінал працювати.

3. На **локальному пристрої** відкрийте браузер і перейдіть за адресою `http://127.0.0.1:18789`.

4. На **віддаленому пристрої** виведіть токен шлюзу і вставте його в браузер для входу:

   ```bash
   openclaw dashboard --no-open
   ```

   Це виведе URL-адресу панелі керування з убудованим токеном; скопіюйте токен для входу. (Токен також зберігається за шляхом `gateway.auth.token` у файлі `~/.openclaw/openclaw.json`.)

> **Підтвердження віддаленого пристрою:** Коли ви відкриваєте панель керування з іншого пристрою чи телефону, браузер може показати ідентифікатор запиту. На **віддаленому пристрої** виведіть список запитів, що очікують підтвердження:
> ```bash
> openclaw devices list
> ```
> Потім підтвердьте відповідний запит:
> ```bash
> openclaw devices approve <requestId>
> ```
> Це потрібно лише для віддалених або додаткових пристроїв; доступ через loopback з того самого пристрою автентифікується автоматично. Докладніше див. у документації [Віддалений доступ](https://docs.openclaw.ai/gateway/remote).

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Необов’язково: Підключення каналу зв’язку

Коли шлюз запущено, ви можете зв’язатися з вашим локальним агентом з будь-якого пристрою. Оберіть варіант, що відповідає вашому налаштуванню. OpenClaw підтримує [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) та інші канали, повний перелік див. на [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Варіант A: Discord

Для Discord потрібен сервер, на якому **ви маєте права адміністратора**, щоб додати бота. Якщо ви є учасником спільних серверів, але не є власником жодного, скористайтеся Варіантом B (Telegram).

#### Створення облікового запису та сервера Discord

Якщо у вас немає облікового запису Discord, зареєструйтеся на [discord.com](https://discord.com). Вам також потрібен сервер, на якому ви є адміністратором — створіть його, натиснувши іконку **+** на бічній панелі Discord і обравши **Create My Own**. Підійде приватний сервер.

#### Створення застосунку та бота Discord

1. Перейдіть у [Discord Developer Portal](https://discord.com/developers/applications) і натисніть **New Application**. Дайте йому назву (наприклад, «openclaw-bot»).
2. На бічній панелі натисніть **Bot**. Встановіть ім’я користувача для бота.
3. Усе ще на сторінці Bot, прокрутіть до **Privileged Gateway Intents** і увімкніть:
   - **Message Content Intent** (обов’язково)
   - **Server Members Intent** (рекомендовано)
4. Прокрутіть угору й натисніть **Reset Token**, щоб згенерувати токен бота. Скопіюйте його.

#### Додавання бота на ваш сервер

1. На бічній панелі натисніть **OAuth2/ URL Generator**.
2. У розділі **Scopes** увімкніть `bot` і `applications.commands`.
3. У розділі **Bot Permissions** увімкніть: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Скопіюйте згенерований URL, вставте його в браузер, оберіть свій сервер і підтвердьте. Бот має з’явитися у списку учасників вашого сервера.

#### Отримання ідентифікаторів

Увімкніть режим розробника в Discord (**User Settings/ Advanced/ Developer Mode**), потім:
- Клацніть правою кнопкою миші на іконку сервера: **Copy Server ID**
- Клацніть правою кнопкою миші на свій аватар: **Copy User ID**

#### Дозвіл на особисті повідомлення від учасників сервера

Клацніть правою кнопкою миші на іконку сервера/ **Privacy Settings**/ увімкніть **Direct Messages**. Це дозволить боту надсилати вам особисті повідомлення, що необхідно для кроку зі спарювання.

#### Налаштування OpenClaw для Discord

Збережіть токен бота як змінну середовища, потім створіть один файл-патч, який вмикає Discord, посилається на токен і додає ваш сервер у список дозволених. Замініть `<server_id>` і `<user_id>` на зібрані вище ідентифікатори.

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

> **Не покладайтеся на прохання до агента налаштувати це.** Коли увімкнено пісочницю, агент не може писати у файл `~/.openclaw/openclaw.json` зсередини пісочниці — замість цього використовуйте наведені вище CLI-команди на хості.

Перезапустіть шлюз, щоб він застосував нову конфігурацію каналу:

```bash
openclaw gateway run --bind loopback --port 18789
```

Протягом кількох секунд у виведенні шлюзу ви маєте побачити `logged in to discord as <bot-name>`.
#### Прив'яжіть свій обліковий запис Discord

Напишіть боту в Discord. Він відповість коротким кодом прив'язки.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Підтвердьте це на машині, що виконує OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Коди прив'язки закінчуються через годину.

Тепер ви можете спілкуватися зі своїм агентом безпосередньо з Discord і перекладати завдання на своє локальне обладнання.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Варіант Б: Telegram

Telegram простіший за Discord для більшості користувачів, він не потребує сервера та прав адміністратора.

#### Створіть бота Telegram

1. Відкрийте Telegram і напишіть **@BotFather**.
2. Надішліть `/newbot` і дотримуйтесь підказок. Збережіть токен бота, який він вам надасть.

#### Налаштуйте OpenClaw для Telegram

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

Перезапустіть шлюз, а потім надішліть своєму боту будь-яке повідомлення в Telegram. Підтвердьте прив'язку:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Коди прив'язки закінчуються через годину. Тепер ви можете спілкуватися зі своїм агентом через особисті повідомлення Telegram.

---

## Наступні кроки

Тепер, коли ваш агент може отримувати команди з вашого телефону та виконувати їх на вашій локальній машині, ось три напрямки, варті вивчення:

1. **Узагальнювач фондового ринку**: Налаштуйте OpenClaw на отримання даних з фінансових API з фіксованим інтервалом, узагальнення денних рухів за допомогою вашої локальної моделі та надсилання дайджесту на ваш телефон щоранку через обраний вами канал.

2. **Монітор донавчання**: Запустіть завдання навчання віддалено через Telegram або Discord, а потім нехай агент відстежує журнал навчання та звітує про періодичні значення втрат, використання GPU та дискового простору на ваш телефон. Якщо процес зупиняється або відбувається сплеск використання VRAM, ви дізнаєтесь про це негайно, не потребуючи перебувати біля машини.

3. **IOT з локальною VLM**: Направте камеру на вхідні двері, запустіть модель зору на Lemonade і нехай OpenClaw аналізує кадри за запитом або тригером. Запитайте "чи прийшли якісь посилки сьогодні?" зі свого телефону та отримайте пряму відповідь від власного обладнання.

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