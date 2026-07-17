<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Yleiskatsaus

Tämä opas tarjoaa vaiheittaiset esimerkit suuren kielimallin (LLM) hienosäätöön PyTorch- ja ROCm-ympäristössä. Se kattaa useita tekniikoita, tavallisesta hienosäädöstä muistitehokkaisiin Parameter-Efficient Fine-Tuning (PEFT) -strategioihin, jotta voit helposti mukauttaa malleja tarpeisiisi.

**Käytetty malli**: google/gemma-3-4b-it  *(katso [HF-todennuksen käyttöönotto](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) jos malli on suojattu)*  
**Laitteisto**: AMD Radeon™ GPU ROCm-tuella  
**Kehys**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Huomio:** Voit myös kokeilla muita malliarkkitehtuureja, kuten **GPT-OSS-20B**, korvaamalla mallin annetuissa harjoitusskripteissä.
> Täydellinen hienosäätö vaatii vähintään 32 Gt GPU-muistia ja 64 Gt järjestelmämuistia.
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> **Huomio:** LoRA- ja QLoRA-hienosäätö vaatii vähintään 16 Gt GPU-muistia ja 32 Gt järjestelmämuistia.
<!-- @device:end -->

## Mitä opit

- Kuinka hienosäätää LLM LoRA-, QLoRA- ja täydellä hienosäädöllä PyTorchin ja ROCmin avulla
- Kuinka tallentaa ja ottaa käyttöön hienosäädetty malli
- Kuinka seurata harjoittelua ja korjata yleisiä ongelmia

## Muistikonfiguraation asettaminen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset
> **Huomio**: Jos VS Code ei ole asennettuna, voit asentaa sen Ryzen AI Developer Centerin kautta.

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmistoedellytysten asentaminen

#### Luo virtuaaliympäristö

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=60 -->
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
**Myönnä käyttäjällesi pääsy GPU-laitteisiin** (kirjaudu ulos ja takaisin sisään, jotta muutos tulee voimaan):

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=120 -->
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
<!-- @test:id=create-venv timeout=60 -->
```powershell
python -m venv finetune-venv --system-site-packages
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=60 -->
```powershell
python -m venv finetune-venv
finetune-venv\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="finetune-venv\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

#### Perusriippuvuuksien asentaminen
<!-- @require:pytorch -->

#### Lisäriippuvuudet

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Vain ydinpaketit on testattu ja tuettu tässä. **bitsandbytes ei ole hyvin tuettu Windowsissa**, joten Windows-asennus jättää sen pois; käytä LoRA- tai täyttä hienosäätöä Windowsissa (QLoRA vaatii bitsandbytes-paketin ja on tarkoitettu Linuxille).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### HF-todennuksen käyttöönotto (suojatut tai mukautetut / ei-esiasennettut mallit)

Tässä esimerkissä käytämme **google/gemma-3-4b-it**-mallia, joka on **suojattu** malli. Sinun täytyy hyväksyä mallin käyttöehdot Hugging Facessa ja todentautua, jotta harjoitusskriptit voivat ladata sen.

1. **Hyväksy lisenssi:** Avaa [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), kirjaudu sisään (tai luo tili) ja hyväksy lisenssi/käyttöehdot mallin sivulla (esim. "Agree and access repository").
2. **Asenna ja kirjaudu sisään:** Asenna Hugging Face CLI ja suorita sitten tavallinen kirjautuminen:

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

## Tekniikoiden ymmärtäminen

### Mikä on LoRA?

**LoRA (Low-Rank Adaptation)** pitää perusmallin jäädytettynä ja harjoittaa vain pieniä "adapteri"-matriiseja, jotka lisätään tiettyihin kerroksiin.

- **Keskeinen idea**: sen sijaan, että päivitettäisiin valtava painomatriisi miljoonilla parametreilla, opitaan matalan rankin päivitys (kaksi pientä matriisia, joiden tulo sisältää huomattavasti vähemmän parametreja). Tämä vähentää merkittävästi harjoitettavien parametrien määrää ja VRAM-käyttöä säilyttäen samalla suurimman osan täydellisen hienosäädön laadusta.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### Mikä on QLoRA?

**QLoRA** yhdistää **4-bittisen kvantisoinnin** ja **LoRA**n. Perusmalli ladataan 4-bittisenä (suuri muistinsäästö), ja vain LoRA-adapterit harjoitetaan korkeammalla tarkkuudella. Näin saadaan LoRA:n parametritehokkuus sekä huomattavasti pienempi VRAM-käyttö, pienellä laadun heikkenemisellä verrattuna täyden tarkkuuden LoRA:an. Huomaa, että 4-bittinen kvantisointi voi aiheuttaa numeerisia epävakauksia (häviöpiikkejä tai NaN-arvoja), joten käyttäjät saattavat usein suosia **LoRA**a, jos VRAM-muistia on riittävästi.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Huomio**: MXFP4-perusmalleille, kuten `openai/gpt-oss-20b`, suosittelemme käyttämään **LoRA**a (`train_lora.py`) QLoRA:n sijaan. QLoRA-skriptin `bitsandbytes` 4-bittinen polku tyypillisesti dekvantisoii MXFP4-painot BF16-muotoon, joten ajo käyttäytyy kuten tavallinen LoRA. Natiivi MXFP4 vaatii `bitsandbytes`-paketin rakentamisen lähdekoodista sekä yhteensopivan Transformers/Triton/kernels-pinon. Katso [Transformers MXFP4 -dokumentaatio](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---

### 2. Valitse menetelmäsi

| Menetelmä | Muisti | Nopeus | Laatu | Parhaiten sopii |
|--------|--------|-------|---------|----------|
| **QLoRA** (vain Linux) | 12–16 Gt | Nopein | 90–95 % | Vähäinen muistinkäyttö |
| **LoRA** | 24–32 Gt | Nopea | 95–98 % | Tasapainoinen lähestymistapa |
| **Täysi** | 80 Gt+ | Hitain | 100 % | Maksimilaatu |

### 3. Suorita harjoittelu

**Tietoaineisto ja mitä malli oppii**  
Skriptit muuntavat tietoaineiston chat-esimerkeiksi. Esimerkiksi QLoRA-skripti käyttää **Abirate/english_quotes** -aineistoa: kustakin esimerkistä muodostuu käyttäjä–assistentti-pari, kuten:

- **Käyttäjä:** "Give me a quote about: &lt;tag&gt;"
- **Assistentti:** "&lt;quote&gt; – &lt;author&gt;"

Hienosäätö opettaa mallin vastaamaan kehotteisiin, joissa pyydetään lainauksia tietystä aiheesta, ja palauttamaan ne muodossa `<quote text> - <author>`. LoRA- ja täyden hienosäädön skriptit käyttävät **databricks/databricks-dolly-15k** -aineistoa (yleiset ohje/vastaus-parit), joten tarkka tehtävä vaihtelee skriptin mukaan; idea on sama – mukauta malli valitsemaasi tietoaineistoon ja muotoon.

Alla on yhteenveto käytettävissä olevista harjoitusmenetelmistä. Kukin menetelmä linkittää skriptiinsä ja sisältää lyhyen kuvauksen oikean lähestymistavan valitsemiseksi.

| Skripti | Menetelmä | Kuvaus | Tyypillinen VRAM | Suositellaan |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py) | **LoRA** | Harjoittaa pieniä adapteri­matriiseja jäädyttäen perusmallin. 3–5× nopeampi; ~95–98 % täydestä laadusta. | 24–32 Gt | Edistyneet käyttäjät; useita adaptereita; enemmän VRAM-muistia |
| [`train_qlora.py`](assets/train_qlora.py) *(vain Linux)* | **QLoRA** | 4-bittinen kvantisointi + LoRA-adapterit. Pienin muistinkäyttö, nopein, pieni laadun heikkeneminen. Vaatii `bitsandbytes`-paketin (vain Linux). | 12–16 Gt | Useimmat käyttäjät; nopeat kokeilut; rajallinen VRAM |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Täysi hienosäätö** | Päivittää kaikki mallin parametrit. Maksimilaatu; suurin muisti- ja laskentakäyttö. | 40 Gt+ | Maksimilaatu; tutkimus; suuri VRAM |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Huomio:** Täysi hienosäätö (`train_full_finetuning.py`) saattaa vaatia yli 64 Gt järjestelmämuistia eikä välttämättä ole toteutettavissa tällä laitteella. Harkitse LoRA:n tai QLoRA:n käyttöä sen sijaan.
<!-- @os:end -->

<!-- @os:windows -->
> **Huomio:** Täysi hienosäätö (`train_full_finetuning.py`) saattaa vaatia yli 64 Gt järjestelmämuistia eikä välttämättä ole toteutettavissa tällä laitteella. Harkitse LoRA:n käyttöä sen sijaan.
<!-- @os:end -->
<!-- @device:end -->

Valitse haluamasi `Harjoitusmenetelmä`, lataa vastaava skripti ja suorita se seuraavalla komennolla pitäen virtuaaliympäristösi aktivoituna:

```python
python3 train_<method_name>.py.
```

## Hienosäädetyn mallin käyttäminen

### Täydellisen hienosäädön jälkeen

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

### LoRA/QLoRA-harjoittelun jälkeen

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

### LoRA-adapterin yhdistäminen perusmalliin

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Huomio:**  
- Varmista, että hakemiston nimi (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) vastaa harjoittelun todellista tulostehakemistoa.  
- Jos käytit LoRA:a QLoRA:n sijaan, korvaa polku vastaavasti.  
- Jotkin Gemma-mallit vaativat `trust_remote_code=True`-parametrin määrittämistä `from_pretrained`-kutsussa; lisää se, jos näet asiaan liittyvän varoituksen.

Lisäasetuksia varten (täytemerkit, laite jne.) katso harjoitteluun käyttämääsi skriptiä.

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
    "model.safetensors.index.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

shards = glob.glob(os.path.join(out_dir, "model-*.safetensors"))
if not shards:
    print("FAIL: No sharded model safetensors files found")
    sys.exit(1)

print(f"PASS: Full fine-tuned model output looks correct: {out_dir}")
```
<!-- @test:end -->
<!-- @device:end -->
---

## Mukauttamisopas

### Käytä omaa tietoaineistoasi

Kaikki skriptit käyttävät samaa tietoaineistomuotoa. Korvaa latausosio:

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

**Tietoaineistomuoto paikalliselle JSON/JSONL-tiedostolle:**

Tätä menetelmää käytettäessä varmista, että JSON-tiedostosi on oikein jäsennelty jäsennysvirheiden välttämiseksi.

Seuraavia ohjeita on noudatettava:
* **Tiedoston muotoilu:** JSON-tiedostot tulee muotoilla integroidussa kehitysympäristössä (IDE) oikean rakenteen ja syntaksin varmistamiseksi.
* **Vaaditut avaimet:** Mukautetun JSON-tiedoston on sisällettävä avaimet `instruction` ja `response`. Nämä avaimet ovat välttämättömiä menetelmän oikealle toiminnalle.
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
**Tietoaineistomuoto Hugging Face Hub -aineistolle**

Hugging Facen aineistoja käytettäessä varmista, että aineistosi on jäsennelty oikein saumattoman integraation mahdollistamiseksi.

Seuraavia ohjeita tulee noudattaa:
* **Ohje-vastaus-pari:** Keskity aineistoihin, jotka sisältävät `instruction-response`-parin. Tämä rakenne on välttämätön tarkoitetun toiminnallisuuden kannalta.
* **Mukautettujen avainten muokkaaminen:** Jos aineistosi ei noudata `instruction-response`-rakennetta, voit muokata `format_instruction()`-funktiota. Tämä mahdollistaa tiettyjen avainten käyttämisen tarpeen mukaan.

Esimerkkimuokkaus: Tapauksissa, joissa aineiston tulostetta on muokattava, voit muuttaa vastausosiota `format_instruction()`-funktion sisällä tarpeidesi mukaisesti.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Tietoaineistomuoto CSV-tiedostolle**

Jotta skripti toimii CSV-tiedostomuodolla, varmista, että CSV-tiedosto sisältää sarakkeet nimeltä `instruction` ja `response`.
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Harjoitusparametrien säätäminen

Muokkaa harjoitusskriptiä ja muuta muuttujia tavoitteidesi mukaan: **oppimisvauhti** (`LR`), **epookit** (`EPOCHS`), **eräkoko** (`BATCH_SIZE`), **gradienttien kertyminen** (`GRAD_ACCUM_STEPS`) ja LoRA/QLoRA:lle **rankin arvo** (`LORA_R`). Nopeampiin ajoihin käytä vähemmän epookkeja ja korkeampaa oppimisnopeutta (LR); parempaan laatuun käytä enemmän epookkeja ja pienempää LR-arvoa. Pienennä eräkokoa tai sekvenssipituutta, jos kohtaat muistin loppumisvirheitä.

### Muistin optimointivinkit

Jos kohtaat muistin loppumisvirheitä:

**1. Pienennä eräkokoa:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Pienennä sekvenssipituutta:**
```python
max_seq_length=256  # Instead of 512
```

**3. Käytä aggressiivisempaa kvantisointia:**
```
Full → LoRA → QLoRA
```

**4. Ota käyttöön gradienttitarkistuspisteet (vain täysi hienosäätö):**
```python
model.gradient_checkpointing_enable()
```

---

## Seuranta ja virheenkorjaus

### Seuraa GPU-muistia

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Valinnainen) Seuraa kokeiluja Weights & Biasesin avulla

Ajojen ja mittareiden kirjaamiseksi [Weights & Biasesiin](https://wandb.ai):

```bash
pip install wandb
wandb login
```

Aseta harjoitusskriptissä `report_to="wandb"` ja valinnaisesti `run_name="your-experiment-name"` trainer-konfiguraatiossa. Jos et halua käyttää Wandbia, jätä `report_to` oletusarvoonsa tai aseta se arvoon `"none"`.

### Yleisiä ongelmia

#### Muisti loppuu (OOM)

**Ratkaisu:** Pienennä eräkokoa ja/tai käytä QLoRA:a
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### Häviö ei pienene

**Ratkaisu:** Säädä oppimisnopeutta
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Hidas harjoittelu

**Ratkaisu:** Suurenna eräkokoa, jos muisti sallii
```python
BATCH_SIZE = 8
```
## Seuraavat askeleet

Kun olet suorittanut onnistuneen hienosäädön, harkitse seuraavia askeleita saadaksesi enemmän irti mallistasi:

1. **Arvioi** perusteellisesti erillisellä testiaineistolla yleistyvyyden mittaamiseksi ja ylisovittamisen välttämiseksi.
2. **Kokeile** eri hyperparametriarvoja paremman tarkkuuden, nopeuden ja muistin tasapainottamiseksi.
3. **Seuraa** kaikkia kokeilujasi (ja vastaavia mittareitasi) Weights & Biasesin avulla toistettavan tutkimuksen varmistamiseksi.
4. **Kokeile** harjoittelua omilla mukautetuilla tietoaineistoillasi mallin mukauttamiseksi erityisesti käyttötapaukseesi.
5. **Ota käyttöön** hienosäädetty mallisi nopeaa päättelyä varten tehokkaiden taustajärjestelmien, kuten vLLM:n, avulla yhteensopivalla laitteistolla.
6. **Tutustu** edistyneisiin tekniikoihin, kuten kehotesuunnitteluun, sekatarkkuuteen ja pidempiin sekvenssipituuksiin.
7. **Harjoita** useita LoRA-adaptereita eri tehtäviä tai toimialoja varten ja vaihda niitä tarpeen mukaan.

---