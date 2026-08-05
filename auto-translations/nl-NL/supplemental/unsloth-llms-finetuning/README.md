<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Machinevertaling.** Deze pagina is automatisch vertaald vanuit het Engels en is niet door een mens gecontroleerd. Deze pagina kan fouten bevatten en bepaalde instructies, opdrachten, downloads, productbeschikbaarheid of andere inhoud kan per taal of regio verschillen. In geval van tegenstrijdigheid of discrepantie is de oorspronkelijke Engelse versie van de playbook doorslaggevend en prevaleert deze.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Overzicht

Dit playbook laat zien hoe je lokaal een taalmodel finetunet met Unsloth op AMD-hardware.

Het gebruikt een kort Supervised Fine-Tuning (SFT)-voorbeeld met LoRA-adapters op `unsloth/gemma-4-E4B-it`, met een subset van de `mlabonne/FineTome-100k`-dataset. Het doel is om je een eenvoudige end-to-end workflow te geven die setup, training, inferentie en het opslaan van het gefinetunede resultaat omvat.

Het voorbeeld is ontworpen om praktisch en gemakkelijk aan te passen te zijn, zodat je het kunt gebruiken als uitgangspunt voor je eigen datasets en modellen.

## Wat je zult leren

- Hoe je de Unsloth-omgeving opzet
- Hoe je een LLM finetunet met SFT en Unsloth
- Hoe je het gefinetunede resultaat lokaal opslaat

<!-- @device:halo,stx,krk -->
> **Opmerking:** De finetuning-technieken in dit playbook vereisen ten minste **64 GB systeem-RAM**, waarvan ten minste **24 GB beschikbaar moet zijn voor de GPU** (de 24 GB maakt deel uit van de 64 GB, niet als extra daarbovenop).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Opmerking:** De finetuning-technieken in dit playbook vereisen ten minste **24 GB totaal GPU-geheugen** en **32 GB systeem-RAM**.
> - Op Windows combineert het totale GPU-geheugen de toegewezen VRAM van de grafische kaart met gedeeld GPU-geheugen (geleend van het systeem-RAM).
> - Kaarten met minder dan 24 GB toegewezen VRAM kunnen daarom dit playbook nog steeds uitvoeren door gedeeld GPU-geheugen te gebruiken om het verschil aan te vullen.
<!-- @os:end -->

<!-- @os:linux -->
> **Opmerking:** De finetuning-technieken in dit playbook vereisen een grafische kaart met ten minste **24 GB toegewezen GPU-geheugen** en **32 GB systeem-RAM**.
> - Op Linux draait training volledig in het toegewezen VRAM van de grafische kaart.
> - Er wordt niet teruggevallen op gedeeld GPU-geheugen (systeem-RAM) wanneer het VRAM opraakt.
> - Kaarten met minder dan 24 GB toegewezen VRAM raken tijdens training op Linux zonder geheugen, zelfs als het systeem voldoende RAM heeft.
<!-- @os:end -->
<!-- @device:end -->

## Waarom Unsloth?

Unsloth maakt het finetunen van LLM's eenvoudiger om lokaal op hardware uit te voeren door het geheugengebruik te verminderen en de training te versnellen in vergelijking met een standaardopstelling.

In dit playbook gebruiken we Unsloth samen met **LoRA-gebaseerde SFT**. Dat betekent dat het basismodel grotendeels bevroren blijft, terwijl een veel kleinere set adaptergewichten wordt getraind. Dit past goed bij lokale ontwikkeling omdat het lichter is dan volledige finetuning en sneller te itereren is.

Unsloth ondersteunt ook andere trainingsbenaderingen, waaronder QLoRA en reinforcement learning-workflows. Dit playbook richt zich eerst op het eenvoudigste pad: een klein LoRA-finetuningvoorbeeld dat gebruikers kunnen uitvoeren, begrijpen en uitbreiden.

## De geheugenconfiguratie instellen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Controleren op software-updates
> **Opmerking**: Als VS Code niet is geïnstalleerd, kun je het installeren met Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Software-vereisten installeren

### Een virtuele omgeving aanmaken

<!-- @os:linux -->
<!-- @device:halo_box -->
Open een terminal en maak een venv aan met AMD ROCm™ software en PyTorch al geïnstalleerd:
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
**Geef je gebruiker toegang tot GPU-apparaten** (log uit en weer in om dit van kracht te laten worden):

```bash
sudo usermod -aG render,video $LOGNAME
```

Open een terminal en maak een venv aan:
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
> **Opmerking:** Python 3.13 is vereist voor Windows.

<!-- @device:halo_box -->
Open een PowerShell-terminal en maak een virtuele omgeving aan:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Open een PowerShell-terminal en maak een virtuele omgeving aan:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Basisafhankelijkheden installeren
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

### Aanvullende afhankelijkheden

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
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Opmerking:** Tijdens het importeren kan Unsloth optionele `bitsandbytes`-versnellingspaden testen. Op sommige ROCm-versies kun je een melding zien zoals `bitsandbytes library load error: Configured ROCm binary not found`. Dit playbook gebruikt standaard LoRA-finetuning met `optim="adamw_torch"`, dus we vertrouwen niet op de `bitsandbytes`-optimizer of 4-bit QLoRA. Deze melding kan veilig worden genegeerd.

<!-- @os:windows -->
> **Opmerking:** Op Windows ROCm zal Unsloth bij het opstarten verschillende waarschuwingen weergeven — zie [Bekende waarschuwingen](#known-warnings) hieronder. Deze kunnen allemaal veilig worden genegeerd; training werkt correct.
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

## Download het Unsloth-finetuningscript

In plaats van handmatig elke stap uit te voeren, biedt dit playbook een overzichtelijk, end-to-end script hier: [test_unsloth.py](assets/test_unsloth.py).

Voer de volgende code uit om het script te draaien:

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

De rest van het playbook doorloopt conceptueel elke belangrijke stap van het script.

## Hoe het werkt

Het test_unsloth.py-script voert de volgende stappen uit:
* **Model laden**: Laadt unsloth/gemma-4-E4B-it met FastModel.
* **Data voorbereiden**: Standaardiseert de dataset (bijv. FineTome-100k) en past het Gemma-4-chattemplate toe.
* **LoRA toepassen**: Voegt adapters toe aan taal-, aandacht- en MLP-modules voor efficiënte training.
* **Trainen**: Gebruikt SFTTrainer met response-only loss masking.
* **Inferentie**: Voert een snelle generatietest uit om de prestaties te verifiëren.
* **Opslaan**: Exporteert LoRA-adapters lokaal.

## Belangrijke configuratie

Je kunt de volgende constanten aanpassen om je run aan te passen:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Voorbeeld van het Unsloth-welkomstbericht en de output bij het laden van de modelgewichten:

![alt text](assets/welcome.png)

## Dataset voorbereiden

We gebruiken een subset van:
```text
mlabonne/FineTome-100k
```
De dataset wordt:
* Omgezet naar chatformaat
* Verwerkt met het Gemma-4-chattemplate
* Opgeschoond om dubbele BOS-tokens te verwijderen

## Het model trainen

Het script voert een korte trainingsdemo uit, met de volgende parameters:
- ~50 stappen
- Kleine batchgrootte
- Gradient accumulation

Tijdens de training zie je logs zoals:

![alt text](assets/training.png)


## Opslaan en implementeren
### Lokaal opslaan (LoRA)

Het script slaat LoRA-adapters automatisch op in de OUTPUT_DIR.
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

### Samengevoegd model opslaan (voor vLLM) 

<!-- @os:windows -->
> **Opmerking:** vLLM ondersteunt Windows niet. Om uw fijn afgestemde model op Windows te implementeren, gebruikt u llama.cpp (zie [GGUF exporteren](#export-gguf-for-llamacpp) hieronder) of draagt u het samengevoegde model over naar een Linux-machine waarop vLLM draait.
<!-- @os:end -->

<!-- @os:linux -->
Voor implementatie met vLLM voegt u de adapters samen tot een volledig model:
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

### GGUF exporteren (voor llama.cpp)

Rechtstreeks converteren naar GGUF voor lokale inferentie:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Bekende waarschuwingen

Deze waarschuwingen worden door Unsloth bij het opstarten weergegeven op Windows ROCm en kunnen allemaal veilig worden genegeerd:

| Waarschuwing | Reden | Veilig om te negeren? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes heeft geen Windows ROCm-build | Ja — deze playbook gebruikt `adamw_torch`, niet bnb |
| `No ROCm platform found for torch.distributed` | ROCm op Windows mist gedistribueerde training | Ja — training met één GPU wordt hierdoor niet beïnvloed |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth markeert niet-Linux-builds | Ja — Windows ROCm werkt voor SFT met één GPU |
| `triton is not available` | Triton heeft geen Windows-build | Ja — Unsloth valt terug op PyTorch-kernels |

Training zal correct verlopen ondanks deze waarschuwingen.
<!-- @os:end -->

## Volgende stappen
- Probeer [Unsloth Studio](https://unsloth.ai/docs/new/studio), een intuïtieve GUI voor Unsloth
- Train op uw eigen specifieke datasets
- Probeer finetunen met verschillende hyperparameters
- Implementeer met vLLM of llama.cpp
- Probeer QLoRA voor een opstelling met een lager geheugengebruik

## Bronnen

Hieronder vindt u enkele aanvullende bronnen om meer te leren over Unsloth en finetunen:

* [Unsloth Documentatie](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth Fine-tuning Handleiding](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)