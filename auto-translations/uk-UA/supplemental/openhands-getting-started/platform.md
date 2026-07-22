<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Конфігурація платформи

Цей документ описує очікувані конфігурації платформи для запуску цього playbook.

## Необхідні застосунки/фреймворки

### Windows/Linux

- **Lemonade Server** слід встановити, дотримуючись
  [посібника зі встановлення Lemonade](https://lemonade-server.ai/docs/guide/install/).
- **Node.js 22.12 або новіше** та `npm`, що використовуються CLI `agent-canvas`.
- **uv**, менеджер пакетів Python, який Agent Canvas використовує для керування
  середовищем сервера агента. Встановіть його з
  [посібника зі встановлення uv](https://docs.astral.sh/uv/getting-started/installation/).

## Необхідні моделі

### Windows/Linux

Наступна модель має бути доступна для Lemonade Server перед запуском
playbook.

| Тип моделі | ID моделі | Примітки |
| --- | --- | --- |
| GGUF чат-модель | `Qwen3.6-35B-A3B-GGUF` | Обслуговується Lemonade Server за адресою `http://127.0.0.1:13305/api/v1`. Використовуйте меншу GGUF модель на пристроях з менш ніж 32 ГБ пам'яті. |

Запустіть модель за допомогою:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```
