<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# تكوين المنصة

يصف هذا المستند تكوينات المنصة المتوقعة لتشغيل هذا الدليل التطبيقي.

## التطبيقات/الأطر المطلوبة
### Windows/Linux

يجب تثبيت ComfyUI مسبقًا باستخدام التعليمات المقدمة في [دليل تثبيت ComfyUI](../../dependencies/comfyui.md).

## النماذج المطلوبة

### Windows/Linux

يجب أن تكون النماذج التالية موجودة في الدليل الذي تم تثبيت ComfyUI فيه داخل مجلد `models`.

| نوع النموذج | اسم الملف | الحجم | الموقع | التنزيل |
|------------|----------|------|----------|----------|
| مشفّر النص | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [رابط](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [رابط](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| نموذج الانتشار | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [رابط](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [رابط](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


للتحقق من صحة وضع النماذج، [قم بمعاينة الدليل التطبيقي لـ ComfyUI عبر موقع الإعداد التمهيدي](../../README.md#previewing-the-playbooks) واتبع التعليمات. تكون النماذج موضوعة بشكل صحيح إذا لم تظهر صفحة "النماذج غير موجودة" عند تشغيل قالب Z-Image Turbo.