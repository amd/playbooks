<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> 本手册使用了 GitHub 无法渲染的特殊标签。请访问 [amd.com/playbooks](https://amd.com/playbooks) 以正确预览此内容。
<!-- @github-only:end -->

## 概述

本教程提供了使用 PyTorch 和 ROCm 对大语言模型 (LLM) 进行微调的分步示例。它涵盖了多种技术，从标准微调到内存高效的参数高效微调 (PEFT) 策略，让您能够轻松地根据需求调整模型。

**所用模型**：google/gemma-3-4b-it  *(如果是受限模型，请参阅 [启用 HF 身份验证](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models))*  
**硬件**：支持 ROCm 的 AMD Radeon™ GPU  
**框架**：PyTorch + Hugging Face（Transformers、PEFT、Transformer Reinforcement Learning (TRL)）

<!-- @device:halo,halo_box -->
> **注意：** 您也可以尝试其他模型架构，包括 **GPT-OSS-20B**，只需在提供的训练脚本中替换模型即可。
> 完整微调至少需要 32 GB 的 GPU 内存和 64 GB 的系统内存。
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> **注意：** LoRA 和 QLoRA 微调至少需要 16 GB 的 GPU 内存和 32 GB 的系统内存。
<!-- @device:end -->

## 您将学到什么

- 如何使用 PyTorch 和 ROCm，通过 LoRA、QLoRA 和完整微调方式对 LLM 进行微调
- 如何保存和部署您微调后的模型
- 如何监控训练过程并调试常见问题

## 设置内存配置

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 检查软件更新
> **注意**：如果未安装 VS Code，您可以通过 Ryzen AI Developer Center 进行安装。

<!-- @require:software-update -->
<!-- @device:end -->

## 安装软件先决条件

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
**授予您的用户对 GPU 设备的访问权限**（需要注销并重新登录才能生效）：

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

#### 安装基础依赖项
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
**Windows：** 此处仅测试并支持核心软件包。**bitsandbytes 在 Windows 上支持不佳**，因此 Windows 安装省略了它；请在 Windows 上使用 LoRA 或完整微调（QLoRA 需要 bitsandbytes，仅适用于 Linux）。
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### 启用 HF 身份验证（受限或自定义/未预安装的模型）

在本示例中，我们使用 **google/gemma-3-4b-it**，这是一个**受限**模型。您必须先接受该模型在 Hugging Face 上的条款，然后进行身份验证，以便训练脚本能够下载它。

1. **接受许可协议：** 打开 [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it)，登录（或创建账户），并在模型页面上接受许可/条款（例如点击“Agree and access repository”）。
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

## 理解这些技术

### 什么是 LoRA？

**LoRA（低秩自适应）** 保持基础模型冻结，仅训练添加到某些层的小型“适配器”矩阵。

- **核心思想**：与其更新一个包含数百万参数的巨大权重矩阵，不如学习一个低秩更新（两个小矩阵，它们的乘积所包含的参数要少得多）。这样可以在保持大部分完整微调质量的同时，大幅减少可训练参数和显存占用。

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

**QLoRA** 将 **4 位量化**与 **LoRA** 相结合。基础模型以 4 位形式加载（大幅节省内存），仅 LoRA 适配器以更高精度进行训练。这样您就能获得 LoRA 的参数效率外加更低的显存占用，与全精度 LoRA 相比，质量上会有小幅折损。请注意，4 位量化可能会导致数值不稳定（损失值突增或出现 NaN），因此如果显存足够，用户通常更倾向于使用 **LoRA**。

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **注意**：对于像 `openai/gpt-oss-20b` 这样的 MXFP4 基础模型，我们建议使用 **LoRA**（`train_lora.py`）而不是 QLoRA。QLoRA 脚本的 `bitsandbytes` 4 位路径通常会将 MXFP4 权重反量化为 BF16，因此运行方式与标准 LoRA 相同。原生 MXFP4 需要从源代码构建 `bitsandbytes`，并配合匹配的 Transformers/Triton/kernels 技术栈。请参阅 [Transformers MXFP4 文档](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4)。

---

### 2. 选择您的方法

| 方法 | 内存 | 速度 | 质量 | 最适用于 |
|--------|--------|-------|---------|----------|
| **QLoRA**（仅限 Linux） | 12-16GB | 最快 | 90-95% | 低内存占用 |
| **LoRA** | 24-32GB | 快 | 95-98% | 平衡方案 |
| **Full（完整微调）** | 80GB+ | 最慢 | 100% | 最高质量 |
### 3. 运行训练

**数据集及模型学习内容**  
这些脚本会将数据集转换为聊天示例。例如，QLoRA 脚本使用 **Abirate/english_quotes**：每个示例都会变成一对用户与助手的对话，如下所示：

- **用户：** “给我一句关于：&lt;tag&gt; 的名言”
- **助手：** “&lt;quote&gt; – &lt;author&gt;”

微调训练模型，使其在被要求提供关于某主题的名言时能够作出回应，并以 `<quote text> - <author>` 的格式返回结果。LoRA 和全量微调脚本使用 **databricks/databricks-dolly-15k**（通用的指令/响应对），因此具体任务会因脚本而异；但原理相同——根据你选择的数据集和格式来适配模型。

以下是可用训练方法的汇总。每种方法均链接到其脚本，并提供简要说明以帮助你选择合适的方式。

| 脚本                           | 方法            | 说明                                                                                                         | 典型显存占用 | 推荐场景                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | 在冻结基础模型的同时训练小型适配器矩阵。速度快 3–5 倍；质量约为全量微调的 95–98%。                         | 24–32GB      | 高级用户；多个适配器；显存较充裕的情况    |
| [`train_qlora.py`](assets/train_qlora.py)  *(仅限 Linux)*             | **QLoRA**       | 4 位量化 + LoRA 适配器。内存占用最低、速度最快，质量略有折损。需要 `bitsandbytes`（仅限 Linux）。                            | 12–16GB      | 大多数用户；快速实验；显存有限时      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **全量微调** | 更新所有模型参数。质量最高；内存和计算占用也最高。                                    | 40GB+        | 追求最高质量；科研用途；显存充裕的情况           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **注意：** 全量微调（`train_full_finetuning.py`）可能需要超过 64GB 的系统内存，在该设备上可能无法运行。请考虑改用 LoRA 或 QLoRA。
<!-- @os:end -->

<!-- @os:windows -->
> **注意：** 全量微调（`train_full_finetuning.py`）可能需要超过 64GB 的系统内存，在该设备上可能无法运行。请考虑改用 LoRA。
<!-- @os:end -->
<!-- @device:end -->

只需选择你偏好的 `Training method`，下载对应脚本，并在保持虚拟环境处于激活状态的情况下使用以下命令运行它：

```python
python3 train_<method_name>.py.
```

## 使用你的微调模型

### 全量微调之后

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

### LoRA/QLoRA 训练之后

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

### 将 LoRA 适配器合并到基础模型中

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**注意：**  
- 请确保模型目录名称（`output-gemma-3-4b-full`、`output-gemma-3-4b-qlora`）与你训练后实际生成的输出文件夹一致。  
- 如果你使用的是 LoRA 而非 QLoRA，只需相应地替换路径即可。  
- 部分 Gemma 模型需要在 `from_pretrained` 中指定 `trust_remote_code=True`；如果看到相关警告，请添加此参数。

如需了解更多自定义设置（填充标记、设备等），请参阅你用于训练的脚本。

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

### 使用你自己的数据集

所有脚本使用相同的数据集格式。请替换加载部分：

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

使用此方法时，请确保你的 JSON 文件结构正确，以避免解析错误。

必须遵循以下准则：
* **文件格式：** 应在集成开发环境（IDE）中对 JSON 文件进行格式化，以确保结构和语法正确。
* **必需字段：** 自定义 JSON 文件必须包含 `instruction` 和 `response` 这两个键。这些键是该方法能够正常运行的关键。
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

使用来自 Hugging Face 的数据集时，请确保数据集结构正确，以便顺利集成。

应遵循以下准则：
* **指令-响应对：** 优先选择包含 `instruction-response` 对的数据集。此结构对实现预期功能至关重要。
* **自定义字段修改：** 如果你的数据集不符合 `instruction-response` 结构，你可以修改 `format_instruction()` 函数，以适配所需的特定字段。

调整示例：如果数据集的输出需要调整，你可以修改 format_instruction() 函数中的响应部分，以满足你的需求。
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

要在脚本中使用 CSV 文件格式，需要确保 CSV 文件包含名为 `instruction` 和 `response` 的列。
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### 调整训练参数

编辑训练脚本，修改各变量以匹配你的目标：**学习率**（`LR`）、**训练轮数**（`EPOCHS`）、**批大小**（`BATCH_SIZE`）、**梯度累积**（`GRAD_ACCUM_STEPS`），以及针对 LoRA/QLoRA 的**秩**（`LORA_R`）。若想加快训练速度，可减少轮数并提高学习率（LR）；若想获得更好质量，可增加轮数并降低学习率。如果遇到内存不足的错误，请减小批大小或序列长度。

### 内存优化技巧

如果遇到内存不足的错误：

**1. 减小批大小：**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. 减少序列长度：**
```python
max_seq_length=256  # Instead of 512
```

**3. 使用更激进的量化：**
```
Full → LoRA → QLoRA
```

**4. 启用梯度检查点（仅适用于全量微调）：**
```python
model.gradient_checkpointing_enable()
```

---

## 监控与调试

### 查看 GPU 内存

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (可选)使用 Weights & Biases 跟踪实验

要将运行记录和指标记录到 [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

在训练脚本中,在训练器配置中设置 `report_to="wandb"`,并可选择设置 `run_name="your-experiment-name"`。如果您不想使用 Wandb,请将 `report_to` 保留为默认值,或将其设置为 `"none"`。

### 常见问题

#### 内存不足 (OOM)

**解决方案:** 减小批量大小和/或使用 QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### 损失不下降

**解决方案:** 调整学习率
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### 训练速度慢

**解决方案:** 如果内存允许,增大批量大小
```python
BATCH_SIZE = 8
```
## 后续步骤

完成微调后,可以考虑以下后续步骤,以充分发挥模型的效用:

1. **评估** 在保留的测试数据上进行全面评估,以衡量泛化能力并避免过拟合。
2. **实验** 尝试不同的超参数值,以在准确率、速度和内存之间取得更好的权衡。
3. **跟踪** 使用 Weights & Biases 跟踪所有实验(及相应指标),以实现可复现的研究。
4. **尝试** 在您自己的自定义数据集上进行训练,使模型专门适配您的使用场景。
5. **部署** 在兼容硬件上使用 vLLM 等高效后端部署您微调后的模型,以实现快速推理。
6. **探索** 高级技巧,包括提示工程、混合精度和更长的序列长度。
7. **训练** 针对不同任务或领域训练多个 LoRA 适配器,并根据需要进行切换。

---