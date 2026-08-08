<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije proveravana od strane čoveka. Može sadržati greške, a određena uputstva, komande, preuzimanja, dostupnost proizvoda ili drugi sadržaj mogu se razlikovati u zavisnosti od jezika ili regiona. U slučaju bilo kakve nedoslednosti ili neslaganja, merodavna je originalna verzija playbook-a na engleskom jeziku.
<!-- auto-translated-disclaimer:end -->

# Konfiguracija platforme

Ovaj dokument opisuje očekivane konfiguracije platforme za pokretanje ovog priručnika (playbook).

## Potrebne aplikacije/okviri
### Windows/Linux

ComfyUI treba biti unapred instaliran prema uputstvima datim u [Vodiču za instalaciju ComfyUI-ja](../../dependencies/comfyui.md).

## Potrebni modeli

### Windows/Linux

Sledeći modeli moraju biti prisutni u direktorijumu gde je ComfyUI instaliran, unutar foldera `models`.

| Tip modela | Naziv fajla | Veličina | Lokacija | Preuzimanje |
|------------|----------|------|----------|----------|
| Enkoder teksta | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [Link](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Difuzioni model | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Da biste proverili da li su modeli pravilno postavljeni, [pregledajte ComfyUI priručnik koristeći sajt za onboarding](../../README.md#previewing-the-playbooks) i pratite uputstva. Modeli su pravilno postavljeni ako se ne prikaže stranica „Models not found“ prilikom pokretanja Z-Image Turbo šablona.