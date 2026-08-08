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

开发者在一些反复出现的小循环上花费了大量时间:审查已加标签的拉取请求、回复 GitHub 评论、分类新出现的问题、把 Slack 讨论串整理成站会记录或事件复盘,以及跟踪发布或研究相关的信号。每个循环都很熟悉,但仍需要判断:收集正确的上下文、决定哪些内容重要,并把清晰的更新发布到团队日常工作所在的地方。

[OpenHands 自动化](https://docs.openhands.dev/openhands/usage/automations/overview)
将这些循环转化为按计划或事件触发的智能体对话:在这些对话中,AI 软件智能体可以读取上下文、调用工具并生成更新。OpenHands 扩展目录中的共享自动化模板遵循这一模式,涵盖 GitHub 拉取请求审查、仓库监控、Linear 问题分类、事件复盘、Slack 站会摘要以及研究简报:某个自动化被唤醒,使用配置好的集成(例如 GitHub 或 Slack)获取上下文,借助大语言模型(LLM)对该上下文进行推理,然后写回结果。

[Agent Canvas](https://github.com/OpenHands/agent-canvas) 是用于构建和测试这些自动化的本地控制平面。在本 playbook 中,它运行一个 OpenHands Agent Server(执行智能体对话的后端进程),并将该智能体连接到 GitHub 和 Slack 等外部服务。

为了让整个工作流保留在你的 AMD 系统上,该智能体会与由 Lemonade Server 提供服务的本地模型通信。Lemonade 通过一个与 OpenAI 兼容的 API 暴露该模型,因此 Agent Canvas 可以像配置远程 OpenAI 风格端点一样配置它,同时模型、提示词和工作流上下文都保留在本地。

在本 playbook 中,你将构建一个具体的自动化:一个按计划运行的 GitHub 到 Slack 的开发摘要。它使用 GitHub 检查最近的仓库活动,使用 Slack 发布摘要,通过 Agent Canvas API 调用来配置和测试该自动化,并使用 Lemonade 在本地运行 LLM。

![显示 GitHub MCP、OpenHands 自动化、Lemonade Server 和 Slack MCP 的架构图](assets/00-architecture-overview.png)

## 你将学到什么

- 如何启动 Lemonade Server 并验证本地模型能够响应聊天请求
- 如何启动 Agent Canvas 并将其 Agent Server 指向本地 LLM
- 如何通过 Agent Server API 安装 GitHub 和 Slack 模型上下文协议(MCP)服务器
- 如何创建并调度一个按计划运行的 OpenHands 自动化,将开发摘要发布到 Slack
- 如何排查最常见的本地模型和自动化故障

## 核心概念

| 概念 | 是什么 | 在本 playbook 中的作用 |
| --- | --- | --- |
| Lemonade Server | 一个为 AMD 硬件打造的本地 LLM 服务平台,暴露与 OpenAI 兼容的 API。你的数据永远不会离开你的机器。 | 运行为智能体提供支持的模型。 |
| OpenHands Agent Server | 执行 OpenHands 智能体对话的后端进程。 | 承载智能体、其 LLM 配置文件及其 MCP 服务器。 |
| Agent Canvas | OpenHands 的本地控制平面,运行 Agent Server 以及一个用于查看智能体运行情况的 UI。 | 启动各后端并提供你所调用的 API。 |
| MCP 服务器 | 一种模型上下文协议服务器,为智能体提供访问 GitHub 或 Slack 等外部服务的工具。 | 让智能体能够读取 GitHub 并写入 Slack。 |
| OpenHands 自动化 | 一种按计划或事件触发的智能体对话,负责获取上下文、进行推理并将结果写入某处。 | 你在此处构建的 GitHub 到 Slack 摘要即属此类。 |

<!-- @device:stx,krk -->
> [!NOTE]
> 编码智能体工作流受益于更大的模型和更大的上下文窗口。请至少使用 32 GB 系统内存,对于更大的 GGUF 模型,建议使用 64 GB 或更多内存。
<!-- @device:end -->

## 前置条件

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

你需要:

- 按照标准的
  [Lemonade 安装指南](https://lemonade-server.ai/docs/guide/install/)安装好 Lemonade Server。
- Node.js 22.12 或更高版本以及 `npm`,用于安装已发布的 Agent Canvas
  CLI,并通过 `npx` 运行 MCP 服务器。
- 一个最新发布的 `@openhands/agent-canvas` 包,支持基于 schema 的智能体设置、
  `LLMSummarizingCondenserSettings.max_tokens`,以及 LLM 的 `custom_tokenizer` 支持。
- 在 Agent Server 环境中可用的 Python `transformers` 包。当设置了
  `custom_tokenizer` 时,进行基于聊天模板的令牌计数需要用到它。
- 一个对目标仓库具有读取权限的 GitHub 令牌。
- 一个具备 `chat:write` 权限和频道读取权限的 Slack 机器人令牌(`xoxb-...`)。
- 一个 Slack 团队 ID(`T...`)。
- 一个用于发布摘要的 Slack 频道 ID(`C...`)。

在测试该自动化之前,请先将 Slack 应用邀请加入目标频道。

## 本 playbook 中使用的变量

<!-- @device:halo,halo_box,stx,krk -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

```bash
export LEMONADE_BASE_URL="http://127.0.0.1:13305/api/v1"
export LEMONADE_MODEL="Qwen3.6-35B-A3B-GGUF"
export OPENHANDS_LLM_MODEL="openai/${LEMONADE_MODEL}"
export QWEN_CUSTOM_TOKENIZER="Qwen/Qwen3.6-35B-A3B"
export CONDENSER_MAX_TOKENS="56000"
```

以下值将在后续步骤中输入到 Agent Canvas UI 中。请在此处先设置好,以便在
后续复制使用:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

对 `GITHUB_REPO_FILTER` 请使用明确的 `owner/repo` 值。过宽的组织通配符可能会
为本地模型返回过多的 MCP 上下文。

## 1. 启动 Lemonade Server

从 Lemonade CLI 启动模型:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

Lemonade 在以下地址暴露一个与 OpenAI 兼容的 API:

```text
http://127.0.0.1:13305/api/v1
```

可选:如果 Agent Canvas 或自动化运行器不在同一台机器上,请通过安全隧道
发布 Lemonade 端点,并将该 HTTPS URL 用作 LLM 的基础 URL:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. 验证本地模型

确认 Lemonade 能够为所选模型提供服务:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

然后发送一个小的聊天请求:

```bash
curl -sS "${LEMONADE_BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"${LEMONADE_MODEL}"'",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

如果返回结果中包含 `choices` 数组,说明 Lemonade 已经为 Agent Canvas 做好准备。
## 3. 启动 Agent Canvas

安装已发布的 Agent Canvas 包并启动完整的技术栈：

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

如果全局 npm install 因权限错误失败，请参阅下方的 npm
权限故障排查条目。

默认情况下，Agent Canvas 会在 `http://localhost:8000` 上启动。请在
浏览器中打开该 URL。默认的本地后端应在主页上显示为健康状态。

`agent-canvas` 命令会一起启动 agent 服务器、自动化后端和
Web 前端。你只需要这一条命令即可在本地运行 OpenHands。
本手册的其余部分将通过浏览器中的 Agent Canvas UI 配置所有内容。

## 4. 在 UI 中配置本地 LLM

首次启动时，Agent Canvas 会打开一个引导流程。在该流程中：

1. 保持 **OpenHands** 作为所选 agent，然后点击 **Next**。
2. 在 **Set up your LLM** 中，选择 **Advanced**。
3. 保持 **Authentication** 设置为 **API key**。
4. 将 **Custom Model** 设置为 `OPENHANDS_LLM_MODEL` 的值，
   即 `openai/Qwen3.6-35B-A3B-GGUF`。
5. 将 **Base URL** 设置为 `http://127.0.0.1:13305/api/v1`。
6. 对于 **API Key**，输入任意非空占位符，例如 `lemonade-local`。
   Lemonade 不需要真实密钥，但 OpenHands 客户端需要一个值
   来发送。

连接字段应如下所示。API 密钥字段会被 UI 遮罩显示。

![Agent Canvas 首次使用时的 LLM Advanced 设置，包含 Lemonade 模型和本地基础 URL](assets/01-llm-advanced-settings.png)

然后选择 **All** 并设置额外的本地模型字段：

1. 滚动到 **Custom Tokenizer** 并将其设置为 `Qwen/Qwen3.6-35B-A3B`。
2. 滚动到 **LiteLLM Extra Body** 并将其设置为
   `{"enable_thinking": true}`。
3. 点击 **Next**。

![Agent Canvas 首次使用时的 LLM All 标签页，包含 Qwen 自定义分词器](assets/02-llm-all-tokenizer-settings.png)

![Agent Canvas 首次使用时的 LLM All 标签页，已配置 LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

LLM 设置应显示为：

| 字段 | 值 |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

`openai/` 前缀会告知 LiteLLM 针对 Lemonade 端点使用与 OpenAI 兼容
的请求格式。自定义分词器是该 GGUF 模型原始的 Hugging
Face 分词器；它使 OpenHands 能够计算与本地模型服务器所见相同的
聊天模板 token 数量。当前的首次使用 LLM 表单不显示压缩器
（condenser）设置。如果你的 Agent Canvas 版本后续在 **Settings > LLM**
下暴露了压缩器设置，请使用 `llm_summarizing`，并将最大 token
数设置为低于 Lemonade 上下文窗口的值，例如 `56000`。

## 5. 安装 GitHub 和 Slack MCP 服务器

在 Agent Canvas UI 中，打开 **Customize**（或 **Settings > MCP**）以添加
为 agent 提供 GitHub 和 Slack 工具的 MCP 服务器。令牌值
仅会发送到你本地的 Agent Server，并以加密设置的形式持久化保存。

### GitHub MCP 服务器

使用以下设置添加一个新的 MCP 服务器：

| 字段 | 值 |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = 你的 GitHub 令牌 |

请使用对你想要摘要的仓库具有读取权限的 GitHub 令牌。

### Slack MCP 服务器

使用以下设置添加第二个 MCP 服务器：

| 字段 | 值 |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = 你的摘要频道 ID |

将 `SLACK_CHANNEL_IDS` 设置为摘要频道 ID（与
`SLACK_DIGEST_CHANNEL` 相同的值），这样 agent 就无需翻遍每个 Slack
频道。

添加完两个服务器后，在每个服务器上使用 **Test** 按钮确认它
能够连接并公布其工具。GitHub 服务器应列出 GitHub 工具，而
Slack 服务器应列出 Slack 工具。

![已安装 GitHub 和 Slack 服务器的 Agent Canvas MCP 页面](assets/04-mcp-servers-installed.png)

## 6. 创建摘要自动化

在 Agent Canvas UI 中，打开 **Automations** 页面并创建一个新的
自动化：

1. 选择 **Create automation** 并选择 **Prompt preset** 类型。
2. 将 **Name** 设置为 `GitHub Development Digest to Slack`。
3. 将 **Prompt** 设置为以下文本，将仓库和
   频道占位符替换为你自己的值：

   ```text
   Use the GitHub MCP server for exactly one repository: your-org/your-repo.
   Inspect recent development activity since the previous weekday, including
   merged pull requests, newly opened or reopened pull requests, notable
   commits pushed to main or release branches, new issues, important issue
   updates, releases, risks, blockers, and review requests. Keep GitHub
   lookups small: inspect the latest 3 to 5 commits, pull requests, issues,
   and releases. Use the Slack MCP server to post directly to channel ID
   C0123456789. Keep the Slack message concise: title with date range, 3 to 7
   bullets, links back to GitHub, and a Needs attention section only if
   needed. End with: This digest was generated by an AI agent (OpenHands) on
   behalf of the user. Do not include secrets, raw tokens, private
   environment variables, or unrelated Slack messages.
   ```

4. 将 **Trigger** 设置为 **Cron**，调度表达式为 `0 9 * * 1-5`（工作日
   上午 9 点），并将 **Timezone** 设置为你所在的时区，例如
   `America/New_York`。
5. 将 **Timeout** 设置为 `900` 秒。
6. 保存该自动化。

自动化详情页面会显示新建的自动化及其 cron 触发器和
生成的 prompt-preset 入口点。

![创建后的 Agent Canvas 自动化详情页面](assets/05-automation-created.png)
## 7. 测试自动化

在 Agent Canvas UI 的自动化详情页面：

1. 点击 **Run now**(或 **Dispatch**)立即运行一次自动化。
2. 观察同一页面上的运行列表。最新的运行应转变为
   `COMPLETED`。
3. 打开你的目标 Slack 频道。其中应包含生成的摘要。

你不需要等待 cron 计划任务触发——**Run now** 会按需触发一次
运行,这样你可以在依赖计划任务之前确认提示词、MCP 连接和 Slack 发布
是否都正常工作。

![Agent Canvas 自动化运行成功完成](assets/06-automation-run-completed.png)

![Slack 频道显示生成的 OpenHands 摘要](assets/07-slackbot-message.png)

## 故障排除

- **Lemonade 已停止运行：** 在步骤 1 中使用
  `lemonade run "${LEMONADE_MODEL}"` 命令重新启动它，然后重新运行健康
  检查。
- **`npm install -g` 因权限错误而失败：** 在 Linux 或 WSL 上，
  配置一个用户所属的全局 npm 目录，将其添加到你的 shell 启动
  文件中，然后重新安装 Agent Canvas：

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  如果你使用 `zsh`，请将相同的 `export PATH=...` 行添加到 `~/.zshrc` 中,
  而不是 `~/.bashrc`。
- **设置 `custom_tokenizer` 后 Agent Canvas 拒绝 LLM 设置：**
  在 Agent Server Python 环境中安装 `transformers`，如有需要重启 Agent
  Canvas，然后重试保存 LLM 设置。设置 `custom_tokenizer` 时，OpenHands
  需要 Transformers 来加载分词器聊天模板。
- **Agent Canvas 无法连接到 Lemonade：** 验证
  `curl -fsS "${LEMONADE_BASE_URL}/health"`，并确认在
  首次使用的 LLM 表单或 **Settings > LLM** 中输入的基础 URL 与正在
  运行的本地端点或 HTTPS 隧道一致。
- **LLM 设置未保存：** 确保你在输入值后点击了 **Next**。
  重新打开 **Settings > LLM** 以确认这些值
  已被保存。
- **GitHub MCP 无法查看私有仓库：** 确认 GitHub 令牌具有对目标仓库的
  读取权限，并确认 **Customize** 中的 MCP **Test** 按钮
  显示了 GitHub 工具。
- **Slack 可以读取频道但无法发布：** 将 Slack 应用邀请到
  目标频道，并确认该机器人具有 `chat:write` 权限。
- **该自动化列出的 Slack 频道过多：** 使用 Slack 频道 ID，
  并在 **Customize** 中为 Slack MCP 服务器设置 `SLACK_CHANNEL_IDS`。
- **自动化运行失败或超出上下文限制：** 确认启动 Lemonade 时
  使用了 `ctx_size=65536`，确认 OpenHands LLM 已设置 `custom_tokenizer`，
  并使用明确指定的仓库，将 GitHub 结果集限制在 3 到 5
  项之间。如果你的 Agent Canvas 版本提供了压缩器（condenser）设置，请将压缩器
  最大令牌数设置为低于 Lemonade 上下文窗口的值。

## 后续步骤

- 添加一个每周仅发布版本的摘要。
- 添加一个由 GitHub 事件触发的自动化，以更快地获取 PR 或推送提醒。
- 将同一份摘要路由到 Notion、Linear 或其他基于 MCP 的工具中。

## 资源

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Lemonade Server 文档](https://lemonade-server.ai/docs)
- [OpenHands extensions 仓库](https://github.com/OpenHands/extensions)
- [Model Context Protocol 服务器](https://github.com/modelcontextprotocol/servers)
- [Slack MCP 软件包](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)