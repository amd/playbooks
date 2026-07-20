<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> 本手册使用了 GitHub 无法渲染的特殊标签。请访问 [amd.com/playbooks](https://amd.com/playbooks) 以正确预览本内容。
<!-- @github-only:end -->

## 概述

🍋 **Lemonade** 是一个开源的本地 AI 服务器，可让你直接在自己的硬件上运行大语言模型（LLM）、图像生成器和音频模型。它通过行业标准的 **OpenAI API** 公开这些模型，因此任何能与 OpenAI 配合使用的应用都可以立即与 Lemonade 协同工作。在本手册结束时，你将能够使用 Lemonade 在你的计算机上本地运行模型。

## 你将学到什么

在完成本手册后，你将能够：

* **安装 Lemonade Server** 并验证其是否正在运行。
* **下载并与 LLM 对话**，只需一条命令即可完成。
* **探索 Web UI**，并尝试不同的模态，例如视觉、语音转文本和图像生成。
* **在 GPU 后端之间切换**，包括 Vulkan 和 AMD ROCm™ 软件。
* **构建一个由本地 LLM 驱动的 Python 应用**，使用兼容 OpenAI 的 API。
<!-- @device:halo_box,halo,stx,krk -->
* **在 AMD 神经处理单元（NPU）上运行模型**，在 AMD Ryzen™ AI 硬件上使用 Hybrid 和 FLM 执行模式。
<!-- @device:end -->

## 设置内存配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 检查软件更新

<!-- @require:software-update -->
<!-- @device:end -->

## 安装软件先决条件

在开始之前，请确保你具备以下条件：

- 一台运行 **Windows 11** 或受支持的 **Linux** 发行版（Ubuntu 24.04+、Fedora、Debian）的 PC
- 建议配备 **16 GB 内存**，用于运行步骤 1–7 中使用的模型（`Gemma-4-E2B-it-GGUF`，约 3 GB）。如果你想在步骤 6 中使用更大的代码生成模型（`Qwen3.5-35B-A3B-GGUF`，约 20 GB），建议配备 **32 GB 及以上**内存。
- **约 4–30 GB 的可用磁盘空间**，具体取决于你下载的模型。本指南中最大的模型约为 20 GB。
- **Python 3.10–3.13**（用于 Python 应用部分）
- 互联网连接（有线或无线）
<!-- @device:halo_box,halo,stx,krk -->
- [可选] 如果你想在 NPU 上运行模型，需要一块 AMD XDNA 2 NPU（Ryzen AI 300/400/Max 300 系列或 Z2 Extreme），并安装 [Ryzen AI 软件安装说明](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) 中提供的最新驱动程序。
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
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

在运行模型之前，有必要了解*为什么*要这样设置。Lemonade 是一个**本地模型服务器**，它是一个将 AI 模型加载到内存中，并通过 HTTP 将其公开给应用程序的进程，就像云端 AI 服务一样。

### 为什么需要服务器？

| 优势 | 对你意味着什么 |
|---------|----------------------|
| **简化集成** | 应用程序只需与一个 HTTP API 通信，而无需处理特定于硬件的 C++ 或 Python 库。 |
| **共享模型** | 单个已加载的模型可以同时服务于多个应用程序，不会有重复副本占用你的内存。 |
| **云到本地的可移植性** | 为 OpenAI 云 API 编写的代码只需更改一个 URL，即可与 Lemonade 配合使用。 |
| **关注点分离** | 模型管理、流式传输和容错都由服务器处理，开发者可以专注于自己的应用程序。 |

### OpenAI API 标准

Lemonade 实现了 **OpenAI API**，这与 ChatGPT、Azure OpenAI 以及数十种其他服务所使用的接口相同。对话模型很简单：

| 角色 | 谁在说话 |
|------|---------------|
| **system** | 给模型的指令（角色设定、约束条件、可用工具） |
| **user** | 来自人类（或应用程序）发送给模型的消息 |
| **assistant** | 模型生成的响应 |

这意味着任何支持 OpenAI 的库或应用程序，只需在 Lemonade Server 运行时将其指向 `http://localhost:13305/api/v1`，即可与 Lemonade 通信。

## 主要活动 — 你的第一次本地 AI 对话

让我们下载一个 LLM 并与它对话，让 AI 完全在你自己的机器上运行。

### 步骤 1：下载并运行模型

Lemonade 附带一个精选的模型库。让我们从 **Gemma-4-E2B-it** 开始，这是一个功能强大且体积小巧的模型，并支持视觉能力。打开终端并运行：

```
lemonade run Gemma-4-E2B-it-GGUF
```

这一条命令完成了三件事：

1. **下载** 模型（约 3 GB），如果尚未从 Hugging Face 下载的话。（可能需要一些时间）
2. **启动** Lemonade Server 进程，监听端口 13305。
3. **打开 Lemonade App**，以便你可以开始与模型对话。


<!-- @os:windows -->
在 Windows 上，Lemonade App 会自动启动，你可以立即开始对话。如果你安装的是 `minimal.msi` 软件包，则不包含该应用。要开始对话，请打开你的网络浏览器并访问 `http://localhost:13305`。
<!-- @os:end -->

<!-- @os:linux -->
在 Linux 上，打开你的浏览器并导航到 `http://localhost:13305` 以访问 Web 应用。
<!-- @os:end -->

试着输入一个问题：

```
What are three fun facts about lemons?
```

模型将直接在聊天窗口中作出回应。**恭喜！你正在本地运行一个大语言模型。**

![显示日志的 Lemonade App](../../dependencies/assets/ChatwithLogs.png)

在 Lemonade App 的服务器日志窗格中，你可以在每次响应后找到有关模型性能的遥测数据。例如：

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### 第 2 步：探索 Web 界面和不同的模态

Lemonade 内置了一个 Web 界面，你可以在其中：

- **交互**：在熟悉的聊天窗口中与已加载的模型互动
- **浏览模型**：在 Model Manager 标签页中浏览模型
- **下载新模型**：一键下载

尝试使用 Web UI 中的 **Model Manager** 标签页在不同模态之间切换，你可以按 Recipe 或 Category 浏览模型：

1. **视觉：** 你已经加载的 `Gemma-4-E2B-it-GGUF` 模型支持视觉功能。将一张图片粘贴到聊天框中，并让模型描述它。
2. **图像生成：** 在 Image 类别中，从 Model Manager 下载一个图像模型，例如 `SDXL-Turbo`，然后使用 Lemonade Image Generator 输入提示词并在本地生成图像。
3. **音频：** 在 Audio 类别中，下载一个音频模型，例如 `Whisper-Tiny`，它可以进行语音转文本。提供一段录音以在本地对其进行转录。对于文本转语音，可以尝试 Speech 类别中的某个模型，例如 `kokoro-v1`。

![Lemonade 的多模态能力](../../dependencies/assets/multi_modality.png)

### 第 3 步：尝试使用不同后端运行模型

如果你将鼠标悬停在 Lemonade App 中的某个模型上，会看到一个齿轮图标。点击它可以为该模型选择选项，包括选择你想要的后端。

默认情况下，Lemonade 使用 Vulkan 进行 GPU 加速。如果你有受支持的 AMD 独立 GPU，可以切换到 ROCm。

![Lemonade 选择后端](../../dependencies/assets/lemonademodeloptions.png)

要管理已安装的后端，请点击最左侧列中的后端按钮。

或者，你也可以使用以下命令指定后端：

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

你还可以通过环境变量 `LEMONADE_LLAMACPP` 设置默认后端，可选值为：`vulkan`、`rocm` 或 `cpu`。

---

## 深入了解 —— 使用 Python 构建一个 AI 驱动的应用

本地 AI 服务器真正强大之处在于，任何应用程序都可以仅用几行代码就连接到它。为了证明这一点，让我们构建一个小而实用的**学习闪卡生成器**：你给它一个主题，它会生成闪卡，你可以进行互动测验。

### 第 4 步：启动服务器

确认 Lemonade 服务器正在运行。安装完成后，它通常会在后台自动启动。要进行验证，请运行：

```
lemonade status
```

你应该会看到类似这样的信息：`Server is running on port 13305`。

如果服务器未运行，请打开 Lemonade 应用来启动它。使用默认端口 **13305**（你可以在托盘图标中确认或选择该端口）。

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

让我们下载一个不同的模型来生成代码：`Qwen3.5-35B-A3B-GGUF`。这是一个较大（约 20 GB）且性能强劲的模型，最适合拥有 32 GB 以上内存的系统。如果你的可用内存较少，可以改用 `Qwen3.5-9B-GGUF`（约 6 GB）。

你可以从 UI 中下载它，或运行以下命令：
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

将以下提示词输入到 Lemonade Chat UI 中，以生成一个简单闪卡应用的代码。

我们将使用 Qwen3.5-35B-A3B-GGUF（一个更擅长编写代码的更大模型）来生成我们的 Python 应用，而应用本身在运行时会调用 Gemma-4-E2B-it-GGUF（你已经下载的较小模型）。生成的代码随后可以复制到你选择的文件中，并在 Python 中运行。

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

> **提示**：我们通过精心设计提示词，并使用双模型系统来优化资源和速度，遵循了标准的工程实践。

为方便起见，我们提供了示例输出 [`flashcards.py`](assets/flashcards.py)。你可以随意将其下载到自己的目录中。无论哪种方式，你现在都应该拥有一个可以运行的 Python 文件。

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

仅用大约 150 行代码，你就构建了一个由本地 LLM 驱动的功能齐全的学习工具。无需管理任何 API 密钥，没有使用成本，也没有任何数据离开你的机器。

> **关键点：** 注意 `client = OpenAI(base_url=...) ` 这一行是将该应用与 Lemonade（而非 OpenAI 的云服务）联系起来的*唯一*要素。其余代码与你针对任何兼容 OpenAI 的服务所编写的代码完全相同。如果你曾经使用过 OpenAI Python 库，那么你已经知道如何使用 Lemonade 构建应用了。

### 这展示了什么

这个小应用展示了几种真实世界中的集成模式：

| 模式 | 出现位置 |
|---------|-----------------|
| **系统提示词** | `"system"` 消息告诉 LLM 输出结构化的 JSON |
| **结构化输出** | 应用将 LLM 的响应解析为 JSON 以构建闪卡 |
| **无状态请求** | 每次调用 `generate_flashcards()` 都是独立的 |
| **错误处理** | `try/except` 优雅地处理了 LLM 输出不是有效 JSON 的情况 |

这些相同的模式可以扩展到任何应用中，例如聊天机器人、代码助手、内容生成器、自动化工具等。

#### 额外挑战

* 为了增加挑战难度，可以尝试参考[这里](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py)提供的示例，更新应用使其能够为用户朗读闪卡内容。

---

<!-- @device:halo_box,halo,stx,krk -->
## 在 NPU 上运行模型（可选）

如果你的设备是 Ryzen AI 300/400/Max 300 系列或 Z2 Extreme，那么你的设备内置了 **神经处理单元（NPU）**，这是一款专为 AI 工作负载设计的专用芯片。在 NPU 上运行模型比使用 GPU 更节能，因此非常适合后台 AI 任务、长时间会话以及电池供电场景。

Lemonade 支持三种 NPU 执行模式，它们在同一个 OpenAI API 背后对用户完全透明：

| 模式 | 工作原理 | Recipe | 示例模型 |
|------|-------------|--------|----------------|
| **Hybrid（NPU + iGPU）** | NPU 处理提示，iGPU 生成 token | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **仅 NPU** | 整个推理过程都在 NPU 上运行 | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | 在 NPU 上使用 FastFlowLM 引擎，针对 AMD XDNA2 进行优化 | FLM (`flm`) | qwen3.5-4b-FLM |

### 要求

- **AMD Ryzen AI 300/400 系列或 Z2 系列** 处理器
- 对于 **FLM** 模型：可以在 Lemonade 应用内安装 FLM 运行时，或者在运行 FLM 模型时 Lemonade 会自动安装 FLM 运行时。要了解更多关于 FastFlowLM 的信息，请参阅[此处](https://fastflowlm.com/docs/)。


### 第 8 步：运行 Hybrid 模型

Hybrid 模型将工作分配给 NPU 和 iGPU，从而在速度和能效之间取得良好的平衡。在 Lemonade 应用中，从 `Ryzen AI LLM` 列表中选择一个模型，例如 `Qwen3-4B-Hybrid`，或者使用以下命令运行：

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade 会自动检测你的 NPU，并安装 **Ryzen AI LLM** 后端。

> **幕后发生了什么？** 当你发送一条消息时，NPU 会并行处理整个提示（这称为“预填充”/prefill）。然后，iGPU 接管，逐个 token 生成响应（这称为“解码”/decode）。这种混合方式充分发挥了每颗芯片的优势。

### 第 9 步：运行 FLM 模型

FastFlowLM（FLM）模型专门针对 AMD 的 XDNA2 NPU 架构进行了优化，就其体量而言速度可以非常快。例如，从 `FastFlowLM NPU` 列表中选择 `qwen3.5-4b-FLM`，或者使用以下命令：

<!-- @os:windows -->
要在 Windows 上启用 `FastFlowLM`：

* 打开 `Backends Manager` 菜单。
* 找到 `FastFlowLM NPU` 后端类别。
* 点击 Install NPU。
* 安装完成后，约 36 个默认模型将显示在 FFLM 下拉菜单中。
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
首次启动 `Lemonade` 应用时，`FastFlowNPU` 后端默认未启用。
本地应用会打开安装页面，引导你完成设置。

要在 Linux 上启用 `FastFlowLM`：

* 打开 `Lemonade` 应用。
* 访问[官方 FLM](https://lemonade-server.ai/flm_npu_linux.html)文档，选择你的 Linux 发行版并按照 FLM 的安装步骤进行操作。
* 按照安装页面上的说明启用 backports。
* 从[标签页面](https://github.com/FastFlowLM/FastFlowLM/tags)下载最新的 `v0.9.x` 版本。'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
对于 AMD Halo Developer Platform，请务必选择 Debian 13。
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
* 建议：退出 `Lemonade App` 并重新打开，以便系统检测到变更。
* 建议：打开 `Backends Manager` 并点击 Install `FastFlowNPU` Backend。
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
安装成功后，你应该会在 **Lemonade Desktop App** 内的 **Download Manager** 中看到 `flm:npu` 已完成。
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
之后你就可以选择任意可用的 FFLM 模型，并开始使用 NPU 后端。

对于特定模型，可从[模型页面](https://fastflowlm.com/docs/models/qwen/)下载所需模型，并使用文档中提供的 Shell 命令进行验证。
```
flm run qwen3.5-4b-FLM
```
或通过 
```
lemonade run qwen3.5-4b-FLM
```

FLM 模型涵盖了一些最流行的架构（Gemma 3、Qwen 3、Llama 3 和 DeepSeek R1），大小从不到 1 GB 到超过 13 GB 不等。
Lemonade 会自动检测你的 NPU，并安装 **FastFlowLM NPU** 后端。

<!-- @os:windows -->
> **提示：** 为获得最佳 NPU 性能，请启用 turbo 模式：
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### 切换模型

第 6 步中的抽认卡应用同样适用于 NPU 模型，只需更改模型名称即可：

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## 后续步骤

现在你已经在自己的硬件上运行了一个本地 AI 服务器，接下来可以做这些事：

1. **连接你喜爱的应用**：Lemonade 开箱即用地支持 [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk)、[Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/)、[Continue](https://lemonade-server.ai/docs/server/apps/continue/)、[n8n](https://n8n.io/integrations/lemonade-model/) 以及[更多应用](https://lemonade-server.ai/marketplace)。

2. **浏览更多模型**：探索完整的[模型库](https://lemonade-server.ai/docs/server/server_models/)，找到针对编码、推理、视觉等场景优化的模型。使用 Lemonade 应用或 `lemonade list` 查看可用模型。

3. **解锁 ROCm GPU 加速**：如果你拥有受支持的 AMD GPU，可以切换到 ROCm 后端：`lemonade config set llamacpp.backend=rocm`。请参阅[受支持的 AMD GPU](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations)。

4. **阅读完整 API 规范**：Lemonade 支持聊天补全、嵌入、音频转录、图像生成、文本转语音等功能。有关每个端点的详细信息，请参阅[服务器规范](https://lemonade-server.ai/docs/server/server_spec/)。

5. **参与贡献**：Lemonade 是开源项目。请查看[贡献指南](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md)，并寻找[适合新手的问题](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)。