#!/usr/bin/env python
# coding: utf-8

"""
CI-friendly Unsloth training script (Gemma-3N)
- Short smoke-test style run
- Verifies model load, dataset prep, LoRA training, inference, local save,
  merged save, and GGUF export
"""

import os
import time
import unsloth
import torch
from datasets import load_dataset
from transformers import TextStreamer
from unsloth import FastModel
from unsloth.chat_templates import (
    get_chat_template,
    standardize_data_formats,
    train_on_responses_only,
)
from trl import SFTTrainer, SFTConfig


# =========================
# Config
# =========================
MODEL_NAME = "unsloth/gemma-3n-E4B-it"
MAX_SEQ_LEN = 512
DATASET_NAME = "mlabonne/FineTome-100k"
DATASET_SPLIT = "train[:128]"   # smaller split for CI
OUTPUT_DIR = "gemma_3n_lora_ci"
MERGED_DIR = "gemma_3n_merged_ci"

MAX_STEPS = 5
PER_DEVICE_BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 2
LEARNING_RATE = 2e-4

PROMPT = "Explain why the sky is blue."


# =========================
# Utils
# =========================
def log(msg: str):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def require_cuda():
    log("Checking GPU availability...")
    if not torch.cuda.is_available():
        raise RuntimeError(
            "ROCm-enabled PyTorch GPU is not available. "
            "This CI script expects a working GPU environment."
        )
    log(f"GPU available: {torch.cuda.get_device_name(0)}")


# =========================
# Load model
# =========================
def load_model():
    log("Loading model...")
    model, tokenizer = FastModel.from_pretrained(
        model_name=MODEL_NAME,
        max_seq_length=MAX_SEQ_LEN,
        load_in_4bit=False,
    )
    tokenizer = get_chat_template(tokenizer, chat_template="gemma-3")
    return model, tokenizer


# =========================
# Prepare dataset
# =========================
def prepare_dataset(tokenizer):
    log("Loading dataset...")
    dataset = load_dataset(DATASET_NAME, split=DATASET_SPLIT)

    log("Standardizing dataset format...")
    dataset = standardize_data_formats(dataset)

    def format_fn(examples):
        texts = [
            tokenizer.apply_chat_template(
                convo,
                tokenize=False,
                add_generation_prompt=False,
            ).removeprefix("<bos>")
            for convo in examples["conversations"]
        ]
        return {"text": texts}

    log("Applying chat template...")
    dataset = dataset.map(format_fn, batched=True)

    if len(dataset) == 0:
        raise RuntimeError("Prepared dataset is empty")

    log(f"Prepared dataset size: {len(dataset)}")
    return dataset


# =========================
# Apply LoRA
# =========================
def apply_lora(model):
    log("Applying LoRA adapters...")
    model = FastModel.get_peft_model(
        model,
        finetune_language_layers=True,
        finetune_attention_modules=True,
        finetune_mlp_modules=True,
        r=8,
        lora_alpha=8,
        lora_dropout=0,
        bias="none",
    )
    return model


# =========================
# Train
# =========================
def train(model, tokenizer, dataset):
    log("Setting up trainer...")

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        args=SFTConfig(
            dataset_text_field="text",
            per_device_train_batch_size=PER_DEVICE_BATCH_SIZE,
            gradient_accumulation_steps=GRAD_ACCUM_STEPS,
            max_steps=MAX_STEPS,
            learning_rate=LEARNING_RATE,
            logging_steps=1,
            report_to="none",
            optim="adamw_torch",
        ),
    )

    trainer = train_on_responses_only(
        trainer,
        instruction_part="<start_of_turn>user\n",
        response_part="<start_of_turn>model\n",
    )

    log("Starting training...")
    start = time.time()
    stats = trainer.train()
    elapsed = round(time.time() - start, 2)

    log(f"Training finished in {elapsed} sec")
    log(f"Training stats: {stats}")

    return stats


# =========================
# Inference test
# =========================
def run_inference(model, tokenizer):
    log("Running inference smoke test...")

    messages = [{
        "role": "user",
        "content": [{"type": "text", "text": PROMPT}]
    }]

    inputs = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_dict=True,
        return_tensors="pt",
    ).to("cuda")

    _ = model.generate(
        **inputs,
        max_new_tokens=64,
        temperature=1.0,
        top_p=0.95,
        top_k=64,
        streamer=TextStreamer(tokenizer, skip_prompt=True),
    )

    log("Inference smoke test completed")


# =========================
# Save outputs
# =========================
def save_lora(model, tokenizer):
    log(f"Saving LoRA adapters to: {OUTPUT_DIR}")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)


def save_merged(model, tokenizer):
    log(f"Saving merged model to: {MERGED_DIR}")
    model.save_pretrained_merged(MERGED_DIR, tokenizer)


# =========================
# Main
# =========================
def main():
    log("===== Unsloth CI Training Pipeline =====")
    log(f"Python: {os.sys.version}")
    log(f"PyTorch: {torch.__version__}")

    require_cuda()

    model, tokenizer = load_model()
    dataset = prepare_dataset(tokenizer)
    model = apply_lora(model)

    train(model, tokenizer, dataset)
    run_inference(model, tokenizer)

    save_lora(model, tokenizer)
    save_merged(model, tokenizer)

    log("===== Done =====")


if __name__ == "__main__":
    main()