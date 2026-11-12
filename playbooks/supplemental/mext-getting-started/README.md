<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Overview

An AMD Ryzen™ AI Max+ system can hold a lot of model, but not every model. DeepSeek-Coder-V2 at 236B parameters is about 132 GB of weights before you add a single token of context, so on a typical configuration it does not fit, and the load fails.

AMD MEXT Predictive Memory™ changes that. It uses an NVMe SSD as a second tier of system memory and runs an AI engine that predicts which pages the application is about to touch, pulling them back into DRAM before the request arrives. The operating system simply reports more memory than the system physically has.

In this playbook you will roughly double your usable system memory, then load and talk to a 236B-parameter model with llama.cpp on the integrated GPU.

## What You'll Learn

- How MEXT presents flash as an extra tier of system memory
- Where a large model's weights actually live on a unified-memory system: GPU, DRAM, and flash
- How to size the GPU's shared memory pool for a model that does not fit in DRAM
- How to run llama.cpp so that MEXT can do its job, and the one flag that decides whether the model loads at all
- How to read the memory split back out of the system and confirm what happened

## Before You Start

> [!IMPORTANT]
> **The MEXT software bundle is provided by your AMD MEXT representative.** It is not a public download. Everything in this playbook after the bundle is in your hands is reproducible, but you need the bundle first.

Check these before you spend time on the rest:

| Requirement | Why |
|---|---|
| **A second, unused NVMe SSD** | MEXT takes exclusive control of a native NVMe device. It must be unmounted and hold no data you care about. |
| **Drive capacity** | At least 1.75x the MEXT memory you want, 2x or more recommended. For 128 GB of MEXT memory, that is a 256 GB+ drive. |
| **64 GB+ of DRAM** | A documented MEXT requirement. This playbook assumes 128 GB. |
| **Secure Boot disabled** | MEXT loads a kernel module, and Secure Boot may block it. |
| **No swap devices configured** | MEXT requires that no disk swap is configured on the system. |
| **~150 GB free on the OS drive** | For the model file, separate from the MEXT drive. |
| **Root access** | Needed for installation and configuration, though not for ongoing use. |

Supported Linux releases and their minimum kernels are listed in the [AMD MEXT Predictive Memory Installation Guide](https://www.amd.com/content/dam/amd/en/documents/mext-docs/installation-guide.pdf). Ubuntu 22.04, 24.04 and 26.04 are all covered.

> [!NOTE]
> The processors named in the published MEXT system requirements are AMD EPYC™ 7003 Series and AMD Ryzen™ Threadripper™ 5000 Series or newer. Ryzen AI Max+ is not on that list, so treat this combination as an evaluation configuration and confirm support with your AMD MEXT representative before relying on it.

## How MEXT Changes the Memory Picture

It helps to know where the bytes go before you start moving them around.

On a Ryzen AI Max+ system the GPU has almost no memory of its own. The BIOS carves out a small amount of dedicated VRAM, and everything else the GPU uses is ordinary system RAM mapped into the GPU through a mechanism called **GTT** (Graphics Translation Table). The practical consequence: **GPU memory and CPU memory are the same pool.** Giving 100 GB to the GPU takes 100 GB away from everything else.

MEXT adds a tier underneath that pool:

```text
         Without MEXT                      With MEXT
  ┌───────────────────────────┐   ┌───────────────────────────┐
  │   DRAM            128 GB  │   │   DRAM            128 GB  │
  │   ├─ GPU (GTT)            │   │   ├─ GPU (GTT)            │
  │   └─ everything else      │   │   └─ everything else      │
  └───────────────────────────┘   ├───────────────────────────┤
          total: 128 GB           │   MEXT on NVMe    128 GB  │
                                  └───────────────────────────┘
                                          total: ~250 GB
```

Two rules follow from this picture, and they drive every step below:

1. **Memory the GPU has mapped cannot move to flash.** It is pinned in DRAM for as long as the GPU holds it. The more you give the GPU, the less room MEXT has to work in.
2. **MEXT can only tier ordinary application memory.** If an application hands its memory to the GPU driver instead of keeping it as ordinary memory, MEXT is locked out of it.

Rule 2 is the one that decides whether this playbook works, and we come back to it when we run the model.

<!-- @os:linux -->

## Preparing the System

<!-- @require:driver -->

First, confirm there is no swap configured. MEXT requires this:

```bash
swapon --show
```

The command should print nothing. If it lists anything, disable it and remove the entry from `/etc/fstab` so it stays off across reboots:

```bash
sudo swapoff -a
```

Now identify the NVMe device you are dedicating to MEXT, and make sure it is the one you think it is:

```bash
lsblk -d -o NAME,SIZE,MODEL,TRAN
```

```bash
lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINTS /dev/nvme1n1
```

> [!WARNING]
> The drive you hand to MEXT is taken over completely. Confirm it is unmounted, holds nothing you need, and is **not** the drive your operating system boots from before you continue.

## Installing AMD MEXT Predictive Memory

Upload the bundle your AMD MEXT representative provided, then unpack and install it. The installer compiles a kernel module that matches your running kernel, so install it on the kernel you intend to boot.

```bash
tar -xvf mext-v<version>.tgz
```

```bash
cd mext-v<version>
```

Read the license agreement and the bundle's own README before installing:

```bash
less MEXT_EULA-*.txt
```

```bash
less README.txt
```

Then run the interactive installer, which prompts you through the remaining choices, including which NVMe device to use:

```bash
sudo ./install.sh
```

If you need an unattended install for a fleet, the installer documents its own options:

```bash
sudo ./install.sh -h
```

Reboot if the installer asks you to, then confirm the daemon is running:

```bash
systemctl is-active mextd
```

<!-- @test:id=mext-active timeout=60 -->
```bash
systemctl is-active mextd
```
<!-- @test:end -->

You should see `active`. By default MEXT adds memory equal to 20% of DRAM, which you can see immediately:

```bash
free -h
```

## Allocating MEXT Memory

The 20% default is deliberately conservative. For a model this size you want the largest second tier the drive supports, so set MEXT memory to 100% of DRAM, which roughly doubles the system total:

```bash
sudo mext-config --set-config mextMemory=100%
```

The value also accepts an absolute size, for example `mextMemory=128G`. Changing it requires a reboot:

```bash
sudo reboot
```

After the reboot, read back what MEXT actually provisioned:

```bash
/opt/mext/bin/mext_status.sh
```

<!-- @test:id=mext-status timeout=60 -->
```bash
/opt/mext/bin/mext_status.sh
```
<!-- @test:end -->

The summary reports the two tiers separately, with MEXT memory roughly matching the DRAM figure:

```text
Total System Memory:              <DRAM + MEXT>
|
+----->       Memory from DRAM:   <physical DRAM>
+-----> MEXT Predictive Memory:   <added by MEXT> (mextMemory=100%)
```

`free -h` now agrees, reporting a total close to twice the installed DRAM. Nothing else on the system needs to know that half of it is flash.

If you want to exercise the new tier before trusting it with a model, the bundle ships a sample workload:

```bash
/opt/mext/bin/mext_stress.sh
```

## Giving the GPU a Larger Shared Memory Pool

The model's GPU-resident portion, plus its context cache, needs roughly 100 GB of GPU-visible memory. The default GTT pool is half of DRAM, which is not enough, so raise it.

<!-- @require:memory-config -->

For this playbook, set the pool to 100 GB and reboot:

```bash
amd-ttm --set 100
```

```bash
sudo reboot
```

Confirm the pool after the reboot:

```bash
amd-ttm
```

<!-- @test:id=gtt-size timeout=60 -->
```bash
awk '{printf "GTT total: %.1f GiB\n", $1/1073741824}' /sys/class/drm/card0/device/mem_info_gtt_total
```
<!-- @test:end -->

> [!NOTE]
> GTT is a ceiling, not a reservation. Setting it to 100 GB does not consume 100 GB; it permits the GPU to map up to that much system memory when a workload asks for it.

## Installing llama.cpp for AMD GPUs

The [llamacpp-rocm](https://github.com/lemonade-sdk/llamacpp-rocm) project publishes llama.cpp builds for AMD GPUs with the AMD ROCm™ software libraries bundled in, so there is nothing else to install and no system ROCm installation to match. Pick the build for your GPU architecture; Ryzen AI Max+ is `gfx1151`.

```bash
mkdir -p ~/llamacpp-rocm && cd ~/llamacpp-rocm
```

```bash
curl -fsSLO https://github.com/lemonade-sdk/llamacpp-rocm/releases/download/b1364/llama-b1364-ubuntu-rocm-gfx1151-x64.zip
```

```bash
unzip -q -o llama-b1364-ubuntu-rocm-gfx1151-x64.zip && chmod +x llama-server llama-cli
```

Confirm the binary runs and finds the GPU:

```bash
./llama-server --list-devices
```

<!-- @test:id=llamacpp-devices timeout=120 -->
```bash
cd ~/llamacpp-rocm && ./llama-server --list-devices
```
<!-- @test:end -->

You should see your integrated GPU listed, reporting memory close to the GTT pool you configured:

```text
Available devices:
  ROCm0: <your GPU> (<~GTT pool> MiB, <~free> MiB free)
```

## Downloading the Model

<!-- @require:ollama -->

We use Ollama purely as a convenient way to fetch a known-good GGUF file. The model is served by llama.cpp, not by Ollama, because we need command-line control over how the weights are placed in memory.

```bash
ollama pull deepseek-coder-v2:236b
```

This is a 132 GB download and takes a while. When it finishes, resolve the path to the GGUF file it stored:

```bash
ollama show --modelfile deepseek-coder-v2:236b | grep '^FROM' | awk '{print $2}'
```

Save that path, since the next step needs it:

```bash
MODEL=$(ollama show --modelfile deepseek-coder-v2:236b | grep '^FROM' | awk '{print $2}')
```

If your user account cannot read the file, add yourself to the `ollama` group and open a new shell:

```bash
sudo usermod -aG ollama "$USER"
```

## Running a 236B Model

This is the payoff. Start the server:

```bash
cd ~/llamacpp-rocm
```

```bash
./llama-server -m "$MODEL" -c 16384 --load-mode dio --no-host --port 8080
```

Three flags are doing real work here:

| Flag | What it does |
|---|---|
| `-c 16384` | Sets a 16K context window. This model stores its attention cache uncompressed at roughly 4.7 MiB per token, so 16K costs 75 GB. Leaving the context at the model's maximum would ask for hundreds of GB and fail immediately. |
| `--load-mode dio` | Reads the weights straight from the SSD into their destination buffers, skipping the kernel's page cache so no second copy competes for DRAM. |
| `--no-host` | Keeps the CPU-side weights in ordinary memory instead of GPU-registered memory. **Without this the model never loads.** |

Loading takes several minutes, and varies with your SSD and system configuration. Watch for the line that tells you the server is up:

```text
srv  server_on_li: listening on http://127.0.0.1:8080
```

Now ask it something:

```bash
curl -s http://127.0.0.1:8080/completion \
  -d '{"prompt":"Write a Python function that reverses a linked list.","n_predict":64}'
```

A 236B-parameter model is answering you on a desktop that does not have enough DRAM to hold it.

## Where the Memory Actually Went

While the model is loaded, look at the system:

```bash
free -g
```

```bash
/opt/mext/bin/mext_status.sh
```

Total memory in use settles well beyond the DRAM the system physically has, which is the whole point: without MEXT there would be nowhere for the excess to go. The server's own startup log breaks down where the model went. Expect approximate figures along these lines, with the exact split depending on your GTT setting and the build of llama.cpp:

| Buffer | Approximate size | Lives in |
|---|---|---|
| GPU model buffer | ~20 GB | GPU, mapped through GTT |
| KV (context) cache | ~75 GB | GPU, mapped through GTT |
| GPU compute buffer | ~5 GB | GPU, mapped through GTT |
| CPU-side model buffer | ~105 GB | Ordinary memory, tiered by MEXT between DRAM and flash |

The GPU side adds up to roughly 100 GB, which is why the GTT pool was sized the way it was. The remaining expert weights sit in ordinary memory, which is exactly the memory MEXT is able to move between DRAM and the SSD. There is not enough DRAM to hold all of it, so MEXT keeps the hot pages resident and the cold pages on flash, and predicts its way between them.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| Load stalls at roughly the size of DRAM, one core at 100% | `--no-host` is missing. Without it the CPU-side weights go into GPU-registered memory, which is pinned and cannot be tiered to flash, leaving MEXT nothing to move. |
| Load fails immediately asking for hundreds of GB | The context is too large. Pass `-c 16384` explicitly rather than letting the model's maximum apply. |
| `mextd` is not `active` after a reboot | Check `systemctl status mextd`. The most common cause is the MEXT NVMe device not being present yet; confirm it appears in `lsblk`. Drives in hot-pluggable or external enclosures can enumerate after the service has already tried to start. |
| `mextd` fails after a kernel update | The MEXT driver is built per kernel. Reboot into the kernel MEXT was installed against, or reinstall the bundle on the new kernel. |
| Kernel module refuses to load | Confirm Secure Boot is disabled, as the published requirements call for. |
| GPU not listed by `--list-devices` | Confirm the GPU driver is installed and that your user is in the `render` and `video` groups. |

> [!NOTE]
> Stopping `mextd` on a running system is not permitted: to the operating system it looks like pulling out a memory module. To turn MEXT off, disable the service and reboot.

<!-- @os:end -->

## Next Steps

- **Trade context for speed.** Halving the context to `-c 8192` frees roughly 37 GB and keeps more of the model GPU-resident, at the cost of a shorter conversation window. Find the balance your workload needs.
- **Try a model that nearly fits.** A model in the 70B to 120B range leaves most of itself in DRAM and shows what MEXT does when flash is the exception rather than the rule.
- **Put a chat interface in front of it.** The server speaks the OpenAI API on port 8080, so [Open WebUI](open-webui-chat) and similar front ends connect directly.
- **Measure the tier.** Run `/opt/mext/bin/mext_stress.sh` and compare against your workload to understand where prediction helps and where it cannot.
- **Read the official documentation.** The [AMD MEXT Predictive Memory Installation Guide](https://www.amd.com/content/dam/amd/en/documents/mext-docs/installation-guide.pdf) covers the full requirements matrix, deployment options, and service management.
