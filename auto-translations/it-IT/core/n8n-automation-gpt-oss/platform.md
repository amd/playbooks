<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configurazione della Piattaforma

Questo documento descrive le configurazioni di piattaforma previste per l'esecuzione di questo playbook.

## Prerequisiti

### Windows

| Componente | Versione | Note |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Pre-installato e disponibile nel PATH sulla AMD Ryzen™ AI Halo Developer Platform; deve essere installato manualmente su tutti gli altri dispositivi |
| **Lemonade Server** | latest | In esecuzione su `http://localhost:13305/api/v1` |

### Linux

| Componente | Versione | Note |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Pre-installato e disponibile nel PATH sulla AMD Ryzen™ AI Halo Developer Platform; deve essere installato manualmente su tutti gli altri dispositivi |
| **Lemonade Server** | latest | In esecuzione su `http://localhost:13305/api/v1` |


## Lemonade LLM

Il server Lemonade deve essere in esecuzione con il modello appropriato per il dispositivo caricato (vedere il README per il comando `lemonade run` relativo al proprio dispositivo):

| Dispositivo | Endpoint | Modello |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |