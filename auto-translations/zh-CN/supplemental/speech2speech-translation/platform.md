<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **机器翻译。**本页面由英文自动翻译，未经人工审核。其中可能包含错误，某些说明、命令、下载内容、产品可用性或其他内容可能因语言或地区而异。如内容存在任何不一致或差异，应以英文原版 playbook 为准。
<!-- auto-translated-disclaimer:end -->

# 平台配置

本文档介绍了运行此 playbook 所需的平台配置。

## 前提条件

支持 ROCm 的 PyTorch 已预装在 AMD Ryzen™ AI Halo Developer Platform 上。对于所有其他设备，用户必须手动安装支持 ROCm 的 PyTorch。请参阅适用于你操作系统的相应部分：

### Windows

| 组件          | 版本            | 说明                               |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 或更新版本    | 已预装在 AMD Ryzen AI Halo Developer Platform 上；在所有其他设备上必须手动安装 |

### Linux

| 组件          | 版本            | 说明                               |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 或更新版本    | 已预装在 AMD Ryzen AI Halo Developer Platform 上；在所有其他设备上必须手动安装 |

## 所需模型

以下模型已针对你的平台进行了测试和优化：

| 模型 | 参数量 | 大小 | 下载位置 |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2.3B | ~10GB | 已预装在 AMD Ryzen AI Halo Developer Platform 上；在所有其他设备上必须手动安装 |

模型将自动下载到 Hugging Face 缓存目录：
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

请确保至少有 **20GB 的可用空间** 用于存储模型。

## 网络要求

初始设置需要联网以从 Hugging Face 下载模型。下载完成后，该 playbook 即可离线运行。

- 首次下载模型可能需要 **5-10 分钟**，具体时间取决于模型大小和网络连接速度
- 模型会缓存在本地，无需重复下载