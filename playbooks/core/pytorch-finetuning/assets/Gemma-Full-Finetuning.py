# <Insert License>
#!/usr/bin/env python


"""
Fine-tuning Gemma-3 models on AMD Strix Halo (GFX1151)
Supports: Full fine-tuning 
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, prepare_model_for_kbit_training, get_peft_model, PeftModel
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
# Model selection
# -----------------------
# Options: "google/gemma-3-270m-it", "google/gemma-3-1b-it", "google/gemma-3-4b-it",
#          "google/gemma-3-12b-it", "google/gemma-3-27b-it"
MODEL = "google/gemma-3-1b-it"
model_name = MODEL.split("/")[-1]

# -----------------------
# Training parameters
# -----------------------
LR = 5e-5
EPOCHS = 2
BATCH_SIZE = 4

# -----------------------
# Load dataset
# -----------------------
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
print(f"Train: {len(ds['train'])}, Test: {len(ds['test'])}")

# -----------------------
# Load model and tokenizer
# -----------------------
model = AutoModelForCausalLM.from_pretrained(
    MODEL,
    dtype="auto",
    device_map="auto",
    attn_implementation="eager"  # Recommended for Gemma training
)
tokenizer = AutoTokenizer.from_pretrained(MODEL)
torch_dtype = model.dtype
print(f"Weights footprint: {model.get_memory_footprint()/1e9:.2f} GB")

# -----------------------
# SFT training configuration
# -----------------------
args = SFTConfig(
    output_dir=f"output-{model_name}-full",
    max_length=512,
    packing=False,
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    gradient_checkpointing=False,
    optim="adamw_torch_fused",
    logging_steps=10,
    save_strategy="epoch",
    eval_strategy="epoch",
    learning_rate=LR,
    fp16=True if torch_dtype == torch.float16 else False,
    bf16=True if torch_dtype == torch.bfloat16 else False,
    lr_scheduler_type="constant",
    report_to="none",
    dataset_kwargs={"add_special_tokens": False, "append_concat_token": True},
    save_safetensors=True,
    save_total_limit=1
)

trainer = SFTTrainer(
    model=model,
    args=args,
    train_dataset=ds['train'],
    eval_dataset=ds['test'],
    processing_class=tokenizer
)

# -----------------------
# Run training
# -----------------------
reset_peak_mem()
trainer.train()
report_peak_mem("full")
trainer.save_model()

print("Training complete!")
