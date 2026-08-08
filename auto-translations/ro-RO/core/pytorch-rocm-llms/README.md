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


Doriți să rulați modele lingvistice AI puternice pe propriul hardware? Acest ghid vă arată cum.
Acest tutorial folosește PyTorch, susținut de software-ul AMD ROCm™, pentru a rula modele care pot rezuma documente, răspunde la întrebări, genera text și multe altele, toate rulând local.

## Ce veți învăța

- Rulați LLM-uri precum gpt-oss-20b și qwen3.5-4B local, folosind PyTorch și ROCm
- Creați un instrument de rezumare a documentelor folosind LLM-uri

## Setarea configurației memoriei

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificați actualizările software-ului
> **Notă**: Dacă VS Code nu este instalat, îl puteți instala cu Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalarea cerințelor preliminare de software

### Creați un mediu virtual

<!-- @os:linux -->
<!-- @device:halo_box -->
Pe Linux, deschideți un terminal în directorul dorit și urmați comenzile pentru a crea un venv cu ROCm+Pytorch deja instalate.
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
**Acordați utilizatorului dvs. acces la dispozitivele GPU** (deconectați-vă și reconectați-vă pentru ca aceasta să aibă efect):

```bash
sudo usermod -aG render,video $LOGNAME
```

Pe Linux, deschideți un terminal în directorul dorit și urmați comenzile pentru a crea un venv.
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
Pe Windows, deschideți un terminal în directorul dorit și urmați comenzile pentru a crea un venv cu ROCm+Pytorch deja instalate.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env --system-site-packages
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Pe Windows, deschideți un terminal în directorul dorit și urmați comenzile pentru a crea un venv.
<!-- @test:id=create-venv timeout=60 -->
```bash
python -m venv pytorch-env
pytorch-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="pytorch-env\Scripts\activate" -->
<!-- @device:end -->

> **Sfat**: Este posibil ca utilizatorii Windows să trebuiască să modifice Politica de execuție PowerShell (de exemplu,
> setând-o la RemoteSigned sau Unrestricted) înainte de a rula unele comenzi Powershell.

<!-- @os:end -->

### Instalarea dependențelor de bază
<!-- @require:driver,pytorch -->

### Instalarea dependențelor suplimentare

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

## Pornire rapidă cu scripturi exemplu

Acest playbook include scripturi gata de utilizare. Faceți clic pe ele pentru a le previzualiza și descărca în același director cu mediul pe care l-ați creat.

| Script | Descriere | Utilizare |
|--------|-------------|-------|
| [run_llm.py](assets/run_llm.py) | Generare de text LLM de bază | `python run_llm.py` |
| [summarizer.py](assets/summarizer.py) | Instrument de rezumare a documentelor cu suport Harmony | `python summarizer.py --file document.txt` |

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

Ambele scripturi acceptă:
- Selectarea modelului prin steagul `--model`
- Formatarea șabloanelor de chat pentru instrucțiuni corecte ale modelului, deosebit de utilă pentru rezumarea documentelor

## Încărcarea și rularea primului dvs. LLM

Scriptul inclus [run_llm.py](assets/run_llm.py) arată cum se generează text cu LLM-uri folosind PyTorch și AMD ROCm.

> **Notă:** Când încărcați un model, Hugging Face Transformers verifică mai întâi memoria cache locală (`~/.cache/huggingface/hub` pe Linux, `C:\Users\<user>\.cache\huggingface\hub` pe Windows). Dacă modelul nu este în cache, acesta este descărcat automat de pe huggingface.co. Prima rulare poate dura câteva minute, în funcție de dimensiunea modelului și viteza rețelei.

Fragmentul de mai jos arată cum să utilizați modelul și să personalizați întrebările adresate.

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

Încercați scriptul descărcat:

<!-- @test:id=run-llm-simple timeout=600 setup=activate-venv -->
```bash
python run_llm.py --model ${hf_model}
```
<!-- @test:end -->


## Construirea unui instrument de rezumare a documentelor

Acum că ați generat un rezultat LLM local, puteți construi pe baza acestuia realizând un instrument practic de rezumare a documentelor. În această secțiune, veți utiliza scriptul [summarizer.py](assets/summarizer.py) pentru a introduce un fișier .txt și a genera automat un rezumat concis, totul rulând local pe GPU-ul dvs.

Scriptul este conceput să funcționeze fără configurări suplimentare. Deschideți scriptul într-un editor pentru a explora codul, a personaliza instrucțiunile (prompts) și a ajusta parametri precum lungimea și temperatura.

<!-- @test:id=run-summarizer timeout=1000 hidden=True setup=activate-venv -->
```bash
python summarizer.py --model ${hf_model}
```
<!-- @test:end -->

### Exemple de utilizare

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

## Aflați despre parametrii de generare

| Parametru | Ce controlează | Valori tipice |
|-----------|------------------|----------------|
| `max_new_tokens` | Lungimea maximă a rezultatului LLM-ului | Utilizați 50–500 de token-uri pentru rezumate. (1 token reprezintă aproximativ 0,75 cuvinte în limba engleză) |
| `temperature` | Creativitatea. Valorile mici îl fac concentrat, în timp ce valorile mari aduc mai multă imprevizibilitate | - **0,1–0,3**: Concentrat, determinist (bun pentru rezumate) <br> **0,5–0,7**: Echilibrat (utilizare generală) <br> **0,8–1,0**: Creativ, variat (brainstorming) |
| `top_p` | Eșantionare de tip nucleu (Nucleus Sampling) - Valorile mici limitează modelul la rezultate mai restrânse | **0,1-0,5**: Strict, previzibil <br> **0,9-0,95**: (standard, natural, conversațional) |


## Aplicații din lumea reală

- **Analiza lucrărilor de cercetare**: Extrageți concluziile cheie din publicații complexe pentru o revizuire rapidă
- **Agregarea știrilor**: Rezumați articolele de știri în sinteze zilnice scurte sau evidențieri
- **Notițe de întâlnire**: Condensați transcrierile în elemente de acțiune și rezumate concise
- **Revizuirea documentelor juridice**: Extrageți rapid clauzele sau obligațiile relevante din texte juridice lungi
- **Documentarea codului**: Generați prezentări concise ale depozitelor de cod și explicații ale funcțiilor

## Pașii următori

- **Fine-tuning**: Adaptați modelele la domeniul sau jargonul dvs. specific pentru o acuratețe mai bună (consultați Playbook-urile de Fine-tuning)
- **Sisteme RAG**: Combinați LLM-urile cu regăsirea documentelor pentru răspunsuri și căutări conștiente de context
- **Explorarea modelelor**: Experimentați cu modele noi precum Llama 3, Phi-3 sau Qwen pentru rezultate mai bune
- **Implementare în producție**: Utilizați instrumente precum vLLM pentru servirea scalabilă a LLM-urilor în organizații

Sistemul dvs. vă oferă puterea de a rula modele lingvistice sofisticate local. Experimentați cu diferite modele, instrucțiuni (prompts) și parametri pentru a descoperi ce funcționează cel mai bine pentru aplicațiile dvs.