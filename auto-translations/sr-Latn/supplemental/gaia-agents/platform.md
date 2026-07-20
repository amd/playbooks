<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfiguracija platforme

Ovaj dokument opisuje očekivane konfiguracije platforme za pokretanje ovog playbook-a.

## Potrebne aplikacije/frejmvorci

### Windows/Linux

GAIA treba unapred instalirati koristeći uputstva data u [Vodič za instalaciju GAIA](../../dependencies/gaia.md).

Lemonade Server treba unapred instalirati koristeći uputstva data u [Vodič za instalaciju Lemonade](../../dependencies/lemonade.md).

## Potrebni modeli

### Windows/Linux

Hardware Advisor Agent koristi **Qwen3-Coder-30B** za rezonovanje agenta. Ovaj model se automatski preuzima tokom `gaia init`. Nije potrebno ručno preuzimanje modela.