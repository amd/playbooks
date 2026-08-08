<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

# Konfiguracija platforme

Ta dokument opisuje pričakovane konfiguracije platforme za izvajanje tega priročnika.

## Predpogoji

### Windows

| Komponenta | Različica | Opombe |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Vnaprej nameščen in dosegljiv v PATH na platformi AMD Ryzen™ AI Halo Developer Platform; na vseh drugih napravah ga je treba namestiti ročno |
| **Lemonade Server** | najnovejša | Se izvaja na `http://localhost:13305/api/v1` |

### Linux

| Komponenta | Različica | Opombe |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Vnaprej nameščen in dosegljiv v PATH na platformi AMD Ryzen™ AI Halo Developer Platform; na vseh drugih napravah ga je treba namestiti ročno |
| **Lemonade Server** | najnovejša | Se izvaja na `http://localhost:13305/api/v1` |


## Lemonade LLM

Strežnik Lemonade mora delovati z naloženim modelom, ustreznim za napravo (glejte README za ukaz `lemonade run` za vašo napravo):

| Naprava | Končna točka | Model |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |