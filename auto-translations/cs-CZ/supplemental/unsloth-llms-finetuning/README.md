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

Tento playbook ukazuje, jak lokálně doladit (fine-tune) jazykový model pomocí Unsloth na hardwaru AMD.

Používá krátký příklad Supervised Fine-Tuning (SFT) s adaptéry LoRA na modelu `unsloth/gemma-4-E4B-it`, s využitím podmnožiny datasetu `mlabonne/FineTome-100k`. Cílem je poskytnout jednoduchý kompletní pracovní postup od nastavení přes trénování a inferenci až po uložení výsledku doladění.

Příklad je navržen tak, aby byl praktický a snadno upravitelný, takže jej můžete použít jako výchozí bod pro vlastní datasety a modely.

## Co se naučíte

- Jak nastavit prostředí Unsloth
- Jak doladit LLM pomocí SFT s Unsloth
- Jak uložit výsledek doladění do místního úložiště

<!-- @device:halo,stx,krk -->
> **Poznámka:** Techniky doladění v tomto playbooku vyžadují minimálně **64 GB systémové paměti RAM**, přičemž alespoň **24 GB z toho musí být dostupných pro GPU** (těchto 24 GB je součástí oněch 64 GB, nikoli navíc).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Poznámka:** Techniky doladění v tomto playbooku vyžadují minimálně **24 GB celkové paměti GPU** a **32 GB systémové paměti RAM**.
> - Ve Windows se celková paměť GPU skládá z vyhrazené paměti VRAM grafické karty a sdílené paměti GPU (vypůjčené ze systémové paměti RAM).
> - Karty s méně než 24 GB vyhrazené paměti VRAM tak mohou tento playbook stále spustit díky využití sdílené paměti GPU, která tento rozdíl dorovná.
<!-- @os:end -->

<!-- @os:linux -->
> **Poznámka:** Techniky doladění v tomto playbooku vyžadují grafickou kartu s minimálně **24 GB vyhrazené paměti GPU** a **32 GB systémové paměti RAM**.
> - V Linuxu probíhá trénování výhradně ve vyhrazené paměti VRAM grafické karty.
> - Nedochází k přechodu na sdílenou paměť GPU (systémovou paměť RAM), pokud VRAM dojde.
> - Kartám s méně než 24 GB vyhrazené paměti VRAM dojde paměť během trénování v Linuxu, i když má systém dostatek RAM.
<!-- @os:end -->
<!-- @device:end -->

## Proč Unsloth?

Unsloth usnadňuje doladění LLM na lokálním hardwaru tím, že snižuje spotřebu paměti a zrychluje trénování ve srovnání se standardním nastavením.

V tomto playbooku používáme Unsloth společně s **SFT založeným na LoRA**. To znamená, že základní model zůstává převážně zmrazený, zatímco se trénuje mnohem menší sada vah adaptéru. To se dobře hodí pro lokální vývoj, protože je to lehčí než plné doladění a rychlejší na iteraci.

Unsloth také podporuje další přístupy k trénování, včetně QLoRA a pracovních postupů posilovaného učení (reinforcement learning). Tento playbook se nejprve zaměřuje na nejjednodušší cestu: malý příklad doladění LoRA, který mohou uživatelé spustit, pochopit a rozšířit.

<!-- @device:halo_box,halo,stx,krk -->
## Nastavení konfigurace paměti

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru
> **Poznámka**: Pokud není nainstalován VS Code, můžete jej nainstalovat pomocí Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace softwarových předpokladů

<!-- @prereq:hf-models-gemma-4-e4b-it,hf-datasets-finetome-100k -->

### Vytvoření virtuálního prostředí

<!-- @os:linux -->
<!-- @device:halo_box -->
Otevřete terminál a vytvořte venv s již nainstalovaným AMD ROCm™ softwarem a PyTorch:
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
python3 -m venv unsloth-env --system-site-packages
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Udělte svému uživateli přístup k zařízením GPU** (aby se změna projevila, odhlaste se a znovu přihlaste):

```bash
sudo usermod -aG render,video $LOGNAME
```

Otevřete terminál a vytvořte venv:
<!-- @test:id=create-venv timeout=300 -->
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
<!-- @require:driver -->

> **Důležité:** Unsloth zatím nepodporuje sestavení PyTorch 2.13, které je dodáváno s ROCm 10. Pro tento playbook nainstalujte pomocí níže uvedených příkazů **ROCm 7.14 s PyTorch 2.12**. Nepoužívejte balíčky ROCm 10 / PyTorch 2.13.

**Nainstalujte PyTorch s podporou AMD ROCm™ softwaru** ve vytvořeném virtuálním prostředí:

<!-- @device:halo,halo_box -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1151]==2.12.0+rocm7.14.0" "torchvision[device-gfx1151]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1150]==2.12.0+rocm7.14.0" "torchvision[device-gfx1150]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:krk -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1152]==2.12.0+rocm7.14.0" "torchvision[device-gfx1152]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx7900xt -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1100]==2.12.0+rocm7.14.0" "torchvision[device-gfx1100]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx9070xt,r9700 -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1201]==2.12.0+rocm7.14.0" "torchvision[device-gfx1201]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

Pro ostatní zařízení si prosím prostudujte kompletní pokyny v [dokumentaci ROCm 7.14](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html).

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
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git" triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Poznámka:** Během importu může Unsloth prověřovat volitelné akcelerační cesty `bitsandbytes`. U některých verzí ROCm se může zobrazit zpráva typu `bitsandbytes library load error: Configured ROCm binary not found`. Tento playbook používá standardní doladění LoRA s `optim="adamw_torch"`, takže se nespoléháme na optimalizátor `bitsandbytes` ani na 4bitovou QLoRA. Tuto zprávu lze bezpečně ignorovat.

<!-- @os:windows -->
> **Poznámka:** Na ROCm pro Windows Unsloth při spuštění vypíše několik varování — viz [Known Warnings](#known-warnings) níže. Všechna lze bezpečně ignorovat; trénování funguje správně.
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

Namísto ručního provádění každého kroku poskytuje tento playbook čistý, kompletní skript zde: [test_unsloth.py](assets/test_unsloth.py).

Spuštěním následujícího kódu skript spustíte:

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

Zbytek playbooku koncepčně projde každý hlavní krok skriptu.

## Jak to funguje

Skript test_unsloth.py provádí následující kroky:
* **Načtení modelu**: Načte unsloth/gemma-4-E4B-it pomocí FastModel.
* **Příprava dat**: Standardizuje dataset (např. FineTome-100k) a aplikuje chatovací šablonu Gemma-4.
* **Aplikace LoRA**: Přidává adaptéry do jazykových, pozornostních (attention) a MLP modulů pro efektivní trénování.
* **Trénování**: Používá SFTTrainer s maskováním ztráty pouze na odpovědích (response-only loss masking).
* **Inference**: Spustí rychlý test generování pro ověření výkonu.
* **Uložení**: Exportuje adaptéry LoRA lokálně.
## Klíčová konfigurace

Následující konstanty můžete upravit a přizpůsobit si tak svůj běh:

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
* Převedena do chatového formátu
* Zpracována pomocí šablony chatu Gemma-4
* Vyčištěna od duplicitních BOS tokenů

## Trénování modelu

Skript spustí krátkou trénovací ukázku s následujícími parametry:
- ~50 kroků
- Malá velikost dávky
- Akumulace gradientů

Během trénování uvidíte protokoly jako:

![alt text](assets/training.png)


## Ukládání a nasazení

### Místní ukládání (LoRA)

Skript automaticky uloží adaptéry LoRA do OUTPUT_DIR.
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
> **Poznámka:** vLLM nepodporuje Windows. Chcete-li svůj doladěný model nasadit na Windows, použijte llama.cpp (viz [Export GGUF](#export-gguf-for-llamacpp) níže) nebo přeneste sloučený model na linuxový počítač se spuštěným vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Pro nasazení s vLLM sloučte adaptéry do úplného modelu:
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
## Známá varování

Tato varování vypisuje Unsloth při spuštění na Windows ROCm a všechna je bezpečné ignorovat:

| Varování | Důvod | Bezpečné ignorovat? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes nemá sestavení pro Windows ROCm | Ano — tento playbook používá `adamw_torch`, nikoli bnb |
| `No ROCm platform found for torch.distributed` | ROCm na Windows nepodporuje distribuované trénování | Ano — trénování na jednom GPU není ovlivněno |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth označuje sestavení jiná než Linux | Ano — Windows ROCm funguje pro SFT na jednom GPU |
| `triton is not available` | Triton nemá sestavení pro Windows | Ano — Unsloth se přepne zpět na jádra PyTorch |

Trénování bude pokračovat správně i přes tato varování.
<!-- @os:end -->

## Další kroky
- Vyzkoušejte [Unsloth Studio](https://unsloth.ai/docs/new/studio), intuitivní grafické rozhraní pro Unsloth
- Trénujte na vlastních specifických datových sadách
- Vyzkoušejte doladění s jinými hyperparametry
- Nasaďte pomocí vLLM nebo llama.cpp
- Vyzkoušejte QLoRA pro řešení s nižší pamětí

## Zdroje

Níže naleznete další zdroje, kde se dozvíte více o Unsloth a doladění:

* [Dokumentace Unsloth](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Průvodce doladěním Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)