<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Makine çevirisi.** Bu sayfa İngilizce dilinden otomatik olarak çevrilmiştir ve bir kişi tarafından incelenmemiştir. Sayfa hatalar içerebilir ve belirli talimatlar, komutlar, indirmeler, ürün kullanılabilirliği veya diğer içerikler dile veya bölgeye göre farklılık gösterebilir. Herhangi bir tutarsızlık veya farklılık olması durumunda, playbook'un orijinal İngilizce sürümü geçerli ve bağlayıcı olacaktır.
<!-- auto-translated-disclaimer:end -->

# Platform Configuration

Bu belge, bu playbook'u çalıştırmak için beklenen platform yapılandırmalarını açıklamaktadır.

## Gerekli Uygulamalar/Çerçeveler
### Windows/Linux

ComfyUI, [ComfyUI Kurulum Kılavuzu](../../dependencies/comfyui.md) içinde sağlanan talimatlar kullanılarak önceden kurulmuş olmalıdır.

## Gerekli Modeller

### Windows/Linux

Aşağıdaki modeller, ComfyUI'nin kurulu olduğu dizindeki `models` klasörünün içinde bulunmalıdır.

| Model Türü | Dosya Adı | Boyut | Konum | İndirme |
|------------|----------|------|----------|----------|
| Text Encoder | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [Link](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Diffusion Model | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Modellerin doğru şekilde yerleştirilip yerleştirilmediğini test etmek için [onboarding web sitesini kullanarak ComfyUI playbook'unu önizleyin](../../README.md#previewing-the-playbooks) ve talimatları izleyin. Z-Image Turbo şablonu başlatıldığında "Models not found" sayfası görünmüyorsa modeller doğru şekilde yerleştirilmiş demektir.