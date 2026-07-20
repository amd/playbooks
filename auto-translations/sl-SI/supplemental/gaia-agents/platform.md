<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfiguracija platforme

Ta dokument opisuje pričakovane konfiguracije platforme za izvajanje tega priročnika.

## Zahtevane aplikacije/ogrodja

### Windows/Linux

GAIA mora biti vnaprej nameščena po navodilih iz [Vodnika za namestitev GAIA](../../dependencies/gaia.md).

Lemonade Server mora biti vnaprej nameščen po navodilih iz [Vodnika za namestitev Lemonade](../../dependencies/lemonade.md).

## Zahtevani modeli

### Windows/Linux

Agent Hardware Advisor za sklepanje agenta uporablja **Qwen3-Coder-30B**. Ta model se samodejno prenese med izvajanjem ukaza `gaia init`. Ročni prenos modelov ni potreben.