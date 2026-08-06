<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversættelse.** Denne side er automatisk oversat fra engelsk og er ikke blevet gennemgået af et menneske. Den kan indeholde fejl, og visse instruktioner, kommandoer, downloads, produkttilgængelighed eller andet indhold kan variere afhængigt af sprog eller region. I tilfælde af uoverensstemmelse eller afvigelse er den oprindelige engelske version af playbook'en gældende og har forrang.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Oversigt

Denne playbook viser, hvordan du finjusterer en sprogmodel lokalt med Unsloth på AMD-hardware.

Den bruger et kort Supervised Fine-Tuning (SFT)-eksempel med LoRA-adaptere på `unsloth/gemma-4-E4B-it`, ved brug af et udsnit af datasættet `mlabonne/FineTome-100k`. Målet er at give dig en simpel end-to-end-arbejdsgang, der dækker opsætning, træning, inferens og lagring af det finjusterede resultat.

Eksemplet er designet til at være praktisk og nemt at tilpasse, så du kan bruge det som udgangspunkt for dine egne datasæt og modeller.

## Hvad du vil lære

- Hvordan du opsætter Unsloth-miljøet
- Hvordan du finjusterer en LLM ved hjælp af SFT med Unsloth
- Hvordan du gemmer det finjusterede resultat lokalt

<!-- @device:halo,stx,krk -->
> **Bemærk:** Finjusteringsteknikkerne i denne playbook kræver mindst **64 GB systemhukommelse**, hvoraf mindst **24 GB skal være tilgængelig for GPU'en** (de 24 GB er en del af de 64 GB, ikke i tillæg hertil).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Bemærk:** Finjusteringsteknikkerne i denne playbook kræver mindst **24 GB samlet GPU-hukommelse** og **32 GB systemhukommelse**.
> - På Windows kombinerer den samlede GPU-hukommelse grafikkortets dedikerede VRAM med delt GPU-hukommelse (lånt fra systemhukommelsen).
> - Derfor kan kort med mindre end 24 GB dedikeret VRAM stadig køre denne playbook ved at bruge delt GPU-hukommelse til at dække forskellen.
<!-- @os:end -->

<!-- @os:linux -->
> **Bemærk:** Finjusteringsteknikkerne i denne playbook kræver et grafikkort med mindst **24 GB dedikeret GPU-hukommelse** og **32 GB systemhukommelse**.
> - På Linux kører træningen udelukkende i grafikkortets dedikerede VRAM.
> - Den falder ikke tilbage til delt GPU-hukommelse (systemhukommelse), når VRAM løber tør.
> - Kort med mindre end 24 GB dedikeret VRAM vil løbe tør for hukommelse under træning på Linux, selv hvis systemet har rigelig RAM.
<!-- @os:end -->
<!-- @device:end -->

## Hvorfor Unsloth?

Unsloth gør det nemmere at køre LLM-finjustering på lokal hardware ved at reducere hukommelsesforbruget og fremskynde træningen sammenlignet med en standardopsætning.

I denne playbook bruger vi Unsloth sammen med **LoRA-baseret SFT**. Det betyder, at basismodellen for det meste forbliver frosset, mens et meget mindre sæt adapter-vægte trænes. Dette passer godt til lokal udvikling, fordi det er lettere end fuld finjustering og hurtigere at iterere på.

Unsloth understøtter også andre træningsmetoder, herunder QLoRA og reinforcement learning-arbejdsgange. Denne playbook fokuserer først på den enkleste vej: et lille LoRA-finjusteringseksempel, som brugere kan køre, forstå og udvide.

## Indstilling af hukommelseskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tjek for softwareopdateringer
> **Bemærk**: Hvis VS Code ikke er installeret, kan du installere det med Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installation af softwareforudsætninger

### Opret et virtuelt miljø

<!-- @os:linux -->
<!-- @device:halo_box -->
Åbn en terminal, og opret et venv med AMD ROCm™-software og PyTorch allerede installeret:
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
**Giv din bruger adgang til GPU-enheder** (log ud og ind igen, for at dette træder i kraft):

```bash
sudo usermod -aG render,video $LOGNAME
```

Åbn en terminal, og opret et venv:
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
> **Bemærk:** Python 3.13 er påkrævet til Windows.

<!-- @device:halo_box -->
Åbn en PowerShell-terminal, og opret et virtuelt miljø:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Åbn en PowerShell-terminal, og opret et virtuelt miljø:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Installation af grundlæggende afhængigheder
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

### Yderligere afhængigheder

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

> **Bemærk:** Under import kan Unsloth undersøge valgfrie `bitsandbytes`-accelerationsstier. På nogle ROCm-versioner kan du se en meddelelse som `bitsandbytes library load error: Configured ROCm binary not found`. Denne playbook bruger standard LoRA-finjustering med `optim="adamw_torch"`, så vi er ikke afhængige af `bitsandbytes`-optimeringen eller 4-bit QLoRA. Denne meddelelse kan trygt ignoreres.

<!-- @os:windows -->
> **Bemærk:** På Windows ROCm vil Unsloth udskrive flere advarsler ved opstart — se [Kendte advarsler](#known-warnings) nedenfor. Disse kan alle trygt ignoreres; træningen fungerer korrekt.
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

## Download Unsloth-finjusteringsscriptet

I stedet for manuelt at udføre hvert trin, indeholder denne playbook et rent end-to-end-script her: [test_unsloth.py](assets/test_unsloth.py).

Kør følgende kode for at udføre scriptet:

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

Resten af playbooken vil konceptuelt gennemgå hvert væsentligt trin i scriptet. 

## Sådan fungerer det

Scriptet test_unsloth.py udfører følgende trin:
* **Indlæs model**: Indlæser unsloth/gemma-4-E4B-it ved hjælp af FastModel.
* **Forbered data**: Standardiserer datasættet (f.eks. FineTome-100k) og anvender Gemma-4-chatskabelonen.
* **Anvend LoRA**: Tilføjer adaptere til sprog-, opmærksomheds- (attention-) og MLP-moduler for effektiv træning.
* **Træn**: Bruger SFTTrainer med response-only loss-maskering.
* **Inferens**: Kører en hurtig genereringstest for at verificere ydeevnen.
* **Gem**: Eksporterer LoRA-adaptere lokalt.

## Nøglekonfiguration

Du kan ændre følgende konstanter for at tilpasse din kørsel:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Eksempel på Unsloth-velkomstbeskeden og output ved indlæsning af modelvægtene:

![alt text](assets/welcome.png)

## Forbered datasæt

Vi bruger et udsnit af:
```text
mlabonne/FineTome-100k
```
Datasættet er:
* Konverteret til chatformat
* Behandlet ved hjælp af Gemma-4-chatskabelonen
* Renset for at fjerne duplikerede BOS-tokens

## Træn modellen

Scriptet kører en kort træningsdemo med følgende parametre:
- ~50 trin
- Lille batchstørrelse
- Gradientakkumulering

Under træningen vil du se logs som:

![alt text](assets/training.png)


## Lagring og udrulning
### Lokal lagring (LoRA)

Scriptet gemmer automatisk LoRA-adaptere i OUTPUT_DIR.
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

### Gem sammenflettet model (til vLLM)

<!-- @os:windows -->
> **Bemærk:** vLLM understøtter ikke Windows. For at implementere din finjusterede model på Windows kan du bruge llama.cpp (se [Eksportér GGUF](#export-gguf-for-llamacpp) nedenfor) eller overføre den sammenflettede model til en Linux-maskine, der kører vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Til implementering med vLLM skal adapterne flettes sammen til en fuld model:
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

### Eksportér GGUF (til llama.cpp)

Konverter direkte til GGUF til lokal inferens:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Kendte advarsler

Disse advarsler udskrives af Unsloth ved opstart på Windows ROCm og kan alle trygt ignoreres:

| Advarsel | Årsag | Sikker at ignorere? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes har ingen Windows ROCm-build | Ja — denne playbook bruger `adamw_torch`, ikke bnb |
| `No ROCm platform found for torch.distributed` | ROCm på Windows mangler distribueret træning | Ja — enkelt-GPU-træning påvirkes ikke |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth markerer builds, der ikke er Linux | Ja — Windows ROCm fungerer til enkelt-GPU SFT |
| `triton is not available` | Triton har ingen Windows-build | Ja — Unsloth falder tilbage til PyTorch-kerner |

Træningen vil forløbe korrekt på trods af disse advarsler.
<!-- @os:end -->

## Næste skridt
- Prøv [Unsloth Studio](https://unsloth.ai/docs/new/studio), en intuitiv GUI til Unsloth
- Træn på dine egne specifikke datasæt
- Prøv finjustering med forskellige hyperparametre
- Implementér med vLLM eller llama.cpp
- Prøv QLoRA til en opsætning med lavere hukommelsesforbrug

## Ressourcer

Nedenfor er nogle yderligere ressourcer til at lære mere om Unsloth og finjustering:

* [Unsloth Docs](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth Fine-tuning Guide](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)