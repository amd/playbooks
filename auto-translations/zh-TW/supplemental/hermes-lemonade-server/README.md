<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機器翻譯。**本頁面是由英文自動翻譯而成，尚未經過人工審閱。內容可能包含錯誤，且某些指示、命令、下載項目、產品供應情況或其他內容可能因語言或地區而異。如本文件與英文版本之間存在任何不一致或差異，應以該 playbook 之英文原始版本為準。
<!-- auto-translated-disclaimer:end -->

# 在本地使用 Lemonade Server 執行 Hermes Agent

## 概觀

[**Hermes Agent**](https://hermes-agent.nousresearch.com/) 是由 Nous Research 打造的自我改進 AI 代理。它具備內建的學習迴圈，能從經驗中建立技能，跨工作階段建立關於您的持久記憶，並可代替您執行排程自動化。與單純的聊天助理不同，Hermes 會採取實際行動：執行 shell 指令、寫入檔案、瀏覽網頁，並將平行工作流程委派給子代理。

[**Lemonade Server**](https://lemonade-server.ai/) 是驅動這一切的本地推論後端。它是一個開源伺服器，能直接在您的 AMD 硬體上執行 GenAI 模型，並透過業界標準的 OpenAI API 對外提供服務。

兩者結合形成一個完全本地化的 AI 代理堆疊：Lemonade 在您的 GPU 上處理模型推論，Hermes 則提供代理迴圈、記憶、技能與訊息閘道。

> **在您繼續之前：** Hermes Agent 是一個高度自主的 AI 代理。授予任何 AI 代理存取您系統的權限，可能導致不可預測或非預期的結果。請僅在您了解相關風險並能接受自主軟體代表您行事的情況下繼續操作。

---

## 您將學到什麼

完成本指南後，您將能夠：

- **安裝 Hermes Agent** 並將其指向 **Lemonade Server** 作為 AI 後端。
- **（建議）啟用 Docker/Podman 沙盒**，將代理的動作與您的主機隔離。
- **啟動 Hermes 閘道**並確認您的代理已就緒。
- **連接通訊管道**（Discord 或 Telegram），讓您可以從任何裝置與您的代理聊天。

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
- 一台執行 **Ubuntu 24.04+** 或相容的 Debian 基礎 Linux 發行版（具備 `apt-get`）的電腦
- 至少 **12 GB 的 RAM**（若使用較大型模型，建議 64 GB 以上）
- 用於模型權重的 **約 10–30 GB 可用磁碟空間**
- [Podman](https://podman.io/docs/installation)（選用，用於為 Hermes Agent 建立沙盒）
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @os:windows -->
- 一台執行 **Windows 10/11** 的電腦
- 至少 **12 GB 的 RAM**（若使用較大型模型，建議 64 GB 以上）
- 用於模型權重的 **約 10–30 GB 可用磁碟空間**
- Podman（選用，用於為 Hermes Agent 建立沙盒）。請在 WSL 內安裝：
  ```bash 
  sudo apt-get install -y podman
  ```
<!-- @os:end -->

<!-- @device:halo_box -->
> Podman 已預先安裝於 Halo Box，無需額外設定
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @var:id=hermes_model value="Qwen3.6-35B-A3B-GGUF" -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

---

## 拉取並載入推薦模型

本指南推薦使用的模型是來自 Unsloth 的 **Qwen3.6-35B-A3B-GGUF**，這是一款強大的 MoE 模型，具備 263k token 的上下文視窗，非常適合代理工作負載。此模型使用 UD-Q4_K_XL 量化。現在請拉取它：

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

接著以較大的上下文視窗載入它，並儲存此設定以供日後執行使用：

<!-- @require:lemonade-ready -->
<!-- @test:id=lemonade-model-load timeout=900 -->
```bash
lemonade unload
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 262144 --save-options
```
<!-- @test:end -->

此模型的預設上下文長度為 262,144 個 token。若您遇到記憶體不足（OOM）錯誤，請考慮縮小上下文視窗。

> **提示：停用思考模式以加快代理回應速度：** Qwen3.6-35B-A3B 預設以思考模式執行，這會在每次回應前增加延遲。對於代理迴圈而言，這樣的額外開銷會迅速累積。[lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) 儲存庫提供了一個現成的設定檔，可停用思考模式。若要使用它，請下載該檔案並匯入：
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

我們在 WSL 內執行 Hermes Agent，並將其連接到在 Windows 上原生執行的 Lemonade。這讓您能在 Windows 端保留 Lemonade 的 GPU 加速功能的同時，為 Hermes 提供 Linux shell 環境。

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

請在 Ubuntu 終端機內執行：

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

WSL2 執行於虛擬網路中。Windows 上的 Lemonade 綁定至 `127.0.0.1`，而 WSL 無法直接連接到此位址。Windows 連接埠代理可將流量從 WSL 閘道 IP 轉發至 Windows localhost。

**尋找您的 WSL 閘道 IP**（在 WSL 內執行）：

```bash
ip route show default | awk '{print $3}' | head -1
```

**新增連接埠代理**（以系統管理員身分於 PowerShell 中執行，並將 `<WSL-Gateway-IP>` 替換為您的 WSL 閘道 IP）：

```powershell
netsh interface portproxy add v4tov4 listenaddress=<WSL-Gateway-IP> listenport=13305 connectaddress=127.0.0.1 connectport=13305
```

**新增防火牆規則**（於同一個提升權限的 PowerShell 中）：

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**從 WSL 驗證**：

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

若您已於上一步驟載入 Qwen3.6-35B-A3B-GGUF 模型，您應該會看到列出已載入模型的 JSON 輸出。

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

> `netsh portproxy` 規則在重新啟動後仍會保留，但 WSL 閘道 IP 可能在執行 `wsl --shutdown` 後改變。若重新啟動後 WSL 無法連接到 Lemonade，請取得更新後的閘道 IP，並以此新 IP 更新代理設定。

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
> 除非另有說明，否則本節中的指令請於您的 **WSL 終端機**內執行。
<!-- @os:end -->

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

`--skip-setup` 旗標會跳過互動式設定精靈，讓您可以在下一步中手動設定模型後端。

重新載入您的 shell：

```bash
source ~/.bashrc
```

確認安裝：

```bash
hermes --version
```

執行自我診斷以檢查所有相依項目：

```bash
hermes doctor
```

> **提示：** 若您在安裝後看到 `command not found`，請將 Hermes 新增至您的 PATH：
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> 若要使此設定永久生效，請將上述行加入您的 `~/.bashrc` 或 `~/.zshrc` 檔案中。

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
## 設定 Hermes 使用 Lemonade

Hermes 會將其模型設定儲存在 `~/.hermes/config.yaml` 中。您可以使用互動式的 `hermes model` 選擇工具，或直接編寫設定檔。

### 選項 1：互動式選擇工具

<!-- @os:windows -->
> 請在您的 **WSL 終端機** 中執行以下指令。
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

系統提示時：

1. 選擇 **Custom endpoint (enter URL manually)**
<!-- @os:linux -->
2. **API 基底 URL：** `http://127.0.0.1:13305/api/v1`
<!-- @os:end -->
<!-- @os:windows -->
2. **API 基底 URL：** 使用 WSL 閘道器 IP：在 WSL 內執行 `ip route show default | awk '{print $3}' | head -1` 取得該 IP，然後輸入 `http://<WSL-Gateway-IP>:13305/api/v1`
<!-- @os:end -->
3. **API 金鑰：** `lemonade`
4. **API 相容模式：** `1`（自動偵測）
5. **選擇模型：** 從清單中選擇 `Qwen3.6-35B-A3B-GGUF`
6. **情境長度（權杖數）：** `262144`
7. **顯示名稱：** `local-lemonade`（或您偏好的任何名稱）

`hermes model` 會同時儲存目前使用中的模型選擇，以及一個名為 `custom_providers` 的項目，該項目會將情境長度與端點一併儲存。最終在 `~/.hermes/config.yaml` 中的結果如下所示：

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

### 選項 2：直接編寫設定檔

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

在您的 WSL 終端機中，取得 Windows 主機的 IP 並編寫設定檔：

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

## （建議）啟用 Podman 沙盒功能

Hermes Agent 可以將所有代理程式的 shell 與檔案操作透過隔離的容器來執行，而不是直接在主機上執行。這能將任何非預期動作的影響範圍限制在沙盒內，讓您的主機檔案系統與網路不受影響。

建置一個輕量級的沙盒映像檔：

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

接著，建置一個輕量級的沙盒映像檔：

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
> `HERMES_DOCKER_BINARY` 才是告訴 Hermes 改用 Podman 作為執行環境的設定。

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

現在 Hermes 會啟動一個持久性的沙盒容器，並將所有 `terminal` 與檔案工具的呼叫透過該容器進行。此容器的生命週期與 Hermes 行程一致，會在所有工具呼叫之間重複使用，並在 Hermes 結束時銷毀。

> **驗證沙盒是否正常運作：** 啟動 Hermes（`hermes`）並要求它 `run hostname` - 您應該會看到一個簡短的容器 ID，而不是您機器的主機名稱。您也可以要求它 `rm -rf <path-to-a-dummy-file/folder>`：Hermes 會確認刪除動作，但該資料夾實際上仍會保留在您的主機上。這個指令是在容器隔離的 `$HOME` 中執行，而不是您自己的主機環境。

> **需要更強的隔離性嗎？** Hermes 也提供了官方 Docker 映像檔（`nousresearch/hermes-agent`），可在容器內執行整個代理程式行程 - 包含閘道器、工具及所有元件。詳細設定方式請參閱 [Hermes Docker 文件](https://hermes-agent.nousresearch.com/docs/user-guide/docker)。

---

<!-- @os:linux -->
## （建議）Hermes 與 Firecrawl 服務整合

Hermes 可以使用其內建的網頁工具瀏覽並擷取網站內容。然而，許多現代網站使用機器人偵測系統，會封鎖簡單的 HTTP 請求，並回傳驗證挑戰頁面而非實際內容。因此，Hermes 可能無法可靠地從這些網站擷取資訊。

為了克服此限制，[Firecrawl](https://docs.firecrawl.dev/introduction) 提供了一個可自行架設的網頁爬取與內容擷取服務，能夠繞過這些挑戰，充分發揮 Hermes 自動化的潛力。

在此設定中，Firecrawl 是以一組由 Podman 管理的 Docker 容器方式執行。為了簡化生命週期管理與自動啟動，我們將 Firecrawl 註冊為使用者層級的 `systemd` 服務，用來協調底層的 Podman Compose 堆疊。這使得 Hermes 可以使用標準的 `systemctl --user` 指令來啟動、停止與驗證 Firecrawl 服務，而不需直接與容器互動。

為了簡化流程，我們將整個過程拆解為四個步驟：

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
複製並貼上以下設定：
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
此時，服務已定義完成，但尚未向 `systemd` 註冊。
請確認檔案名稱與您上面建立的完全一致，然後執行：
```bash
systemctl --user daemon-reload
systemctl --user enable firecrawl.service
```
如果成功，您應該會看到以下輸出：

> **Created symlink '\~/.config/systemd/user/default.target.wants/firecrawl.service' → '\~/.config/systemd/user/firecrawl.service'.**

 `default.target.wants/` 包含指向設定為自動啟動之服務的符號連結。

### 2. 為您的服務設定 Firecrawl

[SELF-HOST Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) 非常適合需要完全掌控其爬取與資料處理環境的使用者，但代價是需要額外的維護與設定工作。

首先複製（clone）此儲存庫：
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
> 請將 `BULL_AUTH_KEY` 設定為強度較高的密鑰，特別是在任何可從不受信任網路存取的部署環境中。
### 3. 透過 Compose 部署 Hermes

在繼續之前，請確認您已拉取最新的 Hermes Docker 映像檔：
```bash
podman pull docker.io/nousresearch/hermes-agent:latest
```
完成後，下載 Hermes Compose 檔案 [hermes-compose.yaml](assets/hermes-compose.yaml) 並將其放置於根目錄 `/firecrawl` 中：

> 這項慣例是必要的，這樣 `systemd` 才能依照 `WorkingDirectory=${HOME}/firecrawl` 中指定的位置找到並啟動服務。

> 您可以隨時透過新增其他 Firecrawl 服務來擴充此堆疊。完整的可用服務清單可在官方 [Firecrawl docker-compose.yaml](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml) 中找到。

### 4. 透過 Firecrawl 啟動 Hermes 服務

在將控制權交給 `systemd` 之前，請先手動執行此堆疊以確認一切運作正常：
```bash
podman compose -f hermes-compose.yaml up -d
```
如果一切設定正確，您應該會看到 Hermes 容器啟動，且您的命令列輸出應該類似以下內容：
<p align="center">
  <img src="assets/podman_health_verification.png" width="500" height="400" />
</p>

確認無誤後，在繼續之前先將堆疊關閉：
```bash
podman compose -f hermes-compose.yaml down
```
現在一切都已驗證完畢，透過 `systemd` 啟動此服務：
```bash
systemctl --user start firecrawl.service
```
[Hermes API](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server/#endpoints) 可從互動式容器內存取，而 Web 儀表板則可在相同主機及連接埠 http://127.0.0.1:9119 上使用。
<p align="center">
  <img src="assets/System_Service_launch.png" width="500" height="500" />
</p>

若要停止此服務，請執行：
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

**恭喜，您已建置完成一套完全在地端運作的 AI 代理堆疊。**

### Web 儀表板

Hermes 內建一個以瀏覽器為基礎的使用者介面，用於管理設定、API 金鑰、模型、工作階段、記憶體以及排程任務。在閘道或 CLI 執行時開啟第二個終端機，並使用以下指令啟動它：

```bash
hermes dashboard
```

這會啟動一個本機伺服器並在您的瀏覽器中開啟 `http://127.0.0.1:9119`。完整功能參考請參閱[儀表板文件](https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard)。
<p align="center">
  <img src="assets/hermes_dashboard.jpg" width="500" height="300" />
</p>

---

## 選用：連接通訊管道

閘道啟動後，您便可從任何裝置存取您的本機代理。Hermes 支援 [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord)、[Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram) 及其他服務

---

### Discord

Discord 需要一個**您擁有管理員權限**的伺服器，才能新增機器人。如果您與他人共用伺服器但並非擁有者，請改用 Telegram。

#### 建立 Discord 應用程式與機器人

1. 前往 [Discord 開發人員入口網站](https://discord.com/developers/applications) 並點選 **New Application**。為其命名（例如「hermes-bot」）。
2. 在側邊欄中，點選 **Bot**。為機器人設定使用者名稱。
3. 仍在 Bot 頁面上，捲動至 **Privileged Gateway Intents** 並啟用：
   - **Message Content Intent**（必要）
   - **Server Members Intent**（建議）
4. 向上捲動並點選 **Reset Token** 以產生您的機器人權杖。將其複製下來。

#### 將機器人加入您的伺服器

1. 在側邊欄中，點選 **OAuth2 / URL Generator**。
2. 在 **Scopes** 底下，啟用 `bot` 與 `applications.commands`。
3. 在 **Bot Permissions** 底下，啟用：View Channels、Send Messages、Read Message History、Embed Links、Attach Files。
4. 複製產生的網址，將其貼到瀏覽器中，選擇您的伺服器並確認。

#### 收集您的 ID 並允許私訊

在 Discord 中啟用開發人員模式（**User Settings / Advanced / Developer Mode**），然後：
- 右鍵點選您的伺服器圖示：**Copy Server ID**
- 右鍵點選您自己的頭像：**Copy User ID**

右鍵點選您的伺服器圖示 / **Privacy Settings** / 開啟 **Direct Messages** 切換開關。此步驟為配對步驟所必需。

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

機器人應該會在幾秒鐘內於 Discord 上線。傳送一則訊息給它，可以是私訊，也可以是它能看見的頻道中的訊息。

<p align="center">
  <img src="assets/discord_bot.png" width="400" height="300" />
</p>


---

### Telegram

#### 建立 Telegram 機器人

1. 開啟 Telegram 並傳訊給 **@BotFather**。
2. 傳送 `/newbot` 並依照提示操作。儲存它提供給您的機器人權杖。

#### 為 Telegram 設定 Hermes

將以下內容新增至 `~/.hermes/.env`：

```bash
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ALLOWED_USERS=your-telegram-user-id   # comma-separated for multiple users
```

> **不知道您的 Telegram 使用者 ID？** 在 Telegram 中傳訊給 [@userinfobot](https://t.me/userinfobot)，它會回覆您的數字 ID。

然後啟動閘道：

```bash
hermes gateway
```

在 Telegram 中傳送任何訊息給您的機器人以進行測試。您現在可以透過 Telegram 私訊與您的代理聊天。有關 webhook 模式及進階選項，請參閱[完整的 Telegram 設定指南](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram)。

---

## 後續步驟

現在您的代理可以從手機接收指令並在您的本機端執行操作，以下是值得探索的三個方向：

1. **自動化研究摘要**：排程 Hermes 在每天早上搜尋您關心的主題，使用您的本機模型彙整搜尋結果，並透過 Telegram 或 Discord 將摘要推送到您的手機，整個過程完全在您自己的硬體上運作，沒有任何雲端成本。

2. **隨需程式碼審查**：讓 Hermes 指向一個 GitHub 儲存庫，要求它審查開啟中的拉取請求，並讓它將評論或摘要回覆到您的聊天室。透過 Docker 終端機後端，所有 git 操作都在沙盒內執行，讓您的主機保持乾淨。

3. **本機檔案助理**：授予 Hermes 存取工作目錄的權限，並要求它依照您的需求，從手機隨需整理、重新命名、彙整或轉換檔案。由於 Docker 終端機後端會將所有寫入操作限制在沙盒工作空間內，因此意外的破壞性操作能受到控制。