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

Tento tutoriál poskytuje postupné příklady pro doladění (fine-tuning) velkého jazykového modelu (LLM) pomocí PyTorch a ROCm. Zahrnuje několik technik, od standardního doladění až po paměťově efektivní strategie Parameter-Efficient Fine-Tuning (PEFT), takže si model můžete snadno přizpůsobit svým potřebám.

**Použitý model**: google/gemma-3-4b-it (skript QLoRA: openai/gpt-oss-20b)  *(viz [Povolení autentizace HF](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models), pokud je model uzamčený (gated))*  
**Hardware**: GPU AMD Radeon™ s podporou ROCm  
**Framework**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Poznámka:** 
> - Úplné doladění (full fine-tuning) vyžaduje alespoň **64 GB systémové RAM**, z čehož alespoň **32 GB musí být dostupných pro GPU** (těchto 32 GB je součástí oněch 64 GB, nikoli navíc).
> - Můžete vyzkoušet i jiné architektury modelů, včetně **GPT-OSS-20B**, nahrazením modelu v poskytnutých trénovacích skriptech.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **Poznámka:** Doladění pomocí LoRA a QLoRA vyžaduje alespoň **32 GB systémové RAM**, z čehož alespoň **16 GB musí být dostupných pro GPU** (těchto 16 GB je součástí oněch 32 GB, nikoli navíc).
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka:** Doladění pomocí LoRA vyžaduje alespoň **32 GB systémové RAM**, z čehož alespoň **16 GB musí být dostupných pro GPU** (těchto 16 GB je součástí oněch 32 GB, nikoli navíc).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Poznámka:** Doladění pomocí LoRA a QLoRA vyžaduje grafickou kartu s alespoň **16 GB vyhrazené paměti GPU** a **32 GB systémové RAM**.
> - V systému Linux probíhá trénování výhradně ve vyhrazené paměti VRAM grafické karty.
> - Při vyčerpání VRAM nedochází k přepnutí na sdílenou paměť GPU (systémovou RAM).
> - Kartám s méně než 16 GB vyhrazené VRAM dojde při trénování v systému Linux paměť, i když má systém dostatek RAM.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka:** Doladění pomocí LoRA vyžaduje alespoň **16 GB celkové paměti GPU** a **32 GB systémové RAM**.
> - V systému Windows kombinuje celková paměť GPU vyhrazenou VRAM grafické karty se sdílenou pamětí GPU (vypůjčenou ze systémové RAM).
> - Proto mohou tento postup (playbook) spustit i karty s méně než 16 GB vyhrazené VRAM, díky využití sdílené paměti GPU k doplnění rozdílu.
<!-- @os:end -->
<!-- @device:end -->

## Co se naučíte

- Jak doladit LLM pomocí LoRA, QLoRA a úplného doladění s PyTorch a ROCm
- Jak uložit a nasadit doladěný model
- Jak sledovat průběh trénování a řešit běžné problémy

<!-- @device:halo_box,halo,stx,krk -->
## Nastavení konfigurace paměti

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru
> **Poznámka**: Pokud není nainstalován VS Code, můžete jej nainstalovat pomocí Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace požadovaného softwaru

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
**Udělte svému uživateli přístup k zařízením GPU** (aby se změna projevila, odhlaste se a znovu přihlaste):

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
**Windows:** Zde jsou testovány a podporovány pouze základní balíčky. **bitsandbytes není na Windows dobře podporován**, proto instalace pro Windows tento balíček vynechává; na Windows použijte LoRA nebo úplné doladění (QLoRA vyžaduje bitsandbytes a je určena pro Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### Povolení autentizace HF (uzamčené nebo vlastní / nepředinstalované modely)

V tomto příkladu používáme **google/gemma-3-4b-it**, což je **uzamčený (gated)** model. Musíte přijmout podmínky modelu na Hugging Face a poté se autentizovat, aby trénovací skripty mohly model stáhnout.

1. **Přijetí licence:** Otevřete [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), přihlaste se (nebo si vytvořte účet) a přijměte licenci/podmínky na stránce modelu (např. „Agree and access repository“).
2. **Instalace a přihlášení:** Nainstalujte Hugging Face CLI a poté proveďte standardní přihlášení:

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

**LoRA (Low-Rank Adaptation)** ponechává základní model zamrzlý a trénuje pouze malé „adaptérové“ matice, které se přidávají k určitým vrstvám. 

- **Klíčová myšlenka**: místo aktualizace obrovské váhové matice s miliony parametrů se učíme aktualizaci s nízkou hodností (low-rank) (dvě malé matice, jejichž součin má mnohem méně parametrů). To přináší výrazné snížení počtu trénovatelných parametrů a nároků na VRAM při zachování většiny kvality úplného doladění.

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

**QLoRA** kombinuje **4bitovou kvantizaci** s **LoRA**. Základní model se načte ve 4bitové podobě (velká úspora paměti) a v přesnějším formátu se trénují pouze adaptéry LoRA. Získáte tak parametrovou efektivitu LoRA spolu s výrazně nižšími nároky na VRAM, za cenu mírného kompromisu v kvalitě oproti plně přesné LoRA. Upozorňujeme, že 4bitová kvantizace může způsobit numerickou nestabilitu (skoky ve ztrátové funkci nebo hodnoty NaN), takže uživatelé mohou často preferovat **LoRA**, pokud mají k dispozici dostatek VRAM.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Poznámka**: Pro základní modely MXFP4, jako je `openai/gpt-oss-20b`, doporučujeme místo QLoRA použít **LoRA** (`train_lora.py`). 4bitová cesta knihovny `bitsandbytes` ve skriptu QLoRA obvykle dekvantizuje váhy MXFP4 na BF16, takže běh se chová jako standardní LoRA. Nativní MXFP4 vyžaduje `bitsandbytes` sestavené ze zdrojového kódu spolu s odpovídající sadou Transformers/Triton/kernels. Viz [dokumentace Transformers MXFP4](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. Zvolte svoji metodu

| Metoda | Paměť | Rychlost | Kvalita | Nejlepší pro |
|--------|--------|-------|---------|----------|
| **QLoRA** (pouze Linux) | 12-16GB | Nejrychlejší | 90-95% | Nízké využití paměti |
| **LoRA** | 24-32GB | Rychlá | 95-98% | Vyvážený přístup |
| **Full** | 80GB+ | Nejpomalejší | 100% | Maximální kvalita |

### 3. Spusťte trénování

**Datová sada a co se model učí**  
Skripty převádějí datovou sadu na příklady konverzace. Například skript QLoRA používá **Abirate/english_quotes**: každý příklad se stane dvojicí uživatel–asistent, například:

- **Uživatel:** „Give me a quote about: &lt;tag&gt;“
- **Asistent:** „&lt;quote&gt; – &lt;author&gt;“

Doladění (fine-tuning) učí model reagovat na výzvy žádající citáty na určité téma a vracet je ve formátu `<quote text> - <author>`. Skripty pro LoRA a plné doladění používají **databricks/databricks-dolly-15k** (obecné dvojice instrukce/odpověď), takže konkrétní úkol se u jednotlivých skriptů liší; princip je však stejný – přizpůsobit model vámi zvolené datové sadě a formátu.

Níže je uveden přehled dostupných metod trénování. Každá metoda odkazuje na svůj skript a obsahuje stručný popis, který vám pomůže zvolit správný přístup.

| Skript                           | Metoda            | Popis                                                                                                         | Typické VRAM | Doporučeno pro                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Trénuje malé adaptérové matice, přičemž základní model zůstává zmrazený. 3–5× rychlejší; ~95–98 % plné kvality.                         | 24–32GB      | Pokročilí uživatelé; více adaptérů; více VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(pouze Linux)*             | **QLoRA**       | 4bitová kvantizace + adaptéry LoRA. Nejnižší využití paměti, nejrychlejší, mírný kompromis v kvalitě. Vyžaduje `bitsandbytes` (pouze Linux).                            | 12–16GB      | Většina uživatelů; rychlé experimenty; omezené VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Plné doladění (Full Fine-tuning)** | Aktualizuje všechny parametry modelu. Maximální kvalita; nejvyšší nároky na paměť a výpočetní výkon.                                    | 40GB+        | Maximální kvalita; výzkum; velké množství VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Poznámka:** Plné doladění (`train_full_finetuning.py`) může vyžadovat více než 64GB systémové RAM a na tomto zařízení nemusí být proveditelné. Zvažte místo toho použití LoRA nebo QLoRA.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka:** Plné doladění (`train_full_finetuning.py`) může vyžadovat více než 64GB systémové RAM a na tomto zařízení nemusí být proveditelné. Zvažte místo toho použití LoRA.
<!-- @os:end -->
<!-- @device:end -->

Jednoduše vyberte preferovanou `Training method`, stáhněte si odpovídající skript a spusťte jej pomocí příkazu – přičemž vaše virtuální prostředí musí zůstat aktivováno: 

```python
python3 train_<method_name>.py.
```

## Použití vašeho doladěného modelu

### Po plném doladění (Full Fine-Tuning)

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

### Po trénování pomocí LoRA/QLoRA

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
- Ujistěte se, že název adresáře modelu (`output-gemma-3-4b-it-full`, `output-gpt-oss-20b-qlora`) odpovídá vaší skutečné výstupní složce z trénování.  
- Pokud jste místo QLoRA použili LoRA, stačí odpovídajícím způsobem nahradit cestu.  
- Některé modely Gemma vyžadují zadání `trust_remote_code=True` v `from_pretrained`; přidejte toto nastavení, pokud se zobrazí související upozornění.

Další vlastní nastavení (tokeny pro doplnění, zařízení atd.) naleznete ve skriptu, který jste použili pro trénování.

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

### Použití vlastní datové sady

Všechny skripty používají stejný formát datové sady. Nahraďte sekci načítání:

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

**Formát datové sady pro lokální soubor JSON/JSONL:**

Při použití této metody se ujistěte, že vaše soubory JSON mají správnou strukturu, aby nedošlo k chybám při zpracování. 

Je nutné dodržet následující pokyny:
* **Formátování souborů:** Soubory JSON by měly být formátovány v integrovaném vývojovém prostředí (IDE), aby byla zajištěna správná struktura a syntaxe.
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
**Formát datové sady pro datovou sadu z Hugging Face Hub**

Při použití datových sad z Hugging Face se ujistěte, že vaše datové sady mají správnou strukturu, která umožní bezproblémovou integraci. 

Je třeba dodržovat následující pokyny:
* **Dvojice instrukce–odpověď:** Zaměřte se na datové sady, které obsahují dvojici `instruction-response`. Tato struktura je nezbytná pro zamýšlenou funkčnost.
* **Úprava vlastních klíčů:** Pokud vaše datová sada neodpovídá struktuře `instruction-response`, máte možnost upravit funkci `format_instruction()`. To vám umožní přizpůsobit se specifickým klíčům podle potřeby.

Příklad úpravy: V případech, kdy je potřeba upravit výstup datové sady, můžete upravit sekci odpovědi ve funkci format_instruction() tak, aby vyhovovala vašim požadavkům.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Formát datové sady pro soubor CSV**

Aby bylo možné skript použít se souborem ve formátu CSV, musíte zajistit, že soubor CSV obsahuje sloupce nazvané `instruction` a `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Úprava parametrů trénování

Upravte skript pro trénování a změňte proměnné tak, aby odpovídaly vašim cílům: **rychlost učení** (`LR`), **epochy** (`EPOCHS`), **velikost dávky** (`BATCH_SIZE`), **akumulace gradientu** (`GRAD_ACCUM_STEPS`) a u LoRA/QLoRA **hodnost** (`LORA_R`). Pro rychlejší běh použijte méně epoch a vyšší rychlost učení (LR); pro lepší kvalitu použijte více epoch a nižší LR. Pokud narazíte na chyby způsobené nedostatkem paměti, zmenšete velikost dávky nebo délku sekvence.
### Tipy pro optimalizaci paměti

Pokud se setkáte s chybami týkajícími se nedostatku paměti:

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

**4. Povolte Gradient Checkpointing (pouze pro úplné doladění):**
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

Chcete-li zaznamenávat průběhy a metriky do [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

Ve skriptu pro trénování nastavte `report_to="wandb"` a volitelně `run_name="your-experiment-name"` v konfiguraci traineru. Pokud nechcete používat Wandb, ponechte `report_to` na výchozí hodnotě nebo jej nastavte na `"none"`.

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

**Řešení:** Pokud to paměť umožňuje, zvyšte velikost dávky
```python
BATCH_SIZE = 8
```
## Další kroky

Po úspěšném dokončení doladění zvažte následující další kroky, abyste ze svého modelu vytěžili co nejvíce:

1. **Vyhodnoťte** důkladně na vyhrazených testovacích datech, abyste změřili generalizaci a předešli přetrénování.
2. **Experimentujte** s různými hodnotami hyperparametrů pro lepší kompromisy mezi přesností, rychlostí a pamětí.
3. **Sledujte** všechny své experimenty (a odpovídající metriky) pomocí Weights & Biases pro reprodukovatelný výzkum.
4. **Vyzkoušejte** trénování na vlastních datových sadách, abyste model přizpůsobili přesně svému případu užití.
5. **Nasaďte** svůj doladěný model pro rychlou inferenci pomocí efektivních backendů, jako je vLLM, na kompatibilním hardwaru.
6. **Prozkoumejte** pokročilé techniky, včetně prompt engineeringu, smíšené přesnosti a delších délek sekvencí.
7. **Natrénujte** více LoRA adaptérů pro různé úlohy nebo domény a podle potřeby je zaměňujte.

---