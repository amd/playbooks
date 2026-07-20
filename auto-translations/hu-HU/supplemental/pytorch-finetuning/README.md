<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ez a playbook olyan speciális címkéket használ, amelyeket a GitHub nem tud megjeleníteni. A tartalom megfelelő megtekintéséhez kérjük, látogasson el a [amd.com/playbooks](https://amd.com/playbooks) oldalra.
<!-- @github-only:end -->

## Áttekintés

Ez az útmutató lépésről lépésre bemutatja, hogyan lehet egy nagy nyelvi modellt (LLM) finomhangolni PyTorch és ROCm segítségével. Számos technikát ismertet, a hagyományos finomhangolástól kezdve a memóriahatékony Parameter-Efficient Fine-Tuning (PEFT) stratégiákig, hogy könnyedén testre szabhassa a modelleket saját igényei szerint.

**Használt modell**: google/gemma-3-4b-it  *(lásd az [Enable HF authentication](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models) szakaszt, ha zárolt)*  
**Hardver**: AMD Radeon™ GPU ROCm támogatással  
**Keretrendszer**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Megjegyzés:** Más modellarchitektúrákat is kipróbálhat, beleértve a **GPT-OSS-20B**-t is, ha a megadott betanítási szkriptekben lecseréli a modellt.
> A teljes finomhangoláshoz legalább 32 GB GPU memória és 64 GB rendszer RAM szükséges.
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> **Megjegyzés:** A LoRA és QLoRA finomhangoláshoz legalább 16 GB GPU memória és 32 GB rendszer RAM szükséges.
<!-- @device:end -->

## Mit fog megtanulni

- Hogyan finomhangoljon egy LLM-et LoRA, QLoRA és teljes finomhangolás segítségével PyTorch és ROCm használatával
- Hogyan mentse el és telepítse a finomhangolt modelljét
- Hogyan kövesse nyomon a betanítást és hárítsa el a gyakori hibákat

## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések keresése
> **Megjegyzés**: Ha a VS Code nincs telepítve, akkor a Ryzen AI Developer Centerrel telepítheti.

<!-- @require:software-update -->
<!-- @device:end -->

## A szoftveres előfeltételek telepítése

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
**Adjon hozzáférést felhasználójának a GPU-eszközökhöz** (a változás érvénybe lépéséhez jelentkezzen ki, majd be):

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
**Windows:** Itt csak az alapcsomagok vannak tesztelve és támogatva. **A bitsandbytes nincs jól támogatva Windows alatt**, ezért a Windows-os telepítés kihagyja azt; Windows alatt használjon LoRA-t vagy teljes finomhangolást (a QLoRA-hoz bitsandbytes szükséges, és Linuxra van szánva).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### HF-hitelesítés engedélyezése (zárolt vagy egyéni / nem előre telepített modellek esetén)

Ebben a példában a **google/gemma-3-4b-it** modellt használjuk, amely egy **zárolt** modell. El kell fogadnia a modell feltételeit a Hugging Face oldalon, majd hitelesítenie kell magát, hogy a betanítási szkriptek le tudják tölteni.

1. **Fogadja el a licencet:** Nyissa meg a [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it) oldalt, jelentkezzen be (vagy hozzon létre fiókot), és fogadja el a licencet/feltételeket a modell oldalán (pl. „Agree and access repository”).
2. **Telepítés és bejelentkezés:** Telepítse a Hugging Face CLI-t, majd futtassa a szokásos bejelentkezést:

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

A **LoRA (Low-Rank Adaptation)** befagyasztva tartja az alapmodellt, és csak kis „adapter” mátrixokat tanít be, amelyeket bizonyos rétegekhez adnak hozzá.

- **A kulcsgondolat**: ahelyett, hogy egy hatalmas, több millió paraméterből álló súlymátrixot frissítenénk, egy alacsony rangú frissítést tanulunk meg (két kis mátrix, amelyek szorzata sokkal kevesebb paramétert tartalmaz). Ez jelentős csökkenést eredményez a betanítható paraméterek számában és a VRAM-használatban, miközben megőrzi a teljes finomhangolás minőségének nagy részét.

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

A **QLoRA** a **4 bites kvantálást** ötvözi a **LoRA-val**. Az alapmodellt 4 biten töltjük be (jelentős memóriamegtakarítást eredményez), és csak a LoRA adaptereket tanítjuk magasabb pontossággal. Így megkapja a LoRA paraméterhatékonyságát, valamint sokkal alacsonyabb VRAM-igényt, kis minőségromlás mellett a teljes pontosságú LoRA-hoz képest. Vegye figyelembe, hogy a 4 bites kvantálás numerikus instabilitásokat okozhat (veszteség-kiugrások vagy NaN-ok), ezért a felhasználók gyakran előnyben részesíthetik a **LoRA-t**, ha elegendő VRAM áll rendelkezésre.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Megjegyzés**: Az olyan MXFP4 alapmodellek esetén, mint az `openai/gpt-oss-20b`, javasoljuk a **LoRA** (`train_lora.py`) használatát a QLoRA helyett. A QLoRA szkript `bitsandbytes` 4 bites útvonala jellemzően BF16-ra dekvantálja az MXFP4 súlyokat, így a futtatás a szokásos LoRA-hoz hasonlóan viselkedik. A natív MXFP4-hez forrásból épített `bitsandbytes`-ra van szükség, valamint egy hozzá illeszkedő Transformers/Triton/kernels csomagra. Lásd a [Transformers MXFP4 dokumentációt](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---

### 2. Válassza ki a módszert

| Módszer | Memória | Sebesség | Minőség | Legjobban alkalmas |
|--------|--------|-------|---------|----------|
| **QLoRA** (csak Linux) | 12-16GB | Leggyorsabb | 90-95% | Alacsony memóriahasználat |
| **LoRA** | 24-32GB | Gyors | 95-98% | Kiegyensúlyozott megközelítés |
| **Teljes** | 80GB+ | Leglassabb | 100% | Maximális minőség |
### 3. Futtassa a betanítást

**Az adathalmaz és amit a modell megtanul**  
A szkriptek az adathalmazt csevegési példákká alakítják. Például a QLoRA szkript az **Abirate/english_quotes** adathalmazt használja: minden példa egy felhasználó–asszisztens párrá válik, például:

- **Felhasználó:** „Adj egy idézetet erről: &lt;tag&gt;”
- **Asszisztens:** „&lt;idézet&gt; – &lt;szerző&gt;”

A finomhangolás megtanítja a modellt arra, hogy válaszoljon egy adott témáról szóló idézetet kérő promptokra, és `<idézet szövege> - <szerző>` formátumban adja vissza azokat. A LoRA és a teljes finomhangolási szkriptek a **databricks/databricks-dolly-15k** adathalmazt (általános utasítás/válasz párok) használják, így a pontos feladat szkriptenként eltérő; az elgondolás azonban ugyanaz - a modell adaptálása a kiválasztott adathalmazhoz és formátumhoz.

Az alábbiakban összefoglaljuk az elérhető betanítási módszereket. Minden módszer hivatkozik a saját szkriptjére, és rövid leírást ad a megfelelő megközelítés kiválasztásához.

| Szkript                           | Módszer            | Leírás                                                                                                         | Jellemző VRAM | Ajánlott ehhez                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Kis adapter mátrixokat tanít be, miközben az alapmodellt lefagyasztja. 3-5x gyorsabb; ~95-98%-os teljes minőség.                         | 24–32GB      | Haladó felhasználók; több adapter; több VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(csak Linux)*             | **QLoRA**       | 4 bites kvantálás + LoRA adapterek. Legalacsonyabb memóriahasználat, leggyorsabb, kismértékű minőségi kompromisszum. `bitsandbytes` szükséges (csak Linux).                            | 12–16GB      | Legtöbb felhasználó; gyors kísérletek; korlátozott VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Teljes finomhangolás** | Az összes modellparamétert frissíti. Maximális minőség; a legnagyobb memória- és számítási igény.                                    | 40GB+        | Maximális minőség; kutatás; nagy VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Megjegyzés:** A teljes finomhangoláshoz (`train_full_finetuning.py`) 64 GB-nál több rendszer-RAM szükséges lehet, ami ezen az eszközön nem biztos, hogy megvalósítható. Fontolja meg a LoRA vagy QLoRA használatát helyette.
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés:** A teljes finomhangoláshoz (`train_full_finetuning.py`) 64 GB-nál több rendszer-RAM szükséges lehet, ami ezen az eszközön nem biztos, hogy megvalósítható. Fontolja meg a LoRA használatát helyette.
<!-- @os:end -->
<!-- @device:end -->

Egyszerűen válassza ki a kívánt `Training method` (betanítási módszer) opciót, töltse le a megfelelő szkriptet, és futtassa a parancs segítségével, miközben a virtuális környezete aktív marad: 

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

### LoRA/QLoRA betanítás után

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

### A LoRA adapter összevonása az alapmodellel

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Megjegyzés:**  
- Győződjön meg arról, hogy a modell könyvtárának neve (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) megegyezik a betanításból származó tényleges kimeneti mappával.  
- Ha QLoRA helyett LoRA-t használt, egyszerűen cserélje ki az elérési utat ennek megfelelően.  
- Egyes Gemma modellek esetén szükséges a `trust_remote_code=True` megadása a `from_pretrained` függvényben; adja hozzá, ha erre vonatkozó figyelmeztetést lát.

Egyéb testreszabott beállításokért (kitöltő tokenek, eszköz stb.) tekintse meg a betanításhoz használt szkriptet.

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

### Saját adathalmaz használata

Minden szkript ugyanazt az adathalmaz-formátumot használja. Cserélje ki a betöltési szakaszt:

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

**Adathalmaz-formátum helyi JSON/JSONL fájlhoz:**

Ennek a módszernek a használatakor győződjön meg arról, hogy a JSON fájlok megfelelően strukturáltak, hogy elkerülje az elemzési hibákat. 

Az alábbi irányelveket be kell tartani:
* **Fájlformázás:** A JSON fájlokat egy integrált fejlesztői környezetben (IDE) kell formázni, hogy biztosítva legyen a megfelelő szerkezet és szintaxis.
* **Szükséges kulcsok:** Az egyedi JSON fájlnak tartalmaznia kell az `instruction` és `response` kulcsokat. Ezek a kulcsok elengedhetetlenek a módszer megfelelő működéséhez.
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
**Adathalmaz-formátum Hugging Face Hub adathalmazhoz**

A Hugging Face adathalmazainak használatakor győződjön meg arról, hogy az adathalmazok megfelelően vannak strukturálva a zökkenőmentes integráció érdekében. 

Az alábbi irányelveket kell követni:
* **Utasítás-válasz pár:** Összpontosítson az `instruction-response` párt tartalmazó adathalmazokra. Ez a szerkezet elengedhetetlen a kívánt funkcionalitáshoz.
* **Egyedi kulcsmódosítás:** Ha az adathalmaz nem felel meg az `instruction-response` szerkezetnek, lehetősége van módosítani a `format_instruction()` függvényt. Ez lehetővé teszi, hogy a szükséges egyedi kulcsokhoz igazítsa azt.

Példa a módosításra: Abban az esetben, ha az adathalmaz kimenetét módosítani kell, módosíthatja a válasz szakaszt a format_instruction() függvényen belül, hogy megfeleljen az igényeinek.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Adathalmaz-formátum CSV fájlhoz**

Ahhoz, hogy a szkript CSV fájlformátummal is működjön, gondoskodnia kell arról, hogy a CSV fájl tartalmazzon `instruction` és `response` nevű oszlopokat. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Betanítási paraméterek beállítása

Szerkessze a betanítási szkriptet, és módosítsa a változókat a céljainak megfelelően: **tanulási ráta** (`LR`), **epochok** (`EPOCHS`), **kötegméret** (`BATCH_SIZE`), **gradiens akkumuláció** (`GRAD_ACCUM_STEPS`), valamint LoRA/QLoRA esetén a **rang** (`LORA_R`). Gyorsabb futtatáshoz használjon kevesebb epochot és magasabb tanulási rátát (LR); jobb minőséghez több epochot és alacsonyabb LR-t. Csökkentse a kötegméretet vagy a sorozathosszt, ha memóriahiány-hibába ütközik.

### Memóriaoptimalizálási tippek

Ha memóriahiány-hibákkal találkozik:

**1. Csökkentse a kötegméretet:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Csökkentse a sorozathosszt:**
```python
max_seq_length=256  # Instead of 512
```

**3. Használjon agresszívabb kvantálást:**
```
Full → LoRA → QLoRA
```

**4. Kapcsolja be a gradiens ellenőrzőpontozást (csak teljes finomhangolás esetén):**
```python
model.gradient_checkpointing_enable()
```

---

## Megfigyelés és hibakeresés

### Figyelje a GPU memóriát

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Opcionális) Kísérletek követése a Weights & Biases eszközzel

Futtatások és metrikák naplózásához a [Weights & Biases](https://wandb.ai) szolgáltatásba:

```bash
pip install wandb
wandb login
```

A tanítási szkriptben állítsd be a `report_to="wandb"` értéket, és opcionálisan a `run_name="your-experiment-name"` értéket a trainer konfigurációban. Ha nem szeretnéd használni a Wandb-et, hagyd a `report_to` alapértelmezett értékét, vagy állítsd `"none"` értékre.

### Gyakori problémák

#### Memóriahiány (OOM)

**Megoldás:** Csökkentsd a batch méretét és/vagy használj QLoRA-t
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### A veszteség nem csökken

**Megoldás:** Állítsd be a tanulási rátát
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Lassú tanítás

**Megoldás:** Növeld a batch méretét, ha a memória engedi
```python
BATCH_SIZE = 8
```
## Következő lépések

Miután sikeresen elvégezted a finomhangolást, fontold meg a következő lépéseket, hogy még többet hozz ki a modelledből:

1. **Értékeld ki** alaposan a modellt egy kihagyott teszthalmazon, hogy megmérd az általánosítást, és elkerüld a túlillesztést.
2. **Kísérletezz** különböző hiperparaméter-értékekkel a pontosság, a sebesség és a memóriahasználat közötti jobb egyensúly érdekében.
3. **Kövesd nyomon** az összes kísérletedet (és a hozzájuk tartozó metrikákat) a Weights & Biases segítségével a reprodukálható kutatás érdekében.
4. **Próbáld ki** a tanítást saját, egyedi adathalmazokon, hogy a modellt kifejezetten a saját felhasználási esetedhez igazítsd.
5. **Telepítsd** a finomhangolt modelledet gyors következtetéshez, hatékony háttérrendszerek – például vLLM – segítségével, kompatibilis hardveren.
6. **Fedezz fel** további fejlett technikákat, például prompt engineeringet, kevert pontosságot (mixed precision) és hosszabb szekvenciahosszokat.
7. **Taníts** több LoRA adaptert különböző feladatokhoz vagy területekhez, és cseréld őket igény szerint.

---