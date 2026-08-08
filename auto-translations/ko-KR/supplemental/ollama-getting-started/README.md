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

## 개요

Ollama는 대규모 언어 모델을 로컬에서 실행하기 위한 인기 있는 경량 도구입니다. 모델 다운로드, 양자화, 서빙을 간단한 명령줄 인터페이스와 데스크톱 앱 뒤에서 처리해주므로, 몇 분 만에 LLM과 대화를 시작할 수 있습니다.

이 플레이북에서는 Ollama를 설치하고, GPT-OSS 20B 모델을 가져온 후, 터미널과 데스크톱 앱을 통해 대화를 나누는 과정을 안내합니다.

## 배우게 될 내용

- 시스템에 Ollama를 설치하고 실행하는 방법
- GPT-OSS 20B 모델을 로컬에서 가져오고 실행하기
- CLI를 사용하여 모델과 대화하기
- REST API를 통해 프로그래밍 방식으로 모델 쿼리하기

## 메모리 구성 설정

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 소프트웨어 업데이트 확인
> **참고**: VS Code가 설치되어 있지 않다면 Ryzen AI Developer Center에서 설치할 수 있습니다.

<!-- @require:software-update -->
<!-- @device:end -->

## 소프트웨어 필수 구성 요소 설치

<!-- @require:driver -->

### Ollama 설치

<!-- @os:windows -->

1. [ollama.com/download](https://ollama.com/download)에서 설치 프로그램을 다운로드합니다.
2. `.exe` 설치 프로그램을 실행하고 안내에 따릅니다.
3. 설치가 완료되면 Ollama는 백그라운드 서비스로 실행되며 터미널, 데스크톱 앱, 시스템 트레이에서 접근할 수 있습니다.

터미널을 열고 다음을 실행하여 설치를 확인합니다:

```powershell
ollama --version
```

<!-- @test:id=ollama-version-windows timeout=60 hidden=True -->
```powershell
ollama --version
```
<!-- @test:end --> 

설치된 버전 번호가 콘솔에 출력되는 것을 확인할 수 있습니다.
<!-- @os:end -->

<!-- @os:linux -->

공식 설치 스크립트를 실행합니다:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

설치를 확인합니다:

```bash
ollama --version
```

<!-- @test:id=ollama-version-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end --> 

설치된 버전 번호가 콘솔에 출력되는 것을 확인할 수 있습니다.
<!-- @os:end -->

## 첫 모델 가져오기

Ollama는 컨테이너 이미지와 유사한 레지스트리를 통해 모델을 관리합니다. GPT-OSS 20B를 다운로드하려면:

```bash
ollama pull gpt-oss:20b
```

이렇게 하면 모델 가중치가 로컬 머신에 다운로드됩니다(약 12GB). 다운로드는 한 번만 이루어지며, 이후 실행 시에는 디스크에서 모델을 로드합니다.

다음 명령으로 모델이 사용 가능한지 확인할 수 있습니다:

```bash
ollama list
```

출력에서 `gpt-oss:20b`와 함께 크기 및 마지막 수정 날짜를 확인할 수 있습니다.

<!-- @os:windows -->
<!-- @test:id=ollama-list-gpt-oss-20b-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"
$list = (ollama list | Out-String)
if (-not $list) { throw "ollama list returned no output" }
if ($list -notmatch 'gpt-oss:20b') { throw "Model gpt-oss:20b is not present in ollama list. Please download it before running this test." }
Write-Host "OK: gpt-oss:20b is present in ollama list"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=ollama-list-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
p=""
started_here="0"

cleanup() {
  if [ "$started_here" = "1" ] && [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

wait_for_ollama_api() {
  local attempts="${1:-120}"
  local out=""
  for i in $(seq 1 "$attempts"); do
    out="$(curl -s --max-time 2 http://127.0.0.1:11434/api/tags || true)"
    if [ -n "$out" ]; then
      echo "$out"
      return 0
    fi
    sleep 1
  done
  return 1
}

tags_json="$(wait_for_ollama_api 5 || true)"
if [ -z "$tags_json" ]; then
  ollama serve >/tmp/ollama-list-test.log 2>&1 &
  p=$!
  started_here="1"
  tags_json="$(wait_for_ollama_api 120 || true)"
fi
if [ -z "$tags_json" ]; then
  echo "Ollama API not ready on http://127.0.0.1:11434"
  exit 1
fi
echo "OK: Ollama API is responding on http://127.0.0.1:11434"

list="$(ollama list)"
if [ -z "$list" ]; then
  echo "ollama list returned no output"
  exit 1
fi
echo "$list" | grep -q 'gpt-oss:20b' || {
  echo "Model gpt-oss:20b is not present in ollama list. Please download it before running this test."
  exit 1
}
echo "OK: gpt-oss:20b is present in ollama list"
```
<!-- @test:end --> 
<!-- @os:end -->

### 모델 이름 지정

Ollama 모델 이름은 `name:tag` 형식을 따릅니다. 태그는 일반적으로 매개변수 개수 또는 양자화 변형을 나타냅니다. 모델 관리에 유용한 몇 가지 명령은 다음과 같습니다:

| 명령 | 설명 |
|---------|-------------|
| `ollama list` | 다운로드한 모든 모델 표시 |
| `ollama pull <model>` | 실행하지 않고 모델 다운로드 |
| `ollama rm <model>` | 디스크 공간 확보를 위해 모델 제거 |
| `ollama show <model>` | 모델 메타데이터 및 매개변수 표시 |

## 터미널에서 채팅하기

명령줄에서 직접 대화형 채팅 세션을 시작합니다:

```bash
ollama run gpt-oss:20b
```

Ollama가 모델을 메모리에 로드하고 프롬프트로 진입합니다. 무언가를 물어보세요:

```
>>> What is the capital of France and why is it historically significant?
```

모델이 터미널에서 직접 토큰 단위로 응답을 스트리밍합니다. 세션을 종료하려면 `/bye`를 입력하거나 `Ctrl+D`를 누르세요.

> **팁**: 처음 실행할 때는 모델을 메모리에 로드하는 데 몇 초 정도 걸립니다. 동일한 세션 내의 이후 프롬프트는 모델이 이미 로드되어 있으므로 훨씬 빠르게 응답합니다.

<!-- @os:windows -->
## 데스크톱 앱에서 채팅하기

Ollama에는 모델과 상호작용하기 위한 깔끔한 채팅 인터페이스를 제공하는 데스크톱 애플리케이션도 함께 제공됩니다.

시작 메뉴에서 **Ollama**를 열거나 시스템 트레이의 Ollama 아이콘을 클릭한 후 **Open Ollama**를 선택합니다.

앱이 열리면:

1. 사이드바에서 **New Chat**을 클릭합니다.
2. 채팅 입력 영역 우측 하단의 모델 드롭다운에서 **gpt-oss:20b**를 선택합니다.
3. 메시지를 입력하고 Enter를 눌러 채팅을 시작합니다.

<p align="center">
  <img src="assets/ollama_app.png" alt="Ollama desktop app chatting with gpt-oss:20b" width="600"/>
</p>

데스크톱 앱은 사이드바에 대화 기록을 보관하여 이전 채팅을 쉽게 다시 확인할 수 있습니다.
<!-- @os:end -->

## REST API 사용하기

설치 후 Ollama는 백그라운드 서비스로 실행되며 `http://localhost:11434`에서 REST API를 노출하여 자체 애플리케이션과 스크립트에 모델을 통합하는 데 사용할 수 있습니다.

<!-- @os:windows -->
<!-- @test:id=ollama-smoke-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$p = $null
$startedHere = $false
$tmpShow = $null
$tmpGenerate = $null
$tmpChat = $null
$venv = "$PWD\ollama-env-ci"
$pythonSmoke = "$PWD\ollama_python_smoke.py" 

function Wait-OllamaApi {
  param( [int]$MaxAttempts = 120 )
  $resp = $null
  for ($i = 0; $i -lt $MaxAttempts; $i++) {
    $resp = curl.exe -s --max-time 2 http://127.0.0.1:11434/api/tags
    if ($LASTEXITCODE -eq 0 -and $resp) { return $resp }
    Start-Sleep -Seconds 1
  }
  return $null
}

try {
  # If Ollama API is not already up, start it.
  $tagsJson = Wait-OllamaApi -MaxAttempts 5
  if (-not $tagsJson) {
    $p = Start-Process -FilePath "ollama" -ArgumentList "serve" -NoNewWindow -PassThru
    $startedHere = $true
    $tagsJson = Wait-OllamaApi -MaxAttempts 120
  }
  if (-not $tagsJson) { throw "Ollama API not ready on http://127.0.0.1:11434" }
  Write-Host "OK: Ollama API is responding on http://127.0.0.1:11434"

  # /api/tags must include gpt-oss:20b
  $tags = $tagsJson | ConvertFrom-Json
  $model = $tags.models | Where-Object { $_.name -eq "gpt-oss:20b" } | Select-Object -First 1
  if (-not $model) { throw "Model gpt-oss:20b is not present in /api/tags. Please download it before running this test." }
  Write-Host "OK: gpt-oss:20b is present in /api/tags"

  # /api/show should return model metadata
  $showBody = @{ name = "gpt-oss:20b" } | ConvertTo-Json
  $tmpShow = Join-Path $env:TEMP "ollama-show-body.json"
  [System.IO.File]::WriteAllText($tmpShow, $showBody, [System.Text.UTF8Encoding]::new($false))
  $showOut = curl.exe -sS --fail-with-body --max-time 60 http://127.0.0.1:11434/api/show `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpShow"
  if (-not $showOut) { throw "Empty response from /api/show" }
  $showJson = $showOut | ConvertFrom-Json
  if (-not $showJson.details) { throw "/api/show did not return model details for gpt-oss:20b" }
  Write-Host "OK: /api/show returned model details"

  # CLI inference smoke
  $cliOut = & ollama run gpt-oss:20b "Reply with exactly OK"
  if (-not $cliOut) { throw "ollama run returned empty output" }
  $cliText = ($cliOut | Out-String).Trim()
  if ($cliText -notmatch '(^|\s)OK(\s|$)') { throw "ollama run did not return OK. Output was: $cliText" }
  Write-Host "OK: ollama run inference works"

  # /api/generate smoke
  $generateBody = @{
    model  = "gpt-oss:20b"
    prompt = "Reply with exactly OK"
    stream = $false
  } | ConvertTo-Json
  $tmpGenerate = Join-Path $env:TEMP "ollama-generate-body.json"
  [System.IO.File]::WriteAllText($tmpGenerate, $generateBody, [System.Text.UTF8Encoding]::new($false))
  $generateOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:11434/api/generate `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpGenerate"
  if (-not $generateOut) { throw "Empty response from /api/generate" }
  $generateJson = $generateOut | ConvertFrom-Json
  if (-not $generateJson.response) { throw "/api/generate did not return a response field" }
  if ($generateJson.response.Trim() -ne "OK") { throw "/api/generate expected exactly OK but got: $($generateJson.response)" }
  Write-Host "OK: /api/generate works"

  # /api/chat smoke
  $chatBody = @{
    model = "gpt-oss:20b"
    messages = @(
      @{
        role = "user"
        content = "Reply with exactly OK"
      }
    )
    stream = $false
  } | ConvertTo-Json -Depth 5
  $tmpChat = Join-Path $env:TEMP "ollama-chat-body.json"
  [System.IO.File]::WriteAllText($tmpChat, $chatBody, [System.Text.UTF8Encoding]::new($false))
  $chatOut = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:11434/api/chat `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpChat"
  if (-not $chatOut) { throw "Empty response from /api/chat" }
  $chatJson = $chatOut | ConvertFrom-Json
  $chatText = $chatJson.message.content
  if (-not $chatText) { throw "/api/chat did not return message.content" }
  if ($chatText.Trim() -ne "OK") { throw "/api/chat expected exactly OK but got: $chatText" }
  Write-Host "OK: /api/chat works"

  # Python requests smoke
  if (Test-Path $venv) { Remove-Item -Recurse -Force $venv }
  python -m venv $venv
  $py = Join-Path $venv "Scripts\python.exe"
  & $py -m pip install --upgrade pip
  & $py -m pip install requests
@'
import requests
response = requests.post(
    "http://127.0.0.1:11434/api/generate",
    json={
        "model": "gpt-oss:20b",
        "prompt": "Reply with exactly: OK",
        "stream": False,
    },
    timeout=300,
)
response.raise_for_status()
text = response.json()["response"].strip()
if text != "OK":
    raise SystemExit(f"Expected exactly OK, got: {text}")
print("OK: Python requests example works")
'@ | Set-Content -Path $pythonSmoke -Encoding UTF8
  & $py $pythonSmoke
}

finally {
  Remove-Item $tmpShow, $tmpGenerate, $tmpChat, $pythonSmoke -Force -ErrorAction SilentlyContinue
  Remove-Item $venv -Recurse -Force -ErrorAction SilentlyContinue
  if ($startedHere) {
    if ($p -and -not $p.HasExited) {
      Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
    }
  }
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=ollama-smoke-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail
p=""
started_here="0"
venv="./ollama-env-ci"
python_smoke="./ollama_python_smoke.py" 

cleanup() {
  rm -f "$python_smoke"
  rm -rf "$venv"
  if [ "$started_here" = "1" ] && [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

wait_for_ollama_api() {
  local attempts="${1:-120}"
  local out=""
  for i in $(seq 1 "$attempts"); do
    out="$(curl -s --max-time 2 http://127.0.0.1:11434/api/tags || true)"
    if [ -n "$out" ]; then
      echo "$out"
      return 0
    fi
    sleep 1
  done
  return 1
}

tags_json="$(wait_for_ollama_api 5 || true)"
if [ -z "$tags_json" ]; then
  ollama serve >/tmp/ollama-test.log 2>&1 &
  p=$!
  started_here="1"
  tags_json="$(wait_for_ollama_api 120 || true)"
fi
if [ -z "$tags_json" ]; then
  echo "Ollama API not ready on http://127.0.0.1:11434"
  exit 1
fi
echo "OK: Ollama API is responding on http://127.0.0.1:11434"

export TAGS_JSON="$tags_json"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["TAGS_JSON"])
models = data.get("models", [])
for item in models:
    if item.get("name") == "gpt-oss:20b":
        print("OK: gpt-oss:20b is present in /api/tags")
        sys.exit(0)
print("Model gpt-oss:20b is not present in /api/tags. Please download it before running this test.")
sys.exit(1)
PY

show_out="$(curl -s --max-time 60 http://127.0.0.1:11434/api/show \
  -H "Content-Type: application/json" \
  -d '{"name":"gpt-oss:20b"}' || true)"
if [ -z "$show_out" ]; then
  echo "Empty response from /api/show"
  exit 1
fi
export SHOW_OUT="$show_out"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["SHOW_OUT"])
if not data.get("details"):
    print("/api/show did not return model details for gpt-oss:20b")
    sys.exit(1)
print("OK: /api/show returned model details")
PY

cli_out="$(ollama run gpt-oss:20b "Reply with exactly OK" || true)"
if [ -z "$cli_out" ]; then
  echo "ollama run returned empty output"
  exit 1
fi
export CLI_OUT="$cli_out"
python3 - <<'PY'
import os
import sys
text = os.environ["CLI_OUT"].strip()
if "OK" not in text.split():
    print(f"ollama run did not return OK. Output was: {text}")
    sys.exit(1)
print("OK: ollama run inference works")
PY

generate_out="$(curl -s --max-time 300 http://127.0.0.1:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-oss:20b","prompt":"Reply with exactly OK","stream":false}' || true)"
if [ -z "$generate_out" ]; then
  echo "Empty response from /api/generate"
  exit 1
fi
export GENERATE_OUT="$generate_out"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["GENERATE_OUT"])
text = data.get("response", "")
if not text:
    print("/api/generate did not return a response field")
    sys.exit(1)
if text.strip() != "OK":
    print(f"/api/generate expected exactly OK but got: {text}")
    sys.exit(1)
print("OK: /api/generate works")
PY

chat_out="$(curl -s --max-time 300 http://127.0.0.1:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-oss:20b","messages":[{"role":"user","content":"Reply with exactly OK"}],"stream":false}' || true)"
if [ -z "$chat_out" ]; then
  echo "Empty response from /api/chat"
  exit 1
fi
export CHAT_OUT="$chat_out"
python3 - <<'PY'
import json
import os
import sys
data = json.loads(os.environ["CHAT_OUT"])
msg = data.get("message", {})
text = msg.get("content", "")
if not text:
    print("/api/chat did not return message.content")
    sys.exit(1)
if text.strip() != "OK":
    print(f"/api/chat expected exactly OK but got: {text}")
    sys.exit(1)
print("OK: /api/chat works")
PY

rm -rf "$venv"
python3 -m venv "$venv"
py="$venv/bin/python"
"$py" -m pip install --upgrade pip
"$py" -m pip install requests
cat > "$python_smoke" <<'PY'
import requests
response = requests.post(
    "http://127.0.0.1:11434/api/generate",
    json={
        "model": "gpt-oss:20b",
        "prompt": "Reply with exactly: OK",
        "stream": False,
    },
    timeout=300,
)
response.raise_for_status()
text = response.json()["response"].strip()
if text != "OK":
    raise SystemExit(f"Expected exactly OK, got: {text}")
print("OK: Python requests example works")
PY
"$py" "$python_smoke"
```
<!-- @test:end --> 
<!-- @os:end -->

### 터미널에서 응답 생성하기

<!-- @os:linux -->
```bash
curl http://localhost:11434/api/generate -d '{"model": "gpt-oss:20b", "prompt": "Explain GPU acceleration in two sentences.", "stream": false}'
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
curl.exe http://localhost:11434/api/generate -d '{"model": "gpt-oss:20b", "prompt": "Explain GPU acceleration in two sentences.", "stream": false}'
```
<!-- @os:end -->

응답은 모델의 출력을 `response` 필드에 담은 JSON 객체입니다.


### Python 예제
이제 Ollama API를 프로그래밍 방식으로 호출할 수 있으므로, Python에서 호출해 보겠습니다.

#### 터미널에서 가상 환경 생성하기

<!-- @os:linux -->
```bash
sudo apt install -y python3-venv
python3 -m venv ollama-env
source ollama-env/bin/activate
pip install requests
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
python -m venv ollama-env
ollama-env\Scripts\activate
pip install requests
```
<!-- @os:end -->
#### Python 파일 생성하기
동일한 디렉터리에서 VS Code나 다른 편집기를 사용하여 .py 파일을 만들고 다음 코드를 복사하여 붙여넣습니다. 그런 다음 활성화된 환경에서 `python your_file_name.py`로 파일을 실행합니다.

```python
import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "gpt-oss:20b",
        "prompt": "Write a haiku about local AI inference.",
        "stream": False,
    },
)

print(response.json()["response"])
```

### 주요 API 엔드포인트

| 엔드포인트 | 메서드 | 목적 |
|----------|--------|---------|
| `/api/generate` | POST | 단일 턴 텍스트 생성 |
| `/api/chat` | POST | 메시지 기록을 포함한 다중 턴 대화 |
| `/api/tags` | GET | 사용 가능한 모델 목록 표시 |
| `/api/show` | POST | 모델 세부 정보 표시 |
| `/api/pull` | POST | 레지스트리에서 모델 가져오기 |

전체 API 참조는 [Ollama API 문서](https://github.com/ollama/ollama/blob/main/docs/api.md)를 참조하세요.
## 다음 단계

- **다양한 모델 사용해 보기**: [Ollama 모델 라이브러리](https://ollama.com/library)를 둘러보고 소형 코딩 어시스턴트부터 대형 추론 모델까지 수백 개의 사용 가능한 모델을 살펴보세요.
- **사용자 지정 모델 만들기**: [Modelfile](https://github.com/ollama/ollama/blob/main/docs/modelfile.md)을 사용하여 맞춤형 경험을 위한 사용자 지정 시스템 프롬프트, temperature 및 기타 매개변수를 설정하세요.
- **API로 빌드하기**: [Python](https://github.com/ollama/ollama-python) 또는 [JavaScript](https://github.com/ollama/ollama-js) 클라이언트 라이브러리를 사용하여 Ollama를 애플리케이션에 통합하세요.
- **프런트엔드에 연결하기**: Ollama를 [Open WebUI](https://github.com/open-webui/open-webui)와 같은 도구와 함께 사용하여 검색, 페르소나, 문서 업로드 기능을 갖춘 다양한 기능의 채팅 인터페이스를 구성하세요.

자세한 내용은 [Ollama 문서](https://github.com/ollama/ollama/blob/main/README.md)를 참조하세요.