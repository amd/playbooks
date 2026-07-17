<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Översikt


Vill du köra kraftfulla AI-språkmodeller på din egen hårdvara? Den här guiden visar dig hur.
Den här handledningen använder PyTorch med AMD ROCm™-programvara för att köra modeller som kan sammanfatta dokument, besvara frågor, generera text och mycket mer – allt körs lokalt.

## Vad du kommer att lära dig

- Kör LLM:er som gpt-oss-20b och qwen3.5-4B lokalt med PyTorch och ROCm
- Skapa ett verktyg för dokumentsammanfattning med hjälp av LLM:er

## Ange minneskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sök efter programuppdateringar
> **Obs**: Om VS Code inte är installerat kan du installera det via Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installera nödvändig programvara

### Skapa en virtuell miljö

<!-- @os:linux -->
<!-- @device:halo_box -->
På Linux öppnar du en terminal i valfri katalog och följer kommandona för att skapa en venv med ROCm+Pytorch redan installerat.
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
**Ge din användare åtkomst till GPU-enheter** (logga ut och in igen för att detta ska träda i kraft):

```bash
sudo usermod -aG render,video $LOGNAME
```

På Linux öppnar du en terminal i valfri katalog och följer kommandona för att skapa en venv.
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
På Windows öppnar du en terminal i valfri katalog och följer kommandona för att skapa en venv med ROCm+Pytorch redan installerat.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
På Windows öppnar du en terminal i valfri katalog och följer kommandona för att skapa en venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Tips**: Windows-användare kan behöva ändra sin PowerShell-körningspolicy (t.ex.
> ange den till RemoteSigned eller Unrestricted) innan vissa PowerShell-kommandon körs.

<!-- @os:end -->

### Installera grundläggande beroenden
<!-- @require:driver,pytorch -->

### Installera ytterligare beroenden

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

## Snabbstart med exempelskript

Det här playbook-et innehåller färdiga skript. Klicka på dem för att förhandsgranska och ladda ned dem till samma katalog som den miljö du skapade.

| Skript | Beskrivning | Användning |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Grundläggande LLM-textgenerering | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Dokumentsammanfattare med Harmony-stöd | `python summarizer.py --file document.txt` |

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

Båda skripten stöder:
- Modellval via flaggan `--model`
- Formatering av chattmall för korrekt modellpromptning, särskilt användbart vid dokumentsammanfattning

## Ladda och kör din första LLM

Det inkluderade skriptet [run_llm.py](assets/run_llm.py) visar hur man genererar text med LLM:er med hjälp av PyTorch och AMD ROCm.

> **Obs:** När du laddar en modell kontrollerar Hugging Face Transformers först sin lokala cache (`~/.cache/huggingface/hub` på Linux, `C:\Users\<user>\.cache\huggingface\hub` på Windows). Om modellen inte finns i cachen laddas den ned automatiskt från huggingface.co. Den första körningen kan ta några minuter beroende på modellstorlek och nätverkshastighet.

Utdraget nedan visar hur du använder modellen och anpassar de frågor som ställs.

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

Prova det nedladdade skriptet:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Bygga en dokumentsammanfattare

Nu när du har genererat lokal LLM-utdata kan du bygga vidare på det genom att skapa ett praktiskt verktyg för dokumentsammanfattning. I det här avsnittet använder du skriptet [summarizer.py](assets/summarizer.py) för att mata in en .txt-fil och automatiskt generera en kortfattad sammanfattning – allt körs lokalt på din GPU.

Skriptet är utformat för att fungera direkt. Öppna skriptet i en editor för att utforska koden, anpassa promptar och justera parametrar som längd och temperatur.

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### Användningsexempel

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

## Lär dig om genereringsparametrar

| Parameter | Vad den styr | Typiska värden |
|-----------|------------------|----------------|
| `max_new_tokens` | Den maximala längden på LLM:ens utdata | Använd 50–500 tokens för sammanfattningar. (1 token motsvarar ungefär 0,75 engelska ord) |
| `temperature` | Kreativitet. Låga värden ger fokuserade svar, medan höga värden ger mer oförutsägbarhet | - **0.1–0.3**: Fokuserat, deterministiskt (bra för sammanfattningar) <br> **0.5–0.7**: Balanserat (allmänt bruk) <br> **0.8–1.0**: Kreativt, varierat (idégenerering) |
| `top_p` | Kärnsampning – låga värden begränsar modellen till smalare utdata | **0.1-0.5**: Strikt, förutsägbart <br> **0.9-0.95**: (standard, naturligt, konversationsmässigt) |


## Verkliga tillämpningar

- **Analys av forskningsartiklar**: Extrahera viktiga resultat från komplexa publikationer för snabb genomgång
- **Nyhetsaggregering**: Sammanfatta nyhetsartiklar till korta dagliga sammanfattningar eller höjdpunkter
- **Mötesanteckningar**: Kondensera utskrifter till åtgärdspunkter och kortfattade sammanfattningar
- **Granskning av juridiska dokument**: Extrahera relevanta klausuler eller skyldigheter från långa juridiska texter snabbt
- **Koddokumentation**: Generera kortfattade repositoryöversikter och funktionsförklaringar

## Nästa steg

- **Finjustering**: Anpassa modeller till ditt specifika område eller fackspråk för bättre noggrannhet (se Finjusterings-playbooks)
- **RAG-system**: Kombinera LLM:er med dokumenthämtning för kontextmedvetna svar och sökning
- **Modellutforskning**: Experimentera med nya modeller som Llama 3, Phi-3 eller Qwen för bättre resultat
- **Produktionsdriftsättning**: Använd verktyg som vLLM för skalbar LLM-hantering i organisationer

Ditt system ger dig möjligheten att köra sofistikerade språkmodeller lokalt. Experimentera med olika modeller, promptar och parametrar för att upptäcka vad som fungerar bäst för dina tillämpningar.