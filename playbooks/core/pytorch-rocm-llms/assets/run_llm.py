# Copyright Advanced Micro Devices, Inc.
# 
# SPDX-License-Identifier: MIT

"""
Basic LLM Loading and Text Generation
======================================

This script demonstrates how to:
- Load a language model with ROCm acceleration
- Generate text from a prompt
- Use different generation parameters

It works with two families of models:
- openai/gpt-oss-20b (default) -- emits the Harmony token format
- Qwen/Qwen3.5-4B -- a compact model that fits comfortably on Strix/Krackan

Usage:
    python run_llm.py
    python run_llm.py --model Qwen/Qwen3.5-4B
"""
import os
import re
import argparse
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoModelForImageTextToText,
    AutoTokenizer,
)

os.environ["TOKENIZERS_PARALLELISM"] = "false"

DEFAULT_MODEL = "openai/gpt-oss-20b"


def is_harmony_model(model_name):
    """gpt-oss models speak the Harmony channel format; others don't."""
    return "gpt-oss" in model_name.lower()


def load_model(model_name):
    """Load a tokenizer + model, transparently handling causal-LM and
    multimodal (image-text-to-text) checkpoints such as Qwen3.5."""
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )
    except (ValueError, KeyError):
        # Vision-language checkpoints (e.g. Qwen3.5) are not registered under
        # AutoModelForCausalLM; load them via the image-text-to-text head. They
        # still generate text-only when given a text-only prompt.
        model = AutoModelForImageTextToText.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )
    return tokenizer, model


def extract_answer(text, harmony):
    """Pull the user-facing answer out of the raw model output."""
    if harmony:
        # Harmony output exposes multiple channels; we only want `final`.
        final = re.search(r"<\|channel\|>final<\|message\|>(.*?)<\|return\|>", text, re.S)
        return final.group(1).strip() if final else text.strip()
    # Thinking models (e.g. Qwen3.5) wrap chain-of-thought in <think>...</think>.
    return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()


def main():
    parser = argparse.ArgumentParser(description="Generate text with a local LLM")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Hugging Face model id (default: {DEFAULT_MODEL})",
    )
    args = parser.parse_args()

    # Verify ROCm is available
    print("="*10 + " ROCm Configuration" + "="*10)
    print(f"ROCm available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB\n")

    model_name = args.model
    harmony = is_harmony_model(model_name)

    tokenizer, model = load_model(model_name)

    print("✓ Model loaded successfully!\n")

    # Create a simple prompt
    prompt = "Explain what a large language model is in 2 brief sentences."
    print(f"Prompt: {prompt}\n")

    messages = [
        {"role": "system", "content": "You are a helpful technology assistant"},
        {"role": "user", "content": f"{prompt}"},
    ]

    template_kwargs = dict(
        add_generation_prompt=True,
        return_tensors="pt",
        return_dict=True,
    )
    if not harmony:
        # Ask Qwen3.5 for a direct answer instead of a long reasoning trace.
        template_kwargs["enable_thinking"] = False

    try:
        inputs = tokenizer.apply_chat_template(messages, **template_kwargs)
    except TypeError:
        template_kwargs.pop("enable_thinking", None)
        inputs = tokenizer.apply_chat_template(messages, **template_kwargs)

    inputs = inputs.to(model.device)

    generated = model.generate(**inputs, max_new_tokens=350)
    new_tokens = generated[0][inputs["input_ids"].shape[-1]:]

    print("\nGenerating...\n")

    # Keep special tokens for Harmony parsing; drop them otherwise.
    raw = tokenizer.decode(new_tokens, skip_special_tokens=not harmony)
    print(f"Answer: {extract_answer(raw, harmony)}")


if __name__ == "__main__":
    main()
