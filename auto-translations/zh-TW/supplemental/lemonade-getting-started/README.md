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

## 概觀

🍋 **Lemonade** 是一款開源的本機 AI 伺服器,可讓您直接在自己的硬體上執行大型語言模型 (LLM)、影像產生器和音訊模型。它透過業界標準的 **OpenAI API** 公開這些模型,因此任何可與 OpenAI 搭配運作的應用程式都能立即與 Lemonade 搭配運作。完成本教學後,您將能使用 Lemonade 在自己的機器上本機執行模型。

## 您將學到什麼

完成本教學後,您將能夠:

* **安裝 Lemonade Server** 並確認其正在執行。
* **下載並與 LLM 對話**,只需一道指令。
* **探索網頁使用者介面**,並嘗試視覺、語音轉文字、影像產生等不同模態。
* **在 Vulkan 與 AMD ROCm™ 軟體之間切換 GPU 後端**。
* **使用 OpenAI 相容 API,打造由本機 LLM 驅動的 Python 應用程式**。
<!-- @device:halo_box,halo,stx,krk -->
* **在 AMD Ryzen™ AI 硬體上,使用 Hybrid 與 FLM 執行模式,在 AMD 神經處理單元 (NPU) 上執行模型**。
<!-- @device:end -->

<!-- @device:halo_box,halo,stx,krk -->
## 設定記憶體組態

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## 檢查軟體更新

<!-- @require:software-update -->
<!-- @device:end -->

## 安裝軟體必要條件

開始之前,請確認您已具備以下條件:

- 一部執行 **Windows 11** 或受支援的 **Linux** 發行版(Ubuntu 24.04+、Fedora、Debian)的電腦
- 建議具備 **16 GB 記憶體**,以執行步驟 1–7 中所使用的模型(`Gemma-4-E2B-it-GGUF`,約 3 GB)。若您想在步驟 6 使用較大的程式碼產生模型(`Qwen3.5-35B-A3B-GGUF`,約 20 GB),則建議具備 **32 GB 以上**記憶體。
- 依您下載的模型不同,需要**約 4–30 GB 的可用磁碟空間**。本指南中最大的模型約為 20 GB。
- **Python 3.10–3.13**(用於 Python 應用程式章節)
- 網際網路連線(有線或無線)
<!-- @device:halo_box,halo,stx,krk -->
- [選用] 若您想在 NPU 上執行模型,需具備 AMD XDNA 2 NPU(Ryzen AI 300/400/Max 300 系列或 Z2 Extreme),並已安裝來自 [Ryzen AI 軟體安裝說明](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) 的最新驅動程式。
<!-- @device:end -->

<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @require:lemonade -->

<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-update-windows timeout=120 hidden=True -->
```powershell
winget upgrade -e --id AMD.LemonadeServer
lemonade --version

# Upgrading runs the Lemonade Server installer, which stops the running server
# to replace its files and does not start it again. Relaunch it so the local API
# on port 13305 is available for the next steps.
if (-not (Get-Process LemonadeServer -ErrorAction SilentlyContinue)) {
  Start-Process "$env:LOCALAPPDATA\lemonade_server\bin\LemonadeServer.exe"
}
```
<!-- @test:end -->

<!-- @test:id=lemonade-chat-gemma-windows timeout=1200 hidden=True -->
```powershell

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade(robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "Gemma-4-E2B-it-GGUF" } | Select-Object -First 1
if (-not $entry) { throw "Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "Gemma-4-E2B-it-GGUF"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 500
} | ConvertTo-Json -Depth 5
$out = curl.exe -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions -H "Content-Type: application/json" -d $body
if (-not $out) { throw "Empty response from Lemonade chat/completions" }
Write-Host "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-update-linux timeout=120 hidden=True -->
```bash
sudo apt update
sudo apt install --only-upgrade lemonade-server
lemonade --version
```
<!-- @test:end -->

<!-- @test:id=lemonade-chat-gemma-linux timeout=1200 hidden=True -->
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
    if item.get("id") == "Gemma-4-E2B-it-GGUF":
        entry = item
        break

if entry is None:
    print("Model Gemma-4-E2B-it-GGUF is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model Gemma-4-E2B-it-GGUF is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: Gemma-4-E2B-it-GGUF model is downloaded in Lemonade")
PY

body='{
  "model": "Gemma-4-E2B-it-GGUF",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 500
}'

out="$(curl -s --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi

echo "OK: Model Gemma-4-E2B-it-GGUF responded"
```
<!-- @test:end -->
<!-- @os:end -->

---

## 核心概念 — 本機 AI 伺服器的運作方式

在執行模型之前,值得先了解*為何*要以這樣的方式設定。Lemonade 是一個**本機模型伺服器**,也就是一個將 AI 模型載入記憶體,並透過 HTTP 將其公開給應用程式使用的處理程序,運作方式就如同雲端 AI 服務一樣。

### 為什麼需要伺服器?

| 優點 | 對您的意義 |
|---------|----------------------|
| **簡化整合** | 應用程式只需與單一 HTTP API 溝通,而不必處理特定硬體的 C++ 或 Python 程式庫。 |
| **模型共用** | 單一已載入的模型可同時服務多個應用程式,不會有重複複本佔用您的記憶體。 |
| **雲端到本機的可攜性** | 為 OpenAI 雲端 API 撰寫的程式碼,只需變更一個 URL,即可搭配 Lemonade 運作。 |
| **關注點分離** | 模型管理、串流傳輸與容錯處理均由伺服器負責,讓開發人員可以專注於自己的應用程式。 |

### OpenAI API 標準

Lemonade 實作了 **OpenAI API**,這是 ChatGPT、Azure OpenAI 以及數十種其他服務所使用的相同介面。其對話模型十分簡單:

| 角色 | 說話者 |
|------|---------------|
| **system** | 給模型的指示(人物設定、限制條件、可用工具) |
| **user** | 由人類(或應用程式)傳送給模型的訊息 |
| **assistant** | 由模型產生的回應 |

這表示任何支援 OpenAI 的程式庫或應用程式,只要在 Lemonade Server 執行時,將其指向 `http://localhost:13305/api/v1`,即可與 Lemonade 溝通。

## 主要活動 — 您的第一次本機 AI 對話

讓我們下載一個 LLM,並與它對話,整個 AI 運算完全在您自己的機器上執行。

### 步驟 1:下載並執行模型

Lemonade 隨附了一個精選的模型庫。讓我們從 **Gemma-4-E2B-it** 開始,這是一個功能強大且體積精巧的模型,並支援視覺功能。開啟終端機並執行:

```
lemonade run Gemma-4-E2B-it-GGUF
```

這道指令會執行三件事:

1. **下載**模型(約 3 GB)自 Hugging Face(若尚未下載)。(可能需要一些時間)
2. 在連接埠 13305 上**啟動** Lemonade Server 處理程序。
3. **開啟 Lemonade App**,讓您可以開始與模型對話。


<!-- @os:windows -->
在 Windows 上,Lemonade App 會自動啟動,您可以立即開始對話。若您安裝的是 `minimal.msi` 套件,則不會包含此應用程式。要開始對話,請開啟您的網頁瀏覽器並前往 `http://localhost:13305`。
<!-- @os:end -->

<!-- @os:linux -->
在 Linux 上,請開啟您的瀏覽器並前往 `http://localhost:13305`,以存取網頁應用程式。
<!-- @os:end -->

嘗試輸入一個問題:

```
What are three fun facts about lemons?
```

模型會直接在聊天視窗中回應。**恭喜!您正在本機執行大型語言模型。**

![顯示記錄的 Lemonade App](../../dependencies/assets/ChatwithLogs.png)

在 Lemonade App 的伺服器記錄面板中,您可以在每次回應後找到有關模型效能的遙測資料。例如:

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### 步驟 2：探索網頁介面與不同的模態

Lemonade 內建了一個網頁介面，你可以在其中：

- **互動**：在熟悉的聊天視窗中與已載入的模型互動
- **瀏覽模型**：在 Model Manager 分頁中瀏覽模型
- **下載新模型**：一鍵下載

試著使用網頁 UI 中的 **Model Manager** 分頁切換不同的模態，你可以依 Recipe 或 Category 瀏覽模型：

1. **Vision（視覺）：** 你已經載入的 `Gemma-4-E2B-it-GGUF` 模型支援視覺功能。將圖片貼到聊天框中，並要求模型描述該圖片。
2. **Image generation（圖像生成）：** 在 Image 類別中，從 Model Manager 下載一個圖像模型，例如 `SDXL-Turbo`，然後使用 Lemonade Image Generator 輸入提示詞並在本機生成圖像。
3. **Audio（音訊）：** 在 Audio 類別中，下載一個音訊模型，例如 `Whisper-Tiny`，它可以進行語音轉文字。提供一段錄音以在本機進行轉錄。至於文字轉語音，可以嘗試 Speech 類別中的模型，例如 `kokoro-v1`。

![Lemonade 多模態](../../dependencies/assets/multi_modality.png)

### 步驟 3：嘗試使用不同後端執行模型

如果你將滑鼠移到 Lemonade App 中的某個模型上，會看到一個齒輪圖示。點擊此圖示可以讓你選擇該模型的選項，包括選擇你想要的後端。

預設情況下，Lemonade 使用 Vulkan 進行 GPU 加速。如果你擁有受支援的 AMD 獨立顯示卡，可以切換為 ROCm。

![Lemonade 選擇後端](../../dependencies/assets/lemonademodeloptions.png)

若要管理已安裝的後端，請點擊最左欄的後端按鈕。

或者，你也可以使用以下指令指定後端：

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

你也可以使用環境變數 `LEMONADE_LLAMACPP` 來設定預設後端，其值可為：`vulkan`、`rocm` 或 `cpu`。

---

## 深入探討 — 使用 Python 建構 AI 驅動的應用程式

本機 AI 伺服器真正強大之處在於，任何應用程式只需幾行程式碼即可與其連接。為了證明這一點，讓我們來建構一個小巧但功能完整的**學習閃卡產生器**，只要給它一個主題，它就會產生閃卡，並讓你可以互動式地自我測驗。

### 步驟 4：啟動伺服器

確認 Lemonade 伺服器正在執行。安裝完成後，它通常會自動在背景啟動。若要確認，請執行：

```
lemonade status
```

你應該會看到類似這樣的訊息：`Server is running on port 13305`。

如果伺服器未執行，請開啟 Lemonade app 來啟動它。使用預設連接埠 **13305**（你可以從系統匣圖示確認或選擇此連接埠）。

### 步驟 5：安裝 OpenAI Python 用戶端

在終端機中，建立一個 venv 並使用以下指令安裝 OpenAI Python 用戶端：
<!-- @os:linux -->
```bash
# Your specific version of Linux may have different commands
sudo apt update
sudo apt install -y python3-venv
python3 -m venv lemonade-env
source lemonade-env/bin/activate
pip install openai
```
<!-- @os:end -->
<!-- @os:windows -->
```powershell
python -m venv lemonade-env
lemonade-env\Scripts\activate
pip install openai
```
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=env-check-windows timeout=300 hidden=True -->
```powershell
python --version
where.exe python
where.exe pip
python -c "import sys; print(sys.executable)"
python -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=env-check-linux timeout=300 hidden=True -->
```bash
python3 --version
which python3
which pip3
python3 -c "import sys; print(sys.executable)"
python3 -m pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=pip-install-openai-windows timeout=300 hidden=True -->
```powershell
python -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=pip-install-openai-linux timeout=300 hidden=True -->
```bash
python3 -m pip install openai
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-openai-import-windows timeout=120 hidden=True -->
```powershell
python -m pip show openai
python -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=python-openai-import-linux timeout=120 hidden=True -->
```bash
python3 -m pip show openai
python3 -c "from openai import OpenAI; print('OK')"
```
<!-- @test:end -->
<!-- @os:end -->

### 步驟 6：建構閃卡應用程式

讓我們下載另一個模型來產生程式碼：`Qwen3.5-35B-A3B-GGUF`。這是一個較大（約 20 GB）且效能優異的模型，最適合擁有 32 GB 以上記憶體的系統。如果你的可用記憶體較少，可以改用 `Qwen3.5-9B-GGUF`（約 6 GB）。

你可以從 UI 下載，或執行以下指令：
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

將以下提示詞輸入到 Lemonade Chat UI，以產生一個簡單閃卡應用程式的程式碼。

我們將使用 Qwen3.5-35B-A3B-GGUF（一個較大、更擅長撰寫程式碼的模型）來產生我們的 Python 應用程式，而該應用程式在執行時會呼叫 Gemma-4-E2B-it-GGUF（你已經下載的較小模型）。之後可以將程式碼複製到你選擇的檔案中，以在 Python 中執行。

```
Generate a Python script that uses the OpenAI Python library to call a local LLM and create an interactive flashcard study tool.

Connection details:
- Base URL: http://localhost:13305/api/v1
- API key: "lemonade"
- Model to use: "Gemma-4-E2B-it-GGUF"

Structure:

1. A `generate_flashcards(topic, count=5)` function that:
   - Sends a system message instructing the LLM to return ONLY a JSON array of objects with "question" and "answer" fields.
   - Handles malformed JSON gracefully.
   - Returns the parsed list of cards, or an empty list if parsing fails.

2. A `quiz(cards)` function that shuffles the cards and, for each card:
   - Prints `--- Card i/N ---`.
   - Prints `Q: <question>`.
   - Waits for the user to press Enter ("Press Enter to reveal the answer...").
   - Prints `A: <answer>`.
   - Asks "Did you get it right? (y/n): " and tracks the score.
   - At the end, prints `🏆 Score: <score>/<total>`.

3. A main loop that:
   - Prints a `🍋 Lemonade Flashcard Generator` banner on startup.
   - Asks the user for a topic (typing "quit" exits).
   - Prints `✨ Generating N flashcards on: <topic>`.
   - Calls `generate_flashcards` and lists the generated questions as an indented numbered list (`  1. ...`).
   - Offers to start the quiz.
```

> **提示**：我們透過完善的提示詞設計以及使用雙模型系統，遵循了標準的工程實務，以優化資源與速度。

為方便起見，我們已提供範例輸出 [`flashcards.py`](assets/flashcards.py)。你可以自由下載到你的目錄中。無論如何，你現在應該已擁有一個可以執行的 Python 檔案。

<!-- @os:windows -->
<!-- @test:id=lemonade-python-smoke-windows timeout=900 hidden=True -->
```powershell
# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

Start-Sleep -Seconds 5
python lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-python-smoke-linux timeout=600 hidden=True -->
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

sleep 5
python3 lemonade_python_smoke.py
```
<!-- @test:end -->
<!-- @os:end -->


### 步驟 7：執行產生的程式碼

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**以下是你應該會看到的內容：**

```
🍋 Lemonade Flashcard Generator
================================
Powered by a local LLM running on your own hardware.

Enter a topic (or "quit" to exit): the solar system

✨ Generating 5 flashcards on: the solar system

Generated 5 cards!

  1. Which planet is closest to the Sun?
  2. What is the largest planet in our solar system?
  3. Which planet is known as the "Red Planet"?
  4. How many moons does Earth have?
  5. What separates the inner planets from the outer planets?

Start quiz? (y/n): y

--- Card 1/5 ---
Q: What is the largest planet in our solar system?

Press Enter to reveal the answer...
A: Jupiter is the largest planet, with a diameter of about 139,820 km.

Did you get it right? (y/n): y

...

🏆 Score: 4/5
```

只用大約 150 行程式碼，你就建構出一個由本機 LLM 驅動、功能完整的學習工具。沒有 API 金鑰需要管理，沒有使用成本，也沒有任何資料離開你的機器。

> **重點洞察：** 請注意 `client = OpenAI(base_url=...) ` 這一行是將這個應用程式連結到 Lemonade（而非 OpenAI 雲端）的*唯一*一行程式碼。其餘的程式碼與你針對任何相容 OpenAI 的服務所撰寫的程式碼完全相同。如果你曾經使用過 OpenAI Python 函式庫，你就已經懂得如何使用 Lemonade 建構應用程式。

### 這說明了什麼

這個小型應用程式展示了幾種實際的整合模式：

| 模式 | 出現位置 |
|---------|-----------------|
| **系統提示（System prompts）** | `"system"` 訊息告訴 LLM 輸出結構化的 JSON |
| **結構化輸出** | 應用程式將 LLM 的回應解析為 JSON 以建立閃卡 |
| **無狀態請求** | 每次呼叫 `generate_flashcards()` 都是獨立的 |
| **錯誤處理** | `try/except` 能優雅地處理 LLM 輸出不是有效 JSON 的情況 |

這些相同的模式可以擴展到任何應用程式，例如聊天機器人、程式碼助理、內容產生器、自動化工具。

#### 進階挑戰

* 若想要更多挑戰，可以試著更新此應用程式，參考[這裡](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py)提供的範例，讓閃卡內容以語音朗讀給使用者聽。

---

<!-- @device:halo_box,halo,stx,krk -->
## 在 NPU 上運行模型（可選）

如果您擁有 Ryzen AI 300/400/Max 300 系列或 Z2 Extreme,您的設備內建了**神經處理單元 (NPU)**,這是一個專為 AI 工作負載設計的專用晶片。在 NPU 上運行模型比使用 GPU 更節能,非常適合背景 AI 任務、較長的工作階段以及電池供電使用情境。

Lemonade 支援三種 NPU 執行模式,這些模式在同一個 OpenAI API 背後都是透明的:

| 模式 | 運作方式 | Recipe | 範例模型 |
|------|-------------|--------|----------------|
| **Hybrid (NPU + iGPU)** | NPU 處理提示,iGPU 產生 token | OGA (`oga-hybrid`) | Qwen3-4B-Hybrid |
| **NPU-only** | 整個推論在 NPU 上運行 | Ryzen AI LLM (`ryzenai-llm`) | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | 使用 NPU 上的 FastFlowLM 引擎,針對 AMD XDNA2 進行優化 | FLM (`flm`) | qwen3.5-4b-FLM |

### 需求

- **AMD Ryzen AI 300/400 系列或 Z2 系列**處理器
- 針對 **FLM** 模型:可以從 Lemonade 應用程式內安裝 FLM 執行環境,或者在運行 FLM 模型時 Lemonade 會自動安裝 FLM 執行環境。若要進一步了解 FastFlowLM,請參閱[這裡](https://fastflowlm.com/docs/)。


### 步驟 8:運行 Hybrid 模型

Hybrid 模型將工作分配給 NPU 和 iGPU,以取得速度與效率的良好平衡。在 Lemonade App 中,從 `Ryzen AI LLM` 清單中選擇一個模型,例如 `Qwen3-4B-Hybrid`,或使用以下指令運行:

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade 會自動偵測您的 NPU 並安裝 **Ryzen AI LLM** 後端。

> **背後發生了什麼？** 當您傳送訊息時,NPU 會平行處理您的整個提示(這稱為「prefill」)。接著,iGPU 接手並逐一 token 產生回應(這稱為「decode」)。這種混合方式充分發揮了每個晶片的優勢。

### 步驟 9:運行 FLM 模型

FastFlowLM (FLM) 模型專門針對 AMD 的 XDNA2 NPU 架構進行優化,以其大小而言可以非常快速。例如,從 `FastFlowLM NPU` 清單中選擇 `qwen3.5-4b-FLM`,或使用以下指令:

<!-- @os:windows -->
若要在 Windows 上啟用 `FastFlowLM`:

* 開啟 `Backends Manager` 選單。
* 找到 `FastFlowLM NPU` 後端類別。
* 點選 Install NPU。
* 安裝完成後,約有 36 個預設模型將出現在 FFLM 下拉式選單中。
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
當 `Lemonade` App 首次啟動時,`FastFlowNPU` 後端預設不會啟用。
本機應用程式會開啟安裝頁面,引導您完成設定。

若要在 Linux 上啟用 `FastFlowLM`:

* 開啟 `Lemonade` App。
* 造訪[官方 FLM](https://lemonade-server.ai/flm_npu_linux.html) 文件,並選擇您的 Linux 發行版,依照 FLM 的安裝步驟操作。
* 依照安裝頁面上的說明啟用 backports。
* 從[標籤頁面](https://github.com/FastFlowLM/FastFlowLM/tags)下載最新的 `v0.9.x` 版本。'
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
針對 AMD Halo Developer Platform,請務必選擇 Debian 13。
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* 安裝下載的 `.deb` 套件。
* 建議:退出 `Lemonade App` 並重新開啟,以偵測變更。
* 建議:開啟 `Backends Manager` 並點選 Install `FastFlowNPU` Backend。
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
安裝成功後,您應該會在 **Lemonade Desktop App** 內的**下載管理員**中看到 `flm:npu` 已完成。
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
接著您就可以選擇任何可用的 FFLM 模型,並開始使用 NPU 後端。

若要取得特定模型,請從[模型頁面](https://fastflowlm.com/docs/models/qwen/)下載所需模型,並使用文件中提供的 Shell 指令進行驗證。
```
flm run qwen3.5-4b-FLM
```
或透過 
```
lemonade run qwen3.5-4b-FLM
```

FLM 模型包含一些最受歡迎的架構(Gemma 3、Qwen 3、Llama 3 和 DeepSeek R1),大小範圍從不到 1 GB 到超過 13 GB 不等。
Lemonade 會自動偵測您的 NPU 並安裝 **FastFlowLM NPU** 後端。

<!-- @os:windows -->
> **提示：** 為了獲得最佳 NPU 效能,請啟用 turbo 模式：
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### 切換模型

步驟 6 中的記憶卡應用程式同樣適用於 NPU 模型,只需更改模型名稱即可：

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## 後續步驟

您現在已經在自己的硬體上運行了一個本機 AI 伺服器,以下是接下來可以進行的事項：

1. **連接您喜愛的應用程式**：Lemonade 開箱即用,可與 [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk)、[Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/)、[Continue](https://lemonade-server.ai/docs/server/apps/continue/)、[n8n](https://n8n.io/integrations/lemonade-model/)以及[更多其他應用程式](https://lemonade-server.ai/marketplace)搭配使用。

2. **瀏覽更多模型**：探索完整的[模型庫](https://lemonade-server.ai/docs/server/server_models/),尋找針對編碼、推理、視覺等各種用途優化的模型。使用 Lemonade App 或 `lemonade list` 查看可用內容。

3. **解鎖 ROCm GPU 加速**：如果您擁有受支援的 AMD GPU,請切換至 ROCm 後端：`lemonade config set llamacpp.backend=rocm`。請參閱[受支援的 AMD GPU](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations)。

4. **閱讀完整 API 規格**：Lemonade 支援聊天完成、嵌入、音訊轉錄、圖像生成、文字轉語音等功能。請參閱[伺服器規格](https://lemonade-server.ai/docs/server/server_spec/)了解每個端點的詳細資訊。

5. **貢獻**：Lemonade 是開源專案。請查閱[貢獻指南](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md),並尋找 [Good First Issues](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)。

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