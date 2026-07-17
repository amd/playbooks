<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configurazione della Piattaforma

Questo documento descrive le configurazioni di piattaforma previste per l'esecuzione di questo playbook.

## App/Framework Richiesti
### Windows/Linux

ComfyUI deve essere pre-installato seguendo le istruzioni fornite nella [Guida all'Installazione di ComfyUI](../../dependencies/comfyui.md).

## Modelli Richiesti

### Windows/Linux

I seguenti modelli devono essere presenti nella directory in cui è installato ComfyUI, all'interno della cartella `models`.

| Tipo di Modello | Nome File | Dimensione | Posizione | Download |
|------------|----------|------|----------|----------|
| Text Encoder | `qwen_3_4b.safetensors` | 7,49 GB | `models/text_encoders/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162,25 MB | `models/loras/` | [Link](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Modello di Diffusione | `z_image_turbo_bf16.safetensors` | 11,46 GB | `models/diffusion_models/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319,77 MB | `models/vae/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Per verificare che i modelli siano posizionati correttamente, [visualizza in anteprima il playbook ComfyUI tramite il sito di onboarding](../../README.md#previewing-the-playbooks) e segui le istruzioni. I modelli sono posizionati correttamente se non viene visualizzata alcuna pagina "Modelli non trovati" all'avvio del template Z-Image Turbo.