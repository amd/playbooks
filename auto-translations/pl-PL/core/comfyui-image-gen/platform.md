<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tłumaczenie maszynowe.** Ta strona została automatycznie przetłumaczona z języka angielskiego i nie została zweryfikowana przez człowieka. Może zawierać błędy, a niektóre instrukcje, polecenia, pliki do pobrania, dostępność produktów lub inne treści mogą różnić się w zależności od języka lub regionu. W przypadku jakichkolwiek niezgodności lub rozbieżności rozstrzygająca jest oryginalna angielska wersja playbook.
<!-- auto-translated-disclaimer:end -->

# Konfiguracja platformy

Ten dokument opisuje oczekiwane konfiguracje platformy wymagane do uruchomienia tego playbooka.

## Wymagane aplikacje/frameworki
### Windows/Linux

ComfyUI powinno być wcześniej zainstalowane zgodnie z instrukcjami zawartymi w [Przewodniku instalacji ComfyUI](../../dependencies/comfyui.md).

## Wymagane modele

### Windows/Linux

Następujące modele muszą znajdować się w katalogu, w którym zainstalowano ComfyUI, wewnątrz folderu `models`.

| Typ modelu | Nazwa pliku | Rozmiar | Lokalizacja | Pobieranie |
|------------|----------|------|----------|----------|
| Text Encoder | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [Link](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Diffusion Model | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Aby sprawdzić, czy modele zostały poprawnie umieszczone, [wyświetl podgląd playbooka ComfyUI za pomocą witryny onboardingowej](../../README.md#previewing-the-playbooks) i postępuj zgodnie z instrukcjami. Modele są poprawnie umieszczone, jeśli podczas uruchamiania szablonu Z-Image Turbo nie pojawi się strona „Models not found”.