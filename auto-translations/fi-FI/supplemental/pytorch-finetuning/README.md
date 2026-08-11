<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se voi sisältää virheitä, ja tietyt ohjeet, komennot, lataukset, tuotteiden saatavuus tai muu sisältö voivat vaihdella kielen tai alueen mukaan. Mahdollisten ristiriitaisuuksien tai epäjohdonmukaisuuksien ilmetessä alkuperäinen englanninkielinen playbook on ratkaiseva ja ensisijainen versio.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Yleiskatsaus

Tämä opas tarjoaa vaiheittaisia esimerkkejä suuren kielimallin (LLM) hienosäätämisestä PyTorchilla ja ROCmilla. Se kattaa useita tekniikoita tavanomaisesta hienosäädöstä muistitehokkaisiin PEFT-strategioihin (Parameter-Efficient Fine-Tuning), jotta voit mukauttaa malleja helposti omiin tarpeisiisi.

**Käytetty malli**: google/gemma-3-4b-it  *(katso [Enable HF authentication](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models), jos malli on rajoitettu)*  
**Laitteisto**: AMD Radeon™ -näytönohjain, jossa on ROCm-tuki  
**Kehys**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Huomautus:** 
> - Täysi hienosäätö vaatii vähintään **64 Gt järjestelmämuistia**, josta vähintään **32 Gt tulee olla GPU:n käytettävissä** (32 Gt on osa 64 Gt:sta, ei sen lisäksi).
> - Voit myös kokeilla muita mallien arkkitehtuureja, mukaan lukien **GPT-OSS-20B**, korvaamalla mallin annetuissa koulutusskripteissä.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **Huomautus:** LoRA- ja QLoRA-hienosäätö vaativat vähintään **32 Gt järjestelmämuistia**, josta vähintään **16 Gt tulee olla GPU:n käytettävissä** (16 Gt on osa 32 Gt:sta, ei sen lisäksi).
<!-- @os:end -->

<!-- @os:windows -->
> **Huomautus:** LoRA-hienosäätö vaatii vähintään **32 Gt järjestelmämuistia**, josta vähintään **16 Gt tulee olla GPU:n käytettävissä** (16 Gt on osa 32 Gt:sta, ei sen lisäksi).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Huomautus:** LoRA- ja QLoRA-hienosäätö vaativat näytönohjaimen, jossa on vähintään **16 Gt omistettua GPU-muistia**, sekä **32 Gt järjestelmämuistia**.
> - Linuxissa koulutus toimii kokonaan näytönohjaimen omistetussa VRAM-muistissa.
> - Se ei siirry jaettuun GPU-muistiin (järjestelmämuistiin), kun VRAM loppuu kesken.
> - Näytönohjaimet, joissa on alle 16 Gt omistettua VRAM-muistia, jäävät ilman muistia koulutuksen aikana Linuxissa, vaikka järjestelmässä olisi paljon RAM-muistia.
<!-- @os:end -->

<!-- @os:windows -->
> **Huomautus:** LoRA-hienosäätö vaatii vähintään **16 Gt GPU-muistia yhteensä** ja **32 Gt järjestelmämuistia**.
> - Windowsissa GPU-muisti yhteensä koostuu näytönohjaimen omistetusta VRAM-muistista ja jaetusta GPU-muistista (lainattu järjestelmämuistista).
> - Tämän vuoksi näytönohjaimet, joissa on alle 16 Gt omistettua VRAM-muistia, voivat silti käyttää tätä ohjekirjaa hyödyntämällä jaettua GPU-muistia erotuksen kattamiseen.
<!-- @os:end -->
<!-- @device:end -->

## Mitä opit

- Miten hienosäätää LLM:ää käyttäen LoRA:aa, QLoRA:aa ja täyttä hienosäätöä PyTorchilla ja ROCmilla
- Miten tallentaa ja ottaa käyttöön hienosäädetty mallisi
- Miten seurata koulutusta ja vianmäärittää yleisiä ongelmia

## Muistiasetusten määrittäminen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset
> **Huomautus**: Jos VS Code ei ole asennettu, voit asentaa sen Ryzen AI Developer Centerillä.

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmiston edellytysten asentaminen

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
**Myönnä käyttäjällesi pääsy GPU-laitteisiin** (kirjaudu ulos ja takaisin sisään, jotta tämä tulee voimaan):

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
**Windows:** Vain ydinpaketit on testattu ja tuettu tässä. **bitsandbytes ei ole hyvin tuettu Windowsissa**, joten Windows-asennus jättää sen pois; käytä Windowsissa LoRA:aa tai täyttä hienosäätöä (QLoRA vaatii bitsandbytes-kirjaston ja on tarkoitettu Linuxille).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### HF-todennuksen käyttöönotto (rajoitetut tai mukautetut / ei-esiasennetut mallit)

Tässä esimerkissä käytämme mallia **google/gemma-3-4b-it**, joka on **rajoitettu (gated)** malli. Sinun on hyväksyttävä mallin käyttöehdot Hugging Facessa ja sen jälkeen todennettava itsesi, jotta koulutusskriptit voivat ladata sen.

1. **Hyväksy lisenssi:** Avaa [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), kirjaudu sisään (tai luo tili) ja hyväksy lisenssi/ehdot mallin sivulla (esim. "Agree and access repository").
2. **Asenna ja kirjaudu sisään:** Asenna Hugging Face CLI ja suorita sitten tavanomainen kirjautuminen:

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

**LoRA (Low-Rank Adaptation)** pitää perusmallin jäädytettynä ja kouluttaa vain pieniä "sovitin"-matriiseja, jotka lisätään tiettyihin kerroksiin. 

- **Keskeinen idea**: sen sijaan, että päivitettäisiin valtava painomatriisi, jossa on miljoonia parametreja, opimme matalan rangin päivityksen (kaksi pientä matriisia, joiden tulossa on huomattavasti vähemmän parametreja). Tämä antaa suuren vähennyksen koulutettavissa parametreissa ja VRAM-muistin käytössä säilyttäen samalla suurimman osan täyden hienosäädön laadusta.

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

**QLoRA** yhdistää **4-bittisen kvantisoinnin** ja **LoRA:n**. Perusmalli ladataan 4-bittisenä (suuret muistisäästöt), ja vain LoRA-sovittimet koulutetaan korkeammalla tarkkuudella. Näin saat LoRA:n parametritehokkuuden lisäksi paljon matalamman VRAM-muistin käytön, pienellä laatukompromissilla verrattuna täyden tarkkuuden LoRA:aan. Huomaa, että 4-bittinen kvantisointi voi aiheuttaa numeerista epävakautta (häviöpiikkejä tai NaN-arvoja), joten käyttäjät saattavat usein suosia **LoRA:aa**, jos VRAM-muistia on riittävästi käytettävissä.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Huomautus**: MXFP4-perusmalleille, kuten `openai/gpt-oss-20b`, suosittelemme käyttämään **LoRA:aa** (`train_lora.py`) QLoRA:n sijaan. QLoRA-skriptin `bitsandbytes`-kirjaston 4-bittinen polku yleensä dekvantisoi MXFP4-painot BF16-muotoon, jolloin ajo käyttäytyy kuten tavanomainen LoRA. Natiivi MXFP4 vaatii lähdekoodista käännetyn `bitsandbytes`-kirjaston sekä vastaavan Transformers/Triton/kernels-pinon. Katso [Transformers MXFP4 -dokumentaatio](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. Valitse menetelmäsi

| Menetelmä | Muisti | Nopeus | Laatu | Sopii parhaiten |
|--------|--------|-------|---------|----------|
| **QLoRA** (vain Linux) | 12-16GB | Nopein | 90-95% | Alhainen muistinkäyttö |
| **LoRA** | 24-32GB | Nopea | 95-98% | Tasapainoinen lähestymistapa |
| **Full** | 80GB+ | Hitain | 100% | Maksimaalinen laatu |

### 3. Suorita koulutus

**Tietoaineisto ja mitä malli oppii**  
Skriptit muuntavat tietoaineiston keskusteluesimerkeiksi. Esimerkiksi QLoRA-skripti käyttää tietoaineistoa **Abirate/english_quotes**: jokaisesta esimerkistä tulee käyttäjä–assistentti-pari, kuten:

- **Käyttäjä:** ”Anna minulle sitaatti aiheesta: &lt;tag&gt;”
- **Assistentti:** ”&lt;quote&gt; – &lt;author&gt;”

Hienosäätö opettaa mallia vastaamaan kehotteisiin, joissa pyydetään sitaatteja tietystä aiheesta, ja palauttamaan ne muodossa `<quote text> - <author>`. LoRA- ja täyden hienosäädön skriptit käyttävät tietoaineistoa **databricks/databricks-dolly-15k** (yleiset ohje/vastaus-parit), joten tarkka tehtävä vaihtelee skriptin mukaan; idea on sama - mukauta malli valitsemasi tietoaineiston ja muodon mukaan.

Alla on yhteenveto käytettävissä olevista koulutusmenetelmistä. Jokainen menetelmä linkittää skriptiinsä ja tarjoaa lyhyen kuvauksen oikean lähestymistavan valitsemiseksi.

| Skripti                           | Menetelmä            | Kuvaus                                                                                                         | Tyypillinen VRAM | Suositellaan                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Kouluttaa pieniä adapterimatriiseja jäädyttäen peruskielimallin. 3–5x nopeampi; ~95–98% täydestä laadusta.                         | 24–32GB      | Kokeneille käyttäjille; useita adaptereita; enemmän VRAM-muistia    |
| [`train_qlora.py`](assets/train_qlora.py)  *(vain Linux)*             | **QLoRA**       | 4-bittinen kvantisointi + LoRA-adapterit. Pienin muistinkäyttö, nopein, pieni laatukompromissi. Vaatii pakettia `bitsandbytes` (vain Linux).                            | 12–16GB      | Useimmille käyttäjille; nopeisiin kokeiluihin; rajalliseen VRAM-muistiin      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Täysi hienosäätö** | Päivittää kaikki mallin parametrit. Maksimaalinen laatu; suurin muistin- ja laskentatehon käyttö.                                    | 40GB+      | Maksimaalinen laatu; tutkimus; suuri VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Huomautus:** Täysi hienosäätö (`train_full_finetuning.py`) saattaa vaatia yli 64 Gt järjestelmämuistia, eikä se välttämättä ole toteutettavissa tällä laitteella. Harkitse sen sijaan LoRA:n tai QLoRA:n käyttöä.
<!-- @os:end -->

<!-- @os:windows -->
> **Huomautus:** Täysi hienosäätö (`train_full_finetuning.py`) saattaa vaatia yli 64 Gt järjestelmämuistia, eikä se välttämättä ole toteutettavissa tällä laitteella. Harkitse sen sijaan LoRA:n käyttöä.
<!-- @os:end -->
<!-- @device:end -->

Valitse haluamasi `Training method`, lataa vastaava skripti ja suorita se komennolla pitäen virtuaaliympäristösi aktivoituna: 

```python
python3 train_<method_name>.py.
```

## Hienosäädetyn mallisi käyttäminen

### Täyden hienosäädön jälkeen

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

### LoRA/QLoRA-koulutuksen jälkeen

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

### Yhdistä LoRA-adapteri peruskielimalliin

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Huomautus:**  
- Varmista, että mallihakemiston nimi (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) vastaa koulutuksesta saatua todellista tuloskansiotasi.  
- Jos käytit LoRA:a QLoRA:n sijaan, korvaa polku vastaavasti.  
- Jotkin Gemma-mallit vaativat parametrin `trust_remote_code=True` määrittämisen kohdassa `from_pretrained`; lisää se, jos näet siihen liittyvän varoituksen.

Lisää mukautettuja asetuksia varten (täyttötunnukset, laite jne.) katso käyttämääsi koulutusskriptiä.

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

## Mukautusopas

### Käytä omaa tietoaineistoasi

Kaikki skriptit käyttävät samaa tietoaineistomuotoa. Korvaa lataus-osio:

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

Kun käytät tätä menetelmää, varmista, että JSON-tiedostosi on jäsennelty oikein jäsennysvirheiden välttämiseksi. 

Seuraavia ohjeita on noudatettava:
* **Tiedoston muotoilu:** JSON-tiedostot tulee muotoilla integroidussa kehitysympäristössä (IDE) oikean rakenteen ja syntaksin varmistamiseksi.
* **Vaaditut avaimet:** Mukautetun JSON-tiedoston on sisällettävä avaimet `instruction` ja `response`. Nämä avaimet ovat välttämättömiä menetelmän oikean toiminnan kannalta.
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
**Tietoaineistomuoto Hugging Face Hub -tietoaineistolle**

Kun käytät Hugging Face -tietoaineistoja, varmista, että tietoaineistosi on jäsennelty oikein saumattoman integroinnin mahdollistamiseksi. 

Seuraavia ohjeita tulee noudattaa:
* **Ohje-vastaus-pari:** Keskity tietoaineistoihin, jotka sisältävät `instruction-response`-parin. Tämä rakenne on välttämätön aiotun toiminnallisuuden kannalta.
* **Mukautetun avaimen muokkaus:** Jos tietoaineistosi ei noudata `instruction-response`-rakennetta, voit muokata `format_instruction()`-funktiota. Näin voit mukauttaa tarvittavat avaimet.

Esimerkkimukautus: Tapauksissa, joissa tietoaineiston tulostetta on säädettävä, voit muokata vastausosaa format_instruction()-funktiossa tarpeidesi mukaan.
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

Jotta skripti voisi käyttää CSV-tiedostomuotoa, sinun on varmistettava, että CSV-tiedosto sisältää sarakkeet nimeltä `instruction` ja `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Säädä koulutusparametreja

Muokkaa koulutusskriptiä ja muuta muuttujia tavoitteidesi mukaan: **oppimisnopeus** (`LR`), **epookit** (`EPOCHS`), **eräkoko** (`BATCH_SIZE`), **gradienttien kertyminen** (`GRAD_ACCUM_STEPS`) ja LoRA/QLoRA:lle **rank** (`LORA_R`). Nopeampia ajoja varten käytä vähemmän epookkeja ja suurempaa oppimisnopeutta (LR); parempaa laatua varten käytä enemmän epookkeja ja pienempää LR-arvoa. Vähennä eräkokoa tai sekvenssin pituutta, jos muisti loppuu kesken.
### Muistin optimointivinkit

Jos kohtaat muistin loppumiseen liittyviä virheitä:

**1. Pienennä eräkokoa (Batch Size):**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Lyhennä sekvenssin pituutta:**
```python
max_seq_length=256  # Instead of 512
```

**3. Käytä voimakkaampaa kvantisointia:**
```
Full → LoRA → QLoRA
```

**4. Ota käyttöön gradienttien tarkistuspisteet (Gradient Checkpointing) (vain täydellisessä hienosäädössä):**
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

### (Valinnainen) Seuraa kokeiluja Weights & Biases -palvelulla

Kirjaa ajot ja mittarit [Weights & Biases](https://wandb.ai) -palveluun:

```bash
pip install wandb
wandb login
```

Aseta koulutusskriptissä `report_to="wandb"` ja valinnaisesti `run_name="your-experiment-name"` trainer-asetuksissa. Jos et halua käyttää Wandbia, jätä `report_to` oletusarvoonsa tai aseta se arvoon `"none"`.

### Yleiset ongelmat

#### Muisti loppuu (OOM)

**Ratkaisu:** Pienennä eräkokoa ja/tai käytä QLoRA-menetelmää
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

#### Hidas koulutus

**Ratkaisu:** Kasvata eräkokoa, jos muisti riittää
```python
BATCH_SIZE = 8
```
## Seuraavat vaiheet

Kun olet onnistuneesti suorittanut hienosäädön, harkitse seuraavia vaiheita saadaksesi mallistasi enemmän irti:

1. **Arvioi** malli perusteellisesti erillisellä testidatalla yleistettävyyden mittaamiseksi ja ylisovittamisen välttämiseksi.
2. **Kokeile** erilaisia hyperparametrien arvoja paremman tarkkuuden, nopeuden ja muistinkäytön tasapainon saavuttamiseksi.
3. **Seuraa** kaikkia kokeilujasi (ja niihin liittyviä mittareita) Weights & Biases -palvelulla toistettavaa tutkimusta varten.
4. **Kokeile** koulutusta omilla mukautetuilla datajoukoillasi mukauttaaksesi mallin juuri sinun käyttötapaukseesi sopivaksi.
5. **Ota käyttöön** hienosäädetty mallisi nopeaa päättelyä varten käyttämällä tehokkaita taustajärjestelmiä, kuten vLLM, yhteensopivalla laitteistolla.
6. **Tutustu** edistyneempiin tekniikoihin, kuten kehotesuunnitteluun (prompt engineering), sekatarkkuuslaskentaan ja pidempiin sekvenssin pituuksiin.
7. **Kouluta** useita LoRA-adaptereita eri tehtäviä tai osa-alueita varten ja vaihda niitä tarpeen mukaan.

---