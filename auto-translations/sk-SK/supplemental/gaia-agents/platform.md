<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfigurácia platformy

Tento dokument popisuje očakávané konfigurácie platformy pre spustenie tohto playbooku.

## Požadované aplikácie/frameworky

### Windows/Linux

GAIA by mala byť predinštalovaná podľa pokynov uvedených v [Sprievodcovi inštaláciou GAIA](../../dependencies/gaia.md).

Lemonade Server by mal byť predinštalovaný podľa pokynov uvedených v [Sprievodcovi inštaláciou Lemonade](../../dependencies/lemonade.md).

## Požadované modely

### Windows/Linux

Agent Hardware Advisor používa **Qwen3-Coder-30B** na uvažovanie agenta. Tento model sa stiahne automaticky počas `gaia init`. Nie sú potrebné žiadne manuálne sťahovania modelov.