<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Overzicht

Deze playbook laat zien hoe je een taalmodel lokaal kunt fine-tunen met Unsloth op AMD-hardware.

Het gebruikt een kort Supervised Fine-Tuning (SFT)-voorbeeld met LoRA-adapters op `unsloth/gemma-4-E4B-it`, met behulp van een subset van de `mlabonne/FineTome-100k`-dataset. Het doel is om je een eenvoudige end-to-end workflow te bieden die installatie, training, inferentie en het opslaan van het gefinetuned resultaat omvat.

Het voorbeeld is praktisch en eenvoudig aan te passen, zodat je het kunt gebruiken als startpunt voor je eigen datasets en modellen.

## Wat Je Leert

- Hoe je de Unsloth-omgeving instelt
- Hoe je een LLM fine-tunet met SFT via Unsloth
- Hoe je het gefinetuned resultaat opslaat in lokale opslag

<!-- @device:halo,stx,krk -->
> **Opmerking:** De fine-tuningtechnieken in deze playbook vereisen minimaal 24 GB GPU-geheugen en 32 GB systeemgeheugen.
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Opmerking:** De fine-tuningtechnieken in deze playbook vereisen minimaal 24 GB GPU-geheugen en 32 GB systeemgeheugen.
<!-- @os:end -->

<!-- @os:linux -->
> **Opmerking:** De fine-tuningtechnieken in deze playbook vereisen minimaal 24 GB **dedicated** GPU-geheugen en 32 GB systeemgeheugen.
<!-- @os:end -->
<!-- @device:end -->

## Waarom Unsloth?

Unsloth maakt LLM-finetuning eenvoudiger uitvoerbaar op lokale hardware door het geheugengebruik te verminderen en de training te versnellen ten opzichte van een standaardinstelling.

In deze playbook gebruiken we Unsloth samen met **LoRA-gebaseerde SFT**. Dat betekent dat het basismodel grotendeels bevroren blijft, terwijl een veel kleinere set adaptergewichten wordt getraind. Dit is goed geschikt voor lokale ontwikkeling omdat het lichter is dan volledige finetuning en sneller te itereren.

Unsloth ondersteunt ook andere trainingsbenaderingen, waaronder QLoRA en reinforcement learning-workflows. Deze playbook richt zich eerst op het eenvoudigste pad: een klein LoRA-finetuningvoorbeeld dat gebruikers kunnen uitvoeren, begrijpen en uitbreiden.

## De Geheugenconfiguratie Instellen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Controleer op Software-updates
> **Opmerking**: Als VS Code niet is geïnstalleerd, kun je het installeren via het Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Softwarevereisten Installeren

### Een Virtuele Omgeving Aanmaken

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

### Basisafhankelijkheden Installeren
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

### Aanvullende Afhankelijkheden

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

> **Opmerking:** Tijdens het importeren kan Unsloth optionele `bitsandbytes`-versnellingspaden onderzoeken. Op sommige ROCm-versies zie je mogelijk een bericht zoals `bitsandbytes library load error: Configured ROCm binary not found`. Deze playbook gebruikt standaard LoRA-finetuning met `optim="adamw_torch"`, dus we zijn niet afhankelijk van de `bitsandbytes`-optimizer of 4-bit QLoRA. Dit bericht kan veilig worden genegeerd.

<!-- @os:windows -->
> **Opmerking:** Op Windows ROCm zal Unsloth bij het opstarten meerdere waarschuwingen afdrukken — zie [Bekende Waarschuwingen](#known-warnings) hieronder. Deze zijn allemaal veilig te negeren; de training werkt correct.
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

## Het Unsloth Fine-Tuning Script Downloaden

In plaats van elke stap handmatig uit te voeren, biedt deze playbook een overzichtelijk end-to-end script hier: [test_unsloth.py](assets/test_unsloth.py).

Voer de volgende code uit om het script te starten:

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

De rest van de playbook doorloopt conceptueel elke belangrijke stap van het script.

## Hoe Het Werkt

Het test_unsloth.py-script voert de volgende stappen uit:
* **Model laden**: Laadt unsloth/gemma-4-E4B-it met FastModel.
* **Data voorbereiden**: Standaardiseert de dataset (bijv. FineTome-100k) en past de Gemma-4-chattemplate toe.
* **LoRA toepassen**: Voegt adapters toe aan taal-, aandachts- en MLP-modules voor efficiënte training.
* **Trainen**: Gebruikt SFTTrainer met response-only loss masking.
* **Inferentie**: Voert een snelle generatietest uit om de prestaties te verifiëren.
* **Opslaan**: Exporteert LoRA-adapters lokaal.

## Belangrijkste Configuratie

Je kunt de volgende constanten aanpassen om je uitvoering te personaliseren:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Voorbeeld van het Unsloth-welkomstbericht en de uitvoer bij het laden van de modelgewichten:

![alt text](assets/welcome.png)

## Dataset Voorbereiden

We gebruiken een subset van:
```text
mlabonne/FineTome-100k
```
De dataset wordt:
* Omgezet naar chatformaat
* Verwerkt met de Gemma-4-chattemplate
* Opgeschoond om dubbele BOS-tokens te verwijderen

## Het Model Trainen

Het script voert een korte trainingsdemo uit, met de volgende parameters:
- ~50 stappen
- Kleine batchgrootte
- Gradiëntaccumulatie

Tijdens de training zie je logs zoals:

![alt text](assets/training.png)


## Opslaan en Implementeren

### Lokaal Opslaan (LoRA)

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
> **Opmerking:** vLLM ondersteunt Windows niet. Om je gefinetuned model op Windows te implementeren, gebruik je llama.cpp (zie [GGUF exporteren](#export-gguf-for-llamacpp) hieronder) of breng je het samengevoegde model over naar een Linux-machine waarop vLLM draait.
<!-- @os:end -->

<!-- @os:linux -->
Voor implementatie met vLLM, voeg de adapters samen tot een volledig model:
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

### GGUF Exporteren (voor llama.cpp)

Converteer direct naar GGUF voor lokale inferentie:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Bekende Waarschuwingen

Deze waarschuwingen worden door Unsloth bij het opstarten op Windows ROCm afgedrukt en zijn allemaal veilig te negeren:

| Waarschuwing | Reden | Veilig te negeren? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes heeft geen Windows ROCm-build | Ja — deze playbook gebruikt `adamw_torch`, niet bnb |
| `No ROCm platform found for torch.distributed` | ROCm-op-Windows mist gedistribueerde training | Ja — training op één GPU wordt niet beïnvloed |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth markeert niet-Linux-builds | Ja — Windows ROCm werkt voor SFT op één GPU |
| `triton is not available` | Triton heeft geen Windows-build | Ja — Unsloth valt terug op PyTorch-kernels |

Training verloopt correct ondanks deze waarschuwingen.
<!-- @os:end -->

## Volgende Stappen
- Probeer [Unsloth Studio](https://unsloth.ai/docs/new/studio), een intuïtieve GUI voor Unsloth
- Train op je eigen specifieke datasets
- Probeer finetuning met verschillende hyperparameters
- Implementeer met vLLM of llama.cpp
- Probeer QLoRA voor een instelling met minder geheugengebruik

## Bronnen

Hieronder vind je aanvullende bronnen om meer te leren over Unsloth en finetuning:

* [Unsloth Docs](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth Fine-tuning Guide](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)