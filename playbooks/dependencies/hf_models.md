<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Hugging Face models and datasets

The playbook downloads its Hugging Face models and datasets the first time it uses them and keeps them in the Hugging Face cache (`~/.cache/huggingface/hub` unless `HF_HOME` or `HF_HUB_CACHE` points elsewhere), so later runs start without downloading them again.
