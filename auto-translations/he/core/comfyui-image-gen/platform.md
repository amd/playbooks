<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **תרגום מכונה.** דף זה תורגם באופן אוטומטי מאנגלית ולא נבדק על ידי אדם. ייתכן שהוא מכיל שגיאות, וייתכן שהוראות, פקודות, הורדות, זמינות מוצרים, או תוכן אחר מסוימים ישתנו בהתאם לשפה או לאזור. בכל מקרה של אי-התאמה או סתירה, הגרסה המקורית באנגלית של ה-playbook היא הקובעת והמחייבת.
<!-- auto-translated-disclaimer:end -->

# תצורת פלטפורמה

מסמך זה מתאר את תצורות הפלטפורמה הצפויות להרצת ספר משחקים זה.

## אפליקציות/מסגרות עבודה נדרשות
### Windows/Linux

יש להתקין מראש את ComfyUI באמצעות ההוראות המפורטות ב-[מדריך התקנת ComfyUI](../../dependencies/comfyui.md).

## מודלים נדרשים

### Windows/Linux

המודלים הבאים חייבים להיות נוכחים בתיקייה שבה מותקן ComfyUI, בתוך התיקייה `models`.

| סוג מודל | שם קובץ | גודל | מיקום | הורדה |
|------------|----------|------|----------|----------|
| Text Encoder | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [קישור](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [קישור](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Diffusion Model | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [קישור](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [קישור](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


כדי לבדוק האם המודלים ממוקמים כראוי, [הצג תצוגה מקדימה של ספר המשחקים של ComfyUI באמצעות אתר ההכשרה](../../README.md#previewing-the-playbooks) ופעל לפי ההוראות. המודלים ממוקמים כראוי אם לא מופיע דף "Models not found" בעת הפעלת התבנית Z-Image Turbo.