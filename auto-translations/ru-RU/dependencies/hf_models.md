<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Модели и датасеты Hugging Face

Плейбук скачивает свои модели и датасеты Hugging Face при первом использовании и сохраняет их в кеше Hugging Face (`~/.cache/huggingface/hub`, если только `HF_HOME` или `HF_HUB_CACHE` не указывают на другое расположение), поэтому при последующих запусках повторная загрузка не требуется.