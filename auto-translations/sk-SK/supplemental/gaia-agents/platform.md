<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

# Konfigurácia platformy

Tento dokument popisuje očakávané konfigurácie platformy na spustenie tejto príručky.

## Požadované aplikácie/frameworky

### Windows/Linux

GAIA by mala byť predinštalovaná podľa pokynov uvedených v [Návode na inštaláciu GAIA](../../dependencies/gaia.md).

Lemonade Server by mal byť predinštalovaný podľa pokynov uvedených v [Návode na inštaláciu Lemonade](../../dependencies/lemonade.md).

## Požadované modely

### Windows/Linux

Agent Hardware Advisor používa na uvažovanie agenta model **Qwen3-Coder-30B**. Tento model sa automaticky stiahne počas `gaia init`. Manuálne sťahovanie modelov nie je potrebné.