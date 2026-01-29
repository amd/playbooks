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
from transformers import AutoTokenizer, AutoModelForCausalLM

import logging
import warnings

logging.getLogger("transformers").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", category=UserWarning)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def main():
    # Verify ROCm is available
    print("="*10 + " ROCm Configuration" + "="*10)
    print(f"ROCm available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    print()

    # Load model and tokenizer
    model_name = "openai/gpt-oss-20b"
    # To use Mistral-7B instead of GPT-OSS-20B, uncomment the following line
    # model_name = "mistralai/Mistral-7B-Instruct-v0.3"

    print(f"Loading {model_name}...")
    print("First run will download ~14GB, this may take a few minutes")
    print("For AMD Halo Developer Platforms, the model will be pre-installed.")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )

    print("✓ Model loaded successfully!\n")

    # Create a simple prompt
    prompt = "Explain what a large language model is in simple terms:"
    
    print(f"Prompt: {prompt}\n")

    # Tokenize input
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

    # Generate response
    print("Generating... (this may take 10-30 seconds)")
    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        temperature=0.7,
        do_sample=True,
        top_p=0.9
    )

    # Decode and print
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    print()
    print("Model Output:\n")
    response_text = response[len(prompt):].strip() if response.startswith(prompt) else response.strip()
    print(response_text)
    print("\nDone. Try changing the prompt or generation settings for different explanations.")
    
    # Cleanup GPU memory and exit cleanly
    del model
    del tokenizer
    torch.cuda.empty_cache()

if __name__ == "__main__":
    main()
