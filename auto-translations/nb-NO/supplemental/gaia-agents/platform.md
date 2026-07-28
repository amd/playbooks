<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Maskinoversettelse.** Denne siden er automatisk oversatt fra engelsk og har ikke blitt gjennomgått av et menneske. Den kan inneholde feil, og enkelte trinn, kommandoer, nedlastinger eller produkttilgjengelighet kan variere i ditt språk eller din region. Hvis noe ser feil ut, bør du behandle den originale engelske veiledningen som den korrekte kilden.
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