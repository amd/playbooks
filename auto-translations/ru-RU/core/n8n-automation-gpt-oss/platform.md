<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Конфигурация платформы

Этот документ описывает ожидаемые конфигурации платформы для запуска данного сценария.

## Предварительные требования

### Windows

| Компонент | Версия | Примечания |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Предустановлен и доступен в PATH на AMD Ryzen™ AI Halo Developer Platform; на всех остальных устройствах необходимо устанавливать вручную |
| **Lemonade Server** | последняя | Работает на `http://localhost:13305/api/v1` |

### Linux

| Компонент | Версия | Примечания |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Предустановлен и доступен в PATH на AMD Ryzen™ AI Halo Developer Platform; на всех остальных устройствах необходимо устанавливать вручную |
| **Lemonade Server** | последняя | Работает на `http://localhost:13305/api/v1` |


## Lemonade LLM

Сервер Lemonade должен быть запущен с загруженной моделью, соответствующей устройству (см. README для команды `lemonade run` для вашего устройства):

| Устройство | Конечная точка | Модель |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |