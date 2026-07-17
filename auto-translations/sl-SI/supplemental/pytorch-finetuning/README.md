<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Pregled

Ta vadnica ponuja postopne primere za fino nastavitev velikega jezikovnega modela (LLM) s PyTorch in ROCm. Pokriva več tehnik, od standardne fine nastavitve do pomnilniško učinkovitih strategij Parameter-Efficient Fine-Tuning (PEFT), tako da lahko modele enostavno prilagodite svojim potrebam.

**Uporabljen model**: google/gemma-3-4b-it  *(glejte [Omogočanje HF avtentikacije](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models), če je model zaščiten)*  
**Strojna oprema**: AMD Radeon™ GPU s podporo za ROCm  
**Ogrodje**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Opomba:** Preizkusite lahko tudi druge arhitekture modelov, vključno z **GPT-OSS-20B**, tako da v priloženih skriptah za usposabljanje zamenjate model.
> Popolna fina nastavitev zahteva vsaj 32 GB pomnilnika GPU in 64 GB sistemskega RAM-a.
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> **Opomba:** Fina nastavitev z LoRA in QLoRA zahteva vsaj 16 GB pomnilnika GPU in 32 GB sistemskega RAM-a.
<!-- @device:end -->

## Kaj se boste naučili

- Kako fino nastaviti LLM z uporabo LoRA, QLoRA in popolne fine nastavitve s PyTorch in ROCm
- Kako shraniti in namestiti vaš fino nastavljen model
- Kako spremljati usposabljanje in odpravljati pogoste težave

## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme
> **Opomba**: Če VS Code ni nameščen, ga lahko namestite z AMD Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Namestitev predpogojev programske opreme

#### Ustvarjanje virtualnega okolja

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
**Dodelite svojemu uporabniku dostop do naprav GPU** (za uveljavitev se odjavite in znova prijavite):

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

#### Namestitev osnovnih odvisnosti
<!-- @require:pytorch -->

#### Dodatne odvisnosti

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Tukaj so testirani in podprti samo osnovni paketi. **bitsandbytes ni dobro podprt v sistemu Windows**, zato ga namestitev za Windows izpušča; na sistemu Windows uporabite LoRA ali popolno fino nastavitev (QLoRA zahteva bitsandbytes in je namenjen za Linux).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### Omogočanje HF avtentikacije (zaščiteni ali po meri / vnaprej nenaloženi modeli)

V tem primeru uporabljamo **google/gemma-3-4b-it**, ki je **zaščiten** model. Sprejeti morate pogoje modela na Hugging Face in se nato avtenticirati, da bodo skripte za usposabljanje lahko prenesle model.

1. **Sprejmite licenco:** Odprite [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it), se prijavite (ali ustvarite račun) in sprejmite licenco/pogoje na strani modela (npr. »Strinjam se in dostopam do repozitorija«).
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

**LoRA (Low-Rank Adaptation)** ohrani osnovni model zamrznjen in usposablja le majhne »adapterske« matrike, ki se dodajo določenim plastem.

- **Ključna ideja**: namesto posodabljanja ogromne matrike uteži z milijoni parametrov se naučimo posodobitve nizkega ranga (dve majhni matriki, katerih produkt ima bistveno manj parametrov). To zagotavlja veliko zmanjšanje parametrov, ki jih je mogoče usposabljati, in VRAM, hkrati pa ohranja večino kakovosti popolne fine nastavitve.

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

**QLoRA** združuje **4-bitno kvantizacijo** z **LoRA**. Osnovni model se naloži v 4-bitnem formatu (velika prihranek pomnilnika), LoRA adapterji pa se usposabljajo v višji natančnosti. Tako dobite parametrično učinkovitost LoRA in bistveno nižji VRAM, z majhnim kompromisem kakovosti v primerjavi s LoRA v polni natančnosti. Upoštevajte, da lahko 4-bitna kvantizacija povzroči numerične nestabilnosti (skoki izgube ali NaN-i), zato uporabniki pogosto raje izberejo **LoRA**, če je na voljo dovolj VRAM-a.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Opomba**: Za osnovne modele MXFP4, kot je `openai/gpt-oss-20b`, priporočamo uporabo **LoRA** (`train_lora.py`) namesto QLoRA. Pot `bitsandbytes` 4-bit v skripti QLoRA navadno dekvanticira uteži MXFP4 v BF16, zato se zagon obnaša kot standardni LoRA. Nativni MXFP4 zahteva `bitsandbytes`, zgrajen iz izvorne kode, ter ujemajoč se sklad Transformers/Triton/jedra. Glejte [dokumentacijo Transformers MXFP4](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---

### 2. Izberite svojo metodo

| Metoda | Pomnilnik | Hitrost | Kakovost | Najboljše za |
|--------|-----------|---------|----------|--------------|
| **QLoRA** (samo Linux) | 12–16 GB | Najhitrejše | 90–95 % | Nizka poraba pomnilnika |
| **LoRA** | 24–32 GB | Hitro | 95–98 % | Uravnotežen pristop |
| **Popolna** | 80 GB+ | Najpočasnejše | 100 % | Največja kakovost |

### 3. Zaženite usposabljanje

**Nabor podatkov in kaj se model nauči**  
Skripte pretvorijo nabor podatkov v primere pogovorov. Na primer, skripta QLoRA uporablja **Abirate/english_quotes**: vsak primer postane par uporabnik–asistent, kot je:

- **Uporabnik:** »Daj mi citat o: &lt;oznaka&gt;«
- **Asistent:** »&lt;citat&gt; – &lt;avtor&gt;«

Fina nastavitev nauči model, da se odziva na pozive, ki zahtevajo citate o določeni temi, in jih vrne v obliki `<besedilo citata> - <avtor>`. Skripte za LoRA in popolno fino nastavitev uporabljajo **databricks/databricks-dolly-15k** (splošni pari navodil/odgovorov), zato se natančna naloga razlikuje glede na skripto; ideja je enaka – prilagodite model izbranemu naboru podatkov in obliki.

Spodaj je povzetek razpoložljivih metod usposabljanja. Vsaka metoda je povezana s svojo skripto in vsebuje kratek opis za izbiro pravega pristopa.

| Skripta                           | Metoda            | Opis                                                                                                         | Tipičen VRAM | Priporočeno za                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Usposablja majhne adapterske matrike ob zamrznitvi osnovnega modela. 3–5-krat hitrejše; ~95–98 % polne kakovosti.                         | 24–32 GB      | Napredni uporabniki; več adapterjev; več VRAM-a    |
| [`train_qlora.py`](assets/train_qlora.py)  *(samo Linux)*             | **QLoRA**       | 4-bitna kvantizacija + LoRA adapterji. Najnižja poraba pomnilnika, najhitrejše, majhen kompromis kakovosti. Zahteva `bitsandbytes` (samo Linux).                            | 12–16 GB      | Večina uporabnikov; hitri eksperimenti; omejen VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Popolna fina nastavitev** | Posodablja vse parametre modela. Največja kakovost; najvišja poraba pomnilnika in računalniških virov.                                    | 40 GB+        | Največja kakovost; raziskave; velik VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Opomba:** Popolna fina nastavitev (`train_full_finetuning.py`) lahko zahteva več kot 64 GB sistemskega RAM-a in morda ni izvedljiva na tej napravi. Razmislite o uporabi LoRA ali QLoRA.
<!-- @os:end -->

<!-- @os:windows -->
> **Opomba:** Popolna fina nastavitev (`train_full_finetuning.py`) lahko zahteva več kot 64 GB sistemskega RAM-a in morda ni izvedljiva na tej napravi. Razmislite o uporabi LoRA.
<!-- @os:end -->
<!-- @device:end -->

Preprosto izberite želeno `metodo usposabljanja`, prenesite ustrezno skripto in jo zaženite z ukazom ob aktiviranem virtualnem okolju:

```python
python3 train_<method_name>.py.
```

## Uporaba vašega fino nastavljenega modela

### Po popolni fini nastavitvi

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

### Po usposabljanju z LoRA/QLoRA

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

### Združitev LoRA adapterja z osnovnim modelom

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Opomba:**  
- Prepričajte se, da se ime imenika modela (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) ujema z dejansko izhodno mapo iz usposabljanja.  
- Če ste namesto QLoRA uporabili LoRA, preprosto ustrezno zamenjajte pot.  
- Nekateri modeli Gemma zahtevajo navedbo `trust_remote_code=True` v `from_pretrained`; dodajte, če vidite povezano opozorilo.

Za bolj prilagojene nastavitve (žetoni za oblazinjenje, naprava itd.) si oglejte skripto, ki ste jo uporabili za usposabljanje.

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

## Vodnik za prilagajanje

### Uporabite lasten nabor podatkov

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
* **Oblikovanje datoteke:** Datoteke JSON je treba oblikovati v integriranem razvojnem okolju (IDE), da se zagotovi pravilna struktura in sintaksa.
* **Zahtevani ključi:** Datoteka JSON po meri mora vsebovati ključa `instruction` in `response`. Ti ključi so bistvenega pomena za pravilno delovanje metode.
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

Pri uporabi naborov podatkov iz Hugging Face zagotovite, da so vaši nabori podatkov pravilno strukturirani za nemoteno integracijo.

Upoštevati je treba naslednje smernice:
* **Par navodilo-odgovor:** Osredotočite se na nabore podatkov, ki vključujejo par `instruction-response`. Ta struktura je bistvena za predvideno funkcionalnost.
* **Prilagoditev ključev po meri:** Če vaš nabor podatkov ne ustreza strukturi `instruction-response`, imate možnost spremeniti funkcijo `format_instruction()`. To vam omogoča, da po potrebi prilagodite določene ključe.

Primer prilagoditve: V primerih, ko je treba prilagoditi izhod nabora podatkov, lahko spremenite razdelek odgovora znotraj funkcije format_instruction(), da ustreza vašim zahtevam.
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

Da bi skripta delovala z obliko datoteke CSV, morate zagotoviti, da datoteka CSV vsebuje stolpce z imeni `instruction` in `response`. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Prilagoditev parametrov usposabljanja

Uredite skripto za usposabljanje in spremenite spremenljivke glede na svoje cilje: **hitrost učenja** (`LR`), **epohe** (`EPOCHS`), **velikost serije** (`BATCH_SIZE`), **akumulacija gradientov** (`GRAD_ACCUM_STEPS`) in za LoRA/QLoRA **rang** (`LORA_R`). Za hitrejše zagone uporabite manj epoh in višjo hitrost učenja (LR); za boljšo kakovost uporabite več epoh in nižjo LR. Zmanjšajte velikost serije ali dolžino zaporedja, če naletite na napake pomanjkanja pomnilnika.

### Nasveti za optimizacijo pomnilnika

Če naletite na napake pomanjkanja pomnilnika:

**1. Zmanjšajte velikost serije:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Zmanjšajte dolžino zaporedja:**
```python
max_seq_length=256  # Instead of 512
```

**3. Uporabite agresivnejšo kvantizacijo:**
```
Full → LoRA → QLoRA
```

**4. Omogočite preverjanje gradientov (samo za popolno fino nastavitev):**
```python
model.gradient_checkpointing_enable()
```

---

## Spremljanje in odpravljanje napak

### Opazovanje pomnilnika GPU

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Neobvezno) Sledenje eksperimentom z Weights & Biases

Za beleženje zagonov in metrik v [Weights & Biases](https://wandb.ai):

```bash
pip install wandb
wandb login
```

V skripti za usposabljanje nastavite `report_to="wandb"` in po želji `run_name="your-experiment-name"` v konfiguraciji trenerja. Če ne želite uporabljati Wandb, pustite `report_to` pri privzeti vrednosti ali ga nastavite na `"none"`.

### Pogoste težave

#### Pomanjkanje pomnilnika (OOM)

**Rešitev:** Zmanjšajte velikost serije in/ali uporabite QLoRA
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### Izguba se ne zmanjšuje

**Rešitev:** Prilagodite hitrost učenja
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Počasno usposabljanje

**Rešitev:** Povečajte velikost serije, če pomnilnik to dopušča
```python
BATCH_SIZE = 8
```
## Naslednji koraki

Ko uspešno zaključite fino nastavitev, razmislite o naslednjih korakih za boljšo izkoriščenost modela:

1. **Ocenite** temeljito na ločenih testnih podatkih, da izmerite posplošitev in se izognete pretiranemu prilagajanju.
2. **Eksperimentirajte** s preizkušanjem različnih vrednosti hiperparametrov za boljšo natančnost, hitrost in kompromise pomnilnika.
3. **Sledite** vsem svojim eksperimentom (in ustreznim metrikam) z Weights & Biases za ponovljive raziskave.
4. **Preizkusite** usposabljanje na lastnih naborih podatkov po meri, da model prilagodite posebej za vaš primer uporabe.
5. **Namestite** vaš fino nastavljen model za hitro sklepanje z učinkovitimi zaledji, kot je vLLM na združljivi strojni opremi.
6. **Raziščite** napredne tehnike, vključno z oblikovanjem pozivov, mešano natančnostjo in daljšimi dolžinami zaporedij.
7. **Usposobite** več LoRA adapterjev za različne naloge ali domene in jih po potrebi zamenjajte.

---