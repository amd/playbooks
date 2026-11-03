<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Prehľad

Táto príručka ukazuje, ako lokálne doladiť jazykový model pomocou Unsloth na hardvéri AMD.

Používa krátky príklad Supervised Fine-Tuning (SFT) s adaptérmi LoRA na modeli `unsloth/gemma-4-E4B-it`, pričom využíva podmnožinu datasetu `mlabonne/FineTome-100k`. Cieľom je poskytnúť vám jednoduchý end-to-end pracovný postup, ktorý pokrýva nastavenie, tréning, inferenciu a uloženie doladeného výsledku.

Príklad je navrhnutý tak, aby bol praktický a ľahko upraviteľný, takže ho môžete použiť ako východiskový bod pre vlastné datasety a modely.

## Čo sa naučíte

- Ako nastaviť prostredie Unsloth
- Ako doladiť LLM pomocou SFT s Unsloth
- Ako uložiť doladený výsledok do lokálneho úložiska

<!-- @device:halo,stx,krk -->
> **Poznámka:** Techniky dolaďovania v tejto príručke vyžadujú aspoň **64 GB systémovej RAM**, pričom aspoň **24 GB z toho musí byť dostupných pre GPU** (týchto 24 GB je súčasťou 64 GB, nie navyše k nim).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Poznámka:** Techniky dolaďovania v tejto príručke vyžadujú aspoň **24 GB celkovej pamäte GPU** a **32 GB systémovej RAM**.
> - V systéme Windows celková pamäť GPU kombinuje vyhradenú VRAM grafickej karty so zdieľanou pamäťou GPU (vypožičanou zo systémovej RAM).
> - Preto aj karty s menej ako 24 GB vyhradenej VRAM môžu túto príručku spustiť, pretože rozdiel dokáže vykryť zdieľaná pamäť GPU.
<!-- @os:end -->

<!-- @os:linux -->
> **Poznámka:** Techniky dolaďovania v tejto príručke vyžadujú grafickú kartu s aspoň **24 GB vyhradenej pamäte GPU** a **32 GB systémovej RAM**.
> - V systéme Linux beží tréning výhradne vo vyhradenej VRAM grafickej karty.
> - Nedochádza k prechodu na zdieľanú pamäť GPU (systémovú RAM), keď dôjde VRAM.
> - Kartám s menej ako 24 GB vyhradenej VRAM dôjde počas tréningu na Linuxe pamäť, aj keby mal systém dostatok RAM.
<!-- @os:end -->
<!-- @device:end -->

## Prečo Unsloth?

Unsloth uľahčuje spúšťanie dolaďovania LLM na lokálnom hardvéri tým, že znižuje spotrebu pamäte a zrýchľuje tréning v porovnaní so štandardným nastavením.

V tejto príručke používame Unsloth spolu s **SFT založeným na LoRA**. To znamená, že základný model zostáva prevažne zmrazený, zatiaľ čo sa trénuje oveľa menšia sada váh adaptéra. To je vhodné pre lokálny vývoj, pretože je to ľahšie ako úplné dolaďovanie a rýchlejšie na iteráciu.

Unsloth podporuje aj iné prístupy k tréningu, vrátane QLoRA a pracovných postupov reinforcement learning. Táto príručka sa zameriava predovšetkým na najjednoduchšiu cestu: malý príklad LoRA dolaďovania, ktorý si používatelia môžu spustiť, pochopiť a rozšíriť.

<!-- @device:halo_box,halo,stx,krk -->
## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Kontrola aktualizácií softvéru
> **Poznámka**: Ak nie je nainštalovaný VS Code, môžete ho nainštalovať pomocou Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Inštalácia softvérových požiadaviek

### Vytvorenie virtuálneho prostredia

<!-- @os:linux -->
<!-- @device:halo_box -->
Otvorte terminál a vytvorte venv so softvérom AMD ROCm™ a už nainštalovaným PyTorch:
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
**Udeľte svojmu používateľovi prístup k zariadeniam GPU** (aby sa to prejavilo, odhláste sa a znova prihláste):

```bash
sudo usermod -aG render,video $LOGNAME
```

Otvorte terminál a vytvorte venv:
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
<!-- @require:driver -->

> **Dôležité:** Unsloth ešte nepodporuje zostavenie PyTorch 2.13, ktoré je súčasťou ROCm 10. Pre túto príručku nainštalujte **ROCm 7.14 s PyTorch 2.12** pomocou nižšie uvedených príkazov. Nepoužívajte balíky ROCm 10 / PyTorch 2.13.

**Nainštalujte PyTorch s podporou AMD ROCm™** vo vytvorenom virtuálnom prostredí:

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

Ohľadom ostatných zariadení si pozrite úplné pokyny v [dokumentácii ROCm 7.14](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html).

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

> **Poznámka:** Počas importu môže Unsloth skúmať voliteľné akceleračné cesty `bitsandbytes`. Na niektorých verziách ROCm sa môže zobraziť správa ako `bitsandbytes library load error: Configured ROCm binary not found`. Táto príručka používa štandardné dolaďovanie LoRA s `optim="adamw_torch"`, takže sa nespoliehame na optimalizátor `bitsandbytes` ani na 4-bitové QLoRA. Túto správu je možné bezpečne ignorovať.

<!-- @os:windows -->
> **Poznámka:** Na Windows ROCm zobrazí Unsloth pri spustení niekoľko upozornení — pozrite [Známe upozornenia](#known-warnings) nižšie. Všetky sú bezpečné na ignorovanie; tréning funguje správne.
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

## Stiahnutie skriptu na dolaďovanie Unsloth

Namiesto manuálneho vykonávania jednotlivých krokov táto príručka poskytuje čistý, end-to-end skript tu: [test_unsloth.py](assets/test_unsloth.py).

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

Zvyšok príručky koncepčne prejde jednotlivými hlavnými krokmi skriptu. 

## Ako to funguje

Skript test_unsloth.py vykonáva nasledujúce kroky:
* **Načítanie modelu**: Načíta unsloth/gemma-4-E4B-it pomocou FastModel.
* **Príprava dát**: Štandardizuje dataset (napr. FineTome-100k) a aplikuje šablónu chatu Gemma-4.
* **Aplikácia LoRA**: Pridáva adaptéry do jazykových, attention a MLP modulov pre efektívny tréning.
* **Tréning**: Používa SFTTrainer s maskovaním straty len na odpovedi (response-only loss masking).
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
* Konvertovaný do formátu chatu
* Spracovaný pomocou šablóny chatu Gemma-4
* Vyčistený od duplicitných BOS tokenov

## Trénovanie modelu

Skript spustí krátku ukážku trénovania s nasledujúcimi parametrami:
- ~50 krokov
- Malá veľkosť dávky (batch)
- Akumulácia gradientov

Počas trénovania uvidíte záznamy (logy) ako tieto:

![alt text](assets/training.png)


## Uloženie a nasadenie

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
> **Poznámka:** vLLM nepodporuje Windows. Ak chcete nasadiť svoj doladený model na Windows, použite llama.cpp (pozri [Export GGUF](#export-gguf-for-llamacpp) nižšie) alebo prenesite zlúčený model na počítač s Linuxom, na ktorom beží vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Na nasadenie pomocou vLLM zlúčte adaptéry do plného modelu:
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

Priama konverzia do GGUF pre lokálnu inferenciu:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Známe upozornenia

Tieto upozornenia vypisuje Unsloth pri spustení na Windows ROCm a všetky je bezpečné ignorovať:

| Upozornenie | Dôvod | Je bezpečné ignorovať? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes nemá build pre Windows ROCm | Áno — táto príručka používa `adamw_torch`, nie bnb |
| `No ROCm platform found for torch.distributed` | ROCm na Windows nepodporuje distribuované trénovanie | Áno — trénovanie na jednom GPU nie je ovplyvnené |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth označuje builds mimo Linuxu | Áno — Windows ROCm funguje pre SFT na jednom GPU |
| `triton is not available` | Triton nemá build pre Windows | Áno — Unsloth prejde na jadrá PyTorch |

Trénovanie bude prebiehať správne aj napriek týmto upozorneniam.
<!-- @os:end -->

## Ďalšie kroky
- Vyskúšajte [Unsloth Studio](https://unsloth.ai/docs/new/studio), intuitívne GUI pre Unsloth
- Trénujte na vlastných špecifických datasetoch
- Vyskúšajte doladenie s rôznymi hyperparametrami
- Nasaďte pomocou vLLM alebo llama.cpp
- Vyskúšajte QLoRA pre nastavenie s nižšou pamäťovou náročnosťou

## Zdroje

Nižšie nájdete ďalšie zdroje na dozvedenie sa viac o Unsloth a doladení:

* [Dokumentácia Unsloth](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Sprievodca doladením Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)