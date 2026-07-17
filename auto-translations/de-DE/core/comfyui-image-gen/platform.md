<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Plattformkonfiguration

Dieses Dokument beschreibt die erwarteten Plattformkonfigurationen für die Ausführung dieses Playbooks.

## Erforderliche Apps/Frameworks
### Windows/Linux

ComfyUI sollte mithilfe der Anweisungen im [ComfyUI-Installationshandbuch](../../dependencies/comfyui.md) vorinstalliert sein.

## Erforderliche Modelle

### Windows/Linux

Die folgenden Modelle müssen im Verzeichnis, in dem ComfyUI installiert ist, im Ordner `models` vorhanden sein.

| Modelltyp | Dateiname | Größe | Speicherort | Download |
|------------|----------|------|----------|----------|
| Text Encoder | `qwen_3_4b.safetensors` | 7,49 GB | `models/text_encoders/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162,25 MB | `models/loras/` | [Link](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Diffusionsmodell | `z_image_turbo_bf16.safetensors` | 11,46 GB | `models/diffusion_models/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319,77 MB | `models/vae/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Um zu testen, ob die Modelle korrekt platziert sind, [zeigen Sie das ComfyUI-Playbook über die Onboarding-Website in der Vorschau an](../../README.md#previewing-the-playbooks) und folgen Sie den Anweisungen. Die Modelle sind korrekt platziert, wenn beim Starten der Z-Image Turbo-Vorlage keine Seite „Modelle nicht gefunden" erscheint.