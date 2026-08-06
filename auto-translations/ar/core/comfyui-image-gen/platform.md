<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **الترجمة الآلية.** تمت ترجمة هذه الصفحة تلقائيًا من اللغة الإنجليزية ولم تتم مراجعتها من قِبل مترجم بشري. قد تحتوي على أخطاء، وقد تختلف بعض التعليمات أو الأوامر أو خيارات التنزيل أو مدى توفر المنتج أو أي محتوى آخر باختلاف اللغة أو المنطقة. في حال وجود أي تعارض أو تباين، تكون النسخة الإنجليزية الأصلية من الـ playbook هي النسخة المعتمدة والمرجعية، ويُعمل بها في هذه الحالة.
<!-- auto-translated-disclaimer:end -->

# تكوين المنصة

يصف هذا المستند تكوينات المنصة المتوقعة لتشغيل دليل التشغيل هذا.

## التطبيقات/الأطر المطلوبة
### Windows/Linux

يجب تثبيت ComfyUI مسبقًا باستخدام التعليمات الموضحة في [دليل تثبيت ComfyUI](../../dependencies/comfyui.md).

## النماذج المطلوبة

### Windows/Linux

يجب أن تكون النماذج التالية موجودة في الدليل الذي تم تثبيت ComfyUI فيه داخل مجلد `models`.

| نوع النموذج | اسم الملف | الحجم | الموقع | التنزيل |
|------------|----------|------|----------|----------|
| مُرمِّز النص | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [رابط](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [رابط](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| نموذج الانتشار | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [رابط](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [رابط](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


لاختبار ما إذا كانت النماذج موضوعة بشكل صحيح، [قم بمعاينة دليل تشغيل ComfyUI باستخدام موقع الإعداد](../../README.md#previewing-the-playbooks) واتبع التعليمات. تكون النماذج موضوعة بشكل صحيح إذا لم تظهر صفحة "Models not found" عند تشغيل قالب Z-Image Turbo.