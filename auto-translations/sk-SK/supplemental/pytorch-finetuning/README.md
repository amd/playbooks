<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Prehľad

Tento návod poskytuje postupné príklady doladenia veľkého jazykového modelu (LLM) pomocou PyTorch a ROCm. Zahŕňa niekoľko techník, od štandardného doladenia až po pamäťovo efektívne stratégie Parameter-Efficient Fine-Tuning (PEFT), vďaka ktorým môžete modely jednoducho prispôsobiť svojim potrebám.

**Použitý model**: google/gemma-3-4b-it (QLoRA skript: openai/gpt-oss-20b)  *(pozrite si [Povolenie overenia HF](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models), ak je model chránený)*  
**Hardvér**: GPU AMD Radeon™ s podporou ROCm  
**Framework**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Poznámka:** 
> - Úplné doladenie vyžaduje aspoň **64 GB systémovej RAM**, pričom aspoň **32 GB z nej musí byť dostupných pre GPU** (týchto 32 GB je súčasťou 64 GB, nie navyše).
> - Môžete tiež vyskúšať iné architektúry modelov, vrátane **GPT-OSS-20B**, nahradením modelu v poskytnutých trénovacích skriptoch.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **Poznámka:** Doladenie pomocou LoRA a QLoRA vyžaduje aspoň **32 GB systémovej RAM**, pričom aspoň **16 GB z nej musí byť dostupných pre GPU** (týchto 16 GB je súčasťou 32 GB, nie navyše).
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka:** Doladenie pomocou LoRA vyžaduje aspoň **32 GB systémovej RAM**, pričom aspoň **16 GB z nej musí byť dostupných pre GPU** (týchto 16 GB je súčasťou 32 GB, nie navyše).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Poznámka:** Doladenie pomocou LoRA a QLoRA vyžaduje grafickú kartu s aspoň **16 GB vyhradenej GPU pamäte** a **32 GB systémovej RAM**.
> - V systéme Linux prebieha trénovanie výlučne vo vyhradenej VRAM grafickej karty.
> - Nevracia sa k zdieľanej GPU pamäti (systémovej RAM), ak dôjde VRAM.
> - Kartám s menej ako 16 GB vyhradenej VRAM dôjde pamäť počas trénovania na Linuxe, aj keď má systém dostatok RAM.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka:** Doladenie pomocou LoRA vyžaduje aspoň **16 GB celkovej GPU pamäte** a **32 GB systémovej RAM**.
> - V systéme Windows celková GPU pamäť kombinuje vyhradenú VRAM grafickej karty so zdieľanou GPU pamäťou (vypožičanou zo systémovej RAM).
> - Preto karty s menej ako 16 GB vyhradenej VRAM môžu stále spustiť tento postup pomocou zdieľanej GPU pamäte na doplnenie rozdielu.
<!-- @os:end -->
<!-- @device:end -->

## Čo sa naučíte

- Ako doladiť LLM pomocou LoRA, QLoRA a úplného doladenia s PyTorch a ROCm
- Ako uložiť a nasadiť svoj doladený model
- Ako sledovať trénovanie a riešiť bežné problémy

<!-- @device:halo_box,halo,stx,krk -->
## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Kontrola aktualizácií softvéru
> **Poznámka**: Ak nemáte nainštalovaný VS Code, môžete ho nainštalovať pomocou Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Inštalácia softvérových predpokladov

#### Vytvorenie virtuálneho prostredia

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
**Udeľte svojmu používateľovi prístup k zariadeniam GPU** (pre uplatnenie zmeny sa odhláste a znova prihláste):

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

#### Inštalácia základných závislostí
<!-- @require:pytorch -->

#### Ďalšie závislosti

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Tu sú testované a podporované iba základné balíky. **bitsandbytes nie je na Windows dobre podporovaný**, takže inštalácia pre Windows ho vynecháva; na Windows použite LoRA alebo úplné doladenie (QLoRA vyžaduje bitsandbytes a je určená pre Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### Povolenie overenia HF (chránené alebo vlastné / nepreinštalované modely)

V tomto príklade používame **google/gemma-3-4b-it**, čo je **chránený (gated)** model. Musíte prijať podmienky modelu na Hugging Face a potom sa overiť, aby si ho trénovacie skripty mohli stiahnuť.

1. **Prijatie licencie:** Otvorte [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), prihláste sa (alebo si vytvorte účet) a prijmite licenciu/podmienky na stránke modelu (napr. „Agree and access repository“).
2. **Inštalácia a prihlásenie:** Nainštalujte Hugging Face CLI a potom spustite štandardné prihlásenie:

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

## Pochopenie techník

### Čo je LoRA?

**LoRA (Low-Rank Adaptation)** ponecháva základný model zamrznutý a trénuje iba malé „adaptérové“ matice, ktoré sa pridávajú do určitých vrstiev. 

- **Kľúčová myšlienka**: namiesto aktualizácie obrovskej váhovej matice s miliónmi parametrov sa naučíme nízkohodnostnú aktualizáciu (dve malé matice, ktorých súčin má oveľa menej parametrov). To výrazne znižuje počet trénovateľných parametrov a spotrebu VRAM pri zachovaní väčšiny kvality úplného doladenia.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### Čo je QLoRA?

**QLoRA** kombinuje **4-bitovú kvantizáciu** s **LoRA**. Základný model sa načíta v 4-bitovom formáte (veľká úspora pamäte) a iba adaptéry LoRA sa trénujú vo vyššej presnosti. Získate tak efektivitu parametrov LoRA plus oveľa nižšiu spotrebu VRAM, s miernym kompromisom v kvalite v porovnaní s plnopresnou LoRA. Majte na pamäti, že 4-bitová kvantizácia môže spôsobiť numerickú nestabilitu (skoky v strate alebo hodnoty NaN), takže používatelia často uprednostňujú **LoRA**, ak je k dispozícii dostatok VRAM.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Poznámka**: Pre základné modely MXFP4, ako napríklad `openai/gpt-oss-20b`, odporúčame namiesto QLoRA použiť **LoRA** (`train_lora.py`). 4-bitová cesta `bitsandbytes` v QLoRA skripte zvyčajne dekvantizuje váhy MXFP4 na BF16, takže beh sa správa ako štandardná LoRA. Natívna podpora MXFP4 vyžaduje `bitsandbytes` zostavené zo zdrojového kódu spolu so zodpovedajúcim zásobníkom Transformers/Triton/kernels. Pozrite si [dokumentáciu Transformers MXFP4](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. Vyberte si metódu

| Metóda | Pamäť | Rýchlosť | Kvalita | Najvhodnejšie pre |
|--------|--------|-------|---------|----------|
| **QLoRA** (iba Linux) | 12-16GB | Najrýchlejšie | 90-95% | Nízke využitie pamäte |
| **LoRA** | 24-32GB | Rýchle | 95-98% | Vyvážený prístup |
| **Full** | 80GB+ | Najpomalšie | 100% | Maximálna kvalita |

### 3. Spustite trénovanie

**Dataset a čo sa model naučí**  
Skripty premieňajú dataset na príklady konverzácie. Napríklad skript QLoRA používa **Abirate/english_quotes**: každý príklad sa stáva dvojicou user–assistant, napríklad:

- **User:** „Daj mi citát o: &lt;tag&gt;“
- **Assistant:** „&lt;quote&gt; – &lt;author&gt;“

Fine-tuning naučí model reagovať na výzvy žiadajúce citáty na danú tému a vracať ich vo formáte `<quote text> - <author>`. Skripty LoRA a full fine-tuning používajú **databricks/databricks-dolly-15k** (všeobecné dvojice inštrukcia/odpoveď), takže presná úloha sa líši podľa skriptu; myšlienka je rovnaká - prispôsobiť model vášmu zvolenému datasetu a formátu.

Nižšie je súhrn dostupných metód trénovania. Každá metóda odkazuje na svoj skript a poskytuje stručný popis na výber správneho prístupu.

| Skript                           | Metóda            | Popis                                                                                                         | Typická VRAM | Odporúčané pre                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Trénuje malé adaptérové matice pri zmrazení základného modelu. 3–5x rýchlejšie; ~95–98% plnej kvality.                         | 24–32GB      | Pokročilí používatelia; viacero adaptérov; viac VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(iba Linux)*             | **QLoRA**       | 4-bitová kvantizácia + adaptéry LoRA. Najnižšie využitie pamäte, najrýchlejšie, mierny kompromis v kvalite. Vyžaduje `bitsandbytes` (iba Linux).                            | 12–16GB      | Väčšina používateľov; rýchle experimenty; obmedzená VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Full Fine-tuning** | Aktualizuje všetky parametre modelu. Maximálna kvalita; najvyššie využitie pamäte a výpočtu.                                    | 40GB+        | Maximálna kvalita; výskum; veľká VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Poznámka:** Full fine-tuning (`train_full_finetuning.py`) môže vyžadovať viac ako 64GB systémovej RAM a nemusí byť na tomto zariadení realizovateľný. Zvážte namiesto toho použitie LoRA alebo QLoRA.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka:** Full fine-tuning (`train_full_finetuning.py`) môže vyžadovať viac ako 64GB systémovej RAM a nemusí byť na tomto zariadení realizovateľný. Zvážte namiesto toho použitie LoRA.
<!-- @os:end -->
<!-- @device:end -->

Jednoducho si vyberte požadovanú `Training method`, stiahnite si príslušný skript a spustite ho pomocou príkazu pri aktivovanom virtuálnom prostredí: 

```python
python3 train_<method_name>.py.
```

## Používanie vášho doladeného modelu

### Po Full Fine-Tuning

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

### Po tréningu LoRA/QLoRA

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

### Zlúčenie adaptéra LoRA do základného modelu

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Poznámka:**  
- Uistite sa, že názov adresára modelu (`output-gemma-3-4b-it-full`, `output-gpt-oss-20b-qlora`) zodpovedá vášmu skutočnému výstupnému priečinku z trénovania.  
- Ak ste namiesto QLoRA použili LoRA, jednoducho príslušne nahraďte cestu.  
- Niektoré modely Gemma vyžadujú uvedenie `trust_remote_code=True` v `from_pretrained`; pridajte, ak uvidíte súvisiace upozornenie.

Pre ďalšie vlastné nastavenia (padding tokeny, zariadenie atď.), odkazujte sa na skript, ktorý ste použili na trénovanie.

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

## Sprievodca prispôsobením

### Použitie vlastného datasetu

Všetky skripty používajú rovnaký formát datasetu. Nahraďte sekciu načítavania:

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

**Formát datasetu pre lokálny súbor JSON/JSONL:**

Pri použití tejto metódy sa uistite, že vaše súbory JSON sú správne štruktúrované, aby sa predišlo chybám pri parsovaní. 

Je potrebné dodržať nasledujúce pokyny:
* **Formátovanie súborov:** Súbory JSON by mali byť formátované v rámci Integrovaného vývojového prostredia (IDE), aby sa zabezpečila správna štruktúra a syntax.
* **Povinné kľúče:** Vlastný súbor JSON musí obsahovať kľúče `instruction` a `response`. Tieto kľúče sú nevyhnutné pre správne fungovanie metódy.
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
**Formát datasetu pre dataset z Hugging Face Hub**

Pri používaní datasetov z Hugging Face sa uistite, že vaše datasety sú správne štruktúrované, aby ste umožnili bezproblémovú integráciu. 

Mali by sa dodržiavať nasledujúce pokyny:
* **Dvojica inštrukcia-odpoveď:** Zamerajte sa na datasety, ktoré obsahujú dvojicu `instruction-response`. Táto štruktúra je nevyhnutná pre zamýšľanú funkcionalitu.
* **Úprava vlastného kľúča:** Ak váš dataset nezodpovedá štruktúre `instruction-response`, máte možnosť upraviť funkciu `format_instruction()`. To vám umožňuje prispôsobiť sa konkrétnym kľúčom podľa potreby.

Príklad úpravy: V prípadoch, keď je potrebné upraviť výstup datasetu, môžete upraviť sekciu odpovede vo funkcii format_instruction() tak, aby vyhovovala vašim požiadavkám.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Formát datasetu pre súbor CSV**

Aby bol skript kompatibilný s formátom súboru CSV, musíte zabezpečiť, že súbor CSV obsahuje stĺpce s názvom `instruction` a `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Úprava parametrov trénovania

Upravte trénovací skript a zmeňte premenné tak, aby zodpovedali vašim cieľom: **learning rate** (`LR`), **počet epoch** (`EPOCHS`), **veľkosť batchu** (`BATCH_SIZE`), **akumulácia gradientu** (`GRAD_ACCUM_STEPS`) a pre LoRA/QLoRA **rank** (`LORA_R`). Pre rýchlejšie behy použite menej epoch a vyšší learning rate (LR); pre lepšiu kvalitu použite viac epoch a nižší LR. Znížte veľkosť batchu alebo dĺžku sekvencie, ak narazíte na chyby nedostatku pamäte.
### Tipy na optimalizáciu pamäte

Ak narazíte na chyby nedostatku pamäte:

**1. Zmenšite veľkosť dávky (batch size):**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Skráťte dĺžku sekvencie:**
```python
max_seq_length=256  # Instead of 512
```

**3. Použite agresívnejšiu kvantizáciu:**
```
Full → LoRA → QLoRA
```

**4. Povoľte Gradient Checkpointing (len pri úplnom doladení):**
```python
model.gradient_checkpointing_enable()
```

---

## Monitorovanie a ladenie

### Sledovanie pamäte GPU

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Voliteľné) Sledovanie experimentov pomocou Weights & Biases

Ak chcete logovať behy a metriky do [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

V tréningovom skripte nastavte `report_to="wandb"` a voliteľne `run_name="your-experiment-name"` v konfigurácii trénera. Ak nechcete používať Wandb, ponechajte `report_to` na predvolenej hodnote alebo ho nastavte na `"none"`.

### Bežné problémy

#### Nedostatok pamäte (OOM)

**Riešenie:** Zmenšite veľkosť dávky a/alebo použite QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### Strata sa nezmenšuje

**Riešenie:** Upravte mieru učenia (learning rate)
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Pomalý tréning

**Riešenie:** Zväčšite veľkosť dávky, ak to pamäť umožňuje
```python
BATCH_SIZE = 8
```
## Ďalšie kroky

Po úspešnom doladení zvážte nasledujúce kroky, aby ste zo svojho modelu vyťažili čo najviac:

1. **Vyhodnoťte** dôkladne model na vyhradených testovacích dátach, aby ste zmerali schopnosť generalizácie a predišli preučeniu (overfitting).
2. **Experimentujte** so skúšaním rôznych hodnôt hyperparametrov pre lepší pomer presnosti, rýchlosti a pamäťových nárokov.
3. **Sledujte** všetky svoje experimenty (a zodpovedajúce metriky) pomocou Weights & Biases pre reprodukovateľný výskum.
4. **Vyskúšajte** tréning na vlastných dátových sadách, aby ste model prispôsobili presne vášmu prípadu použitia.
5. **Nasaďte** svoj doladený model na rýchlu inferenciu pomocou efektívnych backendov, ako je vLLM, na kompatibilnom hardvéri.
6. **Preskúmajte** pokročilé techniky vrátane prompt engineeringu, zmiešanej presnosti (mixed precision) a dlhších dĺžok sekvencií.
7. **Natrénujte** viacero LoRA adaptérov pre rôzne úlohy alebo domény a podľa potreby ich vymieňajte.

---