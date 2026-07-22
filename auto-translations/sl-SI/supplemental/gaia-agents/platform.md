<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, nekateri koraki, ukazi, prenosi ali razpoložljivost izdelkov pa se lahko razlikujejo glede na vaš jezik ali regijo. Če se vam kaj zdi napačno, upoštevajte, da je izvirni angleški playbook merodajni vir.
<!-- auto-translated-disclaimer:end -->

# Konfiguracija platforme

Ta dokument opisuje pričakovane konfiguracije platforme za izvajanje tega priročnika.

## Zahtevane aplikacije/ogrodja

### Windows/Linux

GAIA mora biti vnaprej nameščena po navodilih iz [Vodnika za namestitev GAIA](../../dependencies/gaia.md).

Lemonade Server mora biti vnaprej nameščen po navodilih iz [Vodnika za namestitev Lemonade](../../dependencies/lemonade.md).

## Zahtevani modeli

### Windows/Linux

Agent Hardware Advisor za sklepanje agenta uporablja **Qwen3-Coder-30B**. Ta model se samodejno prenese med izvajanjem ukaza `gaia init`. Ročni prenos modelov ni potreben.