<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

O vLLM é disponibilizado através de uma imagem de contentor pré-criada com suporte para ROCm. Utilize o comando do launcher em vez de instalar o vLLM ou o PyTorch diretamente no anfitrião:

```bash
vllm-launch
```

O launcher inicia o contentor, direciona-o para o GPU integrado e expõe a API do vLLM compatível com OpenAI em `http://localhost:8001`.