<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configurazione della Piattaforma

Questo documento descrive le configurazioni di piattaforma previste per l'esecuzione di questo playbook.

## Prerequisiti

PyTorch con supporto ROCm è preinstallato sulla AMD Ryzen™ AI Halo Developer Platform. Per tutti gli altri dispositivi, gli utenti devono installare manualmente PyTorch con supporto ROCm. Fare riferimento alla sezione pertinente per il proprio sistema operativo:

### Windows

| Componente    | Versione        | Note                              |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 o successiva | Preinstallato sulla AMD Ryzen AI Halo Developer Platform; deve essere installato manualmente su tutti gli altri dispositivi |

### Linux

| Componente    | Versione        | Note                              |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 o successiva | Preinstallato sulla AMD Ryzen AI Halo Developer Platform; deve essere installato manualmente su tutti gli altri dispositivi |

## Modelli Richiesti

I seguenti modelli sono testati e ottimizzati per la piattaforma:

| Modello | Parametri | Dimensione | Posizione di Download |
|---------|-----------|------------|-----------------------|
| **openai/gpt-oss-20b** | 20B | ~40GB | Preinstallato sulla AMD Ryzen AI Halo Developer Platform; deve essere installato manualmente su tutti gli altri dispositivi |

I modelli verranno scaricati automaticamente nella directory cache di Hugging Face:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Assicurarsi di disporre di almeno **50GB di spazio libero** per l'archiviazione dei modelli.

## Requisiti di Rete

La configurazione iniziale richiede l'accesso a Internet per scaricare i modelli da Hugging Face. Dopo il download, il playbook può essere eseguito offline.

- I download iniziali dei modelli possono richiedere **5-10 minuti** a seconda delle dimensioni del modello e della velocità di connessione
- I modelli vengono memorizzati nella cache locale e non è necessario scaricarli nuovamente