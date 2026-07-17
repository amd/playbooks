<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfigurace platformy

Tento dokument popisuje očekávané konfigurace platformy pro spuštění tohoto playbooku.

## Požadované aplikace/frameworky

### Windows/Linux

GAIA by měla být předinstalována podle pokynů uvedených v [Průvodci instalací GAIA](../../dependencies/gaia.md).

Lemonade Server by měl být předinstalován podle pokynů uvedených v [Průvodci instalací Lemonade](../../dependencies/lemonade.md).

## Požadované modely

### Windows/Linux

Agent Hardware Advisor používá **Qwen3-Coder-30B** pro uvažování agenta. Tento model se stahuje automaticky během `gaia init`. Není vyžadováno žádné ruční stahování modelů.