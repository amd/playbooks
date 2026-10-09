<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Modelos e conjuntos de dados do Hugging Face

O playbook baixa seus modelos e conjuntos de dados do Hugging Face na primeira vez que os utiliza e os mantém no cache do Hugging Face (`~/.cache/huggingface/hub`, a menos que `HF_HOME` ou `HF_HUB_CACHE` apontem para outro lugar), de modo que execuções posteriores iniciem sem a necessidade de baixá-los novamente.