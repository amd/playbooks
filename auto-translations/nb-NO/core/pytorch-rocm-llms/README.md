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


Ønsker du å kjøre kraftige AI-språkmodeller på din egen maskinvare? Denne veiledningen viser deg hvordan.
Denne opplæringen bruker PyTorch drevet av AMD ROCm™-programvare til å kjøre modeller som kan oppsummere dokumenter, svare på spørsmål, generere tekst og mer, alt kjørende lokalt.

## Hva du vil lære

- Kjøre LLM-er som gpt-oss-20b og qwen3.5-4B lokalt ved hjelp av PyTorch og ROCm
- Opprette et verktøy for dokumentoppsummering ved hjelp av LLM-er

<!-- @device:halo_box,halo,stx,krk -->
## Angi minnekonfigurasjonen

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Se etter programvareoppdateringer
> **Merk**: Hvis VS Code ikke er installert, kan du installere det med Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installere nødvendig programvare

### Opprette et virtuelt miljø

<!-- @os:linux -->
<!-- @device:halo_box -->
På Linux åpner du en terminal i mappen du ønsker, og følger kommandoene for å opprette et venv med ROCm+PyTorch allerede installert.
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env --system-site-packages
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Gi brukeren din tilgang til GPU-enheter** (logg ut og inn igjen for at dette skal tre i kraft):

```bash
sudo usermod -aG render,video $LOGNAME
```

På Linux åpner du en terminal i mappen du ønsker, og følger kommandoene for å opprette et venv.
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv pytorch-env
source pytorch-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source pytorch-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->


<!-- @os:windows -->
<!-- @device:halo_box -->
På Windows åpner du en terminal i mappen du ønsker, og følger kommandoene for å opprette et venv med ROCm+PyTorch allerede installert.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
På Windows åpner du en terminal i mappen du ønsker, og følger kommandoene for å opprette et venv.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Tips**: Windows-brukere må kanskje endre sin PowerShell Execution Policy (f.eks.
> sette den til RemoteSigned eller Unrestricted) før de kjører enkelte PowerShell-kommandoer.

<!-- @os:end -->

### Installere grunnleggende avhengigheter
<!-- @require:driver,pytorch -->

### Installere ytterligere avhengigheter

<!-- @var:id=hf_model device=halo,halo_box value="openai/gpt-oss-20b" -->
<!-- @var:id=hf_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen/Qwen3.5-4B" -->

<!-- @device:halo,halo_box -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

> **Merk:** Hvis modellen ikke lastes eller går tom for minne, kan du prøve å installere `kernels`-pakken for å laste modellen med optimalisert kvantisering.
>
> ```bash
> # Bruk denne versjonen som er kompatibel med Transformers-versjonen
> pip install "kernels==0.14.1" 
> ```
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

## Kom raskt i gang med eksempelskript

Denne veiledningen inneholder ferdige skript du kan bruke direkte. Klikk på dem for å forhåndsvise og laste dem ned til samme mappe som miljøet du opprettet.

| Skript | Beskrivelse | Bruk |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Grunnleggende tekstgenerering med LLM | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Dokumentoppsummerer med Harmony-støtte | `python summarizer.py --file document.txt` |

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['run_llm.py', 'summarizer.py', 'example_document.txt']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in ['run_llm.py', 'summarizer.py']:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

Begge skriptene støtter:
- Modellvalg via `--model`-flagget
- Formatering av samtalemaler for riktig utforming av modellprompter, spesielt nyttig for dokumentoppsummering

## Laste inn og kjøre din første LLM

Det medfølgende [run_llm.py](assets/run_llm.py)-skriptet viser hvordan du genererer tekst med LLM-er ved hjelp av PyTorch og AMD ROCm.

> **Merk:** Når du laster inn en modell, sjekker Hugging Face Transformers først den lokale hurtigbufferen (`~/.cache/huggingface/hub` på Linux, `C:\Users\<user>\.cache\huggingface\hub` på Windows). Hvis modellen ikke er bufret, lastes den automatisk ned fra huggingface.co. Den første kjøringen kan ta noen minutter avhengig av modellstørrelse og nettverkshastighet.

Utdraget nedenfor viser hvordan du bruker modellen og tilpasser spørsmålene som stilles.

<!-- @test:id=verify-imports timeout=300 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA/ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    disable_mmap=True
)
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=run-model timeout=600 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForImageTextToText

model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForImageTextToText.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```
<!-- @test:end -->
<!-- @device:end -->

```python
model_name = "${hf_model}"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

# Create system and user prompts
prompt = "Explain what a large language model is in 2 brief sentences."
print(f"Prompt: {prompt}\n")

messages = [
    {"role": "system", "content": "You are a helpful technology assistant"},
    {"role": "user", "content": f"{prompt}"},
]
```

Prøv ut det nedlastede skriptet:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Bygge en dokumentoppsummerer

Nå som du har generert LLM-utdata lokalt, kan du bygge videre på dette ved å lage en praktisk dokumentoppsummerer. I denne delen bruker du skriptet [summarizer.py](assets/summarizer.py) til å mate inn en .txt-fil og automatisk generere et konsist sammendrag, alt kjørende lokalt på GPU-en din.

Skriptet er designet for å fungere uten videre. Åpne skriptet i en editor for å utforske koden, tilpasse prompter og justere parametere som lengde og temperatur.

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### Brukseksempler

```bash
# Summarize the built-in example text (defaults to openai/gpt-oss-20b)
python summarizer.py --model ${hf_model}

# Summarize a text file
python summarizer.py --file example_document.txt

# Adjust creativity with temperature
python summarizer.py --file document.txt --temperature 0.5

# Longer summaries with more tokens
python summarizer.py --file document.txt --max-length 400
```

## Lær om genereringsparametere

| Parameter | Hva den kontrollerer | Typiske verdier |
|-----------|------------------|----------------|
| `max_new_tokens` | Maksimal lengde på LLM-ens utdata | Bruk 50–500 tokens for sammendrag. (1 token tilsvarer omtrent 0,75 engelske ord) |
| `temperature` | Kreativitet. Lave verdier gjør den fokusert, mens høye verdier gir mer uforutsigbarhet | - **0,1–0,3**: Fokusert, deterministisk (bra for sammendrag) <br> **0,5–0,7**: Balansert (generell bruk) <br> **0,8–1,0**: Kreativ, variert (idémyldring) |
| `top_p` | Nucleus Sampling – Lave verdier begrenser modellen til smalere utdata | **0,1-0,5**: Streng, forutsigbar <br> **0,9-0,95**: (standard, naturlig, samtalepreget) |


## Bruk i den virkelige verden

- **Analyse av forskningsartikler**: Trekk ut viktige funn fra komplekse publikasjoner for rask gjennomgang
- **Nyhetssamling**: Oppsummer nyhetsartikler til korte daglige sammendrag eller høydepunkter
- **Møtenotater**: Komprimer transkripsjoner til handlingspunkter og konsise sammendrag
- **Gjennomgang av juridiske dokumenter**: Trekk raskt ut relevante klausuler eller forpliktelser fra lange juridiske tekster
- **Kodedokumentasjon**: Generer konsise oversikter over kodelagre og funksjonsforklaringer
## Neste steg

- **Finjustering**: Tilpass modeller til ditt spesifikke fagfelt eller sjargong for bedre nøyaktighet (se Fine-tuning Playbooks)
- **RAG-systemer**: Kombiner LLM-er med dokumenthenting for kontekstbevisste svar og søk
- **Modellutforskning**: Eksperimenter med nye modeller som Llama 3, Phi-3 eller Qwen for bedre resultater
- **Produksjonsdistribusjon**: Bruk verktøy som vLLM for skalerbar LLM-tjenering i organisasjoner

Systemet ditt gir deg kraften til å kjøre sofistikerte språkmodeller lokalt. Eksperimenter med ulike modeller, prompter og parametere for å finne ut hva som fungerer best for dine bruksområder.