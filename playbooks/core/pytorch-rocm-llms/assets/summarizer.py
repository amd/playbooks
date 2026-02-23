"""
Document Summarizer using LLMs

Usage:
    python summarizer.py
    python summarizer.py --file example_document.txt --model gptoss
"""

import os
import argparse
import logging
import warnings

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

logging.getLogger("transformers").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", category=UserWarning)
os.environ["TOKENIZERS_PARALLELISM"] = "false"


MODELS = {
    "gptoss": "openai/gpt-oss-20b",
    "mistral": "mistralai/Mistral-7B-Instruct-v0.3"
}


class DocumentSummarizer:
    """Summarize documents using Large Language Models"""
    
    def __init__(self, model="mistral"):
        """
        Initialize the summarizer with specified model.
        
        Args:
            model: Model name, must be one of 'gptoss' or 'mistral'
        """
        if model not in MODELS:
            raise ValueError(f"Model must be one of: {list(MODELS.keys())}")
        
        self.model_name = MODELS[model]
        print(f"Loading {model.upper()} ({self.model_name})...")
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto"
        )
        print("[OK] Model ready!\n")
    
    def cleanup(self):
        """Release GPU memory and cleanup resources"""
        if hasattr(self, 'model'):
            del self.model
        if hasattr(self, 'tokenizer'):
            del self.tokenizer
        torch.cuda.empty_cache()
        print("[OK] Cleaned up GPU memory")
    
    def _build_messages(self, text):
        """
        Build chat messages for the model.
        
        Args:
            text: Text to summarize
            
        Returns:
            List of message dicts with role and content
        """
        return [
            {
                "role": "user",
                "content": (
                    "You are an expert at creating concise summaries. "
                    "Summarize the following text in 2–3 sentences maximum, "
                    "focusing only on the most critical information. "
                    "Be extremely brief and to the point.\n\n"
                    f"TEXT:\n{text}"
                ),
            }
        ]
    
    def summarize(self, text, max_length=150, temperature=0.3):
        """
        Summarize the given text.
        
        Args:
            text: Text to summarize
            max_length: Maximum number of tokens to generate
            temperature: Sampling temperature (0.1-1.0)
            
        Returns:
            Summary string
        """
        messages = self._build_messages(text)
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_length,
            temperature=temperature,
            do_sample=True,
            top_p=0.9,
        )
        
        full = self.tokenizer.decode(outputs[0], skip_special_tokens=False)
        
        # Clean up Harmony-style outputs
        # This is needed for summarization because Harmony-style models (like gpt-oss)
        # often include tool/analysis outputs and multiple assistant channels.
        # For summarization, we want only the final channel containing the actual human-readable summary,
        # not internal reasoning steps or tool traces.
        # So we specifically extract only the assistant's final message,
        # ensuring that what we return is concise and appropriate for users expecting a summary.
        
        if "<|start|>assistant<|channel|>final<|message|>" in full:
            final_part = full.split("<|start|>assistant<|channel|>final<|message|>", 1)[1]
            # Stop at <|return|> or <|end|> if present
            for stop_tok in ("<|return|>", "<|end|>"):
                if stop_tok in final_part:
                    final_part = final_part.split(stop_tok, 1)[0]
                    break
            summary = final_part.strip()
        else:
            # Fallback for models without Harmony format (e.g. Mistral)
            summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        
        # Collapse to the last non-empty line to avoid echoed prompts
        lines = [l.strip() for l in summary.splitlines() if l.strip()]
        return lines[-1] if lines else ""

def main():
    parser = argparse.ArgumentParser(description="Summarize documents using LLMs")
    parser.add_argument("--model", default="gptoss", choices=["mistral", "gptoss"], help="Model to use (default: gptoss)")
    parser.add_argument("--file", default=None, help="Path to .txt file to summarize")
    parser.add_argument("--max-length", type=int, default=150, help="Maximum tokens to generate (default: 150)")
    parser.add_argument("--temperature", type=float, default=0.3, help="Sampling temperature 0.1-1.0 (default: 0.3)")
    args = parser.parse_args()
    
    summarizer = DocumentSummarizer(model=args.model)
    
    # Load document
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                document = f.read()
            print(f"[OK] Loaded: {args.file}\n")
        except Exception as e:
            print(f"✗ Error: {e}")
            return
    else:
        # Example document
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
        print("Using example document...\n")
    
    # Generate summary
    print("Generating summary...")
    summary = summarizer.summarize(document, args.max_length, args.temperature)
    print(summary)
    print(f"\n[OK] Done! (max_length={args.max_length}, temperature={args.temperature})\n")
    
    # Cleanup
    summarizer.cleanup()


if __name__ == "__main__":
    main()
