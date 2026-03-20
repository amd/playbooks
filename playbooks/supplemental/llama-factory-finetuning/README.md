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


### Install LLaMA Factory

LLaMA Factory depends on PyTorch. You should already have it installed per the above requirements.

Download the source code from [LLaMA Factory official GitHub repository](https://github.com/hiyouga/LlamaFactory), and install its dependencies.

```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install -e .
pip install -r requirements/metrics.txt
```

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

After running LLM finetuning, output files can be found in the path of "output_dir", like the model checkpoint files, model configuration files,training metrics data files.

<p align="center">
  <img src="assets/qwen3_lora.png" alt="Qwen3 LoRA Fine-tuning" width="600"/>
</p>


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