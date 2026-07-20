<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM je poskytovaný prostredníctvom vopred zostaveného kontajnerového obrazu s podporou ROCm. Namiesto priamej inštalácie vLLM alebo PyTorch na hostiteľskom systéme použite príkaz spúšťača:

```bash
vllm-launch
```

Spúšťač spustí kontajner, zacieli na integrovanú GPU a sprístupní OpenAI-kompatibilné vLLM API na `http://localhost:8001`.