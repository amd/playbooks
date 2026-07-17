<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfigurace platformy

Tento dokument popisuje očekávané konfigurace platformy pro spuštění tohoto playbooku.

## Požadované aplikace/frameworky
### Windows/Linux

ComfyUI by mělo být předem nainstalováno podle pokynů uvedených v [Průvodci instalací ComfyUI](../../dependencies/comfyui.md).

## Požadované modely

### Windows/Linux

Následující modely musí být přítomny v adresáři, kde je nainstalováno ComfyUI, ve složce `models`.

| Typ modelu | Název souboru | Velikost | Umístění | Stažení |
|------------|----------|------|----------|----------|
| Textový enkodér | `qwen_3_4b.safetensors` | 7,49 GB | `models/text_encoders/` | [Odkaz](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162,25 MB | `models/loras/` | [Odkaz](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Difuzní model | `z_image_turbo_bf16.safetensors` | 11,46 GB | `models/diffusion_models/` | [Odkaz](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319,77 MB | `models/vae/` | [Odkaz](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Chcete-li ověřit, zda jsou modely správně umístěny, [zobrazte náhled playbooku ComfyUI prostřednictvím onboardingového webu](../../README.md#previewing-the-playbooks) a postupujte podle pokynů. Modely jsou správně umístěny, pokud se při spuštění šablony Z-Image Turbo nezobrazí stránka „Modely nenalezeny".