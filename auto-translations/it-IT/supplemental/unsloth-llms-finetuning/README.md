<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Questo playbook utilizza tag speciali che GitHub non è in grado di visualizzare. Visita [amd.com/playbooks](https://amd.com/playbooks) per visualizzare correttamente questo contenuto.
<!-- @github-only:end -->

## Panoramica

Questo playbook mostra come eseguire il fine-tuning di un modello linguistico in locale con Unsloth su hardware AMD.

Utilizza un breve esempio di Supervised Fine-Tuning (SFT) con adattatori LoRA su `unsloth/gemma-4-E4B-it`, utilizzando un sottoinsieme del dataset `mlabonne/FineTome-100k`. L'obiettivo è fornire un semplice flusso di lavoro end-to-end che copre configurazione, addestramento, inferenza e salvataggio del risultato ottenuto dal fine-tuning.

L'esempio è progettato per essere pratico e facile da modificare, in modo da poterlo utilizzare come punto di partenza per i propri dataset e modelli.

## Cosa imparerai

- Come configurare l'ambiente Unsloth
- Come eseguire il fine-tuning di un LLM tramite SFT con Unsloth
- Come salvare il risultato del fine-tuning nell'archiviazione locale

<!-- @device:halo,stx,krk -->
> **Nota:** le tecniche di fine-tuning presentate in questo playbook richiedono almeno 24 GB di memoria GPU e 32 GB di RAM di sistema.
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Nota:** le tecniche di fine-tuning presentate in questo playbook richiedono almeno 24 GB di memoria GPU e 32 GB di RAM di sistema.
<!-- @os:end -->

<!-- @os:linux -->
> **Nota:** le tecniche di fine-tuning presentate in questo playbook richiedono almeno 24 GB di memoria GPU **dedicata** e 32 GB di RAM di sistema.
<!-- @os:end -->
<!-- @device:end -->

## Perché Unsloth?

Unsloth semplifica l'esecuzione del fine-tuning di LLM su hardware locale riducendo l'utilizzo della memoria e velocizzando l'addestramento rispetto a una configurazione standard.

In questo playbook, utilizziamo Unsloth insieme a **SFT basato su LoRA**. Ciò significa che il modello di base rimane per lo più congelato, mentre viene addestrato un insieme molto più piccolo di pesi dell'adattatore. Questo approccio è ideale per lo sviluppo locale perché è più leggero rispetto al fine-tuning completo e più veloce da iterare.

Unsloth supporta anche altri approcci di addestramento, tra cui QLoRA e workflow di reinforcement learning. Questo playbook si concentra prima sul percorso più semplice: un piccolo esempio di fine-tuning LoRA che gli utenti possono eseguire, comprendere ed estendere.

## Configurazione della memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verifica degli aggiornamenti software
> **Nota**: se VS Code non è installato, è possibile installarlo con Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installazione dei prerequisiti software

### Creare un ambiente virtuale

<!-- @os:linux -->
<!-- @device:halo_box -->
Apri un terminale e crea un venv con AMD ROCm™ software e PyTorch già installati:
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
python3 -m venv unsloth-env --system-site-packages
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Concedi al tuo utente l'accesso ai dispositivi GPU** (esci e rientra dall'account affinché la modifica abbia effetto):

```bash
sudo usermod -aG render,video $LOGNAME
```

Apri un terminale e crea un venv:
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv unsloth-env
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **Nota:** Python 3.13 è richiesto per Windows.

<!-- @device:halo_box -->
Apri un terminale PowerShell e crea un ambiente virtuale:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Apri un terminale PowerShell e crea un ambiente virtuale:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Installazione delle dipendenze di base
<!-- @require:pytorch,driver -->

<!-- @test:id=verify-torch-env timeout=300 hidden=True setup=activate-venv -->
```python
import sys
import torch

print(f"Python executable: {sys.executable}")
print(f"PyTorch version: {torch.__version__}")
print(f"torch.cuda.is_available(): {torch.cuda.is_available()}")

if not torch.cuda.is_available():
    raise SystemExit("FAIL: ROCm-enabled PyTorch is not visible in this venv")

print("PASS: ROCm-enabled PyTorch is visible")
```
<!-- @test:end -->

### Dipendenze aggiuntive

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Nota:** durante l'importazione, Unsloth potrebbe verificare percorsi opzionali di accelerazione `bitsandbytes`. Su alcune versioni di ROCm, potresti visualizzare un messaggio come `bitsandbytes library load error: Configured ROCm binary not found`. Questo playbook utilizza il fine-tuning LoRA standard con `optim="adamw_torch"`, quindi non facciamo affidamento sull'ottimizzatore `bitsandbytes` o su QLoRA a 4 bit. Questo messaggio può essere tranquillamente ignorato.

<!-- @os:windows -->
> **Nota:** su Windows ROCm, Unsloth stamperà diversi avvisi all'avvio — vedi [Known Warnings](#known-warnings) qui sotto. Questi avvisi possono essere tutti ignorati senza problemi; l'addestramento funziona correttamente.
<!-- @os:end -->

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
```python
import unsloth
import torch
from datasets import load_dataset
from transformers import TextStreamer
from unsloth import FastModel
from unsloth.chat_templates import (
    get_chat_template,
    standardize_data_formats,
    train_on_responses_only,
)
from trl import SFTTrainer, SFTConfig

print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print("PASS: All required imports succeeded")
```
<!-- @test:end -->

## Scaricare lo script di fine-tuning Unsloth

Invece di eseguire manualmente ogni passaggio, questo playbook fornisce uno script pulito ed end-to-end qui: [test_unsloth.py](assets/test_unsloth.py).

Esegui il seguente codice per eseguire lo script:

```bash
python test_unsloth.py
```

<!-- @test:id=verify-script timeout=60 hidden=True -->
```python
import os
import sys
import ast

scripts = ["test_unsloth.py", "test_unsloth_ci.py"]
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing script: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

for script in scripts:
    with open(script, "r", encoding="utf-8") as f:
        ast.parse(f.read(), filename=script)
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=quick-train-unsloth timeout=2400 hidden=True setup=activate-venv -->
```bash
python test_unsloth_ci.py
```
<!-- @test:end -->

Il resto del playbook illustrerà concettualmente ogni passaggio principale dello script.

## Come funziona

Lo script test_unsloth.py esegue i seguenti passaggi:
* **Caricamento del modello**: carica unsloth/gemma-4-E4B-it utilizzando FastModel.
* **Preparazione dei dati**: standardizza il dataset (ad es. FineTome-100k) e applica il template di chat Gemma-4.
* **Applicazione di LoRA**: aggiunge adattatori ai moduli linguistici, di attenzione e MLP per un addestramento efficiente.
* **Addestramento**: utilizza SFTTrainer con mascheramento della perdita solo sulla risposta.
* **Inferenza**: esegue un rapido test di generazione per verificare le prestazioni.
* **Salvataggio**: esporta gli adattatori LoRA in locale.

## Configurazione chiave

Puoi modificare le seguenti costanti per personalizzare la tua esecuzione:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Esempio del messaggio di benvenuto di Unsloth e dell'output durante il caricamento dei pesi del modello:

![alt text](assets/welcome.png)

## Preparare il dataset

Utilizziamo un sottoinsieme di:
```text
mlabonne/FineTome-100k
```
Il dataset è: 
* Convertito in formato chat
* Elaborato utilizzando il template di chat Gemma-4
* Ripulito per rimuovere i token BOS duplicati

## Addestrare il modello

Lo script esegue una breve demo di addestramento, con i seguenti parametri:
- ~50 step
- Batch size ridotto
- Accumulo del gradiente

Durante l'addestramento, vedrai log come i seguenti:

![alt text](assets/training.png)


## Salvataggio e distribuzione

### Salvataggio locale (LoRA)

Lo script salva automaticamente gli adattatori LoRA nella OUTPUT_DIR.
```python
model.save_pretrained("gemma_4_lora")  
tokenizer.save_pretrained("gemma_4_lora")
```

<!-- @test:id=verify-unsloth-lora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_lora_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = (
    glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) +
    glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
)
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: Unsloth LoRA output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end -->

### Salvare il modello unito (per vLLM) 

<!-- @os:windows -->
> **Nota:** vLLM non supporta Windows. Per distribuire il modello sottoposto a fine-tuning su Windows, utilizza llama.cpp (vedi [Export GGUF](#export-gguf-for-llamacpp) più avanti) oppure trasferisci il modello unito su una macchina Linux che esegue vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Per la distribuzione con vLLM, unisci gli adattatori in un modello completo:
```python
model.save_pretrained_merged("gemma-4-finetune", tokenizer)
```
<!-- @os:end -->

<!-- @test:id=verify-unsloth-merged-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_merged_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing merged model directory: {out_dir}")
    sys.exit(1)

required = [
    "config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required merged files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Merged model output looks correct")
```
<!-- @test:end -->

### Esportare GGUF (per llama.cpp)

Converti direttamente in GGUF per l'inferenza locale:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Avvisi noti

Questi avvisi vengono stampati da Unsloth all'avvio su Windows ROCm e possono essere tutti tranquillamente ignorati:

| Avviso | Motivo | Si può ignorare? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes non ha una build per Windows ROCm | Sì — questo playbook usa `adamw_torch`, non bnb |
| `No ROCm platform found for torch.distributed` | ROCm su Windows non supporta il training distribuito | Sì — il training su singola GPU non è interessato |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth segnala le build non Linux | Sì — Windows ROCm funziona per SFT su singola GPU |
| `triton is not available` | Triton non ha una build per Windows | Sì — Unsloth ricorre ai kernel PyTorch |

Il training procederà correttamente nonostante questi avvisi.
<!-- @os:end -->

## Prossimi passi
- Prova [Unsloth Studio](https://unsloth.ai/docs/new/studio), una GUI intuitiva per Unsloth
- Esegui il training sui tuoi dataset specifici
- Prova il finetuning con iperparametri diversi
- Esegui il deploy con vLLM o llama.cpp
- Prova QLoRA per una configurazione con minor utilizzo di memoria

## Risorse

Di seguito alcune risorse aggiuntive per saperne di più su Unsloth e sul finetuning:

* [Documentazione Unsloth](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Guida al fine-tuning di Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)