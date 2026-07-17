<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> 이 플레이북은 GitHub에서 렌더링할 수 없는 특수 태그를 사용합니다. 이 콘텐츠를 올바르게 미리 보려면 [amd.com/playbooks](https://amd.com/playbooks)를 방문하세요.
<!-- @github-only:end -->

## 개요

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> 이 플레이북은 최소 **32GB**의 시스템 메모리가 필요합니다.
<!-- @device:end -->

n8n은 시각적 노드 기반 편집기를 사용하여 앱과 서비스를 연결할 수 있는 워크플로 자동화 플랫폼입니다.

이 플레이북에서는 AP News 비즈니스 섹션을 스크래핑하고, 주요 헤드라인을 추출하며, 시스템에서 실행 중인 로컬 LLM을 사용하여 투자자 중심의 요약을 생성하는 AI 기반 금융 뉴스 요약기를 설정하는 방법을 안내합니다.

## 학습 내용

- n8n 설치 및 실행 방법
- 사전 구축된 워크플로 가져오기 및 구성
- 기본 n8n 통합을 사용하여 Lemonade에 연결하기
- 워크플로 노드 및 데이터 흐름 이해

## Lemonade란?

[Lemonade](https://lemonade-server.ai)는 AMD 하드웨어용으로 구축된 로컬 LLM 서빙 플랫폼입니다. 완전히 사용자의 머신에서 실행되는 OpenAI 호환 API를 제공하므로 데이터가 기기 밖으로 나가지 않습니다.

이 플레이북에서는 Lemonade를 사용하여 n8n이 AI 기반 작업을 위해 연결하는 로컬 LLM을 서빙합니다.

n8n에는 **기본 Lemonade 노드**(`Lemonade Chat Model`)가 포함되어 있어 수준 높은 통합을 제공합니다. 수동 구성이 필요 없으므로 로컬 LLM을 자동화 워크플로에 간편하게 연결할 수 있습니다.

## 메모리 구성 설정

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 소프트웨어 업데이트 확인

<!-- @require:software-update -->
<!-- @device:end -->

## 소프트웨어 사전 요구 사항 설치
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @require:lemonade,podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="gpt-oss-20b-mxfp4-GGUF" -->
<!-- @device:end -->


<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade (robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1
if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
  -H "Content-Type: application/json" `
  --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
}
finally {
  Remove-Item  $tmpBody -Force -ErrorAction SilentlyContinue
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
  "max_tokens": 32
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

<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->

## n8n 설치
<!-- @os:windows -->
npm을 사용하여 n8n을 전역으로 설치합니다.

> **참고**: npm 경고가 일부 표시될 수 있습니다. 이는 정상적인 현상입니다.

```bash
npm install -g n8n
```

<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **팁**: Windows 사용자는 일부 PowerShell 명령을 실행하기 전에 PowerShell 실행 정책을 수정해야 할 수 있습니다(예:
> RemoteSigned 또는 Unrestricted로 설정).
<!-- @os:end -->


<!-- @os:windows -->
> **PATH 문제**: `n8n --version` 실행 시 명령을 찾을 수 없다고 표시되면, npm 전역 bin 디렉터리가 사용자 `PATH`에 포함되어 있는지 확인하세요. 일반적인 설치 경로는 `C:\Users\<username>\AppData\Roaming\npm`입니다.
> 이 경로를 사용자 경로에 추가하고(시스템 환경 변수 편집 > 환경 변수 > 사용자 경로 편집) 터미널을 다시 시작하세요.

<!-- @os:end -->

<!-- @os:linux -->
이제 Podman 서비스를 사용하여 n8n 설치를 컨테이너화합니다.

원하는 디렉터리에 다음 파일을 다운로드하세요: [compose.yml](assets/compose.yml)

해당 디렉터리에서 다음 명령을 실행하세요:
```bash
podman compose up -d
```

이 명령은 n8n을 설치하고 영구 스토리지에 기록합니다.

브라우저 주소 표시줄에 `localhost:5678`을 입력하여 n8n을 실행합니다.
<!-- @os:end -->

<!-- @os:windows -->
## n8n 실행

터미널에서 n8n을 시작합니다:

```bash
n8n start
```

<!-- @test:id=n8n-start-windows timeout=300 hidden=True -->
```powershell
$N8N_CMD = "$env:APPDATA\npm\n8n.cmd"
$p = Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$N8N_CMD`" start" -NoNewWindow -PassThru
try {
  $ok = $false
  for ($i=0; $i -lt 120; $i++) {
    # Check HTTP status code only (body may be empty)
    $code = curl.exe -s -o NUL -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz
    if ($LASTEXITCODE -eq 0 -and $code -eq "200") { $ok = $true; break }
    Start-Sleep -Seconds 1
  }
  if (-not $ok) { throw "n8n not ready on http://127.0.0.1:5678/healthz" }
  Write-Host "OK: n8n server is responding"
} finally {
  # Kill the process actually listening on 5678
  $conn = Get-NetTCPConnection -LocalPort 5678 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($conn) { Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue }
  # Also kill wrapper pid just in case
  if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-start-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

n8n start >/tmp/n8n-test.log 2>&1 &
p=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "n8n not ready on http://127.0.0.1:5678/healthz"
  exit 1
fi

echo "OK: n8n server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
n8n이 로컬 웹 서버를 시작합니다. `'o'`를 누르거나 브라우저에서 `http://localhost:5678`을 열어 편집기에 접속하세요.
<!-- @os:end -->


> **팁**: n8n을 사용하는 동안 터미널 창을 열어 두세요. 닫으면 서버가 중지될 수 있습니다.

## Lemonade 실행

Lemonade는 모델을 실행하고 n8n에 연결하는 로컬 서버입니다.

<!-- @os:linux -->
작업 표시줄의 Lemonade 아이콘을 클릭하여 Lemonade GUI를 엽니다. 여기서 모델, 백엔드를 탐색하고 사전 설치된 모델을 불러올 수 있습니다.
<!-- @os:end -->

<!-- @os:windows -->
Lemonade 아이콘을 클릭하여 Lemonade GUI를 엽니다. 트레이 아이콘을 마우스 오른쪽 버튼으로 클릭하여 앱을 엽니다. 그런 다음 모델, 백엔드를 추가하고 사전 설치된 모델을 불러올 수 있습니다.
<!-- @os:end -->

>**팁**: 실행 중이면 Lemonade GUI는 http://localhost:13305 에서도 접속할 수 있습니다.

또는 터미널을 열고 `lemonade list`를 실행하여 설치된 모델을 확인한 후 다음을 실행하세요:

<!-- @device:halo_box -->
<!-- @os:linux -->
```bash
lemonade run gpt-oss-120b-Q4_K_M --llamacpp vulkan
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo -->
```bash
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
```bash
lemonade run gpt-oss-20b-GGUF --llamacpp vulkan
```
<!-- @device:end -->


## 워크플로 설정

### 1단계: n8n 계정 가입 또는 로그인

n8n을 처음 열면 계정을 만들거나 로그인하라는 메시지가 표시됩니다:

1. 브라우저에서 `http://localhost:5678`을 엽니다.
2. 이메일로 새 로컬 계정을 만들거나, 이미 계정이 있다면 로그인합니다.
3. 로그인하면 n8n 대시보드가 표시됩니다.

> **팁**: 계정에서 잠긴 경우 `n8n user-management:reset`을 시도해 보세요.

### 2단계: 워크플로 가져오기

바로 가져올 수 있는 사전 구축된 워크플로를 제공합니다:

1. 다음 워크플로 파일을 다운로드하세요: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. **Start from Scratch**를 클릭하여 워크플로 편집기를 엽니다. 또는 왼쪽 상단의 + 버튼을 클릭한 후 **Add workflow**를 클릭합니다.
3. 오른쪽 상단 바의 **...** 메뉴(점 세 개)를 클릭하고 **Import from file**을 선택합니다.
4. 다운로드한 `financial-news-workflow.json` 파일을 선택합니다.
5. 워크플로가 캔버스에 나타납니다.


### 3단계: 워크플로 이해

가져온 워크플로에는 9개의 연결된 노드가 포함되어 있습니다:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| 노드 | 목적 |
|------|---------|
| **When clicking 'Execute workflow'** | 워크플로를 시작하는 수동 트리거 |
| **Fetch Financial News Webpage** | `https://apnews.com/business`에 대한 HTTP GET 요청 |
| **Delay to Ensure Page Load** | 페이지 콘텐츠가 완전히 로드되도록 기다리는 대기 노드 |
| **Extract News Headlines & Text** | CSS 선택자를 사용하여 헤드라인, 편집자 추천, 주요 기사, 지역 뉴스를 추출하는 HTML 노드 |
| **Clean Extracted News Data** | 추출된 모든 데이터를 단일 텍스트 필드로 결합하는 Set 노드 |
| **AI Financial News Summarizer** | 금융 분석가 시스템 프롬프트로 뉴스를 처리하는 AI 에이전트 |
| **Lemonade Chat Model** | LLM을 실행하는 로컬 Lemonade 서버에 연결 |
| **Structured Output Parser** | AI 출력을 구조화된 JSON으로 형식화 |
| **Convert to File** | 요약을 다운로드 가능한 파일로 변환 |

### 4단계: Lemonade 자격 증명 구성

워크플로를 실행하기 전에 로컬 Lemonade 서버에 연결해야 합니다:

1. n8n에서 **Lemonade Chat Model** 노드를 더블 클릭합니다.
2. **Credential to connect with** 드롭다운 메뉴에서 **Create New Credential**을 선택합니다.
3. 아래 표의 값을 입력하고 저장을 클릭합니다.
4. Lemonade Server에 불러온 관련 모델을 선택합니다.

  | 필드 | 값 |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **참고**: 테스트 전에 터미널에서 `lemonade status`를 실행하여 Lemonade 서버가 실행 중인지 확인하세요.
<!-- @device:halo_box -->
> 이 워크플로는 GPT-OSS-120B를 사용하며 Lemonade에 사전 설치되어 있습니다. Lemonade Chat Model 노드 설정에서 다른 불러온 모델로 변경할 수 있습니다.
<!-- @device:end -->

### 5단계: 워크플로 테스트

1. 모델이 불러진 상태로 Lemonade가 실행 중인지 확인합니다.
2. 캔버스 하단 중앙의 **Execute workflow**를 클릭합니다.
3. 각 노드가 왼쪽에서 오른쪽으로 실행되는 것을 확인합니다. 완료되면 녹색으로 바뀝니다.
4. **AI Financial News Summarizer** 노드를 더블 클릭하여 하단 창에서 생성된 요약을 확인합니다.
5. **Convert to File** 노드를 더블 클릭하여 하단 창에서 해당 텍스트 파일을 다운로드합니다.

## AI 에이전트 이해

AI Financial News Summarizer는 금융 분석을 위해 설계된 시스템 프롬프트를 사용합니다:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

에이전트는 정제된 뉴스 데이터를 받아 시장 심리가 포함된 구조화된 요약을 출력합니다.

### 워크플로 저장

상단의 워크플로 이름을 클릭하여 원하는 이름으로 변경합니다. 워크플로는 작업하는 동안 자동으로 저장됩니다.

## 다음 단계

- **자동화 예약**: 수동 트리거를 **Schedule Trigger**로 교체하여 매일 실행
- **알림 전송**: **Discord**, **Slack** 또는 **Email** 노드를 추가하여 요약 수신
- **다른 모델 시도**: Lemonade Chat Model 노드에서 모델을 변경하여 다양한 LLM 실험
- **추출 사용자 지정**: HTML Extract 노드의 CSS 선택자를 수정하여 다른 뉴스 섹션 대상 지정
- **다른 백엔드 시도**: n8n은 [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio 및 기타 로컬 LLM 백엔드도 지원합니다.

### n8n 템플릿 탐색

n8n에는 수백 개의 사전 구축된 워크플로 템플릿이 있습니다. 공식 템플릿 라이브러리를 탐색하세요:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

"AI", "LLM" 또는 "automation"을 검색하여 가져와서 사용자 지정할 수 있는 워크플로를 찾아보세요.

자세한 내용은 [n8n 문서](https://docs.n8n.io/)를 참조하세요.