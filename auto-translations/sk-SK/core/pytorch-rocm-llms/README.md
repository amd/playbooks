<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Prehľad


Chcete spúšťať výkonné jazykové modely AI na vlastnom hardvéri? Tento sprievodca vám ukáže ako.
Tento tutoriál využíva PyTorch poháňaný softvérom AMD ROCm™ na spúšťanie modelov, ktoré dokážu sumarizovať dokumenty, odpovedať na otázky, generovať text a oveľa viac – všetko beží lokálne.

## Čo sa naučíte

- Spúšťať LLM modely ako gpt-oss-20b a qwen3.5-4B lokálne pomocou PyTorch a ROCm
- Vytvoriť nástroj na sumarizáciu dokumentov pomocou LLM modelov

## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizácií softvéru
> **Poznámka**: Ak VS Code nie je nainštalovaný, môžete ho nainštalovať pomocou Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Inštalácia softvérových predpokladov

### Vytvorenie virtuálneho prostredia

<!-- @os:linux -->
<!-- @device:halo_box -->
V systéme Linux otvorte terminál v adresári podľa vášho výberu a postupujte podľa príkazov na vytvorenie venv s už nainštalovaným ROCm+Pytorch.
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
**Udeľte svojmu používateľovi prístup k zariadeniam GPU** (pre uplatnenie zmien sa odhláste a znova prihláste):

```bash
sudo usermod -aG render,video $LOGNAME
```

V systéme Linux otvorte terminál v adresári podľa vášho výberu a postupujte podľa príkazov na vytvorenie venv.
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
V systéme Windows otvorte terminál v adresári podľa vášho výberu a postupujte podľa príkazov na vytvorenie venv s už nainštalovaným ROCm+Pytorch.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
V systéme Windows otvorte terminál v adresári podľa vášho výberu a postupujte podľa príkazov na vytvorenie venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Tip**: Používatelia systému Windows môžu pred spustením niektorých príkazov PowerShell potrebovať upraviť politiku spúšťania PowerShell (napr.
> nastaviť ju na RemoteSigned alebo Unrestricted).

<!-- @os:end -->

### Inštalácia základných závislostí
<!-- @require:driver,pytorch -->

### Inštalácia ďalších závislostí

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

## Rýchly štart s ukážkovými skriptmi

Tento playbook obsahuje skripty pripravené na použitie. Kliknite na ne pre náhľad a stiahnite ich do rovnakého adresára, v ktorom ste vytvorili prostredie.

| Skript | Popis | Použitie |
|--------|-------|----------|
| [run_llm.py](assets/run_llm.py) | Základné generovanie textu pomocou LLM | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Sumarizátor dokumentov s podporou Harmony | `python summarizer.py --file document.txt` |

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

Oba skripty podporujú:
- Výber modelu pomocou príznaku `--model`
- Formátovanie pomocou šablóny chatu pre správne zadávanie výziev modelu, čo je obzvlášť užitočné pri sumarizácii dokumentov

## Načítanie a spustenie vášho prvého LLM

Priložený skript [run_llm.py](assets/run_llm.py) ukazuje, ako generovať text pomocou LLM modelov s PyTorch a AMD ROCm.

> **Poznámka:** Pri načítaní modelu Hugging Face Transformers najprv skontroluje lokálnu vyrovnávaciu pamäť (`~/.cache/huggingface/hub` v systéme Linux, `C:\Users\<user>\.cache\huggingface\hub` v systéme Windows). Ak model nie je uložený v cache, automaticky sa stiahne z huggingface.co. Prvé spustenie môže trvať niekoľko minút v závislosti od veľkosti modelu a rýchlosti siete.

Nasledujúci úryvok ukazuje, ako používať model a prispôsobiť kladené otázky.

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

Vyskúšajte stiahnutý skript:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Vytvorenie sumarizátora dokumentov

Teraz, keď ste vygenerovali lokálny výstup LLM, môžete na tom stavať a vytvoriť praktický sumarizátor dokumentov. V tejto časti použijete skript [summarizer.py](assets/summarizer.py) na načítanie súboru .txt a automatické vygenerovanie stručného súhrnu – všetko beží lokálne na vašom GPU.

Skript je navrhnutý tak, aby fungoval hneď po stiahnutí. Otvorte skript v editore, preskúmajte kód, prispôsobte výzvy a upravte parametre ako dĺžka a teplota.

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### Príklady použitia

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

## Informácie o parametroch generovania

| Parameter | Čo ovláda | Typické hodnoty |
|-----------|-----------|-----------------|
| `max_new_tokens` | Maximálna dĺžka výstupu LLM | Použite 50–500 tokenov pre súhrny. (1 token je približne 0,75 anglického slova) |
| `temperature` | Kreativita. Nízke hodnoty zvyšujú zameranosť, vysoké hodnoty prinášajú väčšiu nepredvídateľnosť | - **0.1–0.3**: Zameraný, deterministický (vhodný pre súhrny) <br> **0.5–0.7**: Vyvážený (všeobecné použitie) <br> **0.8–1.0**: Kreatívny, rôznorodý (brainstorming) |
| `top_p` | Vzorkovanie jadra – nízke hodnoty obmedzujú model na užšie výstupy | **0.1-0.5**: Prísny, predvídateľný <br> **0.9-0.95**: (štandardný, prirodzený, konverzačný) |


## Reálne aplikácie

- **Analýza vedeckých článkov**: Extrakcia kľúčových zistení zo zložitých publikácií pre rýchly prehľad
- **Agregácia správ**: Sumarizácia spravodajských článkov do stručných denných prehľadov alebo súhrnu
- **Zápisnice zo stretnutí**: Kondenzácia prepisov do akčných bodov a stručných súhrnutí
- **Kontrola právnych dokumentov**: Rýchla extrakcia relevantných doložiek alebo záväzkov z dlhých právnych textov
- **Dokumentácia kódu**: Generovanie stručných prehľadov repozitárov a vysvetlení funkcií

## Ďalšie kroky

- **Doladenie**: Prispôsobte modely vášmu špecifickému odboru alebo žargónu pre lepšiu presnosť (pozri Playbooks o doladení)
- **RAG systémy**: Kombinujte LLM modely s vyhľadávaním dokumentov pre kontextovo uvedomelé odpovede a vyhľadávanie
- **Prieskum modelov**: Experimentujte s novými modelmi ako Llama 3, Phi-3 alebo Qwen pre lepšie výsledky
- **Produkčné nasadenie**: Používajte nástroje ako vLLM pre škálovateľné nasadenie LLM v organizáciách

Váš systém vám dáva možnosť spúšťať sofistikované jazykové modely lokálne. Experimentujte s rôznymi modelmi, výzvami a parametrami, aby ste zistili, čo najlepšie funguje pre vaše aplikácie.