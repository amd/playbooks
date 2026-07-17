<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM è fornito tramite un'immagine container precompilata con supporto ROCm. Usa il comando launcher invece di installare vLLM o PyTorch direttamente sull'host:

```bash
vllm-launch
```

Il launcher avvia il container, punta alla GPU integrata ed espone l'API vLLM compatibile con OpenAI su `http://localhost:8001`.