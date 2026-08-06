<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинный перевод.** Эта страница была автоматически переведена с английского языка и не прошла проверку человеком. Она может содержать ошибки, а некоторые инструкции, команды, файлы для загрузки, сведения о доступности продуктов или иное содержимое могут отличаться в зависимости от языка или региона. В случае каких-либо несоответствий или расхождений преимущественную силу имеет оригинальная версия playbook на английском языке.
<!-- auto-translated-disclaimer:end -->

# Конфигурация платформы

В этом документе описываются ожидаемые конфигурации платформы для выполнения данного плейбука.

## Необходимые приложения/фреймворки
### Windows/Linux

ComfyUI должен быть предварительно установлен согласно инструкциям, приведённым в [руководстве по установке ComfyUI](../../dependencies/comfyui.md).

## Необходимые модели

### Windows/Linux

Следующие модели должны находиться в папке `models` в каталоге, где установлен ComfyUI.

| Тип модели | Имя файла | Размер | Расположение | Загрузка |
|------------|----------|------|----------|----------|
| Текстовый кодировщик | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [Ссылка](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [Ссылка](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Диффузионная модель | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [Ссылка](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [Ссылка](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Чтобы проверить, правильно ли размещены модели, [просмотрите плейбук ComfyUI на сайте адаптации](../../README.md#previewing-the-playbooks) и следуйте инструкциям. Модели размещены правильно, если при запуске шаблона Z-Image Turbo не появляется страница «Models not found».