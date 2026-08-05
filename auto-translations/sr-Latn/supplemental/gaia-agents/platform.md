<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije proveravana od strane čoveka. Može sadržati greške, a određena uputstva, komande, preuzimanja, dostupnost proizvoda ili drugi sadržaj mogu se razlikovati u zavisnosti od jezika ili regiona. U slučaju bilo kakve nedoslednosti ili neslaganja, merodavna je originalna verzija playbook-a na engleskom jeziku.
<!-- auto-translated-disclaimer:end -->

# Konfiguracija platforme

Ovaj dokument opisuje očekivane konfiguracije platforme za pokretanje ovog playbook-a.

## Potrebne aplikacije/frejmvorci

### Windows/Linux

GAIA treba unapred instalirati koristeći uputstva data u [Vodič za instalaciju GAIA](../../dependencies/gaia.md).

Lemonade Server treba unapred instalirati koristeći uputstva data u [Vodič za instalaciju Lemonade](../../dependencies/lemonade.md).

## Potrebni modeli

### Windows/Linux

Hardware Advisor Agent koristi **Qwen3-Coder-30B** za rezonovanje agenta. Ovaj model se automatski preuzima tokom `gaia init`. Nije potrebno ručno preuzimanje modela.