<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機器翻譯。**本頁面是由英文自動翻譯而成，尚未經過人工審閱。內容可能包含錯誤，且某些指示、命令、下載項目、產品供應情況或其他內容可能因語言或地區而異。如本文件與英文版本之間存在任何不一致或差異，應以該 playbook 之英文原始版本為準。
<!-- auto-translated-disclaimer:end -->

# 在 OpenClaw 中以 Lemonade Server 作為後端運行

## 概觀

[**OpenClaw**](https://openclaw.ai/) 是一個自主式 AI 代理，能夠為您撰寫並執行程式碼、管理檔案，並完成複雜的多步驟任務。與僅回答問題的聊天助理不同，OpenClaw 會在您的系統上實際採取行動，這意味著它需要一個快速且能力強大的 AI 後端，以跟上要求嚴苛的代理迴圈。

[**Lemonade Server**](https://lemonade-server.ai/) 正是這樣的後端。它是一個開源的本機推論伺服器，可直接在您的硬體上運行 GenAI 模型，並透過業界標準的 OpenAI API 將其公開。

兩者結合，形成一套完全本機化的 AI 代理堆疊：Lemonade 負責模型推論，而 OpenClaw 則提供代理迴圈，將模型輸出轉化為實際行動。

> **在繼續之前：** OpenClaw 是一個高度自主的 AI 代理。賦予任何 AI 代理存取您系統的權限，可能導致不可預測或非預期的結果。請僅在您理解相關風險，並能接受自主軟體代您行事的情況下繼續操作。

---

## 您將學到什麼

完成本操作手冊後，您將能夠：

- 了解 **Lemonade Server**
- **安裝 OpenClaw**，並**將其指向 Lemonade Server** 作為其 AI 後端。
- **啟動 OpenClaw 閘道**，並確認您的代理已準備就緒。
- **連接通訊頻道**（Discord 或 Telegram），讓您可以從任何裝置與代理聊天。

---

<!-- @device:halo_box,halo,stx,krk -->
## 設定記憶體組態

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## 檢查軟體更新

<!-- @require:software-update -->
<!-- @device:end -->

## 安裝軟體先決條件

<!-- @os:linux -->
- 一台執行 **Ubuntu 24.04+** 或相容的 Debian 基礎 Linux 發行版，並具備 `apt-get` 的電腦
- 至少 **12 GB 的 RAM**（建議使用較大模型時配備 64 GB 以上）
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/ubuntu/)（選用，用於 OpenClaw 沙盒化）
- 約 **10–30 GB 的可用磁碟空間**，供模型權重使用
<!-- @os:end -->

<!-- @os:windows -->
- 一台執行 **Windows 10/11** 的電腦
- 至少 **12 GB 的 RAM**（建議使用較大模型時配備 64 GB 以上）
- 約 **10–30 GB 的可用磁碟空間**，供模型權重使用
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)（選用，用於 OpenClaw 沙盒化）
<!-- @os:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @os:linux -->
<!-- @prereq:nodejs -->
<!-- @os:end -->
<!-- On Windows OpenClaw runs in WSL, so its Node.js is covered by the openclaw prereq. -->
<!-- @prereq:docker,openclaw,lemonade-models-qwen3-6-35b-a3b,lemonade -->

<!-- @var:id=openclaw_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## 下載並載入建議模型

本操作手冊建議使用的模型為 Unsloth 推出的 **Qwen3.6-35B-A3B-GGUF**，這是一款強大的 MoE 模型，具備 263k token 的上下文視窗，非常適合代理工作負載。此模型採用 UD-Q4_K_XL 量化。現在下載它：

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

接著以較大的上下文視窗載入它，並儲存該設定供日後使用：

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end --> 

此模型的預設上下文長度為 262,144 個 token。若您遇到記憶體不足（OOM）錯誤，可以考慮縮小上下文視窗。不過，由於 Qwen3.6 會利用延伸的上下文來處理複雜任務，我們建議至少維持 128K token 的上下文長度，以保留其思考能力。

> **提示：停用思考模式以加快代理回應速度：** Qwen3.6-35B-A3B 預設以思考模式運行，這會在每次回應前增加延遲。對於代理迴圈而言，這種額外開銷會迅速累積。[lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) 儲存庫提供了現成的設定檔，可停用思考模式。若要使用，請下載該檔案並匯入：
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

我們建議在 WSL 中運行 OpenClaw（建議做法），並將其連接至原生運行於 Windows 上的 Lemonade。這樣一來，您可以在 WSL 中取得 Linux shell 環境來運行 OpenClaw，同時讓 Lemonade 在 Windows 端保留 GPU 加速能力。

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

在 Ubuntu 終端機中執行：

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

結束 WSL 並重新啟動：

```powershell
exit
wsl --shutdown
wsl
```

### 將 Lemonade 從 Windows 橋接至 WSL

WSL2 運行於虛擬網路中。Windows 上的 Lemonade 綁定到 `127.0.0.1`，而 WSL 無法直接存取此位址。Windows 連接埠代理可將流量從 WSL 閘道 IP 轉發至 Windows localhost。

**找出您的 WSL 閘道 IP**（在 WSL 中執行）：

```bash
ip route show default | awk '{print $3}' | head -1
```

**新增連接埠代理**（以系統管理員身分在 PowerShell 中執行，並將 `<WSL-Gateway-IP>` 替換為您的 WSL 閘道 IP）：

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```
> 注意：若您遇到 `netsh: command not found` 錯誤，請改用明確的執行檔名稱 `netsh.exe`

**新增防火牆規則**（在同一個提升權限的 PowerShell 中）：

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**從 WSL 中驗證**：

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

若您已在前一步驟中載入 Qwen3.6-35B-A3B-GGUF 模型，應會看到如下的 JSON 輸出：

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

#### 重啟後保持橋接正常運作

`netsh portproxy` 規則在重新開機後仍會保留,但 WSL 閘道 IP 可能會在 `wsl --shutdown` 或重新開機後改變。發生這種情況時,proxy 仍會指向舊的 IP,導致 Lemonade 無法從 WSL 存取。若發生此情況,請使用下列其中一種選項。

**選項 1(建議)— 自動修復橋接。** 為了避免每次都要手動處理,請使用排程工作,在每次啟動與登入時檢查橋接狀態,僅在閘道 IP 改變時才重建它。請參閱[Lemonade WSL 橋接自動修復指南](assets/RepairLemonadeWslBridge.md)。


**選項 2 — 手動修復橋接。** 首先,在 WSL 內執行以下指令以取得目前的 WSL 閘道 IP:

```bash
ip route show default | awk '{print $3}' | head -1
```

複製此數值;您將在下方用它取代 `<new-WSL-Gateway-IP>`。

接著,在**提升權限的 PowerShell**(以系統管理員身分執行)中,列出現有規則、僅刪除過期的 Lemonade 規則,並使用目前的 IP 新增一條新規則:

```powershell
netsh interface portproxy show all
netsh interface portproxy delete v4tov4 listenaddress=<old-WSL-Gateway-IP> listenport=13305
netsh interface portproxy add v4tov4 listenaddress=<new-WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

在 `show all` 的輸出中,過期的 Lemonade 規則是連線位址為 `127.0.0.1`、連接埠為 `13305` 的項目;其接聽位址為您的 `<old-WSL-Gateway-IP>`。依該位址刪除僅會移除此規則,並不會影響您機器上的其他連接埠 proxy 規則。

您在設定期間新增的防火牆規則是綁定在連接埠 `13305`(而非 IP)上,因此它會持續正常運作,無需重新建立。

> **建議:** 為了避免閘道問題,我們強烈建議採用以下 shell 設定:
> - **Windows 指令**應在 **PowerShell** 中執行
> - **WSL distro 指令**應在**命令提示字元**中執行(以**系統管理員**身分執行)

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
> 請在您的 **WSL 終端機**中執行此章節的指令。
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

`--no-onboard` 旗標會跳過互動式設定精靈,您將在下一步手動設定模型後端,這能讓您精準掌控使用哪個模型與伺服器。

開啟一個新終端機並確認安裝:

```bash
openclaw --version
```

> **提示:** 若安裝後出現 `command not found`,請將 npm 的全域 bin 目錄加入您的 PATH:
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> 若要永久套用此設定,請將上述這一行加入您的 `~/.bashrc` 或 `~/.zshrc` 檔案。

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


### 設定 OpenClaw 以使用 Lemonade

執行 OpenClaw 的非互動式啟用程序。
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

> **OpenClaw 上下文視窗大小設定:** 當 `contextTokens > contextWindow − reserveTokens` 時,OpenClaw 的壓縮機制就會觸發。預設的 `reserveTokensFloor` 為 20,000 個 token,這是一個下限值,當其低於 `reserveTokens` 時會覆寫它,因此任何低於約 37k 的模型上下文都會觸發無限壓縮迴圈。在您的設定中只需設定一次較低的保留值並停用下限值,即可套用到每個模型,無需針對每個模型個別調整:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` 是一個*下限值*(最小保護值),而非保留值本身,僅設定下限值並不會有任何作用。`reserveTokensFloor: 0` 會停用此保護機制,使較低的 `reserveTokens` 得以生效。
>
> **何時套用此設定:** 若您模型的有效上下文視窗低於約 37k,無論是因為模型本身較小(例如 8k、16k、32k),或是因為您特意將其限制為較低的值(例如載入 128k 模型但在 Lemonade 中將上下文設為 16k),都請使用此設定。若不套用,OpenClaw 在啟動時會進入無限壓縮迴圈。

>
> **全上下文使用的大型上下文模型:** 您可以完全跳過此設定。預設值運作良好,壓縮機制會在視窗填滿前及時啟動,模型也有充足空間可產生長篇回應。若您仍套用此設定,請注意 `reserveTokens: 4096` 會將回應長度限制在約 4k token,這可能會截斷長檔案的產生或詳細計畫的內容。
>
> **此設定應放置的位置:** 請將 `compaction` 區塊放在您 `openclaw.json`(通常位於 `~/.openclaw/openclaw.json`)中的 `agents.defaults` 內:
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
> 其餘設定(gateway、channels、models 等)維持不變,只需新增 `compaction` 鍵即可。
### （建議）啟用 Docker 沙箱化

OpenClaw 可以將所有 agent 檔案與程式碼操作導向一個隔離的 Docker 容器，而非直接在您的主機上執行。這樣可將任何非預期動作的影響範圍限制在沙箱內，讓您的主機檔案系統與網路保持不受影響。

建構一次沙箱映像檔（必須已安裝 Docker）：

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

沙箱容器預設**沒有網路存取**。如需綁定掛載與網路覆寫設定，請參閱[沙箱化參考文件](https://docs.openclaw.ai/gateway/sandboxing)。

> #### 疑難排解：Docker 權限被拒
> 
> 如果在執行 Docker 指令時出現「permission denied」：
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
> **步驟 2：如果錯誤仍然存在，套用永久修正方式**
> 
> ```bash
> sudo chgrp docker /lib/systemd/system/docker.socket
> sudo chmod g+w /lib/systemd/system/docker.socket
> ```
> 
> 然後**重新開機**您的系統。
> 
> **快速暫時修正方式**（重新開機後會重置）：
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
## （建議）OpenClaw 與 Firecrawl 服務的整合

[Firecrawl](https://docs.firecrawl.dev/introduction) 提供一個自架的網頁爬取與內容擷取服務，可以克服這些挑戰，釋放 OpenClaw 自動化的完整潛力。

在此設定中，OpenClaw 以一組由 Podman 管理的 Docker 容器形式執行。為了簡化生命週期管理與自動啟動，我們將 Firecrawl 註冊為使用者層級的 `systemd` 服務，用來協調底層的 Podman Compose 堆疊。這讓 OpenClaw 可以使用標準的 `systemctl --user` 指令來啟動閘道器、停止與驗證 Firecrawl 服務，而不需要直接與容器互動。

為求簡單，我們將整個流程拆分為四個步驟：

---

### 1. 註冊系統服務
前往 systemd 使用者設定目錄：
```bash
cd ~/.config/systemd/user
```
建立並開啟一個名為 `firecrawl.service` 的新檔案。
```bash
nano firecrawl.service
```
複製並貼上以下設定內容：
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
此時，服務已被定義，但尚未向 `systemd` 註冊。
請確認檔案名稱與您上面建立的完全一致，然後執行：
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
如果成功，您應該會看到以下輸出：

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

`default.target.wants/` 包含指向已設定為自動啟動之服務的符號連結。

### 2. 設定 Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) 非常適合需要完全掌控其爬取與資料處理環境的使用者，但代價是需要額外的維護與設定工作。

首先複製（clone）此儲存庫：
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
完成後，下載 OpenClaw Compose 檔案 [openclaw-compose.yaml](assets/openclaw-compose.yaml)，並將其放置在根目錄 `/firecrawl` 中：

> 此慣例是必要的，以便 `systemd` 能依照 `WorkingDirectory=${HOME}/firecrawl` 中的指定正確定位並啟動服務。

> 您隨時可以透過新增其他 Firecrawl 服務來擴充此堆疊。可用服務的完整清單可在官方 [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) 中找到。

### 4. 透過 Firecrawl 啟動 OpenClaw 服務

在將控制權交給 `systemd` 之前，請手動執行此堆疊，以驗證一切運作正常：
```bash
podman compose -f openclaw-compose.yaml up -d
```
如果一切設定正確，您應該會看到 OpenClaw 容器啟動，且您的命令列輸出應類似如下：
<p align="center">
  <img src="assets/openclaw_health_verification.png" width="500" height="400" />
</p>

驗證完成後，請先將堆疊關閉再繼續進行：
```bash
podman compose -f openclaw-compose.yaml down
```
在啟動服務之前，您必須確保 `firecrawl` 目錄及其 `.env` 檔案已設定正確的擁有者與權限。
這對於服務在啟動時能寫入您的憑證是必要的。
```bash
sudo chown ${USER}:${USER} ~/firecrawl/.env
chmod 644 ~/firecrawl/.env
```
現在一切都已驗證完成，請透過 `systemd` 啟動服務：
```bash
systemctl --user start firecrawl.service
```
[OpenClaw Actions](https://docs.openclaw.ai/) 可從互動式容器內存取，且 Web 儀表板可在同一主機與連接埠上於 http://127.0.0.1:18789 使用。
<p align="center">
  <img src="assets/OpenClawWebUI-PodmanLaunch.png" width="500" height="500" />
</p>

### 取得您的 `OPENCLAW_GATEWAY_TOKEN`

服務啟動並執行後，您會注意到您的家目錄中（~/.openclaw）會建立一個新的 `.openclaw` 目錄。此目錄預設是鎖定的，因此您需要先解鎖才能取得您的閘道器權杖。

1. 授予該目錄的存取權限：
```bash
sudo chmod 777 ~/.openclaw/
```
2. 讀取您的閘道器權杖：
```bash
grep '"token"' ~/.openclaw/openclaw.json
```
在輸出中找到 `OPENCLAW_GATEWAY_TOKEN` 的值。

3. 在瀏覽器中開啟閘道器儀表板 http://127.0.0.1:18789。在提示進行身分驗證時貼上您的權杖。

若要停止服務，請執行：
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---
## 啟動 OpenClaw Gateway

Gateway 是負責管理 agent 迴圈並提供儀表板服務的 OpenClaw 處理程序：

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

由於 gateway 綁定在 loopback 上，從同一台機器開啟儀表板時會自動驗證身分，本機存取不需要輸入權杖或裝置核准。你應該會看到 OpenClaw 儀表板，並顯示你的 Lemonade 模型為目前使用的後端。

> 若你已啟用沙箱功能，可以在儀表板中請 agent 執行 `run hostname` 來驗證。若你看到的是一串簡短的容器 ID，而非機器的主機名稱，就代表沙箱運作正常。

**恭喜，你已經從零開始建立了一套完全本機運作的 AI agent 堆疊。**

> **需要 gateway 權杖嗎？** 執行 `openclaw dashboard --no-open` 即可印出帶有嵌入權杖的儀表板網址（同時也會嘗試將其複製到剪貼簿）。另外，權杖也會存放在 `~/.openclaw/openclaw.json` 的 `gateway.auth.token` 中。

**透過 SSH 通道從另一台裝置存取儀表板**

若 OpenClaw 執行在遠端機器上，你可以透過 SSH 通道從本機存取其儀表板。該通道會轉送 gateway 連接埠（`18789`），讓你的本機瀏覽器可以透過 `127.0.0.1` 與遠端 gateway 溝通。

1. 在你的**本機**上，先連線到遠端機器一次並接受指紋提示，讓該主機被加入已知主機清單：

   ```bash
   ssh user@<host-ip>
   ```

2. 同樣在你的**本機**上，開啟 SSH 通道：

   ```bash
   ssh -N -L 18789:127.0.0.1:18789 user@<host-ip>
   ```

   > **注意：** 輸入密碼後，終端機不會顯示任何輸出，看起來像是卡住了。這是正常現象：`-N` 旗標會告訴 SSH 不要執行任何遠端指令，因此它只會持續保持通道開啟。請讓這個終端機持續執行。

3. 在你的**本機**上，開啟瀏覽器並前往 `http://127.0.0.1:18789`。

4. 在**遠端機器**上，印出 gateway 權杖並貼到瀏覽器中以登入：

   ```bash
   openclaw dashboard --no-open
   ```

   這會印出帶有嵌入權杖的儀表板網址；複製該權杖以登入。（權杖也會儲存在 `~/.openclaw/openclaw.json` 的 `gateway.auth.token` 中。）

> **核准遠端裝置：** 當你從另一台機器或手機開啟儀表板時，瀏覽器可能會顯示一組請求 ID。在**遠端機器**上，列出待核准的請求：
> ```bash
> openclaw devices list
> ```
> 接著核准符合的請求：
> ```bash
> openclaw devices approve <requestId>
> ```
> 這僅在遠端或次要裝置存取時才需要；來自同一台機器的 loopback 存取會自動驗證。詳情請參閱 [Remote Access](https://docs.openclaw.ai/gateway/remote) 文件。

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## 選用：連接通訊頻道

Gateway 執行後，你就可以從任何裝置連接你的本機 agent。請依你的設定選擇適合的選項。OpenClaw 支援 [Discord](https://docs.openclaw.ai/channels/discord)、[Telegram](https://docs.openclaw.ai/channels/telegram) 及其他頻道，完整清單請見 [docs.openclaw.ai](https://docs.openclaw.ai)。

---

### 選項 A：Discord

Discord 需要一個**你擁有管理員權限**的伺服器才能新增機器人。若你雖與他人共用伺服器，但本身並非擁有者，請改用選項 B（Telegram）。

#### 建立 Discord 帳號與伺服器

若你尚未擁有 Discord 帳號，請至 [discord.com](https://discord.com) 註冊。你也需要一個你擁有管理員身分的伺服器，點選 Discord 側邊欄的 **+** 圖示並選擇 **Create My Own** 即可建立。使用私人伺服器即可。

#### 建立 Discord 應用程式與機器人

1. 前往 [Discord Developer Portal](https://discord.com/developers/applications) 並點選 **New Application**。為其命名（例如「openclaw-bot」）。
2. 在側邊欄中點選 **Bot**。為機器人設定使用者名稱。
3. 仍在 Bot 頁面中，捲動至 **Privileged Gateway Intents**，並啟用：
   - **Message Content Intent**（必要）
   - **Server Members Intent**（建議）
4. 捲動回上方並點選 **Reset Token** 以產生機器人權杖，並將其複製下來。

#### 將機器人加入你的伺服器

1. 在側邊欄中點選 **OAuth2/ URL Generator**。
2. 在 **Scopes** 下，啟用 `bot` 和 `applications.commands`。
3. 在 **Bot Permissions** 下，啟用：View Channels、Send Messages、Read Message History、Embed Links、Attach Files。
4. 複製產生的網址，貼到瀏覽器中，選擇你的伺服器並確認。機器人應該會出現在你伺服器的成員清單中。

#### 收集你的 ID

在 Discord 中啟用開發者模式（**User Settings/ Advanced/ Developer Mode**），然後：
- 在你的伺服器圖示上按右鍵：**Copy Server ID**
- 在你自己的頭像上按右鍵：**Copy User ID**

#### 允許來自伺服器成員的私訊

在你的伺服器圖示上按右鍵/ **Privacy Settings**/ 開啟 **Direct Messages**。這讓機器人可以私訊你，此為配對步驟所必需。

#### 設定 OpenClaw 以連接 Discord

將你的機器人權杖儲存為環境變數，接著建立單一修補檔案以啟用 Discord、參照該權杖，並將你的伺服器加入允許清單。請將 `<server_id>` 與 `<user_id>` 換成上述收集到的 ID。

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

> **請勿仰賴請 agent 幫你設定此項目。** 當沙箱功能啟用時，agent 無法從沙箱內寫入 `~/.openclaw/openclaw.json`，請改在主機上使用上述 CLI 指令。

重新啟動 gateway，使其套用新的頻道設定：

```bash
openclaw gateway run --bind loopback --port 18789
```

你應該會在幾秒內於 gateway 輸出中看到 `logged in to discord as <bot-name>`。
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

現在您可以直接從 Discord 與您的代理對話，並將任務卸載到您的本機硬體上。

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### 選項 B：Telegram

對大多數使用者來說，Telegram 比 Discord 更簡單，不需要伺服器，也不需要管理員權限。

#### 建立 Telegram 機器人

1. 開啟 Telegram 並傳訊給 **@BotFather**。
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

配對代碼會在一小時後過期。現在您可以透過 Telegram 私訊與您的代理對話了。

---

## 後續步驟

既然您的代理可以從您的手機接收指令，並在您的本機上執行動作，以下有三個值得探索的方向：

1. **股市摘要工具**：安排 OpenClaw 定時從金融 API 擷取資料，使用您的本機模型摘要當天的走勢，並透過您選擇的頻道每天早上推送摘要到您的手機。

2. **微調監控器**：透過 Telegram 或 Discord 遠端啟動訓練工作，然後讓代理追蹤訓練日誌，並定期將損失值、GPU 使用率和磁碟使用量回報到您的手機。如果執行過程卡住或 VRAM 突然飆升，您可以立即得知，而不需要人在機器旁邊。

3. **搭配本機 VLM 的物聯網應用**：將攝影機對準您家門口，在 Lemonade 上執行視覺模型，並讓 OpenClaw 依需求或觸發條件分析畫面。從您的手機詢問「今天有包裹送到嗎？」，即可從您自己的硬體得到明確的答案。

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