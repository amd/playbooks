<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Modèles et ensembles de données Hugging Face

Le playbook télécharge ses modèles et ensembles de données Hugging Face lors de leur première utilisation, puis les conserve dans le cache Hugging Face (`~/.cache/huggingface/hub`, à moins que `HF_HOME` ou `HF_HUB_CACHE` n'indique un autre emplacement), de sorte que les exécutions suivantes démarrent sans avoir à les retélécharger.