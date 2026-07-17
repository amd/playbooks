<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Завантажте останній інсталятор ComfyUI для Windows з [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Виберіть конфігурацію обладнання: оберіть `AMD ROCm`.
3. Виберіть місце встановлення ComfyUI: використовуйте шлях за замовчуванням або бажану папку.
4. Налаштування застосунку для робочого столу: рекомендуємо зняти позначку «Automatic Updates», щоб переконатися, що ви використовуєте рекомендовану версію цього застосунку.
5. Натисніть «Next», щоб розпочати встановлення.

<!-- @os:end -->

<!-- @os:linux -->
#### Клонування ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Необов'язково) Перехід до певної версії
```bash
git checkout v0.19.2
```

#### Встановлення залежностей ComfyUI

Активувавши віртуальне середовище Python, виконайте:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Примітка**: Додаткову інформацію див. на [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI).

<!-- @os:end -->