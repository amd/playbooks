<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> 此手冊使用了 GitHub 無法呈現的特殊標籤。請造訪 [amd.com/playbooks](https://amd.com/playbooks) 以正確預覽此內容。
<!-- @github-only:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> 此手冊至少需要 **32GB** 的系統記憶體。
<!-- @device:end -->

## 概觀

程式碼代理工具（Coding agents）是強大的工具，讓開發者能夠透過與由大型語言模型（LLMs）驅動的 AI 代理協作來提升生產力。它們可以嵌入到開發環境中，例如終端機或 VS Code，讓開發者能夠將其無縫整合到工作流程中。

本教學將示範如何使用 Cline、VS Code 和 LM Studio，完全在本機執行程式碼代理。

## 您將學到什麼

* 如何搭配使用 VS Code 與 Cline 程式碼代理，以協助軟體工程任務。
* 如何設定 Cline 與 LM Studio 通訊，以進行程式碼代理的本機推論。
* 如何使用本機程式碼代理解決真實世界的軟體工程任務。

## 設定記憶體組態

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 檢查軟體更新
> **注意**：如果尚未安裝 VS Code，您可以透過 Ryzen AI Developer Center 進行安裝。

<!-- @require:software-update -->
<!-- @device:end -->

## 安裝軟體先決條件

<!-- @require:lmstudio,vscode -->

## 啟動並設定 LM Studio

我們將使用 LM Studio 來提供驅動程式碼代理的 LLM。

- 在搜尋列中搜尋 `LM Studio` 並啟動應用程式。您將看到以下頁面。

![LM Studio 初始畫面](assets/initial-lm-studio.png)

接下來，我們必須在系統上載入 LLM。我們將使用具有較大上下文長度的 `Qwen3-Coder-30B-A3B` 模型。（若尚未安裝，請使用「Model」分頁進行安裝）。
- 點擊 LM Studio 視窗頂端的搜尋列，或按下 `CTRL+L`。點擊 `Manually choose model load parameters` 開關，然後點擊 Qwen3-Coder-30B-A3B 模型。
- 將上下文長度從 `4096` 改為 `32768`，並確保 `GPU Offload` 設為最大值。然後點擊 `Load Model`

![選擇模型](assets/model-list-zoomed.png)

我們使用較大的上下文長度，讓代理能夠處理大型程式碼庫並記住已進行的變更。

![設定模型](assets/selecting-model-zoomed.png)

接下來，我們需要啟用 LM Studio 伺服器。
- 在 LM Studio 左側點擊 Developer 分頁，或按下 `CTRL+2`。
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
<!-- @test:id=lmstudio-load-qwen3-coder-windows timeout=1200 hidden=True -->
```powershell
lms unload --all
lms ps
$ID = "qwen3coder-32k-$env:GITHUB_RUN_ID"
Set-Content -Path "$env:TEMP\lmstudio_model_id.txt" -Value $ID -Encoding utf8
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps
lms chat "$ID" -p "Reply with exactly: OK"
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
lms load qwen3-coder-30b --context-length 32768 --gpu max --identifier "$ID" -y
lms ps # Verify model is really loaded
lms chat "$ID" -p "Reply with exactly: OK"
```
<!-- @test:end -->
<!-- @os:end -->

## 啟動並設定 VS Code

我們將在 VS Code 中安裝 Cline 擴充功能，並將其連接到我們剛才建立的 LM Studio 伺服器。
- 在搜尋列中搜尋 `VS Code` 並啟動應用程式。
- 點擊 VS Code 左側欄位中的 `Extensions` 圖示，並搜尋 `Cline`。然後點擊 `Install` 按鈕。

![安裝 Cline 擴充功能](assets/installing-cline-vscode-extension.png)

- 左側應會出現一個 Cline 圖示。點擊該圖示以開啟 Cline。將會出現一個視窗詢問 `How will you use Cline?`。由於我們將使用透過 LM Studio 執行的本機 LLM，請選擇 `Bring my own API Key` 並點擊 `Continue`。

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

接下來，我們需要設定 Cline 以與我們所設定的 LM Studio 伺服器進行通訊。
- 將 API Provider 設定為 `LM Studio`，並將模型設定為 `Qwen3-Coder-30B-A3B-GGUF`。

>**提示**：可能已有更新的模型可用。若有需要，可考慮下載並切換至 Qwen3.6 系列模型。


![模型設定](assets/cline-model-configuration-zoomed.png)

## 建立您的第一個專案

讓我們使用本機代理來建立一個網站！開啟 VS Code 並選擇一個目錄，Cline 將在該處建立檔案。
- 若要執行此操作，請在 VS Code 左上角選擇 `File -> Open Folder`，並選擇一個資料夾，例如 `Documents`。

![VS Code 空白資料夾](assets/open-cline-test.png)

現在我們已準備好對本機程式碼代理下達提示。
- 點擊左側欄位中的 Cline 擴充功能，並輸入提示以啟動代理。舉例來說，我們使用以下提示：
```code
Create a website showcasing the ability to run local large-language models on an AMD device.
```

接著代理將開始根據提示建立檔案。作為使用者，您可以在 VS Code 中觀看程式碼生成的過程，如下所示。每次 Cline 想要建立檔案時，您可能都需要點擊 `Save`。

![Cline 程式碼生成](assets/cline-code-generation.png)

軟體生成完成後，代理即完成任務，您便可以執行該應用程式。在此案例中，代理寫入了三個檔案：`index.html`、`script.js` 和 `styles.css`。只需雙擊 HTML 檔案，即可載入並與生成的網站互動。

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
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
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
        "max_tokens": 500
    }).encode("utf-8"),
    headers={"Content-Type":"application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=60) as r:
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

在生成網站後，您可以繼續與 Cline 協作以改善網站。以下是兩個可能的改進方向：

- **文件說明**：只需以 `Add a README` 提示代理，代理即可生成記錄該網站的 `README.md` 檔案。
- **動畫效果**：以 `Add an animation that visually represents a large language model running on a laptop.` 提示模型，即可為網站生成一段動畫。

我們鼓勵讀者嘗試使用此設定生成其他應用程式。以下是我們嘗試過的一些有趣範例：

- **復古街機遊戲**：嘗試一些其他提示詞。使用以下提示詞，讓代理使用 `PyGame` 套件以 Python 建立復古風格遊戲也會很有趣：

```code
Create a simple pong game using the PyGame python package.
```

- **資料分析**：編程代理特別有用的一個領域是腳本編寫與資料分析。以下提示詞用於展示本地模型生成股價視覺化資料分析軟體的能力：

```code
Write a Python script that fetches daily price data for AMD (ticker: AMD) from an online API (use the yfinance library so no API key is needed). Loads the last 365 calendar days of data into a Pandas DataFrame. Computes 20-day and 50-day simple moving averages of the closing price. Store the data in a sqlite database and when the script is first run check to see if the sqlite database contains the requested data, if not, fetch it from the API. Plots a single matplotlib line chart with: Close, SMA-20, and SMA-50. Include a title, axis labels, and a legend. Saves the figure to amd_price_sma.png in the current directory and prints the path when done. Allow the user to pass in command line arguments for the total time period of data, the time period for the simple moving average to calculate, as well as to provide different tickers.
```

## 資源

以下是一些額外資源，可協助您進一步了解編程代理、Cline，以及在 上執行工作負載的相關資訊

* 有關 AMD 與 LM Studio 合作夥伴關係及整合的更多資訊：https://www.amd.com/en/ecosystem/isv/consumer-partners/lm-studio.html
* AMD 部落格：介紹如何在 AMD Ryzen™ AI 與 Radeon™ 顯示卡上執行 Cline：https://www.amd.com/en/blogs/2025/how-to-vibe-coding-locally-with-amd-ryzen-ai-and-radeon.html
* Cline 部落格：在 AI PC 上本機執行編程代理：https://cline.bot/blog/local-models-amd