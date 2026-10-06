<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **机器翻译。**本页面由英文自动翻译，未经人工审核。其中可能包含错误，某些说明、命令、下载内容、产品可用性或其他内容可能因语言或地区而异。如内容存在任何不一致或差异，应以英文原版 playbook 为准。
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the AMD Playbooks site.
> GitHub renders the Markdown content, but not the device, OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## 概述

开发者将大量时间花费在小而反复出现的循环工作上：审查带标签的拉取请求、回复 GitHub 评论、梳理新问题、把 Slack 讨论串整理成站会纪要或事件跟进，以及跟踪发布或研究信号。
每一种循环都很熟悉,但仍需要判断力：收集正确的上下文、决定哪些内容重要,并在团队已经使用的地方发布清晰的更新。

[OpenHands automations](https://docs.openhands.dev/openhands/usage/automations/overview) 将这些循环转变为按计划或事件触发的智能体对话：在这些运行中，AI 软件智能体可以读取上下文、调用工具并生成更新。
OpenHands 扩展目录中共享的自动化模板遵循这一模式，涵盖 GitHub 拉取请求审查、仓库监控、Linear 问题分类、事件复盘、Slack 站会摘要和研究简报：一个自动化任务被唤醒，使用配置好的集成（如 GitHub 或 Slack）获取上下文，通过大语言模型（LLM）对该上下文进行推理，并写回结果。

[Agent Canvas](https://github.com/OpenHands/agent-canvas) 是用于构建和测试这些自动化的本地控制平面。
在本实操指南中，它运行一个 OpenHands Agent Server（执行智能体对话的后端进程），并将智能体连接到 GitHub 和 Slack 等外部服务。

为了让整个工作流保留在你的 AMD 系统上，智能体会与由 Lemonade Server 提供的本地模型通信。
Lemonade 通过兼容 OpenAI 的 API 暴露该模型，因此 Agent Canvas 可以像配置远程 OpenAI 风格的端点一样配置它，而模型、提示词和工作流上下文都保留在本地。

在本实操指南中，你将构建一个具体的自动化任务：一个按计划运行的 GitHub 到 Slack 的开发摘要。
它使用 GitHub 检查最近的仓库活动，使用 Slack 发布摘要，使用 Agent Canvas API 调用来配置和测试该自动化任务，并使用 Lemonade 在本地运行 LLM。

![显示 GitHub MCP、OpenHands automation、Lemonade Server 和 Slack MCP 的架构图](assets/00-architecture-overview.png)

## 你将学到什么

- 如何启动 Lemonade Server 并验证本地模型能够响应聊天请求
- 如何启动 Agent Canvas，并将其 Agent Server 指向本地 LLM
- 如何通过 Agent Server API 安装 GitHub 和 Slack 的模型上下文协议（MCP）服务器
- 如何创建并调度一个 OpenHands 自动化任务，将开发摘要发布到 Slack
- 如何排查最常见的本地模型和自动化故障

## 核心概念

| 概念 | 是什么 | 在本实操指南中的作用 |
| --- | --- | --- |
| Lemonade Server | 一个专为 AMD 硬件构建的本地 LLM 服务平台，暴露兼容 OpenAI 的 API。你的数据永远不会离开你的机器。 | 运行为智能体提供支持的模型。 |
| OpenHands Agent Server | 执行 OpenHands 智能体对话的后端进程。 | 承载智能体、其 LLM 配置文件以及其 MCP 服务器。 |
| Agent Canvas | OpenHands 的本地控制平面，运行 Agent Server 以及用于检查智能体运行情况的 UI。 | 启动后端并提供你所调用的 API。 |
| MCP server | 一个模型上下文协议服务器，为智能体提供访问外部服务（如 GitHub 或 Slack）的工具。 | 让智能体能够读取 GitHub 并写入 Slack。 |
| OpenHands automation | 一个按计划或事件触发的智能体对话，获取上下文、对其进行推理，并将结果写入某处。 | 你在此构建的 GitHub 到 Slack 摘要任务。 |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> 编码智能体工作流受益于更大的模型和上下文窗口。
> 请使用至少 32 GB 的系统内存，对于更大的 GGUF 模型，建议使用 64 GB 或更多。
<!-- @device:end -->

## 设置内存配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 检查软件更新

<!-- @require:software-update -->
<!-- @device:end -->

## 前提条件

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:uv,agent-canvas,lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- On Windows the Agent Canvas stack runs from the Docker image (which bundles
     Node.js, uv and agent-canvas), so only the Lemonade model is needed here. -->
<!-- @prereq:lemonade-models-qwen3-35b-a3b -->
<!-- @os:end -->

你需要：

- 按照标准的 [Lemonade installation guide](https://lemonade-server.ai/docs/guide/install/) 安装 Lemonade Server。

<!-- @os:linux -->
- Node.js 22.12 或更高版本以及 `npm`，用于安装已发布的 Agent Canvas CLI，并通过 `npx` 运行 MCP 服务器。
- `uv`，Agent Canvas 用于构建 Agent Server 环境的 Python 包管理器。如果尚未安装，请从 [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/) 进行安装。
- 一个最新发布的 `@openhands/agent-canvas` 包，具备基于模式（schema）驱动的智能体设置、`LLMSummarizingCondenserSettings.max_tokens`，以及 LLM `custom_tokenizer` 支持。
- Agent Server 环境中可用的 Python `transformers` 包。当设置了 `custom_tokenizer` 时，进行聊天模板 token 计数需要该包。
<!-- @os:end -->

<!-- @os:windows -->
- 已安装并正在运行的 [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/)。在 Windows 上，Agent Canvas 技术栈通过已发布的 Docker 镜像运行，该镜像捆绑了 Node.js、`uv`、`transformers` 以及 `@openhands/agent-canvas` 包，因此你无需在宿主机上安装这些内容。
<!-- @os:end -->

- 一个对你希望总结的仓库具有读取权限的 GitHub 令牌。
- 一个具有 `chat:write` 权限和频道读取权限的 Slack 机器人令牌（`xoxb-...`）。
- 一个 Slack 团队 ID（`T...`）。
- 一个用于发布摘要的 Slack 频道 ID（`C...`）。

在测试自动化任务之前，请先将 Slack 应用邀请到目标频道。
## 本指南中使用的变量

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

以下验证命令会使用这两个变量。
模型、分词器以及其他 LLM 设置将在后续步骤中直接输入到 Agent Canvas 界面中，因此在需要用到它们的地方会以字面值的形式内联显示。

以下值将在后续步骤中输入到 Agent Canvas 界面中。
请在此处设置好，以便复制使用：

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

请为 `GITHUB_REPO_FILTER` 使用明确的 `owner/repo` 值。
过于宽泛的组织通配符可能会为本地模型返回过多的 MCP 上下文。

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

## 1. 启动 Lemonade Server

通过 Lemonade CLI 启动模型：

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

> **选择适合你硬件的模型。** `Qwen3.6-35B-A3B-GGUF`（约 20 GB）是适用于此工作流的强力模型，但需要较大的内存池。
> 如果你的设备内存或 GPU 显存有限，请从 Lemonade 模型库中选择一个较小的 GGUF 模型，并在本指南中始终使用该模型 ID（及与之匹配的分词器）。

> **注意：** 首次运行 `lemonade run` 时，如果模型尚未存在，会先下载模型，根据模型大小和你的网络连接情况，这可能需要一些时间。

Lemonade 在以下地址公开了一个兼容 OpenAI 的 API：

```text
http://127.0.0.1:13305/api/v1
```

可选：如果 Agent Canvas 或自动化运行程序不在同一台机器上，可以通过安全隧道将 Lemonade 端点发布出来，并使用其 HTTPS URL 作为 LLM 基础 URL。
[ngrok](https://ngrok.com/) 可以通过安全的 HTTPS URL 将本地端口暴露到互联网上；它需要一个免费的 ngrok 账户，请将 `YOUR_NGROK_DOMAIN.ngrok-free.dev` 替换为你自己预留的域名：

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. 验证本地模型

确认 Lemonade 能够提供所选模型的服务：

<!-- @os:linux -->
```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

然后发送一个简单的聊天请求：

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

然后发送一个简单的聊天请求：

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

如果返回结果中包含 `choices` 数组，则说明 Lemonade 已为 Agent Canvas 做好准备。

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

## 3. 启动 Agent Canvas

<!-- @os:linux -->
安装已发布的 Agent Canvas 软件包并启动完整堆栈：

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

如果全局 npm 安装因权限错误而失败，请参阅下方的 npm 权限问题排查条目。

默认情况下，Agent Canvas 会在 `http://localhost:8000` 上启动。
在浏览器中打开该 URL。
该端口并无特殊含义——如果 8000 已被占用，可以使用 `--port`（或 `-p`）指定任意空闲端口。
默认的本地后端应在主页上显示为健康状态。

> **注意：** 首次启动时会构建 Agent Server 的 `uv` 管理的 Python 环境，因此后端报告健康状态之前可能需要几分钟时间。

`agent-canvas` 命令会同时启动 agent server、自动化后端以及 Web 前端。
在本地运行 OpenHands 只需要这一条命令。
本指南的其余部分将通过浏览器中的 Agent Canvas 界面来完成所有配置。
<!-- @os:end -->

<!-- @os:windows -->
在 Windows 上，请使用 Docker Desktop 运行已发布的 Agent Canvas 容器镜像。
该镜像捆绑了 Agent Server、自动化后端以及 Web 前端，因此你无需在主机上安装 Node.js、`uv` 或 CLI。

首先，创建容器将要挂载的配置和工作区文件夹：

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

拉取已发布的镜像（约 6 GB；该镜像是公开的，因此无需登录）：

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

然后启动堆栈：

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

在浏览器中打开 `http://localhost:8000/canvas`。
如果 8000 端口已被占用，可以映射到其他主机端口，例如 `-p 8080:8000`，然后改为打开 `http://localhost:8080/canvas`。

> **注意：** 首次启动时会在容器内构建 Agent Server 环境，因此后端报告健康状态之前可能需要几分钟时间。

`.openhands` 挂载点会在容器重启后持久保存你的 LLM 配置文件、MCP 服务器以及自动化任务。
本指南的其余部分将通过浏览器中 `http://localhost:8000/canvas` 的 Agent Canvas 界面来完成所有配置。
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
## 4. 在 UI 中配置本地 LLM

首次启动时，Agent Canvas 会打开一个入门引导流程。
在该流程中：

1. 保持 **OpenHands** 作为所选代理，然后点击 **Next**。
2. 在 **Set up your LLM** 页面，选择 **Advanced**。
3. 保持 **Authentication** 设置为 **API key**。
4. 将 **Custom Model** 设置为 `openai/Qwen3.6-35B-A3B-GGUF`。
5. 将 **Base URL** 设置为 `http://127.0.0.1:13305/api/v1`。
6. 对于 **API Key**，输入任意非空占位符，例如 `lemonade-local`。Lemonade 不需要真实的密钥，但 OpenHands 客户端需要一个值才能发送请求。

<!-- @os:windows -->
> **Windows（Docker）：** Agent Server 在容器内运行，因此请将 **Base URL** 设置为 `http://host.docker.internal:13305/api/v1`，而不是 `http://127.0.0.1:13305/api/v1`。
> 从容器内部看，`127.0.0.1` 指的是容器本身；`host.docker.internal` 才能访问运行在 Windows 主机上的 Lemonade，而 Docker Desktop 会自动提供该主机名。
<!-- @os:end -->

连接字段应如下所示。
API 密钥字段会被 UI 遮罩显示。

![Agent Canvas 首次使用的 LLM Advanced 设置，显示 Lemonade 模型和本地基础 URL](assets/01-llm-advanced-settings.png)

然后选择 **All**，并设置额外的本地模型字段：

1. 滚动到 **Custom Tokenizer**，将其设置为 `Qwen/Qwen3.6-35B-A3B`。
2. 滚动到 **LiteLLM Extra Body**，将其设置为 `{"enable_thinking": true}`。
3. 点击 **Next**。

![Agent Canvas 首次使用的 LLM All 选项卡，显示 Qwen 自定义分词器](assets/02-llm-all-tokenizer-settings.png)

![Agent Canvas 首次使用的 LLM All 选项卡，显示已配置的 LiteLLM 额外主体](assets/03-llm-all-extra-body-settings.png)

LLM 设置应显示如下：

| 字段 | 值 |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

`openai/` 前缀告诉 LiteLLM 针对 Lemonade 端点使用与 OpenAI 兼容的请求格式。
自定义分词器是该 GGUF 模型的原始 Hugging Face 分词器；它使 OpenHands 能够统计与本地模型服务器所看到的相同的聊天模板令牌数。
当前的首次使用 LLM 表单不显示压缩器（condenser）设置。
如果你的 Agent Canvas 构建版本在之后的 **Settings > LLM** 中提供了压缩器设置，请使用 `llm_summarizing`，并将最大令牌数设置为低于 Lemonade 上下文窗口的值，例如 `56000`。

## 5. 安装 GitHub 和 Slack MCP 服务器

在 Agent Canvas UI 中，打开 **Customize**（或 **Settings > MCP**）以添加能为代理提供 GitHub 和 Slack 工具的 MCP 服务器。
令牌值仅发送到你的本地 Agent Server，并以加密设置的形式保存。

<!-- @os:windows -->
> **Windows（Docker）：** 下面的 `npx` MCP 服务器命令在容器内运行，而容器中已经包含 Node.js，因此主机上不需要额外安装任何内容。
> 由于 `.openhands` 已挂载，MCP 服务器及其令牌会在容器重启后依然保留。
<!-- @os:end -->

### GitHub MCP 服务器

使用以下设置添加一个新的 MCP 服务器：

| 字段 | 值 |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = 你的 GitHub 令牌 |

使用对你想要汇总摘要的仓库具有读取权限的 GitHub 令牌。

### Slack MCP 服务器

使用以下设置添加第二个 MCP 服务器：

| 字段 | 值 |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = 你的摘要频道 ID |

将 `SLACK_CHANNEL_IDS` 设置为摘要频道 ID（与 `SLACK_DIGEST_CHANNEL` 的值相同），这样代理就不需要翻查每一个 Slack 频道。

添加这两个服务器后，使用每个服务器上的 **Test** 按钮确认其能够连接并公布可用工具。
GitHub 服务器应列出 GitHub 工具，Slack 服务器应列出 Slack 工具。

![已安装 GitHub 和 Slack 服务器的 Agent Canvas MCP 页面](assets/04-mcp-servers-installed.png)

<!-- @test:id=mcp-packages-resolve timeout=300 hidden=True -->
```bash
# The GitHub and Slack MCP servers run via npx and need real tokens to connect,
# so CI only confirms the referenced packages resolve from the npm registry.
npm view @modelcontextprotocol/server-github version
npm view @modelcontextprotocol/server-slack version
```
<!-- @test:end -->

## 6. 创建摘要自动化任务

在 Agent Canvas UI 中，打开 **Automations** 页面并创建一个新的自动化任务：

1. 选择 **Create automation**，并选择 **Prompt preset** 类型。
2. 将 **Name** 设置为 `GitHub Development Digest to Slack`。
3. 将 **Prompt** 设置为以下文本，并将仓库和频道占位符替换为你自己的值：

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

4. 将 **Trigger** 设置为 **Cron**，计划为 `0 9 * * 1-5`（工作日上午 9 点），并将 **Timezone** 设置为你所在的时区，例如 `America/New_York`。
5. 将 **Timeout** 设置为 `900` 秒。
6. 保存该自动化任务。

自动化任务详情页面会显示新创建的自动化任务及其 cron 触发器和生成的提示预设入口点。

![创建后的 Agent Canvas 自动化任务详情页面](assets/05-automation-created.png)
## 7. 测试自动化

在 Agent Canvas UI 的自动化详情页面：

1. 点击 **Run now**（或 **Dispatch**）立即运行一次自动化。
2. 观察同一页面上的运行列表。最新的运行应变为 `COMPLETED`。
3. 打开目标 Slack 频道。其中应包含生成的摘要。

您无需等待 cron 计划触发——**Run now** 会按需触发一次运行，以便您在依赖计划任务之前确认提示词、MCP 连接和 Slack 发布是否都正常工作。

![Agent Canvas 自动化运行成功完成](assets/06-automation-run-completed.png)

![Slack 频道显示生成的 OpenHands 摘要](assets/07-slackbot-message.png)

## 故障排查

<!-- @os:windows -->
- **Docker 端口 8000 已被占用：** 映射到其他主机端口，例如 `docker run ... -p 8080:8000 ...`，然后打开 `http://localhost:8080/canvas`。
- **`docker pull` 因凭据错误而失败**（例如“指定的登录会话不存在”）：从交互式 Windows 会话运行拉取操作，或预先拉取镜像。该镜像是公开的，因此无需 `docker login`。
- **UI 已加载但后端不健康：** 首次启动会在容器内构建 Agent Server 环境。请稍等片刻后刷新，并检查 `docker logs <container>` 以查看进度。
- **Agent Canvas 无法从容器访问 Lemonade：** 将 LLM 的 **Base URL** 设置为 `http://host.docker.internal:13305/api/v1`（而非 `127.0.0.1`），并确认 Lemonade 正在 Windows 主机上运行。
<!-- @os:end -->

- **Lemonade 已停止运行：** 使用步骤 1 中的 `lemonade run "${LEMONADE_MODEL}"` 命令重新启动它，然后重新运行健康检查。
- **`npm install -g` 因权限错误而失败：** 在 Linux 或 WSL 上，配置一个用户拥有的全局 npm 目录，将其添加到 shell 启动文件中，然后重新安装 Agent Canvas：

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  如果您使用的是 `zsh`，请将相同的 `export PATH=...` 行添加到 `~/.zshrc` 而非 `~/.bashrc` 中。
- **设置 `custom_tokenizer` 后 Agent Canvas 拒绝 LLM 设置：** 在 Agent Server 的 Python 环境中安装 `transformers`，如有必要重新启动 Agent Canvas，然后重试保存 LLM 设置。当设置了 `custom_tokenizer` 时，OpenHands 需要 Transformers 才能加载分词器聊天模板。
- **Agent Canvas 无法访问 Lemonade：** 验证 `curl -fsS "${LEMONADE_BASE_URL}/health"`，并确认在首次使用的 LLM 表单或 **Settings > LLM** 中输入的 base URL 与正在运行的本地端点或 HTTPS 隧道相匹配。
- **LLM 设置未保存：** 确保在输入值后点击了 **Next**。重新打开 **Settings > LLM** 以确认值已保存。
- **GitHub MCP 无法查看私有仓库：** 确认 GitHub 令牌对目标仓库具有读取权限，并确认 **Customize** 中的 MCP **Test** 按钮显示了 GitHub 工具。
- **Slack 可以读取频道但无法发布：** 将 Slack 应用邀请到目标频道，并确认该机器人具有 `chat:write` 权限。
- **自动化列出了过多的 Slack 频道：** 使用 Slack 频道 ID，并在 **Customize** 中为 Slack MCP 服务器设置 `SLACK_CHANNEL_IDS`。
- **自动化运行失败或超出上下文：** 确认 Lemonade 启动时使用了 `ctx_size=65536`，确认 OpenHands LLM 已设置 `custom_tokenizer`，并使用明确的仓库，将 GitHub 结果集限制在 3 到 5 项。如果您的 Agent Canvas 版本提供压缩器（condenser）设置，请将压缩器的最大令牌数设置为低于 Lemonade 的上下文窗口。

## 后续步骤

- 添加仅限每周发布的摘要。
- 添加由 GitHub 事件触发的自动化，以实现更快的 PR 或推送提醒。
- 将同一摘要路由到 Notion、Linear 或其他基于 MCP 的工具中。

## 资源

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Lemonade Server 文档](https://lemonade-server.ai/docs)
- [OpenHands 扩展仓库](https://github.com/OpenHands/extensions)
- [Model Context Protocol 服务器](https://github.com/modelcontextprotocol/servers)
- [Slack MCP 包](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)

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