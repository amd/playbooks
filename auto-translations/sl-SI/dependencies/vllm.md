<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM je na voljo prek vnaprej pripravljene slike vsebnika s podporo za ROCm. Namesto neposredne namestitve vLLM ali PyTorch na gostitelju uporabite ukaz za zagon:

```bash
vllm-launch
```

Zaganjalnik zažene vsebnik, cilja na integrirani GPU in izpostavi OpenAI-združljiv vLLM API na `http://localhost:8001`.