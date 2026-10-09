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

Questo tutorial fornisce esempi passo-passo per il fine-tuning di un modello linguistico di grandi dimensioni (LLM) con PyTorch e ROCm. Copre diverse tecniche, dal fine-tuning standard alle strategie Parameter-Efficient Fine-Tuning (PEFT) efficienti in termini di memoria, in modo da poter adattare facilmente i modelli alle tue esigenze.

**Modello utilizzato**: google/gemma-3-4b-it (script QLoRA: openai/gpt-oss-20b)  *(vedi [Abilitare l'autenticazione HF](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) se protetto)*  
**Hardware**: GPU AMD Radeon™ con supporto ROCm  
**Framework**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Nota:** 
> - Il fine-tuning completo richiede almeno **64 GB di RAM di sistema**, di cui almeno **32 GB disponibili per la GPU** (i 32 GB fanno parte dei 64 GB, non si aggiungono ad essi).
> - Puoi anche provare altre architetture di modelli, incluso **GPT-OSS-20B**, sostituendo il modello negli script di addestramento forniti.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **Nota:** Il fine-tuning LoRA e QLoRA richiede almeno **32 GB di RAM di sistema**, di cui almeno **16 GB disponibili per la GPU** (i 16 GB fanno parte dei 32 GB, non si aggiungono ad essi).
<!-- @os:end -->

<!-- @os:windows -->
> **Nota:** Il fine-tuning LoRA richiede almeno **32 GB di RAM di sistema**, di cui almeno **16 GB disponibili per la GPU** (i 16 GB fanno parte dei 32 GB, non si aggiungono ad essi).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Nota:** Il fine-tuning LoRA e QLoRA richiede una scheda grafica con almeno **16 GB di memoria GPU dedicata** e **32 GB di RAM di sistema**.
> - Su Linux, l'addestramento viene eseguito interamente nella VRAM dedicata della scheda grafica.
> - Non ricade sulla memoria GPU condivisa (RAM di sistema) quando la VRAM si esaurisce.
> - Le schede con meno di 16 GB di VRAM dedicata esauriranno la memoria durante l'addestramento su Linux, anche se il sistema dispone di abbondante RAM.
<!-- @os:end -->

<!-- @os:windows -->
> **Nota:** Il fine-tuning LoRA richiede almeno **16 GB di memoria GPU totale** e **32 GB di RAM di sistema**.
> - Su Windows, la memoria GPU totale combina la VRAM dedicata della scheda grafica con la memoria GPU condivisa (presa in prestito dalla RAM di sistema).
> - Pertanto, le schede con meno di 16 GB di VRAM dedicata possono comunque eseguire questo playbook utilizzando la memoria GPU condivisa per colmare la differenza.
<!-- @os:end -->
<!-- @device:end -->

## Cosa imparerai

- Come eseguire il fine-tuning di un LLM utilizzando LoRA, QLoRA e il fine-tuning completo con PyTorch e ROCm
- Come salvare e distribuire il tuo modello sottoposto a fine-tuning
- Come monitorare l'addestramento e risolvere i problemi comuni

<!-- @device:halo_box,halo,stx,krk -->
## Impostazione della configurazione della memoria

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Verifica degli aggiornamenti software
> **Nota**: Se VS Code non è installato, puoi installarlo con Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installazione dei prerequisiti software

<!-- @prereq:hf-models-gemma-3-4b-it,hf-datasets-databricks-dolly-15k -->
<!-- @os:linux -->
<!-- @prereq:hf-datasets-english-quotes -->
<!-- @os:end -->

#### Creazione di un ambiente virtuale

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update 
sudo apt install -y python3-venv 
python3 -m venv finetune-venv --system-site-packages 
source finetune-venv/bin/activate 
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source finetune-venv/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Concedi al tuo utente l'accesso ai dispositivi GPU** (disconnettiti e riconnettiti per rendere effettiva la modifica):

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv finetune-venv
source finetune-venv/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source finetune-venv/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=180 -->
```powershell
python -m venv finetune-venv --system-site-packages
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=180 -->
```powershell
python -m venv finetune-venv
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

#### Installazione delle dipendenze di base
<!-- @require:pytorch -->

#### Dipendenze aggiuntive

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Qui sono testati e supportati solo i pacchetti principali. **bitsandbytes non è ben supportato su Windows**, pertanto l'installazione per Windows lo omette; utilizza LoRA o il fine-tuning completo su Windows (QLoRA richiede bitsandbytes ed è pensato per Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### Abilitare l'autenticazione HF (modelli protetti, personalizzati o non preinstallati)

In questo esempio utilizziamo **google/gemma-3-4b-it**, che è un modello **protetto** (gated). Devi accettare i termini del modello su Hugging Face e quindi autenticarti affinché gli script di addestramento possano scaricarlo.

1. **Accetta la licenza:** Apri [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), accedi (o crea un account) e accetta la licenza/i termini sulla pagina del modello (ad es. "Agree and access repository").
2. **Installa ed esegui l'accesso:** Installa la Hugging Face CLI, quindi esegui il login standard:

```bash
pip install huggingface_hub
hf auth login
```

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['train_qlora.py', 'train_lora.py', 'train_full_finetuning.py']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in scripts:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=verify-imports timeout=60 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import AutoPeftModelForCausalLM
from trl import SFTTrainer

print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @test:id=verify-package-version timeout=60 hidden=True setup=activate-venv -->
```python
import importlib.metadata as md

pkgs = [
    "torch", "transformers", "trl", "peft", "accelerate",
    "datasets", "safetensors", "fsspec", "bitsandbytes",
    "huggingface_hub", "tokenizers",
]
for p in pkgs:
    try:
        print(f"{p}: {md.version(p)}")
    except md.PackageNotFoundError:
        print(f"{p}: NOT INSTALLED")
```
<!-- @test:end -->

<!-- @test:id=quick-train-lora timeout=600 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_lora.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=quick-train-qlora timeout=600 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_qlora.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=quick-train-full-finetuning timeout=1200 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_full_finetuning.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->
<!-- @device:end -->
---

## Comprendere le tecniche

### Cos'è LoRA?

**LoRA (Low-Rank Adaptation)** mantiene il modello base congelato e addestra solo piccole matrici "adattatrici" che vengono aggiunte a determinati livelli. 

- **L'idea chiave**: invece di aggiornare un'enorme matrice di pesi con milioni di parametri, apprendiamo un aggiornamento a basso rango (due piccole matrici il cui prodotto ha molti meno parametri). Questo offre una significativa riduzione dei parametri addestrabili e della VRAM, mantenendo gran parte della qualità del fine-tuning completo.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### Cos'è QLoRA?

**QLoRA** combina la **quantizzazione a 4 bit** con **LoRA**. Il modello base viene caricato in 4 bit (con un notevole risparmio di memoria) e solo gli adattatori LoRA vengono addestrati con una precisione maggiore. In questo modo si ottiene l'efficienza dei parametri di LoRA insieme a un consumo di VRAM molto inferiore, con un piccolo compromesso in termini di qualità rispetto a LoRA a piena precisione. Da notare che la quantizzazione a 4 bit può causare instabilità numeriche (picchi di loss o NaN), quindi gli utenti potrebbero spesso preferire **LoRA** se è disponibile VRAM sufficiente.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Nota**: Per i modelli base MXFP4 come `openai/gpt-oss-20b`, si consiglia di utilizzare **LoRA** (`train_lora.py`) invece di QLoRA. Il percorso a 4 bit di `bitsandbytes` dello script QLoRA in genere de-quantizza i pesi MXFP4 in BF16, quindi l'esecuzione si comporta come LoRA standard. L'MXFP4 nativo richiede `bitsandbytes` compilato dal sorgente oltre a uno stack Transformers/Triton/kernels corrispondente. Vedi la [documentazione MXFP4 di Transformers](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. Scegli il tuo metodo

| Metodo | Memoria | Velocità | Qualità | Ideale per |
|--------|--------|-------|---------|----------|
| **QLoRA** (solo Linux) | 12-16GB | Massima | 90-95% | Basso utilizzo di memoria |
| **LoRA** | 24-32GB | Veloce | 95-98% | Approccio bilanciato |
| **Full** | 80GB+ | Minima | 100% | Massima qualità |

### 3. Esegui l'addestramento

**Dataset e cosa impara il modello**  
Gli script trasformano il dataset in esempi di chat. Ad esempio, lo script QLoRA utilizza **Abirate/english_quotes**: ogni esempio diventa una coppia utente-assistente come:

- **Utente:** “Dammi una citazione su: &lt;tag&gt;”
- **Assistente:** “&lt;citazione&gt; – &lt;autore&gt;”

Il fine-tuning insegna al modello a rispondere a richieste di citazioni su un determinato argomento e a restituirle nel formato `<quote text> - <author>`. Gli script LoRA e full fine-tuning utilizzano **databricks/databricks-dolly-15k** (coppie generiche di istruzione/risposta), quindi il compito esatto varia a seconda dello script; l'idea è la stessa: adattare il modello al dataset e al formato scelti.

Di seguito è riportato un riepilogo dei metodi di addestramento disponibili. Ogni metodo rimanda al rispettivo script e fornisce una breve descrizione per aiutarti a scegliere l'approccio più adatto.

| Script                           | Metodo            | Descrizione                                                                                                         | VRAM tipica | Consigliato per                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Addestra piccole matrici adapter mantenendo congelato il modello base. 3-5 volte più veloce; qualità pari a circa il 95-98% rispetto al modello completo.                         | 24–32GB      | Utenti avanzati; più adapter; maggiore VRAM disponibile    |
| [`train_qlora.py`](assets/train_qlora.py)  *(solo Linux)*             | **QLoRA**       | Quantizzazione a 4 bit + adapter LoRA. Utilizzo di memoria minimo, massima velocità, piccolo compromesso sulla qualità. Richiede `bitsandbytes` (solo Linux).                            | 12–16GB      | La maggior parte degli utenti; esperimenti rapidi; VRAM limitata      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Full Fine-tuning** | Aggiorna tutti i parametri del modello. Massima qualità; massimo utilizzo di memoria e risorse di calcolo.                                    | 40GB+        | Massima qualità; ricerca; ampia disponibilità di VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Nota:** il full fine-tuning (`train_full_finetuning.py`) potrebbe richiedere più di 64GB di RAM di sistema e potrebbe non essere realizzabile su questo dispositivo. Valuta l'utilizzo di LoRA o QLoRA.
<!-- @os:end -->

<!-- @os:windows -->
> **Nota:** il full fine-tuning (`train_full_finetuning.py`) potrebbe richiedere più di 64GB di RAM di sistema e potrebbe non essere realizzabile su questo dispositivo. Valuta l'utilizzo di LoRA.
<!-- @os:end -->
<!-- @device:end -->

Seleziona semplicemente il `Training method` preferito, scarica lo script corrispondente ed eseguilo utilizzando il comando mantenendo attivo il tuo ambiente virtuale: 

```python
python3 train_<method_name>.py.
```

## Utilizzare il modello sottoposto a fine-tuning

### Dopo il Full Fine-Tuning

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "output-gemma-3-4b-it-full",     # Directory containing your fully fine-tuned checkpoint
    device_map="auto",
    torch_dtype="auto"            # Use BF16 if your GPU supports it, else "auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-it-full")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Dopo l'addestramento LoRA/QLoRA

```python
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

# Load model with LoRA or QLoRA adapters
model = AutoPeftModelForCausalLM.from_pretrained(
    "output-gpt-oss-20b-qlora",   # or "output-gemma-3-4b-it-lora" depending on your training
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gpt-oss-20b-qlora")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Unire l'adapter LoRA al modello base

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Nota:**  
- Assicurati che il nome della directory del modello (`output-gemma-3-4b-it-full`, `output-gpt-oss-20b-qlora`) corrisponda alla cartella di output effettiva generata dall'addestramento.  
- Se hai utilizzato LoRA invece di QLoRA, sostituisci semplicemente il percorso di conseguenza.  
- Alcuni modelli Gemma richiedono di specificare `trust_remote_code=True` in `from_pretrained`; aggiungilo se vedi un avviso correlato.

Per impostazioni più personalizzate (token di padding, dispositivo, ecc.), fai riferimento allo script utilizzato per l'addestramento.

<!-- @test:id=verify-lora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys

out_dir = "output-gemma-3-4b-it-lora"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

if not (os.path.exists(os.path.join(out_dir, "adapter_model.safetensors")) or os.path.exists(os.path.join(out_dir, "adapter_model.bin"))):
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: LoRA output looks correct")
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=verify-qlora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys

out_dir = "output-gemma-3-4b-it-qlora"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

if not (os.path.exists(os.path.join(out_dir, "adapter_model.safetensors")) or os.path.exists(os.path.join(out_dir, "adapter_model.bin"))):
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: QLoRA output looks correct")
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=verify-full-finetuning-output timeout=300 hidden=True setup=activate-venv -->
```python
import glob
import os
import sys

out_dir = "output-gemma-3-4b-it-full"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

# Weights may be saved as a single model.safetensors or, when the model
# exceeds max_shard_size, as model-*.safetensors shards plus an index.
single = os.path.exists(os.path.join(out_dir, "model.safetensors"))
shards = glob.glob(os.path.join(out_dir, "model-*.safetensors"))
if not single and not shards:
    print("FAIL: No model safetensors weights found")
    sys.exit(1)

print(f"PASS: Full fine-tuned model output looks correct: {out_dir}")
```
<!-- @test:end -->
<!-- @device:end -->
---

## Guida alla personalizzazione

### Usa il tuo dataset personale

Tutti gli script utilizzano lo stesso formato di dataset. Sostituisci la sezione di caricamento:

```python
from datasets import load_dataset

# Option 1: Local JSON/JSONL file
dataset = load_dataset('json', data_files='your_data.json')

# Option 2: Hugging Face Hub dataset
dataset = load_dataset('username/dataset-name')

# Option 3: CSV file
dataset = load_dataset('csv', data_files='data.csv')

# Format for chat models
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['instruction']},
            {"role": "assistant", "content": example['response']}
        ]
    }

dataset = dataset.map(format_instruction)
```

**Formato del dataset per file JSON/JSONL locali:**

Quando utilizzi questo metodo, assicurati che i tuoi file JSON siano strutturati correttamente per evitare errori di parsing. 

È necessario rispettare le seguenti linee guida:
* **Formattazione del file:** i file JSON dovrebbero essere formattati all'interno di un ambiente di sviluppo integrato (IDE) per garantire una struttura e una sintassi corrette.
* **Chiavi obbligatorie:** il file JSON personalizzato deve contenere le chiavi `instruction` e `response`. Queste chiavi sono essenziali per il corretto funzionamento del metodo.
```json
[
  {
    "instruction": "Your first instruction here",
    "response": "Expected response here"
  },
  {
    "instruction": "Your second instruction here",
    "response": "Expected response here"
  }
]
```
**Formato del dataset per i dataset di Hugging Face Hub**

Quando utilizzi dataset provenienti da Hugging Face, assicurati che siano strutturati correttamente per facilitare un'integrazione senza intoppi. 

È necessario seguire le seguenti linee guida:
* **Coppia istruzione-risposta:** concentrati su dataset che includono una coppia `instruction-response`. Questa struttura è essenziale per il corretto funzionamento previsto.
* **Modifica delle chiavi personalizzate:** se il tuo dataset non è conforme alla struttura `instruction-response`, hai la possibilità di modificare la funzione `format_instruction()`. Questo ti consente di adattarla a chiavi specifiche in base alle tue esigenze.

Esempio di adattamento: nei casi in cui l'output del dataset debba essere modificato, puoi adattare la sezione della risposta all'interno della funzione format_instruction() in base alle tue esigenze.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Formato del dataset per file CSV**

Per utilizzare lo script con un file in formato CSV, devi assicurarti che il file CSV contenga colonne denominate `instruction` e `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Modifica i parametri di addestramento

Modifica lo script di addestramento e cambia le variabili in base ai tuoi obiettivi: **learning rate** (`LR`), **epoche** (`EPOCHS`), **dimensione del batch** (`BATCH_SIZE`), **accumulo del gradiente** (`GRAD_ACCUM_STEPS`) e, per LoRA/QLoRA, il **rank** (`LORA_R`). Per esecuzioni più rapide, usa meno epoche e un learning rate (LR) più alto; per una qualità migliore, usa più epoche e un LR più basso. Riduci la dimensione del batch o la lunghezza della sequenza se incontri errori di memoria insufficiente.
### Suggerimenti per l'ottimizzazione della memoria

Se riscontri errori di memoria insufficiente:

**1. Riduci la dimensione del batch:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Riduci la lunghezza della sequenza:**
```python
max_seq_length=256  # Instead of 512
```

**3. Usa una quantizzazione più aggressiva:**
```
Full → LoRA → QLoRA
```

**4. Abilita il Gradient Checkpointing (solo per il fine-tuning completo):**
```python
model.gradient_checkpointing_enable()
```

---

## Monitoraggio e debug

### Monitora la memoria della GPU

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Facoltativo) Traccia gli esperimenti con Weights & Biases

Per registrare esecuzioni e metriche su [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

Nello script di training, imposta `report_to="wandb"` e facoltativamente `run_name="your-experiment-name"` nella configurazione del trainer. Se preferisci non usare Wandb, lascia `report_to` al suo valore predefinito oppure impostalo su `"none"`.

### Problemi comuni

#### Memoria insufficiente (OOM)

**Soluzione:** riduci la dimensione del batch e/o usa QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### La loss non diminuisce

**Soluzione:** regola il learning rate
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Training lento

**Soluzione:** aumenta la dimensione del batch se la memoria lo consente
```python
BATCH_SIZE = 8
```
## Passaggi successivi

Dopo aver completato con successo il fine-tuning, valuta i seguenti passaggi successivi per ottenere di più dal tuo modello:

1. **Valuta** in modo approfondito su dati di test non utilizzati in precedenza per misurare la capacità di generalizzazione ed evitare l'overfitting.
2. **Sperimenta** provando diversi valori di iperparametri per ottenere un miglior compromesso tra accuratezza, velocità e utilizzo della memoria.
3. **Traccia** tutti i tuoi esperimenti (e le relative metriche) con Weights & Biases per una ricerca riproducibile.
4. **Prova** ad addestrare il modello sui tuoi dataset personalizzati per adattarlo specificamente al tuo caso d'uso.
5. **Distribuisci** il tuo modello sottoposto a fine-tuning per un'inferenza rapida utilizzando backend efficienti come vLLM su hardware compatibile.
6. **Esplora** tecniche avanzate tra cui il prompt engineering, la precisione mista e lunghezze di sequenza maggiori.
7. **Addestra** più adapter LoRA per compiti o domini diversi e sostituiscili in base alle necessità.

---