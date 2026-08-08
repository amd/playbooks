<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversættelse.** Denne side er automatisk oversat fra engelsk og er ikke blevet gennemgået af et menneske. Den kan indeholde fejl, og visse instruktioner, kommandoer, downloads, produkttilgængelighed eller andet indhold kan variere afhængigt af sprog eller region. I tilfælde af uoverensstemmelse eller afvigelse er den oprindelige engelske version af playbook'en gældende og har forrang.
<!-- auto-translated-disclaimer:end -->

# Platformkonfiguration

Dette dokument beskriver de forventede platformkonfigurationer til at køre denne playbook.

## Påkrævede apps/frameworks
### Windows/Linux

ComfyUI bør være forudinstalleret ved hjælp af instruktionerne i [ComfyUI-installationsguiden](../../dependencies/comfyui.md).

## Påkrævede modeller

### Windows/Linux

Følgende modeller skal være til stede i den mappe, hvor ComfyUI er installeret, inde i mappen `models`.

| Modeltype | Filnavn | Størrelse | Placering | Download |
|------------|----------|------|----------|----------|
| Text Encoder | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [Link](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Diffusion Model | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


For at teste, om modellerne er placeret korrekt, kan du [forhåndsvise ComfyUI-playbooken ved hjælp af onboarding-webstedet](../../README.md#previewing-the-playbooks) og følge instruktionerne. Modellerne er placeret korrekt, hvis der ikke vises en "Models not found"-side, når Z-Image Turbo-skabelonen startes.