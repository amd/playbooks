<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Modelos e conjuntos de dados Hugging Face

O playbook transfere os seus modelos e conjuntos de dados Hugging Face na primeira vez que os utiliza e mantém-nos na cache do Hugging Face (`~/.cache/huggingface/hub`, a menos que `HF_HOME` ou `HF_HUB_CACHE` apontem para outro local), pelo que execuções posteriores começam sem ser necessário transferi-los novamente.