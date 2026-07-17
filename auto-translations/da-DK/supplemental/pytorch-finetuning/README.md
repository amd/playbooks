<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Oversigt

Denne vejledning giver trinvise eksempler på finjustering af en stor sprogmodel (LLM) med PyTorch og ROCm. Den dækker flere teknikker, fra standard finjustering til hukommelseseffektive Parameter-Efficient Fine-Tuning (PEFT)-strategier, så du nemt kan tilpasse modeller til dine behov.

**Anvendt model**: google/gemma-3-4b-it  *(se [Aktivér HF-godkendelse](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) hvis modellen er låst)*  
**Hardware**: AMD Radeon™ GPU med ROCm-understøttelse  
**Framework**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Bemærk:** Du kan også prøve andre modelarkitekturer, herunder **GPT-OSS-20B**, ved at erstatte modellen i de medfølgende træningsscripts.
> Fuld finjustering kræver mindst 32 GB GPU-hukommelse og 64 GB systemhukommelse.
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> **Bemærk:** LoRA og QLoRA finjustering kræver mindst 16 GB GPU-hukommelse og 32 GB systemhukommelse.
<!-- @device:end -->

## Hvad du lærer

- Sådan finjusterer du en LLM ved hjælp af LoRA, QLoRA og fuld finjustering med PyTorch og ROCm
- Sådan gemmer og implementerer du din finjusterede model
- Sådan overvåger du træning og fejlfinder almindelige problemer

## Indstilling af hukommelseskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Søg efter softwareopdateringer
> **Bemærk**: Hvis VS Code ikke er installeret, kan du installere det via Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installation af softwareforudsætninger

#### Opret et virtuelt miljø

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
**Giv din bruger adgang til GPU-enheder** (log ud og ind igen for at dette træder i kraft):

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

#### Installation af grundlæggende afhængigheder
<!-- @require:pytorch -->

#### Yderligere afhængigheder

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Kun kernepakker er testet og understøttet her. **bitsandbytes er ikke godt understøttet på Windows**, så Windows-installationen udelader det; brug LoRA eller fuld finjustering på Windows (QLoRA kræver bitsandbytes og er beregnet til Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### Aktivér HF-godkendelse (låste eller brugerdefinerede / ikke-forudinstallerede modeller)

I dette eksempel bruger vi **google/gemma-3-4b-it**, som er en **låst** model. Du skal acceptere modellens vilkår på Hugging Face og derefter godkende dig, så træningsscripts kan downloade den.

1. **Acceptér licensen:** Åbn [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), log ind (eller opret en konto), og acceptér licensen/vilkårene på modelsiden (f.eks. "Agree and access repository").
2. **Installér og log ind:** Installér Hugging Face CLI, og kør derefter standardlogin:

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

## Forståelse af teknikkerne

### Hvad er LoRA?

**LoRA (Low-Rank Adaptation)** holder basismodellen frossen og træner kun små "adapter"-matricer, der tilføjes til bestemte lag.

- **Nøgleidéen**: i stedet for at opdatere en enorm vægtmatrix med millioner af parametre lærer vi en lav-rang-opdatering (to små matricer, hvis produkt har langt færre parametre). Det giver en stor reduktion i trænbare parametre og VRAM, mens det meste af den fulde finjusteringskvalitet bevares.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### Hvad er QLoRA?

**QLoRA** kombinerer **4-bit kvantisering** med **LoRA**. Basismodellen indlæses i 4-bit (stor hukommelsesbesparelse), og kun LoRA-adapterne trænes i højere præcision. Du får dermed parametereffektiviteten fra LoRA plus meget lavere VRAM-forbrug, med en lille kvalitetsmæssig afvejning sammenlignet med fuld-præcisions-LoRA. Bemærk, at 4-bit kvantisering kan forårsage numeriske ustabiliteter (tab-spikes eller NaN'er), så brugere foretrækker ofte **LoRA**, hvis der er tilstrækkelig VRAM til rådighed.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Bemærk**: For MXFP4-basismodeller som `openai/gpt-oss-20b` anbefaler vi at bruge **LoRA** (`train_lora.py`) i stedet for QLoRA. QLoRA-scriptets `bitsandbytes` 4-bit-sti dekkvantiserer typisk MXFP4-vægte til BF16, så kørslen opfører sig som standard LoRA. Native MXFP4 kræver `bitsandbytes` bygget fra kildekode samt en matchende Transformers/Triton/kernels-stak. Se [Transformers MXFP4-dokumentationen](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---

### 2. Vælg din metode

| Metode | Hukommelse | Hastighed | Kvalitet | Bedst til |
|--------|--------|-------|---------|----------|
| **QLoRA** (kun Linux) | 12-16GB | Hurtigst | 90-95% | Lavt hukommelsesforbrug |
| **LoRA** | 24-32GB | Hurtig | 95-98% | Afbalanceret tilgang |
| **Fuld** | 80GB+ | Langsomst | 100% | Maksimal kvalitet |

### 3. Kør træning

**Datasæt og hvad modellen lærer**  
Scriptene omdanner datasættet til chat-eksempler. For eksempel bruger QLoRA-scriptet **Abirate/english_quotes**: hvert eksempel bliver et bruger–assistent-par som:

- **Bruger:** "Giv mig et citat om: &lt;tag&gt;"
- **Assistent:** "&lt;citat&gt; – &lt;forfatter&gt;"

Finjustering lærer modellen at reagere på prompter, der beder om citater om et emne, og returnere dem i formatet `<citatekst> - <forfatter>`. LoRA- og fuld finjusterings-scriptene bruger **databricks/databricks-dolly-15k** (generelle instruktions-/svarpar), så den præcise opgave varierer efter script; idéen er den samme – tilpas modellen til dit valgte datasæt og format.

Nedenfor er en oversigt over de tilgængelige træningsmetoder. Hver metode linker til sit script og giver en kort beskrivelse til hjælp ved valg af den rette tilgang.

| Script                           | Metode            | Beskrivelse                                                                                                         | Typisk VRAM | Anbefalet til                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Træner små adaptermatricer, mens basismodellen er frossen. 3–5x hurtigere; ~95–98% fuld kvalitet.                         | 24–32GB      | Erfarne brugere; flere adaptere; mere VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(kun Linux)*             | **QLoRA**       | 4-bit kvantisering + LoRA-adaptere. Lavest hukommelsesforbrug, hurtigst, lille kvalitetsafvejning. Kræver `bitsandbytes` (kun Linux).                            | 12–16GB      | De fleste brugere; hurtige eksperimenter; begrænset VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Fuld finjustering** | Opdaterer alle modelparametre. Maksimal kvalitet; højest hukommelses- og beregningsforbrug.                                    | 40GB+        | Maksimal kvalitet; forskning; stor VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Bemærk:** Fuld finjustering (`train_full_finetuning.py`) kan kræve mere end 64 GB systemhukommelse og er muligvis ikke gennemførlig på denne enhed. Overvej at bruge LoRA eller QLoRA i stedet.
<!-- @os:end -->

<!-- @os:windows -->
> **Bemærk:** Fuld finjustering (`train_full_finetuning.py`) kan kræve mere end 64 GB systemhukommelse og er muligvis ikke gennemførlig på denne enhed. Overvej at bruge LoRA i stedet.
<!-- @os:end -->
<!-- @device:end -->

Vælg blot din foretrukne `Træningsmetode`, download det tilsvarende script og udfør det med følgende kommando, mens dit virtuelle miljø er aktiveret:

```python
python3 train_<method_name>.py.
```

## Brug af din finjusterede model

### Efter fuld finjustering

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

### Efter LoRA/QLoRA-træning

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

### Flet LoRA-adapter ind i basismodellen

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Bemærk:**  
- Sørg for, at modelkatalogets navn (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) stemmer overens med din faktiske outputmappe fra træningen.  
- Hvis du brugte LoRA i stedet for QLoRA, skal du blot erstatte stien tilsvarende.  
- Nogle Gemma-modeller kræver angivelse af `trust_remote_code=True` i `from_pretrained`; tilføj dette, hvis du ser en relateret advarsel.

For flere brugerdefinerede indstillinger (padding-tokens, enhed osv.) henvises til det script, du brugte til træning.

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

## Tilpasningsvejledning

### Brug dit eget datasæt

Alle scripts bruger samme datasætformat. Erstat indlæsningssektionen:

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

**Datasætformat for lokal JSON/JSONL-fil:**

Når du bruger denne metode, skal du sikre, at dine JSON-filer er korrekt strukturerede for at undgå parseringsfejl.

Følgende retningslinjer skal overholdes:
* **Filformatering:** JSON-filer bør formateres i et integreret udviklingsmiljø (IDE) for at sikre korrekt struktur og syntaks.
* **Påkrævede nøgler:** Den brugerdefinerede JSON-fil skal indeholde nøglerne `instruction` og `response`. Disse nøgler er afgørende for, at metoden fungerer korrekt.
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
**Datasætformat for Hugging Face Hub-datasæt**

Når du anvender datasæt fra Hugging Face, skal du sikre, at dine datasæt er korrekt strukturerede for at muliggøre problemfri integration.

Følgende retningslinjer bør følges:
* **Instruktions-svar-par:** Fokusér på datasæt, der indeholder et `instruktions-svar`-par. Denne struktur er afgørende for den tilsigtede funktionalitet.
* **Tilpasning af brugerdefinerede nøgler:** Hvis dit datasæt ikke overholder `instruktions-svar`-strukturen, har du mulighed for at ændre funktionen `format_instruction()`. Dette giver dig mulighed for at imødekomme specifikke nøgler efter behov.

Eksempel på justering: I tilfælde, hvor datasættets output skal justeres, kan du ændre svarsektionen i funktionen format_instruction() for at tilpasse den til dine krav.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Datasætformat for CSV-fil**

For at tilpasse scriptet til brug af et CSV-filformat skal du sikre, at CSV-filen indeholder kolonner med navnene `instruction` og `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Juster træningsparametre

Rediger træningsscriptet og ændr variablerne, så de passer til dine mål: **læringsrate** (`LR`), **epoker** (`EPOCHS`), **batchstørrelse** (`BATCH_SIZE`), **gradientakkumulering** (`GRAD_ACCUM_STEPS`), og for LoRA/QLoRA **rang** (`LORA_R`). For hurtigere kørsler bruges færre epoker og en højere læringsrate (LR); for bedre kvalitet bruges flere epoker og en lavere LR. Reducer batchstørrelse eller sekvenslængde, hvis du støder på fejl med utilstrækkelig hukommelse.

### Tips til hukommelsesoptimering

Hvis du støder på fejl med utilstrækkelig hukommelse:

**1. Reducer batchstørrelse:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Reducer sekvenslængde:**
```python
max_seq_length=256  # Instead of 512
```

**3. Brug mere aggressiv kvantisering:**
```
Full → LoRA → QLoRA
```

**4. Aktivér gradient checkpointing (kun fuld finjustering):**
```python
model.gradient_checkpointing_enable()
```

---

## Overvågning og fejlfinding

### Overvåg GPU-hukommelse

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Valgfrit) Spor eksperimenter med Weights & Biases

For at logge kørsler og målinger til [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

I træningsscriptet skal du angive `report_to="wandb"` og eventuelt `run_name="your-experiment-name"` i trainer-konfigurationen. Hvis du foretrækker ikke at bruge Wandb, lad `report_to` forblive på sin standardværdi eller sæt den til `"none"`.

### Almindelige problemer

#### Utilstrækkelig hukommelse (OOM)

**Løsning:** Reducer batchstørrelse og/eller brug QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### Tab falder ikke

**Løsning:** Juster læringsraten
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Langsom træning

**Løsning:** Øg batchstørrelsen, hvis hukommelsen tillader det
```python
BATCH_SIZE = 8
```
## Næste skridt

Når du har gennemført en vellykket finjustering, kan du overveje følgende næste skridt for at få mere ud af din model:

1. **Evaluér** grundigt på tilbageholdte testdata for at måle generaliseringsevnen og undgå overfitting.
2. **Eksperimentér** ved at prøve forskellige hyperparameterværdier for bedre nøjagtighed, hastighed og hukommelsesafvejninger.
3. **Spor** alle dine eksperimenter (og tilhørende målinger) med Weights & Biases for reproducerbar forskning.
4. **Prøv** at træne på dine egne brugerdefinerede datasæt for at tilpasse modellen specifikt til dit anvendelsestilfælde.
5. **Implementér** din finjusterede model til hurtig inferens ved hjælp af effektive backends som vLLM på kompatibel hardware.
6. **Udforsk** avancerede teknikker, herunder prompt engineering, blandet præcision og længere sekvenslængder.
7. **Træn** flere LoRA-adaptere til forskellige opgaver eller domæner og skift mellem dem efter behov.

---