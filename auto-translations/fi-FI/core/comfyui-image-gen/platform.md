<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se voi sisältää virheitä, ja tietyt ohjeet, komennot, lataukset, tuotteiden saatavuus tai muu sisältö voivat vaihdella kielen tai alueen mukaan. Mahdollisten ristiriitaisuuksien tai epäjohdonmukaisuuksien ilmetessä alkuperäinen englanninkielinen playbook on ratkaiseva ja ensisijainen versio.
<!-- auto-translated-disclaimer:end -->

# Alustan määritys

Tässä asiakirjassa kuvataan tämän ohjekirjan (playbook) suorittamiseen tarvittavat alustan määritykset.

## Vaaditut sovellukset/kehykset
### Windows/Linux

ComfyUI tulee olla asennettuna etukäteen [ComfyUI-asennusoppaan](../../dependencies/comfyui.md) ohjeiden mukaisesti.

## Vaaditut mallit

### Windows/Linux

Seuraavien mallien tulee olla läsnä hakemistossa, johon ComfyUI on asennettu, `models`-kansion sisällä.

| Mallityyppi | Tiedostonimi | Koko | Sijainti | Lataus |
|------------|----------|------|----------|----------|
| Text Encoder | `qwen_3_4b.safetensors` | 7.49 Gt | `models/text_encoders/` | [Linkki](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 Mt | `models/loras/` | [Linkki](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Diffusion Model | `z_image_turbo_bf16.safetensors` | 11.46 Gt | `models/diffusion_models/` | [Linkki](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 Mt | `models/vae/` | [Linkki](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Voit testata, onko mallit sijoitettu oikein, [esikatselemalla ComfyUI-ohjekirjaa käyttöönottosivuston avulla](../../README.md#previewing-the-playbooks) ja seuraamalla ohjeita. Mallit on sijoitettu oikein, jos "Models not found" -sivua ei näy Z-Image Turbo -mallipohjaa käynnistettäessä.