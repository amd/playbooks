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

Acest tutorial oferă exemple pas cu pas pentru ajustarea fină (fine-tuning) a unui model lingvistic mare (LLM) folosind PyTorch și ROCm. Acesta acoperă mai multe tehnici, de la ajustarea fină standard până la strategii de ajustare fină eficientă din punct de vedere al parametrilor (Parameter-Efficient Fine-Tuning - PEFT) care economisesc memorie, astfel încât să puteți adapta cu ușurință modelele pentru nevoile dumneavoastră.

**Model utilizat**: google/gemma-3-4b-it  *(consultați [Activarea autentificării HF](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) dacă modelul este restricționat)*  
**Hardware**: GPU AMD Radeon™ cu suport ROCm  
**Framework**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Notă:** 
> - Ajustarea fină completă necesită cel puțin **64 GB de RAM de sistem**, din care cel puțin **32 GB trebuie să fie disponibili pentru GPU** (cei 32 GB fac parte din cei 64 GB, nu se adaugă la aceștia).
> - Puteți încerca, de asemenea, și alte arhitecturi de modele, inclusiv **GPT-OSS-20B**, prin înlocuirea modelului în scripturile de antrenare furnizate.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **Notă:** Ajustarea fină LoRA și QLoRA necesită cel puțin **32 GB de RAM de sistem**, din care cel puțin **16 GB trebuie să fie disponibili pentru GPU** (cei 16 GB fac parte din cei 32 GB, nu se adaugă la aceștia).
<!-- @os:end -->

<!-- @os:windows -->
> **Notă:** Ajustarea fină LoRA necesită cel puțin **32 GB de RAM de sistem**, din care cel puțin **16 GB trebuie să fie disponibili pentru GPU** (cei 16 GB fac parte din cei 32 GB, nu se adaugă la aceștia).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Notă:** Ajustarea fină LoRA și QLoRA necesită o placă video cu cel puțin **16 GB de memorie GPU dedicată** și **32 GB de RAM de sistem**.
> - Pe Linux, antrenarea rulează în întregime în memoria VRAM dedicată a plăcii video.
> - Aceasta nu trece la memoria GPU partajată (RAM de sistem) atunci când VRAM se epuizează.
> - Plăcile cu mai puțin de 16 GB de VRAM dedicată vor rămâne fără memorie în timpul antrenării pe Linux, chiar dacă sistemul dispune de suficient RAM.
<!-- @os:end -->

<!-- @os:windows -->
> **Notă:** Ajustarea fină LoRA necesită cel puțin **16 GB de memorie GPU totală** și **32 GB de RAM de sistem**.
> - Pe Windows, memoria GPU totală combină VRAM dedicată a plăcii video cu memoria GPU partajată (împrumutată din RAM-ul de sistem).
> - Prin urmare, plăcile cu mai puțin de 16 GB de VRAM dedicată pot totuși rula acest playbook folosind memoria GPU partajată pentru a compensa diferența.
<!-- @os:end -->
<!-- @device:end -->

## Ce veți învăța

- Cum să ajustați fin un LLM folosind LoRA, QLoRA și ajustare fină completă cu PyTorch și ROCm
- Cum să salvați și să implementați modelul dumneavoastră ajustat fin
- Cum să monitorizați antrenarea și să depanați problemele comune

<!-- @device:halo_box,halo,stx,krk -->
## Configurarea memoriei

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Verificarea actualizărilor software
> **Notă**: Dacă VS Code nu este instalat, îl puteți instala cu Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalarea cerințelor preliminare software

#### Crearea unui mediu virtual

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update 
sudo apt install -y python3-venv 
python3 -m venv finetune-venv --system-site-packages 
source finetune-venv/bin/activate 
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source finetune-venv/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Acordați utilizatorului dumneavoastră acces la dispozitivele GPU** (deconectați-vă și reconectați-vă pentru ca acest lucru să intre în vigoare):

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv finetune-venv
source finetune-venv/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source finetune-venv/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=180 -->
```powershell
python -m venv finetune-venv --system-site-packages
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=180 -->
```powershell
python -m venv finetune-venv
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

#### Instalarea dependențelor de bază
<!-- @require:pytorch -->

#### Dependențe suplimentare

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Aici sunt testate și suportate doar pachetele de bază. **bitsandbytes nu este bine suportat pe Windows**, astfel că instalarea pentru Windows omite acest pachet; folosiți LoRA sau ajustare fină completă pe Windows (QLoRA necesită bitsandbytes și este destinat pentru Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### Activarea autentificării HF (modele restricționate sau personalizate / neinstalate în prealabil)

În acest exemplu folosim **google/gemma-3-4b-it**, care este un model **restricționat** (gated). Trebuie să acceptați termenii modelului pe Hugging Face și apoi să vă autentificați, astfel încât scripturile de antrenare să îl poată descărca.

1. **Acceptați licența:** Deschideți [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), autentificați-vă (sau creați un cont) și acceptați licența/termenii de pe pagina modelului (de ex. „Agree and access repository”).
2. **Instalați și autentificați-vă:** Instalați Hugging Face CLI, apoi rulați autentificarea standard:

```bash
pip install huggingface_hub
hf auth login
```

<!-- @test:id=verify-scripts timeout=30 hidden=True -->
```python
import os
import sys
import ast

# Check that required script files exist
scripts = ['train_qlora.py', 'train_lora.py', 'train_full_finetuning.py']
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing files: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

# Verify Python scripts have valid syntax
for script in scripts:
    with open(script, 'r') as f:
        ast.parse(f.read())
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=verify-imports timeout=60 hidden=True setup=activate-venv -->
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import AutoPeftModelForCausalLM
from trl import SFTTrainer

print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print("PASS: All imports successful")
```
<!-- @test:end -->

<!-- @test:id=verify-package-version timeout=60 hidden=True setup=activate-venv -->
```python
import importlib.metadata as md

pkgs = [
    "torch", "transformers", "trl", "peft", "accelerate",
    "datasets", "safetensors", "fsspec", "bitsandbytes",
    "huggingface_hub", "tokenizers",
]
for p in pkgs:
    try:
        print(f"{p}: {md.version(p)}")
    except md.PackageNotFoundError:
        print(f"{p}: NOT INSTALLED")
```
<!-- @test:end -->

<!-- @test:id=quick-train-lora timeout=600 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_lora.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=quick-train-qlora timeout=600 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_qlora.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=quick-train-full-finetuning timeout=1200 hidden=True setup=activate-venv -->
```python
import os
import subprocess
import sys

os.environ["QUICK_TRAIN"] = "1"
os.environ["QUICK_TRAIN_MODEL"] = "unsloth/gemma-3-4b-it"
r = subprocess.run([sys.executable, "train_full_finetuning.py"], timeout=600)
sys.exit(r.returncode)
```
<!-- @test:end -->
<!-- @device:end -->
---

## Înțelegerea tehnicilor

### Ce este LoRA?

**LoRA (Low-Rank Adaptation)** păstrează modelul de bază înghețat și antrenează doar matrice mici de tip „adaptor” care sunt adăugate la anumite straturi. 

- **Ideea de bază**: în loc să actualizăm o matrice de greutăți uriașă cu milioane de parametri, învățăm o actualizare de rang redus (două matrice mici al căror produs are mult mai puțini parametri). Acest lucru oferă o reducere semnificativă a parametrilor antrenabili și a VRAM-ului, păstrând în același timp cea mai mare parte a calității ajustării fine complete.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### Ce este QLoRA?

**QLoRA** combină **cuantizarea pe 4 biți** cu **LoRA**. Modelul de bază este încărcat pe 4 biți (economii mari de memorie), iar doar adaptoarele LoRA sunt antrenate cu precizie mai mare. Astfel obțineți eficiența parametrilor din LoRA plus un consum mult mai redus de VRAM, cu un mic compromis de calitate comparativ cu LoRA cu precizie completă. Rețineți că cuantizarea pe 4 biți poate cauza instabilități numerice (vârfuri de pierdere sau valori NaN), astfel încât utilizatorii pot prefera adesea **LoRA** dacă este disponibil suficient VRAM.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Notă**: Pentru modelele de bază MXFP4, cum ar fi `openai/gpt-oss-20b`, vă recomandăm să folosiți **LoRA** (`train_lora.py`) în locul QLoRA. Calea pe 4 biți a `bitsandbytes` din scriptul QLoRA de obicei decuantizează greutățile MXFP4 la BF16, astfel încât rularea se comportă ca un LoRA standard. MXFP4 nativ necesită `bitsandbytes` construit din sursă, plus un stack corespunzător de Transformers/Triton/kernels. Consultați [documentația Transformers MXFP4](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. Alegeți Metoda Dvs.

| Metodă | Memorie | Viteză | Calitate | Cel Mai Potrivit Pentru |
|--------|--------|-------|---------|----------|
| **QLoRA** (doar Linux) | 12-16GB | Cea mai rapidă | 90-95% | Utilizare Redusă a Memoriei |
| **LoRA** | 24-32GB | Rapid | 95-98% | Abordare echilibrată |
| **Full** | 80GB+ | Cea mai lentă | 100% | Calitate maximă |

### 3. Rulați Antrenarea

**Setul de date și ce învață modelul**  
Scripturile transformă setul de date în exemple de chat. De exemplu, scriptul QLoRA folosește **Abirate/english_quotes**: fiecare exemplu devine o pereche utilizator–asistent precum:

- **Utilizator:** „Dă-mi un citat despre: &lt;tag&gt;”
- **Asistent:** „&lt;citat&gt; – &lt;autor&gt;”

Ajustarea fină învață modelul să răspundă la prompturi care solicită citate despre un subiect și să le returneze în formatul `<quote text> - <author>`. Scripturile LoRA și de ajustare fină completă folosesc **databricks/databricks-dolly-15k** (perechi generale instrucțiune/răspuns), astfel încât sarcina exactă variază în funcție de script; ideea este aceeași - adaptarea modelului la setul de date și formatul ales de dvs.

Mai jos este un rezumat al metodelor de antrenare disponibile. Fiecare metodă face trimitere la scriptul său și oferă o scurtă descriere pentru alegerea abordării potrivite.

| Script                           | Metodă            | Descriere                                                                                                         | VRAM Tipic | Recomandat Pentru                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Antrenează matrice mici de adaptor păstrând înghețat modelul de bază. De 3-5 ori mai rapid; ~95-98% din calitatea completă.                         | 24–32GB      | Utilizatori avansați; adaptoare multiple; mai multă VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(doar Linux)*             | **QLoRA**       | Cuantizare pe 4 biți + adaptoare LoRA. Cea mai redusă utilizare a memoriei, cea mai rapidă, compromis mic de calitate. Necesită `bitsandbytes` (doar Linux).                            | 12–16GB      | Majoritatea utilizatorilor; experimente rapide; VRAM limitat      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Ajustare Fină Completă** | Actualizează toți parametrii modelului. Calitate maximă; cea mai mare utilizare de memorie și calcul.                                    | 40GB+        | Calitate maximă; cercetare; VRAM mare           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Notă:** Ajustarea fină completă (`train_full_finetuning.py`) poate necesita mai mult de 64GB de RAM de sistem și este posibil să nu fie fezabilă pe acest dispozitiv. Luați în considerare utilizarea LoRA sau QLoRA în schimb.
<!-- @os:end -->

<!-- @os:windows -->
> **Notă:** Ajustarea fină completă (`train_full_finetuning.py`) poate necesita mai mult de 64GB de RAM de sistem și este posibil să nu fie fezabilă pe acest dispozitiv. Luați în considerare utilizarea LoRA în schimb.
<!-- @os:end -->
<!-- @device:end -->

Pur și simplu selectați `Training method` preferată, descărcați scriptul corespunzător și executați-l folosind comanda păstrând mediul dvs. virtual activat: 

```python
python3 train_<method_name>.py.
```

## Utilizarea Modelului Dvs. Ajustat Fin

### După Ajustarea Fină Completă

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "output-gemma-3-4b-it-full",     # Directory containing your fully fine-tuned checkpoint
    device_map="auto",
    torch_dtype="auto"            # Use BF16 if your GPU supports it, else "auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-it-full")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### După Antrenarea LoRA/QLoRA

```python
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

# Load model with LoRA or QLoRA adapters
model = AutoPeftModelForCausalLM.from_pretrained(
    "output-gemma-3-4b-it-qlora",   # or "output-gemma-3-4b-lora" depending on your training
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gemma-3-4b-it-qlora")

# Generate text
prompt = "Explain quantum computing:"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### Combinați Adaptorul LoRA în Modelul de Bază

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Notă:**  
- Asigurați-vă că numele directorului modelului (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) corespunde folderului real de ieșire din antrenare.  
- Dacă ați folosit LoRA în loc de QLoRA, doar înlocuiți calea corespunzător.  
- Unele modele Gemma necesită specificarea `trust_remote_code=True` în `from_pretrained`; adăugați dacă vedeți un avertisment aferent.

Pentru mai multe setări personalizate (jetoane de umplere, dispozitiv etc.), consultați scriptul pe care l-ați folosit pentru antrenare.

<!-- @test:id=verify-lora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys

out_dir = "output-gemma-3-4b-it-lora"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

if not (os.path.exists(os.path.join(out_dir, "adapter_model.safetensors")) or os.path.exists(os.path.join(out_dir, "adapter_model.bin"))):
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: LoRA output looks correct")
```
<!-- @test:end -->

<!-- @os:linux -->
<!-- @test:id=verify-qlora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys

out_dir = "output-gemma-3-4b-it-qlora"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

if not (os.path.exists(os.path.join(out_dir, "adapter_model.safetensors")) or os.path.exists(os.path.join(out_dir, "adapter_model.bin"))):
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: QLoRA output looks correct")
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @test:id=verify-full-finetuning-output timeout=300 hidden=True setup=activate-venv -->
```python
import glob
import os
import sys

out_dir = "output-gemma-3-4b-it-full"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "config.json",
    "tokenizer_config.json",
    "tokenizer.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

# Weights may be saved as a single model.safetensors or, when the model
# exceeds max_shard_size, as model-*.safetensors shards plus an index.
single = os.path.exists(os.path.join(out_dir, "model.safetensors"))
shards = glob.glob(os.path.join(out_dir, "model-*.safetensors"))
if not single and not shards:
    print("FAIL: No model safetensors weights found")
    sys.exit(1)

print(f"PASS: Full fine-tuned model output looks correct: {out_dir}")
```
<!-- @test:end -->
<!-- @device:end -->
---

## Ghid de Personalizare

### Utilizați Propriul Set de Date

Toate scripturile folosesc același format de set de date. Înlocuiți secțiunea de încărcare:

```python
from datasets import load_dataset

# Option 1: Local JSON/JSONL file
dataset = load_dataset('json', data_files='your_data.json')

# Option 2: Hugging Face Hub dataset
dataset = load_dataset('username/dataset-name')

# Option 3: CSV file
dataset = load_dataset('csv', data_files='data.csv')

# Format for chat models
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['instruction']},
            {"role": "assistant", "content": example['response']}
        ]
    }

dataset = dataset.map(format_instruction)
```

**Format de Set de Date pentru fișier JSON/JSONL local:**

Când folosiți această metodă, vă rugăm să vă asigurați că fișierele dvs. JSON sunt structurate corect pentru a evita erorile de parsare. 

Trebuie respectate următoarele orientări:
* **Formatarea Fișierului:** Fișierele JSON ar trebui formatate într-un Mediu de Dezvoltare Integrat (IDE) pentru a asigura structura și sintaxa corectă.
* **Chei Necesare:** Fișierul JSON personalizat trebuie să conțină cheile `instruction` și `response`. Aceste chei sunt esențiale pentru ca metoda să funcționeze corect.
```json
[
  {
    "instruction": "Your first instruction here",
    "response": "Expected response here"
  },
  {
    "instruction": "Your second instruction here",
    "response": "Expected response here"
  }
]
```
**Format de Set de Date pentru set de date de pe Hugging Face Hub**

Când utilizați seturi de date de pe Hugging Face, vă rugăm să vă asigurați că seturile dvs. de date sunt structurate corect pentru a facilita o integrare fără probleme. 

Trebuie respectate următoarele orientări:
* **Pereche Instrucțiune-Răspuns:** Concentrați-vă pe seturi de date care includ o pereche `instruction-response`. Această structură este esențială pentru funcționalitatea dorită.
* **Modificarea Cheilor Personalizate:** Dacă setul dvs. de date nu se conformează structurii `instruction-response`, aveți opțiunea de a modifica funcția `format_instruction()`. Aceasta vă permite să adaptați chei specifice după cum este necesar.

Exemplu de Ajustare: În cazurile în care rezultatul setului de date trebuie ajustat, puteți modifica secțiunea de răspuns din cadrul funcției format_instruction() pentru a se potrivi cerințelor dvs.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Format de Set de Date pentru fișier CSV**

Pentru a adapta scriptul la utilizarea unui format de fișier CSV, trebuie să vă asigurați că fișierul CSV conține coloane denumite `instruction` și `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Ajustați Parametrii de Antrenare

Editați scriptul de antrenare și schimbați variabilele pentru a se potrivi obiectivelor dvs.: **rata de învățare** (`LR`), **epoci** (`EPOCHS`), **dimensiunea lotului** (`BATCH_SIZE`), **acumularea gradientului** (`GRAD_ACCUM_STEPS`) și, pentru LoRA/QLoRA, **rangul** (`LORA_R`). Pentru execuții mai rapide, folosiți mai puține epoci și o rată de învățare (LR) mai mare; pentru o calitate mai bună, folosiți mai multe epoci și o LR mai mică. Reduceți dimensiunea lotului sau lungimea secvenței dacă întâmpinați erori de memorie insuficientă.
### Sfaturi pentru optimizarea memoriei

Dacă întâmpinați erori de memorie insuficientă:

**1. Reduceți dimensiunea batch-ului:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Reduceți lungimea secvenței:**
```python
max_seq_length=256  # Instead of 512
```

**3. Utilizați o cuantizare mai agresivă:**
```
Full → LoRA → QLoRA
```

**4. Activați Gradient Checkpointing (doar pentru fine-tuning complet):**
```python
model.gradient_checkpointing_enable()
```

---

## Monitorizare și depanare

### Urmăriți memoria GPU

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Opțional) Urmăriți experimentele cu Weights & Biases

Pentru a înregistra rulările și metricile în [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

În scriptul de antrenare, setați `report_to="wandb"` și, opțional, `run_name="your-experiment-name"` în configurația trainer-ului. Dacă preferați să nu utilizați Wandb, lăsați `report_to` la valoarea implicită sau setați-l la `"none"`.

### Probleme frecvente

#### Memorie insuficientă (OOM)

**Soluție:** Reduceți dimensiunea batch-ului și/sau utilizați QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### Pierderea (loss) nu scade

**Soluție:** Ajustați rata de învățare
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Antrenare lentă

**Soluție:** Creșteți dimensiunea batch-ului dacă memoria permite
```python
BATCH_SIZE = 8
```
## Pași următori

După ce ați finalizat cu succes procesul de fine-tuning, luați în considerare următorii pași pentru a obține mai mult de la modelul dvs.:

1. **Evaluați** temeinic pe date de test separate pentru a măsura generalizarea și a evita supraadaptarea (overfitting).
2. **Experimentați** încercând diferite valori ale hiperparametrilor pentru un compromis mai bun între acuratețe, viteză și memorie.
3. **Urmăriți** toate experimentele dvs. (și metricile corespunzătoare) cu Weights & Biases pentru cercetare reproductibilă.
4. **Încercați** antrenarea pe propriile seturi de date personalizate pentru a adapta modelul specific cazului dvs. de utilizare.
5. **Implementați** modelul dvs. ajustat fin pentru inferență rapidă utilizând backend-uri eficiente precum vLLM pe hardware compatibil.
6. **Explorați** tehnici avansate, inclusiv prompt engineering, precizie mixtă și lungimi de secvență mai mari.
7. **Antrenați** mai mulți adaptoare LoRA pentru sarcini sau domenii diferite și schimbați-le după necesitate.

---