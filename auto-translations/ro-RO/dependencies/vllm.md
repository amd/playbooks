<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM este furnizat printr-o imagine de container preconstruită cu suport ROCm. Utilizați comanda de lansare în loc să instalați vLLM sau PyTorch direct pe gazdă:

```bash
vllm-launch
```

Lansatorul pornește containerul, vizează GPU-ul integrat și expune API-ul vLLM compatibil cu OpenAI pe `http://localhost:8001`.