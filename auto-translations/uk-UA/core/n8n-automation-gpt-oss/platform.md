<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинний переклад.** Цю сторінку було автоматично перекладено з англійської мови, і вона не була перевірена людиною. Вона може містити помилки, а певні інструкції, команди, завантаження, доступність продукту чи інший вміст можуть відрізнятися залежно від мови чи регіону. У разі будь-яких невідповідностей чи розбіжностей переважну силу має оригінальна англомовна версія playbook.
<!-- auto-translated-disclaimer:end -->

# Конфігурація платформи

У цьому документі описано очікувані конфігурації платформи для виконання цього playbook.

## Попередні вимоги

### Windows

| Компонент | Версія | Примітки |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Попередньо встановлено та доступно в PATH на AMD Ryzen™ AI Halo Developer Platform; на всіх інших пристроях потрібно встановити вручну |
| **Lemonade Server** | остання | Працює за адресою `http://localhost:13305/api/v1` |

### Linux

| Компонент | Версія | Примітки |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Попередньо встановлено та доступно в PATH на AMD Ryzen™ AI Halo Developer Platform; на всіх інших пристроях потрібно встановити вручну |
| **Lemonade Server** | остання | Працює за адресою `http://localhost:13305/api/v1` |


## Lemonade LLM

Сервер Lemonade має бути запущений із завантаженою моделлю, що відповідає пристрою (див. README для команди `lemonade run` для вашого пристрою):

| Пристрій | Кінцева точка | Модель |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |