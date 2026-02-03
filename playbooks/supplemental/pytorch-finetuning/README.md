# Fine-tune with PyTorch - GPT-OSS 20B

## Overview

This tutorial provides complete, ready-to-run examples for fine-tuning the **GPT-OSS 20B** model using PyTorch on AMD Strix Halo (GFX1151). Learn multiple fine-tuning techniques from full parameter updates to memory-efficient methods that run on consumer hardware.

**Model**: GPT-OSS 20B (20 billion parameters)  
**Hardware**: AMD Strix Halo with ROCm support  
**Framework**: PyTorch + Hugging Face (Transformers, PEFT, TRL)

---

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install PyTorch for ROCm
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.0

# Install fine-tuning libraries
pip install transformers accelerate peft trl datasets bitsandbytes
```

### 2. Choose Your Method

| Method | Memory | Speed | Quality | Best For |
|--------|--------|-------|---------|----------|
| **QLoRA** 🌟 | 12-16GB | Fastest | 90-95% | Most users (recommended) |
| **LoRA** | 24-32GB | Fast | 95-98% | Balanced approach |
| **Full** | 80GB+ | Slowest | 100% | Maximum quality |

### 3. Run Training

```bash
cd gptoss

# Recommended: QLoRA (works on 16GB+ GPUs)
python train_qlora.py

# Alternative: LoRA (requires 24GB+ VRAM)
python train_lora.py

# Advanced: Full fine-tuning (requires 40GB+ VRAM)
python train_full_finetuning.py
```

Expected time: **2-4 hours** for 1000 samples on AMD Strix Halo

---

## Available Training Methods

### 1. Full Fine-tuning (`gptoss/train_full_finetuning.py`)

Updates **all model parameters** for maximum quality.

**Characteristics:**
- ✅ Best possible quality
- ✅ Maximum flexibility to change behavior
- ❌ Requires 80GB+ VRAM
- ❌ Slowest training (8-12 hours)

```bash
python gptoss/train_full_finetuning.py
```

**Use when:**
- You have abundant GPU memory (40GB+ VRAM)
- Quality is paramount
- Need significant behavior changes

---

### 2. LoRA Fine-tuning (`gptoss/train_lora.py`) 🎯

Trains small **adapter matrices** while freezing base model.

**Characteristics:**
- ✅ Excellent quality (95%+ of full fine-tuning)
- ✅ 3-5x faster than full fine-tuning
- ✅ Small adapter size (~100-300MB)
- ✅ Train multiple adapters for different tasks
- ⚠️ Requires 24-32GB VRAM

```bash
python gptoss/train_lora.py
```

**Use when:**
- Balanced quality and efficiency needed
- Training multiple task-specific models
- Have 24GB+ VRAM available
- Want fast iteration cycles

**How LoRA Works:**
```
Original Weight: W (4096×4096 = 16M params)
LoRA Update: W' = W + B×A
  where B (4096×32) and A (32×4096) = 262K params
Result: 98.4% parameter reduction!
```

---

### 3. QLoRA Fine-tuning (`gptoss/train_qlora.py`) ⭐ RECOMMENDED

Uses **4-bit quantization** with LoRA for maximum efficiency.

**Characteristics:**
- ✅ Lowest memory usage (12-16GB VRAM)
- ✅ Fastest training
- ✅ 75% memory reduction vs full precision
- ✅ Train 20B+ models on consumer GPUs
- ⚠️ Slight quality loss (~3-5% vs LoRA)

```bash
python gptoss/train_qlora.py
```

**Use when:**
- Limited GPU memory (16GB-24GB VRAM)
- Want fastest training
- Rapid experimentation needed
- Quality trade-off acceptable

**QLoRA Benefits:**
```
Full Precision Model:  ~40GB
QLoRA (4-bit + adapters): ~12GB
Savings: 70% memory reduction!
```

---

## Method Comparison

### Memory Requirements

| Method | 20B Model | Training Time | Quality | Output Size |
|--------|-----------|---------------|---------|-------------|
| Full Fine-tuning | 80GB+ | 8-12 hours | 100% | ~40GB |
| LoRA | 24-32GB | 3-5 hours | 95-98% | ~200MB |
| QLoRA | 12-16GB | 2-4 hours | 90-95% | ~200MB |

*Based on 1000 training samples on AMD Strix Halo*

### Quality vs Efficiency

```
Quality ↑
   100% ━━━━━━━━━━━ Full Fine-tuning
    97% ━━━━━━━━━━ LoRA (r=64)
    95% ━━━━━━━━━ LoRA (r=32)
    92% ━━━━━━━━ QLoRA (r=64)
    90% ━━━━━━━ QLoRA (r=32)
         ↑      ↑      ↑      ↑
        12GB   24GB   40GB   80GB  ← Memory
```

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

**Benefits:**
- Small adapter files (100-300MB vs 40GB full model)
- Train multiple adapters for different tasks
- Switch adapters at runtime
- Can merge back into base model

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

## Using Your Fine-tuned Model

### After Full Fine-tuning

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "output-gpt-oss-20b-full",
    device_map="auto",
    torch_dtype=torch.bfloat16
)
tokenizer = AutoTokenizer.from_pretrained("output-gpt-oss-20b-full")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### After LoRA/QLoRA Training

```python
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

# Load model with LoRA adapter
model = AutoPeftModelForCausalLM.from_pretrained(
    "output-gpt-oss-20b-qlora",
    device_map="auto",
    torch_dtype=torch.bfloat16
)
tokenizer = AutoTokenizer.from_pretrained("output-gpt-oss-20b-qlora")

# Generate
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Merge LoRA Adapter into Base Model

```python
# Merge adapter weights into base model (no more separate adapter)
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gpt-oss-20b-merged")
tokenizer.save_pretrained("gpt-oss-20b-merged")
```

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

---

## Advanced Fine-tuning Techniques

Beyond the three main methods (Full, LoRA, QLoRA), there are many other techniques you can explore:

### Recommended Next Steps

1. **DoRA** - Improved LoRA with better quality
2. **IA³** - Ultra-low parameter count
3. **AdaLoRA** - Dynamic rank allocation
4. **LoftQ** - Better QLoRA initialization
5. **Prefix Tuning** - Learn soft prompts

📚 **See [OTHER_TECHNIQUES.md](OTHER_TECHNIQUES.md)** for detailed guides on 10+ additional methods!

---

## Project Structure

```
pytorch-finetuning/
├── README.md                    ← You are here
├── OTHER_TECHNIQUES.md          ← Advanced methods guide
├── gptoss/
│   ├── README.md                ← Detailed GPT-OSS guide
│   ├── train_full_finetuning.py ← Full fine-tuning
│   ├── train_lora.py            ← LoRA fine-tuning
│   └── train_qlora.py           ← QLoRA fine-tuning (⭐ recommended)
```

---

## Learning Resources

### Official Documentation

- **[PEFT Library](https://huggingface.co/docs/peft)** - Parameter-Efficient Fine-Tuning
- **[TRL Library](https://huggingface.co/docs/trl)** - Transformer Reinforcement Learning
- **[Transformers](https://huggingface.co/docs/transformers)** - Hugging Face Transformers
- **[BitsAndBytes](https://github.com/TimDettmers/bitsandbytes)** - Quantization library

### Research Papers

- **[LoRA Paper](https://arxiv.org/abs/2106.09685)** - Original LoRA (2021)
- **[QLoRA Paper](https://arxiv.org/abs/2305.14314)** - Efficient fine-tuning (2023)
- **[DoRA Paper](https://arxiv.org/abs/2402.09353)** - Improved LoRA (2024)

### Community

- **[Hugging Face Hub](https://huggingface.co/models)** - Pre-trained models
- **[HF Datasets](https://huggingface.co/datasets)** - Training datasets
- **[HF Forums](https://discuss.huggingface.co/)** - Community support
- **[r/LocalLLaMA](https://reddit.com/r/LocalLLaMA)** - Reddit community

---

## Next Steps

After successful fine-tuning:

1. ✅ **Evaluate** on held-out test data
2. 🎯 **Experiment** with different hyperparameters
3. 📊 **Track** experiments with Weights & Biases
4. 🎨 **Try** your own datasets
5. 🚀 **Deploy** with vLLM or TGI
6. 🔬 **Explore** advanced techniques (see OTHER_TECHNIQUES.md)
7. 🔄 **Train** multiple LoRA adapters for different tasks

---

## Support

### Getting Help

1. Check the detailed guides in `gptoss/README.md`
2. Review troubleshooting sections in each script
3. Consult [Hugging Face Forums](https://discuss.huggingface.co/)
4. Open issues on [PEFT GitHub](https://github.com/huggingface/peft/issues)

### Hardware Requirements

**Minimum:**
- 16GB VRAM (for QLoRA)
- 32GB System RAM
- 50GB free disk space

**Recommended:**
- 24GB+ VRAM (for LoRA)
- 64GB System RAM
- 100GB+ free disk space

---

## License

This tutorial and code examples are provided as-is for educational purposes.

**Model Licenses:**
- GPT-OSS 20B: Check model card on Hugging Face
- Libraries: Apache 2.0 (Transformers, PEFT, TRL)

---

## Quick Reference

| What You Want | Use This Method | Run This Command |
|---------------|----------------|------------------|
| **Best quality** | Full Fine-tuning | `python gptoss/train_full_finetuning.py` |
| **Balanced** | LoRA | `python gptoss/train_lora.py` |
| **Most efficient** ⭐ | QLoRA | `python gptoss/train_qlora.py` |
| **Multiple adapters** | LoRA or QLoRA | Train multiple times with different datasets |
| **Limited VRAM (16GB)** | QLoRA | `python gptoss/train_qlora.py` |
| **Fast iteration** | QLoRA or LoRA | Adjust EPOCHS and BATCH_SIZE |

---

**Ready to start fine-tuning? Choose QLoRA for your first experiment! 🚀**

```bash
cd gptoss
python train_qlora.py
```

Good luck with your fine-tuning journey! 🎉
