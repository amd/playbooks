<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Конфигурация платформы

Этот документ описывает ожидаемые конфигурации платформы для запуска данного сценария.

## Windows

### Установка LM Studio

LM Studio должен быть предварительно установлен:

| Компонент | Версия | Расположение |
|-----------|---------|----------|
| **LM Studio (Модели + Разное)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Программа)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Кэш)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Загрузка модели

Следующие модели должны уже присутствовать в директории моделей LM Studio (`C:\Users\...\.lmstudio\models`):

| Тип модели | Квантизация | Размер | Расположение |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### Установка LM Studio

Подробности см. в файле lmstudio.md (внутри папки зависимостей).

### Загрузка модели

Аналогично Windows.