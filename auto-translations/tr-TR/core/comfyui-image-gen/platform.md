<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

Bu belge, bu playbook'u çalıştırmak için beklenen platform yapılandırmalarını açıklamaktadır.

## Gerekli Uygulamalar/Çerçeveler
### Windows/Linux

ComfyUI, [ComfyUI Kurulum Kılavuzu](../../dependencies/comfyui.md)'nda sağlanan talimatlar kullanılarak önceden kurulmuş olmalıdır.

## Gerekli Modeller

### Windows/Linux

Aşağıdaki modeller, ComfyUI'nin kurulu olduğu dizinde `models` klasörünün içinde bulunmalıdır.

| Model Türü | Dosya Adı | Boyut | Konum | İndir |
|------------|----------|------|----------|----------|
| Metin Kodlayıcı | `qwen_3_4b.safetensors` | 7,49 GB | `models/text_encoders/` | [Bağlantı](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162,25 MB | `models/loras/` | [Bağlantı](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Difüzyon Modeli | `z_image_turbo_bf16.safetensors` | 11,46 GB | `models/diffusion_models/` | [Bağlantı](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319,77 MB | `models/vae/` | [Bağlantı](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Modellerin doğru yerleştirilip yerleştirilmediğini test etmek için [katılım web sitesini kullanarak ComfyUI playbook'unu önizleyin](../../README.md#previewing-the-playbooks) ve talimatları izleyin. Z-Image Turbo şablonu başlatılırken "Modeller bulunamadı" sayfası görünmüyorsa modeller doğru şekilde yerleştirilmiş demektir.