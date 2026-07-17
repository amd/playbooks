<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Overview

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> This playbook requires a minimum of **32GB** of system memory.
<!-- @device:end -->

n8n is a workflow automation platform that lets you connect apps and services using a visual node-based editor.

This playbook teaches you how to set up an AI-powered financial news summarizer that scrapes the AP News business section, extracts key headlines, and uses a local LLM running on your system to generate an investor-focused summary.

## What You'll Learn

- How to install and launch n8n
- Importing and configuring a pre-built workflow
- Connecting to Lemonade using the native n8n integration
- Understanding workflow nodes and data flow

## What is Lemonade?

[Lemonade](https://lemonade-server.ai) is a local LLM serving platform built for AMD hardware. It provides an OpenAI-compatible API that runs entirely on your machine—your data never leaves your device.

In this playbook, we use Lemonade to serve a local LLM that n8n connects to for AI-powered tasks. 

n8n includes a **native Lemonade node** (`Lemonade Chat Model`) that provides a first-class integration - no need for manual configuration. This makes connecting your local LLM to automation workflows straightforward.

## Setting the Memory Configuration

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Check for Software Updates

<!-- @require:software-update -->
<!-- @device:end -->

## Installing Software Prerequisites
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

## Installing n8n
<!-- @os:windows -->
Install n8n globally using npm.

> **Note**: You may see some npm warnings. This is expected.

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
> **Tip**: Windows users may need to modify their PowerShell Execution Policy (e.g.
> setting it to RemoteSigned or Unrestricted) before running some Powershell commands.
<!-- @os:end -->


<!-- @os:windows -->
> **PATH Issue**: If `n8n --version` says command not found, ensure your npm global bin directory is on the user `PATH`. The usual installation path is at `C:\Users\<username>\AppData\Roaming\npm`. 
> Add this to the user path (Edit the system environment variables > Environment Variables > Edit User Path) and reload the terminal. 

<!-- @os:end -->

<!-- @os:linux -->
We are now going to use Podman service to containerize our n8n installation.

Please download the following into a directory of your choice: [compose.yml](assets/compose.yml)

In that directory, run the following command:
```bash
podman compose up -d
```

This should install n8n and write to a persistent storage.

Launch n8n by typing `localhost:5678` into your browser address bar.
<!-- @os:end -->

<!-- @os:windows -->
## Launching n8n

Start n8n from the terminal:

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
n8n starts a local web server. Press `'o'` or Open your browser to `http://localhost:5678` to access the editor.
<!-- @os:end -->


> **Tip**: Keep the terminal window open while using n8n. Closing it might stop the server.

## Launching Lemonade

Lemonade is the local server that will run a model and connect to n8n. 

<!-- @os:linux -->
Open the Lemonade GUI by clicking the Lemonade Icon in the taskbar. You can browse models, backends, and load the pre-installed models from here.
<!-- @os:end -->

<!-- @os:windows -->
Open the Lemonade GUI by clicking the Lemonade Icon. Right click the tray icon to open the app. Then, you can add models, backends, and load the pre-installed models.
<!-- @os:end -->

>**Tip**: Once running, the Lemonade GUI is also accessible at http://localhost:13305

Alternatively, you can open a terminal and run `lemonade list` to see what models are installed. Then, run:

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


## Setting Up the Workflow

### Step 1: Sign Up or Log In to n8n

When you first open n8n, you'll be prompted to create an account or log in:

1. Open `http://localhost:5678` in your browser
2. Create a new local account with your email, or log in if you already have one
3. Once logged in, you'll see the n8n dashboard

> **Tip**: If locked out of your account, try `n8n user-management:reset`

### Step 2: Import the Workflow

We've provided a pre-built workflow that you can import directly:

1. Download the following workflow file: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Click **Start from Scratch** to open the workflow editor. Alternatively, click the + Button in the top left, and then **Add workflow**.
3. Click the **...** menu (three dots) in the top right bar and select **Import from file**
4. Select the downloaded `financial-news-workflow.json` file
5. The workflow will appear on the canvas


### Step 3: Understanding the Workflow

The imported workflow contains 9 connected nodes:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Node | Purpose |
|------|---------|
| **When clicking 'Execute workflow'** | Manual trigger to start the workflow |
| **Fetch Financial News Webpage** | HTTP GET request to `https://apnews.com/business` |
| **Delay to Ensure Page Load** | Wait node to ensure page content is fully loaded |
| **Extract News Headlines & Text** | HTML node that extracts headlines, editor's picks, top stories, and regional news using CSS selectors |
| **Clean Extracted News Data** | Set node that combines all extracted data into a single text field |
| **AI Financial News Summarizer** | AI Agent that processes the news with a financial analyst system prompt |
| **Lemonade Chat Model** | Connects to your local Lemonade server running the LLM |
| **Structured Output Parser** | Formats the AI output as structured JSON |
| **Convert to File** | Converts the summary to a downloadable file |

### Step 4: Configure Lemonade Credentials

Before running the workflow, you need to connect it to your local Lemonade server:

1. Double click the **Lemonade Chat Model** node in n8n
2. In the dropdown menu **Credential to connect with** select **Create New Credential**
3. Enter the values in the table below and click save.
4. Choose the relevant model that you have loaded in Lemonade Server.

  | Field | Value |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Note**: Before testing, run `lemonade status` in a terminal to confirm that the Lemonade server is running.
<!-- @device:halo_box -->
> This workflow uses GPT-OSS-120B and it is pre-installed in Lemonade. You can change this to other loaded models in the Lemonade Chat Model node settings.
<!-- @device:end -->

### Step 5: Test the Workflow

1. Ensure Lemonade is running with a model loaded
2. Click **Execute workflow** at the bottom center of the canvas
3. Watch each node execute from left to right—they turn green when complete
4. Double click the **AI Financial News Summarizer** node to see the generated summary in the bottom pane.
5. Double click the **Convert to File** node to download the corresponding text file in the bottom pane.

## Understanding the AI Agent

The AI Financial News Summarizer uses a system prompt designed for financial analysis:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

The agent receives the cleaned news data and outputs a structured summary with market sentiment.

### Saving Your Workflow

Click the workflow name at the top and rename it if desired. Workflows auto-save as you work.

## Next Steps

- **Schedule automation**: Replace Manual Trigger with a **Schedule Trigger** to run daily
- **Send notifications**: Add a **Discord**, **Slack**, or **Email** node to receive summaries
- **Try different models**: Change the model in the Lemonade Chat Model node to experiment with different LLMs
- **Customize extraction**: Modify the HTML Extract node's CSS selectors to target different news sections
- **Try different backends**: n8n also supports [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio, and other local LLM backends

### Explore n8n Templates

n8n has hundreds of pre-built workflow templates. Browse the official template library at:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Search for "AI", "LLM", or "automation" to find workflows you can import and customize.

For more information, check out the [n8n Documentation](https://docs.n8n.io/).

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
