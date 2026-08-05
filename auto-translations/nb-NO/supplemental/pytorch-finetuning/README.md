<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversettelse.** Denne siden ble automatisk oversatt fra engelsk og har ikke blitt gjennomgått av et menneske. Den kan inneholde feil, og enkelte instruksjoner, kommandoer, nedlastinger, produkttilgjengelighet eller annet innhold kan variere etter språk eller region. Ved eventuelle uoverensstemmelser eller avvik er den opprinnelige engelske versjonen av playbook-en gjeldende.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Oversikt

Denne veiledningen gir trinnvise eksempler for finjustering av en stor språkmodell (LLM) med PyTorch og ROCm. Den dekker flere teknikker, fra standard finjustering til minneeffektive Parameter-Efficient Fine-Tuning (PEFT)-strategier, slik at du enkelt kan tilpasse modeller til dine behov.

**Brukt modell**: google/gemma-3-4b-it  *(se [Aktiver HF-autentisering](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) hvis den er sperret)*  
**Maskinvare**: AMD Radeon™ GPU med ROCm-støtte  
**Rammeverk**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Merk:** 
> - Full finjustering krever minst **64 GB systemminne**, hvorav minst **32 GB må være tilgjengelig for GPU-en** (de 32 GB-ene er en del av de 64 GB-ene, ikke i tillegg til dem).
> - Du kan også prøve andre modellarkitekturer, inkludert **GPT-OSS-20B**, ved å bytte ut modellen i de medfølgende treningsskriptene.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **Merk:** LoRA- og QLoRA-finjustering krever minst **32 GB systemminne**, hvorav minst **16 GB må være tilgjengelig for GPU-en** (de 16 GB-ene er en del av de 32 GB-ene, ikke i tillegg til dem).
<!-- @os:end -->

<!-- @os:windows -->
> **Merk:** LoRA-finjustering krever minst **32 GB systemminne**, hvorav minst **16 GB må være tilgjengelig for GPU-en** (de 16 GB-ene er en del av de 32 GB-ene, ikke i tillegg til dem).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Merk:** LoRA- og QLoRA-finjustering krever et grafikkort med minst **16 GB dedikert GPU-minne** og **32 GB systemminne**.
> - På Linux kjører treningen utelukkende i grafikkortets dedikerte VRAM.
> - Den faller ikke tilbake til delt GPU-minne (systemminne) når VRAM går tom.
> - Kort med mindre enn 16 GB dedikert VRAM vil gå tom for minne under trening på Linux, selv om systemet har rikelig med RAM.
<!-- @os:end -->

<!-- @os:windows -->
> **Merk:** LoRA-finjustering krever minst **16 GB totalt GPU-minne** og **32 GB systemminne**.
> - På Windows kombineres grafikkortets dedikerte VRAM med delt GPU-minne (lånt fra systemminnet) til totalt GPU-minne.
> - Derfor kan kort med mindre enn 16 GB dedikert VRAM likevel kjøre denne oppskriften ved å bruke delt GPU-minne til å dekke differansen.
<!-- @os:end -->
<!-- @device:end -->

## Hva du vil lære

- Hvordan finjustere en LLM ved bruk av LoRA, QLoRA og full finjustering med PyTorch og ROCm
- Hvordan lagre og distribuere den finjusterte modellen din
- Hvordan overvåke trening og feilsøke vanlige problemer

## Konfigurere minneinnstillinger

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sjekk etter programvareoppdateringer
> **Merk**: Hvis VS Code ikke er installert, kan du installere det med Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installere programvareforutsetninger

#### Opprett et virtuelt miljø

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
**Gi brukeren din tilgang til GPU-enheter** (logg ut og inn igjen for at dette skal tre i kraft):

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

#### Installere grunnleggende avhengigheter
<!-- @require:pytorch -->

#### Ytterligere avhengigheter

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Kun kjernepakker er testet og støttet her. **bitsandbytes er ikke godt støttet på Windows**, så Windows-installasjonen utelater den; bruk LoRA eller full finjustering på Windows (QLoRA krever bitsandbytes og er beregnet for Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### Aktiver HF-autentisering (sperrede eller egendefinerte / ikke-forhåndsinstallerte modeller)

I dette eksemplet bruker vi **google/gemma-3-4b-it**, som er en **sperret** modell. Du må godta modellens vilkår på Hugging Face og deretter autentisere deg slik at treningsskriptene kan laste den ned.

1. **Godta lisensen:** Åpne [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), logg inn (eller opprett en konto), og godta lisensen/vilkårene på modellsiden (f.eks. «Agree and access repository»).
2. **Installer og logg inn:** Installer Hugging Face CLI, og kjør deretter standard innlogging:

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

## Forstå teknikkene

### Hva er LoRA?

**LoRA (Low-Rank Adaptation)** holder grunnmodellen frosset og trener kun små «adapter»-matriser som legges til bestemte lag. 

- **Nøkkelideen**: i stedet for å oppdatere en enorm vektmatrise med millioner av parametere, lærer vi en lavrangs-oppdatering (to små matriser der produktet har langt færre parametere). Dette gir en stor reduksjon i antall trenbare parametere og VRAM-bruk, samtidig som mesteparten av kvaliteten fra full finjustering beholdes.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### Hva er QLoRA?

**QLoRA** kombinerer **4-bits kvantisering** med **LoRA**. Grunnmodellen lastes inn i 4-bit (store minnebesparelser), og kun LoRA-adapterne trenes med høyere presisjon. Dermed får du parametereffektiviteten til LoRA pluss mye lavere VRAM-bruk, med et lite kvalitetstap sammenlignet med LoRA med full presisjon. Merk at 4-bits kvantisering kan forårsake numerisk ustabilitet (tapstopper eller NaN-verdier), så brukere foretrekker ofte **LoRA** hvis nok VRAM er tilgjengelig.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Merk**: For MXFP4-grunnmodeller som `openai/gpt-oss-20b` anbefaler vi å bruke **LoRA** (`train_lora.py`) i stedet for QLoRA. QLoRA-skriptets 4-bits-bane i `bitsandbytes` dekvantiserer vanligvis MXFP4-vektene til BF16, slik at kjøringen oppfører seg som vanlig LoRA. Nativ MXFP4 krever `bitsandbytes` bygget fra kildekode, i tillegg til en matchende Transformers/Triton/kernels-stakk. Se [Transformers MXFP4-dokumentasjonen](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. Velg metode

| Metode | Minne | Hastighet | Kvalitet | Best egnet for |
|--------|--------|-------|---------|----------|
| **QLoRA** (kun Linux) | 12-16GB | Raskest | 90-95% | Lavt minnebruk |
| **LoRA** | 24-32GB | Rask | 95-98% | Balansert tilnærming |
| **Full** | 80GB+ | Tregest | 100% | Maksimal kvalitet |

### 3. Kjør trening

**Datasett og hva modellen lærer**  
Skriptene gjør datasettet om til chat-eksempler. QLoRA-skriptet bruker for eksempel **Abirate/english_quotes**: hvert eksempel blir et bruker–assistent-par som:

- **Bruker:** «Gi meg et sitat om: &lt;tag&gt;»
- **Assistent:** «&lt;sitat&gt; – &lt;forfatter&gt;»

Finjustering lærer modellen å svare på forespørsler om sitater om et emne, og å returnere dem i formatet `<sitattekst> - <forfatter>`. LoRA- og full finjusteringsskriptene bruker **databricks/databricks-dolly-15k** (generelle instruksjon/svar-par), så den eksakte oppgaven varierer fra skript til skript; ideen er den samme - tilpass modellen til datasettet og formatet du har valgt.

Nedenfor er en oversikt over tilgjengelige treningsmetoder. Hver metode lenker til sitt skript og gir en kort beskrivelse for å velge riktig tilnærming.

| Skript                           | Metode            | Beskrivelse                                                                                                         | Typisk VRAM | Anbefalt for                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Trener små adaptermatriser mens basemodellen fryses. 3–5x raskere; ~95–98% av full kvalitet.                         | 24–32GB      | Avanserte brukere; flere adaptere; mer VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(kun Linux)*             | **QLoRA**       | 4-bit kvantisering + LoRA-adaptere. Lavest minnebruk, raskest, liten kvalitetsavveining. Krever `bitsandbytes` (kun Linux).                            | 12–16GB      | De fleste brukere; raske eksperimenter; begrenset VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Full finjustering** | Oppdaterer alle modellparametere. Maksimal kvalitet; høyest minne- og beregningsbruk.                                    | 40GB+      | Maksimal kvalitet; forskning; stort VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Merk:** Full finjustering (`train_full_finetuning.py`) kan kreve mer enn 64GB systemminne (RAM), og kan være uegnet for denne enheten. Vurder å bruke LoRA eller QLoRA i stedet.
<!-- @os:end -->

<!-- @os:windows -->
> **Merk:** Full finjustering (`train_full_finetuning.py`) kan kreve mer enn 64GB systemminne (RAM), og kan være uegnet for denne enheten. Vurder å bruke LoRA i stedet.
<!-- @os:end -->
<!-- @device:end -->

Velg ønsket `Training method`, last ned det tilhørende skriptet, og kjør det med kommandoen mens det virtuelle miljøet er aktivert: 

```python
python3 train_<method_name>.py.
```

## Bruke din finjusterte modell

### Etter full finjustering

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

### Etter LoRA/QLoRA-trening

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

### Slå sammen LoRA-adapter med basemodellen

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Merk:**  
- Sørg for at navnet på modellmappen (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) samsvarer med den faktiske utdatamappen fra treningen.  
- Hvis du brukte LoRA i stedet for QLoRA, erstatter du bare stien tilsvarende.  
- Enkelte Gemma-modeller krever at du angir `trust_remote_code=True` i `from_pretrained`; legg til dette hvis du ser en relatert advarsel.

For flere tilpassede innstillinger (padding-tokens, enhet osv.), se skriptet du brukte til trening.

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

## Tilpasningsveiledning

### Bruk ditt eget datasett

Alle skriptene bruker samme datasettformat. Erstatt lastedelen:

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

**Datasettformat for lokal JSON/JSONL-fil:**

Når du bruker denne metoden, må du sørge for at JSON-filene dine er riktig strukturert for å unngå tolkningsfeil. 

Følgende retningslinjer må følges:
* **Filformatering:** JSON-filer bør formateres i et integrert utviklingsmiljø (IDE) for å sikre riktig struktur og syntaks.
* **Nødvendige nøkler:** Den tilpassede JSON-filen må inneholde nøklene `instruction` og `response`. Disse nøklene er essensielle for at metoden skal fungere korrekt.
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
**Datasettformat for Hugging Face Hub-datasett**

Når du bruker datasett fra Hugging Face, må du sørge for at datasettene dine er riktig strukturert for å muliggjøre sømløs integrasjon. 

Følgende retningslinjer bør følges:
* **Instruksjon-svar-par:** Fokuser på datasett som inkluderer et `instruction-response`-par. Denne strukturen er essensiell for den tiltenkte funksjonaliteten.
* **Tilpasset nøkkelendring:** Hvis datasettet ditt ikke samsvarer med `instruction-response`-strukturen, har du muligheten til å endre `format_instruction()`-funksjonen. Dette lar deg tilpasse for spesifikke nøkler ved behov.

Eksempel på justering: I tilfeller der datasettets output må justeres, kan du endre svar-delen i format_instruction()-funksjonen for å tilpasse den til dine behov.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Datasettformat for CSV-fil**

For å tilpasse skriptet til bruk av CSV-filformat, må du sørge for at CSV-filen inneholder kolonner kalt `instruction` og `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Juster treningsparametere

Rediger treningsskriptet og endre variablene for å matche dine mål: **læringsrate** (`LR`), **epoker** (`EPOCHS`), **batchstørrelse** (`BATCH_SIZE`), **gradientakkumulering** (`GRAD_ACCUM_STEPS`), og for LoRA/QLoRA **rank** (`LORA_R`). For raskere kjøringer, bruk færre epoker og en høyere læringsrate (LR); for bedre kvalitet, bruk flere epoker og en lavere LR. Reduser batchstørrelse eller sekvenslengde hvis du får feil på grunn av manglende minne.
### Tips for minneoptimalisering

Hvis du støter på feil relatert til at minnet er fullt (out-of-memory):

**1. Reduser batch-størrelse:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Reduser sekvenslengde:**
```python
max_seq_length=256  # Instead of 512
```

**3. Bruk mer aggressiv kvantisering:**
```
Full → LoRA → QLoRA
```

**4. Aktiver Gradient Checkpointing (kun ved full finjustering):**
```python
model.gradient_checkpointing_enable()
```

---

## Overvåking og feilsøking

### Følg med på GPU-minne

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Valgfritt) Spor eksperimenter med Weights & Biases

For å logge kjøringer og metrikker til [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

I opplæringsskriptet setter du `report_to="wandb"` og eventuelt `run_name="your-experiment-name"` i trainer-konfigurasjonen. Hvis du foretrekker å ikke bruke Wandb, lar du `report_to` stå på standardverdien eller setter den til `"none"`.

### Vanlige problemer

#### Fullt minne (OOM)

**Løsning:** Reduser batch-størrelse og/eller bruk QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### Tapet (loss) reduseres ikke

**Løsning:** Juster læringsraten
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Treg opplæring

**Løsning:** Øk batch-størrelsen hvis minnet tillater det
```python
BATCH_SIZE = 8
```
## Neste steg

Etter at du har fullført vellykket finjustering, kan du vurdere følgende neste steg for å få mer ut av modellen din:

1. **Evaluer** grundig på tilbakeholdte testdata for å måle generalisering og unngå overtilpasning.
2. **Eksperimenter** ved å prøve ulike verdier for hyperparametere for bedre nøyaktighet, hastighet og minnebruk.
3. **Spor** alle eksperimentene dine (og tilhørende metrikker) med Weights & Biases for reproduserbar forskning.
4. **Prøv** å trene på dine egne tilpassede datasett for å tilpasse modellen spesifikt til ditt bruksområde.
5. **Distribuer** den finjusterte modellen din for rask inferens ved hjelp av effektive backend-løsninger som vLLM på kompatibel maskinvare.
6. **Utforsk** avanserte teknikker, inkludert prompt engineering, blandet presisjon og lengre sekvenslengder.
7. **Tren** flere LoRA-adaptere for ulike oppgaver eller domener, og bytt mellom dem etter behov.

---