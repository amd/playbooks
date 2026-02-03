#!/usr/bin/env python
"""
LoRA Fine-tuning GPT-OSS 20B on AMD Strix Halo (GFX1151)

This script uses LoRA (Low-Rank Adaptation) to efficiently fine-tune by training
small adapter matrices while freezing the base model.

Best for: Balanced quality and efficiency, training multiple adapters
Memory Requirements: ~24-32GB VRAM
Training Speed: 3-5x faster than full fine-tuning
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
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


# -----------------------
# Model Configuration
# -----------------------
MODEL = "gpt-oss/gpt-oss-20b"
model_name = MODEL.split("/")[-1]

# -----------------------
# LoRA Configuration
# -----------------------
LORA_R = 32                    # Rank of LoRA matrices (higher = more capacity)
LORA_ALPHA = 64                # Scaling factor (usually 2x rank)
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
LR = 3e-4                      # Higher learning rate for LoRA
EPOCHS = 3
BATCH_SIZE = 4                 # Can use larger batch with LoRA
GRAD_ACCUM_STEPS = 4

# -----------------------
# Load Dataset
# -----------------------
print("Loading dataset...")
ds = load_dataset("Abirate/english_quotes", split="train").shuffle(seed=42).select(range(1000))

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

# -----------------------
# Load Model and Tokenizer
# -----------------------
print(f"\nLoading {MODEL}...")

model = AutoModelForCausalLM.from_pretrained(
    MODEL,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True,
    low_cpu_mem_usage=True
)

tokenizer = AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print(f"Base model loaded. Memory footprint: {model.get_memory_footprint()/1e9:.2f} GB")

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

# Apply LoRA to model
model = get_peft_model(model, lora_config)

# Print trainable parameters
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
total_params = sum(p.numel() for p in model.parameters())
print("\n" + "="*60)
print("LoRA Configuration Applied")
print("="*60)
print(f"Trainable params: {trainable_params:,} ({100 * trainable_params / total_params:.2f}%)")
print(f"Total params: {total_params:,}")
print(f"LoRA rank: {LORA_R}")
print(f"LoRA alpha: {LORA_ALPHA}")
print(f"Target modules: {', '.join(LORA_TARGET_MODULES)}")
print("="*60 + "\n")

# -----------------------
# Training Configuration
# -----------------------
args = SFTConfig(
    output_dir=f"output-{model_name}-lora",
    
    # Dataset settings
    max_seq_length=512,
    packing=False,
    
    # Training hyperparameters
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=GRAD_ACCUM_STEPS,
    learning_rate=LR,
    
    # Optimizer
    optim="adamw_torch_fused",
    
    # Mixed precision
    bf16=True,
    fp16=False,
    
    # Learning rate schedule
    lr_scheduler_type="cosine",
    warmup_ratio=0.05,
    
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
print("Starting LoRA Fine-tuning...")
print(f"Effective batch size: {BATCH_SIZE * GRAD_ACCUM_STEPS}")
print(f"Learning rate: {LR}\n")

reset_peak_mem()
trainer.train()
report_peak_mem("(LoRA)")

# -----------------------
# Save LoRA Adapter
# -----------------------
print("\nSaving LoRA adapter...")
model.save_pretrained(f"output-{model_name}-lora")
tokenizer.save_pretrained(f"output-{model_name}-lora")

print("\n" + "="*60)
print("Training Complete!")
print("="*60)
print(f"LoRA adapter saved to: output-{model_name}-lora")
print(f"Adapter size: ~{trainable_params * 2 / 1e6:.1f} MB (much smaller than full model!)")
print("\nTo use your LoRA adapter:")
print("  from peft import AutoPeftModelForCausalLM")
print(f"  model = AutoPeftModelForCausalLM.from_pretrained('output-{model_name}-lora')")
print(f"  tokenizer = AutoTokenizer.from_pretrained('output-{model_name}-lora')")
print("\nTo merge adapter with base model:")
print("  merged_model = model.merge_and_unload()")
print("  merged_model.save_pretrained('output-merged')")
