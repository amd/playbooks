<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinöversättning.** Den här sidan har automatiskt översatts från engelska och har inte granskats av en människa. Den kan innehålla fel, och vissa instruktioner, kommandon, nedladdningar, produkttillgänglighet eller annat innehåll kan variera beroende på språk eller region. Vid eventuella motsägelser eller avvikelser är det den ursprungliga engelska versionen av playbook som gäller och har företräde.
<!-- auto-translated-disclaimer:end -->

# Plattformskonfiguration

Detta dokument beskriver de förväntade plattformskonfigurationerna för att köra denna playbook.

## Förutsättningar

### Windows

| Komponent | Version | Anteckningar |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Förinstallerat och tillgängligt i PATH på AMD Ryzen™ AI Halo Developer Platform; måste installeras manuellt på alla andra enheter |
| **Lemonade Server** | senaste | Körs på `http://localhost:13305/api/v1` |

### Linux

| Komponent | Version | Anteckningar |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Förinstallerat och tillgängligt i PATH på AMD Ryzen™ AI Halo Developer Platform; måste installeras manuellt på alla andra enheter |
| **Lemonade Server** | senaste | Körs på `http://localhost:13305/api/v1` |


## Lemonade LLM

Lemonade-servern bör vara igång med den för enheten lämpliga modellen inläst (se README för kommandot `lemonade run` för din enhet):

| Enhet | Ändpunkt | Modell |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |