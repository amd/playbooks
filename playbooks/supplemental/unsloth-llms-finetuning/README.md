## Overview

<!-- ![alt text](assets/unsloth.png) -->

Unsloth is a high-efficiency LLM fine-tuning framework designed to make advanced model customization accessible on modern hardware.

This playbook teaches you how to use Unsloth for practical fine-tuning workflows that run efficiently on local AI systems like Ryzen™ AI Halo.

## What You'll Learn

- How to set up the Unsloth environment
- How to fine-tune a LLM using SFT with Unsloth
- How to save the fine-tuned result in local storage

## Why Unsloth?
Fine-tuning large language models no longer requires massive compute or complex infrastructure—Unsloth focuses on making it fast and memory-efficient.

A key strength of Unsloth lies in its VRAM optimization and accelerated training pipeline. By leveraging techniques such as optimized kernels and parameter-efficient fine-tuning (PEFT), it significantly reduces memory usage while enabling much faster training compared to standard approaches.

In this project, we primarily adopt Supervised Fine-Tuning (SFT) with QLoRA, where only a small subset of parameters is updated. This allows us to fine-tune large models on consumer-grade hardware without sacrificing performance.

Beyond SFT, Unsloth also supports GRPO-based reinforcement learning, enabling further alignment toward domain-specific objectives when needed.

Overall, Unsloth bridges the gap between research and real-world deployment—making it practical to adapt foundation models into specialized systems efficiently.

## Set up your environment

<!-- @os:windows -->
On Windows, open a terminal in the directory of your choice and follow the commands to create a venv with ROCm+Pytorch already installed.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv unsloth-env --system-site-packages
unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->

> **Tip**: Windows users may need to modify their PowerShell Execution Policy (e.g.
> setting it to RemoteSigned or Unrestricted) before running some Powershell commands.

<!-- @os:end -->

<!-- @os:linux -->
On Linux, open a terminal and run the following prompt to create a venv with ROCm+Pytorch already installed:
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv unsloth-env --system-site-packages
source unsloth-env/bin/activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" --> 
<!-- @os:end -->

### Installing Basic Dependencies
<!-- @require:pytorch -->

### Additional Dependencies

<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install --no-deps git+https://github.com/unslothai/unsloth-zoo.git
pip install --no-deps --upgrade timm
pip install datasets transformers trl
```
<!-- @test:end -->

## Download the Unsloth Fine Tuning Script

Instead of manually executing each step, this playbook provides a clean, end-to-end script here: [test_unsloth.py](assets/test_unsloth.py).

Run the following code to execute the script:

```bash
python test_unsloth.py
```

The rest of the playbook will conceptually go through each major step of the script. 

## How It Works
The test_unsloth.py script performs the following steps:
* **Load Model**: Loads unsloth/gemma-3n-E4B-it using FastModel.
* **Prepare Data**: Standardizes the dataset (e.g., FineTome-100k) and applies the Gemma-3 chat template.
* **Apply LoRA**: Adds adapters to language, attention, and MLP modules for efficient training.
* **Train**: Uses SFTTrainer with response-only loss masking.
* **Inference**: Runs a quick generation test to verify performance.
* **Save**: Exports LoRA adapters locally.

## Key Configuration
You can modify the following constants to customize your run:

```python
MODEL_NAME = "unsloth/gemma-3n-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_3n_lora"
```

Example of the Unsloth welcome message and output when loading the model weights:
![alt text](assets/welcome.png)

## Prepare Dataset

We use a subset of:
```text
mlabonne/FineTome-100k
```
The dataset is: 
* Converted into chat format
* Processed using the Gemma-3 chat template
* Cleaned to remove duplicate BOS tokens

## Train the Model

The script runs a short training demo, with the following parameters:
- ~50 steps
- Small batch size
- Gradient accumulation

During training, you will see logs such as:
```
![alt text](assets/training.png)


## Optional: Lower Memory (4-bit)
You can enable 4-bit quantization by using a 4-bit quantized model:
```python
load_in_4bit = True
model_name = "unsloth/gemma-3n-E4B-it-unsloth-bnb-4bit"
```
This reduces memory usage significantly with minimal quality loss.

## Saving and Deployment
### Local Saving (LoRA)

The script automatically saves LoRA adapters to the OUTPUT_DIR.
```python
model.save_pretrained("gemma_3n_lora")  
tokenizer.save_pretrained("gemma_3n_lora")
```

### Save merged model (for vLLM) 

For deployment with vLLM, merge the adapters into a full model:
```python
model.save_pretrained_merged("gemma-3N-finetune", tokenizer)
```

### Export GGUF (for llama.cpp)

Convert directly to GGUF for local inference:
```python
model.save_pretrained_gguf("gemma_3n_finetune", tokenizer, quantization_method="Q8_0")
```


## Next Steps
- Train on your own specific datasets
- Try finetuning with different hyperparameters
- Experiment with different quantization levels to understand the tradeoff between memory usage and quality
- Deploy with vLLM or llama.cpp

## Resources

Below are some additional resources to learn more about unsloth and finetuning on 

* [Unsloth Docs](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth Fine-tuning Guide](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)
