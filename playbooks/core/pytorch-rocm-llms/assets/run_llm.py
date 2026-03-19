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

Usage:
    python run_llm.py
"""
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

os.environ["TOKENIZERS_PARALLELISM"] = "false"


# Helper function to parse the final output
def extract_final(text):
    import re
    final = re.search(r"<\|channel\|>final<\|message\|>(.*?)<\|return\|>", text, re.S)
    return final.group(1).strip() if final else None


def main():
    # Verify ROCm is available
    print("="*10 + " ROCm Configuration" + "="*10)
    print(f"ROCm available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB\n")


    model_name = "openai/gpt-oss-20b"

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )

    print("✓ Model loaded successfully!\n")

    # Create a simple prompt
    prompt = "Explain what a large language model is in 2 brief sentences."
    print(f"Prompt: {prompt}\n")

    messages = [
        {"role": "system", "content": "You are a helpful technology assistant"},
        {"role": "user", "content": f"{prompt}"},
    ]

    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt",
        return_dict=True,
    ).to(model.device)

    generated = model.generate(**inputs, max_new_tokens=350)
    total_output = tokenizer.decode(generated[0][inputs["input_ids"].shape[-1] :])

    print("\nGenerating...\n")

    # the output of the model is in a form called 'Harmony Token Format'. The helper function called parses the final response.
    print(f"Answer: {extract_final(total_output)}")


if __name__ == "__main__":
    main()