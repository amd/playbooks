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

Dit playbook laat zien hoe je een taalmodel lokaal kunt fine-tunen met Unsloth op AMD-hardware.

Het maakt gebruik van een kort Supervised Fine-Tuning (SFT)-voorbeeld met LoRA-adapters op `unsloth/gemma-4-E4B-it`, waarbij een subset van de `mlabonne/FineTome-100k`-dataset wordt gebruikt. Het doel is om je een eenvoudige end-to-end workflow te geven die setup, training, inferentie en het opslaan van het fine-getunede resultaat omvat.

Het voorbeeld is opgezet om praktisch en eenvoudig aan te passen te zijn, zodat je het als uitgangspunt kunt gebruiken voor je eigen datasets en modellen.

## Wat je zult leren

- Hoe je de Unsloth-omgeving opzet
- Hoe je een LLM fine-tunet met behulp van SFT met Unsloth
- Hoe je het fine-getunede resultaat lokaal opslaat

<!-- @device:halo,stx,krk -->
> **Opmerking:** De fine-tuningtechnieken in dit playbook vereisen minimaal **64 GB systeem-RAM**, waarvan minimaal **24 GB beschikbaar is voor de GPU** (de 24 GB maakt deel uit van de 64 GB, niet extra daarbovenop).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Opmerking:** De fine-tuningtechnieken in dit playbook vereisen minimaal **24 GB totaal GPU-geheugen** en **32 GB systeem-RAM**.
> - Op Windows combineert het totale GPU-geheugen het toegewijde VRAM van de videokaart met gedeeld GPU-geheugen (geleend van het systeem-RAM).
> - Daarom kunnen kaarten met minder dan 24 GB toegewijd VRAM dit playbook toch uitvoeren door gedeeld GPU-geheugen te gebruiken om het verschil aan te vullen.
<!-- @os:end -->

<!-- @os:linux -->
> **Opmerking:** De fine-tuningtechnieken in dit playbook vereisen een videokaart met minimaal **24 GB toegewijd GPU-geheugen** en **32 GB systeem-RAM**.
> - Op Linux draait training volledig in het toegewijde VRAM van de videokaart.
> - Het valt niet terug op gedeeld GPU-geheugen (systeem-RAM) wanneer het VRAM opraakt.
> - Kaarten met minder dan 24 GB toegewijd VRAM zullen tijdens training op Linux zonder geheugen komen te zitten, zelfs als het systeem voldoende RAM heeft.
<!-- @os:end -->
<!-- @device:end -->

## Waarom Unsloth?

Unsloth maakt het fine-tunen van LLM's eenvoudiger om lokaal op hardware uit te voeren door het geheugengebruik te verminderen en de training te versnellen in vergelijking met een standaardopzet.

In dit playbook gebruiken we Unsloth samen met **LoRA-gebaseerde SFT**. Dat betekent dat het basismodel grotendeels bevroren blijft, terwijl een veel kleinere set adapterge wichten wordt getraind. Dit past goed bij lokale ontwikkeling omdat het lichter is dan volledige fine-tuning en sneller itereert.

Unsloth ondersteunt ook andere trainingsbenaderingen, waaronder QLoRA en reinforcement learning-workflows. Dit playbook richt zich eerst op het eenvoudigste pad: een klein LoRA fine-tuningvoorbeeld dat gebruikers kunnen uitvoeren, begrijpen en uitbreiden.

<!-- @device:halo_box,halo,stx,krk -->
## De geheugenconfiguratie instellen

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Controleren op software-updates
> **Opmerking**: Als VS Code niet is geïnstalleerd, kun je het installeren via Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Softwarevereisten installeren

### Een virtuele omgeving maken

<!-- @os:linux -->
<!-- @device:halo_box -->
Open een terminal en maak een venv aan met AMD ROCm™-software en PyTorch al geïnstalleerd:
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
<!-- @require:driver -->

> **Belangrijk:** Unsloth ondersteunt de PyTorch 2.13-build die met ROCm 10 wordt meegeleverd nog niet. Installeer voor dit playbook **ROCm 7.14 met PyTorch 2.12** met behulp van de onderstaande commando's. Gebruik niet de ROCm 10 / PyTorch 2.13-pakketten.

**Installeer PyTorch met ondersteuning voor AMD ROCm™-software** in de aangemaakte virtuele omgeving:

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

Raadpleeg voor andere apparaten de [ROCm 7.14-documentatie](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html) voor volledige instructies.

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
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git" triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Opmerking:** Tijdens het importeren kan Unsloth optionele `bitsandbytes`-versnellingspaden onderzoeken. Bij sommige ROCm-versies kan een melding verschijnen zoals `bitsandbytes library load error: Configured ROCm binary not found`. Dit playbook gebruikt standaard LoRA fine-tuning met `optim="adamw_torch"`, dus we vertrouwen niet op de `bitsandbytes`-optimizer of 4-bit QLoRA. Deze melding kan veilig worden genegeerd.

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

## Het Unsloth fine-tuningscript downloaden

In plaats van elke stap handmatig uit te voeren, biedt dit playbook hier een overzichtelijk, end-to-end script: [test_unsloth.py](assets/test_unsloth.py).

Voer de volgende code uit om het script uit te voeren:

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

Het script test_unsloth.py voert de volgende stappen uit:
* **Model laden**: Laadt unsloth/gemma-4-E4B-it met behulp van FastModel.
* **Data voorbereiden**: Standaardiseert de dataset (bijv. FineTome-100k) en past de Gemma-4 chattemplate toe.
* **LoRA toepassen**: Voegt adapters toe aan taal-, aandacht- en MLP-modules voor efficiënte training.
* **Trainen**: Gebruikt SFTTrainer met response-only loss masking.
* **Inferentie**: Voert een snelle generatietest uit om de prestaties te verifiëren.
* **Opslaan**: Exporteert LoRA-adapters lokaal.
## Sleutelconfiguratie

U kunt de volgende constanten aanpassen om uw run te personaliseren:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Voorbeeld van het Unsloth-welkomstbericht en de uitvoer bij het laden van de modelgewichten:

![alt text](assets/welcome.png)

## Dataset voorbereiden

We gebruiken een subset van:
```text
mlabonne/FineTome-100k
```
De dataset wordt:
* Geconverteerd naar chatformaat
* Verwerkt met behulp van de Gemma-4 chat-template
* Opgeschoond om dubbele BOS-tokens te verwijderen

## Het model trainen

Het script voert een korte trainingsdemo uit, met de volgende parameters:
- ~50 stappen
- Kleine batchgrootte
- Gradiëntaccumulatie

Tijdens het trainen ziet u logs zoals:

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
> **Opmerking:** vLLM ondersteunt Windows niet. Om uw fijngetunede model op Windows te implementeren, gebruikt u llama.cpp (zie [GGUF exporteren](#export-gguf-for-llamacpp) hieronder) of verplaatst u het samengevoegde model naar een Linux-machine waarop vLLM draait.
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

| Waarschuwing | Reden | Veilig te negeren? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes heeft geen Windows ROCm-build | Ja — dit playbook gebruikt `adamw_torch`, niet bnb |
| `No ROCm platform found for torch.distributed` | ROCm-op-Windows ondersteunt geen gedistribueerde training | Ja — training op één GPU wordt hierdoor niet beïnvloed |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth markeert niet-Linux-builds | Ja — Windows ROCm werkt voor SFT op één GPU |
| `triton is not available` | Triton heeft geen Windows-build | Ja — Unsloth valt terug op PyTorch-kernels |

Training verloopt correct ondanks deze waarschuwingen.
<!-- @os:end -->

## Volgende stappen
- Probeer [Unsloth Studio](https://unsloth.ai/docs/new/studio), een intuïtieve GUI voor Unsloth
- Train op uw eigen specifieke datasets
- Probeer finetuning met verschillende hyperparameters
- Implementeer met vLLM of llama.cpp
- Probeer QLoRA voor een opstelling met minder geheugengebruik

## Bronnen

Hieronder vindt u enkele aanvullende bronnen om meer te leren over Unsloth en finetuning:

* [Unsloth-documentatie](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth Finetuning-handleiding](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)