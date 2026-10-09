<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Hugging Face modellek és adatkészletek

A könyvtár első használatkor letölti a szükséges Hugging Face modelleket és adatkészleteket, majd eltárolja azokat a Hugging Face gyorsítótárában (`~/.cache/huggingface/hub`, hacsak a `HF_HOME` vagy a `HF_HUB_CACHE` máshova nem mutat), így a későbbi futtatások már nem igénylik azok ismételt letöltését.