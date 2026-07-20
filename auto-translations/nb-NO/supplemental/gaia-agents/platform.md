<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Plattformkonfigurasjon

Dette dokumentet beskriver de forventede plattformkonfigurasjonene for å kjøre denne playbooken.

## Nødvendige apper/rammeverk

### Windows/Linux

GAIA bør være forhåndsinstallert ved hjelp av instruksjonene i [GAIA-installasjonsveiledning](../../dependencies/gaia.md).

Lemonade Server bør være forhåndsinstallert ved hjelp av instruksjonene i [Lemonade-installasjonsveiledning](../../dependencies/lemonade.md).

## Nødvendige modeller

### Windows/Linux

Hardware Advisor Agent bruker **Qwen3-Coder-30B** til agentresonnering. Denne modellen lastes ned automatisk under `gaia init`. Ingen manuell nedlasting av modeller er nødvendig.