<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Machinevertaling.** Deze pagina is automatisch vertaald vanuit het Engels en is niet door een mens gecontroleerd. Deze pagina kan fouten bevatten en bepaalde instructies, opdrachten, downloads, productbeschikbaarheid of andere inhoud kan per taal of regio verschillen. In geval van tegenstrijdigheid of discrepantie is de oorspronkelijke Engelse versie van de playbook doorslaggevend en prevaleert deze.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Overzicht

Deze tutorial biedt stapsgewijze voorbeelden voor het fine-tunen van een large language model (LLM) met PyTorch en ROCm. Het behandelt verschillende technieken, van standaard fine-tuning tot geheugenefficiënte Parameter-Efficient Fine-Tuning (PEFT)-strategieën, zodat u modellen eenvoudig kunt aanpassen aan uw behoeften.

**Gebruikt model**: google/gemma-3-4b-it  *(zie [HF-authenticatie inschakelen](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) indien afgeschermd)*  
**Hardware**: AMD Radeon™ GPU met ROCm-ondersteuning  
**Framework**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Opmerking:** 
> - Volledige fine-tuning vereist ten minste **64 GB systeem-RAM**, waarvan ten minste **32 GB beschikbaar moet zijn voor de GPU** (de 32 GB maakt deel uit van de 64 GB, niet daar bovenop).
> - U kunt ook andere modelarchitecturen proberen, waaronder **GPT-OSS-20B**, door het model in de meegeleverde trainingsscripts te vervangen.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **Opmerking:** LoRA- en QLoRA-fine-tuning vereisen ten minste **32 GB systeem-RAM**, waarvan ten minste **16 GB beschikbaar moet zijn voor de GPU** (de 16 GB maakt deel uit van de 32 GB, niet daar bovenop).
<!-- @os:end -->

<!-- @os:windows -->
> **Opmerking:** LoRA-fine-tuning vereist ten minste **32 GB systeem-RAM**, waarvan ten minste **16 GB beschikbaar moet zijn voor de GPU** (de 16 GB maakt deel uit van de 32 GB, niet daar bovenop).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Opmerking:** LoRA- en QLoRA-fine-tuning vereisen een grafische kaart met ten minste **16 GB toegewezen GPU-geheugen** en **32 GB systeem-RAM**.
> - Op Linux verloopt training volledig in het toegewezen VRAM van de grafische kaart.
> - Er wordt niet teruggevallen op gedeeld GPU-geheugen (systeem-RAM) wanneer het VRAM opraakt.
> - Kaarten met minder dan 16 GB toegewezen VRAM krijgen tijdens training op Linux een tekort aan geheugen, zelfs als het systeem voldoende RAM heeft.
<!-- @os:end -->

<!-- @os:windows -->
> **Opmerking:** LoRA-fine-tuning vereist ten minste **16 GB totaal GPU-geheugen** en **32 GB systeem-RAM**.
> - Op Windows combineert het totale GPU-geheugen het toegewezen VRAM van de grafische kaart met gedeeld GPU-geheugen (geleend van systeem-RAM).
> - Kaarten met minder dan 16 GB toegewezen VRAM kunnen deze playbook daarom nog steeds uitvoeren door gedeeld GPU-geheugen te gebruiken om het verschil aan te vullen.
<!-- @os:end -->
<!-- @device:end -->

## Wat u zult leren

- Hoe u een LLM fine-tunet met LoRA, QLoRA en volledige fine-tuning met PyTorch en ROCm
- Hoe u uw fine-getunede model opslaat en implementeert
- Hoe u training monitort en veelvoorkomende problemen debugt

## De geheugenconfiguratie instellen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Controleren op software-updates
> **Opmerking**: Als VS Code niet is geïnstalleerd, kunt u het installeren met Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Softwarevereisten installeren

#### Een virtuele omgeving maken

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
**Geef uw gebruiker toegang tot GPU-apparaten** (log uit en weer in om dit van kracht te laten worden):

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
**Windows:** Hier worden alleen de kernpakketten getest en ondersteund. **bitsandbytes wordt niet goed ondersteund op Windows**, dus de Windows-installatie laat het weg; gebruik LoRA of volledige fine-tuning op Windows (QLoRA vereist bitsandbytes en is bedoeld voor Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### HF-authenticatie inschakelen (afgeschermde of aangepaste / niet-vooraf geïnstalleerde modellen)

In dit voorbeeld gebruiken we **google/gemma-3-4b-it**, wat een **afgeschermd** model is. U moet de voorwaarden van het model op Hugging Face accepteren en vervolgens authenticeren, zodat de trainingsscripts het kunnen downloaden.

1. **Accepteer de licentie:** Open [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), meld u aan (of maak een account aan), en accepteer de licentie/voorwaarden op de modelpagina (bijv. “Agree and access repository”).
2. **Installeren en inloggen:** Installeer de Hugging Face CLI en voer vervolgens de standaard login uit:

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

- **Het kernidee**: in plaats van een enorme gewichtsmatrix met miljoenen parameters bij te werken, leren we een low-rank update (twee kleine matrices waarvan het product veel minder parameters heeft). Dat levert een grote vermindering op van trainbare parameters en VRAM, terwijl het grootste deel van de kwaliteit van volledige fine-tuning behouden blijft.

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

**QLoRA** combineert **4-bit-kwantisatie** met **LoRA**. Het basismodel wordt geladen in 4-bit (grote geheugenbesparing), en alleen de LoRA-adapters worden getraind met hogere precisie. Zo krijgt u de parameterefficiëntie van LoRA plus veel lager VRAM-gebruik, met een kleine kwaliteitsafweging ten opzichte van full-precision LoRA. Let op dat 4-bit-kwantisatie numerieke instabiliteiten kan veroorzaken (loss spikes of NaN's), waardoor gebruikers vaak de voorkeur geven aan **LoRA** als er voldoende VRAM beschikbaar is.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Opmerking**: Voor MXFP4-basismodellen zoals `openai/gpt-oss-20b` raden we aan om **LoRA** (`train_lora.py`) te gebruiken in plaats van QLoRA. Het 4-bit-pad van `bitsandbytes` in het QLoRA-script dekwantiseert MXFP4-gewichten doorgaans naar BF16, waardoor de run zich gedraagt als standaard LoRA. Native MXFP4 vereist `bitsandbytes` gebouwd vanuit de broncode plus een bijpassende Transformers/Triton/kernels-stack. Zie de [Transformers MXFP4-documentatie](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. Kies Uw Methode

| Methode | Geheugen | Snelheid | Kwaliteit | Beste Voor |
|--------|--------|-------|---------|----------|
| **QLoRA** (alleen Linux) | 12-16GB | Snelst | 90-95% | Laag Geheugengebruik |
| **LoRA** | 24-32GB | Snel | 95-98% | Gebalanceerde aanpak |
| **Full** | 80GB+ | Traagst | 100% | Maximale kwaliteit |

### 3. Training Uitvoeren

**Dataset en wat het model leert**  
De scripts zetten de dataset om in chatvoorbeelden. Zo gebruikt het QLoRA-script bijvoorbeeld **Abirate/english_quotes**: elk voorbeeld wordt een gebruiker-assistent paar zoals:

- **Gebruiker:** “Geef me een citaat over: &lt;tag&gt;”
- **Assistent:** “&lt;citaat&gt; – &lt;auteur&gt;”

Fine-tuning leert het model te reageren op prompts die vragen om citaten over een onderwerp en deze terug te geven in het formaat `<quote text> - <author>`. De LoRA- en full fine-tuning-scripts gebruiken **databricks/databricks-dolly-15k** (algemene instructie/antwoord-paren), dus de exacte taak verschilt per script; het idee is hetzelfde - pas het model aan op uw gekozen dataset en formaat.

Hieronder vindt u een overzicht van de beschikbare trainingsmethoden. Elke methode verwijst naar het bijbehorende script en bevat een korte beschrijving om u te helpen de juiste aanpak te kiezen.

| Script                           | Methode            | Beschrijving                                                                                                         | Typisch VRAM | Aanbevolen Voor                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Traint kleine adaptermatrices terwijl het basismodel bevroren blijft. 3-5x sneller; ~95-98% volledige kwaliteit.                         | 24–32GB      | Gevorderde gebruikers; meerdere adapters; meer VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(alleen Linux)*             | **QLoRA**       | 4-bit kwantisatie + LoRA-adapters. Laagste geheugengebruik, snelst, kleine kwaliteitsafweging. Vereist `bitsandbytes` (alleen Linux).                            | 12–16GB      | De meeste gebruikers; snelle experimenten; beperkt VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Full Fine-tuning** | Werkt alle modelparameters bij. Maximale kwaliteit; hoogste geheugen- en rekengebruik.                                    | 40GB+        | Maximale kwaliteit; onderzoek; groot VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Opmerking:** Full fine-tuning (`train_full_finetuning.py`) kan meer dan 64GB systeem-RAM vereisen en is mogelijk niet haalbaar op dit apparaat. Overweeg in plaats daarvan LoRA of QLoRA te gebruiken.
<!-- @os:end -->

<!-- @os:windows -->
> **Opmerking:** Full fine-tuning (`train_full_finetuning.py`) kan meer dan 64GB systeem-RAM vereisen en is mogelijk niet haalbaar op dit apparaat. Overweeg in plaats daarvan LoRA te gebruiken.
<!-- @os:end -->
<!-- @device:end -->

Selecteer eenvoudig uw gewenste `Training method`, download het bijbehorende script en voer het uit met het commando terwijl uw virtuele omgeving actief blijft: 

```python
python3 train_<method_name>.py.
```

## Uw Fine-Getunede Model Gebruiken

### Na Volledige Fine-Tuning

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

### Na LoRA/QLoRA Training

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

### LoRA-Adapter Samenvoegen met Basismodel

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Opmerking:**  
- Zorg ervoor dat de naam van de modelmap (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) overeenkomt met uw daadwerkelijke uitvoermap van de training.  
- Als u LoRA in plaats van QLoRA hebt gebruikt, vervangt u het pad dienovereenkomstig.  
- Sommige Gemma-modellen vereisen het specificeren van `trust_remote_code=True` in `from_pretrained`; voeg dit toe als u een gerelateerde waarschuwing ziet.

Raadpleeg voor meer aangepaste instellingen (padding-tokens, apparaat, enz.) het script dat u voor de training heeft gebruikt.

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

### Uw Eigen Dataset Gebruiken

Alle scripts gebruiken hetzelfde datasetformaat. Vervang het ladingsgedeelte:

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

**Datasetformaat voor Lokaal JSON/JSONL-bestand:**

Zorg er bij het gebruik van deze methode voor dat uw JSON-bestanden correct gestructureerd zijn om parseerfouten te voorkomen. 

De volgende richtlijnen moeten worden nageleefd:
* **Bestandsindeling:** JSON-bestanden moeten worden opgemaakt binnen een geïntegreerde ontwikkelomgeving (IDE) om een juiste structuur en syntaxis te garanderen.
* **Vereiste Sleutels:** Het aangepaste JSON-bestand moet de sleutels `instruction` en `response` bevatten. Deze sleutels zijn essentieel om de methode correct te laten functioneren.
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

Zorg er bij het gebruik van datasets van Hugging Face voor dat uw datasets correct gestructureerd zijn om een naadloze integratie mogelijk te maken. 

De volgende richtlijnen moeten worden gevolgd:
* **Instructie-Antwoord Paar:** Focus op datasets die een `instruction-response` paar bevatten. Deze structuur is essentieel voor de beoogde functionaliteit.
* **Aangepaste Sleutelwijziging:** Als uw dataset niet voldoet aan de `instruction-response` structuur, heeft u de mogelijkheid om de functie `format_instruction()` aan te passen. Hiermee kunt u specifieke sleutels naar wens gebruiken.

Voorbeeldaanpassing: In gevallen waarin de uitvoer van de dataset moet worden aangepast, kunt u het antwoordgedeelte binnen de functie format_instruction() wijzigen om aan uw vereisten te voldoen.
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

Om het script te kunnen gebruiken met een CSV-bestandsformaat, moet u ervoor zorgen dat het CSV-bestand kolommen bevat met de namen `instruction` en `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Trainingsparameters Aanpassen

Bewerk het trainingsscript en wijzig de variabelen om aan uw doelen te voldoen: **leersnelheid** (`LR`), **epochs** (`EPOCHS`), **batchgrootte** (`BATCH_SIZE`), **gradiëntaccumulatie** (`GRAD_ACCUM_STEPS`), en voor LoRA/QLoRA **rang** (`LORA_R`). Gebruik voor snellere runs minder epochs en een hogere leersnelheid (LR); gebruik voor een betere kwaliteit meer epochs en een lagere LR. Verminder de batchgrootte of sequentielengte als u foutmeldingen over onvoldoende geheugen tegenkomt.
### Tips voor geheugenoptimalisatie

Als u out-of-memory-fouten tegenkomt:

**1. Verklein de batchgrootte:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Verklein de sequentielengte:**
```python
max_seq_length=256  # Instead of 512
```

**3. Gebruik een agressievere kwantisatie:**
```
Full → LoRA → QLoRA
```

**4. Schakel Gradient Checkpointing in (alleen bij volledige fine-tuning):**
```python
model.gradient_checkpointing_enable()
```

---

## Monitoring & Debuggen

### GPU-geheugen in de gaten houden

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Optioneel) Experimenten bijhouden met Weights & Biases

Om runs en metrieken te loggen naar [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

Stel in het trainingsscript `report_to="wandb"` in en optioneel `run_name="your-experiment-name"` in de trainer-configuratie. Als u liever geen Wandb gebruikt, laat `report_to` dan op de standaardwaarde staan of stel deze in op `"none"`.

### Veelvoorkomende problemen

#### Out of Memory (OOM)

**Oplossing:** Verklein de batchgrootte en/of gebruik QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### Loss neemt niet af

**Oplossing:** Pas de leersnelheid aan
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Langzame training

**Oplossing:** Vergroot de batchgrootte als het geheugen dit toelaat
```python
BATCH_SIZE = 8
```
## Volgende stappen

Nadat u succesvol een fine-tuning heeft voltooid, kunt u de volgende stappen overwegen om meer uit uw model te halen:

1. **Evalueer** grondig op achtergehouden testdata om generalisatie te meten en overfitting te voorkomen.
2. **Experimenteer** door verschillende hyperparameterwaarden te proberen voor een betere balans tussen nauwkeurigheid, snelheid en geheugengebruik.
3. **Houd** al uw experimenten (en bijbehorende metrieken) bij met Weights & Biases voor reproduceerbaar onderzoek.
4. **Probeer** te trainen op uw eigen aangepaste datasets om het model specifiek af te stemmen op uw use-case.
5. **Implementeer** uw gefinetunede model voor snelle inferentie met efficiënte backends zoals vLLM op compatibele hardware.
6. **Verken** geavanceerde technieken zoals prompt engineering, mixed precision en langere sequentielengtes.
7. **Train** meerdere LoRA-adapters voor verschillende taken of domeinen en wissel ze naar behoefte.

---