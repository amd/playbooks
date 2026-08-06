<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **机器翻译。**本页面由英文自动翻译，未经人工审核。其中可能包含错误，某些说明、命令、下载内容、产品可用性或其他内容可能因语言或地区而异。如内容存在任何不一致或差异，应以英文原版 playbook 为准。
<!-- auto-translated-disclaimer:end -->

# 平台配置

本文档介绍运行此手册所需的预期平台配置。

## 必需的应用程序/框架

### Windows/Linux
应从[此处](https://lemonade-server.ai/install_options.html)预先安装 Lemonade。

- **Open WebUI**（前端网页应用）
- **Lemonade Server**（后端模型服务器）

> 此手册以**原生**方式运行 **Lemonade**（Lemonade server/app）。**Open WebUI** 在 Linux 上以**容器**方式运行（通过 Podman），在 Windows 上以 **Python 软件包**方式运行。`open-webui` PyPI 软件包仅支持 Python ≤ 3.12，因此使用 Linux 容器可以避免管理较旧版本的 Python。

## 模型（在 Lemonade 中）

模型应在 **Lemonade 应用程序**内下载（使用内置的 Model Manager），或通过 Lemonade 的模型管理命令（`lemonade pull <model_name>`）下载。此手册假定以下推荐模型已下载完成，并显示在模型列表端点中。

检查模型可用性：
- 打开：`http://localhost:13305/api/v1/models`
- 已下载的模型将列在 `"data"` 下。

### 推荐模型

| 功能 | 模型 ID | 备注 |
|---|----|-----|
| LLM（文本输入 → 文本输出） | `Qwen3-4B-Hybrid`（或类似模型） | 任何用于聊天、文本补全、编码或推理的 Lemonade LLM 模型 |
| VLM（图像 → 文本） | `Qwen3.5-4B-GGUF`（或**视觉**类别中的任何模型） | 任何能够将图像作为输入一部分的多模态/视觉能力模型 |
| 图像生成（文本 → 图像） | `SDXL-Turbo`（或**图像**类别中的任何模型） | 任何能够根据文本提示生成图像的 Stable Diffusion 模型 |
| 音频（语音 → 文本） | `Whisper-Large-v3`（或**音频**类别中的任何模型） | 任何能够将音频转换为文本的 ASR 模型 |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## 使用的端口

- **Lemonade Server：** `http://localhost:13305`
- **Open WebUI：** `http://localhost:8080`

如果您的系统上已占用这些端口，请在启动服务器时更改它们。