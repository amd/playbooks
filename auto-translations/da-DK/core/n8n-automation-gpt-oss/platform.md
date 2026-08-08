<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversættelse.** Denne side er automatisk oversat fra engelsk og er ikke blevet gennemgået af et menneske. Den kan indeholde fejl, og visse instruktioner, kommandoer, downloads, produkttilgængelighed eller andet indhold kan variere afhængigt af sprog eller region. I tilfælde af uoverensstemmelse eller afvigelse er den oprindelige engelske version af playbook'en gældende og har forrang.
<!-- auto-translated-disclaimer:end -->

# Platformkonfiguration

Dette dokument beskriver de forventede platformkonfigurationer til afvikling af denne playbook.

## Forudsætninger

### Windows

| Komponent | Version | Bemærkninger |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Forudinstalleret og tilgængelig i PATH på AMD Ryzen™ AI Halo Developer Platform; skal installeres manuelt på alle andre enheder |
| **Lemonade Server** | seneste | Kører på `http://localhost:13305/api/v1` |

### Linux

| Komponent | Version | Bemærkninger |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Forudinstalleret og tilgængelig i PATH på AMD Ryzen™ AI Halo Developer Platform; skal installeres manuelt på alle andre enheder |
| **Lemonade Server** | seneste | Kører på `http://localhost:13305/api/v1` |


## Lemonade LLM

Lemonade-serveren skal køre med den enhedsspecifikke model indlæst (se README for `lemonade run`-kommandoen til din enhed):

| Enhed | Endpoint | Model |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |