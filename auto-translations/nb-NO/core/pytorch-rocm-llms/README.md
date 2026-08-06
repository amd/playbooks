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


Vil du kjøre kraftige KI-språkmodeller på din egen maskinvare? Denne veiledningen viser deg hvordan.
Denne opplæringen bruker PyTorch drevet av AMD ROCm™-programvare til å kjøre modeller som kan oppsummere dokumenter, svare på spørsmål, generere tekst og mer, alt kjørende lokalt.

## Hva du vil lære

- Kjør LLM-er som gpt-oss-20b og qwen3.5-4B lokalt ved hjelp av PyTorch og ROCm
- Opprett et verktøy for dokumentoppsummering ved hjelp av LLM-er

## Angi minnekonfigurasjonen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sjekk etter programvareoppdateringer
> **Merk**: Hvis VS Code ikke er installert, kan du installere det med Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installere programvareforutsetninger

### Opprett et virtuelt miljø

<!-- @os:linux -->
<!-- @device:halo_box -->
På Linux åpner du en terminal i mappen du ønsker, og følger kommandoene for å opprette et venv med ROCm+Pytorch allerede installert.
<!-- @test:id=create-venv timeout=120 -->
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
<!-- @test:id=create-venv timeout=120 -->
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
På Windows åpner du en terminal i mappen du ønsker, og følger kommandoene for å opprette et venv med ROCm+Pytorch allerede installert.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
På Windows åpner du en terminal i mappen du ønsker, og følger kommandoene for å opprette et venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Tips**: Windows-brukere må kanskje endre PowerShell-utførelsespolicyen sin (for eksempel
> ved å sette den til RemoteSigned eller Unrestricted) før de kjører enkelte PowerShell-kommandoer.

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
pip install transformers==4.57.1 safetensors==0.6.2 accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
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
pip install "transformers>=5.9.0" safetensors accelerate sentencepiece protobuf
```
<!-- @test:end -->
<!-- @os:end -->
<!-- @device:end -->

## Hurtigstart med eksempelskript

Denne veiledningen inneholder skript som er klare til bruk. Klikk på dem for å forhåndsvise og laste dem ned til samme mappe som miljøet du opprettet.

| Skript | Beskrivelse | Bruk |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Grunnleggende LLM-tekstgenerering | `python run_llm.py` |
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
- Modellvalg via flagget `--model`
- Formatering av chat-mal for riktig modellinstruksjon, spesielt nyttig for dokumentoppsummering

## Laste inn og kjøre din første LLM

Det inkluderte [run_llm.py](assets/run_llm.py)-skriptet viser hvordan du genererer tekst med LLM-er ved hjelp av PyTorch og AMD ROCm.

> **Merk:** Når du laster inn en modell, sjekker Hugging Face Transformers først den lokale mellomlagringen (`~/.cache/huggingface/hub` på Linux, `C:\Users\<user>\.cache\huggingface\hub` på Windows). Hvis modellen ikke er mellomlagret, lastes den automatisk ned fra huggingface.co. Den første kjøringen kan ta noen minutter, avhengig av modellstørrelse og nettverkshastighet.

Utdraget nedenfor viser hvordan du bruker modellen og tilpasser spørsmålene som stilles.

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
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
    device_map="auto"
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

Nå som du har generert lokal LLM-utdata, kan du bygge videre på dette ved å lage en praktisk dokumentoppsummerer. I denne delen skal du bruke [summarizer.py](assets/summarizer.py)-skriptet til å mate inn en .txt-fil og automatisk generere et konsist sammendrag, alt kjørende lokalt på GPU-en din.

Skriptet er utformet for å fungere rett ut av boksen. Åpne skriptet i en editor for å utforske koden, tilpasse spørringer og justere parametere som lengde og temperatur.

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
| `max_new_tokens` | Maksimal lengde på LLM-ens utdata | Bruk 50–500 token for sammendrag. (1 token tilsvarer omtrent 0,75 engelske ord) |
| `temperature` | Kreativitet. Lave verdier gjør den fokusert, mens høye verdier gir mer uforutsigbarhet | - **0,1–0,3**: Fokusert, deterministisk (bra for sammendrag) <br> **0,5–0,7**: Balansert (generell bruk) <br> **0,8–1,0**: Kreativ, variert (idémyldring) |
| `top_p` | Nucleus Sampling - Lave verdier begrenser modellen til smalere utdata | **0,1-0,5**: Streng, forutsigbar <br> **0,9-0,95**: (standard, naturlig, samtalepreget) |


## Bruksområder i praksis

- **Analyse av forskningsartikler**: Trekk ut viktige funn fra komplekse publikasjoner for rask gjennomgang
- **Nyhetsaggregering**: Oppsummer nyhetsartikler til korte daglige sammendrag eller høydepunkter
- **Møtenotater**: Kondenser transkripsjoner til handlingspunkter og konsise sammendrag
- **Gjennomgang av juridiske dokumenter**: Trekk raskt ut relevante klausuler eller forpliktelser fra lange juridiske tekster
- **Kodedokumentasjon**: Generer konsise oversikter over repositorier og funksjonsforklaringer

## Neste steg

- **Finjustering**: Tilpass modeller til ditt spesifikke felt eller fagterminologi for bedre nøyaktighet (se veiledninger for finjustering)
- **RAG-systemer**: Kombiner LLM-er med dokumenthenting for kontekstbevisste svar og søk
- **Modellutforskning**: Eksperimenter med nye modeller som Llama 3, Phi-3 eller Qwen for bedre resultater
- **Produksjonsdistribusjon**: Bruk verktøy som vLLM for skalerbar LLM-tjeneste i organisasjoner

Systemet ditt gir deg muligheten til å kjøre avanserte språkmodeller lokalt. Eksperimenter med forskjellige modeller, spørringer og parametere for å finne ut hva som fungerer best for dine bruksområder.