<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Overview

Developers spend a lot of time on small recurring loops: reviewing labeled
pull requests, answering GitHub comments, triaging new issues, turning Slack
threads into standup notes or incident follow-ups, and tracking release or
research signals. Each loop is familiar, but it still requires judgment:
gather the right context, decide what matters, and post a clear update where
the team already works.

[OpenHands automations](https://docs.openhands.dev/openhands/usage/automations/overview)
turn those loops into scheduled or event-triggered agent conversations: runs
where an AI software agent can read context, call tools, and produce an update.
The shared automation templates in the OpenHands extensions catalog follow
this pattern for GitHub pull request review, repository monitoring, Linear
issue triage, incident retrospectives, Slack standup digests, and research
briefs: an automation wakes up, uses configured integrations such as GitHub or
Slack to fetch context, reasons over that context with a large language model
(LLM), and writes back a result.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) is the local control
plane for building and testing those automations. In this playbook it runs an
OpenHands Agent Server, the backend process that executes agent conversations,
and connects the agent to external services such as GitHub and Slack.

To keep the workflow on your AMD system, the agent talks to a local model
served by Lemonade Server. Lemonade exposes that model through an
OpenAI-compatible API, so Agent Canvas can configure it like a remote
OpenAI-style endpoint while the model, prompt, and workflow context stay local.

In this playbook, you will build one concrete automation: a scheduled
GitHub-to-Slack development digest. It uses GitHub to inspect recent repository
activity, Slack to post the digest, Agent Canvas API calls to configure and
test the automation, and Lemonade to run the LLM locally.

![Architecture diagram showing GitHub MCP, OpenHands automation, Lemonade Server, and Slack MCP](assets/00-architecture-overview.png)

## What You'll Learn

- How to start Lemonade Server and verify a local model answers chat requests
- How to launch Agent Canvas and point its Agent Server at a local LLM
- How to install GitHub and Slack Model Context Protocol (MCP) servers through
  the Agent Server API
- How to create and dispatch a scheduled OpenHands automation that posts a
  development digest to Slack
- How to troubleshoot the most common local-model and automation failures

## Core Concepts

| Concept | What it is | Where it fits in this playbook |
| --- | --- | --- |
| Lemonade Server | A local LLM serving platform built for AMD hardware that exposes an OpenAI-compatible API. Your data never leaves your machine. | Runs the model that powers the agent. |
| OpenHands Agent Server | The backend process that executes OpenHands agent conversations. | Hosts the agent, its LLM profile, and its MCP servers. |
| Agent Canvas | The local control plane for OpenHands that runs Agent Server and a UI for inspecting agent runs. | Launches the backends and provides the API you call. |
| MCP server | A Model Context Protocol server that gives an agent tools for an external service such as GitHub or Slack. | Lets the agent read GitHub and write to Slack. |
| OpenHands automation | A scheduled or event-triggered agent conversation that fetches context, reasons over it, and writes a result somewhere. | The GitHub-to-Slack digest you build here. |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Coding-agent workflows benefit from a larger model and context window. Use at
> least 32 GB of system memory, and prefer 64 GB or more for larger GGUF models.
<!-- @device:end -->

## Setting the Memory Configuration

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Check for Software Updates

<!-- @require:software-update -->
<!-- @device:end -->

## Prerequisites

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- @os:end -->

You need:

- Lemonade Server installed by following the standard
  [Lemonade installation guide](https://lemonade-server.ai/docs/guide/install/).

<!-- @os:linux -->
- Node.js 22.12 or later and `npm`, used to install the published Agent Canvas
  CLI and run MCP servers with `npx`.
- `uv`, the Python package manager Agent Canvas uses to build the Agent
  Server environment. If it is not already installed, install it from the
  [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).
- A recent published `@openhands/agent-canvas` package with
  schema-driven agent settings, `LLMSummarizingCondenserSettings.max_tokens`,
  and LLM `custom_tokenizer` support.
- The Python `transformers` package available in the Agent Server environment.
  It is required for chat-template token counting when `custom_tokenizer` is
  set.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  installed and running. On Windows, the Agent Canvas stack runs from the
  published Docker image, which bundles Node.js, `uv`, `transformers`, and the
  `@openhands/agent-canvas` package, so you do not install those on the host.
<!-- @os:end -->

- A GitHub token with read access to the repository you want summarized.
- A Slack bot token (`xoxb-...`) with `chat:write` and channel read access.
- A Slack team ID (`T...`).
- A Slack channel ID (`C...`) where the digest should be posted.

Invite the Slack app to the target channel before testing the automation.

## Variables Used in This Playbook

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

These two variables are used by the verification commands below. The model,
tokenizer, and other LLM settings are entered directly in the Agent Canvas UI
in later steps, so their literal values are shown inline where you need them.

The following values are entered into the Agent Canvas UI in later steps. Set
them here so you can copy them in:

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

Use an explicit `owner/repo` value for `GITHUB_REPO_FILTER`. Broad organization
wildcards can return too much MCP context for local models.

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. Start Lemonade Server

Start the model from the Lemonade CLI:

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

> **Choose a model that fits your hardware.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) is a strong model for this workflow but needs a large memory pool. If your device has limited memory or GPU VRAM, pick a smaller GGUF model from the Lemonade model library and use that model ID (and its matching tokenizer) throughout this playbook.

> **Note:** The first `lemonade run` downloads the model if it isn't already present, which can take a while depending on the model size and your connection.

Lemonade exposes an OpenAI-compatible API at:

```text
http://127.0.0.1:13305/api/v1
```

Optional: if Agent Canvas or the automation runner is not on the same machine,
publish the Lemonade endpoint through a secure tunnel and use the HTTPS URL as
the LLM base URL. [ngrok](https://ngrok.com/) exposes a local port to the
internet over a secure HTTPS URL; it requires a free ngrok account, and you
replace `YOUR_NGROK_DOMAIN.ngrok-free.dev` with your own reserved domain:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Verify the Local Model

Confirm Lemonade can serve the selected model:

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Then send a small chat request:

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

Then send a small chat request:

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

If this returns a `choices` array, Lemonade is ready for Agent Canvas.

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

## 3. Start Agent Canvas

<!-- @os:linux -->
Install the published Agent Canvas package and start the full stack:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

If the global npm install fails with a permissions error, see the npm
permissions troubleshooting entry below.

By default, Agent Canvas starts on `http://localhost:8000`. Open that URL in
your browser. The port is not special—if 8000 is already in use, pass any free
port with `--port` (or `-p`). The default local backend should show as healthy
on the home screen.

> **Note:** The first launch builds the Agent Server's `uv`-managed Python
> environment, so it can take a few minutes before the backend reports healthy.

The `agent-canvas` command starts the agent server, the automation backend, and
the web frontend together. You only need this one command to run OpenHands
locally. The rest of this playbook configures everything through the Agent
Canvas UI in your browser.
<!-- @os:end -->

<!-- @os:windows -->
On Windows, run the published Agent Canvas container image with Docker Desktop.
The image bundles the Agent Server, automation backend, and web frontend, so
you do not install Node.js, `uv`, or the CLI on the host.

First, create the config and workspace folders the container mounts:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Pull the published image (about 6 GB; it is public, so no login is required):

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

Then start the stack:

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

Open `http://localhost:8000/canvas` in your browser. If port 8000 is already in
use, map a different host port, for example `-p 8080:8000`, and open
`http://localhost:8080/canvas` instead.

> **Note:** The first launch builds the Agent Server environment inside the
> container, so it can take a few minutes before the backend reports healthy.

The `.openhands` mount persists your LLM profile, MCP servers, and automations
across container restarts. The rest of this playbook configures everything
through the Agent Canvas UI in your browser at `http://localhost:8000/canvas`.
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

# Verify the image is present (pre-provisioned on the runner). Pulling over a
# non-interactive CI session fails on the Docker credential helper, so CI does
# not pull; provision the image on the runner beforehand with:
#   docker pull ghcr.io/openhands/agent-canvas:1.14.0
$imgId = docker images -q $image
if (-not $imgId) { throw "Image $image is not present. Pre-provision it on this runner: docker pull $image" }
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

## 4. Configure the Local LLM in the UI

On first launch, Agent Canvas opens an onboarding flow. In that flow:

1. Keep **OpenHands** selected as the agent and click **Next**.
2. On **Set up your LLM**, select **Advanced**.
3. Keep **Authentication** set to **API key**.
4. Set **Custom Model** to `openai/Qwen3.6-35B-A3B-GGUF`.
5. Set **Base URL** to `http://127.0.0.1:13305/api/v1`.
6. For **API Key**, enter any non-empty placeholder such as `lemonade-local`.
   Lemonade does not require a real key, but the OpenHands client needs a value
   to send.

<!-- @os:windows -->
> **Windows (Docker):** the Agent Server runs inside the container, so set
> **Base URL** to `http://host.docker.internal:13305/api/v1` instead of
> `http://127.0.0.1:13305/api/v1`. From inside the container, `127.0.0.1` is the
> container itself; `host.docker.internal` reaches Lemonade running on the
> Windows host, and Docker Desktop provides that hostname automatically.
<!-- @os:end -->

The connection fields should look like this. The API key field is masked by
the UI.

![Agent Canvas first-use LLM Advanced settings with the Lemonade model and local base URL](assets/01-llm-advanced-settings.png)

Then select **All** and set the extra local-model fields:

1. Scroll to **Custom Tokenizer** and set it to `Qwen/Qwen3.6-35B-A3B`.
2. Scroll to **LiteLLM Extra Body** and set it to
   `{"enable_thinking": true}`.
3. Click **Next**.

![Agent Canvas first-use LLM All tab with the Qwen custom tokenizer](assets/02-llm-all-tokenizer-settings.png)

![Agent Canvas first-use LLM All tab with LiteLLM extra body configured](assets/03-llm-all-extra-body-settings.png)

The LLM settings should show:

| Field | Value |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

The `openai/` prefix tells LiteLLM to use OpenAI-compatible request formatting
against the Lemonade endpoint. The custom tokenizer is the original Hugging
Face tokenizer for the GGUF model; it lets OpenHands count the same
chat-template tokens that the local model server sees. The current first-use
LLM form does not show condenser settings. If your Agent Canvas build exposes
condenser settings later under **Settings > LLM**, use `llm_summarizing` and
set max tokens below the Lemonade context window, such as `56000`.

## 5. Install GitHub and Slack MCP Servers

In the Agent Canvas UI, open **Customize** (or **Settings > MCP**) to add the
MCP servers that give the agent tools for GitHub and Slack. Token values are
sent only to your local Agent Server and are persisted as encrypted settings.

<!-- @os:windows -->
> **Windows (Docker):** the `npx` MCP server commands below run inside the
> container, which already includes Node.js, so nothing extra is installed on
> the host. Because `.openhands` is mounted, the MCP servers and their tokens
> persist across container restarts.
<!-- @os:end -->

### GitHub MCP server

Add a new MCP server with these settings:

| Field | Value |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = your GitHub token |

Use a GitHub token with read access to the repository you want summarized.

### Slack MCP server

Add a second MCP server with these settings:

| Field | Value |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = your digest channel ID |

Set `SLACK_CHANNEL_IDS` to the digest channel ID (the same value as
`SLACK_DIGEST_CHANNEL`) so the agent does not need to page through every Slack
channel.

After adding both servers, use the **Test** button on each one to confirm it
connects and advertises tools. The GitHub server should list GitHub tools, and
the Slack server should list Slack tools.

![Agent Canvas MCP page with GitHub and Slack servers installed](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. Create the Digest Automation

In the Agent Canvas UI, open the **Automations** page and create a new
automation:

1. Choose **Create automation** and select the **Prompt preset** type.
2. Set the **Name** to `GitHub Development Digest to Slack`.
3. Set the **Prompt** to the following text, replacing the repository and
   channel placeholders with your values:

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

4. Set the **Trigger** to **Cron** with the schedule `0 9 * * 1-5` (9 AM on
   weekdays) and set the **Timezone** to your timezone, for example
   `America/New_York`.
5. Set the **Timeout** to `900` seconds.
6. Save the automation.

The automation detail page shows the new automation with its cron trigger and
the generated prompt-preset entrypoint.

![Agent Canvas automation detail after creation](assets/05-automation-created.png)

## 7. Test the Automation

From the automation detail page in the Agent Canvas UI:

1. Click **Run now** (or **Dispatch**) to run the automation once immediately.
2. Watch the run list on the same page. The latest run should transition to
   `COMPLETED`.
3. Open your target Slack channel. It should contain the generated digest.

You do not need to wait for the cron schedule to fire—**Run now** triggers a
run on demand so you can confirm the prompt, MCP connections, and Slack posting
all work before relying on the schedule.

![Agent Canvas automation run completed successfully](assets/06-automation-run-completed.png)

![Slack channel showing the generated OpenHands digest](assets/07-slackbot-message.png)

## Troubleshooting

<!-- @os:windows -->
- **Docker port 8000 is already in use:** map a different host port, for example
  `docker run ... -p 8080:8000 ...`, and open `http://localhost:8080/canvas`.
- **`docker pull` fails with a credential error** (for example, "A specified
  logon session does not exist"): run the pull from an interactive Windows
  session, or pre-pull the image. The image is public, so no `docker login` is
  required.
- **The UI loads but the backend is unhealthy:** the first launch builds the
  Agent Server environment inside the container. Wait a minute and refresh, then
  check `docker logs <container>` for progress.
- **Agent Canvas cannot reach Lemonade from the container:** set the LLM
  **Base URL** to `http://host.docker.internal:13305/api/v1` (not `127.0.0.1`),
  and confirm Lemonade is running on the Windows host.
<!-- @os:end -->

- **Lemonade is down:** restart it with the
  `lemonade run "${LEMONADE_MODEL}"` command in step 1, then re-run the health
  check.
- **`npm install -g` fails with a permissions error:** on Linux or WSL,
  configure a user-owned global npm directory, add it to your shell startup
  file, then install Agent Canvas again:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  If you use `zsh`, add the same `export PATH=...` line to `~/.zshrc` instead
  of `~/.bashrc`.
- **Agent Canvas rejects the LLM settings after setting `custom_tokenizer`:**
  install `transformers` in the Agent Server Python environment, restart Agent
  Canvas if needed, and retry saving the LLM settings. OpenHands requires
  Transformers to load the tokenizer chat template when `custom_tokenizer` is
  set.
- **Agent Canvas cannot reach Lemonade:** verify
  `curl -fsS "${LEMONADE_BASE_URL}/health"` and confirm the base URL entered in
  the first-use LLM form or **Settings > LLM** matches the running local
  endpoint or HTTPS tunnel.
- **The LLM settings did not save:** make sure you clicked **Next** after
  entering the values. Reopen **Settings > LLM** to confirm the values
  persisted.
- **GitHub MCP cannot see private repositories:** confirm the GitHub token has
  read access to the target repository and that the MCP **Test** button in
  **Customize** advertises GitHub tools.
- **Slack can read channels but cannot post:** invite the Slack app to the
  target channel and confirm the bot has `chat:write`.
- **The automation lists too many Slack channels:** use a Slack channel ID and
  set `SLACK_CHANNEL_IDS` on the Slack MCP server in **Customize**.
- **The automation run fails or exceeds context:** confirm Lemonade was started
  with `ctx_size=65536`, confirm the OpenHands LLM has `custom_tokenizer` set,
  and use an explicit repository with GitHub result sets capped to 3 to 5
  items. If your Agent Canvas build exposes condenser settings, set condenser
  max tokens below the Lemonade context window.

## Next Steps

- Add a weekly release-only digest.
- Add a GitHub event-triggered automation for faster PR or push alerts.
- Route the same digest into Notion, Linear, or another MCP-backed tool.

## Resources

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Lemonade Server documentation](https://lemonade-server.ai/docs)
- [OpenHands extensions repository](https://github.com/OpenHands/extensions)
- [Model Context Protocol servers](https://github.com/modelcontextprotocol/servers)
- [Slack MCP package](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

<!-- @test:id=lemonade-unload timeout=60 hidden=True -->
```bash
# CI cleanup: unload the model so the GPU pool is free
lemonade unload || true
```
<!-- @test:end -->
