<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

This document describes the expected platform configurations for running this playbook.

## Required Apps/Frameworks
### Windows/Linux

ComfyUI should be pre-installed using the instructions provided in [ComfyUI Installation Guide](../../dependencies/comfyui.md).

## Required Models

### Windows/Linux

The following models must be present in the directory where ComfyUI is installed inside of the `models` folder.

| Model Type | Filename | Size | Location | Download |
|------------|----------|------|----------|----------|
| Text Encoder | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [Link](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Diffusion Model | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


To test whether the models are correctly placed, [preview the ComfyUI playbook using the onboarding website](../../README.md#previewing-the-playbooks) and follow instructions. Models are correctly placed if no "Models not found" page shows up when launching the Z-Image Turbo template.