<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Конфігурація платформи

Цей документ описує очікувані конфігурації платформи для запуску цього посібника.

## Windows

### Встановлення LM Studio

LM Studio має бути попередньо встановлений:

| Компонент | Версія | Розташування |
|-----------|---------|----------|
| **LM Studio (Моделі + Різне)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Програма)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Кеш)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Завантаження моделі

Наступні моделі вже мають бути присутні в директорії моделей LM Studio (`C:\Users\...\.lmstudio\models`):

| Тип моделі | Квантизація | Розмір | Розташування |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### Встановлення LM Studio

Докладніше див. у файлі lmstudio.md (у папці залежностей).

### Завантаження моделі

Те саме, що й у Windows.