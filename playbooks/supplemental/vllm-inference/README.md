<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->


## Overview

vLLM is a high-performance inference engine designed for large language models (LLMs). It provides optimized serving with continuous batching for high throughput and an OpenAI-compatible API for seamless application integration. This makes vLLM great for production deployments where speed and resource efficiency are critical.

This playbook teaches you how to serve LLMs using containerized vLLM on the integrated GPU and interact with models through the OpenAI Python API.

## What You'll Learn

- How to set up and start a vLLM server with AMD ROCm™ support
- How to interact with models via OpenAI-compatible API endpoints
- How to send prompts to the local server with `vllm-prompt`

## Setting the Memory Configuration

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Check for Software Updates

> **Note**: If VS Code is not installed, you can install it with AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installing Software Prerequisites

This playbook uses a prebuilt container image that includes vLLM, ROCm support, and the helper scripts needed to launch the server. You do not need to install PyTorch, vLLM, or local playbook scripts manually.

There is no host-side vLLM installation step. Start vLLM with:

```bash
vllm-launch
```

The launcher starts the container, targets the integrated GPU, and exposes a local OpenAI-compatible vLLM server. Alternatively, click the vLLM icon in the taskbar.

## Quick Start

### 1. Confirm the vLLM Server Is Running

The `vllm-launch` may take a couple minutes to initialize everything. Once it starts, the server is available at `http://localhost:8001`. Keep the launch terminal open because the server runs in the foreground, then open a separate terminal for the remaining steps. The examples below use `Qwen/Qwen3-1.7B`; if your launcher is configured for a different model, substitute that model ID in the requests.

### 2. Send a Prompt

Use the provided `vllm-prompt` script to send a request to the local vLLM OpenAI-compatible server:

```bash
vllm-prompt "Tell me a story"
```

### 3. Chat with the model using the OpenAI Python API

Since vLLM exposes an OpenAI-compatible API, you can use the `openai` Python package to interact with it. Install the client package in your local Python environment:

```bash
python3 -m pip install openai
```

Create an `OpenAI` client pointed at the local vLLM server instead of OpenAI's servers. The `api_key` is required by the client but vLLM doesn't validate it, so any string works:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Then send a chat completion request. This uses the same message format as the OpenAI API — a list of messages with roles like `"user"` and `"assistant"`. Setting `stream=True` means the response will arrive incrementally rather than all at once:

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

Finally, iterate over the streamed chunks and print each piece of text as it arrives:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

The included [chat_with_model.py](assets/chat_with_model.py) script contains the entire example and can be downloaded.


## Troubleshooting

### Connection refused

Make sure the server is running:
```bash
curl http://localhost:8001/health
```

## Summary

In this playbook, you learned how to:

- Start containerized vLLM with ROCm support on the integrated GPU
- Start a vLLM server with OpenAI-compatible API endpoints on port 8001
- Send prompts with `vllm-prompt`
- Make API calls to the vLLM server using both streaming and non-streaming requests
- Troubleshoot common issues with server startup, memory, and client connections

You now have a containerized vLLM deployment for serving large language models with optimized performance on the integrated GPU.

## Next Steps

- **Try different models** — Swap the model in the `vllm-launch` configuration to experiment with different LLMs and compare performance.
- **Build an application** — Use the OpenAI-compatible API to integrate vLLM into a Python app, chatbot, or automation workflow.
- **Fine-tune and serve** — Fine-tune a model using LoRA or QLoRA, then deploy it with vLLM for optimized inference.

## Additional Resources

- **[vLLM Official Documentation](https://docs.vllm.ai/)** — Comprehensive guides and API references
- **[vLLM GitHub Repository](https://github.com/vllm-project/vllm)** — Source code, issues, and community discussions
