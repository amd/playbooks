<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije proveravana od strane čoveka. Može sadržati greške, a određena uputstva, komande, preuzimanja, dostupnost proizvoda ili drugi sadržaj mogu se razlikovati u zavisnosti od jezika ili regiona. U slučaju bilo kakve nedoslednosti ili neslaganja, merodavna je originalna verzija playbook-a na engleskom jeziku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Pregled

Ovaj vodič pruža korak-po-korak primere za fino podešavanje velikog jezičkog modela (LLM) pomoću PyTorch i ROCm. Obuhvata nekoliko tehnika, od standardnog fino podešavanja do memorijski efikasnih Parameter-Efficient Fine-Tuning (PEFT) strategija, kako biste lako prilagodili modele svojim potrebama.

**Korišćeni model**: google/gemma-3-4b-it  *(pogledajte [Omogućavanje HF autentifikacije](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) ako je model zaključan)*  
**Hardver**: AMD Radeon™ GPU sa ROCm podrškom  
**Radni okvir**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Napomena:** 
> - Potpuno fino podešavanje zahteva najmanje **64 GB sistemske RAM memorije**, od čega najmanje **32 GB mora biti dostupno GPU-u** (tih 32 GB je deo tih 64 GB, a ne dodatnih 32 GB).
> - Možete takođe isprobati i druge arhitekture modela, uključujući **GPT-OSS-20B**, tako što ćete zameniti model u priloženim skriptama za obuku.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **Napomena:** LoRA i QLoRA fino podešavanje zahtevaju najmanje **32 GB sistemske RAM memorije**, od čega najmanje **16 GB mora biti dostupno GPU-u** (tih 16 GB je deo tih 32 GB, a ne dodatnih 16 GB).
<!-- @os:end -->

<!-- @os:windows -->
> **Napomena:** LoRA fino podešavanje zahteva najmanje **32 GB sistemske RAM memorije**, od čega najmanje **16 GB mora biti dostupno GPU-u** (tih 16 GB je deo tih 32 GB, a ne dodatnih 16 GB).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Napomena:** LoRA i QLoRA fino podešavanje zahtevaju grafičku karticu sa najmanje **16 GB namenske GPU memorije** i **32 GB sistemske RAM memorije**.
> - Na Linux-u, obuka se u potpunosti izvršava u namenskoj VRAM memoriji grafičke kartice.
> - Ne prelazi se na deljenu GPU memoriju (sistemsku RAM memoriju) kada ponestane VRAM-a.
> - Kartice sa manje od 16 GB namenske VRAM memorije ostaće bez memorije tokom obuke na Linux-u, čak i ako sistem ima dovoljno RAM memorije.
<!-- @os:end -->

<!-- @os:windows -->
> **Napomena:** LoRA fino podešavanje zahteva najmanje **16 GB ukupne GPU memorije** i **32 GB sistemske RAM memorije**.
> - Na Windows-u, ukupna GPU memorija kombinuje namensku VRAM memoriju grafičke kartice sa deljenom GPU memorijom (pozajmljenom iz sistemske RAM memorije).
> - Zbog toga, kartice sa manje od 16 GB namenske VRAM memorije i dalje mogu da pokrenu ovaj priručnik koristeći deljenu GPU memoriju za nadoknadu razlike.
<!-- @os:end -->
<!-- @device:end -->

## Šta ćete naučiti

- Kako da fino podesite LLM koristeći LoRA, QLoRA i potpuno fino podešavanje sa PyTorch i ROCm
- Kako da sačuvate i primenite svoj fino podešeni model
- Kako da pratite obuku i rešavate uobičajene probleme

<!-- @device:halo_box,halo,stx,krk -->
## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Provera ažuriranja softvera
> **Napomena**: Ako VS Code nije instaliran, možete ga instalirati putem Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instaliranje neophodnog softvera

#### Kreiranje virtuelnog okruženja

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
**Dodelite svom korisniku pristup GPU uređajima** (odjavite se i ponovo prijavite kako bi ovo stupilo na snagu):

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

#### Instaliranje osnovnih zavisnosti
<!-- @require:pytorch -->

#### Dodatne zavisnosti

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Ovde su testirani i podržani samo osnovni paketi. **bitsandbytes nije dobro podržan na Windows-u**, pa ga Windows instalacija izostavlja; koristite LoRA ili potpuno fino podešavanje na Windows-u (QLoRA zahteva bitsandbytes i namenjena je za Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### Omogućavanje HF autentifikacije (zaključani ili prilagođeni / unapred neinstalirani modeli)

U ovom primeru koristimo **google/gemma-3-4b-it**, koji je **zaključani (gated)** model. Morate prihvatiti uslove modela na Hugging Face, a zatim se autentifikovati kako bi skripte za obuku mogle da ga preuzmu.

1. **Prihvatite licencu:** Otvorite [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), prijavite se (ili napravite nalog) i prihvatite licencu/uslove na strani modela (npr. „Agree and access repository“).
2. **Instalirajte i prijavite se:** Instalirajte Hugging Face CLI, a zatim pokrenite standardnu prijavu:

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

## Razumevanje tehnika

### Šta je LoRA?

**LoRA (Low-Rank Adaptation)** zadržava bazni model zamrznutim i trenira samo male „adapter" matrice koje se dodaju određenim slojevima. 

- **Ključna ideja**: umesto ažuriranja ogromne matrice težina sa milionima parametara, učimo ažuriranje niskog ranga (dve male matrice čiji proizvod ima mnogo manje parametara). To daje veliko smanjenje broja parametara koji se treniraju i VRAM memorije, uz zadržavanje najvećeg dela kvaliteta potpunog fino podešavanja.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### Šta je QLoRA?

**QLoRA** kombinuje **4-bitnu kvantizaciju** sa **LoRA**. Bazni model se učitava u 4-bitnom formatu (velika ušteda memorije), a samo se LoRA adapteri treniraju u višoj preciznosti. Tako dobijate efikasnost parametara LoRA plus mnogo manju potrošnju VRAM memorije, uz mali kompromis u kvalitetu u odnosu na LoRA pune preciznosti. Imajte u vidu da 4-bitna kvantizacija može izazvati numeričku nestabilnost (skokove gubitka ili NaN vrednosti), pa korisnici često mogu preferirati **LoRA** ako je dostupno dovoljno VRAM memorije.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Napomena**: Za MXFP4 bazne modele poput `openai/gpt-oss-20b`, preporučujemo korišćenje **LoRA** (`train_lora.py`) umesto QLoRA. `bitsandbytes` 4-bitna putanja QLoRA skripte obično dekvantizuje MXFP4 težine u BF16, pa se izvršavanje ponaša kao standardni LoRA. Nativni MXFP4 zahteva `bitsandbytes` izgrađen iz izvornog koda plus odgovarajući Transformers/Triton/kernels sloj. Pogledajte [Transformers MXFP4 dokumentaciju](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. Izaberite metod

| Metod | Memorija | Brzina | Kvalitet | Najbolje za |
|--------|--------|-------|---------|----------|
| **QLoRA** (samo Linux) | 12-16GB | Najbrže | 90-95% | Malu upotrebu memorije |
| **LoRA** | 24-32GB | Brzo | 95-98% | Uravnotežen pristup |
| **Full** | 80GB+ | Najsporije | 100% | Maksimalan kvalitet |

### 3. Pokrenite obuku

**Skup podataka i šta model uči**  
Skripte pretvaraju skup podataka u primere razgovora. Na primer, QLoRA skripta koristi **Abirate/english_quotes**: svaki primer postaje par korisnik–asistent poput:

- **Korisnik:** „Daj mi citat o: &lt;tag&gt;"
- **Asistent:** „&lt;citat&gt; – &lt;autor&gt;"

Fino podešavanje uči model da odgovara na upite kojima se traže citati o nekoj temi i da ih vraća u formatu `<quote text> - <author>`. LoRA i skripte za potpuno fino podešavanje koriste **databricks/databricks-dolly-15k** (opšti parovi instrukcija/odgovor), tako da se tačan zadatak razlikuje u zavisnosti od skripte; ideja je ista - prilagoditi model odabranom skupu podataka i formatu.

Ispod se nalazi pregled dostupnih metoda obuke. Svaki metod je povezan sa svojom skriptom i sadrži kratak opis za odabir pravog pristupa.

| Skripta                           | Metod            | Opis                                                                                                         | Tipičan VRAM | Preporučeno za                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Obučava male matrice adaptera dok osnovni model ostaje zamrznut. 3–5 puta brže; ~95–98% punog kvaliteta.                         | 24–32GB      | Napredni korisnici; više adaptera; više VRAM-a    |
| [`train_qlora.py`](assets/train_qlora.py)  *(samo Linux)*             | **QLoRA**       | 4-bitna kvantizacija + LoRA adapteri. Najmanja upotreba memorije, najbrže, mali kompromis u kvalitetu. Zahteva `bitsandbytes` (samo Linux).                            | 12–16GB      | Većina korisnika; brzi eksperimenti; ograničen VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Potpuno fino podešavanje** | Ažurira sve parametre modela. Maksimalan kvalitet; najveća upotreba memorije i procesorske snage.                                    | 40GB+        | Maksimalan kvalitet; istraživanje; veliki VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Napomena:** Potpuno fino podešavanje (`train_full_finetuning.py`) može zahtevati više od 64GB sistemske RAM memorije i možda nije izvodljivo na ovom uređaju. Razmislite o korišćenju LoRA ili QLoRA umesto toga.
<!-- @os:end -->

<!-- @os:windows -->
> **Napomena:** Potpuno fino podešavanje (`train_full_finetuning.py`) može zahtevati više od 64GB sistemske RAM memorije i možda nije izvodljivo na ovom uređaju. Razmislite o korišćenju LoRA umesto toga.
<!-- @os:end -->
<!-- @device:end -->

Jednostavno izaberite željeni `Training method`, preuzmite odgovarajuću skriptu i izvršite je pomoću komande dok vaše virtuelno okruženje ostaje aktivirano: 

```python
python3 train_<method_name>.py.
```

## Korišćenje vašeg fino podešenog modela

### Nakon potpunog finog podešavanja

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

### Nakon LoRA/QLoRA obuke

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

### Spajanje LoRA adaptera u osnovni model

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Napomena:**  
- Uverite se da naziv direktorijuma modela (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) odgovara vašem stvarnom izlaznom folderu iz obuke.  
- Ako ste koristili LoRA umesto QLoRA, samo zamenite putanju u skladu s tim.  
- Neki Gemma modeli zahtevaju navođenje `trust_remote_code=True` u `from_pretrained`; dodajte ako vidite povezano upozorenje.

Za dodatna prilagođena podešavanja (tokeni za popunjavanje, uređaj, itd.), pogledajte skriptu koju ste koristili za obuku.

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

## Vodič za prilagođavanje

### Koristite sopstveni skup podataka

Sve skripte koriste isti format skupa podataka. Zamenite deo za učitavanje:

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

**Format skupa podataka za lokalnu JSON/JSONL datoteku:**

Kada koristite ovaj metod, uverite se da su vaše JSON datoteke ispravno strukturirane kako biste izbegli greške u obradi. 

Moraju se poštovati sledeće smernice:
* **Formatiranje datoteke:** JSON datoteke treba formatirati u integrisanom razvojnom okruženju (IDE) kako bi se obezbedila ispravna struktura i sintaksa.
* **Obavezni ključevi:** Prilagođena JSON datoteka mora sadržati ključeve `instruction` i `response`. Ovi ključevi su neophodni da bi metod ispravno funkcionisao.
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
**Format skupa podataka za Hugging Face Hub skup podataka**

Kada koristite skupove podataka sa Hugging Face, uverite se da su vaši skupovi podataka pravilno strukturirani kako bi se omogućila neometana integracija. 

Treba se pridržavati sledećih smernica:
* **Par instrukcija-odgovor:** Fokusirajte se na skupove podataka koji sadrže par `instruction-response`. Ova struktura je neophodna za nameravanu funkcionalnost.
* **Prilagođena izmena ključeva:** Ako vaš skup podataka ne odgovara strukturi `instruction-response`, imate mogućnost da izmenite funkciju `format_instruction()`. Ovo vam omogućava da prilagodite specifične ključeve po potrebi.

Primer prilagođavanja: U slučajevima kada je potrebno prilagoditi izlaz skupa podataka, možete izmeniti deo odgovora unutar funkcije format_instruction() kako bi odgovarao vašim zahtevima.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Format skupa podataka za CSV datoteku**

Da bi skripta mogla da koristi format CSV datoteke, morate obezbediti da CSV datoteka sadrži kolone pod nazivom `instruction` i `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Prilagodite parametre obuke

Uredite skriptu za obuku i promenite promenljive kako bi odgovarale vašim ciljevima: **stopa učenja** (`LR`), **epohe** (`EPOCHS`), **veličina serije** (`BATCH_SIZE`), **akumulacija gradijenta** (`GRAD_ACCUM_STEPS`), i za LoRA/QLoRA **rang** (`LORA_R`). Za brže pokretanje koristite manje epoha i veću stopu učenja (LR); za bolji kvalitet koristite više epoha i manju LR. Smanjite veličinu serije ili dužinu sekvence ako naiđete na greške zbog nedostatka memorije.
### Saveti za optimizaciju memorije

Ako naiđete na greške zbog nedovoljne memorije:

**1. Smanjite veličinu batch-a:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Smanjite dužinu sekvence:**
```python
max_seq_length=256  # Instead of 512
```

**3. Koristite agresivniju kvantizaciju:**
```
Full → LoRA → QLoRA
```

**4. Omogućite Gradient Checkpointing (samo za potpuno fino podešavanje):**
```python
model.gradient_checkpointing_enable()
```

---

## Praćenje i otklanjanje grešaka

### Praćenje GPU memorije

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Opciono) Praćenje eksperimenata pomoću Weights & Biases

Da biste beležili pokretanja i metrike na [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

U skripti za obuku, postavite `report_to="wandb"` i po želji `run_name="your-experiment-name"` u konfiguraciji trenera. Ako ne želite da koristite Wandb, ostavite `report_to` na podrazumevanoj vrednosti ili je postavite na `"none"`.

### Uobičajeni problemi

#### Nedovoljno memorije (OOM)

**Rešenje:** Smanjite veličinu batch-a i/ili koristite QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### Gubitak se ne smanjuje

**Rešenje:** Podesite stopu učenja
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Spora obuka

**Rešenje:** Povećajte veličinu batch-a ako memorija to dozvoljava
```python
BATCH_SIZE = 8
```
## Sledeći koraci

Nakon što uspešno završite fino podešavanje, razmotrite sledeće korake kako biste izvukli još više iz svog modela:

1. **Ocenite** temeljno na test podacima koji nisu korišćeni u obuci kako biste izmerili generalizaciju i izbegli preprilagođavanje (overfitting).
2. **Eksperimentišite** isprobavanjem različitih vrednosti hiperparametara radi boljeg odnosa tačnosti, brzine i memorije.
3. **Pratite** sve svoje eksperimente (i odgovarajuće metrike) pomoću Weights & Biases radi reproduktivnog istraživanja.
4. **Isprobajte** obuku na sopstvenim prilagođenim skupovima podataka kako biste prilagodili model specifično za svoj slučaj upotrebe.
5. **Primenite** svoj fino podešeni model za brzo zaključivanje koristeći efikasne backend-e kao što je vLLM na kompatibilnom hardveru.
6. **Istražite** napredne tehnike uključujući prompt inženjering, mešovitu preciznost i duže dužine sekvenci.
7. **Obučite** više LoRA adaptera za različite zadatke ili domene i menjajte ih po potrebi.

---