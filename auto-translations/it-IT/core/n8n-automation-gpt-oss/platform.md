<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduzione automatica.** Questa pagina è stata tradotta automaticamente dall'inglese e non è stata revisionata da una persona. Potrebbe contenere errori e alcune istruzioni, comandi, download, disponibilità dei prodotti o altri contenuti potrebbero variare in base alla lingua o alla regione. In caso di incongruenza o discrepanza, prevale la versione originale in lingua inglese del playbook.
<!-- auto-translated-disclaimer:end -->

# Configurazione della piattaforma

Questo documento descrive le configurazioni di piattaforma previste per l'esecuzione di questo playbook.

## Prerequisiti

### Windows

| Componente | Versione | Note |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Preinstallato e disponibile nel PATH sulla AMD Ryzen™ AI Halo Developer Platform; deve essere installato manualmente su tutti gli altri dispositivi |
| **Lemonade Server** | latest | In esecuzione su `http://localhost:13305/api/v1` |

### Linux

| Componente | Versione | Note |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Preinstallato e disponibile nel PATH sulla AMD Ryzen™ AI Halo Developer Platform; deve essere installato manualmente su tutti gli altri dispositivi |
| **Lemonade Server** | latest | In esecuzione su `http://localhost:13305/api/v1` |


## Lemonade LLM

Il server Lemonade deve essere in esecuzione con il modello appropriato per il dispositivo caricato (consultare il README per il comando `lemonade run` relativo al proprio dispositivo):

| Dispositivo | Endpoint | Modello |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |