<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

<!-- @toggle:link=ethernet -->
<!-- @toggle:nodes=2 -->
# Clustering Two Ryzen™ AI Halos with RPC
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
# Clustering Four Ryzen™ AI Halos with RPC
<!-- @toggle:end -->
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
# Clustering Two Ryzen™ AI Halos with RPC over USB4
<!-- @toggle:end -->

## Overview

<!-- @toggle:link=ethernet -->
Your Ryzen™ AI Halo is already capable of running large language models locally. Clustering takes this further by combining the GPU memory of multiple systems over a local network, giving you access to even larger models with stronger reasoning, better code generation, and deeper multilingual understanding, all entirely on your own hardware.
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
Your Ryzen™ AI Halo is already capable of running large language models locally. Clustering takes this further by combining the GPU memory of multiple systems, giving you access to even larger models with stronger reasoning, better code generation, and deeper multilingual understanding, all entirely on your own hardware.
<!-- @toggle:end -->

<!-- @toggle:link=ethernet -->
<!-- @toggle:nodes=2 -->
This playbook teaches you how to cluster two Ryzen AI Halo systems using llama.cpp's RPC engine and run GLM 4.7, a 358B parameter model, across both machines with AMD ROCm™ acceleration.
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
This playbook teaches you how to cluster four Ryzen AI Halo systems using llama.cpp's RPC engine and run Kimi K2.6, a large mixture-of-experts model, across all four machines with AMD ROCm™ acceleration.
<!-- @toggle:end -->
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
This playbook teaches you how to cluster two Ryzen AI Halo systems connected directly with a single USB4/Thunderbolt™ cable, with no network switch required. Using llama.cpp's RPC engine, you will run GLM 4.7, a 358B parameter model, across both machines with AMD ROCm™ acceleration.
<!-- @toggle:end -->

## What You'll Learn

- How to extend VRAM allocation on Ryzen AI Halo systems
<!-- @toggle:link=usb4 -->
- Setting up a direct USB4/Thunderbolt network link between two systems
<!-- @toggle:end -->
- Installing llama.cpp with ROCm and RPC support
<!-- @toggle:link=ethernet -->
<!-- @toggle:nodes=2 -->
- Configuring an RPC worker and launching distributed inference across two nodes
- Running a 358B parameter model across two networked Ryzen AI Halo systems
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
- Configuring RPC workers and launching distributed inference across four nodes
- Running a 1T parameter model across four networked Ryzen AI Halo systems
<!-- @toggle:end -->
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
- Configuring an RPC worker and launching distributed inference across two nodes
- Running a 358B parameter model across two Ryzen AI Halo systems
<!-- @toggle:end -->

## Setting the Memory Configuration

<!-- @toggle:nodes=2 -->
> **Note**: Complete this step on both Machine 1 and Machine 2.
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
> **Note**: Complete this step on all four machines (Machine 1 through Machine 4).
<!-- @toggle:end -->

<!-- @toggle:link=ethernet -->
<!-- @os:windows -->
On Windows, to run larger models that require higher memory, we need to use the AMD Variable Graphics Memory (iGPU VRAM) allocation.

Running a 358B-parameter model across the cluster requires a large GPU memory
allocation, so this step is required here (not optional). Follow the memory
configuration below, and set the allocation on each machine to at least
**96 GB** (Windows: AMD Variable Graphics Memory in Adrenalin; Linux: `amd-ttm --set 120`).

<!-- @device:halo_box -->
<!-- @os:windows -->
> **Running models near or above 128 GB:** On AMD Ryzen™ AI Max 400 Series (Gorgon Halo) systems running Windows, models that approach or exceed 128 GB of memory require additional configuration to run without errors. Follow the [AMD Ryzen AI Max PRO 400 Series Windows OS Guidelines](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines) before loading the model.
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:linux -->
<!-- @toggle:end -->
On Linux, ROCm utilizes a shared system memory pool, and this pool is configured by default to half the system memory.

This amount can be increased by changing the kernel's Translation Table Manager (TTM) page setting, with the following instructions. AMD recommends setting the minimum dedicated VRAM in the BIOS (0.5 GB).

* Install the pipx utility and add the path for pipx installed wheels into the system search path.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Install the amd-debug-tools wheel from PyPI.
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

<!-- @toggle:link=ethernet -->

<!-- @os:end -->
<!-- @toggle:end -->
<!-- @device:halo_box -->
## Check for Software Updates

<!-- @require:software-update -->
<!-- @device:end -->
## Prerequisites

### Hardware

<!-- @toggle:link=ethernet -->
<!-- @toggle:nodes=2 -->
This playbook requires two Ryzen AI Halo units and one Ethernet switch, connected in a star topology with each unit wired directly to the switch.
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
This playbook requires four Ryzen AI Halo units and one Ethernet switch, connected in a star topology with each unit wired directly to the switch.
<!-- @toggle:end -->
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
This playbook requires two Ryzen AI Halo units connected directly to each other with one USB4/Thunderbolt cable.
<!-- @toggle:end -->

<!-- @toggle:link=ethernet -->
<!-- @toggle:nodes=2 -->
| Component | Quantity | Description |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Compute nodes that form the cluster |
| 10Gbps Ethernet switch | 1 | Central switch to allow multi node Ryzen AI Halo communication (at least 2 ports) |
| Ethernet cable | 2 | Connects each Halo unit to the switch (Cat 7 or higher recommended) |
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
| Component | Quantity | Description |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Compute nodes that form the cluster |
| 10Gbps Ethernet switch | 1 | Central switch to allow multi node Ryzen AI Halo communication (at least 4 ports) |
| Ethernet cable | 4 | Connects each Halo unit to the switch (Cat 7 or higher recommended) |
<!-- @toggle:end -->
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
| Component | Quantity | Description |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Compute nodes that form the cluster |
| USB4/Thunderbolt cable | 1 | Connects the two Halo units directly (USB4 40Gbps, Thunderbolt 3, or Thunderbolt 4 certified) |
<!-- @toggle:end -->

<!-- @toggle:link=ethernet -->
<!-- @toggle:nodes=2 -->
> **Note**: Two Ethernet switch ports are required to connect the two Ryzen AI Halo units. A third port is required if you access the model from a separate client machine instead of from one of the Halo units.
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
> **Note**: Four Ethernet switch ports are required to connect the four Ryzen AI Halo units. A fifth port is required if you access the model from a separate client machine instead of from one of the Halo units.
<!-- @toggle:end -->
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
> **Note**: The cable must be rated for 40Gbps data. USB-C charging cables and USB 3.x cables will not establish a network link between the two units.

> **Note**: Each Halo unit should keep its regular Ethernet or Wi-Fi connection for internet access and model downloads. The USB4 link carries only the traffic between the two nodes.
<!-- @toggle:end -->

### Software
<!-- @toggle:link=ethernet -->
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Please install:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) with the **Desktop Development with C++** workload
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->
<!-- @toggle:end -->

<!-- @toggle:link=ethernet -->
<!-- @os:linux -->
<!-- @toggle:end -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @toggle:link=ethernet -->
<!-- @os:end -->
<!-- @toggle:end -->

## Physical Hardware Setup

<!-- @toggle:nodes=2 -->
> **Note**: Complete this step on both Machine 1 and Machine 2.
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
> **Note**: Complete this step on all four machines (Machine 1 through Machine 4).
<!-- @toggle:end -->

<!-- @toggle:link=ethernet -->
Connect each Ryzen AI Halo unit to the Ethernet switch using a Cat 7 (or higher) cable. This establishes the 10Gbps link used for high-speed communication between the nodes.
<!-- @os:linux -->
### 1. Determine Network Interfaces
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
Connect the two Ryzen AI Halo units using the USB4/Thunderbolt cable, plugging each end into a USB4 port. This establishes a direct point-to-point link between the nodes.
<!-- @toggle:end -->

<!-- @toggle:link=ethernet -->
On each machine, find the name of its network interface and note it down (it will be referred to below as `IFNAME`). Run:
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
Over this cable, Linux creates a virtual network interface named `thunderbolt0`, which carries regular network traffic just like an Ethernet port.

### 1. Confirm the Cable Is Detected
<!-- @toggle:end -->

```bash
<!-- @toggle:link=ethernet -->
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
ip -br link show thunderbolt0
<!-- @toggle:end -->
```

<!-- @toggle:link=ethernet -->
This prints the interface name directly, for example:
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
The interface should be `UP`:
<!-- @toggle:end -->

```bash
<!-- @toggle:link=ethernet -->
enp191s0
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
thunderbolt0     UP             02:c6:d6:17:b8:d8 <BROADCAST,MULTICAST,UP,LOWER_UP>
<!-- @toggle:end -->
```

<!-- @toggle:link=ethernet -->
### 2. Verify Network Link Speeds
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
> **Note**: If `thunderbolt0` is missing or not `UP`, check that the cable is seated in a USB4 port on both machines and is rated for 40Gbps data.
<!-- @toggle:end -->

<!-- @toggle:link=ethernet -->
Confirm the link is active and running at full speed by checking the speed of your interface:
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
### 2. Assign Static IP Addresses

NetworkManager brings `thunderbolt0` up automatically, but with a random `169.254.x.x` link-local address that can change between reboots. Assign each machine a fixed address on a private subnet so the controller can always reach the RPC worker. This is a one-time step, and the setting persists across reboots.

On **Machine 1**:
<!-- @toggle:end -->

```bash
<!-- @toggle:link=ethernet -->
sudo ethtool <IFNAME> | grep Speed
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
sudo nmcli con add type ethernet ifname thunderbolt0 con-name usb4-cluster \
  ipv4.method manual ipv4.addresses 10.55.0.1/24 \
  connection.autoconnect-priority 10
sudo nmcli con up usb4-cluster
<!-- @toggle:end -->
```

<!-- @toggle:link=ethernet -->
> **Note**: Replace `<IFNAME>` with the output interface name from [1. Determine Network Interfaces](#1-determine-network-interfaces)

You should see a speed of `10000Mb/s`:
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
On **Machine 2**:
<!-- @toggle:end -->

```bash
<!-- @toggle:link=ethernet -->
	Speed: 10000Mb/s
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
sudo nmcli con add type ethernet ifname thunderbolt0 con-name usb4-cluster \
  ipv4.method manual ipv4.addresses 10.55.0.2/24 \
  connection.autoconnect-priority 10
sudo nmcli con up usb4-cluster
<!-- @toggle:end -->
```

<!-- @toggle:link=ethernet -->
> **Note**: If the speed is lower than `10000Mb/s` or the link does not come up, check the cable connection and confirm the switch port is set to 10Gbps. Some switches require auto-negotiation to be disabled and the link speed set manually; refer to your switch's documentation.
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
| Flag | Purpose |
|------|---------|
| `ifname thunderbolt0` | Binds the connection profile to the USB4 network interface |
| `ipv4.method manual` | Disables automatic addressing in favor of a static address |
| `ipv4.addresses` | Static IP address for this machine on the USB4 link |
| `connection.autoconnect-priority 10` | Takes precedence over NetworkManager's automatic link-local profile, so the static address is applied after every reboot |
<!-- @toggle:end -->

<!-- @toggle:link=ethernet -->
<!-- @os:end -->
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
> **Note**: If your local network already uses the `10.55.0.x` range, choose another private subnet (for example, `10.66.0.x`) and substitute it in the commands throughout this playbook.
<!-- @toggle:end -->

<!-- @toggle:link=ethernet -->
<!-- @os:windows -->
### Verify Network Link Speed
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
Confirm the address was applied:
<!-- @toggle:end -->

<!-- @toggle:link=ethernet -->
On each machine, check the link speed of your network interfaces:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
```bash
ip -br addr show thunderbolt0
<!-- @toggle:end -->
```

<!-- @toggle:link=ethernet -->
Your Ethernet interface should be `Up` and running at `10 Gbps`:
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
You should see `10.55.0.1/24` on Machine 1 and `10.55.0.2/24` on Machine 2.
<!-- @toggle:end -->

<!-- @toggle:link=ethernet -->
```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
### 3. Verify the Connection

From Machine 1, ping Machine 2 over the USB4 link:

```bash
ping -c 3 10.55.0.2
<!-- @toggle:end -->
```

<!-- @toggle:link=ethernet -->
> **Note**: If the speed is lower than `10 Gbps` or the link does not come up, check the cable connection and confirm the switch port is set to 10Gbps. Some switches require auto-negotiation to be disabled and the link speed set manually; refer to your switch's documentation.
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
You should see all packets received:
<!-- @toggle:end -->

<!-- @toggle:link=ethernet -->
<!-- @os:end -->
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
```bash
3 packets transmitted, 3 received, 0% packet loss
```
<!-- @toggle:end -->

## Installing llama.cpp

<!-- @toggle:nodes=2 -->
> **Note**: Complete this step on both Machine 1 and Machine 2.
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
> **Note**: Complete this step on all four machines (Machine 1 through Machine 4).
<!-- @toggle:end -->

Two installation options are available:

- [Option 1: Lemonade SDK (Recommended)](#option-1-lemonade-sdk-recommended) - pre-built binaries, fastest setup
- [Option 2: Manual Source Build](#option-2-manual-source-build) - build from source with full control over build flags

### Option 1: Lemonade SDK (Recommended)

The Lemonade SDK provides nightly builds of llama.cpp with AMD ROCm 7 acceleration, targeting GPUs such as gfx1151 (Strix Halo / Ryzen AI Max+ 395) and other recent Radeon architectures.

<!-- @toggle:link=ethernet -->
<!-- @toggle:nodes=2 -->
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

This directory now contains ROCm-enabled builds of `llama-cli.exe`, `llama-server.exe`, and `rpc-server.exe`, precompiled for your Ryzen AI Halo system.

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
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
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

This directory now contains ROCm-enabled builds of `llama-cli.exe`, `llama-server.exe`, and `ggml-rpc-server.exe`, precompiled for your Ryzen AI Halo system.

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
<!-- @toggle:end -->
<!-- @toggle:end -->
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

This directory now contains ROCm-enabled builds of `llama-cli`, `llama-server`, and `rpc-server`, precompiled for your Ryzen AI Halo system.

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
<!-- @toggle:link=ethernet -->
<!-- @os:end -->
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->

<!-- @toggle:end -->
With llama.cpp prepared on each node, proceed to [Downloading the Model](#downloading-the-model).

### Option 2: Manual Source Build

<!-- @toggle:link=ethernet -->
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
| `-DGPU_TARGETS=gfx1151` | Targets the Ryzen AI Halo GPU (Radeon 8060s) |
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
<!-- @toggle:end -->
#### Step 1: Build llama.cpp

Clone the repository:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Build with ROCm and RPC support:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Build Flag | Purpose |
|-----------|---------|
| `-DGGML_HIP=ON` | Enables the ROCm software stack |
| `-DGGML_RPC=ON` | Enables RPC for distributed inference |
| `-DAMDGPU_TARGETS="gfx1151"` | Targets the Ryzen AI Halo GPU (Radeon 8060s) |

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
<!-- @toggle:link=ethernet -->
<!-- @os:end -->
<!-- @toggle:end -->

## Downloading the Model

<!-- @toggle:nodes=2 -->
This playbook uses [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), a 358B parameter model in the `Q4_K_XL` quantization from [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). At this quantization the model requires approximately 205GB of storage and fits within the combined GPU memory of two Ryzen AI Halo nodes.
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
This playbook uses [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) in the `UD-Q2_K_XL` quantization from [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). This quantization fits within the combined GPU memory of four Ryzen AI Halo nodes.
<!-- @toggle:end -->

Download the GGUF files using the Hugging Face CLI:
<!-- @toggle:link=ethernet -->
<!-- @os:linux -->
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->

<!-- @toggle:end -->
```bash
pip install huggingface-hub
<!-- @toggle:nodes=2 -->
hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
<!-- @toggle:end -->
```
<!-- @toggle:link=ethernet -->
<!-- @toggle:nodes=2 -->
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->
<!-- @toggle:end -->
<!-- @toggle:end -->

<!-- @toggle:nodes=2 -->
> **Note**: The model download must be completed on Machine 1 (the controller). The RPC worker nodes do not need a local copy of the model files.
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
> **Note**: The model download must be completed on Machine 1 (the controller). The RPC worker nodes (Machines 2, 3, and 4) do not need a local copy of the model files.
<!-- @toggle:end -->

## Launching the Model on the Cluster

<!-- @toggle:nodes=2 -->
The llama.cpp RPC (Remote Procedure Call) engine allows a single llama.cpp instance to offload model layers to remote workers over the network. One machine acts as the **controller** (Machine 1), handling tokenization, scheduling, and orchestration. The other machine runs a lightweight **RPC server** (Machine 2) that exposes its GPU memory and compute to the controller.
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
The llama.cpp RPC (Remote Procedure Call) engine allows a single llama.cpp instance to offload model layers to remote workers over the network. One machine acts as the **controller** (Machine 1), handling tokenization, scheduling, and orchestration. The other three machines each run a lightweight **RPC server** (Machines 2, 3, and 4) that expose their GPU memory and compute to the controller.
<!-- @toggle:end -->

<!-- @toggle:link=ethernet -->
<!-- @toggle:nodes=2 -->
At load time, llama.cpp shards the model across both nodes. Once loaded, inference proceeds as if running on a single accelerator. RPC handles tensor transfers and synchronization behind the scenes.
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
At load time, llama.cpp shards the model across all four nodes. Once loaded, inference proceeds as if running on a single accelerator. RPC handles tensor transfers and synchronization behind the scenes.
<!-- @toggle:end -->
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
At load time, llama.cpp shards the model across both nodes. Once loaded, inference proceeds as if running on a single accelerator. RPC handles tensor transfers and synchronization over the USB4 link behind the scenes.
<!-- @toggle:end -->

<!-- @toggle:nodes=2 -->
### Step 1: Start the RPC Server (Machine 2)
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
### Step 1: Start the RPC Servers (Machines 2, 3, and 4)
<!-- @toggle:end -->

<!-- @toggle:link=ethernet -->
<!-- @toggle:nodes=2 -->
On Machine 2, start the RPC server to expose its GPU resources to the controller:
<!-- @os:linux -->
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
On each of Machines 2, 3, and 4, start the RPC server to expose its GPU resources to the controller:
<!-- @os:linux -->
<!-- @toggle:end -->
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
On Machine 2, start the RPC server to expose its GPU resources to the controller:

<!-- @toggle:end -->
```bash
<!-- @toggle:link=ethernet -->
./ggml-rpc-server -p 50053 -c --host 0.0.0.0
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
./ggml-rpc-server -p 50053 -c --host 10.55.0.2
<!-- @toggle:end -->
```
<!-- @toggle:link=ethernet -->
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\ggml-rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->
<!-- @toggle:end -->

<!-- @toggle:link=ethernet -->
| Flag | Purpose |
|------|---------|
| `-p` | Port to broadcast the RPC server on |
| `-c` | Enables a local cache for large tensors, avoiding repeated network transfers during model loading |
| `--host` | IP address to bind the RPC server to (`0.0.0.0` for all interfaces) |
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
| Flag | Purpose |
|------|---------|
| `-p` | Port to broadcast the RPC server on |
| `-c` | Enables a local cache for large tensors, avoiding repeated network transfers during model loading |
| `--host` | IP address to bind the RPC server to (`10.55.0.2`, so the server only accepts connections over the USB4 link) |
<!-- @toggle:end -->

For more options, refer to the [llama.cpp RPC documentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Step 2: Launch the Model (Machine 1)

<!-- @toggle:nodes=2 -->
With the RPC server running on Machine 2, launch inference from Machine 1 using either `llama-cli` or `llama-server`.
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
With the RPC servers running on Machines 2, 3, and 4, launch inference from Machine 1 using either `llama-cli` or `llama-server`.
<!-- @toggle:end -->

#### llama-cli

`llama-cli` provides a terminal-based interface for interacting directly with the model. It is ideal for benchmarking, debugging, and low-level experimentation.

<!-- @toggle:link=ethernet -->
<!-- @os:linux -->
<!-- @toggle:end -->
```bash
./llama-cli \
<!-- @toggle:nodes=2 -->
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
<!-- @toggle:end -->
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
<!-- @toggle:link=ethernet -->
<!-- @toggle:nodes=2 -->
  --rpc <RPC_WORKER_IP>:50053
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
  -b 4096 \
  -ub 4096 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
<!-- @toggle:end -->
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
  --rpc 10.55.0.2:50053
<!-- @toggle:end -->
```
<!-- @toggle:link=ethernet -->
<!-- @toggle:nodes=2 -->

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
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **Finding `<RPC_WORKER_IP>`**: On Machine 2, run `ipconfig | findstr /C:"IPv4"` in Terminal (Powershell) to find its local IP address.

<!-- @os:end -->
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->

> **Finding `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: On each of Machines 2, 3, and 4, run `hostname -I | awk '{print $1}'` to find its local IP address.
<!-- @os:end -->

<!-- @os:windows -->
> **Note**: Run this command in Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **Finding `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: On each of Machines 2, 3, and 4, run `ipconfig | findstr /C:"IPv4"` in Terminal (Powershell) to find its local IP address.

<!-- @os:end -->
<!-- @toggle:end -->
<!-- @toggle:end -->

Once running, `llama-cli` displays model loading progress and enters an interactive prompt where you can chat directly with the model:

<!-- @toggle:nodes=2 -->
![llama-cli running GLM 4.7 across two nodes](assets/llama-cli-example.png)
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
![llama-cli running Kimi K2.6 across four nodes](assets/llama-cli-example.png)
<!-- @toggle:end -->

#### llama-server

`llama-server` exposes the same inference engine through a persistent server process with an integrated web UI and an OpenAI-compatible HTTP API. This is the preferred interface for longer-running deployments, multi-user access, and integration with external tooling.

<!-- @toggle:link=ethernet -->
<!-- @os:linux -->
<!-- @toggle:end -->
```bash
./llama-server \
<!-- @toggle:nodes=2 -->
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
<!-- @toggle:end -->
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
<!-- @toggle:nodes=4 -->
  -b 4096 \
  -ub 4096 \
<!-- @toggle:end -->
  --host 0.0.0.0 \
  --port 8081 \
<!-- @toggle:link=ethernet -->
<!-- @toggle:nodes=2 -->
  --rpc <RPC_WORKER_IP>:50053
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
<!-- @toggle:end -->
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
  --rpc 10.55.0.2:50053
<!-- @toggle:end -->
```
<!-- @toggle:link=ethernet -->
<!-- @toggle:nodes=2 -->

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
  -lm none `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **Finding `<RPC_WORKER_IP>`**: On Machine 2, run `ipconfig | findstr /C:"IPv4"` in Terminal (Powershell) to find its local IP address.
<!-- @os:end -->
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->

> **Finding `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: On each of Machines 2, 3, and 4, run `hostname -I | awk '{print $1}'` to find its local IP address.
<!-- @os:end -->

<!-- @os:windows -->
> **Note**: Run this command in Terminal (Powershell).

```powershell
.\llama-server.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **Finding `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: On each of Machines 2, 3, and 4, run `ipconfig | findstr /C:"IPv4"` in Terminal (Powershell) to find its local IP address.
<!-- @os:end -->
<!-- @toggle:end -->
<!-- @toggle:end -->

Once started, open `http://<HOST_IP>:8081` in your browser to access the built-in web UI. This provides a browser-based chat interface for interacting with the model:

<!-- @toggle:nodes=2 -->
![llama-server web UI running GLM 4.7 across two nodes](assets/llama-server-example.png)
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
![llama-server web UI running Kimi K2.6 across four nodes](assets/llama-server-example.png)
<!-- @toggle:end -->

<!-- @toggle:link=ethernet -->
<!-- @os:linux -->
> **Finding `<HOST_IP>`**: On Machine 1, run `hostname -I | awk '{print $1}'` to find its local IP address.
<!-- @os:end -->

<!-- @os:windows -->
> **Finding `<HOST_IP>`**: On Machine 1, run `ipconfig | findstr /C:"IPv4"` in Terminal (Powershell) to find its local IP address.
<!-- @os:end -->
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
> **Finding `<HOST_IP>`**: On Machine 1 itself, use `localhost`. From another device on your network, use Machine 1's local network IP address, found by running `ip route get 1.1.1.1 | grep -oP 'src \K\S+'` on Machine 1.
<!-- @toggle:end -->

#### Parameter Reference

<!-- @toggle:link=ethernet -->
<!-- @toggle:nodes=2 -->
| Flag | Purpose |
|------|---------|
| `-m` | Path to the GGUF model file (use the first shard, `00001-of-00005`) |
| `-c` | Context size in tokens. Larger values use more memory |
| `-fa on` | Enables rocWMMA Flash Attention for improved performance on AMD GPUs |
| `-ngl 999` | Offloads all model layers to the GPU |
| `-lm none` | Sets the model load mode to `none`, disabling memory-mapping to reduce load times when model size exceeds system RAM but fits in VRAM |
| `--host` | IP to bind `llama-server` to (`llama-server` only) |
| `--port` | Port to serve the HTTP API on (`llama-server` only) |
| `--rpc` | Comma-separated list of RPC worker endpoints (`IP:port`) |
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
| Flag | Purpose |
|------|---------|
| `-m` | Path to the GGUF model file (use the first shard, `00001-of-00008`) |
| `-c` | Context size in tokens. Larger values use more memory |
| `-fa on` | Enables rocWMMA Flash Attention for improved performance on AMD GPUs |
| `-ngl 999` | Offloads all model layers to the GPU |
| `-lm none` | Sets the model load mode to `none`, disabling memory-mapping to reduce load times when model size exceeds system RAM but fits in VRAM |
| `-b` | Logical batch size in tokens. Setting to 4096 balances throughput and memory usage across nodes |
| `-ub` | Physical (micro) batch size for prompt processing. Matching `-b` avoids unnecessary chunking overhead |
| `--host` | IP to bind `llama-server` to (`llama-server` only) |
| `--port` | Port to serve the HTTP API on (`llama-server` only) |
| `--rpc` | Comma-separated list of RPC worker endpoints (`IP:port`) |
<!-- @toggle:end -->
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
| Flag | Purpose |
|------|---------|
| `-m` | Path to the GGUF model file (use the first shard, `00001-of-00005`) |
| `-c` | Context size in tokens. Larger values use more memory |
| `-fa on` | Enables rocWMMA Flash Attention for improved performance on AMD GPUs |
| `-ngl 999` | Offloads all model layers to the GPU |
| `-lm none` | Sets the model load mode to `none`, disabling memory-mapping to reduce load times when model size exceeds system RAM but fits in VRAM |
| `--host` | IP to bind `llama-server` to (`llama-server` only) |
| `--port` | Port to serve the HTTP API on (`llama-server` only) |
| `--rpc` | Comma-separated list of RPC worker endpoints (`IP:port`), here the USB4 link address of Machine 2 |
<!-- @toggle:end -->

For full parameter usage, refer to the [llama-cli documentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) and [llama-server documentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Next Steps

- **Connect third-party applications**: `llama-server` exposes an OpenAI-compatible API. Point any OpenAI-compatible application (such as Open WebUI) at `http://<HOST_IP>:8081` with any placeholder API key (e.g., `none`) to connect to your cluster
- **Explore other models**: Browse quantized GGUFs on [Hugging Face](https://huggingface.co/models?search=gguf) to find models that fit within your cluster's combined GPU memory
<!-- @toggle:link=ethernet -->
<!-- @toggle:nodes=2 -->
- **Scale to four nodes**: Add two more Ryzen AI Halo systems as additional RPC workers to access models at the 1 trillion parameter scale. Pass additional endpoints to `--rpc` as a comma-separated list (e.g., `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)
<!-- @toggle:end -->
<!-- @toggle:nodes=4 -->
- **Scale beyond four nodes**: Add further Ryzen AI Halo systems as additional RPC workers to access models beyond the 1 trillion parameter scale. Pass additional endpoints to `--rpc` as a comma-separated list (e.g., `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)
<!-- @toggle:end -->
<!-- @toggle:end -->
<!-- @toggle:link=usb4 -->
- **Scale to four nodes**: A USB4 cable links exactly two machines. To cluster four Ryzen AI Halo systems and access models at the 1 trillion parameter scale, follow the four-node RPC clustering playbook, which connects the nodes through a 10Gbps Ethernet switch

<!-- @toggle:end -->
