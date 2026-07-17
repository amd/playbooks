<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platformconfiguratie

Dit document beschrijft de verwachte platformconfiguraties voor het uitvoeren van dit playbook.

## Vereiste apps/frameworks
### Windows/Linux

ComfyUI moet vooraf geïnstalleerd zijn aan de hand van de instructies in de [ComfyUI-installatiegids](../../dependencies/comfyui.md).

## Vereiste modellen

### Windows/Linux

De volgende modellen moeten aanwezig zijn in de map waar ComfyUI is geïnstalleerd, in de map `models`.

| Modeltype | Bestandsnaam | Grootte | Locatie | Downloaden |
|------------|----------|------|----------|----------|
| Tekstencoder | `qwen_3_4b.safetensors` | 7,49 GB | `models/text_encoders/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162,25 MB | `models/loras/` | [Link](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Diffusiemodel | `z_image_turbo_bf16.safetensors` | 11,46 GB | `models/diffusion_models/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319,77 MB | `models/vae/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Om te controleren of de modellen correct zijn geplaatst, [bekijt u het ComfyUI-playbook via de onboardingwebsite](../../README.md#previewing-the-playbooks) en volgt u de instructies. De modellen zijn correct geplaatst als er geen pagina "Modellen niet gevonden" verschijnt bij het starten van de Z-Image Turbo-sjabloon.