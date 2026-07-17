<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# 使用 RCCL 集群两台 Ryzen™ AI Halo

## 概述

您的 Ryzen™ AI Halo 已经能够在本地运行大型语言模型。集群功能通过本地网络将多台系统的 GPU 内存合并，使您能够访问更大的模型，获得更强的推理能力、更好的代码生成能力以及更深入的多语言理解能力，且完全在您自己的硬件上运行。

本 playbook 将教您如何使用 RCCL（ROCm Communication Collectives Library）通过 vLLM 集群两台 Ryzen AI Halo 系统，并在两台机器上以 ROCm 加速运行 Qwen3.5-397B（一个拥有 3970 亿参数的模型）。

## 您将学到的内容

- 如何扩展 Ryzen AI Halo 系统上的 VRAM 分配
- 使用 ROCm 支持启动 vLLM
- 为两台 Ryzen AI Halo 系统之间的多节点张量并行推理配置 RCCL
- 在两台联网的 Ryzen AI Halo 系统上运行 3970 亿参数模型

## 前提条件

### 硬件

本 playbook 需要两台 Ryzen AI Halo 设备和一台以太网交换机，采用星形拓扑连接，每台设备直接通过网线连接到交换机。

| 组件 | 数量 | 描述 |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | 构成集群的计算节点 |
| 10Gbps 以太网交换机 | 1 | 用于实现多节点 Ryzen AI Halo 通信的中央交换机（至少 2 个端口） |
| 以太网线缆 | 2 | 将每台 Halo 设备连接到交换机（推荐使用 Cat 7 或更高规格） |

> **注意**：连接两台 Ryzen AI Halo 设备需要两个以太网交换机端口。如果您从独立的客户端机器（而非其中一台 Halo 设备）访问模型，则还需要第三个端口。

### 软件
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## 物理硬件设置

> **注意**：在机器 1 和机器 2 上均需完成此步骤。

使用 Cat 7（或更高规格）网线将每台 Ryzen AI Halo 设备连接到以太网交换机。这将建立用于节点间高速通信的 10Gbps 链路。

### 1. 确定网络接口

在每台机器上，找到其网络接口名称并记录下来（在后续说明中将以 `IFNAME` 表示）。运行：

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

这将直接打印接口名称，例如：

```bash
enp191s0
```

### 2. 验证网络链路速度

通过检查接口速度，确认链路已激活并以全速运行：

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注意**：将 `<IFNAME>` 替换为[1. 确定网络接口](#1-determine-network-interfaces)中输出的接口名称

您应该看到速度为 `10000Mb/s`：

```bash
	Speed: 10000Mb/s
```

> **注意**：如果速度低于 `10000Mb/s` 或链路未能建立，请检查网线连接并确认交换机端口已设置为 10Gbps。某些交换机需要禁用自动协商并手动设置链路速度；请参阅您的交换机文档。

## 扩展 VRAM 分配

> **注意**：在机器 1 和机器 2 上均需完成此步骤。

### 运行大型模型的内存配置

在 Linux 上，ROCm 使用共享系统内存池，该内存池默认配置为系统内存的一半。

可以通过更改内核的 Translation Table Manager（TTM）页面设置来增加此数量，具体操作如下。AMD 建议在 BIOS 中将最小专用 VRAM 设置为 0.5 GB。

* 安装 pipx 工具并将 pipx 安装的 wheel 路径添加到系统搜索路径中。

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* 从 PyPI 安装 amd-debug-tools wheel。
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

## vLLM 容器初始化

> **注意**：在机器 1 和机器 2 上均需完成此步骤。

您的 Ryzen AI Halo 随附了打包在预构建容器镜像中的 vLLM，您可以使用 Podman（一款免费开源的容器工具）来运行它。

### 1. 创建模型下载目录

在本 playbook 中提供 Qwen3.5-397B 模型服务时，vLLM 将自动将模型权重下载到您的系统。为确保这些权重可从容器内部访问，请先创建一个容器可以挂载的 models 目录：

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. 启动 vLLM 容器

以下命令将启动容器并进入交互式 shell。它会挂载您刚刚创建的 models 目录，并将您的 `IFNAME` 传递给 `NCCL_SOCKET_IFNAME` 和 `GLOO_SOCKET_IFNAME`，告知 RCCL（vLLM 用于协调集群中 GPU 的库）使用哪个接口。

使用以下命令启动容器：

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **注意**：将 `<IFNAME>` 替换为[1. 确定网络接口](#1-determine-network-interfaces)中输出的接口名称

## 在集群上运行模型

vLLM 使用 Ray 编排集群，并使用 RCCL 处理节点间的 GPU 到 GPU 通信。一台机器充当**头节点**（机器 1），负责协调推理；另一台作为**工作节点**（机器 2）加入，贡献其 GPU 内存和算力。

> **注意**：Ray 是 vLLM 的可选依赖项，仅在预配置的 Podman 容器中可用。

启动时，vLLM 使用张量并行将模型分片到两个节点上。加载完成后，推理过程就如同在单个加速器上运行一样。

### 步骤 1：启动 Ray 头节点（机器 1）

在机器 1 上，启动 Ray 头节点以初始化集群：

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **查找 `<MACHINE_1_IP>`**：在机器 1 上，运行 `hostname -I | awk '{print $1}'` 以查找其本地 IP 地址。

### 步骤 2：加入集群（机器 2）

在机器 2 上，连接到头节点以组建集群：

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **查找 `<MACHINE_2_IP>`**：在机器 2 上，运行 `hostname -I | awk '{print $1}'` 以查找其本地 IP 地址。

### 步骤 3：提供模型服务（机器 1）

在机器 1 上，启动 vLLM 服务器。这将自动下载模型并开始在两个节点上提供服务：

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
| `--host` | 服务器绑定的 IP 地址（`0.0.0.0` 表示所有接口） |
| `--max-model-len` | 最大上下文长度（以 token 为单位） |
| `--gpu-memory-utilization` | 分配的 GPU 内存比例（0.0–1.0） |
| `--dtype` | 模型权重的数据类型 |
| `--tensor-parallel-size` | 模型分片所跨的 GPU 数量（设置为集群中的 GPU 总数） |
| `--distributed-executor-backend` | 多节点执行的后端（集群部署使用 `ray`） |
| `--enforce-eager` | 禁用 CUDA 图编译以提高兼容性 |
| `--language-model-only` | 跳过加载辅助模型组件（例如视觉编码器） |
| `--reasoning-parser` | 为模型启用结构化推理输出解析 |

有关完整参数用法，请参阅 [vLLM 文档](https://docs.vllm.ai/en/latest/configuration/engine_args/)。

## 访问模型

vLLM 提供与 OpenAI 兼容的 API，因此您可以将任何兼容的客户端或界面连接到您的集群。一个常用选项是 [Open WebUI](https://github.com/open-webui/open-webui)，它提供基于浏览器的聊天界面。

要将 Open WebUI 连接到您的 vLLM 端点：

1. 打开**设置** > **管理面板** > **连接**
2. 点击**管理 OpenAI API 连接**上的 **+**
3. 将**连接类型**设置为**外部**
4. 将 **URL** 设置为 `http://<MACHINE_1_IP>:7000/v1`
5. 在 **Auth** 下，从下拉菜单中选择**无**
6. 将**模型 ID** 留空以自动发现端点中的所有模型

> **查找 `<MACHINE_1_IP>`**：在机器 1 上，运行 `hostname -I | awk '{print $1}'` 以查找其本地 IP 地址。如果从机器 1 本身访问 Open WebUI，可以使用 `http://localhost:7000/v1`。

![vLLM 端点的 Open WebUI 连接设置](assets/openwebui-connection.png)

连接后，从 Open WebUI 的模型下拉菜单中选择模型并开始聊天。该模型现在正在您的两台 Ryzen AI Halo 节点上运行：

![在 Open WebUI 中与 Qwen3.5-397B 聊天](assets/openwebui-chat.png)

## 后续步骤

- **探索其他模型**：在 [Hugging Face](https://huggingface.co/models?&sort=trending) 上发现适合您集群组合 GPU 内存的新模型
- **扩展至四节点**：再添加两台 Ryzen AI Halo 系统作为额外的 Ray 工作节点，将模型分片到更多 GPU 上。这需要一台至少有四个端口的以太网交换机，每个节点各占一个端口。在每台额外的工作节点上按照[步骤 2：加入集群](#step-2-join-the-cluster-machine-2)操作，并相应增加 `--tensor-parallel-size`
- **尝试其他并行策略**：vLLM 支持针对混合专家模型的[专家并行](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/)以及用于提高吞吐量的[数据并行](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/)。尝试使用 `--enable-expert-parallel` 和 `--data-parallel-size` 为您的工作负载找到最佳配置