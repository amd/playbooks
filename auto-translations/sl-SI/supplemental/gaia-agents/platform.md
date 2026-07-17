<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfiguracija platforme

Ta dokument opisuje pričakovane konfiguracije platforme za izvajanje tega priročnika.

## Zahtevane aplikacije/ogrodja

### Windows/Linux

GAIA mora biti predhodno nameščena z uporabo navodil, navedenih v [Vodniku za namestitev GAIA](../../dependencies/gaia.md).

Lemonade Server mora biti predhodno nameščen z uporabo navodil, navedenih v [Vodniku za namestitev Lemonade](../../dependencies/lemonade.md).

## Zahtevani modeli

### Windows/Linux

Agent za svetovanje glede strojne opreme uporablja **Qwen3-Coder-30B** za sklepanje agenta. Ta model se samodejno prenese med `gaia init`. Ročno prenašanje modelov ni potrebno.