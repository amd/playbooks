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

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> 此手冊至少需要 **32GB** 的系統記憶體。
<!-- @device:end -->

## 概覽

編碼代理（Coding agents）是強大的工具，透過與由大型語言模型（LLM）支援的 AI 代理協作，賦予開發人員更多能力。它們可以嵌入開發環境中，例如終端機或 VS Code，讓開發人員的工作流程能無縫整合。

本教學展示如何使用 Cline、VS Code 與 LM Studio，完全在本機執行編碼代理。

## 您將學到什麼

* 如何搭配使用 VS Code 與 Cline 編碼代理，協助軟體工程任務。
* 如何配置 Cline 與 LM Studio 通訊，以進行編碼代理的本機推論。
* 如何使用本機編碼代理解決實際的軟體工程問題。

## 設定記憶體配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 檢查軟體更新
> **注意**：若尚未安裝 VS Code，您可以透過 Ryzen AI Developer Center 進行安裝。

<!-- @require:software-update -->
<!-- @device:end -->

## 安裝軟體先決條件

<!-- @require:lmstudio,vscode -->

## 啟動並配置 LM Studio

我們將使用 LM Studio 來提供支援編碼代理的 LLM。

- 在搜尋列中搜尋 `LM Studio` 並啟動應用程式，您將會看到以下畫面。

![LM Studio 初始畫面](assets/initial-lm-studio.png)

接下來，我們必須在系統上載入 LLM。我們將使用具有大型上下文長度的 `Qwen3-Coder-30B-A3B` 模型。（若尚未安裝，請使用 Model 頁籤進行安裝）。
- 按一下 LM Studio 視窗頂部的搜尋列，或按下 `CTRL+L`。按一下切換選項 `Manually choose model load parameters`，然後按一下 Qwen3-Coder-30B-A3B 模型。
- 將上下文長度從 `4096` 變更為 `32768`，並確保 `GPU Offload` 已設為最大值。接著按一下 `Load Model`

![選擇模型](assets/model-list-zoomed.png)

我們使用較大的上下文長度，讓代理能夠處理大型程式碼庫並記住已進行的變更。

![配置模型](assets/selecting-model-zoomed.png)

接下來，我們需要啟用 LM Studio Server。
- 按一下 LM Studio 左側的 Developer 頁籤，或按下 `CTRL+2`。
- 勾選狀態切換開關，並確保其設定為 `Running`。

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-up-windows timeout=120 hidden=True -->
```powershell
lms server start --port 1234
curl.exe -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-up-linux timeout=120 hidden=True -->
```bash
lms server start --port 1234
curl -s http://127.0.0.1:1234/v1/models
```
<!-- @test:end -->
<!-- @os:end -->

![伺服器狀態](assets/lm-studio-server-status.png)

<!-- @os:windows -->
<!-- @test:id=lmstudio-select-gpu-runtime-windows timeout=120 hidden=True -->
```powershell
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
$rt = ((lms runtime ls) -match 'vulkan' | Select-Object -First 1)
if ($rt) {
  lms runtime select (($rt.Trim() -split '\s+')[0])
  lms runtime ls | Select-String 'ENGINE|✓'
} else {
  Write-Output "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
if ($LASTEXITCODE -ne 0) { lms unload --all; Start-Sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y }
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-select-gpu-runtime-linux timeout=120 hidden=True -->
```bash
# CI: pin a GPU (Vulkan) runtime so tests don't fall back to the CPU engine.
lms runtime ls
GPU_RT="$(lms runtime ls 2>/dev/null | awk '/vulkan/{print $1; exit}')"
if [ -n "$GPU_RT" ]; then
  lms runtime select "$GPU_RT"
  lms runtime ls | grep -E 'ENGINE|✓'
else
  echo "WARNING: no Vulkan runtime installed; GPU acceleration unavailable. Install with: lms get <vulkan-runtime>"
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-load-qwen3-coder-linux timeout=1200 hidden=True -->
```bash
lms unload --all || true
lms ps
ID="qwen3coder-32k-${GITHUB_RUN_ID}"
echo "$ID" > /tmp/lmstudio_model_id.txt
# retry once: large-model loads can transiently fail under memory pressure
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y || { lms unload --all; sleep 5; lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y; }
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## 啟動並配置 VS Code

我們將在 VS Code 中安裝 Cline 擴充功能，並將其連接至我們剛才建立的 LM Studio 伺服器。
- 在搜尋列中搜尋 `VS Code` 並啟動應用程式。
- 按一下 VS Code 左側欄位的 `Extensions` 圖示，搜尋 `Cline`。然後按一下 `Install` 按鈕。

![安裝 Cline 擴充功能](assets/installing-cline-vscode-extension.png)

- 左側應會出現 Cline 圖示。按一下該圖示以開啟 Cline。會出現一個視窗詢問 `How will you use Cline?`。由於我們將使用透過 LM Studio 執行的本機 LLM，請選擇 `Bring my own API Key` 並按下 `Continue`。

<!-- @os:windows -->
<!-- @test:id=cline-install-and-verify-windows timeout=300 hidden=True -->
```powershell
code --install-extension saoudrizwan.claude-dev
code --list-extensions | Select-String -Pattern "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=cline-install-and-verify-linux timeout=300 hidden=True -->
```bash
code --install-extension saoudrizwan.claude-dev
code --list-extensions | grep -i "saoudrizwan.claude-dev"
```
<!-- @test:end -->
<!-- @os:end -->

![帳戶建立](assets/cline-how-will-you-use-cline-zoomed.png)

接下來，我們需要配置 Cline 以與我們設定的 LM Studio 伺服器通訊。
- 將 API Provider 設為 `LM Studio`，模型設為 `Qwen3-Coder-30B-A3B-GGUF`。

>**提示**：可能有較新的模型可用。如有需要，可考慮下載並切換至 Qwen3.6 模型。


![模型配置](assets/cline-model-configuration-zoomed.png)

## 建立您的第一個專案

讓我們使用本機代理建立一個網站！開啟 VSCode 並選擇您想要的目錄，Cline 將在該處建立檔案。
- 若要執行此操作，請點選 VS Code 左上角的 `File -> Open Folder`，並選擇像 `Documents` 這樣的資料夾。

![VS Code 空白資料夾](assets/open-cline-test.png)

現在我們已準備好向本機編碼代理下達提示。
- 按一下左側欄位的 Cline 擴充功能，並輸入提示以啟動代理。舉例來說，讓我們使用以下提示：
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

代理將依據提示開始建立檔案。作為使用者，您可以在 VS Code 中觀看程式碼的生成過程，如下所示。每次 Cline 想要建立檔案時，您可能需要按一下 `Save`。

![Cline 程式碼生成](assets/cline-code-generation.png)

軟體生成完成後，代理的任務即告完成，您便可以執行該應用程式。在此範例中，代理寫入了三個檔案：`index.html`、`script.js` 與 `styles.css`。只要直接雙擊該 HTML 檔案，即可載入並與生成的網站互動。

<!-- @os:windows -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-windows timeout=300 hidden=True -->
```python
import json, urllib.request, os

model_id_path = os.path.join(os.environ["TEMP"], "lmstudio_model_id.txt")
with open(model_id_path, "r", encoding="utf-8") as f:
    model_id = f.read().strip()

req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 64
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-coding-prompt-endpoint-linux timeout=300 hidden=True -->
```python
import json, urllib.request
with open("/tmp/lmstudio_model_id.txt", "r", encoding="utf-8") as f:
    model_id = f.read().strip()
req = urllib.request.Request(
    "http://127.0.0.1:1234/v1/chat/completions",
    data=json.dumps({
        "model": model_id,
        "messages": [{"role":"user","content":"Write a Python function add(a,b) that returns a+b. Only output code."}],
        "temperature": 0,
        "max_tokens": 64
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=120) as r:
    print(r.read().decode("utf-8", "replace"))
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lmstudio-server-stop-windows timeout=300 hidden=True -->
```powershell
$ID = Get-Content "$env:TEMP\lmstudio_model_id.txt" -Raw
$ID = $ID.Trim()
lms unload "$ID"
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-server-stop-linux timeout=300 hidden=True -->
```bash
ID="$(cat /tmp/lmstudio_model_id.txt)"
lms unload "$ID" || true
lms ps
lms server stop
```
<!-- @test:end -->
<!-- @os:end -->
## 後續步驟

在生成網站後，您可以繼續與 Cline 協作以改善該網站。以下是兩個可能的改進方向：

- **文件說明**：只需向代理提示 `Add a README`，代理即可生成記錄該網站的 `README.md` 檔案。
- **動畫效果**：提示模型 `Add an animation that visually represents a large language model running on a laptop.`，即可為網站生成一段動畫。

我們鼓勵讀者嘗試使用此設置生成其他應用程式。以下是我們嘗試過的一些有趣範例：

- **復古街機遊戲**：嘗試其他一些提示。讓代理使用 `PyGame` 套件以 Python 建立復古風格的遊戲也會很有趣，可使用以下提示：

```code
Create a simple pong game using the PyGame python package.
```

- **資料分析**：程式碼代理特別有用的一個領域是腳本編寫與資料分析。以下提示展示了本地模型為股價視覺化生成資料分析軟體的能力：

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## 資源

以下是一些額外資源，可協助您進一步了解程式碼代理、Cline，以及在 AMD 上執行工作負載

* 有關 AMD 與 LM Studio 合作夥伴關係及整合的更多資訊：https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD 部落格文章，介紹如何在 AMD Ryzen™ AI 及 Radeon™ 顯示卡上執行 Cline：https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Cline 部落格文章，介紹如何在 AI PC 上本地執行程式碼代理：https://cline.bot/blog/local-models-amd