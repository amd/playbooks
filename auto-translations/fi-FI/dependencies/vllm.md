<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM toimitetaan valmiiksi rakennetun konttikuvan kautta ROCm-tuella. Käytä käynnistyskomentoa vLLM:n tai PyTorchin suoran asentamisen sijaan isäntäjärjestelmälle:

```bash
vllm-launch
```

Käynnistyskomento käynnistää kontin, kohdistaa integroidun GPU:n ja tarjoaa OpenAI-yhteensopivan vLLM API:n osoitteessa `http://localhost:8001`.