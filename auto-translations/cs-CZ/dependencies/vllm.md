<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM je poskytován prostřednictvím předpřipraveného obrazu kontejneru s podporou ROCm. Místo instalace vLLM nebo PyTorch přímo na hostitele použijte příkaz spouštěče:

```bash
vllm-launch
```

Spouštěč spustí kontejner, zacílí na integrovanou GPU a zpřístupní API vLLM kompatibilní s OpenAI na adrese `http://localhost:8001`.