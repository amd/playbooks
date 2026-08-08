<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Machinevertaling.** Deze pagina is automatisch vertaald vanuit het Engels en is niet door een mens gecontroleerd. Deze pagina kan fouten bevatten en bepaalde instructies, opdrachten, downloads, productbeschikbaarheid of andere inhoud kan per taal of regio verschillen. In geval van tegenstrijdigheid of discrepantie is de oorspronkelijke Engelse versie van de playbook doorslaggevend en prevaleert deze.
<!-- auto-translated-disclaimer:end -->

# Platformconfiguratie

Dit document beschrijft de verwachte platformconfiguraties voor het uitvoeren van deze playbook.

## Vereisten

### Windows

| Component | Versie | Opmerkingen |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Vooraf geïnstalleerd en beschikbaar in PATH op het AMD Ryzen™ AI Halo Developer Platform; moet handmatig worden geïnstalleerd op alle andere apparaten |
| **Lemonade Server** | nieuwste | Draait op `http://localhost:13305/api/v1` |

### Linux

| Component | Versie | Opmerkingen |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Vooraf geïnstalleerd en beschikbaar in PATH op het AMD Ryzen™ AI Halo Developer Platform; moet handmatig worden geïnstalleerd op alle andere apparaten |
| **Lemonade Server** | nieuwste | Draait op `http://localhost:13305/api/v1` |


## Lemonade LLM

De Lemonade-server moet draaien met het voor het apparaat geschikte model geladen (zie de README voor het `lemonade run`-commando voor uw apparaat):

| Apparaat | Endpoint | Model |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |