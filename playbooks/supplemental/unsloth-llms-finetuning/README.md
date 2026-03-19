## Overview

<!-- ![alt text](assets/unsloth.png) -->

Unsloth is a high-efficiency LLM fine-tuning framework designed to make advanced model customization accessible on modern hardware.

It streamlines supervised fine-tuning (SFT), parameter-efficient fine-tuning (PEFT), QLoRA, and reinforcement learning approaches such as GRPO—allowing developers to adapt powerful foundation models to domain-specific tasks without large-scale infrastructure.

Rather than relying on costly distributed training clusters, Unsloth enables practical, reproducible fine-tuning workflows that run efficiently on local AI systems like Ryzen™ AI Halo.

## What You'll Learn

- How to set up the Unsloth environment
- How to fine-tune a LLM using SFT with Unsloth
- How to save the fine-tune result in local storage

## Why Unsloth?
Fine-tuning large language models has traditionally required significant compute resources and complex infrastructure. For many developers, adapting a foundation model to a specific domain—such as finance or enterprise applications—can be difficult and costly. Unsloth makes this process practical and accessible.

Unsloth is built to streamline modern LLM fine-tuning workflows, supporting techniques such as Supervised Fine-Tuning (SFT), Parameter-Efficient Fine-Tuning (PEFT), QLoRA, and reinforcement learning methods like GRPO. Instead of managing distributed systems or heavy engineering overhead, developers can focus on task design, data quality, and evaluation.

A key advantage of Unsloth is its strong support for parameter-efficient methods. With PEFT and QLoRA, only a small subset of parameters needs to be trained, significantly reducing memory requirements and training time while maintaining model performance. This allows powerful models to be adapted on a single machine.

Unsloth also enables advanced alignment through GRPO-based reinforcement learning. Beyond imitation learning, developers can directly optimize model behavior toward domain-specific objectives—such as generating investor-focused financial summaries or emphasizing risk signals.

By combining efficiency, simplicity, and reproducibility, Unsloth bridges the gap between cutting-edge research and practical deployment, enabling developers to turn general-purpose foundation models into domain-specialized systems.

<!-- @os:windows -->
On Windows, open Command Prompt and run the following prompt to create a venv with ROCm+Pytorch already installed: 
<!-- @test:id=create-venv timeout=60 -->
```cmd
python -m venv unsloth-env --system-site-packages
unsloth-env\Scripts\activate.bat
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate.bat" -->
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

## Installing Basic Dependencies
<!-- @require:pytorch -->

## Additional Dependencies

<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install --no-deps git+https://github.com/unslothai/unsloth-zoo.git
pip install --no-deps --upgrade timm
pip install datasets transformers trl
```
<!-- @test:end -->

## Unsloth LoRA Fine-tuning Example

Instead of manually executing each step, this playbook provides a clean, end-to-end script:

[test_unsloth.py](assets/test_unsloth.py)

Run the demo training pipeline with:

```bash
python assets/test_unsloth.py
```

## How It Works
The test_unsloth.py script performs the following steps:
* Load Model: Loads unsloth/gemma-3n-E4B-it using FastModel.
* Prepare Data: Standardizes the dataset (e.g., FineTome-100k) and applies the Gemma-3 chat template.
* Apply LoRA: Adds adapters to language, attention, and MLP modules for efficient training.
* Train: Uses SFTTrainer with response-only loss masking.
* Inference: Runs a quick generation test to verify performance.
* Save: Exports LoRA adapters locally.

## Key Configuration
You can modify the following constants in assets/test_unsloth.py to customize your run:

```python
MODEL_NAME = "unsloth/gemma-3n-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_3n_lora"
```

Unsloth welcome message and Loading the model weights:
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

The script runs a short demo training:
```text
~50 steps
Small batch size with gradient accumulation
Optimized for local hardware
During training, you will see logs such as:
```
![alt text](assets/training.png)


## Optional: Lower Memory (4-bit)
You can enable 4-bit quantization by modifying the model:
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
Train on your own dataset

Increase training steps or epochs

Enable 4-bit QLoRA for lower memory

Deploy with vLLM or llama.cpp
## Resources

Below are some additional resources to learn more about unsloth and finetuning on 

* Unsloth Docs
https://docs.unsloth.ai

* GitHub
https://github.com/unslothai/unsloth

* Fine-tuning Guide
https://docs.unsloth.ai/get-started/fine-tuning-llms-guide
