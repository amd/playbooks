<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# Lemonade Server를 백엔드로 사용하여 OpenClaw 실행

## 개요

[**OpenClaw**](https://openclaw.ai/)는 코드를 작성하고 실행하며, 파일을 관리하고, 복잡한 다단계 작업을 대신 처리할 수 있는 자율 AI 에이전트입니다. 단순히 질문에 답하는 채팅 어시스턴트와 달리, OpenClaw는 시스템에서 실제 작업을 수행합니다. 따라서 까다로운 에이전트 루프를 따라갈 수 있는 빠르고 유능한 AI 백엔드가 필요합니다.

[**Lemonade Server**](https://lemonade-server.ai/)가 바로 그 백엔드입니다. 하드웨어에서 직접 GenAI 모델을 실행하고 업계 표준 OpenAI API를 통해 노출하는 오픈 소스 로컬 추론 서버입니다.

두 가지를 함께 사용하면 완전한 로컬 AI 에이전트 스택이 구성됩니다. Lemonade는 모델 추론을 처리하고, OpenClaw는 모델 출력을 실제 작업으로 전환하는 에이전트 루프를 제공합니다.

> **계속하기 전에:** OpenClaw는 고도로 자율적인 AI 에이전트입니다. AI 에이전트에게 시스템 접근 권한을 부여하면 예측할 수 없거나 의도하지 않은 결과가 발생할 수 있습니다. 위험을 이해하고 자율 소프트웨어가 대신 작동하는 것에 동의하는 경우에만 진행하십시오.

---

## 학습 내용

이 플레이북을 마치면 다음을 수행할 수 있습니다:

- **Lemonade Server**에 대해 알아보기
- **OpenClaw를 설치**하고 AI 백엔드로 **Lemonade Server를 지정**하기
- **OpenClaw 게이트웨이를 시작**하고 에이전트가 작동 준비가 되었는지 확인하기
- **통신 채널**(Discord 또는 Telegram)을 **연결**하여 모든 기기에서 에이전트와 채팅하기

---

## 메모리 구성 설정

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 소프트웨어 업데이트 확인

<!-- @require:software-update -->
<!-- @device:end -->

## 소프트웨어 필수 구성 요소 설치

<!-- @os:linux -->
- **Ubuntu 24.04+** 또는 `apt-get`이 있는 호환 Debian 기반 Linux 배포판을 실행하는 PC
- 최소 **12 GB RAM** (대형 모델의 경우 64 GB 이상 권장)
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/) (선택 사항, OpenClaw 샌드박싱용)

- 모델 가중치를 위한 **~10–30 GB의 여유 디스크 공간**
<!-- @os:end -->
<!-- @os:windows -->
- **Windows 10/11**을 실행하는 PC
- 최소 **12 GB RAM** (대형 모델의 경우 64 GB 이상 권장)
- 모델 가중치를 위한 **~10–30 GB의 여유 디스크 공간**
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (선택 사항, OpenClaw 샌드박싱용)
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## 권장 모델 가져오기 및 로드

이 플레이북에서 권장하는 모델은 Unsloth의 **Qwen3.6-35B-A3B-GGUF**로, 263k 토큰 컨텍스트 창을 갖춘 강력한 MoE 모델이며 에이전트 워크로드에 적합합니다. 이 모델은 UD-Q4_K_XL 양자화를 사용합니다. 지금 가져오십시오:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

그런 다음 큰 컨텍스트 창으로 로드하고 향후 실행을 위해 해당 설정을 저장합니다:

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

모델의 기본 컨텍스트 길이는 262,144 토큰입니다. 메모리 부족(OOM) 오류가 발생하면 컨텍스트 창을 줄이는 것을 고려하십시오. 그러나 Qwen3.6은 복잡한 작업에 확장된 컨텍스트를 활용하므로, 사고 기능을 유지하기 위해 최소 128K 토큰의 컨텍스트 길이를 유지하는 것을 권장합니다.

> **팁: 더 빠른 에이전트 응답을 위해 사고 비활성화:** Qwen3.6-35B-A3B는 기본적으로 사고 모드로 실행되며, 각 응답 전에 지연이 추가됩니다. 에이전트 루프에서는 이 오버헤드가 빠르게 누적됩니다. [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) 저장소는 사고를 비활성화하는 즉시 사용 가능한 구성을 제공합니다. 사용하려면 파일을 다운로드하고 가져오십시오:
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

## WSL 설정

OpenClaw를 WSL 내부에서 실행하고(권장) Windows에서 기본적으로 실행되는 Lemonade에 연결합니다. 이렇게 하면 Lemonade의 GPU 가속을 Windows 측에 유지하면서 OpenClaw를 위한 Linux 셸 환경을 제공합니다.

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

WSL2는 가상 네트워크에서 실행됩니다. Windows의 Lemonade는 `127.0.0.1`에 바인딩되며, WSL은 이를 직접 접근할 수 없습니다. Windows 포트 프록시는 WSL 게이트웨이 IP에서 Windows 로컬호스트로 트래픽을 전달합니다.

**WSL 게이트웨이 IP 찾기** (WSL 내부에서 실행):

```bash
ip route show default | awk '{print $3}' | head -1
```

**포트 프록시 추가** (관리자 권한으로 PowerShell에서 실행, `<WSL-Gateway-IP>`를 WSL 게이트웨이 IP로 교체):

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**방화벽 규칙 추가** (동일한 관리자 권한 PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**WSL에서 확인**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

이전 단계에서 Qwen3.6-35B-A3B-GGUF 모델을 이미 로드한 경우 다음과 같은 JSON 출력이 표시됩니다:

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

> `netsh portproxy` 규칙은 재부팅 후에도 유지되지만 WSL 게이트웨이 IP는 `wsl --shutdown` 후 변경될 수 있습니다. 재시작 후 WSL에서 Lemonade에 접근할 수 없게 되면 업데이트된 게이트웨이 IP를 가져와 이 새 IP로 프록시를 업데이트하십시오.

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

## OpenClaw 설치 및 구성

### OpenClaw 설치
<!-- @os:windows -->
> 이 섹션의 명령은 **WSL 터미널** 내부에서 실행하십시오.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

`--no-onboard` 플래그는 대화형 설정 마법사를 건너뜁니다. 다음 단계에서 모델 백엔드를 수동으로 구성하여 사용할 모델과 서버를 정밀하게 제어할 수 있습니다.

새 터미널을 열고 설치를 확인합니다:

```bash
openclaw --version
```

> **팁:** 설치 후 `command not found`가 표시되면 npm의 전역 bin 디렉터리를 PATH에 추가하십시오:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> 이를 영구적으로 적용하려면 위 줄을 `~/.bashrc` 또는 `~/.zshrc` 파일에 추가하십시오.

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


### Lemonade를 사용하도록 OpenClaw 구성

OpenClaw의 비대화형 온보딩을 실행합니다.
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

이 명령은 OpenClaw의 구성을 `~/.openclaw/openclaw.json`에 저장합니다.

> **OpenClaw 컨텍스트 창 크기 조정:** OpenClaw의 압축은 `contextTokens > contextWindow − reserveTokens`일 때 트리거됩니다. 기본 `reserveTokensFloor`는 20,000 토큰으로, 더 낮을 때 `reserveTokens`를 재정의하는 하한값입니다. 따라서 ~37k 미만의 모델 컨텍스트는 무한 압축 루프를 트리거합니다. 구성에서 낮은 예약값을 설정하고 하한값을 한 번 비활성화하면 모든 모델에 적용되며, 모델별 조정이 필요하지 않습니다:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor`는 *하한값*(최소 가드)이며 예약값 자체가 아닙니다. 하한값만 설정하면 효과가 없습니다. `reserveTokensFloor: 0`은 가드를 비활성화하여 더 낮은 `reserveTokens`가 허용됩니다.
>
> **적용 시기:** 모델의 유효 컨텍스트 창이 ~37k 미만인 경우 이 구성을 사용하십시오. 모델이 작거나(예: 8k, 16k, 32k) 의도적으로 더 낮은 값으로 제한한 경우(예: 128k 모델을 로드하지만 Lemonade에서 컨텍스트를 16k로 설정)가 해당됩니다. 이 설정 없이는 OpenClaw가 시작 시 무한 압축 루프에 진입합니다.
>
> **전체 컨텍스트의 대형 컨텍스트 모델:** 이 설정을 완전히 건너뛸 수 있습니다. 기본값이 잘 작동하며, 창이 가득 차기 전에 압축이 시작되고 모델은 긴 응답을 생성할 충분한 공간을 갖습니다. 적용하는 경우 `reserveTokens: 4096`은 응답 길이를 ~4k 토큰으로 제한하여 긴 파일 생성이나 상세한 계획이 잘릴 수 있습니다.
>
> **추가 위치:** `compaction` 블록을 `openclaw.json`의 `agents.defaults` 내부에 배치하십시오(일반적으로 `~/.openclaw/openclaw.json`):
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
> 나머지 구성(게이트웨이, 채널, 모델 등)은 변경되지 않으며, `compaction` 키만 추가하면 됩니다.

### (권장) Docker 샌드박싱 활성화

OpenClaw는 모든 에이전트 파일 및 코드 작업을 호스트에서 직접 실행하는 대신 격리된 Docker 컨테이너를 통해 라우팅할 수 있습니다. 이렇게 하면 의도하지 않은 작업의 영향 범위가 샌드박스로 제한되어 호스트 파일 시스템과 네트워크가 영향을 받지 않습니다.

샌드박스 이미지를 한 번 빌드합니다(Docker가 설치되어 있어야 함):

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

`~/.openclaw/openclaw.json`의 기존 `agents.defaults` 블록 내부에 `sandbox` 키를 추가하려면 다음을 실행합니다:

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

샌드박스 컨테이너는 기본적으로 **네트워크 접근이 없습니다**. 바인드 마운트 및 네트워크 재정의에 대해서는 [샌드박싱 참조](https://docs.openclaw.ai/gateway/sandboxing)를 참조하십시오.

> #### 문제 해결: Docker 권한 거부
> 
> Docker 명령 실행 시 "permission denied"가 발생하는 경우:
> 
> **1단계: 사용자를 docker 그룹에 추가**
> 
> ```bash
> sudo groupadd docker                    # 필요한 경우 그룹 생성
> sudo usermod -aG docker $USER           # 그룹에 자신을 추가
> newgrp docker                           # 변경 사항 활성화
> docker run hello-world                  # 테스트
> ```
> 
> **2단계: 오류가 지속되면 영구적인 수정 적용**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> 그런 다음 시스템을 **재부팅**하십시오.
> 
> **임시 빠른 수정** (재부팅 후 초기화됨):
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

### OpenClaw 게이트웨이 시작

게이트웨이는 에이전트 루프를 관리하고 대시보드를 제공하는 OpenClaw 프로세스입니다:

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

게이트웨이가 실행 중인 상태에서 두 번째 터미널에서 다음을 실행하여 대시보드를 엽니다:

```bash
openclaw dashboard
```

게이트웨이가 루프백에 바인딩되므로, 같은 머신에서 열면 대시보드가 자동으로 인증됩니다. 로컬 접근에는 토큰 입력이나 기기 승인이 필요하지 않습니다. Lemonade 모델이 활성 백엔드로 나열된 OpenClaw 대시보드가 표시됩니다.

> 샌드박싱을 활성화한 경우 대시보드에서 에이전트에게 `run hostname`을 요청하여 확인할 수 있습니다. 머신의 호스트 이름 대신 짧은 컨테이너 ID가 표시되면 샌드박스가 작동 중입니다.

**축하합니다, 완전한 로컬 AI 에이전트 스택을 처음부터 구축했습니다.**

> **게이트웨이 토큰이 필요하신가요?** `openclaw dashboard --no-open`을 실행하면 토큰이 포함된 대시보드 URL이 출력됩니다(클립보드에 복사도 시도됩니다). 또는 토큰은 `~/.openclaw/openclaw.json`의 `gateway.auth.token`에 있습니다.
>
> **원격 기기 승인:** 두 번째 머신이나 휴대폰에서 대시보드를 열면 브라우저에 요청 ID가 표시됩니다. 게이트웨이를 실행 중인 머신으로 돌아가서 다음을 실행합니다:
> ```bash
> openclaw devices approve <requestId>
> ```
> 이는 원격 또는 보조 기기에만 필요하며, 같은 머신의 루프백 접근은 자동으로 인증됩니다.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## 선택 사항: 통신 채널 연결

게이트웨이가 실행되면 모든 기기에서 로컬 에이전트에 접근할 수 있습니다. 설정에 맞는 옵션을 선택하십시오. OpenClaw는 [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram) 및 기타 채널을 지원합니다. 전체 목록은 [docs.openclaw.ai](https://docs.openclaw.ai)에서 확인하십시오.

---

### 옵션 A: Discord

Discord는 봇을 추가하기 위해 **관리자 권한이 있는** 서버가 필요합니다. 서버를 공유하지만 소유하지 않은 경우 옵션 B(Telegram)를 사용하십시오.

#### Discord 계정 및 서버 만들기

Discord 계정이 없으면 [discord.com](https://discord.com)에서 가입하십시오. 또한 관리자인 서버가 필요합니다. Discord 사이드바에서 **+** 아이콘을 클릭하고 **나만의 서버 만들기**를 선택하여 서버를 만드십시오. 비공개 서버도 괜찮습니다.

#### Discord 애플리케이션 및 봇 만들기

1. [Discord 개발자 포털](https://discord.com/developers/applications)로 이동하여 **새 애플리케이션**을 클릭합니다. 이름을 지정합니다(예: "openclaw-bot").
2. 사이드바에서 **봇**을 클릭합니다. 봇의 사용자 이름을 설정합니다.
3. 봇 페이지에서 **Privileged Gateway Intents**로 스크롤하여 다음을 활성화합니다:
   - **Message Content Intent** (필수)
   - **Server Members Intent** (권장)
4. 위로 스크롤하여 **토큰 재설정**을 클릭하여 봇 토큰을 생성합니다. 복사하십시오.

#### 서버에 봇 추가

1. 사이드바에서 **OAuth2/ URL Generator**를 클릭합니다.
2. **Scopes**에서 `bot` 및 `applications.commands`를 활성화합니다.
3. **Bot Permissions**에서 다음을 활성화합니다: 채널 보기, 메시지 보내기, 메시지 기록 읽기, 링크 임베드, 파일 첨부.
4. 생성된 URL을 복사하여 브라우저에 붙여넣고, 서버를 선택한 후 확인합니다. 봇이 서버의 멤버 목록에 표시됩니다.

#### ID 수집

Discord에서 개발자 모드를 활성화합니다(**사용자 설정/ 고급/ 개발자 모드**). 그런 다음:
- 서버 아이콘을 마우스 오른쪽 버튼으로 클릭: **서버 ID 복사**
- 자신의 아바타를 마우스 오른쪽 버튼으로 클릭: **사용자 ID 복사**

#### 서버 멤버로부터 DM 허용

서버 아이콘을 마우스 오른쪽 버튼으로 클릭/ **개인 정보 설정**/ **다이렉트 메시지** 토글 켜기. 이렇게 하면 봇이 DM을 보낼 수 있으며, 페어링 단계에 필요합니다.

#### Discord용 OpenClaw 구성

봇 토큰을 환경 변수로 저장한 다음, Discord를 활성화하고 토큰을 참조하며 서버를 허용 목록에 추가하는 단일 패치 파일을 만듭니다. `<server_id>`와 `<user_id>`를 위에서 수집한 ID로 교체하십시오.

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

> **에이전트에게 이 구성을 요청하지 마십시오.** 샌드박싱이 활성화된 경우 에이전트는 샌드박스 내부에서 `~/.openclaw/openclaw.json`에 쓸 수 없습니다. 대신 호스트에서 위의 CLI 명령을 사용하십시오.

새 채널 구성을 적용하기 위해 게이트웨이를 재시작합니다:

```bash
openclaw gateway run --bind loopback --port 18789
```

몇 초 내에 게이트웨이 출력에 `logged in to discord as <bot-name>`이 표시됩니다.

#### Discord 계정 페어링

Discord에서 봇에게 DM을 보냅니다. 봇이 짧은 페어링 코드로 응답합니다.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

OpenClaw를 실행 중인 머신에서 승인합니다:
```bash
openclaw pairing approve discord <CODE>
```

> 페어링 코드는 한 시간 후에 만료됩니다.

이제 Discord에서 직접 에이전트와 채팅하고 로컬 하드웨어에 작업을 오프로드할 수 있습니다.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### 옵션 B: Telegram

Telegram은 대부분의 사용자에게 Discord보다 간단합니다. 서버나 관리자 권한이 필요하지 않습니다.

#### Telegram 봇 만들기

1. Telegram을 열고 **@BotFather**에게 메시지를 보냅니다.
2. `/newbot`을 보내고 안내에 따릅니다. 제공된 봇 토큰을 저장합니다.

#### Telegram용 OpenClaw 구성

토큰을 환경 변수로 저장합니다:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

`~/.openclaw/openclaw.json`에 채널 구성을 추가합니다(또는 대시보드를 통해 패치):

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

게이트웨이를 재시작한 다음 Telegram에서 봇에게 메시지를 보냅니다. 페어링을 승인합니다:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

페어링 코드는 한 시간 후에 만료됩니다. 이제 Telegram DM을 통해 에이전트와 채팅할 수 있습니다.

---

## 다음 단계

에이전트가 휴대폰에서 명령을 받고 로컬 머신에서 작업을 수행할 수 있게 되었으므로, 다음 세 가지 방향을 탐