<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Pregled


Želite da pokrenete moćne AI jezičke modele na sopstvenom hardveru? Ovaj vodič vam pokazuje kako.
Ovaj tutorijal koristi PyTorch pokrenut AMD ROCm™ softverom za pokretanje modela koji mogu da sumiraju dokumente, odgovaraju na pitanja, generišu tekst i još mnogo toga – sve lokalno.

## Šta ćete naučiti

- Pokrenite LLM-ove poput gpt-oss-20b i qwen3.5-4B lokalno koristeći PyTorch i ROCm
- Napravite alat za sumarizaciju dokumenata koristeći LLM-ove

## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Proverite softverska ažuriranja
> **Napomena**: Ako VS Code nije instaliran, možete ga instalirati putem Ryzen AI Developer Center-a.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalacija softverskih preduslova

### Kreiranje virtuelnog okruženja

<!-- @os:linux -->
<!-- @device:halo_box -->
Na Linux-u, otvorite terminal u direktorijumu po vašem izboru i pratite komande za kreiranje venv-a sa već instaliranim ROCm+Pytorch.
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
**Dodelite svom korisniku pristup GPU uređajima** (odjavite se i ponovo prijavite da bi ovo stupilo na snagu):

```bash
sudo usermod -aG render,video $LOGNAME
```

Na Linux-u, otvorite terminal u direktorijumu po vašem izboru i pratite komande za kreiranje venv-a.
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
Na Windows-u, otvorite terminal u direktorijumu po vašem izboru i pratite komande za kreiranje venv-a sa već instaliranim ROCm+Pytorch.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Na Windows-u, otvorite terminal u direktorijumu po vašem izboru i pratite komande za kreiranje venv-a.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Savet**: Korisnici Windows-a možda će morati da izmene PowerShell politiku izvršavanja (npr.
> postavljanjem na RemoteSigned ili Unrestricted) pre pokretanja nekih Powershell komandi.

<!-- @os:end -->

### Instalacija osnovnih zavisnosti
<!-- @require:driver,pytorch -->

### Instalacija dodatnih zavisnosti

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

## Brzi početak sa primerima skripti

Ovaj playbook uključuje skripte spremne za upotrebu. Kliknite na njih da biste pregledali i preuzeli ih u isti direktorijum u kome ste kreirali okruženje.

| Skripta | Opis | Upotreba |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Osnovno generisanje teksta pomoću LLM-a | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Sumarizator dokumenata sa podrškom za Harmony | `python summarizer.py --file document.txt` |

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

Obe skripte podržavaju:
- Izbor modela putem zastavice `--model`
- Formatiranje šablona za razgovor radi ispravnog zadavanja upita modelu, posebno korisno za sumarizaciju dokumenata

## Učitavanje i pokretanje vašeg prvog LLM-a

Priložena skripta [run_llm.py](assets/run_llm.py) pokazuje kako da generišete tekst pomoću LLM-ova koristeći PyTorch i AMD ROCm.

> **Napomena:** Kada učitate model, Hugging Face Transformers najpre proverava lokalni keš (`~/.cache/huggingface/hub` na Linux-u, `C:\Users\<user>\.cache\huggingface\hub` na Windows-u). Ako model nije keširan, automatski se preuzima sa huggingface.co. Prvo pokretanje može potrajati nekoliko minuta u zavisnosti od veličine modela i brzine mreže.

Isečak ispod pokazuje kako da koristite model i prilagodite postavljena pitanja.

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

Isprobajte preuzetu skriptu:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Pravljenje sumarizatora dokumenata

Sada kada ste generisali lokalni LLM izlaz, možete to nadograditi pravljenjem praktičnog sumarizatora dokumenata. U ovom odeljku ćete koristiti skriptu [summarizer.py](assets/summarizer.py) da unesete .txt fajl i automatski generišete sažet rezime – sve lokalno na vašem GPU-u.

Skripta je dizajnirana da radi odmah po preuzimanju. Otvorite skriptu u editoru da biste istražili kod, prilagodili upite i podesili parametre poput dužine i temperature.

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### Primeri upotrebe

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

## Saznajte više o parametrima generisanja

| Parametar | Šta kontroliše | Tipične vrednosti |
|-----------|------------------|----------------|
| `max_new_tokens` | Maksimalna dužina izlaza LLM-a | Koristite 50–500 tokena za rezimee. (1 token je otprilike 0,75 engleskih reči) |
| `temperature` | Kreativnost. Niske vrednosti čine izlaz fokusiranim, dok visoke vrednosti donose veću nepredvidivost | - **0.1–0.3**: Fokusiran, determinističan (dobro za rezimee) <br> **0.5–0.7**: Uravnotežen (opšta upotreba) <br> **0.8–1.0**: Kreativan, raznovrstan (brainstorming) |
| `top_p` | Nucleus uzorkovanje – niske vrednosti ograničavaju model na uže izlaze | **0.1-0.5**: Strogo, predvidivo <br> **0.9-0.95**: (standardno, prirodno, konverzacijsko) |


## Primene u stvarnom svetu

- **Analiza naučnih radova**: Izvucite ključne nalaze iz složenih publikacija radi brzog pregleda
- **Agregacija vesti**: Sumirajte novinske članke u kratke dnevne preglede ili istaknute tačke
- **Beleške sa sastanaka**: Kondenzujte transkripte u akcione stavke i sažete rezimee
- **Pregled pravnih dokumenata**: Brzo izvucite relevantne klauzule ili obaveze iz dugih pravnih tekstova
- **Dokumentacija koda**: Generišite sažete preglede repozitorijuma i objašnjenja funkcija

## Sledeći koraci

- **Fino podešavanje**: Prilagodite modele vašoj specifičnoj oblasti ili žargonu radi bolje preciznosti (pogledajte Playbook-ove za fino podešavanje)
- **RAG sistemi**: Kombinujte LLM-ove sa preuzimanjem dokumenata radi odgovora i pretrage svesnih konteksta
- **Istraživanje modela**: Eksperimentišite sa novim modelima poput Llama 3, Phi-3 ili Qwen za bolje rezultate
- **Produkcijsko postavljanje**: Koristite alate poput vLLM za skalabilno posluživanje LLM-ova u organizacijama

Vaš sistem vam daje moć da lokalno pokrenete sofisticirane jezičke modele. Eksperimentišite sa različitim modelima, upitima i parametrima kako biste otkrili šta najbolje funkcioniše za vaše primene.