<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

O vLLM é fornecido por meio de uma imagem de contêiner pré-construída com suporte a ROCm. Use o comando do launcher em vez de instalar o vLLM ou o PyTorch diretamente no host:

```bash
vllm-launch
```

O launcher inicia o contêiner, direciona a GPU integrada e expõe a API do vLLM compatível com OpenAI em `http://localhost:8001`.