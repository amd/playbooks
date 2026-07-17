<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM jest dostarczany jako gotowy obraz kontenera z obsługą ROCm. Zamiast instalować vLLM lub PyTorch bezpośrednio na hoście, użyj polecenia uruchamiającego:

```bash
vllm-launch
```

Program uruchamiający startuje kontener, kieruje działanie na zintegrowany GPU i udostępnia API vLLM zgodne z OpenAI pod adresem `http://localhost:8001`.