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
> 此教學課程需要至少 **32GB** 的系統記憶體。
<!-- @device:end -->

## 概觀

編碼代理程式是強大的工具，透過與由大型語言模型 (LLM) 支援的 AI 代理程式協作，賦予開發人員能力。它們可以嵌入到開發環境中，例如終端機或 VS Code，讓開發人員能夠將其無縫整合到工作流程中。

本教學課程說明如何使用 Cline、VS Code 和 LM Studio，在您的本機上完全執行編碼代理程式。

## 您將學到什麼

* 如何使用搭載 Cline 編碼代理程式的 VS Code，協助軟體工程任務。
* 如何設定 Cline 與 LM Studio 通訊，以進行編碼代理程式的本機推論。
* 如何使用本機編碼代理程式解決實際的軟體工程任務。

<!-- @device:halo_box,halo,stx,krk -->
## 設定記憶體組態

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## 檢查軟體更新
> **注意**：如果尚未安裝 VS Code，您可以透過 Ryzen AI Developer Center 進行安裝。

<!-- @require:software-update -->
<!-- @device:end -->

## 安裝軟體必要條件

<!-- @require:lmstudio,vscode -->

## 啟動並設定 LM Studio

我們將使用 LM Studio 來提供驅動編碼代理程式的 LLM。

- 在搜尋列中搜尋 `LM Studio` 並啟動應用程式。您會看到以下畫面。

![LM Studio 初始畫面](assets/initial-lm-studio.png)

接下來，我們必須在系統上載入 LLM。我們將使用具有較大內容長度的 `Qwen3-Coder-30B-A3B` 模型。（如果尚未安裝，請使用 Model 分頁進行安裝）。
- 按一下 LM Studio 視窗頂端的搜尋列，或按下 `CTRL+L`。按一下切換開關 `Manually choose model load parameters`，然後按一下 Qwen3-Coder-30B-A3B 模型。
- 將內容長度從 `4096` 變更為 `32768`，並確保 `GPU Offload` 設定為最大值。然後，按一下 `Load Model`

![選取模型](assets/model-list-zoomed.png)

我們使用較大的內容長度，讓代理程式能夠處理大型程式碼庫，並記住已進行的變更。

![設定模型](assets/selecting-model-zoomed.png)

接下來，我們需要啟用 LM Studio Server。
- 按一下 LM Studio 左側的 Developer 分頁，或按下 `CTRL+2`。
- 勾選狀態切換開關，確保其設定為 `Running`。

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

## 啟動並設定 VS Code

我們將在 VS Code 中安裝 Cline 擴充功能，並將其連接到我們剛剛建立的 LM Studio 伺服器。
- 在搜尋列中搜尋 `VS Code` 並啟動應用程式。
- 按一下 VS Code 左側欄位中的 `Extensions` 圖示，並搜尋 `Cline`。然後按一下 `Install` 按鈕。

![安裝 Cline 擴充功能](assets/installing-cline-vscode-extension.png)

- 左側應會出現 Cline 圖示。按一下該圖示以開啟 Cline。將會出現一個視窗詢問 `How will you use Cline?`。由於我們將使用透過 LM Studio 執行的本機 LLM，請選擇 `Bring my own API Key` 並按下 `Continue`。

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

![建立帳戶](assets/cline-how-will-you-use-cline-zoomed.png)

接下來，我們需要設定 Cline 與我們設定的 LM Studio 伺服器通訊。
- 將 API Provider 設定為 `LM Studio`，並將模型設定為 `Qwen3-Coder-30B-A3B-GGUF`。

>**提示**：可能會有較新的模型可用。如有需要，可考慮下載並切換至 Qwen3.6 模型。


![模型設定](assets/cline-model-configuration-zoomed.png)

## 建立您的第一個專案

讓我們使用本機代理程式來建立一個網站！開啟 VSCode 並選擇一個目錄，Cline 將在其中建立檔案。
- 若要執行此操作，請在 VS Code 左上角選擇 `File -> Open Folder`，並選擇一個資料夾，例如 `Documents`。

![VS Code 空白資料夾](assets/open-cline-test.png)

現在我們已準備好向本機編碼代理程式下達提示。
- 按一下左側欄位中的 Cline 擴充功能，並輸入提示以啟動代理程式。例如，我們可以使用以下提示：
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

接著，代理程式將開始根據提示建立檔案。使用者可以在 VS Code 中觀看程式碼的產生過程，如下所示。每次 Cline 要建立檔案時，您可能需要按一下 `Save`。

![Cline 程式碼產生](assets/cline-code-generation.png)

軟體產生完成後，代理程式的工作即告完成，您即可執行該應用程式。在此範例中，代理程式撰寫了三個檔案：`index.html`、`script.js` 和 `styles.css`。只需雙擊 HTML 檔案，即可載入並與所產生的網站互動。

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

在產生網站之後，您可以繼續與 Cline 合作，改善該網站。以下是兩個可能的改善方向：

- **文件說明**：只需向代理程式提示 `Add a README`，代理程式即可產生記錄該網站的 `README.md` 檔案。
- **動畫效果**：向模型提示 `Add an animation that visually represents a large language model running on a laptop.`，即可為網站產生動畫。

我們鼓勵讀者嘗試使用此設定產生其他應用程式。以下是我們嘗試過的一些有趣範例：

- **復古街機遊戲**：嘗試其他提示。使用以下提示，也可以讓代理程式利用 `PyGame` 套件，使用 Python 建立復古風格的遊戲，過程相當有趣：

```code
Create a simple pong game using the PyGame python package.
```

- **資料分析**：編碼代理程式特別有用的一個領域是腳本撰寫與資料分析。以下提示可展示本機模型產生股價視覺化資料分析軟體的能力：

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## 資源

以下是一些額外的資源，可協助您深入了解 Coding Agents、Cline，以及在 AMD 硬體上執行工作負載。

* 更多有關 AMD 與 LM Studio 合作夥伴關係的資訊：https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD 部落格：說明如何在 AMD Ryzen™ AI 與 Radeon™ 顯示卡上執行 Cline：https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Cline 部落格：在 AI PC 上本機執行 Coding Agents：https://cline.bot/blog/local-models-amd