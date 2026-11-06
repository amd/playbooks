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

vLLM 是一款专为大语言模型 (LLM) 设计的高性能推理引擎。它通过连续批处理提供优化的服务，实现高吞吐量，并提供与 OpenAI 兼容的 API，便于无缝集成到应用程序中。这使得 vLLM 非常适合对速度和资源效率要求严苛的生产部署场景。

本手册将教您如何在集成 GPU 上使用容器化的 vLLM 提供 LLM 服务，并通过 OpenAI Python API 与模型进行交互。

## 您将学到什么

- 如何设置并启动支持 AMD ROCm™ 的 vLLM 服务器
- 如何通过与 OpenAI 兼容的 API 端点与模型进行交互
- 如何使用 `vllm-prompt` 向本地服务器发送提示词

## 设置内存配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 检查软件更新

> **注意**：如果未安装 VS Code，您可以通过 AMD Ryzen™ AI Developer Center 进行安装。

<!-- @require:software-update -->
<!-- @device:end -->

## 安装软件先决条件

vLLM 运行在一个预构建的容器中，该容器已预先匹配好 ROCm 及其依赖项。无需进行额外安装。

无需在主机端执行 vLLM 安装步骤。通过以下方式启动 vLLM：

```bash
vllm-launch
```

启动器会启动容器，定位到集成 GPU，并暴露一个与 OpenAI 兼容的本地 vLLM 服务器。您也可以点击任务栏中的 vLLM 图标。

## 快速入门

### 1. 确认 vLLM 服务器正在运行

`vllm-launch` 可能需要几分钟时间来完成所有初始化工作。启动后，服务器将在 `http://localhost:8001` 上可用。请保持启动终端处于打开状态，因为服务器在前台运行，然后再打开一个单独的终端执行后续步骤。以下示例使用 `Qwen/Qwen3-1.7B`；如果您的启动器配置为其他模型，请在请求中替换为相应的模型 ID。

### 2. 发送提示词

使用提供的 `vllm-prompt` 脚本向本地 vLLM OpenAI 兼容服务器发送请求：

```bash
vllm-prompt "Tell me a story"
```

### 3. 使用 OpenAI Python API 与模型聊天

由于 vLLM 暴露了与 OpenAI 兼容的 API，您可以使用 `openai` Python 软件包与之交互。

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

安装 OpenAI 软件包
```bash
pip install openai
```

创建一个指向本地 vLLM 服务器（而非 OpenAI 服务器）的 `OpenAI` 客户端。客户端需要提供 `api_key`，但 vLLM 不会对其进行验证，因此任意字符串都可以使用：

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

然后，发送一个聊天补全请求。此请求使用与 OpenAI API 相同的消息格式——一个包含 `"user"` 和 `"assistant"` 等角色的消息列表。设置 `stream=True` 意味着响应将以增量方式到达，而不是一次性全部返回：

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

默认情况下，`vllm-launch` 会在端口 `8001` 上提供 `Qwen/Qwen3-1.7B` 作为测试模型。您可以更改模型、端口和 vLLM 服务参数，而无需重新构建或编辑容器。

### 经过 AMD 测试的模型

以下模型已经过预配置并通过 AMD 验证：

| 模型 | 备注 |
|-------|-------|
| `Qwen/Qwen3-1.7B` | 默认模型。轻量且加载速度快。 |
| `openai/gpt-oss-20b` | 更大的模型，可获得更高质量的响应。 |

### 启动不同的模型

使用 `--model`（或 `-m`）传入模型 ID：

```bash
vllm-launch --model openai/gpt-oss-20b
```

### 更改端口

使用 `--port`（或 `-p`）传入一个大于 1024 的端口号；默认值为 `8001`：

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

如果您更改了端口，请将客户端的 `base_url` 指向相同的端口（例如 `http://localhost:8080/v1`）。

### 传递额外的 vLLM 参数

任何附加参数都会直接转发给 vLLM，因此您可以调整服务行为，例如上下文长度或数据类型。提供这些参数有两种方式。

**内联方式**，在启动器选项之后添加：

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**持久化方式**，在 `~/.local/share/vLLM/vllm-launch.conf` 配置文件中添加。该文件默认不存在——您需要创建它，并以 Bash 数组的形式添加您的参数：

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

使用 `+=` 可以在默认参数的基础上进行追加，而不是替换它们：

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

您可以将已下载的模型放置在上述任一目录中，并通过向 `--model` 传递其路径或 ID 来启动它：

```bash
vllm-launch --model /var/cache/models/my-model
```

> **注意**：只要将模型放置在上述目录之一中，预计以这种方式运行您自己下载的模型即可正常工作，但该工作流程目前尚未经过 AMD 官方验证。

## 故障排除

### 连接被拒绝

请确保服务器正在运行：
```bash
curl http://localhost:8001/health
```

## 总结

通过本手册，您已学会如何：

- 在集成 GPU 上启动支持 ROCm 的容器化 vLLM
- 在端口 8001 上启动具有 OpenAI 兼容 API 端点的 vLLM 服务器
- 使用 `vllm-prompt` 发送提示词
- 使用流式和非流式请求对 vLLM 服务器进行 API 调用
- 排查服务器启动、内存及客户端连接方面的常见问题

现在，您已拥有一个容器化的 vLLM 部署方案，可在集成 GPU 上以优化的性能提供大语言模型服务。

## 后续步骤

- **尝试不同的模型** — 使用 `vllm-launch --model <model>` 体验不同的 LLM 并比较性能表现（参见[选择和配置模型](#choosing-and-configuring-a-model)）。
- **构建应用程序** — 使用与 OpenAI 兼容的 API，将 vLLM 集成到 Python 应用程序、聊天机器人或自动化工作流中。
- **微调并提供服务** — 使用 LoRA 或 QLoRA 对模型进行微调，然后通过 vLLM 部署以实现优化的推理性能。
## 其他资源

- **[vLLM 官方文档](https://docs.vllm.ai/)** —— 全面的指南和 API 参考
- **[vLLM GitHub 仓库](https://github.com/vllm-project/vllm)** —— 源代码、问题反馈与社区讨论