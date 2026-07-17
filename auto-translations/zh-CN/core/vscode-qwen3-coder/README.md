<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> 此 playbook 使用了 GitHub 无法渲染的特殊标签。请访问 [amd.com/playbooks](https://amd.com/playbooks) 以正确预览此内容。
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> 此 playbook 需要至少 **32GB** 的系统内存。
<!-- @device:end -->

## 概述

编码代理是通过与由大型语言模型（LLM）支持的 AI 代理协作来赋能开发者的强大工具。它们可以嵌入到开发环境中，例如终端或 VS Code，从而无缝集成到开发者的工作流程中。

本教程演示如何使用 Cline、VS Code 和 LM Studio 在本地计算机上完整运行一个编码代理。

## 您将学到的内容

* 如何运行带有 Cline 编码代理的 VS Code 以辅助软件工程任务。
* 如何配置 Cline 以与 LM Studio 通信，从而在本地推理编码代理。
* 如何使用本地编码代理解决实际的软件工程任务。

## 设置内存配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 检查软件更新
> **注意**：如果未安装 VS Code，您可以通过 Ryzen AI Developer Center 进行安装。

<!-- @require:software-update -->
<!-- @device:end -->

## 安装软件先决条件

<!-- @require:lmstudio,vscode -->

## 启动并配置 LM Studio

我们将使用 LM Studio 来为编码代理提供 LLM 服务。

- 在搜索栏中搜索 `LM Studio` 并启动该应用程序。您将看到以下页面。

![LM Studio 初始界面](assets/initial-lm-studio.png)

接下来，我们需要在系统上加载 LLM。我们将使用具有较大上下文长度的 `Qwen3-Coder-30B-A3B` 模型。（如果尚未安装，请使用"模型"选项卡进行安装）。
- 点击 LM Studio 窗口顶部的搜索栏，或按 `CTRL+L`。点击 `Manually choose model load parameters` 开关，然后点击 Qwen3-Coder-30B-A3B 模型。
- 将上下文长度从 `4096` 更改为 `32768`，并确保 `GPU Offload` 处于最大值。然后点击 `Load Model`。

![选择模型](assets/model-list-zoomed.png)

我们使用较大的上下文长度，以便代理能够处理大型代码库并记住已做的更改。

![配置模型](assets/selecting-model-zoomed.png)

接下来，我们需要启用 LM Studio 服务器。
- 点击左侧的"Developer"选项卡，或在 LM Studio 中按 `CTRL+2`。
- 检查状态切换开关，确保其设置为 `Running`。

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-up-windows timeout=120 hidden=True -->
```powershell
lms server start --port 1234
curl.exe -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-up-linux timeout=120 hidden=True -->
```bash
lms server start --port 1234
curl -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

![服务器状态](assets/lm-studio-server-status.png)

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-qwen3-coder-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="qwen3coder-32k-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## 启动并配置 VS Code

我们将在 VS Code 中安装 Cline 扩展，并将其连接到我们刚刚创建的 LM Studio 服务器。
- 在搜索栏中搜索 `VS Code` 并启动该应用程序。
- 点击 VS Code 左侧列中的 `Extensions` 图标，搜索 `Cline`，然后点击 `Install` 按钮。

![安装 Cline 扩展](assets/installing-cline-vscode-extension.png)

- 左侧应出现一个 Cline 图标。点击该图标以打开 Cline。将会弹出一个窗口询问 `How will you use Cline?`。由于我们将使用通过 LM Studio 运行的本地 LLM，请选择 `Bring my own API Key` 并点击 `Continue`。

<!-- @os:windows -->
<!-- @test:id=cline-install-and-verify-windows timeout=300 hidden=True -->
```powershell
code --install-extension saoudrizwan.claude-dev
code --list-extensions | Select-String -Pattern "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=cline-install-and-verify-linux timeout=300 hidden=True -->
```bash
code --install-extension saoudrizwan.claude-dev
code --list-extensions | grep -i "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

![账户创建](assets/cline-how-will-you-use-cline-zoomed.png)

接下来，我们需要配置 Cline 以与我们设置的 LM Studio 服务器通信。
- 将 API Provider 设置为 `LM Studio`，将模型设置为 `Qwen3-Coder-30B-A3B-GGUF`。

>**提示**：可能有更新的模型可用。如有需要，可考虑下载并切换到 Qwen3.6 模型。


![模型配置](assets/cline-model-configuration-zoomed.png)

## 创建您的第一个项目

让我们使用本地代理来创建一个网站！在 VS Code 中打开您选择的目录，Cline 将在该目录中创建文件。
- 为此，请点击 VS Code 左上角的 `File -> Open Folder`，然后选择一个文件夹，例如 `Documents`。

![VS Code 空文件夹](assets/open-cline-test.png)

现在我们已准备好向本地编码代理发送提示。
- 点击左侧列中的 Cline 扩展，输入提示以启动代理。例如，我们可以使用以下提示：
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

代理随后将根据提示开始创建文件。作为用户，您可以在 VS Code 中观察代码的生成过程，如下所示。每次 Cline 想要创建文件时，您可能需要点击 `Save`。

![Cline 代码生成](assets/cline-code-generation.png)

生成软件后，代理即完成任务，您可以运行该应用程序。在本例中，代理写入了三个文件：`index.html`、`script.js` 和 `styles.css`。只需双击 HTML 文件，即可加载并与生成的网站进行交互。

<!-- @os:windows -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request
with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()
req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-stop-windows timeout=300 hidden=True -->
```powershell
$ID = Get-Content "$env:TEMP\lmstudio_model_id.txt" -Raw
$ID = $ID.Trim()
lms unload "$ID"
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-stop-linux timeout=300 hidden=True -->
```bash
ID="$(cat /tmp/lmstudio_model_id.txt)"
lms unload "$ID" || true
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

## 后续步骤

生成网站后，您可以继续与 Cline 合作来改进网站。以下是两个可能的改进方向：

- **文档**：向代理发送提示 `Add a README`，代理即可生成一个记录网站信息的 `README.md` 文件。
- **动画**：向模型发送提示 `Add an animation that visually represents a large language model running on a laptop.`，为网站生成一个动画。

我们鼓励读者尝试使用此设置生成其他应用程序。以下是我们尝试过的一些有趣示例：

- **复古街机游戏**：尝试其他提示。让代理使用以下提示通过 `PyGame` 包创建 Python 复古风格游戏也很有趣：

```code
Create a simple pong game using the PyGame python package.
```

- **数据分析**：编码代理特别有用的一个领域是脚本编写和数据分析。以下提示展示了本地模型生成用于股票价格可视化的数据分析软件的能力：

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## 资源

以下是一些额外资源，可帮助您进一步了解编码代理、Cline 以及在上面运行工作负载的相关信息：

* 有关 AMD LM Studio 合作伙伴关系和集成的更多信息：https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD 博客，介绍如何在 AMD Ryzen™ AI 和 Radeon™ 显卡上运行 Cline：https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Cline 博客，介绍如何在 AI PC 上本地运行编码代理：https://cline.bot/blog/local-models-amd