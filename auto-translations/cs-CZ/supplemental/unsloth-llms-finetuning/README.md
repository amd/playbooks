<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Tato příručka používá speciální značky, které GitHub neumí zobrazit. Pro správné zobrazení tohoto obsahu navštivte prosím [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->

## Přehled

Tato příručka ukazuje, jak lokálně doladit jazykový model pomocí Unsloth na hardwaru AMD.

Používá krátký příklad Supervised Fine-Tuning (SFT) s adaptéry LoRA na modelu `unsloth/gemma-4-E4B-it`, s využitím podmnožiny datové sady `mlabonne/FineTome-100k`. Cílem je poskytnout vám jednoduchý end-to-end pracovní postup, který zahrnuje nastavení, trénování, inferenci a uložení doladěného výsledku.

Příklad je navržen tak, aby byl praktický a snadno upravitelný, takže jej můžete použít jako výchozí bod pro vlastní datové sady a modely.

## Co se naučíte

- Jak nastavit prostředí Unsloth
- Jak doladit LLM pomocí SFT s Unsloth
- Jak uložit doladěný výsledek do lokálního úložiště

<!-- @device:halo,stx,krk -->
> **Poznámka:** Techniky doladění v této příručce vyžadují alespoň 24 GB paměti GPU a 32 GB systémové paměti RAM.
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Poznámka:** Techniky doladění v této příručce vyžadují alespoň 24 GB paměti GPU a 32 GB systémové paměti RAM.
<!-- @os:end -->

<!-- @os:linux -->
> **Poznámka:** Techniky doladění v této příručce vyžadují alespoň 24 GB **vyhrazené** paměti GPU a 32 GB systémové paměti RAM.
<!-- @os:end -->
<!-- @device:end -->

## Proč Unsloth?

Unsloth usnadňuje spouštění doladění LLM na lokálním hardwaru tím, že snižuje spotřebu paměti a urychluje trénování ve srovnání se standardním nastavením.

V této příručce používáme Unsloth spolu s **LoRA-based SFT**. To znamená, že základní model zůstává převážně zmrazený, zatímco se trénuje mnohem menší sada adaptérových vah. To je vhodné pro lokální vývoj, protože je to lehčí než plné doladění a rychlejší na iterace.

Unsloth také podporuje další přístupy k trénování, včetně QLoRA a workflow s posilovaným učením. Tato příručka se nejprve zaměřuje na nejjednodušší cestu: malý příklad LoRA doladění, který si uživatelé mohou spustit, pochopit a dále rozšířit.

## Nastavení konfigurace paměti

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru
> **Poznámka**: Pokud VS Code není nainstalován, můžete jej nainstalovat pomocí Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace softwarových předpokladů

### Vytvoření virtuálního prostředí

<!-- @os:linux -->
<!-- @device:halo_box -->
Otevřete terminál a vytvořte venv s již nainstalovaným AMD ROCm™ softwarem a PyTorch:
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
python3 -m venv unsloth-env --system-site-packages
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Udělte svému uživateli přístup k zařízením GPU** (aby se to projevilo, odhlaste se a znovu přihlaste):

```bash
sudo usermod -aG render,video $LOGNAME
```

Otevřete terminál a vytvořte venv:
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv unsloth-env
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **Poznámka:** Pro Windows je vyžadován Python 3.13.

<!-- @device:halo_box -->
Otevřete terminál PowerShell a vytvořte virtuální prostředí:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Otevřete terminál PowerShell a vytvořte virtuální prostředí:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Instalace základních závislostí
<!-- @require:pytorch,driver -->

<!-- @test:id=verify-torch-env timeout=300 hidden=True setup=activate-venv -->
```python
import sys
import torch

print(f"Python executable: {sys.executable}")
print(f"PyTorch version: {torch.__version__}")
print(f"torch.cuda.is_available(): {torch.cuda.is_available()}")

if not torch.cuda.is_available():
    raise SystemExit("FAIL: ROCm-enabled PyTorch is not visible in this venv")

print("PASS: ROCm-enabled PyTorch is visible")
```
<!-- @test:end -->

### Další závislosti

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Poznámka:** Během importu může Unsloth zkoušet volitelné akcelerační cesty `bitsandbytes`. U některých verzí ROCm se může zobrazit zpráva jako `bitsandbytes library load error: Configured ROCm binary not found`. Tato příručka používá standardní LoRA doladění s `optim="adamw_torch"`, takže se nespoléháme na optimalizátor `bitsandbytes` ani na 4bitové QLoRA. Tuto zprávu lze bezpečně ignorovat.

<!-- @os:windows -->
> **Poznámka:** Na Windows ROCm zobrazí Unsloth při spuštění několik varování — viz [Known Warnings](#known-warnings) níže. Všechna je bezpečné ignorovat; trénování funguje správně.
<!-- @os:end -->

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
```python
import unsloth
import torch
from datasets import load_dataset
from transformers import TextStreamer
from unsloth import FastModel
from unsloth.chat_templates import (
    get_chat_template,
    standardize_data_formats,
    train_on_responses_only,
)
from trl import SFTTrainer, SFTConfig

print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print("PASS: All required imports succeeded")
```
<!-- @test:end -->

## Stažení skriptu pro doladění Unsloth

Namísto ručního provádění každého kroku poskytuje tato příručka přehledný end-to-end skript zde: [test_unsloth.py](assets/test_unsloth.py).

Spusťte následující kód pro spuštění skriptu:

```bash
python test_unsloth.py
```

<!-- @test:id=verify-script timeout=60 hidden=True -->
```python
import os
import sys
import ast

scripts = ["test_unsloth.py", "test_unsloth_ci.py"]
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing script: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

for script in scripts:
    with open(script, "r", encoding="utf-8") as f:
        ast.parse(f.read(), filename=script)
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=quick-train-unsloth timeout=2400 hidden=True setup=activate-venv -->
```bash
python test_unsloth_ci.py
```
<!-- @test:end -->

Zbytek příručky konceptuálně projde jednotlivé hlavní kroky skriptu. 

## Jak to funguje

Skript test_unsloth.py provádí následující kroky:
* **Načtení modelu**: Načte unsloth/gemma-4-E4B-it pomocí FastModel.
* **Příprava dat**: Standardizuje datovou sadu (např. FineTome-100k) a aplikuje šablonu chatu Gemma-4.
* **Aplikace LoRA**: Přidává adaptéry do jazykových, attention a MLP modulů pro efektivní trénování.
* **Trénování**: Používá SFTTrainer s maskováním ztráty pouze pro odpovědi.
* **Inference**: Spustí rychlý test generování pro ověření výkonu.
* **Uložení**: Exportuje LoRA adaptéry lokálně.

## Klíčová konfigurace

Následující konstanty můžete upravit pro přizpůsobení běhu:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Příklad uvítací zprávy Unsloth a výstupu při načítání vah modelu:

![alt text](assets/welcome.png)

## Příprava datové sady

Používáme podmnožinu:
```text
mlabonne/FineTome-100k
```
Datová sada je: 
* Převedena do formátu chatu
* Zpracována pomocí šablony chatu Gemma-4
* Vyčištěna od duplicitních tokenů BOS

## Trénování modelu

Skript spustí krátkou trénovací ukázku s následujícími parametry:
- ~50 kroků
- Malá velikost dávky
- Akumulace gradientu

Během trénování uvidíte protokoly jako:

![alt text](assets/training.png)


## Ukládání a nasazení

### Lokální ukládání (LoRA)

Skript automaticky uloží LoRA adaptéry do OUTPUT_DIR.
```python
model.save_pretrained("gemma_4_lora")  
tokenizer.save_pretrained("gemma_4_lora")
```

<!-- @test:id=verify-unsloth-lora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_lora_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = (
    glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) +
    glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
)
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: Unsloth LoRA output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end -->

### Uložení sloučeného modelu (pro vLLM) 

<!-- @os:windows -->
> **Poznámka:** vLLM nepodporuje Windows. Pro nasazení doladěného modelu na Windows použijte llama.cpp (viz [Export GGUF](#export-gguf-for-llamacpp) níže) nebo přeneste sloučený model na linuxový počítač se spuštěným vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Pro nasazení pomocí vLLM sloučte adaptéry do plného modelu:
```python
model.save_pretrained_merged("gemma-4-finetune", tokenizer)
```
<!-- @os:end -->

<!-- @test:id=verify-unsloth-merged-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_merged_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing merged model directory: {out_dir}")
    sys.exit(1)

required = [
    "config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required merged files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Merged model output looks correct")
```
<!-- @test:end -->

### Export GGUF (pro llama.cpp)

Převeďte přímo na GGUF pro lokální inferenci:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Známá upozornění

Tato upozornění vypisuje Unsloth při spuštění na Windows ROCm a všechna je bezpečné ignorovat:

| Upozornění | Důvod | Bezpečné ignorovat? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes nemá build pro Windows ROCm | Ano — tento playbook používá `adamw_torch`, nikoli bnb |
| `No ROCm platform found for torch.distributed` | ROCm na Windows nepodporuje distribuované trénování | Ano — trénování na jednom GPU není ovlivněno |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth označuje jiné než linuxové buildy | Ano — Windows ROCm funguje pro SFT na jednom GPU |
| `triton is not available` | Triton nemá build pro Windows | Ano — Unsloth přechází na jádra PyTorch |

Trénování bude probíhat správně i přes tato upozornění.
<!-- @os:end -->

## Další kroky
- Vyzkoušejte [Unsloth Studio](https://unsloth.ai/docs/new/studio), intuitivní grafické rozhraní pro Unsloth
- Trénujte na vlastních specifických datových sadách
- Vyzkoušejte doladění s různými hyperparametry
- Nasaďte pomocí vLLM nebo llama.cpp
- Vyzkoušejte QLoRA pro nastavení s nižší náročností na paměť

## Zdroje

Níže je uvedeno několik dalších zdrojů, kde se dozvíte více o Unsloth a doladění:

* [Dokumentace Unsloth](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Průvodce doladěním od Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)