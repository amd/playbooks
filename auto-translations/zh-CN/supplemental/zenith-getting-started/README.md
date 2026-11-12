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

刚刚拿到你的 Windows Ryzen AI Halo？

你的 **Ryzen™ AI Halo** 出厂时已经配置好 Windows，可直接用于本地 AI 开发。该镜像搭载了 AMD 的 AI 技术栈 —— **Lemonade Server**、**ComfyUI**，以及支持 **ROCm™ 的 PyTorch** —— 同时还包含 **Microsoft Project Zenith**，这是一个预先配置好的 Windows 开发者环境，配备现代化工具链和智能体终端应用。

在本导览中，你将了解到设备上已经安装了哪些内容、已经为你预先配置好了哪些设置，以及如何尽快上手使用。


## 你将学到什么

完成本手册后，你将能够：

* **识别你的 Ryzen AI Halo 上搭载的 AI 软件**，并了解每个组件的用途。
* **认识已经为你预先配置好的 Windows 和工具链设置**。
* **启动 Lemonade Server**、下载模型，并确认其 OpenAI 兼容端点已正常运行。
* **将 Intelligent Terminal 连接**到你的本地 Lemonade 模型。
* **将 GitHub Copilot CLI 连接**到同一个本地端点（可选）。
* **根据任务需求在本地模型和云端模型之间做出选择**。

## 检查软件更新
<!-- @require:software-update -->
## 设置内存配置
<!-- @require:memory-config -->
---

## 第一部分——你的设备上有什么

### AMD AI 技术栈

这些组件共同使 Ryzen AI Halo 成为一台本地 AI 设备。三者均已预装。

| 软件 | 功能 | 启动方式 |
|----------|--------------|-----------------|
| **Lemonade Server** | 具有 OpenAI 兼容 API 的本地 LLM 服务器。可在你的 GPU 和 NPU 上运行模型，并使其他应用能够使用本地模型。 | 开始菜单 → **Lemonade Server** |
| **ComfyUI** | 用于图像和扩散模型的节点图应用程序。自带独立运行环境。 | 桌面快捷方式 |
| **PyTorch with ROCm** | 支持 GPU 加速的 PyTorch，已预装进系统 Python 中。 | 在任意终端中输入 `python` |

### Zenith 开发者工具链

Microsoft 推出的 Project Zenith 为系统增添了现代化的 Windows 开发环境。其主要新增内容如下：

| 工具 | 用途 |
|------|---------------|
| **Intelligent Terminal** | 内置 AI 智能体面板的终端。只需用自然语言描述需求即可获取命令，无需记忆语法。使用 `Ctrl+Shift+.` 打开智能体面板 |
| **GitHub Copilot CLI** | 终端中的智能体式编程——可规划多步骤任务、编辑文件、在你的批准下运行命令。在终端下拉菜单中有专属配置文件。 |
| **WSL 2 with Ubuntu** | 面向以 Linux 为先的机器学习工具链的完整 Linux 环境。运行 `wsl` 即可进入。`wslc` 可创建并运行 Linux 容器。 |
| **uv** | 快速的 Python 包与环境管理器。可用 `uv venv` 和 `uv pip install` 替代 pip。 |
| **PowerShell 7** | 默认 shell，取代了旧版 Windows PowerShell 5。 |
| **PowerToys** | 包含命令面板（`Win+Alt+Space`）和 FancyZones 窗口平铺等实用工具。 |

此外还包括：Git、Visual Studio Code、带 nvm 的 Node.js、.NET SDK 10、GitHub CLI、Azure CLI、Windows App CLI（`winapp`）、Oh My Posh，以及适用于 Windows 的 Coreutils。

### 已为你预先配置好的 Windows 设置

Zenith 预先设置了一些开发者通常需要手动修改的 Windows 和 shell 设置。以下内容无需特意阅读——列出它们只是为了让你了解这些都是刻意为之，而非疏漏。

| 设置项 | 配置方式 | 原因 |
|---------|---------------|--------------|
| 默认 shell | PowerShell 7 | 现代 shell 功能；旧版 PowerShell 5 不再作为默认选项 |
| 长路径支持 | 已启用 | 深层依赖树不再受 260 字符路径限制的影响 |
| 文件资源管理器 | 标题栏显示完整路径 | 在多个项目文件夹间切换工作时更容易查看位置 |
| 外观 | 深色模式 | 已设为新用户的默认选项 |
| 终端字体 | Cascadia Mono NF | 包含 CLI 工具所需的字形 |
| 提示符 | Oh My Posh | 在提示符中显示 Git 分支和 Python 环境信息 |
| `ls` 行为 | Coreutils | `ls`、`cat` 和 `grep` 的行为与 Linux 上一致 |
| 任务栏 | 已固定终端、VS Code、AMD Ryzen AI Developer Center | 你最常用的工具只需一键即可打开 |

---

## 第二部分——运行本地模型

Lemonade 是一款针对 AMD 本地推理进行优化的本地 LLM 服务器。

### 第一步——启动 Lemonade Server

点击快捷方式或通过 Windows 开始菜单打开 **Lemonade**，然后通过访问 `http://localhost:13305` 打开网页图形界面，确认其正在运行。
<!-- @require:lemonade-ready -->
### 步骤 2 — 下载模型

**镜像中不包含任何模型** — 请打开 Lemonade 来选择并下载你的模型。

> [!TIP]
> 你可能需要从右下角的工具栏中打开此 Web UI。
<!-- Screenshot: loading the lemonade Model to help users find it -->
<p align="center">
  <img src="assets/lemonade_model.png" alt="Loading a Lemonade Model in the UI" width="600"/>
</p>
针对 Ryzen AI Halo 上的智能体工作，有两个推荐：

| 模型 | 类型 | 选择理由 |
|-------|------|---------------|
| **Qwen3.8 27B** | 稠密模型 | 每个 token 都会使用全部参数，这通常意味着在处理高难度问题时具有更强的推理能力。由于此时的速度受限于内存带宽，生成速度会较慢。 |
| **Qwen3.6 35B-A3B MTP** | 混合专家模型 | 每个 token 只激活一小部分参数，因此在仍然是大模型的同时，生成速度明显快于同等规模的稠密模型。 |

这两个模型都能装入 Ryzen AI Halo 的统一内存中。如果你还不确定该选哪个，可以先从 MoE 模型开始——对于日常编码来说，响应速度比原始能力更重要，而且你随时都可以切换。


> [!TIP]
> **进行智能体工作时，可以考虑关闭思考模式。** Qwen3.6-35B-A3B 默认会在每次回复前进行思考，而这种延迟在智能体循环中会迅速累积。[lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) 仓库发布了一个现成的配置，可以禁用该功能：
>
> ```powershell
> curl.exe -LO https://raw.githubusercontent.com/lemonade-sdk/recipes/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json
> lemonade import Qwen3.6-35B-A3B-NoThinking.json
> ```
### 第 3 步 — 找到你的模型名称

智能体工具需要的模型名称必须与 Lemonade 报告的名称完全一致。用 CLI 列出已加载的内容：

<!-- @test:id=zenith-lemonade-models timeout=60 -->
```powershell
curl.exe http://localhost:13305/api/v1/models
```
<!-- @test:end -->

或者,只需在界面中记下模型的名称——你将在下一部分粘贴它。

> [!TIP]
> 你的 Lemonade 端点是 `http://localhost:13305/v1`。不需要 API 密钥,但有些应用要求该字段不能为空——被要求时,输入任意占位文本即可。

---

## 第 3 部分 — 连接 Zenith 智能体工具

许多应用会首先指向云订阅服务。下面介绍如何改为将它们指向你刚刚启动的免费本地模型。

### 连接 Intelligent Terminal

Intelligent Terminal 会在你的标准终端中添加一个智能体面板,这样你就可以用自然语言来帮助编写和理解终端输出。

1. 从开始菜单打开 **Intelligent Terminal**。它是与经典 Windows Terminal 不同的独立应用。
2. 打开智能体的设置,找到 **BYOM**（自带模型）或 **Custom endpoint or local model**（自定义端点或本地模型）部分。
3. 选择 **Add New**（新增）并输入：
   - **Base URL:** `http://localhost:13305/v1`
   - **Model ID:** 第 2 部分第 3 步中记下的模型名称
4. 保存后,从模型下拉列表中选择你的新提供方。自定义模型会以 `(BYOK)` 后缀显示。

<!-- Screenshot: the BYOM / custom endpoint dialog with Base URL and Model ID filled in, just before saving. -->
<p align="center">
  <img src="assets/add_lemonade_endpoint.png" alt="Adding a local Lemonade model to Intelligent Terminal: the custom endpoint dialog with the Base URL and Model ID filled in" width="600"/>
</p>

5. 按 `Ctrl+Shift+.` 打开智能体面板,向它提问。它可以浏览你的文件夹、写入文件,并协助你处理复杂的终端命令。

> [!TIP]
> 你的提示词现在会发送到运行在你自己的 GPU 和 NPU 上的模型。没有任何数据离开本机——你可以通过观察 Lemonade 的网页界面在智能体工作时出现活动来确认这一点。


<!-- Screenshot: the terminal with the agent pane open, mid-task — e.g. reading a file or navigating a folder — with the local (BYOK) model selected and visible. -->
<p align="center">
  <img src="assets/agent_pane_screen.png" alt="Intelligent Terminal with the agent pane open, using the local Lemonade model to read a file and navigate the project folder" width="600"/>
</p>

> [!NOTE]
> Intelligent Terminal 将端点凭据存储在 Windows 凭据管理器中，而不是设置文件里。如果以后要更改密钥，需要先移除该端点，然后重新添加。

### 可选：连接 GitHub Copilot CLI

> [!IMPORTANT]
> **你必须先登录 GitHub，才能配置本地模型。** Copilot CLI 将自定义提供方配置置于 GitHub 账户身份验证之后，因此即使你的最终状态完全是本地化的，登录这一步也是无法绕过的。免费的 GitHub Copilot 账户即可满足需求。

Copilot CLI 已经在你的 PATH 中，并且在 Terminal 下拉菜单中有专属配置文件。

1. 打开 **Windows Terminal**，选择 **GitHub Copilot** 配置文件，或者在任意 shell 中运行 `copilot`。
2. 如果尚未完成初始设置，请先完成它。
3. 配置一个与 OpenAI 兼容的自定义提供方，指向 Lemonade 端点（`http://localhost:13305/v1`），并填写你的模型名称。

进入后一些有用的命令：

| 命令 | 作用 |
|---------|--------------|
| `/plan` | 在编写任何代码之前起草实施计划 |
| `Shift+Tab` | 切换智能体模式，包括自动驾驶模式 |
| `/resume` | 恢复之前的会话及其上下文 |

### 选择本地还是云端

两种工具都可以在不同提供方之间切换，这使得双层工作流切实可行：

- **本地（Lemonade）** — 日常编码、重构、解释代码、迭代。无限制、私密、可离线使用。
- **云端** — 偶尔遇到需要前沿模型额外能力的问题时使用。

大多数工作都能轻松归入第一类，这正是拥有如此强大本地算力的意义所在。

---

## 接下来可以做什么

| 如果你想要…… | 试试这个教程 |
|-----------------|-------------------|
| 深入学习 Lemonade——视觉、语音、图像生成、后端 | [Lemonade 入门指南](https://developer.amd.com/playbooks/lemonade-getting-started) |
| 使用基于节点的工作流生成图像 | [使用 ComfyUI 和 Z Image Turbo 生成图像](https://developer.amd.com/playbooks/comfyui-image-gen) |
| 在 VS Code 中使用本地模型 | [使用 VSCode 和 Qwen3-Coder 进行本地 LLM 编码](https://developer.amd.com/playbooks/vscode-qwen3-coder) |
| 在本地服务器上构建智能体工作流 | [使用 Lemonade Server 在本地运行 OpenClaw](https://developer.amd.com/playbooks/openclaw-lemonade-server) |
| 在你自己的数据上微调模型 | [使用 Unsloth 微调 LLM](https://developer.amd.com/playbooks/unsloth-llms-finetuning) |

## 故障排查

### 智能体工具无法连接到模型

Lemonade 不会在登录时自动启动——需要从开始菜单打开它。要确认服务器是否已启动：

<!-- @test:id=zenith-lemonade-status timeout=60 -->
```powershell
lemonade status
```
<!-- @test:end -->

### 模型名称被拒绝

它必须与 Lemonade 报告的名称完全一致。重新运行 `/api/v1/models` 命令，并逐字复制该值。

### 检查 ROCm PyTorch

你的 GPU 应该无需任何设置即可被 PyTorch 使用。要验证这一点：

<!-- @test:id=zenith-torch-check timeout=120 -->
```powershell
python -c "import torch; print('GPU available:', torch.cuda.is_available())"
```
<!-- @test:end -->

如果返回 `False`，请从任务栏打开 **AMD Ryzen AI Developer Center**，安装所有待处理的更新，然后重启。

### 使用大型模型时响应较慢

Token 生成受内存带宽而非容量的限制，因此更大的模型运行速度并不会按其规模比例简单地变慢。切换到混合专家（mixture-of-experts）模型，例如 Qwen3.6 35B MTP，它每个 token 仅激活一部分参数，生成速度比同等规模的稠密模型快得多。

### 模型下拉列表为空

该镜像不附带任何模型。请先通过 Lemonade 的模型管理器下载一个——参见第 2 部分第 2 步。