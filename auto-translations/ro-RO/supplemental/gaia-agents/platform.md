<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configurarea Platformei

Acest document descrie configurațiile de platformă așteptate pentru rularea acestui playbook.

## Aplicații/Framework-uri Necesare

### Windows/Linux

GAIA trebuie să fie preinstalat folosind instrucțiunile furnizate în [Ghidul de Instalare GAIA](../../dependencies/gaia.md).

Lemonade Server trebuie să fie preinstalat folosind instrucțiunile furnizate în [Ghidul de Instalare Lemonade](../../dependencies/lemonade.md).

## Modele Necesare

### Windows/Linux

Hardware Advisor Agent utilizează **Qwen3-Coder-30B** pentru raționamentul agentului. Acest model este descărcat automat în timpul `gaia init`. Nu sunt necesare descărcări manuale de modele.