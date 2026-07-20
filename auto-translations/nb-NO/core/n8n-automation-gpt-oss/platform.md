<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Plattformkonfigurasjon

Dette dokumentet beskriver de forventede plattformkonfigurasjonene for kjøring av denne playbooken.

## Forutsetninger

### Windows

| Komponent | Versjon | Merknader |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Forhåndsinstallert og tilgjengelig i PATH på AMD Ryzen™ AI Halo Developer Platform; må installeres manuelt på alle andre enheter |
| **Lemonade Server** | nyeste | Kjører på `http://localhost:13305/api/v1` |

### Linux

| Komponent | Versjon | Merknader |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Forhåndsinstallert og tilgjengelig i PATH på AMD Ryzen™ AI Halo Developer Platform; må installeres manuelt på alle andre enheter |
| **Lemonade Server** | nyeste | Kjører på `http://localhost:13305/api/v1` |


## Lemonade LLM

Lemonade-serveren bør kjøre med den enhetsspesifikke modellen lastet inn (se README for `lemonade run`-kommandoen for enheten din):

| Enhet | Endepunkt | Modell |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |