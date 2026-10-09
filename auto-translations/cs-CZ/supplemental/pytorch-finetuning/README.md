<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Přehled

Tento tutoriál poskytuje postupné příklady pro doladění (fine-tuning) velkého jazykového modelu (LLM) pomocí PyTorch a ROCm. Zahrnuje několik technik, od standardního doladění až po paměťově efektivní strategie parametricky efektivního doladění (PEFT), abyste mohli modely snadno přizpůsobit svým potřebám.

**Použitý model**: google/gemma-3-4b-it (skript QLoRA: openai/gpt-oss-20b)  *(viz [Povolení autentizace HF](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models), pokud je model uzamčený)*  
**Hardware**: GPU AMD Radeon™ s podporou ROCm  
**Framework**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Poznámka:** 
> - Úplné doladění vyžaduje nejméně **64 GB systémové paměti RAM**, přičemž alespoň **32 GB z toho musí být dostupných pro GPU** (těchto 32 GB je součástí 64 GB, nikoli navíc).
> - Můžete také vyzkoušet jiné architektury modelů, včetně **GPT-OSS-20B**, nahrazením modelu v poskytnutých tréninkových skriptech.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **Poznámka:** Doladění pomocí LoRA a QLoRA vyžaduje nejméně **32 GB systémové paměti RAM**, přičemž alespoň **16 GB z toho musí být dostupných pro GPU** (těchto 16 GB je součástí 32 GB, nikoli navíc).
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka:** Doladění pomocí LoRA vyžaduje nejméně **32 GB systémové paměti RAM**, přičemž alespoň **16 GB z toho musí být dostupných pro GPU** (těchto 16 GB je součástí 32 GB, nikoli navíc).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Poznámka:** Doladění pomocí LoRA a QLoRA vyžaduje grafickou kartu s alespoň **16 GB vyhrazené paměti GPU** a **32 GB systémové paměti RAM**.
> - V systému Linux probíhá trénink zcela ve vyhrazené paměti VRAM grafické karty.
> - Pokud dojde VRAM, systém se nepřepne na sdílenou paměť GPU (systémovou RAM).
> - Kartám s méně než 16 GB vyhrazené VRAM dojde během tréninku v systému Linux paměť, i když má systém dostatek RAM.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka:** Doladění pomocí LoRA vyžaduje nejméně **16 GB celkové paměti GPU** a **32 GB systémové paměti RAM**.
> - V systému Windows kombinuje celková paměť GPU vyhrazenou VRAM grafické karty se sdílenou pamětí GPU (vypůjčenou ze systémové RAM).
> - Proto mohou tento playbook spustit i karty s méně než 16 GB vyhrazené VRAM, a to pomocí sdílené paměti GPU, která rozdíl doplní.
<!-- @os:end -->
<!-- @device:end -->

## Co se naučíte

- Jak doladit LLM pomocí LoRA, QLoRA a úplného doladění s PyTorch a ROCm
- Jak uložit a nasadit doladěný model
- Jak sledovat trénink a řešit běžné problémy

<!-- @device:halo_box,halo,stx,krk -->
## Nastavení konfigurace paměti

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru
> **Poznámka**: Pokud není nainstalován VS Code, můžete ho nainstalovat pomocí Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace softwarových předpokladů

<!-- @prereq:hf-models-gemma-3-4b-it,hf-datasets-databricks-dolly-15k -->
<!-- @os:linux -->
<!-- @prereq:hf-datasets-english-quotes -->
<!-- @os:end -->

#### Vytvoření virtuálního prostředí

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
**Udělte svému uživateli přístup k zařízením GPU** (aby se projevil, je nutné se odhlásit a znovu přihlásit):

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

#### Instalace základních závislostí
<!-- @require:pytorch -->

#### Další závislosti

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Zde jsou testovány a podporovány pouze základní balíčky. **bitsandbytes není na Windows dobře podporován**, takže instalace pro Windows ho vynechává; na Windows použijte LoRA nebo úplné doladění (QLoRA vyžaduje bitsandbytes a je určeno pro Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### Povolení autentizace HF (uzamčené nebo vlastní / nepředinstalované modely)

V tomto příkladu používáme **google/gemma-3-4b-it**, což je **uzamčený (gated)** model. Je nutné přijmout podmínky modelu na Hugging Face a poté se autentizovat, aby si ho tréninkové skripty mohly stáhnout.

1. **Přijměte licenci:** Otevřete [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), přihlaste se (nebo si vytvořte účet) a na stránce modelu přijměte licenci/podmínky (např. „Agree and access repository“).
2. **Nainstalujte a přihlaste se:** Nainstalujte Hugging Face CLI a poté spusťte standardní přihlášení:

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

## Pochopení technik

### Co je LoRA?

**LoRA (Low-Rank Adaptation)** ponechává základní model zmrazený a trénuje pouze malé „adaptérové“ matice, které se přidávají k určitým vrstvám. 

- **Klíčová myšlenka**: místo aktualizace obrovské váhové matice s miliony parametrů se naučíme nízkoranková aktualizace (dvě malé matice, jejichž součin má mnohem méně parametrů). To přináší výrazné snížení počtu trénovatelných parametrů a nároků na VRAM, přičemž je zachována většina kvality úplného doladění.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### Co je QLoRA?

**QLoRA** kombinuje **4bitovou kvantizaci** s **LoRA**. Základní model je načten ve 4bitovém formátu (velká úspora paměti) a trénují se pouze adaptéry LoRA s vyšší přesností. Získáte tak parametrickou efektivitu LoRA spolu s mnohem nižšími nároky na VRAM, za cenu mírného kompromisu v kvalitě oproti LoRA s plnou přesností. Všimněte si, že 4bitová kvantizace může způsobovat numerickou nestabilitu (výkyvy ztrátové funkce nebo hodnoty NaN), takže uživatelé mohou často preferovat **LoRA**, pokud je k dispozici dostatek VRAM.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Poznámka**: Pro základní modely MXFP4, jako je `openai/gpt-oss-20b`, doporučujeme místo QLoRA používat **LoRA** (`train_lora.py`). 4bitová cesta `bitsandbytes` ve skriptu QLoRA obvykle dekvantizuje váhy MXFP4 do formátu BF16, takže se běh chová jako standardní LoRA. Nativní podpora MXFP4 vyžaduje `bitsandbytes` sestavený ze zdrojového kódu spolu s odpovídající sadou Transformers/Triton/kernels. Viz [dokumentace Transformers MXFP4](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. Zvolte svou metodu

| Metoda | Paměť | Rychlost | Kvalita | Nejlepší pro |
|--------|--------|-------|---------|----------|
| **QLoRA** (pouze Linux) | 12–16 GB | Nejrychlejší | 90–95 % | Nízké využití paměti |
| **LoRA** | 24–32 GB | Rychlá | 95–98 % | Vyvážený přístup |
| **Full** | 80 GB+ | Nejpomalejší | 100 % | Maximální kvalita |

### 3. Spusťte trénování

**Dataset a co se model učí**  
Skripty převádějí dataset na chatové příklady. Například skript QLoRA používá **Abirate/english_quotes**: každý příklad se stane dvojicí uživatel–asistent, například:

- **Uživatel:** „Dej mi citát na téma: &lt;tag&gt;“
- **Asistent:** „&lt;citát&gt; – &lt;autor&gt;“

Doladění (fine-tuning) učí model reagovat na výzvy žádající citáty na dané téma a vracet je ve formátu `<text citátu> - <autor>`. Skripty pro LoRA a plné doladění používají **databricks/databricks-dolly-15k** (obecné dvojice instrukce/odpověď), takže konkrétní úloha se podle skriptu liší; princip je ale stejný – přizpůsobit model vašemu zvolenému datasetu a formátu.

Níže je přehled dostupných metod trénování. Každá metoda odkazuje na svůj skript a obsahuje stručný popis pro výběr správného přístupu.

| Skript                           | Metoda            | Popis                                                                                                         | Typická VRAM | Doporučeno pro                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Trénuje malé adaptérové matice při zmrazeném základním modelu. 3–5× rychlejší; ~95–98 % plné kvality.                         | 24–32 GB      | Pokročilí uživatelé; více adaptérů; více VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(pouze Linux)*             | **QLoRA**       | 4bitová kvantizace + adaptéry LoRA. Nejnižší spotřeba paměti, nejrychlejší, mírný kompromis v kvalitě. Vyžaduje `bitsandbytes` (pouze Linux).                            | 12–16 GB      | Většina uživatelů; rychlé experimenty; omezená VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Plné doladění (Full Fine-tuning)** | Aktualizuje všechny parametry modelu. Maximální kvalita; nejvyšší nároky na paměť a výpočet.                                    | 40 GB+        | Maximální kvalita; výzkum; velká VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Poznámka:** Plné doladění (`train_full_finetuning.py`) může vyžadovat více než 64 GB systémové RAM a na tomto zařízení nemusí být proveditelné. Zvažte místo toho použití LoRA nebo QLoRA.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka:** Plné doladění (`train_full_finetuning.py`) může vyžadovat více než 64 GB systémové RAM a na tomto zařízení nemusí být proveditelné. Zvažte místo toho použití LoRA.
<!-- @os:end -->
<!-- @device:end -->

Jednoduše vyberte preferovanou `Training method`, stáhněte si odpovídající skript a spusťte jej pomocí příkazu, přičemž ponechte aktivované virtuální prostředí: 

```python
python3 train_<method_name>.py.
```

## Používání doladěného modelu

### Po plném doladění

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

### Po trénování LoRA/QLoRA

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

### Sloučení adaptéru LoRA do základního modelu

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Poznámka:**  
- Ujistěte se, že název adresáře modelu (`output-gemma-3-4b-it-full`, `output-gpt-oss-20b-qlora`) odpovídá skutečné výstupní složce z trénování.  
- Pokud jste místo QLoRA použili LoRA, stačí odpovídajícím způsobem upravit cestu.  
- Některé modely Gemma vyžadují zadání `trust_remote_code=True` v `from_pretrained`; přidejte jej, pokud se zobrazí související varování.

Pro další vlastní nastavení (padding tokeny, zařízení atd.) nahlédněte do skriptu, který jste použili pro trénování.

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

## Průvodce přizpůsobením

### Použití vlastního datasetu

Všechny skripty používají stejný formát datasetu. Nahraďte sekci načítání:

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

**Formát datasetu pro lokální soubor JSON/JSONL:**

Při použití této metody se ujistěte, že vaše soubory JSON mají správnou strukturu, aby se předešlo chybám při analýze. 

Je nutné dodržet následující pokyny:
* **Formátování souboru:** Soubory JSON by měly být formátovány v integrovaném vývojovém prostředí (IDE), aby byla zajištěna správná struktura a syntaxe.
* **Povinné klíče:** Vlastní soubor JSON musí obsahovat klíče `instruction` a `response`. Tyto klíče jsou nezbytné pro správné fungování metody.
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
**Formát datasetu pro dataset z Hugging Face Hub**

Při použití datasetů z Hugging Face se ujistěte, že jsou vaše datasety správně strukturované, aby byla zajištěna bezproblémová integrace. 

Je třeba dodržovat následující pokyny:
* **Dvojice instrukce–odpověď:** Zaměřte se na datasety, které obsahují dvojici `instruction-response`. Tato struktura je nezbytná pro zamýšlenou funkčnost.
* **Úprava vlastních klíčů:** Pokud váš dataset neodpovídá struktuře `instruction-response`, můžete upravit funkci `format_instruction()`. To vám umožní přizpůsobit se konkrétním klíčům podle potřeby.

Příklad úpravy: V případech, kdy je potřeba upravit výstup datasetu, můžete upravit sekci response ve funkci format_instruction() tak, aby odpovídala vašim požadavkům.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Formát datasetu pro soubor CSV**

Aby skript mohl pracovat se souborem ve formátu CSV, musíte zajistit, že soubor CSV obsahuje sloupce nazvané `instruction` a `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Úprava parametrů trénování

Upravte trénovací skript a změňte proměnné podle svých cílů: **rychlost učení** (`LR`), **epochy** (`EPOCHS`), **velikost dávky** (`BATCH_SIZE`), **akumulace gradientu** (`GRAD_ACCUM_STEPS`) a pro LoRA/QLoRA **rank** (`LORA_R`). Pro rychlejší běhy použijte méně epoch a vyšší rychlost učení (LR); pro lepší kvalitu použijte více epoch a nižší LR. Pokud narazíte na chyby z nedostatku paměti, snižte velikost dávky nebo délku sekvence.
### Tipy pro optimalizaci paměti

Pokud narazíte na chyby způsobené nedostatkem paměti:

**1. Snižte velikost dávky:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Zkraťte délku sekvence:**
```python
max_seq_length=256  # Instead of 512
```

**3. Použijte agresivnější kvantizaci:**
```
Full → LoRA → QLoRA
```

**4. Povolte Gradient Checkpointing (pouze pro Full fine-tuning):**
```python
model.gradient_checkpointing_enable()
```

---

## Monitorování a ladění

### Sledování paměti GPU

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Volitelné) Sledování experimentů pomocí Weights & Biases

Chcete-li zaznamenávat běhy a metriky do [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

Ve skriptu pro trénování nastavte `report_to="wandb"` a volitelně `run_name="your-experiment-name"` v konfiguraci traineru. Pokud nechcete používat Wandb, ponechte `report_to` na výchozí hodnotě nebo ji nastavte na `"none"`.

### Běžné problémy

#### Nedostatek paměti (OOM)

**Řešení:** Snižte velikost dávky a/nebo použijte QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### Ztráta se nesnižuje

**Řešení:** Upravte rychlost učení
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Pomalé trénování

**Řešení:** Zvyšte velikost dávky, pokud to paměť dovoluje
```python
BATCH_SIZE = 8
```
## Další kroky

Po úspěšném dokončení fine-tuningu zvažte následující další kroky, abyste ze svého modelu vytěžili co nejvíce:

1. **Vyhodnoťte** důkladně model na vyhrazených testovacích datech, abyste změřili schopnost generalizace a předešli přetrénování.
2. **Experimentujte** se zkoušením různých hodnot hyperparametrů pro lepší přesnost, rychlost a kompromisy v paměti.
3. **Sledujte** všechny své experimenty (a odpovídající metriky) pomocí Weights & Biases pro reprodukovatelný výzkum.
4. **Vyzkoušejte** trénování na vlastních datových sadách, abyste model přizpůsobili přesně svému případu použití.
5. **Nasaďte** svůj fine-tunovaný model pro rychlou inferenci pomocí efektivních backendů, jako je vLLM, na kompatibilním hardwaru.
6. **Prozkoumejte** pokročilé techniky, včetně prompt engineeringu, smíšené přesnosti a delších délek sekvencí.
7. **Natrénujte** více LoRA adaptérů pro různé úlohy nebo domény a podle potřeby je zaměňujte.

---