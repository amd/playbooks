<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **기계 번역.** 이 페이지는 영어에서 자동으로 번역되었으며 사람에 의한 검토를 거치지 않았습니다. 이 페이지에는 오류가 포함될 수 있으며, 특정 지침, 명령어, 다운로드, 제품 가용성 또는 기타 콘텐츠가 언어나 지역에 따라 다를 수 있습니다. 본 번역본과 원문 사이에 불일치 또는 차이가 있는 경우, 영어 원문 playbook이 우선하며 이에 따릅니다.
<!-- auto-translated-disclaimer:end -->

#로컬 환경에서 Lemonade Server로 Hermes Agent 실행하기

## 개요

[**Hermes Agent**](https://hermes-agent.nousresearch.com/)는 Nous Research에서 개발한 자기 개선형 AI 에이전트입니다. 내장된 학습 루프를 통해 경험으로부터 스킬을 만들고, 세션 전반에 걸쳐 사용자에 대한 영구적인 메모리를 구축하며, 사용자를 대신하여 예약된 자동화 작업을 실행할 수 있습니다. 단순한 채팅 어시스턴트와 달리, Hermes는 셸 명령 실행, 파일 작성, 웹 브라우징, 병렬 작업 흐름을 서브에이전트에 위임하는 등 실제 작업을 수행합니다.

[**Lemonade Server**](https://lemonade-server.ai/)는 이를 구동하는 로컬 추론 백엔드입니다. AMD 하드웨어에서 직접 GenAI 모델을 실행하고 업계 표준 OpenAI API를 통해 이를 노출하는 오픈소스 서버입니다.

두 소프트웨어를 함께 사용하면 완전한 로컬 AI 에이전트 스택을 구성할 수 있습니다. Lemonade는 GPU에서 모델 추론을 처리하고, Hermes는 에이전트 루프, 메모리, 스킬, 메시징 게이트웨이를 제공합니다.

> **계속하기 전에:** Hermes Agent는 매우 자율적인 AI 에이전트입니다. 어떤 AI 에이전트에게든 시스템 접근 권한을 부여하면 예측할 수 없거나 의도하지 않은 결과가 발생할 수 있습니다. 위험성을 이해하고 자율 소프트웨어가 사용자를 대신하여 작동하는 것에 문제가 없다고 판단될 때만 진행하세요.

---

## 학습 내용

이 플레이북을 완료하면 다음을 수행할 수 있습니다:

- **Hermes Agent를 설치**하고 이를 AI 백엔드인 **Lemonade Server**에 연결하기
- **(권장) Docker/Podman 샌드박싱을 활성화**하여 에이전트의 작업을 호스트로부터 격리하기
- **Hermes 게이트웨이를 시작**하고 에이전트가 준비되었는지 확인하기
- **통신 채널(Discord 또는 Telegram)을 연결**하여 모든 기기에서 에이전트와 대화하기

---

## 메모리 구성 설정

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 소프트웨어 업데이트 확인

<!-- @require:software-update -->
<!-- @device:end -->

## 소프트웨어 사전 요구 사항 설치

<!-- @os:linux -->
- `apt-get`을 사용하는 **Ubuntu 24.04+** 또는 호환되는 Debian 기반 Linux 배포판이 설치된 PC
- 최소 **12GB의 RAM** (더 큰 모델의 경우 64GB 이상 권장)
- 모델 가중치를 위한 **약 10~30GB의 여유 디스크 공간**
- [Podman](https://podman.io/docs/installation) (선택 사항, Hermes Agent 샌드박싱용)
  ```bash 
  sudo apt-get install -y podman`
  ```
<!-- @os:end -->

<!-- @os:windows -->
- **Windows 10/11**이 설치된 PC
- 최소 **12GB의 RAM** (더 큰 모델의 경우 64GB 이상 권장)
- 모델 가중치를 위한 **약 10~30GB의 여유 디스크 공간**
- Podman (선택 사항, Hermes Agent 샌드박싱용). WSL 내부에 설치:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman은 Halo Box에 사전 설치되어 있으며 별도 설정이 필요하지 않습니다
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## 권장 모델 다운로드 및 로드

이 플레이북에서 권장하는 모델은 Unsloth의 **Qwen3.6-35B-A3B-GGUF**로, 263k 토큰 컨텍스트 윈도우를 갖춘 강력한 MoE 모델이며 에이전트 워크로드에 적합합니다. 이 모델은 UD-Q4_K_XL 양자화를 사용합니다. 지금 다운로드하세요:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

그런 다음 큰 컨텍스트 윈도우로 모델을 로드하고 이후 실행을 위해 해당 설정을 저장합니다:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

이 모델의 기본 컨텍스트 길이는 262,144 토큰입니다. 메모리 부족(OOM) 오류가 발생하면 컨텍스트 윈도우를 줄이는 것을 고려하세요.

> **팁: 더 빠른 에이전트 응답을 위해 씽킹 비활성화하기:** Qwen3.6-35B-A3B는 기본적으로 씽킹 모드로 실행되며, 이는 각 응답 전에 지연 시간을 추가합니다. 에이전트 루프에서는 이러한 오버헤드가 빠르게 누적됩니다. [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) 저장소에서는 씽킹을 비활성화하는 준비된 구성 파일을 제공합니다. 이를 사용하려면 파일을 다운로드한 후 가져오세요:
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

## WSL 설정

Hermes Agent는 WSL 내부에서 실행하고 Windows에서 네이티브로 실행되는 Lemonade에 연결합니다. 이를 통해 Lemonade의 GPU 가속을 Windows 측에서 유지하면서 Hermes를 위한 Linux 셸 환경을 제공받을 수 있습니다.

### WSL 및 Ubuntu 설치

관리자 권한으로 PowerShell을 열고 WSL 커널을 설치합니다:

```powershell
wsl --install --no-distribution
```

그런 다음 Ubuntu를 설치합니다:

```powershell
wsl --install -d Ubuntu-24.04
```

### WSL에서 systemd 활성화

Ubuntu 터미널 내부에서 다음을 실행합니다:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

WSL을 재시작합니다:

```powershell
wsl --shutdown
wsl
```

### Windows에서 WSL로 Lemonade 브리지 연결

WSL2는 가상 네트워크에서 실행됩니다. Windows의 Lemonade는 `127.0.0.1`에 바인딩되며, WSL은 이를 직접 접근할 수 없습니다. Windows 포트 프록시는 WSL 게이트웨이 IP에서 Windows localhost로 트래픽을 전달합니다.

**WSL 게이트웨이 IP 찾기** (WSL 내부에서 실행):

```bash
ip route show default | awk '{print $3}' | head -1
```

**포트 프록시 추가** (관리자 권한 PowerShell에서 실행, `<WSL-Gateway-IP>`를 WSL 게이트웨이 IP로 대체):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**방화벽 규칙 추가** (동일한 관리자 권한 PowerShell에서):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**WSL에서 확인**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

이전 단계에서 이미 Qwen3.6-35B-A3B-GGUF 모델을 로드했다면, 로드된 모델을 나열하는 JSON 출력이 표시되어야 합니다.

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

> `netsh portproxy` 규칙은 재부팅 후에도 유지되지만, `wsl --shutdown` 이후에는 WSL 게이트웨이 IP가 변경될 수 있습니다. 재시작 후 WSL에서 Lemonade에 접근할 수 없게 되면, 업데이트된 게이트웨이 IP를 확인하고 이 새 IP로 프록시를 업데이트하세요.

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

## Hermes Agent 설치

<!-- @os:windows -->
> 별도로 명시되지 않은 한 이 섹션의 명령은 **WSL 터미널** 내부에서 실행하세요.
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

`--skip-setup` 플래그는 대화형 설정 마법사를 건너뛰어 다음 단계에서 모델 백엔드를 수동으로 구성할 수 있도록 해줍니다.

셸을 다시 로드합니다:

```bash
source ~/.bashrc
```

설치를 확인합니다:

```bash
hermes --version
```

모든 종속성을 확인하기 위해 자체 진단을 실행합니다:

```bash
hermes doctor
```

> **팁:** 설치 후 `command not found`가 표시되면 Hermes를 PATH에 추가하세요:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> 이를 영구적으로 적용하려면 위 줄을 `~/.bashrc` 또는 `~/.zshrc`에 추가하세요.

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
## Hermes에서 Lemonade를 사용하도록 구성하기

Hermes는 모델 구성을 `~/.hermes/config.yaml`에 저장합니다. 대화형 `hermes model` 선택기를 사용하거나 구성 파일을 직접 작성할 수 있습니다.

### 옵션 1: 대화형 선택기

<!-- @os:windows -->
> 다음 명령을 **WSL 터미널** 안에서 실행하세요.
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

메시지가 표시되면:

1. **Custom endpoint (enter URL manually)**를 선택합니다
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** WSL 게이트웨이 IP를 사용합니다. WSL 내부에서 `ip route show default | awk '{print $3}' | head -1`을 실행하여 확인한 다음 `http://<WSL-Gateway-IP>:13305/api/v1`을 입력합니다
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1` (자동 감지)
5. **Select model:** 목록에서 `Qwen3.6-35B-A3B-GGUF`를 선택합니다
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade` (원하는 이름을 사용해도 됩니다)

`hermes model`은 활성 모델 선택과 함께 엔드포인트와 컨텍스트 길이를 저장하는 이름 있는 `custom_providers` 항목을 저장합니다. `~/.hermes/config.yaml`의 결과는 다음과 같습니다:

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

### 옵션 2: 구성 파일 직접 작성하기

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

WSL 터미널 안에서 Windows 호스트 IP를 확인하고 구성 파일을 작성합니다:

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

## (권장) Podman 샌드박싱 활성화하기

Hermes Agent는 모든 에이전트 셸 및 파일 작업을 호스트에서 직접 실행하는 대신 격리된 컨테이너를 통해 라우팅할 수 있습니다. 이를 통해 의도하지 않은 작업의 영향 범위를 샌드박스로 제한하고, 호스트 파일 시스템과 네트워크는 영향을 받지 않도록 유지할 수 있습니다.

경량 샌드박스 이미지를 빌드합니다:

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
WSL 터미널로 진입합니다:

```powershell
wsl -d Ubuntu-24.04
```

그런 다음, 경량 샌드박스 이미지를 빌드합니다:

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

그런 다음 Hermes가 컨테이너 런타임으로 Podman을 사용하도록 구성하고 터미널 백엔드를 설정합니다:

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> `terminal.backend`는 여전히 `docker`입니다.
> `HERMES_DOCKER_BINARY`는 Hermes에게 런타임으로 Podman을 대신 사용하도록 지시하는 역할을 합니다.

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

이제 Hermes는 지속적인 샌드박스 컨테이너를 생성하고 모든 `terminal` 및 파일 도구 호출을 이 컨테이너를 통해 라우팅합니다. 이 컨테이너는 Hermes 프로세스의 생명 주기를 공유하며, 모든 도구 호출에서 재사용되고, Hermes가 종료되면 삭제됩니다.

> **샌드박스가 작동하는지 확인하기:** Hermes를 시작하고(`hermes`) `run hostname`을 요청해 보세요. 여러분 컴퓨터의 호스트 이름 대신 짧은 컨테이너 ID가 표시되어야 합니다. 또한 `rm -rf <path-to-a-dummy-file/folder>`를 요청해 볼 수도 있습니다. Hermes는 삭제를 확인해 주지만, 실제로는 해당 폴더가 여러분의 호스트에 그대로 남아 있습니다. 이 명령은 여러분의 `$HOME`이 아니라 컨테이너의 격리된 `$HOME` 내부에서 실행되었기 때문입니다.

> **더 강력한 격리가 필요하신가요?** Hermes는 게이트웨이, 도구 등 전체 에이전트 프로세스를 컨테이너 내부에서 실행하는 공식 Docker 이미지(`nousresearch/hermes-agent`)도 제공합니다. 설정 방법은 [Hermes Docker 문서](https://hermes-agent.nousresearch.com/docs/user-guide/docker)를 참조하세요.

---

<!-- @os:linux -->
## (권장) Firecrawl 서비스와 Hermes 통합하기

Hermes는 내장된 웹 도구를 사용하여 웹사이트를 탐색하고 콘텐츠를 추출할 수 있습니다. 하지만 많은 최신 웹사이트는 봇 탐지 시스템을 사용하여 단순한 HTTP 요청을 차단하고 실제 콘텐츠 대신 챌린지 페이지를 반환합니다. 그 결과, Hermes가 이러한 사이트에서 정보를 안정적으로 추출하지 못할 수 있습니다.

이러한 한계를 극복하기 위해, [Firecrawl](https://docs.firecrawl.dev/introduction)은 이러한 챌린지를 우회하여 Hermes 자동화의 잠재력을 최대한 활용할 수 있는 자체 호스팅형 웹 크롤링 및 콘텐츠 추출 서비스를 제공합니다.

이 설정에서 Firecrawl은 Podman으로 관리되는 일련의 Docker 컨테이너로 실행됩니다. 수명 주기 관리와 자동 시작을 간소화하기 위해, 기본이 되는 Podman Compose 스택을 조율하는 사용자 수준 `systemd` 서비스로 Firecrawl을 등록합니다. 이를 통해 Hermes는 컨테이너와 직접 상호작용하는 대신 표준 `systemctl --user` 명령을 사용하여 Firecrawl 서비스를 시작, 중지 및 확인할 수 있습니다.

간단하게 진행할 수 있도록, 전체 과정을 네 단계로 나누었습니다:

---

### 1. 시스템 서비스 등록하기
systemd 사용자 구성 디렉터리로 이동합니다:
```bash
cd ~/.config/systemd/user
```
`firecrawl.service`라는 새 파일을 만들고 엽니다.
```bash
nano firecrawl.service
```
다음 구성을 복사하여 붙여넣습니다:
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
이 시점에서 서비스는 정의되었지만 아직 `systemd`에 등록되지는 않았습니다. 
위에서 만든 파일 이름과 정확히 일치하는지 확인한 다음, 다음을 실행합니다:
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
성공하면 다음과 같은 출력이 표시됩니다:

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/`에는 자동으로 시작하도록 구성된 서비스에 대한 심볼릭 링크가 포함되어 있습니다.

### 2. 서비스에 맞게 Firecrawl 구성하기

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md)은 스크래핑 및 데이터 처리 환경을 완전히 제어해야 하는 사용자에게 이상적이지만, 유지 관리와 구성에 추가적인 노력이 필요하다는 트레이드오프가 있습니다.

먼저 리포지토리를 클론합니다:
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
루트 `/firecrawl` 디렉터리에 `.env`를 생성합니다:
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
> 신뢰할 수 없는 네트워크에서 접근 가능한 배포 환경이라면 특히, `BULL_AUTH_KEY`를 강력한 비밀 값으로 설정하세요.
### 3. Compose를 통한 Hermes 배포

계속 진행하기 전에 최신 Hermes Docker 이미지를 가져왔는지 확인하세요:
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
완료되면 Hermes Compose 파일 [hermes-compose.yaml](assets/hermes-compose.yaml)을 다운로드하여 루트 `/firecrawl` 디렉터리에 배치하세요:

> 이 규칙은 `systemd`가 `WorkingDirectory=${HOME}/firecrawl`에 지정된 대로 서비스를 찾아 올바르게 시작하기 위해 필요합니다.

> 필요에 따라 추가 Firecrawl 서비스를 추가하여 언제든지 스택을 확장할 수 있습니다. 사용 가능한 전체 서비스 목록은 공식 [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml)에서 확인할 수 있습니다.

### 4. Firecrawl을 통해 Hermes 서비스 실행

`systemd`에 제어권을 넘기기 전에 스택을 수동으로 실행하여 모든 것이 올바르게 작동하는지 확인하세요:
```bash
podman compose -f hermes-compose.yaml up -d
```
모든 것이 올바르게 구성되었다면 Hermes 컨테이너가 실행되는 것을 볼 수 있으며 명령줄 출력은 다음과 유사하게 표시됩니다:
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

확인이 끝나면 계속 진행하기 전에 스택을 다시 종료하세요:
```bash
podman compose -f hermes-compose.yaml down
```
이제 모든 것이 확인되었으므로 `systemd`를 통해 서비스를 시작하세요:
```bash
systemctl --user start firecrawl.service
```
[Hermes API](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints)는 대화형 컨테이너 내에서 접근할 수 있으며, 웹 대시보드는 동일한 호스트와 포트인 http://127.0.0.1:9119 에서 사용할 수 있습니다.
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

서비스를 중지하려면 다음을 실행하세요:
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native

대화형 CLI 세션을 직접 시작합니다: 

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

**축하합니다, 완전한 로컬 AI 에이전트 스택을 구축하셨습니다.**

### 웹 대시보드

Hermes에는 구성, API 키, 모델, 세션, 메모리, cron 작업을 관리하기 위한 브라우저 기반 UI가 포함되어 있습니다. 게이트웨이나 CLI가 실행 중인 동안 두 번째 터미널을 열고 다음으로 실행하세요:

```bash
hermes dashboard
```

이렇게 하면 로컬 서버가 시작되고 브라우저에서 `http://127.0.0.1:9119`가 열립니다. 전체 기능 참조는 [대시보드 문서](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard)를 확인하세요.
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## 선택 사항: 통신 채널 연결

게이트웨이가 실행되면 어떤 기기에서든 로컬 에이전트에 접근할 수 있습니다. Hermes는 [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) 등을 지원합니다

---

### Discord

Discord에서는 봇을 추가하려면 **관리자 권한이 있는** 서버가 필요합니다. 서버를 공유하지만 소유하고 있지 않다면 대신 Telegram을 사용하세요.

#### Discord 애플리케이션 및 봇 생성

1. [Discord Developer Portal](https://discord.com/developers/applications)로 이동하여 **New Application**을 클릭합니다. 이름을 지정합니다(예: "hermes-bot").
2. 사이드바에서 **Bot**을 클릭합니다. 봇의 사용자 이름을 설정합니다.
3. Bot 페이지에서 **Privileged Gateway Intents**로 스크롤하여 다음을 활성화합니다:
   - **Message Content Intent**(필수)
   - **Server Members Intent**(권장)
4. 다시 위로 스크롤하여 **Reset Token**을 클릭해 봇 토큰을 생성합니다. 복사해 두세요.

#### 서버에 봇 추가

1. 사이드바에서 **OAuth2 / URL Generator**를 클릭합니다.
2. **Scopes**에서 `bot`과 `applications.commands`를 활성화합니다.
3. **Bot Permissions**에서 다음을 활성화합니다: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. 생성된 URL을 복사하여 브라우저에 붙여넣고, 서버를 선택한 후 확인합니다.

#### ID 수집 및 DM 허용

Discord에서 개발자 모드를 활성화한 후(**User Settings / Advanced / Developer Mode**):
- 서버 아이콘을 마우스 오른쪽 버튼으로 클릭: **Copy Server ID**
- 자신의 아바타를 마우스 오른쪽 버튼으로 클릭: **Copy User ID**

서버 아이콘을 마우스 오른쪽 버튼으로 클릭 / **Privacy Settings** / **Direct Messages**를 켭니다. 이는 페어링 단계에 필요합니다.

#### Discord용 Hermes 구성

`~/.hermes/.env`에 다음을 추가하세요:

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

그런 다음 게이트웨이를 시작합니다:

```bash
hermes gateway
```

몇 초 안에 Discord에서 봇이 온라인 상태로 표시되어야 합니다. DM이나 봇이 볼 수 있는 채널에서 메시지를 보내세요.

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### Telegram 봇 생성

1. Telegram을 열고 **@BotFather**에게 메시지를 보냅니다.
2. `/newbot`을 전송하고 안내에 따릅니다. 제공되는 봇 토큰을 저장하세요.

#### Telegram용 Hermes 구성

`~/.hermes/.env`에 다음을 추가하세요:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **Telegram 사용자 ID를 모르시나요?** Telegram에서 [@userinfobot](https://t.me/userinfobot)에게 메시지를 보내면 숫자 ID로 응답합니다.

그런 다음 게이트웨이를 시작합니다:

```bash
hermes gateway
```

테스트를 위해 Telegram에서 봇에게 아무 메시지나 보내세요. 이제 Telegram DM을 통해 에이전트와 채팅할 수 있습니다. 웹훅 모드와 고급 옵션은 [전체 Telegram 설정 가이드](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram)를 참조하세요.

---

## 다음 단계

이제 에이전트가 휴대폰에서 명령을 받아 로컬 머신에서 작업을 수행할 수 있게 되었으니, 살펴볼 만한 세 가지 방향을 소개합니다:

1. **자동 리서치 요약**: 매일 아침 관심 있는 주제에 대해 웹을 검색하도록 Hermes를 예약하고, 로컬 모델로 결과를 요약한 후 Telegram이나 Discord를 통해 휴대폰으로 요약본을 전송하도록 설정하세요. 클라우드 비용 없이 모두 자신의 하드웨어에서 실행됩니다.

2. **주문형 코드 리뷰**: Hermes를 GitHub 저장소로 연결하여 열린 풀 리퀘스트를 검토하도록 요청하고, 그 결과에 대한 댓글이나 요약을 다시 채팅으로 게시하도록 하세요. Docker 터미널 백엔드를 사용하면 모든 git 작업이 샌드박스 내에서 실행되어 호스트를 깨끗하게 유지합니다.

3. **로컬 파일 어시스턴트**: Hermes에 작업 디렉터리에 대한 접근 권한을 부여하고, 휴대폰에서 요청에 따라 파일을 정리, 이름 변경, 요약 또는 변환하도록 요청하세요. Docker 터미널 백엔드가 모든 쓰기 작업을 샌드박스 작업 공간으로 제한하므로 실수로 인한 파괴적인 작업이 제한됩니다.