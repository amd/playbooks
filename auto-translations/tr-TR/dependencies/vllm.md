<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM, ROCm desteğiyle önceden oluşturulmuş bir konteyner imajı aracılığıyla sağlanmaktadır. Ana makineye doğrudan vLLM veya PyTorch yüklemek yerine başlatıcı komutunu kullanın:

```bash
vllm-launch
```

Başlatıcı konteyneri başlatır, entegre GPU'yu hedefler ve OpenAI uyumlu vLLM API'sini `http://localhost:8001` adresinde kullanıma sunar.