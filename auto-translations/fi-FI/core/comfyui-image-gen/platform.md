<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Alustan konfigurointi

Tässä asiakirjassa kuvataan odotetut alustan konfiguraatiot tämän playbook-oppaan suorittamiseen.

## Vaaditut sovellukset/kehykset
### Windows/Linux

ComfyUI tulee olla esiasennettuna noudattamalla ohjeita, jotka on annettu [ComfyUI-asennusoppaassa](../../dependencies/comfyui.md).

## Vaaditut mallit

### Windows/Linux

Seuraavien mallien tulee olla läsnä hakemistossa, johon ComfyUI on asennettu, `models`-kansion sisällä.

| Mallityyppi | Tiedostonimi | Koko | Sijainti | Lataus |
|------------|----------|------|----------|----------|
| Tekstikooderi | `qwen_3_4b.safetensors` | 7,49 Gt | `models/text_encoders/` | [Linkki](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162,25 Mt | `models/loras/` | [Linkki](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Diffuusiomalli | `z_image_turbo_bf16.safetensors` | 11,46 Gt | `models/diffusion_models/` | [Linkki](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319,77 Mt | `models/vae/` | [Linkki](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Voit testata, onko mallit sijoitettu oikein, [esikatsele ComfyUI-playbookia käyttöönottosivuston kautta](../../README.md#previewing-the-playbooks) ja seuraa ohjeita. Mallit on sijoitettu oikein, jos "Models not found" -sivua ei näy Z-Image Turbo -mallinetta käynnistettäessä.