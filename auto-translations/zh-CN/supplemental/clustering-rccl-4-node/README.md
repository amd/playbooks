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

您的 Ryzen™ AI Halo 已经能够在本地运行大语言模型。通过集群化，可以进一步在本地网络上整合多台系统的 GPU 内存，使您能够运行更大规模、具备更强推理能力、更优代码生成能力以及更深入多语言理解能力的模型，而这一切完全在您自己的硬件上完成。

本实践指南将教您如何使用 RCCL（ROCm Communication Collectives Library）将四台 Ryzen AI Halo 系统组建成集群，并结合 vLLM，在所有四台机器上通过 ROCm 加速运行拥有 397B 参数的 Qwen3.5-397B 模型。

## 您将学到的内容

- 如何在 Ryzen AI Halo 系统上扩展 VRAM 分配
- 如何启动支持 ROCm 的 vLLM
- 如何为跨四台 Ryzen AI Halo 系统的多节点张量并行推理配置 RCCL
- 如何在四台联网的 Ryzen AI Halo 系统上运行拥有 397B 参数的模型

## 前提条件

### 硬件

本实践指南需要四台 Ryzen AI Halo 设备和一台以太网交换机，以星形拓扑连接，每台设备均直接通过网线连接到交换机。

| 组件 | 数量 | 说明 |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | 组成集群的计算节点 |
| 10Gbps 以太网交换机 | 1 | 支持多节点 Ryzen AI Halo 通信的中心交换机（至少 4 个端口） |
| 以太网线缆 | 4 | 将每台 Halo 设备连接到交换机（建议使用 Cat 7 或更高规格） |

> **注意**：连接四台 Ryzen AI Halo 设备需要四个以太网交换机端口。如果您从单独的客户端机器而非其中一台 Halo 设备访问模型，则需要第五个端口。

### 软件
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## 物理硬件设置

> **注意**：请在所有四台机器（机器 1 至机器 4）上完成此步骤。

使用 Cat 7（或更高规格）网线将每台 Ryzen AI Halo 设备连接到以太网交换机。这将建立用于节点间高速通信的 10Gbps 链路。

### 1. 确定网络接口

在每台机器上，查找并记录其网络接口的名称（后续说明中将其称为 `IFNAME`）。运行：

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

此命令将直接打印接口名称，例如：

```bash
enp191s0
```

### 2. 验证网络链路速率

通过检查接口的速率，确认链路处于活动状态并以全速运行：

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注意**：将 `<IFNAME>` 替换为[1. 确定网络接口](#1-determine-network-interfaces)中输出的接口名称

您应当看到速率为 `10000Mb/s`：

```bash
	Speed: 10000Mb/s
```

> **注意**：如果速率低于 `10000Mb/s` 或链路未建立，请检查线缆连接，并确认交换机端口已设置为 10Gbps。部分交换机需要禁用自动协商并手动设置链路速率；请参阅您交换机的相关文档。

## 扩展 VRAM 分配

> **注意**：请在所有四台机器（机器 1 至机器 4）上完成此步骤。

### 运行大模型的内存配置

在 Linux 上，ROCm 使用共享系统内存池，该内存池默认配置为系统内存的一半。

可以通过更改内核的转换表管理器（Translation Table Manager，TTM）页面设置来增加此数值，具体说明如下。AMD 建议在 BIOS 中将最小专用 VRAM 设置为 0.5 GB。

* 安装 pipx 工具，并将 pipx 安装的 wheel 包路径添加到系统搜索路径中。

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* 从 PyPI 安装 amd-debug-tools wheel 包。
  ```bash
  pipx install amd-debug-tools
  ```

* 运行 amd-ttm 工具以查询当前的共享内存设置。
  ```bash
  amd-ttm
  ```

* 将共享内存设置重新配置为 **120 GB**：
  ```bash
  amd-ttm --set 120
  ```

* 重启系统以使更改生效。

## vLLM 容器初始化

> **注意**：请在所有四台机器（机器 1 至机器 4）上完成此步骤。

您的 Ryzen AI Halo 随附一个预构建的容器镜像，其中已打包了 vLLM，您可以使用 Podman（一款免费开源的容器工具）来运行它。

### 1. 创建模型下载目录

当您在本实践指南中提供 Qwen3.5-397B 模型服务时，vLLM 会自动将模型权重下载到您的系统中。为确保这些权重可在容器内访问，请先创建一个可供容器挂载的模型目录：

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. 启动 vLLM 容器

下面的命令将启动容器，并将您带入交互式 shell。它会挂载您刚创建的模型目录，并将您的 `IFNAME` 传递给 `NCCL_SOCKET_IFNAME` 和 `GLOO_SOCKET_IFNAME`，以告知 RCCL（vLLM 用于在集群中协调 GPU 的库）应使用哪个接口。

使用以下命令启动容器：

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **注意**：将 `<IFNAME>` 替换为[1. 确定网络接口](#1-determine-network-interfaces)中输出的接口名称

## 在集群上运行模型

vLLM 使用 Ray 来编排集群，并使用 RCCL 处理跨节点的 GPU 间通信。其中一台机器（机器 1）作为头节点，负责协调推理。其余三台机器（机器 2、3 和 4）作为工作节点加入集群，贡献各自的 GPU 内存和计算资源。

> **注意**：Ray 是 vLLM 的一个可选依赖项，仅在预配置的 Podman 容器内可用。

启动时，vLLM 会使用张量并行技术将模型分片到所有四个节点上。加载完成后，推理过程将如同在单个加速器上运行一样进行。

#### 防止 Ray 内存不足（OOM）错误

默认情况下，Ray 会监控每个节点的主机内存，并在内存使用率超过 95% 时终止占用内存最大的进程。在您的 Ryzen™ AI Halo 上，GPU 与主机共享同一块内存池，因此加载模型可能会触发 `ray.exceptions.OutOfMemoryError` 并终止工作进程。

为避免这种情况，我们将在每台机器启动并加入集群之前，导出环境变量 `RAY_memory_monitor_refresh_ms=0`。
### 第 1 步：启动 Ray 头节点（机器 1）

在机器 1 上，启动 Ray 头节点以初始化集群：

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **查找 `<MACHINE_1_IP>`**：在机器 1 上，运行 `hostname -I | awk '{print $1}'` 以查找其本地 IP 地址。

### 第 2 步：加入集群（机器 2、3 和 4）

在机器 2、3 和 4 中的每一台上，连接到头节点以组成集群：

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_N_IP> --num-gpus=1
```

> **查找 `<MACHINE_N_IP>`**：在每台工作机器上，运行 `hostname -I | awk '{print $1}'` 以查找其本地 IP 地址。

### 第 3 步：提供模型服务（机器 1）

在机器 1 上，启动 vLLM 服务器。这将自动下载模型，并开始在所有四个节点上提供服务：

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
| `--port` | 提供 HTTP API 服务的端口 |
| `--host` | 服务器绑定的 IP 地址（`0.0.0.0` 表示所有接口） |
| `--max-model-len` | 最大上下文长度（以 token 为单位） |
| `--gpu-memory-utilization` | 分配的 GPU 内存比例（0.0–1.0） |
| `--dtype` | 模型权重的数据类型 |
| `--tensor-parallel-size` | 用于分片模型的 GPU 数量（设置为集群中的 GPU 总数） |
| `--distributed-executor-backend` | 多节点执行的后端（集群部署使用 `ray`） |
| `--enforce-eager` | 禁用 CUDA 图编译以确保兼容性 |
| `--language-model-only` | 跳过加载辅助模型组件（例如视觉编码器） |
| `--reasoning-parser` | 为模型启用结构化推理输出解析 |

有关完整的参数用法，请参阅 [vLLM 文档](https://docs.vllm.ai/en/latest/configuration/engine_args/)。

## 访问模型

vLLM 提供了与 OpenAI 兼容的 API，因此您可以将任何兼容的客户端或界面连接到您的集群。一个常用选项是 [Open WebUI](https://github.com/open-webui/open-webui)，它提供了基于浏览器的聊天界面。

要将 Open WebUI 连接到您的 vLLM 端点：

1. 打开 **设置** > **管理员面板** > **连接**
2. 在 **管理 OpenAI API 连接** 上点击 **+**
3. 将 **连接类型** 设置为 **外部**
4. 将 **URL** 设置为 `http://<MACHINE_1_IP>:7000/v1`
5. 在 **身份验证** 下，从下拉菜单中选择 **无**
6. 保持 **模型 ID** 为空，以自动发现来自该端点的所有模型

> **查找 `<MACHINE_1_IP>`**：在机器 1 上，运行 `hostname -I | awk '{print $1}'` 以查找其本地 IP 地址。如果要从机器 1 本身访问 Open WebUI，可以使用 `http://localhost:7000/v1`。

![用于 vLLM 端点的 Open WebUI 连接设置](assets/openwebui-connection.png)

连接后，从 Open WebUI 的模型下拉菜单中选择模型并开始聊天。该模型现在正在您所有四个 Ryzen AI Halo 节点上运行：

![在 Open WebUI 中与 Qwen3.5-397B 聊天](assets/openwebui-chat.png)

## 后续步骤

- **探索其他模型**：在 [Hugging Face](https://huggingface.co/models?&sort=trending) 上发现适合您集群合并 GPU 内存容量的新模型
- **扩展到四个节点以上**：添加更多 Ryzen AI Halo 系统作为额外的 Ray 工作节点，以在更多 GPU 上分片模型。在每台额外的工作机器上执行[第 2 步：加入集群](#step-2-join-the-cluster-machines-2-3-and-4)，并相应增加 `--tensor-parallel-size`
- **尝试其他并行策略**：vLLM 支持用于混合专家模型的[专家并行](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/)以及用于提升吞吐量的[数据并行](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/)。尝试使用 `--enable-expert-parallel` 和 `--data-parallel-size` 来为您的工作负载找到最佳配置