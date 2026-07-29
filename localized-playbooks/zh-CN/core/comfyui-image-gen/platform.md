<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# 平台配置

本文档描述了运行此工作手册所需的预期平台配置。

## 必需的应用程序/框架
### Windows/Linux

应按照[ComfyUI 安装指南](../../dependencies/comfyui.md)中提供的说明预先安装 ComfyUI。

## 必需的模型

### Windows/Linux

以下模型必须存在于安装 ComfyUI 的目录下的 `models` 文件夹中。

| 模型类型 | 文件名 | 大小 | 位置 | 下载 |
|------------|----------|------|----------|----------|
| 文本编码器 | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [链接](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [链接](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| 扩散模型 | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [链接](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [链接](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |
