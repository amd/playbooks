<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

Ez a dokumentum a playbook futtatásához szükséges platform-konfigurációkat írja le.

## Szükséges alkalmazások/keretrendszerek
### Windows/Linux

A ComfyUI-t előre telepíteni kell a [ComfyUI telepítési útmutatóban](../../dependencies/comfyui.md) megadott utasítások szerint.

## Szükséges modellek

### Windows/Linux

A következő modelleknek jelen kell lenniük abban a könyvtárban, ahová a ComfyUI telepítve van, a `models` mappán belül.

| Modell típusa | Fájlnév | Méret | Helye | Letöltés |
|------------|----------|------|----------|----------|
| Szövegkódoló | `qwen_3_4b.safetensors` | 7,49 GB | `models/text_encoders/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162,25 MB | `models/loras/` | [Link](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Diffúziós modell | `z_image_turbo_bf16.safetensors` | 11,46 GB | `models/diffusion_models/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319,77 MB | `models/vae/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Annak ellenőrzéséhez, hogy a modellek megfelelően vannak-e elhelyezve, [tekintse meg a ComfyUI playbook előnézetét az onboarding weboldalon](../../README.md#previewing-the-playbooks), és kövesse az utasításokat. A modellek megfelelően vannak elhelyezve, ha a Z-Image Turbo sablon indításakor nem jelenik meg a „Modellek nem találhatók" oldal.