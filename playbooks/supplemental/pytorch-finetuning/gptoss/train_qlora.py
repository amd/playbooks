#!/usr/bin/env python
"""
QLoRA Fine-tuning GPT-OSS 20B on AMD Strix Halo (GFX1151)

QLoRA uses 4-bit quantization with LoRA adapters for maximum memory efficiency.
This enables fine-tuning 20B+ models on consumer GPUs.

Best for: Limited VRAM, rapid experimentation, maximum accessibility
Memory Requirements: ~12-16GB VRAM
Training Speed: Fastest
Quality: Slight degradation vs LoRA, but still excellent
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
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
# QLoRA Configuration
# -----------------------
# 4-bit quantization settings
LOAD_IN_4BIT = True
BNB_4BIT_QUANT_TYPE = "nf4"           # Normal Float 4-bit (optimal for weights)
BNB_4BIT_COMPUTE_DTYPE = torch.bfloat16
BNB_4BIT_USE_DOUBLE_QUANT = True      # Double quantization for extra compression

# LoRA settings (slightly higher rank to compensate for quantization)
LORA_R = 64                            # Higher rank for QLoRA
LORA_ALPHA = 128                       # 2x rank
LORA_DROPOUT = 0.05
LORA_TARGET_MODULES = [
    "q_proj", "k_proj", "v_proj", "o_proj",
    "gate_proj", "up_proj", "down_proj"
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
# Configure 4-bit Quantization
# -----------------------
print("\n" + "="*60)
print("Quantization Configuration")
print("="*60)
print(f"Quantization: 4-bit NF4")
print(f"Compute dtype: BFloat16")
print(f"Double quantization: Enabled")
print("="*60 + "\n")

bnb_config = BitsAndBytesConfig(
    load_in_4bit=LOAD_IN_4BIT,
    bnb_4bit_quant_type=BNB_4BIT_QUANT_TYPE,
    bnb_4bit_compute_dtype=BNB_4BIT_COMPUTE_DTYPE,
    bnb_4bit_use_double_quant=BNB_4BIT_USE_DOUBLE_QUANT
)

# -----------------------
# Load Model in 4-bit
# -----------------------
print(f"Loading {MODEL} in 4-bit...")
print("This dramatically reduces memory usage (~75% reduction)\n")

model = AutoModelForCausalLM.from_pretrained(
    MODEL,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
    torch_dtype=torch.bfloat16
)

tokenizer = AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print(f"Quantized model loaded. Memory footprint: {model.get_memory_footprint()/1e9:.2f} GB")
print("(Compare to ~40GB for full precision!)\n")

# -----------------------
# Prepare Model for Training
# -----------------------
model = prepare_model_for_kbit_training(model)

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

print("="*60)
print("QLoRA Configuration Applied")
print("="*60)
print(f"Trainable params: {trainable_params:,} ({100 * trainable_params / total_params:.2f}%)")
print(f"All params: {total_params:,}")
print(f"LoRA rank: {LORA_R}")
print(f"LoRA alpha: {LORA_ALPHA}")
print(f"Target modules: {len(LORA_TARGET_MODULES)} layer types")
print("="*60 + "\n")

# -----------------------
# Training Configuration
# -----------------------
args = SFTConfig(
    output_dir=f"output-{model_name}-qlora",
    
    # Dataset settings
    max_seq_length=512,
    packing=False,
    
    # Training hyperparameters
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=GRAD_ACCUM_STEPS,
    learning_rate=LR,
    
    # Optimizer (paged optimizer for QLoRA)
    optim="paged_adamw_32bit",        # Memory-efficient paged optimizer
    
    # Mixed precision
    bf16=True,
    fp16=False,
    
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
print(f"Effective batch size: {BATCH_SIZE * GRAD_ACCUM_STEPS}")
print(f"Learning rate: {LR}")
print(f"Expected time: 2-4 hours for 1000 samples\n")

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
print(f"QLoRA adapter saved to: output-{model_name}-qlora")
print(f"Adapter size: ~{trainable_params * 2 / 1e6:.1f} MB")
print("\n📊 QLoRA Benefits:")
print("  ✓ 75% less memory than full precision")
print("  ✓ Faster training than full fine-tuning")
print("  ✓ Comparable quality to full LoRA")
print("  ✓ Can train 70B+ models on consumer GPUs")

print("\nTo use your QLoRA adapter:")
print("  from peft import AutoPeftModelForCausalLM")
print(f"  model = AutoPeftModelForCausalLM.from_pretrained(")
print(f"      'output-{model_name}-qlora',")
print("      device_map='auto',")
print("      torch_dtype=torch.bfloat16")
print("  )")

print("\nTo merge adapter with base model:")
print("  # Load with quantization for merging")
print("  merged_model = model.merge_and_unload()")
print("  merged_model.save_pretrained('output-merged')")
