<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **机器翻译。**本页面由英文自动翻译，未经人工审核。其中可能包含错误，某些说明、命令、下载内容、产品可用性或其他内容可能因语言或地区而异。如内容存在任何不一致或差异，应以英文原版 playbook 为准。
<!-- auto-translated-disclaimer:end -->

# 平台配置 — Lemonade Local AI

本文档描述了本剧本所假定的预安装软件、模型路径和特定平台的先决条件。

## 预安装软件

| 软件 | 版本 | 用途 |
|----------|---------|---------|
| Lemonade Server | 最新版本 | 具有 OpenAI 兼容 API 的本地 LLM 服务器 |
| Python | 3.10–3.13 | OpenAI Python 客户端示例所需 |

## 默认模型存储

通过 Lemonade 下载的模型使用 Hugging Face Hub 规范进行存储：

| 平台 | 默认路径 |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |
| Linux | `~/.cache/huggingface/hub/` |

要更改存储位置，请设置 `HF_HOME` 环境变量。

## 硬件要求

| 硬件目标 | 要求 |
|----------------|-------------|
| **CPU** | 任何现代 x86-64 处理器（AMD 或 Intel） |
| **GPU (Vulkan)** | 任何支持 Vulkan 驱动程序的 GPU |
| **GPU (ROCm)** | AMD Radeon RX 7000/9000 系列或 Radeon PRO W7000 系列；AMD Ryzen AI MAX+ Pro 395 |
| **NPU** | AMD Ryzen AI 300 系列处理器，Windows 11 |

## 网络要求

- 首次下载模型需要互联网连接（根据模型不同，大小为 1–25 GB）
- 模型下载完成后无需互联网连接