<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Конфігурація платформи

У цьому документі описано очікувані конфігурації платформи для виконання цього playbook.

## Windows

### Встановлення LM Studio

LM Studio має бути попередньо встановлено:

| Компонент | Версія | Розташування |
|-----------|---------|----------|
| **LM Studio (Models + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Завантаження моделі

Наведені нижче моделі мають вже перебувати в каталозі моделей LM Studio (`C:\Users\...\.lmstudio\models`):

| Тип моделі | Квантування | Розмір | Розташування |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### Встановлення LM Studio

Докладніші відомості наведено в lmstudio.md (у папці dependencies).

### Завантаження моделі

Так само, як і в Windows.