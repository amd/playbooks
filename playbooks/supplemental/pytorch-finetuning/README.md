# Fine-tune with PyTorch - Gemma-3-4B

## Overview

This tutorial provides step-by-step examples for fine-tuning a large language model with PyTorch and ROCm on AMD Strix Halo. It covers several techniques, from standard fine-tuning to memory-efficient PEFT strategies, so you can easily adapt models for your needs.

**Model Used**: google/gemma-3-4b-it
**Hardware**: AMD Strix Halo with ROCm support  
**Framework**: PyTorch + Hugging Face (Transformers, PEFT, TRL)

> **Note:** You can also try other model architectures, including **GPT-OSS-20B**, by substituting the model in the provided training scripts.

---

## Quick Start

### 1. Install Dependencies

<!-- @os:linux -->
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate
```
<!-- os:end -->

<!-- @os:windows -->
```bat
python -m venv venv
venv\Scripts\activate
```
<!-- os:end -->

### Installing Basic Dependencies
<!-- @require:pytorch -->

### Additional Dependencies

<!-- @os:linux -->

```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- os:end -->

<!-- @os:windows -->
**Windows:** Only core packages are tested and supported here.
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- os:end -->

### Enable HF Authentication if not using local models
Authenticate with the Hugging Face Hub to access some model files:
```bash
hf auth login
```

### 2. Choose Your Method

| Method | Memory | Speed | Quality | Best For |
|--------|--------|-------|---------|----------|
| **QLoRA** 🌟 | 12-16GB | Fastest | 90-95% | Most users|
| **LoRA** | 24-32GB | Fast | 95-98% | Balanced approach |
| **Full** | 80GB+ | Slowest | 100% | Maximum quality |

### 3. Run Training

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

**LoRA (Low-Rank Adaptation)** freezes the original model and trains small "adapter" matrices:

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

**QLoRA** = **4-bit Quantization** + **LoRA**

1. Load base model in 4-bit (75% memory savings)
2. Add LoRA adapters trained in BF16
3. Best of both worlds!

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

---

## Using Your Fine-tuned Model (for Gemma 3 4B)

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

#### For Faster Training (Lower Quality)
```python
LR = 5e-4              # Higher learning rate
EPOCHS = 1             # Fewer epochs
BATCH_SIZE = 8         # Larger batch (if memory allows)
LORA_R = 16            # Smaller rank
```

#### For Better Quality (Slower Training)
```python
LR = 1e-4              # Lower learning rate
EPOCHS = 5             # More epochs
GRAD_ACCUM_STEPS = 16  # More gradient accumulation
LORA_R = 64            # Larger rank
```

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

### Track Experiments with Weights & Biases

```bash
pip install wandb
wandb login
```

In training script:
```python
args = SFTConfig(
    # ... other settings ...
    report_to="wandb",
    run_name="gpt-oss-20b-qlora-experiment"
)
```

View metrics at [wandb.ai](https://wandb.ai)

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

After successful fine-tuning:

1. **Evaluate** on held-out test data
2. **Experiment** with different hyperparameters
3. **Track** experiments with Weights & Biases
4. **Try** your own datasets
5. **Deploy** with vLLM
6. **Explore** advanced techniques (see OTHER_TECHNIQUES.md)
7. **Train** multiple LoRA adapters for different tasks

---

Good luck with your fine-tuning journey! 🎉
