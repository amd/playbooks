# Configurazione della Piattaforma

Questo documento descrive le configurazioni di piattaforma previste per l'esecuzione di questo playbook.

## Prerequisiti

PyTorch con supporto ROCm è preinstallato sulla AMD Ryzen™ AI Halo Developer Platform. Per tutti gli altri dispositivi, gli utenti devono installare manualmente PyTorch con supporto ROCm. Fare riferimento alla sezione pertinente per il proprio sistema operativo:

### Windows

| Componente    | Versione        | Note                              |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Preinstallato sulla AMD Ryzen AI Halo Developer Platform; deve essere installato manualmente su tutti gli altri dispositivi |


### Linux

| Componente    | Versione        | Note                              |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Preinstallato sulla AMD Ryzen AI Halo Developer Platform; deve essere installato manualmente su tutti gli altri dispositivi |


## Modelli Richiesti

I seguenti modelli sono testati e ottimizzati per la piattaforma:

| Modello | Parametri | Dimensione | Posizione di Download |
|---------|-----------|------------|-----------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Scarica da HF

I modelli verranno scaricati automaticamente nella directory cache di Hugging Face: `~/.cache/huggingface/hub/`

Assicurarsi di avere almeno **20GB di spazio libero** per l'archiviazione dei modelli.

## Requisiti di Rete

La configurazione iniziale richiede l'accesso a Internet per scaricare i modelli da Hugging Face. Dopo il download, il playbook può essere eseguito offline.

- I download iniziali dei modelli possono richiedere **5-10 minuti** a seconda delle dimensioni del modello e della velocità di connessione
- I modelli vengono memorizzati nella cache locale e non è necessario scaricarli nuovamente