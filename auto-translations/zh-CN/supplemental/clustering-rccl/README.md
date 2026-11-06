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

# 使用 RCCL 对两台 Ryzen™ AI Halo 进行集群化

## 概述

您的 Ryzen™ AI Halo 已经能够在本地运行大语言模型。集群化更进一步,通过局域网将多台系统的 GPU 内存组合在一起,使您能够访问更大的模型,获得更强的推理能力、更好的代码生成能力以及更深入的多语言理解能力,而这一切都完全基于您自己的硬件运行。

本实践指南将向您展示如何使用 RCCL(ROCm Communication Collectives Library)配合 vLLM 对两台 Ryzen AI Halo 系统进行集群化,并借助 ROCm 加速在两台机器上运行拥有 3970 亿参数的 Qwen3.5-397B 模型。

## 您将学到什么

- 如何在 Ryzen AI Halo 系统上扩展 VRAM 分配
- 启动支持 ROCm 的 vLLM
- 为跨两台 Ryzen AI Halo 系统的多节点张量并行推理配置 RCCL
- 在两台联网的 Ryzen AI Halo 系统上运行一个 3970 亿参数的模型

## 前提条件

### 硬件

本实践指南需要两台 Ryzen AI Halo 设备和一台以太网交换机,以星形拓扑连接,每台设备直接通过网线连接到交换机。

| 组件 | 数量 | 说明 |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | 构成集群的计算节点 |
| 10Gbps 以太网交换机 | 1 | 用于支持多节点 Ryzen AI Halo 通信的中心交换机(至少 2 个端口) |
| 以太网线缆 | 2 | 将每台 Halo 设备连接到交换机(建议使用 Cat 7 或更高规格) |

> **注意**:连接两台 Ryzen AI Halo 设备需要两个以太网交换机端口。如果您是从单独的客户端机器(而不是从某台 Halo 设备)访问模型,则还需要第三个端口。

### 软件
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## 物理硬件设置

> **注意**:请在机器 1 和机器 2 上都完成此步骤。

使用 Cat 7(或更高规格)线缆将每台 Ryzen AI Halo 设备连接到以太网交换机。这将建立节点之间用于高速通信的 10Gbps 链路。

### 1. 确定网络接口

在每台机器上,找到其网络接口的名称并记录下来(在后续说明中将称为 `IFNAME`)。运行:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

这将直接打印出接口名称,例如:

```bash
enp191s0
```

### 2. 验证网络链路速度

通过检查接口速度,确认链路处于活动状态并以全速运行:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注意**:将 `<IFNAME>` 替换为 [1. 确定网络接口](#1-determine-network-interfaces) 中输出的接口名称

您应当看到速度为 `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **注意**:如果速度低于 `10000Mb/s` 或链路无法建立,请检查线缆连接,并确认交换机端口已设置为 10Gbps。某些交换机需要禁用自动协商并手动设置链路速度;请参阅您的交换机文档。

## 扩展 VRAM 分配

> **注意**:请在**机器 1 和机器 2 上都**完成此步骤。

在整个集群上运行大型模型需要较大的 GPU 内存分配,
因此此步骤在这里是必需的(不可选)。请遵循下面的
内存配置说明,将每台机器的分配量至少设置为 **96 GB**
(Linux:`amd-ttm --set 120`)。

<!-- @require:memory-config -->

## vLLM 容器初始化

> **注意**:请在机器 1 和机器 2 上都完成此步骤。

您的 Ryzen AI Halo 在一个预构建的容器镜像中附带了 vLLM,您可以使用 Podman(一个免费开源的容器工具)来运行它。

### 1. 创建模型下载目录

当您在本实践指南中提供 Qwen3.5-397B 模型服务时,vLLM 会自动将模型权重下载到您的系统中。为确保这些权重可以从容器内部访问,请先创建一个可供容器挂载的模型目录:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. 启动 vLLM 容器

下面的命令将启动容器并进入一个交互式 shell。它会挂载您刚刚创建的模型目录,并将您的 `IFNAME` 传递给 `NCCL_SOCKET_IFNAME` 和 `GLOO_SOCKET_IFNAME`,以告知 RCCL(vLLM 用于在集群间协调 GPU 的库)应使用哪个接口。

使用以下命令启动容器:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **注意**:将 `<IFNAME>` 替换为 [1. 确定网络接口](#1-determine-network-interfaces) 中输出的接口名称

## 在集群上运行模型

vLLM 使用 Ray 来编排集群,并使用 RCCL 处理跨节点的 GPU 到 GPU 通信。一台机器作为**头节点**(机器 1),负责协调推理工作;另一台作为**工作节点**(机器 2)加入集群,贡献其 GPU 内存和算力。

> **注意**:Ray 是 vLLM 的一个可选依赖项,仅在预配置的 Podman 容器内可用。

启动时,vLLM 会使用张量并行技术将模型分片到两个节点上。加载完成后,推理过程就如同在单个加速器上运行一样。

#### 防止 Ray 发生内存溢出(OOM)错误

默认情况下,Ray 会监控每个节点的主机内存,并在内存使用率超过 95% 时终止占用内存最大的进程。在您的 Ryzen™ AI Halo 上,GPU 和主机共享同一个内存池,因此加载模型可能会触发 `ray.exceptions.OutOfMemoryError` 并导致工作进程被终止。

为防止这种情况发生,我们将在启动和加入集群之前,在每台机器上导出 `RAY_memory_monitor_refresh_ms=0`。

### 步骤 1:启动 Ray 头节点(机器 1)

在机器 1 上,启动 Ray 头节点以初始化集群:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **查找 `<MACHINE_1_IP>`**:在机器 1 上运行 `hostname -I | awk '{print $1}'` 以查找其本地 IP 地址。

### 步骤 2:加入集群(机器 2)

在机器 2 上,连接到头节点以组成集群:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **查找 `<MACHINE_2_IP>`**:在机器 2 上运行 `hostname -I | awk '{print $1}'` 以查找其本地 IP 地址。

### 步骤 3:提供模型服务(机器 1)

在机器 1 上,启动 vLLM 服务器。这将自动下载模型,并开始在两个节点上提供服务:

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

#### 参数参考

| 标志 | 用途 |
|------|---------|
| `--port` | 提供 HTTP API 服务的端口 |
| `--host` | 绑定服务器的 IP 地址（`0.0.0.0` 表示绑定所有接口） |
| `--max-model-len` | 最大上下文长度（以 token 为单位） |
| `--gpu-memory-utilization` | 分配的 GPU 内存比例（0.0–1.0） |
| `--dtype` | 模型权重的数据类型 |
| `--tensor-parallel-size` | 分片模型所跨越的 GPU 数量（设置为集群中的 GPU 总数） |
| `--distributed-executor-backend` | 多节点执行的后端（集群部署使用 `ray`） |
| `--enforce-eager` | 禁用 CUDA 图编译以提高兼容性 |
| `--language-model-only` | 跳过加载辅助模型组件（例如视觉编码器） |
| `--reasoning-parser` | 为模型启用结构化推理输出解析 |

有关完整的参数用法，请参阅 [vLLM 文档](https://docs.vllm.ai/en/latest/configuration/engine_args/)。

## 访问模型

vLLM 提供了与 OpenAI 兼容的 API，因此你可以将任何兼容的客户端或界面连接到你的集群。一个流行的选择是 [Open WebUI](https://github.com/open-webui/open-webui)，它提供基于浏览器的聊天界面。

要将 Open WebUI 连接到你的 vLLM 端点：

1. 打开 **Settings** > **Admin Panel** > **Connections**
2. 点击 **Manage OpenAI API Connections** 上的 **+**
3. 将 **Connection Type** 设置为 **External**
4. 将 **URL** 设置为 `http://<MACHINE_1_IP>:7000/v1`
5. 在 **Auth** 下，从下拉菜单中选择 **None**
6. 将 **Model IDs** 留空，以自动发现该端点上的所有模型

> **查找 `<MACHINE_1_IP>`**：在机器 1 上，运行 `hostname -I | awk '{print $1}'` 来查找其本地 IP 地址。如果从机器 1 本身访问 Open WebUI，你可以使用 `http://localhost:7000/v1`。

![用于 vLLM 端点的 Open WebUI 连接设置](assets/openwebui-connection.png)

连接后，从 Open WebUI 的模型下拉菜单中选择模型并开始聊天。该模型现在正跨你的两个 Ryzen AI Halo 节点运行：

![在 Open WebUI 中与 Qwen3.5-397B 聊天](assets/openwebui-chat.png)

## 后续步骤

- **探索其他模型**：在 [Hugging Face](https://huggingface.co/models?&sort=trending) 上发现适合你集群组合 GPU 内存大小的新模型
- **扩展到四个节点**：添加另外两台 Ryzen AI Halo 系统作为额外的 Ray 工作节点，以便将模型分片到更多 GPU 上。这需要一台至少有四个端口的以太网交换机，每个节点占用一个端口。在每台新增的工作节点上执行[步骤 2：加入集群](#step-2-join-the-cluster-machine-2)，并相应地增大 `--tensor-parallel-size`
- **尝试其他并行策略**：vLLM 支持用于专家混合模型的[专家并行](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/)，以及用于提升吞吐量的[数据并行](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/)。尝试使用 `--enable-expert-parallel` 和 `--data-parallel-size`，为你的工作负载找到最佳配置