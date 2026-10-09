<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Hugging Face-modeller og -datasæt

Playbooken downloader sine Hugging Face-modeller og -datasæt, første gang den bruger dem, og gemmer dem i Hugging Face-cachen (`~/.cache/huggingface/hub`, medmindre `HF_HOME` eller `HF_HUB_CACHE` peger et andet sted hen), så senere kørsler starter uden at skulle downloade dem igen.