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

# 使用 RPC 集群化四台 Ryzen™ AI Halo

## 概述

您的 Ryzen™ AI Halo 已经能够在本地运行大语言模型。集群化则更进一步，通过本地网络将多台系统的 GPU 内存组合在一起，让您能够访问更大的模型，获得更强的推理能力、更出色的代码生成能力以及更深入的多语言理解能力，而这一切都完全在您自己的硬件上完成。

本指南将教您如何使用 llama.cpp 的 RPC 引擎集群化四台 Ryzen AI Halo 系统，并在所有四台机器上通过 AMD ROCm™ 加速运行 Kimi K2.6（一个大型混合专家模型）。

## 您将学到的内容

- 如何在 Ryzen AI Halo 系统上扩展 VRAM 分配
- 安装支持 ROCm 和 RPC 的 llama.cpp
- 配置 RPC 工作节点并在四个节点间启动分布式推理
- 在四台联网的 Ryzen AI Halo 系统上运行一个 1T 参数规模的模型

## 设置内存配置

> **注意**：请在所有四台机器（机器 1 到机器 4）上完成此步骤。

<!-- @device:halo_box -->
<!-- @os:windows -->
> **运行接近或超过 128 GB 的模型：** 在运行 Windows 的 AMD Ryzen™ AI Max 400 系列（Gorgon Halo）系统上，接近或超过 128 GB 内存的模型需要额外的配置才能正常运行，不会出错。请在加载模型之前，先按照 [AMD Ryzen AI Max PRO 400 系列 Windows 操作系统指南](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines) 进行操作。
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
在 Windows 上，要运行需要更高内存的大型模型，我们需要使用 AMD 可变图形内存（iGPU VRAM）分配功能。

您可以通过打开 AMD Software: Adrenalin Edition 控制面板并导航至：`Performance > Tuning > AMD Variable Graphics Memory` 来完成此操作。将数值设置为 **96 GB**。请重启系统以使更改生效。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
在 Linux 上，ROCm 使用共享系统内存池，该内存池默认配置为系统内存的一半。

可以通过更改内核的转换表管理器（TTM）页面设置来增加此数量，具体说明如下。AMD 建议在 BIOS 中设置最低专用 VRAM（0.5 GB）。

* 安装 pipx 工具，并将 pipx 安装的 wheel 包路径添加到系统搜索路径中。

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* 从 PyPI 安装 amd-debug-tools wheel 包。
  ```bash
  pipx install amd-debug-tools
  ```

* 运行 amd-ttm 工具查询共享内存的当前设置。
  ```bash
  amd-ttm
  ```

* 将共享内存设置重新配置为 **120 GB**：
  ```bash
  amd-ttm --set 120
  ```

* 重启系统以使更改生效。


<!-- @os:end -->
<!-- @device:halo_box -->
## 检查软件更新

<!-- @require:software-update -->
<!-- @device:end -->
## 先决条件

### 硬件

本指南需要四台 Ryzen AI Halo 设备和一台以太网交换机，以星型拓扑连接，每台设备直接连接到交换机。

| 组件 | 数量 | 描述 |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | 组成集群的计算节点 |
| 10Gbps 以太网交换机 | 1 | 允许多节点 Ryzen AI Halo 通信的中央交换机（至少 4 个端口） |
| 以太网线缆 | 4 | 将每台 Halo 设备连接到交换机（建议使用 Cat 7 或更高规格） |

> **注意**：连接四台 Ryzen AI Halo 设备需要四个以太网交换机端口。如果您要从单独的客户端机器而不是从某台 Halo 设备访问模型，则需要第五个端口。

### 软件
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
请安装：
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe)，并选择 **使用 C++ 的桌面开发** 工作负载
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## 物理硬件设置

> **注意**：请在所有四台机器（机器 1 到机器 4）上完成此步骤。

使用 Cat 7（或更高规格）线缆将每台 Ryzen AI Halo 设备连接到以太网交换机。这将建立用于节点间高速通信的 10Gbps 链路。
<!-- @os:linux -->
### 1. 确定网络接口

在每台机器上，找到其网络接口的名称并记录下来（下文中将称之为 `IFNAME`）。运行：

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

这将直接打印接口名称，例如：

```bash
enp191s0
```

### 2. 验证网络链路速度

通过检查接口的速度，确认链路处于活动状态并以全速运行：

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注意**：将 `<IFNAME>` 替换为 [1. 确定网络接口](#1-确定网络接口) 中输出的接口名称

您应该会看到速度为 `10000Mb/s`：

```bash
	Speed: 10000Mb/s
```

> **注意**：如果速度低于 `10000Mb/s` 或链路未建立，请检查线缆连接，并确认交换机端口已设置为 10Gbps。某些交换机需要禁用自动协商并手动设置链路速度，请参阅您交换机的文档。

<!-- @os:end -->

<!-- @os:windows -->
### 验证网络链路速度

在每台机器上，检查网络接口的链路速度：

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

您的以太网接口应显示为 `Up`，并以 `10 Gbps` 运行：

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **注意**：如果速度低于 `10 Gbps` 或链路未建立，请检查线缆连接，并确认交换机端口已设置为 10Gbps。某些交换机需要禁用自动协商并手动设置链路速度，请参阅您交换机的文档。

<!-- @os:end -->

## 安装 llama.cpp

> **注意**：请在所有四台机器（机器 1 到机器 4）上完成此步骤。

有两种安装选项可供选择：

- [选项 1：Lemonade SDK（推荐）](#option-1-lemonade-sdk-recommended) - 预构建二进制文件，设置速度最快
- [选项 2：手动源码构建](#option-2-manual-source-build) - 从源码构建，可完全控制构建标志
### 选项 1：Lemonade SDK（推荐）

Lemonade SDK 提供经过 AMD ROCm 7 加速的 llama.cpp 夜间构建版本，面向 gfx1151（Strix Halo / Ryzen AI Max+ 395）等 GPU 以及其他较新的 Radeon 架构。

<!-- @os:windows -->
#### 步骤 1：下载预编译二进制文件

访问最新版本发布页面，下载与您的平台和 GPU 目标相匹配的压缩包：

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

下载名为 `llama-bxxxx-windows-rocm-gfx1151-x64.zip` 的文件（其中 `xxxx` 为构建编号）。

#### 步骤 2：解压二进制文件

解压下载的压缩包：

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

此目录现在包含专为您的 Ryzen AI Halo 系统预编译的、启用了 ROCm 的 `llama-cli.exe`、`llama-server.exe` 和 `ggml-rpc-server.exe` 构建版本。

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

访问最新版本发布页面，下载与您的平台和 GPU 目标相匹配的压缩包：

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

下载名为 `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` 的文件（其中 `xxxx` 为构建编号）。

#### 步骤 2：解压并准备二进制文件

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

此目录现在包含专为您的 Ryzen AI Halo 系统预编译的、启用了 ROCm 的 `llama-cli`、`llama-server` 和 `rpc-server` 构建版本。

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
在每个节点上准备好 llama.cpp 后，请继续阅读[下载模型](#downloading-the-model)部分。

### 选项 2：手动源码构建

<!-- @os:windows -->
#### 步骤 1：构建 llama.cpp

打开 **x64 Native Tools Command Prompt**（随 Visual Studio Build Tools 安装）并克隆仓库：

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
| `-DGGML_RPC=ON` | 启用用于分布式推理的 RPC |
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

#### 步骤 3：将 HIP 添加到您的用户路径

上述构建步骤仅为当前会话设置了 `%HIP_PATH%\bin`。要使 HIP 库在任意终端中可用（而不仅限于 x64 Native Tools Command Prompt），请将其永久添加到您的用户 `PATH` 中：

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

在每个节点上准备好 llama.cpp 后，请继续阅读[下载模型](#downloading-the-model)部分。
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
| `-DGGML_RPC=ON` | 启用用于分布式推理的 RPC |
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

在每个节点上准备好 llama.cpp 后，请继续阅读[下载模型](#downloading-the-model)部分。
<!-- @os:end -->

## 下载模型

本手册使用来自 [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL) 的 `UD-Q2_K_XL` 量化版本的 [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6)。此量化版本可容纳于四个 Ryzen AI Halo 节点的 GPU 内存总和之内。

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

> **注意**：模型下载必须在机器 1（控制器）上完成。RPC 工作节点（机器 2、3 和 4）不需要在本地保存模型文件副本。

## 在集群上启动模型

llama.cpp 的 RPC（远程过程调用）引擎允许单个 llama.cpp 实例通过网络将模型层卸载到远程工作节点上。一台机器作为**控制器**（机器 1），负责分词、调度和编排。其他三台机器（机器 2、3 和 4）各自运行一个轻量级的 **RPC 服务器**，向控制器开放其 GPU 内存和计算能力。

在加载时，llama.cpp 会将模型分片到所有四个节点上。加载完成后，推理过程就如同在单个加速器上运行一样。RPC 在幕后负责张量传输和同步。

### 步骤 1：启动 RPC 服务器（机器 2、3 和 4）

在机器 2、3 和 4 上，分别启动 RPC 服务器，以便将其 GPU 资源开放给控制器：
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
| `-p` | RPC 服务器广播所用的端口 |
| `-c` | 为大型张量启用本地缓存，避免在模型加载过程中重复进行网络传输 |
| `--host` | RPC 服务器绑定的 IP 地址（`0.0.0.0` 表示绑定所有接口） |

有关更多选项，请参阅 [llama.cpp RPC 文档](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md)。

### 步骤 2：启动模型（机器 1）

在机器 2、3 和 4 上运行 RPC 服务器后，使用 `llama-cli` 或 `llama-server` 从机器 1 启动推理。
#### llama-cli

`llama-cli` 提供基于终端的界面，用于直接与模型交互。它非常适合用于基准测试、调试和底层实验。

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

> **查找 `<RPC_WORKER_2_IP>`、`<RPC_WORKER_3_IP>`、`<RPC_WORKER_4_IP>`**：在机器 2、3 和 4 上分别在终端（Powershell）中运行 `ipconfig | findstr /C:"IPv4"` 以查找其本地 IP 地址。

<!-- @os:end -->

运行后，`llama-cli` 会显示模型加载进度，并进入一个交互式提示符，您可以在其中直接与模型聊天：

![llama-cli running Kimi K2.6 across four nodes](assets/llama-cli-example.png)

#### llama-server

`llama-server` 通过一个持久化的服务器进程来暴露相同的推理引擎，该进程集成了 Web UI 和与 OpenAI 兼容的 HTTP API。对于长时间运行的部署、多用户访问以及与外部工具的集成，这是首选的接口。

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
> **注意**：请在终端（Powershell）中运行此命令。

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

启动后，在浏览器中打开 `http://<HOST_IP>:8081` 即可访问内置的 Web UI。该界面提供基于浏览器的聊天界面，用于与模型进行交互：

![llama-server web UI running Kimi K2.6 across four nodes](assets/llama-server-example.png)

<!-- @os:linux -->
> **查找 `<HOST_IP>`**：在机器 1 上运行 `hostname -I | awk '{print $1}'` 以查找其本地 IP 地址。
<!-- @os:end -->

<!-- @os:windows -->
> **查找 `<HOST_IP>`**：在机器 1 上的终端（Powershell）中运行 `ipconfig | findstr /C:"IPv4"` 以查找其本地 IP 地址。
<!-- @os:end -->

#### 参数参考

| 标志 | 用途 |
|------|---------|
| `-m` | GGUF 模型文件的路径（使用第一个分片，`00001-of-00008`） |
| `-c` | 上下文大小（以 token 为单位）。值越大，占用的内存越多 |
| `-fa on` | 启用 rocWMMA Flash Attention，以提升 AMD GPU 上的性能 |
| `-ngl 999` | 将所有模型层卸载到 GPU |
| `-lm none` | 将模型加载模式设置为 `none`，禁用内存映射，以便在模型大小超过系统内存但适配显存时缩短加载时间 |
| `-b` | 逻辑批处理大小（以 token 为单位）。设置为 4096 可在各节点间平衡吞吐量与内存使用 |
| `-ub` | 用于提示处理的物理（微）批处理大小。与 `-b` 保持一致可避免不必要的分块开销 |
| `--host` | 绑定 `llama-server` 的 IP（仅适用于 `llama-server`） |
| `--port` | 提供 HTTP API 服务的端口（仅适用于 `llama-server`） |
| `--rpc` | 以逗号分隔的 RPC 工作节点端点列表（`IP:port`） |

有关完整的参数用法，请参阅 [llama-cli 文档](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) 和 [llama-server 文档](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)。

## 后续步骤

- **连接第三方应用程序**：`llama-server` 暴露了一个与 OpenAI 兼容的 API。将任何与 OpenAI 兼容的应用程序（例如 Open WebUI）指向 `http://<HOST_IP>:8081`，并使用任意占位 API 密钥（例如 `none`），即可连接到您的集群
- **探索其他模型**：在 [Hugging Face](https://huggingface.co/models?search=gguf) 上浏览量化的 GGUF 模型，找到适合您集群总 GPU 内存大小的模型
- **扩展至四个节点以上**：添加更多 Ryzen AI Halo 系统作为额外的 RPC 工作节点，以使用超过 1 万亿参数规模的模型。将额外的端点以逗号分隔的形式传递给 `--rpc`（例如 `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`）