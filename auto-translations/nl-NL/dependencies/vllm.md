<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM wordt geleverd via een vooraf gebouwde containerimage met ROCm-ondersteuning. Gebruik het launcher-commando in plaats van vLLM of PyTorch rechtstreeks op de host te installeren:

```bash
vllm-launch
```

De launcher start de container, richt zich op de geïntegreerde GPU en stelt de OpenAI-compatibele vLLM API beschikbaar op `http://localhost:8001`.