<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Конфигурация платформы

В этом документе описаны ожидаемые конфигурации платформы для выполнения данного плейбука.

## Windows

### Установка LM Studio

LM Studio должна быть предустановлена:

| Компонент | Версия | Расположение |
|-----------|---------|----------|
| **LM Studio (Models + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Загрузка модели

Следующие модели уже должны находиться в каталоге моделей LM Studio (`C:\Users\...\.lmstudio\models`):

| Тип модели | Квантование | Размер | Расположение |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### Установка LM Studio

Подробнее см. в файле lmstudio.md (внутри папки dependencies).

### Загрузка модели

Так же, как и в Windows.