<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機器翻譯。**本頁面是由英文自動翻譯而成，尚未經過人工審閱。內容可能包含錯誤，且某些指示、命令、下載項目、產品供應情況或其他內容可能因語言或地區而異。如本文件與英文版本之間存在任何不一致或差異，應以該 playbook 之英文原始版本為準。
<!-- auto-translated-disclaimer:end -->

# 以 Lemonade Server 為後端執行 OpenClaw

## 概述

[**OpenClaw**](https://openclaw.ai/) 是一個自主 AI 代理程式，能夠代表您撰寫並執行程式碼、管理檔案，並完成複雜的多步驟任務。與只回答問題的聊天助理不同，OpenClaw 會在您的系統上採取實際行動，這意味著它需要一個能跟上高需求代理迴圈的快速且強大的 AI 後端。

[**Lemonade Server**](https://lemonade-server.ai/) 正是這樣的後端。它是一個開源的本地推論伺服器，可直接在您的硬體上執行 GenAI 模型，並透過業界標準的 OpenAI API 對外提供服務。

兩者結合，構成了一個完全本地化的 AI 代理堆疊：Lemonade 負責模型推論，OpenClaw 則提供代理迴圈，將模型輸出轉化為實際行動。

> **繼續之前請注意：** OpenClaw 是一個高度自主的 AI 代理程式。授予任何 AI 代理程式對您系統的存取權，可能會導致不可預測或非預期的結果。請務必先了解相關風險，並在您能接受自主軟體代表您行事的前提下再繼續操作。

---

## 您將學到什麼

完成本操作手冊後，您將能夠：

- 了解 **Lemonade Server**
- **安裝 OpenClaw**，並**將其指向 Lemonade Server** 作為其 AI 後端。
- **啟動 OpenClaw 閘道器**並確認您的代理程式已準備就緒。
- **連接通訊頻道**（Discord 或 Telegram），讓您可以從任何裝置與您的代理程式聊天。

---

<!-- @device:halo_box,halo,stx,krk -->
## 設定記憶體配置

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## 檢查軟體更新

<!-- @require:software-update -->
<!-- @device:end -->

## 安裝軟體先決條件

<!-- @os:linux -->
- 執行 **Ubuntu 24.04+** 或相容的 Debian 系 Linux 發行版（具備 `apt-get`）的電腦
- 至少 **12 GB 的 RAM**（若要使用較大的模型建議 64 GB 以上）
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/)（可選，用於為 OpenClaw 建立沙盒環境）
- **約 10–30 GB 的可用磁碟空間**，用於存放模型權重
<!-- @os:end -->

<!-- @os:windows -->
- 執行 **Windows 10/11** 的電腦
- 至少 **12 GB 的 RAM**（若要使用較大的模型建議 64 GB 以上）
- **約 10–30 GB 的可用磁碟空間**，用於存放模型權重
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)（可選，用於為 OpenClaw 建立沙盒環境）
<!-- @os:end -->

<!-- @require:lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## 拉取並載入推薦模型

本操作手冊推薦的模型是來自 Unsloth 的 **Qwen3.6-35B-A3B-GGUF**，這是一個強大的 MoE 模型，具備 263k token 的上下文視窗，非常適合代理工作負載。此模型採用 UD-Q4_K_XL 量化方式。請立即拉取它：

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

接著以較大的上下文視窗載入它，並將此設定儲存以供日後使用：

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

此模型的預設上下文長度為 262,144 個 token。若您遇到記憶體不足（OOM）錯誤，可考慮縮小上下文視窗。但由於 Qwen3.6 會利用擴充的上下文來處理複雜任務，我們建議至少保持 128K token 的上下文長度，以維持其思考能力。

> **提示：停用思考模式以加快代理程式回應速度：** Qwen3.6-35B-A3B 預設會以思考模式運作，這會在每次回應前增加延遲。對於代理迴圈而言，這種額外開銷會迅速累積。[lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) 儲存庫提供了一個現成的設定檔，可停用思考模式。若要使用它，請下載該檔案並匯入：
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

我們建議在 WSL 中執行 OpenClaw，並將其連接到原生執行於 Windows 上的 Lemonade。這樣一來，您可以在 Windows 端保有 Lemonade 的 GPU 加速功能，同時為 OpenClaw 提供一個 Linux shell 環境。

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

在 Ubuntu 終端機內執行：

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

結束 WSL 並重新啟動它：

```powershell
exit
wsl --shutdown
wsl
```

### 將 Windows 上的 Lemonade 橋接至 WSL

WSL2 在虛擬網路中執行。Windows 上的 Lemonade 綁定到 `127.0.0.1`，而 WSL 無法直接連接到它。Windows 連接埠代理可將流量從 WSL 閘道 IP 轉發到 Windows 本機（localhost）。

**尋找您的 WSL 閘道 IP**（在 WSL 內執行）：

```bash
ip route show default | awk '{print $3}' | head -1
```

**新增連接埠代理**（以系統管理員身分在 PowerShell 中執行，將 `<WSL-Gateway-IP>` 替換為您的 WSL 閘道 IP）：

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> 注意：若您遇到 `netsh: command not found` 錯誤，請嘗試改用明確的執行檔名稱 `netsh.exe`

**新增防火牆規則**（在同一個具管理員權限的 PowerShell 中）：

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**從 WSL 驗證**：

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

若您在前一步驟已載入 Qwen3.6-35B-A3B-GGUF 模型，應該會看到如下的 JSON 輸出：

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

#### 重新啟動後保持橋接正常運作

`netsh portproxy` 規則在重新開機後仍會保留，但 WSL 閘道器 IP 可能在執行 `wsl --shutdown` 或重新開機後發生變化。發生這種情況時，代理仍會指向舊的 IP，導致 Lemonade 從 WSL 中無法連線。若發生此情況，請使用下列其中一種方法。

**選項 1（建議）— 自動修復橋接。** 為避免每次都手動操作，請使用排程工作，在每次啟動與登入時檢查橋接狀態，並僅在閘道器 IP 已變更時才重建橋接。請參閱 [Lemonade WSL 橋接自動修復指南](assets/RepairLemonadeWslBridge.md)。


**選項 2 — 手動修復橋接。** 首先，在 WSL 內執行以下指令以取得目前的 WSL 閘道器 IP：

```bash
ip route show default | awk '{print $3}' | head -1
```

複製此值；您將在下方用它取代 `<new-WSL-Gateway-IP>`。

接著，在**具系統管理員權限的 PowerShell**（以系統管理員身分執行）中，列出現有規則、刪除已過期的 Lemonade 規則，並使用目前的 IP 新增一條規則：

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

在 `show all` 的輸出中，過期的 Lemonade 規則是連線位址為 `127.0.0.1`、連接埠為 `13305` 的項目；其監聽位址就是您的 `<old-WSL-Gateway-IP>`。依該位址刪除只會移除這一條規則，不會影響您機器上其他的連接埠代理規則。

您在設定期間新增的防火牆規則綁定於連接埠 `13305`（而非 IP），因此它仍會持續運作，不需要重新建立。

> **建議：** 為避免閘道器問題，我們強烈建議採用以下 shell 設定：
> - **Windows 指令**應在 **PowerShell** 中執行
> - **WSL 發行版指令**應在**命令提示字元**（以**系統管理員**身分執行）中執行

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
> 請在您的 **WSL 終端機**內執行本節中的指令。
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

`--no-onboard` 旗標會跳過互動式設定精靈，您將在下一步手動設定模型後端，這讓您能精確控制使用哪個模型與伺服器。

開啟一個新終端機並確認安裝：

```bash
openclaw --version
```

> **提示：** 若安裝後出現 `command not found`，請將 npm 的全域 bin 目錄加入 PATH：
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> 若要使其永久生效，請將上述行加入您的 `~/.bashrc` 或 `~/.zshrc` 檔案。

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


### 設定 OpenClaw 使用 Lemonade

執行 OpenClaw 的非互動式導入設定。
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

> **OpenClaw 上下文視窗大小設定：** 當 `contextTokens > contextWindow − reserveTokens` 時，OpenClaw 的壓縮機制便會觸發。預設的 `reserveTokensFloor` 為 20,000 tokens，這是一個下限值，當其低於 `reserveTokens` 時會覆蓋它，因此任何低於約 37k 的模型上下文都會觸發無限壓縮迴圈。在您的設定中一次設定較低的保留值並停用該下限，即可套用到每個模型，不需要針對個別模型調整：
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` 是一個*下限*（最小防護值），而不是保留值本身，僅設定下限並不會產生任何效果。`reserveTokensFloor: 0` 會停用此防護，讓較低的 `reserveTokens` 值得以生效。
>
> **何時套用此設定：** 若您模型的有效上下文視窗低於約 37k，無論是因為模型本身較小（例如 8k、16k、32k），或是因為您刻意將其限制在較低值（例如載入 128k 模型但在 Lemonade 中將上下文設為 16k），請使用此設定。若不套用，OpenClaw 在啟動時將進入無限壓縮迴圈。

>
> **大型上下文模型於完整上下文下運作：** 您可以完全跳過此設定。預設值即可正常運作，壓縮機制會在視窗填滿前適時啟動，且模型仍有充裕空間可產生較長的回應。若您仍套用此設定，請注意 `reserveTokens: 4096` 會將回應長度限制在約 4k tokens，可能導致長檔案產生或詳細規劃被截斷。
>
> **應在何處新增此設定：** 請將 `compaction` 區塊放置於 `openclaw.json`（通常位於 `~/.openclaw/openclaw.json`）中的 `agents.defaults` 內：
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
> 您設定檔的其餘部分（gateway、channels、models 等）維持不變，只需新增 `compaction` 這個鍵即可。
### （建議）啟用 Docker 沙盒功能

OpenClaw 可以將所有代理程式的檔案與程式碼操作導向獨立的 Docker 容器，而非直接在主機上執行。這樣能將任何非預期動作的影響範圍限制在沙盒內，讓主機檔案系統與網路不受影響。

建置一次沙盒映像檔（必須已安裝 Docker）：

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

# Docker Desktop injects its WSL cli-tools a few seconds after the distro boots.
for i in $(seq 1 30); do
  docker version >/dev/null 2>&1 && break
  sleep 2
done
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

執行以下指令，在 `~/.openclaw/openclaw.json` 中現有的 `agents.defaults` 區塊內加入 `sandbox` 鍵：

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

沙盒容器預設**沒有網路存取權限**。有關綁定掛載與網路覆寫設定，請參閱 [沙盒參考文件](https://docs.openclaw.ai/gateway/sandboxing)。

> #### 疑難排解：Docker 權限被拒
> 
> 如果在執行 Docker 指令時出現「permission denied」錯誤：
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
> **步驟 2：若問題仍未解決，套用永久修復方式**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> 接著**重新啟動**您的系統。
> 
> **快速臨時修復**（重新開機後會失效）：
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

<!-- @os:linux -->
## （建議）OpenClaw 與 Firecrawl 服務整合

[Firecrawl](https://docs.firecrawl.dev/introduction) 提供自架式的網頁爬取與內容擷取服務，能夠克服這些挑戰，充分發揮 OpenClaw 自動化的完整潛力。

在此設定中，OpenClaw 以一組由 Podman 管理的 Docker 容器方式執行。為了簡化生命週期管理與自動啟動，我們將 Firecrawl 註冊為使用者層級的 `systemd` 服務，藉此協調底層的 Podman Compose 堆疊。這讓 OpenClaw 可以使用標準的 `systemctl --user` 指令來啟動閘道、停止並驗證 Firecrawl 服務，而不需要直接與容器互動。

為了簡化整個流程，我們將其拆分為四個步驟：

---

### 1. 註冊系統服務
前往 systemd 使用者設定目錄：
```bash
cd ~/.config/systemd/user
```
建立並開啟名為 `firecrawl.service` 的新檔案。
```bash
nano firecrawl.service
```
複製並貼上以下設定：
```bash
[Unit]
Description=OpenClaw Firecrawl Service
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=%h/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman compose -f openclaw-compose.yaml config --quiet

# Generate token and write to .env file
ExecStartPre=/bin/bash -c 'chmod 644 %h/firecrawl/.env && echo "OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 32)" > %h/firecrawl/.env'

# Step 1: Start containers in detached mode
ExecStart=/usr/bin/podman compose -f openclaw-compose.yaml up -d --remove-orphans

# Step 2: Wait for container to be healthy/ready
ExecStartPost=/bin/sleep 5

# Step 3: Run onboarding inside container in detached mode
ExecStartPost=/usr/bin/podman exec -d openclaw_gateway /bin/bash -c "openclaw onboard \
    --non-interactive \
    --accept-risk \
    --mode local \
    --auth-choice skip \
    --gateway-auth token \
    --gateway-token "$OPENCLAW_GATEWAY_TOKEN" "

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f openclaw-compose.yaml down

[Install]
WantedBy=default.target
```
至此，該服務已被定義，但尚未在 `systemd` 中註冊。
請確認檔案名稱與您上方建立的完全一致，然後執行：
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
如果成功，您應該會看到以下輸出：

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` 內包含指向已設定為自動啟動之服務的符號連結。

### 2. 設定 Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) 非常適合需要完全掌控其擷取與資料處理環境的使用者，但代價是需要投入更多維護與設定工作。

首先複製（clone）該儲存庫：
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
在 `/firecrawl` 目錄中建立一個 `.env` 檔案：
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY="" # optional
```
### 3. 使用 Podman Compose 部署 OpenClaw

在繼續之前，請確認您已拉取最新的 OpenClaw Docker 映像檔：
```bash
podman pull ghcr.io/openclaw/openclaw:latest
```
完成後，下載 OpenClaw Compose 檔案 [openclaw-compose.yaml](assets/openclaw-compose.yaml) 並將其放置於根目錄 `/firecrawl` 中：

> 依照 `WorkingDirectory=${HOME}/firecrawl` 的指定，此慣例是 `systemd` 正確找到並啟動服務所必需的。

> 您隨時可以依需求加入其他 Firecrawl 服務來擴充此堆疊。完整可用服務清單可於官方 [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) 中找到。

### 4. 透過 Firecrawl 啟動 OpenClaw 服務

在將控制權交給 `systemd` 之前，請先手動執行該堆疊，驗證一切運作正常：
```bash
podman compose -f openclaw-compose.yaml up -d
```
如果一切設定正確，您應該會看到 OpenClaw 容器啟動，且命令列輸出應類似如下：
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

驗證完成後，在繼續之前先將堆疊關閉：
```bash
podman compose -f openclaw-compose.yaml down
```
在啟動服務之前，您必須確保 `firecrawl` 目錄及其 `.env` 檔案設定了正確的擁有者與權限。
這對於服務在啟動時能夠寫入您的憑證是必要的。
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
現在一切都已驗證完成，透過 `systemd` 啟動該服務：
```bash
systemctl --user start firecrawl.service
```
[OpenClaw Actions](https://docs.openclaw.ai/) 可從互動式容器內存取，而 Web 儀表板則可於同一主機的相同連接埠 http://127.0.0.1:18789 使用。
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### 取得您的 `OPENCLAW_GATEWAY_TOKEN`

服務啟動並執行後，您會發現主目錄下新建立了一個 `.openclaw` 目錄（~/.openclaw）。此目錄預設是鎖定的，因此您需要先解鎖才能取得您的閘道權杖。

1. 授予該目錄存取權限：
```bash
sudo chmod 777 ~/.openclaw/
```
2. 讀取您的閘道權杖：
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
在輸出結果中找到 `OPENCLAW_GATEWAY_TOKEN` 的值。

3. 在瀏覽器中開啟閘道儀表板 http://127.0.0.1:18789。系統提示驗證時，貼上您的權杖。

若要停止服務，請執行：
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## 啟動 OpenClaw Gateway

gateway 是負責管理 agent 迴圈並提供儀表板服務的 OpenClaw 程序：

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

若要開啟儀表板，請在 gateway 仍在執行的情況下，於第二個終端機中執行：

```bash
openclaw dashboard
```

由於 gateway 綁定於 loopback，當從同一台機器開啟儀表板時會自動驗證通過，本機存取不需要輸入 token 或裝置核准。你應該會看到 OpenClaw 儀表板，並列出你的 Lemonade 模型作為使用中的後端。

> 如果你已啟用沙盒功能，可以透過在儀表板中要求 agent 執行 `run hostname` 來驗證。如果你看到的是短容器 ID 而非你機器的主機名稱，就表示沙盒運作正常。

**恭喜，你已從零開始建構了一個完全在地端運作的 AI agent 堆疊。**

> **需要 gateway token 嗎？** 執行 `openclaw dashboard --no-open` 以印出內嵌 token 的儀表板 URL（也會嘗試將其複製到剪貼簿）。或者，token 也存放於 `~/.openclaw/openclaw.json` 中的 `gateway.auth.token`。

**從另一台裝置存取儀表板（透過 SSH 通道）**

如果 OpenClaw 是在遠端機器上執行，你可以透過 SSH 通道從你的本機存取其儀表板。此通道會轉發 gateway 連接埠（`18789`），讓你的本機瀏覽器可以透過 `127.0.0.1` 與遠端 gateway 溝通。

1. 從你的**本機**，先連線至遠端機器一次並接受指紋提示，讓該主機加入你的已知主機清單：

   ```bash
   ssh user@<host-ip>
   ```

2. 仍在你的**本機**上，開啟 SSH 通道：

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **注意：** 輸入密碼後，終端機不會顯示任何輸出，看起來像是卡住了。這是正常現象：`-N` 旗標告訴 SSH 不要執行任何遠端指令，因此它只會保持通道開啟。請讓此終端機持續執行。

3. 在你的**本機**上，開啟瀏覽器並前往 `http://127.0.0.1:18789`。

4. 在**遠端機器**上，印出 gateway token 並將其貼到瀏覽器中登入：

   ```bash
   openclaw dashboard --no-open
   ```

   這會印出內嵌 token 的儀表板 URL；複製 token 以登入。（此 token 也存放於 `~/.openclaw/openclaw.json` 中的 `gateway.auth.token`。）

> **核准遠端裝置：** 當你從另一台機器或手機開啟儀表板時，瀏覽器可能會顯示一個請求 ID。在**遠端機器**上，列出待處理的請求：
> ```bash
> openclaw devices list
> ```
> 然後核准對應的請求：
> ```bash
> openclaw devices approve <requestId>
> ```
> 這僅在遠端或次要裝置存取時才需要；來自同一台機器的 loopback 存取會自動驗證通過。詳情請參閱[遠端存取](https://docs.openclaw.ai/gateway/remote)文件。

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## 選用：連接通訊頻道

一旦 gateway 執行中，你就可以從任何裝置存取你的在地端 agent。請選擇符合你設定的選項。OpenClaw 支援 [Discord](https://docs.openclaw.ai/channels/discord)、[Telegram](https://docs.openclaw.ai/channels/telegram) 及其他頻道，完整清單請參閱 [docs.openclaw.ai](https://docs.openclaw.ai)。

---

### 選項 A：Discord

Discord 需要一個**你擁有管理員權限**的伺服器才能新增機器人。如果你有共享的伺服器但並非其擁有者，請改用選項 B（Telegram）。

#### 建立 Discord 帳號與伺服器

如果你還沒有 Discord 帳號，請至 [discord.com](https://discord.com) 註冊。你也需要一個你具有管理員身分的伺服器，可點選 Discord 側邊欄的 **+** 圖示並選擇**建立專屬伺服器**來建立一個。私人伺服器即可。

#### 建立 Discord 應用程式與機器人

1. 前往 [Discord Developer Portal](https://discord.com/developers/applications) 並點選 **New Application**。為它命名（例如「openclaw-bot」）。
2. 在側邊欄中，點選 **Bot**。為機器人設定一個使用者名稱。
3. 仍在 Bot 頁面上，捲動至 **Privileged Gateway Intents** 並啟用：
   - **Message Content Intent**（必要）
   - **Server Members Intent**（建議）
4. 捲動回上方，點選 **Reset Token** 以產生你的機器人 token。複製它。

#### 將機器人加入你的伺服器

1. 在側邊欄中，點選 **OAuth2/ URL Generator**。
2. 在 **Scopes** 底下，啟用 `bot` 和 `applications.commands`。
3. 在 **Bot Permissions** 底下，啟用：View Channels、Send Messages、Read Message History、Embed Links、Attach Files。
4. 複製產生的 URL，貼到你的瀏覽器中，選擇你的伺服器並確認。此機器人現在應該會出現在你伺服器的成員清單中。

#### 收集你的 ID

在 Discord 中啟用開發者模式（**User Settings/ Advanced/ Developer Mode**），然後：
- 右鍵點選你的伺服器圖示：**Copy Server ID**
- 右鍵點選你自己的頭像：**Copy User ID**

#### 允許來自伺服器成員的私訊

右鍵點選你的伺服器圖示/ **Privacy Settings**/ 切換開啟 **Direct Messages**。這可讓機器人私訊你，這是配對步驟所必需的。

#### 為 Discord 設定 OpenClaw

將你的機器人 token 存為環境變數，然後建立一個單一的修補檔，用來啟用 Discord、參照該 token，並將你的伺服器加入允許清單。請將 `<server_id>` 和 `<user_id>` 替換為上方收集到的 ID。

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

> **請勿依賴要求 agent 來設定此項目。** 當啟用沙盒功能時，agent 無法從沙盒內部寫入 `~/.openclaw/openclaw.json`，請改在主機上使用上述 CLI 指令。

重新啟動 gateway 以套用新的頻道設定：

```bash
openclaw gateway run --bind loopback --port 18789
```

你應該會在幾秒鐘內於 gateway 輸出中看到 `logged in to discord as <bot-name>`。
#### 配對您的 Discord 帳號

在 Discord 中私訊機器人。它會回覆一組簡短的配對代碼。

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

在執行 OpenClaw 的機器上核准它：
```bash
openclaw pairing approve discord <CODE>
```

> 配對代碼會在一小時後過期。

現在您可以直接從 Discord 與您的代理程式對話，並將工作交給本機硬體處理。

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### 選項 B：Telegram

對大多數使用者來說，Telegram 比 Discord 更簡單，不需要伺服器，也不需要管理員權限。

#### 建立 Telegram 機器人

1. 開啟 Telegram，並傳訊息給 **@BotFather**。
2. 傳送 `/newbot` 並依照提示操作。儲存它給您的機器人權杖。

#### 為 Telegram 設定 OpenClaw

將權杖儲存為環境變數：

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

將頻道設定加入 `~/.openclaw/openclaw.json`（或透過儀表板進行修補）：

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

重新啟動閘道器，然後在 Telegram 中傳送任何訊息給您的機器人。核准配對：

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

配對代碼會在一小時後過期。現在您可以透過 Telegram 私訊與您的代理程式對話。

---

## 後續步驟

既然您的代理程式現在可以從手機接收指令並在本機執行動作，以下是三個值得探索的方向：

1. **股市摘要工具**：排程 OpenClaw 以固定間隔從金融 API 擷取資料，用您的本機模型摘要當天的漲跌走勢，並在每天早上透過您選擇的頻道推播摘要到您的手機。

2. **微調監控器**：透過 Telegram 或 Discord 遠端啟動訓練工作，然後讓代理程式追蹤訓練紀錄，並定期回報損失值、GPU 使用率與磁碟使用量到您的手機。如果訓練過程停滯或 VRAM 突然飆升，您無需守在機器旁就能立即得知。

3. **搭配本機 VLM 的物聯網應用**：將攝影機對準您家前門，在 Lemonade 上執行視覺模型，並讓 OpenClaw 依需求或觸發條件分析畫面。從您的手機詢問「今天有包裹送達嗎？」，就能從您自己的硬體得到直接的答案。

<!-- @os:linux -->
<!-- @test:id=lemonade-unload-linux timeout=60 hidden=True -->
```bash
# CI cleanup: unload the model so the GPU pool is free
lemonade unload || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-unload-windows timeout=60 hidden=True -->
```powershell
# CI cleanup: unload the model so the GPU pool is free
lemonade unload
exit 0
```
<!-- @test:end -->
<!-- @os:end -->