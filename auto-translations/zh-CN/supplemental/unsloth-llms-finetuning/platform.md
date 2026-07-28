<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **机器翻译。**本页面由英文自动翻译而成,尚未经过人工审核。其中可能存在错误,部分步骤、命令、下载内容或产品的可用性在您所在的语言或地区可能有所不同。如发现任何问题,请以英文原版 playbook 为准。
<!-- auto-translated-disclaimer:end -->

# 平台配置

本文档描述了运行此手册所需的预期平台配置。

## 前提条件

AMD Ryzen™ AI Halo Developer Platform 已预装支持 ROCm 的 PyTorch。对于所有其他设备，用户必须手动安装支持 ROCm 的 PyTorch。请参阅适用于您操作系统的相关部分：


### Windows

| 组件     | 版本         | 说明                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | 在 AMD Ryzen AI Halo Developer Platform 上已预装；在所有其他设备上必须手动安装 |


### Linux

| 组件     | 版本         | 说明                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | 在 AMD Ryzen AI Halo Developer Platform 上已预装；在所有其他设备上必须手动安装 |


## 所需模型

以下模型已针对您的平台进行了测试和优化：

| 模型 | 参数 | 大小 | 下载位置 |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | 从 HF 下载

模型将自动下载到 Hugging Face 缓存目录：`~/.cache/huggingface/hub/`

请确保至少有 **20GB 可用空间** 用于模型存储。

## 网络要求

初始设置需要联网以从 Hugging Face 下载模型。下载完成后，该手册可离线运行。

- 首次下载模型可能需要 **5-10 分钟**，具体取决于模型大小和网络连接速度
- 模型会在本地缓存，无需重复下载