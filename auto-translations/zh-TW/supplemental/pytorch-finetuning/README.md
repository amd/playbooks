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

本教學提供了使用 PyTorch 與 ROCm 微調大型語言模型（LLM）的逐步範例。內容涵蓋多種技術，從標準微調到記憶體效率高的參數高效微調（PEFT）策略，讓您能夠輕鬆地為自身需求調整模型。

**使用模型**：google/gemma-3-4b-it（QLoRA 腳本：openai/gpt-oss-20b） *(若為受限模型，請參閱 [Enable HF authentication](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models))*  
**硬體**：支援 ROCm 的 AMD Radeon™ GPU  
**框架**：PyTorch + Hugging Face（Transformers、PEFT、Transformer Reinforcement Learning (TRL)）

<!-- @device:halo,halo_box -->
> **注意：** 
> - 完整微調至少需要 **64 GB 系統記憶體**，其中至少 **32 GB 可供 GPU 使用**（這 32 GB 是 64 GB 的一部分，並非額外增加）。
> - 您也可以透過在提供的訓練腳本中替換模型，嘗試其他模型架構，包括 **GPT-OSS-20B**。
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **注意：** LoRA 與 QLoRA 微調至少需要 **32 GB 系統記憶體**，其中至少 **16 GB 可供 GPU 使用**（這 16 GB 是 32 GB 的一部分，並非額外增加）。
<!-- @os:end -->

<!-- @os:windows -->
> **注意：** LoRA 微調至少需要 **32 GB 系統記憶體**，其中至少 **16 GB 可供 GPU 使用**（這 16 GB 是 32 GB 的一部分，並非額外增加）。
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **注意：** LoRA 與 QLoRA 微調需要至少具備 **16 GB 專用 GPU 記憶體** 及 **32 GB 系統記憶體** 的顯示卡。
> - 在 Linux 上，訓練完全在顯示卡的專用 VRAM 中執行。
> - 當 VRAM 用盡時，不會回退使用共用 GPU 記憶體（系統記憶體）。
> - 在 Linux 上，專用 VRAM 低於 16 GB 的顯示卡在訓練期間將會記憶體不足，即使系統擁有充足的記憶體也是如此。
<!-- @os:end -->

<!-- @os:windows -->
> **注意：** LoRA 微調至少需要 **16 GB 總 GPU 記憶體** 及 **32 GB 系統記憶體**。
> - 在 Windows 上，總 GPU 記憶體結合了顯示卡的專用 VRAM 與共用 GPU 記憶體（借用自系統記憶體）。
> - 因此，專用 VRAM 低於 16 GB 的顯示卡仍可透過使用共用 GPU 記憶體來彌補差額，執行此教學。
<!-- @os:end -->
<!-- @device:end -->

## 您將學到什麼

- 如何使用 LoRA、QLoRA 及完整微調，搭配 PyTorch 與 ROCm 微調 LLM
- 如何儲存並部署您微調後的模型
- 如何監控訓練過程並除錯常見問題

<!-- @device:halo_box,halo,stx,krk -->
## 設定記憶體組態

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## 檢查軟體更新
> **注意**：若尚未安裝 VS Code，您可以透過 Ryzen AI Developer Center 進行安裝。

<!-- @require:software-update -->
<!-- @device:end -->

## 安裝軟體必要條件

#### 建立虛擬環境

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update 
sudo apt install -y python3-venv 
python3 -m venv finetune-venv --system-site-packages 
source finetune-venv/bin/activate 
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source finetune-venv/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**授予您的使用者存取 GPU 裝置的權限**（登出並重新登入後生效）：

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv finetune-venv
source finetune-venv/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source finetune-venv/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=180 -->
```powershell
python -m venv finetune-venv --system-site-packages
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=180 -->
```powershell
python -m venv finetune-venv
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

#### 安裝基本相依套件
<!-- @require:pytorch -->

#### 額外相依套件

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows：** 此處僅測試並支援核心套件。**bitsandbytes 在 Windows 上並未獲得良好支援**，因此 Windows 安裝時將其省略；請在 Windows 上使用 LoRA 或完整微調（QLoRA 需要 bitsandbytes，僅適用於 Linux）。
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### 啟用 HF 驗證（受限或自訂／非預先安裝的模型）

在此範例中，我們使用 **google/gemma-3-4b-it**，這是一個**受限**模型。您必須先在 Hugging Face 上接受該模型的條款，然後進行驗證，訓練腳本才能下載此模型。

1. **接受授權條款：** 開啟 [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it)，登入（或建立帳號），並在模型頁面上接受授權條款（例如「Agree and access repository」）。
2. **安裝並登入：** 安裝 Hugging Face CLI，然後執行標準登入：

```bash
pip install huggingface_hub
hf auth login
```

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['train_qlora.py', 'train_lora.py', 'train_full_finetuning.py']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in scripts:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=verify-imports timeout=60 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import AutoPeftModelForCausalLM
from trl import SFTTrainer

print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @test:id=verify-package-version timeout=60 hidden=True setup=activate-venv -->
```python
import importlib.metadata as md

pkgs = [
    "torch", "transformers", "trl", "peft", "accelerate",
    "datasets", "safetensors", "fsspec", "bitsandbytes",
    "huggingface_hub", "tokenizers",
]
for p in pkgs:
    try:
        print(f"{p}: {md.version(p)}")
    except md.PackageNotFoundError:
        print(f"{p}: NOT INSTALLED")
```
<!-- @test:end -->

<!-- @test:id=quick-train-lora timeout=600 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_lora.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=quick-train-qlora timeout=600 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_qlora.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=quick-train-full-finetuning timeout=1200 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_full_finetuning.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->
<!-- @device:end -->
---

## 了解各項技術

### 什麼是 LoRA？

**LoRA（低秩適應）** 會凍結基礎模型，僅訓練加入特定層的小型「適配器」矩陣。

- **核心概念**：我們不再更新具有數百萬參數的龐大權重矩陣，而是學習一個低秩更新（兩個小矩陣，其乘積的參數量遠少於原本）。這能大幅降低可訓練參數量與 VRAM 使用量，同時維持大部分完整微調的品質。

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### 什麼是 QLoRA？

**QLoRA** 結合了 **4 位元量化** 與 **LoRA**。基礎模型以 4 位元載入（可大幅節省記憶體），僅 LoRA 適配器以較高精度進行訓練。因此您可以同時獲得 LoRA 的參數效率與更低的 VRAM 使用量，與全精度 LoRA 相比僅有些微品質上的取捨。請注意，4 位元量化可能導致數值不穩定（損失值突增或出現 NaN），因此在 VRAM 充足的情況下，使用者通常可能更偏好使用 **LoRA**。

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **注意**：對於像 `openai/gpt-oss-20b` 這類的 MXFP4 基礎模型，我們建議使用 **LoRA**（`train_lora.py`）而非 QLoRA。QLoRA 腳本的 `bitsandbytes` 4 位元路徑通常會將 MXFP4 權重反量化為 BF16，因此執行方式會與標準 LoRA 相同。原生 MXFP4 需要從原始碼建置的 `bitsandbytes`，以及相符的 Transformers/Triton/kernels 堆疊。請參閱 [Transformers MXFP4 文件](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4)。

---
### 2. 選擇您的方法

| 方法 | 記憶體 | 速度 | 品質 | 最適合 |
|--------|--------|-------|---------|----------|
| **QLoRA**（僅限 Linux） | 12-16GB | 最快 | 90-95% | 低記憶體使用量 |
| **LoRA** | 24-32GB | 快 | 95-98% | 平衡的方式 |
| **Full** | 80GB+ | 最慢 | 100% | 最高品質 |

### 3. 執行訓練

**資料集與模型學習的內容**  
這些腳本會將資料集轉換成對話範例。舉例來說，QLoRA 腳本使用 **Abirate/english_quotes**：每個範例會變成類似以下的使用者─助理配對：

- **使用者：**「給我一句關於：&lt;tag&gt; 的名言」
- **助理：**「&lt;quote&gt; – &lt;author&gt;」

微調會教導模型回應要求提供某主題名言的提示，並以 `<quote text> - <author>` 的格式回傳。LoRA 與完整微調腳本則使用 **databricks/databricks-dolly-15k**（通用的指令/回應配對），因此實際任務依腳本而異；但概念相同——將模型調整以符合您所選的資料集與格式。

以下是可用訓練方法的摘要。每種方法都連結到其腳本，並提供簡短說明以協助您選擇合適的方式。

| 腳本                           | 方法            | 說明                                                                                                         | 典型 VRAM | 建議對象                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | 訓練小型的適配器矩陣，同時凍結基礎模型。速度快 3–5 倍；品質約為完整訓練的 95–98%。                         | 24–32GB      | 進階使用者；多個適配器；較多 VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *（僅限 Linux）*             | **QLoRA**       | 4-bit 量化 + LoRA 適配器。記憶體使用量最低、速度最快，品質略有取捨。需要 `bitsandbytes`（僅限 Linux）。                            | 12–16GB      | 大多數使用者；快速實驗；有限 VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **完整微調** | 更新所有模型參數。最高品質；記憶體與運算需求最高。                                    | 40GB+        | 最高品質；研究用途；大容量 VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **注意：** 完整微調（`train_full_finetuning.py`）可能需要超過 64GB 的系統記憶體，在此裝置上可能無法執行。請考慮改用 LoRA 或 QLoRA。
<!-- @os:end -->

<!-- @os:windows -->
> **注意：** 完整微調（`train_full_finetuning.py`）可能需要超過 64GB 的系統記憶體，在此裝置上可能無法執行。請考慮改用 LoRA。
<!-- @os:end -->
<!-- @device:end -->

只需選擇您偏好的 `Training method`，下載對應的腳本，並在保持虛擬環境啟用的狀態下執行以下指令： 

```python
python3 train_<method_name>.py.
```

## 使用您微調後的模型

### 完整微調後

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "output-gemma-3-4b-it-full",     # Directory containing your fully fine-tuned checkpoint
    device_map="auto",
    torch_dtype="auto"            # Use BF16 if your GPU supports it, else "auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-it-full")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### LoRA/QLoRA 訓練後

```python
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

# Load model with LoRA or QLoRA adapters
model = AutoPeftModelForCausalLM.from_pretrained(
    "output-gpt-oss-20b-qlora",   # or "output-gemma-3-4b-it-lora" depending on your training
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gpt-oss-20b-qlora")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### 將 LoRA 適配器合併至基礎模型

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**注意：**  
- 請確認模型目錄名稱（`output-gemma-3-4b-it-full`、`output-gpt-oss-20b-qlora`）與您訓練後實際的輸出資料夾名稱一致。  
- 若您使用的是 LoRA 而非 QLoRA，只需相應地替換路徑即可。  
- 部分 Gemma 模型需要在 `from_pretrained` 中指定 `trust_remote_code=True`；若看到相關警告，請加入此設定。

如需更多自訂設定（填充權杖、裝置等），請參閱您訓練時所使用的腳本。

<!-- @test:id=verify-lora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys

out_dir = "output-gemma-3-4b-it-lora"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

if not (os.path.exists(os.path.join(out_dir, "adapter_model.safetensors")) or os.path.exists(os.path.join(out_dir, "adapter_model.bin"))):
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: LoRA output looks correct")
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=verify-qlora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys

out_dir = "output-gemma-3-4b-it-qlora"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

if not (os.path.exists(os.path.join(out_dir, "adapter_model.safetensors")) or os.path.exists(os.path.join(out_dir, "adapter_model.bin"))):
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: QLoRA output looks correct")
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=verify-full-finetuning-output timeout=300 hidden=True setup=activate-venv -->
```python
import glob
import os
import sys

out_dir = "output-gemma-3-4b-it-full"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

# Weights may be saved as a single model.safetensors or, when the model
# exceeds max_shard_size, as model-*.safetensors shards plus an index.
single = os.path.exists(os.path.join(out_dir, "model.safetensors"))
shards = glob.glob(os.path.join(out_dir, "model-*.safetensors"))
if not single and not shards:
    print("FAIL: No model safetensors weights found")
    sys.exit(1)

print(f"PASS: Full fine-tuned model output looks correct: {out_dir}")
```
<!-- @test:end -->
<!-- @device:end -->
---

## 自訂指南

### 使用您自己的資料集

所有腳本使用相同的資料集格式。請替換載入區段：

```python
from datasets import load_dataset

# Option 1: Local JSON/JSONL file
dataset = load_dataset('json', data_files='your_data.json')

# Option 2: Hugging Face Hub dataset
dataset = load_dataset('username/dataset-name')

# Option 3: CSV file
dataset = load_dataset('csv', data_files='data.csv')

# Format for chat models
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['instruction']},
            {"role": "assistant", "content": example['response']}
        ]
    }

dataset = dataset.map(format_instruction)
```

**本機 JSON/JSONL 檔案的資料集格式：**

使用此方法時，請確保您的 JSON 檔案結構正確，以避免解析錯誤。

必須遵守以下準則：
* **檔案格式：** JSON 檔案應在整合開發環境（IDE）中進行格式化，以確保正確的結構與語法。
* **必要的鍵值：** 自訂 JSON 檔案必須包含 `instruction` 與 `response` 這兩個鍵值。這些鍵值對於該方法能否正確運作至關重要。
```json
[
  {
    "instruction": "Your first instruction here",
    "response": "Expected response here"
  },
  {
    "instruction": "Your second instruction here",
    "response": "Expected response here"
  }
]
```
**Hugging Face Hub 資料集的資料集格式**

使用來自 Hugging Face 的資料集時，請確保您的資料集結構正確，以利順利整合。

請遵循以下準則：
* **指令－回應配對：** 請專注於包含 `instruction-response` 配對的資料集。此結構對於預期功能而言至關重要。
* **自訂鍵值修改：** 若您的資料集不符合 `instruction-response` 結構，您可以修改 `format_instruction()` 函式。這讓您能夠依需求調整特定的鍵值。

調整範例：若資料集的輸出需要調整，您可以修改 format_instruction() 函式中的回應區段，以符合您的需求。
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**CSV 檔案的資料集格式**

若要讓腳本使用 CSV 檔案格式，您需要確保 CSV 檔案包含名為 `instruction` 與 `response` 的欄位。
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### 調整訓練參數

編輯訓練腳本並變更變數以符合您的目標：**學習率**（`LR`）、**訓練輪數**（`EPOCHS`）、**批次大小**（`BATCH_SIZE`）、**梯度累積**（`GRAD_ACCUM_STEPS`），以及針對 LoRA/QLoRA 的 **秩**（`LORA_R`）。若要加快執行速度，可使用較少的訓練輪數與較高的學習率（LR）；若要提升品質，則可使用較多的訓練輪數與較低的 LR。若遇到記憶體不足的錯誤，請減少批次大小或序列長度。
### 記憶體最佳化秘訣

如果遇到記憶體不足的錯誤：

**1. 減少批次大小（Batch Size）：**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. 減少序列長度：**
```python
max_seq_length=256  # Instead of 512
```

**3. 使用更積極的量化：**
```
Full → LoRA → QLoRA
```

**4. 啟用梯度檢查點（Gradient Checkpointing）（僅限完整微調）：**
```python
model.gradient_checkpointing_enable()
```

---

## 監控與偵錯

### 監看 GPU 記憶體

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### （選用）使用 Weights & Biases 追蹤實驗

若要將執行記錄與指標記錄到 [Weights & Biases](https://wandb.ai)：

```bash
pip install wandb
wandb login
```

在訓練腳本中，於訓練器設定中設定 `report_to="wandb"`，並可選擇性地設定 `run_name="your-experiment-name"`。如果您不想使用 Wandb，請將 `report_to` 保留為預設值，或將其設為 `"none"`。

### 常見問題

#### 記憶體不足（OOM）

**解決方案：** 減少批次大小及／或使用 QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### 損失未下降

**解決方案：** 調整學習率
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### 訓練速度緩慢

**解決方案：** 若記憶體允許，增加批次大小
```python
BATCH_SIZE = 8
```
## 後續步驟

成功完成微調後，請考慮以下後續步驟，以充分發揮您的模型效益：

1. **評估**：在保留的測試資料上進行徹底評估，以衡量泛化能力並避免過度擬合。
2. **實驗**：嘗試不同的超參數值，以在準確度、速度與記憶體之間取得更好的平衡。
3. **追蹤**：使用 Weights & Biases 追蹤所有實驗（及其對應指標），以利研究的可重現性。
4. **嘗試**：在您自己的自訂資料集上進行訓練，以針對您的使用情境調整模型。
5. **部署**：使用相容硬體上的高效後端（例如 vLLM）部署您微調後的模型，以實現快速推論。
6. **探索**：進階技術，包括提示工程（prompt engineering）、混合精度與更長的序列長度。
7. **訓練**：針對不同任務或領域訓練多個 LoRA 適配器，並依需求進行替換。

---