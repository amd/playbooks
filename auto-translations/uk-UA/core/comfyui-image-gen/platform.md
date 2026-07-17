<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Конфігурація платформи

Цей документ описує очікувані конфігурації платформи для запуску цього посібника.

## Необхідні застосунки/фреймворки
### Windows/Linux

ComfyUI має бути попередньо встановлений відповідно до інструкцій, наведених у [Посібнику з встановлення ComfyUI](../../dependencies/comfyui.md).

## Необхідні моделі

### Windows/Linux

Наступні моделі мають бути розміщені в директорії, де встановлено ComfyUI, у папці `models`.

| Тип моделі | Назва файлу | Розмір | Розташування | Завантаження |
|------------|----------|------|----------|----------|
| Текстовий енкодер | `qwen_3_4b.safetensors` | 7,49 ГБ | `models/text_encoders/` | [Посилання](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162,25 МБ | `models/loras/` | [Посилання](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Дифузійна модель | `z_image_turbo_bf16.safetensors` | 11,46 ГБ | `models/diffusion_models/` | [Посилання](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319,77 МБ | `models/vae/` | [Посилання](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Щоб перевірити, чи правильно розміщено моделі, [перегляньте посібник ComfyUI на вебсайті онбордингу](../../README.md#previewing-the-playbooks) та дотримуйтесь інструкцій. Моделі розміщено правильно, якщо під час запуску шаблону Z-Image Turbo не з'являється сторінка «Моделі не знайдено».