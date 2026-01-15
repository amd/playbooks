## Overview

Fine-tuning large language models (LLMs) adapts pre-trained models to your specific tasks and data. Unlike training from scratch, fine-tuning leverages existing knowledge while teaching the model new behaviors—whether that's writing in a particular style, following specific instructions, or mastering domain-specific knowledge.

This tutorial teaches you how to fine-tune LLMs like Gemma models using PyTorch and popular libraries like Hugging Face Transformers, PEFT, and TRL on your STX Halo™ GPU. You'll learn multiple fine-tuning techniques, from full parameter updates to memory-efficient methods that run on consumer hardware.

## What You'll Learn

- Understanding different fine-tuning methods and when to use each
- Setting up your environment for LLM fine-tuning
- Preparing datasets for instruction tuning and chat models
- Running fine-tuning jobs on your STX Halo™
- Memory optimization techniques for large models

> **🚀 Quick Start**: If you want to jump straight to training, see [Running Your First Fine-Tuning Job](#running-your-first-fine-tuning-job) or browse the [Example Scripts Reference](#example-scripts-reference) to find the right script for your needs.

## Fine-Tuning Methods

Choose a fine-tuning method based on your GPU memory and quality requirements:

| Method | Memory Usage | Quality | Best For |
|--------|--------------|---------|----------|
| **QLoRA** | Lowest (~0.5× model size) | Good | Limited hardware (16GB VRAM), large models (70B+) |
| **8-bit + LoRA** | Low (1×–1.5× model size) | Very Good | 13B–30B models on 24GB GPUs |
| **LoRA** | Moderate (1.5×–2× model size) | Very Good | Task-specific adaptation, multiple adapters |
| **Full Fine-tuning** | Highest (4×+ model size) | Best | Smaller models (< 7B), maximum quality |

### QLoRA (4-bit Quantization + LoRA)

Most memory-efficient method using 4-bit quantization. Ideal for rapid experimentation and training large models on consumer hardware.

**Memory Requirements**: 7B: 5–7GB | 13B: 10–12GB | 30B: 20–24GB | 70B: 40–48GB

**Example Scripts**:
- Gemma: `assets/gemma/train_qlora.py`
- GPTOSS: `assets/gptoss/train_qlora.py`

[QLoRA Documentation](https://ai.google.dev/gemma/docs/core/huggingface_text_finetune_qlora)

---

### 8-bit + LoRA

Loads base model in 8-bit precision with LoRA adapters in full precision. Good balance of quality and efficiency.

**Memory Requirements**: 7B: 8–12GB | 13B: 16–20GB | 30B: 32–40GB

**Example Scripts**:
- Gemma: `assets/gemma/train_8bit_lora.py`
- GPTOSS: `assets/gptoss/train_8bit_lora.py`

---

### LoRA (Low-Rank Adaptation)

Trains small adapter matrices while freezing the base model. Excellent for creating multiple task-specific adapters.

**Memory Requirements**: 7B: 14–18GB | 13B: 28–32GB | 30B: 60–70GB

**Example Scripts**:
- Gemma: `assets/gemma/train_lora.py`
- GPTOSS: `assets/gptoss/train_lora.py`

[PEFT Documentation](https://huggingface.co/docs/peft)

---

### Full Fine-Tuning

Updates all model parameters. Provides maximum quality but requires significant GPU memory.

**Memory Requirements**: 7B: 28GB+ | 13B: 52GB+ | 30B+: 100GB+

**Example Scripts**:
- Gemma: `assets/gemma/train_full_finetuning.py`
- GPTOSS: `assets/gptoss/train_full_finetuning.py`

[Full Fine-tuning Guide](https://ai.google.dev/gemma/docs/core/huggingface_text_full_finetune)

## Prerequisites

### System Requirements

Your STX Halo™ GPU comes optimized for PyTorch with ROCm support. For fine-tuning, you'll need:

- **GPU Memory**: Minimum 16GB VRAM (24GB+ recommended for larger models)
- **System RAM**: 32GB+ recommended
- **Storage**: 50GB+ free space for models and datasets
- **Python**: 3.10 or newer

### Required Libraries

Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.0
pip install transformers accelerate peft trl datasets bitsandbytes
```

> **Note**: Your STX Halo™ uses AMD ROCm. The `bitsandbytes` library provides ROCm support for quantization on AMD GPUs.

## Preparing Your Dataset

Fine-tuning requires properly formatted training data. Most modern LLM fine-tuning uses **instruction-following** or **conversational** formats.

### Dataset Format

Your dataset should be in JSON or JSONL format with this structure:

**Instruction format:**

```json
[
  {
    "instruction": "Explain what photosynthesis is.",
    "input": "",
    "output": "Photosynthesis is the process by which plants convert light energy into chemical energy..."
  },
  {
    "instruction": "Translate the following to French.",
    "input": "Hello, how are you?",
    "output": "Bonjour, comment allez-vous?"
  }
]
```

**Chat format:**

```json
[
  {
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "What is machine learning?"},
      {"role": "assistant", "content": "Machine learning is a subset of artificial intelligence..."}
    ]
  }
]
```

### Popular Datasets

Here are some commonly used datasets for LLM fine-tuning:

- **openassistant-guanaco**: High-quality conversational dataset
- **alpaca**: Instruction-following dataset with 52K examples
- **dolly-15k**: Diverse instruction dataset from Databricks
- **ShareGPT**: Real ChatGPT conversations

You can load these from Hugging Face or prepare your own custom dataset following the formats above.

## Running Your First Fine-Tuning Job

We provide ready-to-use training scripts for popular LLMs. Select your model family and fine-tuning method:

### Gemma Models

Google's Gemma models (2B, 7B, and larger) are optimized for instruction following and chat:

```bash
# QLoRA (most accessible, 16GB+ VRAM)
python assets/gemma/train_qlora.py

# LoRA (better quality, 24GB+ VRAM)
python assets/gemma/train_lora.py

# 8-bit + LoRA (good balance, 16-24GB VRAM)
python assets/gemma/train_8bit_lora.py

# Full fine-tuning (maximum quality, 32GB+ VRAM)
python assets/gemma/train_full_finetuning.py
```

### GPTOSS Models

GPTOSS open-source models with strong general capabilities:

```bash
# QLoRA (most accessible, 16GB+ VRAM)
python assets/gptoss/train_qlora.py

# LoRA (better quality, 24GB+ VRAM)
python assets/gptoss/train_lora.py

# 8-bit + LoRA (good balance, 16-24GB VRAM)
python assets/gptoss/train_8bit_lora.py

# Full fine-tuning (maximum quality, 32GB+ VRAM)
python assets/gptoss/train_full_finetuning.py
```

### Steps to Fine-Tune

1. **Prepare your dataset** in instruction or chat format (see [Preparing Your Dataset](#preparing-your-dataset))
2. **Choose a script** based on your model and available GPU memory
3. **Edit the script** to point to your dataset path and adjust hyperparameters if needed
4. **Run the training** using one of the commands above

Training a 7B model on a typical instruction dataset should complete in 2–4 hours on your STX Halo™.

> **Tip**: Start with QLoRA—it's the most memory-efficient and works well for most use cases. You can always switch to LoRA or full fine-tuning later if you need higher quality.

<!-- ## Using Your Fine-Tuned Model -->

<!-- After training completes, you'll have either a fully fine-tuned model or LoRA adapter weights. Use the inference scripts to load and test your model:

**Gemma Models**:
- `assets/gemma/inference_full_model.py` - Load and use a fully fine-tuned Gemma model
- `assets/gemma/inference_lora_adapter.py` - Load base Gemma model + LoRA adapter

**GPTOSS Models**:
- `assets/gptoss/inference_full_model.py` - Load and use a fully fine-tuned GPTOSS model
- `assets/gptoss/inference_lora_adapter.py` - Load base GPTOSS model + LoRA adapter -->

## Best Practices

### 1. Start Small, Scale Up

Begin with QLoRA on a small model (Gemma 2B or 7B) and a subset of your data:

Once the pipeline works and you've validated results, scale to larger models or full datasets. If quality isn't sufficient, move to more powerful methods:


### 2. Use Proper Prompt Formatting

Match your training prompts to the model's expected format:

```
# For Llama-2 Chat
<s>[INST] {instruction} [/INST] {response}</s>

# For Alpaca format
### Instruction:
{instruction}

### Response:
{response}
```

Check the model card on Hugging Face for the correct format.

### 3. Save Checkpoints Regularly

The example scripts save intermediate checkpoints, allowing you to resume training if interrupted and select the best checkpoint based on validation performance.

### 4. Version Your Experiments

Keep track of model name, fine-tuning method, dataset, and key hyperparameters. This makes it easy to reproduce successful experiments.

## Resources

### Official Documentation

- [Full Fine-tuning Guide](https://ai.google.dev/gemma/docs/core/huggingface_text_full_finetune)
- [QLoRA Guide](https://ai.google.dev/gemma/docs/core/huggingface_text_finetune_qlora)
- [PEFT Library](https://huggingface.co/docs/peft)
- [BitsAndBytes Integration](https://huggingface.co/blog/hf-bitsandbytes-integration)
- [TRL (Transformer Reinforcement Learning)](https://huggingface.co/docs/trl)

### Community Resources

- [Hugging Face Model Hub](https://huggingface.co/models): Pre-trained models to fine-tune
- [Hugging Face Datasets](https://huggingface.co/datasets): Training datasets
- [LoRA Research Paper](https://arxiv.org/abs/2106.09685): Original LoRA publication
- [QLoRA Research Paper](https://arxiv.org/abs/2305.14314): QLoRA methodology

---

## Quick Reference: Choosing Your Script

| Your Situation | Recommended Script | Command |
|----------------|-------------------|---------|
| 🆕 Just getting started | Gemma QLoRA | `python assets/gemma/train_qlora.py` |
| 💰 Limited VRAM (16GB) | Any QLoRA script | `python assets/{model}/train_qlora.py` |
| ⚡ Good VRAM (24GB) | 8-bit + LoRA or LoRA | `python assets/{model}/train_lora.py` |
| 🎯 Maximum quality | Full fine-tuning | `python assets/{model}/train_full_finetuning.py` |
| 🔬 Production adapter | LoRA or 8-bit LoRA | `python assets/{model}/train_lora.py` |
| 🧪 Quick experiments | QLoRA | `python assets/{model}/train_qlora.py` |

Replace `{model}` with `gemma` or `gptoss` based on which model family you're using.

---

Fine-tuning LLMs is both art and science. Experiment with different methods, track your results, and iterate based on what works for your specific use case. Your STX Halo™ provides the compute power—now go build something amazing!
