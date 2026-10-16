<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# 平台配置

本文档介绍了运行此 playbook 所需的平台配置。

## 前提条件

支持 ROCm 的 PyTorch 已预装在 AMD Ryzen™ AI Halo Developer Platform 上。对于所有其他设备，用户必须手动安装支持 ROCm 的 PyTorch。请参考适用于您操作系统的相应部分：

### Windows

| 组件          | 版本            | 备注                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 或更高版本  | 已预装在 AMD Ryzen AI Halo Developer Platform 上；必须在所有其他设备上手动安装 |

### Linux

| 组件          | 版本            | 备注                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 或更高版本  | 已预装在 AMD Ryzen AI Halo Developer Platform 上；必须在所有其他设备上手动安装 |

## 所需模型

以下模型已针对您的平台进行了测试和优化：

| 模型 | 参数量 | 大小 | 下载位置 |
|-------|------------|------|-------------------|
| **openai/gpt-oss-20b** | 20B | ~40GB | 已预装在 AMD Ryzen AI Halo Developer Platform 上；必须在所有其他设备上手动安装 |

模型可以从 Hugging Face 或 ModelScope 下载。加载模型时，所使用的平台会先检查对应的本地缓存；如果模型尚未缓存，则会自动下载。

Hugging Face 缓存目录：

- **Windows**：`C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**：`~/.cache/huggingface/hub/`

ModelScope 缓存目录：

- **Windows**：`C:\Users\<username>\.cache\modelscope\models\`
- **Linux**：`~/.cache/modelscope/models/`

请确保至少有 **50GB 可用空间** 用于模型存储。

## 网络要求

初始设置需要互联网连接，以便从 Hugging Face 或 ModelScope 下载模型。下载完成后，playbook 可以使用本地缓存离线运行。

- 首次下载模型可能需要 **5-10 分钟**，具体取决于模型大小和网络连接速度
- 模型会在本地缓存，无需重复下载
