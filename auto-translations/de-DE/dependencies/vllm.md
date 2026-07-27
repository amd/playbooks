<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM wird über ein vorgefertigtes Container-Image mit ROCm-Unterstützung bereitgestellt. Verwenden Sie den Launcher-Befehl, anstatt vLLM oder PyTorch direkt auf dem Host zu installieren:

```bash
vllm-launch
```

Der Launcher startet den Container, adressiert die integrierte GPU und stellt die OpenAI-kompatible vLLM-API unter `http://localhost:8001` bereit.