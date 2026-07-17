<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM leveres gjennom et forhåndsbygd container-image med ROCm-støtte. Bruk launcher-kommandoen i stedet for å installere vLLM eller PyTorch direkte på verten:

```bash
vllm-launch
```

Launcheren starter containeren, retter seg mot den integrerte GPU, og eksponerer det OpenAI-kompatible vLLM API på `http://localhost:8001`.