<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Overzicht


Wilt u krachtige AI-taalmodellen op uw eigen hardware uitvoeren? Deze handleiding laat u zien hoe.
Deze tutorial gebruikt PyTorch aangedreven door AMD ROCm™-software om modellen uit te voeren die documenten kunnen samenvatten, vragen kunnen beantwoorden, tekst kunnen genereren en meer, allemaal lokaal uitgevoerd.

## Wat U Leert

- LLM's zoals gpt-oss-20b en qwen3.5-4B lokaal uitvoeren met PyTorch en ROCm
- Een tool voor het samenvatten van documenten maken met behulp van LLM's

## De Geheugenconfiguratie Instellen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Controleren op Software-updates
> **Opmerking**: Als VS Code niet is geïnstalleerd, kunt u het installeren via het Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Software-vereisten Installeren

### Een Virtuele Omgeving Aanmaken

<!-- @os:linux -->
<!-- @device:halo_box -->
Open op Linux een terminal in de map van uw keuze en volg de opdrachten om een venv aan te maken met ROCm+Pytorch al geïnstalleerd.
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
**Verleen uw gebruiker toegang tot GPU-apparaten** (log uit en weer in om dit van kracht te laten worden):

```bash
sudo usermod -aG render,video $LOGNAME
```

Open op Linux een terminal in de map van uw keuze en volg de opdrachten om een venv aan te maken.
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
Open op Windows een terminal in de map van uw keuze en volg de opdrachten om een venv aan te maken met ROCm+Pytorch al geïnstalleerd.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Open op Windows een terminal in de map van uw keuze en volg de opdrachten om een venv aan te maken.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Tip**: Windows-gebruikers moeten mogelijk hun PowerShell-uitvoeringsbeleid aanpassen (bijv.
> instellen op RemoteSigned of Unrestricted) voordat ze bepaalde PowerShell-opdrachten uitvoeren.

<!-- @os:end -->

### Basisafhankelijkheden Installeren
<!-- @require:driver,pytorch -->

### Aanvullende Afhankelijkheden Installeren

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

## Snel Starten met Voorbeeldscripts

Dit playbook bevat kant-en-klare scripts. Klik erop om ze te bekijken en download ze naar dezelfde map als de omgeving die u hebt aangemaakt.

| Script | Beschrijving | Gebruik |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Basistekstgeneratie met LLM | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Documentsamenvatting met Harmony-ondersteuning | `python summarizer.py --file document.txt` |

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

Beide scripts ondersteunen:
- Modelselectie via de `--model`-vlag
- Opmaak van chatsjablonen voor correcte modelprompting, vooral nuttig voor het samenvatten van documenten

## Uw Eerste LLM Laden en Uitvoeren

Het meegeleverde script [run_llm.py](assets/run_llm.py) laat zien hoe u tekst kunt genereren met LLM's via PyTorch en AMD ROCm.

> **Opmerking:** Wanneer u een model laadt, controleert Hugging Face Transformers eerst de lokale cache (`~/.cache/huggingface/hub` op Linux, `C:\Users\<user>\.cache\huggingface\hub` op Windows). Als het model niet in de cache staat, wordt het automatisch gedownload van huggingface.co. De eerste uitvoering kan enkele minuten duren, afhankelijk van de modelgrootte en netwerksnelheid.

Het onderstaande fragment laat zien hoe u het model kunt gebruiken en de gestelde vragen kunt aanpassen.

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

Probeer het gedownloade script uit:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Een Documentsamenvatting Bouwen

Nu u lokale LLM-uitvoer hebt gegenereerd, kunt u daarop voortbouwen door een praktische documentsamenvatting te maken. In dit gedeelte gebruikt u het script [summarizer.py](assets/summarizer.py) om een .txt-bestand in te voeren en automatisch een beknopte samenvatting te genereren, allemaal lokaal uitgevoerd op uw GPU.

Het script is ontworpen om direct te werken. Open het script in een editor om de code te verkennen, prompts aan te passen en parameters zoals lengte en temperatuur te verfijnen.

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### Gebruiksvoorbeelden

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

## Meer Informatie over Generatieparameters

| Parameter | Wat Het Regelt | Typische Waarden |
|-----------|------------------|----------------|
| `max_new_tokens` | De maximale lengte van de uitvoer van de LLM | Gebruik 50–500 tokens voor samenvattingen. (1 token is ongeveer 0,75 Engelse woorden) |
| `temperature` | Creativiteit. Lage waarden maken het gefocust, terwijl hoge waarden meer onvoorspelbaarheid met zich meebrengen | - **0.1–0.3**: Gefocust, deterministisch (goed voor samenvattingen) <br> **0.5–0.7**: Gebalanceerd (algemeen gebruik) <br> **0.8–1.0**: Creatief, gevarieerd (brainstormen) |
| `top_p` | Nucleus Sampling - Lage waarden beperken het model tot engere uitvoer | **0.1-0.5**: Strikt, voorspelbaar <br> **0.9-0.95**: (standaard, natuurlijk, conversationeel) |


## Toepassingen in de Praktijk

- **Analyse van Onderzoeksartikelen**: Extraheer belangrijke bevindingen uit complexe publicaties voor snelle beoordeling
- **Nieuwsaggregatie**: Vat nieuwsartikelen samen tot beknopte dagelijkse overzichten of hoogtepunten
- **Vergadernotities**: Verdicht transcripties tot actiepunten en beknopte samenvattingen
- **Beoordeling van Juridische Documenten**: Extraheer snel relevante clausules of verplichtingen uit lange juridische teksten
- **Codedocumentatie**: Genereer beknopte repository-overzichten en functietoelichtingen

## Volgende Stappen

- **Fijnafstelling**: Pas modellen aan uw specifieke vakgebied of jargon aan voor betere nauwkeurigheid (zie Fine-tuning Playbooks)
- **RAG-systemen**: Combineer LLM's met documentophaling voor contextbewuste antwoorden en zoekopdrachten
- **Modelverkenning**: Experimenteer met nieuwe modellen zoals Llama 3, Phi-3 of Qwen voor betere resultaten
- **Productie-implementatie**: Gebruik tools zoals vLLM voor schaalbare LLM-dienstverlening in organisaties

Uw systeem geeft u de mogelijkheid om geavanceerde taalmodellen lokaal uit te voeren. Experimenteer met verschillende modellen, prompts en parameters om te ontdekken wat het beste werkt voor uw toepassingen.