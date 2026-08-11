<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

# Konfigurace platformy

Tento dokument popisuje očekávané konfigurace platformy pro spuštění tohoto playbooku.

## Požadavky

### Windows

| Komponenta | Verze | Poznámky |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Předinstalováno a dostupné v PATH na platformě AMD Ryzen™ AI Halo Developer Platform; na všech ostatních zařízeních musí být nainstalováno ručně |
| **Lemonade Server** | nejnovější | Běží na `http://localhost:13305/api/v1` |

### Linux

| Komponenta | Verze | Poznámky |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Předinstalováno a dostupné v PATH na platformě AMD Ryzen™ AI Halo Developer Platform; na všech ostatních zařízeních musí být nainstalováno ručně |
| **Lemonade Server** | nejnovější | Běží na `http://localhost:13305/api/v1` |


## Lemonade LLM

Server Lemonade by měl běžet s načteným modelem odpovídajícím danému zařízení (viz README pro příkaz `lemonade run` pro vaše zařízení):

| Zařízení | Koncový bod | Model |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |