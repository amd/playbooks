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


Wilt u krachtige AI-taalmodellen op uw eigen hardware uitvoeren? Deze handleiding laat u zien hoe.
In deze tutorial wordt PyTorch gebruikt, aangedreven door AMD ROCm™-software, om modellen uit te voeren die documenten kunnen samenvatten, vragen kunnen beantwoorden, tekst kunnen genereren en meer, allemaal lokaal uitgevoerd.

## Wat u gaat leren

- Voer LLM's zoals gpt-oss-20b en qwen3.5-4B lokaal uit met behulp van PyTorch en ROCm
- Maak een documentsamenvattingstool met LLM's

<!-- @device:halo_box,halo,stx,krk -->
## Het geheugen configureren

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Controleren op software-updates
> **Opmerking**: Als VS Code niet is geïnstalleerd, kunt u het installeren via het Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## De vereiste software installeren

### Een virtuele omgeving maken

<!-- @os:linux -->
<!-- @device:halo_box -->
Open op Linux een terminal in de map van uw keuze en volg de commando's om een venv te maken met ROCm+PyTorch al geïnstalleerd.
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
**Geef uw gebruiker toegang tot GPU-apparaten** (log uit en weer in om dit effect te laten hebben):

```bash
sudo usermod -aG render,video $LOGNAME
```

Open op Linux een terminal in de map van uw keuze en volg de commando's om een venv te maken.
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
Open op Windows een terminal in de map van uw keuze en volg de commando's om een venv te maken met ROCm+PyTorch al geïnstalleerd.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Open op Windows een terminal in de map van uw keuze en volg de commando's om een venv te maken.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Tip**: Windows-gebruikers moeten mogelijk hun PowerShell Execution Policy aanpassen (bijvoorbeeld
> door deze in te stellen op RemoteSigned of Unrestricted) voordat ze sommige PowerShell-commando's uitvoeren.

<!-- @os:end -->

### Basisafhankelijkheden installeren
<!-- @require:driver,pytorch -->

### Aanvullende afhankelijkheden installeren

<!-- @var:id=hf_model device=halo,halo_box value="openai/gpt-oss-20b" -->
<!-- @var:id=hf_model device=stx,krk,rx7900xt,rx9070xt,r9700 value="Qwen/Qwen3.5-4B" -->
<!-- @device:halo,halo_box -->
<!-- @prereq:hf-models-gpt-oss-20b -->
<!-- @device:end -->
<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @prereq:hf-models-qwen3-5-4b -->
<!-- @device:end -->

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

> **Opmerking:** Als het model niet laadt of zonder geheugen komt te zitten, probeer dan het `kernels`-pakket te installeren om het model te laden met geoptimaliseerde kwantisering.
>
> ```bash
> # Gebruik deze versie, die compatibel is met de Transformers-versie
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

## Snel starten met voorbeeldscripts

Deze playbook bevat kant-en-klare scripts. Klik erop om ze te bekijken en te downloaden naar dezelfde map als de omgeving die u hebt gemaakt.

| Script | Beschrijving | Gebruik |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Basis LLM-tekstgeneratie | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Documentsamenvatter met Harmony-ondersteuning | `python summarizer.py --file document.txt` |

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
- Chatsjabloonopmaak voor correcte modelprompting, vooral nuttig voor documentsamenvatting

## Uw eerste LLM laden en uitvoeren

Het meegeleverde script [run_llm.py](assets/run_llm.py) laat zien hoe u tekst kunt genereren met LLM's met behulp van PyTorch en AMD ROCm.

> **Opmerking:** Wanneer u een model laadt, controleert Hugging Face Transformers eerst de lokale cache (`~/.cache/huggingface/hub` op Linux, `C:\Users\<user>\.cache\huggingface\hub` op Windows). Als het model niet in de cache staat, wordt het automatisch gedownload van huggingface.co. De eerste keer uitvoeren kan enkele minuten duren, afhankelijk van de modelgrootte en netwerksnelheid.

Het onderstaande fragment laat zien hoe u het model kunt gebruiken en de gestelde vragen kunt aanpassen.

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

Probeer het gedownloade script uit:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Een documentsamenvatter bouwen

Nu u lokale LLM-output hebt gegenereerd, kunt u hierop voortbouwen door een praktische documentsamenvatter te maken. In dit gedeelte gebruikt u het script [summarizer.py](assets/summarizer.py) om een .txt-bestand in te voeren en automatisch een beknopte samenvatting te genereren, allemaal lokaal uitgevoerd op uw GPU.

Het script is ontworpen om direct te werken. Open het script in een editor om de code te verkennen, prompts aan te passen en parameters zoals lengte en temperatuur bij te stellen.

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

## Meer informatie over generatieparameters

| Parameter | Wat het bepaalt | Typische waarden |
|-----------|------------------|----------------|
| `max_new_tokens` | De maximale lengte van de output van de LLM | Gebruik 50–500 tokens voor samenvattingen. (1 token is ongeveer 0,75 Engelse woorden) |
| `temperature` | Creativiteit. Lage waarden maken het gefocust, hoge waarden zorgen voor meer onvoorspelbaarheid | - **0,1–0,3**: Gefocust, deterministisch (goed voor samenvattingen) <br> **0,5–0,7**: Gebalanceerd (algemeen gebruik) <br> **0,8–1,0**: Creatief, gevarieerd (brainstormen) |
| `top_p` | Nucleus Sampling - Lage waarden beperken het model tot nauwere uitvoer | **0,1-0,5**: Strikt, voorspelbaar <br> **0,9-0,95**: (standaard, natuurlijk, conversatieel) |


## Toepassingen in de praktijk

- **Analyse van onderzoekspublicaties**: Haal belangrijke bevindingen uit complexe publicaties voor snelle beoordeling
- **Nieuwsaggregatie**: Vat nieuwsartikelen samen tot korte dagelijkse overzichten of hoogtepunten
- **Vergadernotities**: Comprimeer transcripten tot actiepunten en beknopte samenvattingen
- **Beoordeling van juridische documenten**: Haal snel relevante clausules of verplichtingen uit lange juridische teksten
- **Codedocumentatie**: Genereer beknopte overzichten van repositories en uitleg van functies
## Volgende stappen

- **Fine-tuning**: Pas modellen aan voor uw specifieke vakgebied of terminologie voor betere nauwkeurigheid (zie Fine-tuning Playbooks)
- **RAG-systemen**: Combineer LLM's met documentophaling voor contextbewuste antwoorden en zoekfunctionaliteit
- **Modelverkenning**: Experimenteer met nieuwe modellen zoals Llama 3, Phi-3 of Qwen voor betere resultaten
- **Productie-implementatie**: Gebruik tools zoals vLLM voor schaalbare LLM-serving in organisaties

Uw systeem geeft u de kracht om geavanceerde taalmodellen lokaal uit te voeren. Experimenteer met verschillende modellen, prompts en parameters om te ontdekken wat het beste werkt voor uw toepassingen.