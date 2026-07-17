<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platformconfiguratie

Dit document beschrijft de verwachte platformconfiguraties voor het uitvoeren van dit playbook.

## Vereisten

### Windows

| Component | Versie | Opmerkingen |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Vooraf geïnstalleerd en beschikbaar in PATH op het AMD Ryzen™ AI Halo Developer Platform; moet handmatig worden geïnstalleerd op alle andere apparaten |
| **Lemonade Server** | nieuwste | Actief op `http://localhost:13305/api/v1` |

### Linux

| Component | Versie | Opmerkingen |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Vooraf geïnstalleerd en beschikbaar in PATH op het AMD Ryzen™ AI Halo Developer Platform; moet handmatig worden geïnstalleerd op alle andere apparaten |
| **Lemonade Server** | nieuwste | Actief op `http://localhost:13305/api/v1` |


## Lemonade LLM

De Lemonade server moet actief zijn met het apparaatgeschikte model geladen (zie de README voor het `lemonade run`-commando voor uw apparaat):

| Apparaat | Eindpunt | Model |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |