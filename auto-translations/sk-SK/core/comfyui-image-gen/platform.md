<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

# Konfigurácia platformy

Tento dokument popisuje očakávané konfigurácie platformy na spustenie tohto playbooku.

## Požadované aplikácie/frameworky
### Windows/Linux

ComfyUI by mal byť predinštalovaný podľa pokynov uvedených v [Sprievodcovi inštaláciou ComfyUI](../../dependencies/comfyui.md).

## Požadované modely

### Windows/Linux

Nasledujúce modely musia byť prítomné v adresári, kde je nainštalovaný ComfyUI, vo vnútri priečinka `models`.

| Typ modelu | Názov súboru | Veľkosť | Umiestnenie | Stiahnutie |
|------------|----------|------|----------|----------|
| Textový kóder | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [Odkaz](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [Odkaz](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Difúzny model | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [Odkaz](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [Odkaz](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Ak chcete otestovať, či sú modely správne umiestnené, [zobrazte si náhľad playbooku ComfyUI pomocou onboardingovej webovej stránky](../../README.md#previewing-the-playbooks) a postupujte podľa pokynov. Modely sú správne umiestnené, ak sa pri spustení šablóny Z-Image Turbo nezobrazí stránka „Models not found“.