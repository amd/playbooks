# LLM Fine-tuning with LLaMA Factory

## Overview

Efficient fine-tuning is vital for adapting large language models (LLMs) to downstream tasks. LLaMA Factory is an open-source and user-friendly platform that streamlines the training and fine-tuning of large language models (LLMs) and multimodal models. It allows users to customize hundreds of pre-trained models locally with minimal coding.

This playbook teaches you how to finetune LLMs using LLaMA Factory on your local AMD hardware.

## What you'll learn

- How to set up LLaMA Factory with ROCm support
- How to configure LLM finetuning parameters (using Qwen/Qwen3-4B-Instruct-2507 as an example)
- How to run LLaMA Factory finetuning
- How to run inference with the fine-tuned model
- How to export the fine-tuned model 

## Estimated Time
- Duration: It will take about 60 minutes to run this playbook (depending on your model/dataset size and network speed).
- View the [LlaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory) for more information.

## Setting up the Environment

### Installing Basic Dependencies
<!-- @os:linux -->
<!-- @require:rocm,pytorch,driver -->
<!-- @os:end -->
<!-- @os:windows -->
<!-- @require:pytorch,driver -->
<!-- @os:end -->

### Installing Additional Dependencies
- **Python**: ensure minimum verison is 3.11
```bash
pip install huggingface_hub
```

<!-- @os:linux -->
<!-- @test:id=create-venv timeout=120 hidden=True -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv venv
source venv/bin/activate
python3 --version
pip --version
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="source venv/bin/activate" --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 hidden=True setup=activate-venv -->
```bash
python3 -m pip install --upgrade pip
python3 -m pip install huggingface_hub
```
<!-- @test:end --> 
<!-- @os:end -->

### Install LLaMA Factory

LLaMA Factory depends on PyTorch. You should already have it installed per the above requirements.

Download the source code from [LLaMA Factory official GitHub repository](https://github.com/hiyouga/LlamaFactory), and install its dependencies.

<!-- @os:linux -->
<!-- @test:id=install-llamafactory timeout=900 setup=activate-venv -->
```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install -e .
pip install -r requirements/metrics.txt
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=verify-llamafactory-cli timeout=60 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory
llamafactory-cli version || python -m llamafactory.cli version || true
command -v llamafactory-cli
```
<!-- @test:end --> 
<!-- @os:end -->

Having successfully installed LLaMA Factory, let's run fine-tuning on it.

## Using LLaMA Factory CLI for Fine Tuning 

This section will cover how to prepare finetuning datasets, configure LoRA/QLoRA parameters, and run LoRA finetuning.

### Dataset Preparation

LLaMA Factory supports finetuning datasets in the Alpaca format and ShareGPT format. All the available datasets have been defined in the [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). If you are using a custom dataset, please make sure to add a dataset description in dataset_info.json and specify the dataset name before training. Details can be found in their docs [here](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

In this playbook, we will use the identity and alpaca_en_demo datasets as an example, and configure the dataset information in the next step.


### Finetuning parameter configuration

LLaMA Factory supports multiple finetuning schemes.

| Finetuning schemes | LLaMA Factory Examples |
|-----------|------|
| Full-Parameter    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| LoRA fine-tuning  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| QLoRA fine-tuning | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

<!-- @os:linux -->
<!-- @test:id=verify-llamafactory-files timeout=60 hidden=True setup=activate-venv -->
```python
import os
import sys

base = "LlamaFactory"
required = [
    "examples/train_lora/qwen3_lora_sft.yaml",
    "examples/inference/qwen3_lora_sft.yaml",
    "examples/merge_lora/qwen3_lora_sft.yaml",
]

missing = [p for p in required if not os.path.exists(os.path.join(base, p))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

print("PASS: Required LLaMA Factory example files exist")
```
<!-- @test:end --> 
<!-- @os:end -->

These example configuration files have specified model parameters, fine-tuning method parameters, dataset parameters, evaluation parameters, and more. You can configure them according to your own needs. In this playbook, we will use [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml). 

**Key parameters explained:**
- `model_name_or_path` - HuggingFace Model name or local model file path.
- `stage` - Training stage. Options: rm(reward modeling), pt(pretrain), sft(Supervised Fine-Tuning), PPO, DPO, KTO, ORPO.
- `do_train` - true for training, false for evaluation
- `finetuning_type` - Fine-tuning method. Options: freeze, lora, full
- `lora_rank` - The dimensionality of the low-rank matrix used in LoRA,Typical values: 4, 6, 8, 16 (smaller values = fewer parameters = faster fine-tuning; larger values = better task adaptation but higher resource usage).
- `lora_target` - Target modules for LoRA method. Default: all.
- `dataset` - Dataset(s) to use. Use “,” to separate multiple datasets
- `output_dir` - File-tuning Output path
- `logging_steps` - Logging interval in steps
- `save_steps` - Model checkpoint saving interval.
- `overwrite_output_dir` - Whether to allow overwriting the output directory.
- `per_device_train_batch_size` - Training batch size per device.
- `gradient_accumulation_steps` - Number of gradient accumulation steps.
- `learning_rate` - Learning rate
- `num_train_epochs` - Number of training epochs
- `lr_scheduler_type` - Learning rate schedule. Options: linear, cosine, polynomial, constant, etc.
- `warmup_ratio` - Learning rate warmup ratio

We will modify the default value of lora_rank to run fine-tuning on AMD GPUs.

```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```

### Run LLaMA factory finetuning 

**llamafactory-cli** is the official command-line interface (CLI) tool for LLaMA Factory,developed to simplify end-to-end LLM workflows (data preparation → fine-tuning → evaluation → deployment) without writing complex code. 

For training/fine-tuning, **llamafactory-cli train** is the core subcommand of the LLaMA Factory CLI. It abstracts fine-tuning workflows (data preprocessing, hyperparameter tuning, hardware optimization) into a single CLI command, supporting multiple fine-tuning paradigms (LoRA/QLoRA/Full Fine-Tuning) and optimized for low-resource GPUs (e.g., QLoRA on 16GB VRAM).

You can run LLaMA Factory finetuning using the below command, which is based on the modified configuration file of Qwen3 LoRA finetuning. 

```bash
llamafactory-cli train examples/train_lora/qwen3_lora_sft.yaml
```

<!-- @os:linux -->
<!-- @test:id=quick-train-llamafactory-lora timeout=1800 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory

cp examples/train_lora/qwen3_lora_sft.yaml examples/train_lora/qwen3_lora_sft_ci.yaml

sed -i 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's|output_dir: .*|output_dir: saves/qwen3_lora_sft_ci|g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/overwrite_output_dir: false/overwrite_output_dir: true/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/per_device_train_batch_size: .*/per_device_train_batch_size: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/gradient_accumulation_steps: .*/gradient_accumulation_steps: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/num_train_epochs: .*/num_train_epochs: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/logging_steps: .*/logging_steps: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/save_steps: .*/save_steps: 5/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

After running LLM finetuning, all generated outputs are stored in the "output_dir", including model checkpoint files, configuration files, and training metrics.

<p align="center">
  <img src="assets/qwen3_lora.png" alt="Qwen3 LoRA Fine-tuning" width="600"/>
</p>

<!-- @os:linux -->
<!-- @test:id=verify-llamafactory-train-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = " "
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "trainer_state.json",
    "training_args.bin",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) + glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: LLaMA Factory training output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end --> 
<!-- @os:end -->

### Test the fine-tuned model 

**llamafactory-cli chat** is designed for interactive chat/inference with LLMs (both base models and LoRA-fine-tuned models). LLaMA Factory provides the sample configuration to run inference of fine-tuned models in [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference). You can also modify this sample configuration to change the settings such as the inference backend.

Use the following command to test Qwen3 finetuned model:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
An example chat using the finetuned model is shown below:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Finetuned model" width="600"/>
</p>


### Export the fine-tuned model

For production use-cases, the pre-trained model and the LoRA adapter need to be merged and exported into a single model. This merged model can be used as a normal HuggingFace model file. LLaMA Factory provides the sample configurations in [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora).

Use the following command to export Qwen3 finetuned model:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
The result of exporting the finetuned model is shown below.

<p align="center">
  <img src="assets/qwen3_export.png" alt="Export Qwen3 Finetuned model " width="600"/>
</p>

<!-- @os:linux -->
<!-- @test:id=export-llamafactory-model timeout=1800 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory
pip install pyyaml

python - <<'PY'
import yaml
from pathlib import Path

src = Path("examples/merge_lora/qwen3_lora_sft.yaml")
dst = Path("examples/merge_lora/qwen3_lora_sft_ci.yaml")

cfg = yaml.safe_load(src.read_text())

cfg["adapter_name_or_path"] = "saves/qwen3_lora_sft_ci"
cfg["export_dir"] = "saves/qwen3_lora_sft_ci_merged"

dst.write_text(yaml.safe_dump(cfg, sort_keys=False))
print(f"Wrote {dst}")
PY

llamafactory-cli export examples/merge_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=verify-llamafactory-export-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "LlamaFactory/saves/qwen3_lora_sft_ci_merged"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing export directory: {out_dir}")
    sys.exit(1)

required = ["config.json",]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required export files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Exported merged model output looks correct")
```
<!-- @test:end --> 
<!-- @os:end -->

## Using LLaMA Factory GUI
LLaMA-Factory also supports zero-code fine-tuning of large language models through a web UI in the browser.

Use the following command to open it:

```bash
llamafactory-cli webui
```


## Next Steps
- Try different models such as gpt-oss and other state of the art models.
- Experiment with different backends on the finetuned model
 
For more documentation, please visit: https://llamafactory.readthedocs.io/en/latest/ 