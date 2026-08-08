<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Machinevertaling.** Deze pagina is automatisch vertaald vanuit het Engels en is niet door een mens gecontroleerd. Deze pagina kan fouten bevatten en bepaalde instructies, opdrachten, downloads, productbeschikbaarheid of andere inhoud kan per taal of regio verschillen. In geval van tegenstrijdigheid of discrepantie is de oorspronkelijke Engelse versie van de playbook doorslaggevend en prevaleert deze.
<!-- auto-translated-disclaimer:end -->

# Platformconfiguratie

Dit document beschrijft de verwachte platformconfiguraties voor het uitvoeren van dit playbook.

## Vereiste apps/frameworks

### Windows/Linux

GAIA moet vooraf zijn geïnstalleerd volgens de instructies in de [GAIA-installatiehandleiding](../../dependencies/gaia.md).

Lemonade Server moet vooraf zijn geïnstalleerd volgens de instructies in de [Lemonade-installatiehandleiding](../../dependencies/lemonade.md).

## Vereiste modellen

### Windows/Linux

De Hardware Advisor Agent gebruikt **Qwen3-Coder-30B** voor agentredenering. Dit model wordt automatisch gedownload tijdens `gaia init`. Handmatig modellen downloaden is niet nodig.