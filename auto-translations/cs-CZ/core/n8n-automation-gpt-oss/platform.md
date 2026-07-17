<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfigurace platformy

Tento dokument popisuje očekávané konfigurace platformy pro spuštění tohoto playbooku.

## Předpoklady

### Windows

| Komponenta | Verze | Poznámky |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Předinstalováno a dostupné v PATH na platformě AMD Ryzen™ AI Halo Developer Platform; na všech ostatních zařízeních je nutná ruční instalace |
| **Lemonade Server** | nejnovější | Spuštěno na `http://localhost:13305/api/v1` |

### Linux

| Komponenta | Verze | Poznámky |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Předinstalováno a dostupné v PATH na platformě AMD Ryzen™ AI Halo Developer Platform; na všech ostatních zařízeních je nutná ruční instalace |
| **Lemonade Server** | nejnovější | Spuštěno na `http://localhost:13305/api/v1` |


## Lemonade LLM

Server Lemonade by měl být spuštěn s načteným modelem odpovídajícím danému zařízení (příkaz `lemonade run` pro vaše zařízení naleznete v souboru README):

| Zařízení | Endpoint | Model |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |