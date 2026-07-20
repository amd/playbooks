<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM предоставляется в виде готового образа контейнера с поддержкой ROCm. Используйте команду запуска (launcher) вместо установки vLLM или PyTorch непосредственно на хосте:

```bash
vllm-launch
```

Скрипт запуска запускает контейнер, задействует встроенный GPU и предоставляет доступ к API vLLM, совместимому с OpenAI, по адресу `http://localhost:8001`.