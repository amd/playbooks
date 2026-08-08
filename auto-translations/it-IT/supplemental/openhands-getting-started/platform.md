<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduzione automatica.** Questa pagina è stata tradotta automaticamente dall'inglese e non è stata revisionata da una persona. Potrebbe contenere errori e alcune istruzioni, comandi, download, disponibilità dei prodotti o altri contenuti potrebbero variare in base alla lingua o alla regione. In caso di incongruenza o discrepanza, prevale la versione originale in lingua inglese del playbook.
<!-- auto-translated-disclaimer:end -->

# Configurazione della piattaforma

Questo documento descrive le configurazioni della piattaforma previste per l'esecuzione di questo playbook.

## App/Framework richiesti

### Windows/Linux

- **Lemonade Server** deve essere installato seguendo la
  [guida all'installazione di Lemonade](https://lemonade-server.ai/docs/guide/install/).
- **Node.js 22.12 o versioni successive** e `npm`, utilizzati dalla CLI `agent-canvas`.
- **uv**, il gestore di pacchetti Python che Agent Canvas utilizza per gestire l'ambiente
  del server dell'agente. Installalo dalla
  [guida all'installazione di uv](https://docs.astral.sh/uv/getting-started/installation/).

## Modelli richiesti

### Windows/Linux

Il seguente modello deve essere disponibile su Lemonade Server prima di avviare il
playbook.

| Tipo di modello | ID modello | Note |
| --- | --- | --- |
| Modello di chat GGUF | `Qwen3.6-35B-A3B-GGUF` | Servito da Lemonade Server su `http://127.0.0.1:13305/api/v1`. Utilizza un modello GGUF più piccolo su dispositivi con meno di 32 GB di memoria. |

Avvia il modello con:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```
