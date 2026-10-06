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

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) 是 DeepSeek V4 系列中专注于效率的变体——这是一个拥有 2840 亿参数的混合专家（Mixture of Experts）模型，其中激活参数为 130 亿。根据 [DeepSeek 的技术报告](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash)，该模型在 SWE-bench Verified 上的得分为 79%，在 LiveCodeBench 上的得分为 91.6%。

[ds4（Dwarf Star 4）](https://github.com/antirez/ds4) 是专为该模型架构打造的专用推理引擎。与通用运行时不同，ds4 直接面向 DeepSeek V4 系列，并针对 AMD ROCm™ 软件进行了特定架构的内核优化。目前，它是 Strix Halo 上 DeepSeek V4 Flash 性能最佳的实现之一。

本教程将展示如何使用 `ai-toolbox-cockpit`（一个终端 UI）来设置 ds4、下载模型权重，并在 AMD Ryzen™ AI Halo Developer Platform 上启动本地提供 DeepSeek V4 Flash 服务。

## 你将学到什么

- 如何安装并启动 `ai-toolbox-cockpit` 终端 UI
- 如何创建 ds4 ROCm toolbox 容器
- 为单个 Halo 节点下载推荐的量化版本
- 启动 ds4 推理服务器并暴露一个兼容 OpenAI 的接口端点
- 将 Web UI 或编码代理连接到本地服务器

## 设置内存配置

<!-- @require:memory-config -->

## 安装软件前置条件

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @prereq:distrobox,ds4-cockpit,ds4-toolbox-image -->

> **此配置的系统要求（单节点 IQ2_XXS，126k 上下文）：**
> - 具有 **至少 128 GB 统一内存** 的 Strix Halo 系统。
> - **将 BIOS 专用显存（UMA 帧缓冲）设置为最小值**，以便共享内存池可以尽可能大。
> - **GPU 共享内存池至少设置为 110 GB**：运行 `amd-ttm --set 110`（参见上面的内存配置步骤）并重启。如果数值过低，在以 126k 上下文加载模型时可能会出现内存不足的问题。如果你的系统可用内存较少，请改为降低服务器模式（Server Mode）中的 **Context** 值。
>
> **注意：** 可以先尝试将 **GPU 共享内存池** 设置为 **110 GB** 作为起始值。如果遇到内存不足错误，请提高共享内存池大小或降低上下文大小。

ai-toolbox-cockpit 使用容器 toolbox 来运行 ds4 引擎。请安装 `podman`、`distrobox` 和 `pipx`：

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

ds4 的作者提供了多种 GGUF 格式的 DeepSeek V4 Flash 量化版本。下面所有模型均使用了重要性矩阵（imatrix）校准，可为模型中对编码和推理任务最重要的部分保留更高精度。

| 量化版本 | 大小 | 说明 |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | 约 80.8 GB | 推荐用于单个 128 GB 节点 |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | 约 97 GB | 保持第 37–42 层为 Q4 精度以获得更高准确度。可在 128 GB 内容纳，但留给上下文的空间更少 |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | 约 153 GB | 质量更高。需要通过多节点集群使用两个 Halo 节点 |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | 约 3.6 GB | 用于推测解码（speculative decoding）的可选附加组件，可提升生成速度 |

**IQ2_XXS imatrix** 模型是一个不错的起点。它可以轻松容纳在单个节点上，并为上下文窗口留下足够的内存空间。

## 安装 ai-toolbox-cockpit

[ai-toolbox-cockpit](https://github.com/kyuz0/ai-toolbox-cockpit) 是一个轻量级终端 UI，可以轻松安装各种 AI 后端。我们将用它来处理创建 ds4 容器、下载模型权重和启动服务器等任务。使用 `pipx` 安装它：

<!-- @test:id=ds4-cockpit-install-linux timeout=300 -->
```bash
pipx install git+https://github.com/kyuz0/ai-toolbox-cockpit.git
```
<!-- @test:end -->

启动 cockpit：
```bash
ai-toolbox-cockpit
```

<!-- @test:id=ds4-cockpit-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
# Verify the pipx-installed cockpit entry point is on PATH (do NOT launch the TUI).
command -v ai-toolbox-cockpit
echo "OK: ai-toolbox-cockpit is installed and on PATH"
```
<!-- @test:end -->

## 步骤 1：创建 Toolbox

在 **Interactive Toolboxes** 选项卡中，为 ds4 选择最新可用/稳定的 toolbox（例如 `ds4-rocm-10.0`），然后点击 **Create/Update**。这会拉取容器镜像并创建 toolbox 环境。


<p align="center">
  <img src="assets/ai-toolbox-cockpit-toolboxes.png" alt="Selecting the ds4 toolbox in ai-toolbox-cockpit" width="800"/>
</p>

<!-- @test:id=ds4-toolbox-image-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# The toolbox version changes over time, so match the image family, not a fixed tag.
if ! podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ai-toolbox-cockpit (Interactive Toolboxes tab) first."
  exit 1
fi
echo "OK: ds4 toolbox container image is present"
```
<!-- @test:end -->

## 步骤 2：下载模型

前往 **Models** 选项卡。首先选择后端（ds4）。然后从下拉菜单中选择 **IQ2_XXS imatrix（约 80.8 GB）**，并点击 **Download**。模型文件将默认保存到 `~/ds4`（你也可以更改存储路径）。

> **注意：** IQ2_XXS 模型大约为 80 GB，因此下载时间取决于你的网络连接，可能需要较长时间。下载完成后即可继续。

<p align="center">
  <img src="assets/ai-toolbox-cockpit-models.png" alt="Selecting and downloading the IQ2_XXS model" width="800"/>
</p>

<!-- @test:id=ds4-model-downloaded-linux timeout=60 hidden=True -->
```bash
set -euo pipefail

# ai-toolbox-cockpit saves model weights to ~/ds4 by default
model_dir="$HOME/ds4"

if [ ! -d "$model_dir" ]; then
  echo "Model directory $model_dir does not exist. Download the model in ai-toolbox-cockpit (Model Manager tab) first."
  exit 1
fi

if ! find "$model_dir" -maxdepth 2 -iname '*.gguf' | grep -q .; then
  echo "No .gguf model files found under $model_dir. Download the IQ2_XXS imatrix model in ai-toolbox-cockpit first."
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

## 步骤 3：启动服务器

前往 **Server Mode** 选项卡。选择已下载的模型和 toolbox，然后配置上下文大小、主机和端口。准备就绪后，点击 **Start ds4-server**。

> **提示** `126000` 的上下文大小是一个合理的起始值，应该可以在单个节点上容纳——如果你有多余的内存，可以将其设置得更高；如果遇到内存不足错误，可以将其调低。本指南中使用的端口（`8000`）是任意的；你可以选择任何空闲端口。

> **KV 磁盘缓存（可选）。** 启用 **KV Disk Cache** 会将 KV 缓存卸载到磁盘上（位于 **Host Cache Dir**，默认为 `~/.cache/ds4-kv`），这样重复的系统提示（system prompts）会从 SSD 恢复，而不需要重新计算。这是针对具有长且重复提示的编码代理工作流的一种性能优化，**并非**运行服务器所必需。

<p align="center">
  <img src="assets/ai-toolbox-cockpit-server.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

服务器将启动并监听 8000 端口，在 `http://localhost:8000/v1` 暴露一个兼容 OpenAI 的 API 端点。

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
  echo "No .gguf model found under $MODEL_DIR. Download it in ai-toolbox-cockpit first."
  exit 1
fi
model_name="$(basename "$model_file")"

# Pick the toolbox image (version-agnostic).
image="$(podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox' | head -1)"
if [ -z "$image" ]; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ai-toolbox-cockpit first."
  exit 1
fi

# Always stop/remove the server on exit so it never holds GPU memory afterwards.
cleanup() {
  podman stop -t 10 "$CONTAINER" >/dev/null 2>&1 || true
  podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# keep-id maps the calling user into the container. Root does not need it, and as root it cannot
# be combined with --ipc=host (crun fails to mount /dev/mqueue), so root keeps the host user namespace.
userns=keep-id
if [ "$(id -u)" -eq 0 ]; then
  userns=host
fi

# Remove any stale instance, then start ds4-server detached (same flags ai-toolbox-cockpit uses, with -d instead of -it).
podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
podman run -d --name "$CONTAINER" \
  --device /dev/dri --device /dev/kfd \
  --group-add keep-groups \
  --security-opt seccomp=unconfined \
  --ipc=host \
  --cap-add=SYS_PTRACE \
  --security-opt label=disable \
  --userns="$userns" \
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
docker run --network=host \
  -e PORT=3000 \
  -e OPENAI_BASE_URL=http://localhost:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

在浏览器中打开 `http://localhost:3000` 即可开始聊天。

> **注意：** `--network=host` 会将 Web UI 置于主机网络中，使其能够直接通过 `localhost` 访问 ds4 服务器。这样可以让 ds4 服务器保持绑定在回环接口上（无需在其他接口上公开）。

> **提示：** Web UI 端口（此处为 `3000`，通过 `PORT` 设置）是任意的——如果 `3000` 已被占用，可以选择任何空闲端口，并在浏览器中打开该端口。请确保 `OPENAI_BASE_URL` 中的端口与 ds4 服务器运行的端口一致。

## 连接编码代理

ds4 服务器同时提供兼容 OpenAI 和 Anthropic 的端点，因此大多数编码代理都可以直接连接到它。例如，要将其添加到 `pi` 编码代理，请在 `~/.pi/agent/models.json` 中添加以下内容：

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

> **提示**：如果您的编码代理或 Web UI 运行在与 Halo 平台不同的机器上，您需要通过 SSH 转发服务器端口（此处为 `8000`）：
> ```bash
> ssh -L 8000:localhost:8000 <halo-host-ip>
> ```

## 后续步骤

- **多节点集群**：如果您拥有两台 Halo 设备，ds4 支持通过流水线并行（pipeline parallelism）将 Q4 模型（约 153 GB）分布到两台机器上。有关设置说明，请参阅 [ds4-toolbox 文档](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism)。
- **推测解码（MTP）**：下载 MTP 权重（约 3.6 GB），并向服务器传入 `--mtp` 以获得更快的生成速度。
- **KV 缓存磁盘卸载**：对于编码代理工作流，启用 `--kv-disk-dir`，以便重复的系统提示从 SSD 恢复，而不是每次都重新计算。

更多信息请参阅 [ds4 仓库](https://github.com/antirez/ds4) 和 [ds4-cockpit 工具箱](https://github.com/kyuz0/strix-halo-ds4-toolbox)。