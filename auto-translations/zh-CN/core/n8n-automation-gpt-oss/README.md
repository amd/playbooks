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
> 此工作手册需要至少 **32GB** 的系统内存。
<!-- @device:end -->

n8n 是一个工作流自动化平台，可让你使用可视化的基于节点的编辑器连接各种应用和服务。

本工作手册将教你如何搭建一个由 AI 驱动的财经新闻摘要生成器，该工具会抓取 AP News 的商业新闻板块、提取关键headlines，并使用本地运行在你系统上的 LLM 生成面向投资者的摘要。

## 你将学到什么

- 如何安装并启动 n8n
- 导入并配置预构建的工作流
- 使用原生的 n8n 集成连接到 Lemonade
- 了解工作流节点与数据流

## 什么是 Lemonade？

[Lemonade](https://lemonade-server.ai) 是一个专为 AMD 硬件打造的本地 LLM 服务平台。它提供了与 OpenAI 兼容的 API，完全在你的本地机器上运行——你的数据永远不会离开你的设备。

在本工作手册中，我们使用 Lemonade 来提供本地 LLM 服务，n8n 会连接到该服务以执行 AI 驱动的任务。

n8n 内置了**原生 Lemonade 节点**（`Lemonade Chat Model`），提供了一流的集成体验——无需手动配置。这使得将本地 LLM 连接到自动化工作流变得非常简单。

## 设置内存配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 检查软件更新

<!-- @require:software-update -->
<!-- @device:end -->

## 安装软件先决条件
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

## 安装 n8n
<!-- @os:windows -->
使用 npm 全局安装 n8n。

> **注意**：你可能会看到一些 npm 警告，这是正常现象。

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
> **提示**：Windows 用户在运行某些 PowerShell 命令之前，可能需要修改 PowerShell 执行策略（例如
> 将其设置为 RemoteSigned 或 Unrestricted）。
<!-- @os:end -->


<!-- @os:windows -->
> **PATH 问题**：如果 `n8n --version` 提示命令未找到，请确保你的 npm 全局 bin 目录已添加到用户 `PATH` 中。通常的安装路径位于 `C:\Users\<username>\AppData\Roaming\npm`。
> 将其添加到用户路径中（编辑系统环境变量 > 环境变量 > 编辑用户路径），然后重新加载终端。

<!-- @os:end -->

<!-- @os:linux -->
接下来我们将使用 Podman 服务来容器化我们的 n8n 安装。

请将以下文件下载到你选择的目录中：[compose.yml](assets/compose.yml)

在该目录中，运行以下命令：
```bash
podman compose up -d
```

这将安装 n8n 并写入持久化存储。

在浏览器地址栏中输入 `localhost:5678` 以启动 n8n。
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
n8n 会启动一个本地 Web 服务器。按下 `'o'` 键或打开浏览器访问 `http://localhost:5678` 以进入编辑器。
<!-- @os:end -->


> **提示**：使用 n8n 期间请保持终端窗口打开。关闭它可能会导致服务器停止运行。

## 启动 Lemonade

Lemonade 是运行模型并连接到 n8n 的本地服务器。

<!-- @os:linux -->
点击任务栏中的 Lemonade 图标打开 Lemonade GUI。你可以在这里浏览模型、后端，并加载预安装的模型。
<!-- @os:end -->

<!-- @os:windows -->
点击 Lemonade 图标打开 Lemonade GUI。右键点击托盘图标以打开该应用。之后，你可以添加模型、后端，并加载预安装的模型。
<!-- @os:end -->

>**提示**：运行后，Lemonade GUI 也可以通过 http://localhost:13305 访问。

或者，你也可以打开终端并运行 `lemonade list` 查看已安装的模型。然后运行：

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

### 步骤 1：注册或登录 n8n

首次打开 n8n 时，系统会提示你创建账户或登录：

1. 在浏览器中打开 `http://localhost:5678`
2. 使用你的邮箱创建一个新的本地账户，如果你已有账户则直接登录
3. 登录后，你将看到 n8n 仪表盘

> **提示**：如果账户被锁定，可以尝试运行 `n8n user-management:reset`

### 步骤 2：导入工作流

我们已提供了一个预构建的工作流，你可以直接导入：

1. 下载以下工作流文件：[financial-news-workflow.json](assets/financial-news-workflow.json)
2. 点击 **Start from Scratch** 打开工作流编辑器。或者，点击左上角的 + 按钮，然后选择 **Add workflow**。
3. 点击右上角的 **...** 菜单（三个点），选择 **Import from file**
4. 选择下载好的 `financial-news-workflow.json` 文件
5. 工作流将出现在画布上
### 第 3 步:了解工作流

导入的工作流包含 9 个已连接的节点:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| 节点 | 用途 |
|------|---------|
| **When clicking 'Execute workflow'** | 用于启动工作流的手动触发器 |
| **Fetch Financial News Webpage** | 向 `https://apnews.com/business` 发送 HTTP GET 请求 |
| **Delay to Ensure Page Load** | 用于确保页面内容完全加载的等待节点 |
| **Extract News Headlines & Text** | HTML 节点,使用 CSS 选择器提取标题、编辑精选、头条新闻和地区新闻 |
| **Clean Extracted News Data** | Set 节点,将所有提取的数据合并到一个文本字段中 |
| **AI Financial News Summarizer** | AI 代理,使用金融分析师系统提示词处理新闻 |
| **Lemonade Chat Model** | 连接到运行 LLM 的本地 Lemonade 服务器 |
| **Structured Output Parser** | 将 AI 输出格式化为结构化 JSON |
| **Convert to File** | 将摘要转换为可下载的文件 |

### 第 4 步:配置 Lemonade 凭证

在运行工作流之前,您需要将其连接到本地 Lemonade 服务器:

1. 在 n8n 中双击 **Lemonade Chat Model** 节点
2. 在下拉菜单 **Credential to connect with** 中选择 **Create New Credential**
3. 在下表中输入相应值,然后点击保存。
4. 选择您在 Lemonade Server 中已加载的相关模型。

  | 字段 | 值 |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **注意**:在测试之前,请在终端中运行 `lemonade status` 以确认 Lemonade 服务器正在运行。
<!-- @device:halo_box -->
> 此工作流使用 GPT-OSS-120B,该模型已预装在 Lemonade 中。您可以在 Lemonade Chat Model 节点设置中将其更改为其他已加载的模型。
<!-- @device:end -->

### 第 5 步:测试工作流

1. 确保 Lemonade 正在运行且已加载模型
2. 点击画布底部中央的 **Execute workflow**
3. 观察每个节点从左到右依次执行——完成后会变为绿色
4. 双击 **AI Financial News Summarizer** 节点,在底部面板中查看生成的摘要。
5. 双击 **Convert to File** 节点,在底部面板中下载相应的文本文件。

## 了解 AI 代理

AI Financial News Summarizer 使用专为金融分析设计的系统提示词:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

该代理接收清洗后的新闻数据,并输出带有市场情绪的结构化摘要。

### 保存您的工作流

点击顶部的工作流名称,如果需要可以重命名。工作流会在您操作时自动保存。

## 后续步骤

- **安排自动化任务**:将手动触发器替换为 **Schedule Trigger**,以实现每日运行
- **发送通知**:添加 **Discord**、**Slack** 或 **Email** 节点以接收摘要
- **尝试不同的模型**:在 Lemonade Chat Model 节点中更改模型,以试用不同的 LLM
- **自定义提取内容**:修改 HTML Extract 节点的 CSS 选择器,以定位不同的新闻板块
- **尝试不同的后端**:n8n 还支持 [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model)、LM Studio 以及其他本地 LLM 后端

### 探索 n8n 模板

n8n 提供数百个预构建的工作流模板。请浏览官方模板库:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

搜索“AI”“LLM”或“automation”,以查找可导入并自定义的工作流。

如需了解更多信息,请查阅 [n8n 文档](https://docs.n8n.io/)。

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