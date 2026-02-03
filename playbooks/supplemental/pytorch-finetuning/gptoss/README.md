# GPT-OSS 20B Fine-tuning Examples

This directory contains complete examples for fine-tuning the **GPT-OSS 20B** model using different techniques on AMD Strix Halo (GFX1151).

## Model Information

- **Model**: GPT-OSS 20B (20 billion parameters)
- **Model ID**: `gpt-oss/gpt-oss-20b`
- **Architecture**: GPT-style decoder-only transformer
- **License**: Open source

## Available Training Scripts

### 1. Full Fine-tuning (`train_full_finetuning.py`)

Updates all model parameters for maximum quality.

**Characteristics:**
- ✓ Best quality and flexibility
- ✗ Highest memory usage (~80GB+ VRAM)
- ✗ Slowest training
- ✓ Best for significant behavior changes

**Memory**: ~80GB+ VRAM | **Speed**: Slowest | **Quality**: Best

```bash
python train_full_finetuning.py
```

**When to use:**
- You have substantial GPU memory (40GB+ VRAM)
- Maximum quality is paramount
- You need to significantly change model behavior

---

### 2. LoRA Fine-tuning (`train_lora.py`)

Trains small adapter matrices while freezing the base model.

**Characteristics:**
- ✓ Excellent quality (95%+ of full fine-tuning)
- ✓ Moderate memory usage (~24-32GB VRAM)
- ✓ Fast training (3-5x faster than full)
- ✓ Small adapter size (~100-300MB)
- ✓ Can train multiple adapters for different tasks

**Memory**: ~24-32GB VRAM | **Speed**: Fast | **Quality**: Excellent

```bash
python train_lora.py
```

**When to use:**
- Balanced approach between quality and efficiency
- Want to train multiple task-specific adapters
- Need fast iteration cycles
- Have 24GB+ VRAM available

**LoRA Parameters:**
- **Rank (r)**: 32 - Controls adapter capacity
- **Alpha**: 64 - Scaling factor (2×rank)
- **Target modules**: Attention + MLP layers
- **Dropout**: 0.05 - Regularization

---

### 3. QLoRA Fine-tuning (`train_qlora.py`)

Most memory-efficient method using 4-bit quantization + LoRA.

**Characteristics:**
- ✓ Lowest memory usage (~12-16GB VRAM)
- ✓ Fastest training
- ✓ 75% memory reduction vs full precision
- ✓ Can train massive models on consumer GPUs
- ⚠ Slight quality degradation (~3-5%)

**Memory**: ~12-16GB VRAM | **Speed**: Fastest | **Quality**: Very Good

```bash
python train_qlora.py
```

**When to use:**
- Limited GPU memory (16GB-24GB VRAM)
- Rapid experimentation and prototyping
- Training 20B+ models on consumer hardware
- Quality loss from quantization is acceptable

**QLoRA Parameters:**
- **Quantization**: 4-bit NF4 (Normal Float 4)
- **Compute dtype**: BFloat16
- **Double quantization**: Enabled
- **LoRA rank**: 64 (higher to compensate for quantization)
- **LoRA alpha**: 128

---

## Quick Start

### Prerequisites

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.0
pip install transformers accelerate peft trl datasets bitsandbytes
```

### Run Your First Training

**Option 1: QLoRA (Recommended for most users)**
```bash
python train_qlora.py
```
Expected time: 2-4 hours for 1000 samples on STX Halo

**Option 2: LoRA (If you have 24GB+ VRAM)**
```bash
python train_lora.py
```
Expected time: 3-5 hours for 1000 samples

**Option 3: Full Fine-tuning (If you have 40GB+ VRAM)**
```bash
python train_full_finetuning.py
```
Expected time: 8-12 hours for 1000 samples

---

## Comparison Table

| Method | VRAM Needed | Training Time | Quality | Adapter Size | Use Case |
|--------|-------------|---------------|---------|--------------|----------|
| **Full** | 80GB+ | 8-12h | 100% | Full model (~40GB) | Maximum quality, ample resources |
| **LoRA** | 24-32GB | 3-5h | 95-98% | ~100-300MB | Balanced approach, multiple adapters |
| **QLoRA** | 12-16GB | 2-4h | 90-95% | ~100-300MB | Limited resources, fast iteration |

*Times based on 1000 training samples on AMD Strix Halo*

---

## Using Your Fine-tuned Model

### After Full Fine-tuning

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("output-gpt-oss-20b-full")
tokenizer = AutoTokenizer.from_pretrained("output-gpt-oss-20b-full")

prompt = "Give me a quote about wisdom:"
inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=100)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### After LoRA/QLoRA Training

```python
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

# Load model with adapter
model = AutoPeftModelForCausalLM.from_pretrained(
    "output-gpt-oss-20b-qlora",
    device_map="auto",
    torch_dtype=torch.bfloat16
)
tokenizer = AutoTokenizer.from_pretrained("output-gpt-oss-20b-qlora")

# Generate
prompt = "Give me a quote about wisdom:"
inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=100)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Merge LoRA Adapter with Base Model

```python
from peft import AutoPeftModelForCausalLM

# Load model with adapter
model = AutoPeftModelForCausalLM.from_pretrained(
    "output-gpt-oss-20b-lora",
    device_map="auto"
)

# Merge and save
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gpt-oss-20b-merged")
tokenizer.save_pretrained("gpt-oss-20b-merged")
```

---

## Customization Guide

### Using Your Own Dataset

Replace the dataset loading section in any script:

```python
from datasets import load_dataset

# Option 1: Load from local JSON/JSONL
ds = load_dataset('json', data_files='your_data.json')

# Option 2: Load from Hugging Face Hub
ds = load_dataset('username/dataset-name')

# Format your data
def format_chat(example):
    return {
        "messages": [
            {"role": "user", "content": example['instruction']},
            {"role": "assistant", "content": example['response']}
        ]
    }

ds = ds.map(format_chat)
```

### Adjusting Training Parameters

**For faster training (lower quality):**
```python
LR = 5e-4              # Higher learning rate
EPOCHS = 1             # Fewer epochs
BATCH_SIZE = 8         # Larger batch
LORA_R = 16            # Smaller rank
```

**For better quality (slower training):**
```python
LR = 1e-4              # Lower learning rate
EPOCHS = 5             # More epochs
GRAD_ACCUM_STEPS = 8   # More gradient accumulation
LORA_R = 64            # Larger rank
```

### Memory Optimization Tips

If you run out of memory:

1. **Reduce batch size:**
   ```python
   BATCH_SIZE = 1
   GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
   ```

2. **Enable gradient checkpointing** (Full fine-tuning only):
   ```python
   model.gradient_checkpointing_enable()
   ```

3. **Reduce sequence length:**
   ```python
   max_seq_length=256  # Instead of 512
   ```

4. **Use more aggressive quantization:**
   - Full → LoRA → QLoRA

---

## Monitoring Training

### Track with Weights & Biases

```bash
pip install wandb
wandb login
```

In training script:
```python
args = SFTConfig(
    # ... other args ...
    report_to="wandb",
    run_name="gpt-oss-20b-qlora-experiment"
)
```

### Watch GPU Memory

```bash
# AMD ROCm
watch -n 1 rocm-smi

# Check memory usage
rocm-smi --showmeminfo vram
```

---

## Troubleshooting

### Out of Memory (OOM)

**Solution 1:** Reduce batch size
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
```

**Solution 2:** Use QLoRA instead of LoRA
```bash
python train_qlora.py  # Instead of train_lora.py
```

**Solution 3:** Reduce sequence length
```python
max_seq_length=256  # In SFTConfig
```

### Loss Not Decreasing

**Solution 1:** Adjust learning rate
```python
LR = 1e-4  # Try lower LR
# or
LR = 5e-4  # Try higher LR
```

**Solution 2:** Check data formatting
Ensure your dataset messages are properly formatted

**Solution 3:** Add warmup
```python
warmup_ratio=0.1  # 10% warmup steps
```

### Slow Training

**Solution 1:** Increase batch size
```python
BATCH_SIZE = 8  # If memory allows
```

**Solution 2:** Use BF16
```python
bf16=True  # Should already be enabled
```

**Solution 3:** Reduce logging
```python
logging_steps=20  # Instead of 5
```

---

## Next Steps

After successfully fine-tuning:

1. **Evaluate your model** on a held-out test set
2. **Try different datasets** for your specific use case
3. **Experiment with hyperparameters** (learning rate, rank, etc.)
4. **Deploy your model** with vLLM or Text Generation Inference
5. **Train multiple adapters** for different tasks (LoRA only)
6. **Explore advanced techniques** (see ../OTHER_TECHNIQUES.md)

---

## Additional Resources

- [PEFT Documentation](https://huggingface.co/docs/peft)
- [TRL Documentation](https://huggingface.co/docs/trl)
- [QLoRA Paper](https://arxiv.org/abs/2305.14314)
- [LoRA Paper](https://arxiv.org/abs/2106.09685)
- [Hugging Face Models](https://huggingface.co/models)
- [Hugging Face Datasets](https://huggingface.co/datasets)
