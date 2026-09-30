<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversettelse.** Denne siden ble automatisk oversatt fra engelsk og har ikke blitt gjennomgått av et menneske. Den kan inneholde feil, og enkelte instruksjoner, kommandoer, nedlastinger, produkttilgjengelighet eller annet innhold kan variere etter språk eller region. Ved eventuelle uoverensstemmelser eller avvik er den opprinnelige engelske versjonen av playbook-en gjeldende.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Oversikt

Denne oppskriften viser hvordan du finjusterer en språkmodell lokalt med Unsloth på AMD-maskinvare.

Den bruker et kort eksempel på veiledet finjustering (Supervised Fine-Tuning, SFT) med LoRA-adaptere på `unsloth/gemma-4-E4B-it`, ved bruk av et utvalg fra datasettet `mlabonne/FineTome-100k`. Målet er å gi deg en enkel ende-til-ende-arbeidsflyt som dekker oppsett, trening, inferens og lagring av det finjusterte resultatet.

Eksempelet er utformet for å være praktisk og enkelt å tilpasse, slik at du kan bruke det som utgangspunkt for dine egne datasett og modeller.

## Hva du vil lære

- Hvordan du setter opp Unsloth-miljøet
- Hvordan du finjusterer en LLM med SFT ved hjelp av Unsloth
- Hvordan du lagrer det finjusterte resultatet lokalt

<!-- @device:halo,stx,krk -->
> **Merk:** Finjusteringsteknikkene i denne oppskriften krever minst **64 GB systemminne (RAM)**, hvorav minst **24 GB må være tilgjengelig for GPU-en** (disse 24 GB-ene er en del av de 64 GB-ene, ikke i tillegg til dem).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Merk:** Finjusteringsteknikkene i denne oppskriften krever minst **24 GB total GPU-minne** og **32 GB systemminne (RAM)**.
> - På Windows kombinerer det totale GPU-minnet grafikkortets dedikerte VRAM med delt GPU-minne (lånt fra systemminnet).
> - Kort med mindre enn 24 GB dedikert VRAM kan derfor likevel kjøre denne oppskriften ved å bruke delt GPU-minne for å dekke differansen.
<!-- @os:end -->

<!-- @os:linux -->
> **Merk:** Finjusteringsteknikkene i denne oppskriften krever et grafikkort med minst **24 GB dedikert GPU-minne** og **32 GB systemminne (RAM)**.
> - På Linux kjører treningen utelukkende i grafikkortets dedikerte VRAM.
> - Den faller ikke tilbake til delt GPU-minne (systemminne) når VRAM-en er brukt opp.
> - Kort med mindre enn 24 GB dedikert VRAM vil gå tom for minne under trening på Linux, selv om systemet har rikelig med RAM.
<!-- @os:end -->
<!-- @device:end -->

## Hvorfor Unsloth?

Unsloth gjør det enklere å kjøre LLM-finjustering på lokal maskinvare ved å redusere minnebruken og gjøre treningen raskere sammenlignet med et standardoppsett.

I denne oppskriften bruker vi Unsloth sammen med **LoRA-basert SFT**. Det betyr at grunnmodellen for det meste holdes fastfrosset, mens et mye mindre sett med adapter-vekter trenes. Dette passer godt for lokal utvikling fordi det er lettere enn full finjustering og raskere å iterere på.

Unsloth støtter også andre treningsmetoder, inkludert QLoRA og arbeidsflyter for forsterkende læring. Denne oppskriften fokuserer først på den enkleste veien: et lite LoRA-finjusteringseksempel som brukere kan kjøre, forstå og utvide.

<!-- @device:halo_box,halo,stx,krk -->
## Konfigurere minneinnstillingene

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Sjekk etter programvareoppdateringer
> **Merk**: Hvis VS Code ikke er installert, kan du installere det med Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installere nødvendig programvare

### Opprett et virtuelt miljø

<!-- @os:linux -->
<!-- @device:halo_box -->
Åpne en terminal og opprett et venv med AMD ROCm™-programvare og PyTorch allerede installert:
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
**Gi brukeren din tilgang til GPU-enheter** (logg ut og inn igjen for at dette skal tre i kraft):

```bash
sudo usermod -aG render,video $LOGNAME
```

Åpne en terminal og opprett et venv:
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
> **Merk:** Python 3.13 er påkrevd for Windows.

<!-- @device:halo_box -->
Åpne en PowerShell-terminal og opprett et virtuelt miljø:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Åpne en PowerShell-terminal og opprett et virtuelt miljø:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Installere grunnleggende avhengigheter
<!-- @require:driver -->

> **Viktig:** Unsloth støtter ennå ikke PyTorch 2.13-versjonen som følger med ROCm 10. For denne oppskriften, installer **ROCm 7.14 med PyTorch 2.12** ved hjelp av kommandoene nedenfor. Ikke bruk ROCm 10 / PyTorch 2.13-pakkene.

**Installer PyTorch med støtte for AMD ROCm™-programvare** i det opprettede virtuelle miljøet:

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

For andre enheter, se [ROCm 7.14-dokumentasjonen](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html) for fullstendige instruksjoner.

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

### Ytterligere avhengigheter

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

> **Merk:** Under import kan Unsloth undersøke valgfrie akselerasjonsbaner for `bitsandbytes`. På enkelte ROCm-versjoner kan du se en melding som `bitsandbytes library load error: Configured ROCm binary not found`. Denne oppskriften bruker standard LoRA-finjustering med `optim="adamw_torch"`, så vi er ikke avhengige av `bitsandbytes`-optimeringsverktøyet eller 4-bit QLoRA. Denne meldingen kan trygt ignoreres.

<!-- @os:windows -->
> **Merk:** På Windows ROCm vil Unsloth skrive ut flere advarsler ved oppstart — se [Kjente advarsler](#known-warnings) nedenfor. Disse kan alle trygt ignoreres; treningen fungerer korrekt.
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

## Last ned Unsloth-finjusteringsskriptet

I stedet for å utføre hvert trinn manuelt, gir denne oppskriften et rent, ende-til-ende-skript her: [test_unsloth.py](assets/test_unsloth.py).

Kjør følgende kode for å utføre skriptet:

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

Resten av oppskriften vil konseptuelt gå gjennom hvert hovedtrinn i skriptet. 

## Hvordan det fungerer

Skriptet test_unsloth.py utfører følgende trinn:
* **Last inn modell**: Laster inn unsloth/gemma-4-E4B-it ved hjelp av FastModel.
* **Klargjør data**: Standardiserer datasettet (f.eks. FineTome-100k) og bruker Gemma-4-chatmalen.
* **Bruk LoRA**: Legger til adaptere i språk-, oppmerksomhets- (attention) og MLP-moduler for effektiv trening.
* **Trening**: Bruker SFTTrainer med maskering av tap som kun gjelder respons.
* **Inferens**: Kjører en rask genereringstest for å verifisere ytelsen.
* **Lagre**: Eksporterer LoRA-adaptere lokalt.
## Nøkkelkonfigurasjon

Du kan endre følgende konstanter for å tilpasse kjøringen din:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Eksempel på Unsloths velkomstmelding og resultat ved lasting av modellvektene:

![alt text](assets/welcome.png)

## Klargjør datasettet

Vi bruker et delsett av:
```text
mlabonne/FineTome-100k
```
Datasettet er: 
* Konvertert til chatformat
* Behandlet ved hjelp av Gemma-4-chatmalen
* Renset for å fjerne duplikate BOS-tokener

## Tren modellen

Skriptet kjører en kort treningsdemo, med følgende parametere:
- ~50 steg
- Liten batch-størrelse
- Gradientakkumulering

Under trening vil du se logger som:

![alt text](assets/training.png)


## Lagring og distribusjon

### Lokal lagring (LoRA)

Skriptet lagrer automatisk LoRA-adaptere til OUTPUT_DIR.
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

### Lagre sammenslått modell (for vLLM) 

<!-- @os:windows -->
> **Merk:** vLLM støtter ikke Windows. For å distribuere din finjusterte modell på Windows, bruk llama.cpp (se [Eksporter GGUF](#export-gguf-for-llamacpp) nedenfor) eller overfør den sammenslåtte modellen til en Linux-maskin som kjører vLLM.
<!-- @os:end -->

<!-- @os:linux -->
For distribusjon med vLLM, slå sammen adapterne til en full modell:
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

### Eksporter GGUF (for llama.cpp)

Konverter direkte til GGUF for lokal inferens:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Kjente advarsler

Disse advarslene skrives ut av Unsloth ved oppstart på Windows ROCm og er trygge å ignorere:

| Advarsel | Årsak | Trygt å ignorere? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes har ingen Windows ROCm-build | Ja — denne oppskriften bruker `adamw_torch`, ikke bnb |
| `No ROCm platform found for torch.distributed` | ROCm på Windows mangler distribuert trening | Ja — enkelt-GPU-trening påvirkes ikke |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth flagger ikke-Linux-builder | Ja — Windows ROCm fungerer for enkelt-GPU SFT |
| `triton is not available` | Triton har ingen Windows-build | Ja — Unsloth faller tilbake til PyTorch-kjerner |

Treningen vil fortsette korrekt til tross for disse advarslene.
<!-- @os:end -->

## Neste steg
- Prøv [Unsloth Studio](https://unsloth.ai/docs/new/studio), et intuitivt GUI for Unsloth
- Tren på dine egne spesifikke datasett
- Prøv finjustering med forskjellige hyperparametere
- Distribuer med vLLM eller llama.cpp
- Prøv QLoRA for et oppsett med lavere minnebruk

## Ressurser

Nedenfor er noen ytterligere ressurser for å lære mer om Unsloth og finjustering:

* [Unsloth Docs](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth Fine-tuning Guide](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)