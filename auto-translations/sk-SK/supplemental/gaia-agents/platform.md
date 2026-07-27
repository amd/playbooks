<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré kroky, príkazy, súbory na stiahnutie alebo dostupnosť produktov sa môžu vo vašom jazyku alebo regióne líšiť. Ak sa vám niečo zdá nesprávne, považujte pôvodný anglický playbook za zdroj pravdivých informácií.
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