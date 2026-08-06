<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinöversättning.** Den här sidan har automatiskt översatts från engelska och har inte granskats av en människa. Den kan innehålla fel, och vissa instruktioner, kommandon, nedladdningar, produkttillgänglighet eller annat innehåll kan variera beroende på språk eller region. Vid eventuella motsägelser eller avvikelser är det den ursprungliga engelska versionen av playbook som gäller och har företräde.
<!-- auto-translated-disclaimer:end -->

# Plattformskonfiguration

Detta dokument beskriver de förväntade plattformskonfigurationerna för att köra denna spelbok.

## Obligatoriska appar/ramverk

### Windows/Linux

GAIA bör vara förinstallerat med hjälp av instruktionerna som tillhandahålls i [GAIA-installationsguide](../../dependencies/gaia.md).

Lemonade Server bör vara förinstallerat med hjälp av instruktionerna som tillhandahålls i [Lemonade-installationsguide](../../dependencies/lemonade.md).

## Obligatoriska modeller

### Windows/Linux

Hardware Advisor Agent använder **Qwen3-Coder-30B** för agentresonemang. Denna modell laddas ner automatiskt under `gaia init`. Ingen manuell modellnedladdning krävs.