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

刚拿到你的 Windows Ryzen AI Halo？

你的 **Ryzen™ AI Halo** 在出厂时已经配置好了 Windows，可用于本地 AI 开发。该镜像搭载了 AMD 的 AI 技术栈 —— **Lemonade Server**、**ComfyUI** 和支持 **ROCm™ 的 PyTorch**，并配备了 **Microsoft Project Zenith**，这是一套预先配置好的 Windows 开发者环境，拥有现代化的工具链和具备智能体能力的终端应用。

在本导览中，你将了解已安装的内容、已为你预先配置的内容，以及如何尽快上手运行。


## 你将学到什么

读完本手册后，你将能够：

* **识别你的 Ryzen AI Halo 上搭载的 AI 软件**，并了解每个组件的用途。
* **识别已为你预先配置好的 Windows 和工具链设置**。
* **启动 Lemonade Server**，下载模型，并确认其兼容 OpenAI 的接口已正常运行。
* **将 Intelligent Terminal 连接**到你本地的 Lemonade 模型。
* **将 GitHub Copilot CLI 连接**到同一个本地接口（可选）。
* **根据任务需要，在本地模型和云端模型之间做出选择**。

## 检查软件更新

<!-- @require:software-update -->

## 设置内存配置

<!-- @require:memory-config -->

---

## 第 1 部分 — 你的设备上有什么

### AMD AI 技术栈

正是这些组件使 Ryzen AI Halo 成为一台本地 AI 设备。这三者均已预先安装。

| 软件 | 作用 | 如何启动 |
|----------|--------------|-----------------|
| **Lemonade Server** | 带有兼容 OpenAI 的 API 的本地 LLM 服务器。可在你的 GPU 和 NPU 上运行模型，也正是它让其他应用能够使用本地模型。 | 开始菜单 → **Lemonade Server** |
| **ComfyUI** | 用于图像和扩散模型的节点图应用程序。自带独立运行时。 | 桌面快捷方式 |
| **PyTorch with ROCm** | 支持 GPU 加速的 PyTorch，已预先安装到系统 Python 中。 | 在任意终端中输入 `python` |

### Zenith 开发者工具链

来自 Microsoft 的 Project Zenith 为系统添加了现代化的 Windows 开发环境。其中的重点新增内容如下：

| 工具 | 用途 |
|------|---------------|
| **Intelligent Terminal** | 内置 AI 智能体面板的终端。可以用自然语言请求命令，而不必死记语法。按 `Ctrl+Shift+.` 打开智能体面板。 |
| **GitHub Copilot CLI** | 在终端中实现具备智能体能力的编码 —— 可规划多步骤任务、编辑文件、在你的批准下运行命令。在终端下拉菜单中有自己的配置文件。 |
| **WSL 2 with Ubuntu** | 面向以 Linux 为先的机器学习工具的完整 Linux 环境。运行 `wsl` 进入。`wslc` 可创建并运行 Linux 容器。 |
| **uv** | 快速的 Python 包与环境管理工具。可用 `uv venv` 和 `uv pip install` 替代 pip。 |
| **PowerShell 7** | 默认 shell，取代了旧版 Windows PowerShell 5。 |
| **PowerToys** | 包含命令面板（`Win+Alt+Space`）和 FancyZones 窗口平铺等实用工具。 |

此外还包括：Git、Visual Studio Code、Node.js（含 nvm）、.NET SDK 10、GitHub CLI、Azure CLI、Windows App CLI（`winapp`）、Oh My Posh，以及适用于 Windows 的 Coreutils。

### 已为你预先配置好的 Windows 设置

Zenith 预设了许多开发者通常需要手动修改的 Windows 和 shell 设置。以下内容无需你特别留意——之所以列出，是为了让你知道这些设置是刻意为之，而非偶然出现。

| 设置 | 配置为 | 有何帮助 |
|---------|---------------|--------------|
| 默认 shell | PowerShell 7 | 现代化的 shell 功能；旧版 PowerShell 5 已不再是默认选项 |
| 长路径支持 | 已启用 | 复杂的依赖树不会再受限于 260 字符的路径长度限制 |
| 文件资源管理器 | 标题栏显示完整路径 | 在多个项目文件夹间切换工作时更容易辨认 |
| 外观 | 深色模式 | 已设为新用户的默认选项 |
| 终端字体 | Cascadia Mono NF | 包含 CLI 工具所需的字形 |
| 提示符 | Oh My Posh | 在提示符中显示 Git 分支和 Python 环境 |
| `ls` 行为 | Coreutils | `ls`、`cat` 和 `grep` 的行为与在 Linux 上一致 |
| 任务栏 | 已固定终端、VS Code、AMD Ryzen AI Developer Center | 你最常用的工具只需一键即可打开 |

---

## 第 2 部分 — 运行本地模型

Lemonade 是一款针对 AMD 本地推理优化的本地 LLM 服务器。

### 第一步 — 启动 Lemonade Server

点击快捷方式或通过 Windows 开始菜单打开 **Lemonade**，然后通过打开位于 `http://localhost:13305` 的网页图形界面来确认它正在运行。

<!-- @require:lemonade-ready -->

### 第二步 — 下载模型

**该镜像不附带任何模型** —— 打开 Lemonade，选择你需要的模型并下载。

> [!TIP]
> 你可能需要从右下角的工具栏打开网页界面。

<!-- Screenshot: loading the lemonade Model to help users find it -->
<p align="center">
  <img src="assets/lemonade_model.png" alt="Loading a Lemonade Model in the UI" width="600"/>
</p>

针对 Ryzen AI Halo 上的智能体工作，有两项推荐：

| 模型 | 类型 | 推荐理由 |
|-------|------|---------------|
| **Qwen3.8 27B** | 稠密模型 | 每个参数都会用于每个 token 的计算，这通常意味着在高难度问题上有更强的推理能力。生成速度较慢，因为此处的速度受限于内存带宽。 |
| **Qwen3.6 35B-A3B MTP** | 混合专家模型 | 每个 token 只会激活一部分参数，因此相比同等规模的稠密模型，生成速度明显更快，同时依然是一个大模型。 |

这两款模型都能装入 Ryzen AI Halo 的统一内存中。如果你不确定选哪个，可以先从 MoE 模型开始 —— 对于日常编码而言，响应速度往往比单纯的能力更重要，而且你随时都可以切换模型。


> [!TIP]
> **进行智能体相关工作时，可以考虑关闭思考模式。** Qwen3.6-35B-A3B 默认会在每次回复前进行思考，而这种延迟在智能体循环中会迅速累积。[lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) 仓库提供了一份现成的配置文件，可以禁用该功能：
>
> ```powershell
> curl.exe -LO https://raw.githubusercontent.com/lemonade-sdk/recipes/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json
> lemonade import Qwen3.6-35B-A3B-NoThinking.json
> ```
### 第 3 步 — 查找你的模型名称

智能体工具需要的模型名称必须与 Lemonade 所报告的完全一致。使用 CLI 列出已加载的内容：

<!-- @test:id=zenith-lemonade-models timeout=60 -->
```powershell
curl.exe http://localhost:13305/api/v1/models
```
<!-- @test:end -->

或者，直接在 UI 中记下模型的名称——你将在下一部分粘贴它。

> [!TIP]
> 你的 Lemonade 终结点是 `http://localhost:13305/v1`。不需要 API 密钥，但部分应用要求该字段不能为空——如有要求，可输入任意占位文本。

---

## 第 3 部分 — 连接 Zenith 智能体工具

许多应用首先指向云端订阅服务。下面介绍如何将它们改为指向你刚刚启动的免费本地模型。

### 连接 Intelligent Terminal

Intelligent Terminal 会在标准终端中添加一个智能体面板，这样你就可以使用自然语言来帮助编写和理解终端输出。

1. 从开始菜单打开 **Intelligent Terminal**。它是一个与经典 Windows 终端不同的独立应用。
2. 打开智能体的设置，找到 **BYOM**（自带模型）或 **Custom endpoint or local model** 部分。
3. 选择 **Add New** 并输入：
   - **Base URL：** `http://localhost:13305/v1`
   - **Model ID：** 第 2 部分第 3 步中记下的模型名称
4. 保存后，从模型下拉菜单中选择你的新提供方。自定义模型会显示带有 `(BYOK)` 后缀的标识。

<!-- Screenshot: the BYOM / custom endpoint dialog with Base URL and Model ID filled in, just before saving. -->
<p align="center">
  <img src="assets/add_lemonade_endpoint.png" alt="Adding a local Lemonade model to Intelligent Terminal: the custom endpoint dialog with the Base URL and Model ID filled in" width="600"/>
</p>

5. 按下 `Ctrl+Shift+.` 打开智能体面板并向它提问。它可以浏览你的文件夹、写入文件，并帮助你处理复杂的终端命令。

> [!TIP]
> 现在你的提示词会发送给运行在你自己 GPU 和 NPU 上的模型。没有任何数据离开本机——你可以通过观察 Lemonade 的 Web UI 在智能体工作时出现活动来确认这一点。


<!-- Screenshot: the terminal with the agent pane open, mid-task — e.g. reading a file or navigating a folder — with the local (BYOK) model selected and visible. -->
<p align="center">
  <img src="assets/agent_pane_screen.png" alt="Intelligent Terminal with the agent pane open, using the local Lemonade model to read a file and navigate the project folder" width="600"/>
</p>

> [!NOTE]
> Intelligent Terminal 将终结点凭据存储在 Windows 凭据管理器中，而不是设置文件里。如需以后更改密钥，请先移除该终结点，然后重新添加。

### 可选：连接 GitHub Copilot CLI

> [!IMPORTANT]
> **在配置本地模型之前，你必须先登录 GitHub。** Copilot CLI 将自定义提供方配置放在 GitHub 账户身份验证之后，因此即使你的最终状态完全是本地化的，这一登录步骤也是不可避免的。免费的 GitHub Copilot 账户即可满足需求。

Copilot CLI 已经添加到你的 PATH 中，并在终端下拉菜单中有专属的配置文件。

1. 打开 **Windows 终端** 并选择 **GitHub Copilot** 配置文件，或在任意 shell 中运行 `copilot`。
2. 如果还没有完成初始设置，请先完成它。
3. 配置一个自定义的 OpenAI 兼容提供方，指向 Lemonade 终结点（`http://localhost:13305/v1`）并填入你的模型名称。

进入后可用的命令：

| 命令 | 作用 |
|---------|--------------|
| `/plan` | 在编写任何代码之前先起草一份实现计划 |
| `Shift+Tab` | 循环切换智能体模式，包括自动驾驶模式 |
| `/resume` | 恢复之前的会话及其上下文 |

### 选择本地或云端

两种工具都可以在提供方之间切换，这使得双层工作流变得切实可行：

- **本地（Lemonade）** — 日常编码、重构、解释代码、迭代开发。不受限制、保护隐私、可离线使用。
- **云端** — 偶尔遇到需要前沿模型额外能力的问题时使用。

大部分工作都能轻松归入第一类，这正是拥有如此强大本地算力的意义所在。

---

## 接下来可以做什么

| 如果你想… | 可以尝试这个实践指南 |
|-----------------|-------------------|
| 深入学习 Lemonade——视觉、语音、图像生成、后端 | [Getting Started with Lemonade](https://developer.amd.com/playbooks/lemonade-getting-started) |
| 使用基于节点的工作流生成图像 | [Generating Images with ComfyUI and Z Image Turbo](https://developer.amd.com/playbooks/comfyui-image-gen) |
| 在 VS Code 中使用本地模型 | [Local LLM Coding with VSCode and Qwen3-Coder](https://developer.amd.com/playbooks/vscode-qwen3-coder) |
| 在本地服务器上构建智能体工作流 | [Running OpenClaw Locally with Lemonade Server](https://developer.amd.com/playbooks/openclaw-lemonade-server) |
| 使用自己的数据微调模型 | [Fine-Tuning LLMs with Unsloth](https://developer.amd.com/playbooks/unsloth-llms-finetuning) |

## 故障排查

### 智能体工具无法连接到模型

Lemonade 不会在登录时自动启动——请从开始菜单打开它。要确认服务器是否已启动：

<!-- @test:id=zenith-lemonade-status timeout=60 -->
```powershell
lemonade status
```
<!-- @test:end -->

### 模型名称被拒绝

名称必须与 Lemonade 报告的名称完全一致。请重新运行 `/api/v1/models` 命令，并原样复制该值。

### 检查 ROCm PyTorch

你的 GPU 应该无需任何设置即可被 PyTorch 使用。要验证这一点：

<!-- @test:id=zenith-torch-check timeout=120 -->
```powershell
python -c "import torch; print('GPU available:', torch.cuda.is_available())"
```
<!-- @test:end -->

如果返回 `False`，请从任务栏打开 **AMD Ryzen AI Developer Center**，安装任何待处理的更新，然后重启。

### 使用大模型时响应缓慢

令牌生成速度受内存带宽而非容量的限制，因此更大的模型并不会简单地按其体积比例变慢。可以切换到混合专家（mixture-of-experts）模型，例如 Qwen3.6 35B MTP，这类模型每个令牌仅激活一小部分参数，生成速度比同等规模的稠密模型快得多。

### 模型下拉菜单为空

该镜像未附带任何模型。请先通过 Lemonade 的 Model Manager 下载一个——参见第 2 部分第 2 步。