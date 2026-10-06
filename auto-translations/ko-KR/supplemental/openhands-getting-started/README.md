<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **기계 번역.** 이 페이지는 영어에서 자동으로 번역되었으며 사람에 의한 검토를 거치지 않았습니다. 이 페이지에는 오류가 포함될 수 있으며, 특정 지침, 명령어, 다운로드, 제품 가용성 또는 기타 콘텐츠가 언어나 지역에 따라 다를 수 있습니다. 본 번역본과 원문 사이에 불일치 또는 차이가 있는 경우, 영어 원문 playbook이 우선하며 이에 따릅니다.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## 개요

[OpenHands](https://github.com/All-Hands-AI/OpenHands)는 코드를 작성하고, 명령을
실행하고, 웹을 탐색하고, 실제 작업 공간에서 파일을 편집할 수 있는 AI 소프트웨어
에이전트입니다. 채팅창에서 제안을 복사해오는 대신, 에이전트를 프로젝트 폴더에
연결하여 작업을 직접 수행하게 할 수 있습니다: 기능 구현, 버그 수정, 테스트
작성, 또는 코드베이스 설명 등입니다.

[Agent Canvas](https://github.com/OpenHands/agent-canvas)는 OpenHands를 실행하기
위해 권장되는 브라우저 UI입니다. 단일 `agent-canvas` 명령으로 에이전트 서버,
자동화 백엔드, 웹 프런트엔드를 함께 시작하므로 브라우저에서 에이전트와 대화를
진행할 수 있습니다.

모든 작업을 AMD 시스템 내에서 유지하기 위해, 에이전트는 Lemonade Server가
제공하는 로컬 모델과 통신합니다. Lemonade는 해당 모델을 OpenAI 호환 API로
노출하므로, Agent Canvas는 다른 OpenAI 방식 엔드포인트와 마찬가지로 이를 구성할
수 있으며, 모델, 코드, 대화 컨텍스트는 모두 사용자의 기기에 남아 있습니다.

이 플레이북에서는 로컬 모델을 시작하고, Agent Canvas를 실행하고, 해당 모델을
가리키도록 설정한 다음, 실제 프로젝트 폴더를 대상으로 첫 번째 코딩 작업을
실행해 봅니다.

## 배우게 될 내용

- Lemonade Server를 시작하고 로컬 모델이 채팅 요청에 응답하는지 확인하는 방법
- npm 패키지로 Agent Canvas를 설치하고 실행하는 방법
- 로컬 Lemonade 모델을 LLM으로 사용하도록 Agent Canvas를 구성하는 방법
- OpenHands 대화를 시작하고 에이전트가 작업 공간에서 파일을 편집하고 명령을
  실행하는 과정을 지켜보는 방법
- 에이전트가 변경한 내용을 검토하고 후속 메시지로 방향을 조정하는 방법

## 핵심 개념

| 개념 | 설명 | 이 플레이북에서의 역할 |
| --- | --- | --- |
| Lemonade Server | AMD 하드웨어를 위해 만들어진 로컬 LLM 서빙 플랫폼으로, OpenAI 호환 API를 노출합니다. 데이터는 절대 사용자의 기기를 벗어나지 않습니다. | 에이전트를 구동하는 모델을 실행합니다. |
| OpenHands | 작업 공간 내에서 파일을 읽고 편집하며, 셸 명령을 실행하고, 웹을 탐색하는 AI 소프트웨어 에이전트입니다. | 채팅에서 직접 조작하는 에이전트입니다. |
| Agent Canvas | OpenHands 대화를 실행하고 도구 호출 및 파일 변경 사항을 표시하는 브라우저 UI 및 백엔드입니다. | 스택을 실행하고 대화를 호스팅합니다. |
| 작업 공간 | 에이전트가 읽고 수정할 수 있도록 허용된 프로젝트 폴더입니다. | 에이전트의 편집 및 명령의 대상입니다. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> 코딩 에이전트 워크플로는 더 큰 모델과 컨텍스트 창을 사용할 때 더 나은 성능을
> 보입니다. 최소 32GB의 시스템 메모리를 사용하고, 더 큰 GGUF 모델을 사용하려면
> 64GB 이상을 권장합니다.
<!-- @device:end -->

## 메모리 구성 설정

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 소프트웨어 업데이트 확인

<!-- @require:software-update -->
<!-- @device:end -->

## 사전 준비 사항


<!-- @os:linux -->
<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here.
     lemonade-chat-windows asserts the model is already downloaded. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

다음이 필요합니다:

- 아래 모델을 서빙할 수 있도록 설치된 Lemonade Server.

<!-- @os:linux -->
- Node.js 22.12 이상 및 `npm`(`agent-canvas` CLI에서 사용).
- Agent Canvas가 에이전트 서버 환경을 관리하는 데 사용하는 Python 패키지
  관리자인 `uv`. 시스템에 아직 설치되어 있지 않다면 Agent Canvas를 실행하기 전에
  [uv 설치 가이드](https://docs.astral.sh/uv/getting-started/installation/)에서
  설치하세요.
<!-- @os:end -->

<!-- @os:windows -->
- 설치되어 실행 중인
  [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/).
  Windows에서는 Agent Canvas 스택이 게시된 Docker 이미지에서 실행되며, 이
  이미지에는 Node.js, `uv`, `@openhands/agent-canvas` 패키지가 번들로 포함되어
  있으므로 호스트에 해당 항목들을 따로 설치할 필요가 없습니다.
<!-- @os:end -->

- 작업할 프로젝트 폴더. 에이전트가 작업하기를 원하는 로컬 git 저장소 또는 코드
  디렉터리라면 무엇이든 가능합니다.

<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @os:linux -->
<!-- @test:id=prereq-clis-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

lemonade --version
node -v
npm -v

# uv is a required prerequisite (agent-canvas uses it to build its Python env).
# Install it only if the runner doesn't already have it.
# TODO: remove this self-provisioning once the runners ship uv by default.
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"
uv --version

echo "OK: lemonade, node, npm, and uv are all available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=prereq-clis-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# On Windows the Agent Canvas stack runs from the published Docker image, so the
# only host prerequisites are Lemonade and a running Docker engine. Node.js, uv,
# and agent-canvas are bundled inside the container.
lemonade --version
docker version --format "{{.Server.Version}}"

Write-Host "OK: lemonade and docker are available"
```
<!-- @test:end -->
<!-- @os:end -->

## 1. Lemonade Server 시작하기

Lemonade CLI에서 모델을 시작합니다:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **하드웨어에 맞는 모델을 선택하세요.** `Qwen3.6-35B-A3B-GGUF`(~20GB)는 강력한
> 코딩 모델이지만 큰 메모리 풀이 필요합니다. 기기의 메모리나 GPU VRAM이
> 제한적이라면, 대신 Lemonade 모델 라이브러리에서 더 작은 GGUF 모델을 선택하고
> 이 플레이북 전체에서 해당 모델 ID를 사용하세요.

> **참고:** 처음 `lemonade run`을 실행하면 모델이 아직 없는 경우 다운로드하며,
> 모델 크기와 네트워크 환경에 따라 시간이 걸릴 수 있습니다.

Lemonade는 다음 주소에서 OpenAI 호환 API를 노출합니다:

```text
http://127.0.0.1:13305/api/v1
```

## 2. 로컬 모델 확인하기

Lemonade가 선택한 모델을 서빙할 수 있는지 확인합니다:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

그런 다음 작은 채팅 요청을 보냅니다:

```bash
curl -sS "http://127.0.0.1:13305/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.6-35B-A3B-GGUF",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

`choices` 배열이 반환되면 Lemonade가 Agent Canvas를 사용할 준비가 된
것입니다.

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
model_id = "${lemonade_model}"

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
PY

body='{
  "model": "${lemonade_model}",
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
$entry = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

$body = @{
  model = "${lemonade_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openhands-lemonade-chat-body.json"
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
## 3. Agent Canvas 설치 및 실행

<!-- @os:linux -->
게시된 Agent Canvas 패키지를 전역으로 설치합니다:

```bash
npm install -g @openhands/agent-canvas
```

<!-- @test:id=agent-canvas-version-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# agent-canvas is expected to be provisioned on the runner. Fail loudly if it
# isn't, rather than installing it here.
if ! command -v agent-canvas >/dev/null 2>&1; then
  echo "agent-canvas is not on PATH; the runner must provision it before CI runs"
  exit 1
fi

# Prefer --version; fall back to --help if this build has no --version flag.
agent-canvas --version || agent-canvas --help

echo "OK: agent-canvas CLI is on PATH"
```
<!-- @test:end -->

그런 다음 터미널에서 전체 스택을 시작합니다:

```bash
agent-canvas
```

기본적으로 Agent Canvas는 `http://localhost:8000`에서 시작됩니다. 해당 URL을
브라우저에서 엽니다. 이 포트는 특별한 의미가 없으며, 8000번이 이미 사용 중이라면
Agent Canvas를 실행할 때 `--port`(또는 `-p`)로 사용 가능한 포트를 지정하면 됩니다:

```bash
agent-canvas --port 3000
```

그런 다음 `http://localhost:3000`을 대신 엽니다. 기본 로컬 백엔드는 홈 화면에서
정상(healthy) 상태로 표시되어야 합니다.

`agent-canvas` 명령은 에이전트 서버, 자동화 백엔드, 웹 프런트엔드를 함께
시작합니다. OpenHands를 로컬에서 실행하려면 이 명령 하나만 있으면 됩니다.

<!-- @test:id=agent-canvas-server-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

log="/tmp/agent-canvas-ci.log"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

# First launch builds the agent server's uv-managed Python env, so allow a generous startup window.
agent-canvas >"$log" 2>&1 &
p=$!

# Probe the agent-server backend health (18000/server_info), NOT just the 8000
# ingress root: the ingress serves the static frontend and returns 200 for /
# even when the agent-server is down.
ok=false
for i in $(seq 1 300); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18000/server_info || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  if ! kill -0 "$p" 2>/dev/null; then
    echo "agent-canvas process exited before it finished starting"
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "agent-server not ready on http://127.0.0.1:18000/server_info"
  echo "---- agent-canvas log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: agent-canvas agent-server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
Windows에서는 Docker Desktop으로 게시된 Agent Canvas 컨테이너 이미지를
실행합니다. 이 이미지에는 Agent Server, 자동화 백엔드, 웹 프런트엔드가 모두
포함되어 있으므로 호스트에 Node.js, `uv`, CLI를 설치할 필요가 없습니다.

먼저 컨테이너가 마운트할 설정 폴더와 작업 공간 폴더를 생성합니다:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

게시된 이미지를 가져옵니다(공개 이미지이므로 로그인이 필요하지 않습니다):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

그런 다음 스택을 시작합니다:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

브라우저에서 `http://localhost:8000/canvas`를 엽니다. 8000번 포트가 이미 사용
중이라면 다른 호스트 포트를 매핑합니다(예: `-p 8080:8000`). 이 경우
`http://localhost:8080/canvas`를 대신 엽니다.

> **참고:** 최초 실행 시에는 컨테이너 내부에서 Agent Server를 초기화하므로
> 백엔드가 정상(healthy) 상태로 표시되기까지 1~2분 정도 걸릴 수 있습니다.

`.openhands` 마운트는 컨테이너를 다시 시작해도 LLM 프로필과 설정을 유지합니다.
이 플레이북의 나머지 부분에서는 브라우저의 Agent Canvas UI를 통해 모든 것을
설정합니다.

<!-- @test:id=agent-canvas-docker-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$image    = "ghcr.io/openhands/agent-canvas:1.14.0"
$name     = "openhands-agent-canvas-ci"
$hostPort = 18080

# The image is expected to be provisioned on the runner. Fail loudly if it
# isn't, rather than pulling it here.
$imgId = docker images -q $image
if (-not $imgId) {
  throw "Image $image is not present; the runner must provision it before CI runs"
}
Write-Host "OK: $image is present"

if (docker ps -aq -f "name=$name") { docker rm -f $name | Out-Null }

try {
  docker run -d --name $name -p "${hostPort}:8000" $image | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "docker run failed for $image" }

  # Probe the agent-server backend health through the container proxy
  # (/server_info -> agent-server on 18000 inside the container), not just the
  # /canvas static UI, which can return 200 while the backend is still down.
  $ok = $false
  for ($i = 0; $i -lt 300; $i++) {
    $canvas = try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:${hostPort}/canvas").StatusCode } catch { 0 }
    $info   = try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://localhost:${hostPort}/server_info").StatusCode } catch { 0 }
    if ($canvas -eq 200 -and $info -eq 200) { $ok = $true; break }
    $state = docker inspect -f "{{.State.Status}}" $name 2>$null
    if ($state -ne "running") { throw "Container $name exited before it finished starting" }
    Start-Sleep -Seconds 2
  }

  if (-not $ok) {
    docker logs --tail 40 $name
    throw "agent-canvas backend not healthy on http://localhost:${hostPort}/server_info"
  }
  Write-Host "OK: agent-canvas Docker stack is healthy (/canvas and /server_info return 200)"
}
finally {
  if (docker ps -aq -f "name=$name") { docker rm -f $name | Out-Null }
}
```
<!-- @test:end -->
<!-- @os:end -->

## 4. 로컬 LLM 구성

최초 실행 시 Agent Canvas는 온보딩 흐름을 엽니다. 이 흐름에서:

1. 에이전트로 **OpenHands**가 선택된 상태를 유지하고 **Next**를 클릭합니다.
2. **Set up your LLM**에서 **Advanced**를 선택합니다.
3. **Authentication**을 **API key**로 유지합니다.
4. **Custom Model**을 `openai/Qwen3.6-35B-A3B-GGUF`로 설정합니다.
5. **Base URL**을 `http://127.0.0.1:13305/api/v1`로 설정합니다.
   <!-- @os:windows -->
   > Windows에서는 스택이 컨테이너 내에서 실행되므로 호스트의 `127.0.0.1`에
   > 접근할 수 없습니다. 컨테이너화된 에이전트가 Windows 호스트에서 실행 중인
   > Lemonade에 접근할 수 있도록 대신 `http://host.docker.internal:13305/api/v1`을
   > 사용하십시오.
   <!-- @os:end -->
6. **API Key**에는 `lemonade-local`과 같이 비어 있지 않은 임의의 플레이스홀더
   값을 입력합니다. Lemonade는 실제 키를 필요로 하지 않지만, OpenHands
   클라이언트는 전송할 값이 필요합니다.
7. **Next**를 클릭합니다.

완료된 Advanced 설정은 다음과 같아야 합니다. API key 필드는 UI에서
마스킹 처리됩니다.

![Lemonade 모델과 로컬 base URL이 적용된 Agent Canvas 최초 사용 시 LLM Advanced 설정](assets/01-llm-advanced-settings.png)

Agent Canvas는 이 값들을 LLM 프로필로 저장합니다. 사용 중인 버전에서 프로필
이름을 묻는 경우 `lemonade-local`처럼 공백이 없는 이름을 사용하십시오. 나중에
모델을 변경하려면 **Settings > LLM**을 열고 동일한 Advanced 필드를
업데이트하십시오. 채팅 입력란에서 `/model` 명령으로 저장된 프로필을 전환할 수
있습니다.

## 5. 작업 공간 열기

에이전트는 사용자가 지정한 작업 공간 내의 파일만 읽고 수정할 수 있습니다.
작업을 시작하기 전에 Agent Canvas가 프로젝트 폴더를 가리키도록 설정하십시오:

1. 홈 화면에서 **Open Workspace**를 선택합니다.
2. 프로젝트가 포함된 폴더를 선택합니다(예: 에이전트가 작업할 git 저장소).
3. 해당 작업 공간에서 새 대화를 시작합니다.

파일 읽기, 명령 실행, 코드 편집 등 에이전트가 수행하는 모든 작업은 해당
작업 공간으로 범위가 제한됩니다.

![온보딩 이후의 Agent Canvas 홈 화면](assets/02-agent-canvas-home.png)

## 6. 첫 번째 코딩 작업 실행

작업 공간을 열고 로컬 LLM을 선택한 상태에서, 채팅에 구체적인 작업을
입력합니다. 작고 검증 가능한 작업이 좋은 첫 작업입니다. 예를 들면:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

대화 타임라인을 지켜보십시오. OpenHands는 다음을 수행합니다:

- 레이아웃을 파악하기 위해 작업 공간을 읽습니다.
- 요청된 함수와 테스트 블록이 포함된 `hello.py`를 생성합니다.
- 필요한 경우 `python3 hello.py`를 실행하여 출력을 확인합니다.
- 수행한 작업과 모든 명령 출력을 채팅에 보고합니다.

작업 공간에 새 파일이 나타나는 것을 확인할 수 있으며, 에이전트의 최종
메시지는 수행한 변경 사항을 설명해야 합니다. 이것이 핵심 성과 순간입니다.
즉, 에이전트가 여러분의 프로젝트 폴더에서 실제 코드를 작성하고 실행한
것입니다.

## 7. 에이전트 검토 및 조정

에이전트가 한 단계를 완료한 후에는 다음 단계를 수락하기 전에 작업 내용을
검토하십시오:

- **파일 변경 사항**: 작업 공간 파일 브라우저 또는 에이전트의 diff 보기를
  사용하여 정확히 무엇이 추가, 변경, 삭제되었는지 확인합니다.
- **명령 출력**: 에이전트가 실행한 명령을 펼쳐서 stdout, stderr, 종료
  코드(exit code)를 확인합니다.
- **후속 조치**: 결과가 원하는 바와 다르다면, 동일한 대화에서 수정 사항을
  답장으로 입력합니다. 에이전트는 이전 컨텍스트를 유지하면서 동일한 파일을
  대상으로 반복 작업합니다.

예를 들어, 테스트가 예상한 인사말을 출력하지 않았다면 다음과 같이
답장합니다:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

에이전트는 파일을 다시 읽고, 명령을 실행하고, 문제를 진단한 다음, 동일한
대화 내에서 파일을 다시 편집합니다.
## 문제 해결

<!-- @os:linux -->
- **`agent-canvas`가 PATH에 없는 경우:** `npm install -g @openhands/agent-canvas`로 다시 설치하고, 새 터미널에서 `agent-canvas`를 실행할 수 있도록 npm 전역 바이너리 디렉터리가 PATH에 포함되어 있는지 확인하세요.
- **`npm install -g`가 권한 오류로 실패하는 경우:** 사용자 소유의 전역 npm 디렉터리를 구성한 다음 터미널을 다시 열고 Agent Canvas를 다시 설치하세요.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv`가 없는 경우:** [uv 설치 가이드](https://docs.astral.sh/uv/getting-started/installation/)에서 설치하세요. Agent Canvas는 `uv`를 사용하여 에이전트 서버의 Python 환경을 관리합니다.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` 또는 `docker run`이 연결에 실패하는 경우:** Docker Desktop이 실행 중인지(시스템 트레이에 고래 아이콘이 표시됨), 엔진이 시작을 완료했는지 확인하세요. `docker version`을 실행하면 Client와 Server 섹션이 모두 출력되어야 합니다.
- **컨테이너는 시작되지만 백엔드가 정상 상태가 되지 않는 경우:** 첫 실행 시 컨테이너 내부에서 Agent Server를 초기화합니다. 1~2분 정도 기다린 후 `docker logs <container>`로 오류를 확인하세요.
- **컨테이너가 Lemonade에 연결할 수 없는 경우:** 컨테이너는 `host.docker.internal`을 통해 호스트에 접근합니다. `lemonade status`로 Lemonade가 Windows 호스트에서 서비스를 제공하고 있는지 확인하고, LLM을 구성할 때 기본 URL로 `http://host.docker.internal:13305/api/v1`을 사용하세요.
<!-- @os:end -->

- **UI는 로드되지만 백엔드가 비정상 상태로 표시되는 경우:** 에이전트 서버가 시작을 완료할 때까지 1~2분 정도 기다린 후 새로 고침하세요. 계속 비정상 상태라면 스택을 다시 시작하고 로그에서 오류를 확인하세요.
- **Lemonade 채팅 요청이 연결 오류로 실패하는 경우:** `curl -fsS "http://127.0.0.1:13305/api/v1/health"`가 성공하는지, `lemonade status`로 Lemonade가 여전히 모델을 서비스 중인지 확인하세요.
- **에이전트가 컨텍스트 길이 또는 토큰 한도 메시지와 함께 오류를 내는 경우:** 에이전트가 지나치게 큰 기록을 유지하지 않도록 새 대화를 시작하세요. 계속 발생한다면 메모리가 허용하는 한도 내에서 기본값인 65536보다 큰 `ctx_size`(예: `ctx_size=131072`)로 Lemonade를 다시 시작하세요.
- **에이전트가 품질이 낮거나 불완전한 편집을 생성하는 경우:** Lemonade에서 더 큰 모델로 전환하거나, 에이전트에게 더 작고 구체적인 작업을 주어 다음 변경을 요청하기 전에 완료하도록 하세요.

## 다음 단계

- 단위 테스트 파일 추가나 알려진 버그 수정 같은 더 큰 작업을 동일한 작업 공간에서 시도해 보고, 변경 사항을 유지하기 전에 에이전트의 diff를 검토하세요.
- 에이전트가 작업 중 이슈를 읽거나 업데이트를 게시할 수 있도록 **Customize**에서 GitHub나 Slack 같은 MCP 서버를 연결하세요.
- 빠른 소형 모델과 더 강력한 대형 모델 등 여러 LLM 프로필을 저장해 두고, 대화 도중 `/model`로 전환하며 사용해 보세요.
- 반복되는 개발 루프를 예약 실행 또는 이벤트 트리거 기반 에이전트 실행으로 전환하려면 [OpenHands automations](https://docs.openhands.dev/openhands/usage/automations/overview)로 넘어가세요.

## 리소스

- [OpenHands 문서](https://docs.openhands.dev/)
- [Agent Canvas 개요](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Agent Canvas 설정](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM 프로필 및 모델 구성](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Lemonade Server 문서](https://lemonade-server.ai/docs)

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