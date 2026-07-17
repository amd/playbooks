<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configurarea Platformei

Acest document descrie configurațiile de platformă așteptate pentru rularea acestui playbook.

## Aplicații/Framework-uri Necesare
### Windows/Linux

ComfyUI trebuie să fie pre-instalat folosind instrucțiunile furnizate în [Ghidul de Instalare ComfyUI](../../dependencies/comfyui.md).

## Modele Necesare

### Windows/Linux

Următoarele modele trebuie să fie prezente în directorul unde este instalat ComfyUI, în interiorul folderului `models`.

| Tip Model | Nume Fișier | Dimensiune | Locație | Descărcare |
|------------|----------|------|----------|----------|
| Encoder Text | `qwen_3_4b.safetensors` | 7,49 GB | `models/text_encoders/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162,25 MB | `models/loras/` | [Link](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Model de Difuzie | `z_image_turbo_bf16.safetensors` | 11,46 GB | `models/diffusion_models/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319,77 MB | `models/vae/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Pentru a testa dacă modelele sunt plasate corect, [previzualizați playbook-ul ComfyUI folosind site-ul de onboarding](../../README.md#previewing-the-playbooks) și urmați instrucțiunile. Modelele sunt plasate corect dacă nicio pagină „Modele negăsite" nu apare la lansarea șablonului Z-Image Turbo.