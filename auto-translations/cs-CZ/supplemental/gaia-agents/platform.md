<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

# Konfigurace platformy

Tento dokument popisuje očekávané konfigurace platformy pro spuštění této příručky (playbook).

## Požadované aplikace/frameworky

### Windows/Linux

GAIA by měla být předem nainstalována podle pokynů uvedených v [průvodci instalací GAIA](../../dependencies/gaia.md).

Lemonade Server by měl být předem nainstalován podle pokynů uvedených v [průvodci instalací Lemonade](../../dependencies/lemonade.md).

## Požadované modely

### Windows/Linux

Agent Hardware Advisor používá pro uvažování agenta model **Qwen3-Coder-30B**. Tento model se automaticky stáhne během `gaia init`. Ruční stahování modelů není nutné.