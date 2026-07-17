<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

Цей документ описує очікувані конфігурації платформи для запуску цього посібника.

## Windows

### Встановлення LM Studio

LM Studio має бути попередньо встановлено:

| Компонент | Версія | Розташування |
|-----------|---------|----------|
| **LM Studio (Моделі + Різне)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Програма)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Кеш)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Завантаження моделей

Наступні моделі вже мають бути присутні в каталозі моделей LM Studio (`C:\Users\...\.lmstudio\models`):

| Пристрій | Тип моделі | Квантизація | Розмір (ГБ) | Розташування |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### Встановлення LM Studio

Докладніше див. у [lmstudio.md](../../dependencies/lmstudio.md).

### Завантаження моделей

Те саме, що й у Windows.