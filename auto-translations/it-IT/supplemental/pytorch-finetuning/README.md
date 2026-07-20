<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Questo playbook utilizza tag speciali che GitHub non è in grado di renderizzare. Visita [amd.com/playbooks](https://amd.com/playbooks) per visualizzare correttamente questo contenuto in anteprima.
<!-- @github-only:end -->

## Panoramica

Questo tutorial fornisce esempi passo dopo passo per il fine-tuning di un large language model (LLM) con PyTorch e ROCm. Copre diverse tecniche, dal fine-tuning standard alle strategie di Parameter-Efficient Fine-Tuning (PEFT) efficienti in termini di memoria, così da poter adattare facilmente i modelli alle proprie esigenze.

**Modello utilizzato**: google/gemma-3-4b-it  *(vedi [Abilitare l'autenticazione HF](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) se il modello è gated)*  
**Hardware**: GPU AMD Radeon™ con supporto ROCm  
**Framework**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Nota:** Puoi anche provare altre architetture di modello, incluso **GPT-OSS-20B**, sostituendo il modello negli script di training forniti.
> Il full fine-tuning richiede almeno 32 GB di memoria GPU e 64 GB di RAM di sistema.
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> **Nota:** Il fine-tuning con LoRA e QLoRA richiede almeno 16 GB di memoria GPU e 32 GB di RAM di sistema.
<!-- @device:end -->

## Cosa Imparerai

- Come effettuare il fine-tuning di un LLM usando LoRA, QLoRA e il full fine-tuning con PyTorch e ROCm
- Come salvare e distribuire il tuo modello sottoposto a fine-tuning
- Come monitorare il training e risolvere i problemi più comuni

## Impostazione della Configurazione della Memoria

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Controllo degli Aggiornamenti Software
> **Nota**: Se VS Code non è installato, puoi installarlo con Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installazione dei Prerequisiti Software

#### Creazione di un Ambiente Virtuale

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=60 -->
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
**Concedi al tuo utente l'accesso ai dispositivi GPU** (esegui il logout e poi di nuovo il login affinché questo abbia effetto):

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=120 -->
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
<!-- @test:id=create-venv timeout=60 -->
```powershell
python -m venv finetune-venv --system-site-packages
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=60 -->
```powershell
python -m venv finetune-venv
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

#### Installazione delle Dipendenze di Base
<!-- @require:pytorch -->

#### Dipendenze Aggiuntive

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Qui sono testati e supportati solo i pacchetti principali. **bitsandbytes non è ben supportato su Windows**, quindi l'installazione su Windows lo omette; usa LoRA o il full fine-tuning su Windows (QLoRA richiede bitsandbytes ed è pensato per Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### Abilitare l'autenticazione HF (modelli gated o personalizzati / non preinstallati)

In questo esempio utilizziamo **google/gemma-3-4b-it**, che è un modello **gated**. Devi accettare i termini del modello su Hugging Face e poi autenticarti affinché gli script di training possano scaricarlo.

1. **Accetta la licenza:** Apri [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), accedi (o crea un account) e accetta la licenza/i termini nella pagina del modello (ad es. "Agree and access repository").
2. **Installa ed effettua il login:** Installa la CLI di Hugging Face, poi esegui il login standard:

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

## Comprendere le Tecniche

### Cos'è LoRA?

**LoRA (Low-Rank Adaptation)** mantiene congelato il modello base e addestra solo piccole matrici "adapter" che vengono aggiunte a determinati layer. 

- **L'idea chiave**: invece di aggiornare un'enorme matrice di pesi con milioni di parametri, si apprende un aggiornamento a basso rango (due piccole matrici il cui prodotto ha molti meno parametri). Questo consente una notevole riduzione dei parametri addestrabili e della VRAM, mantenendo gran parte della qualità del full fine-tuning.

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

**QLoRA** combina la **quantizzazione a 4 bit** con **LoRA**. Il modello base viene caricato in 4 bit (con un grande risparmio di memoria), e solo gli adapter LoRA vengono addestrati con una precisione maggiore. In questo modo si ottiene l'efficienza dei parametri di LoRA più un consumo di VRAM molto più basso, con un piccolo compromesso in termini di qualità rispetto a LoRA a piena precisione. Nota che la quantizzazione a 4 bit può causare instabilità numeriche (picchi di loss o NaN), quindi gli utenti potrebbero spesso preferire **LoRA** se è disponibile abbastanza VRAM.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Nota**: Per modelli base MXFP4 come `openai/gpt-oss-20b`, si consiglia di utilizzare **LoRA** (`train_lora.py`) invece di QLoRA. Il percorso a 4 bit di `bitsandbytes` nello script QLoRA in genere dequantizza i pesi MXFP4 in BF16, quindi l'esecuzione si comporta come una LoRA standard. Il supporto nativo per MXFP4 richiede `bitsandbytes` compilato dal sorgente insieme a uno stack Transformers/Triton/kernels compatibile. Consulta la [documentazione MXFP4 di Transformers](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---

### 2. Scegli il Tuo Metodo

| Metodo | Memoria | Velocità | Qualità | Ideale Per |
|--------|--------|-------|---------|----------|
| **QLoRA** (solo Linux) | 12-16GB | La più veloce | 90-95% | Basso Utilizzo di Memoria |
| **LoRA** | 24-32GB | Veloce | 95-98% | Approccio bilanciato |
| **Full** | 80GB+ | La più lenta | 100% | Massima qualità |
### 3. Esegui il Training

**Dataset e cosa apprende il modello**  
Gli script trasformano il dataset in esempi di chat. Ad esempio, lo script QLoRA utilizza **Abirate/english_quotes**: ogni esempio diventa una coppia utente–assistente come:

- **Utente:** “Dammi una citazione su: &lt;tag&gt;”
- **Assistente:** “&lt;citazione&gt; – &lt;autore&gt;”

Il fine-tuning insegna al modello a rispondere ai prompt che richiedono citazioni su un argomento e a restituirle nel formato `<quote text> - <author>`. Gli script LoRA e full fine-tuning utilizzano **databricks/databricks-dolly-15k** (coppie generiche istruzione/risposta), quindi il compito esatto varia a seconda dello script; l'idea è la stessa - adattare il modello al dataset e al formato scelti.

Di seguito è riportato un riepilogo dei metodi di training disponibili. Ogni metodo rimanda al proprio script e fornisce una breve descrizione per aiutarti a scegliere l'approccio giusto.

| Script                           | Metodo            | Descrizione                                                                                                         | VRAM tipica | Consigliato per                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Addestra piccole matrici adattatrici mantenendo congelato il modello base. 3–5x più veloce; ~95–98% della qualità completa.                         | 24–32GB      | Utenti avanzati; adattatori multipli; più VRAM disponibile    |
| [`train_qlora.py`](assets/train_qlora.py)  *(solo Linux)*             | **QLoRA**       | Quantizzazione a 4 bit + adattatori LoRA. Utilizzo di memoria minimo, il più veloce, con una piccola riduzione della qualità. Richiede `bitsandbytes` (solo Linux).                            | 12–16GB      | La maggior parte degli utenti; esperimenti rapidi; VRAM limitata      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Full Fine-tuning** | Aggiorna tutti i parametri del modello. Massima qualità; utilizzo massimo di memoria e calcolo.                                    | 40GB+        | Massima qualità; ricerca; VRAM elevata           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Nota:** il full fine-tuning (`train_full_finetuning.py`) potrebbe richiedere più di 64GB di RAM di sistema e potrebbe non essere fattibile su questo dispositivo. Valuta l'utilizzo di LoRA o QLoRA come alternativa.
<!-- @os:end -->

<!-- @os:windows -->
> **Nota:** il full fine-tuning (`train_full_finetuning.py`) potrebbe richiedere più di 64GB di RAM di sistema e potrebbe non essere fattibile su questo dispositivo. Valuta l'utilizzo di LoRA come alternativa.
<!-- @os:end -->
<!-- @device:end -->

Seleziona semplicemente il `Training method` preferito, scarica lo script corrispondente ed eseguilo utilizzando il comando mantenendo attivo il tuo ambiente virtuale: 

```python
python3 train_<method_name>.py.
```

## Utilizzo del tuo Modello Sottoposto a Fine-Tuning

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

### Dopo il Training con LoRA/QLoRA

```python
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

# Load model with LoRA or QLoRA adapters
model = AutoPeftModelForCausalLM.from_pretrained(
    "output-gemma-3-4b-it-qlora",   # or "output-gemma-3-4b-lora" depending on your training
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-it-qlora")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Unire l'Adattatore LoRA nel Modello Base

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Nota:**  
- Assicurati che il nome della directory del modello (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) corrisponda alla cartella di output effettiva generata dal training.  
- Se hai utilizzato LoRA invece di QLoRA, sostituisci semplicemente il percorso di conseguenza.  
- Alcuni modelli Gemma richiedono la specifica di `trust_remote_code=True` in `from_pretrained`; aggiungilo se visualizzi un avviso correlato.

Per impostazioni più personalizzate (token di padding, dispositivo, ecc.), fai riferimento allo script utilizzato per il training.

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
    "model.safetensors.index.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

shards = glob.glob(os.path.join(out_dir, "model-*.safetensors"))
if not shards:
    print("FAIL: No sharded model safetensors files found")
    sys.exit(1)

print(f"PASS: Full fine-tuned model output looks correct: {out_dir}")
```
<!-- @test:end -->
<!-- @device:end -->
---

## Guida alla Personalizzazione

### Utilizza il Tuo Dataset

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

**Formato del Dataset per File JSON/JSONL Locali:**

Quando utilizzi questo metodo, assicurati che i tuoi file JSON siano strutturati correttamente per evitare errori di parsing. 

È necessario rispettare le seguenti linee guida:
* **Formattazione del File:** i file JSON devono essere formattati all'interno di un ambiente di sviluppo integrato (IDE) per garantire una struttura e una sintassi corrette.
* **Chiavi Richieste:** il file JSON personalizzato deve contenere le chiavi `instruction` e `response`. Queste chiavi sono essenziali per il corretto funzionamento del metodo.
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
**Formato del Dataset per Dataset di Hugging Face Hub**

Quando utilizzi dataset provenienti da Hugging Face, assicurati che i tuoi dataset siano strutturati correttamente per facilitare un'integrazione senza problemi. 

È necessario seguire le seguenti linee guida:
* **Coppia Istruzione-Risposta:** concentrati su dataset che includono una coppia `instruction-response`. Questa struttura è essenziale per il corretto funzionamento previsto.
* **Modifica delle Chiavi Personalizzate:** se il tuo dataset non è conforme alla struttura `instruction-response`, hai la possibilità di modificare la funzione `format_instruction()`. Questo ti consente di adattarla a chiavi specifiche in base alle tue esigenze.

Esempio di Adattamento: nei casi in cui l'output del dataset debba essere modificato, puoi adattare la sezione di risposta all'interno della funzione format_instruction() in base alle tue esigenze.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Formato del Dataset per File CSV**

Per adattare lo script all'utilizzo di un file in formato CSV, devi assicurarti che il file CSV contenga colonne denominate `instruction` e `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Regola i Parametri di Training

Modifica lo script di training e cambia le variabili in base ai tuoi obiettivi: **learning rate** (`LR`), **epoche** (`EPOCHS`), **dimensione del batch** (`BATCH_SIZE`), **accumulo del gradiente** (`GRAD_ACCUM_STEPS`) e, per LoRA/QLoRA, il **rank** (`LORA_R`). Per esecuzioni più rapide utilizza meno epoche e un learning rate (LR) più elevato; per una qualità migliore utilizza più epoche e un LR più basso. Riduci la dimensione del batch o la lunghezza della sequenza se riscontri errori di memoria insufficiente.

### Consigli per l'Ottimizzazione della Memoria

Se riscontri errori di memoria insufficiente:

**1. Riduci la Dimensione del Batch:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Riduci la Lunghezza della Sequenza:**
```python
max_seq_length=256  # Instead of 512
```

**3. Utilizza una Quantizzazione Più Aggressiva:**
```
Full → LoRA → QLoRA
```

**4. Abilita il Gradient Checkpointing (solo per il Full Fine-Tuning):**
```python
model.gradient_checkpointing_enable()
```

---

## Monitoraggio e Debug

### Monitora la Memoria della GPU

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Facoltativo) Monitorare gli esperimenti con Weights & Biases

Per registrare le esecuzioni e le metriche su [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

Nello script di addestramento, impostare `report_to="wandb"` e facoltativamente `run_name="your-experiment-name"` nella configurazione del trainer. Se si preferisce non utilizzare Wandb, lasciare `report_to` al valore predefinito oppure impostarlo su `"none"`.

### Problemi comuni

#### Memoria esaurita (OOM)

**Soluzione:** Ridurre la dimensione del batch e/o utilizzare QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### La perdita non diminuisce

**Soluzione:** Regolare il learning rate
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Addestramento lento

**Soluzione:** Aumentare la dimensione del batch se la memoria lo consente
```python
BATCH_SIZE = 8
```
## Passaggi successivi

Dopo aver completato con successo il fine-tuning, valutare i seguenti passaggi successivi per ottenere di più dal modello:

1. **Valutare** approfonditamente su dati di test non utilizzati per l'addestramento, per misurare la capacità di generalizzazione ed evitare l'overfitting.
2. **Sperimentare** provando diversi valori di iperparametri per ottenere un migliore compromesso tra accuratezza, velocità e utilizzo della memoria.
3. **Monitorare** tutti gli esperimenti (e le relative metriche) con Weights & Biases per una ricerca riproducibile.
4. **Provare** ad addestrare il modello sui propri dataset personalizzati per adattarlo specificamente al proprio caso d'uso.
5. **Distribuire** il modello sottoposto a fine-tuning per un'inferenza rapida utilizzando backend efficienti come vLLM su hardware compatibile.
6. **Esplorare** tecniche avanzate, tra cui prompt engineering, precisione mista e sequenze di lunghezza maggiore.
7. **Addestrare** più adattatori LoRA per diverse attività o domini e scambiarli in base alle esigenze.

---