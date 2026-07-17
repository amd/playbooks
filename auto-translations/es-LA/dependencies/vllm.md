<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM se proporciona a través de una imagen de contenedor precompilada con soporte para ROCm. Usa el comando del lanzador en lugar de instalar vLLM o PyTorch directamente en el host:

```bash
vllm-launch
```

El lanzador inicia el contenedor, apunta al iGPU integrado y expone la API de vLLM compatible con OpenAI en `http://localhost:8001`.