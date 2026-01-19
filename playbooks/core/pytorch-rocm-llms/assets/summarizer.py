"""
Document Summarizer using LLMs

Usage:
    python summarizer.py --file mydocument.txt
    python summarizer.py --file report.txt --model mistral --max-length 100
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import argparse
import logging
import warnings

logging.getLogger("transformers").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", category=UserWarning)
os.environ["TOKENIZERS_PARALLELISM"] = "false"


MODELS = {
    "mistral": "mistralai/Mistral-7B-Instruct-v0.3",
    "gptoss": "openai/gpt-oss-20b"
}


class DocumentSummarizer:
    def __init__(self, model="mistral"):
        if model not in MODELS:
            raise ValueError(f"Model must be one of: {list(MODELS.keys())}")
        
        self.model_name = MODELS[model]
        print(f"Loading {model.upper()} ({self.model_name})...")
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        print("✓ Model ready!\n")
    
    def cleanup(self):
        """Release GPU memory and cleanup resources"""
        if hasattr(self, 'model'):
            del self.model
        if hasattr(self, 'tokenizer'):
            del self.tokenizer
        torch.cuda.empty_cache()
        print("✓ Cleaned up GPU memory")
    
    def summarize(self, text, max_length=150, temperature=0.3):
        prompt = f"""[INST] You are an expert at creating concise summaries. Summarize the following text in 2-3 sentences maximum, focusing ONLY on the most critical information. Avoid repeating details - extract only the key essence.

TEXT TO SUMMARIZE:
{text}

INSTRUCTIONS:
- Maximum 2-3 sentences
- Extract only the most important concepts
- Do NOT rephrase everything
- Be extremely brief and to the point

SUMMARY: [/INST]"""
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_length,
            temperature=temperature,
            do_sample=True,
            top_p=0.9
        )
        
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return full_response.split("[/INST]")[-1].strip()
    
    def summarize_batch(self, documents, max_length=150, temperature=0.3):
        summaries = []
        for i, doc in enumerate(documents, 1):
            print(f"Processing {i}/{len(documents)}...")
            summaries.append(self.summarize(doc, max_length, temperature))
        return summaries


def main():
    parser = argparse.ArgumentParser(description="Summarize documents using LLMs")
    parser.add_argument("--model", default="mistral", choices=["mistral", "gptoss"],
                        help="Model: mistral (7B) or gptoss (20B)")
    parser.add_argument("--file", default=None, help="Path to .txt file")
    parser.add_argument("--max-length", type=int, default=150, help="Max tokens (default: 150)")
    parser.add_argument("--temperature", type=float, default=0.3, help="Temperature 0.1-1.0 (default: 0.3)")
    args = parser.parse_args()
    
    summarizer = DocumentSummarizer(model=args.model)
    
    # Load document
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                document = f.read()
            print(f"✓ Loaded: {args.file}\n")
        except Exception as e:
            print(f"✗ Error: {e}")
            return
    else:
        document = """Large language models (LLMs) are neural networks with billions of parameters 
trained on massive text datasets. They learn to predict the next word in a sequence, 
developing an understanding of language patterns, facts, and reasoning. Modern LLMs like 
GPT-4, Claude, and Llama can perform diverse tasks including translation, question answering, 
code generation, and creative writing. The key breakthrough was the transformer architecture, 
which uses attention mechanisms to process sequences in parallel. Training these models requires 
enormous computational resources, but once trained, they can run on consumer hardware for 
inference tasks. Recent advances include instruction tuning, where models are fine-tuned to 
follow user instructions more accurately, and reinforcement learning from human feedback (RLHF), 
which aligns model outputs with human preferences. The field continues to evolve rapidly with 
new architectures, training techniques, and applications emerging regularly."""
    
    print("Using example document...")
    
    # Generate summary
    print("Generating summary...")
    summary = summarizer.summarize(document, args.max_length, args.temperature)
    print(summary)
    print(f"\n✓ Done! (max_length={args.max_length}, temperature={args.temperature})\n")
    
    # Cleanup GPU memory and exit cleanly
    summarizer.cleanup()

if __name__ == "__main__":
    main()
