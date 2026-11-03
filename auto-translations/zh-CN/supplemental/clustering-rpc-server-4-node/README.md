<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **机器翻译。**本页面由英文自动翻译，未经人工审核。其中可能包含错误，某些说明、命令、下载内容、产品可用性或其他内容可能因语言或地区而异。如内容存在任何不一致或差异，应以英文原版 playbook 为准。
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# 使用 RPC 集群部署四台 Ryzen™ AI Halo

## 概述

您的 Ryzen™ AI Halo 已经能够在本地运行大语言模型。而集群化则更进一步，通过局域网将多台系统的 GPU 内存组合在一起，使您能够访问更大的模型，获得更强的推理能力、更出色的代码生成能力和更深入的多语言理解能力——这一切完全基于您自己的硬件。

本指南将教您如何使用 llama.cpp 的 RPC 引擎集群化四台 Ryzen AI Halo 系统，并借助 AMD ROCm™ 加速在全部四台机器上运行 Kimi K2.6（一个大型混合专家模型）。

## 您将学到的内容

- 如何在 Ryzen AI Halo 系统上扩展 VRAM 分配
- 安装支持 ROCm 和 RPC 的 llama.cpp
- 配置 RPC 工作节点并在四个节点上启动分布式推理
- 在四台联网的 Ryzen AI Halo 系统上运行一个 1T 参数的模型

## 设置内存配置

> **注意**：请在**全部四台机器（机器 1 至机器 4）**上完成此步骤。

在集群上运行一个 1T 参数的模型需要较大的 GPU 内存分配，因此此步骤是必需的（非可选项）。请按照下方的内存配置说明，将每台机器的分配量设置为至少 **96 GB**（Windows 系统：在 Adrenalin 中设置 AMD Variable Graphics Memory；Linux 系统：`amd-ttm --set 120`）。

<!-- @device:halo_box -->
<!-- @os:windows -->
> **运行接近或超过 128 GB 的模型：** 在运行 Windows 的 AMD Ryzen™ AI Max 400 系列（Gorgon Halo）系统上，接近或超过 128 GB 内存的模型需要额外的配置才能正常运行而不出错。请在加载模型之前，先按照 [AMD Ryzen AI Max PRO 400 系列 Windows 操作系统指南](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines) 进行操作。
<!-- @os:end -->
<!-- @device:end -->

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 检查软件更新

<!-- @require:software-update -->
<!-- @device:end -->
## 先决条件

### 硬件

本指南需要四台 Ryzen AI Halo 设备和一台以太网交换机，以星型拓扑结构连接，每台设备均直接接入交换机。

| 组件 | 数量 | 说明 |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | 构成集群的计算节点 |
| 10Gbps 以太网交换机 | 1 | 用于支持多节点 Ryzen AI Halo 通信的中央交换机（至少 4 个端口） |
| 以太网线缆 | 4 | 将每台 Halo 设备连接到交换机（建议使用 Cat 7 或更高规格） |

> **注意**：连接四台 Ryzen AI Halo 设备需要四个以太网交换机端口。如果您从单独的客户端机器而非某台 Halo 设备访问模型，则还需要第五个端口。

### 软件
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
请安装：
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe)，并选择 **Desktop Development with C++** 工作负载
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## 物理硬件设置

> **注意**：请在全部四台机器（机器 1 至机器 4）上完成此步骤。

使用 Cat 7（或更高规格）线缆将每台 Ryzen AI Halo 设备连接到以太网交换机。这将建立用于节点间高速通信的 10Gbps 链路。
<!-- @os:linux -->
### 1. 确定网络接口

在每台机器上，找到其网络接口的名称并记录下来（下文将称之为 `IFNAME`）。运行：

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

这将直接输出接口名称，例如：

```bash
enp191s0
```

### 2. 验证网络链路速度

通过检查接口速度来确认链路处于活动状态并以全速运行：

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注意**：请将 `<IFNAME>` 替换为 [1. 确定网络接口](#1-确定网络接口) 中输出的接口名称

您应当看到速度为 `10000Mb/s`：

```bash
	Speed: 10000Mb/s
```

> **注意**：如果速度低于 `10000Mb/s` 或链路未建立，请检查线缆连接，并确认交换机端口已设置为 10Gbps。部分交换机需要禁用自动协商并手动设置链路速度，请参阅您的交换机文档。

<!-- @os:end -->

<!-- @os:windows -->
### 验证网络链路速度

在每台机器上，检查其网络接口的链路速度：

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

您的以太网接口应显示为 `Up` 状态，并以 `10 Gbps` 速度运行：

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **注意**：如果速度低于 `10 Gbps` 或链路未建立，请检查线缆连接，并确认交换机端口已设置为 10Gbps。部分交换机需要禁用自动协商并手动设置链路速度，请参阅您的交换机文档。

<!-- @os:end -->

## 安装 llama.cpp

> **注意**：请在全部四台机器（机器 1 至机器 4）上完成此步骤。

可选择以下两种安装方式：

- [方式一：Lemonade SDK（推荐）](#option-1-lemonade-sdk-recommended) - 预编译二进制文件，设置速度最快
- [方式二：手动源码构建](#option-2-manual-source-build) - 从源码构建，可完全控制构建标志

### 方式一：Lemonade SDK（推荐）

Lemonade SDK 提供了带有 AMD ROCm 7 加速的 llama.cpp 每日构建版本，适用于 gfx1151（Strix Halo / Ryzen AI Max+ 395）等 GPU 以及其他较新的 Radeon 架构。

<!-- @os:windows -->
#### 步骤 1：下载预编译二进制文件

前往最新版本发布页面，下载与您的平台和 GPU 目标匹配的压缩包：

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

下载名为 `llama-bxxxx-windows-rocm-gfx1151-x64.zip` 的文件（其中 `xxxx` 为构建编号）。

#### 步骤 2：解压二进制文件

解压下载的压缩包：

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

该目录现在包含了针对您的 Ryzen AI Halo 系统预编译的、支持 ROCm 的 `llama-cli.exe`、`llama-server.exe` 和 `ggml-rpc-server.exe` 构建版本。

#### 步骤 3：验证 GPU 检测

```bash
.\llama-cli.exe --list-devices
```

预期输出：

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### 步骤 1：下载预编译二进制文件

访问最新版本发布页面，下载与您的平台和 GPU 目标匹配的压缩包：

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

下载名为 `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` 的文件（其中 `xxxx` 为构建版本号）。

#### 步骤 2：解压并准备二进制文件

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

此目录现在包含为您的 Ryzen AI Halo 系统预编译的、支持 ROCm 的 `llama-cli`、`llama-server` 和 `rpc-server` 构建版本。

#### 步骤 3：验证 GPU 检测情况

```bash
./llama-cli --list-devices
```

预期输出：

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
在每个节点上准备好 llama.cpp 后，继续进行[下载模型](#downloading-the-model)。

### 方式二：手动源码构建

<!-- @os:windows -->
#### 步骤 1：构建 llama.cpp

打开 **x64 Native Tools Command Prompt**（随 Visual Studio Build Tools 一起安装），然后克隆仓库：

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

将 HIP 添加到您的路径中，并启用 ROCm 和 RPC 支持进行构建：

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| 构建标志 | 用途 |
|-----------|---------|
| `-DGGML_HIP=ON` | 启用 ROCm/HIP 软件栈 |
| `-DGGML_RPC=ON` | 启用分布式推理的 RPC 支持 |
| `-DGPU_TARGETS=gfx1151` | 面向 Ryzen AI Halo GPU（Radeon 8060s） |
| `-G Ninja` | 使用 Ninja 构建系统 |

#### 步骤 2：验证 GPU 检测情况

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

预期输出：

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### 步骤 3：将 HIP 添加到用户路径中

上述构建步骤仅为当前会话设置了 `%HIP_PATH%\bin`。为使 HIP 库在任意终端（而不仅是 x64 Native Tools Command Prompt）中都可用，请将其永久添加到您的用户 `PATH` 中：

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

在每个节点上准备好 llama.cpp 后，继续进行[下载模型](#downloading-the-model)。
<!-- @os:end -->

<!-- @os:linux -->
#### 步骤 1：构建 llama.cpp

克隆仓库：

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

启用 ROCm 和 RPC 支持进行构建：

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| 构建标志 | 用途 |
|-----------|---------|
| `-DGGML_HIP=ON` | 启用 ROCm 软件栈 |
| `-DGGML_RPC=ON` | 启用分布式推理的 RPC 支持 |
| `-DAMDGPU_TARGETS="gfx1151"` | 面向 Ryzen AI Halo GPU（Radeon 8060s） |

有关更多构建选项，请参阅 [llama.cpp 构建文档](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)。

#### 步骤 2：验证 GPU 检测情况

```bash
cd rocm/bin
./llama-cli --list-devices
```

预期输出：

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

在每个节点上准备好 llama.cpp 后，继续进行[下载模型](#downloading-the-model)。
<!-- @os:end -->

## 下载模型

本实践手册使用 [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL) 提供的 `UD-Q2_K_XL` 量化版本的 [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6)。该量化版本可容纳于四个 Ryzen AI Halo 节点的合计 GPU 内存之内。

使用 Hugging Face CLI 下载 GGUF 文件：
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

> **注意**：模型下载必须在机器 1（控制器）上完成。RPC 工作节点（机器 2、3 和 4）无需在本地保留一份模型文件副本。

## 在集群上启动模型

llama.cpp 的 RPC（远程过程调用）引擎允许单个 llama.cpp 实例将模型层卸载到网络上的远程工作节点。一台机器充当**控制器**（机器 1），负责分词、调度和编排。其余三台机器各自运行一个轻量级的 **RPC 服务器**（机器 2、3 和 4），将其 GPU 内存和计算能力暴露给控制器。

在加载时，llama.cpp 会将模型分片到所有四个节点上。加载完成后，推理过程如同在单个加速器上运行一样进行。RPC 在幕后负责处理张量传输和同步。

### 步骤 1：启动 RPC 服务器（机器 2、3 和 4）

在机器 2、3 和 4 上，分别启动 RPC 服务器，以将其 GPU 资源暴露给控制器：
<!-- @os:linux -->
```bash
./ggml-rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\ggml-rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| 标志 | 用途 |
|------|---------|
| `-p` | 用于广播 RPC 服务器的端口 |
| `-c` | 为大型张量启用本地缓存，避免在模型加载期间重复进行网络传输 |
| `--host` | 绑定 RPC 服务器的 IP 地址（`0.0.0.0` 表示所有接口） |

更多选项请参阅 [llama.cpp RPC 文档](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md)。

### 步骤 2：启动模型（机器 1）

在机器 2、3 和 4 上运行 RPC 服务器后，从机器 1 使用 `llama-cli` 或 `llama-server` 启动推理。

#### llama-cli

`llama-cli` 提供了基于终端的界面，可直接与模型交互。它非常适合用于基准测试、调试和底层实验。

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **查找 `<RPC_WORKER_2_IP>`、`<RPC_WORKER_3_IP>`、`<RPC_WORKER_4_IP>`**：在机器 2、3 和 4 上分别运行 `hostname -I | awk '{print $1}'` 以查找其本地 IP 地址。
<!-- @os:end -->

<!-- @os:windows -->
> **注意**：请在终端（Powershell）中运行此命令。

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

> **查找 `<RPC_WORKER_2_IP>`、`<RPC_WORKER_3_IP>`、`<RPC_WORKER_4_IP>`**：在机器 2、3 和 4 上，在终端（Powershell）中分别运行 `ipconfig | findstr /C:"IPv4"` 以查找其本地 IP 地址。

<!-- @os:end -->

启动后，`llama-cli` 会显示模型加载进度，并进入一个交互式提示界面，您可以在其中直接与模型对话：

![llama-cli 在四个节点上运行 Kimi K2.6](assets/llama-cli-example.png)
#### llama-server

`llama-server` 通过一个持久化的服务器进程来提供相同的推理引擎，该进程集成了 Web UI 和与 OpenAI 兼容的 HTTP API。对于运行时间较长的部署、多用户访问以及与外部工具集成而言，这是首选的接口。

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **查找 `<RPC_WORKER_2_IP>`、`<RPC_WORKER_3_IP>`、`<RPC_WORKER_4_IP>`**：在机器 2、3 和 4 上分别运行 `hostname -I | awk '{print $1}'` 以查找其本地 IP 地址。
<!-- @os:end -->

<!-- @os:windows -->
> **注意**：在终端（Powershell）中运行此命令。

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

> **查找 `<RPC_WORKER_2_IP>`、`<RPC_WORKER_3_IP>`、`<RPC_WORKER_4_IP>`**：在机器 2、3 和 4 上分别在终端（Powershell）中运行 `ipconfig | findstr /C:"IPv4"` 以查找其本地 IP 地址。
<!-- @os:end -->

启动后，在浏览器中打开 `http://<HOST_IP>:8081` 即可访问内置的 Web UI。该界面提供了一个基于浏览器的聊天界面，用于与模型进行交互：

![在四个节点上运行 Kimi K2.6 的 llama-server Web UI](assets/llama-server-example.png)

<!-- @os:linux -->
> **查找 `<HOST_IP>`**：在机器 1 上运行 `hostname -I | awk '{print $1}'` 以查找其本地 IP 地址。
<!-- @os:end -->

<!-- @os:windows -->
> **查找 `<HOST_IP>`**：在机器 1 上在终端（Powershell）中运行 `ipconfig | findstr /C:"IPv4"` 以查找其本地 IP 地址。
<!-- @os:end -->

#### 参数参考

| 标志 | 用途 |
|------|---------|
| `-m` | GGUF 模型文件的路径（使用第一个分片，`00001-of-00008`） |
| `-c` | 以 token 为单位的上下文大小。值越大，占用的内存越多 |
| `-fa on` | 启用 rocWMMA Flash Attention，以提升 AMD GPU 上的性能 |
| `-ngl 999` | 将所有模型层卸载到 GPU |
| `-lm none` | 将模型加载模式设置为 `none`，当模型大小超过系统内存但可容纳于显存时，禁用内存映射以缩短加载时间 |
| `-b` | 以 token 为单位的逻辑批次大小。设置为 4096 可在各节点之间平衡吞吐量和内存使用 |
| `-ub` | 用于提示处理的物理（微）批次大小。使其与 `-b` 保持一致可避免不必要的分块开销 |
| `--host` | 用于绑定 `llama-server` 的 IP（仅 `llama-server`） |
| `--port` | 用于提供 HTTP API 服务的端口（仅 `llama-server`） |
| `--rpc` | 以逗号分隔的 RPC 工作节点端点列表（`IP:port`） |

有关完整的参数使用说明，请参阅 [llama-cli 文档](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) 和 [llama-server 文档](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)。

## 后续步骤

- **连接第三方应用程序**：`llama-server` 公开了一个与 OpenAI 兼容的 API。将任何与 OpenAI 兼容的应用程序（例如 Open WebUI）指向 `http://<HOST_IP>:8081`，并使用任意占位符 API 密钥（例如 `none`），即可连接到你的集群
- **探索其他模型**：在 [Hugging Face](https://huggingface.co/models?search=gguf) 上浏览量化后的 GGUF 模型，以找到适合你集群综合 GPU 显存容量的模型
- **扩展至四个节点以上**：添加更多 Ryzen AI Halo 系统作为额外的 RPC 工作节点，以访问超过万亿参数规模的模型。将其他端点以逗号分隔的列表形式传递给 `--rpc`（例如 `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`）