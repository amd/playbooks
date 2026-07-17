<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Конфігурація платформи

Цей документ описує очікувані конфігурації платформи для запуску цього посібника.

## Передумови

### Windows

| Компонент | Версія | Примітки |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Попередньо встановлено та доступно в PATH на AMD Ryzen™ AI Halo Developer Platform; необхідно встановити вручну на всіх інших пристроях |
| **Lemonade Server** | остання | Запущено на `http://localhost:13305/api/v1` |

### Linux

| Компонент | Версія | Примітки |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Попередньо встановлено та доступно в PATH на AMD Ryzen™ AI Halo Developer Platform; необхідно встановити вручну на всіх інших пристроях |
| **Lemonade Server** | остання | Запущено на `http://localhost:13305/api/v1` |


## Lemonade LLM

Сервер Lemonade має бути запущено із завантаженою моделлю, відповідною для пристрою (див. README для команди `lemonade run` для вашого пристрою):

| Пристрій | Кінцева точка | Модель |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |