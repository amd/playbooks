<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM este disponibil printr-o imagine de container preconstruită cu suport ROCm. Utilizați comanda launcher-ului în loc să instalați vLLM sau PyTorch direct pe sistemul gazdă:

```bash
vllm-launch
```

Launcher-ul pornește containerul, vizează GPU-ul integrat și expune API-ul vLLM compatibil cu OpenAI la `http://localhost:8001`.