<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije proveravana od strane čoveka. Može sadržati greške, a određena uputstva, komande, preuzimanja, dostupnost proizvoda ili drugi sadržaj mogu se razlikovati u zavisnosti od jezika ili regiona. U slučaju bilo kakve nedoslednosti ili neslaganja, merodavna je originalna verzija playbook-a na engleskom jeziku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Pregled


Želite da pokrenete moćne AI jezičke modele na sopstvenom hardveru? Ovaj vodič vam pokazuje kako.
Ovaj tutorijal koristi PyTorch pokretan AMD ROCm™ softverom za pokretanje modela koji mogu da sumiraju dokumente, odgovaraju na pitanja, generišu tekst i još mnogo toga, sve lokalno.

## Šta ćete naučiti

- Pokrenite LLM-ove poput gpt-oss-20b i qwen3.5-4B lokalno koristeći PyTorch i ROCm
- Napravite alat za sumiranje dokumenata koristeći LLM-ove

## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Provera ažuriranja softvera
> **Napomena**: Ako VS Code nije instaliran, možete ga instalirati pomoću Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instaliranje neophodnog softvera

### Kreiranje virtuelnog okruženja

<!-- @os:linux -->
<!-- @device:halo_box -->
Na Linuxu, otvorite terminal u direktorijumu po izboru i pratite komande da biste kreirali venv sa već instaliranim ROCm+Pytorch.
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
**Odobrite svom korisniku pristup GPU uređajima** (odjavite se i ponovo prijavite da bi ovo stupilo na snagu):

```bash
sudo usermod -aG render,video $LOGNAME
```

Na Linuxu, otvorite terminal u direktorijumu po izboru i pratite komande da biste kreirali venv.
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
Na Windows-u, otvorite terminal u direktorijumu po izboru i pratite komande da biste kreirali venv sa već instaliranim ROCm+Pytorch.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Na Windows-u, otvorite terminal u direktorijumu po izboru i pratite komande da biste kreirali venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Savet**: Windows korisnicima će možda biti potrebno da izmene svoju PowerShell Execution Policy (npr.
> da je postave na RemoteSigned ili Unrestricted) pre pokretanja nekih Powershell komandi.

<!-- @os:end -->

### Instaliranje osnovnih zavisnosti
<!-- @require:driver,pytorch -->

### Instaliranje dodatnih zavisnosti

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

Ovaj priručnik uključuje spremne skripte za upotrebu. Kliknite na njih da biste ih pregledali i preuzeli u isti direktorijum kao okruženje koje ste kreirali.

| Skripta | Opis | Upotreba |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Osnovno generisanje teksta pomoću LLM-a | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Sumarizator dokumenata sa Harmony podrškom | `python summarizer.py --file document.txt` |

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
- Izbor modela putem `--model` opcije
- Formatiranje chat šablona za pravilno kreiranje upita ka modelu, posebno korisno za sumiranje dokumenata

## Učitavanje i pokretanje vašeg prvog LLM-a

Priložena skripta [run_llm.py](assets/run_llm.py) pokazuje kako da generišete tekst pomoću LLM-ova koristeći PyTorch i AMD ROCm.

> **Napomena:** Kada učitate model, Hugging Face Transformers prvo proverava svoj lokalni keš (`~/.cache/huggingface/hub` na Linuxu, `C:\Users\<user>\.cache\huggingface\hub` na Windows-u). Ako model nije keširan, automatski se preuzima sa huggingface.co. Prvo pokretanje može potrajati nekoliko minuta u zavisnosti od veličine modela i brzine mreže.

Isečak ispod pokazuje kako da koristite model i prilagodite pitanja koja se postavljaju.

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


## Kreiranje sumarizatora dokumenata

Sada kada ste generisali lokalni LLM izlaz, možete da nadogradite to praveći praktičan sumarizator dokumenata. U ovom odeljku, koristićete skriptu [summarizer.py](assets/summarizer.py) da unesete .txt fajl i automatski generišete sažet rezime, sve pokrenuto lokalno na vašem GPU-u.

Skripta je dizajnirana da radi odmah nakon instalacije. Otvorite skriptu u editoru da biste istražili kod, prilagodili upite i podesili parametre poput dužine i temperature.

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

## Upoznajte parametre generisanja

| Parametar | Šta kontroliše | Tipične vrednosti |
|-----------|------------------|----------------|
| `max_new_tokens` | Maksimalnu dužinu izlaza LLM-a | Koristite 50–500 tokena za rezimee. (1 token je otprilike 0,75 engleskih reči) |
| `temperature` | Kreativnost. Niske vrednosti je čine fokusiranom, dok visoke vrednosti donose više nepredvidivosti | - **0,1–0,3**: Fokusirano, deterministički (dobro za rezimee) <br> **0,5–0,7**: Uravnoteženo (opšta upotreba) <br> **0,8–1,0**: Kreativno, raznovrsno (brejnstorming) |
| `top_p` | Nucleus Sampling - Niske vrednosti ograničavaju model na uže izlaze | **0,1-0,5**: Strogo, predvidljivo <br> **0,9-0,95**: (standardno, prirodno, konverzaciono) |


## Primene u stvarnom svetu

- **Analiza istraživačkih radova**: Izdvajanje ključnih nalaza iz kompleksnih publikacija radi brzog pregleda
- **Agregacija vesti**: Sumiranje vesti u kratke dnevne preglede ili istaknute stavke
- **Beleške sa sastanaka**: Sažimanje transkripata u konkretne zadatke i sažete rezimee
- **Pregled pravnih dokumenata**: Brzo izdvajanje relevantnih klauzula ili obaveza iz dugih pravnih tekstova
- **Dokumentacija koda**: Generisanje sažetih pregleda repozitorijuma i objašnjenja funkcija

## Sledeći koraci

- **Fino podešavanje (Fine-tuning)**: Prilagodite modele svojoj specifičnoj oblasti ili terminologiji radi bolje preciznosti (pogledajte priručnike za fino podešavanje)
- **RAG sistemi**: Kombinujte LLM-ove sa pretraživanjem dokumenata za odgovore i pretragu svesnu konteksta
- **Istraživanje modela**: Eksperimentišite sa novim modelima poput Llama 3, Phi-3 ili Qwen za bolje rezultate
- **Produkciono postavljanje**: Koristite alate poput vLLM za skalabilno posluživanje LLM-ova u organizacijama

Vaš sistem vam daje moć da pokrećete sofisticirane jezičke modele lokalno. Eksperimentišite sa različitim modelima, upitima i parametrima da biste otkrili šta najbolje odgovara vašim primenama.