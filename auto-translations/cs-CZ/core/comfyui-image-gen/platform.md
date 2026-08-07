<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

# Konfigurace platformy

Tento dokument popisuje očekávané konfigurace platformy pro spuštění tohoto playbooku.

## Požadované aplikace/frameworky
### Windows/Linux

ComfyUI by měl být předinstalován podle pokynů uvedených v [Průvodci instalací ComfyUI](../../dependencies/comfyui.md).

## Požadované modely

### Windows/Linux

Následující modely musí být přítomny v adresáři, kam je nainstalováno ComfyUI, uvnitř složky `models`.

| Typ modelu | Název souboru | Velikost | Umístění | Stažení |
|------------|----------|------|----------|----------|
| Textový kodér | `qwen_3_4b.safetensors` | 7,49 GB | `models/text_encoders/` | [Odkaz](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162,25 MB | `models/loras/` | [Odkaz](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Difuzní model | `z_image_turbo_bf16.safetensors` | 11,46 GB | `models/diffusion_models/` | [Odkaz](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319,77 MB | `models/vae/` | [Odkaz](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Chcete-li ověřit, zda jsou modely správně umístěny, [zobrazte náhled playbooku ComfyUI pomocí onboardingového webu](../../README.md#previewing-the-playbooks) a postupujte podle pokynů. Modely jsou správně umístěny, pokud se při spuštění šablony Z-Image Turbo nezobrazí stránka „Models not found“.