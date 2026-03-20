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

This playbook teaches you how to serve LLMs using vLLM on your GPU and interact with models through a modern web interface.

## In This Playbook, You Will Learn

- How to set up and start a vLLM server with ROCm support
- How to download and configure LLM models (using Qwen3-1.7B as an example)
- How to interact with models via OpenAI-compatible API endpoints
- How to use the Gradio web interface for interactive chat with streaming responses
- How to configure server parameters for different use cases

## Installing vLLM

vLLM can be installed in several ways depending on your environment and preferences:

- **PyPI Wheel** - Install from Python Package Index using pip
- **Docker** - Use prebuilt container images with ROCm support for AMD GPUs
- **Build from Source** - Compile vLLM locally with custom configurations

For this playbook, we'll use the **prebuilt wheel** which includes vLLM with ROCm support, making it the easiest way to get started on AMD GPUs.

## Preparation

### Install vLLM

Create a Python virtual environment and activate it:

```bash
python -m venv vllm_env
source vllm_env/bin/activate
```

Install PyTorch 2.9.1 with ROCm support:

```bash
pip install torch==2.9.1 --extra-index-url https://download.pytorch.org/whl/rocm7.12
```

Install vLLM from the prebuilt ROCm wheel:

```bash
pip install vllm --extra-index-url https://wheels.vllm.ai/rocm/0.16.1/rocm712
```

## Quick Start

### 1. Start the vLLM Server

Start the vLLM server:

```bash
vllm serve /data/Qwen3_1_7B
```

The server will start on `http://localhost:8000` with the Qwen3-1.7B model.

**Common server options:**

```bash
# Allow external connections and customize settings
vllm serve /data/Qwen3_1_7B \
  --max-model-len 4096
```

### 2. Test the server with curl

You can test the server using the curl script:

```bash
./curl_script.sh
```

Or use the curl command directly:

```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "/data/Qwen3_1_7B",
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

### 3. Use the Gradio Web Interface

For an interactive chat experience, launch the Gradio client:

```bash
./run_gradio_client.sh
```

Then open your browser to `http://localhost:7860`

**Custom Configuration:**

```bash
# Change port
./run_gradio_client.sh --port 8080

# Different model
./run_gradio_client.sh --model /path/to/model

# Different vLLM server
./run_gradio_client.sh --server http://192.168.1.100:8000

# All options
./run_gradio_client.sh --port 8080 --model /data/Qwen3_1_7B --server http://localhost:8000
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
vllm serve /data/Qwen3_1_7B --gpu-memory-utilization 0.7
```

Or limit the maximum model length:
```bash
vllm serve /data/Qwen3_1_7B --max-model-len 2048
```

### Gradio client issues

**"Gradio not found" error:**
```bash
pip install -r requirements_gradio.txt
```

**"Cannot connect to vLLM server" in UI:**
- Verify the vLLM server is running: `curl http://localhost:8000/health`
- Check the server URL in the Gradio settings panel
- Ensure firewall allows connections on port 8000

**Streaming not working:**
- Update to the latest version of Gradio: `pip install --upgrade gradio`
- Verify vLLM server supports streaming API
- Check browser console for JavaScript errors

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
