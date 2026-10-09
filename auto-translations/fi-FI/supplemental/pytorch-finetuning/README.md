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

Tämä ohje tarjoaa vaiheittaisia esimerkkejä suurten kielimallien (LLM) hienosäätämiseen PyTorchin ja ROCmin avulla. Siinä käsitellään useita tekniikoita, standardista hienosäädöstä muistitehokkaisiin Parameter-Efficient Fine-Tuning (PEFT) -strategioihin, jotta voit helposti mukauttaa malleja omiin tarpeisiisi.

**Käytetty malli**: google/gemma-3-4b-it (QLoRA-skripti: openai/gpt-oss-20b)  *(katso [Enable HF authentication](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models), jos malli on rajoitettu)*  
**Laitteisto**: AMD Radeon™ -näytönohjain, jossa on ROCm-tuki  
**Kehys**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Huomio:** 
> - Täysi hienosäätö vaatii vähintään **64 Gt järjestelmämuistia**, josta vähintään **32 Gt tulee olla GPU:n käytettävissä** (tämä 32 Gt on osa 64 Gt:sta, ei sen lisäksi).
> - Voit myös kokeilla muita mallien arkkitehtuureja, mukaan lukien **GPT-OSS-20B**, korvaamalla mallin tarjotuissa koulutusskripteissä.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **Huomio:** LoRA- ja QLoRA-hienosäätö vaativat vähintään **32 Gt järjestelmämuistia**, josta vähintään **16 Gt tulee olla GPU:n käytettävissä** (tämä 16 Gt on osa 32 Gt:sta, ei sen lisäksi).
<!-- @os:end -->

<!-- @os:windows -->
> **Huomio:** LoRA-hienosäätö vaatii vähintään **32 Gt järjestelmämuistia**, josta vähintään **16 Gt tulee olla GPU:n käytettävissä** (tämä 16 Gt on osa 32 Gt:sta, ei sen lisäksi).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Huomio:** LoRA- ja QLoRA-hienosäätö vaativat näytönohjaimen, jossa on vähintään **16 Gt omistettua GPU-muistia**, sekä **32 Gt järjestelmämuistia**.
> - Linuxissa koulutus ajetaan kokonaan näytönohjaimen omistetussa VRAM-muistissa.
> - Se ei siirry jaettuun GPU-muistiin (järjestelmämuistiin), kun VRAM loppuu.
> - Näytönohjaimet, joissa on alle 16 Gt omistettua VRAM-muistia, jäävät ilman muistia koulutuksen aikana Linuxissa, vaikka järjestelmässä olisi runsaasti RAM-muistia.
<!-- @os:end -->

<!-- @os:windows -->
> **Huomio:** LoRA-hienosäätö vaatii vähintään **16 Gt kokonais-GPU-muistia** ja **32 Gt järjestelmämuistia**.
> - Windowsissa kokonais-GPU-muisti yhdistää näytönohjaimen omistetun VRAM-muistin ja jaetun GPU-muistin (lainattu järjestelmämuistista).
> - Tämän vuoksi näytönohjaimet, joissa on alle 16 Gt omistettua VRAM-muistia, voivat silti käyttää tätä ohjetta hyödyntämällä jaettua GPU-muistia erotuksen kattamiseen.
<!-- @os:end -->
<!-- @device:end -->

## Mitä opit

- Kuinka hienosäätää LLM-mallia LoRA:lla, QLoRA:lla ja täydellä hienosäädöllä PyTorchin ja ROCmin avulla
- Kuinka tallentaa ja ottaa käyttöön hienosäädetty mallisi
- Kuinka seurata koulutusta ja virheenjäljittää yleisiä ongelmia

<!-- @device:halo_box,halo,stx,krk -->
## Muistimäärityksen asettaminen

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset
> **Huomio**: Jos VS Code ei ole asennettu, voit asentaa sen Ryzen AI Developer Centerin kautta.

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmiston esivaatimusten asentaminen

#### Luo virtuaaliympäristö

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
**Myönnä käyttäjällesi pääsy GPU-laitteisiin** (kirjaudu ulos ja takaisin sisään, jotta tämä astuu voimaan):

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

#### Perusriippuvuuksien asentaminen
<!-- @require:pytorch -->

#### Lisäriippuvuudet

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Vain ydinpaketit on testattu ja niitä tuetaan täällä. **bitsandbytes ei ole hyvin tuettu Windowsissa**, joten Windows-asennus jättää sen pois; käytä LoRA:a tai täyttä hienosäätöä Windowsissa (QLoRA vaatii bitsandbytesin ja on tarkoitettu Linuxille).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### Ota HF-todennus käyttöön (rajoitetut tai mukautetut / ei-esiasennetut mallit)

Tässä esimerkissä käytämme mallia **google/gemma-3-4b-it**, joka on **rajoitettu (gated)** malli. Sinun täytyy hyväksyä mallin käyttöehdot Hugging Facessa ja sen jälkeen todentaa itsesi, jotta koulutusskriptit voivat ladata sen.

1. **Hyväksy käyttöoikeussopimus:** Avaa [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), kirjaudu sisään (tai luo tili) ja hyväksy mallin sivulla olevat käyttöehdot (esim. "Agree and access repository").
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

**LoRA (Low-Rank Adaptation)** pitää perusmallin jäädytettynä ja kouluttaa vain pieniä "adapteri"-matriiseja, jotka lisätään tiettyihin kerroksiin. 

- **Keskeinen idea**: sen sijaan, että päivitettäisiin valtava painomatriisi, jossa on miljoonia parametreja, opimme matala-asteisen päivityksen (kaksi pientä matriisia, joiden tulo sisältää huomattavasti vähemmän parametreja). Tämä vähentää merkittävästi koulutettavien parametrien määrää ja VRAM-käyttöä säilyttäen samalla suurimman osan täyden hienosäädön laadusta.

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

**QLoRA** yhdistää **4-bittisen kvantisoinnin** ja **LoRA:n**. Perusmalli ladataan 4-bittisenä (suuri muistisäästö), ja vain LoRA-adapterit koulutetaan korkeammalla tarkkuudella. Näin saat LoRA:n parametritehokkuuden ja huomattavasti pienemmän VRAM-käytön, pienellä laatukompromissilla verrattuna täyden tarkkuuden LoRA:an. Huomaa, että 4-bittinen kvantisointi voi aiheuttaa numeerista epävakautta (häviöpiikkejä tai NaN-arvoja), joten käyttäjät saattavat usein suosia **LoRA:a**, jos VRAM-muistia on riittävästi saatavilla.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Huomio**: MXFP4-perusmalleille, kuten `openai/gpt-oss-20b`, suosittelemme **LoRA:n** (`train_lora.py`) käyttöä QLoRA:n sijaan. QLoRA-skriptin `bitsandbytes`-kirjaston 4-bittinen polku yleensä dekvantisoi MXFP4-painot BF16-muotoon, jolloin ajo käyttäytyy kuin tavallinen LoRA. Natiivi MXFP4 vaatii lähdekoodista käännetyn `bitsandbytes`-kirjaston sekä yhteensopivan Transformers/Triton/kernels-pinon. Katso [Transformers MXFP4 -dokumentaatio](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. Valitse menetelmä

| Menetelmä | Muisti | Nopeus | Laatu | Soveltuu parhaiten |
|--------|--------|-------|---------|----------|
| **QLoRA** (vain Linux) | 12–16 Gt | Nopein | 90–95 % | Vähäinen muistinkäyttö |
| **LoRA** | 24–32 Gt | Nopea | 95–98 % | Tasapainoinen lähestymistapa |
| **Full** | 80 Gt+ | Hitain | 100 % | Paras mahdollinen laatu |

### 3. Suorita koulutus

**Tietoaineisto ja se, mitä malli oppii**  
Skriptit muuntavat tietoaineiston chat-esimerkeiksi. Esimerkiksi QLoRA-skripti käyttää tietoaineistoa **Abirate/english_quotes**: jokaisesta esimerkistä tulee käyttäjä–assistentti-pari seuraavasti:

- **Käyttäjä:** ”Anna minulle sitaatti aiheesta: &lt;tag&gt;”
- **Assistentti:** ”&lt;quote&gt; – &lt;author&gt;”

Hienosäätö opettaa mallia vastaamaan kehotteisiin, joissa pyydetään sitaattia tietystä aiheesta, ja palauttamaan ne muodossa `<quote text> - <author>`. LoRA- ja täydellisen hienosäädön skriptit käyttävät tietoaineistoa **databricks/databricks-dolly-15k** (yleiset ohje/vastaus-parit), joten tarkka tehtävä vaihtelee skriptin mukaan; idea on sama - mukauta malli valitsemaasi tietoaineistoon ja muotoon.

Alla on yhteenveto saatavilla olevista koulutusmenetelmistä. Jokainen menetelmä linkittyy omaan skriptiinsä ja sisältää lyhyen kuvauksen, jonka avulla voit valita oikean lähestymistavan.

| Skripti                           | Menetelmä            | Kuvaus                                                                                                         | Tyypillinen VRAM | Suositeltu käyttö                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Kouluttaa pieniä adapterimatriiseja perusmallin pysyessä jäädytettynä. 3–5 kertaa nopeampi; noin 95–98 % täydestä laadusta.                         | 24–32 Gt      | Edistyneille käyttäjille; useita adaptereita; enemmän VRAM-muistia    |
| [`train_qlora.py`](assets/train_qlora.py)  *(vain Linux)*             | **QLoRA**       | 4-bittinen kvantisointi + LoRA-adapterit. Vähäisin muistinkäyttö, nopein, pieni laatukompromissi. Vaatii `bitsandbytes`-kirjaston (vain Linux).                            | 12–16 Gt      | Useimmille käyttäjille; nopeat kokeilut; rajallinen VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Täydellinen hienosäätö** | Päivittää kaikki mallin parametrit. Paras mahdollinen laatu; suurin muistin- ja laskentatehon käyttö.                                    | 40 Gt+        | Paras mahdollinen laatu; tutkimus; paljon VRAM-muistia           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Huomautus:** Täydellinen hienosäätö (`train_full_finetuning.py`) saattaa vaatia yli 64 Gt järjestelmämuistia, eikä se välttämättä ole mahdollista tällä laitteella. Harkitse sen sijaan LoRA- tai QLoRA-menetelmän käyttöä.
<!-- @os:end -->

<!-- @os:windows -->
> **Huomautus:** Täydellinen hienosäätö (`train_full_finetuning.py`) saattaa vaatia yli 64 Gt järjestelmämuistia, eikä se välttämättä ole mahdollista tällä laitteella. Harkitse sen sijaan LoRA-menetelmän käyttöä.
<!-- @os:end -->
<!-- @device:end -->

Valitse haluamasi `Training method`, lataa vastaava skripti ja suorita se komennolla pitäen virtuaaliympäristösi aktivoituna: 

```python
python3 train_<method_name>.py.
```

## Hienosäädetyn mallisi käyttäminen

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

### LoRA/QLoRA-koulutuksen jälkeen

```python
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

# Load model with LoRA or QLoRA adapters
model = AutoPeftModelForCausalLM.from_pretrained(
    "output-gpt-oss-20b-qlora",   # or "output-gemma-3-4b-it-lora" depending on your training
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained("output-gpt-oss-20b-qlora")

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

**Huomautus:**  
- Varmista, että mallihakemiston nimi (`output-gemma-3-4b-it-full`, `output-gpt-oss-20b-qlora`) vastaa koulutuksen todellista tulostehostekansiota.  
- Jos käytit LoRA-menetelmää QLoRA:n sijaan, korvaa polku vastaavasti.  
- Jotkin Gemma-mallit vaativat `trust_remote_code=True`-määrityksen kohdassa `from_pretrained`; lisää se, jos näet tähän liittyvän varoituksen.

Lisää mukautettuja asetuksia varten (täyttömerkit, laite jne.) katso käyttämääsi koulutusskriptiä.

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

## Mukautusopas

### Oman tietoaineiston käyttäminen

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

**Tietoaineiston muoto paikalliselle JSON/JSONL-tiedostolle:**

Kun käytät tätä menetelmää, varmista, että JSON-tiedostosi ovat oikein jäsenneltyjä, jotta vältytään jäsennysvirheiltä. 

Seuraavia ohjeita on noudatettava:
* **Tiedoston muotoilu:** JSON-tiedostot tulee muotoilla integroidussa kehitysympäristössä (IDE) oikean rakenteen ja syntaksin varmistamiseksi.
* **Vaaditut avaimet:** Mukautetun JSON-tiedoston on sisällettävä avaimet `instruction` ja `response`. Nämä avaimet ovat välttämättömiä menetelmän toimimiseksi oikein.
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
**Tietoaineiston muoto Hugging Face Hub -tietoaineistolle**

Kun käytät Hugging Face -tietoaineistoja, varmista, että tietoaineistosi ovat oikein jäsenneltyjä sujuvan integroinnin mahdollistamiseksi. 

Seuraavia ohjeita tulisi noudattaa:
* **Ohje–vastaus-pari:** Keskity tietoaineistoihin, jotka sisältävät `instruction-response`-parin. Tämä rakenne on olennainen halutun toiminnallisuuden kannalta.
* **Avaimien mukautettu muokkaus:** Jos tietoaineistosi ei noudata `instruction-response`-rakennetta, voit muokata `format_instruction()`-funktiota. Näin voit mukauttaa tarvittavia avaimia.

Esimerkki mukautuksesta: Jos tietoaineiston tulostetta on tarvetta säätää, voit muokata `format_instruction()`-funktion vastausosiota tarpeidesi mukaan.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Tietoaineiston muoto CSV-tiedostolle**

Jotta skripti toimisi CSV-tiedostomuodon kanssa, varmista, että CSV-tiedostossa on sarakkeet nimeltä `instruction` ja `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Koulutusparametrien säätäminen

Muokkaa koulutusskriptiä ja muuta muuttujia tavoitteidesi mukaisesti: **oppimisnopeus** (`LR`), **epookit** (`EPOCHS`), **eräkoko** (`BATCH_SIZE`), **gradienttien kertymä** (`GRAD_ACCUM_STEPS`) ja LoRA/QLoRA-menetelmille **järjestysluku** (`LORA_R`). Nopeampia ajoja varten käytä vähemmän epookkeja ja korkeampaa oppimisnopeutta (LR); paremman laadun saavuttamiseksi käytä enemmän epookkeja ja alhaisempaa LR-arvoa. Pienennä eräkokoa tai sekvenssin pituutta, jos muisti loppuu kesken.
### Muistin optimointivinkit

Jos kohtaat muistin loppumiseen liittyviä virheitä:

**1. Pienennä eräkokoa:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Pienennä sekvenssin pituutta:**
```python
max_seq_length=256  # Instead of 512
```

**3. Käytä voimakkaampaa kvantisointia:**
```
Full → LoRA → QLoRA
```

**4. Ota käyttöön gradient checkpointing (vain täydelle hienosäädölle):**
```python
model.gradient_checkpointing_enable()
```

---

## Seuranta ja virheenjäljitys

### Tarkkaile GPU-muistia

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Valinnainen) Seuraa kokeiluja Weights & Biasesilla

Jotta voit kirjata ajot ja mittarit palveluun [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

Aseta koulutusskriptissä `report_to="wandb"` ja valinnaisesti `run_name="your-experiment-name"` trainer-konfiguraatiossa. Jos et halua käyttää Wandbia, jätä `report_to` oletusarvoonsa tai aseta se arvoon `"none"`.

### Yleisiä ongelmia

#### Muisti loppuu (OOM)

**Ratkaisu:** Pienennä eräkokoa ja/tai käytä QLoRA
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

**Ratkaisu:** Suurenna eräkokoa, jos muisti sen sallii
```python
BATCH_SIZE = 8
```
## Seuraavat vaiheet

Kun olet suorittanut hienosäädön onnistuneesti, harkitse seuraavia vaiheita saadaksesi mallistasi enemmän irti:

1. **Arvioi** perusteellisesti erillisellä testidatalla yleistymiskyvyn mittaamiseksi ja ylisovittumisen välttämiseksi.
2. **Kokeile** erilaisia hyperparametriarvoja saavuttaaksesi paremman tasapainon tarkkuuden, nopeuden ja muistinkäytön välillä.
3. **Seuraa** kaikkia kokeilujasi (ja niihin liittyviä mittareita) Weights & Biasesin avulla toistettavaa tutkimusta varten.
4. **Kokeile** koulutusta omilla mukautetuilla datajoukoillasi mukauttaaksesi mallin juuri omaan käyttötarkoitukseesi.
5. **Ota käyttöön** hienosäädetty mallisi nopeaa päättelyä varten käyttämällä tehokkaita taustajärjestelmiä, kuten vLLM, yhteensopivalla laitteistolla.
6. **Tutki** edistyneempiä tekniikoita, kuten prompt engineering -menetelmiä, sekatarkkuutta (mixed precision) ja pidempiä sekvenssin pituuksia.
7. **Kouluta** useita LoRA-adaptereita eri tehtäviä tai osa-alueita varten ja vaihda niitä tarpeen mukaan.

---