<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversettelse.** Denne siden ble automatisk oversatt fra engelsk og har ikke blitt gjennomgått av et menneske. Den kan inneholde feil, og enkelte instruksjoner, kommandoer, nedlastinger, produkttilgjengelighet eller annet innhold kan variere etter språk eller region. Ved eventuelle uoverensstemmelser eller avvik er den opprinnelige engelske versjonen av playbook-en gjeldende.
<!-- auto-translated-disclaimer:end -->

# Plattformkonfigurasjon

Dette dokumentet beskriver de forventede plattformkonfigurasjonene for å kjøre denne playbooken.

## Nødvendige apper/rammeverk

### Windows/Linux

GAIA bør være forhåndsinstallert ved hjelp av instruksjonene i [GAIA-installasjonsveiledning](../../dependencies/gaia.md).

Lemonade Server bør være forhåndsinstallert ved hjelp av instruksjonene i [Lemonade-installasjonsveiledning](../../dependencies/lemonade.md).

## Nødvendige modeller

### Windows/Linux

Hardware Advisor Agent bruker **Qwen3-Coder-30B** til agentresonnering. Denne modellen lastes ned automatisk under `gaia init`. Ingen manuell nedlasting av modeller er nødvendig.