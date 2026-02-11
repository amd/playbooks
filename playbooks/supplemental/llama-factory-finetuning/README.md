# LLM Fine-tuning with llama factory

## Overview

Efficient fine-tuning is vital for adapting large language models (LLMs) to downstream tasks. Llama factory is an open-source, efficient, and user-friendly platform designed to streamline the training and fine-tuning of large language models (LLMs) and multimodal models. Its core strength lies in enabling users to customize hundreds of pre-trained models locally with minimal coding, spanning from data preparation and model training to human alignment and deployment.

This playbook teaches you how to finetune LLMs using llama factory on your STX Halo™ GPU and other AMD RDNA3 and RDNA4 GPUs.

## In This Playbook, You Will Learn

- How to set up llama factory with ROCm support
- How to configure LLM finetuning parameters (using Qwen/Qwen3-4B-Instruct-2507 as an example)
- How to run llama factory finetuning
- How to run inference with fine-tuned model
- How to export the fine-tuned model 

## Instructions

### Install llama factory on ROCm GPU

llama factory depends on PyTorch, and rocm developers can install PyTorch through the below options: 
- Using a prebuilt Docker image with PyTorch pre-installed from [AMD rocm pytorch docker hub] (https://hub.docker.com/r/rocm/pytorch/tags )
- Using a wheels package from [offical PyTorch webiste](https://pytorch.org/get-started/locally/)
- Building PyTorch from source as the steps of [rocm document](https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/3rd-party/pytorch-install.html#build-pytorch-from-source)

For this playbook, we'll use the **prebuilt Docker image** which includes Pytorch with ROCm support, making it the easiest way to get started on AMD GPUs. The below command is just for your reference, please use the latest version ROCm docker image.

#### Pull the Docker Image
First, pull the ROCm PyTorch Docker image:

```bash
docker pull rocm/pytorch:rocm7.2_ubuntu24.04_py3.12_pytorch_release_2.9.1 
```

#### Launch the PyTorch docker container
Start the ROCm PyTorch container with AMD GPU access and mount your local data directory if need.

```bash
docker run -it \
    --cap-add=SYS_PTRACE \
    --security-opt seccomp=unconfined \
    --device=/dev/kfd \
    --device=/dev/dri \
    --group-add video \
    --ipc=host \
    --shm-size 8G \
    -v {host data path}:/data \
    rocm/pytorch:rocm7.2_ubuntu24.04_py3.12_pytorch_release_2.9.1
```

#### Install llama factory

Download the source code from [llama factory official GitHub repository](https://github.com/hiyouga/LlamaFactory),and install LLaMA Factory with dependencies.

```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install -e .
pip install -r requirements/metrics.txt
```

If you would like to try Llama Factory QLora finetuning through BitsandBytes library, you also need to install bitsandbytes. In this playbook, we introdue how to compile and install bitsandbytes library on AMD ROCm GPU, which can help developer enjoy the latest bitsandbytes quantization solutions.

```bash
# Install bitsandbytes from source
# Clone bitsandbytes repo
git clone https://github.com/bitsandbytes-foundation/bitsandbytes.git && cd bitsandbytes/

# Compile & install
apt-get install -y build-essential cmake  # install build tools dependencies, unless present
cmake -DCOMPUTE_BACKEND=hip -DBNB_ROCM_ARCH="gfx1150" -S . # Use -DBNB_ROCM_ARCH to target specific gpu arch,gfx1201 for 9070xt GPU, hgx1150 for strix halo
make
pip install -e .
```

Now you have installed llama factory successfully on AMD ROCm GPU. and next step is to run LLM finetuning on it.

### Run llama factory finetuing 

In this section, we will introduce finetuning dataset, parameter configuration,Lora
#### Dataset Preparation

Llama factory supports the finetuning datasets in Alpaca format and ShareGPT format. All the avaiable datasets have been defined in Llama Factory [dataset_info.json] (https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). If you are using a custom dataset, please make sure to add a dataset description in dataset_info.json and specify dataset: dataset_name before training to use it. Detailes can be found in their [offical document](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

In this playbook, we will use identity and alpaca_en_demo datasets as an example.

#### Finetuning parameter configuration

Llama factory supports mutilple finetuning schemes, and has provides the parameter configuration examples for fine-tuning. you can find full-Parameter fine-tuning example from [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full), LoRA fine-tuning example in [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora),QLoRA fine-tuning example in [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora).

This configuration file specifies model parameters, fine-tuning method parameters, dataset parameters, evaluation parameters, etc. You need to configure them according to your own needs. In this playbook, we take [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml) as an example. 

**Key parameters explained:**
- `model_name_or_path` - Huggingface Model name or local model file path.
- `stage` - Training stage. Options: rm(reward modeling), pt(pretrain), sft(Supervised Fine-Tuning), PPO, DPO, KTO, ORPO.
- `do_train` - true for training, false for evaluation
- `finetuning_type` - Fine-tuning method. Options: freeze, lora, full
- `lora_rank` - The dimensionality of the low-rank matrix used in LoRA,Typical values: 4, 6, 8, 16(smaller values = fewer parameters = faster fine-tuning; larger values = better task adaptation but higher resource usage).
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

In this playbook,we modified the default value of lora_rank to run fine-tuning on AMD GPUs.

```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```

if you would like to run bitsandbytes QLoRA finetuning, you can also tried to modify lora_rank in the corresponding configuration file.

```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_qlora/qwen3_lora_sft_bnb_npu.yaml
```

#### Run Llama factory finetuning 

**llamafactory-cli** is the official command-line interface (CLI) tool for LLaMA Factory,developed to simplify end-to-end LLM workflows (data preparation → fine-tuning → evaluation → deployment) without writing complex code.For training/fine-tuning, **llamafactory-cli train** is the flagship subcommand of the LLaMA Factory CLI, designed for end-to-end fine-tuning of large language models (LLMs) with minimal code. It abstracts complex fine-tuning workflows (data preprocessing, hyperparameter tuning, hardware optimization) into a single CLI command, supporting multiple fine-tuning paradigms (LoRA/QLoRA/Full Fine-Tuning) and optimized for low-resource GPUs (e.g., QLoRA on 16GB VRAM). Unlike custom PyTorch training scripts, it enforces best practices (e.g., gradient checkpointing, mixed precision) and natively integrates with Hugging Face ecosystems—making it the primary tool for customizing LLMs in LLaMA Factory.

You can run llama factory finetuning using the below command,which is based on the modified configuration file for Qwen3 LoRA finetuning. 
```bash
llamafactory-cli train examples/train_lora/qwen3_lora_sft.yaml
```
If you would like to try QLoRA with bitsandbytes, the below command is a typical example.
```bash
llamafactory-cli train examples/train_qlora/qwen3_lora_sft_bnb_npu.yaml
```
After running LLM finetuning, output files can be found in the path of "output_dir", like the model checkpoint directory, model configuration files,training metrics data files. 

### Llama factory finetuned model's inference and export 
#### Fine-tuned model inference 
**llamafactory-cli chat** is a core subcommand of the LLaMA Factory CLI, designed for interactive chat/inference with LLMs (both base models and LoRA-fine-tuned models). It simplifies the process of running conversational inference with minimal configuration, supports mainstream LLMs, and offers flexible control over generation hyperparameters (temperature, max tokens, etc.). Llama factory also provided the sample configuration to run inference of fine-tuned models in [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference).

In this playbook, we used the below command to run Qwen3 finetuned model inference 
```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```

#### Export the fine-tuned model
**llamafactory-cli export** is a critical subcommand of the LLaMA Factory CLI, designed to convert fine-tuned LLMs (base models + LoRA adapters) into deployment-friendly formats for production use. It bridges the gap between LLaMA Factory’s fine-tuning workflow (PyTorch/Hugging Face format) and real-world deployment tools (e.g., llama.cpp, vLLM), supporting quantization (4/8-bit) and cross-format compatibility.  

In this playbook, we used the below command to export Qwen3 finetuned model. 
```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
## Next Steps
- **Try more models on AMD GPUs**: We use qwen3 as an example, developer can try other supported models,like gpt-oss, on AMD GPUs.
- **Try more finetuning schemes on AMD GPUs**: We use LoRA as an example, developer can try others,like full-Parameter, on AMD GPUs.

For more documentation, please visit: https://llamafactory.readthedocs.io/en/latest/ 