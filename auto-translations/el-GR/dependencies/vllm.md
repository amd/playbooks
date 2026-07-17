<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

Το vLLM παρέχεται μέσω ενός προκατασκευασμένου container image με υποστήριξη ROCm. Χρησιμοποιήστε την εντολή εκκίνησης αντί να εγκαταστήσετε απευθείας το vLLM ή το PyTorch στον host:

```bash
vllm-launch
```

Η εκκίνηση ξεκινά το container, στοχεύει στο integrated GPU και εκθέτει το OpenAI-compatible vLLM API στο `http://localhost:8001`.