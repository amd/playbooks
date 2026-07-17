<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM поставляется в виде готового образа контейнера с поддержкой ROCm. Используйте команду запуска вместо прямой установки vLLM или PyTorch на хост:

```bash
vllm-launch
```

Лаунчер запускает контейнер, использует интегрированный GPU и открывает совместимый с OpenAI API vLLM по адресу `http://localhost:8001`.