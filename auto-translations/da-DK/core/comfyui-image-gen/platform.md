<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

Dette dokument beskriver de forventede platformskonfigurationer til at køre denne playbook.

## Påkrævede apps/frameworks
### Windows/Linux

ComfyUI skal være forudinstalleret ved hjælp af instruktionerne i [ComfyUI installationsvejledningen](../../dependencies/comfyui.md).

## Påkrævede modeller

### Windows/Linux

Følgende modeller skal være til stede i den mappe, hvor ComfyUI er installeret, inde i `models`-mappen.

| Modeltype | Filnavn | Størrelse | Placering | Download |
|------------|----------|------|----------|----------|
| Tekstkoder | `qwen_3_4b.safetensors` | 7,49 GB | `models/text_encoders/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162,25 MB | `models/loras/` | [Link](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Diffusionsmodel | `z_image_turbo_bf16.safetensors` | 11,46 GB | `models/diffusion_models/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319,77 MB | `models/vae/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


For at teste, om modellerne er placeret korrekt, skal du [forhåndsvise ComfyUI playbooken via onboarding-webstedet](../../README.md#previewing-the-playbooks) og følge instruktionerne. Modellerne er placeret korrekt, hvis der ikke vises nogen "Models not found"-side, når Z-Image Turbo-skabelonen startes.