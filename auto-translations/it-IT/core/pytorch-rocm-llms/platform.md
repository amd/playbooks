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

## Prerequisiti

PyTorch con supporto ROCm è preinstallato su AMD Ryzen™ AI Halo Developer Platform. Per tutti gli altri dispositivi, gli utenti devono installare manualmente PyTorch con supporto ROCm. Fare riferimento alla sezione pertinente per il proprio sistema operativo:

### Windows

| Componente     | Versione         | Note                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 o superiore    | Preinstallato su AMD Ryzen AI Halo Developer Platform; deve essere installato manualmente su tutti gli altri dispositivi |

### Linux

| Componente     | Versione         | Note                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 o superiore    | Preinstallato su AMD Ryzen AI Halo Developer Platform; deve essere installato manualmente su tutti gli altri dispositivi |

## Modelli richiesti

I seguenti modelli sono testati e ottimizzati per la piattaforma in uso:

| Modello | Parametri | Dimensione | Posizione di download |
|-------|------------|------|-------------------|
| **openai/gpt-oss-20b** | 20B | ~40GB | Preinstallato su AMD Ryzen AI Halo Developer Platform; deve essere installato manualmente su tutti gli altri dispositivi |

I modelli verranno scaricati automaticamente nella directory della cache di Hugging Face:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Assicurarsi di avere almeno **50GB di spazio libero** per l'archiviazione dei modelli.

## Requisiti di rete

La configurazione iniziale richiede l'accesso a Internet per scaricare i modelli da Hugging Face. Dopo il download, il playbook può essere eseguito offline.

- Il primo download dei modelli può richiedere **5-10 minuti**, a seconda delle dimensioni del modello e della velocità della connessione
- I modelli vengono memorizzati nella cache locale e non è necessario scaricarli nuovamente