<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfiguracija platforme

Ovaj dokument opisuje očekivane konfiguracije platforme za pokretanje ovog priručnika.

## Potrebne aplikacije/okviri
### Windows/Linux

ComfyUI treba biti unapred instaliran prema uputstvima datim u [Vodiču za instalaciju ComfyUI](../../dependencies/comfyui.md).

## Potrebni modeli

### Windows/Linux

Sledeći modeli moraju biti prisutni u direktorijumu gde je instaliran ComfyUI, unutar fascikle `models`.

| Tip modela | Naziv datoteke | Veličina | Lokacija | Preuzimanje |
|------------|----------|------|----------|----------|
| Tekstualni enkoder | `qwen_3_4b.safetensors` | 7,49 GB | `models/text_encoders/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162,25 MB | `models/loras/` | [Link](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Difuzioni model | `z_image_turbo_bf16.safetensors` | 11,46 GB | `models/diffusion_models/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319,77 MB | `models/vae/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Da biste proverili da li su modeli ispravno postavljeni, [pregledajte ComfyUI priručnik putem veb-sajta za uvođenje](../../README.md#previewing-the-playbooks) i pratite uputstva. Modeli su ispravno postavljeni ako se stranica „Modeli nisu pronađeni" ne pojavi prilikom pokretanja Z-Image Turbo šablona.