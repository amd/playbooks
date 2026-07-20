<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Alustan konfigurointi

Tässä dokumentissa kuvataan tämän playbookin ajamiseen odotetut alustan konfiguraatiot.

## Edellytykset

### Windows

| Komponentti | Versio | Huomautukset |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Esiasennettu ja saatavilla PATH-muuttujassa AMD Ryzen™ AI Halo Developer Platform -alustalla; on asennettava manuaalisesti kaikkiin muihin laitteisiin |
| **Lemonade Server** | latest | Käynnissä osoitteessa `http://localhost:13305/api/v1` |

### Linux

| Komponentti | Versio | Huomautukset |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Esiasennettu ja saatavilla PATH-muuttujassa AMD Ryzen™ AI Halo Developer Platform -alustalla; on asennettava manuaalisesti kaikkiin muihin laitteisiin |
| **Lemonade Server** | latest | Käynnissä osoitteessa `http://localhost:13305/api/v1` |


## Lemonade LLM

Lemonade-palvelimen tulisi olla käynnissä laitteelle sopiva malli ladattuna (katso README:sta `lemonade run` -komento laitteellesi):

| Laite | Päätepiste | Malli |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |