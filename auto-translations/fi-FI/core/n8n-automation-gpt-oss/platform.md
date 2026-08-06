<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se voi sisältää virheitä, ja tietyt ohjeet, komennot, lataukset, tuotteiden saatavuus tai muu sisältö voivat vaihdella kielen tai alueen mukaan. Mahdollisten ristiriitaisuuksien tai epäjohdonmukaisuuksien ilmetessä alkuperäinen englanninkielinen playbook on ratkaiseva ja ensisijainen versio.
<!-- auto-translated-disclaimer:end -->

# Alustan määritys

Tässä asiakirjassa kuvataan tämän ohjeiston suorittamiseen tarvittavat alustan määritykset.

## Edellytykset

### Windows

| Komponentti | Versio | Huomautukset |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Esiasennettu ja käytettävissä PATH-muuttujassa AMD Ryzen™ AI Halo Developer Platform -laitteessa; muihin laitteisiin on asennettava manuaalisesti |
| **Lemonade Server** | uusin | Toimii osoitteessa `http://localhost:13305/api/v1` |

### Linux

| Komponentti | Versio | Huomautukset |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Esiasennettu ja käytettävissä PATH-muuttujassa AMD Ryzen™ AI Halo Developer Platform -laitteessa; muihin laitteisiin on asennettava manuaalisesti |
| **Lemonade Server** | uusin | Toimii osoitteessa `http://localhost:13305/api/v1` |


## Lemonade LLM

Lemonade-palvelimen tulee olla käynnissä ja laitteelle sopiva malli ladattuna (katso oman laitteesi `lemonade run`-komento README-tiedostosta):

| Laite | Päätepiste | Malli |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |