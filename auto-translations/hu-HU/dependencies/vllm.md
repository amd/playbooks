<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

A vLLM egy előre elkészített, ROCm-támogatással rendelkező konténerképen keresztül érhető el. A launcher parancs használatával indítsd el, ahelyett hogy közvetlenül a hoszton telepítenéd a vLLM-et vagy a PyTorch-ot:

```bash
vllm-launch
```

A launcher elindítja a konténert, az integrált GPU-t célozza meg, és elérhetővé teszi az OpenAI-kompatibilis vLLM API-t a `http://localhost:8001` címen.