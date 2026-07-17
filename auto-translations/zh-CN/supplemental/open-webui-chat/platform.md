<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# 平台配置

本文档描述了运行此 playbook 所需的预期平台配置。

## 所需应用/框架

### Windows/Linux
Lemonade 应预先从[此处](https://lemonade-server.ai/install_options.html)安装。

- **Open WebUI**（前端 Web 应用）
- **Lemonade Server**（后端模型服务器）

> 本 playbook **原生**运行 **Lemonade**（Lemonade server/app）。**Open WebUI** 在 Linux 上以**容器**方式运行（通过 Podman），在 Windows 上以 **Python 包**方式运行。`open-webui` PyPI 包仅支持 Python ≤ 3.12，因此 Linux 容器方式可避免管理旧版 Python。

## 模型（在 Lemonade 中）

模型应在 **Lemonade 应用**内下载（使用内置的模型管理器），或通过 Lemonade 的模型管理命令（`lemonade pull <model_name>`）下载。本 playbook 假设以下推荐模型已下载，并显示在模型列表端点中。

检查模型可用性：
- 打开：`http://localhost:13305/api/v1/models`
- 已下载的模型将列在 `"data"` 下。

### 推荐模型

| 能力 | 模型 ID | 备注 |
|---|----|-----|
| LLM（文本输入 → 文本输出） | `Qwen3-4B-Hybrid`（或类似模型） | 任何用于聊天、文本补全、编程或推理的 Lemonade LLM 模型 |
| VLM（图像 → 文本） | `Qwen3.5-4B-GGUF`（或 **Vision** 类别中的任意模型） | 任何可将图像作为输入的多模态/视觉能力模型 |
| 图像生成（文本 → 图像） | `SDXL-Turbo`（或 **Image** 类别中的任意模型） | 任何可根据文本提示生成图像的 Stable Diffusion 模型 |
| 音频（语音 → 文本） | `Whisper-Large-v3`（或 **Audio** 类别中的任意模型） | 任何可将音频转换为文本的 ASR 模型 |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## 使用的端口

- **Lemonade Server：** `http://localhost:13305`
- **Open WebUI：** `http://localhost:8080`

如果这些端口在您的系统上已被占用，请在启动服务器时更改它们。