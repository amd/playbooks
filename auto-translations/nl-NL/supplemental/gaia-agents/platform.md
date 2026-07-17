<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platformconfiguratie

Dit document beschrijft de verwachte platformconfiguraties voor het uitvoeren van dit playbook.

## Vereiste apps/frameworks

### Windows/Linux

GAIA moet vooraf worden geïnstalleerd aan de hand van de instructies in de [GAIA-installatiegids](../../dependencies/gaia.md).

Lemonade Server moet vooraf worden geïnstalleerd aan de hand van de instructies in de [Lemonade-installatiegids](../../dependencies/lemonade.md).

## Vereiste modellen

### Windows/Linux

De Hardware Advisor Agent gebruikt **Qwen3-Coder-30B** voor agentredenering. Dit model wordt automatisch gedownload tijdens `gaia init`. Er zijn geen handmatige modeldownloads vereist.