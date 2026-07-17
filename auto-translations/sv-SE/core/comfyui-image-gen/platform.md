<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Plattformskonfiguration

Det här dokumentet beskriver de förväntade plattformskonfigurationerna för att köra den här spelboken.

## Nödvändiga appar/ramverk
### Windows/Linux

ComfyUI bör vara förinstallerat med hjälp av instruktionerna i [ComfyUI-installationsguiden](../../dependencies/comfyui.md).

## Nödvändiga modeller

### Windows/Linux

Följande modeller måste finnas i den katalog där ComfyUI är installerat, inuti mappen `models`.

| Modelltyp | Filnamn | Storlek | Plats | Nedladdning |
|------------|----------|------|----------|----------|
| Textkodare | `qwen_3_4b.safetensors` | 7,49 GB | `models/text_encoders/` | [Länk](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162,25 MB | `models/loras/` | [Länk](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Diffusionsmodell | `z_image_turbo_bf16.safetensors` | 11,46 GB | `models/diffusion_models/` | [Länk](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319,77 MB | `models/vae/` | [Länk](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


För att testa om modellerna är korrekt placerade, [förhandsgranska ComfyUI-spelboken via introduktionswebbplatsen](../../README.md#previewing-the-playbooks) och följ instruktionerna. Modellerna är korrekt placerade om ingen sida med "Models not found" visas när Z-Image Turbo-mallen startas.