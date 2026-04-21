<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### GAIA

GAIA is AMD's open-source framework for building AI agents that run locally on AMD hardware with Ryzen AI acceleration.

#### Installing GAIA

<!-- @os:windows -->

1. Open PowerShell
2. Create a virtual environment and install GAIA:
```cmd
uv venv .venv
.\.venv\Scripts\Activate.ps1
uv pip install amd-gaia
```

<!-- @os:end -->

<!-- @os:linux -->

1. Open a terminal
2. Create a virtual environment and install GAIA:
```bash
uv venv .venv
source .venv/bin/activate
uv pip install amd-gaia
```

<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-uv-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

if (Get-Command uv -ErrorAction SilentlyContinue) {
Write-Host "uv already available on PATH"
uv --version
exit 0
}

Write-Host "uv not found. Installing..."
powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"

$uvBin = Join-Path $env:USERPROFILE ".local\bin"
if (Test-Path $uvBin) {
$env:PATH = "$uvBin;$env:PATH"
}

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
throw "uv install completed but uv is still not on PATH"
}

uv --version
where.exe uv
Write-Host "OK: uv installed and available on PATH"
```
<!-- @test:end --> 
<!-- @os:end --> 

<!-- @os:linux -->
<!-- @test:id=install-uv-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

if command -v uv >/dev/null 2>&1; then
echo "uv already available on PATH"
uv --version
exit 0
fi

echo "uv not found. Installing..."
curl -LsSf https://astral.sh/uv/install.sh | sh

export PATH="$HOME/.local/bin:$PATH"

command -v uv >/dev/null 2>&1
uv --version
which uv
echo "OK: uv installed and available on PATH"

```
<!-- @test:end --> 
<!-- @os:end --> 


<!-- @os:windows -->
<!-- @test:id=python-env-check-windows timeout=30 hidden=True -->
```powershell
python --version
where.exe python
```
<!-- @test:end --> 
<!-- @os:end --> 

<!-- @os:linux -->
<!-- @test:id=python-env-check-linux timeout=30 hidden=True -->
```bash
set -euo pipefail
python3 --version
which python3
```
<!-- @test:end --> 
<!-- @os:end --> 


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
lspci | head -n 5
echo "OK: lspci is available"
```
<!-- @test:end --> 
<!-- @os:end --> 


<!-- @os:windows --> 
<!-- @test:id=gaia-create-venv-install-windows timeout=600 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"
$uvBin = Join-Path $env:USERPROFILE ".local\bin"
if (Test-Path $uvBin) { $env:PATH = "$uvBin;$env:PATH" }
uv venv .venv
.\.venv\Scripts\Activate.ps1
uv pip install amd-gaia
gaia --version
python -c "import gaia; print('OK')"
```
<!-- @test:end --> 
<!-- @os:end --> 

<!-- @os:linux --> 
<!-- @test:id=gaia-create-venv-install-linux timeout=600 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
uv venv .venv
source .venv/bin/activate
uv pip install amd-gaia
gaia --version
python3 -c "import gaia; print('OK')"
```
<!-- @test:end --> 
<!-- @os:end --> 


#### Initializing GAIA

After installation, run `gaia init` to set up Lemonade Server and download models:

```
gaia init
```

This installs Lemonade Server, downloads the default models, and verifies the setup.

<!-- @test:id=gaia-lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end --> 

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
  max_tokens = 32
} | ConvertTo-Json -Depth 5
$out = curl.exe -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions -H "Content-Type: application/json" -d $body
if (-not $out) { throw "Empty response from Lemonade chat/completions" }
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
  "max_tokens": 32
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

#### Verifying Installation

Verify that GAIA v0.16.2 or later is installed:

```
gaia --version
```

Then run a quick test to confirm GAIA is working:

```
gaia chat
```

Type a message and press Enter. Type `quit` to exit.

> **Important**: Make sure Lemonade Server is running before using GAIA. GAIA requires Lemonade Server to be started manually.

For more information, see the [GAIA documentation](https://amd-gaia.ai).
