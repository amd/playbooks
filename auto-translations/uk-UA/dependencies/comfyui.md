<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Завантажте останній інсталятор ComfyUI для Windows з [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Виберіть конфігурацію апаратного забезпечення: оберіть `AMD ROCm`.
3. Виберіть, куди встановити ComfyUI: використайте шлях за замовчуванням або вашу власну папку.
4. Налаштування Desktop App: рекомендуємо зняти позначку "Automatic Updates", щоб гарантовано використовувати рекомендовану версію цього застосунку.
5. Натисніть "Next", щоб розпочати встановлення.

<!-- @os:end -->

<!-- @os:linux -->
#### Клонувати ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Необов'язково) Перейти на конкретну версію
```bash
git checkout v0.19.2
```

#### Встановлення залежностей ComfyUI

Активувавши віртуальне середовище Python, виконайте:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Примітка**: Додаткову інформацію дивіться на [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI).

<!-- @os:end -->