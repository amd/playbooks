<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traduzione automatica.** Questa pagina è stata tradotta automaticamente dall'inglese e non è stata revisionata da una persona. Potrebbe contenere errori e alcune istruzioni, comandi, download, disponibilità dei prodotti o altri contenuti potrebbero variare in base alla lingua o alla regione. In caso di incongruenza o discrepanza, prevale la versione originale in lingua inglese del playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Panoramica

Questo playbook mostra come eseguire il fine-tuning locale di un modello linguistico con Unsloth su hardware AMD.

Utilizza un breve esempio di Supervised Fine-Tuning (SFT) con adattatori LoRA su `unsloth/gemma-4-E4B-it`, utilizzando un sottoinsieme del dataset `mlabonne/FineTome-100k`. L'obiettivo è fornire un semplice flusso di lavoro end-to-end che copre configurazione, addestramento, inferenza e salvataggio del risultato del fine-tuning.

L'esempio è pensato per essere pratico e facile da modificare, così da poterlo utilizzare come punto di partenza per i propri dataset e modelli.

## Cosa Imparerai

- Come configurare l'ambiente Unsloth
- Come eseguire il fine-tuning di un LLM utilizzando SFT con Unsloth
- Come salvare il risultato del fine-tuning in archiviazione locale

<!-- @device:halo,stx,krk -->
> **Nota:** Le tecniche di fine-tuning descritte in questo playbook richiedono almeno **64 GB di RAM di sistema**, di cui almeno **24 GB disponibili per la GPU** (i 24 GB fanno parte dei 64 GB, non sono aggiuntivi).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Nota:** Le tecniche di fine-tuning descritte in questo playbook richiedono almeno **24 GB di memoria GPU totale** e **32 GB di RAM di sistema**.
> - Su Windows, la memoria GPU totale combina la VRAM dedicata della scheda grafica con la memoria GPU condivisa (presa in prestito dalla RAM di sistema).
> - Pertanto, le schede con meno di 24 GB di VRAM dedicata possono comunque eseguire questo playbook utilizzando la memoria GPU condivisa per compensare la differenza.
<!-- @os:end -->

<!-- @os:linux -->
> **Nota:** Le tecniche di fine-tuning descritte in questo playbook richiedono una scheda grafica con almeno **24 GB di memoria GPU dedicata** e **32 GB di RAM di sistema**.
> - Su Linux, l'addestramento viene eseguito interamente nella VRAM dedicata della scheda grafica.
> - Non è previsto il fallback sulla memoria GPU condivisa (RAM di sistema) quando la VRAM si esaurisce.
> - Le schede con meno di 24 GB di VRAM dedicata esauriranno la memoria durante l'addestramento su Linux, anche se il sistema dispone di ampia RAM.
<!-- @os:end -->
<!-- @device:end -->

## Perché Unsloth?

Unsloth rende più semplice eseguire il fine-tuning di LLM su hardware locale, riducendo l'utilizzo della memoria e velocizzando l'addestramento rispetto a una configurazione standard.

In questo playbook, utilizziamo Unsloth insieme a **SFT basato su LoRA**. Ciò significa che il modello di base rimane per lo più congelato, mentre viene addestrato un insieme molto più piccolo di pesi degli adattatori. Questo approccio è ideale per lo sviluppo locale perché è più leggero rispetto al fine-tuning completo e più veloce da iterare.

Unsloth supporta anche altri approcci di addestramento, tra cui QLoRA e flussi di lavoro di reinforcement learning. Questo playbook si concentra prima sul percorso più semplice: un piccolo esempio di fine-tuning LoRA che gli utenti possono eseguire, comprendere ed estendere.

## Impostazione della Configurazione della Memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verifica degli Aggiornamenti Software
> **Nota**: Se VS Code non è installato, puoi installarlo con Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installazione dei Prerequisiti Software

### Creare un Ambiente Virtuale

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
**Concedi al tuo utente l'accesso ai dispositivi GPU** (esegui il logout e il login per rendere effettiva la modifica):

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

### Installazione delle Dipendenze di Base
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

### Dipendenze Aggiuntive

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Nota:** Durante l'importazione, Unsloth potrebbe verificare percorsi di accelerazione opzionali di `bitsandbytes`. Su alcune versioni di ROCm, potresti visualizzare un messaggio come `bitsandbytes library load error: Configured ROCm binary not found`. Questo playbook utilizza il fine-tuning LoRA standard con `optim="adamw_torch"`, quindi non facciamo affidamento sull'ottimizzatore `bitsandbytes` o su QLoRA a 4 bit. Questo messaggio può essere tranquillamente ignorato.

<!-- @os:windows -->
> **Nota:** Su Windows ROCm, Unsloth stamperà diversi avvisi all'avvio — vedi [Avvisi Noti](#known-warnings) di seguito. Sono tutti sicuri da ignorare; l'addestramento funziona correttamente.
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

## Scaricare lo Script di Fine-Tuning Unsloth

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

Il resto del playbook illustrerà concettualmente ogni fase principale dello script.

## Come Funziona

Lo script test_unsloth.py esegue i seguenti passaggi:
* **Carica Modello**: Carica unsloth/gemma-4-E4B-it utilizzando FastModel.
* **Prepara Dati**: Standardizza il dataset (ad es. FineTome-100k) e applica il template di chat Gemma-4.
* **Applica LoRA**: Aggiunge adattatori ai moduli linguistici, di attenzione e MLP per un addestramento efficiente.
* **Addestra**: Utilizza SFTTrainer con mascheramento della perdita solo sulla risposta.
* **Inferenza**: Esegue un rapido test di generazione per verificare le prestazioni.
* **Salva**: Esporta gli adattatori LoRA localmente.

## Configurazione Chiave

Puoi modificare le seguenti costanti per personalizzare la tua esecuzione:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Esempio del messaggio di benvenuto di Unsloth e dell'output durante il caricamento dei pesi del modello:

![alt text](assets/welcome.png)

## Preparare il Dataset

Utilizziamo un sottoinsieme di:
```text
mlabonne/FineTome-100k
```
Il dataset viene: 
* Convertito in formato chat
* Elaborato utilizzando il template di chat Gemma-4
* Pulito per rimuovere i token BOS duplicati

## Addestrare il Modello

Lo script esegue una breve demo di addestramento, con i seguenti parametri:
- ~50 passi
- Batch size ridotto
- Accumulo del gradiente

Durante l'addestramento, vedrai log come questi:

![alt text](assets/training.png)


## Salvataggio e Distribuzione
### Salvataggio locale (LoRA)

Lo script salva automaticamente gli adattatori LoRA in OUTPUT_DIR.
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

### Salvataggio del modello unito (per vLLM) 

<!-- @os:windows -->
> **Nota:** vLLM non supporta Windows. Per distribuire il modello sottoposto a fine-tuning su Windows, utilizza llama.cpp (vedi [Esportazione GGUF](#export-gguf-for-llamacpp) più sotto) oppure trasferisci il modello unito su una macchina Linux che esegue vLLM.
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

### Esportazione GGUF (per llama.cpp)

Converti direttamente in GGUF per l'inferenza locale:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Avvisi noti

Questi avvisi vengono stampati da Unsloth all'avvio su Windows ROCm e possono essere tutti ignorati in sicurezza:

| Avviso | Motivo | Sicuro da ignorare? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes non ha una build per Windows ROCm | Sì — questo playbook utilizza `adamw_torch`, non bnb |
| `No ROCm platform found for torch.distributed` | ROCm su Windows non supporta l'addestramento distribuito | Sì — l'addestramento con una singola GPU non ne risente |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth segnala le build non Linux | Sì — Windows ROCm funziona per SFT con singola GPU |
| `triton is not available` | Triton non ha una build per Windows | Sì — Unsloth ricorre ai kernel PyTorch |

L'addestramento procederà correttamente nonostante questi avvisi.
<!-- @os:end -->

## Passaggi successivi
- Prova [Unsloth Studio](https://unsloth.ai/docs/new/studio), un'interfaccia grafica intuitiva per Unsloth
- Esegui l'addestramento sui tuoi dataset specifici
- Prova il fine-tuning con iperparametri diversi
- Distribuisci con vLLM o llama.cpp
- Prova QLoRA per una configurazione con minor utilizzo di memoria

## Risorse

Di seguito sono riportate alcune risorse aggiuntive per saperne di più su Unsloth e sul fine-tuning:

* [Documentazione Unsloth](https://docs.unsloth.ai)

* [Unsloth su GitHub](https://github.com/unslothai/unsloth)

* [Guida al fine-tuning di Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)