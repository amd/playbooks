<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Prehľad

Tento tutoriál poskytuje podrobné príklady doladenia veľkého jazykového modelu (LLM) pomocou PyTorch a ROCm. Pokrýva niekoľko techník, od štandardného doladenia až po pamäťovo efektívne stratégie Parameter-Efficient Fine-Tuning (PEFT), aby ste mohli jednoducho prispôsobiť modely svojim potrebám.

**Použitý model**: google/gemma-3-4b-it  *(pozri [Povolenie HF autentifikácie](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) ak je model chránený)*  
**Hardvér**: AMD Radeon™ GPU s podporou ROCm  
**Framework**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Poznámka:** Môžete tiež vyskúšať iné architektúry modelov, vrátane **GPT-OSS-20B**, nahradením modelu v poskytnutých trénovacích skriptoch.
> Úplné doladenie vyžaduje aspoň 32 GB pamäte GPU a 64 GB systémovej RAM.
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> **Poznámka:** Doladenie pomocou LoRA a QLoRA vyžaduje aspoň 16 GB pamäte GPU a 32 GB systémovej RAM.
<!-- @device:end -->

## Čo sa naučíte

- Ako doladiť LLM pomocou LoRA, QLoRA a úplného doladenia s PyTorch a ROCm
- Ako uložiť a nasadiť váš doladený model
- Ako monitorovať trénovanie a ladiť bežné problémy

## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizácií softvéru
> **Poznámka**: Ak VS Code nie je nainštalovaný, môžete ho nainštalovať pomocou Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Inštalácia softvérových predpokladov

#### Vytvorenie virtuálneho prostredia

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
**Udeľte svojmu používateľovi prístup k zariadeniam GPU** (odhláste sa a znova prihláste, aby sa zmena prejavila):

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

#### Inštalácia základných závislostí
<!-- @require:pytorch -->

#### Ďalšie závislosti

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Tu sú testované a podporované iba základné balíky. **bitsandbytes nie je dobre podporovaný na Windows**, preto inštalácia pre Windows ho vynecháva; na Windows používajte LoRA alebo úplné doladenie (QLoRA vyžaduje bitsandbytes a je určené pre Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### Povolenie HF autentifikácie (chránené alebo vlastné / vopred nenainštalované modely)

V tomto príklade používame **google/gemma-3-4b-it**, čo je **chránený** model. Musíte prijať podmienky modelu na Hugging Face a následne sa autentifikovať, aby trénovacie skripty mohli model stiahnuť.

1. **Prijmite licenciu:** Otvorte [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), prihláste sa (alebo si vytvorte účet) a prijmite licenciu/podmienky na stránke modelu (napr. „Agree and access repository").
2. **Nainštalujte a prihláste sa:** Nainštalujte Hugging Face CLI a potom spustite štandardné prihlásenie:

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

**LoRA (Low-Rank Adaptation)** ponecháva základný model zmrazený a trénuje iba malé „adaptérové" matice, ktoré sa pridávajú k určitým vrstvám.

- **Kľúčová myšlienka**: namiesto aktualizácie obrovskej váhovej matice s miliónmi parametrov sa naučíme nízkohodnostovú aktualizáciu (dve malé matice, ktorých súčin má oveľa menej parametrov). To prináša výrazné zníženie trénovateľných parametrov a VRAM pri zachovaní väčšiny kvality úplného doladenia.

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

**QLoRA** kombinuje **4-bitovú kvantizáciu** s **LoRA**. Základný model sa načíta v 4-bitoch (výrazná úspora pamäte) a iba LoRA adaptéry sa trénujú vo vyššej presnosti. Získate tak parametrickú efektívnosť LoRA plus oveľa nižšiu VRAM, s malým kompromisom v kvalite v porovnaní s LoRA v plnej presnosti. Upozorňujeme, že 4-bitová kvantizácia môže spôsobiť numerické nestability (skoky straty alebo NaN), preto používatelia môžu uprednostniť **LoRA**, ak je k dispozícii dostatok VRAM.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Poznámka**: Pre základné modely MXFP4 ako `openai/gpt-oss-20b` odporúčame používať **LoRA** (`train_lora.py`) namiesto QLoRA. Cesta `bitsandbytes` 4-bit v skripte QLoRA zvyčajne dekvantizuje váhy MXFP4 na BF16, takže beh sa správa ako štandardná LoRA. Natívny MXFP4 vyžaduje `bitsandbytes` zostavený zo zdrojového kódu plus zodpovedajúci zásobník Transformers/Triton/kernels. Pozri [dokumentáciu Transformers MXFP4](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---

### 2. Vyberte svoju metódu

| Metóda | Pamäť | Rýchlosť | Kvalita | Najvhodnejšie pre |
|--------|--------|-------|---------|----------|
| **QLoRA** (iba Linux) | 12–16 GB | Najrýchlejšia | 90–95 % | Nízke využitie pamäte |
| **LoRA** | 24–32 GB | Rýchla | 95–98 % | Vyvážený prístup |
| **Úplné** | 80 GB+ | Najpomalšia | 100 % | Maximálna kvalita |

### 3. Spustite trénovanie

**Datasety a čo sa model naučí**  
Skripty transformujú dataset na chatové príklady. Napríklad skript QLoRA používa **Abirate/english_quotes**: každý príklad sa stane párom používateľ–asistent ako:

- **Používateľ:** „Daj mi citát o: &lt;tag&gt;"
- **Asistent:** „&lt;quote&gt; – &lt;author&gt;"

Doladenie naučí model reagovať na výzvy žiadajúce citáty o téme a vracať ich vo formáte `<quote text> - <author>`. Skripty LoRA a úplného doladenia používajú **databricks/databricks-dolly-15k** (všeobecné páry inštrukcia/odpoveď), takže presná úloha sa líši podľa skriptu; myšlienka je rovnaká – prispôsobiť model vášmu zvolenému datasetu a formátu.

Nižšie je zhrnutie dostupných metód trénovania. Každá metóda odkazuje na svoj skript a poskytuje stručný popis pre výber správneho prístupu.

| Skript                           | Metóda            | Popis                                                                                                         | Typická VRAM | Odporúčané pre                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Trénuje malé adaptérové matice pri zmrazení základného modelu. 3–5× rýchlejšie; ~95–98 % plnej kvality.                         | 24–32 GB      | Pokročilí používatelia; viacero adaptérov; viac VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(iba Linux)*             | **QLoRA**       | 4-bitová kvantizácia + LoRA adaptéry. Najnižšie využitie pamäte, najrýchlejšia, malý kompromis v kvalite. Vyžaduje `bitsandbytes` (iba Linux).                            | 12–16 GB      | Väčšina používateľov; rýchle experimenty; obmedzená VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Úplné doladenie** | Aktualizuje všetky parametre modelu. Maximálna kvalita; najvyššie využitie pamäte a výpočtového výkonu.                                    | 40 GB+        | Maximálna kvalita; výskum; veľká VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Poznámka:** Úplné doladenie (`train_full_finetuning.py`) môže vyžadovať viac ako 64 GB systémovej RAM a nemusí byť na tomto zariadení realizovateľné. Zvážte použitie LoRA alebo QLoRA.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka:** Úplné doladenie (`train_full_finetuning.py`) môže vyžadovať viac ako 64 GB systémovej RAM a nemusí byť na tomto zariadení realizovateľné. Zvážte použitie LoRA.
<!-- @os:end -->
<!-- @device:end -->

Jednoducho vyberte preferovanú `Metódu trénovania`, stiahnite zodpovedajúci skript a spustite ho pomocou príkazu pri aktívnom virtuálnom prostredí:

```python
python3 train_<method_name>.py.
```

## Používanie vášho doladeného modelu

### Po úplnom doladení

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

### Po trénovaní LoRA/QLoRA

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

### Zlúčenie LoRA adaptéra so základným modelom

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Poznámka:**  
- Uistite sa, že názov adresára modelu (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) zodpovedá vášmu skutočnému výstupnému priečinku z trénovania.  
- Ak ste použili LoRA namiesto QLoRA, jednoducho nahraďte cestu zodpovedajúcim spôsobom.  
- Niektoré modely Gemma vyžadujú zadanie `trust_remote_code=True` v `from_pretrained`; pridajte, ak uvidíte súvisiace upozornenie.

Pre ďalšie vlastné nastavenia (tokeny výplne, zariadenie atď.) si pozrite skript, ktorý ste použili na trénovanie.

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

## Sprievodca prispôsobením

### Použite vlastný dataset

Všetky skripty používajú rovnaký formát datasetu. Nahraďte sekciu načítania:

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

Pri použití tejto metódy sa uistite, že vaše súbory JSON sú správne štruktúrované, aby ste predišli chybám pri parsovaní.

Je potrebné dodržiavať nasledujúce pokyny:
* **Formátovanie súboru:** Súbory JSON by mali byť formátované v integrovanom vývojovom prostredí (IDE), aby sa zabezpečila správna štruktúra a syntax.
* **Požadované kľúče:** Vlastný súbor JSON musí obsahovať kľúče `instruction` a `response`. Tieto kľúče sú nevyhnutné pre správne fungovanie metódy.
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

Pri využívaní datasetov z Hugging Face sa uistite, že vaše datasety sú správne štruktúrované pre bezproblémovú integráciu.

Je potrebné dodržiavať nasledujúce pokyny:
* **Pár inštrukcia-odpoveď:** Zamerajte sa na datasety, ktoré obsahujú pár `instruction-response`. Táto štruktúra je nevyhnutná pre zamýšľanú funkčnosť.
* **Úprava vlastných kľúčov:** Ak váš dataset nezodpovedá štruktúre `instruction-response`, máte možnosť upraviť funkciu `format_instruction()`. To vám umožní podľa potreby prispôsobiť konkrétne kľúče.

Príklad úpravy: V prípadoch, keď je potrebné upraviť výstup datasetu, môžete upraviť sekciu odpovede vo funkcii format_instruction() podľa svojich požiadaviek.
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

Aby skript mohol pracovať so súborom vo formáte CSV, musíte zabezpečiť, že súbor CSV obsahuje stĺpce s názvami `instruction` a `response`.
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Úprava parametrov trénovania

Upravte trénovací skript a zmeňte premenné podľa svojich cieľov: **rýchlosť učenia** (`LR`), **epochy** (`EPOCHS`), **veľkosť dávky** (`BATCH_SIZE`), **akumulácia gradientov** (`GRAD_ACCUM_STEPS`) a pre LoRA/QLoRA **rank** (`LORA_R`). Pre rýchlejšie behy použite menej epoch a vyššiu rýchlosť učenia (LR); pre lepšiu kvalitu použite viac epoch a nižšiu LR. Znížte veľkosť dávky alebo dĺžku sekvencie, ak narazíte na chyby nedostatku pamäte.

### Tipy na optimalizáciu pamäte

Ak narazíte na chyby nedostatku pamäte:

**1. Znížte veľkosť dávky:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Znížte dĺžku sekvencie:**
```python
max_seq_length=256  # Instead of 512
```

**3. Použite agresívnejšiu kvantizáciu:**
```
Full → LoRA → QLoRA
```

**4. Povoľte kontrolné body gradientov (iba úplné doladenie):**
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

Na zaznamenávanie behov a metrík do [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

V trénovacom skripte nastavte `report_to="wandb"` a voliteľne `run_name="your-experiment-name"` v konfigurácii trénera. Ak nechcete používať Wandb, ponechajte `report_to` na predvolenej hodnote alebo nastavte na `"none"`.

### Bežné problémy

#### Nedostatok pamäte (OOM)

**Riešenie:** Znížte veľkosť dávky a/alebo použite QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### Strata sa neznižuje

**Riešenie:** Upravte rýchlosť učenia
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Pomalé trénovanie

**Riešenie:** Zvýšte veľkosť dávky, ak to pamäť dovoľuje
```python
BATCH_SIZE = 8
```
## Ďalšie kroky

Po úspešnom dokončení doladenia zvážte nasledujúce kroky, aby ste zo svojho modelu vyťažili viac:

1. **Vyhodnoťte** dôkladne na odložených testovacích dátach, aby ste zmerali generalizáciu a predišli pretrénovaniu.
2. **Experimentujte** skúšaním rôznych hodnôt hyperparametrov pre lepšiu presnosť, rýchlosť a kompromisy v pamäti.
3. **Sledujte** všetky svoje experimenty (a zodpovedajúce metriky) pomocou Weights & Biases pre reprodukovateľný výskum.
4. **Vyskúšajte** trénovanie na vlastných datasetoch, aby ste model prispôsobili konkrétne pre váš prípad použitia.
5. **Nasaďte** váš doladený model pre rýchlu inferenciu pomocou efektívnych backendov, ako je vLLM na kompatibilnom hardvéri.
6. **Preskúmajte** pokročilé techniky vrátane prompt engineeringu, zmiešanej presnosti a dlhších dĺžok sekvencií.
7. **Trénujte** viacero LoRA adaptérov pre rôzne úlohy alebo domény a podľa potreby ich vymieňajte.

---