<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> 本使用手册使用了 GitHub 无法渲染的特殊标签。请访问 [amd.com/playbooks](https://amd.com/playbooks) 以正确预览此内容。
<!-- @github-only:end -->


## 概述

vLLM 是一款专为大语言模型（LLM）设计的高性能推理引擎。它通过持续批处理提供优化的服务以实现高吞吐量，并提供与 OpenAI 兼容的 API 以实现无缝的应用程序集成。这使得 vLLM 非常适合对速度和资源效率要求严苛的生产部署环境。

本使用手册将教您如何在集成 GPU 上使用容器化的 vLLM 提供 LLM 服务，并通过 OpenAI Python API 与模型进行交互。

## 您将学到什么

- 如何设置并启动支持 AMD ROCm™ 的 vLLM 服务器
- 如何通过与 OpenAI 兼容的 API 端点与模型进行交互
- 如何使用 `vllm-prompt` 向本地服务器发送提示词

## 设置内存配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 检查软件更新

> **注意**：如果尚未安装 VS Code，您可以通过 AMD Ryzen™ AI Developer Center 进行安装。

<!-- @require:software-update -->
<!-- @device:end -->

## 安装软件前置条件

本使用手册使用预构建的容器镜像，其中包含 vLLM、ROCm 支持以及启动服务器所需的辅助脚本。您无需手动安装 PyTorch、vLLM 或本地使用手册脚本。

无需在主机端安装 vLLM。请使用以下命令启动 vLLM：

```bash
vllm-launch
```

该启动程序会启动容器，以集成 GPU 为目标，并暴露一个本地的、与 OpenAI 兼容的 vLLM 服务器。或者，您也可以单击任务栏中的 vLLM 图标。

## 快速开始

### 1. 确认 vLLM 服务器正在运行

`vllm-launch` 可能需要几分钟时间来初始化所有内容。启动后，服务器将在 `http://localhost:8001` 上可用。请保持启动终端处于打开状态，因为服务器在前台运行，然后为剩余步骤打开一个单独的终端。以下示例使用 `Qwen/Qwen3-1.7B`；如果您的启动程序配置了其他模型，请在请求中替换为该模型 ID。

### 2. 发送提示词

使用提供的 `vllm-prompt` 脚本向本地的与 OpenAI 兼容的 vLLM 服务器发送请求：

```bash
vllm-prompt "Tell me a story"
```

### 3. 使用 OpenAI Python API 与模型聊天

由于 vLLM 提供了与 OpenAI 兼容的 API，您可以使用 `openai` Python 包与其进行交互。

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

创建一个指向本地 vLLM 服务器（而非 OpenAI 服务器）的 `OpenAI` 客户端。客户端要求提供 `api_key`，但 vLLM 不会对其进行验证，因此任何字符串都可以使用：

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

接下来，发送一个聊天补全请求。该请求使用与 OpenAI API 相同的消息格式——由带有 `"user"` 和 `"assistant"` 等角色的消息组成的列表。设置 `stream=True` 意味着响应将以增量方式到达，而不是一次性全部返回：

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


## 故障排除

### 连接被拒绝

请确保服务器正在运行：
```bash
curl http://localhost:8001/health
```

## 总结

在本使用手册中，您学习了如何：

- 在集成 GPU 上启动支持 ROCm 的容器化 vLLM
- 在 8001 端口上启动具有与 OpenAI 兼容的 API 端点的 vLLM 服务器
- 使用 `vllm-prompt` 发送提示词
- 使用流式和非流式请求两种方式向 vLLM 服务器发起 API 调用
- 排查服务器启动、内存以及客户端连接方面的常见问题

现在，您已拥有一个容器化的 vLLM 部署方案，可在集成 GPU 上以优化性能提供大语言模型服务。

## 后续步骤

- **尝试不同模型** — 在 `vllm-launch` 配置中更换模型，以试验不同的 LLM 并比较其性能。
- **构建应用程序** — 使用与 OpenAI 兼容的 API 将 vLLM 集成到 Python 应用、聊天机器人或自动化工作流中。
- **微调并部署** — 使用 LoRA 或 QLoRA 微调模型，然后使用 vLLM 进行部署以实现优化推理。

## 更多资源

- **[vLLM 官方文档](https://docs.vllm.ai/)** — 全面的指南和 API 参考
- **[vLLM GitHub 仓库](https://github.com/vllm-project/vllm)** — 源代码、问题反馈与社区讨论