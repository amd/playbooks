<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM jest dostarczany w postaci gotowego obrazu kontenera z obsługą ROCm. Zamiast instalować vLLM lub PyTorch bezpośrednio na hoście, użyj polecenia uruchamiającego (launcher):

```bash
vllm-launch
```

Launcher uruchamia kontener, kieruje działanie na zintegrowany GPU i udostępnia zgodne z OpenAI API vLLM pod adresem `http://localhost:8001`.