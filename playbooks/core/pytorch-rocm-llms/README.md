## Overview

Want to run powerful AI language models on your own STX Halo™ GPU? This guide shows you how.
This tutorial uses PyTorch powered by AMD's ROCm to run models that can summarize documents, answer questions, generate text, and more, all running locally.

## What You'll Learn

- Run LLMs like Mistral-7B-Instruct and gpt-oss-20b locally using PyTorch and ROCm
- Create a document summarization tool using LLMs

## Prerequisites

- **Python 3.10 or newer**
- **16GB+ GPU memory** (24GB+ recommended for 20B models)
- **50GB+ free disk space** for model storage

## Setting Up Your Environment

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

## Loading and Running Your First LLM

The included `run_llm.py` script shows how to load and generate text with LLMs using PyTorch and AMD ROCm. On the first run, model weights are automatically downloaded. The script supports choosing between Mistral 7B (fast) and GPTOSS 20B (higher quality), lets you specify which model to use with `--model`, and handles GPU memory cleanup and suppresses excess warnings for a smooth experience. 

Take a look at how prompts are tokenized and sent to the model, understanding this process lets you adapt LLMs for any text generation or summarization task. Here’s a minimal example from the script:

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

To try it out:

```bash
python assets/run_llm.py --model mistral
```

The script will run a sample prompt and print a model-generated response to the console.


## Building a Document Summarizer

Build on your LLM setup by turning it into a practical document summarizer. In this section, you will use the `assets/summarizer.py` script to feed in a .txt file and automatically generate a concise summary, all running locally on your GPU.

The script is designed to work out of the box: point it at a text file, pick a model, and it returns a clear 2–3 sentence overview. As you explore the code, you can customize prompts, tweak parameters like length and temperature, and see how different models behave.

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
