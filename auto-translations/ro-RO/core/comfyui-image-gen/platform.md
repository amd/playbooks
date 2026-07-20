<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configurare platformă

Acest document descrie configurațiile de platformă preconizate pentru rularea acestui playbook.

## Aplicații/Framework-uri necesare
### Windows/Linux

ComfyUI trebuie preinstalat urmând instrucțiunile din [Ghidul de instalare ComfyUI](../../dependencies/comfyui.md).

## Modele necesare

### Windows/Linux

Următoarele modele trebuie să fie prezente în directorul în care este instalat ComfyUI, în interiorul folderului `models`.

| Tip model | Nume fișier | Dimensiune | Locație | Descărcare |
|------------|----------|------|----------|----------|
| Text Encoder | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [Link](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Diffusion Model | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Pentru a testa dacă modelele sunt plasate corect, [previzualizați playbook-ul ComfyUI folosind site-ul de onboarding](../../README.md#previewing-the-playbooks) și urmați instrucțiunile. Modelele sunt plasate corect dacă nu apare nicio pagină „Models not found” la lansarea șablonului Z-Image Turbo.