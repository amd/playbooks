## Overview

Want to run powerful AI language models on your own STX Halo™ ? This guide shows you how.
This tutorial uses PyTorch powered by AMD's ROCm to run models that can summarize documents, answer questions, generate text, and more, all running locally.

## What You'll Learn

- Run LLMs like gpt-oss-20b and Mistral-7B-Instruct locally using PyTorch and ROCm
- Create a document summarization tool using LLMs

## Prerequisites

- **Python 3.10 or newer**
- **16GB+ GPU memory** (24GB+ recommended for 20B models)
- **50GB+ free disk space** for model storage

## Setting Up Your Environment

### Create a Virtual Environment

<!-- @os:windows -->
On Windows, open Command Prompt and run:
```cmd
python -m venv llm-env
llm-env\Scripts\activate.bat
```
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv llm-env
source llm-env/bin/activate
```
<!-- @os:end -->

### Installing Basic Dependencies
<!-- @require:pytorch -->

### Additional Dependencies

```bash
pip install transformers accelerate sentencepiece protobuf
```

## Quick Start with Example Scripts

This playbook includes ready-to-use scripts in the `assets/` folder (click to preview):

| Script | Description | Usage |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Basic LLM text generation | `python assets/run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Document summarizer with file input | `python assets/summarizer.py --file document.txt` |

Both scripts support:
- Model selection: `--model mistral` or `--model gptoss`
- Automatic GPU cleanup (no hanging processes)
- Warning suppression for cleaner output

## Loading and Running Your First LLM

The included [run_llm.py](assets/run_llm.py) script shows how to load and generate text with LLMs using PyTorch and AMD ROCm. On the first run, model weights are automatically downloaded.

Take a look at how prompts are tokenized and sent to the model, understanding this process lets you adapt LLMs for any text generation or summarization task. Here’s a minimal example from the script:

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "openai/gpt-oss-20b"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto"
)
```

To try it out:

```bash
python assets/run_llm.py
```

## Building a Document Summarizer

Build on your LLM setup by turning it into a practical document summarizer. In this section, you will use the [summarizer.py](assets/summarizer.py) script to feed in a .txt file and automatically generate a concise summary, all running locally on your GPU.

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
python assets/summarizer.py --file <file.txt>

# Shorter summary with lower temperature
python assets/summarizer.py --file <file.txt>  --temperature 0.2

# Use larger model for complex documents
python assets/summarizer.py --file <file.txt> --model gptoss
```

### Batch Summarization
To summarize multiple documents at once, you can use the `summarize_batch` method as shown below:
```python
from summarizer import DocumentSummarizer

summarizer = DocumentSummarizer(model="gptoss")
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

- **Research Paper Analysis**: Extract key findings from complex publications for quick review
- **News Aggregation**: Summarize news articles into brief daily digests or highlights
- **Meeting Notes**: Condense transcripts into actionable items and concise summaries
- **Legal Document Review**: Extract relevant clauses or obligations from long legal texts quickly
- **Code Documentation**: Generate concise repository overviews and function explanations

## Next Steps

- **Fine-tuning**: Adapt models to your specific field or jargon for better accuracy (see PyTorch Fine-tuning Playbook)
- **RAG Systems**: Combine LLMs with document retrieval for context-aware answers and search
- **Model Exploration**: Experiment with new models like Llama 3, Phi-3, or Qwen for better results
- **Production Deployment**: Use tools like vLLM or TGI for scalable LLM serving in organizations

Your STX Halo™ gives you the power to run sophisticated language models locally. Experiment with different models, prompts, and parameters to discover what works best for your applications.
