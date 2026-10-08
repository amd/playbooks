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
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## 개요

개발자는 레이블이 지정된 풀 리퀘스트 검토, GitHub 댓글 응답, 새 이슈 분류, Slack 스레드를 스탠드업 노트나 인시던트 후속 조치로 전환하는 작업, 릴리스 또는 연구 신호 추적 등 작지만 반복적인 루프에 많은 시간을 소비합니다.
각 루프는 익숙하지만 여전히 판단이 필요합니다. 즉, 적절한 컨텍스트를 수집하고, 무엇이 중요한지 결정하며, 팀이 이미 작업하고 있는 곳에 명확한 업데이트를 게시해야 합니다.

[OpenHands 자동화](https://docs.openhands.dev/openhands/usage/automations/overview)는 이러한 루프를 예약되거나 이벤트로 트리거되는 에이전트 대화, 즉 AI 소프트웨어 에이전트가 컨텍스트를 읽고, 도구를 호출하고, 업데이트를 생성하는 실행으로 전환합니다.
OpenHands 확장 카탈로그에 있는 공유 자동화 템플릿은 GitHub 풀 리퀘스트 검토, 리포지토리 모니터링, Linear 이슈 분류, 인시던트 회고, Slack 스탠드업 다이제스트, 연구 브리핑에 대해 이 패턴을 따릅니다. 자동화가 깨어나서, GitHub 또는 Slack과 같이 구성된 통합을 사용해 컨텍스트를 가져오고, 대규모 언어 모델(LLM)로 해당 컨텍스트에 대해 추론한 뒤, 결과를 다시 작성합니다.

[Agent Canvas](https://github.com/OpenHands/agent-canvas)는 이러한 자동화를 빌드하고 테스트하기 위한 로컬 제어 플레인입니다.
이 플레이북에서는 에이전트 대화를 실행하는 백엔드 프로세스인 OpenHands Agent Server를 실행하고, 에이전트를 GitHub 및 Slack과 같은 외부 서비스에 연결합니다.

워크플로를 AMD 시스템에 유지하기 위해 에이전트는 Lemonade Server가 제공하는 로컬 모델과 통신합니다.
Lemonade는 OpenAI 호환 API를 통해 해당 모델을 노출하므로, Agent Canvas는 모델, 프롬프트, 워크플로 컨텍스트를 로컬에 유지하면서 원격 OpenAI 스타일 엔드포인트처럼 이를 구성할 수 있습니다.

이 플레이북에서는 예약된 GitHub-to-Slack 개발 다이제스트라는 하나의 구체적인 자동화를 빌드합니다.
이는 GitHub를 사용해 최근 리포지토리 활동을 검사하고, Slack을 사용해 다이제스트를 게시하며, Agent Canvas API 호출로 자동화를 구성하고 테스트하고, Lemonade로 LLM을 로컬에서 실행합니다.

![GitHub MCP, OpenHands 자동화, Lemonade Server, Slack MCP를 보여주는 아키텍처 다이어그램](assets/00-architecture-overview.png)

## 배우게 될 내용

- Lemonade Server를 시작하고 로컬 모델이 채팅 요청에 응답하는지 확인하는 방법
- Agent Canvas를 실행하고 해당 Agent Server가 로컬 LLM을 가리키도록 설정하는 방법
- Agent Server API를 통해 GitHub 및 Slack 모델 컨텍스트 프로토콜(MCP) 서버를 설치하는 방법
- 개발 다이제스트를 Slack에 게시하는 예약된 OpenHands 자동화를 생성하고 디스패치하는 방법
- 가장 흔한 로컬 모델 및 자동화 오류를 해결하는 방법

## 핵심 개념

| 개념 | 설명 | 이 플레이북에서의 역할 |
| --- | --- | --- |
| Lemonade Server | OpenAI 호환 API를 노출하는, AMD 하드웨어를 위해 구축된 로컬 LLM 서빙 플랫폼입니다. 데이터가 머신을 벗어나지 않습니다. | 에이전트를 구동하는 모델을 실행합니다. |
| OpenHands Agent Server | OpenHands 에이전트 대화를 실행하는 백엔드 프로세스입니다. | 에이전트, 해당 LLM 프로필, MCP 서버를 호스팅합니다. |
| Agent Canvas | Agent Server와 에이전트 실행을 검사하기 위한 UI를 실행하는, OpenHands를 위한 로컬 제어 플레인입니다. | 백엔드를 실행하고 호출할 API를 제공합니다. |
| MCP 서버 | 에이전트에 GitHub나 Slack과 같은 외부 서비스용 도구를 제공하는 모델 컨텍스트 프로토콜 서버입니다. | 에이전트가 GitHub를 읽고 Slack에 쓸 수 있게 합니다. |
| OpenHands 자동화 | 컨텍스트를 가져오고, 추론하고, 어딘가에 결과를 작성하는 예약되거나 이벤트로 트리거되는 에이전트 대화입니다. | 여기서 빌드하는 GitHub-to-Slack 다이제스트입니다. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> 코딩 에이전트 워크플로는 더 큰 모델과 컨텍스트 윈도우를 사용할 때 이점을 얻습니다.
> 최소 32GB의 시스템 메모리를 사용하고, 더 큰 GGUF 모델의 경우 64GB 이상을 권장합니다.
<!-- @device:end -->

## 메모리 구성 설정

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 소프트웨어 업데이트 확인

<!-- @require:software-update -->
<!-- @device:end -->

## 사전 요구 사항

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

다음이 필요합니다:

- 표준 [Lemonade 설치 가이드](https://lemonade-server.ai/docs/guide/install/)를 따라 설치된 Lemonade Server.

<!-- @os:linux -->
- 공개된 Agent Canvas CLI를 설치하고 `npx`로 MCP 서버를 실행하는 데 사용되는 Node.js 22.12 이상 및 `npm`.
- Agent Canvas가 Agent Server 환경을 빌드하는 데 사용하는 Python 패키지 관리자인 `uv`. 아직 설치되어 있지 않다면 [uv 설치 가이드](https://docs.astral.sh/uv/getting-started/installation/)에서 설치하세요.
- 스키마 기반 에이전트 설정, `LLMSummarizingCondenserSettings.max_tokens`, LLM `custom_tokenizer` 지원이 포함된 최신 공개 `@openhands/agent-canvas` 패키지.
- Agent Server 환경에서 사용 가능한 Python `transformers` 패키지. `custom_tokenizer`가 설정된 경우 채팅 템플릿 토큰 수 계산에 필요합니다.
<!-- @os:end -->

<!-- @os:windows -->
- 설치되어 실행 중인 [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/). Windows에서는 Agent Canvas 스택이 공개된 Docker 이미지에서 실행되며, 여기에는 Node.js, `uv`, `transformers`, `@openhands/agent-canvas` 패키지가 번들로 포함되어 있으므로 호스트에 이러한 것들을 설치할 필요가 없습니다.
<!-- @os:end -->

- 요약할 리포지토리에 대한 읽기 액세스 권한이 있는 GitHub 토큰.
- `chat:write` 및 채널 읽기 액세스 권한이 있는 Slack 봇 토큰(`xoxb-...`).
- Slack 팀 ID(`T...`).
- 다이제스트가 게시될 Slack 채널 ID(`C...`).

자동화를 테스트하기 전에 대상 채널에 Slack 앱을 초대하세요.
## 이 플레이북에서 사용하는 변수

<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @os:linux -->
```bash
export LEMONADE_BASE_URL="http://127.0.0.1:13305/api/v1"
export LEMONADE_MODEL="Qwen3.6-35B-A3B-GGUF"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
$env:LEMONADE_BASE_URL = "http://127.0.0.1:13305/api/v1"
$env:LEMONADE_MODEL = "Qwen3.6-35B-A3B-GGUF"
```
<!-- @os:end -->

이 두 변수는 아래의 확인 명령에 사용됩니다.
모델, 토크나이저 및 기타 LLM 설정은 이후 단계에서 Agent Canvas UI에 직접 입력하므로, 필요한 곳에서 실제 값을 그대로 보여줍니다.

다음 값은 이후 단계에서 Agent Canvas UI에 입력됩니다.
복사해서 사용할 수 있도록 여기에 설정해 둡니다:

<!-- @os:linux -->
```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
$env:GITHUB_REPO_FILTER = "your-org/your-repo"
$env:SLACK_DIGEST_CHANNEL = "C0123456789"
$env:DIGEST_TIMEZONE = "America/New_York"
```
<!-- @os:end -->

`GITHUB_REPO_FILTER`에는 명시적인 `owner/repo` 값을 사용하세요.
범위가 넓은 조직 와일드카드를 사용하면 로컬 모델에 과도한 MCP 컨텍스트가 반환될 수 있습니다.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Lemonade Server 시작

Lemonade CLI에서 모델을 시작합니다:

<!-- @os:linux -->
```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "$env:LEMONADE_MODEL"
```
<!-- @os:end -->

> **하드웨어에 맞는 모델을 선택하세요.** `Qwen3.6-35B-A3B-GGUF`(약 20GB)는 이 워크플로에 적합한 강력한 모델이지만 큰 메모리 풀이 필요합니다.
> 장치의 메모리나 GPU VRAM이 제한적이라면 Lemonade 모델 라이브러리에서 더 작은 GGUF 모델을 선택하고, 이 플레이북 전체에서 해당 모델 ID(및 일치하는 토크나이저)를 사용하세요.

> **참고:** 최초 `lemonade run` 실행 시 모델이 아직 없으면 다운로드하므로, 모델 크기와 연결 상태에 따라 시간이 걸릴 수 있습니다.

Lemonade는 다음 위치에서 OpenAI 호환 API를 제공합니다:

```text
http://127.0.0.1:13305/api/v1
```

선택 사항: Agent Canvas 또는 자동화 러너가 동일한 머신에 있지 않은 경우, 보안 터널을 통해 Lemonade 엔드포인트를 게시하고 HTTPS URL을 LLM 기본 URL로 사용하세요.
[ngrok](https://ngrok.com/)은 보안 HTTPS URL을 통해 로컬 포트를 인터넷에 노출합니다. 무료 ngrok 계정이 필요하며, `YOUR_NGROK_DOMAIN.ngrok-free.dev`를 자신이 예약한 도메인으로 바꾸세요:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. 로컬 모델 확인

Lemonade가 선택한 모델을 서비스할 수 있는지 확인합니다:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

그런 다음 간단한 채팅 요청을 보냅니다:

```bash
curl -sS "${LEMONADE_BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"${LEMONADE_MODEL}"'",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
curl.exe -s "$env:LEMONADE_BASE_URL/models"
```

그런 다음 간단한 채팅 요청을 보냅니다:

```powershell
$body = @{
  model    = "$env:LEMONADE_MODEL"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens  = 64
} | ConvertTo-Json -Depth 5
curl.exe -sS "$env:LEMONADE_BASE_URL/chat/completions" -H "Content-Type: application/json" -d $body
```
<!-- @os:end -->

`choices` 배열이 반환되면 Lemonade가 Agent Canvas에서 사용할 준비가 된 것입니다.

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
entry = None
for item in data.get("data", []):
    if item.get("id") == "${lemonade_model}":
        entry = item
        break

if entry is None:
    print("Model ${lemonade_model} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: ${lemonade_model} model is downloaded in Lemonade")
PY

body='{
  "model": "${lemonade_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 64
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi
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

if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1

if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

$body = @{
  model    = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens  = 64
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "digest-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->
<!-- @os:end -->

## 3. Agent Canvas 시작

<!-- @os:linux -->
게시된 Agent Canvas 패키지를 설치하고 전체 스택을 시작합니다:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

전역 npm 설치가 권한 오류로 실패하는 경우, 아래의 npm 권한 문제 해결 항목을 참고하세요.

기본적으로 Agent Canvas는 `http://localhost:8000`에서 시작됩니다.
브라우저에서 해당 URL을 여세요.
이 포트는 특별한 의미가 없으며, 8000번이 이미 사용 중이면 `--port`(또는 `-p`)로 사용 가능한 다른 포트를 지정할 수 있습니다.
기본 로컬 백엔드는 홈 화면에서 정상(healthy) 상태로 표시되어야 합니다.

> **참고:** 최초 실행 시 Agent Server의 `uv` 기반 Python 환경을 빌드하므로, 백엔드가 정상 상태로 보고되기까지 몇 분 정도 걸릴 수 있습니다.

`agent-canvas` 명령은 에이전트 서버, 자동화 백엔드, 웹 프런트엔드를 함께 시작합니다.
OpenHands를 로컬에서 실행하려면 이 명령 하나만 있으면 됩니다.
이 플레이북의 나머지 부분은 브라우저의 Agent Canvas UI를 통해 모든 것을 구성합니다.
<!-- @os:end -->

<!-- @os:windows -->
Windows에서는 Docker Desktop으로 게시된 Agent Canvas 컨테이너 이미지를 실행합니다.
이 이미지에는 Agent Server, 자동화 백엔드, 웹 프런트엔드가 번들로 포함되어 있으므로, 호스트에 Node.js, `uv`, CLI를 설치할 필요가 없습니다.

먼저 컨테이너가 마운트할 config 및 workspace 폴더를 생성합니다:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

게시된 이미지를 가져옵니다(약 6GB이며, 공개 이미지이므로 로그인이 필요하지 않습니다):

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

브라우저에서 `http://localhost:8000/canvas`를 엽니다.
8000번 포트가 이미 사용 중이면 다른 호스트 포트를 매핑하세요. 예를 들어 `-p 8080:8000`을 사용하고 대신 `http://localhost:8080/canvas`를 엽니다.

> **참고:** 최초 실행 시 컨테이너 내부에 Agent Server 환경을 빌드하므로, 백엔드가 정상 상태로 보고되기까지 몇 분 정도 걸릴 수 있습니다.

`.openhands` 마운트는 컨테이너 재시작 간에도 LLM 프로필, MCP 서버, 자동화 설정을 유지합니다.
이 플레이북의 나머지 부분은 브라우저의 `http://localhost:8000/canvas`에 있는 Agent Canvas UI를 통해 모든 것을 구성합니다.
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=uv-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->

<!-- @test:id=agent-canvas-version timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
# Prefer --version; fall back to --help if this build has no --version flag.
agent-canvas --version || agent-canvas --help
echo "OK: agent-canvas CLI is on PATH"
```
<!-- @test:end -->

<!-- @test:id=agent-canvas-start timeout=1200 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
log="/tmp/agent-canvas-test.log"
p=""
cleanup() {
  set +e
  for port in 8000 18000 18001 3001; do
    pid="$(ss -ltnp 2>/dev/null | grep ":$port " | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2)"
    [ -n "$pid" ] && kill "$pid" 2>/dev/null
  done
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null
    sleep 2
    kill -9 "$p" 2>/dev/null
  fi
}
# Preserve the real exit code; cleanup must never flip a pass to a fail (or vice versa).
trap 'rc=$?; cleanup; exit $rc' EXIT

# First launch builds the agent server's uv-managed Python env, so allow a generous startup window.
agent-canvas >"$log" 2>&1 &
p=$!

# Probe the agent-server backend health (18000/server_info), NOT just the 8000 ingress root:
# the ingress serves the static frontend and returns 200 for / even when the agent-server is down.
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
  cat "$log" || true
  exit 1
fi

echo "OK: agent-canvas agent-server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=agent-canvas-docker-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$image    = "ghcr.io/openhands/agent-canvas:1.14.0"
$name     = "digest-agent-canvas-ci"
$hostPort = 18080

# Pull the image if the runner doesn't already have it. The published image is
# public, so no login is needed. A non-interactive session can trip over a
# configured Docker credential helper (ghcr is unauthenticated here), so pull
# with an isolated, empty Docker config that has no credsStore/credHelpers.
# TODO: remove this self-provisioning once the runners ship the image by default.
$imgId = docker images -q $image
if (-not $imgId) {
  Write-Host "Image $image not present; pulling..."
  $dockerCfg = Join-Path $env:TEMP "digest-docker-cfg"
  New-Item -ItemType Directory -Force -Path $dockerCfg | Out-Null
  '{}' | Set-Content -Path (Join-Path $dockerCfg "config.json") -Encoding ascii
  docker --config $dockerCfg pull $image
  if ($LASTEXITCODE -ne 0) { throw "docker pull failed for $image" }
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
## 4. UI에서 로컬 LLM 구성

최초 실행 시 Agent Canvas는 온보딩 흐름을 엽니다.
해당 흐름에서:

1. 에이전트로 **OpenHands**가 선택된 상태를 유지하고 **Next**를 클릭합니다.
2. **Set up your LLM**에서 **Advanced**를 선택합니다.
3. **Authentication**을 **API key**로 유지합니다.
4. **Custom Model**을 `openai/Qwen3.6-35B-A3B-GGUF`로 설정합니다.
5. **Base URL**을 `http://127.0.0.1:13305/api/v1`로 설정합니다.
6. **API Key**에는 `lemonade-local`과 같이 비어 있지 않은 임의의 자리표시자 값을 입력합니다. Lemonade는 실제 키를 요구하지 않지만, OpenHands 클라이언트는 전송할 값을 필요로 합니다.

<!-- @os:windows -->
> **Windows(Docker):** Agent Server는 컨테이너 내부에서 실행되므로, **Base URL**을 `http://127.0.0.1:13305/api/v1` 대신 `http://host.docker.internal:13305/api/v1`로 설정합니다.
> 컨테이너 내부에서 `127.0.0.1`은 컨테이너 자체를 가리킵니다. `host.docker.internal`은 Windows 호스트에서 실행 중인 Lemonade에 접근하는 주소이며, Docker Desktop이 이 호스트 이름을 자동으로 제공합니다.
<!-- @os:end -->

연결 필드는 다음과 같이 표시되어야 합니다.
API 키 필드는 UI에서 마스킹 처리됩니다.

![Lemonade 모델과 로컬 Base URL이 설정된 Agent Canvas 최초 사용 LLM Advanced 설정](assets/01-llm-advanced-settings.png)

그런 다음 **All**을 선택하고 추가 로컬 모델 필드를 설정합니다.

1. **Custom Tokenizer**까지 스크롤하여 `Qwen/Qwen3.6-35B-A3B`로 설정합니다.
2. **LiteLLM Extra Body**까지 스크롤하여 `{"enable_thinking": true}`로 설정합니다.
3. **Next**를 클릭합니다.

![Qwen 사용자 정의 토크나이저가 설정된 Agent Canvas 최초 사용 LLM All 탭](assets/02-llm-all-tokenizer-settings.png)

![LiteLLM extra body가 구성된 Agent Canvas 최초 사용 LLM All 탭](assets/03-llm-all-extra-body-settings.png)

LLM 설정은 다음과 같이 표시되어야 합니다.

| 필드 | 값 |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

`openai/` 접두사는 LiteLLM에 Lemonade 엔드포인트에 대해 OpenAI 호환 요청 형식을 사용하도록 지시합니다.
사용자 정의 토크나이저는 해당 GGUF 모델의 원본 Hugging Face 토크나이저이며, 이를 통해 OpenHands는 로컬 모델 서버가 보는 것과 동일한 채팅 템플릿 토큰 수를 계산할 수 있습니다.
현재의 최초 사용 LLM 양식에는 condenser 설정이 표시되지 않습니다.
이후 Agent Canvas 빌드에서 **Settings > LLM** 아래에 condenser 설정이 노출되는 경우, `llm_summarizing`을 사용하고 최대 토큰 수를 Lemonade 컨텍스트 윈도우보다 낮은 값, 예를 들어 `56000`으로 설정하세요.

## 5. GitHub 및 Slack MCP 서버 설치

Agent Canvas UI에서 **Customize**(또는 **Settings > MCP**)를 열어, 에이전트에 GitHub 및 Slack 작업 도구를 제공하는 MCP 서버를 추가합니다.
토큰 값은 로컬 Agent Server에만 전송되며, 암호화된 설정으로 저장됩니다.

<!-- @os:windows -->
> **Windows(Docker):** 아래의 `npx` MCP 서버 명령은 이미 Node.js가 포함된 컨테이너 내부에서 실행되므로, 호스트에는 추가로 설치되는 것이 없습니다.
> `.openhands`가 마운트되어 있으므로, MCP 서버와 해당 토큰은 컨테이너를 재시작해도 유지됩니다.
<!-- @os:end -->

### GitHub MCP 서버

다음 설정으로 새 MCP 서버를 추가합니다.

| 필드 | 값 |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = 사용자의 GitHub 토큰 |

요약하려는 리포지토리에 대한 읽기 권한이 있는 GitHub 토큰을 사용하세요.

### Slack MCP 서버

다음 설정으로 두 번째 MCP 서버를 추가합니다.

| 필드 | 값 |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = 사용자의 다이제스트 채널 ID |

`SLACK_CHANNEL_IDS`를 다이제스트 채널 ID(`SLACK_DIGEST_CHANNEL`과 동일한 값)로 설정하여, 에이전트가 모든 Slack 채널을 일일이 확인할 필요가 없도록 하세요.

두 서버를 모두 추가한 후, 각 서버에서 **Test** 버튼을 사용하여 연결이 되고 도구 목록이 표시되는지 확인하세요.
GitHub 서버에서는 GitHub 도구 목록이, Slack 서버에서는 Slack 도구 목록이 표시되어야 합니다.

![GitHub 및 Slack 서버가 설치된 Agent Canvas MCP 페이지](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. 다이제스트 자동화 생성

Agent Canvas UI에서 **Automations** 페이지를 열고 새 자동화를 생성합니다.

1. **Create automation**을 선택하고 **Prompt preset** 유형을 선택합니다.
2. **Name**을 `GitHub Development Digest to Slack`으로 설정합니다.
3. **Prompt**를 다음 텍스트로 설정하고, 리포지토리 및 채널 자리표시자를 사용자의 값으로 교체합니다.

   ```text
   Use the GitHub MCP server for exactly one repository: your-org/your-repo.
   Inspect recent development activity since the previous weekday, including
   merged pull requests, newly opened or reopened pull requests, notable
   commits pushed to main or release branches, new issues, important issue
   updates, releases, risks, blockers, and review requests. Keep GitHub
   lookups small: inspect the latest 3 to 5 commits, pull requests, issues,
   and releases. Use the Slack MCP server to post directly to channel ID
   C0123456789. Keep the Slack message concise: title with date range, 3 to 7
   bullets, links back to GitHub, and a Needs attention section only if
   needed. End with: This digest was generated by an AI agent (OpenHands) on
   behalf of the user. Do not include secrets, raw tokens, private
   environment variables, or unrelated Slack messages.
   ```

4. **Trigger**를 **Cron**으로 설정하고 일정을 `0 9 * * 1-5`(평일 오전 9시)로, **Timezone**을 사용자의 시간대(예: `America/New_York`)로 설정합니다.
5. **Timeout**을 `900`초로 설정합니다.
6. 자동화를 저장합니다.

자동화 상세 페이지에는 생성된 새 자동화가 cron 트리거 및 생성된 prompt-preset 진입점과 함께 표시됩니다.

![생성 후의 Agent Canvas 자동화 상세 페이지](assets/05-automation-created.png)
## 7. 자동화 테스트

Agent Canvas UI의 자동화 상세 페이지에서:

1. **Run now**(또는 **Dispatch**)를 클릭하여 자동화를 즉시 한 번 실행합니다.
2. 같은 페이지에서 실행 목록을 확인합니다. 최신 실행이 `COMPLETED` 상태로 전환되어야 합니다.
3. 대상 Slack 채널을 엽니다. 생성된 다이제스트가 표시되어야 합니다.

cron 일정이 실행될 때까지 기다릴 필요는 없습니다. **Run now**를 사용하면 일정에 의존하기 전에 프롬프트, MCP 연결, Slack 게시가 모두 정상적으로 작동하는지 즉시 확인할 수 있도록 요청 시 실행을 트리거합니다.

![자동화 실행이 성공적으로 완료된 Agent Canvas](assets/06-automation-run-completed.png)

![생성된 OpenHands 다이제스트를 보여주는 Slack 채널](assets/07-slackbot-message.png)

## 문제 해결

<!-- @os:windows -->
- **Docker 포트 8000이 이미 사용 중인 경우:** 다른 호스트 포트를 매핑합니다. 예를 들어 `docker run ... -p 8080:8000 ...`로 실행한 다음 `http://localhost:8080/canvas`를 엽니다.
- **`docker pull`이 자격 증명 오류로 실패하는 경우** (예: "A specified logon session does not exist"): 대화형 Windows 세션에서 pull을 실행하거나 이미지를 미리 pull해 둡니다. 이미지는 공개되어 있으므로 `docker login`이 필요하지 않습니다.
- **UI는 로드되지만 백엔드가 비정상인 경우:** 최초 실행 시 컨테이너 내부에 Agent Server 환경을 빌드합니다. 1분 정도 기다렸다가 새로 고치고, 진행 상황은 `docker logs <container>`로 확인하세요.
- **컨테이너에서 Agent Canvas가 Lemonade에 연결할 수 없는 경우:** LLM **Base URL**을 `http://host.docker.internal:13305/api/v1`로 설정하고(`127.0.0.1`이 아님), Lemonade가 Windows 호스트에서 실행 중인지 확인합니다.
<!-- @os:end -->

- **Lemonade가 중단된 경우:** 1단계의 `lemonade run "${LEMONADE_MODEL}"` 명령으로 다시 시작한 다음, 상태 확인을 다시 실행합니다.
- **`npm install -g`이 권한 오류로 실패하는 경우:** Linux 또는 WSL에서는 사용자 소유의 전역 npm 디렉터리를 구성하고 셸 시작 파일에 추가한 다음 Agent Canvas를 다시 설치합니다:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

`zsh`를 사용하는 경우 동일한 `export PATH=...` 줄을 `~/.bashrc` 대신 `~/.zshrc`에 추가하세요.
- **`custom_tokenizer` 설정 후 Agent Canvas가 LLM 설정을 거부하는 경우:** Agent Server Python 환경에 `transformers`를 설치하고, 필요하면 Agent Canvas를 재시작한 다음 LLM 설정 저장을 다시 시도합니다. `custom_tokenizer`가 설정된 경우 OpenHands는 토크나이저 채팅 템플릿을 로드하기 위해 Transformers가 필요합니다.
- **Agent Canvas가 Lemonade에 연결할 수 없는 경우:** `curl -fsS "${LEMONADE_BASE_URL}/health"`를 확인하고, 최초 사용 시 LLM 양식 또는 **Settings > LLM**에 입력한 기본 URL이 실행 중인 로컬 엔드포인트 또는 HTTPS 터널과 일치하는지 확인합니다.
- **LLM 설정이 저장되지 않는 경우:** 값을 입력한 후 **Next**를 클릭했는지 확인하세요. **Settings > LLM**을 다시 열어 값이 유지되었는지 확인합니다.
- **GitHub MCP가 비공개 저장소를 볼 수 없는 경우:** GitHub 토큰이 대상 저장소에 대한 읽기 권한을 가지고 있는지, **Customize**의 MCP **Test** 버튼이 GitHub 도구를 광고하는지 확인합니다.
- **Slack이 채널을 읽을 수는 있지만 게시할 수 없는 경우:** Slack 앱을 대상 채널에 초대하고 봇이 `chat:write` 권한을 가지고 있는지 확인합니다.
- **자동화가 너무 많은 Slack 채널을 나열하는 경우:** Slack 채널 ID를 사용하고 **Customize**에서 Slack MCP 서버에 `SLACK_CHANNEL_IDS`를 설정합니다.
- **자동화 실행이 실패하거나 컨텍스트를 초과하는 경우:** Lemonade가 `ctx_size=65536`으로 시작되었는지, OpenHands LLM에 `custom_tokenizer`가 설정되었는지 확인하고, GitHub 결과 세트를 3~5개 항목으로 제한한 명시적 저장소를 사용합니다. Agent Canvas 빌드에 condenser 설정이 노출되어 있다면 condenser 최대 토큰을 Lemonade 컨텍스트 윈도우보다 낮게 설정합니다.

## 다음 단계

- 주간 릴리스 전용 다이제스트를 추가합니다.
- 더 빠른 PR 또는 push 알림을 위한 GitHub 이벤트 트리거 자동화를 추가합니다.
- 동일한 다이제스트를 Notion, Linear 또는 다른 MCP 기반 도구로 라우팅합니다.

## 리소스

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Lemonade Server 문서](https://lemonade-server.ai/docs)
- [OpenHands extensions 저장소](https://github.com/OpenHands/extensions)
- [Model Context Protocol 서버](https://github.com/modelcontextprotocol/servers)
- [Slack MCP 패키지](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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
try { lemonade unload } catch {}
```
<!-- @test:end -->
<!-- @os:end -->