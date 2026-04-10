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

This playbook teaches you how to serve LLMs using vLLM on your STX Halo™ GPU and interact with models through the OpenAI Python API.

## In This Playbook, You Will Learn

- How to set up and start a vLLM server with ROCm support
- How to interact with models via OpenAI-compatible API endpoints
- How to configure server parameters for different use cases

## Installing vLLM

vLLM can be installed in several ways depending on your environment and preferences:

- **AMD ROCm Wheel Index** - Install AMD-provided ROCm-enabled vLLM wheels using pip
- **Docker** - Use prebuilt container images with ROCm support for AMD GPUs
- **Build from Source** - Compile vLLM locally with custom configurations

For this playbook, we'll use the prebuilt AMD ROCm wheel from AMD's package index, which is the easiest way to get started with ROCm-enabled vLLM on AMD GPUs.

## Preparation

### Install vLLM

Create a Python 3.12 virtual environment and activate it:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install ROCm 7.12.0 and PyTorch 2.9.1 in the virtual environment:

```bash
python -m pip install \
  --index-url https://repo.amd.com/rocm/whl/gfx1151/ \
  "torch==2.9.1+rocm7.12.0" \
  "torchaudio==2.9.0+rocm7.12.0" \
  "torchvision==0.24.0+rocm7.12.0"
```

Install vLLM from the prebuilt ROCm wheel:

```bash
python -m pip install \
  --extra-index-url https://rocm.frameworks.amd.com/whl/gfx1151/ \
  "vllm==0.16.1.dev10+g11515110f.d20260323.rocm712"
```

Set the environment variables required by the ROCm pip packages before starting vLLM:

```bash
export PYTHONPATH=.venv/lib/python3.12/site-packages/_rocm_sdk_core/share/amd_smi
export FLASH_ATTENTION_TRITON_AMD_ENABLE=TRUE
```

Check the installation:

```bash
echo "=== vLLM ===" && python -c "import vllm; print('vLLM version:', vllm.__version__)"
echo "=== PyTorch ===" && python -c "import torch; print('PyTorch:', torch.__version__); print('HIP available:', torch.cuda.is_available()); print('HIP built:', torch.backends.hip.is_built() if hasattr(torch.backends, 'hip') else 'N/A')"
echo "=== flash-attn ===" && python -c "import flash_attn; print('flash-attn:', flash_attn.__version__)"
```

## Quick Start

### 1. Start the vLLM Server

Start the vLLM server:

```bash
vllm serve Qwen/Qwen3-1.7B
```

The server will start on `http://localhost:8000` with the Qwen3-1.7B model. The server runs in the foreground, so open a separate terminal for the remaining steps.

**Common server options:**

```bash
vllm serve Qwen/Qwen3-1.7B \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.9 \
  --max-num-seqs 16
```

- `--max-model-len` - Sets the maximum context length. Longer contexts use more memory, so lowering this frees up GPU memory for other uses.
- `--gpu-memory-utilization` - Controls what fraction of GPU memory vLLM reserves (0.0-1.0). vLLM pre-allocates memory for its KV cache, which stores the attention state for active requests. A higher value means more cache space and more concurrent requests, but setting it too high can cause out-of-memory errors.
- `--max-num-seqs` - The maximum number of requests vLLM will process at once. vLLM uses continuous batching, meaning it can dynamically add and remove requests from a running batch rather than waiting for an entire batch to finish. This keeps the GPU busy and improves throughput.

### 2. Test the server with curl

You can test the server using the curl script:

```bash
./assets/curl_script.sh
```

Or use the curl command directly:

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

Since vLLM exposes an OpenAI-compatible API, you can use the `openai` Python package to interact with it. Install it first:

```bash
python -m venv .openai-venv
source .openai-venv/bin/activate
python -m pip install openai
```

The included `chat_with_model.py` script demonstrates this. First, create an `OpenAI` client pointed at the local vLLM server instead of OpenAI's servers. The `api_key` is required by the client but vLLM doesn't validate it, so any string works:

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

Run the script:

```bash
python assets/chat_with_model.py
```

## Troubleshooting

### Connection refused

Make sure the server is running:
```bash
curl http://localhost:8000/health
```

### Out of memory

Reduce GPU memory usage when starting the server:
```bash
vllm serve Qwen/Qwen3-1.7B --gpu-memory-utilization 0.7
```

Or limit the maximum model length:
```bash
vllm serve Qwen/Qwen3-1.7B --max-model-len 2048
```

## Requirements

### For vLLM Server
- Python 3.8+
- vLLM installed
- GPU with sufficient memory

## Summary

In this playbook, you learned how to:

- Set up and run vLLM with ROCm support for high-performance LLM inference on AMD GPUs
- Start and configure a vLLM server with OpenAI-compatible API endpoints on port 8000
- Test the server using curl commands and API requests
- Make API calls to the vLLM server using both streaming and non-streaming requests
- Troubleshoot common issues with server startup, memory, and client connections

You now have a fully functional vLLM deployment for serving large language models with optimized performance on your GPU.

## Additional Resources

- **[vLLM Official Documentation](https://docs.vllm.ai/)** - Comprehensive guides and API references
- **[vLLM GitHub Repository](https://github.com/vllm-project/vllm)** - Source code, issues, and community discussions
