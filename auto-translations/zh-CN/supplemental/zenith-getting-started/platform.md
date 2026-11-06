<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **机器翻译。**本页面由英文自动翻译，未经人工审核。其中可能包含错误，某些说明、命令、下载内容、产品可用性或其他内容可能因语言或地区而异。如内容存在任何不一致或差异，应以英文原版 playbook 为准。
<!-- auto-translated-disclaimer:end -->

# 平台配置 — Windows Ryzen AI Halo（Project Zenith）

本文档描述了本实战手册的预装软件和平台假设。仅适用于搭载 Microsoft Project Zenith 的 Ryzen AI Halo 的 **Windows** 镜像。

## AMD AI 技术栈

| 软件 | 版本 | 用途 |
|----------|---------|---------|
| Lemonade Server | 最新版本 | 具有 OpenAI 兼容 API 的本地 LLM 服务器。为所有用户安装。不会在登录时启动。未预装任何模型。 |
| ComfyUI Desktop | 最新版本 | 节点图式图像与扩散工作流。内置自有的 Python 和 ROCm 运行时。 |
| PyTorch（ROCm） | torch、torchvision、torchaudio，搭配 `rocm-sdk-devel` 7.14.0 | GPU 加速的 PyTorch，离线安装到系统 Python 中 |

## Project Zenith 工具链

| 软件 | 版本 | 备注 |
|----------|---------|-------|
| Python | 3.14.7 | 系统 Python；承载 ROCm PyTorch 技术栈 |
| PowerShell | 7.6.8 | 默认终端配置文件 |
| Intelligent Terminal | 预览版 | 首次登录时按用户安装 |
| GitHub Copilot CLI | 1.0.94 | 机器级安装；拥有专属终端配置文件 |
| GitHub Copilot（应用） | 最新版本 | 已移除桌面快捷方式；从开始菜单启动 |
| WSL（含 Ubuntu） | 26.04.1 | 首次登录时按用户创建副本（约 1.46 GB） |
| Node.js + NVM for Windows | 1.2.2（nvm） | nvm 仅为第一个用户账户安装 |
| uv | 最新版本 | Python 包与环境管理器 |
| PowerToys | 0.101 | 按用户注册命令面板 |
| .NET SDK | 10 | |
| Windows App CLI（`winapp`） | 最新版本 | |
| Git、Visual Studio Code | 最新版本 | |
| GitHub CLI、Azure CLI | 最新版本 | |
| Oh My Posh、Coreutils for Windows | 最新版本 | 注册到每个用户的 PowerShell 配置文件中 |
| OpenSSH Server | 内置 | 已安装；默认情况下 `sshd` 服务已禁用并停止 |

## 预配置的 Windows 设置

| 设置 | 值 |
|---------|-------|
| 长路径 | 已在机器级启用（`LongPathsEnabled = 1`） |
| 文件资源管理器 | 标题栏中显示完整路径 |
| 外观 | 为新用户设置深色模式 |
| 字体 | Cascadia Mono NF、Cascadia Mono NF Italic、Cascadia Code NF |
| 终端默认配置文件 | PowerShell 7 |
| 任务栏固定项 | Windows Terminal、Visual Studio Code、AMD Ryzen AI Developer Center |

## 本地服务器端点

| 属性 | 值 |
|----------|-------|
| 基础 URL | `http://localhost:13305/v1` |
| 备用路径前缀 | `http://localhost:13305/api/v1` |
| 身份验证 | 默认无需身份验证。需要非空密钥的应用可接受任意占位符。 |
| 健康检查 | `http://localhost:13305/api/v1/health` |
| 模型列表 | `http://localhost:13305/api/v1/models` |

## 模型

该镜像未预装任何模型。可通过 Lemonade 的模型管理器或 CLI 按需下载。

在该平台上进行智能体相关工作时，推荐的起点模型如下：

| 模型 | 类型 | 备注 |
|-------|------|-------|
| Qwen3.8 27B | 稠密模型 | 单 token 推理能力更强；生成速度较慢，因为吞吐量受带宽限制 |
| Qwen3.6 35B MTP | 混合专家模型 | 在相近规模下交互响应更快；通常是智能体工作流的更优默认选择 |

### 默认模型存储

通过 Lemonade 下载的模型使用 Hugging Face Hub 规范：

| 平台 | 默认路径 |
|----------|-------------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |

设置 `HF_HOME` 环境变量以更改存储位置。

## 硬件要求

| 硬件目标 | 要求 |
|----------------|-------------|
| **设备** | AMD Ryzen AI Halo（Gorgon Halo），Windows 镜像 |
| **GPU** | AMD Radeon™ 集成显卡（RDNA 3.5） |
| **NPU** | AMD XDNA™ 2 NPU，供 Lemonade 混合执行模式使用 |
| **内存** | 最低 64 GB；对于更大的模型推荐 128 GB 以上 |

## 网络要求

- 首次下载模型时需要互联网连接（根据模型大小为 1–25 GB）
- 如使用云端智能体登录，需要互联网连接
- 模型下载完成后，本地推理无需互联网

## 已知平台说明

- **Lemonade Server 不会在登录时启动。** 该镜像中已移除其启动快捷方式，因此必须手动启动，依赖它的应用才能访问该端点。
- **nvm 仅为第一个用户账户安装。** Node.js 也已进行机器级安装，因此可能需要调整两者之间的 PATH 优先级。
- **Intelligent Terminal 是在首次登录时按用户安装的**，而非机器级安装。
- **在 Intelligent Terminal 中使用自定义模型端点需要 GitHub Copilot CLI 或 OpenCode** 作为底层智能体。其他内置智能体不支持自定义的 OpenAI 兼容提供方。