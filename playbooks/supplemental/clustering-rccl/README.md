<<<<<<< Updated upstream
<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Clustering with Two Halos (RCCL)
=======
# Clustering Two STX Halos with RCCL
>>>>>>> Stashed changes

## Overview

Your STX Halo™ is already capable of running large language models locally. Clustering takes this further by combining the GPU memory of multiple systems over a local network, giving you access to even larger models with stronger reasoning, better code generation, and deeper multilingual understanding, all entirely on your own hardware.

This playbook teaches you how to cluster two STX Halo™ systems using RCCL (ROCm Communication Collectives Library) with vLLM and run Qwen3.5-397B, a 397B parameter model, across both machines with ROCm acceleration.

## What You'll Learn

- How to extend VRAM allocation on STX Halo™ systems
- Installing vLLM with ROCm support
- Configuring RCCL for multi-node tensor-parallel inference across two STX Halo™ systems
- Running a 397B parameter model across two networked STX Halo™ systems

## Prerequisites
<!-- @require:driver -->
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Extending VRAM Allocation

> **Note**: Complete this step on both Machine 1 and Machine 2.

### Memory configuration for running large models

On Linux, ROCm utilizes a shared system memory pool, and this pool is configured by default to half the system memory.

This amount can be increased by changing the kernel's Translation Table Manager (TTM) page setting, with the following instructions. AMD recommends setting the minimum dedicated VRAM in the BIOS (0.5GB)

* Install the pipx utility and add the path for pipx installed wheels into the system search path.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Install the amd-debug-tools wheel from PyPi.
  ```bash
  pipx install amd-debug-tools
  ```

* Run the amd-ttm tool to query the current settings for shared memory.
  ```bash
  amd-ttm
  ```

* Reconfigure shared memory settings to **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Reboot the system for changes to take effect.

For `amd-ttm` usage examples, see the [ROCm documentation](https://rocm.docs.amd.com/projects/radeon-ryzen/en/docs-7.0.2/docs/install/installryz/native_linux/install-ryzen.html#amd-ttm-usage-examples).

## Installing vLLM

> **Note**: Complete this step on both Machine 1 and Machine 2.

### Step 1: Create a Python Environment

It's recommended to use [uv](https://docs.astral.sh/uv/getting-started/installation/), a fast Python environment manager, to create and manage Python environments. Install uv via the official installer:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

After installing `uv`, you can create a new Python environment using the following commands:

```bash
uv venv --python 3.12 --seed --managed-python
source .venv/bin/activate
```

### Step 2: Install vLLM Prebuilt Wheels

Install the latest vLLM prebuilt wheels with AMD ROCm™ 7 acceleration:

```bash
uv pip install vllm --extra-index-url https://wheels.vllm.ai/rocm/
```

### Step 3: Verify the Installation

Confirm that vLLM is installed correctly:

```bash
vllm --version
```

If the installation was successful, this will print the vLLM version followed by the ROCm version (e.g., `0.17.1+rocm700`).

## Running the Model on the Cluster

vLLM uses Ray to orchestrate the cluster and RCCL to handle GPU-to-GPU communication across nodes. One machine acts as the **head node** (Machine 1), coordinating inference. The other joins as a **worker node** (Machine 2), contributing its GPU memory and compute.

At launch, vLLM shards the model across both nodes using tensor parallelism. Once loaded, inference proceeds as if running on a single accelerator.

### Step 1: Start the Ray Head Node (Machine 1)

On Machine 1, start the Ray head node to initialize the cluster:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Finding `<MACHINE_1_IP>`**: On Machine 1, run `hostname -I | awk '{print $1}'` to find its local IP address.

### Step 2: Join the Cluster (Machine 2)

On Machine 2, connect to the head node to form the cluster:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Finding `<MACHINE_2_IP>`**: On Machine 2, run `hostname -I | awk '{print $1}'` to find its local IP address.

### Step 3: Serve the Model (Machine 1)

On Machine 1, launch the vLLM server. This will automatically download the model and begin serving it across both nodes:

```bash
vllm serve Qwen/Qwen3.5-397B-A17B-GPTQ-Int4 \
  --port 7000 \
  --host 0.0.0.0 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.9 \
  --dtype float16 \
  --tensor-parallel-size 2 \
  --distributed-executor-backend ray \
  --enforce-eager \
  --language-model-only \
  --reasoning-parser qwen3
```

## Next Steps
