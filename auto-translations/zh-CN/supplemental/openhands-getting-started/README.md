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
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## 概述

[OpenHands](https://github.com/All-Hands-AI/OpenHands) 是一款 AI 软件智能体，能够在真实的工作区中编写代码、运行命令、浏览网页以及编辑文件。你无需再从聊天窗口中复制建议，而是可以将该智能体指向一个项目文件夹，让它去完成实际工作：实现一个功能、修复一个 bug、编写测试，或者解释一份代码库。

[Agent Canvas](https://github.com/OpenHands/agent-canvas) 是运行 OpenHands 推荐使用的浏览器 UI。一条 `agent-canvas` 命令即可同时启动智能体服务器、自动化后端和网页前端，让你可以直接在浏览器中与智能体进行对话。

为了将一切都保留在你的 AMD 系统上，该智能体与 Lemonade Server 提供的本地模型进行通信。Lemonade 通过一个与 OpenAI 兼容的 API 暴露该模型，因此 Agent Canvas 可以像配置任何其他 OpenAI 风格的端点一样对其进行配置，同时模型、你的代码以及对话上下文都保留在你的本机上。

在本实践指南中，你将启动一个本地模型，启动 Agent Canvas，将其指向该模型，并针对一个真实的项目文件夹运行你的第一个编码任务。

## 你将学到什么

- 如何启动 Lemonade Server 并确认本地模型能够响应聊天请求
- 如何从 npm 包安装并启动 Agent Canvas
- 如何配置 Agent Canvas 以将本地 Lemonade 模型用作 LLM
- 如何开始一次 OpenHands 对话，并观察该智能体在工作区中编辑文件、运行命令
- 如何查看智能体所做的更改，并通过后续消息对其进行引导

## 核心概念

| 概念 | 是什么 | 在本实践指南中的作用 |
| --- | --- | --- |
| Lemonade Server | 一个专为 AMD 硬件打造的本地 LLM 服务平台，暴露与 OpenAI 兼容的 API。你的数据永远不会离开你的设备。 | 运行为智能体提供支持的模型。 |
| OpenHands | 一款 AI 软件智能体，能够在工作区中读取和编辑文件、运行 shell 命令以及浏览网页。 | 你在聊天中驱动的智能体。 |
| Agent Canvas | 运行 OpenHands 对话，并显示工具调用和文件更改的浏览器 UI 及后端。 | 启动整个技术栈并承载你的对话。 |
| 工作区 | 允许智能体读取和修改的项目文件夹。 | 智能体编辑和执行命令的目标。 |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> 编码智能体工作流从更大的模型和更大的上下文窗口中受益。请使用至少 32 GB 的系统内存，对于更大的 GGUF 模型，建议使用 64 GB 或更多内存。
<!-- @device:end -->

## 设置内存配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 检查软件更新

<!-- @require:software-update -->
<!-- @device:end -->

## 前置条件


<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- @os:end -->

你需要：

- 已安装 Lemonade Server，并能够提供下述模型服务。

<!-- @os:linux -->
- Node.js 22.12 或更高版本，以及 `npm`（供 `agent-canvas` CLI 使用）。
- `uv`，Agent Canvas 用来管理智能体服务器环境的 Python 包管理器。如果你的系统尚未安装它，请在启动 Agent Canvas 之前，从
  [uv 安装指南](https://docs.astral.sh/uv/getting-started/installation/)
  中安装它。
<!-- @os:end -->

<!-- @os:windows -->
- [适用于 Windows 的 Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)，
  已安装并正在运行。在 Windows 上，Agent Canvas 技术栈是从官方发布的 Docker 镜像中运行的，该镜像已内置了 Node.js、`uv`
  以及 `@openhands/agent-canvas` 包，因此你无需在主机上安装这些内容。
<!-- @os:end -->

- 一个供你操作的项目文件夹。这可以是任何本地 git 仓库，或者你希望该智能体处理的代码目录。

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

## 1. 启动 Lemonade Server

从 Lemonade CLI 启动模型：

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

> **选择一个适合你硬件的模型。** `Qwen3.6-35B-A3B-GGUF`（约 20 GB）是一款强大的编码模型，但需要较大的内存池。如果你的设备内存或 GPU 显存有限，请改为从 Lemonade 模型库中选择一个较小的 GGUF 模型，并在本实践指南中全程使用该模型 ID。

> **注意：** 首次执行 `lemonade run` 时，如果模型尚未存在，会先下载该模型，根据模型大小和你的网络连接情况，这可能需要一些时间。

Lemonade 在以下地址暴露一个与 OpenAI 兼容的 API：

```text
http://127.0.0.1:13305/api/v1
```

## 2. 验证本地模型

确认 Lemonade 能够提供所选模型的服务：

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

然后发送一个简单的聊天请求：

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

如果返回结果中包含 `choices` 数组，则说明 Lemonade 已准备好供 Agent Canvas 使用。

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
## 3. 安装并启动 Agent Canvas

<!-- @os:linux -->
全局安装已发布的 Agent Canvas 软件包：

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

然后从终端启动完整的技术栈：

```bash
agent-canvas
```

默认情况下，Agent Canvas 会在 `http://localhost:8000` 上启动。请在浏览器中打开该 URL。该端口并非固定不变——如果 8000 已被占用，可以在启动 Agent Canvas 时使用 `--port`（或 `-p`）传递任意空闲端口：

```bash
agent-canvas --port 3000
```

然后改为打开 `http://localhost:3000`。默认的本地后端应在主屏幕上显示为健康状态。

`agent-canvas` 命令会同时启动代理服务器、自动化后端和 Web 前端。您只需运行这一条命令即可在本地运行 OpenHands。

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
在 Windows 上，请使用 Docker Desktop 运行已发布的 Agent Canvas 容器镜像。该镜像捆绑了 Agent Server、自动化后端和 Web 前端，因此无需在主机上安装 Node.js、`uv` 或 CLI。

首先，创建容器要挂载的配置和工作区文件夹：

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

拉取已发布的镜像（该镜像是公开的，无需登录）：

```powershell
docker pull ghcr.io/openhands/agent-canvas:1.14.0
```

然后启动技术栈：

```powershell
docker run -it --rm `
  -p 8000:8000 `
  -v "$($env:USERPROFILE)\.openhands:/home/openhands/.openhands" `
  -v "$($env:PROJECTS_PATH):/projects" `
  ghcr.io/openhands/agent-canvas:1.14.0
```

在浏览器中打开 `http://localhost:8000/canvas`。如果 8000 端口已被占用，请映射到其他主机端口，例如 `-p 8080:8000`，然后改为打开 `http://localhost:8080/canvas`。

> **注意：** 首次启动时会在容器内初始化 Agent Server，因此后端报告健康状态之前可能需要一两分钟。

`.openhands` 挂载会在容器重启之间持久保存您的 LLM 配置文件和设置。本手册的其余部分将通过浏览器中的 Agent Canvas UI 来配置一切。

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

## 4. 配置本地 LLM

首次启动时，Agent Canvas 会打开一个引导流程。在该流程中：

1. 保持 **OpenHands** 作为所选代理，然后点击 **Next**。
2. 在 **Set up your LLM** 页面，选择 **Advanced**。
3. 保持 **Authentication** 设置为 **API key**。
4. 将 **Custom Model** 设置为 `openai/Qwen3.6-35B-A3B-GGUF`。
5. 将 **Base URL** 设置为 `http://127.0.0.1:13305/api/v1`。
   <!-- @os:windows -->
   > 在 Windows 上，该技术栈运行在容器中，无法通过 `127.0.0.1` 访问主机。请改用
   > `http://host.docker.internal:13305/api/v1`，以便容器化的代理能够访问运行在
   > Windows 主机上的 Lemonade。
   <!-- @os:end -->
6. 对于 **API Key**，输入任意非空占位符，例如 `lemonade-local`。Lemonade 不需要真实的密钥，
   但 OpenHands 客户端需要一个值来发送。
7. 点击 **Next**。

完成后的 Advanced 设置应如下所示。API 密钥字段会被界面遮蔽显示。

![Agent Canvas 首次使用的 LLM Advanced 设置，包含 Lemonade 模型和本地基础 URL](assets/01-llm-advanced-settings.png)

Agent Canvas 会将这些值保存为一个 LLM 配置文件。如果您的版本要求您为该配置文件命名，请使用不含空格的名称，例如 `lemonade-local`。如果您以后更改模型，请打开 **Settings > LLM** 并更新相同的 Advanced 字段。您可以在聊天输入框中使用 `/model` 命令切换已保存的配置文件。

## 5. 打开工作区

代理只能读取和修改您所选工作区内的文件。在开始任务之前，请将 Agent Canvas 指向您的项目文件夹：

1. 在主屏幕上，选择 **Open Workspace**。
2. 选择包含您项目的文件夹（例如，您希望代理处理的 git 仓库）。
3. 在该工作区中开始新的对话。

代理所做的一切——读取文件、运行命令、编辑代码——都限定在该工作区范围内。

![引导完成后的 Agent Canvas 主页](assets/02-agent-canvas-home.png)

## 6. 运行您的第一个编码任务

在打开工作区并选择本地 LLM 后，在聊天框中输入一个具体的任务。一个好的初始任务应该是小而可验证的，例如：

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

观察对话时间线。OpenHands 将会：

- 读取工作区以了解结构。
- 创建包含所请求函数和测试代码块的 `hello.py`。
- 可选地运行 `python3 hello.py` 来验证输出。
- 在聊天中报告它所做的操作以及任何命令输出。

您应该会看到新文件出现在工作区中，代理的最终消息应描述它所做的更改。这就是成果时刻：代理已经在您的项目文件夹中编写并运行了真实的代码。

## 7. 审查并引导代理

代理完成一个步骤后，在接受下一个步骤之前请先审查其工作：

- **文件更改**：使用工作区文件浏览器或代理的差异视图，查看具体添加、更改或删除的内容。
- **命令输出**：展开代理运行的任何命令，查看标准输出、标准错误和退出代码。
- **后续跟进**：如果结果不是您想要的，请在同一对话中回复更正内容。代理会保留之前的上下文，并在相同文件上继续迭代。

例如，如果测试没有打印出预期的问候语，请回复：

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

代理将重新读取文件、运行命令、诊断问题，并再次编辑文件——全部在同一对话中完成。
## 故障排除

<!-- @os:linux -->
- **`agent-canvas` 不在 PATH 中：** 使用
  `npm install -g @openhands/agent-canvas` 重新安装，并在从新终端启动
  `agent-canvas` 之前确认 npm 全局二进制文件目录已添加到 PATH 中。
- **`npm install -g` 因权限错误而失败：** 配置一个用户拥有的全局 npm 目录，
  然后重新打开终端并再次安装 Agent Canvas。

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **缺少 `uv`：** 从
  [uv 安装指南](https://docs.astral.sh/uv/getting-started/installation/)进行安装。
  Agent Canvas 使用 `uv` 来管理代理服务器的 Python 环境。
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` 或 `docker run` 连接失败：** 确保 Docker Desktop
  正在运行（其鲸鱼图标显示在系统托盘中），并且引擎已完成启动。`docker version`
  应同时打印 Client 和 Server 部分。
- **容器已启动但后端始终未变为健康状态：** 首次启动时会在容器内初始化
  Agent Server；请等待一两分钟，然后查看 `docker logs <container>` 是否有错误。
- **容器无法连接到 Lemonade：** 容器通过
  `host.docker.internal` 访问主机。请使用 `lemonade status`
  确认 Lemonade 正在 Windows 主机上提供服务，并在配置 LLM 时使用
  `http://host.docker.internal:13305/api/v1` 作为 Base URL。
<!-- @os:end -->

- **界面已加载但后端显示不健康：** 等待一两分钟，让代理服务器完成启动，
  然后刷新页面。如果仍然不健康，请重启整个堆栈并检查日志中的错误。
- **Lemonade 聊天请求因连接错误而失败：** 确认
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` 执行成功，并且
  Lemonade 仍在通过 `lemonade status` 提供该模型的服务。
- **代理报出上下文长度或令牌限制相关的错误消息：** 开启一个新的对话，
  避免代理携带过大的历史记录。如果问题持续出现，请以大于默认值 65536 的
  `ctx_size`（例如 `ctx_size=131072`）重启 Lemonade（前提是内存允许）。
- **代理生成的编辑质量低或不完整：** 切换到 Lemonade 中更大的模型，
  或给代理分配一个更小、更具体的任务，等它完成后再要求进行下一步更改。

## 后续步骤

- 在同一个工作区中尝试更大的任务，例如添加单元测试文件或修复已知的错误，
  并在保留更改之前审阅代理生成的差异。
- 在**自定义**下连接一个 MCP 服务器（如 GitHub 或 Slack），
  以便代理在工作时可以读取问题或发布更新。
- 保存多个 LLM 配置文件（一个快速的小模型和一个更强大的大模型），
  并在对话过程中使用 `/model` 在它们之间切换。
- 前往[OpenHands 自动化](https://docs.openhands.dev/openhands/usage/automations/overview)，
  将重复性的开发流程转变为计划性或事件触发的代理运行。

## 资源

- [OpenHands 文档](https://docs.openhands.dev/)
- [Agent Canvas 概览](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Agent Canvas 设置](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM 配置文件与模型配置](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Lemonade Server 文档](https://lemonade-server.ai/docs)

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