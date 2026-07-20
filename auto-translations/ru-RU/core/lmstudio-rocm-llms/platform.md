<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Конфигурация платформы

В этом документе описаны ожидаемые конфигурации платформы для запуска данного playbook.

## Windows

### Установка LM Studio

LM Studio должна быть предустановлена:

| Компонент | Версия | Расположение |
|-----------|---------|----------|
| **LM Studio (Models + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Загрузка модели

Следующие модели уже должны присутствовать в каталоге моделей LM Studio (`C:\Users\...\.lmstudio\models`):

| Устройство | Тип модели | Квантование | Размер (ГБ) | Расположение |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### Установка LM Studio

Дополнительные сведения см. в [lmstudio.md](../../dependencies/lmstudio.md).

### Загрузка модели

Так же, как и в Windows.