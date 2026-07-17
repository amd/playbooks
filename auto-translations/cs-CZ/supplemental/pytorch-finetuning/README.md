<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Přehled

Tento tutoriál poskytuje podrobné příklady pro doladění velkého jazykového modelu (LLM) pomocí PyTorch a ROCm. Zahrnuje několik technik, od standardního doladění po paměťově efektivní strategie Parameter-Efficient Fine-Tuning (PEFT), takže můžete snadno přizpůsobit modely svým potřebám.

**Použitý model**: google/gemma-3-4b-it  *(viz [Povolení HF autentizace](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) pro uzamčené modely)*  
**Hardware**: AMD Radeon™ GPU s podporou ROCm  
**Framework**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Poznámka:** Můžete také vyzkoušet jiné architektury modelů, včetně **GPT-OSS-20B**, nahrazením modelu v poskytnutých tréninkových skriptech.
> Plné doladění vyžaduje alespoň 32 GB paměti GPU a 64 GB systémové RAM.
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> **Poznámka:** Doladění pomocí LoRA a QLoRA vyžaduje alespoň 16 GB paměti GPU a 32 GB systémové RAM.
<!-- @device:end -->

## Co se naučíte

- Jak doladit LLM pomocí LoRA, QLoRA a plného doladění s PyTorch a ROCm
- Jak uložit a nasadit váš doladěný model
- Jak sledovat trénink a ladit běžné problémy

## Nastavení konfigurace paměti

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru
> **Poznámka**: Pokud VS Code není nainstalován, můžete ho nainstalovat pomocí Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace softwarových předpokladů

#### Vytvoření virtuálního prostředí

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
**Udělte svému uživateli přístup k zařízením GPU** (pro aktivaci se odhlaste a znovu přihlaste):

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

#### Instalace základních závislostí
<!-- @require:pytorch -->

#### Další závislosti

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Zde jsou testovány a podporovány pouze základní balíčky. **bitsandbytes není na Windows dobře podporován**, proto instalace pro Windows jej vynechává; na Windows používejte LoRA nebo plné doladění (QLoRA vyžaduje bitsandbytes a je určeno pro Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### Povolení HF autentizace (uzamčené nebo vlastní / nepředinstalované modely)

V tomto příkladu používáme **google/gemma-3-4b-it**, což je **uzamčený** model. Musíte přijmout podmínky modelu na Hugging Face a poté se autentizovat, aby tréninkové skripty mohly model stáhnout.

1. **Přijměte licenci:** Otevřete [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), přihlaste se (nebo si vytvořte účet) a přijměte licenci/podmínky na stránce modelu (např. „Agree and access repository").
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

**LoRA (Low-Rank Adaptation)** ponechává základní model zmrazený a trénuje pouze malé „adaptérové" matice, které se přidávají k určitým vrstvám.

- **Klíčová myšlenka**: místo aktualizace obrovské matice vah s miliony parametrů se naučíme nízkořadou aktualizaci (dvě malé matice, jejichž součin má mnohem méně parametrů). To přináší velké snížení trénovatelných parametrů a VRAM při zachování většiny kvality plného doladění.

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

**QLoRA** kombinuje **4-bitovou kvantizaci** s **LoRA**. Základní model je načten ve 4 bitech (velká úspora paměti) a pouze LoRA adaptéry jsou trénovány ve vyšší přesnosti. Získáte tak parametrickou efektivitu LoRA plus mnohem nižší VRAM, s malým kompromisem v kvalitě oproti LoRA v plné přesnosti. Upozorňujeme, že 4-bitová kvantizace může způsobit numerické nestability (skoky ve ztrátě nebo NaN), takže uživatelé mohou často preferovat **LoRA**, pokud je k dispozici dostatek VRAM.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Poznámka**: Pro základní modely MXFP4, jako je `openai/gpt-oss-20b`, doporučujeme používat **LoRA** (`train_lora.py`) místo QLoRA. Cesta `bitsandbytes` 4-bit ve skriptu QLoRA obvykle dekváantizuje váhy MXFP4 na BF16, takže běh se chová jako standardní LoRA. Nativní MXFP4 vyžaduje `bitsandbytes` sestavený ze zdrojového kódu plus odpovídající zásobník Transformers/Triton/kernels. Viz [dokumentace Transformers MXFP4](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---

### 2. Vyberte svou metodu

| Metoda | Paměť | Rychlost | Kvalita | Nejlepší pro |
|--------|--------|-------|---------|----------|
| **QLoRA** (pouze Linux) | 12–16 GB | Nejrychlejší | 90–95 % | Nízká spotřeba paměti |
| **LoRA** | 24–32 GB | Rychlá | 95–98 % | Vyvážený přístup |
| **Plné** | 80 GB+ | Nejpomalejší | 100 % | Maximální kvalita |

### 3. Spusťte trénink

**Datová sada a co se model naučí**  
Skripty převádějí datovou sadu na chatovací příklady. Například skript QLoRA používá **Abirate/english_quotes**: každý příklad se stane párem uživatel–asistent jako:

- **Uživatel:** „Dej mi citát o: &lt;tag&gt;"
- **Asistent:** „&lt;quote&gt; – &lt;author&gt;"

Doladění naučí model reagovat na výzvy žádající o citáty na dané téma a vracet je ve formátu `<quote text> - <author>`. Skripty LoRA a plného doladění používají **databricks/databricks-dolly-15k** (obecné páry instrukce/odpověď), takže přesný úkol se liší podle skriptu; myšlenka je stejná – přizpůsobit model zvolené datové sadě a formátu.

Níže je přehled dostupných metod tréninku. Každá metoda odkazuje na svůj skript a poskytuje stručný popis pro výběr správného přístupu.

| Skript                           | Metoda            | Popis                                                                                                         | Typická VRAM | Doporučeno pro                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Trénuje malé adaptérové matice při zmrazení základního modelu. 3–5× rychlejší; ~95–98 % plné kvality.                         | 24–32 GB      | Pokročilí uživatelé; více adaptérů; více VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(pouze Linux)*             | **QLoRA**       | 4-bitová kvantizace + LoRA adaptéry. Nejnižší spotřeba paměti, nejrychlejší, malý kompromis v kvalitě. Vyžaduje `bitsandbytes` (pouze Linux).                            | 12–16 GB      | Většina uživatelů; rychlé experimenty; omezená VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Plné doladění** | Aktualizuje všechny parametry modelu. Maximální kvalita; nejvyšší spotřeba paměti a výpočetního výkonu.                                    | 40 GB+        | Maximální kvalita; výzkum; velká VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Poznámka:** Plné doladění (`train_full_finetuning.py`) může vyžadovat více než 64 GB systémové RAM a nemusí být na tomto zařízení proveditelné. Zvažte místo toho použití LoRA nebo QLoRA.
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka:** Plné doladění (`train_full_finetuning.py`) může vyžadovat více než 64 GB systémové RAM a nemusí být na tomto zařízení proveditelné. Zvažte místo toho použití LoRA.
<!-- @os:end -->
<!-- @device:end -->

Jednoduše vyberte preferovanou `Metodu tréninku`, stáhněte odpovídající skript a spusťte ho pomocí níže uvedeného příkazu při aktivovaném virtuálním prostředí:

```python
python3 train_<method_name>.py.
```

## Použití vašeho doladěného modelu

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

### Po tréninku LoRA/QLoRA

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

### Sloučení LoRA adaptéru do základního modelu

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Poznámka:**  
- Ujistěte se, že název adresáře modelu (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) odpovídá skutečné výstupní složce z tréninku.  
- Pokud jste použili LoRA místo QLoRA, jednoduše odpovídajícím způsobem nahraďte cestu.  
- Některé modely Gemma vyžadují zadání `trust_remote_code=True` v `from_pretrained`; přidejte, pokud se zobrazí příslušné varování.

Pro další vlastní nastavení (tokeny odsazení, zařízení atd.) se podívejte do skriptu, který jste použili pro trénink.

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

Při použití této metody se ujistěte, že vaše soubory JSON jsou správně strukturovány, aby nedocházelo k chybám při parsování.

Je nutné dodržovat následující pokyny:
* **Formátování souboru:** Soubory JSON by měly být formátovány v integrovaném vývojovém prostředí (IDE), aby byla zajištěna správná struktura a syntaxe.
* **Požadované klíče:** Vlastní soubor JSON musí obsahovat klíče `instruction` a `response`. Tyto klíče jsou nezbytné pro správné fungování metody.
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

Při využívání datových sad z Hugging Face se ujistěte, že vaše datové sady jsou správně strukturovány pro bezproblémovou integraci.

Je třeba dodržovat následující pokyny:
* **Pár instrukce–odpověď:** Zaměřte se na datové sady, které obsahují pár `instruction-response`. Tato struktura je nezbytná pro zamýšlenou funkčnost.
* **Úprava vlastních klíčů:** Pokud vaše datová sada neodpovídá struktuře `instruction-response`, máte možnost upravit funkci `format_instruction()`. To vám umožní přizpůsobit konkrétní klíče podle potřeby.

Příklad úpravy: V případech, kdy je třeba upravit výstup datové sady, můžete upravit sekci odpovědi ve funkci format_instruction() tak, aby vyhovovala vašim požadavkům.
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

Aby skript mohl pracovat se souborem ve formátu CSV, musíte zajistit, že soubor CSV obsahuje sloupce s názvem `instruction` a `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Úprava parametrů tréninku

Upravte tréninkový skript a změňte proměnné tak, aby odpovídaly vašim cílům: **rychlost učení** (`LR`), **epochy** (`EPOCHS`), **velikost dávky** (`BATCH_SIZE`), **akumulace gradientů** (`GRAD_ACCUM_STEPS`) a pro LoRA/QLoRA **rank** (`LORA_R`). Pro rychlejší běhy použijte méně epoch a vyšší rychlost učení (LR); pro lepší kvalitu použijte více epoch a nižší LR. Snižte velikost dávky nebo délku sekvence, pokud narazíte na chyby způsobené nedostatkem paměti.

### Tipy pro optimalizaci paměti

Pokud narazíte na chyby způsobené nedostatkem paměti:

**1. Snižte velikost dávky:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Snižte délku sekvence:**
```python
max_seq_length=256  # Instead of 512
```

**3. Použijte agresivnější kvantizaci:**
```
Full → LoRA → QLoRA
```

**4. Povolte kontrolní body gradientů (pouze plné doladění):**
```python
model.gradient_checkpointing_enable()
```

---

## Sledování a ladění

### Sledování paměti GPU

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Volitelné) Sledování experimentů pomocí Weights & Biases

Pro zaznamenávání běhů a metrik do [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

V tréninkovém skriptu nastavte `report_to="wandb"` a volitelně `run_name="your-experiment-name"` v konfiguraci tréneru. Pokud nechcete používat Wandb, ponechte `report_to` na výchozí hodnotě nebo nastavte na `"none"`.

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

#### Pomalý trénink

**Řešení:** Zvyšte velikost dávky, pokud to paměť dovoluje
```python
BATCH_SIZE = 8
```
## Další kroky

Po úspěšném dokončení doladění zvažte následující kroky, jak ze svého modelu vytěžit více:

1. **Vyhodnoťte** důkladně na oddělených testovacích datech, abyste změřili generalizaci a předešli přetrénování.
2. **Experimentujte** zkoušením různých hodnot hyperparametrů pro lepší kompromisy mezi přesností, rychlostí a pamětí.
3. **Sledujte** všechny své experimenty (a odpovídající metriky) pomocí Weights & Biases pro reprodukovatelný výzkum.
4. **Vyzkoušejte** trénink na vlastních datových sadách, abyste model přizpůsobili konkrétně pro váš případ použití.
5. **Nasaďte** svůj doladěný model pro rychlé odvozování pomocí efektivních backendů, jako je vLLM na kompatibilním hardwaru.
6. **Prozkoumejte** pokročilé techniky včetně prompt engineeringu, smíšené přesnosti a delších délek sekvencí.
7. **Trénujte** více LoRA adaptérů pro různé úkoly nebo domény a podle potřeby je přepínejte.

---