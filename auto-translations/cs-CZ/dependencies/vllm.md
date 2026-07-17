<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM je poskytován prostřednictvím předpřipraveného kontejnerového obrazu s podporou ROCm. Místo přímé instalace vLLM nebo PyTorch na hostiteli použijte příkaz spouštěče:

```bash
vllm-launch
```

Spouštěč spustí kontejner, zaměří se na integrovaný GPU a zpřístupní OpenAI-kompatibilní vLLM API na `http://localhost:8001`.