<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機器翻譯。**本頁面是由英文自動翻譯而成，尚未經過人工審閱。內容可能包含錯誤，且某些指示、命令、下載項目、產品供應情況或其他內容可能因語言或地區而異。如本文件與英文版本之間存在任何不一致或差異，應以該 playbook 之英文原始版本為準。
<!-- auto-translated-disclaimer:end -->

# 在本機使用 Lemonade Server 執行 Hermes Agent

## 概觀

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) 是由 Nous Research 打造的自我改進型 AI 代理程式。它內建學習迴圈，能從經驗中建立技能，跨工作階段建立關於您的持久記憶,並可代表您執行排程自動化作業。與單純的聊天助理不同,Hermes 會採取實際行動:執行 shell 指令、寫入檔案、瀏覽網頁,以及將平行工作串流委派給子代理程式。

[**Lemonade Server**](https://lemonade-server.ai/) 是驅動它的本機推論後端。這是一個開源伺服器,可直接在您的 AMD 硬體上執行 GenAI 模型,並透過業界標準的 OpenAI API 公開這些模型。

兩者結合形成一套完全本機化的 AI 代理程式堆疊:Lemonade 在您的 GPU 上處理模型推論,而 Hermes 提供代理程式迴圈、記憶、技能與訊息閘道。

> **在您繼續之前:** Hermes Agent 是一個高度自主的 AI 代理程式。讓任何 AI 代理程式存取您的系統,都可能導致不可預測或非預期的結果。請僅在您了解相關風險並能接受自主軟體代表您採取行動的情況下繼續。

---

## 您將學到什麼

完成本操作手冊後,您將能夠:

- **安裝 Hermes Agent** 並將其指向 **Lemonade Server** 作為其 AI 後端。
- **（建議）啟用 Docker/Podman 沙箱**,將代理程式的動作與主機隔離。
- **啟動 Hermes 閘道**並確認您的代理程式已就緒。
- **連接通訊頻道**（Discord 或 Telegram）,讓您能從任何裝置與代理程式聊天。

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
- 執行 **Ubuntu 24.04+** 或相容的 Debian 系 Linux 發行版（具備 `apt-get`）的電腦
- 至少 **12 GB 的 RAM**（建議 64 GB 以上以執行較大型模型）
- **約 10–30 GB 的可用磁碟空間**用於模型權重
- [Podman](https://podman.io/docs/installation)（選用,用於對 Hermes Agent 進行沙箱化）
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @os:windows -->
- 執行 **Windows 10/11** 的電腦
- 至少 **12 GB 的 RAM**（建議 64 GB 以上以執行較大型模型）
- **約 10–30 GB 的可用磁碟空間**用於模型權重
- Podman（選用,用於對 Hermes Agent 進行沙箱化）。請在 WSL 內安裝:
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Halo Box 已預先安裝 Podman,無需任何設定
<!-- @device:end -->

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @require:lemonade -->
<!-- @prereq:hermes,lemonade-models-qwen3-6-35b-a3b,podman,lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## 提取並載入建議的模型

本操作手冊建議使用的模型是來自 Unsloth 的 **Qwen3.6-35B-A3B-GGUF**,這是一個強大的 MoE 模型,具備 263k 權杖的上下文視窗,非常適合代理程式工作負載。此模型使用 UD-Q4_K_XL 量化。現在請提取此模型:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

接著以較大的上下文視窗載入它,並儲存此設定供日後執行使用:

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

此模型的預設上下文長度為 262,144 個權杖。若您遇到記憶體不足（OOM）錯誤,可考慮縮小上下文視窗。

> **提示:停用思考功能以加快代理程式回應速度:** Qwen3.6-35B-A3B 預設以思考模式執行,這會在每次回應前增加延遲。對於代理程式迴圈而言,此額外開銷會迅速累積。[lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) 儲存庫提供了現成的設定檔,可停用思考功能。若要使用它,請下載該檔案並匯入:
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
$entry = $parsed.data | Where-Object { $_.id -eq "${hermes_model}" } | Select-Object -First 1

if (-not $entry) {throw "Model ${hermes_model} is not present in Lemonade /api/v1/models."}
if (-not $entry.downloaded) {throw "Model ${hermes_model} is present but not downloaded in Lemonade. Please download it before running CI."}
Write-Host "OK: ${hermes_model} model is downloaded in Lemonade"

if ($entry.recipe_options.ctx_size -ne 262144) {
  throw "Model ${hermes_model} is not saved with ctx_size=262144. Run: lemonade load ${hermes_model} --ctx-size 262144 --save-options"
}
Write-Host "OK: ${hermes_model} is saved with ctx_size=262144"

$body = @{
  model = "${hermes_model}"
  messages = @(
    @{
      role = "user"
      content = "Reply with exactly: OK"
    }
  )
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "hermes-lemonade-chat-body.json"
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
model_id = "${hermes_model}"

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
  "model": "${hermes_model}",
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

我們會在 WSL 內執行 Hermes Agent,並將其連接至原生執行於 Windows 上的 Lemonade。這讓您能擁有 Hermes 的 Linux shell 環境,同時在 Windows 端保留 Lemonade 的 GPU 加速能力。

### 安裝 WSL 與 Ubuntu

以系統管理員身分開啟 PowerShell,並安裝 WSL 核心:

```powershell
wsl --install --no-distribution
```

接著安裝 Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### 在 WSL 中啟用 systemd

在 Ubuntu 終端機內執行以下指令:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

重新啟動 WSL:

```powershell
wsl --shutdown
wsl
```

### 將 Lemonade 從 Windows 橋接至 WSL

WSL2 在虛擬網路中執行。Windows 上的 Lemonade 繫結至 `127.0.0.1`,而 WSL 無法直接存取此位址。Windows 連接埠代理可將流量從 WSL 閘道 IP 轉發至 Windows 的 localhost。

**尋找您的 WSL 閘道 IP**（在 WSL 內執行）:

```bash
ip route show default | awk '{print $3}' | head -1
```

**新增連接埠代理**（以系統管理員身分在 PowerShell 中執行,並將 `<WSL-Gateway-IP>` 替換為您的 WSL 閘道 IP）:

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**新增防火牆規則**（在同一個提升權限的 PowerShell 中執行）:

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**從 WSL 進行驗證**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

若您已在前一步驟載入了 Qwen3.6-35B-A3B-GGUF 模型,應會看到列出已載入模型的 JSON 輸出。

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

> `netsh portproxy` 規則在重新開機後仍會保留,但 WSL 閘道 IP 可能會在執行 `wsl --shutdown` 之後變更。若重新啟動後 WSL 無法連線至 Lemonade,請取得更新後的閘道 IP,並以此新 IP 更新代理設定。

<!-- @test:id=wsl-lemonade-bridge-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
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

## 安裝 Hermes Agent

<!-- @os:windows -->
> 除非另有說明,請在本節中於您的 **WSL 終端機**內執行這些指令。
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

`--skip-setup` 旗標會跳過互動式設定精靈,讓您能在下一步手動設定模型後端。

重新載入您的 shell:

```bash
source ~/.bashrc
```

確認安裝:

```bash
hermes --version
```

執行自我診斷以檢查所有相依項目:

```bash
hermes doctor
```

> **提示:** 若安裝後看到 `command not found`,請將 Hermes 加入您的 PATH:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> 若要使其永久生效,請將上述這一行加入您的 `~/.bashrc` 或 `~/.zshrc`。

<!-- @os:linux -->
<!-- @test:id=hermes-version-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-version-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
hermes --version
# hermes doctor is a self-diagnostic; run it for the logs but don't gate CI on it (it can probe live model/runtime state that varies on the runner).
hermes doctor || true
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-version-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes version check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---
## 設定 Hermes 以使用 Lemonade

Hermes 會將其模型設定儲存在 `~/.hermes/config.yaml` 中。您可以使用互動式的 `hermes model` 選取器，或是直接撰寫設定檔。

### 選項 1：互動式選取器

<!-- @os:windows -->
> 請在您的 **WSL 終端機** 內執行以下指令。
<!-- @os:end -->

<!-- @os:linux -->
```bash
hermes model
```
<!-- @os:end -->

<!-- @os:windows -->
```bash
hermes model
```
<!-- @os:end -->

出現提示時：

1. 選取 **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **API base URL:** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API base URL:** 使用 WSL 閘道 IP：在 WSL 內執行 `ip route show default | awk '{print $3}' | head -1` 取得該 IP，接著輸入 `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **API key:** `lemonade`
4. **API compatibility mode:** `1` (Auto-detect)
5. **Select model:** 從清單中選取 `Qwen3.6-35B-A3B-GGUF`
6. **Context length in tokens:** `262144`
7. **Display name:** `local-lemonade`（或任何您偏好的名稱）

`hermes model` 會同時儲存目前使用中的模型選擇，以及一筆名為 `custom_providers` 的項目，用來將內容長度與端點一併儲存。`~/.hermes/config.yaml` 中的結果如下所示：

```yaml
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
```

### 選項 2：直接撰寫設定檔

<!-- @os:linux -->

```bash
mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<'EOF'
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://127.0.0.1:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://127.0.0.1:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->

在您的 WSL 終端機內，取得 Windows 主機 IP 並寫入設定檔：

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

mkdir -p ~/.hermes
cat >> ~/.hermes/config.yaml <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF
```

<!-- @test:id=hermes-lemonade-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

WINDOWS_HOST="$(ip route show default | awk '{print $3}' | head -1)"
if [ -z "$WINDOWS_HOST" ]; then
  echo "Could not determine WSL gateway IP"
  exit 1
fi

# Write the model config fresh so the test is idempotent across CI runs.
# (An append would create duplicate YAML keys and later break the gateway test.)
mkdir -p "$HOME/.hermes"
rm -f "$HOME/.hermes/config.yaml"
cat > "$HOME/.hermes/config.yaml" <<EOF
model:
  default: Qwen3.6-35B-A3B-GGUF
  provider: custom
  base_url: http://$WINDOWS_HOST:13305/api/v1
  api_key: lemonade
custom_providers:
  - name: local-lemonade
    base_url: http://$WINDOWS_HOST:13305/api/v1
    api_key: lemonade
    model: Qwen3.6-35B-A3B-GGUF
    models:
      Qwen3.6-35B-A3B-GGUF:
        context_length: 262144
EOF

config="$HOME/.hermes/config.yaml"

grep -q "provider: custom" "$config"
grep -q "Qwen3.6-35B-A3B-GGUF" "$config"
grep -q "13305" "$config"
grep -q "context_length: 262144" "$config"

echo "OK: Hermes config.yaml contains Lemonade model configuration (Windows host)"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-lemonade-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes Lemonade config check failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

---

## （建議）啟用 Podman 沙盒環境

Hermes Agent 可以將所有代理程式的 shell 與檔案操作導向隔離的容器，而不是直接在您的主機上執行。這能將任何非預期動作的影響範圍侷限在沙盒內，使您的主機檔案系統與網路不受影響。

建置一個輕量的沙盒映像檔：

<!-- @os:linux -->
```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

<!-- @test:id=hermes-sandbox-image-linux timeout=1800 hidden=True -->
```bash
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
進入您的 WSL 終端機：

```powershell
wsl -d Ubuntu-24.04
```

接著，建置一個輕量的沙盒映像檔：

```bash
podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

<!-- @test:id=hermes-sandbox-image-windows timeout=1800 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

podman version

podman build -t hermes-sandbox:bookworm-slim - <<'DOCKERFILE'
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

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

echo "OK: Hermes sandbox Podman image is available inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-image-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox image build failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

接著，設定 Hermes 使用 Podman 作為容器執行環境，並設定終端機後端：

```bash
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> ~/.hermes/.env

cat >> ~/.hermes/config.yaml <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF
```

> `terminal.backend` 仍然是 `docker`。
> `HERMES_DOCKER_BINARY` 才是告訴 Hermes 要使用 Podman 作為執行環境而非 Docker 的設定。

<!-- @os:linux -->
<!-- @test:id=hermes-sandbox-config-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

# The sandbox image must exist before Hermes can use it as the terminal backend.
podman image inspect hermes-sandbox:bookworm-slim >/dev/null

# Point Hermes at Podman as the container runtime (idempotent: drop any prior line first).
mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

# Append the terminal backend block (config.yaml is rewritten fresh by the model-config test each run, so this appends exactly once per run).
cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-sandbox-config-windows timeout=120 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config test first."
  exit 1
fi

podman image inspect hermes-sandbox:bookworm-slim >/dev/null

mkdir -p "$HOME/.hermes"
touch "$HOME/.hermes/.env"
grep -v '^HERMES_DOCKER_BINARY=' "$HOME/.hermes/.env" > "$HOME/.hermes/.env.tmp" || true
mv "$HOME/.hermes/.env.tmp" "$HOME/.hermes/.env"
echo "HERMES_DOCKER_BINARY=/usr/bin/podman" >> "$HOME/.hermes/.env"

cat >> "$config" <<'EOF'
terminal:
  backend: docker
  docker_image: hermes-sandbox:bookworm-slim
EOF

grep -q "HERMES_DOCKER_BINARY=/usr/bin/podman" "$HOME/.hermes/.env"
grep -q "backend: docker" "$config"
grep -q "docker_image: hermes-sandbox:bookworm-slim" "$config"

echo "OK: Hermes sandbox (Podman) configuration was written inside WSL"
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-sandbox-config-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"
  if ($LASTEXITCODE -ne 0) { throw "Hermes sandbox config failed inside WSL" }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

Hermes 現在會啟動一個持續執行的沙盒容器，並將所有 `terminal` 與檔案工具呼叫導向該容器。此容器的生命週期與 Hermes 處理程序相同，會在所有工具呼叫間被重複使用，並在 Hermes 結束時銷毀。

> **驗證沙盒是否正常運作：** 啟動 Hermes（`hermes`）並請它 `run hostname`——您應該會看到一串簡短的容器 ID，而不是您機器的主機名稱。您也可以請它 `rm -rf <path-to-a-dummy-file/folder>`：Hermes 會確認刪除動作，但該資料夾仍會留在您的主機上。這是因為該指令是在容器的隔離 `$HOME` 中執行，而非您的主機上。

> **需要更強的隔離？** Hermes 也提供官方的 Docker 映像檔（`nousresearch/hermes-agent`），可將整個代理程式處理程序（包含閘道、工具等全部）運行在容器內。詳細設定方式請參閱 [Hermes Docker 說明文件](https://hermes-agent.nousresearch.com/docs/user-guide/docker)。

---

<!-- @os:linux -->
## （建議）Hermes 與 Firecrawl 服務的整合

Hermes 可以使用其內建的網頁工具來瀏覽並擷取網站內容。然而，許多現代網站都採用了機器人偵測系統，這類系統會封鎖簡單的 HTTP 請求，並回傳驗證頁面而非實際內容。因此，Hermes 可能無法可靠地從這些網站擷取資訊。

為克服此限制，[Firecrawl](https://docs.firecrawl.dev/introduction) 提供了一套可自行架設的網頁爬取與內容擷取服務，能夠繞過這些驗證機制，充分發揮 Hermes 自動化的潛力。

在此設定中，Firecrawl 以一組由 Podman 管理的 Docker 容器形式執行。為了簡化生命週期管理與自動啟動，我們將 Firecrawl 註冊為使用者層級的 `systemd` 服務，用以協調底層的 Podman Compose 堆疊。如此一來，Hermes 便可使用標準的 `systemctl --user` 指令來啟動、停止及驗證 Firecrawl 服務，而無需直接與容器互動。

為了簡化整個流程，我們將其拆分為四個步驟：

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
Description=Firecrawl
After=podman.service
Requires=podman.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${HOME}/firecrawl

# Optional: Validate config before starting
ExecStartPre=/usr/bin/podman -f hermes-compose.yaml config --quiet

# Start containers in detached mode
ExecStart=/usr/bin/podman compose -f hermes-compose.yaml up -d --remove-orphans

# Stop containers when the service stops
ExecStop=/usr/bin/podman compose -f hermes-compose.yaml down

[Install]
WantedBy=default.target

```
此時，服務已經定義完成，但尚未向 `systemd` 註冊。
請確認檔名與您上方建立的檔名完全一致，接著執行：
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
若成功，您應該會看到以下輸出：

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

`default.target.wants/` 包含了指向已設定為自動啟動之服務的符號連結。

### 2. 為您的服務設定 Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) 非常適合需要完全掌控其爬取與資料處理環境的使用者，但代價是需要投入額外的維護與設定作業。

首先複製（clone）儲存庫：
```bash
git clone https://github.com/firecrawl/firecrawl.git
```
在根目錄 `/firecrawl` 中建立 `.env`：
```bash
# ===== Required ENVS ======
PORT=3002
HOST=0.0.0.0

# ===== Firecrawl =====
# FIRECRAWL_API_KEY=""

# ===== Proxy =====
# PROXY_SERVER can be a full URL (e.g. http://0.1.2.3:1234) or just an IP and port combo (e.g. 0.1.2.3:1234)
# Do not uncomment PROXY_USERNAME and PROXY_PASSWORD if your proxy is unauthenticated
# PROXY_SERVER=
# PROXY_USERNAME=
# PROXY_PASSWORD=

# This key lets you access the queue admin panel. Change this if your deployment is publicly accessible.
BULL_AUTH_KEY=CHANGEME

# ===== System Resource Configuration =====
# Maximum CPU usage threshold (0.0-1.0). Worker will reject new jobs when CPU usage exceeds this value.
# Default: 0.8 (80%)
# MAX_CPU=0.8

# Maximum RAM usage threshold (0.0-1.0). Worker will reject new jobs when memory usage exceeds this value.
# Default: 0.8 (80%)
# MAX_RAM=0.8
```
> 請將 `BULL_AUTH_KEY` 設定為一組高強度的密鑰，尤其是在任何可從不受信任網路存取的部署環境中。
### 3. 透過 Compose 部署 Hermes

在繼續之前，請確認您已經拉取最新的 Hermes Docker 映像檔：
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
完成後，下載 Hermes Compose 檔案 [hermes-compose.yaml](assets/hermes-compose.yaml) 並將其放置在根目錄 `/firecrawl` 中：

> 這個慣例是必要的，因為 `systemd` 需要依照 `WorkingDirectory=${HOME}/firecrawl` 中的指定來找到並啟動服務。

> 您隨時可以透過新增其他 Firecrawl 服務來擴充此堆疊。完整的可用服務清單可在官方 [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) 中找到。

### 4. 透過 Firecrawl 啟動 Hermes 服務 

在將控制權交給 `systemd` 之前，先手動執行此堆疊以驗證一切運作正常：
```bash
podman compose -f hermes-compose.yaml up -d
```
如果一切設定正確，您應該會看到 Hermes 容器啟動，且命令列輸出應類似如下：
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

驗證完成後，在繼續之前先將堆疊關閉：
```bash
podman compose -f hermes-compose.yaml down
```
現在一切都已驗證完畢，透過 `systemd` 啟動服務：
```bash
systemctl --user start firecrawl.service
```
[Hermes API](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) 可從互動式容器內存取，而 Web 儀表板則可在相同的主機和連接埠上以 http://127.0.0.1:9119 存取。
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

若要停止服務，請執行：
```bash
systemctl --user stop firecrawl.service
```
<!-- @os:end -->
---

## Hermes Native

直接啟動互動式 CLI 工作階段： 

```bash
hermes
```

<!-- @os:linux -->
<!-- @test:id=hermes-gateway-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started successfully"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=hermes-gateway-windows timeout=300 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

$script = @'
set -euo pipefail

export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

config="$HOME/.hermes/config.yaml"
if [ ! -f "$config" ]; then
  echo "Missing $config. Run the Hermes config step first."
  exit 1
fi

log="/tmp/hermes-gateway-ci.log"

cleanup() {
  if [ -n "${gateway_pid:-}" ] && kill -0 "$gateway_pid" 2>/dev/null; then
    kill "$gateway_pid" 2>/dev/null || true
    sleep 2
    kill -9 "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

rm -f "$log"

hermes gateway run >"$log" 2>&1 &
gateway_pid=$!

# `hermes gateway run` is a long-running message bridge + cron scheduler with no
# HTTP health endpoint, so we detect a successful boot by (1) a known startup
# marker appearing in the log and (2) the process still being alive afterwards
# (i.e. it parsed config.yaml and did not crash). "No messaging platforms
# enabled" is expected in CI (no channel token) and is not a failure.
ok=false
for i in $(seq 1 60); do
  if grep -qE "Hermes Gateway Starting|gateway\.run|cron scheduler" "$log" 2>/dev/null; then
    ok=true
    break
  fi
  if ! kill -0 "$gateway_pid" 2>/dev/null; then
    echo "Hermes gateway process exited before it finished starting"
    break
  fi
  sleep 1
done

# Give it a moment to surface any immediate post-banner crash, then confirm it is still running.
sleep 3

if [ "$ok" = "true" ] && kill -0 "$gateway_pid" 2>/dev/null; then
  echo "OK: Hermes gateway started inside WSL"
else
  echo "Hermes gateway did not start"
  echo "---- Gateway log ----"
  cat "$log" || true
  exit 1
fi
'@

$script = $script -replace "`r`n", "`n"

$tmp = Join-Path $env:TEMP "hermes-gateway-windows.sh"
[System.IO.File]::WriteAllText($tmp, $script, [System.Text.UTF8Encoding]::new($false))

try {
  $full = [System.IO.Path]::GetFullPath($tmp)
  $drive = $full.Substring(0,1).ToLower()
  $rest = $full.Substring(2).Replace('\','/')
  $wslTmp = "/mnt/$drive$rest"

  wsl -d Ubuntu-24.04 -- bash "$wslTmp"

  if ($LASTEXITCODE -ne 0) {
    throw "Hermes gateway test failed inside WSL"
  }
}
finally {
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->

**恭喜，您已成功建立一套完全本地化的 AI 代理堆疊。**

### Web 儀表板

Hermes 包含一個基於瀏覽器的使用者介面，可用來管理設定、API 金鑰、模型、工作階段、記憶體和排程工作。在閘道或 CLI 執行時開啟第二個終端機，並使用以下指令啟動：

```bash
hermes dashboard
```

這會啟動一個本地伺服器，並在您的瀏覽器中開啟 `http://127.0.0.1:9119`。完整功能說明請參閱[儀表板文件](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard)。
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## 選用：連接通訊頻道

一旦閘道開始運作，您就可以從任何裝置連線到您的本地代理。Hermes 支援 [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord)、[Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) 以及其他平台

---

### Discord

Discord 需要一個**您擁有管理員權限**的伺服器，才能新增機器人。如果您與他人共用伺服器但並非擁有者，請改用 Telegram。

#### 建立 Discord 應用程式和機器人

1. 前往 [Discord Developer Portal](https://discord.com/developers/applications) 並點選 **New Application**。為其命名（例如「hermes-bot」）。
2. 在側邊欄中，點選 **Bot**。為機器人設定使用者名稱。
3. 仍在 Bot 頁面上，捲動到 **Privileged Gateway Intents** 並啟用：
   - **Message Content Intent**（必要）
   - **Server Members Intent**（建議）
4. 捲動回上方並點選 **Reset Token** 以產生您的機器人權杖。複製它。

#### 將機器人加入您的伺服器

1. 在側邊欄中，點選 **OAuth2 / URL Generator**。
2. 在 **Scopes** 下，啟用 `bot` 和 `applications.commands`。
3. 在 **Bot Permissions** 下，啟用：View Channels、Send Messages、Read Message History、Embed Links、Attach Files。
4. 複製產生的 URL，將其貼到瀏覽器中，選擇您的伺服器並確認。

#### 收集您的 ID 並允許私訊

在 Discord 中啟用開發者模式（**User Settings / Advanced / Developer Mode**），然後：
- 在您的伺服器圖示上按右鍵：**Copy Server ID**
- 在您自己的頭像上按右鍵：**Copy User ID**

在您的伺服器圖示上按右鍵 / **Privacy Settings** / 開啟 **Direct Messages**。此步驟是配對流程所必需的。

#### 為 Discord 設定 Hermes

將以下內容新增至 `~/.hermes/.env`：

```bash
# Required
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=your-discord-user-id
```

然後啟動閘道：

```bash
hermes gateway
```

機器人應該會在幾秒鐘內於 Discord 上線。傳送訊息給它，無論是私訊還是在它能看到的頻道中皆可。

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### 建立 Telegram 機器人

1. 開啟 Telegram 並傳送訊息給 **@BotFather**。
2. 傳送 `/newbot` 並依照提示操作。儲存它提供給您的機器人權杖。

#### 為 Telegram 設定 Hermes

將以下內容新增至 `~/.hermes/.env`：

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **不知道您的 Telegram 使用者 ID？** 在 Telegram 中傳送訊息給 [@userinfobot](https://t.me/userinfobot)，它會回覆您的數字 ID。

然後啟動閘道：

```bash
hermes gateway
```

在 Telegram 中傳送任何訊息給您的機器人以進行測試。現在您可以透過 Telegram 私訊與您的代理聊天。完整的 webhook 模式及進階選項，請參閱[完整的 Telegram 設定指南](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram)。

---

## 後續步驟

現在您的代理可以從您的手機接收指令並在您的本地機器上執行動作，以下是三個值得探索的方向：

1. **自動化研究摘要**：排程 Hermes 在每天早上為您關心的主題搜尋網路資訊，使用您的本地模型彙整發現的結果，並透過 Telegram 或 Discord 將摘要推送到您的手機，整個過程都在您自己的硬體上運行，無需任何雲端成本。

2. **隨選程式碼審查**：讓 Hermes 指向一個 GitHub 儲存庫，要求它審查開啟中的拉取請求，並讓它將評論或摘要回覆到您的聊天中。透過 Docker 終端機後端，所有 git 操作都在沙盒中執行，保持您的主機環境乾淨整潔。

3. **本地檔案助理**：授予 Hermes 存取工作目錄的權限，並要求它從您的手機隨選整理、重新命名、摘要或轉換檔案。由於 Docker 終端機後端將所有寫入操作限制在沙盒工作區內，意外的破壞性操作得以被控制在範圍內。