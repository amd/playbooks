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

## Predpoklady

### Windows

| Komponent | Verzia | Poznámky |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Predinštalované a dostupné v PATH na AMD Ryzen™ AI Halo Developer Platform; na všetkých ostatných zariadeniach musí byť nainštalované manuálne |
| **Lemonade Server** | najnovšia | Beží na `http://localhost:13305/api/v1` |

### Linux

| Komponent | Verzia | Poznámky |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Predinštalované a dostupné v PATH na AMD Ryzen™ AI Halo Developer Platform; na všetkých ostatných zariadeniach musí byť nainštalované manuálne |
| **Lemonade Server** | najnovšia | Beží na `http://localhost:13305/api/v1` |


## Lemonade LLM

Server Lemonade by mal bežať s modelom vhodným pre dané zariadenie (pozrite si súbor README pre príkaz `lemonade run` pre vaše zariadenie):

| Zariadenie | Koncový bod | Model |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |