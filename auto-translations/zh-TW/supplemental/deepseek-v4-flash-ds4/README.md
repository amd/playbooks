<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機器翻譯。**本頁面是由英文自動翻譯而成，尚未經過人工審閱。內容可能包含錯誤，且某些指示、命令、下載項目、產品供應情況或其他內容可能因語言或地區而異。如本文件與英文版本之間存在任何不一致或差異，應以該 playbook 之英文原始版本為準。
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## 概觀

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) 是 DeepSeek V4 系列中專注於效率的變體——這是一個擁有 2840 億參數的混合專家（Mixture of Experts）模型，具有 130 億個活躍參數。根據[DeepSeek 的技術報告](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash)，該模型在 SWE-bench Verified 上得分 79%，在 LiveCodeBench 上得分 91.6%。

[ds4（Dwarf Star 4）](https://github.com/antirez/ds4)是專為此模型架構打造的專用推論引擎。它並非通用型執行環境，而是直接針對 DeepSeek V4 系列，提供針對 AMD ROCm™ 軟體優化的架構專屬核心（kernel）。目前它是 Strix Halo 上效能最佳的 DeepSeek V4 Flash 實作之一。

本教學將說明如何使用終端機使用者介面 `ai-toolbox-cockpit` 來設定 ds4、下載模型權重，並在 AMD Ryzen™ AI Halo 開發者平台上於本機啟動 DeepSeek V4 Flash 推論服務。

## 您將學到什麼

- 如何安裝並啟動 `ai-toolbox-cockpit` 終端機使用者介面
- 如何建立 ds4 ROCm 工具箱（toolbox）容器
- 下載適合單一 Halo 節點的建議量化版本
- 啟動 ds4 推論伺服器並對外提供相容 OpenAI 的端點
- 連接 Web UI 或程式碼代理（coding agent）至本機伺服器

## 設定記憶體配置

<!-- @require:memory-config -->

## 安裝軟體先決條件

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @prereq:distrobox,ds4-cockpit,ds4-toolbox-image -->

> **此設定的系統需求（單節點 IQ2_XXS，126k 上下文）：**
> - 具備**至少 128 GB 統一記憶體**的 Strix Halo 系統。
> - **BIOS 專用 VRAM（UMA 畫面緩衝區）設為最小值**，以使共享記憶體池可以盡量放大。
> - GPU **共享記憶體池設定為至少 110 GB**：執行 `amd-ttm --set 110`（請參見上方的記憶體配置步驟）並重新開機。若數值過低，當模型以 126k 上下文載入時可能會發生記憶體不足的情況。若您的系統可用記憶體較少，請改為在伺服器模式（Server Mode）中降低**上下文（Context）**值。
>
> **注意：** 建議先將 **GPU 共享記憶體池**設定為 **110 GB** 作為起始值。若遇到記憶體不足的錯誤，請提高共享記憶體池或降低上下文大小。

ai-toolbox-cockpit 使用容器化工具箱來執行 ds4 引擎。請安裝 `podman`、`distrobox` 和 `pipx`：

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

ds4 的作者提供了多個 GGUF 格式的 DeepSeek V4 Flash 量化版本。以下所有模型均使用重要性矩陣（importance matrix，imatrix）校準，這能為模型中對程式設計與推理任務最重要的部分保留較高的精度。

| 量化版本 | 大小 | 說明 |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | 約 80.8 GB | 建議用於單一 128 GB 節點 |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | 約 97 GB | 將第 37–42 層保持在 Q4 精度以提升準確度。可容納於 128 GB 中，但留給上下文的空間較少 |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | 約 153 GB | 更高品質。需要透過多節點叢集使用兩個 Halo 節點 |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | 約 3.6 GB | 可選附加項目，用於投機解碼（speculative decoding）以提升生成速度 |

**IQ2_XXS imatrix** 模型是不錯的起點。它可以輕鬆容納於單一節點，並為上下文視窗留有合理的記憶體空間。

## 安裝 ai-toolbox-cockpit

[ai-toolbox-cockpit](https://github.com/kyuz0/ai-toolbox-cockpit) 是一個輕量級終端機使用者介面，可讓安裝各種 AI 後端變得簡單。我們將使用它來處理建立 ds4 容器、下載模型權重，以及啟動伺服器等工作。請使用 `pipx` 安裝：

<!-- @test:id=ds4-cockpit-install-linux timeout=300 -->
```bash
pipx install git+https://github.com/kyuz0/ai-toolbox-cockpit.git
```
<!-- @test:end -->

啟動 cockpit：
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

## 步驟 1：建立工具箱

在**互動式工具箱（Interactive Toolboxes）**分頁中，選擇 ds4 可用的最新/穩定版工具箱（例如 `ds4-rocm-10.0`），然後點擊**建立/更新（Create/Update）**。此動作會拉取容器映像檔並建立工具箱環境。


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

## 步驟 2：下載模型

前往**模型（Models）**分頁。首先選擇後端（ds4）。接著從下拉選單中選擇 **IQ2_XXS imatrix（約 80.8 GB）**，然後點擊**下載（Download）**。模型檔案預設會儲存至 `~/ds4`（您可以變更儲存路徑）。

> **注意：** IQ2_XXS 模型約為 80 GB，因此下載時間可能依您的網路連線狀況而有所不同。下載完成後即可繼續進行。

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

## 步驟 3：啟動伺服器

前往**伺服器模式（Server Mode）**分頁。選擇已下載的模型與工具箱，然後設定上下文大小、主機與連接埠。準備完成後，點擊**啟動 ds4-server（Start ds4-server）**。

> **提示：** 上下文大小 `126000` 是一個合理的起始值，應該能在單一節點上順利運作——若您有多餘的記憶體，可以設定更高；若遇到記憶體不足的錯誤，則可降低該值。連接埠（本指南中為 `8000`）為任意設定，可選擇任何可用的連接埠。

> **KV 磁碟快取（可選）。** 啟用 **KV 磁碟快取（KV Disk Cache）**會將 KV 快取卸載至磁碟（位於**主機快取目錄（Host Cache Dir）**，預設為 `~/.cache/ds4-kv`），使重複的系統提示（system prompts）可以從 SSD 還原，而無需重新計算。這是針對具有長且重複提示的程式碼代理工作流程的效能優化，並**非**執行伺服器所必需。

<p align="center">
  <img src="assets/ai-toolbox-cockpit-server.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

伺服器將啟動並監聽連接埠 8000，在 `http://localhost:8000/v1` 提供相容 OpenAI 的 API 端點。

**快速測試：**
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
## 連接 Web UI

您可以連接任何支援 OpenAI API 格式的聊天介面。例如，若要使用 HuggingFace ChatUI：

```bash
docker run --network=host \
  -e PORT=3000 \
  -e OPENAI_BASE_URL=http://localhost:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

在瀏覽器中開啟 `http://localhost:3000` 即可開始聊天。

> **注意：** `--network=host` 會將 Web UI 置於主機的網路上，以便它能直接透過 `localhost` 連到 ds4 伺服器。這樣可讓 ds4 伺服器維持綁定在 loopback（不需要暴露在其他介面上）。

> **提示：** Web UI 的連接埠（此處為 `3000`，透過 `PORT` 設定）是任意的——如果 `3000` 已被佔用，可選擇任何可用的連接埠，並改用該連接埠開啟瀏覽器。請確認 `OPENAI_BASE_URL` 中的連接埠與 ds4 伺服器執行所用的連接埠一致。

## 連接編碼代理

ds4 伺服器同時提供與 OpenAI 及 Anthropic 相容的端點，因此大多數編碼代理都能直接連接到它。例如，若要將其加入 `pi` 編碼代理，請在 `~/.pi/agent/models.json` 中加入以下區塊：

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

> **提示**：如果您的編碼代理或 Web UI 執行於與 Halo 平台不同的機器上，您需要透過 SSH 轉發伺服器連接埠（此處為 `8000`）：
> ```bash
> ssh -L 8000:localhost:8000 <halo-host-ip>
> ```

## 後續步驟

- **多節點叢集**：如果您擁有兩台 Halo 裝置，ds4 支援透過管線平行處理（pipeline parallelism）將 Q4 模型（約 153 GB）分散到兩台機器上。請參閱 [ds4-toolbox 文件](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) 以取得設定說明。
- **推測性解碼（MTP）**：下載 MTP 權重（約 3.6 GB），並在伺服器啟動時傳入 `--mtp` 以提升生成速度。
- **KV 快取磁碟卸載**：針對編碼代理工作流程，啟用 `--kv-disk-dir`，讓重複的系統提示詞能從 SSD 還原，而不必每次重新計算。

如需更多資訊，請參閱 [ds4 儲存庫](https://github.com/antirez/ds4) 及 [ds4-cockpit 工具箱](https://github.com/kyuz0/strix-halo-ds4-toolbox)。