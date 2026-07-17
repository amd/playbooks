<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfigurácia platformy

Tento dokument popisuje očakávané konfigurácie platformy pre spustenie tohto playbooku.

## Predpoklady

### Windows

| Komponent | Verzia | Poznámky |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Predinštalovaný a dostupný v PATH na AMD Ryzen™ AI Halo Developer Platform; na všetkých ostatných zariadeniach je potrebná manuálna inštalácia |
| **Lemonade Server** | najnovšia | Spustený na `http://localhost:13305/api/v1` |

### Linux

| Komponent | Verzia | Poznámky |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Predinštalovaný a dostupný v PATH na AMD Ryzen™ AI Halo Developer Platform; na všetkých ostatných zariadeniach je potrebná manuálna inštalácia |
| **Lemonade Server** | najnovšia | Spustený na `http://localhost:13305/api/v1` |


## Lemonade LLM

Server Lemonade by mal byť spustený s načítaným modelom vhodným pre dané zariadenie (pozri README pre príkaz `lemonade run` pre vaše zariadenie):

| Zariadenie | Endpoint | Model |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |