<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Clustering Two STX Halos with llama.cpp RPC

## Overview

Your STX Halo™ is already capable of running large language models locally. Clustering takes this further by combining the GPU memory of multiple systems over a local network, giving you access to even larger models with stronger reasoning, better code generation, and deeper multilingual understanding, all entirely on your own hardware.

This playbook teaches you how to cluster two STX Halo™ systems using llama.cpp's RPC engine and run GLM 4.7, a 358B parameter model, across both machines with ROCm acceleration.

## What You'll Learn

- How to extend VRAM allocation on STX Halo™ systems
- Installing llama.cpp with ROCm and RPC support
- Configuring an RPC worker and launching distributed inference across two nodes
- Running a 358B parameter model across two networked STX Halo™ systems

## Prerequisites
<!-- @require:driver -->

<!-- @os:windows -->
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) with the **Desktop Development with C++** workload
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Extending VRAM Allocation

> **Note**: Complete this step on both Machine 1 and Machine 2.

<!-- @os:windows -->
### Memory configuration for running large models

On Windows, to run larger models that require higher memory, we need to use the AMD Variable Graphics Memory (iGPU VRAM) allocation.

This can be done by opening AMD Software: Adrenalin Edition control panel and navigating to: `Performance > Tuning > AMD Variable Graphics Memory`. Set the value to **96 GB**. Please reboot the system for the changes to take effect.

<!-- @os:end -->

<!-- @os:linux -->
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

<!-- @os:end -->

## Installing llama.cpp

> **Note**: Complete this step on both Machine 1 and Machine 2.

Two installation options are available:

- [Option 1: Lemonade SDK (Recommended)](#option-1-lemonade-sdk-recommended) - pre-built binaries, fastest setup
- [Option 2: Manual Source Build](#option-2-manual-source-build) - build from source with full control over build flags

### Option 1: Lemonade SDK (Recommended)

The Lemonade SDK provides nightly builds of llama.cpp with AMD ROCm™ 7 acceleration, targeting GPUs such as gfx1151 (Strix Halo / Ryzen AI Max+ 395) and other recent Radeon architectures.

<!-- @os:windows -->
#### Step 1: Download the Pre-Built Binaries

Navigate to the latest release page and download the archive matching your platform and GPU target:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Download the file named `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (where `xxxx` is the build number).

#### Step 2: Extract the Binaries

Unzip the downloaded archive:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

This directory now contains ROCm-enabled builds of `llama-cli.exe`, `llama-server.exe`, and `rpc-server.exe`, precompiled for your STX Halo™ system.

#### Step 3: Verify GPU Detection

```bash
.\llama-cli.exe --list-devices
```

Expected output:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Step 1: Download the Pre-Built Binaries

Navigate to the latest release page and download the archive matching your platform and GPU target:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Download the file named `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (where `xxxx` is the build number).

#### Step 2: Extract and Prepare the Binaries

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

This directory now contains ROCm-enabled builds of `llama-cli`, `llama-server`, and `rpc-server`, precompiled for your STX Halo™ system.

#### Step 3: Verify GPU Detection

```bash
./llama-cli --list-devices
```

Expected output:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
With llama.cpp prepared on each node, proceed to [Downloading the Model](#downloading-the-model).

### Option 2: Manual Source Build

<!-- @os:windows -->
#### Step 1: Build llama.cpp

Open the **x64 Native Tools Command Prompt** (installed with Visual Studio Build Tools) and clone the repository:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Add HIP to your path and build with ROCm and RPC support:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Build Flag | Purpose |
|-----------|---------|
| `-DGGML_HIP=ON` | Enables the ROCm/HIP software stack |
| `-DGGML_RPC=ON` | Enables RPC for distributed inference |
| `-DGPU_TARGETS=gfx1151` | Targets the STX Halo™ GPU (Radeon 8060s) |
| `-G Ninja` | Uses the Ninja build system |

#### Step 2: Verify GPU Detection

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Expected output:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Step 3: Add HIP to Your User Path

The build step above set `%HIP_PATH%\bin` for the current session only. To make the HIP libraries available in any terminal (not just the x64 Native Tools Command Prompt), add it to your user `PATH` permanently:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

With llama.cpp prepared on each node, proceed to [Downloading the Model](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Step 1: Build llama.cpp

Clone the repository:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Build with ROCm and RPC support:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Build Flag | Purpose |
|-----------|---------|
| `-DGGML_HIP=ON` | Enables the ROCm software stack |
| `-DGGML_RPC=ON` | Enables RPC for distributed inference |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Enables rocWMMA for enhanced Flash Attention on AMD GPUs |
| `-DAMDGPU_TARGETS="gfx1151"` | Targets the STX Halo™ GPU (Radeon 8060s) |

For more build options, refer to the [llama.cpp build documentation](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Step 2: Verify GPU Detection

```bash
cd rocm/bin
./llama-cli --list-devices
```

Expected output:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

With llama.cpp prepared on each node, proceed to [Downloading the Model](#downloading-the-model).
<!-- @os:end -->

## Downloading the Model

This playbook uses [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), a 358B parameter model in the `Q4_K_XL` quantization from [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). At this quantization the model requires approximately 205GB of storage and fits within the combined GPU memory of two STX Halo™ nodes.

Download the GGUF files using the Hugging Face CLI:
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

> **Note**: The model download must be completed on Machine 1 (the controller). The RPC worker nodes do not need a local copy of the model files.

## Launching the Model on the Cluster

The llama.cpp RPC (Remote Procedure Call) engine allows a single llama.cpp instance to offload model layers to remote workers over the network. One machine acts as the **controller** (Machine 1), handling tokenization, scheduling, and orchestration. The other machine runs a lightweight **RPC server** (Machine 2) that exposes its GPU memory and compute to the controller.

At load time, llama.cpp shards the model across both nodes. Once loaded, inference proceeds as if running on a single accelerator. RPC handles tensor transfers and synchronization behind the scenes.

### Step 1: Start the RPC Server (Machine 2)

On Machine 2, start the RPC server to expose its GPU resources to the controller:
<!-- @os:linux -->
```bash
./rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| Flag | Purpose |
|------|---------|
| `-p` | Port to broadcast the RPC server on |
| `-c` | Enables a local cache for large tensors, avoiding repeated network transfers during model loading |
| `--host` | IP address to bind the RPC server to (`0.0.0.0` for all interfaces) |

For more options, refer to the [llama.cpp RPC documentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Step 2: Launch the Model (Machine 1)

With the RPC server running on Machine 2, launch inference from Machine 1 using either `llama-cli` or `llama-server`.

#### llama-cli

`llama-cli` provides a terminal-based interface for interacting directly with the model. It is ideal for benchmarking, debugging, and low-level experimentation.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --rpc <RPC_WORKER_IP>:50053
```

> **Finding `<RPC_WORKER_IP>`**: On Machine 2, run `hostname -I | awk '{print $1}'` to find its local IP address.
<!-- @os:end -->

<!-- @os:windows -->
> **Note**: Run this command in Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Finding `<RPC_WORKER_IP>`**: On Machine 2, run `ipconfig | findstr /C:"IPv4"` in Terminal (Powershell) to find its local IP address.

<!-- @os:end -->

Once running, `llama-cli` displays model loading progress and enters an interactive prompt where you can chat directly with the model:

![llama-cli running GLM 4.7 across two nodes](assets/llama-cli-example.png)

#### llama-server

`llama-server` exposes the same inference engine through a persistent server process with an integrated web UI and an OpenAI-compatible HTTP API. This is the preferred interface for longer-running deployments, multi-user access, and integration with external tooling.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **Finding `<RPC_WORKER_IP>`**: On Machine 2, run `hostname -I | awk '{print $1}'` to find its local IP address.
<!-- @os:end -->

<!-- @os:windows -->
> **Note**: Run this command in Terminal (Powershell).

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **Finding `<RPC_WORKER_IP>`**: On Machine 2, run `ipconfig | findstr /C:"IPv4"` in Terminal (Powershell) to find its local IP address.
<!-- @os:end -->

Once started, open `http://<HOST_IP>:8081` in your browser to access the built-in web UI. This provides a browser-based chat interface for interacting with the model:

![llama-server web UI running GLM 4.7 across two nodes](assets/llama-server-example.png)

<!-- @os:linux -->
> **Finding `<HOST_IP>`**: On Machine 1, run `hostname -I | awk '{print $1}'` to find its local IP address.
<!-- @os:end -->

<!-- @os:windows -->
> **Finding `<HOST_IP>`**: On Machine 1, run `ipconfig | findstr /C:"IPv4"` in Terminal (Powershell) to find its local IP address.
<!-- @os:end -->

#### Parameter Reference

| Flag | Purpose |
|------|---------|
| `-m` | Path to the GGUF model file (use the first shard, `00001-of-00005`) |
| `-c` | Context size in tokens. Larger values use more memory |
| `-fa on` | Enables rocWMMA Flash Attention for improved performance on AMD GPUs |
| `-ngl 999` | Offloads all model layers to the GPU |
| `--no-mmap` | Disables memory-mapping, reducing load times when model size exceeds system RAM but fits in VRAM |
| `--host` | IP to bind `llama-server` to (`llama-server` only) |
| `--port` | Port to serve the HTTP API on (`llama-server` only) |
| `--rpc` | Comma-separated list of RPC worker endpoints (`IP:port`) |

For full parameter usage, refer to the [llama-cli documentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) and [llama-server documentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Next Steps

- **Connect third-party applications**: `llama-server` exposes an OpenAI-compatible API. Point any OpenAI-compatible application (such as Open WebUI) at `http://<HOST_IP>:8081` with any placeholder API key (e.g., `none`) to connect to your cluster
- **Explore other models**: Browse quantized GGUFs on [Hugging Face](https://huggingface.co/models?search=gguf) to find models that fit within your cluster's combined GPU memory
- **Scale to four nodes**: Add two more STX Halo™ systems as additional RPC workers to access models at the 1 trillion parameter scale. Pass additional endpoints to `--rpc` as a comma-separated list (e.g., `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)