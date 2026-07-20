# Configurazione della piattaforma

Questo documento descrive le configurazioni della piattaforma previste per l'esecuzione di questo playbook.

## Prerequisiti

PyTorch con supporto ROCm è preinstallato su AMD Ryzen™ AI Halo Developer Platform. Per tutti gli altri dispositivi, gli utenti devono installare manualmente PyTorch con supporto ROCm. Fare riferimento alla sezione relativa al proprio sistema operativo:


### Windows

| Componente     | Versione         | Note                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Preinstallato su AMD Ryzen AI Halo Developer Platform; deve essere installato manualmente su tutti gli altri dispositivi |


### Linux

| Componente     | Versione         | Note                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Preinstallato su AMD Ryzen AI Halo Developer Platform; deve essere installato manualmente su tutti gli altri dispositivi |


## Modelli richiesti

I seguenti modelli sono testati e ottimizzati per la piattaforma in uso:

| Modello | Parametri | Dimensione | Posizione di download |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Scarica da HF

I modelli verranno scaricati automaticamente nella directory della cache di Hugging Face: `~/.cache/huggingface/hub/`

Assicurarsi di disporre di almeno **20GB di spazio libero** per l'archiviazione dei modelli.

## Requisiti di rete

La configurazione iniziale richiede accesso a Internet per scaricare i modelli da Hugging Face. Dopo il download, il playbook può essere eseguito offline.

- Il primo download dei modelli può richiedere **5-10 minuti**, a seconda delle dimensioni del modello e della velocità della connessione
- I modelli vengono memorizzati nella cache locale e non è necessario scaricarli nuovamente