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

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def main():
    # Verify ROCm is available
    print("="*10 + " ROCm Configuration" + "="*10)
    print(f"ROCm available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    print()

    # Load model and tokenizer
    model_name = "mistralai/Mistral-7B-Instruct-v0.3"
    # model_name = "openai/gpt-oss-20b"
    print(f"Loading {model_name}...")
    print("(First run will download ~14GB, this may take a few minutes)")
    print()

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )

    print("✓ Model loaded successfully!")
    print()

    # Create a simple prompt
    prompt = "Explain what a large language model is in simple terms:"
    
    print("="*70)
    print("Generating Response")
    print("="*70)
    print(f"Prompt: {prompt}")
    print()

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
    print("="*70)
    print("Model Output")
    print("="*70)
    # Show the *new* lines only, not the prompt again
    response_text = response[len(prompt):].strip() if response.startswith(prompt) else response.strip()
    print(response_text)
    print("="*70)
    print()
    print("Done. Try changing the prompt or generation settings for different explanations.")

if __name__ == "__main__":
    main()
