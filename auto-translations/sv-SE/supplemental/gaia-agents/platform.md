<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Plattformskonfiguration

Detta dokument beskriver de förväntade plattformskonfigurationerna för att köra denna spelbok.

## Obligatoriska appar/ramverk

### Windows/Linux

GAIA bör vara förinstallerat med hjälp av instruktionerna som tillhandahålls i [GAIA-installationsguide](../../dependencies/gaia.md).

Lemonade Server bör vara förinstallerat med hjälp av instruktionerna som tillhandahålls i [Lemonade-installationsguide](../../dependencies/lemonade.md).

## Obligatoriska modeller

### Windows/Linux

Hardware Advisor Agent använder **Qwen3-Coder-30B** för agentresonemang. Denna modell laddas ner automatiskt under `gaia init`. Ingen manuell modellnedladdning krävs.