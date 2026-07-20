<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

Το vLLM παρέχεται μέσω μιας προκατασκευασμένης εικόνας container με υποστήριξη ROCm. Χρησιμοποιήστε την εντολή launcher αντί να εγκαταστήσετε το vLLM ή το PyTorch απευθείας στον host:

```bash
vllm-launch
```

Ο launcher εκκινεί το container, στοχεύει την ενσωματωμένη GPU και εκθέτει το συμβατό με OpenAI API του vLLM στο `http://localhost:8001`.