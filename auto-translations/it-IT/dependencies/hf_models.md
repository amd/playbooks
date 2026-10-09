<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Modelli e dataset Hugging Face

Il playbook scarica i suoi modelli e dataset Hugging Face al primo utilizzo e li conserva nella cache di Hugging Face (`~/.cache/huggingface/hub`, a meno che `HF_HOME` o `HF_HUB_CACHE` non puntino altrove), in modo che le esecuzioni successive partano senza doverli scaricare di nuovo.