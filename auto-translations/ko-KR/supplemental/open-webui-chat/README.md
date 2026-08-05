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
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> 이 플레이북은 최소 **32GB**의 시스템 메모리가 필요합니다.
<!-- @device:end -->

## 개요

[Open WebUI](https://docs.openwebui.com)는 친숙한 챗봇 경험을 제공하는 동시에 하나 이상의 AI 모델 서버에 대한 프론트엔드 역할을 하는, 자체 호스팅되는 브라우저 기반 인터페이스입니다. 특정 제공업체에 종속되는 대신, Open WebUI는 **OpenAI 호환 API를 노출하는 모든 백엔드**에 연결할 수 있으므로 UI를 전환하지 않고도 모델과 기능을 바꿀 수 있습니다.

이 플레이북에서는 백엔드로 [**Lemonade**](https://lemonade-server.ai)를 사용합니다. 이는 여러 모달리티를 지원하는 **통합 OpenAI 호환 엔드포인트**를 노출하기 때문입니다:
- 텍스트 생성을 위한 **대규모 언어 모델(LLM)**
- 이미지 이해를 위한 **비전 모델**
- 이미지 생성을 위한 **Stable Diffusion**
- 음성을 텍스트로 변환하는 **오디오 전사 모델**

이 설정을 통해 **완전한 멀티모달 워크플로를 처음부터 끝까지** 탐색할 수 있습니다.

---

## 학습할 내용

이 과정을 마치면 다음을 수행할 수 있게 됩니다:

- Open WebUI를 로컬 OpenAI 호환 백엔드(Lemonade)에 연결
- 브라우저에서 로컬 LLM과 채팅
- 이미지를 업로드하고 비전 모델에 질문하기
- Stable Diffusion 모델(SDXL-Turbo / SDXL)을 사용하여 텍스트 프롬프트로 이미지 생성
- 다른 백엔드(Ollama, vLLM, llama.cpp server 등)를 사용할 수 있도록 멘탈 모델 이해하기

---

## 핵심 개념(멘탈 모델)

### 세 가지 구성 요소

| 구성 요소 | 역할 | 예시 |
|---|---|---|
| 프론트엔드(UI) | 사용자가 상호작용하는 웹 앱 | Open WebUI |
| 백엔드(모델 서버) | 모델을 호스팅하고 HTTP 엔드포인트를 노출 | Lemonade, Ollama, vLLM, llama.cpp server, OpenAI 호환 서버 |
| 모델 | 실제 LLM / 비전 / 디퓨전 / 오디오 모델 | CodeLlama, DeepSeek, Gemma-MM, SDXL, SD-Turbo, Whisper |

#### "OpenAI 호환 API"가 중요한 이유

Open WebUI는 다음과 같은 표준 OpenAI 스타일 엔드포인트를 중심으로 구축되었습니다:
  - 채팅: `/chat/completions`
  - 모델 목록: `/models`
  - 이미지 생성: `/images/generations`
  - 오디오 전사: `/audio/transcriptions`

Lemonade는 이러한 엔드포인트를 `http://localhost:13305/api/v1/...` 아래에 노출합니다

백엔드가 이러한 엔드포인트를 지원하면 Open WebUI는 최소한의 설정만으로 해당 백엔드와 통신할 수 있습니다. 이것이 워크플로를 변경하지 않고도 백엔드를 전환할 수 있는 이유입니다.

#### 두 개의 서비스, 두 개의 포트

이 플레이북 전반에서 두 가지 별도 서비스를 사용하게 됩니다:

| 서비스 | URL | 하는 일 |
|---|---|---|
| **Lemonade**(GUI) | `http://localhost:13305` | 모델 탐색, 다운로드 및 관리 |
| **Open WebUI** | `http://localhost:8080` | 채팅, 이미지 업로드, 이미지 생성 — 사용자용 UI |

Lemonade는 모델을 실행하고, Open WebUI는 사용자가 상호작용하는 인터페이스입니다. 먼저 Lemonade GUI를 사용하여 모델을 다운로드한 다음, Open WebUI에서 사용하세요.

---

## 메모리 구성 설정

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 소프트웨어 업데이트 확인

<!-- @require:software-update -->
<!-- @device:end -->

## 초기 설정

이 플레이북은 백엔드로 Lemonade가 실행 중이어야 하며, Linux에서는 Open WebUI를 실행하기 위한 컨테이너 엔진(Podman)이 필요합니다. Open WebUI를 설치하기 전에 이를 먼저 설정하세요.

<!-- @os:windows -->
<!-- @device:halo_box,halo,stx,krk -->
<!-- @require:lemonade -->
<!-- @device:end -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver,lemonade -->
<!-- @device:end -->
---
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
<!-- @require:lemonade,podman -->
<!-- @device:end -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver,lemonade,podman -->
<!-- @device:end -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
---
<!-- @device:end -->
<!-- @os:end -->

<!-- @test:id=lemonade-cli-verify timeout=30 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end --> 

## Lemonade에서 모델 다운로드하기

Open WebUI를 설치하기 전에, 사용하려는 모델이 Lemonade에서 다운로드되어 준비되어 있는지 확인하세요.

1. `http://localhost:13305`에서 Lemonade GUI를 엽니다.
2. 사용 가능한 모델을 탐색하고 사용하려는 모델을 다운로드합니다(예: 채팅용 LLM, 비전 모델, 그리고/또는 이미지 생성을 위한 Stable Diffusion 모델).
3. 브라우저에서 `http://localhost:13305/api/v1/models`를 방문하여 API가 응답하는지 확인합니다 — 다운로드한 모델이 나열되어야 합니다.

> 모델은 **Open WebUI**(`localhost:8080`)에 표시되기 전에 **Lemonade**(`localhost:13305`)에서 먼저 다운로드되어야 합니다. 나중에 Open WebUI에서 모델이 표시되지 않으면 여기로 돌아와서 먼저 Lemonade를 확인하세요.


<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
<!-- @test:id=openwebui-lemonade-multimodal-smoke-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$tmpChat = $null
$tmpVision = $null
$tmpImg = $null

try {
  # Wait for /models
  $modelsJson = $null
  for ($i=0; $i -lt 120; $i++) {
    $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
    if ($modelsJson) { break }
    Start-Sleep -Seconds 1
  }
  if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
  Write-Host "OK: Lemonade server is responding"
  
  # Verify required models are present + downloaded
  $parsed = $modelsJson | ConvertFrom-Json
  $required = @(
    "Qwen3-4B-Hybrid",
    "Qwen3.5-4B-GGUF",
    "SDXL-Turbo"
  )
  foreach ($mid in $required) {
    $entry = $parsed.data | Where-Object { $_.id -eq $mid } | Select-Object -First 1
    if (-not $entry) { throw "Model $mid is not present in /api/v1/models. Please download it." }
    if (-not $entry.downloaded) { throw "Model $mid is present but not downloaded. Please download it." }
    Write-Host "OK: $mid is downloaded"
  }

  # Chat completion smoke test (LLM)
  $chatBody = @{
    model = "Qwen3-4B-Hybrid"
    messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
    temperature = 0
    max_tokens = 500
    stream = $false
  } | ConvertTo-Json -Depth 6
  $tmpChat = Join-Path $env:TEMP "chat-body.json"
  [System.IO.File]::WriteAllText($tmpChat, $chatBody, [System.Text.UTF8Encoding]::new($false))
  $chatOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer -" `
    --data-binary "@$tmpChat"
  if (-not $chatOut) { throw "Empty response from chat/completions" }
  $chatParsed = $chatOut | ConvertFrom-Json
  $chatText = $chatParsed.choices[0].message.content
  if ($chatText -notmatch "\bOK\b") { throw "LLM chat test failed. Got: $chatText" }
  Write-Host "OK: LLM chat works"

  # Vision smoke test (OpenAI-style image_url)
  $png1x1 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO8p+S4AAAAASUVORK5CYII="
  $dataUrl = "data:image/png;base64,$png1x1"
  $visionBody = @{
    model = "Qwen3.5-4B-GGUF"
    messages = @(@{
      role = "user"
      content = @(
        @{ type = "text"; text = "If you can see an image input, reply with exactly: OK" },
        @{ type = "image_url"; image_url = @{ url = $dataUrl } }
      )
    })
    temperature = 0
    max_tokens = 256
  } | ConvertTo-Json -Depth 10
  $tmpVision = Join-Path $env:TEMP "vision-body.json"
  [System.IO.File]::WriteAllText($tmpVision, $visionBody, [System.Text.UTF8Encoding]::new($false))
  $visionOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer -" `
    --data-binary "@$tmpVision"
  if (-not $visionOut) { throw "Empty response from vision chat/completions" }
  $visionParsed = $visionOut | ConvertFrom-Json
  if (-not $visionParsed.choices -or $visionParsed.choices.Count -lt 1) { throw "Unexpected vision response (no choices). Raw response: $visionOut" }
  $visionText = $visionParsed.choices[0].message.content
  if ([string]::IsNullOrWhiteSpace($visionText)) { throw "Vision returned empty content. Raw response: $visionOut" }
  if ($visionText -notmatch "\bOK\b") { throw "Vision test failed. Got: $visionText. Raw response: $visionOut" }
  Write-Host "OK: Vision chat works"

  # Image generation smoke test
  $imgBody = @{
    model  = "SDXL-Turbo"
    prompt = "A simple red cube on a white table, studio lighting"
    size   = "256x256"
    steps  = 4
    response_format = "b64_json"
  } | ConvertTo-Json -Depth 6
  $tmpImg = Join-Path $env:TEMP "img-body.json"
  [System.IO.File]::WriteAllText($tmpImg, $imgBody, [System.Text.UTF8Encoding]::new($false))
  $imgOut = curl.exe -sS --fail-with-body --max-time 900 http://127.0.0.1:13305/api/v1/images/generations `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer -" `
    --data-binary "@$tmpImg"
  if (-not $imgOut) { throw "Empty response from images/generations" }
  $imgParsed = $imgOut | ConvertFrom-Json
  if (-not $imgParsed.data -or -not $imgParsed.data[0].b64_json) { throw "Image generation did not return data[0].b64_json. Raw response: $imgOut" }
  Write-Host "OK: Image generation works"
}
finally {
  @($tmpChat, $tmpVision, $tmpImg) |
  Where-Object { $_ } |
  ForEach-Object { Remove-Item $_ -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=openwebui-lemonade-multimodal-smoke-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$tmpChat = $null
$tmpVision = $null
$tmpImg = $null

try {
  # Wait for /models
  $modelsJson = $null
  for ($i=0; $i -lt 120; $i++) {
    $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
    if ($modelsJson) { break }
    Start-Sleep -Seconds 1
  }
  if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
  Write-Host "OK: Lemonade server is responding"
  
  # Verify required models are present + downloaded
  $parsed = $modelsJson | ConvertFrom-Json
  $required = @(
    "Qwen3.5-4B-GGUF",
    "SDXL-Turbo"
  )
  foreach ($mid in $required) {
    $entry = $parsed.data | Where-Object { $_.id -eq $mid } | Select-Object -First 1
    if (-not $entry) { throw "Model $mid is not present in /api/v1/models. Please download it." }
    if (-not $entry.downloaded) { throw "Model $mid is present but not downloaded. Please download it." }
    Write-Host "OK: $mid is downloaded"
  }

  # Chat completion smoke test (LLM)
  $chatBody = @{
    model = "Qwen3.5-4B-GGUF"
    messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
    temperature = 0
    max_tokens = 500
    stream = $false
  } | ConvertTo-Json -Depth 6
  $tmpChat = Join-Path $env:TEMP "chat-body.json"
  [System.IO.File]::WriteAllText($tmpChat, $chatBody, [System.Text.UTF8Encoding]::new($false))
  $chatOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer -" `
    --data-binary "@$tmpChat"
  if (-not $chatOut) { throw "Empty response from chat/completions" }
  $chatParsed = $chatOut | ConvertFrom-Json
  $chatText = $chatParsed.choices[0].message.content
  if ($chatText -notmatch "\bOK\b") { throw "LLM chat test failed. Got: $chatText" }
  Write-Host "OK: LLM chat works"

  # Vision smoke test (OpenAI-style image_url)
  $png1x1 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO8p+S4AAAAASUVORK5CYII="
  $dataUrl = "data:image/png;base64,$png1x1"
  $visionBody = @{
    model = "Qwen3.5-4B-GGUF"
    messages = @(@{
      role = "user"
      content = @(
        @{ type = "text"; text = "If you can see an image input, reply with exactly: OK" },
        @{ type = "image_url"; image_url = @{ url = $dataUrl } }
      )
    })
    temperature = 0
    max_tokens = 256
  } | ConvertTo-Json -Depth 10
  $tmpVision = Join-Path $env:TEMP "vision-body.json"
  [System.IO.File]::WriteAllText($tmpVision, $visionBody, [System.Text.UTF8Encoding]::new($false))
  $visionOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer -" `
    --data-binary "@$tmpVision"
  if (-not $visionOut) { throw "Empty response from vision chat/completions" }
  $visionParsed = $visionOut | ConvertFrom-Json
  if (-not $visionParsed.choices -or $visionParsed.choices.Count -lt 1) { throw "Unexpected vision response (no choices). Raw response: $visionOut" }
  $visionText = $visionParsed.choices[0].message.content
  if ([string]::IsNullOrWhiteSpace($visionText)) { throw "Vision returned empty content. Raw response: $visionOut" }
  if ($visionText -notmatch "\bOK\b") { throw "Vision test failed. Got: $visionText. Raw response: $visionOut" }
  Write-Host "OK: Vision chat works"

  # Image generation smoke test
  $imgBody = @{
    model  = "SDXL-Turbo"
    prompt = "A simple red cube on a white table, studio lighting"
    size   = "256x256"
    steps  = 4
    response_format = "b64_json"
  } | ConvertTo-Json -Depth 6
  $tmpImg = Join-Path $env:TEMP "img-body.json"
  [System.IO.File]::WriteAllText($tmpImg, $imgBody, [System.Text.UTF8Encoding]::new($false))
  $imgOut = curl.exe -sS --fail-with-body --max-time 900 http://127.0.0.1:13305/api/v1/images/generations `
    -H "Content-Type: application/json" `
    -H "Authorization: Bearer -" `
    --data-binary "@$tmpImg"
  if (-not $imgOut) { throw "Empty response from images/generations" }
  $imgParsed = $imgOut | ConvertFrom-Json
  if (-not $imgParsed.data -or -not $imgParsed.data[0].b64_json) { throw "Image generation did not return data[0].b64_json. Raw response: $imgOut" }
  Write-Host "OK: Image generation works"
}
finally {
  @($tmpChat, $tmpVision, $tmpImg) |
  Where-Object { $_ } |
  ForEach-Object { Remove-Item $_ -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end -->
<!-- @device:end -->
<!-- @os:end --> 

<!-- @os:linux --> 
<!-- @test:id=openwebui-lemonade-multimodal-smoke-linux timeout=1800 hidden=True -->
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
import base64, json, os, sys, urllib.request

data = json.loads(os.environ["MODELS_JSON"])
required = [
  "Qwen3.5-4B-GGUF",
  "SDXL-Turbo",
]

by_id = {m.get("id"): m for m in data.get("data", [])}
for mid in required:
  m = by_id.get(mid)
  if not m:
    print(f"Model {mid} is not present in /api/v1/models. Please download it.")
    sys.exit(1)
  if not m.get("downloaded", False):
    print(f"Model {mid} is present but not downloaded. Please download it.")
    sys.exit(1)
  print(f"OK: {mid} is downloaded")

def post_json(url, payload, timeout=300):
  req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={
      "Content-Type": "application/json",
      "Authorization": "Bearer -",
    },
    method="POST",
  )
  try:
    with urllib.request.urlopen(req, timeout=timeout) as r:
      return json.loads(r.read().decode("utf-8"))
  except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", errors="replace")
    raise SystemExit(f"POST {url} failed with HTTP {e.code}. Response body:\n{body}")

# LLM chat smoke test
chat = post_json("http://127.0.0.1:13305/api/v1/chat/completions", {
  "model": "Qwen3.5-4B-GGUF",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 500,
  "stream": False,
}, timeout=300)
text = chat["choices"][0]["message"]["content"]
if "OK" not in text:
  raise SystemExit(f"LLM chat test failed. Got: {text}")
print("OK: LLM chat works")

# Vision smoke test (OpenAI image_url format)
png1x1 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO8p+S4AAAAASUVORK5CYII="
data_url = "data:image/png;base64," + png1x1
vision = post_json("http://127.0.0.1:13305/api/v1/chat/completions", {
  "model": "Qwen3.5-4B-GGUF",
  "messages": [{
    "role": "user",
    "content": [
      {"type": "text", "text": "If you can see an image input, reply with exactly: OK"},
      {"type": "image_url", "image_url": {"url": data_url}},
    ],
  }],
  "temperature": 0,
  "max_tokens": 256,
}, timeout=300)
if not vision.get("choices"):
  raise SystemExit(f"Unexpected vision response (no choices). Raw response:\n{json.dumps(vision, indent=2)}")
vtext = vision["choices"][0]["message"].get("content", "")
if not vtext.strip():
  raise SystemExit(f"Vision returned empty content. Raw response:\n{json.dumps(vision, indent=2)}")
if "OK" not in vtext:
  raise SystemExit(f"Vision test failed. Got: {vtext}\nRaw response:\n{json.dumps(vision, indent=2)}")
print("OK: Vision chat works")

# Image generation smoke test
img = post_json("http://127.0.0.1:13305/api/v1/images/generations", {
  "model": "SDXL-Turbo",
  "prompt": "A simple red cube on a white table, studio lighting",
  "size": "256x256",
  "steps": 4,
  "response_format": "b64_json",
}, timeout=900)
b64 = img.get("data", [{}])[0].get("b64_json")
if not b64:
  raise SystemExit("Image generation did not return data[0].b64_json")
print("OK: Image generation works")
PY
```
<!-- @test:end --> 
<!-- @os:end --> 

## Open WebUI 설치

<!-- @os:windows -->
### 1. Python 3.12 설치

Open WebUI는 **Python 3.12**가 필요합니다 — Python 3.13 이상에서는 설치되지 않습니다. Windows Python 런처(`py`)를 사용하면 기존 Python 버전과 충돌 없이 3.12를 나란히 설치할 수 있습니다.

```powershell
winget install Python.Python.3.12
```

설치 후 터미널을 닫았다가 다시 열고 다음을 통해 확인하세요:

```powershell
py -3.12 --version
# Python 3.12.x
```

<!-- @device:halo_box -->
> **참고:** 시스템에는 Python 3.13이 미리 설치되어 있습니다. 3.12를 설치해도 이에 영향을 주지 않습니다 — `python`은 계속 3.13을 사용하며, `py -3.12`는 필요할 때만 3.12를 대상으로 합니다.
<!-- @device:end -->

<!-- @test:id=python-env-check-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$v = (& py -3.12 --version) 2>&1
if ($LASTEXITCODE -ne 0) { throw "Python 3.12 was not found. Install it with: winget install Python.Python.3.12" }
if ($v -notmatch "Python 3\.12\.") { throw "Expected Python 3.12.x but got: $v" }

Write-Host "OK: $v"
```
<!-- @test:end --> 

### 2. 가상 환경을 생성하고 Open WebUI 설치하기

```powershell
mkdir openwebui
cd openwebui
py -3.12 -m venv openwebui-venv
.\openwebui-venv\Scripts\activate
pip install open-webui beautifulsoup4
```

<!-- @test:id=openwebui-install-venv-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$work = Join-Path (Get-Location) "openwebui"
if (Test-Path $work) { Remove-Item -Recurse -Force $work }
New-Item -ItemType Directory -Force -Path $work | Out-Null

Push-Location $work
try {
  py -3.12 -m venv openwebui-venv
  $py = Join-Path $work "openwebui-venv\Scripts\python.exe"

  & $py -m pip install --upgrade pip
  if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed" }

  & $py -m pip install open-webui beautifulsoup4
  if ($LASTEXITCODE -ne 0) { throw "pip install open-webui beautifulsoup4 failed" }

  Write-Host "OK: open-webui installed in venv"
}
finally {
  Pop-Location
}
```
<!-- @test:end --> 

<!-- @test:id=openwebui-install-check-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$work = Join-Path (Get-Location) "openwebui"
$venv = Join-Path $work "openwebui-venv"
$py = Join-Path $venv "Scripts\python.exe"

& $py -c "import open_webui; print('OK: import open_webui')"
& $py -c "import bs4; print('OK: bs4 import')"
```
<!-- @test:end --> 

<!-- @test:id=openwebui-cli-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$work = Join-Path (Get-Location) "openwebui"
$venv = Join-Path $work "openwebui-venv"
$ow = Join-Path $venv "Scripts\open-webui.exe"

if (-not (Test-Path $ow)) { throw "open-webui.exe not found at $ow" }

& $ow --help | Out-Null
Write-Host "OK: open-webui CLI is available"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
이제 Podman 서비스를 사용하여 Open WebUI 설치를 컨테이너화하겠습니다.

원하는 디렉터리에 다음을 다운로드하세요: [compose.yml](assets/compose.yml)

해당 디렉터리에서 다음 명령을 실행합니다:

```bash
podman compose up -d
```

이 명령은 Open WebUI 이미지를 가져와 영구 저장소에 기록합니다.

브라우저 주소창에 `localhost:8080`을 입력하여 Open WebUI를 실행하세요.

<!-- @test:id=openwebui-podman-prereq-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PODMAN_COMPOSE_PROVIDER="$(command -v podman-compose)"
export PODMAN_COMPOSE_WARNING_LOGS=false

podman --version
podman compose version
podman info >/dev/null

if [ ! -f compose.yml ]; then
  echo "compose.yml not found in current working directory (playbooks/supplemental/open-webui-chat/assets)"
  exit 1
fi

echo "OK: Podman, Podman Compose, and compose.yml are available"
```
<!-- @test:end -->

<!-- @test:id=openwebui-compose-validate-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path
import sys
import yaml

path = Path("compose.yml")
if not path.exists():
    raise SystemExit("compose.yml not found")

data = yaml.safe_load(path.read_text())
svc = data.get("services", {}).get("open-webui")
if not svc:
    raise SystemExit("compose.yml does not define services.open-webui")

expected_image = "ghcr.io/open-webui/open-webui:main"
if svc.get("image") != expected_image:
    raise SystemExit(f"Expected image {expected_image}, got {svc.get('image')}")

if svc.get("container_name") != "open-webui":
    raise SystemExit("Expected container_name: open-webui")

if svc.get("network_mode") != "host":
    raise SystemExit("Expected network_mode: host")

volumes = svc.get("volumes", [])
if "open_webui_data:/app/backend/data" not in volumes:
    raise SystemExit("Expected open_webui_data:/app/backend/data volume mount")

if "open_webui_data" not in data.get("volumes", {}):
    raise SystemExit("Expected top-level open_webui_data volume")

print("OK: compose.yml matches the Open WebUI Podman setup")
PY

podman compose -f compose.yml config >/dev/null

echo "OK: podman compose can parse compose.yml"
```
<!-- @test:end -->
<!-- @os:end -->

> **팁**: Open WebUI는 [GitHub](https://github.com/open-webui/open-webui)에서 다른 설치 옵션도 제공합니다.
## Open WebUI 서버 시작하기

<!-- @os:windows -->
- 다음 명령을 실행하여 Open WebUI HTTP 서버를 시작합니다:
```bash
open-webui serve
```
<!-- @os:end -->

- 브라우저에서 `http://localhost:8080`으로 이동합니다.
- Open WebUI에서 로컬 관리자 계정을 생성하라는 메시지가 표시됩니다. 로그인하면 채팅 인터페이스가 표시됩니다.

<p align="center">
  <img src="assets/open-webui_chat_interface.png" alt="Open WebUI Chat Interface" width="600"/>
</p>

<!-- @os:windows -->
> 터미널 창을 닫지 마세요. 창을 닫으면 Open WebUI가 중지됩니다.
<!-- @os:end -->

<!-- @os:linux -->
> 컨테이너는 백그라운드에서 실행됩니다. `compose.yml` 파일이 있는 디렉터리에서 `podman compose down`(중지) 및 `podman compose up -d`(시작) 명령으로 관리할 수 있습니다. 계정과 설정은 `open_webui_data` 볼륨에 유지됩니다.
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openwebui-server-smoke-windows timeout=900 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$work = Join-Path (Get-Location) "openwebui"
$venv = Join-Path $work "openwebui-venv"
$ow = Join-Path $venv "Scripts\open-webui.exe"
if (-not (Test-Path $ow)) { throw "open-webui not found. Run openwebui-install-venv-windows first." }

# Fresh data dir so auth mode/config isn't polluted by previous runs
$dataDir = Join-Path $work "openwebui-data-ci"
if (Test-Path $dataDir) { Remove-Item -Recurse -Force $dataDir }
New-Item -ItemType Directory -Force -Path $dataDir | Out-Null

$env:DATA_DIR = $dataDir
$env:WEBUI_AUTH = "False" # Disable auth for CI
$env:ENABLE_PERSISTENT_CONFIG = "False" # Ensure environment-variable config applies for the run and isn't overridden by persistent settings

$logOut = Join-Path $work "openwebui-ci-out.log"
$logErr = Join-Path $work "openwebui-ci-err.log"
$p = Start-Process -FilePath $ow -ArgumentList "serve --port 8080" -NoNewWindow -PassThru -RedirectStandardOutput $logOut -RedirectStandardError $logErr
try {
  $ok = $false
  for ($i=0; $i -lt 90; $i++) {
    $health = curl.exe -s --max-time 2 http://127.0.0.1:8080/health
    if ($health) { $ok = $true; break }
    Start-Sleep -Seconds 1
  }
  if (-not $ok) { throw "Open WebUI not ready on http://127.0.0.1:8080" }
  Write-Host "OK: Open WebUI is responding on /health"
}
finally {
  if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end --> 
<!-- @os:end --> 

<!-- @os:linux -->
<!-- @test:id=openwebui-podman-server-smoke-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

export PODMAN_COMPOSE_PROVIDER="$(command -v podman-compose)"
export PODMAN_COMPOSE_WARNING_LOGS=false

cleanup() {
  podman compose -f compose.yml down >/dev/null 2>&1 || true
}
trap cleanup EXIT

# Clean up a stale container from a previous failed run.
podman rm -f open-webui >/dev/null 2>&1 || true

podman compose -f compose.yml up -d

health=""
for i in $(seq 1 180); do
  health="$(curl -fsS --max-time 2 http://127.0.0.1:8080/health || true)"
  if [ -n "$health" ]; then
    break
  fi
  sleep 1
done

if [ -z "$health" ]; then
  echo "Open WebUI did not become ready on http://127.0.0.1:8080/health"
  echo "Container status:"
  podman ps -a || true
  echo "Open WebUI logs:"
  podman logs --tail 200 open-webui || true
  exit 1
fi

echo "OK: Open WebUI container is responding on /health"

# Verify that the Open WebUI container can reach Lemonade through host networking.
podman exec open-webui sh -lc 'python -c "import json, urllib.request; data=json.load(urllib.request.urlopen(\"http://127.0.0.1:13305/api/v1/models\", timeout=10)); assert \"data\" in data; print(\"OK: Open WebUI container can reach Lemonade models endpoint\")"'
```
<!-- @test:end --> 
<!-- @os:end --> 

## Open WebUI를 Lemonade에 연결하기

이제 Lemonade가 `localhost:13305`에서, Open WebUI가 `localhost:8080`에서 모두 실행 중이므로, Open WebUI가 Lemonade의 모델을 사용할 수 있도록 두 서비스를 연결하겠습니다.

Open WebUI에서:

1. 오른쪽 상단의 **사용자 프로필 아이콘**을 클릭한 다음 **Settings**를 선택합니다.

   <p align="center">
     <img src="assets/open_settings.png" alt="Click the user profile icon" width="300"/>
   </p>

2. Settings 패널에서 왼쪽 하단의 **Admin Settings**를 클릭합니다.

   <p align="center">
     <img src="assets/click_admin_settings.png" alt="Select Admin Settings" width="450"/>
   </p>

3. Admin Settings 사이드바에서 **Connections**를 클릭합니다(또는 `http://localhost:8080/admin/settings/connections`로 직접 이동합니다).

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Admin Settings Connections page" width="600"/>
   </p>

4. **OpenAI API** 아래에서 새 연결을 추가합니다:
   - **Base URL:** `http://localhost:13305/api/v1`
   - **API Key:** `-` (로컬에서는 대시 하나면 됩니다)

   <p align="center">
     <img src="assets/connection_form.png" alt="Connection details for Lemonade server" width="400"/>
   </p>

5. **"Manage OpenAI API Connections"** 아래에서 `http://localhost:13305/api/v1`만 활성화되어 있는지 확인합니다. 다른 연결(예: 기본 OpenAI 연결)은 비활성화합니다.

   <p align="center">
     <img src="assets/admin_settings_connections.png" alt="Manage OpenAI API Connections with only Lemonade enabled" width="600"/>
   </p>

6. **Save**를 클릭합니다.

7. **(권장)** 로컬 LLM에서 Open WebUI가 원활하게 동작하도록 자동 생성 기능을 비활성화합니다. **Admin Settings → Settings → Interface**로 이동하여 다음 기능을 끕니다:
   - Title Generation
   - Follow Up Generation
   - Tags Generation

   <p align="center">
     <img src="assets/admin_settings.png" alt="Admin Settings Interface — disable Title, Follow Up, and Tags Generation" width="600"/>
   </p>

8. **Save**를 클릭한 다음 `http://localhost:8080`으로 돌아갑니다.
9. 모델 드롭다운을 클릭합니다 — Lemonade에서 다운로드한 모델이 표시되어야 합니다.

---

## 주요 활동

이제 모든 준비가 끝났습니다. 흥미로운 세 가지 작업을 살펴보겠습니다.

---

### 활동 1: 로컬 LLM과 채팅하기
<!-- @os:windows -->
<!-- @device:halo,stx,krk -->
1. 인터페이스 왼쪽 상단의 드롭다운 메뉴를 클릭합니다. 설치한 Lemonade 모델이 표시됩니다. 계속 진행할 모델을 선택합니다. (예: `Qwen3-4B-Hybrid`)

    <p align="center">
      <img src="assets/model_selection.png" alt="Model Selection" width="600"/>
    </p>

2. LLM에 메시지를 입력하고 전송을 클릭합니다(또는 Enter 키를 누릅니다). LLM이 메모리에 로드되는 데 몇 초 정도 걸린 후 응답이 스트리밍되어 표시됩니다.

    <p align="center">
      <img src="assets/sending_a_message.png" alt="Sending a message" width="37.5%"/>
      <img src="assets/llm_response.png" alt="LLM Response" width="50%"/>
    </p>
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
1. 인터페이스 왼쪽 상단의 드롭다운 메뉴를 클릭합니다. 설치한 Lemonade 모델이 표시됩니다. 계속 진행할 모델을 선택합니다. (예: `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. LLM에 메시지를 입력하고 전송을 클릭합니다(또는 Enter 키를 누릅니다). LLM이 메모리에 로드되는 데 몇 초 정도 걸린 후 응답이 스트리밍되어 표시됩니다.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>
<!-- @device:end -->    

3. 모델이 채팅에서 응답합니다.

4. 이때 시스템에서 `Task Manager`를 엽니다. 선택한 모델이 **Hybrid**인지 **NPU**인지에 따라 각각 **높은 GPU 또는 NPU 사용률**이 표시됩니다. 작업 관리자를 통해 모델이 로컬에서 실행되고 있음을 확인할 수 있습니다.

    <p align="center">
      <img src="assets/task_manager.png" alt="Task Manager GPU/NPU utilization" width="700"/>
    </p>
<!-- @os:end -->

<!-- @os:linux -->
1. 인터페이스 왼쪽 상단의 드롭다운 메뉴를 클릭합니다. 설치한 Lemonade 모델이 표시됩니다. 계속 진행할 모델을 선택합니다. (예: `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/linux_model_selection.png" alt="Model Selection" width="600"/>
   </p>

2. LLM에 메시지를 입력하고 전송을 클릭합니다(또는 Enter 키를 누릅니다). LLM이 메모리에 로드되는 데 몇 초 정도 걸린 후 응답이 스트리밍되어 표시됩니다.

   <p align="center">
     <img src="assets/linux_sending_a_message.png" alt="Sending a message" width="41.8%"/>
     <img src="assets/linux_llm_response.png" alt="LLM Response" width="46%"/>
   </p>

3. 모델이 채팅에서 응답합니다.
<!-- @os:end -->

이를 통해 Open WebUI가 OpenAI 호환 채팅 엔드포인트를 사용하여 Lemonade에 요청을 보낼 수 있음을 확인할 수 있습니다.

---

### 활동 2: 이미지 업로드 후 질문하기 (비전)

이 작업에는 이미지 입력을 지원하는 모델(비전 또는 멀티모달 모델)이 필요합니다.

1. 필터 아이콘을 클릭하고 "By Category"를 선택한 다음 **Vision** 섹션에서 모델을 선택합니다(예: `Qwen3.5-4B-GGUF`)

   <p align="center">
     <img src="assets/lemonade_vlms.png" alt="Lemonade VLM's" width="600"/>
   </p>

2. 메시지 상자의 **`+`** 버튼을 클릭하고 이미지를 업로드합니다
3. 실제 이미지 이해가 필요한 질문을 합니다: `Do you think this is a well-designed GUI?`

   <p align="center">
     <img src="assets/vlm_prompt.png" alt="VLM Prompt" width="43%"/>
     <img src="assets/vlm_response.png" alt="VLM Response" width="40%"/>
   </p>

4. 모델은 일반적인 텍스트가 아닌 이미지 내용을 기반으로 답변합니다.

이를 통해 Open WebUI가 백엔드(Lemonade)를 거쳐 비전 모델에 멀티모달 요청(텍스트 + 이미지)을 보낼 수 있음을 확인할 수 있습니다.

---

<!-- @os:windows -->
### 활동 3: 텍스트 프롬프트로 이미지 생성하기 (Stable Diffusion)

Stable Diffusion 모델은 텍스트 생성을 지원하지 않으며, Images API를 통해서만 이미지를 생성합니다.

#### 1단계: Open WebUI에서 이미지 생성 구성하기

1. Lemonade GUI(`http://localhost:13305`)에서 `SDXL-Turbo`(빠름) 또는 `SDXL-Base-1.0`(고품질)를 검색하여 다운로드합니다.
2. **Admin Settings → Images**(http://localhost:8080/admin/settings/images)로 이동합니다
3. 다음과 같이 설정합니다:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` 또는 `SDXL-Base-1.0`
4. 매개변수를 추가로 지정하려면 텍스트 필드에 JSON 형식으로 추가합니다. 예: `{ "steps": 4, "cfg_scale": 1 }`. 사용 가능한 매개변수는 [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html)에서 확인할 수 있습니다.

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. 저장합니다
#### 2단계: 모델에 이미지 생성 허용
이 단계는 모델에서 이미지 생성 기능을 활성화하도록 보장합니다.
1. **Admin Settings → Models**(http://localhost:8080/admin/settings/models)로 이동하여 모델을 선택합니다
2. `Image Generation`을 켭니다

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### 3단계: 채팅 화면에서 이미지 생성하기

1. `http://localhost:8080`의 채팅 화면으로 돌아갑니다.
2. 모델 드롭다운에서 **텍스트 생성 LLM**을 선택합니다(예: Qwen, Llama). 이는 채팅 모델 선택기이므로 **Stable Diffusion 모델을 선택하지 마세요**.
3. 메시지 입력 영역에서 **Integrations**를 클릭하고, **Image**를 켭니다.
4. 다음과 같은 프롬프트를 사용해 보세요: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. 이미지가 생성되어 채팅에 나타납니다.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

이는 Open WebUI가 "2단계" 워크플로를 조율할 수 있음을 보여줍니다:
  - LLM이 프롬프트를 다듬는 데 도움을 줍니다
  - 이미지는 Stable Diffusion을 사용하는 Lemonade의 Images 엔드포인트를 통해 생성됩니다
<!-- @os:end -->

<!-- @os:linux -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
### 활동 3: 텍스트 프롬프트로 이미지 생성하기(Stable Diffusion)

Stable Diffusion 모델은 텍스트 생성을 지원하지 않으며, Images API를 통해서만 이미지를 생성합니다.

#### 1단계: Open WebUI에서 이미지 생성 구성하기

1. Lemonade GUI(`http://localhost:13305`)에서 `SDXL-Turbo`(빠름) 또는 `SDXL-Base-1.0`(고품질)를 검색하여 다운로드합니다.
2. **Admin Settings → Images**(http://localhost:8080/admin/settings/images)로 이동합니다
3. 다음과 같이 설정합니다:
   - **Image Generation:** ON
   - **Image Generation Engine:** Default (OpenAI)
   - **OpenAI API Base URL:** `http://localhost:13305/api/v1`
   - **OpenAI API Key:** `-`
   - **Model:** `SDXL-Turbo` 또는 `SDXL-Base-1.0`
4. 매개변수를 추가로 지정하고 싶다면 텍스트 필드에 JSON 형식으로 추가하세요. 예: `{ "steps": 4, "cfg_scale": 1 }`. 사용 가능한 매개변수는 [Image Generation (Stable Diffusion CPP)](https://lemonade-server.ai/models.html)에서 확인하세요.

   <p align="center">
     <img src="assets/images_settings.png" alt="Open WebUI Image Generation settings" width="600"/>
   </p>

5. 저장


#### 2단계: 모델에 이미지 생성 허용
이 단계는 모델에서 이미지 생성 기능을 활성화하도록 보장합니다.
1. **Admin Settings → Models**(http://localhost:8080/admin/settings/models)로 이동하여 모델을 선택합니다
2. `Image Generation`을 켭니다

   <p align="center">
     <img src="assets/model_settings.png" alt="Model Settings" width="45%"/>
     <img src="assets/edit_model.png" alt="Edit Model" width="50%"/>
   </p>

#### 3단계: 채팅 화면에서 이미지 생성하기

1. `http://localhost:8080`의 채팅 화면으로 돌아갑니다.
2. 모델 드롭다운에서 **텍스트 생성 LLM**을 선택합니다(예: Qwen, Llama). 이는 채팅 모델 선택기이므로 **Stable Diffusion 모델을 선택하지 마세요**.
3. 메시지 입력 영역에서 **Integrations**를 클릭하고, **Image**를 켭니다.
4. 다음과 같은 프롬프트를 사용해 보세요: `A cinematic photo of heavy traffic at sunset, ultra detailed`.
5. 이미지가 생성되어 채팅에 나타납니다.

   <p align="center">
     <img src="assets/image_gen_prompt.png" alt="Image Generation" width="49%"/>
     <img src="assets/image_gen_response.png" alt="Generated image response" width="32.5%"/>
   </p>

이는 Open WebUI가 "2단계" 워크플로를 조율할 수 있음을 보여줍니다:
  - LLM이 프롬프트를 다듬는 데 도움을 줍니다
  - 이미지는 Stable Diffusion을 사용하는 Lemonade의 Images 엔드포인트를 통해 생성됩니다
<!-- @device:end -->
<!-- @os:end -->

---

## 문제 해결

### "Open WebUI에 모델이 표시되지 않습니다"
- 먼저 Lemonade를 확인하세요: 브라우저에서 `http://localhost:13305/api/v1/models`을 열어 모델이 나열되어 있고 다운로드되었는지 확인합니다
- 그다음 Open WebUI 연결을 확인하세요: `http://localhost:8080/admin/settings/connections`에서 **Admin Settings → Connections**로 이동하여 Base URL이 `http://localhost:13305/api/v1`인지 확인합니다

### "This model does not support chat completion" 오류 메시지
- 채팅 모델 드롭다운에서 이미지 모델(SDXL-Turbo / SDXL-Base-1.0)을 선택했습니다.
- **해결 방법**: 채팅용으로 LLM을 선택하고, 생성에는 Image 토글 + Images 설정을 사용하세요.
<p align="center">
  <img src="assets/model_not_supported_error.png" alt="This model does not support chat completion error message" width="600"/>
</p>

### 이미지 생성 오류/시간 초과
- 먼저 `SDXL-Turbo`로 시작하세요(빠르고 단계 수가 적음)
- 작동이 확인되면 품질을 위해 이미지 모델을 `SDXL-Base-1.0`으로 전환하세요

---

## 다음 단계

이제 여러분은 작동하는 **'로컬 AI 스택'**을 갖게 되었습니다. 표준 API를 통해 다양한 유형의 모델을 제어하는 단일 UI입니다.

완전히 새로운 워크플로를 여는 세 가지 확장 방법을 소개합니다:

### 1. Whisper를 이용한 음성-텍스트 변환

Whisper 모델을 사용하여 오디오를 텍스트로 변환한 다음, 이를 LLM에 입력하여 요약, 액션 아이템 정리, 또는 재작성을 시도해 보세요. 이는 회의록 및 음성 기반 어시스턴트의 기초가 됩니다.

### 2. Open WebUI 내에서 Python 코딩하기

Open WebUI에 내장된 코드 실행 환경을 사용하여 UI를 벗어나지 않고 Python 스니펫을 실행하고, 출력을 확인하고, 더 빠르게 반복 작업을 할 수 있습니다. [참고 자료](https://lemonade-server.ai/docs/server/apps/open-webui/#python-coding)

### 3. Open WebUI 내에서 HTML 렌더링하기

인터페이스에서 직접 HTML 출력을 렌더링합니다. 이는 빠른 프로토타입, 형식이 지정된 보고서, 대화형 스니펫을 만드는 데 놀라울 만큼 강력한 기능입니다. [참고 자료](https://lemonade-server.ai/docs/server/apps/open-webui/#html-rendering)

---

## 참고 자료

- [Open WebUI (GitHub)](https://github.com/open-webui/open-webui)
- [Lemonade (GitHub)](https://github.com/lemonade-sdk/lemonade)
- [Lemonade Server 문서](https://lemonade-server.ai/docs)
- [Lemonade Server CLI](https://lemonade-server.ai/docs/lemonade-cli/)
- [Lemonade ↔ Open WebUI 통합 가이드](https://lemonade-server.ai/docs/server/apps/open-webui)
- [Lemonade Server API 명세(엔드포인트)](https://lemonade-server.ai/docs/server/server_spec)
- [동영상 안내(Lemonade)](https://www.youtube.com/watch?v=mcf7dDybUco)
- [동영상 안내(Open WebUI + Lemonade)](https://www.youtube.com/watch?v=yZs-Yzl736E)

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