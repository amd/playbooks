<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maschinelle Übersetzung.** Diese Seite wurde automatisch aus dem Englischen übersetzt und nicht von einem Menschen überprüft. Sie kann Fehler enthalten, und bestimmte Anweisungen, Befehle, Downloads, Produktverfügbarkeiten oder andere Inhalte können je nach Sprache oder Region abweichen. Im Falle von Unstimmigkeiten oder Widersprüchen ist die englische Originalversion des playbook maßgeblich und hat Vorrang.
<!-- auto-translated-disclaimer:end -->

# Plattformkonfiguration

Dieses Dokument beschreibt die erwarteten Plattformkonfigurationen für die Ausführung dieses Playbooks.

## Erforderliche Apps/Frameworks
### Windows/Linux

ComfyUI sollte gemäß den Anweisungen im [ComfyUI-Installationsleitfaden](../../dependencies/comfyui.md) vorinstalliert sein.

## Erforderliche Modelle

### Windows/Linux

Die folgenden Modelle müssen in dem Verzeichnis vorhanden sein, in dem ComfyUI installiert ist, innerhalb des Ordners `models`.

| Modelltyp | Dateiname | Größe | Speicherort | Download |
|------------|----------|------|----------|----------|
| Text Encoder | `qwen_3_4b.safetensors` | 7,49 GB | `models/text_encoders/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162,25 MB | `models/loras/` | [Link](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Diffusion Model | `z_image_turbo_bf16.safetensors` | 11,46 GB | `models/diffusion_models/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319,77 MB | `models/vae/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Um zu testen, ob die Modelle korrekt platziert sind, [zeigen Sie eine Vorschau des ComfyUI-Playbooks über die Onboarding-Website an](../../README.md#previewing-the-playbooks) und folgen Sie den Anweisungen. Die Modelle sind korrekt platziert, wenn beim Starten der Z-Image Turbo-Vorlage keine Seite „Models not found“ angezeigt wird.