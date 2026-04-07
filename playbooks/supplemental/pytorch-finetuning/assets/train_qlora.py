#!/usr/bin/env python
# Copyright Advanced Micro Devices, Inc.
# 
# SPDX-License-Identifier: MIT

"""
LoRA Fine-tuning GPT-OSS 20B (Pre-quantized) on AMD Strix Halo (GFX1151)

This script fine-tunes the pre-quantized GPT-OSS 20B model using LoRA adapters.
The model comes pre-quantized with Mxfp4, so we don't need additional quantization.

Best for: Limited VRAM, rapid experimentation, maximum accessibility
Memory Requirements: ~12-16GB VRAM
Training Speed: Fast
Quality: Excellent with pre-quantized model
"""

import gc
import os
import torch

# Use bitsandbytes (bnb) for quantization on Linux, but skip it on Windows (or if bnb is incomplete).
# This patch avoids errors during LoRA adapter injection on platforms where bnb is unavailable or unsupported.
# If you enable true QLoRA (with load_in_4bit), remove this block and ensure bitsandbytes is installed and working.
try:
    import bitsandbytes as _bnb
    if not hasattr(_bnb, "nn"):
        import types
        _bnb.nn = types.ModuleType("nn")
except ImportError:
    pass

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model
from trl import SFTConfig, SFTTrainer
from datasets import load_dataset

# -----------------------
# Utility Functions
# -----------------------
def reset_peak_mem():
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()

def report_peak_mem(tag: str = ""):
    if torch.cuda.is_available():
        print(f"Peak training memory{(' ' + tag) if tag else ''}: "
              f"{torch.cuda.max_memory_allocated()/1e9:.2f} GB")

def cleanup_gpu_memory():
    """Release GPU memory and cleanup resources"""
    try:
        print("\nCleaning up GPU memory...")
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            torch.cuda.empty_cache()
        print("GPU memory cleanup complete.")
    except Exception as e:
        print(f"[Warning] during cleanup: {e}")


# -----------------------
# Model Configuration
# -----------------------
MODEL = "openai/gpt-oss-20b" # pre-quantized 4-bit (Mxfp4) model
model_name = MODEL.split("/")[-1]

# -----------------------
# LoRA Configuration (for Pre-quantized Model)
# -----------------------
# The model is already quantized with Mxfp4
# We only need to configure LoRA adapters

# LoRA settings
LORA_R = 64                    # Rank of LoRA matrices (higher = more capacity)
LORA_ALPHA = 128                # Scaling factor (usually 2x rank)
LORA_DROPOUT = 0.05            # Dropout for regularization
LORA_TARGET_MODULES = [        # Which layers to add LoRA adapters to
    "q_proj",                  # Query projection
    "k_proj",                  # Key projection  
    "v_proj",                  # Value projection
    "o_proj",                  # Output projection
    "gate_proj",               # Gate projection (MLP)
    "up_proj",                 # Up projection (MLP)
    "down_proj"                # Down projection (MLP)
]

# -----------------------
# Training Parameters
# -----------------------
LR = 2e-4                              # Standard QLoRA learning rate
EPOCHS = 3
BATCH_SIZE = 4
GRAD_ACCUM_STEPS = 4

# -----------------------
# Load Dataset
# -----------------------
print("Loading dataset...")
QUICK_TRAIN = os.environ.get("QUICK_TRAIN") == "1"
if QUICK_TRAIN and os.environ.get("QUICK_TRAIN_MODEL"):
    MODEL = os.environ["QUICK_TRAIN_MODEL"]
    model_name = MODEL.split("/")[-1]
    print(f"QUICK_TRAIN=1: using non-gated model for smoke test: {MODEL}")
n_samples = 8 if QUICK_TRAIN else 1000
if QUICK_TRAIN:
    print("QUICK_TRAIN=1: using 1 step and a tiny dataset (smoke test).")
ds = load_dataset("Abirate/english_quotes", split="train").shuffle(seed=42).select(range(n_samples))

def format_chat(ex):
    return {
        "messages": [
            {"role": "user", "content": f"Give me a quote about: {ex['tags']}"},
            {"role": "assistant", "content": f"{ex['quote']} - {ex['author']}"}
        ]
    }

ds = ds.map(format_chat, remove_columns=ds.column_names)
ds = ds.train_test_split(test_size=0.2)
print(f"Train samples: {len(ds['train'])}, Test samples: {len(ds['test'])}")
print(f"Total selected samples: {n_samples}")

# -----------------------
# Load Model (Pre-quantized)
# -----------------------
print("\nLoading Pre-quantized Model")
print(f"Model: {MODEL}")

# The model is already pre-quantized with Mxfp4Config
# We don't need to apply additional quantization
model = AutoModelForCausalLM.from_pretrained(
    MODEL,
    device_map="auto",
    trust_remote_code=True,
    dtype=torch.bfloat16  # Use dtype instead of torch_dtype
)

tokenizer = AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True)
tokenizer.model_max_length = 512  # Set max sequence length
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print(f"Pre-quantized model loaded. Memory footprint: {model.get_memory_footprint()/1e9:.2f} GB")

# -----------------------
# Prepare Model for Training
# -----------------------
# Enable gradient checkpointing for memory efficiency
if hasattr(model, 'enable_input_require_grads'):
    model.enable_input_require_grads()
else:
    def make_inputs_require_grad(module, input, output):
        output.requires_grad_(True)
    model.get_input_embeddings().register_forward_hook(make_inputs_require_grad)

# -----------------------
# Configure LoRA
# -----------------------
lora_config = LoraConfig(
    r=LORA_R,
    lora_alpha=LORA_ALPHA,
    target_modules=LORA_TARGET_MODULES,
    lora_dropout=LORA_DROPOUT,
    bias="none",
    task_type="CAUSAL_LM",
    inference_mode=False
)

# Apply LoRA adapters
model = get_peft_model(model, lora_config)

# Print parameter info
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
total_params = sum(p.numel() for p in model.parameters())

print("\nQLoRA Configuration Applied")
print(f"Trainable params: {trainable_params:,} ({100 * trainable_params / total_params:.2f}%)")
print(f"All params: {total_params:,}")
print(f"LoRA rank: {LORA_R}")
print(f"LoRA alpha: {LORA_ALPHA}")
print(f"Target modules: {len(LORA_TARGET_MODULES)} layer types\n")

# -----------------------
# Mixed precision: use bf16 if supported, else fp16, else fp32
# -----------------------
_use_bf16 = False
_use_fp16 = False
if torch.cuda.is_available():
    if (
        getattr(torch.cuda, "is_bf16_supported", None)
        and torch.cuda.is_bf16_supported()
    ):
        _use_bf16 = True
        print("Using bf16 mixed precision.")
    else:
        _use_fp16 = True
        print("bf16 not supported; using fp16 mixed precision.")
else:
    print("No GPU / bf16 not available; using fp32.")

# -----------------------
# Training Configuration
# -----------------------
args = SFTConfig(
    output_dir=f"output-{model_name}-qlora",
    
    # Dataset settings
    packing=False,
    
    # Training hyperparameters
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=GRAD_ACCUM_STEPS,
    learning_rate=LR,
    **(dict(max_steps=1) if QUICK_TRAIN else {}),
    
    # Optimizer
    optim="adamw_torch_fused",        # Fused optimizer for better performance
    
    # Mixed precision (set from runtime bf16/fp16 support check above)
    bf16=_use_bf16,
    fp16=_use_fp16,
    
    # Learning rate schedule
    lr_scheduler_type="cosine",
    warmup_ratio=0.03,
    max_grad_norm=0.3,                # Gradient clipping for stability
    
    # Logging and saving
    logging_steps=5,
    save_strategy="epoch",
    eval_strategy="epoch",
    save_safetensors=True,
    save_total_limit=2,
    
    # Other
    report_to="none",
    dataset_kwargs={
        "add_special_tokens": False,
        "append_concat_token": True
    }
)

# -----------------------
# Initialize Trainer
# -----------------------
trainer = SFTTrainer(
    model=model,
    args=args,
    train_dataset=ds['train'],
    eval_dataset=ds['test'],
    processing_class=tokenizer
)

# -----------------------
# Run Training
# -----------------------
print("Starting QLoRA Fine-tuning...")
print(f"Model: {MODEL}")
print(f"Trainable parameters: {trainable_params:,}")
print(f"Effective batch size: {BATCH_SIZE * GRAD_ACCUM_STEPS}")
print(f"Learning rate: {LR}")
if QUICK_TRAIN:
    print("Quick smoke mode enabled: tiny dataset + max_steps=1")
else:
    print(f"Epochs: {EPOCHS}")
    print(f"Expected time: 2-4 hours for 1000 samples\n")
print()

reset_peak_mem()
trainer.train()
report_peak_mem("(QLoRA)")

# -----------------------
# Save QLoRA Adapter
# -----------------------
print("\nSaving QLoRA adapter...")
model.save_pretrained(f"output-{model_name}-qlora")
tokenizer.save_pretrained(f"output-{model_name}-qlora")

print("\n" + "="*60)
print("Training Complete!")
print("="*60)
print(f"LoRA adapter saved to: output-{model_name}-qlora")
print(f"Adapter size: ~{trainable_params * 2 / 1e6:.1f} MB")

print("\nTo use your QLoRA adapter:")
print("  from peft import AutoPeftModelForCausalLM")
print(f"  model = AutoPeftModelForCausalLM.from_pretrained('output-{model_name}-qlora')")
print(f"  tokenizer = AutoTokenizer.from_pretrained('output-{model_name}-qlora')")
print("\nTo merge adapter with base model:")
print("  merged_model = model.merge_and_unload()")
print("  merged_model.save_pretrained('output-merged')")

# -----------------------
# Cleanup GPU Memory
# -----------------------
cleanup_gpu_memory()