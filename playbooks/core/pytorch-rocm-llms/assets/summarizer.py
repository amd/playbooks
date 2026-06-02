# Copyright Advanced Micro Devices, Inc.
# 
# SPDX-License-Identifier: MIT

"""
Document Summarizer using LLMs

Usage:
    python summarizer.py
    python summarizer.py --file example_document.txt --model gptoss
"""

import os
import argparse
import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

logging.getLogger("transformers").setLevel(logging.ERROR)
os.environ["TOKENIZERS_PARALLELISM"] = "false"


MODELS = {
    "gptoss": "openai/gpt-oss-20b",
    # download more models here as needed
}


class DocumentSummarizer:
    """Summarize documents using Large Language Models"""

    def __init__(self, model="gptoss"):
        """
        Initialize the summarizer with specified model.
        
        Args:
            model: Model name, must be one of 'gptoss' or 'mistral'
        """
        if model not in MODELS:
            raise ValueError(f"Model must be one of: {list(MODELS.keys())}")

        self.model_key = model
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

    def summarize(self, text, max_length=1024, temperature=0.3, reasoning_effort="low"):
        """
        Summarize the given text.

        Args:
            text: Text to summarize
            max_length: Maximum number of tokens to generate
            temperature: Sampling temperature (0.1-1.0)
            reasoning_effort: For Harmony-format models (gpt-oss):
                              "low" | "medium" | "high". Ignored by other models.

        Returns:
            Summary string
        """
        messages = self._build_messages(text)

        # gpt-oss supports a `reasoning_effort` argument in its chat template.
        # For non-Harmony models this kwarg will be silently ignored by most
        # templates, but we guard it just in case.
        template_kwargs = dict(
            tokenize=False,
            add_generation_prompt=True,
        )
        if self.model_key == "gptoss":
            template_kwargs["reasoning_effort"] = reasoning_effort

        try:
            prompt = self.tokenizer.apply_chat_template(messages, **template_kwargs)
        except TypeError:
            # Template doesn't accept reasoning_effort -- retry without it
            template_kwargs.pop("reasoning_effort", None)
            prompt = self.tokenizer.apply_chat_template(messages, **template_kwargs)

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
        # Harmony-format models (like gpt-oss) emit multiple channels --
        # `analysis` (chain-of-thought) and `final` (user-facing answer).
        # We only want the `final` channel for summarization.

        final_marker = "<|channel|>final<|message|>"

        if final_marker in full:
            final_part = full.split(final_marker, 1)[1]
            # Stop at end-of-turn markers if present
            for stop_tok in ("<|return|>", "<|end|>", "<|start|>"):
                if stop_tok in final_part:
                    final_part = final_part.split(stop_tok, 1)[0]
                    break
            summary = final_part.strip()

            if not summary:
                return (
                    "[Warning: model produced an empty final answer. "
                    "Try increasing --max-length or lowering --reasoning-effort.]"
                )
            return summary

        # No final-channel marker found.
        if "<|channel|>analysis" in full or "assistantanalysis" in full:
            # Model ran out of tokens while still reasoning.
            return (
                "[Warning: model did not produce a final answer before hitting "
                "the token limit. Try increasing --max-length (e.g. 2048) or "
                "setting --reasoning-effort low.]"
            )

        # Fallback for non-Harmony models (e.g. Mistral): decode without
        # special tokens and strip the echoed prompt.
        decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        input_decoded = self.tokenizer.decode(inputs["input_ids"][0], skip_special_tokens=True)
        if decoded.startswith(input_decoded):
            decoded = decoded[len(input_decoded):]
        return decoded.strip()


def main():
    parser = argparse.ArgumentParser(description="Summarize documents using LLMs")
    parser.add_argument("--model", default="gptoss", choices=list(MODELS.keys()),
                        help="Model to use (default: gptoss)")
    parser.add_argument("--file", default=None, help="Path to .txt file to summarize")
    parser.add_argument("--max-length", type=int, default=1024,
                        help="Maximum tokens to generate (default: 1024). "
                             "gpt-oss needs headroom for its reasoning channel.")
    parser.add_argument("--temperature", type=float, default=0.3,
                        help="Sampling temperature 0.1-1.0 (default: 0.3)")
    parser.add_argument("--reasoning-effort", default="low",
                        choices=["low", "medium", "high"],
                        help="Reasoning effort for Harmony models like gpt-oss "
                             "(default: low). Lower = less thinking, faster, "
                             "more likely to fit in --max-length.")
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
    summary = summarizer.summarize(
        document,
        max_length=args.max_length,
        temperature=args.temperature,
        reasoning_effort=args.reasoning_effort,
    )
    print(summary)
    print(f"\n[OK] Done! (max_length={args.max_length}, "
          f"temperature={args.temperature}, "
          f"reasoning_effort={args.reasoning_effort})\n")

    summarizer.cleanup()


if __name__ == "__main__":
    main()
