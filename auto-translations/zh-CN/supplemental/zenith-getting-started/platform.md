<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **机器翻译。**本页面由英文自动翻译，未经人工审核。其中可能包含错误，某些说明、命令、下载内容、产品可用性或其他内容可能因语言或地区而异。如内容存在任何不一致或差异，应以英文原版 playbook 为准。
<!-- auto-translated-disclaimer:end -->

# 平台配置 — Windows Ryzen AI Halo (Project Zenith)

本文档介绍本行动手册所预装的软件和平台假设前提。它仅适用于 Ryzen AI Halo 的 **Windows** 镜像，该镜像随附 Microsoft Project Zenith。

## AMD AI 技术栈

| 软件 | 版本 | 用途 |
|----------|---------|------|
| Lemonade Server | 最新版本 | 具备 OpenAI 兼容 API 的本地 LLM 服务器。已为所有用户安装。不会在登录时启动。未预装任何模型。 |
| ComfyUI Desktop | 最新版本 | 节点图式图像与扩散工作流。内置了自身的 Python 和 ROCm 运行时。 |
| PyTorch (ROCm) | torch、torchvision、torchaudio，附带 `rocm-sdk-devel` 7.14.0 | GPU 加速的 PyTorch，已离线安装到系统 Python 中 |

## Project Zenith 工具链

| 软件 | 版本 | 说明 |
|------|------|------|
| Python | 3.14.7 | 系统 Python；承载 ROCm PyTorch 技术栈 |
| PowerShell | 7.6.8 | 默认终端配置文件 |
| Intelligent Terminal | 预览版 | 在首次登录时按用户安装 |
| GitHub Copilot CLI | 1.0.94 | 全机安装；专属终端配置文件 |
| GitHub Copilot（应用） | 最新版本 | 桌面快捷方式已移除；从“开始”菜单启动 |
| WSL with Ubuntu | 26.04.1 | 在首次登录时按用户创建副本（约 1.46 GB） |
| Node.js + NVM for Windows | 1.2.2 (nvm) | nvm 仅为第一个用户账户安装 |
| uv | 最新版本 | Python 包与环境管理器 |
| PowerToys | 0.101 | 按用户注册命令面板 |
| .NET SDK | 10 | |
| Windows App CLI (`winapp`) | 最新版本 | |
| Git、Visual Studio Code | 最新版本 | |
| GitHub CLI、Azure CLI | 最新版本 | |
| Oh My Posh、Coreutils for Windows | 最新版本 | 注册到每个用户的 PowerShell 配置文件中 |
| OpenSSH Server | 内置组件 | 已安装；`sshd` 服务默认已禁用并停止 |

## 预配置的 Windows 设置

| 设置 | 值 |
|------|-----|
| 长路径 | 已在全机范围内启用（`LongPathsEnabled = 1`） |
| 文件资源管理器 | 标题栏中显示完整路径 |
| 外观 | 新用户默认设置为深色模式 |
| 字体 | Cascadia Mono NF、Cascadia Mono NF Italic、Cascadia Code NF |
| 终端默认配置文件 | PowerShell 7 |
| 任务栏固定项 | Windows Terminal、Visual Studio Code、AMD Ryzen AI Developer Center |

## 本地服务器端点

| 属性 | 值 |
|------|-----|
| 基础 URL | `http://localhost:13305/v1` |
| 备用路径前缀 | `http://localhost:13305/api/v1` |
| 身份验证 | 默认无需身份验证。要求非空密钥的应用可接受任意占位符。 |
| 健康检查 | `http://localhost:13305/api/v1/health` |
| 模型列表 | `http://localhost:13305/api/v1/models` |

## 模型

镜像中未预装任何模型。可通过 Lemonade 的 Model Manager 或 CLI 按需下载。

推荐用于本平台智能体工作的起始模型：

| 模型 | 类型 | 说明 |
|------|------|------|
| Qwen3.8 27B | 稠密模型 | 单 token 推理能力更强；由于吞吐量受带宽限制，生成速度较慢 |
| Qwen3.6 35B MTP | 混合专家模型 | 在相当规模下响应更快，交互性更好；通常是智能体工作流更合适的默认选择 |

### 默认模型存储

通过 Lemonade 下载的模型遵循 Hugging Face Hub 规范：

| 平台 | 默认路径 |
|------|---------|
| Windows | `%USERPROFILE%\.cache\huggingface\hub\` |

设置 `HF_HOME` 环境变量可更改存储位置。

## 硬件要求

| 硬件目标 | 要求 |
|----------|------|
| **设备** | AMD Ryzen AI Halo（Gorgon Halo），Windows 镜像 |
| **GPU** | AMD Radeon™ 集成显卡（RDNA 3.5） |
| **NPU** | AMD XDNA™ 2 NPU，供 Lemonade 混合执行模式使用 |
| **内存** | 最低 64 GB；建议 128 GB 以上以支持更大模型 |

## 网络要求

- 首次下载模型需要网络连接（根据模型不同，大小为 1–25 GB）
- 若使用云端智能体登录，需要网络连接
- 模型下载完成后，本地推理无需网络连接

## 已知平台说明

- **Lemonade Server 不会在登录时启动。** 其启动快捷方式已从镜像中移除，因此必须手动启动它，依赖它的应用才能访问该端点。
- **nvm 仅为第一个用户账户安装。** Node.js 也进行了全机安装，因此可能需要调整两者之间的 PATH 优先级。
- **Intelligent Terminal 在首次登录时按用户安装**，而非全机安装。
- **Intelligent Terminal 中的自定义模型端点需要以 GitHub Copilot CLI 或 OpenCode** 作为底层智能体。其他内置智能体不支持自定义的 OpenAI 兼容提供方。