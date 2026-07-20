<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# 在 OpenClaw 中以 Lemonade Server 作為後端運行

## 概觀

[**OpenClaw**](https://openclaw.ai/) 是一款自主 AI 代理，能夠代表您撰寫並執行程式碼、管理檔案，並處理複雜的多步驟任務。與只會回答問題的聊天助理不同，OpenClaw 會在您的系統上實際執行動作，因此它需要一個快速且強大的 AI 後端，才能跟上高要求的代理循環運作。

[**Lemonade Server**](https://lemonade-server.ai/) 正是這樣的後端。它是一個開源的本地推論伺服器，能直接在您的硬體上運行生成式 AI 模型，並透過業界標準的 OpenAI API 對外提供服務。

兩者結合後，形成一套完全本地化的 AI 代理堆疊：Lemonade 負責模型推論，OpenClaw 則提供代理循環，將模型輸出轉化為實際動作。

> **在繼續之前：** OpenClaw 是一款高度自主的 AI 代理。讓任何 AI 代理存取您的系統，都可能導致不可預期或非預期的結果。請在充分理解相關風險，並能接受自主軟體代您行事的前提下再繼續操作。

---

## 您將學到什麼

完成本操作手冊後，您將能夠：

- 認識 **Lemonade Server**
- **安裝 OpenClaw** 並**將其指向 Lemonade Server** 作為其 AI 後端。
- **啟動 OpenClaw 閘道器**並確認您的代理已可開始運作。
- **連接通訊管道**（Discord 或 Telegram），讓您可以在任何裝置上與您的代理聊天。

---

## 設定記憶體配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 檢查軟體更新

<!-- @require:software-update -->
<!-- @device:end -->

## 安裝軟體先決條件

<!-- @os:linux -->
- 一台執行 **Ubuntu 24.04+** 或相容的、具備 `apt-get` 的 Debian 系 Linux 發行版的電腦
- 至少 **12 GB 記憶體**（若使用較大型模型，建議 64 GB 以上）
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/)（選用，用於為 OpenClaw 建立沙箱環境）

- **約 10–30 GB 的可用磁碟空間**，用於存放模型權重
<!-- @os:end -->
<!-- @os:windows -->
- 一台執行 **Windows 10/11** 的電腦
- 至少 **12 GB 記憶體**（若使用較大型模型，建議 64 GB 以上）
- **約 10–30 GB 的可用磁碟空間**，用於存放模型權重
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)（選用，用於為 OpenClaw 建立沙箱環境）
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## 拉取並載入建議的模型

本操作手冊推薦的模型是來自 Unsloth 的 **Qwen3.6-35B-A3B-GGUF**，這是一款強大的 MoE 模型，具備 263k 令牌的上下文視窗，非常適合代理工作負載。此模型採用 UD-Q4_K_XL 量化。現在就拉取它：

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

接著以較大的上下文視窗載入它，並儲存此設定供未來使用：

<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

此模型的預設上下文長度為 262,144 個令牌。如果您遇到記憶體不足（OOM）錯誤，可以考慮縮小上下文視窗。不過，由於 Qwen3.6 會利用擴充的上下文來處理複雜任務，我們建議至少維持 128K 令牌的上下文長度，以保留其思考能力。

> **提示：停用思考模式以加快代理回應速度：** Qwen3.6-35B-A3B 預設以思考模式運行，這會在每次回應前增加延遲。對於代理循環而言，這種開銷會迅速累積。[lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) 儲存庫提供了一個現成的設定檔，可以停用思考模式。要使用它，請下載該檔案並匯入：
>
> ```bash
> curl -LO https://raw.githubusercontent.com/lemonade-sdk/recipes/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json
> lemonade import Qwen3.6-35B-A3B-NoThinking.json
> ```

---

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$modelsJson = $null
for ($i = 0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}

if (-not $modelsJson) {throw "Lemonade server not ready on http://127.0.0.1:13305"}
Write-Host "OK: Lemonade server is responding"

$parsed = $modelsJson | ConvertFrom-Json
$entry = $parsed.data | Where-Object { $_.id -eq "${openclaw_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${openclaw_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${openclaw_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${openclaw_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${openclaw_model} is not saved with ctx_size=262144. Run: lemonade load ${openclaw_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${openclaw_model} is saved with ctx_size=262144"

$body = @{
  model = "${openclaw_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "openclaw-lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
    -H "Content-Type: application/json" `
    --data-binary "@$tmpBody"
  if (-not $out) {throw "Empty response from Lemonade chat/completions"}
  Write-Host "OK: Lemonade chat/completions returned a response"
}
finally {
  Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-chat-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

export MODELS_JSON="$models_json"

python3 - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["MODELS_JSON"])
model_id = "${openclaw_model}"

entry = None
for item in data.get("data", []):
    if item.get("id") == model_id:
        entry = item
        break

if entry is None:
    print(f"Model {model_id} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print(f"Model {model_id} is present but not downloaded in Lemonade. Please download it before running CI.")
    sys.exit(1)

print(f"OK: {model_id} model is downloaded in Lemonade")

ctx_size = entry.get("recipe_options", {}).get("ctx_size")
if ctx_size != 262144:
    print(f"Model {model_id} is not saved with ctx_size=262144. Run: lemonade load {model_id} --ctx-size 262144 --save-options")
    sys.exit(1)
print(f"OK: {model_id} is saved with ctx_size=262144")
PY

body='{
  "model": "${openclaw_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Lemonade chat/completions returned a response"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->

## 設定 WSL

我們在 WSL（推薦方式）中運行 OpenClaw，並將其連接到原生運行於 Windows 上的 Lemonade。這樣一來，您就能在 OpenClaw 中使用 Linux shell 環境，同時保留 Lemonade 在 Windows 端的 GPU 加速能力。

### 安裝 WSL 與 Ubuntu

以系統管理員身分開啟 PowerShell，並安裝 WSL 核心：

```powershell
wsl --install --no-distribution
```

接著安裝 Ubuntu：

```powershell
wsl --install -d Ubuntu-24.04
```

### 在 WSL 中啟用 systemd

在 Ubuntu 終端機中執行以下指令：

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

重新啟動 WSL：

```powershell
wsl --shutdown
wsl
```

### 將 Lemonade 從 Windows 橋接至 WSL

WSL2 運行於虛擬網路中。Windows 上的 Lemonade 會綁定至 `127.0.0.1`，而 WSL 無法直接存取此位址。透過 Windows 連接埠代理，即可將流量從 WSL 閘道器 IP 轉發至 Windows 本機主機。

**找出您的 WSL 閘道器 IP**（在 WSL 中執行）：

```bash
ip route show default | awk '{print $3}' | head -1
```

**新增連接埠代理**（以系統管理員身分在 PowerShell 中執行，將 `<WSL-Gateway-IP>` 替換為您的 WSL 閘道器 IP）：

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**新增防火牆規則**（在同一個提升權限的 PowerShell 中執行）：

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**從 WSL 進行驗證**：

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

如果您在前一個步驟中已經載入 Qwen3.6-35B-A3B-GGUF 模型，應該會看到如下所示的 JSON 輸出：

```json
{
  "data": [
    {
      "checkpoint": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL",
      "checkpoints": {
        "main": "unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_XL"
      },
      "mmproj": "unsloth/Qwen3.6-35B-A3B-GGUF:mmproj-F16.gguf",
      ....
    }
  ],
  "object": "list"
}
```

> `netsh portproxy` 規則在重新開機後仍會保留，但執行 `wsl --shutdown` 後，WSL 閘道器 IP 可能會發生變化。如果重新啟動後從 WSL 無法連接到 Lemonade，請取得更新後的閘道器 IP，並以此新 IP 更新代理設定。

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

echo "WSL gateway IP: $WINDOWS_HOST"

models_json="$(curl -fsS --max-time 5 "http://$WINDOWS_HOST:13305/api/v1/models")"

if [ -z "$models_json" ]; then
  echo "Could not reach Lemonade from WSL at http://$WINDOWS_HOST:13305/api/v1/models"
  echo "Check the Windows netsh portproxy and firewall rule from the README."
  exit 1
fi

echo "$models_json" | python3 -m json.tool >/dev/null
echo "OK: WSL can reach native Windows Lemonade through the bridge"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "wsl-lemonade-bridge-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "WSL Lemonade bridge test failed"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 

---
<!-- @os:end -->

## 安裝並設定 OpenClaw

### 安裝 OpenClaw
<!-- @os:windows -->
> 請在您的 **WSL 終端機**中執行本節的指令。
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

`--no-onboard` 旗標會略過互動式設定精靈，您將在下一步中手動設定模型後端，這能讓您精確掌控所使用的模型與伺服器。

開啟一個新的終端機並確認安裝：

```bash
openclaw --version
```

> **提示：** 如果安裝後出現 `command not found`，請將 npm 的全域 bin 目錄加入 PATH：
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> 若要讓此設定永久生效，請將上面這行加入您的 `~/.bashrc` 或 `~/.zshrc` 檔案中。

<!-- @os:linux -->
<!-- @test:id=openclaw-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
echo "HOME=$HOME"
echo "PATH=$PATH"
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
node -v
npm -v
openclaw --version
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->
### 配置 OpenClaw 以使用 Lemonade

執行 OpenClaw 的非互動式引導設定。
<!-- @os:linux -->
```bash
openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->
<!-- @os:windows -->
```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->

此指令會將 OpenClaw 的設定寫入 `~/.openclaw/openclaw.json`。

> **OpenClaw 情境視窗大小設定：** 當 `contextTokens > contextWindow − reserveTokens` 時，OpenClaw 的壓縮機制便會觸發。預設的 `reserveTokensFloor` 為 20,000 個 token，這是一個下限值，當其低於 `reserveTokens` 時會覆蓋該值，因此任何低於約 37k 的模型情境都會觸發無限壓縮循環。在設定中只需設定一次較低的保留值並停用該下限，即可套用於每一個模型，不需針對個別模型進行調整：
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` 是一個*下限值*（最低保障值），而非保留值本身，僅設定下限值不會有任何效果。`reserveTokensFloor: 0` 會停用此保障機制，讓較低的 `reserveTokens` 值得以生效。
>
> **何時套用此設定：** 若您的模型有效情境視窗低於約 37k，無論是因為模型本身較小（例如 8k、16k、32k），或是您刻意將其限制為較低的值（例如載入一個 128k 的模型，但在 Lemonade 中將情境設為 16k），請套用此設定。若未套用，OpenClaw 在啟動時會進入無限壓縮循環。

>
> **在完整情境下使用大型情境模型：** 您可以完全略過此設定。預設值即可正常運作，壓縮機制會在視窗填滿前適時啟動，且模型仍有充裕空間可產生較長的回應。若您仍套用此設定，請注意 `reserveTokens: 4096` 會將回應長度限制在約 4k 個 token，這可能會截斷較長的檔案生成內容或詳細計畫。
>
> **在何處新增此設定：** 將 `compaction` 區塊放置於您的 `openclaw.json`（通常位於 `~/.openclaw/openclaw.json`）中的 `agents.defaults` 內：
>
> ```json
> {
>   "agents": {
>     "defaults": {
>       "workspace": "/home/<you>/.openclaw/workspace",
>       "model": {
>         "primary": "lemonade/<your-model-id>"
>       },
>       "compaction": {
>         "reserveTokens": 4096,
>         "reserveTokensFloor": 0
>       }
>     }
>   }
> }
> ```
>
> 您設定檔中的其餘部分（gateway、channels、models 等）皆維持不變，僅需新增 `compaction` 這個 key 即可。

### （建議）啟用 Docker 沙箱功能

OpenClaw 可以將所有代理程式的檔案與程式碼操作導向一個獨立的 Docker 容器，而非直接在主機上執行。這樣可將任何非預期動作的影響範圍限縮在沙箱內，讓您主機的檔案系統與網路不受影響。

建置一次沙箱映像檔（必須已安裝 Docker）：

```bash
docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE
```

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

docker version

docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

echo "OK: OpenClaw sandbox Docker image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

執行以下指令，在 `~/.openclaw/openclaw.json` 中現有的 `agents.defaults` 區塊內新增 `sandbox` 這個 key：

```bash
cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5
openclaw config patch --file ./sandbox.patch.json5
```

沙箱容器預設**沒有網路存取權限**。請參閱[沙箱參考文件](https://docs.openclaw.ai/gateway/sandboxing)以了解掛載綁定與網路覆寫設定。

> #### 疑難排解：Docker 權限遭拒
> 
> 若您在執行 Docker 指令時收到「permission denied」訊息：
> 
> **步驟 1：將您的使用者加入 docker 群組**
> 
> ```bash
> sudo groupadd docker                    # Create group if needed
> sudo usermod -aG docker $USER           # Add yourself to the group
> newgrp docker                           # Activate the change
> docker run hello-world                  # Test it
> ```
> 
> **步驟 2：若問題持續發生，請套用永久修正方式**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> 接著**重新啟動**您的系統。
> 
> **快速暫時修正方式**（重新啟動後會重設）：
> ```bash
> sudo chmod 666 /var/run/docker.sock
> ```

<!-- @os:linux -->
<!-- @test:id=openclaw-onboard-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "127.0.0.1:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=openclaw-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written"
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-onboard-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

mkdir -p "$HOME/.openclaw"
rm -f "$HOME/.openclaw/openclaw.json"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"

if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "${openclaw_model}" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk

config="$HOME/.openclaw/openclaw.json"
test -f "$config"

grep -q "lemonade" "$config"
grep -q "${openclaw_model}" "$config"
grep -q "$WINDOWS_HOST:13305" "$config"

echo "OK: OpenClaw onboarding wrote Lemonade configuration inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-onboard-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw onboarding failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=openclaw-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="/mnt/wsl/docker-desktop/cli-tools/usr/bin:$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

docker_config="$(mktemp -d)"
cleanup() {
  rm -rf "$docker_config"
}
trap cleanup EXIT
export DOCKER_CONFIG="$docker_config"
printf '{ "auths": {} }\n' > "$DOCKER_CONFIG/config.json"

config="$HOME/.openclaw/openclaw.json"

if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi

docker image inspect openclaw-sandbox:bookworm-slim >/dev/null

cat > sandbox.patch.json5 <<JSON5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none"
      }
    }
  }
}
JSON5

openclaw config patch --file ./sandbox.patch.json5

grep -q '"sandbox"' "$config"
grep -Eq '"mode"[[:space:]]*:[[:space:]]*"non-main"' "$config"
grep -Eq '"scope"[[:space:]]*:[[:space:]]*"session"' "$config"
grep -Eq '"workspaceAccess"[[:space:]]*:[[:space:]]*"none"' "$config"

echo "OK: OpenClaw sandbox configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"
$tmp = Join-Path $env:TEMP "openclaw-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "OpenClaw sandbox config patch failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

### 啟動 OpenClaw Gateway

Gateway 是負責管理代理程式循環並提供儀表板服務的 OpenClaw 程序：

```bash
openclaw gateway run --bind loopback --port 18789
```

<!-- @os:linux -->
<!-- @test:id=openclaw-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable"
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=openclaw-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.openclaw/openclaw.json"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the OpenClaw onboarding test first."
  exit 1
fi
log="/tmp/openclaw-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

openclaw gateway run --bind loopback --port 18789 >"$log" 2>&1 &
gateway_pid=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:18789/ || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "OpenClaw gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi

echo "OK: OpenClaw gateway is reachable inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "openclaw-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "OpenClaw gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end --> 
<!-- @os:end -->

若要開啟儀表板，請在 gateway 仍在執行時，於第二個終端機中執行以下指令：

```bash
openclaw dashboard
```

由於 gateway 會綁定至 loopback，因此當儀表板從同一台機器開啟時會自動完成驗證，本機存取不需要輸入權杖或裝置核准。您應該會看到 OpenClaw 儀表板，並顯示您的 Lemonade 模型為使用中的後端。

> 若您已啟用沙箱功能，可以透過在儀表板中要求代理程式 `run hostname` 來進行驗證。若您看到的是簡短的容器 ID，而非您機器的主機名稱，即表示沙箱功能運作正常。

**恭喜，您已從零開始建構出一套完全在地端運行的 AI 代理程式堆疊。**

> **需要 gateway 權杖嗎？** 執行 `openclaw dashboard --no-open` 即可印出內嵌權杖的儀表板網址（該指令也會嘗試將其複製到您的剪貼簿）。您也可以在 `~/.openclaw/openclaw.json` 的 `gateway.auth.token` 中找到此權杖。
>
> **核准遠端裝置：** 當您從第二台機器或手機開啟儀表板時，瀏覽器會顯示一組請求 ID。請回到執行 gateway 的機器上，執行：
> ```bash
> openclaw devices approve <requestId>
> ```
> 此步驟僅在使用遠端或次要裝置時才需要，來自同一台機器的 loopback 存取會自動完成驗證。

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## 選用：連接通訊頻道

一旦 gateway 開始執行，您便可以從任何裝置存取您的本機代理程式。請選擇符合您設定的選項。OpenClaw 支援 [Discord](https://docs.openclaw.ai/channels/discord)、[Telegram](https://docs.openclaw.ai/channels/telegram) 及其他頻道，完整清單請參閱 [docs.openclaw.ai](https://docs.openclaw.ai)。

---

### 選項 A：Discord

Discord 需要一個**您擁有管理員權限**的伺服器才能新增機器人。若您與他人共用伺服器但並非擁有者，請改用選項 B（Telegram）。
#### 建立 Discord 帳號與伺服器

如果您沒有 Discord 帳號，請至 [discord.com](https://discord.com) 註冊。您還需要一台您具有管理員權限的伺服器，可透過點擊 Discord 側邊欄的 **+** 圖示並選擇 **Create My Own** 來建立。私人伺服器即可。

#### 建立 Discord 應用程式與機器人

1. 前往 [Discord 開發者入口網站](https://discord.com/developers/applications)，點擊 **New Application**。為其命名（例如「openclaw-bot」）。
2. 在側邊欄中，點擊 **Bot**。為機器人設定使用者名稱。
3. 仍在 Bot 頁面上，捲動至 **Privileged Gateway Intents**，並啟用：
   - **Message Content Intent**（必要）
   - **Server Members Intent**（建議）
4. 捲動回頂部並點擊 **Reset Token** 以產生您的機器人權杖。將其複製下來。

#### 將機器人加入您的伺服器

1. 在側邊欄中，點擊 **OAuth2/ URL Generator**。
2. 在 **Scopes** 下，啟用 `bot` 和 `applications.commands`。
3. 在 **Bot Permissions** 下，啟用：View Channels、Send Messages、Read Message History、Embed Links、Attach Files。
4. 複製產生的 URL，貼到您的瀏覽器中，選擇您的伺服器並確認。機器人現在應該會出現在您伺服器的成員清單中。

#### 收集您的 ID

在 Discord 中啟用開發者模式（**User Settings/ Advanced/ Developer Mode**），然後：
- 右鍵點擊您的伺服器圖示：**Copy Server ID**
- 右鍵點擊您自己的頭像：**Copy User ID**

#### 允許伺服器成員傳送私訊

右鍵點擊您的伺服器圖示/ **Privacy Settings**/ 開啟 **Direct Messages**。這樣可讓機器人傳送私訊給您，這是配對步驟所必需的。

#### 為 Discord 設定 OpenClaw

將您的機器人權杖儲存為環境變數，然後建立一個修補檔，啟用 Discord、參照該權杖，並將您的伺服器加入允許清單。將 `<server_id>` 和 `<user_id>` 替換為上述收集到的 ID。

```bash
export DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN"

cat > discord.patch.json5 <<JSON5
{
  channels: {
    discord: {
      enabled: true,
      token: { source: "env", provider: "default", id: "DISCORD_BOT_TOKEN" },
      dmPolicy: "pairing",
      groupPolicy: "allowlist",
      guilds: {
        "<server_id>": {
          requireMention: false,
          users: ["<user_id>"],
        },
      },
    },
  },
}
JSON5
openclaw config patch --file ./discord.patch.json5
```

> **請勿依賴要求代理程式來設定此項。** 當沙箱功能啟用時，代理程式無法從沙箱內部寫入 `~/.openclaw/openclaw.json`，請改用主機上的上述 CLI 指令。

重新啟動閘道，使其套用新的頻道設定：

```bash
openclaw gateway run --bind loopback --port 18789
```

您應該會在幾秒鐘內於閘道輸出中看到 `logged in to discord as <bot-name>`。

#### 配對您的 Discord 帳號

在 Discord 中私訊機器人。它會回覆一組簡短的配對碼。

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

在執行 OpenClaw 的機器上核准該配對：
```bash
openclaw pairing approve discord <CODE>
```

> 配對碼會在一小時後過期。

您現在可以直接從 Discord 與您的代理程式聊天，並將工作交由您的本地硬體處理。

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### 選項 B：Telegram

對大多數使用者而言，Telegram 比 Discord 更簡單，不需要伺服器也不需要管理員權限。

#### 建立 Telegram 機器人

1. 開啟 Telegram，並傳送訊息給 **@BotFather**。
2. 傳送 `/newbot` 並依照提示操作。儲存它提供給您的機器人權杖。

#### 為 Telegram 設定 OpenClaw

將權杖儲存為環境變數：

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

將頻道設定加入 `~/.openclaw/openclaw.json`（或透過儀表板修補）：

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "YOUR_BOT_TOKEN",
      "dmPolicy": "pairing"
    }
  }
}
```

重新啟動閘道，然後在 Telegram 中傳送任何訊息給您的機器人。核准配對：

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

配對碼會在一小時後過期。您現在可以透過 Telegram 私訊與您的代理程式聊天。

---

## 後續步驟

現在您的代理程式可以接收來自手機的指令，並在您的本地機器上執行動作，以下是三個值得探索的方向：

1. **股市摘要工具**：排程 OpenClaw 以固定間隔從金融 API 擷取資料，使用您的本地模型摘要當日的市場走勢，並每天早上透過您選擇的頻道推播摘要到您的手機。

2. **微調監控**：透過 Telegram 或 Discord 遠端啟動訓練工作，然後讓代理程式追蹤訓練日誌，並將定期的損失值、GPU 使用率和磁碟使用量回報到您的手機。如果訓練過程停滯或 VRAM 飆升，您無需親臨機器旁即可立即得知。

3. **搭配本地 VLM 的物聯網應用**：將攝影機對準您的前門，在 Lemonade 上執行視覺模型，並讓 OpenClaw 依需求或觸發條件分析畫面。從您的手機詢問「今天有包裹送達嗎？」，即可從您自己的硬體獲得直接的答案。