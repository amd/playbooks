<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM é fornecido por meio de uma imagem de contêiner pré-construída com suporte a ROCm. Use o comando do launcher em vez de instalar vLLM ou PyTorch diretamente no host:

```bash
vllm-launch
```

O launcher inicia o contêiner, direciona para o GPU integrado e expõe a API vLLM compatível com OpenAI em `http://localhost:8001`.