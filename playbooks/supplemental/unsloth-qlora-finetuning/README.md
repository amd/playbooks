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

```bash
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

Start QLoRA Fine-tuning 
```bash
./scripts/run_qlora_training.sh llama
```

The successful sign in log:
```text
Training completed. Do not forget to share your model on huggingface.co/models =)
-------------------------------------------------- Peft Weights after training --------------------------------------------------
base_model.model.model.layers.0.self_attn.q_proj.lora_A.default.weight:
shape: (64, 2048)
mean: 0.000003
std: 0.012781
min: -0.023816
max: 0.023442
percentile_25: -0.011042
percentile_50: -0.000020
percentile_75: 0.011043
base_model.model.model.layers.0.self_attn.q_proj.lora_B.default.weight:
shape: (4096, 64)
mean: 0.000003
std: 0.000679
min: -0.003111
max: 0.002177
percentile_25: -0.000536
percentile_50: -0.000000
percentile_75: 0.000540
---------------------------------------------------------------------------------------------------------------------------------


-------------------------------------------------- Trainer Output --------------------------------------------------
TrainOutput(global_step=100, training_loss=1.15819159808103, metrics={'train_runtime': 436.7624, 'train_samples_per_second': 0.458, 'train_steps_per_second': 0.229, 'total_flos': 1053550340505600.0, 'train_loss': 1.15819159808103, 'epoch': 0.2})
--------------------------------------------------------------------------------------------------------------------

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
Output example:

```text
Config: batch=1 seq=128 heads=32 dim=128 dtype=torch.float16
  - torch_ref  | timed                    | fwd_diff=0.000e+00 bwd_diff=0.000e+00 | fwd=0.17ms bwd=0.22ms | stable=True
  - flash_attn | timed                    | fwd_diff=1.953e-03 bwd_diff=3.906e-03 | fwd=0.26ms bwd=0.79ms | stable=True
  - sdpa       | timed                    | fwd_diff=1.953e-03 bwd_diff=3.906e-03 | fwd=0.07ms bwd=0.13ms | stable=True

Config: batch=1 seq=2048 heads=32 dim=128 dtype=torch.float16
  - torch_ref  | timed                    | fwd_diff=0.000e+00 bwd_diff=0.000e+00 | fwd=6.11ms bwd=9.36ms | stable=True
  - flash_attn | timed                    | fwd_diff=1.953e-03 bwd_diff=3.906e-03 | fwd=1.34ms bwd=16.28ms | stable=True
  - sdpa       | timed                    | fwd_diff=1.953e-03 bwd_diff=3.906e-03 | fwd=2.13ms bwd=4.46ms | stable=True

Config: batch=4 seq=128 heads=32 dim=128 dtype=torch.float16
  - torch_ref  | timed                    | fwd_diff=0.000e+00 bwd_diff=0.000e+00 | fwd=0.15ms bwd=0.22ms | stable=True
  - flash_attn | timed                    | fwd_diff=2.441e-03 bwd_diff=3.906e-03 | fwd=0.22ms bwd=0.95ms | stable=True
  - sdpa       | timed                    | fwd_diff=2.441e-03 bwd_diff=3.906e-03 | fwd=0.10ms bwd=0.18ms | stable=True

Config: batch=4 seq=2048 heads=32 dim=128 dtype=torch.float16
  - torch_ref  | timed                    | fwd_diff=0.000e+00 bwd_diff=0.000e+00 | fwd=23.19ms bwd=36.10ms | stable=True
  - flash_attn | timed                    | fwd_diff=1.953e-03 bwd_diff=7.812e-03 | fwd=7.04ms bwd=62.54ms | stable=True
  - sdpa       | timed                    | fwd_diff=1.953e-03 bwd_diff=7.812e-03 | fwd=6.49ms bwd=14.03ms | stable=True

Config: batch=1 seq=128 heads=32 dim=128 dtype=torch.bfloat16
  - torch_ref  | timed                    | fwd_diff=0.000e+00 bwd_diff=0.000e+00 | fwd=0.16ms bwd=0.21ms | stable=True
  - flash_attn | timed                    | fwd_diff=3.125e-02 bwd_diff=3.125e-02 | fwd=0.23ms bwd=0.82ms | stable=True
  - sdpa       | timed                    | fwd_diff=3.125e-02 bwd_diff=3.125e-02 | fwd=0.07ms bwd=0.14ms | stable=True

Config: batch=1 seq=2048 heads=32 dim=128 dtype=torch.bfloat16
  - torch_ref  | timed                    | fwd_diff=0.000e+00 bwd_diff=0.000e+00 | fwd=6.21ms bwd=9.46ms | stable=True
  - flash_attn | timed                    | fwd_diff=2.344e-02 bwd_diff=6.250e-02 | fwd=1.32ms bwd=18.18ms | stable=True
  - sdpa       | timed                    | fwd_diff=2.344e-02 bwd_diff=6.250e-02 | fwd=2.12ms bwd=3.89ms | stable=True

Config: batch=4 seq=128 heads=32 dim=128 dtype=torch.bfloat16
  - torch_ref  | timed                    | fwd_diff=0.000e+00 bwd_diff=0.000e+00 | fwd=0.15ms bwd=0.21ms | stable=True
  - flash_attn | timed                    | fwd_diff=1.953e-02 bwd_diff=3.125e-02 | fwd=0.22ms bwd=1.01ms | stable=True
  - sdpa       | timed                    | fwd_diff=1.953e-02 bwd_diff=3.125e-02 | fwd=0.10ms bwd=0.19ms | stable=True

Config: batch=4 seq=2048 heads=32 dim=128 dtype=torch.bfloat16
  - torch_ref  | timed                    | fwd_diff=0.000e+00 bwd_diff=0.000e+00 | fwd=23.13ms bwd=36.02ms | stable=True
  - flash_attn | timed                    | fwd_diff=2.344e-02 bwd_diff=6.250e-02 | fwd=7.05ms bwd=70.68ms | stable=True
  - sdpa       | timed                    | fwd_diff=2.344e-02 bwd_diff=6.250e-02 | fwd=6.52ms bwd=12.10ms | stable=True
```

### MoE accuracy/performance
#### FP16
```bash
./scripts/run_kernel_benchmark.sh moe --dtypes fp16
```
Output example:
```text
=== dtype=fp16 (torch.float16) ===

Config: batch=1, seq=128, hidden=2048, experts=64
Parity   fwd_diff=0.000e+00 | bwd_diff=0.000e+00 | router_diff=0.000e+00 | stable=True
Perf     target: fwd=30.97ms bwd=43.62ms | ref: fwd=30.48ms bwd=41.88ms | stable=True

Config: batch=1, seq=512, hidden=2048, experts=64
Parity   fwd_diff=0.000e+00 | bwd_diff=0.000e+00 | router_diff=0.000e+00 | stable=True
Perf     target: fwd=32.55ms bwd=46.75ms | ref: fwd=32.55ms bwd=46.82ms | stable=True

Config: batch=4, seq=128, hidden=2048, experts=64
Parity   fwd_diff=0.000e+00 | bwd_diff=0.000e+00 | router_diff=0.000e+00 | stable=True
Perf     target: fwd=32.95ms bwd=46.71ms | ref: fwd=32.81ms bwd=46.70ms | stable=True

Config: batch=4, seq=512, hidden=2048, experts=64
Parity   fwd_diff=0.000e+00 | bwd_diff=0.000e+00 | router_diff=0.000e+00 | stable=True
Perf     target: fwd=42.04ms bwd=76.50ms | ref: fwd=41.85ms bwd=75.95ms | stable=True
```
#### BF16
```bash
./scripts/run_kernel_benchmark.sh moe --dtypes bf16
```
Output example:
```text
Config: batch=1, seq=128, hidden=2048, experts=64
Parity   fwd_diff=0.000e+00 | bwd_diff=0.000e+00 | router_diff=0.000e+00 | stable=True
Perf     target: fwd=30.23ms bwd=45.18ms | ref: fwd=29.95ms bwd=44.19ms | stable=True

Config: batch=1, seq=512, hidden=2048, experts=64
Parity   fwd_diff=0.000e+00 | bwd_diff=0.000e+00 | router_diff=0.000e+00 | stable=True
Perf     target: fwd=32.47ms bwd=48.94ms | ref: fwd=32.34ms bwd=49.06ms | stable=True

Config: batch=4, seq=128, hidden=2048, experts=64
Parity   fwd_diff=0.000e+00 | bwd_diff=0.000e+00 | router_diff=0.000e+00 | stable=True
Perf     target: fwd=32.29ms bwd=48.99ms | ref: fwd=32.57ms bwd=49.05ms | stable=True

Config: batch=4, seq=512, hidden=2048, experts=64
Parity   fwd_diff=0.000e+00 | bwd_diff=0.000e+00 | router_diff=0.000e+00 | stable=True
Perf     target: fwd=42.92ms bwd=77.06ms | ref: fwd=42.76ms bwd=76.96ms | stable=True
```
## Next Steps
TODO

## Resources

Below are some additional resources to learn more about unsloth and finetuning on 

* A comprehensive official guide covering basics and best practices for supervised fine-tuning (SFT), QLoRA, RL methods (including GRPO), dataset prep, and workflows. Fine‑tuning LLMs Guide | Unsloth Documentation https://docs.unsloth.ai/get-started/fine-tuning-llms-guide?utm_source=chatgpt.com

* Unsloth GitHub Repository: The central code repo with installation instructions, example notebooks, and links to additional resources such as community discussions and blog posts. Unsloth on GitHub (unslothai/unsloth)https://github.com/unslothai/unsloth?utm_source=chatgpt.com

* A model-specific walkthrough showing how to run and fine-tune the Qwen3 family with Unsloth, including setups for longer context lengths and advanced workflows: https://unsloth.ai/docs/models/qwen3-how-to-run-and-fine-tune?utm_source=chatgpt.com