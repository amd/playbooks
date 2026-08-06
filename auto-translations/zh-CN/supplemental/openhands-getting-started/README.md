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

[OpenHands](https://github.com/All-Hands-AI/OpenHands) 是一个 AI 软件智能体，
可以在真实的工作区中编写代码、运行命令、浏览网页并编辑文件。你无需从聊天窗口中
复制建议，只需将该智能体指向一个项目文件夹，让它完成实际工作：实现功能、修复
错误、编写测试或解释代码库。

[Agent Canvas](https://github.com/OpenHands/agent-canvas) 是运行 OpenHands 推荐使用的浏览器
界面。只需一条 `agent-canvas` 命令即可同时启动智能体服务器、自动化后端和网页前端，
让你可以在浏览器中与智能体进行对话。

为了让一切都保留在你的 AMD 系统上，该智能体与由 Lemonade Server 提供服务的本地模型
进行交互。Lemonade 通过兼容 OpenAI 的 API 公开该模型，因此 Agent Canvas 可以像配置
任何其他 OpenAI 风格的端点一样对其进行配置，同时模型、你的代码和对话上下文都会
保留在你的机器上。

在本手册中，你将启动一个本地模型、启动 Agent Canvas、将其指向该模型，并针对一个
真实的项目文件夹运行你的第一个编码任务。

## 你将学到什么

- 如何启动 Lemonade Server 并确认本地模型能够响应聊天请求
- 如何从 npm 软件包安装并启动 Agent Canvas
- 如何配置 Agent Canvas 使用本地 Lemonade 模型作为 LLM
- 如何启动 OpenHands 对话，并观察智能体在工作区中编辑文件和运行命令
- 如何审查智能体所做的更改，并通过后续消息引导它

## 核心概念

| 概念 | 是什么 | 在本手册中的作用 |
| --- | --- | --- |
| Lemonade Server | 一个为 AMD 硬件构建的本地 LLM 服务平台，公开兼容 OpenAI 的 API。你的数据永远不会离开你的机器。 | 运行为智能体提供支持的模型。 |
| OpenHands | 一个 AI 软件智能体，可在工作区内读取和编辑文件、运行 shell 命令并浏览网页。 | 你在聊天中驱动的智能体。 |
| Agent Canvas | 运行 OpenHands 对话并显示工具调用和文件更改的浏览器界面和后端。 | 启动整套系统并承载你的对话。 |
| 工作区 | 允许智能体读取和修改的项目文件夹。 | 智能体编辑和执行命令的目标对象。 |

<!-- @device:stx,krk -->
> [!NOTE]
> 编码智能体工作流受益于更大的模型和上下文窗口。请使用至少 32 GB 的系统内存，
> 对于更大的 GGUF 模型，建议使用 64 GB 或更多。
<!-- @device:end -->

## 前提条件

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

你需要：

- 已安装 Lemonade Server，并能够提供以下模型的服务。
- Node.js 22.12 或更高版本以及 `npm`（`agent-canvas` CLI 使用它们）。
- `uv`，Agent Canvas 用于管理智能体服务器环境的 Python 包管理器。如果你的系统尚未
  安装它，请在启动 Agent Canvas 之前，从
  [uv 安装指南](https://docs.astral.sh/uv/getting-started/installation/)进行安装。
- 一个供智能体工作的项目文件夹。这可以是任何你希望智能体处理的本地 git 仓库或代码
  目录。

<!-- @device:halo,halo_box,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

## 1. 启动 Lemonade Server

从 Lemonade CLI 启动模型：

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

Lemonade 在以下位置公开兼容 OpenAI 的 API：

```text
http://127.0.0.1:13305/api/v1
```



## 2. 验证本地模型

确认 Lemonade 能够为所选模型提供服务：

```bash
curl -s "http://127.0.0.1:13305/api/v1/models" | python3 -m json.tool
```

然后发送一个小的聊天请求：

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

如果返回一个 `choices` 数组，则说明 Lemonade 已为 Agent Canvas 做好准备。

## 3. 安装并启动 Agent Canvas

全局安装已发布的 Agent Canvas 软件包：

```bash
npm install -g @openhands/agent-canvas
```

然后在终端中启动整套系统：

```bash
agent-canvas
```

默认情况下，Agent Canvas 会在 `http://localhost:8000` 上启动。在浏览器中打开该
URL。如果端口 8000 已被占用，请在启动 Agent Canvas 时传入 `--port`（或 `-p`）参数：

```bash
agent-canvas --port 3000
```

在 Windows 上的 PowerShell 中同样适用相同的命令。然后改为打开
`http://localhost:3000`。默认本地后端应在主屏幕上显示为健康状态。

`agent-canvas` 命令会同时启动智能体服务器、自动化后端和网页前端。你只需要这一条
命令即可在本地运行 OpenHands。

## 4. 配置本地 LLM

首次启动时，Agent Canvas 会打开一个引导流程。在该流程中：

1. 保持 **OpenHands** 作为所选智能体，然后点击 **Next**。
2. 在 **Set up your LLM** 中，选择 **Advanced**。
3. 保持 **Authentication** 设置为 **API key**。
4. 将 **Custom Model** 设置为 `openai/Qwen3.6-35B-A3B-GGUF`。
5. 将 **Base URL** 设置为 `http://127.0.0.1:13305/api/v1`。
6. 对于 **API Key**，输入任意非空的占位符，例如 `lemonade-local`。
   Lemonade 不需要真实的密钥，但 OpenHands 客户端需要一个值来发送。
7. 点击 **Next**。

完成后的 Advanced 设置应如下所示。API 密钥字段会被界面遮盖。

![Agent Canvas 首次使用时的 LLM 高级设置，显示 Lemonade 模型和本地基础 URL](assets/01-llm-advanced-settings.png)

Agent Canvas 会将这些值保存为一个 LLM 配置文件。如果你的版本要求你为该配置文件
命名，请使用不含空格的名称，例如 `lemonade-local`。如果之后想更换模型，请打开
**Settings > LLM** 并更新相同的 Advanced 字段。你可以在聊天输入框中使用
`/model` 命令切换已保存的配置文件。

## 5. 打开工作区

智能体只能读取和修改你所选工作区内的文件。在开始任务之前，请将 Agent Canvas
指向你的项目文件夹：

1. 在主屏幕上，选择 **Open Workspace**。
2. 选择包含你的项目的文件夹（例如，你希望智能体处理的 git 仓库）。
3. 在该工作区中开始一个新对话。

智能体所做的一切——读取文件、运行命令、编辑代码——都仅限于该工作区。

![引导完成后的 Agent Canvas 主屏幕](assets/02-agent-canvas-home.png)
## 6. 运行你的第一个编码任务

在打开工作区并选择本地 LLM 后，在聊天中输入一个具体任务。一个好的初始任务应该小而可验证，例如：

```text
Create a new file called hello.py that defines a function greet(name) that
returns "Hello, {name}!", and add a small test that prints greet("World")
when run as a script.
```

观察对话时间线。OpenHands 将会：

- 读取工作区以了解其结构。
- 创建 `hello.py`，其中包含所请求的函数和测试代码块。
- 可选地运行 `python3 hello.py` 以验证输出。
- 在聊天中报告它所做的操作以及任何命令输出。

你应该会看到工作区中出现新文件，并且智能体的最终消息应描述它所做的更改。这就是收获的时刻：智能体在你的项目文件夹中编写并运行了真实的代码。

## 7. 检查并引导智能体

在智能体完成一个步骤后，先审查其工作，再接受下一步：

- **文件更改**：使用工作区文件浏览器或智能体的差异（diff）视图，查看具体添加、更改或删除了什么内容。
- **命令输出**：展开智能体运行的任何命令，查看标准输出（stdout）、标准错误（stderr）和退出代码。
- **后续跟进**：如果结果不是你想要的，在同一对话中回复并给出更正意见。智能体会保留先前的上下文，并在相同的文件上进行迭代。

例如，如果测试没有打印出预期的问候语，回复：

```text
The script did not print anything. Run python3 hello.py and fix it so the
greet("World") test prints to stdout.
```

智能体会重新读取文件、运行命令、诊断问题，并再次编辑该文件——所有这些都在同一对话中完成。

## 故障排除

- **`agent-canvas` 不在 PATH 中：** 使用
  `npm install -g @openhands/agent-canvas` 重新安装，并确认 npm 全局二进制文件
  目录已加入 PATH。在 Windows 上，运行 `npm config get prefix`；
  返回的目录（通常是 `%APPDATA%\npm` 或 `%USERPROFILE%\.npm-global`）
  必须已加入用户 PATH，然后才能从新终端启动 `agent-canvas`。
- **`npm install -g` 因权限错误而失败：** 配置一个用户拥有的
  全局 npm 目录，然后重新打开终端并再次安装 Agent Canvas。

  <!-- @os:linux -->
  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix ~/.npm-global
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
  . ~/.profile
  npm install -g @openhands/agent-canvas
  ```
  <!-- @os:end -->

  <!-- @os:windows -->
  ```powershell
  New-Item -ItemType Directory -Force "$env:USERPROFILE\.npm-global"
  npm config set prefix "$env:USERPROFILE\.npm-global"
  $env:Path = "$env:USERPROFILE\.npm-global;$env:Path"
  npm install -g @openhands/agent-canvas
  ```

  要使 Windows 的 PATH 更改永久生效，请在 **设置 > 系统 > 关于 > 高级系统设置 >
  环境变量** 中将 `%USERPROFILE%\.npm-global` 添加到
  用户 PATH，然后打开一个新终端。
  <!-- @os:end -->
- **界面已加载，但后端显示不健康：** 等待几秒钟，让
  智能体服务器完成启动，然后刷新。如果仍然不健康，请重启
  `agent-canvas` 并检查终端输出中的错误信息。
- **Lemonade 聊天请求因连接错误而失败：** 确认
  `curl -fsS "http://127.0.0.1:13305/api/v1/health"` 执行成功，并且
  Lemonade 仍在通过 `lemonade status` 提供该模型的服务。
- **智能体报出上下文长度或令牌限制的错误信息：** 使用更大的
  `ctx_size`（例如 `ctx_size=65536`）重启 Lemonade，并开始一个
  全新的对话，以避免智能体携带过大的历史记录。
- **智能体产生低质量或不完整的编辑：** 切换到 Lemonade 中的更大
  模型，或者给智能体一个更小、更具体的任务，让它先完成再要求
  进行下一次更改。
- **缺少 `uv`：** 从
  [uv 安装指南](https://docs.astral.sh/uv/getting-started/installation/)安装它。
  Agent Canvas 使用 `uv` 来管理智能体服务器的 Python 环境。

## 后续步骤

- 在同一工作区中尝试一个更大的任务，例如添加一个单元测试文件或
  修复一个已知的错误，并在保留更改之前查看智能体的差异（diff）。
- 在 **Customize** 下连接一个 MCP 服务器（如 GitHub 或 Slack），以便
  智能体在工作时可以读取问题或发布更新。
- 保存多个 LLM 配置文件（一个快速的小模型和一个更强大的大模型），并
  在对话过程中使用 `/model` 在它们之间切换。
- 前往[OpenHands 自动化](https://docs.openhands.dev/openhands/usage/automations/overview)，
  将重复性的开发循环转变为定时或事件触发的智能体运行。

## 资源

- [OpenHands 文档](https://docs.openhands.dev/)
- [Agent Canvas 概览](https://docs.openhands.dev/openhands/usage/agent-canvas/overview)
- [Agent Canvas 设置](https://docs.openhands.dev/openhands/usage/agent-canvas/setup)
- [LLM 配置文件与模型配置](https://docs.openhands.dev/openhands/usage/agent-canvas/llm-profiles)
- [Lemonade Server 文档](https://lemonade-server.ai/docs)