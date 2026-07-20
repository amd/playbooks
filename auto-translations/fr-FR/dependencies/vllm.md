<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM est fourni sous la forme d'une image de conteneur préconstruite avec prise en charge de ROCm. Utilisez la commande du lanceur au lieu d'installer vLLM ou PyTorch directement sur l'hôte :

```bash
vllm-launch
```

Le lanceur démarre le conteneur, cible le GPU intégré et expose l'API vLLM compatible OpenAI sur `http://localhost:8001`.