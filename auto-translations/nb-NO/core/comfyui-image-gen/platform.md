<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversettelse.** Denne siden ble automatisk oversatt fra engelsk og har ikke blitt gjennomgått av et menneske. Den kan inneholde feil, og enkelte instruksjoner, kommandoer, nedlastinger, produkttilgjengelighet eller annet innhold kan variere etter språk eller region. Ved eventuelle uoverensstemmelser eller avvik er den opprinnelige engelske versjonen av playbook-en gjeldende.
<!-- auto-translated-disclaimer:end -->

# Plattformkonfigurasjon

Dette dokumentet beskriver de forventede plattformkonfigurasjonene for å kjøre denne spillboken.

## Nødvendige apper/rammeverk
### Windows/Linux

ComfyUI bør være forhåndsinstallert ved hjelp av instruksjonene som er gitt i [ComfyUI-installasjonsveiledning](../../dependencies/comfyui.md).

## Nødvendige modeller

### Windows/Linux

Følgende modeller må finnes i katalogen der ComfyUI er installert, inne i `models`-mappen.

| Modeltype | Filnavn | Størrelse | Plassering | Nedlasting |
|------------|----------|------|----------|----------|
| Tekstkoder | `qwen_3_4b.safetensors` | 7,49 GB | `models/text_encoders/` | [Lenke](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162,25 MB | `models/loras/` | [Lenke](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Diffusjonsmodell | `z_image_turbo_bf16.safetensors` | 11,46 GB | `models/diffusion_models/` | [Lenke](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319,77 MB | `models/vae/` | [Lenke](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


For å teste om modellene er plassert riktig, [forhåndsvis ComfyUI-spillboken ved hjelp av onboarding-nettstedet](../../README.md#previewing-the-playbooks) og følg instruksjonene. Modellene er plassert riktig hvis ingen «Models not found»-side vises når du starter Z-Image Turbo-malen.