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

# 使用 RPC 组建两台 Ryzen™ AI Halo 集群

## 概述

您的 Ryzen™ AI Halo 已经能够在本地运行大语言模型。而集群化能够更进一步,通过局域网整合多台系统的 GPU 显存,让您能够访问具有更强推理能力、更好代码生成能力以及更深层次多语言理解能力的更大模型,而这一切全部都在您自己的硬件上完成。

本手册将指导您使用 llama.cpp 的 RPC 引擎组建两台 Ryzen AI Halo 系统的集群,并借助 AMD ROCm™ 加速,在两台机器上运行拥有 3580 亿参数的 GLM 4.7 模型。

## 您将学到什么

- 如何扩展 Ryzen AI Halo 系统上的显存分配
- 安装带有 ROCm 和 RPC 支持的 llama.cpp
- 配置 RPC 工作节点并在两个节点上启动分布式推理
- 在两台联网的 Ryzen AI Halo 系统上运行拥有 3580 亿参数的模型

## 设置内存配置

> **注意**:请在机器 1 和机器 2 上都完成此步骤。

<!-- @os:windows -->
在 Windows 系统上,要运行需要更高内存的大型模型,我们需要使用 AMD Variable Graphics Memory(iGPU VRAM)分配功能。

您可以通过打开 AMD Software: Adrenalin Edition 控制面板,并导航到:`Performance > Tuning > AMD Variable Graphics Memory` 来完成此操作。将该值设置为 **96 GB**。请重启系统以使更改生效。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
在 Linux 系统上,ROCm 使用共享系统内存池,默认情况下该内存池配置为系统内存的一半。

可以通过以下说明更改内核的转换表管理器(Translation Table Manager,TTM)页面设置来增加此数量。AMD 建议在 BIOS 中设置最小专用显存(0.5 GB)。

* 安装 pipx 实用工具,并将 pipx 安装的软件包路径添加到系统搜索路径中。

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* 从 PyPI 安装 amd-debug-tools 软件包。
  ```bash
  pipx install amd-debug-tools
  ```

* 运行 amd-ttm 工具以查询当前共享内存设置。
  ```bash
  amd-ttm
  ```

* 将共享内存设置重新配置为 **120 GB**:
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

本手册需要两台 Ryzen AI Halo 设备和一台以太网交换机,以星型拓扑连接,每台设备直接与交换机相连。

| 组件 | 数量 | 描述 |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | 组成集群的计算节点 |
| 10Gbps 以太网交换机 | 1 | 用于实现多节点 Ryzen AI Halo 通信的中央交换机(至少 2 个端口) |
| 以太网电缆 | 2 | 将每台 Halo 设备连接到交换机(建议使用 Cat 7 或更高规格) |

> **注意**:连接两台 Ryzen AI Halo 设备需要两个以太网交换机端口。如果您是从单独的客户端机器而非某台 Halo 设备访问模型,则需要第三个端口。

### 软件
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
请安装:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe),并勾选 **Desktop Development with C++** 工作负载
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## 物理硬件设置

> **注意**:请在机器 1 和机器 2 上都完成此步骤。

使用 Cat 7(或更高规格)电缆将每台 Ryzen AI Halo 设备连接到以太网交换机。这样可以建立用于节点间高速通信的 10Gbps 链路。
<!-- @os:linux -->
### 1. 确定网络接口

在每台机器上,找到其网络接口的名称并记录下来(下文中将其称为 `IFNAME`)。运行:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

此命令会直接输出接口名称,例如:

```bash
enp191s0
```

### 2. 验证网络链路速度

通过检查接口速度,确认链路处于活动状态且以全速运行:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注意**:将 `<IFNAME>` 替换为 [1. 确定网络接口](#1-determine-network-interfaces) 中输出的接口名称

您应该会看到 `10000Mb/s` 的速度:

```bash
	Speed: 10000Mb/s
```

> **注意**:如果速度低于 `10000Mb/s` 或链路未建立,请检查电缆连接,并确认交换机端口已设置为 10Gbps。部分交换机需要禁用自动协商并手动设置链路速度,请参阅您的交换机文档。

<!-- @os:end -->

<!-- @os:windows -->
### 验证网络链路速度

在每台机器上,检查网络接口的链路速度:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

您的以太网接口应处于 `Up` 状态,并以 `10 Gbps` 运行:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **注意**:如果速度低于 `10 Gbps` 或链路未建立,请检查电缆连接,并确认交换机端口已设置为 10Gbps。部分交换机需要禁用自动协商并手动设置链路速度,请参阅您的交换机文档。

<!-- @os:end -->

## 安装 llama.cpp

> **注意**:请在机器 1 和机器 2 上都完成此步骤。

提供两种安装方式:

- [方式一:Lemonade SDK(推荐)](#option-1-lemonade-sdk-recommended) - 预构建二进制文件,设置速度最快
- [方式二:手动源码构建](#option-2-manual-source-build) - 从源码构建,可完全控制构建标志

### 方式一:Lemonade SDK(推荐)

Lemonade SDK 提供了带有 AMD ROCm 7 加速的 llama.cpp 每夜构建版本,面向 gfx1151(Strix Halo / Ryzen AI Max+ 395)等 GPU 以及其他近期的 Radeon 架构。

<!-- @os:windows -->
#### 步骤 1：下载预构建二进制文件

导航到最新的发布页面，下载与您的平台和 GPU 目标匹配的压缩包：

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

下载名为 `llama-bxxxx-windows-rocm-gfx1151-x64.zip` 的文件（其中 `xxxx` 为构建版本号）。

#### 步骤 2：解压二进制文件

解压下载的压缩包：

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

此目录现在包含针对您的 Ryzen AI Halo 系统预编译的支持 ROCm 的 `llama-cli.exe`、`llama-server.exe` 和 `rpc-server.exe` 构建版本。

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

导航到最新的发布页面，下载与您的平台和 GPU 目标匹配的压缩包：

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

下载名为 `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` 的文件（其中 `xxxx` 为构建版本号）。

#### 步骤 2：解压并准备二进制文件

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

此目录现在包含针对您的 Ryzen AI Halo 系统预编译的支持 ROCm 的 `llama-cli`、`llama-server` 和 `rpc-server` 构建版本。

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
在每个节点上准备好 llama.cpp 后，继续[下载模型](#downloading-the-model)。

### 选项 2：手动源代码构建

<!-- @os:windows -->
#### 步骤 1：构建 llama.cpp

打开 **x64 Native Tools Command Prompt**（随 Visual Studio Build Tools 一起安装），并克隆仓库：

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

将 HIP 添加到您的路径中，并使用 ROCm 和 RPC 支持进行构建：

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| 构建标志 | 用途 |
|-----------|---------|
| `-DGGML_HIP=ON` | 启用 ROCm/HIP 软件栈 |
| `-DGGML_RPC=ON` | 启用用于分布式推理的 RPC |
| `-DGPU_TARGETS=gfx1151` | 面向 Ryzen AI Halo GPU（Radeon 8060s） |
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

上述构建步骤仅为当前会话设置了 `%HIP_PATH%\bin`。要使 HIP 库在任何终端中都可用（而不仅仅是 x64 Native Tools Command Prompt），请将其永久添加到您的用户 `PATH` 中：

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

在每个节点上准备好 llama.cpp 后，继续[下载模型](#downloading-the-model)。
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
| `-DGGML_RPC=ON` | 启用用于分布式推理的 RPC |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | 在 AMD GPU 上启用 rocWMMA 以增强 Flash Attention |
| `-DAMDGPU_TARGETS="gfx1151"` | 面向 Ryzen AI Halo GPU（Radeon 8060s） |

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

在每个节点上准备好 llama.cpp 后，继续[下载模型](#downloading-the-model)。
<!-- @os:end -->

## 下载模型

本操作手册使用 [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7)，这是一个来自 [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL) 的 358B 参数模型，采用 `Q4_K_XL` 量化。在此量化级别下，该模型大约需要 205GB 的存储空间，并可以放入两个 Ryzen AI Halo 节点的组合 GPU 内存中。

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

> **注意**：模型下载必须在机器 1（控制器）上完成。RPC 工作节点不需要本地保存模型文件的副本。

## 在集群上启动模型

llama.cpp RPC（远程过程调用）引擎允许单个 llama.cpp 实例通过网络将模型层卸载到远程工作节点。一台机器充当**控制器**（机器 1），负责分词、调度和编排。另一台机器运行轻量级的 **RPC 服务器**（机器 2），将其 GPU 内存和计算能力暴露给控制器。

在加载时，llama.cpp 会将模型分片到两个节点上。加载完成后，推理过程就如同在单个加速器上运行一样。RPC 会在幕后处理张量传输和同步。

### 步骤 1：启动 RPC 服务器（机器 2）

在机器 2 上，启动 RPC 服务器，将其 GPU 资源暴露给控制器：
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
| `-p` | 广播 RPC 服务器所使用的端口 |
| `-c` | 为大型张量启用本地缓存，避免在模型加载过程中重复进行网络传输 |
| `--host` | 绑定 RPC 服务器的 IP 地址（`0.0.0.0` 表示所有接口） |

有关更多选项，请参阅 [llama.cpp RPC 文档](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md)。

### 步骤 2：启动模型（机器 1）

在机器 2 上运行 RPC 服务器后，使用 `llama-cli` 或 `llama-server` 从机器 1 启动推理。

#### llama-cli

`llama-cli` 提供基于终端的界面，可直接与模型交互。它非常适合进行基准测试、调试和底层实验。

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

> **查找 `<RPC_WORKER_IP>`**：在机器 2 上，运行 `hostname -I | awk '{print $1}'` 来查找其本地 IP 地址。
<!-- @os:end -->

<!-- @os:windows -->
> **注意**：在终端（Powershell）中运行此命令。

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **查找 `<RPC_WORKER_IP>`**：在机器 2 上，在终端（Powershell）中运行 `ipconfig | findstr /C:"IPv4"` 来查找其本地 IP 地址。

<!-- @os:end -->

运行后，`llama-cli` 会显示模型加载进度，并进入一个交互式提示符，您可以直接在其中与模型进行聊天：

![llama-cli 在两个节点上运行 GLM 4.7](assets/llama-cli-example.png)
#### llama-server

`llama-server` 通过一个持久化的服务器进程暴露相同的推理引擎,该进程集成了 Web UI 和兼容 OpenAI 的 HTTP API。对于长期运行的部署、多用户访问以及与外部工具的集成,这是首选接口。

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

> **查找 `<RPC_WORKER_IP>`**:在 Machine 2 上运行 `hostname -I | awk '{print $1}'` 以找到其本地 IP 地址。
<!-- @os:end -->

<!-- @os:windows -->
> **注意**:在 Terminal(Powershell)中运行此命令。

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

> **查找 `<RPC_WORKER_IP>`**:在 Machine 2 上,在 Terminal(Powershell)中运行 `ipconfig | findstr /C:"IPv4"` 以找到其本地 IP 地址。
<!-- @os:end -->

启动后,在浏览器中打开 `http://<HOST_IP>:8081` 即可访问内置的 Web UI。这提供了一个基于浏览器的聊天界面,用于与模型进行交互:

![在两个节点上运行 GLM 4.7 的 llama-server web UI](assets/llama-server-example.png)

<!-- @os:linux -->
> **查找 `<HOST_IP>`**:在 Machine 1 上运行 `hostname -I | awk '{print $1}'` 以找到其本地 IP 地址。
<!-- @os:end -->

<!-- @os:windows -->
> **查找 `<HOST_IP>`**:在 Machine 1 上,在 Terminal(Powershell)中运行 `ipconfig | findstr /C:"IPv4"` 以找到其本地 IP 地址。
<!-- @os:end -->

#### 参数参考

| 标志 | 用途 |
|------|---------|
| `-m` | GGUF 模型文件的路径(使用第一个分片,`00001-of-00005`) |
| `-c` | 上下文大小(以 token 为单位)。值越大,占用的内存越多 |
| `-fa on` | 启用 rocWMMA Flash Attention,以提升在 AMD GPU 上的性能 |
| `-ngl 999` | 将所有模型层卸载到 GPU |
| `--no-mmap` | 禁用内存映射,当模型大小超过系统内存但可容纳于显存时,可减少加载时间 |
| `--host` | `llama-server` 绑定的 IP(仅适用于 `llama-server`) |
| `--port` | 提供 HTTP API 服务的端口(仅适用于 `llama-server`) |
| `--rpc` | 以逗号分隔的 RPC 工作节点端点列表(`IP:port`) |

有关完整的参数用法,请参阅 [llama-cli 文档](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md)和 [llama-server 文档](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)。

## 后续步骤

- **连接第三方应用程序**:`llama-server` 暴露了一个兼容 OpenAI 的 API。将任何兼容 OpenAI 的应用程序(例如 Open WebUI)指向 `http://<HOST_IP>:8081`,并使用任意占位 API 密钥(例如 `none`),即可连接到您的集群
- **探索其他模型**:在 [Hugging Face](https://huggingface.co/models?search=gguf) 上浏览量化的 GGUF 模型,找到适合您集群总 GPU 内存的模型
- **扩展到四个节点**:再添加两台 Ryzen AI Halo 系统作为额外的 RPC 工作节点,即可访问达到万亿参数规模的模型。可将额外的端点以逗号分隔的形式传递给 `--rpc`(例如 `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)