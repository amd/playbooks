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

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) 是 DeepSeek V4 系列中专注于效率的变体——一个拥有 2840 亿参数的混合专家（Mixture of Experts）模型，激活参数为 130 亿。根据[DeepSeek 的技术报告](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash)，该模型在 SWE-bench Verified 上得分 79%，在 LiveCodeBench 上得分 91.6%。

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) 是专门为该模型架构构建的专用推理引擎。与通用运行时不同，ds4 直接针对 DeepSeek V4 系列，为 AMD ROCm™ 软件提供架构特定的内核优化。目前，它是 Strix Halo 上性能最佳的 DeepSeek V4 Flash 实现之一。

本教程展示了如何使用 `ds4-cockpit`（一款终端 UI）来设置 ds4、下载模型权重，并在 AMD Ryzen™ AI Halo 开发者平台上本地启动 DeepSeek V4 Flash 服务。

## 您将学到什么

- 如何安装并启动 `ds4-cockpit` 终端 UI
- 如何创建 ds4 ROCm 工具箱容器
- 为单个 Halo 节点下载推荐的量化版本
- 启动 ds4 推理服务器并公开与 OpenAI 兼容的端点
- 将 Web UI 或编码代理连接到本地服务器

## 设置内存配置

<!-- @require:memory-config -->

## 安装软件先决条件

> **本配置的系统要求（单节点 IQ2_XXS，126k 上下文）：**
> - 一台**至少配备 128 GB 统一内存**的 Strix Halo 系统。
> - **BIOS 专用 VRAM（UMA 帧缓冲区）设置为最低值**，以便共享内存池尽可能大。
> - GPU **共享内存池至少设置为 110 GB**：运行 `amd-ttm --set 110`（参见上面的内存配置步骤）并重启。如果模型在 126k 上下文下加载时数值过低，可能会导致内存不足。如果您的系统可用内存较少，请改为在服务器模式中降低**上下文（Context）**值。
>
> **注意：** 尝试将**GPU 共享内存池**设置为 **110 GB** 作为起始值。如果遇到内存不足错误，请增加共享内存池或降低上下文大小。

ds4-cockpit 使用容器工具箱来运行 ds4 引擎。请安装 `podman`、`distrobox` 和 `pipx`：

```bash
sudo apt update
sudo apt install -y podman distrobox pipx
```

<!-- @test:id=ds4-prereqs-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
podman --version
distrobox version 2>/dev/null || distrobox --version
pipx --version
echo "OK: podman, distrobox, and pipx are installed"
```
<!-- @test:end -->

## 可用的量化版本

ds4 的作者提供了多个采用 GGUF 格式的 DeepSeek V4 Flash 量化版本。以下所有模型都使用了重要性矩阵（imatrix）校准，该方法可为模型中对编码和推理任务最重要的部分保留更高的精度。

| 量化版本 | 大小 | 说明 |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80.8 GB | 推荐用于单个 128 GB 节点 |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | 第 37–42 层保持 Q4 精度以获得更好的准确性。可容纳于 128 GB，但为上下文留出的空间较少 |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | 更高质量。需要通过多节点集群使用两个 Halo 节点 |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3.6 GB | 用于推测解码的可选附加组件，以提升生成速度 |

**IQ2_XXS imatrix** 模型是一个不错的起点。它可以轻松容纳在单个节点中，并为合理的上下文窗口留出了足够的内存。

## 安装 ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) 是一款轻量级终端 UI，可让您轻松在 Strix Halo 上运行 ds4。它负责创建工具箱容器、下载模型权重以及启动服务器。使用 `pipx` 安装：

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

启动 cockpit：
```bash
ds4-cockpit
```

<!-- @test:id=ds4-cockpit-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
# Verify the pipx-installed cockpit entry point is on PATH (do NOT launch the TUI).
command -v ds4-cockpit
echo "OK: ds4-cockpit is installed and on PATH"
```
<!-- @test:end -->

## 创建工具箱

在**交互式工具箱（Interactive Toolboxes）**选项卡中，选择最新的可用/稳定工具箱（例如 `ds4-rocm-7.2.4`），然后点击**创建/更新（Create/Update）**。这将拉取容器镜像并创建工具箱环境。


<p align="center">
  <img src="assets/ds4-cockpit-toolboxes.png" alt="Selecting the ds4 toolbox in ds4-cockpit" width="800"/>
</p>

<!-- @test:id=ds4-toolbox-image-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# The toolbox version changes over time, so match the image family, not a fixed tag.
if ! podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ds4-cockpit (Interactive Toolboxes tab) first."
  exit 1
fi
echo "OK: ds4 toolbox container image is present"
```
<!-- @test:end -->

## 下载模型

前往**模型管理器（Model Manager）**选项卡。从下拉菜单中选择 **IQ2_XXS imatrix (~80.8 GB)**，然后点击**下载（Download）**。模型文件默认将保存到 `~/ds4`（您可以更改存储路径）。

> **注意：** IQ2_XXS 模型大小约为 80 GB，因此根据您的网络连接情况，下载可能需要一段时间。下载完成后即可继续操作。

<p align="center">
  <img src="assets/ds4-cockpit-model-manager.png" alt="Selecting and downloading the IQ2_XXS model" width="800"/>
</p>

<!-- @test:id=ds4-model-downloaded-linux timeout=60 hidden=True -->
```bash
set -euo pipefail

# ds4-cockpit saves model weights to ~/ds4 by default
model_dir="$HOME/ds4"

if [ ! -d "$model_dir" ]; then
  echo "Model directory $model_dir does not exist. Download the model in ds4-cockpit (Model Manager tab) first."
  exit 1
fi

if ! find "$model_dir" -maxdepth 2 -iname '*.gguf' | grep -q .; then
  echo "No .gguf model files found under $model_dir. Download the IQ2_XXS imatrix model in ds4-cockpit first."
  exit 1
fi

# Prefer to confirm the recommended IQ2_XXS imatrix quantization is present.
if find "$model_dir" -maxdepth 2 -iname '*IQ2*imatrix*.gguf' | grep -q .; then
  echo "OK: IQ2_XXS imatrix model is downloaded"
else
  echo "OK: a GGUF model is present (recommended IQ2_XXS imatrix file not detected by name)"
fi
```
<!-- @test:end -->

## 启动服务器

前往**服务器模式（Server Mode）**选项卡。选择已下载的模型和工具箱，然后配置上下文大小、主机和端口。准备就绪后，点击**启动 ds4-server（Start ds4-server）**。

> **提示** `126000` 的上下文大小是一个合理的起始值，应该能够容纳在单个节点中——如果您有多余的内存，可以将其设置得更高；如果遇到内存不足错误，则可以降低该值。本指南中的端口（`8000`）是随意选定的；您可以选择任何空闲端口。

> **KV 磁盘缓存（可选）。** 开启 **KV Disk Cache** 会将 KV 缓存卸载到磁盘（位于**主机缓存目录（Host Cache Dir）**，默认为 `~/.cache/ds4-kv`），这样重复的系统提示词就可以从 SSD 中恢复，而无需重新计算。这是针对具有长而重复提示词的编码代理工作流的一项性能优化，**并非**运行服务器所必需的。

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

服务器将启动并监听 8000 端口，在 `http://localhost:8000/v1` 公开一个与 OpenAI 兼容的 API 端点。

**快速测试：**
```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "deepseek-v4-flash",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": false
  }'
```

<!-- @test:id=ds4-server-chat-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

# This runner is shared with other playbooks, and ds4 at a 126k context consumes almost the entire GPU memory pool.
# So rather than keeping ds4 resident, CI starts the server, verifies a chat completion, then stops it again.
# This frees the memory for the next job.
# ds4 has no separate "unload"; stopping the server process is what releases the ~80 GB model.

CONTAINER="ds4-ci-server"
MODEL_DIR="$HOME/ds4"

# Locate the downloaded model (prefer the recommended IQ2_XXS imatrix file).
model_file="$(find "$MODEL_DIR" -maxdepth 2 -iname '*IQ2*imatrix*.gguf' 2>/dev/null | head -1)"
if [ -z "$model_file" ]; then
  model_file="$(find "$MODEL_DIR" -maxdepth 2 -iname '*.gguf' 2>/dev/null | head -1)"
fi
if [ -z "$model_file" ]; then
  echo "No .gguf model found under $MODEL_DIR. Download it in ds4-cockpit first."
  exit 1
fi
model_name="$(basename "$model_file")"

# Pick the toolbox image (version-agnostic).
image="$(podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox' | head -1)"
if [ -z "$image" ]; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ds4-cockpit first."
  exit 1
fi

# Always stop/remove the server on exit so it never holds GPU memory afterwards.
cleanup() {
  podman stop -t 10 "$CONTAINER" >/dev/null 2>&1 || true
  podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# Remove any stale instance, then start ds4-server detached (same flags ds4-cockpit uses, with -d instead of -it).
podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
podman run -d --name "$CONTAINER" \
  --device /dev/dri --device /dev/kfd \
  --group-add keep-groups \
  --security-opt seccomp=unconfined \
  --ipc=host \
  --cap-add=SYS_PTRACE \
  --security-opt label=disable \
  --userns=keep-id \
  -p 127.0.0.1:8000:8000 \
  -v "$MODEL_DIR":/models:ro \
  "$image" \
  ds4-server -m "/models/$model_name" --ctx 126000 --host 0.0.0.0 --port 8000

# Wait for readiness; the ~80 GB model can take a few minutes to load.
up=false
for i in $(seq 1 240); do
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 http://127.0.0.1:8000/v1/models || true)"
  if [ -n "$code" ] && [ "$code" != "000" ]; then
    up=true
    break
  fi
  if ! podman inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null | grep -q true; then
    echo "ds4-server container exited during startup:"
    podman logs "$CONTAINER" 2>&1 | tail -40 || true
    exit 1
  fi
  sleep 2
done

if [ "$up" != "true" ]; then
  echo "ds4 server did not become ready on http://127.0.0.1:8000"
  podman logs "$CONTAINER" 2>&1 | tail -40 || true
  exit 1
fi
echo "OK: ds4 server is responding on :8000"

body='{
  "model": "deepseek-v4-flash",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32,
  "stream": false
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from ds4 /v1/chat/completions"
  exit 1
fi

export DS4_OUT="$out"
python3 - <<'PY'
import json, os, sys

data = json.loads(os.environ["DS4_OUT"])
choices = data.get("choices")
if not choices:
    print("Response has no 'choices':")
    print(json.dumps(data, indent=2)[:2000])
    sys.exit(1)

message = choices[0].get("message", {}) or {}
content = message.get("content") or message.get("reasoning_content")
if not content:
    print("Response choice has empty content:")
    print(json.dumps(data, indent=2)[:2000])
    sys.exit(1)

print("OK: ds4 chat/completions returned content")
PY

echo "OK: ds4 server test complete; server stopped and GPU memory released"
```
<!-- @test:end -->

## 连接 Web UI

您可以连接任何支持 OpenAI API 格式的聊天界面。例如，使用 HuggingFace ChatUI：

```bash
docker run -p 3000:3000 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

在浏览器中打开 `http://localhost:3000` 即可开始聊天。
## 连接编码代理

ds4 服务器同时暴露了兼容 OpenAI 和 Anthropic 的端点，因此大多数编码代理都可以直接连接到它。例如，要将其添加到 `pi` 编码代理中，请将以下代码块添加到 `~/.pi/agent/models.json`：

```json
"ds4": {
  "name": "ds4.c local",
  "baseUrl": "http://localhost:8000/v1",
  "api": "openai-completions",
  "apiKey": "dsv4-local",
  "compat": {
    "supportsStore": false,
    "supportsDeveloperRole": false,
    "supportsReasoningEffort": true,
    "supportsUsageInStreaming": true,
    "maxTokensField": "max_tokens",
    "supportsStrictMode": false,
    "thinkingFormat": "deepseek",
    "requiresReasoningContentOnAssistantMessages": true
  },
  "models": [
    {
      "id": "deepseek-v4-flash",
      "name": "DeepSeek V4 Flash (ds4.c local)",
      "reasoning": true,
      "thinkingLevelMap": {
        "off": null,
        "minimal": "low",
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "xhigh"
      },
      "input": ["text"],
      "contextWindow": 131072,
      "maxTokens": 65536,
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 }
    }
  ]
}
```

> **提示**：如果您的编码代理或 Web UI 运行在与 Halo 平台不同的机器上，您需要通过 SSH 转发 8000 端口：
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```

## 后续步骤

- **多节点集群**：如果您拥有两台 Halo 设备，ds4 支持通过流水线并行将 Q4 模型（约 153 GB）分布到两台机器上。有关设置说明，请参阅 [ds4-toolbox 文档](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism)。
- **推测解码（MTP）**：下载 MTP 权重（约 3.6 GB），并向服务器传递 `--mtp` 参数以获得更快的生成速度。
- **KV 缓存磁盘卸载**：对于编码代理工作流，启用 `--kv-disk-dir`，这样重复的系统提示词可以从 SSD 中恢复，而无需每次都重新计算。

更多信息，请参阅 [ds4 仓库](https://github.com/antirez/ds4) 和 [ds4-cockpit 工具箱](https://github.com/kyuz0/strix-halo-ds4-toolbox)。