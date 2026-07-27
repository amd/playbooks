<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM je na voljo prek vnaprej pripravljene slike vsebnika (container image) s podporo za ROCm. Namesto neposredne namestitve vLLM ali PyTorch na gostitelju uporabite ukaz za zagon (launcher):

```bash
vllm-launch
```

Zaganjalnik zažene vsebnik, cilja na integrirani GPU in izpostavi z OpenAI združljiv vLLM API na naslovu `http://localhost:8001`.