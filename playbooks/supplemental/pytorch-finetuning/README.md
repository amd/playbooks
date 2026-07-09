<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Overview

This tutorial provides step-by-step examples for fine-tuning a large language model (LLM) with PyTorch and ROCm. It covers several techniques, from standard fine-tuning to memory-efficient Parameter-Efficient Fine-Tuning (PEFT) strategies, so you can easily adapt models for your needs.

**Model Used**: google/gemma-3-4b-it  *(see [Enable HF authentication](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) if gated)*  
**Hardware**: AMD Radeon™ GPU with ROCm support  
**Framework**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Note:** You can also try other model architectures, including **GPT-OSS-20B**, by substituting the model in the provided training scripts.
> Full fine-tuning requires at least 32 GB of GPU memory and 64 GB of system RAM.
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> **Note:** LoRA and QLoRA fine-tuning require at least 16 GB of GPU memory and 32 GB system RAM.
<!-- @device:end -->

## What You'll Learn

- How to fine-tune an LLM using LoRA, QLoRA, and full fine-tuning with PyTorch and ROCm
- How to save and deploy your fine-tuned model
- How to monitor training and debug common issues

## Setting the Memory Configuration

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Check for Software Updates
> **Note**: If VS Code is not installed, you can install it with Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installing Software Prerequisites

#### Create a Virtual Environment

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
**Grant your user access to GPU devices** (log out and back in for this to take effect):

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

#### Installing Basic Dependencies
<!-- @require:pytorch -->

#### Additional Dependencies

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Only core packages are tested and supported here. **bitsandbytes is not well supported on Windows**, so the Windows install omits it; use LoRA or full fine-tuning on Windows (QLoRA requires bitsandbytes and is intended for Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### Enable HF authentication (gated or custom / non–preinstalled models)

In this example we use **google/gemma-3-4b-it**, which is a **gated** model. You must accept the model’s terms on Hugging Face and then authenticate so the training scripts can download it.

1. **Accept the license:** Open [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), sign in (or create an account), and accept the license/terms on the model page (e.g. “Agree and access repository”).
2. **Install and log in:** Install the Hugging Face CLI, then run the standard login:

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

## Understanding the Techniques

### What is LoRA?

**LoRA (Low-Rank Adaptation)** keeps the base model frozen and only trains small "adapter" matrices that get added to certain layers. 

- **The key idea**: instead of updating a huge weight matrix with millions of parameters, we learn a low-rank update (two small matrices whose product has much fewer parameters). That gives a large reduction in trainable parameters and VRAM while keeping most of the full fine-tuning quality.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### What is QLoRA?

**QLoRA** combines **4-bit quantization** with **LoRA**. The base model is loaded in 4-bit (large memory savings), and only the LoRA adapters are trained in higher precision. So you get the parameter efficiency of LoRA plus much lower VRAM, with a small quality trade-off compared to full-precision LoRA. Note that 4-bit quantization can cause numerical instabilities (loss spikes or NaNs), so users may often prefer **LoRA** if enough VRAM is available.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Note**: For MXFP4 base models like `openai/gpt-oss-20b`, we recommend using **LoRA** (`train_lora.py`) instead of QLoRA. The QLoRA script's `bitsandbytes` 4-bit path typically dequantizes MXFP4 weights to BF16, so the run behaves like standard LoRA. Native MXFP4 needs `bitsandbytes` built from source plus a matching Transformers/Triton/kernels stack. See the [Transformers MXFP4 docs](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---

### 2. Choose Your Method

| Method | Memory | Speed | Quality | Best For |
|--------|--------|-------|---------|----------|
| **QLoRA** (Linux only) | 12-16GB | Fastest | 90-95% | Low Memory Usage |
| **LoRA** | 24-32GB | Fast | 95-98% | Balanced approach |
| **Full** | 80GB+ | Slowest | 100% | Maximum quality |

### 3. Run Training

**Dataset and what the model learns**  
The scripts turn the dataset into chat examples. For example, the QLoRA script uses **Abirate/english_quotes**: each example becomes a user–assistant pair like:

- **User:** “Give me a quote about: &lt;tag&gt;”
- **Assistant:** “&lt;quote&gt; – &lt;author&gt;”

Fine-tuning teaches the model to respond to prompts asking for quotes about a topic and to return them in the format `<quote text> - <author>`. The LoRA and full fine-tuning scripts use **databricks/databricks-dolly-15k** (general instruction/response pairs), so the exact task varies by script; the idea is the same - adapt the model to your chosen dataset and format.

Below is a summary of the available training methods. Each method links to its script and provides a brief description for choosing the right approach.

| Script                           | Method            | Description                                                                                                         | Typical VRAM | Recommended For                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Trains small adapter matrices while freezing base model. 3–5x faster; ~95–98% full quality.                         | 24–32GB      | Advanced users; multiple adapters; more VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(Linux only)*             | **QLoRA**       | 4-bit quantization + LoRA adapters. Lowest memory use, fastest, small quality trade-off. Requires `bitsandbytes` (Linux only).                            | 12–16GB      | Most users; fast experiments; limited VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Full Fine-tuning** | Updates all model parameters. Maximum quality; highest memory and compute usage.                                    | 40GB+        | Maximum quality; research; large VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Note:** Full fine-tuning (`train_full_finetuning.py`) may require more than 64GB of system RAM and may not be feasible on this device. Consider using LoRA or QLoRA instead.
<!-- @os:end -->

<!-- @os:windows -->
> **Note:** Full fine-tuning (`train_full_finetuning.py`) may require more than 64GB of system RAM and may not be feasible on this device. Consider using LoRA instead.
<!-- @os:end -->
<!-- @device:end -->

Simply select your preferred `Training method`, download the corresponding script and execute it using the command keeping your virtual environment activated: 

```python
python3 train_<method_name>.py.
```

## Using your Fine-Tuned Model

### After Full Fine-Tuning

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

### After LoRA/QLoRA Training

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

### Merge LoRA Adapter into Base Model

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Note:**  
- Make sure the model directory name (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) matches your actual output folder from training.  
- If you used LoRA instead of QLoRA, just substitute the path accordingly.  
- Some Gemma models require specifying `trust_remote_code=True` in `from_pretrained`; add if you see a related warning.

For more custom settings (padding tokens, device, etc), refer to the script that you used for training.

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

## Customization Guide

### Use your Own Dataset

All scripts use the same dataset format. Replace the loading section:

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

**Dataset Format for Local JSON/JSONL file:**

When using this method, please ensure that your JSON files are correctly structured to avoid parsing errors. 

The following guidelines must be adhered to:
* **File Formatting:** JSON files should be formatted within an Integrated Development Environment (IDE) to ensure proper structure and syntax.
* **Required Keys:** The custom JSON file must contain the keys `instruction` and `response`. These keys are essential for the method to function correctly.
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
**Dataset Format for Hugging Face Hub dataset**

When utilizing datasets from Hugging Face, please ensure that your datasets are structured correctly to facilitate seamless integration. 

The following guidelines should be followed:
* **Instruction-Response Pair:** Focus on datasets that include an `instruction-response` pair. This structure is essential for the intended functionality.
* **Custom Key Modification:** If your dataset does not conform to the `instruction-response` structure, you have the option to modify the `format_instruction()` function. This allows you to accommodate specific keys as needed.

Example Adjustment: In cases where the dataset's output needs to be adjusted, you can modify the response section within the format_instruction() function to fit your requirements.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Dataset Format for CSV file**

To accommodate the script using a CSV file format, you need to ensure that the CSV file contains columns named `instruction` and `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Adjust Training Parameters

Edit the training script and change the variables to match your goals: **learning rate** (`LR`), **epochs** (`EPOCHS`), **batch size** (`BATCH_SIZE`), **gradient accumulation** (`GRAD_ACCUM_STEPS`), and for LoRA/QLoRA **rank** (`LORA_R`). For faster runs use fewer epochs and a higher learning rate (LR); for better quality use more epochs and a lower LR. Reduce batch size or sequence length if you hit out-of-memory errors.

### Memory Optimization Tips

If you encounter out-of-memory errors:

**1. Reduce Batch Size:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Reduce Sequence Length:**
```python
max_seq_length=256  # Instead of 512
```

**3. Use More Aggressive Quantization:**
```
Full → LoRA → QLoRA
```

**4. Enable Gradient Checkpointing (Full fine-tuning only):**
```python
model.gradient_checkpointing_enable()
```

---

## Monitoring & Debugging

### Watch GPU Memory

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Optional) Track Experiments with Weights & Biases

To log runs and metrics to [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

In the training script, set `report_to="wandb"` and optionally `run_name="your-experiment-name"` in the trainer config. If you prefer not to use Wandb, leave `report_to` at its default or set it to `"none"`.

### Common Issues

#### Out of Memory (OOM)

**Solution:** Reduce batch size and/or use QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### Loss Not Decreasing

**Solution:** Adjust learning rate
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Slow Training

**Solution:** Increase batch size if memory allows
```python
BATCH_SIZE = 8
```
## Next Steps

After you have completed successful fine-tuning, consider the following next steps to get more from your model:

1. **Evaluate** thoroughly on held-out test data to measure generalization and avoid overfitting.
2. **Experiment** by trying different hyperparameter values for better accuracy, speed, and memory trade-offs.
3. **Track** all your experiments (and corresponding metrics) with Weights & Biases for reproducible research.
4. **Try** training on your own custom datasets to adapt the model specifically for your use-case.
5. **Deploy** your fine-tuned model for fast inference using efficient backends such as vLLM on compatible hardware.
6. **Explore** advanced techniques including prompt engineering, mixed precision, and longer sequence lengths.
7. **Train** multiple LoRA adapters for different tasks or domains and swap them as needed.

---