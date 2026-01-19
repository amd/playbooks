## Overview

Want to run powerful AI language models on your own computer? This guide shows you how.

Large language models (LLMs) are AI systems that can understand and generate human-like text. Think ChatGPT, but running locally on your machine. Instead of paying for API access or worrying about data privacy, you can run these models yourself using your STX Halo™ GPU.

This tutorial uses PyTorch (a popular AI framework) powered by ROCm (AMD's GPU acceleration technology) to run models that can summarize documents, answer questions, generate text, and more. Your GPU makes this fast enough to be practical.

## What You'll Learn

- Run LLMs locally using PyTorch and ROCm
- Create a document summarization tool using LLMs

## Prerequisites

- **Python 3.10 or newer**
- **16GB+ GPU memory** (24GB+ recommended for 20B models)
- **50GB+ free disk space** for model storage

## Setting Up Your Environment

<!-- @os:linux -->
### Create a Virtual Environment

```bash
python3 -m venv llm-env
source llm-env/bin/activate
```

### Install PyTorch with ROCm Support

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm7.2
```

### Install Additional Dependencies

```bash
pip install transformers accelerate sentencepiece protobuf
```

> **Note**: Your STX Halo™ GPU uses AMD ROCm 7.2. The PyTorch 2.8 ROCm build provides native GPU acceleration.
<!-- @os:end -->

## Quick Start with Example Scripts

This playbook includes ready-to-use scripts in the `assets/` folder:

| Script | Description | Usage |
|--------|-------------|-------|
| **run_llm.py** | Basic LLM text generation | `python assets/run_llm.py` |
| **summarizer.py** | Document summarizer with file input | `python assets/summarizer.py --file document.txt` |

Both scripts support:
- Model selection: `--model mistral` or `--model gptoss`
- Automatic GPU cleanup (no hanging processes)
- Warning suppression for cleaner output

### Quick Examples

```bash
# Basic text generation
python assets/run_llm.py

# Summarize a text file
python assets/summarizer.py --file article.txt

# Use larger model for better quality
python assets/summarizer.py --file report.txt --model gptoss --max-length 100
```

## Understanding the Basics

### Model Size and Memory

| Model Size | Parameters | Memory (FP16) | Best For |
|------------|-----------|---------------|----------|
| **7B** | 7 billion | ~14GB | Fast inference, most tasks |
| **13B** | 13 billion | ~26GB | Better quality, complex tasks |
| **20B** | 20 billion | ~40GB | High quality, specialized tasks |

### Key Components

- **Tokenizer**: Converts text to/from numeric tokens
- **Model**: Processes tokens and predicts outputs
- **Generation Parameters**: Control output quality and creativity

## Loading Your First LLM

The `run_llm.py` script demonstrates basic LLM usage:

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "mistralai/Mistral-7B-Instruct-v0.3"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto"
)
```

Run it:

```bash
python assets/run_llm.py
```

First run downloads the model (~14GB). You'll see the model generate a response about LLMs.

## Building a Document Summarizer

To try out document summarization directly, run `assets/summarizer.py`. This standalone script provides everything you need—just pass a `.txt` file and it will generate a concise summary for you. Explore the script to learn more and customize as needed.

### Key Features

- **File input support**: Process `.txt` files directly
- **Optimized prompts**: Generates truly concise 2-3 sentence summaries
- **Model selection**: Choose between Mistral 7B (fast) or GPTOSS 20B (higher quality)
- **Adjustable parameters**: Control summary length and creativity
- **Clean output**: Suppresses warnings, proper GPU cleanup

### Core Implementation

```python
class DocumentSummarizer:
    def __init__(self, model="mistral"):
        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype=torch.float16, device_map="auto"
        )
    
    def summarize(self, text, max_length=150, temperature=0.3):
        # Optimized prompt for concise summaries
        prompt = f"""[INST] You are an expert at creating concise summaries. 
Summarize the following text in 2-3 sentences maximum, focusing ONLY on 
the most critical information. Avoid repeating details.

TEXT: {text}

SUMMARY: [/INST]"""
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")
        outputs = self.model.generate(**inputs, max_new_tokens=max_length, 
                                      temperature=temperature)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
```

### Usage Examples

```bash
# Summarize a text file
python assets/summarizer.py --file mydocument.txt

# Shorter summary with lower temperature
python assets/summarizer.py --file report.txt --max-length 100 --temperature 0.2

# Use larger model for complex documents
python assets/summarizer.py --file research.txt --model gptoss
```

### Batch Processing

```python
from summarizer import DocumentSummarizer

summarizer = DocumentSummarizer(model="mistral")
summaries = summarizer.summarize_batch(documents)
```

## Generation Parameters

| Parameter | What It Controls | Typical Values |
|-----------|------------------|----------------|
| `max_new_tokens` | Length of output | 50–500 for summaries |
| `temperature` | Randomness/creativity | 0.2–0.3 for summaries, 0.7–0.9 for creative tasks |
| `top_p` | Nucleus sampling | 0.9 (standard) |

**Temperature Guide**: 
- 0.1–0.3: Focused, deterministic (good for summaries)
- 0.5–0.7: Balanced (general use)
- 0.8–1.0: Creative, varied (brainstorming)

## Comparing Models

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **Mistral 7B Instruct** | 7B | Fast | Very Good | General summaries, high throughput |
| **GPTOSS 20B** | 20B | Moderate | Excellent | Complex documents, nuanced understanding |

Start with Mistral for learning, scale to GPTOSS for production quality.

## Performance Tips

### Enable Flash Attention (Optional)

```bash
pip install flash-attn --no-build-isolation
```

```python
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto",
    attn_implementation="flash_attention_2"  # 2-3x faster
)
```

## Real-World Applications

- **Research Paper Analysis**: Extract key findings
- **News Aggregation**: Summarize articles
- **Meeting Notes**: Condense transcripts into action items
- **Legal Document Review**: Extract relevant clauses
- **Code Documentation**: Generate repository summaries

## Next Steps

- **Fine-tuning**: Adapt models to your domain (see PyTorch Fine-tuning Playbook)
- **RAG Systems**: Combine LLMs with document retrieval
- **Model Exploration**: Try Llama 3, Phi-3, Qwen
- **Production Deployment**: Use vLLM or TGI for serving at scale

### Resources

- [Hugging Face Transformers Documentation](https://huggingface.co/docs/transformers)
- [PyTorch ROCm Documentation](https://pytorch.org/get-started/locally/)
- [Mistral AI Documentation](https://docs.mistral.ai/)

Your STX Halo™ GPU gives you the power to run sophisticated language models locally. Experiment with different models, prompts, and parameters to discover what works best for your applications.
