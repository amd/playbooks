<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Overzicht

Deze tutorial biedt stapsgewijze voorbeelden voor het fine-tunen van een groot taalmodel (LLM) met PyTorch en ROCm. Het behandelt verschillende technieken, van standaard fine-tuning tot geheugenefficiënte Parameter-Efficient Fine-Tuning (PEFT)-strategieën, zodat u modellen eenvoudig kunt aanpassen aan uw behoeften.

**Gebruikt model**: google/gemma-3-4b-it  *(zie [HF-authenticatie inschakelen](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) indien afgegrendeld)*  
**Hardware**: AMD Radeon™ GPU met ROCm-ondersteuning  
**Framework**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Opmerking:** U kunt ook andere modelarchitecturen uitproberen, waaronder **GPT-OSS-20B**, door het model in de meegeleverde trainingsscripts te vervangen.
> Volledige fine-tuning vereist minimaal 32 GB GPU-geheugen en 64 GB systeemgeheugen.
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> **Opmerking:** LoRA- en QLoRA-fine-tuning vereisen minimaal 16 GB GPU-geheugen en 32 GB systeemgeheugen.
<!-- @device:end -->

## Wat u leert

- Hoe u een LLM fine-tunet met LoRA, QLoRA en volledige fine-tuning met PyTorch en ROCm
- Hoe u uw fine-tuned model opslaat en implementeert
- Hoe u de training bewaakt en veelvoorkomende problemen oplost

## De geheugenconfiguratie instellen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Controleren op software-updates
> **Opmerking**: Als VS Code niet is geïnstalleerd, kunt u het installeren via het Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Software-vereisten installeren

#### Een virtuele omgeving aanmaken

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
**Verleen uw gebruiker toegang tot GPU-apparaten** (log uit en weer in om dit van kracht te laten worden):

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

#### Basisafhankelijkheden installeren
<!-- @require:pytorch -->

#### Aanvullende afhankelijkheden

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Hier worden alleen kernpakketten getest en ondersteund. **bitsandbytes wordt niet goed ondersteund op Windows**, dus de Windows-installatie laat het weg; gebruik LoRA of volledige fine-tuning op Windows (QLoRA vereist bitsandbytes en is bedoeld voor Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### HF-authenticatie inschakelen (afgegrendelde of aangepaste / niet-voorgeïnstalleerde modellen)

In dit voorbeeld gebruiken we **google/gemma-3-4b-it**, wat een **afgegrendeld** model is. U moet de modelvoorwaarden op Hugging Face accepteren en vervolgens authenticeren zodat de trainingsscripts het kunnen downloaden.

1. **Accepteer de licentie:** Open [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), meld u aan (of maak een account aan) en accepteer de licentie/voorwaarden op de modelpagina (bijv. "Agree and access repository").
2. **Installeer en log in:** Installeer de Hugging Face CLI en voer vervolgens de standaard aanmelding uit:

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

## De technieken begrijpen

### Wat is LoRA?

**LoRA (Low-Rank Adaptation)** houdt het basismodel bevroren en traint alleen kleine "adapter"-matrices die aan bepaalde lagen worden toegevoegd.

- **Het kernidee**: in plaats van een enorme gewichtsmatrix met miljoenen parameters bij te werken, leren we een laag-rang update (twee kleine matrices waarvan het product veel minder parameters heeft). Dit levert een grote vermindering van traineerbare parameters en VRAM op, terwijl het grootste deel van de kwaliteit van volledige fine-tuning behouden blijft.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### Wat is QLoRA?

**QLoRA** combineert **4-bit kwantisering** met **LoRA**. Het basismodel wordt geladen in 4-bit (grote geheugenbesparingen), en alleen de LoRA-adapters worden getraind in hogere precisie. U krijgt dus de parameterefficiëntie van LoRA plus een veel lager VRAM-gebruik, met een kleine kwaliteitsafweging ten opzichte van LoRA met volledige precisie. Merk op dat 4-bit kwantisering numerieke instabiliteiten kan veroorzaken (verliessprongen of NaN's), waardoor gebruikers vaak de voorkeur geven aan **LoRA** als er voldoende VRAM beschikbaar is.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Opmerking**: Voor MXFP4-basismodellen zoals `openai/gpt-oss-20b` raden we aan **LoRA** (`train_lora.py`) te gebruiken in plaats van QLoRA. Het `bitsandbytes` 4-bit pad van het QLoRA-script dequantiseert MXFP4-gewichten doorgaans naar BF16, waardoor de uitvoering zich gedraagt als standaard LoRA. Native MXFP4 vereist `bitsandbytes` gebouwd vanuit de broncode plus een bijpassende Transformers/Triton/kernels-stack. Zie de [Transformers MXFP4-documentatie](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---

### 2. Kies uw methode

| Methode | Geheugen | Snelheid | Kwaliteit | Het beste voor |
|--------|--------|-------|---------|----------|
| **QLoRA** (alleen Linux) | 12-16GB | Snelst | 90-95% | Laag geheugengebruik |
| **LoRA** | 24-32GB | Snel | 95-98% | Gebalanceerde aanpak |
| **Volledig** | 80GB+ | Langzaamst | 100% | Maximale kwaliteit |

### 3. Training uitvoeren

**Dataset en wat het model leert**  
De scripts zetten de dataset om in chatvoorbeelden. Het QLoRA-script gebruikt bijvoorbeeld **Abirate/english_quotes**: elk voorbeeld wordt een gebruiker-assistent-paar zoals:

- **Gebruiker:** "Geef me een citaat over: &lt;tag&gt;"
- **Assistent:** "&lt;quote&gt; – &lt;author&gt;"

Fine-tuning leert het model te reageren op prompts die vragen om citaten over een onderwerp en deze terug te geven in het formaat `<quote text> - <author>`. De LoRA- en volledige fine-tuning-scripts gebruiken **databricks/databricks-dolly-15k** (algemene instructie-/antwoordparen), dus de exacte taak varieert per script; het idee is hetzelfde: pas het model aan uw gekozen dataset en formaat aan.

Hieronder vindt u een overzicht van de beschikbare trainingsmethoden. Elke methode verwijst naar het bijbehorende script en geeft een korte beschrijving voor het kiezen van de juiste aanpak.

| Script                           | Methode            | Beschrijving                                                                                                         | Typisch VRAM | Aanbevolen voor                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Traint kleine adaptermatrices terwijl het basismodel bevroren blijft. 3–5x sneller; ~95–98% volledige kwaliteit.                         | 24–32GB      | Gevorderde gebruikers; meerdere adapters; meer VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(alleen Linux)*             | **QLoRA**       | 4-bit kwantisering + LoRA-adapters. Laagste geheugengebruik, snelst, kleine kwaliteitsafweging. Vereist `bitsandbytes` (alleen Linux).                            | 12–16GB      | De meeste gebruikers; snelle experimenten; beperkt VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Volledige fine-tuning** | Werkt alle modelparameters bij. Maximale kwaliteit; hoogste geheugen- en rekengebruik.                                    | 40GB+        | Maximale kwaliteit; onderzoek; groot VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Opmerking:** Volledige fine-tuning (`train_full_finetuning.py`) kan meer dan 64 GB systeemgeheugen vereisen en is mogelijk niet haalbaar op dit apparaat. Overweeg in plaats daarvan LoRA of QLoRA te gebruiken.
<!-- @os:end -->

<!-- @os:windows -->
> **Opmerking:** Volledige fine-tuning (`train_full_finetuning.py`) kan meer dan 64 GB systeemgeheugen vereisen en is mogelijk niet haalbaar op dit apparaat. Overweeg in plaats daarvan LoRA te gebruiken.
<!-- @os:end -->
<!-- @device:end -->

Selecteer eenvoudig uw gewenste `Trainingsmethode`, download het bijbehorende script en voer het uit met de opdracht terwijl uw virtuele omgeving geactiveerd is:

```python
python3 train_<method_name>.py.
```

## Uw fine-tuned model gebruiken

### Na volledige fine-tuning

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

### Na LoRA/QLoRA-training

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

### LoRA-adapter samenvoegen met het basismodel

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Opmerking:**  
- Zorg ervoor dat de naam van de modelmap (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) overeenkomt met uw werkelijke uitvoermap van de training.  
- Als u LoRA in plaats van QLoRA hebt gebruikt, vervangt u het pad dienovereenkomstig.  
- Sommige Gemma-modellen vereisen het opgeven van `trust_remote_code=True` in `from_pretrained`; voeg dit toe als u een gerelateerde waarschuwing ziet.

Voor meer aangepaste instellingen (opvultokens, apparaat, enz.) raadpleegt u het script dat u voor de training hebt gebruikt.

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

## Aanpassingsgids

### Uw eigen dataset gebruiken

Alle scripts gebruiken hetzelfde datasetformaat. Vervang het laadgedeelte:

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

**Datasetformaat voor lokaal JSON/JSONL-bestand:**

Wanneer u deze methode gebruikt, moet u ervoor zorgen dat uw JSON-bestanden correct zijn gestructureerd om parseerfouten te voorkomen.

De volgende richtlijnen moeten worden nageleefd:
* **Bestandsopmaak:** JSON-bestanden moeten worden opgemaakt binnen een Integrated Development Environment (IDE) om een correcte structuur en syntaxis te garanderen.
* **Vereiste sleutels:** Het aangepaste JSON-bestand moet de sleutels `instruction` en `response` bevatten. Deze sleutels zijn essentieel voor het correct functioneren van de methode.
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
**Datasetformaat voor Hugging Face Hub-dataset**

Wanneer u datasets van Hugging Face gebruikt, moet u ervoor zorgen dat uw datasets correct zijn gestructureerd voor een naadloze integratie.

De volgende richtlijnen dienen te worden gevolgd:
* **Instructie-antwoordpaar:** Richt u op datasets die een `instruction-response`-paar bevatten. Deze structuur is essentieel voor de beoogde functionaliteit.
* **Aanpassing van aangepaste sleutels:** Als uw dataset niet voldoet aan de `instruction-response`-structuur, kunt u de functie `format_instruction()` aanpassen. Hiermee kunt u specifieke sleutels naar behoefte accommoderen.

Voorbeeldaanpassing: In gevallen waarin de uitvoer van de dataset moet worden aangepast, kunt u het antwoordgedeelte binnen de functie format_instruction() aanpassen aan uw vereisten.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Datasetformaat voor CSV-bestand**

Om het script te laten werken met een CSV-bestandsformaat, moet u ervoor zorgen dat het CSV-bestand kolommen bevat met de namen `instruction` en `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Trainingsparameters aanpassen

Bewerk het trainingsscript en wijzig de variabelen zodat ze overeenkomen met uw doelen: **leersnelheid** (`LR`), **epochs** (`EPOCHS`), **batchgrootte** (`BATCH_SIZE`), **gradiëntaccumulatie** (`GRAD_ACCUM_STEPS`), en voor LoRA/QLoRA **rang** (`LORA_R`). Gebruik voor snellere uitvoeringen minder epochs en een hogere leersnelheid (LR); gebruik voor betere kwaliteit meer epochs en een lagere LR. Verklein de batchgrootte of sequentielengte als u geheugenfouten krijgt.

### Tips voor geheugenoptimalisatie

Als u geheugenfouten tegenkomt:

**1. Verklein de batchgrootte:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Verklein de sequentielengte:**
```python
max_seq_length=256  # Instead of 512
```

**3. Gebruik agressievere kwantisering:**
```
Full → LoRA → QLoRA
```

**4. Schakel gradiëntcontrolepunten in (alleen volledige fine-tuning):**
```python
model.gradient_checkpointing_enable()
```

---

## Bewaking en foutopsporing

### GPU-geheugen bewaken

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Optioneel) Experimenten bijhouden met Weights & Biases

Om uitvoeringen en statistieken te loggen naar [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

Stel in het trainingsscript `report_to="wandb"` in en optioneel `run_name="your-experiment-name"` in de trainerconfiguratie. Als u Wandb liever niet gebruikt, laat u `report_to` op de standaardwaarde staan of stelt u het in op `"none"`.

### Veelvoorkomende problemen

#### Onvoldoende geheugen (OOM)

**Oplossing:** Verklein de batchgrootte en/of gebruik QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### Verlies neemt niet af

**Oplossing:** Pas de leersnelheid aan
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Trage training

**Oplossing:** Vergroot de batchgrootte als het geheugen het toelaat
```python
BATCH_SIZE = 8
```
## Volgende stappen

Nadat u de fine-tuning succesvol hebt voltooid, kunt u de volgende stappen overwegen om meer uit uw model te halen:

1. **Evalueer** grondig op afgehouden testdata om generalisatie te meten en overfitting te voorkomen.
2. **Experimenteer** door verschillende hyperparameterwaarden uit te proberen voor betere nauwkeurigheid, snelheid en geheugenafwegingen.
3. **Volg** al uw experimenten (en bijbehorende statistieken) bij met Weights & Biases voor reproduceerbaar onderzoek.
4. **Probeer** te trainen op uw eigen aangepaste datasets om het model specifiek aan te passen voor uw gebruiksscenario.
5. **Implementeer** uw fine-tuned model voor snelle inferentie met behulp van efficiënte backends zoals vLLM op compatibele hardware.
6. **Verken** geavanceerde technieken, waaronder prompt engineering, gemengde precisie en langere sequentielengten.
7. **Train** meerdere LoRA-adapters voor verschillende taken of domeinen en wissel ze naar behoefte uit.

---