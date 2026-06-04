<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->


# High-Performance LLM Inference with vLLM

## Overview

vLLM is a high-performance inference engine designed for large language models (LLMs). It provides optimized serving with continuous batching for high throughput and an OpenAI-compatible API for seamless application integration. This makes vLLM great for production deployments where speed and resource efficiency are critical.

This playbook teaches you how to serve LLMs using containerized vLLM on the integrated GPU and interact with models through the OpenAI Python API.

## In This Playbook, You Will Learn

- How to set up and start a vLLM server with ROCm support
- How to interact with models via OpenAI-compatible API endpoints
- How to verify the local server and send chat completion requests

## Starting vLLM

This playbook uses a prebuilt container image that includes vLLM, ROCm support, and the helper scripts needed to launch the server. You do not need to install PyTorch, vLLM, or local playbook scripts manually.

There is no host-side vLLM installation step. Start vLLM with:

```bash
vllm-launch
```

The launcher starts the container, targets the integrated GPU, and exposes a local OpenAI-compatible vLLM server.

<!-- @test:id=vllm-launch-available-linux timeout=30 hidden=true -->
```bash
command -v vllm-launch
```
<!-- @test:end -->

## Quick Start

### 1. Confirm the vLLM Server Is Running

After `vllm-launch` starts, the server is available at `http://localhost:8000`. Keep the launch terminal open because the server runs in the foreground, then open a separate terminal for the remaining steps. The examples below use `Qwen/Qwen3-1.7B`; if your launcher is configured for a different model, substitute that model ID in the requests.

### 2. Test the server with curl

Send a chat completion request directly to the local server:

```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3-1.7B",
    "messages": [
      {
        "role": "user",
        "content": "What is the sum of 123 and 456? Show your reasoning."
      }
    ],
    "temperature": 0.7,
    "max_tokens": 2048
  }'
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
    base_url="http://localhost:8000/v1",
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

You can run the complete example directly from the terminal:

```bash
python3 - <<'PY'
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY",
)

response = client.chat.completions.create(
    model="Qwen/Qwen3-1.7B",
    messages=[
        {"role": "user", "content": "Tell me a short story"},
    ],
    max_tokens=2048,
    stream=True,
)

for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)

print()
PY
```

## Troubleshooting

### Connection refused

Make sure the server is running:
```bash
curl http://localhost:8000/health
```

### Out of memory

If the launcher exits with an out-of-memory error, use a smaller model or reduce the configured context length before restarting:

```bash
vllm-launch
```

## Requirements

### For vLLM Server
- Linux
- `vllm-launch` container launcher
- AMD system with a supported integrated GPU
- Sufficient memory for the selected model

## Summary

In this playbook, you learned how to:

- Start containerized vLLM with ROCm support on the integrated GPU
- Start a vLLM server with OpenAI-compatible API endpoints on port 8000
- Test the server using curl commands and API requests
- Make API calls to the vLLM server using both streaming and non-streaming requests
- Troubleshoot common issues with server startup, memory, and client connections

You now have a containerized vLLM deployment for serving large language models with optimized performance on the integrated GPU.

## Additional Resources

- **[vLLM Official Documentation](https://docs.vllm.ai/)** - Comprehensive guides and API references
- **[vLLM GitHub Repository](https://github.com/vllm-project/vllm)** - Source code, issues, and community discussions
