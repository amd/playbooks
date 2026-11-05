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
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## 概述

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> 本教程需要至少 **32GB** 的系统内存。
<!-- @device:end -->

n8n 是一个工作流自动化平台，允许您使用可视化的基于节点的编辑器连接各种应用和服务。

本教程将教您如何搭建一个由 AI 驱动的财经新闻摘要生成器，它会从新闻 RSS 源中获取最新的商业头条，并使用运行在您本地系统上的 LLM 生成面向投资者的摘要。

<!-- @device:halo_box -->
> **注意：** 部分 AMD Ryzen AI Halo 系统已预装了本教程所需的模型，而其他系统则没有。两种情况均受支持。当您进入 **启动 Lemonade** 部分时，请检查该模型是否已在 Lemonade 中可用——如果已有，您可以直接加载；如果没有，请先在那里下载。
<!-- @device:end -->

## 您将学到的内容

- 如何安装并启动 n8n
- 导入和配置预构建的工作流
- 使用原生 n8n 集成连接 Lemonade
- 理解工作流节点和数据流

## 什么是 Lemonade？

[Lemonade](https://lemonade-server.ai) 是一个为 AMD 硬件打造的本地 LLM 服务平台。它提供了一个兼容 OpenAI 的 API，完全在本地运行——您的数据不会离开您的设备。

在本教程中，我们使用 Lemonade 来提供一个本地 LLM，供 n8n 连接以执行 AI 驱动的任务。

n8n 包含一个**原生 Lemonade 节点**（`Lemonade Chat Model`），它提供了一流的集成体验——无需手动配置。这使得将本地 LLM 连接到自动化工作流变得非常简单。

<!-- @device:halo_box,halo,stx,krk -->
## 设置内存配置

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## 检查软件更新

<!-- @require:software-update -->
<!-- @device:end -->

## 安装软件前置依赖
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @prereq:n8n,lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- Linux runs n8n as a Podman container (see compose.yml below), so Node.js and a host n8n install are not required; podman is the only extra prerequisite. -->
<!-- @require:lemonade,podman -->
<!-- @prereq:podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @prereq:lemonade-models-gpt-oss-120b -->
<!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @prereq:lemonade-models-gpt-oss-20b -->
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

<!-- @os:windows -->
<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->
<!-- @os:end -->

## 安装 n8n
<!-- @os:windows -->
> [!IMPORTANT]
> **n8n 仅支持 Node.js 20.19 至 24.x 版本**
> （参见 [n8n 安装文档](https://docs.n8n.io/deploy/host-n8n/install-options/install-with-npm)）。
> nodejs.org 上的当前发布版本比此范围更新。在 Node 26 上安装 n8n 会在
> Windows 上失败，并出现 `EBADPLATFORM` 或本机构建错误，安装结果会抛出
> `MODULE_NOT_FOUND`。请在继续之前确认您的版本：
>
> ```cmd
> node --version
> ```
>
> 如果版本不在 20.19&ndash;24.x 范围内，请使用
> [nvm-windows](https://github.com/coreybutler/nvm-windows) 安装受支持的版本（`nvm install 24.10.0 && nvm use 24.10.0`）。

使用 npm 全局安装 n8n。请固定版本号&mdash;在撰写本文时，n8n 的最新发行版本
将仅限 Linux 的二进制文件声明为硬性依赖，导致在 Windows 上的所有受支持
Node 版本下安装都会失败，并提示 `EBADPLATFORM`：

> **注意**：您可能会看到一些 npm 警告。这是预期行为。

```bash
npm install -g n8n@2.45.6
```

<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **提示**：Windows 用户在运行某些 PowerShell 命令之前，可能需要修改其 PowerShell 执行策略
> （例如将其设置为 RemoteSigned 或 Unrestricted）。
<!-- @os:end -->


<!-- @os:windows -->
> **PATH 问题**：如果 `n8n --version` 提示命令未找到，请确保您的 npm 全局 bin 目录已添加到用户 `PATH` 中。常见的安装路径为 `C:\Users\<username>\AppData\Roaming\npm`。
> 将其添加到用户路径中（编辑系统环境变量 > 环境变量 > 编辑用户路径），然后重新加载终端。

<!-- @os:end -->

<!-- @os:linux -->
现在我们将使用 Podman 服务来容器化我们的 n8n 安装。

请将以下文件下载到您选择的目录中：[compose.yml](assets/compose.yml)

在该目录中，运行以下命令：
```bash
podman compose up -d
```

这应该会安装 n8n 并写入持久化存储。

在浏览器地址栏中输入 `localhost:5678` 启动 n8n。
<!-- @os:end -->

<!-- @os:windows -->
## 启动 n8n

从终端启动 n8n：

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

export PODMAN_COMPOSE_PROVIDER="$(command -v podman-compose)"
cleanup() {
  podman compose -f compose.yml down >/dev/null 2>&1 || true
}
trap cleanup EXIT

podman rm -f n8n >/dev/null 2>&1 || true
podman compose -f compose.yml up -d

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
  podman ps -a || true
  podman logs n8n 2>&1 | tail -30 || true
  exit 1
fi

echo "OK: n8n server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
n8n 会启动一个本地 Web 服务器。按下 `'o'` 或在浏览器中打开 `http://localhost:5678` 即可访问编辑器。
<!-- @os:end -->


> **提示**：在使用 n8n 时请保持终端窗口打开。关闭它可能会停止服务器。

## 使用 Lemonade 启动模型

Lemonade 是将运行模型并连接到 n8n 的本地服务器。

<!-- @os:linux -->
点击任务栏中的 Lemonade 图标，打开 Lemonade GUI。在此处，您可以浏览模型和后端，下载任何尚未安装的模型，并加载它。出厂时已预装该模型的系统可以直接加载。
<!-- @os:end -->

<!-- @os:windows -->
点击 Lemonade 图标，打开 Lemonade GUI。右键单击托盘图标以打开该应用。在此处，您可以浏览模型和后端，下载任何尚未安装的模型，并加载它。出厂时已预装该模型的系统可以直接加载。
<!-- @os:end -->

>**提示**：启动后，Lemonade GUI 也可通过 http://localhost:13305 访问

或者，您也可以打开终端并运行 `lemonade list` 查看已安装的模型。然后运行：

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


## 设置工作流

### 第 1 步：注册或登录 n8n

当您首次打开 n8n 时，系统会提示您创建账户或登录：

1. 在浏览器中打开 `http://localhost:5678`
2. 使用您的邮箱创建一个新的本地账户，或者如果您已有账户，请直接登录
3. 登录后，您将看到 n8n 仪表板

> **提示**：如果账户被锁定，请尝试运行 `n8n user-management:reset`
### 第 2 步：导入工作流

我们提供了一个预构建的工作流，您可以直接导入：

1. 下载以下工作流文件：[financial-news-workflow.json](assets/financial-news-workflow.json)
2. 点击 **Start from Scratch** 打开工作流编辑器。或者，点击左上角的 **+** 按钮，选择 **New workflow**，然后选择 **Build workflow**。
3. 点击右上角的 **...** 菜单（三个点），选择 **Import from file**
4. 选择下载的 `financial-news-workflow.json` 文件
5. 工作流将显示在画布上


### 第 3 步：了解工作流

导入的工作流包含 8 个相互连接的节点：

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| 节点 | 用途 |
|------|---------|
| **When clicking 'Execute workflow'** | 用于启动工作流的手动触发器 |
| **Fetch Financial News Feed** | RSS Read 节点，从 RSS 订阅源拉取最新的商业头条新闻（默认使用纽约时报商业版订阅源，无需 API 密钥） |
| **Aggregate Headlines** | Aggregate 节点，将每个订阅源条目中的标题和摘要收集到一个列表中 |
| **Clean Extracted News Data** | Set 节点，将所有标题合并为一个单一的文本字段 |
| **AI Financial News Summarizer** | 使用金融分析师系统提示处理新闻的 AI Agent |
| **Lemonade Chat Model** | 连接到运行 LLM 的本地 Lemonade 服务器 |
| **Structured Output Parser** | 将 AI 输出格式化为结构化 JSON |
| **Convert to File** | 将摘要转换为可下载的文件 |

> **提示**：要使用其他新闻来源，请双击 **Fetch Financial News Feed** 节点，并将 URL 替换为您偏好的任何商业或市场类 RSS 订阅源。

### 第 4 步：配置 Lemonade 凭据

在运行工作流之前，您需要将其连接到本地 Lemonade 服务器：

1. 在 n8n 中双击 **Lemonade Chat Model** 节点
2. 在下拉菜单 **Credential to connect with** 中选择 **Create New Credential**
3. 在下表中输入对应的值，然后点击保存。
4. 选择您已在 Lemonade Server 中加载的相应模型。

  | 字段 | 值 |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **注意**：在测试之前，请在终端中运行 `lemonade status` 以确认 Lemonade 服务器正在运行。
<!-- @device:halo_box -->
> 此工作流使用 GPT-OSS-120B，该模型已预装在 Lemonade 中。您可以在 Lemonade Chat Model 节点设置中将其更改为其他已加载的模型。
<!-- @device:end -->

### 第 5 步：测试工作流

1. 确保 Lemonade 正在运行并已加载模型
2. 点击画布底部中间的 **Execute workflow**
3. 观察每个节点从左到右依次执行——完成后节点会变为绿色
4. 双击 **AI Financial News Summarizer** 节点，在底部面板中查看生成的摘要。
5. 双击 **Convert to File** 节点，在底部面板中下载对应的文本文件。

## 了解 AI Agent

AI Financial News Summarizer 使用专为金融分析设计的系统提示：

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

该 Agent 接收经过清理的新闻数据，并输出带有市场情绪的结构化摘要。

### 保存您的工作流

点击顶部的工作流名称以在需要时重命名。工作流在您操作时会自动保存。

## 后续步骤

- **安排自动化**：将 Manual Trigger 替换为 **Schedule Trigger**，以实现每日运行
- **发送通知**：添加 **Discord**、**Slack** 或 **Email** 节点以接收摘要
- **尝试不同模型**：在 Lemonade Chat Model 节点中更改模型，以试验不同的 LLM
- **更改新闻来源**：将 **Fetch Financial News Feed** 节点指向不同的 RSS 订阅源，以关注其他板块或出版物
- **尝试不同的后端**：n8n 还支持 [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model)、LM Studio 以及其他本地 LLM 后端

### 探索 n8n 模板

n8n 拥有数百个预构建的工作流模板。请浏览官方模板库：

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

搜索 "AI"、"LLM" 或 "automation" 以查找可导入和自定义的工作流。

有关更多信息，请查阅 [n8n Documentation](https://docs.n8n.io/)。

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