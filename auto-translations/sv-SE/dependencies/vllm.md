<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM tillhandahålls via en förbyggd containeravbildning med ROCm-stöd. Använd startkommandot istället för att installera vLLM eller PyTorch direkt på värden:

```bash
vllm-launch
```

Startprogrammet startar containern, riktar sig mot den integrerade GPU:n och exponerar det OpenAI-kompatibla vLLM API:et på `http://localhost:8001`.