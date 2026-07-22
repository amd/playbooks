<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Конфигурация платформы

В этом документе описываются ожидаемые конфигурации платформы для выполнения этого playbook.

## Необходимые приложения/фреймворки

### Windows/Linux

- **Lemonade Server** должен быть установлен согласно
  [руководству по установке Lemonade](https://lemonade-server.ai/docs/guide/install/).
- **Node.js 22.12 или новее** и `npm`, используемые CLI `agent-canvas`.
- **uv**, менеджер пакетов Python, который Agent Canvas использует для управления
  окружением сервера агента. Установите его согласно
  [руководству по установке uv](https://docs.astral.sh/uv/getting-started/installation/).

## Необходимые модели

### Windows/Linux

Следующая модель должна быть доступна для Lemonade Server перед запуском
playbook.

| Тип модели | ID модели | Примечания |
| --- | --- | --- |
| GGUF чат-модель | `Qwen3.6-35B-A3B-GGUF` | Обслуживается Lemonade Server по адресу `http://127.0.0.1:13305/api/v1`. Используйте модель GGUF меньшего размера на устройствах с объёмом памяти менее 32 ГБ. |

Запустите модель с помощью:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```
