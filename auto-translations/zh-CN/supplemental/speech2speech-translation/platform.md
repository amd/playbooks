<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **机器翻译。**本页面由英文自动翻译而成,尚未经过人工审核。其中可能存在错误,部分步骤、命令、下载内容或产品的可用性在您所在的语言或地区可能有所不同。如发现任何问题,请以英文原版 playbook 为准。
<!-- auto-translated-disclaimer:end -->

# 平台配置

本文档介绍了运行此 playbook 所需的平台配置。

## 前提条件

带有 ROCm 支持的 PyTorch 已预装在 AMD Ryzen™ AI Halo Developer Platform 上。对于所有其他设备，用户必须手动安装带有 ROCm 支持的 PyTorch。请参阅适用于您操作系统的相关部分：

### Windows

| 组件     | 版本         | 说明                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 或更高版本    | 已预装在 AMD Ryzen AI Halo Developer Platform 上；必须在所有其他设备上手动安装 |

### Linux

| 组件     | 版本         | 说明                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 或更高版本    | 已预装在 AMD Ryzen AI Halo Developer Platform 上；必须在所有其他设备上手动安装 |

## 所需模型

以下模型已针对您的平台进行了测试和优化：

| 模型 | 参数 | 大小 | 下载位置 |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2.3B | ~10GB | 已预装在 AMD Ryzen AI Halo Developer Platform 上；必须在所有其他设备上手动安装 |

模型将自动下载到 Hugging Face 缓存目录：
- **Windows**：`C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**：`~/.cache/huggingface/hub/`

请确保至少有 **20GB 的可用空间** 用于模型存储。

## 网络要求

初始设置需要互联网访问才能从 Hugging Face 下载模型。下载完成后，该 playbook 可以离线运行。

- 首次下载模型可能需要 **5-10 分钟**，具体取决于模型大小和连接速度
- 模型会缓存在本地，无需重新下载