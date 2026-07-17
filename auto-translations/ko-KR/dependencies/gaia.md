<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### GAIA

GAIA는 Ryzen AI 가속을 통해 AMD 하드웨어에서 로컬로 실행되는 AI 에이전트를 구축하기 위한 AMD의 오픈 소스 프레임워크입니다.

#### GAIA 설치

<!-- @device:halo_box -->
<!-- @os:windows -->
1. Windows에서 원하는 디렉터리에 터미널을 열고 다음 명령어를 따라 venv를 생성합니다.
<!-- @test:id=create-venv-halo-box-windows timeout=60 -->
```bash
python -m venv gaia-env --system-site-packages
gaia-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="gaia-env\Scripts\activate" -->

2. 그런 다음, `pip`을 사용하여 **Gaia**를 설치합니다.
<!-- @test:id=pip-install-amd-gaia-halo-box-windows timeout=300 setup=activate-venv -->
```bash
pip install amd-gaia
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
1. Linux에서 원하는 디렉터리에 터미널을 열고 다음 명령어를 따라 venv를 생성합니다.
<!-- @test:id=create-venv-halo-box-linux timeout=60 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv gaia-env --system-site-packages
source gaia-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source gaia-env/bin/activate" -->

2. 그런 다음, `pip`을 사용하여 **Gaia**를 설치합니다.
<!-- @test:id=pip-install-amd-gaia-halo-box-linux timeout=300 setup=activate-venv -->
```bash
pip install amd-gaia
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
1. Windows에서 원하는 디렉터리에 터미널을 열고 다음 명령어를 따라 venv를 생성합니다.
<!-- @test:id=create-venv-windows timeout=60 -->
```bash
python -m venv gaia-env
gaia-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="gaia-env\Scripts\activate" -->

2. 그런 다음, `pip`을 사용하여 **Gaia**를 설치합니다.
<!-- @test:id=pip-install-amd-gaia-windows timeout=300 setup=activate-venv -->
```bash
pip install amd-gaia
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
1. Linux에서 원하는 디렉터리에 터미널을 열고 다음 명령어를 따라 venv를 생성합니다.
<!-- @test:id=create-venv-linux timeout=60 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv gaia-env
source gaia-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source gaia-env/bin/activate" -->

2. 그런 다음, `pip`을 사용하여 **Gaia**를 설치합니다.
<!-- @test:id=pip-install-amd-gaia-linux timeout=300 setup=activate-venv -->
```bash
pip install amd-gaia
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

3. GAIA 초기화

설치 후, `gaia init`을 실행하여 Lemonade Server를 설정하고 모델을 다운로드합니다:

```bash
gaia init
```

이 명령은 Lemonade Server를 설치하고, 기본 모델을 다운로드하며, 설정을 확인합니다.

<!-- @os:linux -->
<!-- @test:id=verify-lspci-linux timeout=120 hidden=True -->
```bash
set -euo pipefail

if ! command -v lspci >/dev/null 2>&1; then
echo "lspci not found. Installing pciutils..."
sudo apt update
sudo apt install -y pciutils
fi

command -v lspci >/dev/null 2>&1
lspci | head -n 5 || true
echo "OK: lspci is available"
```
<!-- @test:end --> 
<!-- @os:end --> 


<!-- @os:windows --> 
<!-- @test:id=gaia-version-windows timeout=60 hidden=True setup=activate-venv -->
```bash
lemonade --version
gaia --version
python -c "import gaia; print('OK')"
```
<!-- @test:end --> 
<!-- @os:end --> 

<!-- @os:linux --> 
<!-- @test:id=gaia-version-linux timeout=60 hidden=True setup=activate-venv -->
```bash
lemonade --version
gaia --version
python3 -c "import gaia; print('OK')"
```
<!-- @test:end --> 
<!-- @os:end --> 


<!-- @os:windows -->
<!-- @test:id=gaia-lemonade-health-windows timeout=300 hidden=True -->
```powershell
$health = $null
for ($i=0; $i -lt 120; $i++) {
  $health = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/health
  if ($health) { break }
  Start-Sleep -Seconds 1
}
if (-not $health) { throw "Lemonade server not ready on http://127.0.0.1:13305/api/v1/health" }
Write-Host "OK: Lemonade server health endpoint responded"
```
<!-- @test:end --> 
<!-- @os:end --> 

<!-- @os:linux -->
<!-- @test:id=gaia-lemonade-health-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

health=""
for i in $(seq 1 120); do
  health="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/health || true)"
  if [ -n "$health" ]; then
    break
  fi
  sleep 1
done

if [ -z "$health" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305/api/v1/health"
  exit 1
fi

echo "OK: Lemonade server health endpoint responded"

```
<!-- @test:end --> 
<!-- @os:end --> 

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-qwen-windows timeout=1200 hidden=True -->
```powershell
# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade(robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "Qwen3-Coder-30B-A3B-Instruct-GGUF" } | Select-Object -First 1
if (-not $entry) { throw "Model Qwen3-Coder-30B-A3B-Instruct-GGUF is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model Qwen3-Coder-30B-A3B-Instruct-GGUF is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: Qwen3-Coder-30B-A3B-Instruct-GGUF model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "Qwen3-Coder-30B-A3B-Instruct-GGUF"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 300
} | ConvertTo-Json -Depth 5
$out = curl.exe -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions -H "Content-Type: application/json" -d $body
if (-not $out) { throw "Empty response from Lemonade chat/completions" }
Write-Host "OK: Lemonade chat/completions works"
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-chat-qwen-linux timeout=1200 hidden=True -->
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
    if item.get("id") == "Qwen3-Coder-30B-A3B-Instruct-GGUF":
        entry = item
        break

if entry is None:
    print("Model Qwen3-Coder-30B-A3B-Instruct-GGUF is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model Qwen3-Coder-30B-A3B-Instruct-GGUF is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: Qwen3-Coder-30B-A3B-Instruct-GGUF model is downloaded in Lemonade")
PY

body='{
  "model": "Qwen3-Coder-30B-A3B-Instruct-GGUF",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 300
}'

out="$(curl -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

#### 설치 확인

GAIA v0.16.2 이상이 설치되어 있는지 확인합니다:

```bash
gaia --version
```

> **중요**: GAIA를 사용하기 전에 Lemonade Server가 실행 중인지 확인하십시오. GAIA는 Lemonade Server를 수동으로 시작해야 합니다.

자세한 내용은 [GAIA 문서](https://amd-gaia.ai)를 참조하십시오.