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


Vil du køre kraftfulde AI-sprogmodeller på din egen hardware? Denne guide viser dig hvordan.
Denne vejledning bruger PyTorch drevet af AMD ROCm™-software til at køre modeller, der kan opsummere dokumenter, besvare spørgsmål, generere tekst og meget mere, alt sammen kørende lokalt.

## Hvad du vil lære

- Kør LLM'er som gpt-oss-20b og qwen3.5-4B lokalt ved hjælp af PyTorch og ROCm
- Opret et værktøj til dokumentopsummering ved hjælp af LLM'er

<!-- @device:halo_box,halo,stx,krk -->
## Indstilling af hukommelseskonfigurationen

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Tjek for softwareopdateringer
> **Bemærk**: Hvis VS Code ikke er installeret, kan du installere det med Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installation af softwareforudsætninger

### Opret et virtuelt miljø

<!-- @os:linux -->
<!-- @device:halo_box -->
På Linux skal du åbne en terminal i den mappe, du ønsker, og følge kommandoerne for at oprette et venv med ROCm+Pytorch allerede installeret.
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
**Giv din bruger adgang til GPU-enheder** (log ud og ind igen for at dette træder i kraft):

```bash
sudo usermod -aG render,video $LOGNAME
```

På Linux skal du åbne en terminal i den mappe, du ønsker, og følge kommandoerne for at oprette et venv.
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
På Windows skal du åbne en terminal i den mappe, du ønsker, og følge kommandoerne for at oprette et venv med ROCm+Pytorch allerede installeret.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
På Windows skal du åbne en terminal i den mappe, du ønsker, og følge kommandoerne for at oprette et venv.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Tip**: Windows-brugere skal muligvis ændre deres PowerShell Execution Policy (f.eks.
> indstille den til RemoteSigned eller Unrestricted), før de kører nogle PowerShell-kommandoer.

<!-- @os:end -->

### Installation af grundlæggende afhængigheder
<!-- @require:driver,pytorch -->

### Installation af yderligere afhængigheder

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

> **Bemærk:** Hvis modellen ikke kan indlæses eller løber tør for hukommelse, kan du prøve at installere pakken `kernels` for at indlæse modellen med optimeret kvantisering.
>
> ```bash
> # Use this version which is compatible with the Transformers version
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

## Hurtig start med eksempelscripts

Denne playbook indeholder brugsklare scripts. Klik på dem for at forhåndsvise og downloade dem til samme mappe som det miljø, du har oprettet.

| Script | Beskrivelse | Anvendelse |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Grundlæggende LLM-tekstgenerering | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Dokumentopsummering med Harmony-understøttelse | `python summarizer.py --file document.txt` |

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

Begge scripts understøtter:
- Modelvalg via flaget `--model`
- Chatskabelonformatering til korrekt modelprompting, især nyttig til dokumentopsummering

## Indlæsning og kørsel af din første LLM

Det medfølgende [run_llm.py](assets/run_llm.py)-script viser, hvordan man genererer tekst med LLM'er ved hjælp af PyTorch og AMD ROCm.

> **Bemærk:** Når du indlæser en model, tjekker Hugging Face Transformers først dens lokale cache (`~/.cache/huggingface/hub` på Linux, `C:\Users\<user>\.cache\huggingface\hub` på Windows). Hvis modellen ikke er cachelagret, downloades den automatisk fra huggingface.co. Den første kørsel kan tage et par minutter afhængigt af modelstørrelse og netværkshastighed.

Uddraget nedenfor viser, hvordan man bruger modellen og tilpasser de stillede spørgsmål.

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

Prøv det downloadede script:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Opbygning af en dokumentopsummering

Nu hvor du har genereret lokal LLM-output, kan du bygge videre på dette ved at lave en praktisk dokumentopsummering. I dette afsnit vil du bruge [summarizer.py](assets/summarizer.py)-scriptet til at indlæse en .txt-fil og automatisk generere et kortfattet resumé, alt sammen kørende lokalt på din GPU.

Scriptet er designet til at fungere ud af boksen. Åbn scriptet i en editor for at udforske koden, tilpasse prompts og justere parametre som længde og temperature.

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### Eksempler på anvendelse

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

## Lær om genereringsparametre

| Parameter | Hvad den styrer | Typiske værdier |
|-----------|------------------|----------------|
| `max_new_tokens` | Den maksimale længde af LLM'ens output | Brug 50–500 tokens til resuméer. (1 token er omkring 0,75 engelske ord) |
| `temperature` | Kreativitet. Lave værdier gør den fokuseret, mens høje værdier medfører mere uforudsigelighed | - **0,1–0,3**: Fokuseret, deterministisk (godt til resuméer) <br> **0,5–0,7**: Balanceret (generel brug) <br> **0,8–1,0**: Kreativ, varieret (idéudvikling) |
| `top_p` | Nucleus Sampling - Lave værdier begrænser modellen til mere snævre output | **0,1-0,5**: Strengt, forudsigeligt <br> **0,9-0,95**: (standard, naturligt, samtalepræget) |


## Anvendelser i den virkelige verden

- **Analyse af forskningsartikler**: Udtræk vigtige resultater fra komplekse publikationer til hurtig gennemgang
- **Nyhedsaggregering**: Opsummer nyhedsartikler til korte daglige digests eller highlights
- **Mødenotater**: Kondenser transskriptioner til handlingspunkter og kortfattede resuméer
- **Gennemgang af juridiske dokumenter**: Udtræk relevante klausuler eller forpligtelser fra lange juridiske tekster hurtigt
- **Kodedokumentation**: Generer kortfattede repository-oversigter og funktionsforklaringer
## Næste skridt

- **Fine-tuning**: Tilpas modeller til dit specifikke fagområde eller jargon for bedre nøjagtighed (se Fine-tuning Playbooks)
- **RAG-systemer**: Kombinér LLM'er med dokumenthentning for kontekstbevidste svar og søgning
- **Modeludforskning**: Eksperimentér med nye modeller som Llama 3, Phi-3 eller Qwen for bedre resultater
- **Produktionsimplementering**: Brug værktøjer som vLLM til skalerbar LLM-servering i organisationer

Dit system giver dig mulighed for at køre avancerede sprogmodeller lokalt. Eksperimentér med forskellige modeller, prompts og parametre for at finde ud af, hvad der fungerer bedst til dine applikationer.