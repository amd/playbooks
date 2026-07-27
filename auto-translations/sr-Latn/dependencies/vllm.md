<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM se isporučuje kroz unapred izgrađenu kontejnersku sliku sa ROCm podrškom. Koristite komandu za pokretanje umesto direktne instalacije vLLM-a ili PyTorch-a na hostu:

```bash
vllm-launch
```

Pokretač (launcher) pokreće kontejner, cilja integrisani GPU i izlaže OpenAI-kompatibilan vLLM API na `http://localhost:8001`.