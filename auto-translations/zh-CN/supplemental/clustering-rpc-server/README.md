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

# 使用 RPC 对两台 Ryzen™ AI Halo 进行集群组网

## 概述

您的 Ryzen™ AI Halo 已经能够在本地运行大语言模型。而集群组网可以更进一步，通过本地网络合并多台系统的 GPU 内存，让您能够运行更大的模型，获得更强的推理能力、更出色的代码生成能力以及更深入的多语言理解能力——这一切都完全在您自己的硬件上完成。

本操作手册将教您如何使用 llama.cpp 的 RPC 引擎对两台 Ryzen AI Halo 系统进行集群组网，并借助 AMD ROCm™ 加速，在这两台机器上运行 GLM 4.7（一款拥有 358B 参数的模型）。

## 您将学到

- 如何在 Ryzen AI Halo 系统上扩展 VRAM 分配
- 安装具备 ROCm 和 RPC 支持的 llama.cpp
- 配置 RPC 工作节点并在两个节点间启动分布式推理
- 在两台联网的 Ryzen AI Halo 系统上运行一个 358B 参数的模型

## 设置内存配置

> **注意**：请在 **Machine 1 和 Machine 2** 上都完成此步骤。

在集群上运行一个 358B 参数的模型需要较大的 GPU 内存分配，因此此步骤在这里是必需的（而非可选）。请按照下面的内存配置进行设置，并将每台机器的分配量设置为至少 **96 GB**（Windows：在 Adrenalin 中设置 AMD Variable Graphics Memory；Linux：`amd-ttm --set 120`）。

<!-- @device:halo_box -->
<!-- @os:windows -->
> **运行接近或超过 128 GB 的模型**：在运行 Windows 的 AMD Ryzen™ AI Max 400 系列（Gorgon Halo）系统上，内存占用接近或超过 128 GB 的模型在加载前需要额外的配置才能避免出错。请在加载模型之前，遵循 [AMD Ryzen AI Max PRO 400 系列 Windows 操作系统指南](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines)进行配置。
<!-- @os:end -->
<!-- @device:end -->

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## 检查软件更新

<!-- @require:software-update -->
<!-- @device:end -->
## 前提条件

### 硬件

本操作手册需要两台 Ryzen AI Halo 设备和一台以太网交换机，以星型拓扑结构连接，每台设备直接通过网线连接至交换机。

| 组件 | 数量 | 说明 |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | 组成集群的计算节点 |
| 10Gbps 以太网交换机 | 1 | 用于支持多节点 Ryzen AI Halo 通信的中央交换机（至少需要 2 个端口） |
| 以太网线 | 2 | 将每台 Halo 设备连接至交换机（建议使用 Cat 7 或更高规格） |

> **注意**：连接两台 Ryzen AI Halo 设备需要两个以太网交换机端口。如果您从单独的客户端机器而非某台 Halo 设备访问模型，则还需要第三个端口。

### 软件
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
请安装：
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe)（需包含**使用 C++ 的桌面开发**工作负载）
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## 物理硬件设置

> **注意**：请在 Machine 1 和 Machine 2 上都完成此步骤。

使用 Cat 7（或更高规格）网线将每台 Ryzen AI Halo 设备连接到以太网交换机。这将建立起节点之间用于高速通信的 10Gbps 链路。
<!-- @os:linux -->
### 1. 确定网络接口

在每台机器上，找到其网络接口名称并记录下来（下文将以 `IFNAME` 表示）。运行：

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

这会直接打印出接口名称，例如：

```bash
enp191s0
```

### 2. 验证网络链路速率

通过检查您的接口速率，确认链路处于活动状态且以满速运行：

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注意**：请将 `<IFNAME>` 替换为 [1. 确定网络接口](#1-determine-network-interfaces) 中输出的接口名称

您应当会看到 `10000Mb/s` 的速率：

```bash
	Speed: 10000Mb/s
```

> **注意**：如果速率低于 `10000Mb/s` 或链路未能建立，请检查网线连接，并确认交换机端口已设置为 10Gbps。有些交换机需要先禁用自动协商功能并手动设置链路速率；请参阅您所使用交换机的相关文档。

<!-- @os:end -->

<!-- @os:windows -->
### 验证网络链路速率

在每台机器上，检查其网络接口的链路速率：

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

您的以太网接口应处于 `Up` 状态，并以 `10 Gbps` 运行：

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **注意**：如果速率低于 `10 Gbps` 或链路未能建立，请检查网线连接，并确认交换机端口已设置为 10Gbps。有些交换机需要先禁用自动协商功能并手动设置链路速率；请参阅您所使用交换机的相关文档。

<!-- @os:end -->

## 安装 llama.cpp

> **注意**：请在 Machine 1 和 Machine 2 上都完成此步骤。

提供两种安装方式：

- [方式一：Lemonade SDK（推荐）](#option-1-lemonade-sdk-recommended) —— 预编译二进制文件，设置速度最快
- [方式二：手动源码构建](#option-2-manual-source-build) —— 从源码构建，可完全控制构建参数

### 方式一：Lemonade SDK（推荐）

Lemonade SDK 提供带有 AMD ROCm 7 加速的 llama.cpp 每日构建版本，面向 gfx1151（Strix Halo / Ryzen AI Max+ 395）等 GPU 以及其他近期的 Radeon 架构。

<!-- @os:windows -->
#### 步骤 1：下载预编译二进制文件

转到最新发布版本页面，下载与您的平台和 GPU 目标相匹配的压缩包：

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

下载名为 `llama-bxxxx-windows-rocm-gfx1151-x64.zip` 的文件（其中 `xxxx` 为构建编号）。

#### 步骤 2：解压二进制文件

解压下载的压缩包：

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

该目录现在包含了针对您的 Ryzen AI Halo 系统预编译的、支持 ROCm 的 `llama-cli.exe`、`llama-server.exe` 和 `rpc-server.exe`。

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
#### 步骤 1：下载预构建二进制文件

访问最新版本页面，下载与您的平台和 GPU 目标相匹配的压缩包：

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

下载名为 `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` 的文件（其中 `xxxx` 是构建编号）。

#### 步骤 2：解压并准备二进制文件

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

该目录现在包含启用 ROCm 的 `llama-cli`、`llama-server` 和 `rpc-server` 构建版本，已针对您的 Ryzen AI Halo 系统预编译完成。

#### 步骤 3：验证 GPU 检测

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
在每个节点上准备好 llama.cpp 后，继续执行[下载模型](#downloading-the-model)。

### 选项 2：手动源码构建

<!-- @os:windows -->
#### 步骤 1：构建 llama.cpp

打开 **x64 Native Tools Command Prompt**（随 Visual Studio Build Tools 一起安装），并克隆代码仓库：

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
| `-DGGML_RPC=ON` | 启用 RPC 以支持分布式推理 |
| `-DGPU_TARGETS=gfx1151` | 以 Ryzen AI Halo GPU（Radeon 8060s）为目标 |
| `-G Ninja` | 使用 Ninja 构建系统 |

#### 步骤 2：验证 GPU 检测

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

#### 步骤 3：将 HIP 添加到用户路径

上述构建步骤仅在当前会话中设置了 `%HIP_PATH%\bin`。为了让 HIP 库在任意终端中可用（而不仅限于 x64 Native Tools Command Prompt），请将其永久添加到用户 `PATH` 中：

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

在每个节点上准备好 llama.cpp 后，继续执行[下载模型](#downloading-the-model)。
<!-- @os:end -->

<!-- @os:linux -->
#### 步骤 1：构建 llama.cpp

克隆代码仓库：

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
| `-DGGML_RPC=ON` | 启用 RPC 以支持分布式推理 |
| `-DAMDGPU_TARGETS="gfx1151"` | 以 Ryzen AI Halo GPU（Radeon 8060s）为目标 |

有关更多构建选项，请参阅 [llama.cpp 构建文档](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)。

#### 步骤 2：验证 GPU 检测

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

在每个节点上准备好 llama.cpp 后，继续执行[下载模型](#downloading-the-model)。
<!-- @os:end -->

## 下载模型

本操作指南使用 [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7)，这是一个 358B 参数的模型，采用来自 [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL) 的 `Q4_K_XL` 量化版本。在此量化级别下，该模型大约需要 205GB 的存储空间，并可容纳在两个 Ryzen AI Halo 节点的合并 GPU 显存中。

使用 Hugging Face CLI 下载 GGUF 文件：
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

> **注意**：模型下载必须在机器 1（控制器）上完成。RPC 工作节点不需要本地保存模型文件副本。

## 在集群上启动模型

llama.cpp RPC（远程过程调用）引擎允许单个 llama.cpp 实例通过网络将模型层卸载到远程工作节点。一台机器充当**控制器**（机器 1），负责分词、调度和编排。另一台机器运行一个轻量级的 **RPC 服务器**（机器 2），将其 GPU 内存和算力提供给控制器使用。

在加载时，llama.cpp 会将模型分片到两个节点上。加载完成后，推理过程就如同运行在单个加速器上一样。RPC 在后台处理张量传输和同步。

### 步骤 1：启动 RPC 服务器（机器 2）

在机器 2 上，启动 RPC 服务器以将其 GPU 资源提供给控制器：
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
| `--host` | 用于绑定 RPC 服务器的 IP 地址（`0.0.0.0` 表示所有接口） |

有关更多选项，请参阅 [llama.cpp RPC 文档](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md)。

### 步骤 2：启动模型（机器 1）

在机器 2 上运行 RPC 服务器后，从机器 1 使用 `llama-cli` 或 `llama-server` 启动推理。

#### llama-cli

`llama-cli` 提供了一个基于终端的界面，可直接与模型进行交互。它非常适合用于基准测试、调试和底层实验。

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  --rpc <RPC_WORKER_IP>:50053
```

> **查找 `<RPC_WORKER_IP>`**：在机器 2 上运行 `hostname -I | awk '{print $1}'` 以查找其本地 IP 地址。
<!-- @os:end -->

<!-- @os:windows -->
> **注意**：请在终端（Powershell）中运行此命令。

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **查找 `<RPC_WORKER_IP>`**：在机器 2 上的终端（Powershell）中运行 `ipconfig | findstr /C:"IPv4"` 以查找其本地 IP 地址。

<!-- @os:end -->

运行后，`llama-cli` 将显示模型加载进度，并进入一个交互式提示界面，您可以在其中直接与模型进行对话：

![llama-cli 在两个节点上运行 GLM 4.7](assets/llama-cli-example.png)
#### llama-server

`llama-server` 通过一个持久运行的服务器进程来提供相同的推理引擎，该进程集成了 Web UI 和兼容 OpenAI 的 HTTP API。对于长期运行的部署、多用户访问以及与外部工具的集成，这是首选的接口。

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **查找 `<RPC_WORKER_IP>`**：在机器 2 上，运行 `hostname -I | awk '{print $1}'` 以查找其本地 IP 地址。
<!-- @os:end -->

<!-- @os:windows -->
> **注意**：在终端（Powershell）中运行此命令。

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

> **查找 `<RPC_WORKER_IP>`**：在机器 2 上，在终端（Powershell）中运行 `ipconfig | findstr /C:"IPv4"` 以查找其本地 IP 地址。
<!-- @os:end -->

启动后，在浏览器中打开 `http://<HOST_IP>:8081` 即可访问内置的 Web UI。该界面提供了一个基于浏览器的聊天界面，用于与模型进行交互：

![llama-server 在两个节点上运行 GLM 4.7 的 Web UI](assets/llama-server-example.png)

<!-- @os:linux -->
> **查找 `<HOST_IP>`**：在机器 1 上，运行 `hostname -I | awk '{print $1}'` 以查找其本地 IP 地址。
<!-- @os:end -->

<!-- @os:windows -->
> **查找 `<HOST_IP>`**：在机器 1 上，在终端（Powershell）中运行 `ipconfig | findstr /C:"IPv4"` 以查找其本地 IP 地址。
<!-- @os:end -->

#### 参数参考

| 标志 | 用途 |
|------|---------|
| `-m` | GGUF 模型文件的路径（使用第一个分片，`00001-of-00005`） |
| `-c` | 上下文大小（以 token 为单位）。值越大，占用的内存越多 |
| `-fa on` | 启用 rocWMMA Flash Attention，以提升 AMD GPU 上的性能 |
| `-ngl 999` | 将所有模型层卸载到 GPU |
| `-lm none` | 将模型加载模式设置为 `none`，禁用内存映射，以便在模型大小超过系统内存但适合 VRAM 时减少加载时间 |
| `--host` | 绑定 `llama-server` 的 IP（仅适用于 `llama-server`） |
| `--port` | 提供 HTTP API 服务的端口（仅适用于 `llama-server`） |
| `--rpc` | 以逗号分隔的 RPC 工作节点端点列表（`IP:port`） |

有关完整的参数用法，请参阅 [llama-cli 文档](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) 和 [llama-server 文档](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)。

## 后续步骤

- **连接第三方应用程序**：`llama-server` 提供了一个兼容 OpenAI 的 API。将任何兼容 OpenAI 的应用程序（如 Open WebUI）指向 `http://<HOST_IP>:8081`，并使用任意占位 API 密钥（例如 `none`），即可连接到您的集群
- **探索其他模型**：在 [Hugging Face](https://huggingface.co/models?search=gguf) 上浏览量化的 GGUF 模型，以找到适合您集群总 GPU 内存容量的模型
- **扩展到四个节点**：再添加两台 Ryzen AI Halo 系统作为额外的 RPC 工作节点，即可使用达到一万亿参数规模的模型。将额外的端点以逗号分隔的列表形式传递给 `--rpc`（例如 `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`）