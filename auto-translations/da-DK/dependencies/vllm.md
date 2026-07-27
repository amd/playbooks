<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM leveres via et prækompileret containerbillede med ROCm-understøttelse. Brug launcher-kommandoen i stedet for at installere vLLM eller PyTorch direkte på værten:

```bash
vllm-launch
```

Launcheren starter containeren, målretter mod den integrerede GPU og eksponerer det OpenAI-kompatible vLLM API på `http://localhost:8001`.