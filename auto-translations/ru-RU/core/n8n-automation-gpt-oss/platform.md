<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинный перевод.** Эта страница была автоматически переведена с английского языка и не прошла проверку человеком. Она может содержать ошибки, а некоторые инструкции, команды, файлы для загрузки, сведения о доступности продуктов или иное содержимое могут отличаться в зависимости от языка или региона. В случае каких-либо несоответствий или расхождений преимущественную силу имеет оригинальная версия playbook на английском языке.
<!-- auto-translated-disclaimer:end -->

# Конфигурация платформы

В этом документе описаны ожидаемые конфигурации платформы для выполнения этого плейбука.

## Предварительные требования

### Windows

| Компонент | Версия | Примечания |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Предустановлен и доступен в PATH на AMD Ryzen™ AI Halo Developer Platform; на всех остальных устройствах требуется установка вручную |
| **Lemonade Server** | latest | Работает по адресу `http://localhost:13305/api/v1` |

### Linux

| Компонент | Версия | Примечания |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Предустановлен и доступен в PATH на AMD Ryzen™ AI Halo Developer Platform; на всех остальных устройствах требуется установка вручную |
| **Lemonade Server** | latest | Работает по адресу `http://localhost:13305/api/v1` |


## Lemonade LLM

Сервер Lemonade должен быть запущен с загруженной моделью, соответствующей устройству (см. README для команды `lemonade run` для вашего устройства):

| Устройство | Конечная точка | Модель |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |