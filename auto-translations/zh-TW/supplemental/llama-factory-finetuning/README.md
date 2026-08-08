<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機器翻譯。**本頁面是由英文自動翻譯而成，尚未經過人工審閱。內容可能包含錯誤，且某些指示、命令、下載項目、產品供應情況或其他內容可能因語言或地區而異。如本文件與英文版本之間存在任何不一致或差異，應以該 playbook 之英文原始版本為準。
<!-- auto-translated-disclaimer:end -->

## 概述

高效微調對於將大型語言模型（LLM）調整以適應下游任務至關重要。LLaMA Factory 是一個開源且使用者友善的平台，能簡化大型語言模型與多模態模型的訓練與微調。它讓使用者能夠在本機以最少的程式撰寫，自訂數百種預訓練模型。

本手冊將教您如何在您的本機 AMD 硬體上，使用 LLaMA Factory 微調 LLM。

<!-- @device:stx,krk -->
> **注意：** 本手冊中的微調技術至少需要 **32 GB 系統記憶體**，其中至少要有 **16 GB 可供 GPU 使用**（此 16 GB 是 32 GB 中的一部分，並非額外需求）。
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **注意：** 本手冊中的微調技術至少需要 **16 GB 的 GPU 記憶體總量**及 **32 GB 系統記憶體**。
> - 在 Windows 上，GPU 記憶體總量結合了顯示卡的專用 VRAM 與共享 GPU 記憶體（由系統記憶體借用）。
> - 因此，專用 VRAM 少於 16 GB 的顯示卡仍可透過使用共享 GPU 記憶體來補足差額，藉此執行本手冊內容。
<!-- @os:end -->

<!-- @os:linux -->
> **注意：** 本手冊中的微調技術需要一張至少具備 **16 GB 專用 GPU 記憶體**的顯示卡，以及 **32 GB 系統記憶體**。
> - 在 Linux 上，訓練完全在顯示卡的專用 VRAM 中執行。
> - 當 VRAM 用盡時，並不會回退使用共享 GPU 記憶體（系統記憶體）。
> - 專用 VRAM 少於 16 GB 的顯示卡，在 Linux 上訓練時將會發生記憶體不足的情況，即使系統擁有充足的記憶體也一樣。
<!-- @os:end -->
<!-- @device:end -->

## 您將學到什麼

- 如何使用 AMD ROCm™ 軟體設定 LLaMA Factory
- 如何設定 LLM 微調參數（以 Qwen/Qwen3-4B-Instruct-2507 為範例）
- 如何執行 LLaMA Factory 微調
- 如何使用微調後的模型進行推論
- 如何匯出微調後的模型 

## 預估時間

- 所需時間：執行本手冊約需 60 分鐘（視您的模型/資料集大小及網路速度而定）。
- 如需更多資訊，請參閱 [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory)。

## 設定記憶體組態

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 檢查軟體更新

<!-- @require:software-update -->
<!-- @device:end -->

## 安裝軟體先決條件

<!-- @os:linux -->
<!-- @test:id=python-prereqs-check timeout=120 hidden=True -->
```bash
python3 --version
pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-prereqs-check timeout=120 hidden=True -->
```powershell
python --version
pip --version
```
<!-- @test:end -->
<!-- @os:end -->

#### 建立虛擬環境

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv llamafactory-env --system-site-packages
source llamafactory-env/bin/activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="source llamafactory-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**授予您的使用者存取 GPU 裝置的權限**（需登出並重新登入才會生效）：

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv llamafactory-env
source llamafactory-env/bin/activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="source llamafactory-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv llamafactory-env --system-site-packages
llamafactory-env\Scripts\activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="llamafactory-env\Scripts\activate" --> 
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv llamafactory-env
llamafactory-env\Scripts\activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="llamafactory-env\Scripts\activate" --> 
<!-- @device:end -->
<!-- @os:end -->

### 安裝基本相依套件

<!-- @require:pytorch,driver -->
 
### 安裝額外相依套件

> **注意**：請確認 Python 版本為 3.11、3.12 或 3.13

```bash
pip install huggingface_hub
```

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 hidden=True setup=activate-venv -->
```bash
python3 -m pip install --upgrade pip
python3 -m pip install huggingface_hub
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 hidden=True setup=activate-venv -->
```powershell
python -m pip install --upgrade pip
python -m pip install huggingface_hub
```
<!-- @test:end --> 
<!-- @os:end -->

### 安裝 LLaMA Factory

LLaMA Factory 依賴 PyTorch。根據上述需求，您應該已經安裝好了。

從 [LLaMA Factory 官方 GitHub 儲存庫](https://github.com/hiyouga/LlamaFactory)下載原始碼，並安裝其相依套件。

<!-- @device:halo_box -->
<!-- @test:id=install-llamafactory timeout=900 setup=activate-venv -->
```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install setuptools --break-system-packages
pip install -e . --break-system-packages
pip install -r requirements/metrics.txt --break-system-packages
```
<!-- @test:end --> 
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=install-llamafactory timeout=900 setup=activate-venv -->
```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install -e .
pip install -r requirements/metrics.txt 
```
<!-- @test:end --> 
<!-- @device:end -->

驗證 `llamafactory-cli` 是否可執行。

<!-- @os:linux -->
<!-- @test:id=verify-llamafactory-cli timeout=60 hidden=False setup=activate-venv -->
```bash
cd LlamaFactory
llamafactory-cli version || python -m llamafactory.cli version || true
echo "llamafactory-cli is available"
command -v llamafactory-cli
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=verify-llamafactory-cli timeout=60 hidden=False setup=activate-venv -->
```powershell
cd LlamaFactory
if (Get-Command llamafactory-cli -ErrorAction SilentlyContinue) {
    llamafactory-cli version
    Write-Host "llamafactory-cli is available"
} else {
    Write-Host "llamafactory-cli is not available"
}
```
<!-- @test:end --> 
<!-- @os:end -->

範例輸出：

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

成功安裝 LLaMA Factory 後，讓我們開始執行微調。

## 使用 LLaMA Factory CLI 進行微調 

本節將說明如何準備微調資料集、設定 LoRA/QLoRA 參數，以及執行 LoRA 微調。

### 資料集準備

LLaMA Factory 支援 Alpaca 格式與 ShareGPT 格式的微調資料集。所有可用的資料集皆已定義於 [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json) 中。若您使用自訂資料集，請務必在 `dataset_info.json` 中新增資料集說明，並在訓練前指定資料集名稱。詳情請參閱其文件說明，連結在[這裡](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html)。

在本手冊中，我們將以 identity 及 alpaca_en_demo 資料集作為範例，並於下一步驟中設定資料集資訊。
### 微調參數配置

LLaMA Factory 支援多種微調方案。

| 微調方案 | LLaMA Factory 範例 |
|-----------|------|
| 全參數微調    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| LoRA 微調  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| QLoRA 微調 | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

<!-- @test:id=verify-llamafactory-files timeout=60 hidden=True setup=activate-venv -->
```python
import os
import sys

base = "LlamaFactory"
required = [
    "examples/train_lora/qwen3_lora_sft.yaml",
    "examples/inference/qwen3_lora_sft.yaml",
    "examples/merge_lora/qwen3_lora_sft.yaml",
]

missing = [p for p in required if not os.path.exists(os.path.join(base, p))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

print("PASS: Required LLaMA Factory example files exist")
```
<!-- @test:end -->

這些範例配置檔案已指定模型參數、微調方法參數、資料集參數、評估參數等等。您可以根據自身需求進行配置。在本操作手冊中，我們將使用 [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml)。

**關鍵參數說明：**
- `model_name_or_path` - Hugging Face 模型名稱或本機模型檔案路徑。
- `stage` - 訓練階段。選項：rm（獎勵建模）、pt（預訓練）、sft（監督式微調）、PPO、DPO、KTO、ORPO。
- `do_train` - true 表示訓練，false 表示評估
- `finetuning_type` - 微調方法。選項：freeze、lora、full
- `lora_rank` - LoRA 中使用的低秩矩陣維度，常見數值：4、6、8、16（數值越小 = 參數越少 = 微調速度越快；數值越大 = 任務適應性更佳但資源消耗較高）。
- `lora_target` - LoRA 方法的目標模組。預設值：all。
- `dataset` - 使用的資料集。多個資料集請使用「,」分隔
- `output_dir` - 微調輸出路徑
- `logging_steps` - 記錄日誌的步數間隔
- `save_steps` - 模型檢查點儲存間隔。
- `overwrite_output_dir` - 是否允許覆寫輸出目錄。
- `per_device_train_batch_size` - 每個裝置的訓練批次大小。
- `gradient_accumulation_steps` - 梯度累積步數。
- `learning_rate` - 學習率
- `num_train_epochs` - 訓練回合數
- `lr_scheduler_type` - 學習率排程。選項：linear、cosine、polynomial、constant 等。
- `warmup_ratio` - 學習率預熱比例

<!-- @os:linux -->
我們將修改 `lora_rank` 的預設值，以在 AMD Ryzen™ 與 AMD Radeon™ GPU 上執行微調。
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
我們將更新預設的 LoRA 微調配置，以更好地相容 AMD Ryzen™ 與 AMD Radeon™ GPU：
- 將 `lora_rank` 從 `8` 設為 `6`，以降低微調過程中的記憶體使用量。
- 使用 `fp16` 而非 `bf16`，以獲得更廣泛的 AMD GPU 相容性並降低記憶體使用量。
- 在 Windows 上將 `dataloader_num_workers` 設為 `0`，以避免因多行程資料載入而導致的 `"Can't pickle local object<>"` 錯誤。

```powershell
$filePath = "examples/train_lora/qwen3_lora_sft.yaml"

# Create a backup before modifying the YAML file
Copy-Item -Path $filePath -Destination "$filePath.bak" -Force

# Read the file and update the training settings
$content = Get-Content -Path $filePath -Raw

$newContent = $content `
  -replace 'lora_rank: 8', 'lora_rank: 6' `
  -replace 'bf16: true', 'fp16: true' `
  -replace 'dataloader_num_workers: 4', 'dataloader_num_workers: 0'

Set-Content -Path $filePath -Value $newContent
```
<!-- @os:end -->

### 執行 LLaMA Factory 微調

**llamafactory-cli** 是 LLaMA Factory 的官方命令列介面（CLI）工具，旨在簡化端對端的 LLM 工作流程（資料準備 → 微調 → 評估 → 部署），無需撰寫複雜的程式碼。

在訓練/微調方面，**llamafactory-cli train** 是 LLaMA Factory CLI 的核心子命令。它將微調工作流程（資料預處理、超參數調整、硬體最佳化）抽象化為單一 CLI 命令，支援多種微調範式（LoRA/QLoRA/全參數微調），並針對低資源 GPU 進行了最佳化（例如在 16GB VRAM 上執行 QLoRA）。

您可以使用以下命令執行 LLaMA Factory 微調，該命令基於已修改的 Qwen3 LoRA 微調配置檔案。

```bash
llamafactory-cli train examples/train_lora/qwen3_lora_sft.yaml
```

<!-- @os:linux -->
<!-- @test:id=quick-train-llamafactory-lora timeout=1200 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory

cp examples/train_lora/qwen3_lora_sft.yaml examples/train_lora/qwen3_lora_sft_ci.yaml

sed -i 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's|output_dir: .*|output_dir: saves/qwen3_lora_sft_ci|g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/overwrite_output_dir: false/overwrite_output_dir: true/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/per_device_train_batch_size: .*/per_device_train_batch_size: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/gradient_accumulation_steps: .*/gradient_accumulation_steps: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/num_train_epochs: .*/num_train_epochs: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/logging_steps: .*/logging_steps: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/save_steps: .*/save_steps: 5/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true

sed -i 's/max_samples: .*/max_samples: 16/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
if grep -q '^max_steps:' examples/train_lora/qwen3_lora_sft_ci.yaml; then
  sed -i 's/^max_steps:.*/max_steps: 5/g' examples/train_lora/qwen3_lora_sft_ci.yaml
else
  printf '\nmax_steps: 5\n' >> examples/train_lora/qwen3_lora_sft_ci.yaml
fi
if grep -q '^save_total_limit:' examples/train_lora/qwen3_lora_sft_ci.yaml; then
  sed -i 's/^save_total_limit:.*/save_total_limit: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml
else
  printf 'save_total_limit: 1\n' >> examples/train_lora/qwen3_lora_sft_ci.yaml
fi

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=quick-train-llamafactory-lora timeout=1200 hidden=True setup=activate-venv -->
```powershell
Set-Location -Path "LlamaFactory"

Copy-Item -Path "examples/train_lora/qwen3_lora_sft.yaml" -Destination "examples/train_lora/qwen3_lora_sft_ci.yaml"

$filePath = "examples/train_lora/qwen3_lora_sft_ci.yaml"
(Get-Content -Path $filePath) -replace 'lora_rank: 8', 'lora_rank: 6' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'bf16:\s*true', 'fp16: true' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'dataloader_num_workers:\s*4', 'dataloader_num_workers: 0' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'output_dir: .*', 'output_dir: saves/qwen3_lora_sft_ci' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'overwrite_output_dir: false', 'overwrite_output_dir: true' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'per_device_train_batch_size: .*', 'per_device_train_batch_size: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'gradient_accumulation_steps: .*', 'gradient_accumulation_steps: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'num_train_epochs: .*', 'num_train_epochs: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'logging_steps: .*', 'logging_steps: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'save_steps: .*', 'save_steps: 5' | Set-Content -Path $filePath

(Get-Content -Path $filePath) -replace 'max_samples: .*', 'max_samples: 16' | Set-Content -Path $filePath
if (Select-String -Path $filePath -Pattern '^max_steps:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^max_steps:.*', 'max_steps: 5' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value ""
    Add-Content -Path $filePath -Value "max_steps: 5"
}
if (Select-String -Path $filePath -Pattern '^save_total_limit:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^save_total_limit:.*', 'save_total_limit: 1' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value "save_total_limit: 1"
}

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

執行 LLM 微調後，所有產生的輸出都會儲存在「output_dir」中，包括模型檢查點檔案、配置檔案以及訓練指標。

<p align="center">
  <img src="assets/qwen3_lora.png" alt="Qwen3 LoRA Fine-tuning" width="600"/>
</p>

<!-- @test:id=verify-llamafactory-train-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "LlamaFactory/saves/qwen3_lora_sft_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "trainer_state.json",
    "training_args.bin",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) + glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: LLaMA Factory training output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end --> 

### 測試微調後的模型

**llamafactory-cli chat** 專為 LLM（包括基礎模型與經 LoRA 微調的模型）的互動式聊天/推論而設計。LLaMA Factory 在 [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference) 中提供了範例配置，用於執行微調模型的推論。您也可以修改此範例配置以變更設定，例如推論後端。

使用以下命令測試 Qwen3 微調模型：

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
以下顯示使用微調模型進行聊天的範例：

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### 匯出微調後的模型

對於生產環境使用案例，需要將預訓練模型與 LoRA 配接器合併並匯出為單一模型。此合併後的模型可作為一般的 Hugging Face 模型檔案使用。LLaMA Factory 在 [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora) 中提供了範例配置。

使用以下命令匯出 Qwen3 微調模型：

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
匯出微調模型的結果如下所示。

<p align="center">
  <img src="assets/qwen3_export.png" alt="Export Qwen3 Fine-Tuned model " width="600"/>
</p>

<!-- @os:linux -->
<!-- @test:id=export-llamafactory-model timeout=1800 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory
pip install pyyaml

python - <<'PY'
import yaml
from pathlib import Path

src = Path("examples/merge_lora/qwen3_lora_sft.yaml")
dst = Path("examples/merge_lora/qwen3_lora_sft_ci.yaml")

cfg = yaml.safe_load(src.read_text())

cfg["adapter_name_or_path"] = "saves/qwen3_lora_sft_ci"
cfg["export_dir"] = "saves/qwen3_lora_sft_ci_merged"

dst.write_text(yaml.safe_dump(cfg, sort_keys=False))
print(f"Wrote {dst}")
PY

llamafactory-cli export examples/merge_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=export-llamafactory-model timeout=1800 hidden=True setup=activate-venv -->
```powershell
Set-Location -Path "LlamaFactory"
pip install pyyaml

$script = @'
import yaml
from pathlib import Path

src = Path("examples/merge_lora/qwen3_lora_sft.yaml")
dst = Path("examples/merge_lora/qwen3_lora_sft_ci.yaml")

cfg = yaml.safe_load(src.read_text())

cfg["adapter_name_or_path"] = "saves/qwen3_lora_sft_ci"
cfg["export_dir"] = "saves/qwen3_lora_sft_ci_merged"

dst.write_text(yaml.safe_dump(cfg, sort_keys=False))
print(f"Wrote {dst}")
'@

$tempPy = Join-Path $env:TEMP "write_llamafactory_export_config.py"
Set-Content -Path $tempPy -Value $script -Encoding UTF8

python $tempPy
if ($LASTEXITCODE -ne 0) {
    Remove-Item $tempPy -Force -ErrorAction SilentlyContinue
    throw "FAIL: Could not create qwen3_lora_sft_ci.yaml"
}
Remove-Item $tempPy -Force -ErrorAction SilentlyContinue

if (-not (Test-Path "examples/merge_lora/qwen3_lora_sft_ci.yaml")) {throw "FAIL: examples/merge_lora/qwen3_lora_sft_ci.yaml was not created"}

llamafactory-cli export examples/merge_lora/qwen3_lora_sft_ci.yaml
if ($LASTEXITCODE -ne 0) {throw "FAIL: llamafactory-cli export failed"}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @test:id=verify-llamafactory-export-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "LlamaFactory/saves/qwen3_lora_sft_ci_merged"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing export directory: {out_dir}")
    sys.exit(1)

required = ["config.json",]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required export files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Exported merged model output looks correct")
```
<!-- @test:end --> 
## 使用 LLaMA Factory GUI

`LLaMA-Factory` 也支援透過瀏覽器中的網頁 UI 對 LLM 進行零程式碼微調。

請使用以下命令開啟：

```bash
llamafactory-cli webui
```
`LlamaFactory Web UI` 提供了一個精簡的介面，用於管理機器學習工作流程，包括訓練、評估、預測、聊天以及匯出模型。以下是各分頁的簡要介紹：

* **Train**：此分頁可讓您選擇模型和資料集、設定訓練參數，並啟動訓練流程。了解必填與選填參數對於最佳化訓練設定至關重要。
* **Evaluate & Predict**：訓練完成後，您可以使用此分頁評估模型的效能並進行預測。它可深入了解模型在新資料上的準確度與有效性。
* **Chat**：訓練完成後，在 Chat 分頁中載入模型即可與其互動，並查看您的成果。此功能可讓您與已訓練的模型即時交流。
* **Export**：此分頁便於匯出已訓練的模型以供部署或進一步使用。您可以將模型儲存為適用於不同應用程式的各種格式。

如需詳細指引，建議您參考 [LlamaFactory GitHub repository](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) 上的官方文件，以及 [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest)。此外，[Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) 也提供了關於此介面及其功能的寶貴見解。

## 後續步驟
- 嘗試不同的模型，例如 `gpt-oss` 以及其他最先進的模型。
- 在微調後的模型上嘗試不同的後端

如需更多文件，請造訪：https://llamafactory.readthedocs.io/en/latest/