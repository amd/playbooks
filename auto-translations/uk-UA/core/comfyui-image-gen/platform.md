<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинний переклад.** Цю сторінку було автоматично перекладено з англійської мови, і вона не була перевірена людиною. Вона може містити помилки, а певні інструкції, команди, завантаження, доступність продукту чи інший вміст можуть відрізнятися залежно від мови чи регіону. У разі будь-яких невідповідностей чи розбіжностей переважну силу має оригінальна англомовна версія playbook.
<!-- auto-translated-disclaimer:end -->

# Конфігурація платформи

У цьому документі описано очікувані конфігурації платформи для запуску цього playbook.

## Необхідні застосунки/фреймворки
### Windows/Linux

ComfyUI має бути попередньо встановлено за інструкціями з [посібника зі встановлення ComfyUI](../../dependencies/comfyui.md).

## Необхідні моделі

### Windows/Linux

Наведені нижче моделі мають бути присутніми в каталозі, куди встановлено ComfyUI, усередині папки `models`.

| Тип моделі | Ім'я файлу | Розмір | Розташування | Завантаження |
|------------|----------|------|----------|----------|
| Text Encoder | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [Посилання](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [Посилання](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Diffusion Model | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [Посилання](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [Посилання](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Щоб перевірити, чи правильно розміщено моделі, [перегляньте playbook ComfyUI за допомогою вебсайту онбордингу](../../README.md#previewing-the-playbooks) та дотримуйтеся інструкцій. Моделі розміщено правильно, якщо під час запуску шаблону Z-Image Turbo не з'являється сторінка "Models not found".