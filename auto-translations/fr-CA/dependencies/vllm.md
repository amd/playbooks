<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM est fourni sous forme d'image de conteneur préconstruite avec prise en charge de ROCm. Utilisez la commande de lancement au lieu d'installer vLLM ou PyTorch directement sur l'hôte :

```bash
vllm-launch
```

Le lanceur démarre le conteneur, cible le GPU intégré et expose l'API vLLM compatible OpenAI sur `http://localhost:8001`.