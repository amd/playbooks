<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije pregledana od strane čoveka. Može sadržati greške, a pojedini koraci, komande, preuzimanja ili dostupnost proizvoda mogu se razlikovati u vašem jeziku ili regionu. Ako nešto izgleda netačno, smatrajte da je originalni engleski playbook merodavan izvor.
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