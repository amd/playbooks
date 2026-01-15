"""
Document Summarizer using LLMs
==============================

This script provides a DocumentSummarizer class that uses large language models
to summarize text documents.

Usage:
    # Use default model (Mistral 7B)
    python summarizer.py
    
    # Use specific model
    python summarizer.py --model mistral
    python summarizer.py --model gptoss
    
Or import in your own code:
    from summarizer import DocumentSummarizer
    summarizer = DocumentSummarizer(model="mistral")
    summary = summarizer.summarize(your_text)
"""

import argparse
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


# Available models
MODELS = {
    "mistral": "mistralai/Mistral-7B-Instruct-v0.3",
    "gptoss": "Writer/GPTOSS-20B"
}


class DocumentSummarizer:
    """
    A class for summarizing documents using large language models.
    
    Attributes:
        model_name (str): The Hugging Face model identifier
        tokenizer: The model's tokenizer
        model: The loaded language model
    """
    
    def __init__(self, model="mistral"):
        """
        Initialize the summarizer with a specific model.
        
        Args:
            model (str): Model name - "mistral" (7B, ~14GB, fast) or 
                        "gptoss" (20B, ~40GB, higher quality)
        """
        if model not in MODELS:
            raise ValueError(f"Model must be one of: {list(MODELS.keys())}")
        
        self.model_name = MODELS[model]
        
        print("="*70)
        print(f"Loading {model.upper()} ({self.model_name})")
        print("(First run will download the model)")
        print("="*70)
        print()
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        print("✓ Model ready!")
        print()
    
    def summarize(self, text, max_length=200, temperature=0.3):
        """
        Summarize the given text.
        
        Args:
            text (str): The document text to summarize
            max_length (int): Maximum length of summary in tokens
            temperature (float): Sampling temperature (0.1-1.0)
                Lower = more focused, higher = more creative
        
        Returns:
            str: The generated summary
        """
        # Construct the prompt with instruction markers
        prompt = f"""[INST] Summarize the following text concisely, capturing the main points:

{text}

Provide a clear, concise summary. [/INST]"""
        
        # Tokenize the prompt
        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")
        
        # Generate the summary
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_length,
            temperature=temperature,
            do_sample=True,
            top_p=0.9
        )
        
        # Decode the output
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the summary (after [/INST])
        summary = full_response.split("[/INST]")[-1].strip()
        
        return summary
    
    def summarize_batch(self, documents, max_length=200, temperature=0.3):
        """
        Summarize multiple documents.
        
        Args:
            documents (list): List of document texts
            max_length (int): Maximum length per summary
            temperature (float): Sampling temperature
        
        Returns:
            list: List of summaries corresponding to input documents
        """
        summaries = []
        total = len(documents)
        
        for i, doc in enumerate(documents, 1):
            print(f"Processing document {i}/{total}...")
            summary = self.summarize(doc, max_length, temperature)
            summaries.append(summary)
        
        return summaries


def main():
    """Example usage with command-line arguments."""
    
    parser = argparse.ArgumentParser(description="Summarize documents using LLMs")
    parser.add_argument(
        "--model",
        type=str,
        default="mistral",
        choices=["mistral", "gptoss"],
        help="Model to use: mistral (7B, faster) or gptoss (20B, higher quality)"
    )
    
    args = parser.parse_args()
    
    # Initialize the summarizer
    summarizer = DocumentSummarizer(model=args.model)
    
    # Sample document about LLMs
    document = """
    Large language models (LLMs) are neural networks with billions of parameters 
    trained on massive text datasets. They learn to predict the next word in a 
    sequence, developing an understanding of language patterns, facts, and reasoning. 
    Modern LLMs like GPT-4, Claude, and Llama can perform diverse tasks including 
    translation, question answering, code generation, and creative writing. The key 
    breakthrough was the transformer architecture, which uses attention mechanisms 
    to process sequences in parallel. Training these models requires enormous 
    computational resources, but once trained, they can run on consumer hardware 
    for inference tasks. Recent advances include instruction tuning, where models 
    are fine-tuned to follow user instructions more accurately, and reinforcement 
    learning from human feedback (RLHF), which aligns model outputs with human 
    preferences. The field continues to evolve rapidly with new architectures, 
    training techniques, and applications emerging regularly.
    """
    
    print("="*70)
    print("Original Document")
    print("="*70)
    print(document.strip())
    print()
    
    # Generate summary
    print("="*70)
    print("Generating Summary")
    print("="*70)
    print()
    
    summary = summarizer.summarize(document)
    
    print()
    print("="*70)
    print("Summary")
    print("="*70)
    print(summary)
    print("="*70)
    print()
    print("✓ Summarization complete!")
    print()
    print("Tips:")
    print("- Try different models: --model mistral or --model gptoss")
    print("- Adjust temperature (0.1 = focused, 0.9 = creative)")
    print("- Modify max_length for longer or shorter summaries")


if __name__ == "__main__":
    main()
