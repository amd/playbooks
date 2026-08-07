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

vLLM 是一款专为大语言模型（LLM）设计的高性能推理引擎。它通过持续批处理提供优化的服务以实现高吞吐量，并提供与 OpenAI 兼容的 API 以实现无缝的应用集成。这使得 vLLM 非常适合对速度和资源效率要求严苛的生产环境部署。

本手册将教您如何在集成 GPU 上使用容器化的 vLLM 提供 LLM 服务，并通过 OpenAI Python API 与模型进行交互。

## 您将学到什么

- 如何设置并启动支持 AMD ROCm™ 的 vLLM 服务器
- 如何通过与 OpenAI 兼容的 API 端点与模型交互
- 如何使用 `vllm-prompt` 向本地服务器发送提示

## 设置内存配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 检查软件更新

> **注意**：如果未安装 VS Code，您可以通过 AMD Ryzen™ AI Developer Center 进行安装。

<!-- @require:software-update -->
<!-- @device:end -->

## 安装软件先决条件

vLLM 在预构建的容器中运行，ROCm 及其依赖项均已预先匹配。无需进行额外安装。

无需在主机端执行 vLLM 安装步骤。使用以下命令启动 vLLM：

```bash
vllm-launch
```

该启动器会启动容器、定位到集成 GPU，并暴露一个与 OpenAI 兼容的本地 vLLM 服务器。您也可以点击任务栏中的 vLLM 图标。

## 快速入门

### 1. 确认 vLLM 服务器正在运行

`vllm-launch` 可能需要几分钟才能完成初始化。启动后，服务器将在 `http://localhost:8001` 上可用。请保持启动终端处于打开状态，因为服务器在前台运行，然后打开一个单独的终端以执行剩余步骤。以下示例使用 `Qwen/Qwen3-1.7B`；如果您的启动器配置为不同的模型，请在请求中替换为该模型 ID。

### 2. 发送提示

使用提供的 `vllm-prompt` 脚本向本地与 OpenAI 兼容的 vLLM 服务器发送请求：

```bash
vllm-prompt "Tell me a story"
```

### 3. 使用 OpenAI Python API 与模型对话

由于 vLLM 暴露了与 OpenAI 兼容的 API，您可以使用 `openai` Python 包与其交互。

首先，创建一个 Python 虚拟环境：

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

安装 OpenAI 包
```bash
pip install openai
```

创建一个指向本地 vLLM 服务器而非 OpenAI 服务器的 `OpenAI` 客户端。客户端要求提供 `api_key`，但 vLLM 不会对其进行验证，因此任意字符串均可使用：

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

然后，发送一个聊天补全请求。此处使用与 OpenAI API 相同的消息格式——一个包含 `"user"` 和 `"assistant"` 等角色的消息列表。设置 `stream=True` 意味着响应将以增量方式到达，而不是一次性全部返回：

```python
response = client.chat.completions.create(
    model="Qwen/Qwen3-1.7B",
    messages=[
        {"role": "user", "content": "Tell me a short story"},
    ],
    max_tokens=2048,  # Maximum number of tokens the model will generate in its response
    stream=True,
)
```

最后，遍历流式返回的数据块，并在每段文本到达时打印出来：

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

随附的 [chat_with_model.py](assets/chat_with_model.py) 脚本包含了完整示例，可供下载。


## 选择和配置模型

默认情况下，`vllm-launch` 会在端口 `8001` 上提供 `Qwen/Qwen3-1.7B` 作为测试模型。您可以在不重建或编辑容器的情况下更改模型、端口以及 vLLM 服务参数。

### AMD 测试过的模型

以下模型已由 AMD 预配置并验证：

| 模型 | 说明 |
|-------|-------|
| `Qwen/Qwen3-1.7B` | 默认模型。轻量且加载速度快。 |
| `openai/gpt-oss-20b` | 更大的模型，可提供更高质量的响应。 |

### 启动不同的模型

使用 `--model`（或 `-m`）传入模型 ID：

```bash
vllm-launch --model openai/gpt-oss-20b
```

### 更改端口

使用 `--port`（或 `-p`）传入一个大于 1024 的端口；默认端口为 `8001`：

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

如果更改了端口，请将客户端的 `base_url` 指向相同的端口（例如 `http://localhost:8080/v1`）。

### 传递额外的 vLLM 参数

任何附加参数都会直接转发给 vLLM，因此您可以调整诸如上下文长度或数据类型等服务行为。有两种方式可以提供这些参数。

**内联方式**，在启动器选项之后添加：

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**持久化方式**，在位于 `~/.local/share/vLLM/vllm-launch.conf` 的配置文件中添加。此文件默认不存在——请自行创建，并将参数以 Bash 数组的形式添加：

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

使用 `+=` 可以在默认参数的基础上追加，而不是替换它们：

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

若需随时查看所有启动器选项，请运行：

```bash
vllm-launch --help
```

### 模型存储位置

`vllm-launch` 会在以下两个位置查找模型：

| 位置 | 路径 |
|----------|------|
| 系统模型 | `/var/cache/models` |
| 用户模型 | `~/.local/share/vLLM/models` |

您可以将下载的模型放置于上述任一目录中，并通过向 `--model` 传递其路径或 ID 来启动该模型：

```bash
vllm-launch --model /var/cache/models/my-model
```

> **注意**：一旦将模型放置于上述目录之一，以这种方式运行您自己下载的模型预期是可行的，但此工作流程尚未经过 AMD 的正式验证。

## 疑难解答

### 连接被拒绝

请确保服务器正在运行：
```bash
curl http://localhost:8001/health
```

## 总结

在本手册中，您学习了如何：

- 在集成 GPU 上启动支持 ROCm 的容器化 vLLM
- 在端口 8001 上启动具有与 OpenAI 兼容 API 端点的 vLLM 服务器
- 使用 `vllm-prompt` 发送提示
- 使用流式和非流式请求两种方式向 vLLM 服务器发起 API 调用
- 排查服务器启动、内存和客户端连接方面的常见问题

现在，您已拥有一个容器化的 vLLM 部署，可在集成 GPU 上以优化的性能提供大语言模型服务。

## 后续步骤

- **尝试不同的模型** — 使用 `vllm-launch --model <model>` 尝试不同的 LLM，并比较性能表现（参见[选择和配置模型](#choosing-and-configuring-a-model)）。
- **构建应用程序** — 使用与 OpenAI 兼容的 API 将 vLLM 集成到 Python 应用、聊天机器人或自动化工作流中。
- **微调并部署** — 使用 LoRA 或 QLoRA 微调模型，然后通过 vLLM 部署以实现优化的推理性能。
## 其他资源

- **[vLLM 官方文档](https://docs.vllm.ai/)** — 全面的指南和 API 参考
- **[vLLM GitHub 仓库](https://github.com/vllm-project/vllm)** — 源代码、问题反馈和社区讨论