<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducción automática.** Esta página fue traducida automáticamente del inglés y no ha sido revisada por un humano. Puede contener errores, y ciertas instrucciones, comandos, descargas, disponibilidad de productos u otro contenido pueden variar según el idioma o la región. En caso de cualquier incoherencia o discrepancia, la versión original en inglés del playbook prevalecerá y será la que rija.
<!-- auto-translated-disclaimer:end -->

# Configuración de la plataforma

Este documento describe las configuraciones de plataforma esperadas para ejecutar este playbook.

## Aplicaciones/Frameworks requeridos
### Windows/Linux

ComfyUI debe estar preinstalado siguiendo las instrucciones proporcionadas en la [Guía de instalación de ComfyUI](../../dependencies/comfyui.md).

## Modelos requeridos

### Windows/Linux

Los siguientes modelos deben estar presentes en el directorio donde está instalado ComfyUI, dentro de la carpeta `models`.

| Tipo de modelo | Nombre de archivo | Tamaño | Ubicación | Descarga |
|------------|----------|------|----------|----------|
| Text Encoder | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [Enlace](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [Enlace](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Diffusion Model | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [Enlace](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [Enlace](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Para probar si los modelos están colocados correctamente, [previsualiza el playbook de ComfyUI usando el sitio web de incorporación](../../README.md#previewing-the-playbooks) y sigue las instrucciones. Los modelos están colocados correctamente si no aparece una página de "Models not found" al iniciar la plantilla de Z-Image Turbo.