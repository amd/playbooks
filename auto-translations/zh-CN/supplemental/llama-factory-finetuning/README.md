<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **机器翻译。**本页面由英文自动翻译，未经人工审核。其中可能包含错误，某些说明、命令、下载内容、产品可用性或其他内容可能因语言或地区而异。如内容存在任何不一致或差异，应以英文原版 playbook 为准。
<!-- auto-translated-disclaimer:end -->

## 概述

高效的微调对于将大语言模型（LLM）适配到下游任务至关重要。LLaMA Factory 是一个开源且用户友好的平台，可简化大语言模型和多模态模型的训练与微调。它允许用户在本地以最少的编码量自定义数百种预训练模型。

本手册将教您如何在本地 AMD 硬件上使用 LLaMA Factory 微调 LLM。

<!-- @device:stx,krk -->
> **注意：** 本手册中的微调技术至少需要 **32 GB 的系统内存**，其中至少 **16 GB 可供 GPU 使用**（这 16 GB 是 32 GB 中的一部分，而不是额外增加的）。
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **注意：** 本手册中的微调技术至少需要 **16 GB 的 GPU 总内存**和 **32 GB 的系统内存**。
> - 在 Windows 上，GPU 总内存是显卡的专用显存与共享 GPU 内存（从系统内存中借用）的总和。
> - 因此，专用显存低于 16 GB 的显卡仍可通过使用共享 GPU 内存来弥补差额，从而运行本手册中的内容。
<!-- @os:end -->

<!-- @os:linux -->
> **注意：** 本手册中的微调技术需要一块至少具有 **16 GB 专用 GPU 内存**的显卡以及 **32 GB 的系统内存**。
> - 在 Linux 上，训练完全在显卡的专用显存中运行。
> - 当显存耗尽时，不会回退到共享 GPU 内存（系统内存）。
> - 专用显存低于 16 GB 的显卡在 Linux 上训练时会耗尽内存，即使系统拥有充足的内存也是如此。
<!-- @os:end -->
<!-- @device:end -->

## 您将学到什么

- 如何使用 AMD ROCm™ 软件搭建 LLaMA Factory
- 如何配置 LLM 微调参数（以 Qwen/Qwen3-4B-Instruct-2507 为示例）
- 如何运行 LLaMA Factory 微调
- 如何使用微调后的模型进行推理
- 如何导出微调后的模型

## 预计用时

- 时长：运行本手册大约需要 60 分钟（具体取决于您的模型/数据集大小和网络速度）。
- 有关更多信息，请参阅 [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory)。

## 设置内存配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 检查软件更新

<!-- @require:software-update -->
<!-- @device:end -->

## 安装软件先决条件

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

#### 创建虚拟环境

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
**授予您的用户访问 GPU 设备的权限**（需要注销并重新登录才能生效）：

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

### 安装基本依赖项

<!-- @require:pytorch,driver -->
 
### 安装其他依赖项

> **注意**：请确保 Python 版本为 3.11、3.12 或 3.13

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

### 安装 LLaMA Factory

LLaMA Factory 依赖于 PyTorch。根据上述要求，您应该已经安装了它。

从 [LLaMA Factory 官方 GitHub 仓库](https://github.com/hiyouga/LlamaFactory)下载源代码，并安装其依赖项。

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

验证 `llamafactory-cli` 是否可执行。

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

示例输出：

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

成功安装 LLaMA Factory 后，让我们在其上运行微调。

## 使用 LLaMA Factory CLI 进行微调

本节将介绍如何准备微调数据集、配置 LoRA/QLoRA 参数，以及运行 LoRA 微调。

### 数据集准备

LLaMA Factory 支持 Alpaca 格式和 ShareGPT 格式的微调数据集。所有可用的数据集都已在 [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json) 中定义。如果您使用自定义数据集，请确保在 `dataset_info.json` 中添加数据集描述，并在训练前指定数据集名称。详细信息可在其文档中找到，请参见[此处](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html)。

在本手册中，我们将以 identity 和 alpaca_en_demo 数据集为例，并在下一步中配置数据集信息。
### 微调参数配置

LLaMA Factory 支持多种微调方案。

| 微调方案 | LLaMA Factory 示例 |
|-----------|------|
| 全参数微调    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| LoRA 微调  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| QLoRA 微调 | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

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

这些示例配置文件已指定了模型参数、微调方法参数、数据集参数、评估参数等。您可以根据自己的需求对其进行配置。在本手册中，我们将使用 [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml)。

**关键参数说明：**
- `model_name_or_path` - Hugging Face 模型名称或本地模型文件路径。
- `stage` - 训练阶段。可选项：rm（奖励建模）、pt（预训练）、sft（监督微调）、PPO、DPO、KTO、ORPO。
- `do_train` - true 表示训练，false 表示评估
- `finetuning_type` - 微调方法。可选项：freeze、lora、full
- `lora_rank` - LoRA 中使用的低秩矩阵的维度，典型值为：4、6、8、16（数值越小 = 参数越少 = 微调速度越快；数值越大 = 任务适应性更好但资源占用更高）。
- `lora_target` - LoRA 方法的目标模块。默认值：all。
- `dataset` - 要使用的数据集。多个数据集用“,”分隔
- `output_dir` - 微调输出路径
- `logging_steps` - 日志记录的步数间隔
- `save_steps` - 模型检查点保存的步数间隔。
- `overwrite_output_dir` - 是否允许覆盖输出目录。
- `per_device_train_batch_size` - 每个设备的训练批大小。
- `gradient_accumulation_steps` - 梯度累积步数。
- `learning_rate` - 学习率
- `num_train_epochs` - 训练轮数
- `lr_scheduler_type` - 学习率调度方式。可选项：linear、cosine、polynomial、constant 等。
- `warmup_ratio` - 学习率预热比例

<!-- @os:linux -->
我们将修改 `lora_rank` 的默认值，以便在 AMD Ryzen™ 和 AMD Radeon™ GPU 上运行微调。
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
我们将更新默认的 LoRA 微调配置，以更好地兼容 AMD Ryzen™ 和 AMD Radeon™ GPU：
- 将 `lora_rank` 从 `8` 设置为 `6`，以降低微调过程中的显存占用。
- 使用 `fp16` 替代 `bf16`，以获得更广泛的 AMD GPU 兼容性并降低显存占用。
- 在 Windows 上将 `dataloader_num_workers` 设置为 `0`，以避免因多进程数据加载而导致的 `"Can't pickle local object<>"` 错误。

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

### 运行 LLaMA Factory 微调 

**llamafactory-cli** 是 LLaMA Factory 官方的命令行界面（CLI）工具，旨在简化端到端的 LLM 工作流（数据准备 → 微调 → 评估 → 部署），无需编写复杂代码。

对于训练/微调，**llamafactory-cli train** 是 LLaMA Factory CLI 的核心子命令。它将微调工作流（数据预处理、超参数调优、硬件优化）抽象为单个 CLI 命令，支持多种微调范式（LoRA/QLoRA/全参数微调），并针对低资源 GPU 进行了优化（例如，在 16GB 显存上运行 QLoRA）。

您可以使用以下命令运行 LLaMA Factory 微调，该命令基于修改后的 Qwen3 LoRA 微调配置文件。

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

运行 LLM 微调后，所有生成的输出都存储在 “output_dir” 中，包括模型检查点文件、配置文件和训练指标。

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

### 测试微调后的模型 

**llamafactory-cli chat** 专为与 LLM（包括基础模型和经过 LoRA 微调的模型）进行交互式对话/推理而设计。LLaMA Factory 在 [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference) 中提供了运行微调模型推理的示例配置。您也可以修改此示例配置来更改设置，例如推理后端。

使用以下命令测试 Qwen3 微调模型：

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
下面展示了使用微调模型进行对话的示例：

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### 导出微调后的模型

对于生产环境的使用场景，需要将预训练模型与 LoRA 适配器合并并导出为单个模型。合并后的模型可以作为普通的 Hugging Face 模型文件使用。LLaMA Factory 在 [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora) 中提供了示例配置。

使用以下命令导出 Qwen3 微调模型：

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
导出微调模型的结果如下所示。

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

`LLaMA-Factory` 还支持通过浏览器中的网页 UI 进行零代码的大语言模型微调。

使用以下命令打开它：

```bash
llamafactory-cli webui
```
`LlamaFactory Web UI` 提供了一个简洁的界面来管理机器学习工作流程，包括训练、评估、预测、聊天以及导出模型。以下是各个选项卡的简要介绍：

* **Train（训练）**：此选项卡允许您选择模型和数据集、配置训练参数并启动训练过程。理解必需参数和可选参数对于优化训练设置至关重要。
* **Evaluate & Predict（评估与预测）**：训练完成后，您可以使用此选项卡评估模型的性能并进行预测。它提供了模型在新数据上的准确性和有效性的洞察。
* **Chat（聊天）**：训练完成后，可在 Chat 选项卡中加载模型以与其交互，查看您的工作成果。此功能支持与已训练模型进行实时交流。
* **Export（导出）**：此选项卡便于导出已训练的模型以用于部署或进一步使用。您可以将模型保存为适用于不同应用的各种格式。

有关详细指导，建议您参阅 [LlamaFactory GitHub repository](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) 和 [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest) 上的官方文档。此外，[Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) 也为该界面及其功能提供了有价值的见解。

## 后续步骤
- 尝试不同的模型，例如 `gpt-oss` 及其他先进模型。
- 在微调后的模型上试验不同的后端

如需更多文档，请访问：https://llamafactory.readthedocs.io/en/latest/