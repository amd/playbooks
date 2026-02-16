#!/usr/bin/env python
"""
Full Fine-tuning Gemma 3 4B on AMD Strix Halo (GFX1151)

This script demonstrates full parameter fine-tuning which updates all model weights.
Best for: Maximum quality when you have sufficient GPU memory
"""

import gc
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from trl import SFTConfig, SFTTrainer
from datasets import load_dataset

# -----------------------
# Utility functions
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
        print("✓ GPU memory cleaned up")
    except Exception as e:
        print(f"⚠ Warning during cleanup: {e}")


# -----------------------
# Model Configuration
# -----------------------
MODEL = "google/gemma-3-4b-it" 
model_name = MODEL.split("/")[-1]

# -----------------------
# Training Parameters
# -----------------------
LR = 2e-5              # Lower learning rate for full fine-tuning
EPOCHS = 3             # Can do more epochs with smaller model
BATCH_SIZE = 4         # Larger batch size possible with 2B model
GRAD_ACCUM_STEPS = 4   # Accumulate gradients for effective batch size of 16

# -----------------------
# Load and Prepare Dataset
# -----------------------
print("Loading dataset...")

# Databricks Dolly 15k: diverse instructions (QA, summarization, extraction, etc.)
ds = load_dataset("databricks/databricks-dolly-15k", split="train").shuffle(seed=42).select(range(1000))

def format_chat(ex):
    """Format instruction/context/response into chat messages"""
    user_content = ex["instruction"]
    if ex.get("context") and str(ex["context"]).strip():
        user_content = f"{user_content}\n\nContext: {ex['context']}"
    return {
        "messages": [
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": ex["response"]}
        ]
    }

ds = ds.map(format_chat, remove_columns=ds.column_names)
ds = ds.train_test_split(test_size=0.2)
print(f"Train samples: {len(ds['train'])}, Test samples: {len(ds['test'])}")

# -----------------------
# Load Model and Tokenizer
# -----------------------
print(f"\nLoading {MODEL}...")
print("Note: Model is stored as MXFP4 on Hugging Face but will be loaded as BF16 for training")
print("(This is expected - the warning about MXFP4 is informational)\n")

model = AutoModelForCausalLM.from_pretrained(
    MODEL,
    dtype=torch.bfloat16,             # Use BF16 for better stability and ROCm support (dtype not torch_dtype)
    device_map="auto",                # Automatically distribute across available GPUs
    trust_remote_code=True,
    low_cpu_mem_usage=True            # Reduce CPU memory during loading
)

tokenizer = AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True)
tokenizer.model_max_length = 512  # Set max sequence length

print(f"Model loaded. Weights footprint: {model.get_memory_footprint()/1e9:.2f} GB")

# Enable gradient checkpointing to reduce memory usage
model.gradient_checkpointing_enable()
print("Gradient checkpointing enabled (saves memory during backprop)")

# -----------------------
# Training Configuration
# -----------------------
args = SFTConfig(
    output_dir=f"output-{model_name}-full",
    
    # Dataset settings
    packing=False,
    
    # Training hyperparameters
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=GRAD_ACCUM_STEPS,
    learning_rate=LR,
    
    # Memory optimizations
    gradient_checkpointing=True,
    optim="adamw_torch_fused",        # Fused optimizer for better performance
    
    # Mixed precision
    bf16=True,                         # BF16 recommended for ROCm
    fp16=False,
    
    # Learning rate schedule
    lr_scheduler_type="cosine",
    warmup_ratio=0.03,                 # 3% warmup
    
    # Logging and saving
    logging_steps=5,
    save_strategy="epoch",
    eval_strategy="epoch",
    save_safetensors=True,
    save_total_limit=1,                # Keep only last checkpoint to save disk space
    
    # Other
    report_to="none",                  # Change to "wandb" for Weights & Biases tracking
    dataset_kwargs={
        "add_special_tokens": False,
        "append_concat_token": True
    }
)

# -----------------------
# Initialize Trainer
# -----------------------
# Set tokenizer padding
tokenizer.padding_side = "right"
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

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

print("Starting Full Fine-tuning")
print(f"Model: {MODEL}")
print(f"Model size: ~4B parameters")
print(f"Trainable parameters: {model.num_parameters():,}")
print(f"Effective batch size: {BATCH_SIZE * GRAD_ACCUM_STEPS}")
print(f"Learning rate: {LR}")
print(f"Epochs: {EPOCHS}")

reset_peak_mem()
trainer.train()
report_peak_mem("(full fine-tuning)")

# -----------------------
# Save Model
# -----------------------
print("\nSaving fine-tuned model...")
trainer.save_model()
tokenizer.save_pretrained(f"output-{model_name}-full")


print("Training Complete!")
print(f"Model saved to: output-{model_name}-full")
print("\nTo use your fine-tuned model:")
print(f"  model = AutoModelForCausalLM.from_pretrained('output-{model_name}-full')")
print(f"  tokenizer = AutoTokenizer.from_pretrained('output-{model_name}-full')")

# -----------------------
# Cleanup GPU Memory
# -----------------------
cleanup_gpu_memory()
