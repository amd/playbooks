<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# Запуск OpenClaw с Lemonade Server в качестве бэкенда

## Обзор

[**OpenClaw**](https://openclaw.ai/) — это автономный агент ИИ, который может писать и запускать код, управлять файлами и выполнять сложные многошаговые задачи от вашего имени. В отличие от чат-ассистента, который просто отвечает на вопросы, OpenClaw совершает реальные действия в вашей системе, а значит, ему нужен быстрый и мощный бэкенд ИИ, способный справляться с интенсивным агентным циклом.

[**Lemonade Server**](https://lemonade-server.ai/) — именно такой бэкенд. Это локальный сервер инференса с открытым исходным кодом, который запускает модели GenAI непосредственно на вашем оборудовании и предоставляет к ним доступ через стандартный отраслевой OpenAI API.

Вместе они образуют полностью локальный стек агента ИИ: Lemonade обеспечивает инференс модели, а OpenClaw предоставляет агентный цикл, который превращает выходные данные модели в реальные действия.

> **Прежде чем продолжить:** OpenClaw — это высокоавтономный агент ИИ. Предоставление любому агенту ИИ доступа к вашей системе может привести к непредсказуемым или нежелательным последствиям. Продолжайте только в том случае, если вы понимаете риски и готовы к тому, что автономное программное обеспечение будет действовать от вашего имени.

---

## Чему вы научитесь

По завершении этого руководства вы сможете:

- Узнать о **Lemonade Server**
- **Установить OpenClaw** и **подключить его к Lemonade Server** в качестве бэкенда ИИ.
- **Запустить шлюз OpenClaw** и убедиться, что ваш агент готов к работе.
- **Подключить канал связи** (Discord или Telegram), чтобы общаться с агентом с любого устройства.

---

## Настройка конфигурации памяти

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Проверка обновлений программного обеспечения

<!-- @require:software-update -->
<!-- @device:end -->

## Установка необходимых программных компонентов

<!-- @os:linux -->
- ПК под управлением **Ubuntu 24.04+** или совместимого дистрибутива Linux на основе Debian с `apt-get`
- Не менее **12 ГБ оперативной памяти** (рекомендуется 64 ГБ+ для более крупных моделей)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (необязательно, для изоляции OpenClaw в песочнице)

- **~10–30 ГБ свободного места на диске** для весов модели
<!-- @os:end -->
<!-- @os:windows -->
- ПК под управлением **Windows 10/11**
- Не менее **12 ГБ оперативной памяти** (рекомендуется 64 ГБ+ для более крупных моделей)
- **~10–30 ГБ свободного места на диске** для весов модели
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (необязательно, для изоляции OpenClaw в песочнице)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Загрузка и подключение рекомендуемой модели

Рекомендуемая для этого руководства модель — **Qwen3.6-35B-A3B-GGUF** от Unsloth, мощная модель MoE с контекстным окном в 263 тысячи токенов, хорошо подходящая для агентных задач. Эта модель использует квантизацию UD-Q4_K_XL. Загрузите её сейчас:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Затем загрузите её с большим контекстным окном и сохраните эту настройку для будущих запусков:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

Модель имеет контекстную длину по умолчанию 262 144 токена. Если вы столкнётесь с ошибками нехватки памяти (OOM), рассмотрите возможность уменьшения контекстного окна. Однако, поскольку Qwen3.6 использует расширенный контекст для сложных задач, мы рекомендуем сохранять контекстную длину не менее 128K токенов для сохранения возможностей мышления.

> **Совет: отключите режим мышления для более быстрых ответов агента:** Qwen3.6-35B-A3B по умолчанию работает в режиме мышления, что добавляет задержку перед каждым ответом. В агентных циклах эти накладные расходы быстро накапливаются. Репозиторий [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) предоставляет готовую конфигурацию, отключающую режим мышления. Чтобы использовать её, скачайте файл и импортируйте его:
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

Мы запускаем OpenClaw внутри WSL (рекомендуется) и подключаем его к Lemonade, работающему нативно на Windows. Это даёт вам среду оболочки Linux для OpenClaw, сохраняя при этом аппаратное ускорение GPU Lemonade на стороне Windows.

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

Перезапустите WSL:

```powershell
wsl --shutdown
wsl
```

### Проброс Lemonade из Windows в WSL

WSL2 работает в виртуальной сети. Lemonade на Windows привязывается к `127.0.0.1`, который WSL не может достичь напрямую. Прокси портов Windows перенаправляет трафик с IP-адреса шлюза WSL на localhost Windows.

**Найдите IP-адрес шлюза WSL** (выполните внутри WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Добавьте прокси порта** (выполните в PowerShell от имени администратора, заменив `<WSL-Gateway-IP>` на IP-адрес вашего шлюза WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Добавьте правило брандмауэра** (в том же PowerShell с повышенными правами):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Проверьте из WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Если вы уже загрузили модель Qwen3.6-35B-A3B-GGUF на предыдущем шаге, вы должны увидеть вывод JSON следующего вида:

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

> Правило `netsh portproxy` сохраняется после перезагрузки, однако IP-адрес шлюза WSL может измениться после `wsl --shutdown`. Если Lemonade становится недоступен из WSL после перезапуска, получите обновлённый IP-адрес шлюза и обновите прокси с этим новым IP.

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
> Выполняйте команды из этого раздела в вашем **терминале WSL**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

Флаг `--no-onboard` пропускает интерактивный мастер настройки — вы настроите бэкенд модели вручную на следующем шаге, что даёт вам точный контроль над тем, какая модель и сервер используются.

Откройте новый терминал и подтвердите установку:

```bash
openclaw --version
```

> **Совет:** Если после установки вы видите `command not found`, добавьте глобальный каталог bin npm в ваш PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> Чтобы сделать это постоянным, добавьте строку выше в ваш файл `~/.bashrc` или `~/.zshrc`.

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

Запустите неинтерактивную первоначальную настройку OpenClaw.
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

> **Настройка размера контекстного окна OpenClaw:** Сжатие контекста OpenClaw срабатывает, когда `contextTokens > contextWindow − reserveTokens`. Значение `reserveTokensFloor` по умолчанию равно 20 000 токенов — это нижняя граница, которая переопределяет `reserveTokens`, если оно меньше, поэтому любой контекст модели ниже ~37k будет вызывать бесконечный цикл сжатия. Установите низкое значение резерва и отключите нижнюю границу один раз в конфигурации — это применится ко всем моделям без необходимости настройки для каждой:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` — это *нижняя граница* (минимальная защита), а не сам резерв; установка только нижней границы не имеет эффекта. `reserveTokensFloor: 0` отключает защиту, так что меньшее значение `reserveTokens` принимается.
>
> **Когда применять это:** Используйте эту конфигурацию, если эффективное контекстное окно вашей модели ниже ~37k — либо потому что модель небольшая (например, 8k, 16k, 32k), либо потому что вы намеренно ограничили его до меньшего значения (например, загружаете модель с 128k, но устанавливаете контекст 16k в Lemonade). Без этого OpenClaw входит в бесконечный цикл сжатия при запуске.
>
> **Модели с большим контекстом при полном контексте:** Вы можете полностью пропустить это. Настройки по умолчанию работают нормально — сжатие сработает задолго до заполнения окна, и у модели будет достаточно места для генерации длинных ответов. Если вы всё же применяете это, имейте в виду, что `reserveTokens: 4096` ограничивает длину ответа примерно до 4k токенов, что может обрезать длинную генерацию файлов или подробные планы.
>
> **Куда добавить это:** Поместите блок `compaction` внутри `agents.defaults` в вашем `openclaw.json` (обычно находится по пути `~/.openclaw/openclaw.json`):
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
> Остальная часть вашей конфигурации (шлюз, каналы, модели и т.д.) остаётся без изменений — нужно добавить только ключ `compaction`.

### (Рекомендуется) Включение изоляции в Docker-песочнице

OpenClaw может направлять все операции агента с файлами и кодом через изолированный Docker-контейнер, а не выполнять их непосредственно на хосте. Это ограничивает последствия любых непреднамеренных действий рамками песочницы, оставляя файловую систему и сеть хоста нетронутыми.

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

Контейнеры песочницы **не имеют доступа к сети** по умолчанию. Смотрите [справочник по изоляции в песочнице](https://docs.openclaw.ai/gateway/sandboxing) для настройки монтирования томов и переопределения сети.

> #### Устранение неполадок: отказ в доступе к Docker
> 
> Если вы получаете ошибку «permission denied» при выполнении команд Docker:
> 
> **Шаг 1: Добавьте вашего пользователя в группу docker**
> 
> ```bash
> sudo groupadd docker                    # Создать группу, если нужно
> sudo usermod -aG docker $USER           # Добавить себя в группу
> newgrp docker                           # Активировать изменение
> docker run hello-world                  # Проверить
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

### Запуск шлюза OpenClaw

Шлюз — это процесс OpenClaw, который управляет агентным циклом и обслуживает панель управления:

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

Чтобы открыть панель управления, выполните это во втором терминале, пока шлюз ещё работает:

```bash
openclaw dashboard
```

Поскольку шлюз привязан к loopback, панель управления автоматически аутентифицируется при открытии с той же машины — ввод токена или подтверждение устройства для локального доступа не требуются. Вы должны увидеть панель управления OpenClaw с вашей моделью Lemonade, указанной в качестве активного бэкенда.

> Если вы включили изоляцию в песочнице, вы можете проверить её, попросив агента выполнить `run hostname` из панели управления. Если вы видите короткий идентификатор контейнера вместо имени вашей машины, песочница работает.

**Поздравляем, вы создали полностью локальный стек агента ИИ с нуля.**

> **Нужен токен шлюза?** Выполните `openclaw dashboard --no-open`, чтобы вывести URL панели управления со встроенным токеном (также будет предпринята попытка скопировать его в буфер обмена). Кроме того, токен находится в `gateway.auth.token` в `~/.openclaw/openclaw.json`.
>
> **Подтверждение удалённого устройства:** Когда вы открываете панель управления со второй машины или телефона, браузер отображает идентификатор запроса. На машине, где запущен шлюз, выполните:
> ```bash
> openclaw devices approve <requestId>
> ```
> Это требуется только для удалённых или дополнительных устройств — доступ через loopback с той же машины аутентифицируется автоматически.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Необязательно: подключение канала связи

После запуска шлюза вы можете получить доступ к своему локальному агенту с любого устройства. Выберите вариант, подходящий для вашей конфигурации. OpenClaw поддерживает [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) и другие каналы — полный список смотрите на [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Вариант А: Discord

Discord требует сервера, на котором **у вас есть права администратора** для добавления бота. Если вы состоите на серверах, но не владеете ни одним из них, используйте вариант Б (Telegram).

#### Создание аккаунта и сервера Discord

Если у вас нет аккаунта Discord, зарегистрируйтесь на [discord.com](https://discord.com). Вам также нужен сервер, на котором вы являетесь администратором — создайте его, нажав значок **+** на боковой панели Discord и выбрав **Создать сервер**. Подойдёт приватный сервер.

#### Создание приложения и бота Discord

1. Перейдите на [Discord Developer Portal](https://discord.com/developers/applications) и нажмите **New Application**. Дайте ему имя (например, «openclaw-bot»).
2. На боковой панели нажмите **Bot**. Задайте имя пользователя для бота.
3. На той же странице Bot прокрутите до **Privileged Gateway Intents** и включите:
   - **Message Content Intent** (обязательно)
   - **Server Members Intent** (рекомендуется)
4. Прокрутите обратно вверх и нажмите **Reset Token**, чтобы сгенерировать токен бота. Скопируйте его.

#### Добавление бота на ваш сервер

1. На боковой панели нажмите **OAuth2/ URL Generator**.
2. В разделе **Scopes** включите `bot` и `applications.commands`.
3. В разделе **Bot Permissions** включите: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Скопируйте сгенерированный URL, вставьте его в браузер, выберите ваш сервер и подтвердите. Бот должен появиться в списке участников вашего сервера.

#### Получение ваших идентификаторов

Включите режим разработчика в Discord (**Настройки пользователя/ Расширенные/ Режим разработчика**), затем:
- Щёлкните правой кнопкой мыши по значку вашего сервера: **Копировать ID сервера**
- Щёлкните правой кнопкой мыши по своему аватару: **Копировать ID пользователя**

#### Разрешение личных сообщений от участников сервера

Щёлкните правой кнопкой мыши по значку вашего сервера/ **Настройки приватности**/ включите **Личные сообщения**. Это позволяет боту отправлять вам личные сообщения, что необходимо для шага сопряжения.

#### Настройка OpenClaw для Discord

Сохраните токен бота как переменную окружения, затем создайте единый файл патча, который включает Discord, ссылается на токен и добавляет ваш сервер в список разрешённых. Замените `<server_id>` и `<user_id>` на идентификаторы, полученные выше.

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

> **Не полагайтесь на просьбу агента настроить это.** Когда изоляция в песочнице включена, агент не может записывать в `~/.openclaw/openclaw.json` изнутри песочницы — используйте команды CLI выше на хосте.

Перезапустите шлюз, чтобы он подхватил новую конфигурацию канала:

```bash
openclaw gateway run --bind loopback --port 18789
```

В течение нескольких секунд в выводе шлюза должно появиться сообщение `logged in to discord as <bot-name>`.

#### Сопряжение вашего аккаунта Discord

Напишите боту личное сообщение в Discord. Он ответит коротким кодом сопряжения.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Подтвердите его на машине, где запущен OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Коды сопряжения действительны в течение одного часа.

Теперь вы можете общаться с вашим агентом напрямую из Discord и передавать задачи на ваше локальное оборудование.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Вариант Б: Telegram

Telegram проще Discord для большинства пользователей — он не требует сервера и прав администратора.

#### Создание бота Telegram

1. Откройте Telegram и напишите **@BotFather**.
2. Отправьте `/newbot` и следуйте инструкциям. Сохраните токен бота, который он вам выдаст.

#### Настройка OpenClaw для Telegram

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

Перезапустите шлюз, затем отправьте боту любое сообщение в Telegram. Подтвердите сопряжение:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Коды сопряжения действительны в течение одного часа. Теперь вы можете общаться с вашим агентом через личные сообщения в Telegram.

---

## Дальнейшие шаги

Теперь, когда ваш агент может получать команды с вашего телефона и действовать на вашей локальной машине, вот три направления, которые стоит изучить:

1. **Сводка фондового рынка**: настройте OpenClaw на получение данных из финансовых API с фиксированным интервалом, суммирование дневных движений с помощью вашей локальной модели и отправку дайджеста на ваш телефон каждое утро через выбранный канал.

2. **Монитор дообучения**: запустите задание обучения удалённо через Telegram или Discord, затем пусть агент отслеживает журнал обучения и периодически сообщает значения потерь, загрузку GPU и использование диска на ваш телефон. Если выполнение зависнет или VRAM резко возрастёт, вы узнаете об этом немедленно, не находясь у машины.

3. **IoT с локальной VLM**: направьте камеру на входную дверь, запустите модель зрения на Lemonade и пусть OpenClaw анализирует кадры по запросу или по триггеру. Спросите «приходили ли сегодня посылки?» с телефона и получите прямой ответ от вашего собственного оборудования.