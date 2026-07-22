<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Конфигурация платформы

В этом документе описаны ожидаемые конфигурации платформы для запуска этого playbook.

## Необходимые приложения/фреймворки

### Windows/Linux

- **Lemonade Server** должен быть установлен согласно
  [руководству по установке Lemonade](https://lemonade-server.ai/docs/guide/install/).
- **Node.js 22.12 или новее** и `npm`, используемые CLI `agent-canvas` и MCP
  серверами, запускаемыми через `npx`.
- **uv**, менеджер пакетов Python, который Agent Canvas использует для управления
  средой агентского сервера. Установите его из
  [руководства по установке uv](https://docs.astral.sh/uv/getting-started/installation/).

## Необходимые модели

### Windows/Linux

Следующая модель должна быть доступна в Lemonade Server перед запуском
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

## Внешние учётные данные

Для этого playbook требуются:

- Токен GitHub с доступом на чтение к репозиторию, для которого создаётся сводка.
- Токен Slack-бота с правами `chat:write` и доступом на чтение каналов.
- ID команды Slack и ID целевого канала Slack.