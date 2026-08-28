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

[OpenHands](https://github.com/All-Hands-AI/OpenHands) is an AI software agent
that can write code, run commands, browse the web, and edit files in a real
workspace. Instead of copying suggestions out of a chat window, you point the
agent at a project folder and let it do the work: implement a feature, fix a
bug, write tests, or explain a codebase.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) is the recommended
browser UI for running OpenHands. A single `agent-canvas` command starts the
agent server, the automation backend, and the web frontend together, so you can
drive a conversation with the agent from your browser.

To keep everything on your AMD system, the agent talks to a local model served
by Lemonade Server. Lemonade exposes that model through an OpenAI-compatible
API, so Agent Canvas can configure it like any other OpenAI-style endpoint
while the model, your code, and the conversation context all stay on your
machine.

In this playbook, you will start a local model, launch Agent Canvas, point it
at that model, and run your first coding task against a real project folder.

## What You'll Learn

- How to start Lemonade Server and confirm a local model answers chat requests
- How to install and launch Agent Canvas from the npm package
- How to configure Agent Canvas to use a local Lemonade model as the LLM
- How to start an OpenHands conversation and watch the agent edit files and run
  commands in a workspace
- How to review what the agent changed and steer it with follow-up messages

## Core Concepts

| Concept | What it is | Where it fits in this playbook |
| --- | --- | --- |
| Lemonade Server | A local LLM serving platform built for AMD hardware that exposes an OpenAI-compatible API. Your data never leaves your machine. | Runs the model that powers the agent. |
| OpenHands | An AI software agent that reads and edits files, runs shell commands, and browses the web inside a workspace. | The agent you drive from the chat. |
| Agent Canvas | The browser UI and backend that runs OpenHands conversations and shows tool calls and file changes. | Launches the stack and hosts your conversation. |
| Workspace | The project folder the agent is allowed to read and modify. | The target of the agent's edits and commands. |

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

- Lemonade Server installed and able to serve the model below.

<!-- @os:linux -->
- Node.js 22.12 or later and `npm` (used by the `agent-canvas` CLI).
- `uv`, the Python package manager that Agent Canvas uses to manage the agent
  server environment. If your system does not already have it, install it from
  the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/)
  before launching Agent Canvas.
<!-- @os:end -->

<!-- @os:windows -->
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/),
  installed and running. On Windows, the Agent Canvas stack runs from the
  published Docker image, which bundles Node.js, `uv`, and the
  `@openhands/agent-canvas` package, so you do not install those on the host.
<!-- @os:end -->

- A project folder to work in. This can be any local git repository or code
  directory you want the agent to work on.

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

## 1. Start Lemonade Server

Start the model from the Lemonade CLI:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **Choose a model that fits your hardware.** `Qwen3.6-35B-A3B-GGUF` (~20 GB) is a strong coding model but needs a large memory pool. If your device has limited memory or GPU VRAM, pick a smaller GGUF model from the Lemonade model library instead and use that model ID throughout this playbook.

> **Note:** The first `lemonade run` downloads the model if it isn't already present, which can take a while depending on the model size and your connection.

Lemonade exposes an OpenAI-compatible API at:

```text
http://127.0.0.1:13305/api/v1
```

## 2. Verify the Local Model

Confirm Lemonade can serve the selected model:

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

Then send a small chat request:

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

## 3. Install and Launch Agent Canvas

<!-- @os:linux -->
Install the published Agent Canvas package globally:

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

Then start the full stack from a terminal:

```bash
agent-canvas
```

By default, Agent Canvas starts on `http://localhost:8000`. Open that URL in
your browser. The port is not special — if 8000 is already in use, pass any
free port with `--port` (or `-p`) when you launch Agent Canvas:

```bash
agent-canvas --port 3000
```

Then open `http://localhost:3000` instead. The default local backend should show
as healthy on the home screen.

The `agent-canvas` command starts the agent server, the automation backend, and
the web frontend together. You only need this one command to run OpenHands
locally.

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
On Windows, run the published Agent Canvas container image with Docker Desktop.
The image bundles the Agent Server, automation backend, and web frontend, so you
do not install Node.js, `uv`, or the CLI on the host.

First, create the config and workspace folders the container mounts:

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

Pull the published image (it is public, so no login is required):

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

> **Note:** The first launch initializes the Agent Server inside the container,
> so it can take a minute or two before the backend reports healthy.

The `.openhands` mount persists your LLM profile and settings across container
restarts. The rest of this playbook configures everything through the Agent
Canvas UI in your browser.

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

## 4. Configure the Local LLM

On first launch, Agent Canvas opens an onboarding flow. In that flow:

1. Keep **OpenHands** selected as the agent and click **Next**.
2. On **Set up your LLM**, select **Advanced**.
3. Keep **Authentication** set to **API key**.
4. Set **Custom Model** to `openai/Qwen3.6-35B-A3B-GGUF`.
5. Set **Base URL** to `http://127.0.0.1:13305/api/v1`.
   <!-- @os:windows -->
   > On Windows the stack runs in a container, which cannot reach the host at
   > `127.0.0.1`. Use `http://host.docker.internal:13305/api/v1` instead so the
   > containerized agent can reach Lemonade running on the Windows host.
   <!-- @os:end -->
6. For **API Key**, enter any non-empty placeholder such as `lemonade-local`.
   Lemonade does not require a real key, but the OpenHands client needs a value
   to send.
7. Click **Next**.

The completed Advanced settings should look like this. The API key field is
masked by the UI.

![Agent Canvas first-use LLM Advanced settings with the Lemonade model and local base URL](assets/01-llm-advanced-settings.png)

Agent Canvas saves these values as an LLM profile. If your version asks you to
name that profile, use a no-space name such as `lemonade-local`. If you change
models later, open **Settings > LLM** and update the same Advanced fields. You
can switch saved profiles from the chat input with the `/model` command.

## 5. Open a Workspace

The agent can only read and modify files inside a workspace you choose. Before
starting a task, point Agent Canvas at your project folder:

1. From the home screen, choose **Open Workspace**.
2. Select the folder that contains your project (for example, a git repository
   you want the agent to work on).
3. Start a new conversation in that workspace.

Everything the agent does—reading files, running commands, editing code—is
scoped to that workspace.

![Agent Canvas home after onboarding](assets/02-agent-canvas-home.png)

## 6. Run Your First Coding Task

With the workspace open and the local LLM selected, type a concrete task into
the chat. A good first task is small and verifiable, for example:

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

Watch the conversation timeline. OpenHands will:

- Read the workspace to understand the layout.
- Create `hello.py` with the requested function and test block.
- Optionally run `python3 hello.py` to verify the output.
- Report what it did and any command output in the chat.

You should see the new file appear in the workspace, and the agent's final
message should describe the change it made. This is the payoff moment: the
agent wrote and ran real code in your project folder.

## 7. Review and Steer the Agent

After the agent finishes a step, review its work before accepting the next one:

- **File changes**: use the workspace file browser or the agent's diff view to
  see exactly what was added, changed, or deleted.
- **Command output**: expand any command the agent ran to see stdout, stderr,
  and the exit code.
- **Follow-ups**: if the result is not what you wanted, reply in the same
  conversation with a correction. The agent keeps the prior context and
  iterates on the same files.

For example, if the test did not print the expected greeting, reply:

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

The agent will re-read the file, run the command, diagnose the issue, and edit
the file again—all in the same conversation.

## Troubleshooting

<!-- @os:linux -->
- **`agent-canvas` is not on PATH:** reinstall with
  `npm install -g @openhands/agent-canvas` and confirm the npm global binary
  directory is on your PATH before `agent-canvas` can be launched from a new
  terminal.
- **`npm install -g` fails with a permissions error:** configure a user-owned
  global npm directory, then reopen the terminal and install Agent Canvas again.

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **`uv` is missing:** install it from
  [the uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).
  Agent Canvas uses `uv` to manage the agent server Python environment.
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` or `docker run` fails to connect:** make sure Docker Desktop
  is running (its whale icon is in the system tray) and that the engine has
  finished starting. `docker version` should print both a Client and a Server
  section.
- **The container starts but the backend never becomes healthy:** the first
  launch initializes the Agent Server inside the container; give it a minute or
  two, then check `docker logs <container>` for errors.
- **The container cannot reach Lemonade:** the container reaches the host via
  `host.docker.internal`. Confirm Lemonade is serving on the Windows host with
  `lemonade status`, and use `http://host.docker.internal:13305/api/v1` as the
  Base URL when configuring the LLM.
<!-- @os:end -->

- **The UI loads but the backend shows unhealthy:** wait a minute or two for the
  agent server to finish starting, then refresh. If it stays unhealthy, restart
  the stack and check the logs for errors.
- **Lemonade chat requests fail with a connection error:** confirm
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` succeeds and that
  Lemonade is still serving the model with `lemonade status`.
- **The agent errors with a context-length or token-limit message:** start a
  fresh conversation so the agent does not carry an oversized history. If it
  keeps happening, restart Lemonade with a larger `ctx_size` than the default
  65536 (for example `ctx_size=131072`), memory permitting.
- **The agent produces low-quality or incomplete edits:** switch to a larger
  model in Lemonade, or give the agent a smaller, more concrete task and let it
  finish before asking for the next change.

## Next Steps

- Try a larger task in the same workspace, such as adding a unit test file or
  fixing a known bug, and review the agent's diff before keeping the change.
- Connect an MCP server such as GitHub or Slack under **Customize** so the
  agent can read issues or post updates while it works.
- Save several LLM profiles (a fast small model and a stronger large model) and
  switch between them with `/model` mid-conversation.
- Move on to [OpenHands automations](https://docs.openhands.dev/openhands/usage/automations/overview) to
  turn recurring development loops into scheduled or event-triggered agent runs.

## Resources

- [OpenHands documentation](https://docs.openhands.dev/)
- [Agent Canvas overview](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Agent Canvas setup](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM profiles and model configuration](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Lemonade Server documentation](https://lemonade-server.ai/docs)

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
