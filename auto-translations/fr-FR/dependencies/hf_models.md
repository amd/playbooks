<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Modèles et jeux de données Hugging Face

Le playbook télécharge ses modèles et jeux de données Hugging Face lors de leur première utilisation et les conserve dans le cache Hugging Face (`~/.cache/huggingface/hub`, sauf si `HF_HOME` ou `HF_HUB_CACHE` pointe ailleurs), de sorte que les exécutions ultérieures démarrent sans avoir à les retélécharger.