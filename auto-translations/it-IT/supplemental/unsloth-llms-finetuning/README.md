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

Questa guida pratica mostra come eseguire il fine-tuning locale di un modello linguistico con Unsloth su hardware AMD.

Utilizza un breve esempio di Supervised Fine-Tuning (SFT) con adattatori LoRA su `unsloth/gemma-4-E4B-it`, utilizzando un sottoinsieme del dataset `mlabonne/FineTome-100k`. L'obiettivo è fornire un semplice flusso di lavoro end-to-end che copre configurazione, addestramento, inferenza e salvataggio del risultato del fine-tuning.

L'esempio è pensato per essere pratico e facile da modificare, in modo da poterlo utilizzare come punto di partenza per i propri dataset e modelli.

## Cosa imparerai

- Come configurare l'ambiente Unsloth
- Come eseguire il fine-tuning di un LLM utilizzando SFT con Unsloth
- Come salvare il risultato del fine-tuning in archiviazione locale

<!-- @device:halo,stx,krk -->
> **Nota:** Le tecniche di fine-tuning descritte in questa guida richiedono almeno **64 GB di RAM di sistema**, di cui almeno **24 GB disponibili per la GPU** (i 24 GB fanno parte dei 64 GB, non si aggiungono ad essi).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Nota:** Le tecniche di fine-tuning descritte in questa guida richiedono almeno **24 GB di memoria GPU totale** e **32 GB di RAM di sistema**.
> - Su Windows, la memoria GPU totale combina la VRAM dedicata della scheda grafica con la memoria GPU condivisa (presa in prestito dalla RAM di sistema).
> - Pertanto, le schede con meno di 24 GB di VRAM dedicata possono comunque eseguire questa guida utilizzando la memoria GPU condivisa per colmare la differenza.
<!-- @os:end -->

<!-- @os:linux -->
> **Nota:** Le tecniche di fine-tuning descritte in questa guida richiedono una scheda grafica con almeno **24 GB di memoria GPU dedicata** e **32 GB di RAM di sistema**.
> - Su Linux, l'addestramento viene eseguito interamente nella VRAM dedicata della scheda grafica.
> - Non viene effettuato il fallback sulla memoria GPU condivisa (RAM di sistema) quando la VRAM si esaurisce.
> - Le schede con meno di 24 GB di VRAM dedicata esauriranno la memoria durante l'addestramento su Linux, anche se il sistema dispone di molta RAM.
<!-- @os:end -->
<!-- @device:end -->

## Perché Unsloth?

Unsloth semplifica l'esecuzione del fine-tuning di LLM su hardware locale riducendo l'utilizzo della memoria e velocizzando l'addestramento rispetto a una configurazione standard.

In questa guida, utilizziamo Unsloth insieme a **SFT basato su LoRA**. Ciò significa che il modello di base rimane per lo più congelato, mentre viene addestrato un insieme molto più piccolo di pesi degli adattatori. Questo approccio è adatto allo sviluppo locale perché è più leggero rispetto al fine-tuning completo e più veloce da iterare.

Unsloth supporta anche altri approcci di addestramento, inclusi QLoRA e flussi di lavoro di reinforcement learning. Questa guida si concentra prima sul percorso più semplice: un piccolo esempio di fine-tuning LoRA che gli utenti possono eseguire, comprendere ed estendere.

<!-- @device:halo_box,halo,stx,krk -->
## Impostazione della configurazione della memoria

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Verifica degli aggiornamenti software
> **Nota**: Se VS Code non è installato, è possibile installarlo con Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installazione dei prerequisiti software

<!-- @prereq:hf-models-gemma-4-e4b-it,hf-datasets-finetome-100k -->

### Creazione di un ambiente virtuale

<!-- @os:linux -->
<!-- @device:halo_box -->
Apri un terminale e crea un venv con AMD ROCm™ software e PyTorch già installati:
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
python3 -m venv unsloth-env --system-site-packages
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Concedi al tuo utente l'accesso ai dispositivi GPU** (esci e rientra nella sessione affinché la modifica abbia effetto):

```bash
sudo usermod -aG render,video $LOGNAME
```

Apri un terminale e crea un venv:
<!-- @test:id=create-venv timeout=300 -->
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
<!-- @require:driver -->

> **Importante:** Unsloth non supporta ancora la build di PyTorch 2.13 inclusa in ROCm 10. Per questa guida, installa **ROCm 7.14 con PyTorch 2.12** utilizzando i comandi riportati di seguito. Non utilizzare i pacchetti ROCm 10 / PyTorch 2.13.

**Installa PyTorch con supporto AMD ROCm™ software** nell'ambiente virtuale creato:

<!-- @device:halo,halo_box -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1151]==2.12.0+rocm7.14.0" "torchvision[device-gfx1151]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1150]==2.12.0+rocm7.14.0" "torchvision[device-gfx1150]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:krk -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1152]==2.12.0+rocm7.14.0" "torchvision[device-gfx1152]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx7900xt -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1100]==2.12.0+rocm7.14.0" "torchvision[device-gfx1100]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx9070xt,r9700 -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1201]==2.12.0+rocm7.14.0" "torchvision[device-gfx1201]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

Per altri dispositivi, fai riferimento alla [documentazione di ROCm 7.14](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html) per le istruzioni complete.

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
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git" triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Nota:** Durante l'importazione, Unsloth potrebbe sondare percorsi di accelerazione opzionali di `bitsandbytes`. Su alcune versioni di ROCm, potresti visualizzare un messaggio simile a `bitsandbytes library load error: Configured ROCm binary not found`. Questa guida utilizza il fine-tuning LoRA standard con `optim="adamw_torch"`, quindi non facciamo affidamento sull'ottimizzatore `bitsandbytes` o su QLoRA a 4 bit. Questo messaggio può essere tranquillamente ignorato.

<!-- @os:windows -->
> **Nota:** Su Windows ROCm, Unsloth stamperà diversi avvisi all'avvio — vedi [Avvisi noti](#known-warnings) di seguito. Questi avvisi possono essere tranquillamente ignorati; l'addestramento funziona correttamente.
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

## Scaricare lo script di fine-tuning di Unsloth

Invece di eseguire manualmente ogni passaggio, questa guida fornisce uno script pulito ed end-to-end qui: [test_unsloth.py](assets/test_unsloth.py).

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

Il resto della guida illustrerà concettualmente ogni passaggio principale dello script.

## Come funziona

Lo script test_unsloth.py esegue i seguenti passaggi:
* **Caricamento del modello**: Carica unsloth/gemma-4-E4B-it utilizzando FastModel.
* **Preparazione dei dati**: Standardizza il dataset (ad esempio, FineTome-100k) e applica il template di chat di Gemma-4.
* **Applicazione di LoRA**: Aggiunge adattatori ai moduli di linguaggio, attenzione e MLP per un addestramento efficiente.
* **Addestramento**: Utilizza SFTTrainer con mascheramento della perdita solo sulla risposta.
* **Inferenza**: Esegue un rapido test di generazione per verificare le prestazioni.
* **Salvataggio**: Esporta gli adattatori LoRA localmente.
## Configurazione chiave

È possibile modificare le seguenti costanti per personalizzare l'esecuzione:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Esempio del messaggio di benvenuto di Unsloth e dell'output durante il caricamento dei pesi del modello:

![testo alternativo](assets/welcome.png)

## Preparazione del dataset

Utilizziamo un sottoinsieme di:
```text
mlabonne/FineTome-100k
```
Il dataset viene: 
* Convertito nel formato chat
* Elaborato utilizzando il template di chat Gemma-4
* Ripulito per rimuovere i token BOS duplicati

## Addestramento del modello

Lo script esegue una breve demo di addestramento, con i seguenti parametri:
- ~50 passaggi (step)
- Dimensione del batch ridotta
- Accumulo del gradiente

Durante l'addestramento, verranno visualizzati log come questi:

![testo alternativo](assets/training.png)


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

### Salvare il modello unito (merged) (per vLLM) 

<!-- @os:windows -->
> **Nota:** vLLM non supporta Windows. Per distribuire il modello sottoposto a fine-tuning su Windows, utilizzare llama.cpp (vedere [Esportazione GGUF](#export-gguf-for-llamacpp) di seguito) oppure trasferire il modello unito a una macchina Linux che esegue vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Per la distribuzione con vLLM, unire gli adattatori in un modello completo:
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

Convertire direttamente in GGUF per l'inferenza locale:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Avvisi noti

I seguenti avvisi vengono stampati da Unsloth all'avvio su Windows ROCm e possono tutti essere tranquillamente ignorati:

| Avviso | Motivo | È possibile ignorarlo? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes non dispone di una build per Windows ROCm | Sì — questo playbook utilizza `adamw_torch`, non bnb |
| `No ROCm platform found for torch.distributed` | ROCm su Windows non supporta l'addestramento distribuito | Sì — l'addestramento su singola GPU non è interessato |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth segnala le build non Linux | Sì — Windows ROCm funziona per il SFT su singola GPU |
| `triton is not available` | Triton non dispone di una build per Windows | Sì — Unsloth utilizza i kernel di PyTorch come fallback |

L'addestramento procederà correttamente nonostante questi avvisi.
<!-- @os:end -->

## Prossimi passi
- Provare [Unsloth Studio](https://unsloth.ai/docs/new/studio), un'interfaccia grafica intuitiva per Unsloth
- Effettuare l'addestramento sui propri dataset specifici
- Provare il fine-tuning con iperparametri diversi
- Distribuire con vLLM o llama.cpp
- Provare QLoRA per una configurazione con minore utilizzo di memoria

## Risorse

Di seguito sono riportate alcune risorse aggiuntive per saperne di più su Unsloth e sul fine-tuning:

* [Documentazione Unsloth](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Guida al fine-tuning di Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)