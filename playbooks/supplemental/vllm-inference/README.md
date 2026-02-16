
> **🚧 Work in Progress:** This playbook is still under active development. A follow-up PR will migrate from Docker to vLLM wheels.

# High-Performance LLM Inference with vLLM

## Overview

vLLM is a high-performance inference engine designed for large language models (LLMs). It provides optimized serving with PagedAttention for efficient memory management, continuous batching for higher throughput, and an OpenAI-compatible API for seamless integration. This makes vLLM ideal for production deployments where speed and resource efficiency are critical.

This playbook teaches you how to serve LLMs using vLLM on your STX Halo™ GPU and interact with models through a modern web interface.

## In This Playbook, You Will Learn

- How to set up and start a vLLM server with ROCm support
- How to download and configure LLM models (using Qwen3-1.7B as an example)
- How to interact with models via OpenAI-compatible API endpoints
- How to use the Gradio web interface for interactive chat with streaming responses
- How to configure server parameters for different use cases

## Key Features

✨ **Real-time Streaming** - Token-by-token response generation with low latency  
🎨 **Modern Web UI** - Beautiful Gradio interface for interactive chat  
 **OpenAI-Compatible API** - Drop-in replacement for OpenAI endpoints  
🚀 **High Performance** - Optimized vLLM engine with GPU acceleration  
⚙️ **Flexible Configuration** - Customizable parameters for different use cases

## Files

The following files are under `assets` directory:

- `curl_script.sh` - Test the server with curl
- `run_gradio_client.sh` - Launch the Gradio client
- `model_chat_ui.py` - Interactive web UI with streaming support
- `requirements_gradio.txt` - Python dependencies for Gradio

## Installing vLLM

vLLM can be installed in several ways depending on your environment and preferences:

- **Docker (Recommended)** - Use prebuilt container images with ROCm support for AMD GPUs
- **PyPI Wheel** - Install from Python Package Index using pip
- **Build from Source** - Compile vLLM locally with custom configurations

For this playbook, we'll use the **prebuilt Docker image** which includes vLLM with ROCm support, making it the easiest way to get started on AMD GPUs.

## Preparation

### Pull the Docker Image

First, pull the ROCm vLLM Docker image:

```bash
docker pull vllm/vllm-openai-rocm:v0.14.0
```

This Docker image contains vLLM with ROCm support for AMD GPUs. 

**Start a container:**

```bash
docker run -it --network=host --device=/dev/kfd --device=/dev/dri --group-add video --ipc=host \
  --cap-add=SYS_PTRACE --security-opt seccomp=unconfined --shm-size 8G \
  -v /data:/data \
  --entrypoint /bin/bash \
  vllm/vllm-openai-rocm:v0.14.0
```

**Key options explained:**
- `--entrypoint /bin/bash` - Overrides the default container entrypoint to give you a bash shell for interactive work
- `-v /data:/data` - Mounts your host's `/data` directory to the container's `/data` directory. This allows you to:
  - Store model weights on the host filesystem
  - Access models without re-downloading them each time you start a new container
  - Share models across multiple containers
  - You can change this to any directory, e.g., `-v $HOME/models:/data` to use your home directory
- `--device=/dev/kfd --device=/dev/dri` - Grants container access to AMD GPU devices
- `--network=host` - Uses host networking for easy access to the vLLM server
- `--shm-size 8G` - Allocates shared memory for efficient tensor operations 

### Download the Model

Before starting the vLLM server, you need to download your model from Hugging Face to local directory for easier future access without re-downloading it. 

Let's use the Qwen3-1.7B model for example:

```bash
# Install huggingface-cli if not already installed
pip install -U huggingface_hub

# Download the model to /data/Qwen3_1_7B
huggingface-cli download Qwen/Qwen3-1.7B --local-dir /data/Qwen3_1_7B
```

**Note**: The download may take some time depending on your internet connection. The model is approximately 3.4GB.

**Alternative with custom cache directory:**

```bash
# Download with specific cache location
huggingface-cli download Qwen/Qwen3-1.7B --local-dir /data/Qwen3_1_7B --local-dir-use-symlinks False
```

**Verify the download:**

```bash
ls -lh /data/Qwen3_1_7B
```

You should see model files including `config.json`, `model.safetensors`, `tokenizer.json`, etc.


## Quick Start

### 1. Start the vLLM Server

Inside the Docker container, start the vLLM server:

```bash
vllm serve /data/Qwen3_1_7B
```

The server will start on `http://localhost:8000` with the Qwen3-1.7B model.

**Common server options:**

```bash
# Allow external connections and customize settings
vllm serve /data/Qwen3_1_7B \
  --host 0.0.0.0 \
  --port 8000 \
  --gpu-memory-utilization 0.9 \
  --max-model-len 4096
```

**Alternative: Run server directly with docker run (without entering container):**

```bash
docker run --rm \
  --network=host \
  --group-add=video \
  --cap-add=SYS_PTRACE \
  --security-opt seccomp=unconfined \
  --device /dev/kfd \
  --device /dev/dri \
  --ipc=host \
  --shm-size 8G \
  -v /data:/data \
  vllm/vllm-openai-rocm:v0.14.0 \
  --model /data/Qwen3_1_7B
```


### 2. Test the server with curl

You can test the server using the curl script inside the container:

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

**Features:**
- 🔄 **Real-time streaming** - Responses appear token-by-token as they're generated
- 💬 **Chat history** - Persistent conversation context
- ⚙️ **Adjustable parameters** - Temperature, max tokens, system prompt
- 🎨 **Modern UI** - Clean, responsive interface built with Gradio
- 🚀 **Low latency** - See responses start immediately

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

## Gradio Web Interface

The Gradio client (`model_chat_ui.py`) provides a modern web interface for interacting with your vLLM server.

### Features

- **Streaming Responses**: Messages appear token-by-token in real-time as the model generates them
- **Chat History**: Full conversation context is maintained throughout the session
- **Configurable Parameters**:
  - System Prompt: Set custom instructions for the model
  - Temperature (0.0-2.0): Control randomness in responses
  - Max Tokens (128-4096): Limit response length
- **Modern UI**: Clean, responsive interface with intuitive controls
- **Error Handling**: Clear error messages for connection issues or timeouts

### Usage

Launch the Gradio interface:

```bash
./run_gradio_client.sh
```

Or run the Python script directly:

```bash
python3 model_chat_ui.py --port 7860 --model /data/Qwen3_1_7B --server http://localhost:8000
```

### Command-Line Options

```bash
Options:
  -p, --port PORT       Port for Gradio UI (default: 7860)
  -m, --model MODEL     Model name (default: /data/Qwen3_1_7B)
  -s, --server URL      vLLM server URL (default: http://localhost:8000)
  -h, --help            Show help message
```

### Examples

```bash
# Run on different port
./run_gradio_client.sh --port 8080

# Connect to remote vLLM server
./run_gradio_client.sh --server http://192.168.1.100:8000

# Use different model
./run_gradio_client.sh --model /data/Qwen3-14B
```

### Streaming Implementation

The Gradio client uses Server-Sent Events (SSE) to stream responses from the vLLM server:

1. Sends request to `/v1/chat/completions` with `"stream": true`
2. Receives incremental token deltas via SSE
3. Updates the UI in real-time as tokens arrive
4. Provides smooth, ChatGPT-like user experience

## API Usage

### Curl Example

```bash
# Default vLLM server URL
URL="http://localhost:8000/v1/chat/completions"

# Send a chat completion request
curl -X POST "$URL" \
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

### Python Examples

**Non-streaming request:**

```python
import requests

url = "http://localhost:8000/v1/chat/completions"
payload = {
    "model": "/data/Qwen3_1_7B",
    "messages": [
        {"role": "user", "content": "Hello, how are you?"}
    ],
    "temperature": 0.7,
    "max_tokens": 2048
}

response = requests.post(url, json=payload)
result = response.json()
print(result["choices"][0]["message"]["content"])
```

**Streaming request:**

```python
import requests
import json

url = "http://localhost:8000/v1/chat/completions"
payload = {
    "model": "/data/Qwen3_1_7B",
    "messages": [
        {"role": "user", "content": "Tell me a story"}
    ],
    "temperature": 0.7,
    "max_tokens": 2048,
    "stream": True
}

response = requests.post(url, json=payload, stream=True)

# Process streaming response
for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            data_str = line[6:]  # Remove 'data: ' prefix
            
            if data_str.strip() == '[DONE]':
                break
            
            try:
                data = json.loads(data_str)
                if 'choices' in data and len(data['choices']) > 0:
                    delta = data['choices'][0].get('delta', {})
                    content = delta.get('content', '')
                    if content:
                        print(content, end='', flush=True)
            except json.JSONDecodeError:
                continue

print()  # New line at end
```

## Configuration

### Model Path

To use a different model, simply replace the model path in the `vllm serve` command:

```bash
vllm serve /path/to/your/model
```

### Server Parameters

Common vLLM server parameters:

```bash
vllm serve /data/Qwen3_1_7B \
  --host 0.0.0.0              # Allow external connections
  --port 8000                 # Server port (default: 8000)
  --tensor-parallel-size 2    # Use multiple GPUs
  --gpu-memory-utilization 0.9  # GPU memory usage (0.0-1.0)
  --max-model-len 4096        # Maximum sequence length
  --trust-remote-code         # Allow custom model code
```

### Request Parameters

- `temperature` (0.0-2.0) - Controls randomness. Higher = more random
- `max_tokens` - Maximum tokens to generate
- `top_p` (0.0-1.0) - Nucleus sampling parameter
- `frequency_penalty` - Reduce repetition
- `presence_penalty` - Encourage topic diversity

## Troubleshooting

### Server not starting

Check if the model path exists:
```bash
ls -l /data/Qwen3_1_7B
```

If the model directory doesn't exist or is empty, download it first:
```bash
huggingface-cli download Qwen/Qwen3-1.7B --local-dir /data/Qwen3_1_7B
```

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

### For Model Download
```bash
pip install -U huggingface_hub
```

### For vLLM Server
- Python 3.8+
- vLLM installed
- GPU with sufficient memory
- Model downloaded to `/data/Qwen3_1_7B` (see Preparation section)

### For Gradio Client
```bash
pip install -r requirements_gradio.txt
```

## Summary

In this playbook, you learned how to:

- Set up and run vLLM with ROCm support using Docker for high-performance LLM inference on AMD GPUs
- Download and configure language models from Hugging Face for use with vLLM
- Start and configure a vLLM server with OpenAI-compatible API endpoints on port 8000
- Test the server using curl commands and API requests
- Launch and use the Gradio web interface (port 7860) for interactive chat with real-time streaming responses
- Configure server parameters like GPU memory utilization, model length limits, and multi-GPU support
- Make API calls to the vLLM server using both streaming and non-streaming requests
- Troubleshoot common issues with server startup, memory, and client connections

You now have a fully functional vLLM deployment for serving large language models with optimized performance on your STX Halo™ GPU.

## Additional Resources

- **[vLLM Official Documentation](https://docs.vllm.ai/)** - Comprehensive guides and API references
- **[vLLM GitHub Repository](https://github.com/vllm-project/vllm)** - Source code, issues, and community discussions
