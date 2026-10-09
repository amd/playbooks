<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Áttekintés

Ez az oktatóanyag lépésről lépésre bemutatott példákat ad egy nagy nyelvi modell (LLM) PyTorch és ROCm segítségével történő finomhangolásához. Számos technikát bemutat, a standard finomhangolástól a memóriahatékony Parameter-Efficient Fine-Tuning (PEFT) stratégiákig, így könnyedén testre szabhatja a modelleket az igényeinek megfelelően.

**Használt modell**: google/gemma-3-4b-it (QLoRA szkript: openai/gpt-oss-20b)  *(lásd: [HF hitelesítés engedélyezése](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models), ha korlátozott hozzáférésű)*  
**Hardver**: AMD Radeon™ GPU ROCm-támogatással  
**Keretrendszer**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Megjegyzés:** 
> - A teljes finomhangoláshoz legalább **64 GB rendszermemória (RAM)** szükséges, amelyből legalább **32 GB-nak elérhetőnek kell lennie a GPU számára** (ez a 32 GB a 64 GB-ból áll rendelkezésre, nem azon felül).
> - Más modellarchitektúrákat is kipróbálhat, beleértve a **GPT-OSS-20B**-t, ha behelyettesíti a modellt a megadott betanítási szkriptekbe.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **Megjegyzés:** A LoRA és QLoRA finomhangoláshoz legalább **32 GB rendszermemória (RAM)** szükséges, amelyből legalább **16 GB-nak elérhetőnek kell lennie a GPU számára** (ez a 16 GB a 32 GB-ból áll rendelkezésre, nem azon felül).
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés:** A LoRA finomhangoláshoz legalább **32 GB rendszermemória (RAM)** szükséges, amelyből legalább **16 GB-nak elérhetőnek kell lennie a GPU számára** (ez a 16 GB a 32 GB-ból áll rendelkezésre, nem azon felül).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Megjegyzés:** A LoRA és QLoRA finomhangoláshoz legalább **16 GB dedikált GPU-memóriával** és **32 GB rendszermemóriával (RAM)** rendelkező videokártya szükséges.
> - Linux rendszeren a betanítás teljes egészében a videokártya dedikált VRAM-jában fut.
> - Nem áll át megosztott GPU-memóriára (rendszer RAM-ra), ha elfogy a VRAM.
> - A 16 GB-nál kevesebb dedikált VRAM-mal rendelkező kártyák kifogynak a memóriából a betanítás során Linuxon, még akkor is, ha a rendszerben bőven van RAM.
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés:** A LoRA finomhangoláshoz legalább **16 GB teljes GPU-memória** és **32 GB rendszermemória (RAM)** szükséges.
> - Windows rendszeren a teljes GPU-memória egyesíti a videokártya dedikált VRAM-ját a megosztott GPU-memóriával (amelyet a rendszer RAM-ból kölcsönöz).
> - Ezért a 16 GB-nál kevesebb dedikált VRAM-mal rendelkező kártyák is képesek lehetnek futtatni ezt az útmutatót, mivel a különbséget megosztott GPU-memóriával pótolják.
<!-- @os:end -->
<!-- @device:end -->

## Mit fog megtanulni

- Hogyan finomhangoljon egy LLM-et LoRA, QLoRA és teljes finomhangolás használatával PyTorch és ROCm segítségével
- Hogyan mentse el és telepítse a finomhangolt modellt
- Hogyan kövesse nyomon a betanítást, és hárítsa el a gyakori problémákat

<!-- @device:halo_box,halo,stx,krk -->
## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése
> **Megjegyzés**: Ha a VS Code nincs telepítve, telepítheti a Ryzen AI Developer Centerrel.

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftveres előfeltételek telepítése

#### Virtuális környezet létrehozása

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
**Adjon hozzáférést a felhasználójának a GPU-eszközökhöz** (jelentkezzen ki, majd be, hogy ez érvénybe lépjen):

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

#### Alapvető függőségek telepítése
<!-- @require:pytorch -->

#### További függőségek

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Itt csak a lényegi csomagok vannak tesztelve és támogatva. **A bitsandbytes nem igazán támogatott Windows rendszeren**, ezért a Windows telepítés kihagyja azt; használjon LoRA-t vagy teljes finomhangolást Windows alatt (a QLoRA bitsandbytes-ot igényel, és Linuxra szánták).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### HF hitelesítés engedélyezése (korlátozott hozzáférésű vagy egyéni / nem előre telepített modellek)

Ebben a példában a **google/gemma-3-4b-it** modellt használjuk, amely egy **korlátozott hozzáférésű (gated)** modell. El kell fogadnia a modell feltételeit a Hugging Face-en, majd hitelesítenie kell magát, hogy a betanítási szkriptek le tudják tölteni.

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

## A technikák megismerése

### Mi az a LoRA?

A **LoRA (Low-Rank Adaptation)** befagyasztva tartja az alapmodellt, és csak kis „adapter” mátrixokat tanít be, amelyeket bizonyos rétegekhez adunk hozzá.

- **A fő gondolat**: ahelyett, hogy egy hatalmas, több millió paraméteres súlymátrixot frissítenénk, egy alacsony rangú frissítést tanulunk meg (két kis mátrix, amelyek szorzatának sokkal kevesebb paramétere van). Ez jelentősen csökkenti a betanítható paraméterek számát és a VRAM-használatot, miközben megőrzi a teljes finomhangolás minőségének nagy részét.

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

A **QLoRA** a **4 bites kvantálást** kombinálja a **LoRA**-val. Az alapmodell 4 bitesen kerül betöltésre (nagy memóriamegtakarítás), és csak a LoRA adapterek kerülnek betanításra nagyobb pontossággal. Így megkapja a LoRA paraméterhatékonyságát, ráadásul sokkal alacsonyabb VRAM-használat mellett, a teljes pontosságú LoRA-hoz képest csekély minőségi kompromisszum árán. Vegye figyelembe, hogy a 4 bites kvantálás numerikus instabilitást okozhat (veszteségkiugrások vagy NaN-ok), ezért a felhasználók gyakran inkább a **LoRA**-t részesítik előnyben, ha elegendő VRAM áll rendelkezésre.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Megjegyzés**: Az olyan MXFP4 alapmodellek esetén, mint az `openai/gpt-oss-20b`, a **LoRA** (`train_lora.py`) használatát javasoljuk a QLoRA helyett. A QLoRA szkript `bitsandbytes` 4 bites útvonala jellemzően BF16-ra dekvantálja az MXFP4 súlyokat, így a futtatás a standard LoRA-hoz hasonlóan viselkedik. A natív MXFP4-hez forrásból épített `bitsandbytes`-ra, valamint megfelelő Transformers/Triton/kernels halmazra van szükség. Lásd a [Transformers MXFP4 dokumentációt](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. Válassza ki a módszerét

| Módszer | Memória | Sebesség | Minőség | Legjobb célra |
|--------|--------|-------|---------|----------|
| **QLoRA** (csak Linux) | 12-16GB | Leggyorsabb | 90-95% | Alacsony memóriahasználat |
| **LoRA** | 24-32GB | Gyors | 95-98% | Kiegyensúlyozott megközelítés |
| **Full** | 80GB+ | Leglassabb | 100% | Maximális minőség |

### 3. Futtassa a tanítást

**Adathalmaz és amit a modell megtanul**  
A szkriptek az adathalmazt chat példákká alakítják. Például a QLoRA szkript az **Abirate/english_quotes** adathalmazt használja: minden példa egy felhasználó–asszisztens párrá válik, például:

- **Felhasználó:** „Mondj egy idézetet erről: &lt;tag&gt;”
- **Asszisztens:** „&lt;idézet&gt; – &lt;szerző&gt;”

A finomhangolás megtanítja a modellt arra, hogy válaszoljon azokra a promptokra, amelyek egy témához kapcsolódó idézetet kérnek, és azokat a `<idézet szövege> - <szerző>` formátumban adja vissza. A LoRA és a teljes finomhangolási szkriptek a **databricks/databricks-dolly-15k** adathalmazt használják (általános utasítás/válasz párok), így a pontos feladat szkriptenként eltérő; az elv azonban ugyanaz - a modell adaptálása a kiválasztott adathalmazhoz és formátumhoz.

Az alábbiakban összefoglaljuk az elérhető tanítási módszereket. Minden módszer hivatkozik a saját szkriptjére, és rövid leírást ad a megfelelő megközelítés kiválasztásához.

| Szkript                           | Módszer            | Leírás                                                                                                         | Jellemző VRAM | Ajánlott erre                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Kis adapter mátrixokat tanít, miközben a bázismodellt lefagyasztja. 3–5x gyorsabb; ~95–98%-os teljes minőség.                         | 24–32GB      | Haladó felhasználók; több adapter; több VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(csak Linux)*             | **QLoRA**       | 4-bites kvantálás + LoRA adapterek. Legalacsonyabb memóriahasználat, leggyorsabb, kis minőségi kompromisszummal. A `bitsandbytes` szükséges hozzá (csak Linux).                            | 12–16GB      | Legtöbb felhasználó; gyors kísérletek; korlátozott VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Teljes finomhangolás** | Az összes modellparamétert frissíti. Maximális minőség; legmagasabb memória- és számítási igény.                                    | 40GB+      | Maximális minőség; kutatás; nagy VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Megjegyzés:** A teljes finomhangoláshoz (`train_full_finetuning.py`) 64GB-nál több rendszer RAM-ra lehet szükség, és előfordulhat, hogy ez az eszköz nem alkalmas rá. Fontolja meg inkább a LoRA vagy a QLoRA használatát.
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés:** A teljes finomhangoláshoz (`train_full_finetuning.py`) 64GB-nál több rendszer RAM-ra lehet szükség, és előfordulhat, hogy ez az eszköz nem alkalmas rá. Fontolja meg inkább a LoRA használatát.
<!-- @os:end -->
<!-- @device:end -->

Egyszerűen válassza ki a kívánt `Training method` (tanítási módszer) beállítást, töltse le a megfelelő szkriptet, és futtassa a parancs segítségével, miközben a virtuális környezet aktiválva marad: 

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

### LoRA adapter egyesítése az alapmodellel

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Megjegyzés:**  
- Győződjön meg róla, hogy a modell könyvtárának neve (`output-gemma-3-4b-it-full`, `output-gpt-oss-20b-qlora`) megegyezik a tanításból származó tényleges kimeneti mappával.  
- Ha QLoRA helyett LoRA-t használt, egyszerűen cserélje ki az elérési utat ennek megfelelően.  
- Egyes Gemma modellek esetén szükséges lehet a `trust_remote_code=True` megadása a `from_pretrained` függvényben; adja hozzá, ha ezzel kapcsolatos figyelmeztetést lát.

A további egyedi beállításokért (padding tokenek, eszköz stb.) tekintse meg a tanításhoz használt szkriptet.

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

## Testreszabási útmutató

### Saját adathalmaz használata

Minden szkript ugyanazt az adathalmaz-formátumot használja. Cserélje ki a betöltési részt:

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

**Adathalmaz formátuma helyi JSON/JSONL fájlhoz:**

Ennek a módszernek a használatakor győződjön meg róla, hogy a JSON fájlok megfelelően strukturáltak, elkerülve ezzel az elemzési hibákat.

Az alábbi irányelveket kell betartani:
* **Fájlformázás:** A JSON fájlokat egy integrált fejlesztői környezetben (IDE) kell formázni, hogy biztosított legyen a megfelelő szerkezet és szintaxis.
* **Szükséges kulcsok:** Az egyéni JSON fájlnak tartalmaznia kell az `instruction` és `response` kulcsokat. Ezek a kulcsok elengedhetetlenek a módszer megfelelő működéséhez.
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
**Adathalmaz formátuma Hugging Face Hub adathalmazhoz**

A Hugging Face adathalmazainak használatakor győződjön meg róla, hogy az adathalmazok megfelelően strukturáltak a zökkenőmentes integráció érdekében.

Az alábbi irányelveket kell követni:
* **Utasítás-válasz pár:** Olyan adathalmazokra összpontosítson, amelyek `instruction-response` párt tartalmaznak. Ez a szerkezet elengedhetetlen a tervezett működéshez.
* **Egyedi kulcs módosítása:** Ha az adathalmaz nem felel meg az `instruction-response` szerkezetnek, lehetősége van módosítani a `format_instruction()` függvényt. Ez lehetővé teszi, hogy igény szerint egyedi kulcsokat is kezelni tudjon.

Példa módosításra: Ha az adathalmaz kimenetét módosítani kell, a `format_instruction()` függvényen belül módosíthatja a válasz részt, hogy megfeleljen az igényeinek.
```python
def format_instruction(example):
    return {
        "messages": [
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
    }
```
**Adathalmaz formátuma CSV fájlhoz**

Ahhoz, hogy a szkript CSV fájlformátumot használjon, győződjön meg róla, hogy a CSV fájl `instruction` és `response` nevű oszlopokat tartalmaz.
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### A tanítási paraméterek beállítása

Szerkessze a tanítási szkriptet, és módosítsa a változókat a céljainak megfelelően: **tanulási ráta** (`LR`), **epochok száma** (`EPOCHS`), **köteg (batch) méret** (`BATCH_SIZE`), **gradiens akkumuláció** (`GRAD_ACCUM_STEPS`), illetve LoRA/QLoRA esetén a **rank** (`LORA_R`). A gyorsabb futtatásokhoz használjon kevesebb epochot és magasabb tanulási rátát (LR); a jobb minőséghez több epochot és alacsonyabb LR-t. Csökkentse a köteg méretét vagy a szekvencia hosszát, ha memóriahiba (out-of-memory) hibát tapasztal.
### Memóriaoptimalizálási tippek

Ha memóriakifogyási (out-of-memory) hibákba ütközik:

**1. Csökkentse a köteg (batch) méretét:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Csökkentse a szekvenciahosszt:**
```python
max_seq_length=256  # Instead of 512
```

**3. Használjon agresszívabb kvantálást:**
```
Full → LoRA → QLoRA
```

**4. Engedélyezze a gradiens ellenőrzőpontozást (Gradient Checkpointing) (csak teljes finomhangolás esetén):**
```python
model.gradient_checkpointing_enable()
```

---

## Megfigyelés és hibakeresés

### GPU-memória figyelése

```bash
# Check ROCm GPU status
watch -n 1 amd-smi

# Show memory info
rocm-smi --showmeminfo vram
```

### (Opcionális) Kísérletek nyomon követése a Weights & Biases segítségével

Futtatások és metrikák naplózásához a [Weights & Biases](https://wandb.ai) szolgáltatásban:

```bash
pip install wandb
wandb login
```

A tanítási szkriptben állítsa be a `report_to="wandb"` értéket, és opcionálisan a `run_name="your-experiment-name"` értéket a trainer konfigurációban. Ha nem szeretné használni a Wandb-ot, hagyja a `report_to` beállítást az alapértelmezett értéken, vagy állítsa `"none"` értékre.

### Gyakori problémák

#### Memóriakifogyás (OOM)

**Megoldás:** Csökkentse a köteg méretét és/vagy használjon QLoRA-t
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16
# Or: python train_qlora.py
```

#### A veszteség nem csökken

**Megoldás:** Állítsa be a tanulási rátát
```python
LR = 1e-4  # Try lower
# or
LR = 5e-4  # Try higher
```

#### Lassú tanítás

**Megoldás:** Növelje a köteg méretét, ha a memória engedi
```python
BATCH_SIZE = 8
```
## Következő lépések

A sikeres finomhangolás befejezése után érdemes megfontolni az alábbi következő lépéseket, hogy még többet hozhasson ki a modelljéből:

1. **Értékelje ki** alaposan egy elkülönített tesztadathalmazon, hogy mérje az általánosítóképességet, és elkerülje a túlillesztést.
2. **Kísérletezzen** különböző hiperparaméter-értékekkel a jobb pontosság, sebesség és memóriahasználat közötti egyensúly érdekében.
3. **Kövesse nyomon** az összes kísérletét (és a hozzájuk tartozó metrikákat) a Weights & Biases segítségével a reprodukálható kutatás érdekében.
4. **Próbálja ki** a tanítást saját, egyedi adathalmazokon, hogy a modellt kifejezetten az Ön használati esetéhez igazítsa.
5. **Telepítse** a finomhangolt modellt gyors következtetéshez olyan hatékony háttérrendszerek segítségével, mint a vLLM, kompatibilis hardveren.
6. **Fedezzen fel** olyan haladó technikákat, mint a promptmérnöki munka (prompt engineering), a vegyes pontosság (mixed precision) és a hosszabb szekvenciahosszok.
7. **Tanítson** több LoRA adaptert különböző feladatokhoz vagy témakörökhöz, és cserélje őket igény szerint.

---