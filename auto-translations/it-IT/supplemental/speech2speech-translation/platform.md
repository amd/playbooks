# Configurazione della piattaforma

Questo documento descrive le configurazioni della piattaforma previste per l'esecuzione di questo playbook.

## Prerequisiti

PyTorch con supporto ROCm è preinstallato su AMD Ryzen™ AI Halo Developer Platform. Per tutti gli altri dispositivi, gli utenti devono installare manualmente PyTorch con supporto ROCm. Fare riferimento alla sezione pertinente per il proprio sistema operativo:

### Windows

| Componente     | Versione         | Note                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 o versioni successive    | Preinstallato su AMD Ryzen AI Halo Developer Platform; deve essere installato manualmente su tutti gli altri dispositivi |

### Linux

| Componente     | Versione         | Note                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 o versioni successive    | Preinstallato su AMD Ryzen AI Halo Developer Platform; deve essere installato manualmente su tutti gli altri dispositivi |

## Modelli richiesti

I seguenti modelli sono testati e ottimizzati per la piattaforma in uso:

| Modello | Parametri | Dimensione | Posizione di download |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2.3B | ~10GB | Preinstallato su AMD Ryzen AI Halo Developer Platform; deve essere installato manualmente su tutti gli altri dispositivi |

I modelli verranno scaricati automaticamente nella directory della cache di Hugging Face:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Assicurarsi di disporre di almeno **20GB di spazio libero** per l'archiviazione dei modelli.

## Requisiti di rete

La configurazione iniziale richiede l'accesso a Internet per scaricare i modelli da Hugging Face. Dopo il download, il playbook può essere eseguito offline.

- Il primo download dei modelli può richiedere **5-10 minuti**, a seconda delle dimensioni del modello e della velocità di connessione
- I modelli vengono memorizzati nella cache locale e non è necessario scaricarli nuovamente