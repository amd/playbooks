<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **机器翻译。**本页面由英文自动翻译，未经人工审核。其中可能包含错误，某些说明、命令、下载内容、产品可用性或其他内容可能因语言或地区而异。如内容存在任何不一致或差异，应以英文原版 playbook 为准。
<!-- auto-translated-disclaimer:end -->

# 概述

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## 概述

🍋 **Lemonade** 是一款开源的本地 AI 服务器,可让您直接在自己的硬件上运行大语言模型（LLM）、图像生成器和音频模型。它通过行业标准的 **OpenAI API** 对外提供模型服务,因此任何支持 OpenAI 的应用都可以立即与 Lemonade 配合使用。在本教程结束时,您将能够使用 Lemonade 在自己的计算机上本地运行模型。

## 您将学到什么

完成本教程后，您将能够：

* **安装 Lemonade Server** 并验证其是否正常运行。
* **下载并与 LLM 对话**，只需一条命令即可完成。
* **浏览 Web UI**，尝试视觉、语音转文字和图像生成等不同模态。
* **切换 GPU 后端**，在 Vulkan 与 AMD ROCm™ 软件之间切换。
* **构建一个由本地 LLM 驱动的 Python 应用**，使用与 OpenAI 兼容的 API。
<!-- @device:halo_box,halo,stx,krk -->
* **在 AMD 神经处理单元（NPU）上运行模型**，在 AMD Ryzen™ AI 硬件上使用 Hybrid 和 FLM 执行模式。
<!-- @device:end -->

<!-- @device:halo_box,halo,stx,krk -->
## 设置内存配置

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## 检查软件更新

<!-- @require:software-update -->
<!-- @device:end -->

## 安装软件先决条件

在开始之前，请确保您具备以下条件：

- 一台运行 **Windows 11** 或受支持的 **Linux** 发行版（Ubuntu 24.04+、Fedora、Debian）的电脑
- 建议配备 **16 GB 内存**，以运行步骤 1–7 中使用的运行时模型（`Gemma-4-E2B-it-GGUF`，约 3 GB）。如果您想在步骤 6 中使用更大的代码生成模型（`Qwen3.5-35B-A3B-GGUF`，约 20 GB），建议配备 **32 GB 以上**内存。
- 根据您下载的模型不同，需要 **约 4–30 GB 的可用磁盘空间**。本指南中最大的模型约为 20 GB。
- **Python 3.10–3.13**（在 Python 应用部分使用）
- 互联网连接（有线或无线）
<!-- @device:halo_box,halo,stx,krk -->
- [可选] 如果您想在 NPU 上运行模型，需要配备 AMD XDNA 2 NPU（Ryzen AI 300/400/Max 300 系列或 Z2 Extreme），并从 [Ryzen AI Software Installation Instructions](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) 安装最新驱动程序。
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:lemonade-models-gemma-4-e2b,lemonade -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-update-windows timeout=120 hidden=True -->
```powershell
winget upgrade -e --id AMD.LemonadeServer
lemonade --version

# Upgrading runs the Lemonade Server installer, which stops the running server
# to replace its files and does not start it again. Relaunch it so the local API
# on port 13305 is available for the next steps.
if (-not (Get-Process LemonadeServer -ErrorAction SilentlyContinue)) {
  Start-Process "$env:LOCALAPPDATA\lemonade_server\bin\LemonadeServer.exe"
}
```
<!-- @test:end -->

<!-- @test:id=lemonade-chat-gemma-windows timeout=1200 hidden=True -->
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
$entry  = $parsed.data | Where-Object { $_.id -eq "Gemma-4-E2B-it-GGUF" } | Select-Object -First 1
if (-not $entry) { throw "Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "Gemma-4-E2B-it-GGUF"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 500
} | ConvertTo-Json -Depth 5
$out = curl.exe -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions -H "Content-Type: application/json" -d $body
if (-not $out) { throw "Empty response from Lemonade chat/completions" }
Write-Host "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-update-linux timeout=300 hidden=True -->
```bash
sudo apt update
sudo apt install --only-upgrade lemonade-server
lemonade --version
```
<!-- @test:end -->

<!-- @test:id=lemonade-chat-gemma-linux timeout=1200 hidden=True -->
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
    if item.get("id") == "Gemma-4-E2B-it-GGUF":
        entry = item
        break

if entry is None:
    print("Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade")
PY

body='{
  "model": "Gemma-4-E2B-it-GGUF",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 500
}'

out="$(curl -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->

---

## 核心概念 — 本地 AI 服务器的工作原理

在运行模型之前，有必要了解*为什么*要这样设置。Lemonade 是一个**本地模型服务器**，这是一个将 AI 模型加载到内存中并通过 HTTP 将其提供给应用程序的进程，就像云 AI 服务所做的那样。

### 为什么需要服务器？

| 优势 | 对您意味着什么 |
|---------|----------------------|
| **简化集成** | 应用程序与单一 HTTP API 通信，而无需处理特定硬件的 C++ 或 Python 库。 |
| **模型共享** | 一个已加载的模型可以同时服务多个应用，不会产生重复副本占用您的内存。 |
| **云到本地的可移植性** | 为 OpenAI 的云 API 编写的代码，只需更改一个 URL 即可与 Lemonade 配合使用。 |
| **职责分离** | 模型管理、流式传输和容错由服务器处理，开发者可以专注于自己的应用。 |

### OpenAI API 标准

Lemonade 实现了 **OpenAI API**，这与 ChatGPT、Azure OpenAI 以及数十种其他服务使用的接口相同。对话模型很简单：

| 角色 | 发言者 |
|------|---------------|
| **system** | 对模型的指令（人设、约束条件、可用工具） |
| **user** | 来自人类（或应用程序）发送给模型的消息 |
| **assistant** | 模型生成的响应 |

这意味着任何支持 OpenAI 的库或应用，只需在 Lemonade Server 运行时将其指向 `http://localhost:13305/api/v1`，即可与 Lemonade 通信。

## 主要活动 — 您的首次本地 AI 对话

让我们下载一个 LLM 并与之对话，将 AI 完全运行在您自己的机器上。

### 步骤 1：下载并运行模型

Lemonade 自带一个精选的模型库。让我们从 **Gemma-4-E2B-it** 开始，这是一个功能强大且体积紧凑的模型，并支持视觉功能。打开终端并运行：

```
lemonade run Gemma-4-E2B-it-GGUF
```

这一条命令完成三件事：

1. 如果尚未下载，则从 Hugging Face **下载**该模型（约 3 GB）。（可能需要一些时间）
2. 在端口 13305 上**启动** Lemonade Server 进程。
3. **打开 Lemonade App**，以便您可以开始与模型对话。


<!-- @os:windows -->
在 Windows 上，Lemonade App 会自动启动，您可以立即开始对话。如果您安装的是 `minimal.msi` 软件包，则不包含该应用。要开始对话，请打开浏览器并访问 `http://localhost:13305`。
<!-- @os:end -->

<!-- @os:linux -->
在 Linux 上，打开浏览器并导航到 `http://localhost:13305` 即可访问 Web 应用。
<!-- @os:end -->

试着输入一个问题：

```
What are three fun facts about lemons?
```

模型将直接在聊天窗口中回复。**恭喜！您已在本地运行了一个大语言模型。**

![显示日志的 Lemonade App](../../dependencies/assets/ChatwithLogs.png)

在 Lemonade App 的服务器日志窗格中，您可以在每次响应后找到有关模型性能的遥测数据。例如：

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### 第 2 步：探索 Web 界面与不同模态

Lemonade 内置了一个 Web 界面，你可以在其中：

- **交互**：在熟悉的聊天窗口中与已加载的模型互动
- **浏览模型**：在模型管理器（Model Manager）标签页中浏览模型
- **下载新模型**：一键下载

在 Web UI 的 **Model Manager** 标签页中，尝试按配方（Recipe）或按类别（Category）切换浏览不同的模型模态：

1. **视觉（Vision）：** 你已经加载的 `Gemma-4-E2B-it-GGUF` 模型支持视觉功能。将图片粘贴到聊天框中，并让模型描述它。
2. **图像生成（Image generation）：** 在 Image 类别中，从模型管理器下载一个图像模型，例如 `SDXL-Turbo`，然后使用 Lemonade 图像生成器输入提示词，在本地生成图像。
3. **音频（Audio）：** 在 Audio 类别中，下载一个音频模型，例如可以进行语音转文字的 `Whisper-Tiny`。提供一段录音即可在本地进行转录。对于文本转语音，可以尝试 Speech 类别中的模型，例如 `kokoro-v1`。

![Lemonade 多模态](../../dependencies/assets/multi_modality.png)

### 第 3 步：尝试使用不同后端运行模型

如果你将鼠标悬停在 Lemonade App 中的某个模型上，会看到一个齿轮图标。点击该图标可以为该模型选择选项，包括选择你想要的后端。

默认情况下，Lemonade 使用 Vulkan 进行 GPU 加速。如果你拥有受支持的 AMD 独立显卡，可以切换到 ROCm。

![Lemonade 选择后端](../../dependencies/assets/lemonademodeloptions.png)

要管理已安装的后端，请点击最左侧列中的后端按钮。

此外，你也可以使用以下命令来指定后端：

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

你还可以通过环境变量 `LEMONADE_LLAMACPP` 设置默认后端，可选值为：`vulkan`、`rocm` 或 `cpu`。

---

## 深入探索 — 使用 Python 构建一个 AI 驱动的应用

本地 AI 服务器的真正威力在于：任何应用都可以仅用几行代码连接到它。为了证明这一点，我们来构建一个小巧但功能完整的**学习闪卡生成器**，你给它一个主题，它就会生成闪卡，你还可以交互式地自我测验。

### 第 4 步：启动服务器

确认 Lemonade 服务器正在运行。安装完成后，它通常会在后台自动启动。要进行确认，请运行：

```
lemonade status
```

你应该会看到类似这样的消息：`Server is running on port 13305`。

如果服务器未在运行，可以通过打开 Lemonade 应用来启动它。使用默认端口 **13305**（你可以从托盘图标中确认或选择此端口）。

### 第 5 步：安装 OpenAI Python 客户端

在终端中，创建一个 venv 并使用以下命令安装 OpenAI Python 客户端：
<!-- @os:linux -->
```bash
# Your specific version of Linux may have different commands
sudo apt update
sudo apt install -y python3-venv
python3 -m venv lemonade-env
source lemonade-env/bin/activate
pip install openai
```
<!-- @os:end -->
<!-- @os:windows -->
```powershell
python -m venv lemonade-env
lemonade-env\Scripts\activate
pip install openai
```
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=env-check-windows timeout=300 hidden=True -->
```powershell
python --version
where.exe python
where.exe pip
python -c "import sys; print(sys.executable)"
python -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=env-check-linux timeout=300 hidden=True -->
```bash
python3 --version
which python3
which pip3
python3 -c "import sys; print(sys.executable)"
python3 -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=pip-install-openai-windows timeout=300 hidden=True -->
```powershell
python -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=pip-install-openai-linux timeout=300 hidden=True -->
```bash
python3 -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-openai-import-windows timeout=120 hidden=True -->
```powershell
python -m pip show openai
python -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=python-openai-import-linux timeout=120 hidden=True -->
```bash
python3 -m pip show openai
python3 -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

### 第 6 步：构建闪卡应用

让我们下载另一个模型来生成代码：`Qwen3.5-35B-A3B-GGUF`。这是一个较大（约 20 GB）且性能出色的模型，最适合拥有 32 GB 以上内存的系统。如果你的可用内存较少，可以改用 `Qwen3.5-9B-GGUF`（约 6 GB）。

你可以从 UI 中下载它，也可以运行以下命令：
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

将以下提示词输入到 Lemonade Chat UI 中，以生成一个简单闪卡应用的代码。

我们将使用 Qwen3.5-35B-A3B-GGUF（一个更擅长编写代码的大型模型）来生成我们的 Python 应用，而该应用本身在运行时会调用 Gemma-4-E2B-it-GGUF（你已经下载的较小模型）。生成的代码随后可以复制到你选择的文件中，在 Python 中运行。

```
Generate a Python script that uses the OpenAI Python library to call a local LLM and create an interactive flashcard study tool.

Connection details:
- Base URL: http://localhost:13305/api/v1
- API key: "lemonade"
- Model to use: "Gemma-4-E2B-it-GGUF"

Structure:

1. A `generate_flashcards(topic, count=5)` function that:
   - Sends a system message instructing the LLM to return ONLY a JSON array of objects with "question" and "answer" fields.
   - Handles malformed JSON gracefully.
   - Returns the parsed list of cards, or an empty list if parsing fails.

2. A `quiz(cards)` function that shuffles the cards and, for each card:
   - Prints `--- Card i/N ---`.
   - Prints `Q: <question>`.
   - Waits for the user to press Enter ("Press Enter to reveal the answer...").
   - Prints `A: <answer>`.
   - Asks "Did you get it right? (y/n): " and tracks the score.
   - At the end, prints `🏆 Score: <score>/<total>`.

3. A main loop that:
   - Prints a `🍋 Lemonade Flashcard Generator` banner on startup.
   - Asks the user for a topic (typing "quit" exits).
   - Prints `✨ Generating N flashcards on: <topic>`.
   - Calls `generate_flashcards` and lists the generated questions as an indented numbered list (`  1. ...`).
   - Offers to start the quiz.
```

> **提示**：我们通过精心设计提示词，并采用双模型系统来优化资源与速度，遵循了标准的工程实践。

为方便起见，我们提供了示例输出 [`flashcards.py`](assets/flashcards.py)。你可以随意将其下载到你的目录中。无论采用哪种方式，你现在都应该拥有一个可以运行的 Python 文件。

<!-- @os:windows -->
<!-- @test:id=lemonade-python-smoke-windows timeout=900 hidden=True -->
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

Start-Sleep -Seconds 5
python lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-python-smoke-linux timeout=600 hidden=True -->
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

sleep 5
python3 lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


### 第 7 步：运行生成的代码

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**你应该会看到如下内容：**

```
🍋 Lemonade Flashcard Generator
================================
Powered by a local LLM running on your own hardware.

Enter a topic (or "quit" to exit): the solar system

✨ Generating 5 flashcards on: the solar system

Generated 5 cards!

  1. Which planet is closest to the Sun?
  2. What is the largest planet in our solar system?
  3. Which planet is known as the "Red Planet"?
  4. How many moons does Earth have?
  5. What separates the inner planets from the outer planets?

Start quiz? (y/n): y

--- Card 1/5 ---
Q: What is the largest planet in our solar system?

Press Enter to reveal the answer...
A: Jupiter is the largest planet, with a diameter of about 139,820 km.

Did you get it right? (y/n): y

...

🏆 Score: 4/5
```

仅用约 150 行代码，你就构建了一个由本地 LLM 驱动的功能齐全的学习工具。无需管理任何 API 密钥，没有使用成本，且任何数据都不会离开你的本地机器。

> **关键点：** 请注意，`client = OpenAI(base_url=...)` 这一行是将该应用与 Lemonade（而非 OpenAI 云服务）联系起来的*唯一*内容。其余代码与你为任何兼容 OpenAI 的服务所编写的代码完全相同。如果你曾经使用过 OpenAI 的 Python 库，那么你已经知道如何使用 Lemonade 构建应用了。

### 这展示了什么

这个小应用演示了几种真实世界中的集成模式：

| 模式 | 出现位置 |
|---------|-----------------|
| **系统提示词** | `"system"` 消息告诉 LLM 以结构化 JSON 格式输出 |
| **结构化输出** | 应用将 LLM 的响应解析为 JSON，以构建闪卡 |
| **无状态请求** | 每次调用 `generate_flashcards()` 都是相互独立的 |
| **错误处理** | `try/except` 可以优雅地处理 LLM 输出不是有效 JSON 的情况 |

这些相同的模式可以扩展到任何应用中，例如聊天机器人、代码助手、内容生成器、自动化工具等。

#### 额外挑战

* 如果想挑战更高难度，可以尝试参考[此处](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py)提供的示例，更新该应用，使其能够为用户朗读闪卡内容。

---

<!-- @device:halo_box,halo,stx,krk -->
## 在 NPU 上运行模型（可选）

如果您拥有 Ryzen AI 300/400/Max 300 系列或 Z2 Extreme，您的设备内置了**神经处理单元（NPU）**，这是一款专为 AI 工作负载设计的专用芯片。在 NPU 上运行模型比使用 GPU 更节能，非常适合后台 AI 任务、较长的会话以及电池供电的使用场景。

Lemonade 支持三种 NPU 执行模式，它们都在相同的 OpenAI API 背后透明运行：

| 模式 | 工作原理 | Recipe | 示例模型 |
|------|-------------|--------|----------------|
| **混合模式（NPU + iGPU）** | NPU 处理提示词，iGPU 生成 token | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **仅 NPU** | 整个推理过程都在 NPU 上运行 | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | 在 NPU 上使用 FastFlowLM 引擎，针对 AMD XDNA2 进行优化 | FLM (`flm`) | qwen3.5-4b-FLM |

### 要求

- **AMD Ryzen AI 300/400 系列或 Z2 系列**处理器
- 对于 **FLM** 模型：您可以在 Lemonade 应用内安装 FLM 运行时，或者在运行 FLM 模型时，Lemonade 会自动安装 FLM 运行时。要了解更多关于 FastFlowLM 的信息，请参阅[此处](https://fastflowlm.com/docs/)。


### 第 8 步：运行混合模式模型

混合模式模型将工作分配给 NPU 和 iGPU，以在速度和效率之间取得良好的平衡。在 Lemonade App 中，从 `Ryzen AI LLM` 列表中选择一个模型，例如 `Qwen3-4B-Hybrid`，或使用以下命令运行：

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade 会自动检测您的 NPU 并安装 **Ryzen AI LLM** 后端。

> **底层发生了什么？** 当您发送消息时，NPU 会并行处理您的整个提示词（这称为“预填充”）。然后，iGPU 接管并逐个 token 生成响应（这称为“解码”）。这种混合方式充分发挥了每块芯片的优势。

### 第 9 步：运行 FLM 模型

FastFlowLM（FLM）模型专门针对 AMD 的 XDNA2 NPU 架构进行了优化，在同等规模下速度可以非常快。例如，从 `FastFlowLM NPU` 列表中选择 `qwen3.5-4b-FLM`，或使用以下命令：

<!-- @os:windows -->
在 Windows 上启用 `FastFlowLM`：

* 打开 `Backends Manager` 菜单。
* 找到 `FastFlowLM NPU` 后端类别。
* 点击 Install NPU。
* 安装完成后，大约 36 个默认模型将出现在 FFLM 下拉菜单中。
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
首次启动 `Lemonade` 应用时，`FastFlowNPU` 后端默认未启用。
本地应用会打开安装页面，引导您完成设置。

在 Linux 上启用 `FastFlowLM`：

* 打开 `Lemonade` 应用。
* 访问[官方 FLM](https://lemonade-server.ai/flm_npu_linux.html)文档，选择您的 Linux 发行版，并按照 FLM 的安装步骤进行操作。
* 按照安装页面上的说明启用 backports。
* 从[标签页面](https://github.com/FastFlowLM/FastFlowLM/tags)下载最新的 `v0.9.x` 版本。

<!-- @device:halo_box -->
>[!Note]
对于 AMD Halo 开发者平台，请确保选择 Debian 13。
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* 安装下载的 `.deb` 软件包。
* 推荐：退出 `Lemonade App` 并重新打开，以便检测到更改。
* 推荐：打开 `Backends Manager` 并点击 Install `FastFlowNPU` Backend。
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
安装成功后，您应该会看到 **Lemonade Desktop App** 内的**下载管理器**中 `flm:npu` 已完成。
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
然后，您可以选择任何可用的 FFLM 模型并开始使用 NPU 后端。

对于特定模型，请从[模型页面](https://fastflowlm.com/docs/models/qwen/)下载所需的模型，并使用文档中提供的 Shell 命令进行验证。
```
flm run qwen3.5-4b-FLM
```
或通过 
```
lemonade run qwen3.5-4b-FLM
```

FLM 模型包括一些最流行的架构（Gemma 3、Qwen 3、Llama 3 和 DeepSeek R1），大小从不到 1 GB 到超过 13 GB 不等。
Lemonade 会自动检测您的 NPU 并安装 **FastFlowLM NPU** 后端。

<!-- @os:windows -->
> **提示：** 为获得最佳 NPU 性能，请启用 turbo 模式：
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### 切换模型

第 6 步中的闪卡应用同样适用于 NPU 模型，只需更改模型名称：

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## 后续步骤

您现在已经在自己的硬件上运行了一个本地 AI 服务器，以下是接下来可以探索的内容：

1. **连接您喜欢的应用**：Lemonade 开箱即用，支持 [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk)、[Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/)、[Continue](https://lemonade-server.ai/docs/server/apps/continue/)、[n8n](https://n8n.io/integrations/lemonade-model/) 以及[更多应用](https://lemonade-server.ai/marketplace)。

2. **浏览更多模型**：探索完整的[模型库](https://lemonade-server.ai/docs/server/server_models/)，查找针对编程、推理、视觉等场景优化的模型。使用 Lemonade App 或 `lemonade list` 查看可用模型。

3. **解锁 ROCm GPU 加速**：如果您拥有受支持的 AMD GPU，请切换到 ROCm 后端：`lemonade config set llamacpp.backend=rocm`。请参阅[受支持的 AMD GPU](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations)。

4. **阅读完整的 API 规范**：Lemonade 支持聊天补全、嵌入、音频转录、图像生成、文本转语音等功能。请参阅[服务器规范](https://lemonade-server.ai/docs/server/server_spec/)以了解每个端点。

5. **参与贡献**：Lemonade 是开源项目。请查看[贡献指南](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md)，并寻找[适合新手的问题](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)。

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