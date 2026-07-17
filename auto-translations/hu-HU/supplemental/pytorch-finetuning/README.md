<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Áttekintés

Ez az oktatóanyag lépésről lépésre bemutatja, hogyan lehet egy nagy nyelvi modellt (LLM) finomhangolni PyTorch és ROCm segítségével. Számos technikát ismertet, a standard finomhangolástól a memóriahatékony Parameter-Efficient Fine-Tuning (PEFT) stratégiákig, hogy könnyen testre szabhassa a modelleket az igényeinek megfelelően.

**Használt modell**: google/gemma-3-4b-it  *(lásd: [HF hitelesítés engedélyezése](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models), ha a modell hozzáférés-korlátozott)*  
**Hardver**: AMD Radeon™ GPU ROCm támogatással  
**Keretrendszer**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Megjegyzés:** Más modellarchitektúrákat is kipróbálhat, beleértve a **GPT-OSS-20B**-t is, ha a megadott tanítószkriptekben lecseréli a modellt.
> A teljes finomhangoláshoz legalább 32 GB GPU-memória és 64 GB rendszermemória szükséges.
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> **Megjegyzés:** A LoRA és QLoRA finomhangoláshoz legalább 16 GB GPU-memória és 32 GB rendszermemória szükséges.
<!-- @device:end -->

## Mit fog megtanulni

- Hogyan lehet LLM-et finomhangolni LoRA, QLoRA és teljes finomhangolás segítségével PyTorch és ROCm használatával
- Hogyan lehet menteni és telepíteni a finomhangolt modellt
- Hogyan lehet figyelemmel kísérni a tanítást és elhárítani a gyakori problémákat

## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése
> **Megjegyzés**: Ha a VS Code nincs telepítve, az AMD Ryzen AI Developer Center segítségével telepítheti.

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftver-előfeltételek telepítése

#### Virtuális környezet létrehozása

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
**Adjon hozzáférést a felhasználójának a GPU-eszközökhöz** (a módosítás érvénybe lépéséhez jelentkezzen ki, majd be újra):

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

#### Alapvető függőségek telepítése
<!-- @require:pytorch -->

#### További függőségek

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Csak az alapvető csomagok teszteltek és támogatottak itt. **A bitsandbytes nem jól támogatott Windows rendszeren**, ezért a Windows-os telepítés kihagyja; Windows rendszeren használjon LoRA-t vagy teljes finomhangolást (a QLoRA bitsandbytes-t igényel, és Linux rendszerre készült).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### HF hitelesítés engedélyezése (hozzáférés-korlátozott vagy egyéni / előre nem telepített modellek)

Ebben a példában a **google/gemma-3-4b-it** modellt használjuk, amely egy **hozzáférés-korlátozott** modell. El kell fogadnia a modell feltételeit a Hugging Face oldalon, majd hitelesítenie kell magát, hogy a tanítószkriptek le tudják tölteni.

1. **Fogadja el a licencet:** Nyissa meg a [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it) oldalt, jelentkezzen be (vagy hozzon létre fiókot), és fogadja el a licencet/feltételeket a modell oldalán (pl. „Agree and access repository").
2. **Telepítés és bejelentkezés:** Telepítse a Hugging Face CLI-t, majd futtassa a szokásos bejelentkezési parancsot:

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

## A technikák megértése

### Mi az a LoRA?

**A LoRA (Low-Rank Adaptation)** befagyasztja az alapmodellt, és csak kis „adapter" mátrixokat tanít, amelyeket bizonyos rétegekhez adnak hozzá.

- **Az alapötlet**: ahelyett, hogy egy hatalmas súlymátrixot frissítenénk millió paraméterrel, egy alacsony rangú frissítést tanulunk meg (két kis mátrix, amelyek szorzatának jóval kevesebb paramétere van). Ez nagy mértékben csökkenti a tanítható paraméterek számát és a VRAM-igényt, miközben megőrzi a teljes finomhangolás minőségének nagy részét.

```python
# Instead of updating full weight matrix W (16M params):
W_updated = W + ΔW

# LoRA decomposes the update into two small matrices:
W_updated = W + B × A
# B: 4096×32 matrix
# A: 32×4096 matrix
# Total: 262K params (98% reduction!)
```

### Mi az a QLoRA?

**A QLoRA** a **4 bites kvantálást** kombinálja a **LoRA**-val. Az alapmodell 4 biten töltődik be (nagy memóriamegtakarítás), és csak a LoRA adapterek tanítódnak magasabb pontossággal. Így megkapja a LoRA paraméterhatékonyságát és a jóval alacsonyabb VRAM-igényt, egy kis minőségi kompromisszum árán a teljes pontosságú LoRA-hoz képest. Vegye figyelembe, hogy a 4 bites kvantálás numerikus instabilitásokat okozhat (veszteségcsúcsok vagy NaN értékek), ezért a felhasználók gyakran inkább a **LoRA**-t részesítik előnyben, ha elegendő VRAM áll rendelkezésre.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Megjegyzés**: Az MXFP4 alapmodellek esetén, mint például az `openai/gpt-oss-20b`, a **LoRA** (`train_lora.py`) használatát javasoljuk a QLoRA helyett. A QLoRA szkript `bitsandbytes` 4 bites útvonala általában BF16-ra kvantálásmentesíti az MXFP4 súlyokat, így a futtatás standard LoRA-ként viselkedik. A natív MXFP4 forrásból épített `bitsandbytes`-t igényel, valamint egy megfelelő Transformers/Triton/kernels vermet. Lásd a [Transformers MXFP4 dokumentációját](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---

### 2. Válassza ki a módszert

| Módszer | Memória | Sebesség | Minőség | Legjobb alkalmazás |
|--------|--------|-------|---------|----------|
| **QLoRA** (csak Linux) | 12-16 GB | Leggyorsabb | 90-95% | Alacsony memóriahasználat |
| **LoRA** | 24-32 GB | Gyors | 95-98% | Kiegyensúlyozott megközelítés |
| **Teljes** | 80 GB+ | Leglassabb | 100% | Maximális minőség |

### 3. Tanítás futtatása

**Adatkészlet és amit a modell megtanul**  
A szkriptek az adatkészletet csevegési példákká alakítják. Például a QLoRA szkript az **Abirate/english_quotes** adatkészletet használja: minden példa egy felhasználó–asszisztens párként jelenik meg:

- **Felhasználó:** „Adj egy idézetet erről: &lt;tag&gt;"
- **Asszisztens:** „&lt;quote&gt; – &lt;author&gt;"

A finomhangolás megtanítja a modellt, hogy válaszoljon egy témáról szóló idézeteket kérő promptokra, és azokat `<idézet szövege> - <szerző>` formátumban adja vissza. A LoRA és a teljes finomhangolási szkriptek a **databricks/databricks-dolly-15k** adatkészletet használják (általános utasítás/válasz párok), így a pontos feladat szkriptenként változik; az alapötlet ugyanaz – igazítsa a modellt a kiválasztott adatkészlethez és formátumhoz.

Az alábbiakban összefoglaljuk az elérhető tanítási módszereket. Minden módszer hivatkozik a szkriptjére, és rövid leírást tartalmaz a megfelelő megközelítés kiválasztásához.

| Szkript | Módszer | Leírás | Tipikus VRAM | Ajánlott |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py) | **LoRA** | Kis adaptermátrixokat tanít az alapmodell befagyasztása mellett. 3–5-ször gyorsabb; ~95–98%-os teljes minőség. | 24–32 GB | Haladó felhasználók; több adapter; több VRAM |
| [`train_qlora.py`](assets/train_qlora.py)  *(csak Linux)* | **QLoRA** | 4 bites kvantálás + LoRA adapterek. Legalacsonyabb memóriahasználat, leggyorsabb, kis minőségi kompromisszum. `bitsandbytes` szükséges (csak Linux). | 12–16 GB | Legtöbb felhasználó; gyors kísérletek; korlátozott VRAM |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Teljes finomhangolás** | Az összes modellparamétert frissíti. Maximális minőség; legmagasabb memória- és számítási igény. | 40 GB+ | Maximális minőség; kutatás; nagy VRAM |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Megjegyzés:** A teljes finomhangolás (`train_full_finetuning.py`) több mint 64 GB rendszermemóriát igényelhet, és előfordulhat, hogy nem kivitelezhető ezen az eszközön. Fontolja meg a LoRA vagy QLoRA használatát helyette.
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés:** A teljes finomhangolás (`train_full_finetuning.py`) több mint 64 GB rendszermemóriát igényelhet, és előfordulhat, hogy nem kivitelezhető ezen az eszközön. Fontolja meg a LoRA használatát helyette.
<!-- @os:end -->
<!-- @device:end -->

Egyszerűen válassza ki a kívánt `Tanítási módszert`, töltse le a megfelelő szkriptet, és futtassa az alábbi paranccsal, miközben a virtuális környezet aktív marad:

```python
python3 train_<method_name>.py.
```

## A finomhangolt modell használata

### Teljes finomhangolás után

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

### LoRA/QLoRA tanítás után

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

### LoRA adapter egyesítése az alapmodellel

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Megjegyzés:**  
- Győződjön meg arról, hogy a modellkönyvtár neve (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) megegyezik a tanítás tényleges kimeneti mappájával.  
- Ha LoRA-t használt QLoRA helyett, egyszerűen cserélje le az elérési utat ennek megfelelően.  
- Egyes Gemma modellek esetén szükség lehet a `trust_remote_code=True` megadására a `from_pretrained` hívásban; adja hozzá, ha ezzel kapcsolatos figyelmeztetést lát.

Az egyéni beállításokról (kitöltési tokenek, eszköz stb.) tekintse meg a tanításhoz használt szkriptet.

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

## Testreszabási útmutató

### Saját adatkészlet használata

Minden szkript ugyanazt az adatkészlet-formátumot használja. Cserélje le a betöltési részt:

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

**Adatkészlet-formátum helyi JSON/JSONL fájlhoz:**

Ennek a módszernek a használatakor győződjön meg arról, hogy a JSON-fájlok helyesen vannak strukturálva az elemzési hibák elkerülése érdekében.

A következő irányelveket kell betartani:
* **Fájlformázás:** A JSON-fájlokat integrált fejlesztői környezetben (IDE) kell formázni a megfelelő struktúra és szintaxis biztosítása érdekében.
* **Kötelező kulcsok:** Az egyéni JSON-fájlnak tartalmaznia kell az `instruction` és `response` kulcsokat. Ezek a kulcsok elengedhetetlenek a módszer helyes működéséhez.
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
**Adatkészlet-formátum Hugging Face Hub adatkészlethez**

A Hugging Face adatkészleteinek használatakor győződjön meg arról, hogy az adatkészletek helyesen vannak strukturálva a zökkenőmentes integráció érdekében.

A következő irányelveket kell követni:
* **Utasítás-válasz pár:** Összpontosítson az `instruction-response` párt tartalmazó adatkészletekre. Ez a struktúra elengedhetetlen a tervezett funkcionalitáshoz.
* **Egyéni kulcsmódosítás:** Ha az adatkészlet nem felel meg az `instruction-response` struktúrának, lehetősége van a `format_instruction()` függvény módosítására. Ez lehetővé teszi az adott kulcsok szükség szerinti kezelését.

Példa módosításra: Azokban az esetekben, amikor az adatkészlet kimenetét módosítani kell, a `format_instruction()` függvényen belül módosíthatja a válasz részt az igényeinek megfelelően.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Adatkészlet-formátum CSV-fájlhoz**

A szkript CSV-fájl formátummal való használatához győződjön meg arról, hogy a CSV-fájl tartalmaz `instruction` és `response` nevű oszlopokat.
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Tanítási paraméterek módosítása

Szerkessze a tanítószkriptet, és módosítsa a változókat a céljainak megfelelően: **tanulási ráta** (`LR`), **epochák** (`EPOCHS`), **kötegméret** (`BATCH_SIZE`), **gradiens akkumuláció** (`GRAD_ACCUM_STEPS`), és LoRA/QLoRA esetén **rang** (`LORA_R`). A gyorsabb futtatáshoz használjon kevesebb epochát és magasabb tanulási rátát (LR); a jobb minőséghez használjon több epochát és alacsonyabb LR-t. Csökkentse a kötegméretet vagy a szekvenciahosszt, ha memóriahiány-hibákba ütközik.

### Memóriaoptimalizálási tippek

Ha memóriahiány-hibákba ütközik:

**1. Kötegméret csökkentése:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Szekvenciahossz csökkentése:**
```python
max_seq_length=256  # Instead of 512
```

**3. Agresszívabb kvantálás használata:**
```
Full → LoRA → QLoRA
```

**4. Gradiens ellenőrzőpont engedélyezése (csak teljes finomhangoláshoz):**
```python
model.gradient_checkpointing_enable()
```

---

## Figyelés és hibakeresés

### GPU-memória figyelése

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Opcionális) Kísérletek nyomon követése a Weights & Biases segítségével

A futtatások és metrikák naplózásához a [Weights & Biases](https://wandb.ai) szolgáltatásba:

```bash
pip install wandb
wandb login
```

A tanítószkriptben állítsa be a `report_to="wandb"` értéket, és opcionálisan a `run_name="your-experiment-name"` értéket a trainer konfigurációban. Ha nem szeretné használni a Wandb-t, hagyja a `report_to` értékét az alapértelmezetten, vagy állítsa `"none"`-ra.

### Gyakori problémák

#### Memóriahiány (OOM)

**Megoldás:** Csökkentse a kötegméretet és/vagy használjon QLoRA-t
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### A veszteség nem csökken

**Megoldás:** Módosítsa a tanulási rátát
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Lassú tanítás

**Megoldás:** Növelje a kötegméretet, ha a memória engedi
```python
BATCH_SIZE = 8
```
## Következő lépések

A sikeres finomhangolás elvégzése után fontolja meg a következő lépéseket, hogy még többet hozzon ki a modelljéből:

1. **Értékelje** alaposan a visszatartott tesztadatokon az általánosítás mérése és a túlillesztés elkerülése érdekében.
2. **Kísérletezzen** különböző hiperparaméter-értékekkel a jobb pontosság, sebesség és memória-kompromisszumok érdekében.
3. **Kövesse nyomon** az összes kísérletét (és a megfelelő metrikákat) a Weights & Biases segítségével a reprodukálható kutatás érdekében.
4. **Próbálja ki** a saját egyéni adatkészleteken való tanítást, hogy a modellt kifejezetten az Ön felhasználási esetéhez igazítsa.
5. **Telepítse** a finomhangolt modellt gyors következtetéshez hatékony háttérrendszerek, például vLLM segítségével kompatibilis hardveren.
6. **Fedezze fel** a fejlett technikákat, beleértve a prompt engineeringet, a vegyes pontosságot és a hosszabb szekvenciahosszakat.
7. **Tanítson** több LoRA adaptert különböző feladatokhoz vagy területekhez, és szükség szerint cserélje fel őket.

---