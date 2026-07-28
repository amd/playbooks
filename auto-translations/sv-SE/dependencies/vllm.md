<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM tillhandahålls via en förbyggd containeravbildning med stöd för ROCm. Använd startkommandot (launcher) istället för att installera vLLM eller PyTorch direkt på värden:

```bash
vllm-launch
```

Startkommandot startar containern, riktar in sig på den integrerade GPU:n och exponerar det OpenAI-kompatibla vLLM-API:et på `http://localhost:8001`.