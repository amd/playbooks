## Overview

Unsloth is a high-efficiency LLM fine-tuning framework designed to make advanced model customization accessible on modern hardware.

It streamlines supervised fine-tuning (SFT), parameter-efficient fine-tuning (PEFT), QLoRA, and reinforcement learning approaches such as GRPO—allowing developers to adapt powerful foundation models to domain-specific tasks without large-scale infrastructure.

Rather than relying on costly distributed training clusters, Unsloth enables practical, reproducible fine-tuning workflows that run efficiently on local AI systems like Ryzen™ AI Halo.

## What You'll Learn

- How to set up the Unsloth environment
- How to fine-tune an LLM using QLoRA with Unsloth
- How to fine-tune an LLM using GRPO with Unsloth
- How to use Unsloth to benchmark kernel performance on an iGPU

## Why Unsloth?
Fine-tuning large language models has traditionally required significant compute resources and complex infrastructure. For many developers, adapting a foundation model to a specific domain—such as finance or enterprise applications—can be difficult and costly. Unsloth makes this process practical and accessible.

Unsloth is built to streamline modern LLM fine-tuning workflows, supporting techniques such as Supervised Fine-Tuning (SFT), Parameter-Efficient Fine-Tuning (PEFT), QLoRA, and reinforcement learning methods like GRPO. Instead of managing distributed systems or heavy engineering overhead, developers can focus on task design, data quality, and evaluation.

A key advantage of Unsloth is its strong support for parameter-efficient methods. With PEFT and QLoRA, only a small subset of parameters needs to be trained, significantly reducing memory requirements and training time while maintaining model performance. This allows powerful models to be adapted on a single machine.

Unsloth also enables advanced alignment through GRPO-based reinforcement learning. Beyond imitation learning, developers can directly optimize model behavior toward domain-specific objectives—such as generating investor-focused financial summaries or emphasizing risk signals.

By combining efficiency, simplicity, and reproducibility, Unsloth bridges the gap between cutting-edge research and practical deployment, enabling developers to turn general-purpose foundation models into domain-specialized systems.

## Prerequisites



## Installing unsloth

Your STX Halo has docker pre-installed. 

Pull latest PyTorch docker: 

```
sudo docker run -it -d \
  --device /dev/dri \
  --device /dev/kfd \
  --network host \
  --ipc host \
  --group-add video \
  --cap-add SYS_PTRACE \
  --security-opt seccomp=unconfined \
  --privileged \
  --shm-size 32G \
  -v /path/to/your/models:/models \
  -v /path/to/your/share:/share \
  -v /path/to/your/workspace/pr:/workspace \
  --name unsloth_playbook \
  rocm/pytorch:latest /bin/bash
```

Install unsloth_zoo using pip:
```bash
pip install "unsloth_zoo==2025.12.6"
```
Build and install unsloth[amd_radeon]:
```bash
git clone -b amd_radeon --single-branch https://github.com/eliotwang/unsloth.git
cd unsloth

PYTHONPATH="/workspace/unsloth:${PYTHONPATH}" \
UNSLOTH_FORCE_RUNTIME="hip" \
UNSLOTH_FORCE_RUNTIME_VERSION="711" \
UNSLOTH_BOOTSTRAP_ROCM="1" \
UNSLOTH_BOOTSTRAP_PYTHON="$(which python)" \
pip install -e . -v --no-build-isolation
```

## Part I: LLaMA QLoRA Finetuning 

 Pull model to local: \\

```text
LLM-Research/Meta-Llama-3.1-8B-Instruct
```

Start QLoRA Finetuning 
```bash
./scripts/run_qlora_training.sh llama
```

## Part II: GRPO Finetuning 

'''
TODO: Iswarya
'''

## Part III: Attention/MoE Kernel benchmark

### Attention accuracy/performance
```bash
./scripts/run_kernel_benchmark.sh attention
```
### MoE accuracy/performance
#### FP16
```bash
./scripts/run_kernel_benchmark.sh moe --dtypes fp16
```

#### BF16
```bash
./scripts/run_kernel_benchmark.sh moe --dtypes bf16
```

## Next Steps


## Resources

Below are some additional resources to learn more about unsloth and finetuning on 

* A comprehensive official guide covering basics and best practices for supervised fine-tuning (SFT), QLoRA, RL methods (including GRPO), dataset prep, and workflows. Fine‑tuning LLMs Guide | Unsloth Documentation https://docs.unsloth.ai/get-started/fine-tuning-llms-guide?utm_source=chatgpt.com

* Unsloth GitHub Repository: The central code repo with installation instructions, example notebooks, and links to additional resources such as community discussions and blog posts. Unsloth on GitHub (unslothai/unsloth)https://github.com/unslothai/unsloth?utm_source=chatgpt.com

* A model-specific walkthrough showing how to run and fine-tune the Qwen3 family with Unsloth, including setups for longer context lengths and advanced workflows: https://unsloth.ai/docs/models/qwen3-how-to-run-and-fine-tune?utm_source=chatgpt.com