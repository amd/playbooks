<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Pregled

Ta vadnica ponuja postopne primere za natančno prilagajanje velikega jezikovnega modela (LLM) s pomočjo PyTorch in ROCm. Pokriva več tehnik, od standardnega natančnega prilagajanja do pomnilniško učinkovitih strategij Parameter-Efficient Fine-Tuning (PEFT), tako da lahko modele preprosto prilagodite svojim potrebam.

**Uporabljen model**: google/gemma-3-4b-it (skripta QLoRA: openai/gpt-oss-20b)  *(glejte [Omogočanje avtentikacije HF](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models), če gre za model z omejenim dostopom)*  
**Strojna oprema**: GPU AMD Radeon™ s podporo ROCm  
**Ogrodje**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Opomba:** 
> - Popolno natančno prilagajanje zahteva vsaj **64 GB sistemskega RAM-a**, od tega mora biti vsaj **32 GB na voljo GPU-ju** (teh 32 GB je del 64 GB, ne dodatek).
> - Lahko preizkusite tudi druge arhitekture modelov, vključno z **GPT-OSS-20B**, tako da model zamenjate v priloženih skriptih za učenje.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **Opomba:** Natančno prilagajanje z LoRA in QLoRA zahteva vsaj **32 GB sistemskega RAM-a**, od tega mora biti vsaj **16 GB na voljo GPU-ju** (teh 16 GB je del 32 GB, ne dodatek).
<!-- @os:end -->

<!-- @os:windows -->
> **Opomba:** Natančno prilagajanje z LoRA zahteva vsaj **32 GB sistemskega RAM-a**, od tega mora biti vsaj **16 GB na voljo GPU-ju** (teh 16 GB je del 32 GB, ne dodatek).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Opomba:** Natančno prilagajanje z LoRA in QLoRA zahteva grafično kartico z vsaj **16 GB namenskega pomnilnika GPU** in **32 GB sistemskega RAM-a**.
> - V sistemu Linux učenje poteka v celoti v namenskem pomnilniku VRAM grafične kartice.
> - Ne preklopi na deljen pomnilnik GPU (sistemski RAM), ko VRAM zmanjka.
> - Kartice z manj kot 16 GB namenskega pomnilnika VRAM bodo med učenjem v sistemu Linux zmanjkale pomnilnika, tudi če ima sistem veliko RAM-a.
<!-- @os:end -->

<!-- @os:windows -->
> **Opomba:** Natančno prilagajanje z LoRA zahteva vsaj **16 GB skupnega pomnilnika GPU** in **32 GB sistemskega RAM-a**.
> - V sistemu Windows skupni pomnilnik GPU združuje namenski VRAM grafične kartice z deljenim pomnilnikom GPU (izposojenim iz sistemskega RAM-a).
> - Zato lahko kartice z manj kot 16 GB namenskega pomnilnika VRAM še vedno izvedejo ta vodnik z uporabo deljenega pomnilnika GPU za nadomestitev razlike.
<!-- @os:end -->
<!-- @device:end -->

## Kaj se boste naučili

- Kako natančno prilagoditi LLM z uporabo LoRA, QLoRA in popolnega natančnega prilagajanja s PyTorch in ROCm
- Kako shraniti in uvesti svoj natančno prilagojen model
- Kako spremljati učenje in odpravljati pogoste težave

<!-- @device:halo_box,halo,stx,krk -->
## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme
> **Opomba**: Če VS Code ni nameščen, ga lahko namestite z Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Namestitev programskih predpogojev

<!-- @prereq:hf-models-gemma-3-4b-it,hf-datasets-databricks-dolly-15k -->
<!-- @os:linux -->
<!-- @prereq:hf-datasets-english-quotes -->
<!-- @os:end -->

#### Ustvarjanje virtualnega okolja

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
**Dodelite svojemu uporabniku dostop do naprav GPU** (za uveljavitev se odjavite in ponovno prijavite):

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

#### Namestitev osnovnih odvisnosti
<!-- @require:pytorch -->

#### Dodatne odvisnosti

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Tukaj so preizkušeni in podprti samo osnovni paketi. **bitsandbytes v sistemu Windows ni dobro podprt**, zato ga namestitev za Windows izpusti; v sistemu Windows uporabite LoRA ali popolno natančno prilagajanje (QLoRA zahteva bitsandbytes in je namenjen sistemu Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### Omogočanje avtentikacije HF (modeli z omejenim dostopom ali po meri / vnaprej nenameščeni modeli)

V tem primeru uporabljamo **google/gemma-3-4b-it**, ki je model z **omejenim dostopom**. Morate sprejeti pogoje modela na Hugging Face in se nato avtenticirati, da ga skripte za učenje lahko prenesejo.

1. **Sprejmite licenco:** Odprite [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), se prijavite (ali ustvarite račun) in sprejmite licenco/pogoje na strani modela (npr. »Agree and access repository«).
2. **Namestite in se prijavite:** Namestite Hugging Face CLI, nato zaženite standardno prijavo:

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

## Razumevanje tehnik

### Kaj je LoRA?

**LoRA (Low-Rank Adaptation)** ohrani osnovni model zamrznjen in uči samo majhne »adapterske« matrike, ki se dodajo določenim plastem. 

- **Ključna ideja**: namesto posodabljanja ogromne matrike uteži z milijoni parametrov se naučimo posodobitve nizkega ranga (dve majhni matriki, katerih produkt ima veliko manj parametrov). To prinese veliko zmanjšanje učljivih parametrov in VRAM-a, hkrati pa ohranja večino kakovosti popolnega natančnega prilagajanja.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### Kaj je QLoRA?

**QLoRA** združuje **4-bitno kvantizacijo** z **LoRA**. Osnovni model se naloži v 4-bitni obliki (velik prihranek pomnilnika), učijo pa se le adapterji LoRA v višji natančnosti. Tako dobite učinkovitost parametrov LoRA skupaj z veliko nižjo porabo VRAM-a, z majhnim kompromisom glede kakovosti v primerjavi s polno natančnim LoRA. Upoštevajte, da lahko 4-bitna kvantizacija povzroči numerične nestabilnosti (skoke izgube ali vrednosti NaN), zato uporabniki pogosto raje izberejo **LoRA**, če je na voljo dovolj VRAM-a.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Opomba**: Za osnovne modele MXFP4, kot je `openai/gpt-oss-20b`, priporočamo uporabo **LoRA** (`train_lora.py`) namesto QLoRA. Pot 4-bitnega `bitsandbytes` v skripti QLoRA običajno dekvantizira uteži MXFP4 v BF16, zato se zagon obnaša kot standardni LoRA. Za izvorni MXFP4 je potreben `bitsandbytes`, zgrajen iz izvorne kode, skupaj z ustreznim naborom Transformers/Triton/kernels. Glejte [dokumentacijo Transformers MXFP4](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. Izberite svojo metodo

| Metoda | Pomnilnik | Hitrost | Kakovost | Najprimernejša za |
|--------|--------|-------|---------|----------|
| **QLoRA** (samo Linux) | 12-16 GB | Najhitrejša | 90-95% | Nizko porabo pomnilnika |
| **LoRA** | 24-32 GB | Hitra | 95-98% | Uravnotežen pristop |
| **Full** | 80 GB+ | Najpočasnejša | 100% | Najvišjo kakovost |

### 3. Zaženite učenje

**Nabor podatkov in kaj se model nauči**  
Skripte spremenijo nabor podatkov v primere klepeta. Skripta QLoRA na primer uporablja **Abirate/english_quotes**: vsak primer postane par uporabnik–asistent, kot je:

- **Uporabnik:** »Give me a quote about: &lt;tag&gt;«
- **Asistent:** »&lt;quote&gt; – &lt;author&gt;«

Fino prilagajanje model nauči, da se odzove na pozive, ki zahtevajo citate na določeno temo, in jih vrne v obliki `<quote text> - <author>`. Skripti LoRA in popolnega finega prilagajanja uporabljata **databricks/databricks-dolly-15k** (splošni pari navodilo/odgovor), zato se natančna naloga razlikuje glede na skripto; ideja je enaka - prilagoditi model izbranemu naboru podatkov in obliki.

Spodaj je povzetek razpoložljivih metod učenja. Vsaka metoda je povezana s svojo skripto in vsebuje kratek opis za izbiro prave metode.

| Skripta                           | Metoda            | Opis                                                                                                         | Običajen VRAM | Priporočeno za                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Uči majhne prilagoditvene matrike, medtem ko osnovni model ostane zamrznjen. 3–5-krat hitreje; ~95–98 % polne kakovosti.                         | 24–32 GB      | Napredne uporabnike; več prilagoditev; več VRAM-a    |
| [`train_qlora.py`](assets/train_qlora.py)  *(samo Linux)*             | **QLoRA**       | 4-bitna kvantizacija + prilagoditve LoRA. Najnižja poraba pomnilnika, najhitreje, majhen kompromis pri kakovosti. Zahteva `bitsandbytes` (samo Linux).                            | 12–16 GB      | Večino uporabnikov; hitre poskuse; omejen VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Popolno fino prilagajanje** | Posodobi vse parametre modela. Najvišja kakovost; največja poraba pomnilnika in računske moči.                                    | 40 GB+        | Najvišjo kakovost; raziskave; veliko VRAM-a           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Opomba:** Popolno fino prilagajanje (`train_full_finetuning.py`) lahko zahteva več kot 64 GB sistemskega pomnilnika RAM in morda na tej napravi ni izvedljivo. Namesto tega razmislite o uporabi LoRA ali QLoRA.
<!-- @os:end -->

<!-- @os:windows -->
> **Opomba:** Popolno fino prilagajanje (`train_full_finetuning.py`) lahko zahteva več kot 64 GB sistemskega pomnilnika RAM in morda na tej napravi ni izvedljivo. Namesto tega razmislite o uporabi LoRA.
<!-- @os:end -->
<!-- @device:end -->

Preprosto izberite želeno `Training method`, prenesite ustrezno skripto in jo izvedite z ukazom, pri čemer naj bo vaše virtualno okolje aktivirano: 

```python
python3 train_<method_name>.py.
```

## Uporaba vašega fino prilagojenega modela

### Po popolnem finem prilagajanju

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

### Po učenju LoRA/QLoRA

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

### Združitev prilagoditve LoRA z osnovnim modelom

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Opomba:**  
- Prepričajte se, da se ime imenika modela (`output-gemma-3-4b-it-full`, `output-gpt-oss-20b-qlora`) ujema z dejansko izhodno mapo iz učenja.  
- Če ste namesto QLoRA uporabili LoRA, preprosto ustrezno zamenjajte pot.  
- Nekateri modeli Gemma zahtevajo navedbo `trust_remote_code=True` v `from_pretrained`; dodajte, če vidite povezano opozorilo.

Za več nastavitev po meri (žetoni za polnjenje, naprava itd.) glejte skripto, ki ste jo uporabili za učenje.

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

## Vodnik za prilagajanje po meri

### Uporaba lastnega nabora podatkov

Vse skripte uporabljajo enako obliko nabora podatkov. Zamenjajte razdelek za nalaganje:

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

**Oblika nabora podatkov za lokalno datoteko JSON/JSONL:**

Pri uporabi te metode zagotovite, da so vaše datoteke JSON pravilno strukturirane, da se izognete napakam pri razčlenjevanju. 

Upoštevati je treba naslednje smernice:
* **Oblikovanje datotek:** Datoteke JSON naj bodo oblikovane znotraj integriranega razvojnega okolja (IDE), da se zagotovi ustrezna struktura in skladnja.
* **Zahtevani ključi:** Datoteka JSON po meri mora vsebovati ključa `instruction` in `response`. Ta ključa sta nujna za pravilno delovanje metode.
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
**Oblika nabora podatkov za nabor podatkov iz Hugging Face Hub**

Pri uporabi naborov podatkov iz Hugging Face zagotovite, da so vaši nabori podatkov ustrezno strukturirani za nemoteno integracijo. 

Upoštevati je treba naslednje smernice:
* **Par navodilo-odgovor:** Osredotočite se na nabore podatkov, ki vsebujejo par `instruction-response`. Ta struktura je nujna za predvideno delovanje.
* **Prilagoditev ključev po meri:** Če vaš nabor podatkov ne ustreza strukturi `instruction-response`, lahko spremenite funkcijo `format_instruction()`. To vam omogoča prilagoditev določenim ključem po potrebi.

Primer prilagoditve: V primerih, ko je treba prilagoditi izhod nabora podatkov, lahko spremenite razdelek z odgovorom znotraj funkcije format_instruction(), da ustreza vašim zahtevam.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Oblika nabora podatkov za datoteko CSV**

Da bi skripta delovala z obliko datoteke CSV, morate zagotoviti, da datoteka CSV vsebuje stolpca z imenoma `instruction` in `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Prilagoditev parametrov učenja

Uredite skripto za učenje in spremenite spremenljivke, da ustrezajo vašim ciljem: **stopnja učenja** (`LR`), **epohe** (`EPOCHS`), **velikost serije** (`BATCH_SIZE`), **akumulacija gradientov** (`GRAD_ACCUM_STEPS`) in za LoRA/QLoRA **rang** (`LORA_R`). Za hitrejše zagone uporabite manj epoh in višjo stopnjo učenja (LR); za boljšo kakovost uporabite več epoh in nižjo LR. Zmanjšajte velikost serije ali dolžino zaporedja, če naletite na napake zaradi pomanjkanja pomnilnika.
### Nasveti za optimizacijo pomnilnika

Če naletite na napake zaradi pomanjkanja pomnilnika:

**1. Zmanjšajte velikost serije (batch size):**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Zmanjšajte dolžino zaporedja:**
```python
max_seq_length=256  # Instead of 512
```

**3. Uporabite bolj agresivno kvantizacijo:**
```
Full → LoRA → QLoRA
```

**4. Omogočite gradient checkpointing (samo pri polnem fino uglaševanju):**
```python
model.gradient_checkpointing_enable()
```

---

## Spremljanje in odpravljanje napak

### Spremljanje pomnilnika GPE

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Neobvezno) Sledenje eksperimentom z Weights & Biases

Za beleženje zagonov in meritev v [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

V skripti za učenje nastavite `report_to="wandb"` in po želji `run_name="your-experiment-name"` v konfiguraciji trainerja. Če ne želite uporabljati Wandb, pustite `report_to` na privzeti vrednosti ali ga nastavite na `"none"`.

### Pogoste težave

#### Pomanjkanje pomnilnika (OOM)

**Rešitev:** Zmanjšajte velikost serije in/ali uporabite QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### Izguba se ne zmanjšuje

**Rešitev:** Prilagodite stopnjo učenja
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Počasno učenje

**Rešitev:** Povečajte velikost serije, če pomnilnik to dopušča
```python
BATCH_SIZE = 8
```
## Naslednji koraki

Ko uspešno zaključite fino uglaševanje, razmislite o naslednjih korakih, da iz svojega modela izkoristite še več:

1. **Ovrednotite** temeljito na ločenih testnih podatkih, da izmerite posplošitev in se izognete prekomernemu prilagajanju.
2. **Eksperimentirajte** z različnimi vrednostmi hiperparametrov za boljše razmerje med natančnostjo, hitrostjo in porabo pomnilnika.
3. **Sledite** vsem svojim eksperimentom (in pripadajočim meritvam) z Weights & Biases za ponovljive raziskave.
4. **Preizkusite** učenje na lastnih podatkovnih naborih po meri, da model prilagodite svojemu primeru uporabe.
5. **Uvedite** svoj fino uglašeni model za hitro sklepanje z učinkovitimi zalednimi sistemi, kot je vLLM, na združljivi strojni opremi.
6. **Raziščite** napredne tehnike, vključno z oblikovanjem pozivov (prompt engineering), mešano natančnostjo in daljšimi dolžinami zaporedij.
7. **Naučite** več adapterjev LoRA za različne naloge ali domene in jih po potrebi zamenjujte.

---