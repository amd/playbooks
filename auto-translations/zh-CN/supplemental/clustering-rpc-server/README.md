<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# 使用 RPC 集群两台 Ryzen™ AI Halo

## 概述

您的 Ryzen™ AI Halo 已经能够在本地运行大型语言模型。集群技术通过局域网将多台系统的 GPU 内存合并，进一步扩展了这一能力，让您能够访问更大的模型，获得更强的推理能力、更好的代码生成效果以及更深入的多语言理解——所有这些完全在您自己的硬件上运行。

本 playbook 将教您如何使用 llama.cpp 的 RPC 引擎集群两台 Ryzen AI Halo 系统，并借助 AMD ROCm™ 加速在两台机器上运行 GLM 4.7（一个拥有 3580 亿参数的模型）。

## 您将学到的内容

- 如何扩展 Ryzen AI Halo 系统上的 VRAM 分配
- 安装支持 ROCm 和 RPC 的 llama.cpp
- 配置 RPC 工作节点并在两个节点间启动分布式推理
- 在两台联网的 Ryzen AI Halo 系统上运行 3580 亿参数模型

## 设置内存配置

> **注意**：请在机器 1 和机器 2 上均完成此步骤。

<!-- @os:windows -->
在 Windows 上，要运行需要更大内存的模型，我们需要使用 AMD 可变显存（iGPU VRAM）分配功能。

可通过打开 AMD Software: Adrenalin Edition 控制面板并导航至以下路径来完成此操作：`Performance > Tuning > AMD Variable Graphics Memory`。将值设置为 **96 GB**。请重启系统以使更改生效。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
在 Linux 上，ROCm 使用共享系统内存池，该内存池默认配置为系统内存的一半。

可以通过更改内核的转换表管理器（TTM）页面设置来增加此容量，具体操作如下。AMD 建议在 BIOS 中将最小专用 VRAM 设置为 0.5 GB。

* 安装 pipx 工具并将 pipx 安装的 wheel 路径添加到系统搜索路径中。

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* 从 PyPI 安装 amd-debug-tools wheel。
  ```bash
  pipx install amd-debug-tools
  ```

* 运行 amd-ttm 工具以查询共享内存的当前设置。
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
## 前提条件

### 硬件

本 playbook 需要两台 Ryzen AI Halo 设备和一台以太网交换机，以星型拓扑连接，每台设备直接通过网线连接到交换机。

| 组件 | 数量 | 描述 |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | 构成集群的计算节点 |
| 10Gbps 以太网交换机 | 1 | 用于实现多节点 Ryzen AI Halo 通信的中央交换机（至少 2 个端口） |
| 以太网线缆 | 2 | 将每台 Halo 设备连接到交换机（推荐使用 Cat 7 或更高规格） |

> **注意**：连接两台 Ryzen AI Halo 设备需要两个以太网交换机端口。如果您从独立的客户端机器（而非其中一台 Halo 设备）访问模型，则还需要第三个端口。

### 软件
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
请安装：
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)，并选择 **Desktop Development with C++** 工作负载
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## 物理硬件安装

> **注意**：请在机器 1 和机器 2 上均完成此步骤。

使用 Cat 7（或更高规格）网线将每台 Ryzen AI Halo 设备连接到以太网交换机。这将建立用于节点间高速通信的 10Gbps 链路。
<!-- @os:linux -->
### 1. 确定网络接口

在每台机器上，找到其网络接口名称并记录下来（下文将其称为 `IFNAME`）。运行：

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

这将直接打印接口名称，例如：

```bash
enp191s0
```

### 2. 验证网络链路速度

通过检查接口速度，确认链路处于活动状态并以全速运行：

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注意**：将 `<IFNAME>` 替换为[1. 确定网络接口](#1-determine-network-interfaces)中输出的接口名称

您应该看到速度为 `10000Mb/s`：

```bash
	Speed: 10000Mb/s
```

> **注意**：如果速度低于 `10000Mb/s` 或链路未建立，请检查网线连接并确认交换机端口已设置为 10Gbps。某些交换机需要禁用自动协商并手动设置链路速度；请参阅您的交换机文档。

<!-- @os:end -->

<!-- @os:windows -->
### 验证网络链路速度

在每台机器上，检查网络接口的链路速度：

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

您的以太网接口应处于 `Up` 状态并以 `10 Gbps` 运行：

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **注意**：如果速度低于 `10 Gbps` 或链路未建立，请检查网线连接并确认交换机端口已设置为 10Gbps。某些交换机需要禁用自动协商并手动设置链路速度；请参阅您的交换机文档。

<!-- @os:end -->

## 安装 llama.cpp

> **注意**：请在机器 1 和机器 2 上均完成此步骤。

提供两种安装选项：

- [选项 1：Lemonade SDK（推荐）](#option-1-lemonade-sdk-recommended) - 预构建二进制文件，安装最快
- [选项 2：手动源码构建](#option-2-manual-source-build) - 从源码构建，完全控制构建标志

### 选项 1：Lemonade SDK（推荐）

Lemonade SDK 提供带有 AMD ROCm 7 加速的 llama.cpp 每夜构建版本，目标 GPU 包括 gfx1151（Strix Halo / Ryzen AI Max+ 395）及其他近期 Radeon 架构。

<!-- @os:windows -->
#### 步骤 1：下载预构建二进制文件

导航到最新发布页面，下载与您的平台和 GPU 目标匹配的压缩包：

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

下载名为 `llama-bxxxx-windows-rocm-gfx1151-x64.zip` 的文件（其中 `xxxx` 为构建编号）。

#### 步骤 2：解压二进制文件

解压下载的压缩包：

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

该目录现在包含 ROCm 加速版本的 `llama-cli.exe`、`llama-server.exe` 和 `rpc-server.exe`，已为您的 Ryzen AI Halo 系统预编译。

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

导航到最新发布页面，下载与您的平台和 GPU 目标匹配的压缩包：

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

下载名为 `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` 的文件（其中 `xxxx` 为构建编号）。

#### 步骤 2：解压并准备二进制文件

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

该目录现在包含 ROCm 加速版本的 `llama-cli`、`llama-server` 和 `rpc-server`，已为您的 Ryzen AI Halo 系统预编译。

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
在每个节点上准备好 llama.cpp 后，继续进行[下载模型](#downloading-the-model)。

### 选项 2：手动源码构建

<!-- @os:windows -->
#### 步骤 1：构建 llama.cpp

打开 **x64 Native Tools Command Prompt**（随 Visual Studio Build Tools 一起安装），并克隆仓库：

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

将 HIP 添加到您的路径并使用 ROCm 和 RPC 支持进行构建：

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| 构建标志 | 用途 |
|-----------|---------|
| `-DGGML_HIP=ON` | 启用 ROCm/HIP 软件栈 |
| `-DGGML_RPC=ON` | 启用 RPC 以支持分布式推理 |
| `-DGPU_TARGETS=gfx1151` | 目标为 Ryzen AI Halo GPU（Radeon 8060s） |
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

上述构建步骤仅为当前会话设置了 `%HIP_PATH%\bin`。要使 HIP 库在任何终端中均可用（而不仅限于 x64 Native Tools Command Prompt），请将其永久添加到用户 `PATH` 中：

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

使用 ROCm 和 RPC 支持进行构建：

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| 构建标志 | 用途 |
|-----------|---------|
| `-DGGML_HIP=ON` | 启用 ROCm 软件栈 |
| `-DGGML_RPC=ON` | 启用 RPC 以支持分布式推理 |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | 启用 rocWMMA 以增强 AMD GPU 上的 Flash Attention |
| `-DAMDGPU_TARGETS="gfx1151"` | 目标为 Ryzen AI Halo GPU（Radeon 8060s） |

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

在每个节点上准备好 llama.cpp 后，继续进行[下载模型](#downloading-the-model)。
<!-- @os:end -->

## 下载模型

本 playbook 使用 [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7)，这是一个拥有 3580 亿参数的模型，采用来自 [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL) 的 `Q4_K_XL` 量化格式。在此量化级别下，模型需要约 205GB 的存储空间，可容纳在两台 Ryzen AI Halo 节点的合并 GPU 内存中。

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

> **注意**：模型下载必须在机器 1（控制节点）上完成。RPC 工作节点不需要模型文件的本地副本。

## 在集群上启动模型

llama.cpp RPC（远程过程调用）引擎允许单个 llama.cpp 实例通过网络将模型层卸载到远程工作节点。一台机器充当**控制节点**（机器 1），负责处理分词、调度和编排。另一台机器运行轻量级的 **RPC 服务器**（机器 2），将其 GPU 内存和计算资源暴露给控制节点。

在加载时，llama.cpp 将模型分片到两个节点上。加载完成后，推理过程就像在单个加速器上运行一样。RPC 在后台处理张量传输和同步。

### 步骤 1：启动 RPC 服务器（机器 2）

在机器 2 上，启动 RPC 服务器以将其 GPU 资源暴露给控制节点：
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

| 标志 | 用途 |
|------|---------|
| `-p` | RPC 服务器广播的端口 |
| `-c` | 为大型张量启用本地缓存，避免模型加载期间重复进行网络传输 |
| `--host` | RPC 服务器绑定的 IP 地址（`0.0.0.0` 表示所有接口） |

有关更多选项，请参阅 [llama.cpp RPC 文档](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md)。

### 步骤 2：启动模型（机器 1）

在机器 2 上运行 RPC 服务器后，从机器 1 使用 `llama-cli` 或 `llama-server` 启动推理。

#### llama-cli

`llama-cli` 提供基于终端的界面，用于直接与模型交互。它非常适合基准测试、调试和底层实验。

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

> **查找 `<RPC_WORKER_IP>`**：在机器 2 上，运行 `hostname -I | awk '{print $1}'` 以查找其本地 IP 地址。
<!-- @os:end -->

<!-- @os:windows -->
> **注意**：请在终端（Powershell）中运行此命令。

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **查找 `<RPC_WORKER_IP>`**：在机器 2 上，在终端（Powershell）中运行 `ipconfig | findstr /C:"IPv4"` 以查找其本地 IP 地址。

<!-- @os:end -->

运行后，`llama-cli` 将显示模型加载进度，并进入交互式提示符，您可以直接与模型进行对话：

![llama-cli 在两个节点上运行 GLM 4.7](assets/llama-cli-example.png)

#### llama-server

`llama-server` 通过持久化服务器进程暴露相同的推理引擎，并提供集成的 Web UI 和兼容 OpenAI 的 HTTP API。这是长期运行部署、多用户访问以及与外部工具集成的首选接口。

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

> **查找 `<RPC_WORKER_IP>`**：在机器 2 上，运行 `hostname -I | awk '{print $1}'` 以查找其本地 IP 地址。
<!-- @os:end -->

<!-- @os:windows -->
> **注意**：请在终端（Powershell）中运行此命令。

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

> **查找 `<RPC_WORKER_IP>`**：在机器 2 上，在终端（Powershell）中运行 `ipconfig | findstr /C:"IPv4"` 以查找其本地 IP 地址。
<!-- @os:end -->

启动后，在浏览器中打开 `http://<HOST_IP>:8081` 以访问内置 Web UI。这提供了一个基于浏览器的聊天界面，用于与模型交互：

![llama-server Web UI 在两个节点上运行 GLM 4.7](assets/llama-server-example.png)

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
| `-c` | 以 token 为单位的上下文大小。值越大，使用的内存越多 |
| `-fa on` | 启用 rocWMMA Flash Attention 以提升 AMD GPU 上的性能 |
| `-ngl 999` | 将所有模型层卸载到 GPU |
| `--no-mmap` | 禁用内存映射，当模型大小超过系统 RAM 但能容纳在 VRAM 中时可减少加载时间 |
| `--host` | `llama-server` 绑定的 IP（仅限 `llama-server`） |
| `--port` | HTTP API 服务的端口（仅限 `llama-server`） |
| `--rpc` | 以逗号分隔的 RPC 工作节点端点列表（`IP:端口`） |

有关完整参数用法，请参阅 [llama-cli 文档](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md)和 [llama-server 文档](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)。

## 后续步骤

- **连接第三方应用程序**：`llama-server` 暴露兼容 OpenAI 的 API。将任何兼容 OpenAI 的应用程序（例如 Open WebUI）指向 `http://<HOST_IP>:8081`，并使用任意占位符 API 密钥（例如 `none`）即可连接到您的集群
- **探索其他模型**：在 [Hugging Face](https://huggingface.co/models?search=gguf) 上浏览量化的 GGUF 模型，找到适合您集群合并 GPU 内存的模型
- **扩展到四个节点**：再添加两台 Ryzen AI Halo 系统作为额外的 RPC 工作节点，即可访问万亿参数规模的模型。将额外的端点以逗号分隔列表的形式传递给 `--rpc`（例如，`--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`）