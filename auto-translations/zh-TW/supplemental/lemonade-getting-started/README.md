<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> 此 playbook 使用 GitHub 無法渲染的特殊標籤。請前往 [amd.com/playbooks](https://amd.com/playbooks) 正確預覽此內容。
<!-- @github-only:end -->

## 概覽

🍋 **Lemonade** 是一個開源的本地 AI 伺服器，讓您可以直接在自己的硬體上執行大型語言模型（LLM）、圖像生成器和音訊模型。它透過業界標準的 **OpenAI API** 公開這些模型，因此任何能與 OpenAI 搭配使用的應用程式都能立即與 Lemonade 搭配使用。完成本 playbook 後，您將能使用 Lemonade 在自己的機器上本地執行模型。

## 您將學到什麼

完成本 playbook 後，您將能夠：

* **安裝 Lemonade Server** 並驗證其正在執行。
* **使用單一指令下載 LLM 並與其對話**。
* **探索網頁 UI** 並嘗試不同的模態，例如視覺、語音轉文字和圖像生成。
* **在 Vulkan 和 AMD ROCm™ 軟體之間切換 GPU 後端**。
* **使用相容於 OpenAI 的 API 建立由本地 LLM 驅動的 Python 應用程式**。
<!-- @device:halo_box,halo,stx,krk -->
* **使用混合（Hybrid）和 FLM 執行模式在 AMD Neural Processing Unit (NPU) 上執行模型**，適用於 AMD Ryzen™ AI 硬體。
<!-- @device:end -->

## 設定記憶體配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 檢查軟體更新

<!-- @require:software-update -->
<!-- @device:end -->

## 安裝軟體先決條件

開始之前，請確認您具備：

- 執行 **Windows 11** 或受支援 **Linux** 發行版（Ubuntu 24.04+、Fedora、Debian）的 PC
- 建議使用 **16 GB RAM**，適用於步驟 1–7 中使用的執行時期模型（`Gemma-4-E2B-it-GGUF`，約 3 GB）。若您想使用步驟 6 中較大的程式碼生成模型（`Qwen3.5-35B-A3B-GGUF`，約 20 GB），建議使用 **32 GB+**。
- **約 4–30 GB 的可用磁碟空間**，視您下載的模型而定。本指南中最大的模型約為 20 GB。
- **Python 3.10–3.13**（用於 Python 應用程式章節）
- 網際網路連線（有線或無線）
<!-- @device:halo_box,halo,stx,krk -->
- [選用] 搭載 AMD XDNA 2 NPU（Ryzen AI 300/400/Max 300 系列或 Z2 Extreme）的裝置，並已從 [Ryzen AI Software Installation Instructions](https://ryzenai.docs.amd.com/en/latest/inst.html#install-npu-drivers) 安裝最新驅動程式，若您想在 NPU 上執行模型。
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

## 核心概念 — 本地 AI 伺服器的運作方式

在執行模型之前，值得先了解*為何*要這樣設定。Lemonade 是一個**本地模型伺服器**，一個將 AI 模型載入記憶體並透過 HTTP 向應用程式公開的程序，就像雲端 AI 服務一樣。

### 為何需要伺服器？

| 優點 | 對您的意義 |
|---------|----------------------|
| **簡化整合** | 應用程式只需與一個 HTTP API 溝通，無需處理特定硬體的 C++ 或 Python 函式庫。 |
| **共享模型** | 單一已載入的模型可同時服務多個應用程式，不會有重複副本佔用您的 RAM。 |
| **雲端到本地的可攜性** | 為 OpenAI 雲端 API 編寫的程式碼只需更改一個 URL 即可與 Lemonade 搭配使用。 |
| **關注點分離** | 模型管理、串流和容錯由伺服器處理，讓開發人員可以專注於自己的應用程式。 |

### OpenAI API 標準

Lemonade 實作了 **OpenAI API**，這是 ChatGPT、Azure OpenAI 和數十種其他服務所使用的相同介面。對話模型很簡單：

| 角色 | 誰在說話 |
|------|---------------|
| **system** | 給模型的指示（角色設定、限制、可用工具） |
| **user** | 來自人類（或應用程式）給模型的訊息 |
| **assistant** | 由模型生成的回應 |

這意味著任何支援 OpenAI 的函式庫或應用程式，只需在 Lemonade Server 執行時將其指向 `http://localhost:13305/api/v1`，即可與 Lemonade 溝通。

## 主要活動 — 您的第一次本地 AI 對話

讓我們下載一個 LLM 並與它對話，完全在您自己的機器上執行 AI。

### 步驟 1：下載並執行模型

Lemonade 附帶一個精選的模型庫。讓我們從 **Gemma-4-E2B-it** 開始，這是一個功能強大且緊湊的模型，包含視覺支援。開啟終端機並執行：

```
lemonade run Gemma-4-E2B-it-GGUF
```

這個單一指令執行三件事：

1. **下載**模型（約 3 GB）從 Hugging Face，如果尚未下載的話。（可能需要一些時間）
2. **啟動** Lemonade Server 程序，監聽連接埠 13305。
3. **開啟 Lemonade App**，讓您可以開始與模型對話。


<!-- @os:windows -->
在 Windows 上，Lemonade App 會自動啟動，您可以立即開始對話。如果您安裝的是 `minimal.msi` 套件，則不包含該應用程式。若要開始對話，請開啟網頁瀏覽器並前往 `http://localhost:13305`。
<!-- @os:end -->

<!-- @os:linux -->
在 Linux 上，請開啟瀏覽器並前往 `http://localhost:13305` 以存取網頁應用程式。
<!-- @os:end -->

嘗試輸入一個問題：

```
What are three fun facts about lemons?
```

模型將直接在對話視窗中回應。**恭喜！您正在本地執行大型語言模型。**

![顯示日誌的 Lemonade App](../../dependencies/assets/ChatwithLogs.png)

在 Lemonade App 的伺服器日誌面板中，您可以在每次回應後找到有關模型效能的遙測資料。例如：

```
 === Telemetry ===
Input tokens:  24
Output tokens: 527
TTFT (s):      0.052
TPS:           95.99
=================
```

### 步驟 2：探索網頁介面和不同模態

Lemonade 包含一個內建的網頁介面，您可以在其中：

- 在熟悉的對話視窗中**與已載入的模型互動**
- 在「模型管理員」標籤中**瀏覽模型**
- 只需一鍵即可**下載新模型**

嘗試使用網頁 UI 中的**模型管理員**標籤切換不同模態，您可以依配方或依類別瀏覽模型：

1. **視覺：** 您已載入的 `Gemma-4-E2B-it-GGUF` 模型支援視覺功能。將圖像貼入對話框並請模型描述它。
2. **圖像生成：** 在「圖像」類別中，從模型管理員下載圖像模型（例如 `SDXL-Turbo`），然後使用 Lemonade 圖像生成器輸入提示詞並在本地生成圖像。
3. **音訊：** 在「音訊」類別中，下載音訊模型（例如 `Whisper-Tiny`），它可以進行語音轉文字。提供音訊錄音以在本地轉錄。若要進行文字轉語音，請嘗試「語音」類別中的其中一個模型，例如 `kokoro-v1`。

![Lemonade 的多模態功能](../../dependencies/assets/multi_modality.png)

### 步驟 3：嘗試使用不同後端的模型

如果您將滑鼠懸停在 Lemonade App 中的模型上，您會看到一個齒輪圖示。點擊它可讓您選擇模型的選項，包括選擇所需的後端。

預設情況下，Lemonade 使用 Vulkan 進行 GPU 加速。如果您有受支援的 AMD 獨立 GPU，可以切換到 ROCm。

![Lemonade 選擇後端](../../dependencies/assets/lemonademodeloptions.png)

若要管理已安裝的後端，請點擊最左欄中的後端按鈕。

或者，您可以使用以下指令指定後端：

```
lemonade run Gemma-4-E2B-it-GGUF --llamacpp rocm
```

您也可以使用環境變數 `LEMONADE_LLAMACPP` 設定預設後端，可用值為：`vulkan`、`rocm` 或 `cpu`。

---

## 深入探索 — 使用 Python 建立 AI 驅動的應用程式

本地 AI 伺服器的真正威力在於，任何應用程式只需幾行程式碼即可連接到它。為了證明這一點，讓我們建立一個小型但功能完整的**學習閃卡生成器**，您給它一個主題，它生成閃卡，您可以互動式地自我測驗。

### 步驟 4：啟動伺服器

確認 Lemonade 伺服器正在執行。它通常在安裝後會自動在背景啟動。若要驗證，請執行：

```
lemonade status
```

您應該會看到類似以下的訊息：`Server is running on port 13305`。

如果伺服器未執行，請開啟 Lemonade 應用程式來啟動它。使用預設連接埠 **13305**（您可以從系統匣圖示確認或選擇此連接埠）。

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

### 步驟 6：建立閃卡應用程式

讓我們下載一個不同的模型來生成程式碼：`Qwen3.5-35B-A3B-GGUF`。這是一個大型（約 20 GB）且效能優異的模型，最適合搭載 32 GB+ RAM 的系統。如果您的可用 RAM 較少，請改用 `Qwen3.5-9B-GGUF`（約 6 GB）。

您可以從 UI 下載，或執行以下指令：
```
lemonade run Qwen3.5-35B-A3B-GGUF
```

將以下提示詞輸入 Lemonade Chat UI 以生成簡單閃卡應用程式的程式碼。

我們將使用 Qwen3.5-35B-A3B-GGUF（較大的模型，更擅長編寫程式碼）來生成我們的 Python 應用程式，而應用程式本身將在執行時呼叫 Gemma-4-E2B-it-GGUF（您已下載的較小模型）。然後可以將程式碼複製到您選擇的檔案中，以便在 Python 中執行。

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

> **提示**：我們透過徹底的提示詞設計和使用雙模型系統來優化資源和速度，遵循了標準工程實踐。

為了方便起見，我們在 [`flashcards.py`](assets/flashcards.py) 中提供了範例輸出。歡迎將其下載到您的目錄。無論如何，您現在應該有一個可以執行的 Python 檔案。

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


### 步驟 7：執行生成的程式碼

```bash
# Ensure the virtual environment is running
python flashcards.py # replace with your file name
```

**以下是您應該看到的內容：**

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

在大約 150 行程式碼中，您已建立了一個由本地 LLM 驅動的功能完整學習工具。無需管理 API 金鑰，無使用費用，且您的資料永遠不會離開您的機器。

> **關鍵洞察：** 請注意，`client = OpenAI(base_url=...) ` 這一行是將此應用程式與 Lemonade 而非 OpenAI 雲端綁定的*唯一*之處。其餘程式碼與您針對任何相容於 OpenAI 的服務所編寫的程式碼完全相同。如果您曾使用過 OpenAI Python 函式庫，您已經知道如何使用 Lemonade 建立應用程式。

### 這展示了什麼

這個小型應用程式展示了幾種真實世界的整合模式：

| 模式 | 出現位置 |
|---------|-----------------|
| **系統提示詞** | `"system"` 訊息告訴 LLM 輸出結構化的 JSON |
| **結構化輸出** | 應用程式將 LLM 的回應解析為 JSON 以建立閃卡 |
| **無狀態請求** | 每次 `generate_flashcards()` 呼叫都是獨立的 |
| **錯誤處理** | `try/except` 優雅地處理 LLM 輸出不是有效 JSON 的情況 |

這些相同的模式可擴展到任何應用程式，例如聊天機器人、程式碼助理、內容生成器、自動化工具。

#### 額外挑戰

* 若要增加挑戰，請嘗試更新應用程式，讓閃卡向使用者朗讀，參考[此處](https://github.com/lemonade-sdk/lemonade/blob/main/examples/api_text_to_speech.py)提供的範例。

---

<!-- @device:halo_box,halo,stx,krk -->
## 在 NPU 上執行模型（選用）

如果您有 Ryzen AI 300/400/Max 300 系列或 Z2 Extreme，您的裝置內建了 **Neural Processing Unit (NPU)**，這是一個專為 AI 工作負載設計的專用晶片。在 NPU 上執行模型比使用 GPU 更省電，這使其非常適合背景 AI 任務、較長的工作階段和電池供電的使用情境。

Lemonade 支援三種 NPU 執行模式，全部透過相同的 OpenAI API 透明呈現：

| 模式 | 運作方式 | 配方 | 範例模型 |
|------|-------------|--------|----------------|
| **混合（NPU + iGPU）** | NPU 處理提示詞，iGPU 生成 token | OGA（`oga-hybrid`） | Qwen3-4B-Hybrid |
| **僅 NPU** | 整個推論在 NPU 上執行 | Ryzen AI LLM（`ryzenai-llm`） | Qwen-2.5-7B-Instruct-NPU |
| **FLM** | 在 NPU 上使用 FastFlowLM 引擎，針對 AMD XDNA2 優化 | FLM（`flm`） | qwen3.5-4b-FLM |

### 需求

- **AMD Ryzen AI 300/400 系列或 Z2 系列**處理器
- 對於 **FLM** 模型：FLM 執行時期可從 Lemonade 應用程式內安裝，或在執行 FLM 模型時 Lemonade 會自動安裝 FLM 執行時期。若要深入了解 FastFlowLM，請參閱[此處](https://fastflowlm.com/docs/)。


### 步驟 8：執行混合模型

混合模型在 NPU 和 iGPU 之間分配工作，以達到速度和效率的良好平衡。在 Lemonade App 中，從 `Ryzen AI LLM` 清單中選擇一個模型，例如 `Qwen3-4B-Hybrid`，或使用以下指令執行：

```
lemonade run Qwen3-4B-Hybrid
```

Lemonade 會自動偵測您的 NPU 並安裝 **Ryzen AI LLM** 後端。

> **底層發生了什麼？** 當您傳送訊息時，NPU 會並行處理您的整個提示詞（這稱為「預填充」）。然後，iGPU 接手，一次生成一個 token 的回應（這稱為「解碼」）。這種混合方式充分發揮了每個晶片的優勢。

### 步驟 9：執行 FLM 模型

FastFlowLM（FLM）模型專門針對 AMD 的 XDNA2 NPU 架構進行優化，對於其大小而言可以非常快速。例如，從 `FastFlowLM NPU` 清單中選擇 `qwen3.5-4b-FLM`，或使用以下指令：

<!-- @os:windows -->
若要在 Windows 上啟用 `FastFlowLM`：

* 開啟 `Backends Manager` 選單。
* 找到 `FastFlowLM NPU` 後端類別。
* 點擊「安裝 NPU」。
* 安裝完成後，FFLM 下拉選單下將提供約 36 個預設模型。
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @device:halo_box,halo,stx,krk -->
當 `Lemonade` App 首次啟動時，`FastFlowNPU` 後端預設未啟用。
本地應用程式將開啟安裝頁面，引導您完成設定。

若要在 Linux 上啟用 `FastFlowLM`：

* 開啟 `Lemonade` App。
* 造訪[官方 FLM](https://lemonade-server.ai/flm_npu_linux.html) 文件，並依照安裝頁面選擇您的 Linux 發行版，按照 FLM 的安裝步驟操作。
* 依照安裝頁面的指示啟用 backports。
* 從[標籤頁面](https://github.com/FastFlowLM/FastFlowLM/tags)下載最新的 `v0.9.x` 版本。
<!-- @device:end -->

<!-- @device:halo_box -->
>[!Note]
對於 AMD Halo Developer Platform，請確保選擇 Debian 13。
```
fastflowlm_0.9.X_debian13_amd64.deb
```
<!-- @device:end -->

<!-- @device:halo,stx,krk -->
```
fastflowlm_0.9.X_ubuntuY.Z_amd64.deb
```
<!-- @device:end -->
* 安裝已下載的 `.deb` 套件。
* 建議：退出 `Lemonade App` 並重新開啟，以便偵測到變更。
* 建議：開啟 `Backends Manager` 並點擊「安裝 `FastFlowNPU` 後端」。
<!-- @device:end -->
<!-- @os:end -->

<!-- @device:halo_box,halo,stx,krk -->
成功安裝後，您應該會在 **Lemonade Desktop App** 的**下載管理員**中看到 `flm:npu` 已完成。
<p align="center">
  <img width="400" height="400" src="assets/FFLM-installationWizard.png" />
</p>
然後您可以選擇任何可用的 FFLM 模型並開始使用 NPU 後端。

對於特定模型，請從[模型頁面](https://fastflowlm.com/docs/models/qwen/)下載所需模型，並使用文件中提供的 Shell 指令進行驗證。
```
flm run qwen3.5-4b-FLM
```
或透過 
```
lemonade run qwen3.5-4b-FLM
```

FLM 模型包含一些最受歡迎的架構（Gemma 3、Qwen 3、Llama 3 和 DeepSeek R1），大小從不到 1 GB 到超過 13 GB 不等。
Lemonade 會自動偵測您的 NPU 並安裝 **FastFlowLM NPU** 後端。

<!-- @os:windows -->
> **提示：** 若要獲得最佳 NPU 效能，請啟用 turbo 模式：
> ```
> cd C:\Windows\System32\AMD
> .\xrt-smi configure --pmode turbo
> ```
<!-- @os:end -->

### 切換模型

步驟 6 中的閃卡應用程式也適用於 NPU 模型，只需更改模型名稱：

```python
# In flashcards.py, swap the model to run on NPU instead of GPU
response = client.chat.completions.create(
    model="Qwen3-4B-Hybrid",  # swap in any NPU/Hybrid/FLM model
    messages=messages,
)
```
<!-- @device:end -->

## 後續步驟

您已在自己的硬體上執行了本地 AI 伺服器，以下是接下來可以做的事：

1. **連接您喜愛的應用程式**：Lemonade 可直接與 [VS Code Copilot](https://marketplace.visualstudio.com/items?itemName=lemonade-sdk.lemonade-sdk)、[Open WebUI](https://lemonade-server.ai/docs/server/apps/open-webui/)、[Continue](https://lemonade-server.ai/docs/server/apps/continue/)、[n8n](https://n8n.io/integrations/lemonade-model/) 以及[更多應用程式](https://lemonade-server.ai/marketplace)搭配使用。

2. **瀏覽更多模型**：探索完整的[模型庫](https://lemonade-server.ai/docs/server/server_models/)，尋找針對程式碼撰寫、推理、視覺等優化的模型。使用 Lemonade App 或 `lemonade list` 查看可用的模型。

3. **解鎖 ROCm GPU 加速**：如果您有受支援的 AMD GPU，請切換到 ROCm 後端：`lemonade config set llamacpp.backend=rocm`。請參閱[受支援的 AMD GPU](https://github.com/lemonade-sdk/lemonade?tab=readme-ov-file#supported-configurations)。

4. **閱讀完整 API 規格**：Lemonade 支援聊天補全、嵌入、音訊轉錄、圖像生成、文字轉語音等功能。請參閱 [Server Spec](https://lemonade-server.ai/docs/server/server_spec/) 了解每個端點。

5. **貢獻**：Lemonade 是開源的。查看[貢獻指南](https://github.com/lemonade-sdk/lemonade/blob/main/docs/contribute.md)並尋找[適合新手的議題](https://github.com/lemonade-sdk/lemonade/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)。