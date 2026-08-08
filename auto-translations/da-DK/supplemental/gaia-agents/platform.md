<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversættelse.** Denne side er automatisk oversat fra engelsk og er ikke blevet gennemgået af et menneske. Den kan indeholde fejl, og visse instruktioner, kommandoer, downloads, produkttilgængelighed eller andet indhold kan variere afhængigt af sprog eller region. I tilfælde af uoverensstemmelse eller afvigelse er den oprindelige engelske version af playbook'en gældende og har forrang.
<!-- auto-translated-disclaimer:end -->

# Platformkonfiguration

Dette dokument beskriver de forventede platformkonfigurationer for kørsel af denne playbook.

## Påkrævede apps/frameworks

### Windows/Linux

GAIA bør være forudinstalleret ved hjælp af instruktionerne i [GAIA Installation Guide](../../dependencies/gaia.md).

Lemonade Server bør være forudinstalleret ved hjælp af instruktionerne i [Lemonade Installation Guide](../../dependencies/lemonade.md).

## Påkrævede modeller

### Windows/Linux

Hardware Advisor Agent bruger **Qwen3-Coder-30B** til agent-ræsonnering. Denne model downloades automatisk under `gaia init`. Det er ikke nødvendigt at downloade modeller manuelt.