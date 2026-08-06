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

## 總覽

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) 是 DeepSeek V4 系列中專注於效率的變體——一個擁有 2840 億參數的 Mixture of Experts 模型，其中有 130 億個活躍參數。根據 [DeepSeek 的技術報告](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash)，該模型在 SWE-bench Verified 上得分 79%，在 LiveCodeBench 上得分 91.6%。

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) 是專為此模型架構打造的專屬推論引擎。它並非通用型執行環境，而是直接針對 DeepSeek V4 系列，透過針對 AMD ROCm™ software 的架構專屬核心優化來運作。它是目前在 Strix Halo 上效能最佳的 DeepSeek V4 Flash 實作之一。

本教學展示如何使用終端機使用者介面 `ds4-cockpit` 來設定 ds4、下載模型權重，並在 AMD Ryzen™ AI Halo Developer Platform 上本機啟動 DeepSeek V4 Flash 服務。

## 您將學到什麼

- 如何安裝並啟動 `ds4-cockpit` 終端機使用者介面
- 如何建立 ds4 ROCm toolbox 容器
- 為單一 Halo 節點下載建議的量化版本
- 啟動 ds4 推論伺服器並公開一個相容 OpenAI 的端點
- 將 Web UI 或程式碼助理連接至本機伺服器

## 設定記憶體配置

<!-- @require:memory-config -->

## 安裝軟體先決條件

> **此設定的系統需求（單一節點 IQ2_XXS，126k 上下文）：**
> - 一台 Strix Halo 系統，**至少具備 128 GB 統一記憶體**。
> - **BIOS 專用 VRAM（UMA frame buffer）設定為最小值**，以便讓共享記憶體池盡可能大。
> - **GPU 共享記憶體池設定為至少 110 GB**：執行 `amd-ttm --set 110`（請參閱上方的記憶體配置步驟）並重新開機。數值過低可能會在模型以 126k 上下文載入時發生記憶體不足的問題。如果您的系統可用記憶體較少，請改為在 Server Mode 中降低 **Context** 數值。
>
> **注意：** 建議先嘗試將 **GPU 共享記憶體池** 設為 **110 GB** 作為起始值。如果遇到記憶體不足的錯誤，請提高共享記憶體池或降低上下文大小。

ds4-cockpit 使用容器化 toolbox 來執行 ds4 引擎。請安裝 `podman`、`distrobox` 與 `pipx`：

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

ds4 作者以 GGUF 格式提供多個 DeepSeek V4 Flash 的量化版本。以下所有模型皆使用重要性矩陣（imatrix）校準，能為模型中對程式編寫與推理任務最重要的部分保留較高的精度。

| 量化版本 | 大小 | 說明 |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80.8 GB | 建議用於單一 128 GB 節點 |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | 將第 37–42 層保持在 Q4 精度以提升準確度。可容納於 128 GB 內，但留給上下文的空間較少 |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | 品質更高。需要透過多節點叢集使用兩個 Halo 節點 |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3.6 GB | 用於推測式解碼（speculative decoding）以提升生成速度的選用附加元件 |

**IQ2_XXS imatrix** 模型是一個不錯的起點。它可輕鬆容納於單一節點中，並保留足夠的記憶體供合理大小的上下文視窗使用。

## 安裝 ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) 是一個輕量級終端機使用者介面，能讓您輕鬆在 Strix Halo 上安裝並執行 ds4。它可處理建立 toolbox 容器、下載模型權重以及啟動伺服器等工作。請使用 `pipx` 進行安裝：

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

啟動 cockpit：
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

## 建立 Toolbox

在 **Interactive Toolboxes** 分頁中，選擇最新可用/穩定版本的 toolbox（例如 `ds4-rocm-7.2.4`），然後點擊 **Create/Update**。這會拉取容器映像檔並建立 toolbox 環境。


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

## 下載模型

前往 **Model Manager** 分頁。從下拉選單中選擇 **IQ2_XXS imatrix (~80.8 GB)**，然後點擊 **Download**。模型檔案預設會儲存至 `~/ds4`（您可以變更儲存路徑）。

> **注意：** IQ2_XXS 模型約 80 GB，因此下載時間可能依您的網路連線狀況而有所不同。下載完成後即可繼續。

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

## 啟動伺服器

前往 **Server Mode** 分頁。選擇已下載的模型與 toolbox，然後設定上下文大小、主機（host）與連接埠（port）。設定完成後，點擊 **Start ds4-server**。

> **提示** 上下文大小設為 `126000` 是一個合理的起始值，應可容納於單一節點中——如果您有多餘的記憶體，可以設得更高；如果遇到記憶體不足的錯誤，則可以降低此值。連接埠（本指南中為 `8000`）可任意選擇；選擇任何未被使用的連接埠即可。

> **KV Disk Cache（選用）。** 開啟 **KV Disk Cache** 會將 KV 快取卸載至磁碟（位於 **Host Cache Dir**，預設為 `~/.cache/ds4-kv`），這樣重複的系統提示詞就能從 SSD 還原，而不需要重新計算。這是針對具有長且重複提示詞的程式碼助理工作流程的效能優化，並**非**執行伺服器所必需的功能。

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

伺服器啟動後將在連接埠 8000 上監聽，並在 `http://localhost:8000/v1` 公開一個相容 OpenAI 的 API 端點。

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

## 連接 Web UI

您可以連接任何支援 OpenAI API 格式的聊天介面。例如，若要使用 HuggingFace ChatUI：

```bash
docker run -p 3000:3000 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

在瀏覽器中開啟 `http://localhost:3000` 即可開始聊天。
## 連接程式碼代理

ds4 伺服器同時提供 OpenAI 與 Anthropic 相容的端點,因此大多數程式碼代理都可以直接連接到它。舉例來說,若要將它加入 `pi` 程式碼代理,請將以下區塊加入 `~/.pi/agent/models.json`:

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

> **提示**:如果您的程式碼代理或 Web UI 執行在與 Halo 平台不同的機器上,您需要透過 SSH 轉發連接埠 8000:
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```

## 後續步驟

- **多節點叢集**:如果您擁有兩台 Halo 裝置,ds4 支援透過管線平行處理(pipeline parallelism)將 Q4 模型(約 153 GB)分散到兩台機器上。請參閱[ds4-toolbox 文件](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism)以取得設定說明。
- **推測解碼(MTP)**:下載 MTP 權重(約 3.6 GB),並在啟動伺服器時傳入 `--mtp`,以提升產生速度。
- **KV 快取磁碟卸載**:針對程式碼代理工作流程,啟用 `--kv-disk-dir`,讓重複的系統提示可從 SSD 還原,而不必每次重新計算。

如需更多資訊,請參閱 [ds4 儲存庫](https://github.com/antirez/ds4) 與 [ds4-cockpit 工具箱](https://github.com/kyuz0/strix-halo-ds4-toolbox)。