<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije proveravana od strane čoveka. Može sadržati greške, a određena uputstva, komande, preuzimanja, dostupnost proizvoda ili drugi sadržaj mogu se razlikovati u zavisnosti od jezika ili regiona. U slučaju bilo kakve nedoslednosti ili neslaganja, merodavna je originalna verzija playbook-a na engleskom jeziku.
<!-- auto-translated-disclaimer:end -->

# Konfiguracija platforme

Ovaj dokument opisuje očekivane konfiguracije platforme za pokretanje ovog priručnika (playbook).

## Preduslovi

### Windows

| Komponenta | Verzija | Napomene |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Unapred instaliran i dostupan u PATH-u na AMD Ryzen™ AI Halo Developer Platform; mora se ručno instalirati na svim ostalim uređajima |
| **Lemonade Server** | najnovija | Radi na `http://localhost:13305/api/v1` |

### Linux

| Komponenta | Verzija | Napomene |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Unapred instaliran i dostupan u PATH-u na AMD Ryzen™ AI Halo Developer Platform; mora se ručno instalirati na svim ostalim uređajima |
| **Lemonade Server** | najnovija | Radi na `http://localhost:13305/api/v1` |


## Lemonade LLM

Lemonade server treba da bude pokrenut sa učitanim modelom odgovarajućim za uređaj (pogledajte README za komandu `lemonade run` za vaš uređaj):

| Uređaj | Krajnja tačka | Model |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |