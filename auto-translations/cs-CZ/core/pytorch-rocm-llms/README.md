<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Přehled


Chcete spouštět výkonné jazykové modely AI na vlastním hardwaru? Tento průvodce vám ukáže jak.
Tento tutoriál využívá PyTorch s podporou softwaru AMD ROCm™ ke spouštění modelů, které dokáží shrnovat dokumenty, odpovídat na otázky, generovat text a mnoho dalšího – vše běží lokálně.

## Co se naučíte

- Spouštět LLM modely jako gpt-oss-20b a qwen3.5-4B lokálně pomocí PyTorch a ROCm
- Vytvořit nástroj pro sumarizaci dokumentů pomocí LLM

## Nastavení konfigurace paměti

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru
> **Poznámka**: Pokud VS Code není nainstalován, můžete ho nainstalovat pomocí Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace softwarových předpokladů

### Vytvoření virtuálního prostředí

<!-- @os:linux -->
<!-- @device:halo_box -->
Na Linuxu otevřete terminál v adresáři dle vašeho výběru a postupujte podle příkazů pro vytvoření venv s již nainstalovaným ROCm+Pytorch.
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
**Udělte svému uživateli přístup k GPU zařízením** (pro aktivaci se odhlaste a znovu přihlaste):

```bash
sudo usermod -aG render,video $LOGNAME
```

Na Linuxu otevřete terminál v adresáři dle vašeho výběru a postupujte podle příkazů pro vytvoření venv.
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
Na Windows otevřete terminál v adresáři dle vašeho výběru a postupujte podle příkazů pro vytvoření venv s již nainstalovaným ROCm+Pytorch.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Na Windows otevřete terminál v adresáři dle vašeho výběru a postupujte podle příkazů pro vytvoření venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Tip**: Uživatelé Windows možná budou muset upravit zásady spouštění PowerShellu (např.
> nastavit je na RemoteSigned nebo Unrestricted) před spuštěním některých příkazů PowerShellu.

<!-- @os:end -->

### Instalace základních závislostí
<!-- @require:driver,pytorch -->

### Instalace dalších závislostí

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

## Rychlý start s ukázkovými skripty

Tento playbook obsahuje skripty připravené k použití. Klikněte na ně pro náhled a stáhněte je do stejného adresáře, kde jste vytvořili prostředí.

| Skript | Popis | Použití |
|--------|-------|---------|
| [run_llm.py](assets/run_llm.py) | Základní generování textu pomocí LLM | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Sumarizátor dokumentů s podporou Harmony | `python summarizer.py --file document.txt` |

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

Oba skripty podporují:
- Výběr modelu pomocí příznaku `--model`
- Formátování šablony chatu pro správné zadávání výzev modelu, zvláště užitečné pro sumarizaci dokumentů

## Načtení a spuštění prvního LLM

Přiložený skript [run_llm.py](assets/run_llm.py) ukazuje, jak generovat text pomocí LLM s využitím PyTorch a AMD ROCm.

> **Poznámka:** Při načítání modelu Hugging Face Transformers nejprve zkontroluje lokální mezipaměť (`~/.cache/huggingface/hub` na Linuxu, `C:\Users\<user>\.cache\huggingface\hub` na Windows). Pokud model není v mezipaměti, automaticky se stáhne z huggingface.co. První spuštění může trvat několik minut v závislosti na velikosti modelu a rychlosti sítě.

Níže uvedený úryvek ukazuje, jak model používat a přizpůsobit kladené otázky.

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

Vyzkoušejte stažený skript:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Vytvoření sumarizátoru dokumentů

Nyní, když jste vygenerovali lokální výstup LLM, můžete na tom stavět a vytvořit praktický sumarizátor dokumentů. V této části použijete skript [summarizer.py](assets/summarizer.py) k načtení souboru .txt a automatickému vygenerování stručného shrnutí – vše běží lokálně na vašem GPU.

Skript je navržen tak, aby fungoval ihned po spuštění. Otevřete skript v editoru, prozkoumejte kód, přizpůsobte výzvy a upravte parametry jako délku a teplotu.

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### Příklady použití

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

## Informace o parametrech generování

| Parametr | Co ovládá | Typické hodnoty |
|----------|-----------|-----------------|
| `max_new_tokens` | Maximální délka výstupu LLM | Pro shrnutí použijte 50–500 tokenů. (1 token odpovídá přibližně 0,75 anglického slova) |
| `temperature` | Kreativita. Nízké hodnoty zajišťují zaměřenost, vysoké hodnoty přinášejí větší nepředvídatelnost | - **0.1–0.3**: Zaměřené, deterministické (vhodné pro shrnutí) <br> **0.5–0.7**: Vyvážené (obecné použití) <br> **0.8–1.0**: Kreativní, různorodé (brainstorming) |
| `top_p` | Nucleus Sampling – nízké hodnoty omezují model na užší výstupy | **0.1-0.5**: Přísné, předvídatelné <br> **0.9-0.95**: (standardní, přirozené, konverzační) |


## Praktické aplikace

- **Analýza vědeckých článků**: Extrahujte klíčová zjištění ze složitých publikací pro rychlý přehled
- **Agregace zpráv**: Shrňte zpravodajské články do stručných denních přehledů nebo highlights
- **Poznámky ze schůzek**: Zkondenzujte přepisy do akčních bodů a stručných shrnutí
- **Kontrola právních dokumentů**: Rychle extrahujte relevantní klauzule nebo závazky z rozsáhlých právních textů
- **Dokumentace kódu**: Generujte stručné přehledy repozitářů a vysvětlení funkcí

## Další kroky

- **Doladění (Fine-tuning)**: Přizpůsobte modely svému specifickému oboru nebo terminologii pro lepší přesnost (viz playboky pro doladění)
- **RAG systémy**: Kombinujte LLM s vyhledáváním dokumentů pro kontextově uvědomělé odpovědi a vyhledávání
- **Průzkum modelů**: Experimentujte s novými modely jako Llama 3, Phi-3 nebo Qwen pro lepší výsledky
- **Produkční nasazení**: Používejte nástroje jako vLLM pro škálovatelné nasazení LLM v organizacích

Váš systém vám dává možnost spouštět sofistikované jazykové modely lokálně. Experimentujte s různými modely, výzvami a parametry, abyste zjistili, co nejlépe funguje pro vaše aplikace.