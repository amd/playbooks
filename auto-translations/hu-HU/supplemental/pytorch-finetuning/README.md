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

Ez az útmutató lépésről lépésre bemutatja egy nagy nyelvi modell (LLM) finomhangolását PyTorch és ROCm használatával. Számos technikát ismertet, a hagyományos finomhangolástól kezdve a memóriahatékony, paraméterhatékony finomhangolási (PEFT) stratégiákig, hogy könnyedén hozzáigazíthassa a modelleket saját igényeihez.

**Használt modell**: google/gemma-3-4b-it  *(lásd: [HF hitelesítés engedélyezése](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models), ha zárolt modellről van szó)*  
**Hardver**: AMD Radeon™ GPU ROCm-támogatással  
**Keretrendszer**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Megjegyzés:** 
> - A teljes finomhangoláshoz legalább **64 GB rendszer-RAM** szükséges, amelyből legalább **32 GB álljon rendelkezésre a GPU számára** (a 32 GB a 64 GB részét képezi, nem pedig azon felül szükséges).
> - Más modellarchitektúrákat is kipróbálhat, beleértve a **GPT-OSS-20B**-t is, ha a mellékelt tanítási szkriptekben lecseréli a modellt.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **Megjegyzés:** A LoRA és QLoRA finomhangoláshoz legalább **32 GB rendszer-RAM** szükséges, amelyből legalább **16 GB álljon rendelkezésre a GPU számára** (a 16 GB a 32 GB részét képezi, nem pedig azon felül szükséges).
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés:** A LoRA finomhangoláshoz legalább **32 GB rendszer-RAM** szükséges, amelyből legalább **16 GB álljon rendelkezésre a GPU számára** (a 16 GB a 32 GB részét képezi, nem pedig azon felül szükséges).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Megjegyzés:** A LoRA és QLoRA finomhangoláshoz legalább **16 GB dedikált GPU-memóriával** rendelkező videokártya és **32 GB rendszer-RAM** szükséges.
> - Linux alatt a tanítás teljes egészében a videokártya dedikált VRAM-jában fut.
> - Nem tér vissza a megosztott GPU-memóriára (rendszer-RAM), ha a VRAM elfogy.
> - A 16 GB-nál kevesebb dedikált VRAM-mal rendelkező kártyák Linux alatt kifogynak a memóriából a tanítás során, még akkor is, ha a rendszerben bőven van RAM.
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés:** A LoRA finomhangoláshoz legalább **16 GB teljes GPU-memória** és **32 GB rendszer-RAM** szükséges.
> - Windows alatt a teljes GPU-memória a videokártya dedikált VRAM-ját és a megosztott GPU-memóriát (amelyet a rendszer-RAM-ból kölcsönöz) kombinálja.
> - Ezért a 16 GB-nál kevesebb dedikált VRAM-mal rendelkező kártyák is képesek futtatni ezt a playbookot, mivel a különbséget megosztott GPU-memóriával pótolják.
<!-- @os:end -->
<!-- @device:end -->

## Amit meg fog tanulni

- Hogyan finomhangoljon egy LLM-et LoRA, QLoRA és teljes finomhangolás segítségével PyTorch és ROCm használatával
- Hogyan mentse el és telepítse a finomhangolt modellt
- Hogyan kövesse nyomon a tanítást és hárítsa el a gyakori problémákat

## A Memóriakonfiguráció Beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések Ellenőrzése
> **Megjegyzés**: Ha a VS Code nincs telepítve, telepítheti a Ryzen AI Developer Center segítségével.

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftveres Előfeltételek Telepítése

#### Virtuális Környezet Létrehozása

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
**Adjon hozzáférést a felhasználójának a GPU-eszközökhöz** (a hatás érvényesítéséhez jelentkezzen ki, majd be):

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

#### Alapvető Függőségek Telepítése
<!-- @require:pytorch -->

#### További Függőségek

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 accelerate peft trl bitsandbytes "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
**Windows:** Itt csak az alapcsomagokat teszteltük és támogatjuk. **A bitsandbytes nem támogatott megfelelően Windows alatt**, ezért a Windows-telepítés kihagyja azt; Windows alatt használjon LoRA-t vagy teljes finomhangolást (a QLoRA-hoz bitsandbytes szükséges, és Linuxra van szánva).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==4.57.1 safetensors==0.6.2 datasets==4.2.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### HF hitelesítés engedélyezése (zárolt vagy egyéni / nem előre telepített modellek)

Ebben a példában a **google/gemma-3-4b-it** modellt használjuk, amely egy **zárolt** modell. El kell fogadnia a modell feltételeit a Hugging Face-en, majd hitelesítenie kell magát, hogy a tanítási szkriptek le tudják tölteni.

1. **Fogadja el a licencet:** Nyissa meg a [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it) oldalt, jelentkezzen be (vagy hozzon létre egy fiókot), majd fogadja el a licencet/feltételeket a modell oldalán (pl. „Agree and access repository”).
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

## A Technikák Megismerése

### Mi az a LoRA?

A **LoRA (Low-Rank Adaptation)** befagyasztva tartja az alapmodellt, és csak kis „adapter” mátrixokat tanít, amelyeket bizonyos rétegekhez adnak hozzá. 

- **A kulcsötlet**: ahelyett, hogy egy hatalmas, több millió paraméterből álló súlymátrixot frissítenénk, egy alacsony rangú frissítést tanulunk meg (két kis mátrix, amelyek szorzata sokkal kevesebb paraméterből áll). Ez jelentős csökkenést eredményez a tanítható paraméterek számában és a VRAM-felhasználásban, miközben megőrzi a teljes finomhangolás minőségének nagy részét.

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

A **QLoRA** a **4-bites kvantálást** ötvözi a **LoRA**-val. Az alapmodell 4-bites formában töltődik be (jelentős memóriamegtakarítás), és csak a LoRA-adapterek tanulnak nagyobb pontossággal. Így megkapja a LoRA paraméterhatékonyságát, valamint jóval alacsonyabb VRAM-igényt, kis minőségromlás árán a teljes pontosságú LoRA-hoz képest. Vegye figyelembe, hogy a 4-bites kvantálás numerikus instabilitásokat (veszteségkiugrásokat vagy NaN-okat) okozhat, ezért a felhasználók gyakran a **LoRA**-t preferálhatják, ha elegendő VRAM áll rendelkezésre.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Megjegyzés**: Az olyan MXFP4 alapmodellekhez, mint az `openai/gpt-oss-20b`, a **LoRA** (`train_lora.py`) használatát javasoljuk a QLoRA helyett. A QLoRA szkript `bitsandbytes` 4-bites útvonala jellemzően BF16-ra dekvantálja az MXFP4 súlyokat, így a futtatás úgy viselkedik, mint egy standard LoRA. A natív MXFP4-hez forrásból épített `bitsandbytes`-ra, valamint egy hozzá illeszkedő Transformers/Triton/kernels rendszerre van szükség. Lásd a [Transformers MXFP4 dokumentációját](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. Válassza ki a módszert

| Módszer | Memória | Sebesség | Minőség | Legjobban ajánlott |
|--------|--------|-------|---------|----------|
| **QLoRA** (csak Linuxon) | 12-16GB | Leggyorsabb | 90-95% | Alacsony memóriahasználat |
| **LoRA** | 24-32GB | Gyors | 95-98% | Kiegyensúlyozott megközelítés |
| **Full** | 80GB+ | Leglassabb | 100% | Maximális minőség |

### 3. Tanítás futtatása

**Adathalmaz és amit a modell megtanul**  
A szkriptek chat-példákká alakítják az adathalmazt. Például a QLoRA szkript az **Abirate/english_quotes** adathalmazt használja: minden példa egy felhasználó–asszisztens párrá alakul, például:

- **Felhasználó:** „Adj egy idézetet erről: &lt;tag&gt;”
- **Asszisztens:** „&lt;idézet&gt; – &lt;szerző&gt;”

A finomhangolás megtanítja a modellt arra, hogy válaszoljon az adott témával kapcsolatos idézetet kérő promptokra, és `<idézet szövege> - <szerző>` formátumban adja vissza őket. A LoRA és a teljes finomhangolási szkriptek a **databricks/databricks-dolly-15k** adathalmazt használják (általános utasítás/válasz párok), így a pontos feladat szkriptenként eltérő; az alapelv azonban ugyanaz - a modell adaptálása a kiválasztott adathalmazhoz és formátumhoz.

Az alábbiakban a rendelkezésre álló tanítási módszerek összefoglalása látható. Minden módszer a saját szkriptjéhez kapcsolódik, és rövid leírást ad a megfelelő megközelítés kiválasztásához.

| Szkript                           | Módszer            | Leírás                                                                                                         | Jellemző VRAM | Ajánlott                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Kis adaptermátrixokat tanít, miközben az alapmodellt lefagyasztja. 3–5x gyorsabb; ~95–98%-os teljes minőség.                         | 24–32GB      | Haladó felhasználók; több adapter; több VRAM esetén    |
| [`train_qlora.py`](assets/train_qlora.py)  *(csak Linuxon)*             | **QLoRA**       | 4 bites kvantálás + LoRA adapterek. Legalacsonyabb memóriahasználat, leggyorsabb, kismértékű minőségromlás mellett. `bitsandbytes` szükséges (csak Linuxon).                            | 12–16GB      | Legtöbb felhasználó számára; gyors kísérletekhez; korlátozott VRAM esetén      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Teljes finomhangolás** | Az összes modellparamétert frissíti. Maximális minőség; a legnagyobb memória- és számítási igény.                                    | 40GB+        | Maximális minőség; kutatás; nagy VRAM esetén           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Megjegyzés:** A teljes finomhangolás (`train_full_finetuning.py`) 64GB-nál több rendszer RAM-ot igényelhet, és lehet, hogy ezen az eszközön nem megvalósítható. Fontolja meg helyette a LoRA vagy QLoRA használatát.
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés:** A teljes finomhangolás (`train_full_finetuning.py`) 64GB-nál több rendszer RAM-ot igényelhet, és lehet, hogy ezen az eszközön nem megvalósítható. Fontolja meg helyette a LoRA használatát.
<!-- @os:end -->
<!-- @device:end -->

Egyszerűen válassza ki a kívánt `Training method` (tanítási módszer) beállítást, töltse le a hozzá tartozó szkriptet, és futtassa a következő paranccsal, miközben a virtuális környezet aktív marad: 

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
- Győződjön meg róla, hogy a modell könyvtárának neve (`output-gemma-3-4b-full`, `output-gemma-3-4b-qlora`) megegyezik a tanítás során ténylegesen létrejött kimeneti mappával.  
- Ha QLoRA helyett LoRA-t használt, egyszerűen cserélje ki az elérési utat ennek megfelelően.  
- Egyes Gemma modellek megkövetelik a `trust_remote_code=True` megadását a `from_pretrained` függvényben; adja hozzá, ha ezzel kapcsolatos figyelmeztetést lát.

További egyedi beállításokért (padding tokenek, eszköz, stb.) tekintse meg a tanításhoz használt szkriptet.

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

Minden szkript ugyanazt az adathalmaz-formátumot használja. Cserélje le a betöltési részt:

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

Ennek a módszernek a használatakor győződjön meg róla, hogy a JSON fájlok megfelelően vannak felépítve, hogy elkerülje az elemzési hibákat. 

Az alábbi irányelveket kell betartani:
* **Fájlformázás:** A JSON fájlokat egy integrált fejlesztői környezetben (IDE) kell formázni a megfelelő szerkezet és szintaxis biztosítása érdekében.
* **Kötelező kulcsok:** Az egyedi JSON fájlnak tartalmaznia kell az `instruction` és `response` kulcsokat. Ezek a kulcsok elengedhetetlenek ahhoz, hogy a módszer megfelelően működjön.
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

A Hugging Face adathalmazainak használatakor győződjön meg róla, hogy az adathalmazok megfelelően vannak felépítve a zökkenőmentes integráció érdekében. 

Az alábbi irányelveket kell követni:
* **Utasítás-válasz pár:** Olyan adathalmazokra összpontosítson, amelyek `instruction-response` párokat tartalmaznak. Ez a szerkezet elengedhetetlen a kívánt funkció eléréséhez.
* **Egyedi kulcsmódosítás:** Ha az adathalmaz nem felel meg az `instruction-response` szerkezetnek, lehetősége van módosítani a `format_instruction()` függvényt. Ez lehetővé teszi, hogy az igényeinek megfelelő egyedi kulcsokat alkalmazzon.

Példa a módosításra: Ha az adathalmaz kimenetét szükséges módosítani, a format_instruction() függvényen belüli válasz szakaszt módosíthatja az igényeinek megfelelően.
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

Ahhoz, hogy a szkript CSV fájlformátumot használjon, biztosítania kell, hogy a CSV fájl `instruction` és `response` nevű oszlopokat tartalmazzon. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Tanítási paraméterek beállítása

Szerkessze a tanítási szkriptet, és módosítsa a változókat a céljainak megfelelően: **tanulási ráta** (`LR`), **epochok száma** (`EPOCHS`), **batch méret** (`BATCH_SIZE`), **gradiens akkumuláció** (`GRAD_ACCUM_STEPS`), valamint LoRA/QLoRA esetén a **rank** (`LORA_R`). Gyorsabb futtatáshoz használjon kevesebb epochot és magasabb tanulási rátát (LR); jobb minőséghez használjon több epochot és alacsonyabb LR-t. Csökkentse a batch méretét vagy a szekvenciahosszt, ha memóriahiány (out-of-memory) hibába ütközik.
### Memóriaoptimalizálási tippek

Ha memóriahiba-hibaüzeneteket tapasztal:

**1. Csökkentse a Batch Size-t:**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Csökkentse a szekvencia hosszát:**
```python
max_seq_length=256  # Instead of 512
```

**3. Használjon agresszívabb kvantálást:**
```
Full → LoRA → QLoRA
```

**4. Engedélyezze a Gradient Checkpointing funkciót (csak teljes finomhangolás esetén):**
```python
model.gradient_checkpointing_enable()
```

---

## Monitorozás és hibakeresés

### GPU-memória megfigyelése

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

A tanítási szkriptben állítsa be a `report_to="wandb"` értéket, és opcionálisan a `run_name="your-experiment-name"` értéket a trainer konfigurációjában. Ha nem szeretné használni a Wandb-t, hagyja a `report_to` értékét az alapértelmezetten, vagy állítsa `"none"` értékre.

### Gyakori problémák

#### Memóriahiány (OOM)

**Megoldás:** Csökkentse a batch size-t és/vagy használjon QLoRA-t
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

**Megoldás:** Növelje a batch size-t, ha a memória engedi
```python
BATCH_SIZE = 8
```
## Következő lépések

Miután sikeresen elvégezte a finomhangolást, fontolja meg a következő lépéseket, hogy a legtöbbet hozza ki a modelljéből:

1. **Értékelje ki** alaposan a modellt egy elkülönített tesztadathalmazon, hogy megmérje az általánosítási képességét, és elkerülje a túltanulást.
2. **Kísérletezzen** különböző hiperparaméter-értékekkel a jobb pontosság, sebesség és memóriahasználat közötti kompromisszum érdekében.
3. **Kövesse nyomon** az összes kísérletét (és a hozzájuk tartozó metrikákat) a Weights & Biases segítségével a reprodukálható kutatás érdekében.
4. **Próbálja ki** a tanítást saját, egyedi adathalmazokon, hogy a modellt kifejezetten az Ön felhasználási esetéhez igazítsa.
5. **Vezesse be** a finomhangolt modelljét a gyors következtetéshez, hatékony háttérrendszerek, például a vLLM segítségével, kompatibilis hardveren.
6. **Fedezzen fel** olyan haladó technikákat, mint a prompt engineering, a vegyes pontosság (mixed precision) és a hosszabb szekvenciahosszok.
7. **Tanítson** több LoRA adaptert különböző feladatokhoz vagy területekhez, és cserélje őket igény szerint.

---