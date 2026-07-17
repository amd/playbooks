<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

Этот документ описывает ожидаемые конфигурации платформы для запуска данного сценария.

## Windows

### Установка LM Studio

LM Studio должен быть предварительно установлен:

| Компонент | Версия | Расположение |
|-----------|---------|----------|
| **LM Studio (Модели + Прочее)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Программа)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Кэш)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Загрузка моделей

Следующие модели должны уже присутствовать в директории моделей LM Studio (`C:\Users\...\.lmstudio\models`):

| Устройство | Тип модели | Квантизация | Размер (ГБ) | Расположение |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### Установка LM Studio

Подробности см. в [lmstudio.md](../../dependencies/lmstudio.md).

### Загрузка моделей

Аналогично Windows.