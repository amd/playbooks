<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機器翻譯。**本頁面是由英文自動翻譯而成，尚未經過人工審閱。內容可能包含錯誤，且某些指示、命令、下載項目、產品供應情況或其他內容可能因語言或地區而異。如本文件與英文版本之間存在任何不一致或差異，應以該 playbook 之英文原始版本為準。
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Overview

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> 此教學文件需要至少 **32GB** 的系統記憶體。
<!-- @device:end -->

n8n 是一個工作流程自動化平台,讓您可以透過視覺化的節點編輯器來連接應用程式與服務。

本教學文件將教您如何設定一個 AI 驅動的財經新聞摘要工具,該工具會從新聞 RSS 訂閱來源擷取最新的商業頭條新聞,並使用執行於您系統上的本機 LLM 產生以投資人為導向的摘要。

## 您將學到什麼

- 如何安裝並啟動 n8n
- 匯入並設定預先建立的工作流程
- 使用原生 n8n 整合連接到 Lemonade
- 了解工作流程節點與資料流

## 什麼是 Lemonade?

[Lemonade](https://lemonade-server.ai) 是專為 AMD 硬體打造的本機 LLM 伺服平台。它提供與 OpenAI 相容的 API,完全在您的機器上執行—您的資料不會離開您的裝置。

在本教學文件中,我們使用 Lemonade 來提供本機 LLM,供 n8n 連接以執行 AI 驅動的任務。

n8n 內建**原生 Lemonade 節點**(`Lemonade Chat Model`),提供一流的整合體驗——無需手動設定。這使得將您的本機 LLM 連接到自動化工作流程變得非常直接。

<!-- @device:halo_box,halo,stx,krk -->
## 設定記憶體配置

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## 檢查軟體更新

<!-- @require:software-update -->
<!-- @device:end -->

## 安裝軟體先決條件
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @require:lemonade,podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="gpt-oss-20b-mxfp4-GGUF" -->
<!-- @device:end -->


<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade (robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1
if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
  -H "Content-Type: application/json" `
  --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
}
finally {
  Remove-Item  $tmpBody -Force -ErrorAction SilentlyContinue
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
entry = None
for item in data.get("data", []):
    if item.get("id") == "${lemonade_model}":
        entry = item
        break

if entry is None:
    print("Model ${lemonade_model} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: ${lemonade_model} model is downloaded in Lemonade")
PY

body='{
  "model": "${lemonade_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->

## 安裝 n8n
<!-- @os:windows -->
使用 npm 全域安裝 n8n。

> **注意**:您可能會看到一些 npm 警告,這是正常現象。

```bash
npm install -g n8n
```

<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **提示**:Windows 使用者可能需要先修改其 PowerShell 執行原則(例如
> 設定為 RemoteSigned 或 Unrestricted),才能執行某些 Powershell 命令。
<!-- @os:end -->


<!-- @os:windows -->
> **PATH 問題**:如果 `n8n --version` 顯示找不到指令,請確認您的 npm 全域 bin 目錄已加入使用者 `PATH`。通常的安裝路徑為 `C:\Users\<username>\AppData\Roaming\npm`。
> 將此路徑加入使用者路徑中(編輯系統環境變數 > 環境變數 > 編輯使用者路徑),然後重新載入終端機。

<!-- @os:end -->

<!-- @os:linux -->
我們現在要使用 Podman 服務將我們的 n8n 安裝容器化。

請將以下檔案下載至您選擇的目錄:[compose.yml](assets/compose.yml)

在該目錄中,執行以下命令:
```bash
podman compose up -d
```

這應該會安裝 n8n 並寫入持久性儲存空間。

在瀏覽器網址列輸入 `localhost:5678` 以啟動 n8n。
<!-- @os:end -->

<!-- @os:windows -->
## 啟動 n8n

從終端機啟動 n8n:

```bash
n8n start
```

<!-- @test:id=n8n-start-windows timeout=300 hidden=True -->
```powershell
$N8N_CMD = "$env:APPDATA\npm\n8n.cmd"
$p = Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$N8N_CMD`" start" -NoNewWindow -PassThru
try {
  $ok = $false
  for ($i=0; $i -lt 120; $i++) {
    # Check HTTP status code only (body may be empty)
    $code = curl.exe -s -o NUL -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz
    if ($LASTEXITCODE -eq 0 -and $code -eq "200") { $ok = $true; break }
    Start-Sleep -Seconds 1
  }
  if (-not $ok) { throw "n8n not ready on http://127.0.0.1:5678/healthz" }
  Write-Host "OK: n8n server is responding"
} finally {
  # Kill the process actually listening on 5678
  $conn = Get-NetTCPConnection -LocalPort 5678 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($conn) { Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue }
  # Also kill wrapper pid just in case
  if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-start-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

n8n start >/tmp/n8n-test.log 2>&1 &
p=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "n8n not ready on http://127.0.0.1:5678/healthz"
  exit 1
fi

echo "OK: n8n server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
n8n 會啟動一個本機網頁伺服器。按下 `'o'` 鍵或開啟瀏覽器前往 `http://localhost:5678` 以存取編輯器。
<!-- @os:end -->


> **提示**:使用 n8n 時請保持終端機視窗開啟。關閉它可能會停止伺服器。

## 啟動 Lemonade

Lemonade 是將執行模型並連接到 n8n 的本機伺服器。

<!-- @os:linux -->
按一下工作列中的 Lemonade 圖示以開啟 Lemonade GUI。您可以在此瀏覽模型、後端,並載入預先安裝的模型。
<!-- @os:end -->

<!-- @os:windows -->
按一下 Lemonade 圖示以開啟 Lemonade GUI。在系統匣圖示上按一下滑鼠右鍵以開啟應用程式。接著,您可以新增模型、後端,並載入預先安裝的模型。
<!-- @os:end -->

>**提示**:啟動後,Lemonade GUI 也可以透過 http://localhost:13305 存取。

或者,您也可以開啟終端機並執行 `lemonade list` 來查看已安裝的模型。接著執行:

<!-- @device:halo_box -->
<!-- @os:linux -->
```bash
lemonade run gpt-oss-120b-Q4_K_M --llamacpp vulkan
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo -->
```bash
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
```bash
lemonade run gpt-oss-20b-GGUF --llamacpp vulkan
```
<!-- @device:end -->


## 設定工作流程

### 步驟 1:註冊或登入 n8n

當您第一次開啟 n8n 時,系統會提示您建立帳戶或登入:

1. 在瀏覽器中開啟 `http://localhost:5678`
2. 使用您的電子郵件建立新的本機帳戶,如果您已經有帳戶則登入
3. 登入後,您將看到 n8n 儀表板

> **提示**:如果被鎖定在您的帳戶之外,請嘗試 `n8n user-management:reset`

### 步驟 2:匯入工作流程

我們提供了一個預先建立的工作流程,您可以直接匯入:

1. 下載以下工作流程檔案:[financial-news-workflow.json](assets/financial-news-workflow.json)
2. 按一下**從頭開始**以開啟工作流程編輯器。或者,按一下左上角的 + 按鈕,然後選擇**新增工作流程**。
3. 按一下右上方列的 **...** 選單(三個點)並選擇**從檔案匯入**
4. 選擇下載的 `financial-news-workflow.json` 檔案
5. 工作流程將顯示在畫布上
### 步驟 3：了解工作流程

匯入的工作流程包含 8 個相互連接的節點：

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| 節點 | 用途 |
|------|---------|
| **When clicking 'Execute workflow'** | 手動觸發以啟動工作流程 |
| **Fetch Financial News Feed** | RSS Read 節點，會從 RSS 訂閱源中擷取最新的商業新聞標題（預設為 NYT Business 訂閱源，不需要 API 金鑰） |
| **Aggregate Headlines** | Aggregate 節點，會將每個訂閱項目的標題與摘要收集為單一清單 |
| **Clean Extracted News Data** | Set 節點，會將所有標題合併成單一文字欄位 |
| **AI Financial News Summarizer** | AI Agent，使用財經分析師系統提示來處理新聞 |
| **Lemonade Chat Model** | 連線到執行 LLM 的本機 Lemonade 伺服器 |
| **Structured Output Parser** | 將 AI 輸出格式化為結構化 JSON |
| **Convert to File** | 將摘要轉換為可下載的檔案 |

> **提示**：若要使用不同的新聞來源，請雙擊 **Fetch Financial News Feed** 節點，並將網址替換為您偏好的任何商業或市場 RSS 訂閱源。

### 步驟 4：設定 Lemonade 認證

在執行工作流程之前，您需要將其連線到本機 Lemonade 伺服器：

1. 在 n8n 中雙擊 **Lemonade Chat Model** 節點
2. 在下拉式選單 **Credential to connect with** 中選擇 **Create New Credential**
3. 在下表中輸入數值並按一下儲存。
4. 選擇您已在 Lemonade Server 中載入的相關模型。

  | 欄位 | 數值 |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **注意**：測試前，請在終端機中執行 `lemonade status`，以確認 Lemonade 伺服器正在執行中。
<!-- @device:halo_box -->
> 此工作流程使用 GPT-OSS-120B，該模型已預先安裝於 Lemonade 中。您可以在 Lemonade Chat Model 節點設定中將其變更為其他已載入的模型。
<!-- @device:end -->

### 步驟 5：測試工作流程

1. 確認 Lemonade 正在執行且已載入模型
2. 按一下畫布下方中央的 **Execute workflow**
3. 觀察每個節點由左至右依序執行——完成後會轉為綠色
4. 雙擊 **AI Financial News Summarizer** 節點，即可在下方面板中查看產生的摘要。
5. 雙擊 **Convert to File** 節點，即可在下方面板中下載對應的文字檔案。

## 了解 AI Agent

AI Financial News Summarizer 使用專為財經分析設計的系統提示：

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

此代理程式會接收經過清理的新聞資料，並輸出包含市場情緒的結構化摘要。

### 儲存您的工作流程

按一下頂端的工作流程名稱，並依需求重新命名。工作流程會在您操作時自動儲存。

## 後續步驟

- **排程自動化**：將 Manual Trigger 替換為 **Schedule Trigger**，以每日執行
- **傳送通知**：新增 **Discord**、**Slack** 或 **Email** 節點以接收摘要
- **嘗試不同模型**：在 Lemonade Chat Model 節點中變更模型，以試用不同的 LLM
- **變更新聞來源**：將 **Fetch Financial News Feed** 節點指向不同的 RSS 訂閱源，以追蹤其他版面或出版品
- **嘗試不同後端**：n8n 也支援 [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model)、LM Studio 及其他本機 LLM 後端

### 探索 n8n 範本

n8n 提供數百個預先建立的工作流程範本。請瀏覽官方範本庫：

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

搜尋「AI」、「LLM」或「automation」即可找到可匯入並自訂的工作流程。

如需更多資訊，請參閱 [n8n 文件](https://docs.n8n.io/)。

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