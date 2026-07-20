<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Táto príručka používa špeciálne značky, ktoré GitHub nedokáže vykresliť. Ak chcete tento obsah správne zobraziť, navštívte stránku [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->

## Prehľad

Táto príručka ukazuje, ako lokálne doladiť jazykový model pomocou Unsloth na hardvéri AMD.

Používa krátky príklad Supervised Fine-Tuning (SFT) s adaptérmi LoRA na modeli `unsloth/gemma-4-E4B-it`, pričom sa využíva podmnožina datasetu `mlabonne/FineTome-100k`. Cieľom je poskytnúť vám jednoduchý end-to-end pracovný postup, ktorý pokrýva nastavenie, trénovanie, inferenciu a uloženie doladeného výsledku.

Príklad je navrhnutý tak, aby bol praktický a ľahko upraviteľný, takže ho môžete použiť ako východiskový bod pre vlastné datasety a modely.

## Čo sa naučíte

- Ako nastaviť prostredie Unsloth
- Ako doladiť LLM pomocou SFT s Unsloth
- Ako uložiť doladený výsledok do lokálneho úložiska

<!-- @device:halo,stx,krk -->
> **Poznámka:** Techniky doladenia v tejto príručke vyžadujú aspoň 24 GB pamäte GPU a 32 GB systémovej RAM.
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Poznámka:** Techniky doladenia v tejto príručke vyžadujú aspoň 24 GB pamäte GPU a 32 GB systémovej RAM.
<!-- @os:end -->

<!-- @os:linux -->
> **Poznámka:** Techniky doladenia v tejto príručke vyžadujú aspoň 24 GB **vyhradenej** pamäte GPU a 32 GB systémovej RAM.
<!-- @os:end -->
<!-- @device:end -->

## Prečo Unsloth?

Unsloth uľahčuje spúšťanie doladenia LLM na lokálnom hardvéri tým, že znižuje spotrebu pamäte a zrýchľuje trénovanie v porovnaní so štandardným nastavením.

V tejto príručke používame Unsloth spolu s **LoRA-based SFT**. To znamená, že základný model zostáva väčšinou zmrazený, zatiaľ čo sa trénuje oveľa menšia sada váh adaptéra. Toto je vhodné pre lokálny vývoj, pretože je to ľahšie ako úplné doladenie a rýchlejšie na iteráciu.

Unsloth tiež podporuje iné prístupy k trénovaniu, vrátane QLoRA a workflow s posilneným učením (reinforcement learning). Táto príručka sa zameriava predovšetkým na najjednoduchšiu cestu: malý príklad doladenia LoRA, ktorý si používatelia môžu spustiť, pochopiť a rozšíriť.

## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizácií softvéru
> **Poznámka**: Ak nemáte nainštalovaný VS Code, môžete ho nainštalovať pomocou Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Inštalácia softvérových predpokladov

### Vytvorenie virtuálneho prostredia

<!-- @os:linux -->
<!-- @device:halo_box -->
Otvorte terminál a vytvorte venv s už nainštalovaným softvérom AMD ROCm™ a PyTorch:
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
**Udeľte svojmu používateľovi prístup k zariadeniam GPU** (aby sa táto zmena prejavila, odhláste sa a znova prihláste):

```bash
sudo usermod -aG render,video $LOGNAME
```

Otvorte terminál a vytvorte venv:
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
> **Poznámka:** Pre Windows je vyžadovaný Python 3.13.

<!-- @device:halo_box -->
Otvorte terminál PowerShell a vytvorte virtuálne prostredie:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Otvorte terminál PowerShell a vytvorte virtuálne prostredie:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Inštalácia základných závislostí
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

### Ďalšie závislosti

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

> **Poznámka:** Počas importu môže Unsloth preverovať voliteľné akceleračné cesty `bitsandbytes`. V niektorých verziách ROCm sa vám môže zobraziť správa ako `bitsandbytes library load error: Configured ROCm binary not found`. Táto príručka používa štandardné doladenie LoRA s `optim="adamw_torch"`, takže sa nespoliehame na optimalizátor `bitsandbytes` ani na 4-bitové QLoRA. Túto správu je možné bezpečne ignorovať.

<!-- @os:windows -->
> **Poznámka:** Na Windows ROCm vypíše Unsloth pri spustení niekoľko upozornení — pozri [Known Warnings](#known-warnings) nižšie. Všetky je možné bezpečne ignorovať; trénovanie funguje správne.
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

## Stiahnutie skriptu na doladenie Unsloth

Namiesto ručného vykonávania jednotlivých krokov poskytuje táto príručka prehľadný, end-to-end skript tu: [test_unsloth.py](assets/test_unsloth.py).

Spustite nasledujúci kód na spustenie skriptu:

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

Zvyšok príručky koncepčne prejde jednotlivými hlavnými krokmi skriptu.

## Ako to funguje

Skript test_unsloth.py vykonáva nasledujúce kroky:
* **Načítanie modelu**: Načíta unsloth/gemma-4-E4B-it pomocou FastModel.
* **Príprava dát**: Štandardizuje dataset (napr. FineTome-100k) a aplikuje šablónu chatu Gemma-4.
* **Aplikácia LoRA**: Pridáva adaptéry do jazykových, pozornostných a MLP modulov na efektívne trénovanie.
* **Trénovanie**: Používa SFTTrainer s maskovaním straty len na odpovede (response-only loss masking).
* **Inferencia**: Spustí rýchly generačný test na overenie výkonu.
* **Uloženie**: Exportuje adaptéry LoRA lokálne.

## Kľúčová konfigurácia

Nasledujúce konštanty môžete upraviť na prispôsobenie svojho behu:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Príklad uvítacej správy Unsloth a výstupu pri načítaní váh modelu:

![alt text](assets/welcome.png)

## Príprava datasetu

Používame podmnožinu:
```text
mlabonne/FineTome-100k
```
Dataset je: 
* Konvertovaný do formátu chatu
* Spracovaný pomocou šablóny chatu Gemma-4
* Vyčistený od duplicitných tokenov BOS

## Trénovanie modelu

Skript spúšťa krátku ukážku trénovania s nasledujúcimi parametrami:
- ~50 krokov
- Malá veľkosť dávky
- Akumulácia gradientu

Počas trénovania uvidíte logy ako:

![alt text](assets/training.png)


## Ukladanie a nasadenie

### Lokálne uloženie (LoRA)

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

### Uloženie zlúčeného modelu (pre vLLM) 

<!-- @os:windows -->
> **Poznámka:** vLLM nepodporuje Windows. Ak chcete nasadiť svoj doladený model na Windows, použite llama.cpp (pozri [Export GGUF](#export-gguf-for-llamacpp) nižšie) alebo preneste zlúčený model na počítač s Linuxom, na ktorom beží vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Na nasadenie s vLLM zlúčte adaptéry do plného modelu:
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

### Export GGUF (pre llama.cpp)

Priamo konvertujte na GGUF pre lokálnu inferenciu:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Známe upozornenia

Tieto upozornenia vypisuje Unsloth pri spustení na Windows ROCm a všetky je bezpečné ignorovať:

| Upozornenie | Dôvod | Bezpečné ignorovať? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes nemá zostavenie pre Windows ROCm | Áno — táto príručka používa `adamw_torch`, nie bnb |
| `No ROCm platform found for torch.distributed` | ROCm na Windows nepodporuje distribuované trénovanie | Áno — trénovanie na jednej GPU tým nie je ovplyvnené |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth označuje zostavenia mimo Linuxu | Áno — Windows ROCm funguje pre SFT na jednej GPU |
| `triton is not available` | Triton nemá zostavenie pre Windows | Áno — Unsloth prejde na PyTorch jadrá |

Trénovanie bude prebiehať správne aj napriek týmto upozorneniam.
<!-- @os:end -->

## Ďalšie kroky
- Vyskúšajte [Unsloth Studio](https://unsloth.ai/docs/new/studio), intuitívne grafické rozhranie pre Unsloth
- Trénujte na vlastných špecifických súboroch dát
- Vyskúšajte doladenie s inými hyperparametrami
- Nasaďte pomocou vLLM alebo llama.cpp
- Vyskúšajte QLoRA pre nastavenie s nižšou pamäťovou náročnosťou

## Zdroje

Nižšie nájdete ďalšie zdroje, kde sa dozviete viac o Unsloth a doladzovaní:

* [Dokumentácia Unsloth](https://docs.unsloth.ai)

* [Unsloth na GitHube](https://github.com/unslothai/unsloth)

* [Sprievodca doladzovaním Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)