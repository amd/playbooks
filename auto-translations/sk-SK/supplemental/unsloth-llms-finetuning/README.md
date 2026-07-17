<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Tento playbook používa špeciálne značky, ktoré GitHub nedokáže vykresliť. Správny náhľad tohto obsahu nájdete na [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->

## Prehľad

Tento playbook ukazuje, ako lokálne doladiť jazykový model pomocou Unsloth na hardvéri AMD.

Využíva krátky príklad doladenia pod dohľadom (SFT) s LoRA adaptérmi na modeli `unsloth/gemma-4-E4B-it`, pričom sa používa podmnožina datasetu `mlabonne/FineTome-100k`. Cieľom je poskytnúť jednoduchý kompletný pracovný postup, ktorý zahŕňa nastavenie, tréning, inferenciu a uloženie doladeného výsledku.

Príklad je navrhnutý tak, aby bol praktický a ľahko upraviteľný, takže ho môžete použiť ako východiskový bod pre vlastné datasety a modely.

## Čo sa naučíte

- Ako nastaviť prostredie Unsloth
- Ako doladiť LLM pomocou SFT s Unsloth
- Ako uložiť doladený výsledok do lokálneho úložiska

<!-- @device:halo,stx,krk -->
> **Poznámka:** Techniky doladenia v tomto playbooku vyžadujú aspoň 24 GB pamäte GPU a 32 GB systémovej pamäte RAM.
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Poznámka:** Techniky doladenia v tomto playbooku vyžadujú aspoň 24 GB pamäte GPU a 32 GB systémovej pamäte RAM.
<!-- @os:end -->

<!-- @os:linux -->
> **Poznámka:** Techniky doladenia v tomto playbooku vyžadujú aspoň 24 GB **dedikovanej** pamäte GPU a 32 GB systémovej pamäte RAM.
<!-- @os:end -->
<!-- @device:end -->

## Prečo Unsloth?

Unsloth uľahčuje doladenie LLM na lokálnom hardvéri tým, že znižuje využitie pamäte a urýchľuje tréning v porovnaní so štandardným nastavením.

V tomto playbooku používame Unsloth spolu s **SFT založeným na LoRA**. To znamená, že základný model zostáva väčšinou zmrazený, zatiaľ čo sa trénuje oveľa menšia sada váh adaptéra. Je to vhodné pre lokálny vývoj, pretože je ľahšie ako úplné doladenie a rýchlejšie na iteráciu.

Unsloth tiež podporuje iné prístupy k tréningu, vrátane QLoRA a pracovných postupov posilňovaného učenia. Tento playbook sa zameriava najprv na najjednoduchšiu cestu: malý príklad doladenia LoRA, ktorý môžu používatelia spustiť, pochopiť a rozšíriť.

## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizácií softvéru
> **Poznámka**: Ak VS Code nie je nainštalovaný, môžete ho nainštalovať pomocou Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Inštalácia softvérových predpokladov

### Vytvorenie virtuálneho prostredia

<!-- @os:linux -->
<!-- @device:halo_box -->
Otvorte terminál a vytvorte venv s AMD ROCm™ softvérom a PyTorch, ktoré sú už nainštalované:
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
**Udeľte svojmu používateľovi prístup k zariadeniam GPU** (aby sa zmena prejavila, odhláste sa a znova prihláste):

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

> **Poznámka:** Počas importu môže Unsloth testovať voliteľné cesty akcelerácie `bitsandbytes`. Na niektorých verziách ROCm sa môže zobraziť správa ako `bitsandbytes library load error: Configured ROCm binary not found`. Tento playbook používa štandardné doladenie LoRA s `optim="adamw_torch"`, takže sa nespoliehame na optimalizátor `bitsandbytes` ani 4-bitový QLoRA. Túto správu možno bezpečne ignorovať.

<!-- @os:windows -->
> **Poznámka:** Na Windows ROCm bude Unsloth pri spustení vypisovať niekoľko varovaní — pozrite si [Známe varovania](#known-warnings) nižšie. Všetky možno bezpečne ignorovať; tréning funguje správne.
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

Namiesto manuálneho vykonávania každého kroku tento playbook poskytuje čistý, kompletný skript tu: [test_unsloth.py](assets/test_unsloth.py).

Spustite nasledujúci kód na vykonanie skriptu:

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

Zvyšok playbooku bude koncepčne prechádzať každým hlavným krokom skriptu.

## Ako to funguje

Skript test_unsloth.py vykonáva nasledujúce kroky:
* **Načítanie modelu**: Načíta unsloth/gemma-4-E4B-it pomocou FastModel.
* **Príprava dát**: Štandardizuje dataset (napr. FineTome-100k) a aplikuje šablónu chatu Gemma-4.
* **Aplikácia LoRA**: Pridáva adaptéry k jazykovým, pozornostným a MLP modulom pre efektívny tréning.
* **Tréning**: Používa SFTTrainer s maskovaním straty iba na odpovede.
* **Inferencia**: Spustí rýchly test generovania na overenie výkonu.
* **Uloženie**: Exportuje LoRA adaptéry lokálne.

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
* Prevedený do formátu chatu
* Spracovaný pomocou šablóny chatu Gemma-4
* Vyčistený od duplicitných tokenov BOS

## Tréning modelu

Skript spustí krátku ukážku tréningu s nasledujúcimi parametrami:
- ~50 krokov
- Malá veľkosť dávky
- Akumulácia gradientov

Počas tréningu uvidíte záznamy ako:

![alt text](assets/training.png)


## Ukladanie a nasadenie

### Lokálne ukladanie (LoRA)

Skript automaticky ukladá LoRA adaptéry do OUTPUT_DIR.
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
> **Poznámka:** vLLM nepodporuje Windows. Na nasadenie doladeného modelu na Windows použite llama.cpp (pozrite si [Export GGUF](#export-gguf-for-llamacpp) nižšie) alebo presuňte zlúčený model na linuxový počítač so spusteným vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Na nasadenie s vLLM zlúčte adaptéry do úplného modelu:
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

Priamo konvertujte do GGUF pre lokálnu inferenciu:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Známe varovania

Tieto varovania vypisuje Unsloth pri spustení na Windows ROCm a všetky možno bezpečne ignorovať:

| Varovanie | Dôvod | Možno bezpečne ignorovať? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes nemá zostavu pre Windows ROCm | Áno — tento playbook používa `adamw_torch`, nie bnb |
| `No ROCm platform found for torch.distributed` | ROCm na Windows nepodporuje distribuovaný tréning | Áno — tréning na jednom GPU nie je ovplyvnený |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth označuje zostavy mimo Linuxu | Áno — Windows ROCm funguje pre SFT na jednom GPU |
| `triton is not available` | Triton nemá zostavu pre Windows | Áno — Unsloth sa prepne na jadrá PyTorch |

Tréning bude napriek týmto varovaniam prebiehať správne.
<!-- @os:end -->

## Ďalšie kroky
- Vyskúšajte [Unsloth Studio](https://unsloth.ai/docs/new/studio), intuitívne grafické rozhranie pre Unsloth
- Trénujte na vlastných špecifických datasetoch
- Vyskúšajte doladenie s rôznymi hyperparametrami
- Nasaďte pomocou vLLM alebo llama.cpp
- Vyskúšajte QLoRA pre nastavenie s nižšou pamäťou

## Zdroje

Nižšie sú uvedené ďalšie zdroje na získanie ďalších informácií o Unsloth a dolaďovaní:

* [Dokumentácia Unsloth](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Sprievodca dolaďovaním Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)