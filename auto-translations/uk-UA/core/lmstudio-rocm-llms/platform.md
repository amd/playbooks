<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Машинний переклад.** Цю сторінку автоматично перекладено з англійської мови, і вона не була перевірена людиною. Вона може містити помилки, а деякі кроки, команди, завантаження або доступність продуктів можуть відрізнятися у вашій мові чи регіоні. Якщо щось виглядає неправильно, вважайте оригінальний англомовний playbook джерелом достовірної інформації.
<!-- auto-translated-disclaimer:end -->

# Конфігурація платформи

Цей документ описує очікувані конфігурації платформи для виконання цього посібника.

## Windows

### Встановлення LM Studio

LM Studio має бути попередньо встановлено:

| Компонент | Версія | Розташування |
|-----------|---------|----------|
| **LM Studio (Models + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Завантаження моделі

Наступні моделі мають вже бути присутні в каталозі моделей LM Studio (`C:\Users\...\.lmstudio\models`):

| Пристрій | Тип моделі | Квантування | Розмір (ГБ) | Розташування |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### Встановлення LM Studio

Дивіться [lmstudio.md](../../dependencies/lmstudio.md) для отримання додаткової інформації.

### Завантаження моделі

Так само, як і на Windows.