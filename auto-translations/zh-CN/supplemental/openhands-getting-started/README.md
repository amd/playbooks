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

[OpenHands](https://github.com/All-Hands-AI/OpenHands) 是一款 AI 软件代理，能够在真实的工作区中编写代码、运行命令、浏览网页并编辑文件。您无需从聊天窗口中复制建议，只需将代理指向一个项目文件夹，让它完成实际工作：实现新功能、修复错误、编写测试或解释代码库。

[Agent Canvas](https://github.com/OpenHands/agent-canvas) 是运行 OpenHands 的推荐浏览器界面。一条 `agent-canvas` 命令即可同时启动代理服务器、自动化后端和 Web 前端，让您可以在浏览器中与代理进行对话。

为了让一切都保留在您的 AMD 系统本地，代理会与由 Lemonade Server 提供服务的本地模型进行通信。Lemonade 通过与 OpenAI 兼容的 API 公开该模型，因此 Agent Canvas 可以像配置任何其他 OpenAI 风格的端点一样对其进行配置，同时模型、您的代码以及对话上下文都会保留在您的本地设备上。

在本手册中，您将启动一个本地模型、运行 Agent Canvas、将其指向该模型，并针对一个真实的项目文件夹运行您的第一个编码任务。

## 您将学到什么

- 如何启动 Lemonade Server，并确认本地模型能够响应聊天请求
- 如何从 npm 软件包安装并启动 Agent Canvas
- 如何配置 Agent Canvas，使其将本地 Lemonade 模型用作 LLM
- 如何启动一个 OpenHands 对话，并观察代理在工作区中编辑文件和运行
  命令
- 如何查看代理所做的更改，并通过后续消息引导它

## 核心概念

| 概念 | 是什么 | 在本手册中的作用 |
| --- | --- | --- |
| Lemonade Server | 一个专为 AMD 硬件构建的本地 LLM 服务平台，公开与 OpenAI 兼容的 API。您的数据永远不会离开本地设备。 | 运行为代理提供支持的模型。 |
| OpenHands | 一款 AI 软件代理，能够在工作区中读取和编辑文件、运行 shell 命令并浏览网页。 | 您在聊天中驱动的代理。 |
| Agent Canvas | 用于运行 OpenHands 对话并显示工具调用和文件更改的浏览器界面和后端。 | 启动整个技术栈并承载您的对话。 |
| Workspace | 允许代理读取和修改的项目文件夹。 | 代理编辑和命令的操作对象。 |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> 编码代理工作流受益于更大的模型和上下文窗口。请至少使用
> 32 GB 系统内存，对于较大的 GGUF 模型，建议使用 64 GB 或更多内存。
<!-- @device:end -->

## 设置内存配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 检查软件更新

<!-- @require:software-update -->
<!-- @device:end -->

## 先决条件


<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade -->
<!-- @os:end -->

您需要：

- 已安装 Lemonade Server，并能够运行以下模型。

<!-- @os:linux -->
- Node.js 22.12 或更高版本以及 `npm`（`agent-canvas` CLI 使用）。
- `uv`，Agent Canvas 用于管理代理服务器环境的 Python 包管理器。如果您的系统尚未安装它，请在启动 Agent Canvas 之前，从[uv 安装指南](https://docs.astral.sh/uv/getting-started/installation/)进行安装。
<!-- @os:end -->

<!-- @os:windows -->
- [适用于 Windows 的 Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)，
  已安装并正在运行。在 Windows 上，Agent Canvas 技术栈通过已发布的
  Docker 镜像运行，该镜像捆绑了 Node.js、`uv` 和
  `@openhands/agent-canvas` 软件包，因此您无需在主机上安装这些内容。
<!-- @os:end -->

- 一个用于工作的项目文件夹。这可以是您希望代理处理的任何本地 git 仓库或代码目录。

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

> **选择适合您硬件的模型。** `Qwen3.6-35B-A3B-GGUF`（约 20 GB）是一个强大的编码模型，但需要较大的内存池。如果您的设备内存或 GPU 显存有限，请改为从 Lemonade 模型库中选择一个较小的 GGUF 模型，并在本手册中始终使用该模型 ID。

> **注意：** 如果模型尚未存在，首次运行 `lemonade run` 会下载该模型，根据模型大小和网络连接情况，这可能需要一些时间。

Lemonade 在以下位置公开一个与 OpenAI 兼容的 API：

```text
http://127.0.0.1:13305/api/v1
```

## 2. 验证本地模型

确认 Lemonade 能够运行所选模型：

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

如果返回一个 `choices` 数组，则表示 Lemonade 已准备好供 Agent Canvas 使用。

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

然后在终端中启动完整堆栈：

```bash
agent-canvas
```

默认情况下，Agent Canvas 启动于 `http://localhost:8000`。在浏览器中打开该
URL。此端口没有特殊之处——如果 8000 已被占用，可以在启动 Agent Canvas 时
使用 `--port`（或 `-p`）指定任意空闲端口：

```bash
agent-canvas --port 3000
```

然后改为打开 `http://localhost:3000`。默认的本地后端应在主屏幕上显示为健康状态。

`agent-canvas` 命令会一起启动 agent 服务器、自动化后端和 Web 前端。您只需
运行这一个命令即可在本地运行 OpenHands。

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
在 Windows 上，使用 Docker Desktop 运行已发布的 Agent Canvas 容器镜像。
该镜像捆绑了 Agent Server、自动化后端和 Web 前端，因此您无需在主机上
安装 Node.js、`uv` 或 CLI。

首先，创建容器要挂载的配置和工作区文件夹：

```powershell
$env:PROJECTS_PATH = Join-Path $HOME "projects"
New-Item -ItemType Directory -Force -Path $env:PROJECTS_PATH, (Join-Path $env:USERPROFILE ".openhands") | Out-Null
```

拉取已发布的镜像（该镜像是公开的，因此无需登录）：

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

在浏览器中打开 `http://localhost:8000/canvas`。如果端口 8000 已被占用，
请映射到不同的主机端口，例如 `-p 8080:8000`，然后改为打开
`http://localhost:8080/canvas`。

> **注意：** 首次启动会在容器内初始化 Agent Server，因此后端报告健康状态
> 之前可能需要一两分钟。

`.openhands` 挂载会在容器重启后持久保存您的 LLM 配置文件和设置。本手册
的其余部分将通过浏览器中的 Agent Canvas 界面配置所有内容。

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

1. 保持 **OpenHands** 作为所选 agent，然后点击 **Next**。
2. 在 **Set up your LLM** 页面，选择 **Advanced**。
3. 保持 **Authentication** 设置为 **API key**。
4. 将 **Custom Model** 设置为 `openai/Qwen3.6-35B-A3B-GGUF`。
5. 将 **Base URL** 设置为 `http://127.0.0.1:13305/api/v1`。
   <!-- @os:windows -->
   > 在 Windows 上，堆栈运行于容器中，无法通过 `127.0.0.1` 访问主机。请改为
   > 使用 `http://host.docker.internal:13305/api/v1`，以便容器化的 agent 能够
   > 访问在 Windows 主机上运行的 Lemonade。
   <!-- @os:end -->
6. 对于 **API Key**，输入任意非空的占位符，例如 `lemonade-local`。
   Lemonade 不需要真实的密钥，但 OpenHands 客户端需要发送一个值。
7. 点击 **Next**。

完成后的 Advanced 设置应如下所示。API 密钥字段会被界面遮蔽显示。

![Agent Canvas 首次使用的 LLM Advanced 设置，显示 Lemonade 模型和本地 base URL](assets/01-llm-advanced-settings.png)

Agent Canvas 会将这些值保存为一个 LLM 配置文件。如果您的版本要求为该配置
文件命名，请使用不含空格的名称，例如 `lemonade-local`。如果之后更换模型，
请打开 **Settings > LLM** 并更新相同的 Advanced 字段。您可以在聊天输入框中
使用 `/model` 命令切换已保存的配置文件。

## 5. 打开工作区

agent 只能读取和修改您所选工作区内的文件。在开始任务之前，请将 Agent
Canvas 指向您的项目文件夹：

1. 从主屏幕选择 **Open Workspace**。
2. 选择包含您项目的文件夹（例如，您希望 agent 处理的 git 仓库）。
3. 在该工作区中开始新对话。

agent 所做的一切——读取文件、运行命令、编辑代码——都仅限于该工作区。

![引导完成后的 Agent Canvas 主页](assets/02-agent-canvas-home.png)

## 6. 运行您的第一个编码任务

在工作区已打开且已选择本地 LLM 的情况下，在聊天中输入一个具体的任务。
一个好的初始任务应当小且可验证，例如：

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

观察对话时间线。OpenHands 将会：

- 读取工作区以了解其布局。
- 创建 `hello.py`，其中包含所请求的函数和测试代码块。
- 可选地运行 `python3 hello.py` 以验证输出。
- 在聊天中报告其所做的操作以及任何命令输出。

您应能看到新文件出现在工作区中，并且 agent 的最终消息应描述其所做的
更改。这就是收获的时刻：agent 在您的项目文件夹中编写并运行了真实的代码。

## 7. 审查并引导 agent

在 agent 完成一个步骤后，请在接受下一步之前审查其工作：

- **文件更改**：使用工作区文件浏览器或 agent 的差异视图，查看究竟添加、
  更改或删除了哪些内容。
- **命令输出**：展开 agent 运行的任何命令，以查看 stdout、stderr 和退出代码。
- **后续跟进**：如果结果不是您想要的，请在同一对话中回复以进行更正。
  agent 会保留之前的上下文，并在相同文件上继续迭代。

例如，如果测试未打印预期的问候语，请回复：

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

agent 将重新读取文件、运行命令、诊断问题，并再次编辑该文件——所有这些
都在同一对话中完成。
## 故障排查

<!-- @os:linux -->
- **`agent-canvas` 未添加到 PATH 中：** 使用
  `npm install -g @openhands/agent-canvas` 重新安装，并确认 npm 全局二进制文件
  目录已添加到 PATH 中，之后才能在新终端中启动 `agent-canvas`。
- **`npm install -g` 因权限错误而失败：** 配置一个用户拥有的
  全局 npm 目录，然后重新打开终端并再次安装 Agent Canvas。

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
- **缺少 `uv`：** 从
  [uv 安装指南](https://docs.astral.sh/uv/getting-started/installation/) 进行安装。
  Agent Canvas 使用 `uv` 来管理 agent 服务器的 Python 环境。
<!-- @os:end -->

<!-- @os:windows -->
- **`docker pull` 或 `docker run` 无法连接：** 确保 Docker Desktop
  正在运行（其鲸鱼图标出现在系统托盘中），并且引擎已完成启动。`docker version`
  应同时输出 Client 和 Server 两部分内容。
- **容器已启动但后端始终无法变为健康状态：** 首次
  启动时会在容器内初始化 Agent Server；请等待一两分钟，
  然后通过 `docker logs <container>` 查看是否有错误。
- **容器无法连接到 Lemonade：** 容器通过
  `host.docker.internal` 访问主机。请通过 `lemonade status`
  确认 Lemonade 正在 Windows 主机上提供服务，并在配置 LLM 时
  使用 `http://host.docker.internal:13305/api/v1` 作为 Base URL。
<!-- @os:end -->

- **界面已加载，但后端显示不健康：** 请等待一两分钟，让
  agent 服务器完成启动，然后刷新页面。如果仍然不健康，请重启
  该技术栈并查看日志以了解错误信息。
- **Lemonade 聊天请求因连接错误而失败：** 确认
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` 执行成功，并且
  Lemonade 仍在通过 `lemonade status` 提供该模型的服务。
- **agent 报错，提示上下文长度或 token 限制相关的错误：** 开启一个
  新对话，以免 agent 携带过大的历史记录。如果问题
  持续出现，请在内存允许的情况下，将 Lemonade 的 `ctx_size`
  设置得比默认值 65536 更大（例如 `ctx_size=131072`）后重新启动。
- **agent 生成的编辑质量较低或不完整：** 切换到 Lemonade 中
  更大的模型，或者给 agent 分配一个更小、更具体的任务，
  并在提出下一个更改要求之前让其先完成当前任务。

## 后续步骤

- 在同一工作区中尝试一个更大的任务，例如添加单元测试文件或
  修复一个已知错误，并在保留更改之前审查 agent 的差异（diff）。
- 在 **Customize** 下连接一个 MCP 服务器（例如 GitHub 或 Slack），以便
  agent 在工作时可以读取 issue 或发布更新。
- 保存多个 LLM 配置文件（一个快速的小模型和一个更强大的大模型），
  并在对话中途通过 `/model` 在它们之间切换。
- 继续了解 [OpenHands 自动化功能](https://docs.openhands.dev/openhands/usage/automations/overview)，
  将重复性的开发循环转变为按计划或事件触发的 agent 运行任务。

## 资源

- [OpenHands 文档](https://docs.openhands.dev/)
- [Agent Canvas 概述](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
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