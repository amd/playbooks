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

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['chat_with_model.py', 'curl_script.sh']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in ['chat_with_model.py']:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=vllm-assets-linux timeout=30 hidden=True -->
```bash
set -euo pipefail

test -f curl_script.sh
test -f chat_with_model.py

python -m py_compile chat_with_model.py
bash curl_script.sh --help >/dev/null

echo "PASS: Required vLLM asset scripts are present and valid"
```
<!-- @test:end -->

Create a Python 3.12 virtual environment and activate it:

<!-- @test:id=create-venv timeout=30 hidden=True -->
```bash
python3 -m venv .venv
source .venv/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source .venv/bin/activate" -->

Install PyTorch 2.9.1 built for ROCm 7.12.0, along with the required ROCm Python packages, in the virtual environment:

<!-- @test:id=pytorch-install timeout=600 hidden=True setup=activate-venv -->
```bash
python -m pip install \
  --index-url https://repo.amd.com/rocm/whl/gfx1151/ \
  "torch==2.9.1+rocm7.12.0" \
  "torchaudio==2.9.0+rocm7.12.0" \
  "torchvision==0.24.0+rocm7.12.0"
```
<!-- @test:end -->

Install vLLM from the prebuilt ROCm wheel:

<!-- @test:id=vLLM-install timeout=600 hidden=True setup=activate-venv -->
```bash
python -m pip install \
  --extra-index-url https://rocm.frameworks.amd.com/whl/gfx1151/ \
  "vllm==0.16.1.dev10+g11515110f.d20260323.rocm712"
```
<!-- @test:end -->

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

<!-- @test:id=python-env-check-linux timeout=30 hidden=True setup=activate-venv -->
```bash
set -euo pipefail
python3 --version
which python3
```
<!-- @test:end --> 

<!-- @test:id=set-env-var-and-check-install timeout=600 hidden=True setup=activate-venv -->
```bash
export PYTHONPATH=.venv/lib/python3.12/site-packages/_rocm_sdk_core/share/amd_smi
export FLASH_ATTENTION_TRITON_AMD_ENABLE=TRUE
echo "=== vLLM ===" && python -c "import vllm; print('vLLM version:', vllm.__version__)"
echo "=== PyTorch ===" && python -c "import torch; print('PyTorch:', torch.__version__); print('HIP available:', torch.cuda.is_available()); print('HIP built:', torch.backends.hip.is_built() if hasattr(torch.backends, 'hip') else 'N/A')"
echo "=== flash-attn ===" && python -c "import flash_attn; print('flash-attn:', flash_attn.__version__)"
```
<!-- @test:end -->

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
./curl_script.sh
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

Since vLLM exposes an OpenAI-compatible API, you can use the `openai` Python package to interact with it. Activate the `.venv` virtual environment created earlier (if not already active) and install `openai` into it:

```bash
source .venv/bin/activate
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
python chat_with_model.py
```

<!-- @test:id=vllm-server-smoke-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

source .venv/bin/activate

python -m pip install openai

export PYTHONPATH="$PWD/.venv/lib/python3.12/site-packages/_rocm_sdk_core/share/amd_smi"
export FLASH_ATTENTION_TRITON_AMD_ENABLE=TRUE

server_pid=""

cleanup() {
  if [ -n "${server_pid:-}" ] && kill -0 "$server_pid" 2>/dev/null; then
    kill "$server_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$server_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

vllm serve Qwen/Qwen3-1.7B \
  --host 127.0.0.1 \
  --port 8000 \
  --max-model-len 2048 \
  --gpu-memory-utilization 0.7 \
  >/tmp/vllm-test.log 2>&1 &

server_pid=$!

ready=false
for i in $(seq 1 300); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:8000/health || true)"
  if [ "$code" = "200" ]; then
    ready=true
    break
  fi
  sleep 2
done

if [ "$ready" != "true" ]; then
  echo "FAIL: vLLM server did not become ready on http://127.0.0.1:8000/health"
  echo "Last 200 lines of vLLM log:"
  tail -n 200 /tmp/vllm-test.log || true
  exit 1
fi

echo "PASS: vLLM server is responding on /health"

models_json="$(curl -s --max-time 10 http://127.0.0.1:8000/v1/models || true)"

if [ -z "$models_json" ]; then
  echo "FAIL: Empty response from /v1/models"
  exit 1
fi

export MODELS_JSON="$models_json"
python - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["MODELS_JSON"])
model_ids = [item.get("id") for item in data.get("data", [])]

print("Available models:", model_ids)

if "Qwen/Qwen3-1.7B" not in model_ids:
    print("FAIL: Qwen/Qwen3-1.7B was not listed by /v1/models")
    sys.exit(1)

print("PASS: Qwen/Qwen3-1.7B is listed by /v1/models")
PY

direct_response="$(curl -s -X POST --max-time 300 http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3-1.7B",
    "messages": [
      {
        "role": "user",
        "content": "Reply with exactly: OK"
      }
    ],
    "temperature": 0,
    "max_tokens": 32
  }')"

export DIRECT_RESPONSE="$direct_response"
python - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["DIRECT_RESPONSE"])
content = data["choices"][0]["message"]["content"]

print("Direct curl response:", content)

if "OK" not in content:
    print(f"FAIL: Expected direct curl response to contain OK, got: {content!r}")
    sys.exit(1)

print("PASS: Direct curl chat completion worked")
PY

script_response="$(bash curl_script.sh \
  --model Qwen/Qwen3-1.7B \
  --prompt "Reply with exactly: OK" \
  --temperature 0 \
  --max-tokens 32)"

export SCRIPT_RESPONSE="$script_response"
python - <<'PY'
import json
import os
import sys

raw = os.environ["SCRIPT_RESPONSE"]

try:
    data = json.loads(raw)
except json.JSONDecodeError:
    print("FAIL: curl_script.sh did not return valid JSON")
    print(raw)
    sys.exit(1)

content = data["choices"][0]["message"]["content"]

print("curl_script.sh response:", content)

if "OK" not in content:
    print(f"FAIL: Expected curl_script.sh response to contain OK, got: {content!r}")
    sys.exit(1)

print("PASS: curl_script.sh chat completion worked")
PY

python - <<'PY'
from openai import OpenAI
import sys

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY",
)

response = client.chat.completions.create(
    model="Qwen/Qwen3-1.7B",
    messages=[
        {"role": "user", "content": "Reply with exactly: OK"},
    ],
    temperature=0,
    max_tokens=32,
)

content = response.choices[0].message.content or ""
print("OpenAI Python API response:", content)

if "OK" not in content:
    print(f"FAIL: Expected OpenAI Python API response to contain OK, got: {content!r}")
    sys.exit(1)

print("PASS: OpenAI Python API chat completion worked")
PY
```
<!-- @test:end -->

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
