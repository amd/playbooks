## Overview

Want to run powerful AI language models on your own STX Halo™ ? This guide shows you how.
This tutorial uses PyTorch powered by AMD's ROCm to run models that can summarize documents, answer questions, generate text, and more, all running locally.

## What You'll Learn

- Run LLMs like gpt-oss-20b and Mistral-7B-Instruct locally using PyTorch and ROCm
- Create a document summarization tool using LLMs

## Setting Up Your Environment

### Create a Virtual Environment

<!-- @os:windows -->
On Windows, open Command Prompt and run the following prompt to create a venv with ROCm+Pytorch already installed: 
<!-- @test:id=create-venv timeout=60 -->
```cmd
python -m venv llm-env --system-site-packages
llm-env\Scripts\activate.bat
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="llm-env\Scripts\activate.bat" -->
<!-- @os:end -->

<!-- @os:linux -->
On Linux, open a terminal and run the following prompt to create a venv with ROCm+Pytorch already installed:
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv llm-env --system-site-packages
source llm-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source llm-env/bin/activate" -->
<!-- @os:end -->

### Installing Basic Dependencies
<!-- @require:pytorch -->

### Additional Dependencies

<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate sentencepiece protobuf
```
<!-- @test:end -->

## Quick Start with Example Scripts

This playbook includes ready-to-use scripts in the `assets/` folder (click to preview):

| Script | Description | Usage |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Basic LLM text generation | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Document summarizer with Harmony support | `python summarizer.py --file document.txt` |

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['run_llm.py', 'summarizer.py', 'example_document.txt']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in ['run_llm.py', 'summarizer.py']:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

Both scripts support:
- Model selection: `--model gptoss` (default) or `--model mistral`
- Chat template formatting for proper model prompting especially useful for document summarization

## Loading and Running Your First LLM

The included [run_llm.py](assets/run_llm.py) script shows how to load and generate text with LLMs using PyTorch and AMD ROCm. On the first run, model weights are automatically downloaded.

Take a look at how prompts are tokenized and sent to the model. Understanding this process lets you adapt LLMs for any text generation or summarization task. Here's a minimal example from the script:

<!-- @test:id=verify-imports timeout=60 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA/ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @test:id=run-model timeout=600 setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "openai/gpt-oss-20b"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```
<!-- @test:end -->

To try it out:
<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py
```
<!-- @test:end -->

## Building a Document Summarizer

Build on your LLM setup by turning it into a practical document summarizer. In this section, you will use the [summarizer.py](assets/summarizer.py) script to feed in a .txt file and automatically generate a concise summary, all running locally on your GPU.

The script is designed to work out of the box: point it at a text file, pick a model, and it returns a clear 2–3 sentence overview. As you explore the code, you can customize prompts, tweak parameters like length and temperature, and see how different models behave.

To try it out:
<!-- @test:id=run-summarizer timeout=1000 setup=activate-venv -->
```bash
python summarizer.py
```
<!-- @test:end -->

### Usage Examples

```bash
# Summarize document
python summarizer.py

# Summarize a text file
python summarizer.py --file example_document.txt

# Adjust creativity with temperature
python summarizer.py --file document.txt --temperature 0.5

# Try different model instead
python summarizer.py --file document.txt --model mistral

# Longer summaries with more tokens
python summarizer.py --file document.txt --max-length 200
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

Your STX Halo gives you the power to run sophisticated language models locally. Experiment with different models, prompts, and parameters to discover what works best for your applications.
