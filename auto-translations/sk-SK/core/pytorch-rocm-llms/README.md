<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Prehľad


Chcete spúšťať výkonné jazykové modely AI na vlastnom hardvéri? Táto príručka vám ukáže, ako na to.
Tento návod používa PyTorch podporovaný softvérom AMD ROCm™ na spúšťanie modelov, ktoré dokážu sumarizovať dokumenty, odpovedať na otázky, generovať text a ďalšie, a to všetko lokálne.

## Čo sa naučíte

- Spúšťať LLM ako gpt-oss-20b a qwen3.5-4B lokálne pomocou PyTorch a ROCm
- Vytvoriť nástroj na sumarizáciu dokumentov pomocou LLM

## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizácií softvéru
> **Poznámka**: Ak VS Code nie je nainštalovaný, môžete ho nainštalovať pomocou Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Inštalácia požadovaného softvéru

### Vytvorenie virtuálneho prostredia

<!-- @os:linux -->
<!-- @device:halo_box -->
V systéme Linux otvorte terminál v adresári podľa vlastného výberu a postupujte podľa príkazov na vytvorenie venv s už nainštalovaným ROCm+Pytorch.
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
**Udeľte svojmu používateľovi prístup k zariadeniam GPU** (pre uplatnenie zmeny sa odhláste a znova prihláste):

```bash
sudo usermod -aG render,video $LOGNAME
```

V systéme Linux otvorte terminál v adresári podľa vlastného výberu a postupujte podľa príkazov na vytvorenie venv.
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
V systéme Windows otvorte terminál v adresári podľa vlastného výberu a postupujte podľa príkazov na vytvorenie venv s už nainštalovaným ROCm+Pytorch.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
V systéme Windows otvorte terminál v adresári podľa vlastného výberu a postupujte podľa príkazov na vytvorenie venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Tip**: Používatelia systému Windows možno budú musieť upraviť svoje pravidlá vykonávania PowerShell (napr.
> nastaviť ho na RemoteSigned alebo Unrestricted) pred spustením niektorých príkazov PowerShell.

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

## Rýchly štart s ukážkovými skriptami

Táto príručka obsahuje pripravené skripty na okamžité použitie. Kliknutím na ne ich zobrazíte a stiahnete do rovnakého adresára ako prostredie, ktoré ste vytvorili.

| Skript | Popis | Použitie |
|--------|-------------|-------|
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
- Formátovanie šablóny chatu pre správne formulovanie výziev pre model, čo je obzvlášť užitočné pri sumarizácii dokumentov

## Načítanie a spustenie vášho prvého LLM

Priložený skript [run_llm.py](assets/run_llm.py) ukazuje, ako generovať text pomocou LLM s využitím PyTorch a AMD ROCm.

> **Poznámka:** Pri načítaní modelu Hugging Face Transformers najprv skontroluje svoju lokálnu vyrovnávaciu pamäť (`~/.cache/huggingface/hub` v systéme Linux, `C:\Users\<user>\.cache\huggingface\hub` v systéme Windows). Ak model nie je uložený vo vyrovnávacej pamäti, automaticky sa stiahne z huggingface.co. Prvé spustenie môže trvať niekoľko minút v závislosti od veľkosti modelu a rýchlosti siete.

Nižšie uvedený úryvok ukazuje, ako model použiť a prispôsobiť kladené otázky.

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

Teraz, keď ste vygenerovali výstup z lokálneho LLM, môžete na tom stavať a vytvoriť praktický sumarizátor dokumentov. V tejto časti použijete skript [summarizer.py](assets/summarizer.py) na vloženie súboru .txt a automatické vygenerovanie stručného zhrnutia, a to všetko bežiace lokálne na vašom GPU.

Skript je navrhnutý tak, aby fungoval hneď po spustení. Otvorte skript v editore, preskúmajte kód, prispôsobte výzvy a upravte parametre, ako je dĺžka a teplota.

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

| Parameter | Čo riadi | Typické hodnoty |
|-----------|------------------|----------------|
| `max_new_tokens` | Maximálnu dĺžku výstupu LLM | Pre zhrnutia použite 50 – 500 tokenov. (1 token predstavuje približne 0,75 anglického slova) |
| `temperature` | Kreativitu. Nízke hodnoty ju robia sústredenou, vysoké hodnoty prinášajú väčšiu nepredvídateľnosť | - **0,1 – 0,3**: Sústredené, deterministické (vhodné pre zhrnutia) <br> **0,5 – 0,7**: Vyvážené (všeobecné použitie) <br> **0,8 – 1,0**: Kreatívne, rôznorodé (brainstorming) |
| `top_p` | Nucleus sampling – nízke hodnoty obmedzujú model na užší rozsah výstupov | **0,1 – 0,5**: Prísne, predvídateľné <br> **0,9 – 0,95**: (štandardné, prirodzené, konverzačné) |


## Praktické aplikácie

- **Analýza výskumných prác**: Rýchle extrahovanie kľúčových zistení zo zložitých publikácií na účely rýchleho preskúmania
- **Agregácia správ**: Sumarizácia spravodajských článkov do stručných denných prehľadov alebo súhrnov
- **Zápisnice zo stretnutí**: Zredukovanie prepisov na akčné body a stručné zhrnutia
- **Kontrola právnych dokumentov**: Rýchle extrahovanie relevantných klauzúl alebo povinností z dlhých právnych textov
- **Dokumentácia kódu**: Generovanie stručných prehľadov repozitárov a vysvetlení funkcií

## Ďalšie kroky

- **Doladenie (fine-tuning)**: Prispôsobte modely vašej konkrétnej oblasti alebo terminológii pre lepšiu presnosť (pozrite si príručky na doladenie)
- **Systémy RAG**: Kombinujte LLM s vyhľadávaním v dokumentoch pre kontextovo relevantné odpovede a vyhľadávanie
- **Skúmanie modelov**: Experimentujte s novými modelmi ako Llama 3, Phi-3 alebo Qwen pre lepšie výsledky
- **Nasadenie do produkcie**: Používajte nástroje ako vLLM na škálovateľné poskytovanie LLM v organizáciách

Váš systém vám dáva možnosť spúšťať sofistikované jazykové modely lokálne. Experimentujte s rôznymi modelmi, výzvami a parametrami, aby ste zistili, čo najlepšie funguje pre vaše aplikácie.