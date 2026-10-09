<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Modele i zbiory danych Hugging Face

Playbook pobiera swoje modele i zbiory danych Hugging Face przy pierwszym użyciu i przechowuje je w pamięci podręcznej Hugging Face (`~/.cache/huggingface/hub`, chyba że `HF_HOME` lub `HF_HUB_CACHE` wskazuje inną lokalizację), dzięki czemu kolejne uruchomienia nie wymagają ponownego ich pobierania.