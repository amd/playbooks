<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **机器翻译。**本页面由英文自动翻译，未经人工审核。其中可能包含错误，某些说明、命令、下载内容、产品可用性或其他内容可能因语言或地区而异。如内容存在任何不一致或差异，应以英文原版 playbook 为准。
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## 概述

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> 本实践指南要求至少 **32GB** 的系统内存。
<!-- @device:end -->

n8n 是一个工作流自动化平台,可让您使用可视化的基于节点的编辑器连接各种应用和服务。

本实践指南将教您如何设置一个由 AI 驱动的金融新闻摘要工具,该工具从新闻 RSS 源中获取最新的商业头条新闻,并使用系统上运行的本地 LLM 生成面向投资者的摘要。

<!-- @device:halo_box -->
> **注意:** 部分 AMD Ryzen AI Halo 系统已预装了本实践指南所需的模型,而其他系统则没有。两种情况均受支持。当您进入**启动 Lemonade** 部分时,请检查该模型是否已在 Lemonade 中可用——如果已可用,您可以直接加载它;如果没有,请先在那里下载。
<!-- @device:end -->

## 您将学到的内容

- 如何安装和启动 n8n
- 导入和配置预构建的工作流
- 使用 n8n 原生集成连接到 Lemonade
- 了解工作流节点和数据流

## 什么是 Lemonade?

[Lemonade](https://lemonade-server.ai) 是一个专为 AMD 硬件构建的本地 LLM 服务平台。它提供了一个与 OpenAI 兼容的 API,完全在您的本机上运行——您的数据不会离开您的设备。

在本实践指南中,我们使用 Lemonade 来提供本地 LLM 服务,n8n 会连接到该服务以执行 AI 驱动的任务。

n8n 包含一个**原生 Lemonade 节点**(`Lemonade Chat Model`),提供一流的集成——无需手动配置。这使得将本地 LLM 连接到自动化工作流变得十分简便。

<!-- @device:halo_box,halo,stx,krk -->
## 设置内存配置

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## 检查软件更新

<!-- @require:software-update -->
<!-- @device:end -->

## 安装软件前置条件
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
使用 npm 全局安装 n8n。

> **注意**:您可能会看到一些 npm 警告。这是正常现象。

```bash
npm install -g n8n
```

<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **提示**:Windows 用户在运行某些 Powershell 命令之前,可能需要修改其 PowerShell 执行策略
> (例如,将其设置为 RemoteSigned 或 Unrestricted)。
<!-- @os:end -->


<!-- @os:windows -->
> **PATH 问题**:如果 `n8n --version` 提示找不到命令,请确保您的 npm 全局 bin 目录位于用户 `PATH` 中。常见的安装路径为 `C:\Users\<username>\AppData\Roaming\npm`。
> 将此路径添加到用户路径中(编辑系统环境变量 > 环境变量 > 编辑用户路径),然后重新加载终端。

<!-- @os:end -->

<!-- @os:linux -->
现在我们将使用 Podman 服务来容器化我们的 n8n 安装。

请将以下文件下载到您选择的目录中:[compose.yml](assets/compose.yml)

在该目录中,运行以下命令:
```bash
podman compose up -d
```

这应该会安装 n8n 并写入持久化存储。

在浏览器地址栏中输入 `localhost:5678` 以启动 n8n。
<!-- @os:end -->

<!-- @os:windows -->
## 启动 n8n

从终端启动 n8n:

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
n8n 会启动一个本地 Web 服务器。按下 `'o'` 或在浏览器中打开 `http://localhost:5678` 以访问编辑器。
<!-- @os:end -->


> **提示**:在使用 n8n 时,请保持终端窗口处于打开状态。关闭它可能会停止服务器。

## 使用 Lemonade 启动模型

Lemonade 是将运行模型并连接到 n8n 的本地服务器。

<!-- @os:linux -->
点击任务栏中的 Lemonade 图标以打开 Lemonade GUI。在这里,您可以浏览模型和后端,下载任何尚未安装的模型,并加载它。出厂时已预装该模型的系统可以直接加载该模型。
<!-- @os:end -->

<!-- @os:windows -->
点击 Lemonade 图标以打开 Lemonade GUI。右键单击托盘图标以打开该应用。在这里,您可以浏览模型和后端,下载任何尚未安装的模型,并加载它。出厂时已预装该模型的系统可以直接加载该模型。
<!-- @os:end -->

>**提示**:运行后,Lemonade GUI 也可通过 http://localhost:13305 访问。

或者,您也可以打开终端并运行 `lemonade list` 来查看已安装的模型。然后运行:

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

### 第 1 步:注册或登录 n8n

首次打开 n8n 时,系统会提示您创建账户或登录:

1. 在浏览器中打开 `http://localhost:5678`
2. 使用您的邮箱创建一个新的本地账户,或者如果您已有账户,则直接登录
3. 登录后,您将看到 n8n 仪表盘

> **提示**:如果您的账户被锁定,请尝试运行 `n8n user-management:reset`

### 第 2 步:导入工作流

我们提供了一个预构建的工作流,您可以直接导入:

1. 下载以下工作流文件:[financial-news-workflow.json](assets/financial-news-workflow.json)
2. 点击 **Start from Scratch** 以打开工作流编辑器。或者,点击左上角的 + 按钮,然后点击 **Add workflow**。
3. 点击右上角的 **...** 菜单(三个点),选择 **Import from file**
4. 选择下载的 `financial-news-workflow.json` 文件
5. 工作流将显示在画布上
### 第 3 步：了解工作流程

导入的工作流程包含 8 个相互连接的节点：

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| 节点 | 用途 |
|------|---------|
| **When clicking 'Execute workflow'** | 用于启动工作流程的手动触发器 |
| **Fetch Financial News Feed** | RSS Read 节点，用于从 RSS 源中获取最新的商业头条新闻（默认使用纽约时报商业频道，无需 API 密钥） |
| **Aggregate Headlines** | Aggregate 节点，用于从每个新闻源条目中收集标题和摘要，汇总成单一列表 |
| **Clean Extracted News Data** | Set 节点，用于将所有标题合并为单个文本字段 |
| **AI Financial News Summarizer** | AI 代理，使用金融分析师系统提示词来处理新闻 |
| **Lemonade Chat Model** | 连接到运行 LLM 的本地 Lemonade 服务器 |
| **Structured Output Parser** | 将 AI 输出格式化为结构化 JSON |
| **Convert to File** | 将摘要转换为可下载文件 |

> **提示**：若要使用其他新闻来源，请双击 **Fetch Financial News Feed** 节点，并将 URL 替换为任意您偏好的商业或市场 RSS 源。

### 第 4 步：配置 Lemonade 凭据

在运行工作流程之前，您需要将其连接到本地 Lemonade 服务器：

1. 在 n8n 中双击 **Lemonade Chat Model** 节点
2. 在下拉菜单 **Credential to connect with** 中选择 **Create New Credential**
3. 在下表中输入相应的值，然后点击保存。
4. 选择您在 Lemonade Server 中已加载的相关模型。

  | 字段 | 值 |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **注意**：测试之前，请在终端中运行 `lemonade status`，以确认 Lemonade 服务器正在运行。
<!-- @device:halo_box -->
> 此工作流程使用 GPT-OSS-120B，该模型已预先安装在 Lemonade 中。您可以在 Lemonade Chat Model 节点设置中将其更改为其他已加载的模型。
<!-- @device:end -->

### 第 5 步：测试工作流程

1. 确保 Lemonade 正在运行且已加载模型
2. 点击画布底部中央的 **Execute workflow**
3. 观察每个节点从左到右依次执行——完成后会变为绿色
4. 双击 **AI Financial News Summarizer** 节点，即可在底部窗格中查看生成的摘要。
5. 双击 **Convert to File** 节点，即可在底部窗格中下载相应的文本文件。

## 了解 AI 代理

AI Financial News Summarizer 使用专为金融分析设计的系统提示词：

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

该代理接收经过清理的新闻数据，并输出带有市场情绪分析的结构化摘要。

### 保存您的工作流程

点击顶部的工作流程名称，可根据需要重命名。工作流程会在您操作时自动保存。

## 后续步骤

- **安排自动化**：将 Manual Trigger 替换为 **Schedule Trigger**，以实现每日运行
- **发送通知**：添加 **Discord**、**Slack** 或 **Email** 节点以接收摘要
- **尝试不同模型**：在 Lemonade Chat Model 节点中更改模型，以体验不同的 LLM
- **更改新闻来源**：将 **Fetch Financial News Feed** 节点指向其他 RSS 源，以关注不同板块或出版物
- **尝试不同后端**：n8n 还支持 [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model)、LM Studio 及其他本地 LLM 后端

### 探索 n8n 模板

n8n 提供数百个预构建的工作流程模板。请浏览官方模板库：

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

搜索 “AI”、“LLM” 或 “automation”，以查找可导入并自定义的工作流程。

如需了解更多信息，请查阅 [n8n 文档](https://docs.n8n.io/)。

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