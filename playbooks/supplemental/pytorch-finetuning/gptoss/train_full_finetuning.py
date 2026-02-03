#!/usr/bin/env python
"""
Full Fine-tuning GPT-OSS 20B on AMD Strix Halo (GFX1151)

This script demonstrates full parameter fine-tuning which updates all model weights.
Best for: Maximum quality when you have sufficient GPU memory (40GB+ VRAM)

Memory Requirements: ~80GB+ VRAM (requires gradient checkpointing and optimizations)
"""

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


# -----------------------
# Model Configuration
# -----------------------
# GPT-OSS 20B - Open source GPT model
MODEL = "gpt-oss/gpt-oss-20b"  # 20 billion parameters
model_name = MODEL.split("/")[-1]

# -----------------------
# Training Parameters
# -----------------------
LR = 2e-5              # Lower learning rate for full fine-tuning
EPOCHS = 1             # Start with 1 epoch for large models
BATCH_SIZE = 1         # Small batch size due to memory constraints
GRAD_ACCUM_STEPS = 16  # Accumulate gradients for effective batch size of 16

# -----------------------
# Load and Prepare Dataset
# -----------------------
print("Loading dataset...")
ds = load_dataset("Abirate/english_quotes", split="train").shuffle(seed=42).select(range(1000))

def format_chat(ex):
    """Format dataset into chat/instruction format"""
    return {
        "messages": [
            {"role": "user", "content": f"Give me a quote about: {ex['tags']}"},
            {"role": "assistant", "content": f"{ex['quote']} - {ex['author']}"}
        ]
    }

ds = ds.map(format_chat, remove_columns=ds.column_names)
ds = ds.train_test_split(test_size=0.2)
print(f"Train samples: {len(ds['train'])}, Test samples: {len(ds['test'])}")

# -----------------------
# Load Model and Tokenizer
# -----------------------
print(f"\nLoading {MODEL}...")
print("This may take several minutes for a 20B model...")

model = AutoModelForCausalLM.from_pretrained(
    MODEL,
    torch_dtype=torch.bfloat16,      # Use BF16 for better stability and ROCm support
    device_map="auto",                # Automatically distribute across available GPUs
    trust_remote_code=True,
    low_cpu_mem_usage=True            # Reduce CPU memory during loading
)

tokenizer = AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

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
    max_seq_length=512,
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
print("\n" + "="*60)
print("Starting Full Fine-tuning")
print("="*60)
print(f"Model: {MODEL}")
print(f"Trainable parameters: {model.num_parameters():,}")
print(f"Effective batch size: {BATCH_SIZE * GRAD_ACCUM_STEPS}")
print(f"Learning rate: {LR}")
print(f"Epochs: {EPOCHS}")
print("="*60 + "\n")

reset_peak_mem()
trainer.train()
report_peak_mem("(full fine-tuning)")

# -----------------------
# Save Model
# -----------------------
print("\nSaving fine-tuned model...")
trainer.save_model()
tokenizer.save_pretrained(f"output-{model_name}-full")

print("\n" + "="*60)
print("Training Complete!")
print("="*60)
print(f"Model saved to: output-{model_name}-full")
print("\nTo use your fine-tuned model:")
print(f"  model = AutoModelForCausalLM.from_pretrained('output-{model_name}-full')")
print(f"  tokenizer = AutoTokenizer.from_pretrained('output-{model_name}-full')")
