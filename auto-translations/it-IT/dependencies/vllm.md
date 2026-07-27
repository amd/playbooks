<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM viene fornito tramite un'immagine container predefinita con supporto ROCm. Utilizzare il comando del launcher invece di installare vLLM o PyTorch direttamente sull'host:

```bash
vllm-launch
```

Il launcher avvia il container, seleziona la GPU integrata come destinazione ed espone l'API vLLM compatibile con OpenAI su `http://localhost:8001`.