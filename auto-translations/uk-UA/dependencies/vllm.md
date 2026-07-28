<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM надається у вигляді попередньо зібраного образу контейнера з підтримкою ROCm. Використовуйте команду запуску замість встановлення vLLM або PyTorch безпосередньо на хості:

```bash
vllm-launch
```

Ця команда запускає контейнер, використовує вбудований GPU та надає доступ до сумісного з OpenAI API vLLM за адресою `http://localhost:8001`.