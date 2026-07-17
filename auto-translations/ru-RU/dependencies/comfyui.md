<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Загрузите последнюю версию установщика ComfyUI для Windows с сайта [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Выберите конфигурацию оборудования: выберите `AMD ROCm`.
3. Выберите папку для установки ComfyUI: используйте путь по умолчанию или укажите предпочтительную папку.
4. Настройки приложения для рабочего стола: рекомендуем снять флажок «Automatic Updates», чтобы использовать рекомендуемую версию приложения.
5. Нажмите «Next», чтобы начать установку.

<!-- @os:end -->

<!-- @os:linux -->
#### Клонирование ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Необязательно) Переключение на определённую версию
```bash
git checkout v0.19.2
```

#### Установка зависимостей ComfyUI

Активировав виртуальное окружение Python, выполните:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Примечание**: Дополнительную информацию см. на странице [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI).

<!-- @os:end -->