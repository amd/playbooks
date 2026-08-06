<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

# Konfiguracija platforme

Ta dokument opisuje pričakovane konfiguracije platforme za izvajanje tega vodnika.

## Zahtevane aplikacije/ogrodja
### Windows/Linux

ComfyUI mora biti vnaprej nameščen po navodilih iz [Vodnika za namestitev ComfyUI](../../dependencies/comfyui.md).

## Zahtevani modeli

### Windows/Linux

Naslednji modeli morajo biti prisotni v imeniku, kjer je nameščen ComfyUI, znotraj mape `models`.

| Vrsta modela | Ime datoteke | Velikost | Lokacija | Prenos |
|------------|----------|------|----------|----------|
| Kodirnik besedila | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [Povezava](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [Povezava](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Difuzijski model | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [Povezava](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [Povezava](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Če želite preveriti, ali so modeli pravilno nameščeni, [predogledajte vodnik ComfyUI z uporabo spletnega mesta za uvajanje](../../README.md#previewing-the-playbooks) in sledite navodilom. Modeli so pravilno nameščeni, če se pri zagonu predloge Z-Image Turbo ne prikaže stran »Models not found«.