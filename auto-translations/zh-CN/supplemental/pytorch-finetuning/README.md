<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## 概述

本教程提供了使用 PyTorch 和 ROCm 对大型语言模型（LLM）进行微调的分步示例。内容涵盖多种技术，从标准微调到内存高效的参数高效微调（PEFT）策略，帮助您轻松根据需求适配模型。

**所用模型**：google/gemma-3-4b-it  *（如为受限模型，请参阅 [启用 HF 身份验证](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models)）*  
**硬件**：支持 ROCm 的 AMD Radeon™ GPU  
**框架**：PyTorch + Hugging Face（Transformers、PEFT、Transformer Reinforcement Learning (TRL)）

<!-- @device:halo,halo_box -->
> **注意：** 您也可以尝试其他模型架构，包括 **GPT-OSS-20B**，只需在提供的训练脚本中替换模型即可。
> 完整微调至少需要 32 GB GPU 显存和 64 GB 系统内存。
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> **注意：** LoRA 和 QLoRA 微调至少需要 16 GB GPU 显存和 32 GB 系统内存。
<!-- @device:end -->

## 您将学到的内容

- 如何使用 LoRA、QLoRA 以及 PyTorch 和 ROCm 对 LLM 进行完整微调
- 如何保存和部署您的微调模型
- 如何监控训练过程并调试常见问题

## 设置内存配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 检查软件更新
> **注意**：如果未安装 VS Code，可通过 Ryzen AI Developer Center 进行安装。

<!-- @require:software-update -->
<!-- @device:end -->

## 安装软件前置条件

#### 创建虚拟环境

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=60 -->
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
**授予您的用户访问 GPU 设备的权限**（需注销并重新登录后生效）：

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=120 -->
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
<!-- @test:id=create-venv timeout=60 -->
```powershell
python -m venv finetune-venv --system-site-packages
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=60 -->
```powershell
python -m venv finetune-venv
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

#### 安装基本依赖项
<!-- @require:pytorch -->

#### 附加依赖项

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows：** 此处仅测试和支持核心软件包。**bitsandbytes 在 Windows 上支持不完善**，因此 Windows 安装中省略了它；请在 Windows 上使用 LoRA 或完整微调（QLoRA 需要 bitsandbytes，仅适用于 Linux）。
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### 启用 HF 身份验证（受限模型或自定义/非预安装模型）

本示例使用 **google/gemma-3-4b-it**，这是一个**受限**模型。您必须在 Hugging Face 上接受该模型的使用条款，然后进行身份验证，以便训练脚本能够下载它。

1. **接受许可证：** 打开 [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it)，登录（或创建账户），并在模型页面上接受许可证/使用条款（例如"同意并访问仓库"）。
2. **安装并登录：** 安装 Hugging Face CLI，然后运行标准登录命令：

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

## 了解各种技术

### 什么是 LoRA？

**LoRA（低秩适配）** 保持基础模型冻结，仅训练添加到特定层的小型"适配器"矩阵。

- **核心思想**：与其用数百万参数更新庞大的权重矩阵，不如学习一个低秩更新（两个小矩阵的乘积，参数量大幅减少）。这样可以大幅减少可训练参数量和显存占用，同时保留接近完整微调的质量。

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### 什么是 QLoRA？

**QLoRA** 将 **4 位量化**与 **LoRA** 相结合。基础模型以 4 位加载（大幅节省内存），仅以更高精度训练 LoRA 适配器。因此，您可以获得 LoRA 的参数效率加上更低的显存占用，与全精度 LoRA 相比质量略有下降。请注意，4 位量化可能导致数值不稳定（损失尖峰或 NaN），因此如果显存充足，用户通常更倾向于使用 **LoRA**。

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **注意**：对于 `openai/gpt-oss-20b` 等 MXFP4 基础模型，我们建议使用 **LoRA**（`train_lora.py`）而非 QLoRA。QLoRA 脚本的 `bitsandbytes` 4 位路径通常会将 MXFP4 权重反量化为 BF16，因此运行行为类似于标准 LoRA。原生 MXFP4 需要从源码构建 `bitsandbytes`，并配合匹配的 Transformers/Triton/内核栈。请参阅 [Transformers MXFP4 文档](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4)。

---

### 2. 选择您的方法

| 方法 | 内存 | 速度 | 质量 | 最适合 |
|--------|--------|-------|---------|----------|
| **QLoRA**（仅 Linux） | 12-16GB | 最快 | 90-95% | 低内存使用 |
| **LoRA** | 24-32GB | 快 | 95-98% | 均衡方案 |
| **完整微调** | 80GB+ | 最慢 | 100% | 最高质量 |

### 3. 运行训练

**数据集及模型学习内容**  
脚本将数据集转换为对话示例。例如，QLoRA 脚本使用 **Abirate/english_quotes**：每个示例变为如下的用户-助手对：

- **用户：** "给我一句关于：&lt;标签&gt; 的名言"
- **助手：** "&lt;名言&gt; – &lt;作者&gt;"

微调使模型学会响应询问某一主题名言的提示，并以 `<名言文本> - <作者>` 的格式返回结果。LoRA 和完整微调脚本使用 **databricks/databricks-dolly-15k**（通用指令/响应对），因此具体任务因脚本而异；核心思想相同——将模型适配到您选择的数据集和格式。

以下是可用训练方法的摘要。每种方法均链接到其脚本，并提供简要说明以帮助您选择合适的方案。

| 脚本 | 方法 | 描述 | 典型显存 | 推荐对象 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py) | **LoRA** | 在冻结基础模型的同时训练小型适配器矩阵。速度提升 3–5 倍；质量约为完整微调的 95–98%。 | 24–32GB | 高级用户；多适配器；显存较充裕 |
| [`train_qlora.py`](assets/train_qlora.py) *（仅 Linux）* | **QLoRA** | 4 位量化 + LoRA 适配器。内存占用最低，速度最快，质量略有下降。需要 `bitsandbytes`（仅 Linux）。 | 12–16GB | 大多数用户；快速实验；显存有限 |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **完整微调** | 更新所有模型参数。质量最高；内存和计算资源消耗最大。 | 40GB+ | 追求最高质量；科研用途；大显存 |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **注意：** 完整微调（`train_full_finetuning.py`）可能需要超过 64GB 的系统内存，在此设备上可能不可行。请考虑改用 LoRA 或 QLoRA。
<!-- @os:end -->

<!-- @os:windows -->
> **注意：** 完整微调（`train_full_finetuning.py`）可能需要超过 64GB 的系统内存，在此设备上可能不可行。请考虑改用 LoRA。
<!-- @os:end -->
<!-- @device:end -->

只需选择您偏好的"训练方法"，下载对应脚本，并在保持虚拟环境激活的情况下使用以下命令执行：

```python
python3 train_<method_name>.py.
```

## 使用您的微调模型

### 完整微调后

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

### LoRA/QLoRA 训练后

```python
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

# Load model with LoRA or QLoRA adapters
model = AutoPeftModelForCausalLM.from_pretrained(
    "output-gemma-3-4b-it-qlora",   # or "output-gemma-3-4b-lora" depending on your training
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-it-qlora")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### 将 LoRA 适配器合并到基础模型

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**注意：**  
- 请确保模型目录名称（`output-gemma-3-4b-full`、`output-gemma-3-4b-qlora`）与训练实际输出文件夹一致。  
- 如果您使用的是 LoRA 而非 QLoRA，只需相应替换路径即可。  
- 某些 Gemma 模型需要在 `from_pretrained` 中指定 `trust_remote_code=True`；如果看到相关警告，请添加此参数。

如需更多自定义设置（填充标记、设备等），请参阅您用于训练的脚本。

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
    "model.safetensors.index.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

shards = glob.glob(os.path.join(out_dir, "model-*.safetensors"))
if not shards:
    print("FAIL: No sharded model safetensors files found")
    sys.exit(1)

print(f"PASS: Full fine-tuned model output looks correct: {out_dir}")
```
<!-- @test:end -->
<!-- @device:end -->
---

## 自定义指南

### 使用您自己的数据集

所有脚本使用相同的数据集格式。替换加载部分：

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

**本地 JSON/JSONL 文件的数据集格式：**

使用此方法时，请确保您的 JSON 文件结构正确，以避免解析错误。

必须遵守以下准则：
* **文件格式：** JSON 文件应在集成开发环境（IDE）中进行格式化，以确保结构和语法正确。
* **必需键：** 自定义 JSON 文件必须包含 `instruction` 和 `response` 键。这些键对于方法的正常运行至关重要。
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
**Hugging Face Hub 数据集的数据集格式**

使用 Hugging Face 数据集时，请确保您的数据集结构正确，以便无缝集成。

应遵循以下准则：
* **指令-响应对：** 重点关注包含 `instruction-response` 对的数据集。这种结构对于预期功能至关重要。
* **自定义键修改：** 如果您的数据集不符合 `instruction-response` 结构，您可以选择修改 `format_instruction()` 函数，以适配特定键。

示例调整：在需要调整数据集输出的情况下，您可以修改 `format_instruction()` 函数中的响应部分以满足您的需求。
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**CSV 文件的数据集格式**

要使脚本支持 CSV 文件格式，您需要确保 CSV 文件包含名为 `instruction` 和 `response` 的列。
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### 调整训练参数

编辑训练脚本并修改变量以匹配您的目标：**学习率**（`LR`）、**轮次**（`EPOCHS`）、**批次大小**（`BATCH_SIZE`）、**梯度累积**（`GRAD_ACCUM_STEPS`），以及 LoRA/QLoRA 的**秩**（`LORA_R`）。若要加快运行速度，请使用更少的轮次和更高的学习率（LR）；若要提高质量，请使用更多轮次和更低的 LR。如果遇到内存不足错误，请减小批次大小或序列长度。

### 内存优化技巧

如果遇到内存不足错误：

**1. 减小批次大小：**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. 减小序列长度：**
```python
max_seq_length=256  # Instead of 512
```

**3. 使用更激进的量化：**
```
Full → LoRA → QLoRA
```

**4. 启用梯度检查点（仅限完整微调）：**
```python
model.gradient_checkpointing_enable()
```

---

## 监控与调试

### 监控 GPU 内存

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### （可选）使用 Weights & Biases 跟踪实验

要将运行记录和指标记录到 [Weights & Biases](https://wandb.ai)：

```bash
pip install wandb
wandb login
```

在训练脚本中，在训练器配置中设置 `report_to="wandb"`，并可选设置 `run_name="your-experiment-name"`。如果您不想使用 Wandb，请将 `report_to` 保留为默认值或设置为 `"none"`。

### 常见问题

#### 内存不足（OOM）

**解决方案：** 减小批次大小和/或使用 QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### 损失未下降

**解决方案：** 调整学习率
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### 训练缓慢

**解决方案：** 在内存允许的情况下增大批次大小
```python
BATCH_SIZE = 8
```
## 后续步骤

成功完成微调后，请考虑以下后续步骤，以充分发挥模型的潜力：

1. **评估**：在保留的测试数据上进行全面评估，以衡量泛化能力并避免过拟合。
2. **实验**：尝试不同的超参数值，以在准确性、速度和内存之间取得更好的权衡。
3. **跟踪**：使用 Weights & Biases 记录所有实验（及相应指标），以实现可复现的研究。
4. **尝试**：在您自己的自定义数据集上进行训练，使模型专门适配您的使用场景。
5. **部署**：使用 vLLM 等高效后端在兼容硬件上对微调模型进行快速推理。
6. **探索**：包括提示工程、混合精度和更长序列长度在内的高级技术。
7. **训练**：为不同任务或领域训练多个 LoRA 适配器，并按需切换。

---