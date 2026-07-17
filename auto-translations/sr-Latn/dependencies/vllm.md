<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM se isporučuje putem unapred izgrađene slike kontejnera sa ROCm podrškom. Koristite komandu pokretača umesto direktnog instaliranja vLLM ili PyTorch na hostu:

```bash
vllm-launch
```

Pokretač pokreće kontejner, cilja integrisani GPU i izlaže OpenAI-kompatibilni vLLM API na `http://localhost:8001`.