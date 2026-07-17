<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

A vLLM egy előre elkészített, ROCm támogatással rendelkező konténer képfájlon keresztül érhető el. A vLLM vagy PyTorch közvetlen gazdagépre történő telepítése helyett használja az indítóparancsot:

```bash
vllm-launch
```

Az indító elindítja a konténert, az integrált GPU-t célozza meg, és az OpenAI-kompatibilis vLLM API-t a `http://localhost:8001` címen teszi elérhetővé.