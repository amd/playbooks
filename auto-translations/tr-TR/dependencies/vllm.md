<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM, ROCm desteğine sahip önceden oluşturulmuş bir konteyner görüntüsü aracılığıyla sağlanır. vLLM veya PyTorch'u doğrudan ana makineye yüklemek yerine başlatıcı komutunu kullanın:

```bash
vllm-launch
```

Başlatıcı konteyneri başlatır, entegre GPU'yu hedefler ve OpenAI uyumlu vLLM API'sini `http://localhost:8001` adresinde kullanıma sunar.