<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din limba engleză și nu a fost revizuită de o persoană. Aceasta poate conține erori, iar anumite instrucțiuni, comenzi, descărcări, disponibilitatea produselor sau alt conținut pot varia în funcție de limbă sau regiune. În cazul oricărei neconcordanțe sau discrepanțe, versiunea originală în limba engleză a playbook-ului prevalează.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Prezentare generală


Vrei să rulezi modele AI puternice de limbaj pe propriul tău hardware? Acest ghid îți arată cum.
Acest tutorial folosește PyTorch, susținut de software-ul AMD ROCm™, pentru a rula modele care pot rezuma documente, răspunde la întrebări, genera text și multe altele, toate rulând local.

## Ce Vei Învăța

- Rulează LLM-uri precum gpt-oss-20b și qwen3.5-4B local folosind PyTorch și ROCm
- Creează un instrument de rezumare a documentelor folosind LLM-uri

<!-- @device:halo_box,halo,stx,krk -->
## Configurarea Memoriei

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Verifică Actualizările Software
> **Notă**: Dacă VS Code nu este instalat, îl poți instala cu Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalarea Cerințelor Software Prealabile

### Crearea unui Mediu Virtual

<!-- @os:linux -->
<!-- @device:halo_box -->
Pe Linux, deschide un terminal în directorul dorit și urmează comenzile pentru a crea un venv cu ROCm+Pytorch deja instalate.
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
**Acordă-i utilizatorului tău acces la dispozitivele GPU** (deconectează-te și reconectează-te pentru ca aceasta să intre în vigoare):

```bash
sudo usermod -aG render,video $LOGNAME
```

Pe Linux, deschide un terminal în directorul dorit și urmează comenzile pentru a crea un venv.
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
Pe Windows, deschide un terminal în directorul dorit și urmează comenzile pentru a crea un venv cu ROCm+Pytorch deja instalate.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Pe Windows, deschide un terminal în directorul dorit și urmează comenzile pentru a crea un venv.
<!-- @test:id=create-venv timeout=180 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Sfat**: Utilizatorii Windows ar putea avea nevoie să modifice Politica lor de Execuție PowerShell (de exemplu,
> setând-o la RemoteSigned sau Unrestricted) înainte de a rula unele comenzi Powershell.

<!-- @os:end -->

### Instalarea Dependențelor de Bază
<!-- @require:driver,pytorch -->

### Instalarea Dependențelor Suplimentare

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

> **Notă:** Dacă modelul nu se încarcă sau rămâne fără memorie, încearcă să instalezi pachetul `kernels` pentru a încărca modelul cu cuantizare optimizată.
>
> ```bash
> # Folosește această versiune care este compatibilă cu versiunea Transformers
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

## Start Rapid cu Scripturi Exemplu

Acest playbook include scripturi gata de utilizat. Fă clic pe ele pentru a le previzualiza și a le descărca în același director cu mediul pe care l-ai creat.

| Script | Descriere | Utilizare |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Generare de text LLM de bază | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Rezumator de documente cu suport Harmony | `python summarizer.py --file document.txt` |

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

Ambele scripturi suportă:
- Selecția modelului prin steagul `--model`
- Formatarea șabloanelor de chat pentru solicitarea corectă a modelului, utilă în special pentru rezumarea documentelor

## Încărcarea și Rularea Primului Tău LLM

Scriptul inclus [run_llm.py](assets/run_llm.py) arată cum să generezi text cu LLM-uri folosind PyTorch și AMD ROCm.

> **Notă:** Când încarci un model, Hugging Face Transformers verifică mai întâi cache-ul local (`~/.cache/huggingface/hub` pe Linux, `C:\Users\<user>\.cache\huggingface\hub` pe Windows). Dacă modelul nu este stocat în cache, acesta este descărcat automat de pe huggingface.co. Prima rulare poate dura câteva minute, în funcție de dimensiunea modelului și viteza rețelei.

Fragmentul de mai jos arată cum să folosești modelul și să personalizezi întrebările adresate.

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

Încearcă scriptul descărcat:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Construirea unui Rezumator de Documente

Acum că ai generat un rezultat local cu LLM, poți să te bazezi pe acesta creând un rezumator de documente practic. În această secțiune, vei folosi scriptul [summarizer.py](assets/summarizer.py) pentru a introduce un fișier .txt și a genera automat un rezumat concis, totul rulând local pe GPU-ul tău.

Scriptul este conceput să funcționeze direct din start. Deschide scriptul într-un editor pentru a explora codul, a personaliza solicitările și a ajusta parametri precum lungimea și temperatura.

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### Exemple de Utilizare

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

## Aflați despre Parametrii de Generare

| Parametru | Ce Controlează | Valori Tipice |
|-----------|------------------|----------------|
| `max_new_tokens` | Lungimea maximă a rezultatului LLM-ului | Folosește 50–500 de tokenuri pentru rezumate. (1 token reprezintă aproximativ 0,75 cuvinte în limba engleză) |
| `temperature` | Creativitatea. Valorile mici o fac concentrată, iar valorile mari vin cu mai multă imprevizibilitate | - **0,1–0,3**: Concentrat, determinist (bun pentru rezumate) <br> **0,5–0,7**: Echilibrat (utilizare generală) <br> **0,8–1,0**: Creativ, variat (brainstorming) |
| `top_p` | Eșantionare Nucleus - Valorile mici limitează modelul la rezultate mai restrânse | **0,1-0,5**: Strict, previzibil <br> **0,9-0,95**: (standard, natural, conversațional) |


## Aplicații din Lumea Reală

- **Analiza Lucrărilor de Cercetare**: Extrage concluziile cheie din publicații complexe pentru o revizuire rapidă
- **Agregarea Știrilor**: Rezumă articole de știri în rezumate zilnice scurte sau puncte cheie
- **Notițe de Ședință**: Condensează transcrierile în elemente de acțiune și rezumate concise
- **Revizuirea Documentelor Juridice**: Extrage rapid clauzele sau obligațiile relevante din texte juridice lungi
- **Documentarea Codului**: Generează prezentări generale concise ale repository-urilor și explicații ale funcțiilor
## Următorii pași

- **Fine-tuning**: Adaptați modelele la domeniul sau jargonul dumneavoastră specific pentru o acuratețe mai bună (consultați Fine-tuning Playbooks)
- **Sisteme RAG**: Combinați LLM-urile cu recuperarea documentelor pentru răspunsuri și căutări contextuale
- **Explorarea modelelor**: Experimentați cu modele noi precum Llama 3, Phi-3 sau Qwen pentru rezultate mai bune
- **Implementare în producție**: Folosiți instrumente precum vLLM pentru servirea scalabilă a LLM-urilor în organizații

Sistemul dumneavoastră vă oferă puterea de a rula modele lingvistice sofisticate local. Experimentați cu diferite modele, prompturi și parametri pentru a descoperi ce funcționează cel mai bine pentru aplicațiile dumneavoastră.