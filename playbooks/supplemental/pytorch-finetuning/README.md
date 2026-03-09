# Fine-tune LLMs with Pytorch and ROCm

## Overview

This tutorial provides step-by-step examples for fine-tuning a large language model with PyTorch and ROCm on AMD Strix Halo. It covers several techniques, from standard fine-tuning to memory-efficient PEFT strategies, so you can easily adapt models for your needs.

**Model Used**: google/gemma-3-4b-it  
*(this model is gated; see [Enable HF authentication](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models))*  
**Hardware**: AMD Strix Halo with ROCm support  
**Framework**: PyTorch + Hugging Face (Transformers, PEFT, TRL)

> **Note:** You can also try other model architectures, including **GPT-OSS-20B**, by substituting the model in the provided training scripts.

## Quick Start

### 1. Install Dependencies

<!-- @os:windows -->
<!-- @test:id=create-venv timeout=60 -->
```cmd
python -m venv venv
venv\Scripts\activate.bat
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="venv\Scripts\activate.bat" -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv venv
source venv/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source venv/bin/activate" -->
<!-- @os:end -->

### Installing Basic Dependencies
<!-- @require:pytorch -->

### Additional Dependencies

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

### Enable HF authentication (gated or custom / non–preinstalled models)

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

<!-- @test:id=quick-train-one-step timeout=600 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys
os.environ["QUICK_TRAIN"] = "1"
r = subprocess.run([sys.executable, "train_lora.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->

### 2. Choose Your Method

| Method | Memory | Speed | Quality | Best For |
|--------|--------|-------|---------|----------|
| **QLoRA** 🌟 | 12-16GB | Fastest | 90-95% | Most users|
| **LoRA** | 24-32GB | Fast | 95-98% | Balanced approach |
| **Full** | 80GB+ | Slowest | 100% | Maximum quality |

### 3. Run Training

**Dataset and what the model learns**  
The scripts turn the dataset into chat examples. For example, the QLoRA script uses **Abirate/english_quotes**: each example becomes a user–assistant pair like:

- **User:** “Give me a quote about: &lt;tag&gt;”
- **Assistant:** “&lt;quote&gt; – &lt;author&gt;”

So fine-tuning teaches the model to respond to prompts asking for quotes about a topic and to return them in the format `<quote text> - <author>`. The LoRA and full fine-tuning scripts use **databricks/databricks-dolly-15k** (general instruction/response pairs), so the exact task varies by script; the idea is the same - adapt the model to your chosen dataset and format.

Below is a summary of available training methods. Each method links to its script and provides a brief description for choosing the right approach.

| Script                           | Method            | Description                                                                                                         | Typical VRAM | Recommended For                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_qlora.py`](assets/train_qlora.py)               | **QLoRA** 🌟        | 4-bit quantization + LoRA adapters. Lowest memory use, fastest, small quality trade-off.                            | 12–16GB      | Most users; fast experiments; limited VRAM      |
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA** 🎯         | Trains small adapter matrices while freezing base model. 3–5x faster; ~95–98% full quality.                         | 24–32GB      | Advanced users; multiple adapters; more VRAM    |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Full Fine-tuning** | Updates all model parameters. Maximum quality; highest memory and compute usage.                                    | 40GB+        | Maximum quality; research; large VRAM           |

> **Typical time:** ~15–20 minutes for 800 samples on AMD Strix Halo

---

## Understanding the Techniques

### What is LoRA?

**LoRA (Low-Rank Adaptation)** keeps the base model frozen and only trains small "adapter" matrices that get added to certain layers. The key idea: instead of updating a huge weight matrix with millions of parameters, we learn a low-rank update (two small matrices whose product has much fewer parameters). That gives a large reduction in trainable parameters and VRAM while keeping most of the full fine-tuning quality.

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

**QLoRA** combines **4-bit quantization** with **LoRA**: the base model is loaded in 4-bit (large memory savings), and only the LoRA adapters are trained in higher precision. So you get the parameter efficiency of LoRA plus much lower VRAM, with a small quality trade-off compared to full-precision LoRA.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```
---

## Using Your Fine-tuned Model

### After Full Fine-tuning

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "output-gemma-3-4b-full",     # Directory containing your fully fine-tuned checkpoint
    device_map="auto",
    torch_dtype="auto"            # Use BF16 if your GPU supports it, else "auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-full")

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
    "output-gemma-3-4b-qlora",   # or "output-gemma-3-4b-lora" depending on your training
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-qlora")

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

---

## Customization Guide

### Use Your Own Dataset

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

**Dataset Format:**
```json
[
  {
    "messages": [
      {"role": "user", "content": "Your instruction here"},
      {"role": "assistant", "content": "Expected response here"}
    ]
  }
]
```

### Adjust Training Parameters

Edit the training script and change the variables to match your goals: **learning rate** (`LR`), **epochs** (`EPOCHS`), **batch size** (`BATCH_SIZE`), **gradient accumulation** (`GRAD_ACCUM_STEPS`), and for LoRA/QLoRA **rank** (`LORA_R`). For faster runs use fewer epochs and a higher LR; for better quality use more epochs and a lower LR. Reduce batch size or sequence length if you hit out-of-memory errors.

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
watch -n 1 rocm-smi

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

Good luck with your fine-tuning journey! 🎉
