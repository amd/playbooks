#!/usr/bin/env python
# coding: utf-8

"""
Minimal Unsloth training script (Gemma-3N)
- Clean (<200 lines)
- With progress logs
- Suitable for CI / quickstart
"""

import time
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
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
DATASET_SPLIT = "train[:2000]"   # keep small for demo
OUTPUT_DIR = "gemma_3n_lora"


# =========================
# Utils
# =========================
def log(msg: str):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


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

    log("Standardizing format...")
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
            per_device_train_batch_size=1,
            gradient_accumulation_steps=4,
            max_steps=50,  # quick demo
            learning_rate=2e-4,
            logging_steps=5,
            report_to="none",
        ),
    )

    trainer = train_on_responses_only(
        trainer,
        instruction_part="<start_of_turn>user\n",
        response_part="<start_of_turn>model\n",
    )

    log("Start training...")
    start = time.time()

    stats = trainer.train()

    log(f"Training finished in {round(time.time() - start, 2)} sec")
    return stats


# =========================
# Inference test
# =========================
def run_inference(model, tokenizer):
    log("Running inference test...")

    messages = [{
        "role": "user",
        "content": [{"type": "text", "text": "Explain why the sky is blue."}]
    }]

    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
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


# =========================
# Save
# =========================
def save_model(model, tokenizer):
    log("Saving LoRA adapters...")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)


# =========================
# Main
# =========================
def main():
    log("===== Unsloth Training Pipeline =====")

    model, tokenizer = load_model()
    dataset = prepare_dataset(tokenizer)
    model = apply_lora(model)

    train(model, tokenizer, dataset)
    run_inference(model, tokenizer)
    save_model(model, tokenizer)

    log("===== Done =====")


if __name__ == "__main__":
    main()