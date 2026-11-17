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

你的 **Ryzen™ AI Halo** 在出厂时已经为本地 AI 开发配置好了 Windows。该镜像预装了 AMD 的 AI 技术栈 —— **Lemonade Server**、**ComfyUI**，以及支持 **ROCm™** 的 **PyTorch** —— 同时还包含 **Microsoft Project Zenith**，这是一个预先配置好的 Windows 开发者环境，内置现代化工具链和具备智能体能力的终端应用。

在本导览中，你将了解系统中已经安装了哪些内容、哪些配置已经为你预先设置好，以及如何尽快上手使用。


## 你将学到什么

完成本指南后，你将能够：

* **识别你的 Ryzen AI Halo 上预装的 AI 软件**，了解每个组件的用途。
* **认识已经为你预先配置好的** Windows 和工具链设置。
* **启动 Lemonade Server**，下载一个模型，并确认其兼容 OpenAI 的接口已正常运行。
* **将 Intelligent Terminal 连接**到你的本地 Lemonade 模型。
* **将 GitHub Copilot CLI 连接**到同一个本地接口（可选）。
* **根据任务需求在本地模型和云端模型之间进行选择**。

## 检查软件更新
<!-- @require:software-update -->
## 设置内存配置
<!-- @require:memory-config -->

<!-- @device:halo_box -->
<!-- @os:windows -->
> **运行接近或超过 128 GB 的模型：** 在运行 Windows 的 AMD Ryzen™ AI Max 400 Series (Gorgon Halo) 系统上，接近或超过 128 GB 内存的模型需要额外的配置才能正常运行而不出错。请在加载模型之前，先遵循 [AMD Ryzen AI Max PRO 400 Series Windows OS Guidelines](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines) 中的说明进行操作。
<!-- @os:end -->
<!-- @device:end -->
---

## 第一部分 — 你的机器上有什么

### AMD AI 技术栈

这些组件让 Ryzen AI Halo 成为一台本地 AI 机器。三者均已预装。

| 软件 | 功能 | 启动方式 |
|----------|--------------|-----------------|
| **Lemonade Server** | 具有 OpenAI 兼容 API 的本地 LLM 服务器。可在你的 GPU 和 NPU 上运行模型，是其他应用程序使用本地模型的基础。 | 开始菜单 → **Lemonade Server** |
| **ComfyUI** | 用于图像和扩散模型的节点图应用程序。自带独立运行时。 | 桌面快捷方式 |
| **PyTorch with ROCm** | GPU 加速的 PyTorch，已预装到系统 Python 中。 | 在任意终端中运行 `python` |

### Zenith 开发者工具链

来自 Microsoft 的 Project Zenith 添加了现代化的 Windows 开发环境。主要新增内容如下：

| 工具 | 用途 |
|------|---------------|
| **Intelligent Terminal** | 内置 AI 智能体面板的终端。用自然语言描述需求来获取命令，而不必记忆语法。使用 `Ctrl+Shift+.` 打开智能体面板 |
| **GitHub Copilot CLI** | 终端中的智能体式编程工具——可规划多步骤任务、编辑文件、在你批准后运行命令。在终端下拉菜单中有专属配置文件。 |
| **WSL 2 with Ubuntu** | 面向以 Linux 为先的 ML 工具的完整 Linux 环境。运行 `wsl` 进入。`wslc` 可创建并运行 Linux 容器。 |
| **uv** | 快速的 Python 包与环境管理器。用 `uv venv` 和 `uv pip install` 代替 pip。 |
| **PowerShell 7** | 默认 shell，取代了较旧的 Windows PowerShell 5。 |
| **PowerToys** | 包含命令面板（`Win+Alt+Space`）和 FancyZones 窗口平铺功能等实用工具。 |

此外还包含：Git、Visual Studio Code、带 nvm 的 Node.js、.NET SDK 10、GitHub CLI、Azure CLI、Windows App CLI（`winapp`）、Oh My Posh，以及适用于 Windows 的 Coreutils。

### 已为你配置好的 Windows 设置

Zenith 预先设置了一些开发者通常会手动更改的 Windows 和 shell 设置。以下内容并非必读——列出它们只是为了让你知道这些是有意为之，而非偶然出现的。

| 设置 | 配置为 | 作用 |
|---------|---------------|--------------|
| 默认 shell | PowerShell 7 | 现代化 shell 功能；较旧的 PowerShell 5 不再是默认选项 |
| 长路径支持 | 已启用 | 深层依赖树不再受 260 字符路径长度限制 |
| 文件资源管理器 | 标题栏中显示完整路径 | 在多个项目文件夹间工作时更易查看 |
| 外观 | 深色模式 | 已设为新用户的默认外观 |
| 终端字体 | Cascadia Mono NF | 包含 CLI 工具所需的字形 |
| 提示符 | Oh My Posh | 在提示符中显示 Git 分支和 Python 环境 |
| `ls` 行为 | Coreutils | `ls`、`cat` 和 `grep` 的行为与 Linux 上一致 |
| 任务栏 | 已固定 Terminal、VS Code、AMD Ryzen AI Developer Center | 你最常用的工具只需一次点击即可打开 |

---

## 第二部分 — 运行本地模型

Lemonade 是一款针对 AMD 本地推理优化的本地 LLM 服务器。

### 步骤 1 — 启动 Lemonade Server

点击快捷方式或通过 Windows 开始菜单打开 **Lemonade**，然后通过打开网页 GUI `http://localhost:13305` 来确认其正在运行。
<!-- @require:lemonade-ready -->

### 第 2 步 — 下载模型

**镜像中不包含任何模型** —— 打开 Lemonade 以选择你的模型并下载它。

> [!TIP]
> 你可能需要从右下角的工具栏打开网页界面。

<!-- Screenshot: loading the lemonade Model to help users find it -->
<p align="center">
  <img src="assets/lemonade_model.png" alt="Loading a Lemonade Model in the UI" width="600"/>
</p>

针对 Ryzen AI Halo 上的智能体工作，这里有两个推荐：

| 模型 | 类型 | 为什么选择它 |
|-------|------|---------------|
| **Qwen3.8 27B** | 稠密模型 | 每个参数都会用于每个 token，这通常意味着在高难度问题上有更强的推理能力。生成速度较慢，因为此时速度受限于内存带宽。 |
| **Qwen3.6 35B-A3B MTP** | 混合专家模型 | 每个 token 只会激活一小部分参数，因此与相近规模的稠密模型相比，它的生成速度明显更快，同时仍然是一个大模型。 |

两者都能装入 Ryzen AI Halo 的统一内存中。如果你拿不定主意，可以先从 MoE 模型开始——对于日常编码来说，响应速度比原始能力更重要，而且你随时可以切换。


> [!TIP]
> **对于智能体工作，可以考虑关闭思考模式。** Qwen3.6-35B-A3B 默认会在每次响应前进行思考，而这种延迟在智能体循环中会迅速累积。[lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) 仓库发布了一个现成的配置来禁用它：
>
> ```powershell
> curl.exe -LO https://raw.githubusercontent.com/lemonade-sdk/recipes/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json
> lemonade import Qwen3.6-35B-A3B-NoThinking.json
> ```

### 第 3 步 — 找到你的模型名称

智能体工具需要使用与 Lemonade 报告的完全一致的模型名称。使用 CLI 列出已加载的内容：

<!-- @test:id=zenith-lemonade-models timeout=60 -->
```powershell
curl.exe http://localhost:13305/api/v1/models
```
<!-- @test:end -->

或者，直接记下界面中的模型名称——你将在下一部分粘贴它。

> [!TIP]
> 你的 Lemonade 端点是 `http://localhost:13305/v1`。不需要 API 密钥，但有些应用要求该字段不能为空——如果被要求输入，可以输入任意占位文本。

---

## 第 3 部分 — 连接 Zenith 智能体工具

许多应用首先会指向云端订阅。而这里介绍的是如何将它们指向你刚刚启动的免费本地模型。

### 连接 Intelligent Terminal

Intelligent Terminal 会在你的标准终端中添加一个智能体面板，这样你就可以使用自然语言来帮助编写和理解终端输出。

1. 从开始菜单打开 **Intelligent Terminal**。它是一个独立于经典 Windows Terminal 的应用。
2. 打开智能体的设置，找到 **BYOM**（自带模型）或 **Custom endpoint or local model** 部分。
3. 选择 **Add New** 并输入：
   - **Base URL:** `http://localhost:13305/v1`
   - **Model ID:** 第 2 部分第 3 步中记下的模型名称
4. 保存，然后从模型下拉菜单中选择你的新提供方。自定义模型会显示带有 `(BYOK)` 后缀。

<!-- Screenshot: the BYOM / custom endpoint dialog with Base URL and Model ID filled in, just before saving. -->
<p align="center">
  <img src="assets/add_lemonade_endpoint.png" alt="Adding a local Lemonade model to Intelligent Terminal: the custom endpoint dialog with the Base URL and Model ID filled in" width="600"/>
</p>

5. 按下 `Ctrl+Shift+.` 打开智能体面板并向它提问。它可以浏览你的文件夹、写入文件，并帮助你处理复杂的终端命令。

> [!TIP]
> 你的提示词现在会发送到运行在你自己的 GPU 和 NPU 上的模型。没有任何内容会离开这台机器——你可以通过观察 Lemonade 网页界面在智能体工作时活动增多来确认这一点。


<!-- Screenshot: the terminal with the agent pane open, mid-task — e.g. reading a file or navigating a folder — with the local (BYOK) model selected and visible. -->
<p align="center">
  <img src="assets/agent_pane_screen.png" alt="Intelligent Terminal with the agent pane open, using the local Lemonade model to read a file and navigate the project folder" width="600"/>
</p>

> [!NOTE]
> Intelligent Terminal 会将端点凭据存储在 Windows 凭据管理器中，而不是存储在设置文件中。如果以后要更改密钥，需要先移除该端点，然后重新添加。

### 可选：连接 GitHub Copilot CLI

> [!IMPORTANT]
> **你必须先登录 GitHub，才能配置本地模型。** Copilot CLI 将自定义提供方配置放在了 GitHub 账户身份验证之后，因此即使你的最终状态是完全本地化的，登录这一步也是无法避免的。拥有免费的 GitHub Copilot 账户即可。

Copilot CLI 已经在你的 PATH 中，并且在终端下拉菜单中有专属的配置文件。

1. 打开 **Windows Terminal** 并选择 **GitHub Copilot** 配置文件，或在任意 shell 中运行 `copilot`。
2. 如果还没完成初始设置，请先完成它。
3. 配置一个指向 Lemonade 端点（`http://localhost:13305/v1`）的自定义 OpenAI 兼容提供方，并填入你的模型名称。

进入后一些有用的命令：

| 命令 | 作用 |
|---------|--------------|
| `/plan` | 在编写任何代码之前起草一份实施计划 |
| `Shift+Tab` | 在智能体模式之间切换，包括自动驾驶模式 |
| `/resume` | 恢复之前的会话及其上下文 |

### 选择本地还是云端

这两个工具都可以在不同提供方之间切换，这使得两层式工作流变得切实可行：

- **本地（Lemonade）** —— 日常编码、重构、解释代码、迭代开发。不受限制、保护隐私、可离线使用。
- **云端** —— 偶尔遇到需要前沿模型额外能力的问题时使用。

大多数工作都能很好地归入第一类，而这正是拥有如此强大本地算力的意义所在。

---

## 后续方向

| 如果你想要…… | 尝试这份实践指南 |
|-----------------|-------------------|
| 深入学习 Lemonade——视觉、语音、图像生成、后端 | [Lemonade 入门指南](https://developer.amd.com/playbooks/lemonade-getting-started) |
| 使用基于节点的工作流生成图像 | [使用 ComfyUI 和 Z Image Turbo 生成图像](https://developer.amd.com/playbooks/comfyui-image-gen) |
| 在 VS Code 中使用本地模型 | [使用 VSCode 和 Qwen3-Coder 进行本地 LLM 编码](https://developer.amd.com/playbooks/vscode-qwen3-coder) |
| 在本地服务器上构建智能体工作流 | [使用 Lemonade Server 在本地运行 OpenClaw](https://developer.amd.com/playbooks/openclaw-lemonade-server) |
| 在你自己的数据上微调模型 | [使用 Unsloth 微调 LLM](https://developer.amd.com/playbooks/unsloth-llms-finetuning) |

## 故障排查

### 智能体工具无法连接到模型

Lemonade 不会在登录时自动启动——请从开始菜单打开它。要确认服务器已启动：

<!-- @test:id=zenith-lemonade-status timeout=60 -->
```powershell
lemonade status
```
<!-- @test:end -->
### 模型名称被拒绝

模型名称必须与 Lemonade 报告的名称完全一致。重新运行 `/api/v1/models` 命令，并原样复制该值。

### 检查 ROCm PyTorch

你的 GPU 应该无需任何设置即可被 PyTorch 使用。验证方法如下：

<!-- @test:id=zenith-torch-check timeout=120 -->
```powershell
python -c "import torch; print('GPU available:', torch.cuda.is_available())"
```
<!-- @test:end -->

如果返回 `False`，请从任务栏打开 **AMD Ryzen AI Developer Center**，安装所有待处理的更新，然后重启。

### 使用大模型时响应速度较慢

令牌生成速度受限于内存带宽而非容量，因此更大的模型并不会按其规模比例简单地变慢。可以切换到混合专家（mixture-of-experts）模型，例如 Qwen3.6 35B MTP，这类模型每个令牌只激活一小部分参数，生成速度比同等规模的密集模型要快得多。

### 模型下拉列表为空

镜像中未自带任何模型。请先通过 Lemonade 的模型管理器下载一个模型——参见第 2 部分，步骤 2。