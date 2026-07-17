<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Конфигурация платформы

Этот документ описывает ожидаемые конфигурации платформы для запуска данного сценария.

## Необходимые приложения/фреймворки
### Windows/Linux

ComfyUI должен быть предварительно установлен согласно инструкциям, приведённым в [Руководстве по установке ComfyUI](../../dependencies/comfyui.md).

## Необходимые модели

### Windows/Linux

Следующие модели должны находиться в директории, где установлен ComfyUI, внутри папки `models`.

| Тип модели | Имя файла | Размер | Расположение | Загрузка |
|------------|----------|------|----------|----------|
| Текстовый энкодер | `qwen_3_4b.safetensors` | 7,49 ГБ | `models/text_encoders/` | [Ссылка](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162,25 МБ | `models/loras/` | [Ссылка](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Диффузионная модель | `z_image_turbo_bf16.safetensors` | 11,46 ГБ | `models/diffusion_models/` | [Ссылка](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319,77 МБ | `models/vae/` | [Ссылка](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Чтобы проверить, правильно ли размещены модели, [просмотрите сценарий ComfyUI на сайте онбординга](../../README.md#previewing-the-playbooks) и следуйте инструкциям. Модели размещены корректно, если при запуске шаблона Z-Image Turbo не появляется страница «Модели не найдены».