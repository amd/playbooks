<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM leveres gjennom et ferdigbygd containerbilde med støtte for ROCm. Bruk launcher-kommandoen i stedet for å installere vLLM eller PyTorch direkte på verten:

```bash
vllm-launch
```

Launcheren starter containeren, retter seg mot den integrerte GPU-en, og eksponerer det OpenAI-kompatible vLLM-API-et på `http://localhost:8001`.