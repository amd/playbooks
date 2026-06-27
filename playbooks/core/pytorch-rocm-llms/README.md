<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Overview


Want to run powerful AI language models on your own hardware? This guide shows you how.
This tutorial uses PyTorch powered by AMD ROCm™ software to run models that can summarize documents, answer questions, generate text, and more, all running locally.

## What You'll Learn

- Run LLMs like gpt-oss-20b and qwen3.5-4B locally using PyTorch and ROCm
- Create a document summarization tool using LLMs

## Setting the Memory Configuration

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Check for Software Updates
> **Note**: If VS Code is not installed, you can install it with Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installing Software Prerequisites

### Create a Virtual Environment

<!-- @os:linux -->
<!-- @device:halo_box -->
On Linux, open a terminal in the directory of your choice and follow the commands to create a venv with ROCm+Pytorch already installed.
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env --system-site-packages
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Grant your user access to GPU devices** (log out and back in for this to take effect):

```bash
sudo usermod -aG render,video $LOGNAME
```

On Linux, open a terminal in the directory of your choice and follow the commands to create a venv.
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->


<!-- @os:windows -->
<!-- @device:halo_box -->
On Windows, open a terminal in the directory of your choice and follow the commands to create a venv with ROCm+Pytorch already installed.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
On Windows, open a terminal in the directory of your choice and follow the commands to create a venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Tip**: Windows users may need to modify their PowerShell Execution Policy (e.g.
> setting it to RemoteSigned or Unrestricted) before running some Powershell commands.

<!-- @os:end -->

### Installing Basic Dependencies
<!-- @require:driver,pytorch -->

### Installing Additional Dependencies

<!-- @var:id=hf_model device=halo,halo_box value="openai/gpt-oss-20b" -->
<!-- @var:id=hf_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen/Qwen3.5-4B" -->

<!-- @device:halo,halo_box -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install "transformers>=5.9.0" safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

## Quick Start with Example Scripts

This playbook includes ready-to-use scripts. Click them to preview and download them to the same directory as the environment you created.

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
- Model selection via `--model` flag
- Chat template formatting for proper model prompting, especially useful for document summarization

## Loading and Running Your First LLM

The included [run_llm.py](assets/run_llm.py) script shows how to generate text with LLMs using PyTorch and AMD ROCm.

> **Note:** When you load a model, Hugging Face Transformers first checks its local cache (`~/.cache/huggingface/hub` on Linux, `C:\Users\<user>\.cache\huggingface\hub` on Windows). If the model isn't cached, it downloads automatically from huggingface.co. The first run may take a few minutes depending on model size and network speed.

The snippet below shows how to use the model and customize the questions asked.

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA/ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForImageTextToText

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForImageTextToText.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```
<!-- @test:end -->
<!-- @device:end -->

```python
model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

# Create system and user prompts
prompt = "Explain what a large language model is in 2 brief sentences."
print(f"Prompt: {prompt}\n")

messages = [
    {"role": "system", "content": "You are a helpful technology assistant"},
    {"role": "user", "content": f"{prompt}"},
]
```

Try out the downloaded script:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Building a Document Summarizer

Now that you've generated local LLM output, you can build on that by making a practical document summarizer. In this section, you will use the [summarizer.py](assets/summarizer.py) script to feed in a .txt file and automatically generate a concise summary, all running locally on your GPU.

The script is designed to work out of the box. Open the script in an editor to explore the code, customize prompts, and tweak parameters like length and temperature.

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### Usage Examples

```bash
# Summarize the built-in example text (defaults to openai/gpt-oss-20b)
python summarizer.py --model ${hf_model}

# Summarize a text file
python summarizer.py --file example_document.txt

# Adjust creativity with temperature
python summarizer.py --file document.txt --temperature 0.5

# Longer summaries with more tokens
python summarizer.py --file document.txt --max-length 400
```

## Learn about Generation Parameters

| Parameter | What It Controls | Typical Values |
|-----------|------------------|----------------|
| `max_new_tokens` | The maximum length of the LLM's output | Use 50–500 tokens for summaries. (1 token is about 0.75 English words) |
| `temperature` | Creativity. Low values make it focused, while high values come with more unpredictability | - **0.1–0.3**: Focused, deterministic (good for summaries) <br> **0.5–0.7**: Balanced(general use) <br> **0.8–1.0**: Creative, varied (brainstorming) |
| `top_p` | Nucleus Sampling - Low values limit the model to more narrow outputs | **0.1-0.5**: Strict, predictable <br> **0.9-0.95**: (standard, natural, conversational) |


## Real-World Applications

- **Research Paper Analysis**: Extract key findings from complex publications for quick review
- **News Aggregation**: Summarize news articles into brief daily digests or highlights
- **Meeting Notes**: Condense transcripts into actionable items and concise summaries
- **Legal Document Review**: Extract relevant clauses or obligations from long legal texts quickly
- **Code Documentation**: Generate concise repository overviews and function explanations

## Next Steps

- **Fine-tuning**: Adapt models to your specific field or jargon for better accuracy (see Fine-tuning Playbooks)
- **RAG Systems**: Combine LLMs with document retrieval for context-aware answers and search
- **Model Exploration**: Experiment with new models like Llama 3, Phi-3, or Qwen for better results
- **Production Deployment**: Use tools like vLLM for scalable LLM serving in organizations

Your system gives you the power to run sophisticated language models locally. Experiment with different models, prompts, and parameters to discover what works best for your applications.