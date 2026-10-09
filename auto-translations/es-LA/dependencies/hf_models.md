<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Modelos y datasets de Hugging Face

El playbook descarga sus modelos y datasets de Hugging Face la primera vez que los utiliza y los conserva en la caché de Hugging Face (`~/.cache/huggingface/hub`, a menos que `HF_HOME` o `HF_HUB_CACHE` apunten a otra ubicación), de modo que las ejecuciones posteriores comiencen sin necesidad de volver a descargarlos.