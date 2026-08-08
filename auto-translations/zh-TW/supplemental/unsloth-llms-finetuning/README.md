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

本手冊示範如何在 AMD 硬體上使用 Unsloth 於本機微調語言模型。

它使用一個簡短的監督式微調（SFT）範例，並在 `unsloth/gemma-4-E4B-it` 上搭配 LoRA 轉接器，使用 `mlabonne/FineTome-100k` 資料集的子集。目標是為您提供一個涵蓋設定、訓練、推論及儲存微調結果的簡易端對端工作流程。

此範例的設計著重於實用性與易於修改，因此您可以將其作為自身資料集與模型的起點。

## 您將學到什麼

- 如何設定 Unsloth 環境
- 如何使用 Unsloth 以 SFT 微調 LLM
- 如何將微調結果儲存至本機儲存空間

<!-- @device:halo,stx,krk -->
> **注意：** 本手冊中的微調技術至少需要 **64 GB 的系統記憶體**，其中至少需要 **24 GB 可供 GPU 使用**（此 24 GB 為 64 GB 的一部分，而非額外附加）。
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **注意：** 本手冊中的微調技術至少需要 **24 GB 的總 GPU 記憶體**與 **32 GB 的系統記憶體**。
> - 在 Windows 上，總 GPU 記憶體結合了顯示卡的專用 VRAM 與共用 GPU 記憶體（由系統記憶體借用）。
> - 因此，專用 VRAM 少於 24 GB 的顯示卡仍可透過使用共用 GPU 記憶體來補足差額，以執行本手冊的內容。
<!-- @os:end -->

<!-- @os:linux -->
> **注意：** 本手冊中的微調技術需要至少具備 **24 GB 專用 GPU 記憶體**與 **32 GB 系統記憶體**的顯示卡。
> - 在 Linux 上，訓練完全在顯示卡的專用 VRAM 中執行。
> - 當 VRAM 用盡時，不會回退至共用 GPU 記憶體（系統記憶體）。
> - 專用 VRAM 少於 24 GB 的顯示卡在 Linux 上訓練時將會發生記憶體不足的情況，即使系統擁有充足的記憶體也一樣。
<!-- @os:end -->
<!-- @device:end -->

## 為什麼選擇 Unsloth？

相較於標準設定，Unsloth 藉由降低記憶體使用量並加快訓練速度，讓在本機硬體上執行 LLM 微調變得更容易。

在本手冊中，我們將 Unsloth 與 **基於 LoRA 的 SFT** 搭配使用。這代表基礎模型大多維持凍結狀態，而僅訓練一組小得多的轉接器權重。這非常適合本機開發，因為它比完整微調更輕量，且能更快速地反覆調整。

Unsloth 也支援其他訓練方法，包括 QLoRA 與強化學習工作流程。本手冊首先聚焦於最簡單的路徑：一個使用者可以執行、理解並延伸的小型 LoRA 微調範例。

## 設定記憶體組態

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 檢查軟體更新
> **注意**：若尚未安裝 VS Code，您可以透過 Ryzen AI Developer Center 進行安裝。

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

開啟終端機並建立 venv：
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
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **注意：** 在匯入期間，Unsloth 可能會探測選用的 `bitsandbytes` 加速路徑。在某些 ROCm 版本上，您可能會看到類似 `bitsandbytes library load error: Configured ROCm binary not found` 的訊息。本手冊使用搭配 `optim="adamw_torch"` 的標準 LoRA 微調，因此我們不依賴 `bitsandbytes` 最佳化器或 4 位元 QLoRA。此訊息可安全忽略。

<!-- @os:windows -->
> **注意：** 在 Windows ROCm 上，Unsloth 啟動時會列印多則警告訊息——請參閱下方的[已知警告](#known-warnings)。這些訊息皆可安全忽略；訓練仍會正常運作。
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

## 下載 Unsloth 微調指令碼

本手冊提供了一份簡潔的端對端指令碼，而非要求您手動執行每個步驟：[test_unsloth.py](assets/test_unsloth.py)。

執行下列程式碼以執行此指令碼：

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

本手冊的其餘部分將以概念方式逐一說明此指令碼的各個主要步驟。

## 運作方式

test_unsloth.py 指令碼執行以下步驟：
* **載入模型**：使用 FastModel 載入 unsloth/gemma-4-E4B-it。
* **準備資料**：標準化資料集（例如 FineTome-100k）並套用 Gemma-4 聊天範本。
* **套用 LoRA**：將轉接器新增至語言、注意力與 MLP 模組，以進行高效訓練。
* **訓練**：使用 SFTTrainer 並搭配僅限回應的損失遮罩。
* **推論**：執行快速生成測試以驗證效能。
* **儲存**：將 LoRA 轉接器匯出至本機。

## 主要組態

您可以修改下列常數以自訂您的執行方式：

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

載入模型權重時 Unsloth 歡迎訊息與輸出的範例：

![alt text](assets/welcome.png)

## 準備資料集

我們使用以下資料集的子集：
```text
mlabonne/FineTome-100k
```
該資料集已：
* 轉換為聊天格式
* 使用 Gemma-4 聊天範本進行處理
* 經過清理以移除重複的 BOS 權杖

## 訓練模型

此指令碼會執行一個簡短的訓練示範，參數如下：
- 約 50 個步驟
- 較小的批次大小
- 梯度累積

在訓練期間，您將會看到如下的記錄：

![alt text](assets/training.png)


## 儲存與部署
### 本地儲存（LoRA）

腳本會自動將 LoRA adapters 儲存到 OUTPUT_DIR。
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

### 儲存合併模型（適用於 vLLM）

<!-- @os:windows -->
> **注意：** vLLM 不支援 Windows。若要在 Windows 上部署您微調後的模型，請使用 llama.cpp（請參閱下方的 [匯出 GGUF](#export-gguf-for-llamacpp)），或將合併後的模型轉移到執行 vLLM 的 Linux 機器上。
<!-- @os:end -->

<!-- @os:linux -->
若要使用 vLLM 進行部署，請將 adapters 合併為完整模型：
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

### 匯出 GGUF（適用於 llama.cpp）

直接轉換為 GGUF 以進行本地推論：
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## 已知警告

以下警告是 Unsloth 在 Windows ROCm 上啟動時所印出的訊息，皆可安全忽略：

| 警告 | 原因 | 是否可安全忽略？ |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes 沒有 Windows ROCm 版本 | 是 — 本教學使用 `adamw_torch`，而非 bnb |
| `No ROCm platform found for torch.distributed` | Windows 上的 ROCm 不支援分散式訓練 | 是 — 單一 GPU 訓練不受影響 |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth 會標記非 Linux 的建置版本 | 是 — Windows ROCm 可支援單一 GPU 的 SFT |
| `triton is not available` | Triton 沒有 Windows 版本 | 是 — Unsloth 會退回使用 PyTorch kernels |

儘管出現這些警告，訓練仍會正常進行。
<!-- @os:end -->

## 後續步驟
- 試試看 [Unsloth Studio](https://unsloth.ai/docs/new/studio)，這是一個直覺易用的 Unsloth GUI
- 使用您自己的特定資料集進行訓練
- 嘗試使用不同的超參數進行微調
- 使用 vLLM 或 llama.cpp 進行部署
- 試試看 QLoRA 以取得較低記憶體用量的設定

## 資源

以下是一些額外資源，協助您進一步瞭解 Unsloth 與微調：

* [Unsloth 文件](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth 微調指南](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)