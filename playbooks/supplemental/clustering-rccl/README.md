<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Clustering Two STX Halos with RCCL

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

## Locate the network environment variables

> **Note**: Complete this step on both Machine 1 and Machine 2.

On each machine, run `hostname -I | awk '{print $1}'` to find its local IP address.

Now run `ifconfig` and find the name of the network interface that corresponds to the IP address from the previous step and note it down (it will be referred to in the rest of the instructions as `IFNAME`).

Here is an example (IP address is 10.6.207.93, interface is enp191s0):

```bash
enp191s0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 10.6.207.93  netmask 255.255.252.0  broadcast 10.6.207.255
        inet6 fe80::7f35:81ba:90be:3f0c  prefixlen 64  scopeid 0x20<link>
        ether 38:a7:46:e6:b6:bd  txqueuelen 1000  (Ethernet)
        RX packets 7503448  bytes 10474278896 (9.7 GiB)
        RX errors 0  dropped 10313  overruns 0  frame 0
        TX packets 732453  bytes 9990339667 (9.3 GiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

## VLLM container initialization

> **Note**: Complete this step on both Machine 1 and Machine 2.

Podman is a free and open source container tool and your machine has access to a container which has vLLM installed. You can start the container with this command:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g oci-registry.ryai.dev/ryai-vllm:latest
```

## Setting network environment variables

> **Note**: Complete this step on both Machine 1 and Machine 2.

These environment variables need to be set to the `IFNAME` prior to starting the Ray cluster and the vLLM server, so that RCCL will use the correct interface for network communication.

```bash
export NCCL_SOCKET_IFNAME=<IFNAME>
export GLOO_SOCKET_IFNAME=<IFNAME> 
```

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

## Managing the container

Within the podman container, you can stop your work and detach from it using (Ctrl+P, Ctrl+Q). For more instructions and references please go here: https://docs.podman.io/en/latest

