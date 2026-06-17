<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Overview

This playbook shows how to fine-tune a language model locally with Unsloth on AMD hardware.

It uses a short Supervised Fine-Tuning (SFT) example with LoRA adapters on `unsloth/gemma-4-E4B-it`, using a subset of the `mlabonne/FineTome-100k` dataset. The goal is to give you a simple end-to-end workflow that covers setup, training, inference, and saving the fine-tuned result.

The example is designed to be practical and easy to modify, so you can use it as a starting point for your own datasets and models.

## What You'll Learn

- How to set up the Unsloth environment
- How to fine-tune a LLM using SFT with Unsloth
- How to save the fine-tuned result in local storage

<!-- @device:stx,krk -->
> **Note:** Some of the fine-tuning techniques in this playbook may require more than 64GB of system RAM.

<!-- @device:end -->

## Why Unsloth?

Unsloth makes LLM fine-tuning easier to run on local hardware by reducing memory usage and speeding up training compared to a standard setup.

In this playbook, we use Unsloth together with **LoRA-based SFT**. That means the base model stays mostly frozen, while a much smaller set of adapter weights is trained. This is a good fit for local development because it is lighter than full fine-tuning and faster to iterate on.

Unsloth also supports other training approaches, including QLoRA and reinforcement learning workflows. This playbook focuses on the simplest path first: a small LoRA fine-tuning example that users can run, understand, and extend.

## Setting the Memory Configuration

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Check for Software Updates
> **Note**: If VS Code is not installed, you can install it with Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installing Software Prerequisites

### Create a Virtual Environment

<!-- @os:linux -->
<!-- @device:halo_box -->
Open a terminal and create a venv with AMD ROCm™ software and PyTorch already installed:
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
python3 -m venv unsloth-env --system-site-packages
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
**Grant your user access to GPU devices** (log out and back in for this to take effect):

```bash
sudo usermod -aG render,video $LOGNAME
```

Open a terminal and create a venv:
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
> **Note:** Python 3.13 is required for Windows.

<!-- @device:halo_box -->
Open a PowerShell terminal and create a virtual environment:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
Open a PowerShell terminal and create a virtual environment:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Installing Basic Dependencies
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

### Additional Dependencies

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

> **Note:** During import, Unsloth may probe optional `bitsandbytes` acceleration paths. On some ROCm versions, you may see a message such as `bitsandbytes library load error: Configured ROCm binary not found`. This playbook uses standard LoRA fine-tuning with `optim="adamw_torch"`, so we do not rely on the `bitsandbytes` optimizer or 4-bit QLoRA. This message can be safely ignored.

<!-- @os:windows -->
> **Note:** On Windows ROCm, Unsloth will print several warnings at startup — see [Known Warnings](#known-warnings) below. These are all safe to ignore; training works correctly.
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

## Download the Unsloth Fine-Tuning Script

Instead of manually executing each step, this playbook provides a clean, end-to-end script here: [test_unsloth.py](assets/test_unsloth.py).

Run the following code to execute the script:

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

The rest of the playbook will conceptually go through each major step of the script. 

## How It Works

The test_unsloth.py script performs the following steps:
* **Load Model**: Loads unsloth/gemma-4-E4B-it using FastModel.
* **Prepare Data**: Standardizes the dataset (e.g., FineTome-100k) and applies the Gemma-4 chat template.
* **Apply LoRA**: Adds adapters to language, attention, and MLP modules for efficient training.
* **Train**: Uses SFTTrainer with response-only loss masking.
* **Inference**: Runs a quick generation test to verify performance.
* **Save**: Exports LoRA adapters locally.

## Key Configuration

You can modify the following constants to customize your run:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Example of the Unsloth welcome message and output when loading the model weights:

![alt text](assets/welcome.png)

## Prepare Dataset

We use a subset of:
```text
mlabonne/FineTome-100k
```
The dataset is: 
* Converted into chat format
* Processed using the Gemma-4 chat template
* Cleaned to remove duplicate BOS tokens

## Train the Model

The script runs a short training demo, with the following parameters:
- ~50 steps
- Small batch size
- Gradient accumulation

During training, you will see logs such as:

![alt text](assets/training.png)


## Saving and Deployment

### Local Saving (LoRA)

The script automatically saves LoRA adapters to the OUTPUT_DIR.
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

### Save merged model (for vLLM) 

<!-- @os:windows -->
> **Note:** vLLM does not support Windows. To deploy your fine-tuned model on Windows, use llama.cpp (see [Export GGUF](#export-gguf-for-llamacpp) below) or transfer the merged model to a Linux machine running vLLM.
<!-- @os:end -->

<!-- @os:linux -->
For deployment with vLLM, merge the adapters into a full model:
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

### Export GGUF (for llama.cpp)

Convert directly to GGUF for local inference:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Known Warnings

These warnings are printed by Unsloth at startup on Windows ROCm and are all safe to ignore:

| Warning | Reason | Safe to ignore? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes has no Windows ROCm build | Yes — this playbook uses `adamw_torch`, not bnb |
| `No ROCm platform found for torch.distributed` | ROCm-on-Windows lacks distributed training | Yes — single-GPU training is unaffected |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth flags non-Linux builds | Yes — Windows ROCm works for single-GPU SFT |
| `triton is not available` | Triton has no Windows build | Yes — Unsloth falls back to PyTorch kernels |

Training will proceed correctly despite these warnings.
<!-- @os:end -->

## Next Steps
- Try [Unsloth Studio](https://unsloth.ai/docs/new/studio), an intuitive GUI for Unsloth
- Train on your own specific datasets
- Try finetuning with different hyperparameters
- Deploy with vLLM or llama.cpp
- Try QLoRA for a lower-memory setup

## Resources

Below are some additional resources to learn more about Unsloth and finetuning:

* [Unsloth Docs](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth Fine-tuning Guide](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)
