<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинный перевод.** Эта страница была автоматически переведена с английского языка и не прошла проверку человеком. Она может содержать ошибки, а некоторые инструкции, команды, файлы для загрузки, сведения о доступности продуктов или иное содержимое могут отличаться в зависимости от языка или региона. В случае каких-либо несоответствий или расхождений преимущественную силу имеет оригинальная версия playbook на английском языке.
<!-- auto-translated-disclaimer:end -->

# Запуск OpenClaw с Lemonade Server в качестве бэкенда

## Обзор

[**OpenClaw**](https://openclaw.ai/) — это автономный ИИ-агент, который может писать и выполнять код, управлять файлами и решать сложные многоэтапные задачи от вашего имени. В отличие от чат-ассистента, который просто отвечает на вопросы, OpenClaw выполняет реальные действия в вашей системе, а значит ему требуется быстрый и мощный ИИ-бэкенд, способный поспевать за требовательным циклом работы агента.

[**Lemonade Server**](https://lemonade-server.ai/) — именно такой бэкенд. Это опенсорсный локальный сервер вывода, который запускает GenAI-модели непосредственно на вашем оборудовании и предоставляет доступ к ним через отраслевой стандарт OpenAI API.

Вместе они образуют полностью локальный стек ИИ-агента: Lemonade выполняет вывод модели, а OpenClaw обеспечивает цикл работы агента, превращающий вывод модели в реальные действия.

> **Прежде чем продолжить:** OpenClaw — это высоко автономный ИИ-агент. Предоставление любому ИИ-агенту доступа к вашей системе может привести к непредсказуемым или нежелательным последствиям. Продолжайте только в том случае, если вы понимаете риски и готовы к тому, что автономное программное обеспечение будет действовать от вашего имени.

---

## Чему вы научитесь

К концу этого руководства вы сможете:

- Узнать о **Lemonade Server**
- **Установить OpenClaw** и **настроить его на использование Lemonade Server** в качестве ИИ-бэкенда.
- **Запустить шлюз OpenClaw** и убедиться, что ваш агент готов к работе.
- **Подключить канал связи** (Discord или Telegram), чтобы общаться с агентом с любого устройства.

---

## Настройка конфигурации памяти

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Проверка обновлений программного обеспечения

<!-- @require:software-update -->
<!-- @device:end -->

## Установка необходимого программного обеспечения

<!-- @os:linux -->
- ПК с **Ubuntu 24.04+** или совместимым дистрибутивом Linux на базе Debian с `apt-get`
- Не менее **12 ГБ ОЗУ** (рекомендуется 64 ГБ+ для более крупных моделей)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (необязательно, для песочницы OpenClaw)
- **~10–30 ГБ свободного места на диске** для весов модели
<!-- @os:end -->

<!-- @os:windows -->
- ПК с **Windows 10/11**
- Не менее **12 ГБ ОЗУ** (рекомендуется 64 ГБ+ для более крупных моделей)
- **~10–30 ГБ свободного места на диске** для весов модели
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (необязательно, для песочницы OpenClaw)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Загрузка и запуск рекомендуемой модели

Рекомендуемая модель для этого руководства — **Qwen3.6-35B-A3B-GGUF** от Unsloth, мощная MoE-модель с окном контекста в 263 тыс. токенов, хорошо подходящая для рабочих нагрузок агентов. Эта модель использует квантование UD-Q4_K_XL. Загрузите её сейчас:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Затем загрузите её с большим окном контекста и сохраните эту настройку для последующих запусков:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

Модель имеет длину контекста по умолчанию 262 144 токена. Если вы столкнётесь с ошибками нехватки памяти (OOM), рассмотрите возможность уменьшения окна контекста. Однако, поскольку Qwen3.6 использует расширенный контекст для решения сложных задач, мы рекомендуем сохранять длину контекста не менее 128K токенов, чтобы сохранить способности к рассуждению.

> **Совет: отключите режим рассуждения для более быстрых ответов агента:** Qwen3.6-35B-A3B по умолчанию работает в режиме рассуждения (thinking mode), что добавляет задержку перед каждым ответом. В циклах работы агента эти накладные расходы быстро накапливаются. Репозиторий [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) предоставляет готовую конфигурацию, отключающую режим рассуждения. Чтобы её использовать, скачайте файл и импортируйте его:
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

## Настройка WSL

Мы запускаем OpenClaw внутри WSL (рекомендуется) и подключаем его к Lemonade, работающему нативно в Windows. Это даёт вам среду командной оболочки Linux для OpenClaw, сохраняя при этом GPU-ускорение Lemonade на стороне Windows.

### Установка WSL и Ubuntu

Откройте PowerShell от имени администратора и установите ядро WSL:

```powershell
wsl --install --no-distribution
```

Затем установите Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Включение systemd в WSL

Выполните это в терминале Ubuntu:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Выйдите из WSL и перезапустите его:

```powershell
exit
wsl --shutdown
wsl
```

### Проброс Lemonade из Windows в WSL

WSL2 работает в виртуальной сети. Lemonade в Windows привязывается к `127.0.0.1`, к которому WSL не может обратиться напрямую. Прокси портов Windows перенаправляет трафик от шлюзового IP-адреса WSL к localhost Windows.

**Найдите ваш шлюзовой IP-адрес WSL** (выполните внутри WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Добавьте прокси порта** (выполните в PowerShell от имени администратора, заменив `<WSL-Gateway-IP>` на ваш шлюзовой IP-адрес WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> Примечание: если вы столкнётесь с ошибкой `netsh: command not found`, попробуйте использовать явное имя исполняемого файла — `netsh.exe`

**Добавьте правило брандмауэра** (в том же PowerShell с повышенными правами):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Проверьте из WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Если вы уже загрузили модель Qwen3.6-35B-A3B-GGUF на предыдущем шаге, вы должны увидеть JSON-вывод, подобный этому:

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

#### Обеспечение работы моста после перезагрузки

Правило `netsh portproxy` сохраняется после перезагрузки, но IP-адрес шлюза WSL может измениться после `wsl --shutdown` или перезагрузки. Когда это происходит, прокси по-прежнему указывает на старый IP-адрес, и Lemonade становится недоступен из WSL. Если это произошло, воспользуйтесь одним из вариантов ниже.

**Вариант 1 (рекомендуется) — автоматическое восстановление моста.** Чтобы не делать это вручную каждый раз, используйте запланированную задачу, которая проверяет мост при каждом запуске и входе в систему и восстанавливает его только тогда, когда IP-адрес шлюза изменился. См. [руководство по автоматическому восстановлению моста Lemonade WSL](assets/RepairLemonadeWslBridge.md).


**Вариант 2 — восстановление моста вручную.** Сначала получите текущий IP-адрес шлюза WSL, выполнив следующую команду внутри WSL:

```bash
ip route show default | awk '{print $3}' | head -1
```

Скопируйте это значение — оно понадобится вам вместо `<new-WSL-Gateway-IP>` ниже.

Затем в **PowerShell с повышенными правами** (запуск от имени администратора) выведите список существующих правил, удалите только устаревшее правило Lemonade и добавьте новое с текущим IP-адресом:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

В выводе `show all` устаревшее правило Lemonade — это запись, у которой адрес подключения — `127.0.0.1` на порту `13305`; её адрес прослушивания — это ваш `<old-WSL-Gateway-IP>`. Удаление по этому адресу удаляет только это правило и не затрагивает другие правила port-proxy на вашем компьютере.

Правило брандмауэра, добавленное вами во время настройки, привязано к порту `13305` (а не к IP-адресу), поэтому оно продолжает работать и не требует повторного создания.

> **Рекомендация:** Чтобы избежать проблем со шлюзом, мы настоятельно рекомендуем следующую конфигурацию оболочек:
> - **Команды Windows** следует выполнять в **PowerShell**
> - **Команды дистрибутива WSL** следует выполнять в **командной строке (Command Prompt)** (запущенной от имени **администратора**)

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

## Установка и настройка OpenClaw

### Установка OpenClaw
<!-- @os:windows -->
> Выполняйте команды из этого раздела в терминале **WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Флаг `--no-onboard` пропускает интерактивный мастер настройки; вы настроите модель-бэкенд вручную на следующем шаге, что даёт точный контроль над тем, какая модель и сервер используются.

Откройте новый терминал и подтвердите установку:

```bash
openclaw --version
```

> **Совет:** Если после установки вы видите `command not found`, добавьте глобальную bin-директорию npm в PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Чтобы сделать это постоянным, добавьте указанную выше строку в файл `~/.bashrc` или `~/.zshrc`.

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


### Настройка OpenClaw для использования Lemonade

Запустите неинтерактивную настройку OpenClaw (onboarding).
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

Эта команда записывает конфигурацию OpenClaw в `~/.openclaw/openclaw.json`.

> **Размер контекстного окна OpenClaw:** сжатие (compaction) в OpenClaw запускается, когда `contextTokens > contextWindow − reserveTokens`. Значение по умолчанию `reserveTokensFloor` равно 20 000 токенов — это нижняя граница, которая переопределяет `reserveTokens`, если оно меньше, поэтому любое контекстное окно модели меньше ~37 тыс. токенов вызовет бесконечный цикл сжатия. Установите низкое значение резерва и отключите нижнюю границу один раз в конфигурации — это применится ко всем моделям, без необходимости настройки для каждой модели отдельно:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` — это *нижняя граница* (минимальное ограничение), а не сам резерв; установка только этой границы не даст эффекта. `reserveTokensFloor: 0` отключает это ограничение, так что более низкое значение `reserveTokens` принимается.
>
> **Когда это применять:** используйте эту конфигурацию, если эффективное контекстное окно вашей модели меньше ~37 тыс. токенов — либо потому что модель небольшая (например, 8k, 16k, 32k), либо потому что вы намеренно ограничили его до меньшего значения (например, загружаете модель на 128k, но задаёте контекст 16k в Lemonade). Без этого OpenClaw входит в бесконечный цикл сжатия при запуске.
>
> **Модели с большим контекстом при полном размере окна:** это можно полностью пропустить. Значения по умолчанию работают нормально, сжатие начнётся задолго до заполнения окна, и у модели будет достаточно места для генерации длинных ответов. Если вы всё же примените эту настройку, учтите, что `reserveTokens: 4096` ограничивает длину ответа примерно 4 тыс. токенов, что может обрезать генерацию длинных файлов или подробных планов.
>
> **Куда добавить это:** поместите блок `compaction` внутри `agents.defaults` в вашем `openclaw.json` (обычно расположен по пути `~/.openclaw/openclaw.json`):
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
> Остальная часть вашей конфигурации (gateway, channels, models и т. д.) остаётся без изменений — нужно добавить только ключ `compaction`.
### (Рекомендуется) Включение Docker Sandboxing

OpenClaw может направлять все файловые и кодовые операции агента через изолированный контейнер Docker, вместо того чтобы выполнять их напрямую на вашем хосте. Это ограничивает радиус воздействия любого непреднамеренного действия песочницей, оставляя файловую систему и сеть вашего хоста нетронутыми.

Соберите образ песочницы один раз (Docker должен быть установлен):

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

Выполните это, чтобы добавить ключ `sandbox` внутри существующего блока `agents.defaults` в `~/.openclaw/openclaw.json`:

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

Контейнеры песочницы **не имеют доступа к сети** по умолчанию. См. [справочник по песочнице](https://docs.openclaw.ai/gateway/sandboxing) для монтирования привязок и переопределений сети.

> #### Устранение неполадок: отказано в доступе Docker
> 
> Если при выполнении команд Docker вы получаете сообщение "permission denied":
> 
> **Шаг 1: Добавьте своего пользователя в группу docker**
> 
> ```bash
> sudo groupadd docker                    # Создайте группу при необходимости
> sudo usermod -aG docker $USER           # Добавьте себя в группу
> newgrp docker                           # Примените изменение
> docker run hello-world                  # Проверьте
> ```
> 
> **Шаг 2: Если ошибка сохраняется, примените постоянное исправление**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> Затем **перезагрузите** систему.
> 
> **Быстрое временное исправление** (сбрасывается после перезагрузки):
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
## (Рекомендуется) Интеграция OpenClaw с сервисами Firecrawl

[Firecrawl](https://docs.firecrawl.dev/introduction) предоставляет самостоятельно размещаемый сервис веб-краулинга и извлечения контента, который может обойти эти сложности и раскрыть весь потенциал автоматизации OpenClaw. 

В этой настройке OpenClaw работает как набор контейнеров Docker, управляемых с помощью Podman. Чтобы упростить управление жизненным циклом и автоматический запуск, мы регистрируем Firecrawl как пользовательский сервис `systemd`, который оркестрирует лежащий в основе стек Podman Compose. Это позволяет OpenClaw запускать шлюз, останавливать и проверять сервис Firecrawl с помощью стандартных команд `systemctl --user` вместо прямого взаимодействия с контейнерами. 

Чтобы всё было просто, мы разбили весь процесс на четыре шага:

---

### 1. Регистрация системного сервиса
Перейдите в каталог пользовательской конфигурации systemd:
```bash
cd ~/.config/systemd/user
```
Создайте и откройте новый файл с именем `firecrawl.service`.
```bash
nano firecrawl.service
```
Скопируйте и вставьте следующую конфигурацию:
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
На этом этапе сервис определён, но ещё не зарегистрирован в `systemd`. 
Убедитесь, что имя файла точно совпадает с тем, что вы создали выше, затем выполните:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
В случае успеха вы должны увидеть следующий вывод:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` содержит символические ссылки на сервисы, настроенные для автоматического запуска.

### 2. Настройка Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) идеально подходит для тех, кому нужен полный контроль над своей средой скрапинга и обработки данных, но это сопряжено с дополнительными затратами на обслуживание и настройку.

Начните с клонирования репозитория:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
Создайте `.env` в корневом каталоге `/firecrawl`: 
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. Развёртывание OpenClaw с Podman Compose

Прежде чем продолжить, убедитесь, что вы загрузили последний образ Docker для OpenClaw:
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
После этого загрузите файл Compose для OpenClaw [openclaw-compose.yaml](assets/openclaw-compose.yaml) и поместите его в корневой каталог `/firecrawl`:

> Это соглашение необходимо для того, чтобы `systemd` мог корректно найти и запустить сервис, как указано в `WorkingDirectory=${HOME}/firecrawl`.

> Вы всегда можете расширить стек, добавив дополнительные сервисы Firecrawl по мере необходимости. Полный список доступных сервисов можно найти в официальном файле [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Запуск сервиса OpenClaw через Firecrawl 

Прежде чем передать управление `systemd`, убедитесь, что всё работает правильно, запустив стек вручную:
```bash
podman compose -f openclaw-compose.yaml up -d
```
Если всё настроено корректно, вы должны увидеть, что контейнер OpenClaw поднялся, а вывод в командной строке должен выглядеть примерно так:
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

После проверки остановите стек, прежде чем продолжить:
```bash
podman compose -f openclaw-compose.yaml down
```
Перед запуском сервиса необходимо убедиться, что для каталога `firecrawl` и его файла `.env` установлены правильные владелец и права доступа. 
Это необходимо для того, чтобы сервис мог записывать ваши учётные данные при запуске.
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
Теперь, когда всё проверено, запустите сервис через `systemd`:
```bash
systemctl --user start firecrawl.service
```
[Действия OpenClaw](https://docs.openclaw.ai/) доступны изнутри интерактивного контейнера, а веб-панель управления доступна на том же хосте и порте по адресу http://127.0.0.1:18789.
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### Получение вашего `OPENCLAW_GATEWAY_TOKEN`

После запуска сервиса вы заметите, что в вашей домашней папке (~/.openclaw) создан новый каталог `.openclaw`. Этот каталог по умолчанию заблокирован, поэтому вам нужно разблокировать его, чтобы получить токен шлюза.

1. Предоставьте доступ к каталогу:
```bash
sudo chmod 777 ~/.openclaw/
```
2. Прочитайте токен вашего шлюза:
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
Найдите значение `OPENCLAW_GATEWAY_TOKEN` в выводе.

3. Откройте панель управления шлюзом в браузере по адресу http://127.0.0.1:18789. Вставьте свой токен, когда будет предложено пройти аутентификацию.

Чтобы остановить сервис, выполните:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## Запуск шлюза OpenClaw

Шлюз (gateway) — это процесс OpenClaw, который управляет циклом работы агента и обслуживает панель управления:

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

Чтобы открыть панель управления, выполните эту команду во втором терминале, пока шлюз всё ещё работает:

```bash
openclaw dashboard
```

Поскольку шлюз привязан к loopback-интерфейсу, при открытии панели управления с той же машины выполняется автоматическая аутентификация — ввод токена или подтверждение устройства не требуется для локального доступа. Вы должны увидеть панель управления OpenClaw с вашей моделью Lemonade, указанной в качестве активного бэкенда.

> Если вы включили песочницу (sandboxing), вы можете проверить её работу, попросив агента выполнить `run hostname` из панели управления. Если вместо имени хоста вашей машины отображается короткий идентификатор контейнера, значит песочница работает.

**Поздравляем, вы построили полностью локальный стек ИИ-агента с нуля.**

> **Нужен токен шлюза?** Выполните `openclaw dashboard --no-open`, чтобы вывести URL панели управления со встроенным токеном (команда также попытается скопировать его в буфер обмена). Также токен можно найти по пути `gateway.auth.token` в файле `~/.openclaw/openclaw.json`.

**Доступ к панели управления с другого устройства (через SSH-туннель)**

Если OpenClaw работает на удалённой машине, вы можете открыть его панель управления с локальной машины через SSH-туннель. Туннель перенаправляет порт шлюза (`18789`), чтобы ваш локальный браузер мог обращаться к удалённому шлюзу через `127.0.0.1`.

1. На вашей **локальной машине** подключитесь один раз к удалённой машине и подтвердите запрос об отпечатке ключа, чтобы хост был добавлен в список известных хостов:

   ```bash
   ssh user@<host-ip>
   ```

2. Всё ещё на вашей **локальной машине** откройте SSH-туннель:

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **Примечание:** После ввода пароля терминал не выводит никакой информации и выглядит зависшим. Это ожидаемое поведение: флаг `-N` указывает SSH не выполнять никакую команду на удалённой машине, поэтому он просто удерживает туннель открытым. Оставьте этот терминал работающим.

3. На вашей **локальной машине** откройте браузер и перейдите по адресу `http://127.0.0.1:18789`.

4. На **удалённой машине** выведите токен шлюза и вставьте его в браузер для входа:

   ```bash
   openclaw dashboard --no-open
   ```

   Эта команда выводит URL панели управления со встроенным токеном; скопируйте токен для входа. (Токен также хранится по пути `gateway.auth.token` в файле `~/.openclaw/openclaw.json`.)

> **Подтверждение удалённого устройства:** Когда вы открываете панель управления с другой машины или телефона, браузер может отобразить идентификатор запроса. На **удалённой машине** выведите список ожидающих запросов:
> ```bash
> openclaw devices list
> ```
> Затем подтвердите соответствующий запрос:
> ```bash
> openclaw devices approve <requestId>
> ```
> Это требуется только для удалённых или дополнительных устройств; при доступе через loopback с той же машины аутентификация происходит автоматически. Подробности см. в документации [Remote Access](https://docs.openclaw.ai/gateway/remote).

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Дополнительно: подключение канала связи

После запуска шлюза вы можете обращаться к своему локальному агенту с любого устройства. Выберите вариант, подходящий для вашей настройки. OpenClaw поддерживает [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) и другие каналы, полный список см. на [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Вариант A: Discord

Для Discord требуется сервер, на котором **у вас есть права администратора**, чтобы добавить бота. Если вы состоите на общих серверах, но не владеете ни одним из них, используйте Вариант B (Telegram).

#### Создание учётной записи и сервера Discord

Если у вас нет учётной записи Discord, зарегистрируйтесь на [discord.com](https://discord.com). Вам также понадобится сервер, на котором вы являетесь администратором — создайте его, нажав на значок **+** на боковой панели Discord и выбрав **Create My Own**. Подойдёт и приватный сервер.

#### Создание приложения и бота Discord

1. Перейдите в [Discord Developer Portal](https://discord.com/developers/applications) и нажмите **New Application**. Дайте ему имя (например, «openclaw-bot»).
2. На боковой панели нажмите **Bot**. Задайте имя пользователя для бота.
3. Оставаясь на странице Bot, прокрутите вниз до **Privileged Gateway Intents** и включите:
   - **Message Content Intent** (обязательно)
   - **Server Members Intent** (рекомендуется)
4. Прокрутите обратно вверх и нажмите **Reset Token**, чтобы сгенерировать токен бота. Скопируйте его.

#### Добавление бота на ваш сервер

1. На боковой панели нажмите **OAuth2/ URL Generator**.
2. В разделе **Scopes** включите `bot` и `applications.commands`.
3. В разделе **Bot Permissions** включите: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Скопируйте сгенерированный URL, вставьте его в браузер, выберите свой сервер и подтвердите. Бот должен появиться в списке участников вашего сервера.

#### Сбор идентификаторов

Включите режим разработчика в Discord (**User Settings/ Advanced/ Developer Mode**), затем:
- Правой кнопкой мыши по значку вашего сервера: **Copy Server ID**
- Правой кнопкой мыши по вашему собственному аватару: **Copy User ID**

#### Разрешение личных сообщений от участников сервера

Правой кнопкой мыши по значку вашего сервера/ **Privacy Settings**/ включите **Direct Messages**. Это позволит боту писать вам в личные сообщения, что необходимо для этапа сопряжения.

#### Настройка OpenClaw для Discord

Сохраните токен вашего бота как переменную окружения, затем создайте единый патч-файл, который включает Discord, ссылается на токен и добавляет ваш сервер в список разрешённых. Замените `<server_id>` и `<user_id>` на идентификаторы, собранные выше.

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

> **Не полагайтесь на то, что агент сам настроит это.** При включённой песочнице агент не может писать в `~/.openclaw/openclaw.json` изнутри песочницы, вместо этого используйте приведённые выше команды CLI на хосте.

Перезапустите шлюз, чтобы он подхватил новую конфигурацию канала:

```bash
openclaw gateway run --bind loopback --port 18789
```

В течение нескольких секунд в выводе шлюза вы должны увидеть `logged in to discord as <bot-name>`.
#### Привяжите свою учетную запись Discord

Напишите боту в Discord. Он ответит коротким кодом привязки.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Подтвердите его на машине, где запущен OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Коды привязки действительны в течение одного часа.

Теперь вы можете общаться со своим агентом прямо из Discord и перекладывать задачи на свое локальное оборудование.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Вариант Б: Telegram

Telegram проще, чем Discord, для большинства пользователей — не требуется ни сервер, ни права администратора.

#### Создайте бота Telegram

1. Откройте Telegram и напишите **@BotFather**.
2. Отправьте `/newbot` и следуйте подсказкам. Сохраните токен бота, который он вам выдаст.

#### Настройте OpenClaw для Telegram

Сохраните токен как переменную окружения:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Добавьте конфигурацию канала в `~/.openclaw/openclaw.json` (или примените патч через панель управления):

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

Перезапустите шлюз, затем отправьте боту любое сообщение в Telegram. Подтвердите привязку:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Коды привязки действительны в течение одного часа. Теперь вы можете общаться со своим агентом через личные сообщения Telegram.

---

## Дальнейшие шаги

Теперь, когда ваш агент может получать команды с вашего телефона и выполнять действия на вашей локальной машине, вот три направления, которые стоит изучить:

1. **Сводка по фондовому рынку**: настройте OpenClaw на получение данных из финансовых API с заданным интервалом, создание сводки по движениям за день с помощью вашей локальной модели и отправку дайджеста на ваш телефон каждое утро через выбранный вами канал.

2. **Монитор тонкой настройки**: запустите задачу обучения удаленно через Telegram или Discord, а затем пусть агент отслеживает журнал обучения и периодически сообщает на ваш телефон значения потерь, загрузку GPU и использование диска. Если запуск зависает или наблюдается всплеск использования VRAM, вы узнаете об этом немедленно, не находясь у машины.

3. **IOT с локальной VLM**: направьте камеру на входную дверь, запустите модель компьютерного зрения на Lemonade и позвольте OpenClaw анализировать кадры по запросу или по триггеру. Спросите со своего телефона «пришли ли сегодня какие-нибудь посылки?» и получите точный ответ от собственного оборудования.

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