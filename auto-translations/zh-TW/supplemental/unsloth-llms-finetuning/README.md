<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> 此手冊使用 GitHub 無法呈現的特殊標籤。請造訪 [amd.com/playbooks](https://amd.com/playbooks) 以正確預覽此內容。
<!-- @github-only:end -->

## 總覽

本手冊示範如何在 AMD 硬體上使用 Unsloth 於本機微調語言模型。

它使用一個簡短的監督式微調（SFT）範例，並以 LoRA 轉接器套用於 `unsloth/gemma-4-E4B-it`，使用 `mlabonne/FineTome-100k` 資料集的子集。目標是提供一個涵蓋設定、訓練、推論與儲存微調結果的簡單端對端工作流程。

此範例設計成實用且易於修改，讓您可以將其作為自有資料集與模型的起點。

## 您將學到什麼

- 如何設定 Unsloth 環境
- 如何使用 Unsloth 以 SFT 方式微調 LLM
- 如何將微調結果儲存於本機儲存空間

<!-- @device:halo,stx,krk -->
> **注意：** 本手冊中的微調技術至少需要 24 GB 的 GPU 記憶體與 32 GB 的系統 RAM。
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **注意：** 本手冊中的微調技術至少需要 24 GB 的 GPU 記憶體與 32 GB 的系統 RAM。
<!-- @os:end -->

<!-- @os:linux -->
> **注意：** 本手冊中的微調技術至少需要 24 GB 的**專用**GPU 記憶體與 32 GB 的系統 RAM。
<!-- @os:end -->
<!-- @device:end -->

## 為什麼選擇 Unsloth？

相較於標準設定，Unsloth 透過降低記憶體使用量並加快訓練速度，讓 LLM 微調更容易在本機硬體上執行。

在本手冊中，我們將 Unsloth 與**基於 LoRA 的 SFT** 搭配使用。這表示基礎模型大部分保持凍結，而只訓練一組小得多的轉接器權重。這非常適合本機開發，因為它比完整微調更輕量，且能更快地進行迭代。

Unsloth 也支援其他訓練方式，包括 QLoRA 與強化學習工作流程。本手冊先聚焦於最簡單的路徑：一個小型的 LoRA 微調範例，讓使用者可以執行、理解並擴充。

## 設定記憶體組態

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 檢查軟體更新
> **注意**：若未安裝 VS Code，您可以透過 Ryzen AI Developer Center 進行安裝。

<!-- @require:software-update -->
<!-- @device:end -->

## 安裝軟體先決條件

### 建立虛擬環境

<!-- @os:linux -->
<!-- @device:halo_box -->
開啟終端機並建立一個已預先安裝 AMD ROCm™ 軟體與 PyTorch 的 venv：
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
python3 -m venv unsloth-env --system-site-packages
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**授予您的使用者存取 GPU 裝置的權限**（需登出並重新登入才會生效）：

```bash
sudo usermod -aG render,video $LOGNAME
```

開啟終端機並建立一個 venv：
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv unsloth-env
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **注意：** Windows 需要 Python 3.13。

<!-- @device:halo_box -->
開啟 PowerShell 終端機並建立虛擬環境：
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
開啟 PowerShell 終端機並建立虛擬環境：
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### 安裝基本相依套件
<!-- @require:pytorch,driver -->

<!-- @test:id=verify-torch-env timeout=300 hidden=True setup=activate-venv -->
```python
import sys
import torch

print(f"Python executable: {sys.executable}")
print(f"PyTorch version: {torch.__version__}")
print(f"torch.cuda.is_available(): {torch.cuda.is_available()}")

if not torch.cuda.is_available():
    raise SystemExit("FAIL: ROCm-enabled PyTorch is not visible in this venv")

print("PASS: ROCm-enabled PyTorch is visible")
```
<!-- @test:end -->

### 額外相依套件

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **注意：** 匯入期間，Unsloth 可能會探測選用的 `bitsandbytes` 加速路徑。在某些 ROCm 版本上，您可能會看到類似 `bitsandbytes library load error: Configured ROCm binary not found` 的訊息。本手冊使用搭配 `optim="adamw_torch"` 的標準 LoRA 微調，因此我們不依賴 `bitsandbytes` 最佳化器或 4-bit QLoRA。此訊息可以安全地忽略。

<!-- @os:windows -->
> **注意：** 在 Windows ROCm 上，Unsloth 於啟動時會列印數則警告 — 請參閱下方的[已知警告](#known-warnings)。這些警告皆可安全忽略；訓練仍能正常運作。
<!-- @os:end -->

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
```python
import unsloth
import torch
from datasets import load_dataset
from transformers import TextStreamer
from unsloth import FastModel
from unsloth.chat_templates import (
    get_chat_template,
    standardize_data_formats,
    train_on_responses_only,
)
from trl import SFTTrainer, SFTConfig

print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print("PASS: All required imports succeeded")
```
<!-- @test:end -->

## 下載 Unsloth 微調腳本

本手冊在此提供一個乾淨、端對端的腳本，而非手動執行每個步驟：[test_unsloth.py](assets/test_unsloth.py)。

執行以下程式碼以執行該腳本：

```bash
python test_unsloth.py
```

<!-- @test:id=verify-script timeout=60 hidden=True -->
```python
import os
import sys
import ast

scripts = ["test_unsloth.py", "test_unsloth_ci.py"]
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing script: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

for script in scripts:
    with open(script, "r", encoding="utf-8") as f:
        ast.parse(f.read(), filename=script)
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=quick-train-unsloth timeout=2400 hidden=True setup=activate-venv -->
```bash
python test_unsloth_ci.py
```
<!-- @test:end -->

本手冊的其餘部分將概念性地逐步說明該腳本的每個主要步驟。

## 運作方式

test_unsloth.py 腳本執行以下步驟：
* **載入模型**：使用 FastModel 載入 unsloth/gemma-4-E4B-it。
* **準備資料**：標準化資料集（例如 FineTome-100k）並套用 Gemma-4 聊天範本。
* **套用 LoRA**：將轉接器新增至語言、注意力與 MLP 模組，以提高訓練效率。
* **訓練**：使用 SFTTrainer 並搭配僅回應損失遮罩。
* **推論**：執行快速產生測試以驗證效能。
* **儲存**：將 LoRA 轉接器匯出至本機。

## 主要組態

您可以修改以下常數來自訂您的執行：

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

載入模型權重時的 Unsloth 歡迎訊息與輸出範例：

![替代文字](assets/welcome.png)

## 準備資料集

我們使用以下資料集的子集：
```text
mlabonne/FineTome-100k
```
該資料集已：
* 轉換為聊天格式
* 使用 Gemma-4 聊天範本進行處理
* 清理以移除重複的 BOS 標記

## 訓練模型

該腳本會執行一個簡短的訓練示範，參數如下：
- 約 50 個步驟
- 小批次大小
- 梯度累積

在訓練期間，您將看到如下的日誌：

![替代文字](assets/training.png)


## 儲存與部署

### 本機儲存（LoRA）

該腳本會自動將 LoRA 轉接器儲存至 OUTPUT_DIR。
```python
model.save_pretrained("gemma_4_lora")  
tokenizer.save_pretrained("gemma_4_lora")
```

<!-- @test:id=verify-unsloth-lora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_lora_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = (
    glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) +
    glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
)
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: Unsloth LoRA output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end -->

### 儲存合併後的模型（供 vLLM 使用）

<!-- @os:windows -->
> **注意：** vLLM 不支援 Windows。若要在 Windows 上部署您微調的模型，請使用 llama.cpp（請參閱下方的[匯出 GGUF](#export-gguf-for-llamacpp)）或將合併後的模型傳輸至執行 vLLM 的 Linux 機器。
<!-- @os:end -->

<!-- @os:linux -->
若要以 vLLM 部署，請將轉接器合併為完整模型：
```python
model.save_pretrained_merged("gemma-4-finetune", tokenizer)
```
<!-- @os:end -->

<!-- @test:id=verify-unsloth-merged-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_merged_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing merged model directory: {out_dir}")
    sys.exit(1)

required = [
    "config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required merged files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Merged model output looks correct")
```
<!-- @test:end -->

### 匯出 GGUF（供 llama.cpp 使用）

直接轉換為 GGUF 以進行本機推論：
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## 已知警告

以下警告是 Unsloth 在 Windows ROCm 上啟動時所列印的訊息，全部都可以安全地忽略：

| 警告 | 原因 | 可以安全忽略？ |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes 沒有 Windows ROCm 建置版本 | 是——本手冊使用 `adamw_torch`，而非 bnb |
| `No ROCm platform found for torch.distributed` | Windows 上的 ROCm 缺乏分散式訓練支援 | 是——單一 GPU 訓練不受影響 |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth 會標記非 Linux 建置版本 | 是——Windows ROCm 可用於單一 GPU SFT |
| `triton is not available` | Triton 沒有 Windows 建置版本 | 是——Unsloth 會回退使用 PyTorch 核心 |

儘管出現這些警告，訓練仍會正確進行。
<!-- @os:end -->

## 後續步驟
- 嘗試使用 [Unsloth Studio](https://unsloth.ai/docs/new/studio)，這是一個直覺易用的 Unsloth 圖形化介面
- 使用您自己的特定資料集進行訓練
- 嘗試以不同的超參數進行微調
- 使用 vLLM 或 llama.cpp 進行部署
- 嘗試使用 QLoRA 以降低記憶體需求

## 資源

以下是一些額外資源，能協助您進一步了解 Unsloth 與微調：

* [Unsloth 文件](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth 微調指南](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)