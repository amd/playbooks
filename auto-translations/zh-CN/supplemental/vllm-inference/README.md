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

vLLM 是一款专为大语言模型 (LLM) 设计的高性能推理引擎。它通过连续批处理提供优化的服务，实现高吞吐量，并提供与 OpenAI 兼容的 API，以实现无缝的应用程序集成。这使得 vLLM 非常适合对速度和资源效率要求苛刻的生产部署。

本指南将教你如何在集成 GPU 上使用容器化的 vLLM 提供 LLM 服务，并通过 OpenAI Python API 与模型进行交互。

## 你将学到什么

- 如何设置并启动支持 AMD ROCm™ 的 vLLM 服务器
- 如何通过与 OpenAI 兼容的 API 端点与模型交互
- 如何使用 `vllm-prompt` 向本地服务器发送提示词

## 设置内存配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 检查软件更新

> **注意**：如果未安装 VS Code，你可以通过 AMD Ryzen™ AI Developer Center 进行安装。

<!-- @require:software-update -->
<!-- @device:end -->

## 安装软件先决条件

vLLM 运行在一个预构建的容器中，该容器已预先匹配好 ROCm 及其依赖项。无需额外安装。

无需在主机端安装 vLLM。使用以下命令启动 vLLM：

```bash
vllm-launch
```

该启动器会启动容器，定位到集成 GPU，并暴露一个本地的、与 OpenAI 兼容的 vLLM 服务器。你也可以点击任务栏中的 vLLM 图标。

## 快速入门

### 1. 确认 vLLM 服务器正在运行

`vllm-launch` 可能需要几分钟时间来完成初始化。启动后，服务器将在 `http://localhost:8001` 上可用。请保持启动终端处于打开状态，因为服务器在前台运行，然后打开一个单独的终端来执行剩余步骤。以下示例使用 `Qwen/Qwen3-1.7B`；如果你的启动器配置了其他模型，请在请求中替换为该模型 ID。

### 2. 发送提示词

使用提供的 `vllm-prompt` 脚本向本地的 vLLM OpenAI 兼容服务器发送请求：

```bash
vllm-prompt "Tell me a story"
```

### 3. 使用 OpenAI Python API 与模型对话

由于 vLLM 暴露了与 OpenAI 兼容的 API，你可以使用 `openai` Python 包与其交互。

首先，创建一个 Python 虚拟环境：

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->
<!-- @os:end -->

安装 OpenAI 包
```bash
pip install openai
```

创建一个指向本地 vLLM 服务器（而不是 OpenAI 服务器）的 `OpenAI` 客户端。客户端需要 `api_key`，但 vLLM 不会对其进行验证，因此任意字符串都可以使用：

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

然后，发送一个聊天补全请求。这里使用与 OpenAI API 相同的消息格式——一个包含角色（如 `"user"` 和 `"assistant"`）的消息列表。设置 `stream=True` 意味着响应将增量到达，而不是一次性全部返回：

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

最后，遍历流式返回的数据块，并在每段文本到达时将其打印出来：

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

随附的 [chat_with_model.py](assets/chat_with_model.py) 脚本包含了完整示例，可供下载。


## 选择和配置模型

默认情况下，`vllm-launch` 会在端口 `8001` 上将 `Qwen/Qwen3-1.7B` 作为测试模型提供服务。你可以更改模型、端口以及 vLLM 服务参数，而无需重新构建或编辑容器。

### AMD 测试过的模型

以下模型已由 AMD 预先配置并验证：

| 模型 | 说明 |
|-------|-------|
| `Qwen/Qwen3-1.7B` | 默认模型。轻量级，加载速度快。 |
| `openai/gpt-oss-20b` | 更大的模型，可提供更高质量的响应。 |

### 启动其他模型

使用 `--model`（或 `-m`）传入模型 ID：

```bash
vllm-launch --model openai/gpt-oss-20b
```

### 更改端口

使用 `--port`（或 `-p`）传入大于 1024 的端口号；默认端口为 `8001`：

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

如果更改了端口，请将客户端的 `base_url` 指向相同的端口（例如 `http://localhost:8080/v1`）。

### 传递额外的 vLLM 参数

任何额外的参数都会被直接转发给 vLLM，因此你可以调整服务行为，例如上下文长度或数据类型。有两种方式可以提供这些参数。

**内联方式**，紧跟在启动器选项之后：

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**持久化方式**，在 `~/.local/share/vLLM/vllm-launch.conf` 配置文件中。该文件默认不存在——你需要创建它，并以 Bash 数组的形式添加你的参数：

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

使用 `+=` 来追加到默认参数中，而不是替换它们：

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

如需随时查看所有启动器选项，请运行：

```bash
vllm-launch --help
```

### 模型存储位置

`vllm-launch` 会在以下两个位置查找模型：

| 位置 | 路径 |
|----------|------|
| 系统模型 | `/var/cache/models` |
| 用户模型 | `~/.local/share/vLLM/models` |

你可以将下载的模型放入上述任一目录中，然后通过将其路径或 ID 传给 `--model` 来启动它：

```bash
vllm-launch --model /var/cache/models/my-model
```

> **注意**：以这种方式运行你自己下载的模型，只要将模型放置在上述目录之一中，预计应该可以正常工作，但目前 AMD 尚未正式验证此工作流程。

## 故障排除

### 连接被拒绝

请确保服务器正在运行：
```bash
curl http://localhost:8001/health
```

## 总结

在本指南中，你学习了如何：

- 在集成 GPU 上启动支持 ROCm 的容器化 vLLM
- 启动在端口 8001 上提供与 OpenAI 兼容 API 端点的 vLLM 服务器
- 使用 `vllm-prompt` 发送提示词
- 使用流式和非流式请求向 vLLM 服务器发起 API 调用
- 排查服务器启动、内存和客户端连接方面的常见问题

现在，你已经拥有一个容器化的 vLLM 部署，可在集成 GPU 上以优化的性能为大语言模型提供服务。

## 后续步骤

- **尝试不同的模型** —— 使用 `vllm-launch --model <model>` 来试验不同的 LLM 并比较性能表现（参见[选择和配置模型](#choosing-and-configuring-a-model)）。
- **构建应用程序** —— 使用与 OpenAI 兼容的 API，将 vLLM 集成到 Python 应用、聊天机器人或自动化工作流中。
- **微调并部署** —— 使用 LoRA 或 QLoRA 对模型进行微调，然后使用 vLLM 部署以实现优化的推理性能。
## 其他资源

- **[vLLM 官方文档](https://docs.vllm.ai/)** — 完整的指南和 API 参考
- **[vLLM GitHub 仓库](https://github.com/vllm-project/vllm)** — 源代码、问题反馈和社区讨论