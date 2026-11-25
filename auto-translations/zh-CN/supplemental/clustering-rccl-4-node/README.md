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

# 使用 RCCL 集群化四台 Ryzen™ AI Halo

## 概述

你的 Ryzen™ AI Halo 已经能够在本地运行大语言模型。集群化则更进一步，通过本地网络将多台系统的 GPU 显存整合在一起，让你可以访问更大规模的模型，获得更强的推理能力、更好的代码生成能力以及更深入的多语言理解能力，而这一切完全运行在你自己的硬件上。

本实践指南将教你如何使用 RCCL（ROCm Communication Collectives Library）配合 vLLM 集群化四台 Ryzen AI Halo 系统，并借助 ROCm 加速，在全部四台机器上运行 Qwen3.5-397B——一个拥有 397B 参数的模型。

## 你将学到的内容

- 如何在 Ryzen AI Halo 系统上扩展 VRAM 分配
- 如何启动支持 ROCm 的 vLLM
- 如何为跨四台 Ryzen AI Halo 系统的多节点张量并行推理配置 RCCL
- 如何在四台联网的 Ryzen AI Halo 系统上运行一个 397B 参数的模型

## 前提条件

### 硬件

本实践指南需要四台 Ryzen AI Halo 设备和一台以太网交换机，以星型拓扑连接，每台设备直接接入交换机。

| 组件 | 数量 | 说明 |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | 构成集群的计算节点 |
| 10Gbps 以太网交换机 | 1 | 用于实现多节点 Ryzen AI Halo 通信的中心交换机（至少 4 个端口） |
| 以太网线缆 | 4 | 将每台 Halo 设备连接到交换机（建议使用 Cat 7 及以上规格） |

> **注意**：连接四台 Ryzen AI Halo 设备需要四个以太网交换机端口。如果你从单独的客户端机器而非其中一台 Halo 设备访问模型，则需要第五个端口。

### 软件
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## 物理硬件设置

> **注意**：请在全部四台机器（机器 1 至机器 4）上完成此步骤。

使用 Cat 7（或更高规格）线缆将每台 Ryzen AI Halo 设备连接到以太网交换机。这将建立起用于节点间高速通信的 10Gbps 链路。

### 1. 确定网络接口

在每台机器上，找到其网络接口的名称并记录下来（在后续说明中将以 `IFNAME` 指代）。运行：

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

这将直接输出接口名称，例如：

```bash
enp191s0
```

### 2. 验证网络链路速度

通过检查接口速度来确认链路处于活动状态且运行在全速：

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注意**：将 `<IFNAME>` 替换为 [1. 确定网络接口](#1-determine-network-interfaces) 中输出的接口名称

你应该看到速度为 `10000Mb/s`：

```bash
	Speed: 10000Mb/s
```

> **注意**：如果速度低于 `10000Mb/s` 或链路未建立，请检查线缆连接，并确认交换机端口已设置为 10Gbps。部分交换机需要禁用自动协商并手动设置链路速度，请参阅你的交换机文档。

## 扩展 VRAM 分配

> **注意**：请在全部四台机器（机器 1 至机器 4）上完成此步骤。

### 运行大模型的内存配置

在 Linux 上，ROCm 使用共享系统内存池，该内存池默认配置为系统内存的一半。

可以通过以下说明更改内核的转换表管理器（Translation Table Manager，TTM）页面设置来增加这一数量。AMD 建议在 BIOS 中设置最小专用 VRAM（0.5 GB）。

* 安装 pipx 工具，并将 pipx 安装的 wheel 包路径添加到系统搜索路径中。

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* 从 PyPI 安装 amd-debug-tools wheel 包。
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

## vLLM 容器初始化

> **注意**：请在全部四台机器（机器 1 至机器 4）上完成此步骤。

你的 Ryzen AI Halo 随附了打包在预构建容器镜像中的 vLLM，你可以使用 Podman（一个免费开源的容器工具）来运行它。

### 1. 创建模型下载目录

当你在本实践指南中为 Qwen3.5-397B 模型提供服务时，vLLM 会自动将模型权重下载到你的系统中。为确保这些权重可以从容器内部访问，首先创建一个容器可以挂载的 models 目录：

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. 启动 vLLM 容器

下面的命令将启动容器并进入交互式 shell。它会挂载你刚刚创建的 models 目录，并将你的 `IFNAME` 传递给 `NCCL_SOCKET_IFNAME` 和 `GLOO_SOCKET_IFNAME`，告诉 RCCL（vLLM 用于协调跨集群 GPU 的库）使用哪个接口。

使用以下命令启动容器：

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **注意**：将 `<IFNAME>` 替换为 [1. 确定网络接口](#1-determine-network-interfaces) 中输出的接口名称

## 在集群上运行模型

vLLM 使用 Ray 来编排集群，并使用 RCCL 来处理跨节点的 GPU 间通信。一台机器（机器 1）作为头节点，负责协调推理。其余三台机器（机器 2、3 和 4）作为工作节点加入，贡献各自的 GPU 显存和计算能力。

> **注意**：Ray 是 vLLM 的一个可选依赖项，仅在预先配置好的 Podman 容器内部可用。

在启动时，vLLM 使用张量并行技术将模型分片到全部四个节点上。加载完成后，推理过程就如同在单个加速器上运行一样。

#### 防止 Ray 出现 OOM 错误

默认情况下，Ray 会监控每个节点上的主机内存，当内存使用率超过 95% 时，会终止占用内存最大的进程。在你的 Ryzen™ AI Halo 上，GPU 和主机共享同一内存池，因此加载模型可能会触发 `ray.exceptions.OutOfMemoryError` 并终止工作进程。

为避免这种情况，我们将在每台机器启动并加入集群之前，导出 `RAY_memory_monitor_refresh_ms=0`。
### 第 1 步：启动 Ray 头节点（机器 1）

在机器 1 上，启动 Ray 头节点以初始化集群：

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **查找 `<MACHINE_1_IP>`**：在机器 1 上运行 `hostname -I | awk '{print $1}'` 来查找其本地 IP 地址。

### 第 2 步：加入集群（机器 2、3 和 4）

在机器 2、3 和 4 上，分别连接到头节点以组成集群：

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_N_IP> --num-gpus=1
```

> **查找 `<MACHINE_N_IP>`**：在每台工作节点机器上运行 `hostname -I | awk '{print $1}'` 来查找其本地 IP 地址。

### 第 3 步：提供模型服务（机器 1）

在机器 1 上，启动 vLLM 服务器。它会自动下载模型，并开始在全部四个节点上提供服务：

```bash
vllm serve Qwen/Qwen3.5-397B-A17B-GPTQ-Int4 \
  --port 7000 \
  --host 0.0.0.0 \
  --max-model-len 131072 \
  --gpu-memory-utilization 0.8 \
  --dtype float16 \
  --tensor-parallel-size 4 \
  --distributed-executor-backend ray \
  --enforce-eager \
  --language-model-only \
  --reasoning-parser qwen3
```

#### 参数参考

| 标志 | 用途 |
|------|---------|
| `--port` | 用于提供 HTTP API 的端口 |
| `--host` | 服务器绑定的 IP 地址（`0.0.0.0` 表示绑定所有接口） |
| `--max-model-len` | 最大上下文长度（以 token 为单位） |
| `--gpu-memory-utilization` | 分配的 GPU 内存比例（0.0–1.0） |
| `--dtype` | 模型权重的数据类型 |
| `--tensor-parallel-size` | 用于切分模型的 GPU 数量（设置为集群中的 GPU 总数） |
| `--distributed-executor-backend` | 多节点执行所用的后端（集群部署使用 `ray`） |
| `--enforce-eager` | 禁用 CUDA 图编译以确保兼容性 |
| `--language-model-only` | 跳过加载辅助模型组件（例如视觉编码器） |
| `--reasoning-parser` | 为模型启用结构化推理输出解析 |

有关完整的参数用法，请参阅 [vLLM 文档](https://docs.vllm.ai/en/latest/configuration/engine_args/)。

## 访问模型

vLLM 暴露了一个兼容 OpenAI 的 API，因此你可以将任何兼容的客户端或界面连接到你的集群。一个常见的选择是 [Open WebUI](https://github.com/open-webui/open-webui)，它提供了一个基于浏览器的聊天界面。

要将 Open WebUI 连接到你的 vLLM 端点：

1. 打开 **Settings** > **Admin Panel** > **Connections**
2. 点击 **Manage OpenAI API Connections** 上的 **+**
3. 将 **Connection Type** 设置为 **External**
4. 将 **URL** 设置为 `http://<MACHINE_1_IP>:7000/v1`
5. 在 **Auth** 下，从下拉菜单中选择 **None**
6. 将 **Model IDs** 留空，以自动发现该端点的所有模型

> **查找 `<MACHINE_1_IP>`**：在机器 1 上运行 `hostname -I | awk '{print $1}'` 来查找其本地 IP 地址。如果你是从机器 1 本身访问 Open WebUI，可以使用 `http://localhost:7000/v1`。

![用于 vLLM 端点的 Open WebUI 连接设置](assets/openwebui-connection.png)

连接完成后，在 Open WebUI 的模型下拉菜单中选择模型，开始聊天。此时，模型正运行在你全部四个 Ryzen AI Halo 节点之上：

![在 Open WebUI 中与 Qwen3.5-397B 聊天](assets/openwebui-chat.png)

## 后续步骤

- **探索其他模型**：在 [Hugging Face](https://huggingface.co/models?&sort=trending) 上发现适合你集群 GPU 显存总量的新模型
- **扩展到四个节点以上**：添加更多 Ryzen AI Halo 系统作为额外的 Ray 工作节点，以便在更多 GPU 上切分模型。在每台新增的工作节点上执行 [第 2 步：加入集群（机器 2、3 和 4）](#step-2-join-the-cluster-machines-2-3-and-4)，并相应地增大 `--tensor-parallel-size`
- **尝试其他并行策略**：vLLM 支持用于混合专家模型的 [专家并行](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/)，以及用于提高吞吐量的 [数据并行](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/)。尝试使用 `--enable-expert-parallel` 和 `--data-parallel-size`，为你的工作负载找到最佳配置