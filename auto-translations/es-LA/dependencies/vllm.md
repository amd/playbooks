<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM se proporciona a través de una imagen de contenedor prediseñada con soporte para ROCm. Usa el comando del iniciador en lugar de instalar vLLM o PyTorch directamente en el host:

```bash
vllm-launch
```

El iniciador arranca el contenedor, apunta a la GPU integrada y expone la API de vLLM compatible con OpenAI en `http://localhost:8001`.