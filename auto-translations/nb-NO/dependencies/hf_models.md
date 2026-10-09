<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Hugging Face-modeller og datasett

Spillboken laster ned Hugging Face-modellene og datasettene sine første gang den bruker dem, og beholder dem i Hugging Face-hurtigbufferen (`~/.cache/huggingface/hub` med mindre `HF_HOME` eller `HF_HUB_CACHE` peker et annet sted), slik at senere kjøringer starter uten å laste dem ned på nytt.