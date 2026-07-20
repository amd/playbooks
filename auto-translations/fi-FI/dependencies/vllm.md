<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM tarjotaan valmiiksi rakennettuna konttikuvana, jossa on ROCm-tuki. Käytä käynnistyskomentoa sen sijaan, että asentaisit vLLM:n tai PyTorch:n suoraan isäntäkoneelle:

```bash
vllm-launch
```

Käynnistyskomento käynnistää kontin, kohdistaa sen integroituun GPU:hun ja tarjoaa OpenAI-yhteensopivan vLLM API:n osoitteessa `http://localhost:8001`.