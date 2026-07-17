<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# תצורת פלטפורמה

מסמך זה מתאר את תצורות הפלטפורמה הנדרשות להפעלת ה-playbook הזה.

## אפליקציות/מסגרות נדרשות
### Windows/Linux

יש להתקין את ComfyUI מראש בהתאם להוראות המפורטות ב[מדריך התקנת ComfyUI](../../dependencies/comfyui.md).

## מודלים נדרשים

### Windows/Linux

המודלים הבאים חייבים להיות נוכחים בתיקייה שבה מותקן ComfyUI, בתוך תיקיית `models`.

| סוג מודל | שם קובץ | גודל | מיקום | הורדה |
|------------|----------|------|----------|----------|
| מקודד טקסט | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [קישור](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [קישור](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| מודל דיפוזיה | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [קישור](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [קישור](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


כדי לבדוק האם המודלים ממוקמים כראוי, [צפה בתצוגה מקדימה של ה-playbook של ComfyUI באמצעות אתר ה-onboarding](../../README.md#previewing-the-playbooks) ופעל לפי ההוראות. המודלים ממוקמים כראוי אם לא מופיעה דף "Models not found" בעת הפעלת תבנית Z-Image Turbo.