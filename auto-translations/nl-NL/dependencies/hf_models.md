<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Hugging Face-modellen en datasets

Het playbook downloadt de Hugging Face-modellen en datasets bij het eerste gebruik en bewaart ze in de Hugging Face-cache (`~/.cache/huggingface/hub`, tenzij `HF_HOME` of `HF_HUB_CACHE` naar een andere locatie verwijst), zodat latere runs starten zonder dat ze opnieuw hoeven te worden gedownload.