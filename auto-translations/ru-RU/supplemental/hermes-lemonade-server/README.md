<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинный перевод.** Эта страница была автоматически переведена с английского языка и не прошла проверку человеком. Она может содержать ошибки, а некоторые инструкции, команды, файлы для загрузки, сведения о доступности продуктов или иное содержимое могут отличаться в зависимости от языка или региона. В случае каких-либо несоответствий или расхождений преимущественную силу имеет оригинальная версия playbook на английском языке.
<!-- auto-translated-disclaimer:end -->

# Запуск Hermes Agent локально с помощью Lemonade Server

## Обзор

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) — это самообучающийся ИИ-агент, созданный компанией Nous Research. У него есть встроенный цикл обучения: он создаёт навыки на основе опыта, формирует постоянную память о том, кто вы, между сессиями и может выполнять от вашего имени запланированные автоматизации. В отличие от простого чат-ассистента, Hermes выполняет реальные действия: запускает команды оболочки, создаёт файлы, просматривает веб-страницы и делегирует параллельные рабочие потоки субагентам.

[**Lemonade Server**](https://lemonade-server.ai/) — это локальный бэкенд инференса, который обеспечивает его работу. Это сервер с открытым исходным кодом, который запускает GenAI-модели непосредственно на вашем оборудовании AMD и предоставляет их через отраслевой стандарт OpenAI API.

Вместе они образуют полностью локальный стек ИИ-агента: Lemonade выполняет инференс модели на вашем GPU, а Hermes обеспечивает цикл работы агента, память, навыки и шлюз обмена сообщениями.

> **Прежде чем продолжить:** Hermes Agent — это в высокой степени автономный ИИ-агент. Предоставление любому ИИ-агенту доступа к вашей системе может привести к непредсказуемым или нежелательным результатам. Продолжайте только в том случае, если вы понимаете риски и готовы к тому, что автономное программное обеспечение будет действовать от вашего имени.

---

## Чему вы научитесь

К концу этого руководства вы сможете:

- **Установить Hermes Agent** и направить его на **Lemonade Server** в качестве ИИ-бэкенда.
- **(Рекомендуется) Включить песочницу Docker/Podman**, чтобы изолировать действия агента от хост-системы.
- **Запустить шлюз Hermes** и убедиться, что ваш агент готов к работе.
- **Подключить канал связи** (Discord или Telegram), чтобы общаться с агентом с любого устройства.

---

<!-- @device:halo_box,halo,stx,krk -->
## Настройка конфигурации памяти

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Проверка обновлений ПО

<!-- @require:software-update -->
<!-- @device:end -->

## Установка необходимого ПО

<!-- @os:linux -->
- ПК с **Ubuntu 24.04+** или совместимым дистрибутивом Linux на базе Debian с `apt-get`
- Не менее **12 ГБ ОЗУ** (рекомендуется 64 ГБ+ для более крупных моделей)
- **~10–30 ГБ свободного места на диске** для весов моделей
- [Podman](https://podman.io/docs/installation) (опционально, для песочницы Hermes Agent)
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @os:windows -->
- ПК с **Windows 10/11**
- Не менее **12 ГБ ОЗУ** (рекомендуется 64 ГБ+ для более крупных моделей)
- **~10–30 ГБ свободного места на диске** для весов моделей
- Podman (опционально, для песочницы Hermes Agent). Устанавливается внутри WSL:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman предустановлен на Halo Box, и дополнительная настройка не требуется
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## Загрузка и запуск рекомендуемой модели

Рекомендуемая модель для этого руководства — **Qwen3.6-35B-A3B-GGUF** от Unsloth, мощная модель MoE с контекстным окном в 263 тыс. токенов, хорошо подходящая для рабочих нагрузок агентов. Эта модель использует квантование UD-Q4_K_XL. Загрузите её сейчас:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Затем запустите её с большим контекстным окном и сохраните эту настройку для последующих запусков:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

По умолчанию длина контекста модели составляет 262 144 токена. Если вы столкнётесь с ошибками нехватки памяти (OOM), рассмотрите возможность уменьшения контекстного окна.

> **Совет: отключите режим размышлений для более быстрых ответов агента:** Qwen3.6-35B-A3B по умолчанию работает в режиме размышлений, что добавляет задержку перед каждым ответом. Для циклов работы агента эта задержка быстро накапливается. Репозиторий [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) предоставляет готовую конфигурацию, отключающую режим размышлений. Чтобы её использовать, скачайте файл и импортируйте его:
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

## Настройка WSL

Мы запускаем Hermes Agent внутри WSL и подключаем его к Lemonade, работающему нативно в Windows. Это даёт вам среду оболочки Linux для Hermes, сохраняя при этом аппаратное ускорение GPU для Lemonade на стороне Windows.

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

WSL2 работает в виртуальной сети. Lemonade в Windows привязывается к `127.0.0.1`, к которому WSL не может обратиться напрямую. Прокси-сервер портов Windows перенаправляет трафик от IP-адреса шлюза WSL на локальный хост Windows.

**Найдите IP-адрес шлюза WSL** (выполните внутри WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Добавьте прокси портов** (выполните в PowerShell от имени администратора, заменив `<WSL-Gateway-IP>` на IP-адрес вашего шлюза WSL):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**Добавьте правило брандмауэра** (тот же PowerShell с повышенными правами):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Проверьте из WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

Если вы уже загрузили модель Qwen3.6-35B-A3B-GGUF на предыдущем шаге, вы должны увидеть вывод в формате JSON со списком загруженной модели.

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

> Правило `netsh portproxy` сохраняется после перезагрузок, но IP-адрес шлюза WSL может измениться после выполнения `wsl --shutdown`. Если Lemonade становится недоступным из WSL после перезапуска, получите обновлённый IP-адрес шлюза и обновите прокси с этим новым адресом.

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

## Установка Hermes Agent

<!-- @os:windows -->
> Выполняйте команды из этого раздела в терминале **WSL**, если не указано иное.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Флаг `--skip-setup` пропускает интерактивный мастер настройки, чтобы вы могли настроить бэкенд модели вручную на следующем шаге.

Перезагрузите оболочку:

```bash
source ~/.bashrc
```

Подтвердите установку:

```bash
hermes --version
```

Запустите самодиагностику для проверки всех зависимостей:

```bash
hermes doctor
```

> **Совет:** Если после установки вы видите `command not found`, добавьте Hermes в переменную PATH:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> Чтобы сделать это постоянным, добавьте указанную выше строку в файл `~/.bashrc` или `~/.zshrc`.

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
## Настройка Hermes для использования Lemonade

Hermes хранит конфигурацию модели в `~/.hermes/config.yaml`. Вы можете либо воспользоваться интерактивным выбором `hermes model`, либо написать конфигурацию напрямую.

### Вариант 1: Интерактивный выбор

<!-- @os:windows -->
> Выполните следующее внутри вашего **терминала WSL**.
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

При появлении запроса:

1. Выберите **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** используйте IP-адрес шлюза WSL: выполните `ip route show default | awk '{print $3}' | head -1` внутри WSL, чтобы получить его, затем введите `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1` (Auto-detect)
5. **Select model:** выберите `Qwen3.6-35B-A3B-GGUF` из списка
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade` (или любое предпочитаемое вами имя)

`hermes model` сохраняет как активный выбор модели, так и именованную запись `custom_providers`, которая хранит длину контекста вместе с эндпоинтом. Результат в `~/.hermes/config.yaml` выглядит так:

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

### Вариант 2: Написать конфигурацию напрямую

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

Внутри вашего терминала WSL получите IP-адрес хоста Windows и запишите конфигурацию:

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

## (Рекомендуется) Включение песочницы Podman

Hermes Agent может направлять все операции агента с командной оболочкой и файлами через изолированный контейнер, а не выполнять их напрямую на вашем хосте. Это ограничивает область воздействия любого непреднамеренного действия песочницей, оставляя файловую систему и сеть вашего хоста нетронутыми.

Соберите облегчённый образ песочницы:

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
Войдите в терминал WSL:

```powershell
wsl -d Ubuntu-24.04
```

Затем соберите облегчённый образ песочницы:

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

Затем настройте Hermes на использование Podman в качестве среды выполнения контейнеров и задайте бэкенд терминала:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> `terminal.backend` по-прежнему остаётся `docker`.
> Именно `HERMES_DOCKER_BINARY` указывает Hermes использовать Podman в качестве среды выполнения.

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

Теперь Hermes запустит постоянный контейнер-песочницу и будет направлять все вызовы `terminal` и файловых инструментов через него. Контейнер существует в течение всего времени работы процесса Hermes, повторно используется для всех вызовов инструментов и уничтожается при завершении работы Hermes.

> **Проверка работы песочницы:** Запустите Hermes (`hermes`) и попросите его выполнить `run hostname` — вы должны увидеть короткий идентификатор контейнера вместо имени вашей машины. Вы также можете попросить его выполнить `rm -rf <path-to-a-dummy-file/folder>`: Hermes подтвердит удаление, но папка останется на вашем хосте. Команда была выполнена внутри изолированного `$HOME` контейнера, а не вашего.

> **Нужна более строгая изоляция?** Hermes также предоставляет официальный образ Docker (`nousresearch/hermes-agent`), который запускает весь процесс агента внутри контейнера — шлюз, инструменты и всё остальное. Подробности настройки см. в [документации Hermes Docker](https://hermes-agent.nousresearch.com/docs/user-guide/docker).

---

<!-- @os:linux -->
## (Рекомендуется) Интеграция Hermes с сервисами Firecrawl

Hermes может просматривать веб-сайты и извлекать контент из них с помощью встроенных веб-инструментов. Однако многие современные веб-сайты используют системы обнаружения ботов, которые блокируют простые HTTP-запросы и возвращают страницы-испытания вместо реального контента. В результате Hermes может быть не в состоянии надёжно извлечь информацию с таких сайтов.

Чтобы преодолеть это ограничение, [Firecrawl](https://docs.firecrawl.dev/introduction) предоставляет самостоятельно размещаемый сервис веб-обхода и извлечения контента, который может обходить эти проверки и раскрыть весь потенциал автоматизации Hermes.

В данной настройке Firecrawl работает как набор контейнеров Docker, управляемых с помощью Podman. Чтобы упростить управление жизненным циклом и автоматический запуск, мы регистрируем Firecrawl как пользовательскую службу `systemd`, которая оркестрирует базовый стек Podman Compose. Это позволяет Hermes запускать, останавливать и проверять службу Firecrawl с помощью стандартных команд `systemctl --user`, вместо того чтобы взаимодействовать с контейнерами напрямую.

Чтобы всё было проще, мы разбили весь процесс на четыре шага:

---

### 1. Зарегистрируйте системную службу
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
На этом этапе служба определена, но ещё не зарегистрирована в `systemd`.
Убедитесь, что имя файла точно совпадает с тем, что вы создали выше, затем выполните:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
В случае успеха вы должны увидеть следующий вывод:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

`default.target.wants/` содержит символические ссылки на службы, настроенные для автоматического запуска.

### 2. Настройте Firecrawl для вашего сервиса

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) идеально подходит для тех, кому нужен полный контроль над средой скрапинга и обработки данных, но это сопровождается дополнительными затратами на обслуживание и настройку.

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
> Установите `BULL_AUTH_KEY` в качестве надёжного секрета, особенно для любого развёртывания, доступного из ненадёжных сетей.
### 3. Развертывание Hermes через Compose

Прежде чем продолжить, убедитесь, что вы загрузили последний Docker-образ Hermes:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
После этого загрузите файл Compose для Hermes [hermes-compose.yaml](assets/hermes-compose.yaml) и поместите его в корневой каталог `/firecrawl`:

> Это соглашение необходимо для того, чтобы `systemd` мог найти и корректно запустить службу, как указано в `WorkingDirectory=${HOME}/firecrawl`.

> Вы всегда можете расширить стек, добавив дополнительные службы Firecrawl по мере необходимости. Полный список доступных служб можно найти в официальном [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml).

### 4. Запуск службы Hermes через Firecrawl 

Прежде чем передавать управление `systemd`, убедитесь, что всё работает корректно, запустив стек вручную:
```bash
podman compose -f hermes-compose.yaml up -d
```
Если всё настроено правильно, вы увидите, как поднимается контейнер Hermes, и вывод в командной строке должен выглядеть примерно так:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

После проверки остановите стек, прежде чем продолжить:
```bash
podman compose -f hermes-compose.yaml down
```
Теперь, когда всё проверено, запустите службу через `systemd`:
```bash
systemctl --user start firecrawl.service
```
[API Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) доступен изнутри интерактивного контейнера, а веб-панель управления доступна на том же хосте и порту по адресу http://127.0.0.1:9119.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

Чтобы остановить службу, выполните:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native

Запустите интерактивную CLI-сессию напрямую: 

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

**Поздравляем, вы создали полностью локальный стек ИИ-агента.**

### Веб-панель управления

Hermes включает в себя веб-интерфейс на базе браузера для управления конфигурацией, ключами API, моделями, сессиями, памятью и заданиями cron. Откройте второй терминал, пока шлюз или CLI работают, и запустите его с помощью:

```bash
hermes dashboard
```

Это запускает локальный сервер и открывает `http://127.0.0.1:9119` в вашем браузере. Полный справочник по функциям см. в [документации по панели управления](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard).
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## Опционально: подключение канала связи

Как только шлюз запущен, вы можете получить доступ к своему локальному агенту с любого устройства. Hermes поддерживает [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) и другие

---

### Discord

Для Discord требуется сервер, на котором **у вас есть права администратора**, чтобы добавить бота. Если у вас есть общие серверы, но нет собственного, используйте Telegram.

#### Создание приложения и бота Discord

1. Перейдите на [портал разработчиков Discord](https://discord.com/developers/applications) и нажмите **New Application**. Задайте имя (например, "hermes-bot").
2. В боковой панели нажмите **Bot**. Задайте имя пользователя для бота.
3. На странице Bot прокрутите вниз до **Privileged Gateway Intents** и включите:
   - **Message Content Intent** (обязательно)
   - **Server Members Intent** (рекомендуется)
4. Прокрутите обратно вверх и нажмите **Reset Token**, чтобы сгенерировать токен бота. Скопируйте его.

#### Добавление бота на ваш сервер

1. В боковой панели нажмите **OAuth2 / URL Generator**.
2. В разделе **Scopes** включите `bot` и `applications.commands`.
3. В разделе **Bot Permissions** включите: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Скопируйте сгенерированный URL, вставьте его в браузер, выберите свой сервер и подтвердите.

#### Сбор идентификаторов и разрешение личных сообщений

Включите режим разработчика в Discord (**User Settings / Advanced / Developer Mode**), затем:
- Щёлкните правой кнопкой мыши по значку сервера: **Copy Server ID**
- Щёлкните правой кнопкой мыши по своему аватару: **Copy User ID**

Щёлкните правой кнопкой мыши по значку сервера / **Privacy Settings** / включите **Direct Messages**. Это необходимо для этапа сопряжения.

#### Настройка Hermes для Discord

Добавьте следующее в `~/.hermes/.env`:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

Затем запустите шлюз:

```bash
hermes gateway
```

Бот должен появиться в сети в Discord в течение нескольких секунд. Отправьте ему сообщение — либо личное, либо в канале, который он видит.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Создание бота Telegram

1. Откройте Telegram и напишите **@BotFather**.
2. Отправьте `/newbot` и следуйте подсказкам. Сохраните токен бота, который он вам выдаст.

#### Настройка Hermes для Telegram

Добавьте следующее в `~/.hermes/.env`:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **Не знаете свой идентификатор пользователя Telegram?** Напишите [@userinfobot](https://t.me/userinfobot) в Telegram, он ответит вашим числовым ID.

Затем запустите шлюз:

```bash
hermes gateway
```

Отправьте вашему боту любое сообщение в Telegram, чтобы протестировать его. Теперь вы можете общаться со своим агентом через личные сообщения Telegram. Полное руководство по настройке Telegram, включая режим webhook и расширенные параметры, см. в [полном руководстве по настройке Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram).

---

## Дальнейшие шаги

Теперь, когда ваш агент может получать команды с телефона и выполнять действия на локальной машине, вот три направления, которые стоит изучить:

1. **Автоматическая исследовательская сводка**: настройте Hermes на поиск в интернете интересующих вас тем каждое утро, суммирование результатов с помощью вашей локальной модели и отправку сводки на ваш телефон через Telegram или Discord — всё это работает на вашем собственном оборудовании без затрат на облако.

2. **Проверка кода по запросу**: укажите Hermes на репозиторий GitHub, попросите его проверить открытые pull-запросы и опубликовать комментарии или сводку обратно в ваш чат. Благодаря бэкенду терминала Docker все операции git выполняются внутри песочницы, оставляя ваш хост чистым.

3. **Локальный файловый помощник**: предоставьте Hermes доступ к рабочему каталогу и попросите его организовывать, переименовывать, суммировать или преобразовывать файлы по запросу с вашего телефона. Поскольку бэкенд терминала Docker ограничивает все операции записи рабочим пространством песочницы, случайные разрушительные операции локализованы.