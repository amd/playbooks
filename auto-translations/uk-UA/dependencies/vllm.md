<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM надається через попередньо зібраний образ контейнера з підтримкою ROCm. Використовуйте команду запуску замість безпосереднього встановлення vLLM або PyTorch на хості:

```bash
vllm-launch
```

Засіб запуску стартує контейнер, орієнтується на інтегрований GPU та відкриває сумісний з OpenAI API vLLM за адресою `http://localhost:8001`.