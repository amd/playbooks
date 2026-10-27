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

Ez az oktatóanyag lépésről lépésre bemutatott példákat tartalmaz egy nagy nyelvi modell (LLM) finomhangolásához PyTorch és ROCm használatával. Számos technikát ismertet, a standard finomhangolástól kezdve a memóriahatékony Parameter-Efficient Fine-Tuning (PEFT) stratégiákig, hogy könnyedén adaptálhasd a modelleket az igényeidhez.

**Használt modell**: google/gemma-3-4b-it (QLoRA szkript: openai/gpt-oss-20b)  *(ha korlátozott hozzáférésű, lásd: [HF hitelesítés engedélyezése](#enable-hf-authentication-gated-or-custom--nonpreinstalled-models))*  
**Hardver**: AMD Radeon™ GPU ROCm támogatással  
**Keretrendszer**: PyTorch + Hugging Face (Transformers, PEFT, Transformer Reinforcement Learning (TRL))

<!-- @device:halo,halo_box -->
> **Megjegyzés:** 
> - A teljes finomhangoláshoz legalább **64 GB rendszer-RAM** szükséges, amelyből legalább **32 GB-nak elérhetőnek kell lennie a GPU számára** (a 32 GB a 64 GB része, nem pedig azon felül értendő).
> - Más modellarchitektúrákat is kipróbálhatsz, beleértve a **GPT-OSS-20B**-t is, ha a megadott tanítási szkriptekben lecseréled a modellt.
<!-- @device:end -->


<!-- @device:stx,krk -->
<!-- @os:linux -->
> **Megjegyzés:** A LoRA és QLoRA finomhangoláshoz legalább **32 GB rendszer-RAM** szükséges, amelyből legalább **16 GB-nak elérhetőnek kell lennie a GPU számára** (a 16 GB a 32 GB része, nem pedig azon felül értendő).
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés:** A LoRA finomhangoláshoz legalább **32 GB rendszer-RAM** szükséges, amelyből legalább **16 GB-nak elérhetőnek kell lennie a GPU számára** (a 16 GB a 32 GB része, nem pedig azon felül értendő).
<!-- @os:end -->
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Megjegyzés:** A LoRA és QLoRA finomhangoláshoz legalább **16 GB dedikált GPU-memóriával** rendelkező videokártya és **32 GB rendszer-RAM** szükséges.
> - Linux alatt a tanítás teljes egészében a videokártya dedikált VRAM-jában fut.
> - Nem áll át megosztott GPU-memóriára (rendszer-RAM-ra), ha elfogy a VRAM.
> - A 16 GB-nál kevesebb dedikált VRAM-mal rendelkező kártyák a tanítás során Linux alatt kifogynak a memóriából, még akkor is, ha a rendszerben bőven van RAM.
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés:** A LoRA finomhangoláshoz legalább **16 GB teljes GPU-memória** és **32 GB rendszer-RAM** szükséges.
> - Windows alatt a teljes GPU-memória a videokártya dedikált VRAM-ját és a megosztott GPU-memóriát (a rendszer-RAM-ból kölcsönzött részt) egyaránt magában foglalja.
> - Ezért a 16 GB-nál kevesebb dedikált VRAM-mal rendelkező kártyák is képesek futtatni ezt a leírást, mivel a különbséget megosztott GPU-memóriával pótolják.
<!-- @os:end -->
<!-- @device:end -->

## Amit megtanulsz

- Hogyan finomhangolj egy LLM-et LoRA, QLoRA és teljes finomhangolás segítségével PyTorch és ROCm használatával
- Hogyan mentsd el és telepítsd a finomhangolt modelledet
- Hogyan kövesd nyomon a tanítást és hárítsd el a gyakori hibákat

<!-- @device:halo_box,halo,stx,krk -->
## Memóriakonfiguráció beállítása

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése
> **Megjegyzés**: Ha a VS Code nincs telepítve, telepítheted a Ryzen AI Developer Center segítségével.

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftveres előfeltételek telepítése

<!-- @prereq:hf-models-gemma-3-4b-it,hf-datasets-databricks-dolly-15k -->
<!-- @os:linux -->
<!-- @prereq:hf-datasets-english-quotes -->
<!-- @os:end -->

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
**Adj hozzáférést a felhasználódnak a GPU-eszközökhöz** (ennek érvénybe lépéséhez jelentkezz ki, majd vissza):

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
**Windows:** Itt csak a mag csomagok tesztelése és támogatása biztosított. **A bitsandbytes nem igazán támogatott Windows alatt**, ezért a Windows-os telepítés kihagyja azt; Windows alatt használj LoRA-t vagy teljes finomhangolást (a QLoRA a bitsandbytes-ot igényli, és Linuxra lett szánva).
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install transformers==5.10.1 safetensors==0.6.2 datasets==4.4.0 accelerate peft trl "fsspec[http]>=2023.1.0,<=2025.9.0"
```
<!-- @test:end -->
<!-- @os:end -->

#### HF hitelesítés engedélyezése (korlátozott hozzáférésű vagy egyedi / nem előre telepített modellek)

Ebben a példában a **google/gemma-3-4b-it** modellt használjuk, amely egy **korlátozott hozzáférésű (gated)** modell. El kell fogadnod a modell feltételeit a Hugging Face-en, majd hitelesítened kell magad, hogy a tanítási szkriptek le tudják tölteni.

1. **Fogadd el a licencet:** Nyisd meg a [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it) oldalt, jelentkezz be (vagy hozz létre fiókot), majd fogadd el a licencet/feltételeket a modell oldalán (pl. „Agree and access repository”).
2. **Telepítés és bejelentkezés:** Telepítsd a Hugging Face CLI-t, majd futtasd a standard bejelentkezést:

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

A **LoRA (Low-Rank Adaptation)** befagyasztva tartja az alapmodellt, és csak kis "adapter" mátrixokat tanít, amelyeket bizonyos rétegekhez adnak hozzá. 

- **A kulcsötlet**: ahelyett, hogy egy hatalmas, több millió paraméterből álló súlymátrixot frissítenénk, egy alacsony rangú frissítést tanulunk meg (két kis mátrixot, amelyek szorzata sokkal kevesebb paraméterrel rendelkezik). Ez jelentős csökkenést eredményez a tanítható paraméterek számában és a VRAM-igényben, miközben megőrzi a teljes finomhangolás minőségének nagy részét.

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

A **QLoRA** egyesíti a **4 bites kvantálást** a **LoRA**-val. Az alapmodell 4 biten kerül betöltésre (jelentős memóriamegtakarítás mellett), és csak a LoRA adapterek tanítása történik nagyobb pontossággal. Így megkapod a LoRA paraméterhatékonyságát, valamint jóval alacsonyabb VRAM-igényt, kis minőségi kompromisszum árán a teljes pontosságú LoRA-hoz képest. Vedd figyelembe, hogy a 4 bites kvantálás numerikus instabilitásokat (veszteségkiugrásokat vagy NaN-okat) okozhat, ezért a felhasználók gyakran inkább a **LoRA**-t részesítik előnyben, ha elegendő VRAM áll rendelkezésre.

```python
Base Model (4-bit):  10GB  ← Frozen, quantized
LoRA Adapters (BF16): 2GB  ← Trainable, full precision
Total: 12GB (vs 40GB full precision)
```

> **Megjegyzés**: Az olyan MXFP4 alapmodellekhez, mint az `openai/gpt-oss-20b`, a **LoRA** (`train_lora.py`) használatát javasoljuk a QLoRA helyett. A QLoRA szkript `bitsandbytes` 4 bites útvonala jellemzően BF16-ra dekvantálja az MXFP4 súlyokat, így a futtatás a standard LoRA-hoz hasonlóan viselkedik. A natív MXFP4-hez forrásból épített `bitsandbytes`-ra, valamint egy megfelelő Transformers/Triton/kernels verzióköteg-re van szükség. Lásd a [Transformers MXFP4 dokumentációt](https://huggingface.co/docs/transformers/main/en/quantization/mxfp4).

---
### 2. Válassza ki a módszert

| Módszer | Memória | Sebesség | Minőség | Legjobban ajánlott |
|--------|--------|-------|---------|----------|
| **QLoRA** (csak Linux) | 12-16GB | Leggyorsabb | 90-95% | Alacsony memóriahasználat |
| **LoRA** | 24-32GB | Gyors | 95-98% | Kiegyensúlyozott megközelítés |
| **Full** | 80GB+ | Leglassabb | 100% | Maximális minőség |

### 3. Futtassa a tanítást

**Adathalmaz és a modell tanulási folyamata**  
A szkriptek az adathalmazt csevegési példákká alakítják. Például a QLoRA szkript az **Abirate/english_quotes** adathalmazt használja: minden példa egy felhasználó–asszisztens párrá válik, például:

- **Felhasználó:** „Mondj egy idézetet erről: &lt;tag&gt;”
- **Asszisztens:** „&lt;idézet&gt; – &lt;szerző&gt;”

A finomhangolás megtanítja a modellt arra, hogy válaszoljon az adott témával kapcsolatos idézeteket kérő promptokra, és ezeket a következő formátumban adja vissza: `<idézet szövege> - <szerző>`. A LoRA és a teljes finomhangolási szkriptek a **databricks/databricks-dolly-15k** adathalmazt használják (általános utasítás/válasz párok), így a pontos feladat szkriptenként eltérő; az alapgondolat azonban ugyanaz - a modell adaptálása a kiválasztott adathalmazhoz és formátumhoz.

Az alábbiakban összefoglaljuk az elérhető tanítási módszereket. Minden módszer hivatkozik a saját szkriptjére, és rövid leírást ad a megfelelő megközelítés kiválasztásához.

| Szkript                           | Módszer            | Leírás                                                                                                         | Jellemző VRAM | Ajánlott                                 |
|-----------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------|--------------|-------------------------------------------------|
| [`train_lora.py`](assets/train_lora.py)                 | **LoRA**          | Kis adapter mátrixokat tanít, miközben az alapmodellt befagyasztja. 3–5x gyorsabb; ~95–98%-os teljes minőség.                         | 24–32GB      | Haladó felhasználók; több adapter; nagyobb VRAM    |
| [`train_qlora.py`](assets/train_qlora.py)  *(csak Linux)*             | **QLoRA**       | 4 bites kvantálás + LoRA adapterek. Legalacsonyabb memóriahasználat, leggyorsabb, kis minőségi kompromisszum. A `bitsandbytes` szükséges (csak Linux).                            | 12–16GB      | Legtöbb felhasználó; gyors kísérletek; korlátozott VRAM      |
| [`train_full_finetuning.py`](assets/train_full_finetuning.py) | **Teljes finomhangolás** | Az összes modellparamétert frissíti. Maximális minőség; legnagyobb memória- és számítási igény.                                    | 40GB+      | Maximális minőség; kutatás; nagy VRAM           |

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
> **Megjegyzés:** A teljes finomhangoláshoz (`train_full_finetuning.py`) több mint 64GB rendszermemóriára lehet szükség, és előfordulhat, hogy ezen az eszközön nem kivitelezhető. Ehelyett fontolja meg a LoRA vagy QLoRA használatát.
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés:** A teljes finomhangoláshoz (`train_full_finetuning.py`) több mint 64GB rendszermemóriára lehet szükség, és előfordulhat, hogy ezen az eszközön nem kivitelezhető. Ehelyett fontolja meg a LoRA használatát.
<!-- @os:end -->
<!-- @device:end -->

Egyszerűen válassza ki a kívánt `Training method` értéket, töltse le a megfelelő szkriptet, majd futtassa a parancsot, miközben a virtuális környezet aktív marad: 

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

### A LoRA adapter egyesítése az alapmodellel

```python
# Merge LoRA/QLoRA adapter weights into the base model for standalone inference
merged_model = model.merge_and_unload()
merged_model.save_pretrained("gemma-3-4b-merged")
tokenizer.save_pretrained("gemma-3-4b-merged")
```

**Megjegyzés:**  
- Győződjön meg róla, hogy a modell könyvtárának neve (`output-gemma-3-4b-it-full`, `output-gpt-oss-20b-qlora`) megegyezik a tanítás tényleges kimeneti mappájával.  
- Ha QLoRA helyett LoRA-t használt, egyszerűen cserélje ki a megfelelő elérési utat.  
- Egyes Gemma modellek esetén meg kell adni a `trust_remote_code=True` beállítást a `from_pretrained` függvényben; adja hozzá, ha ezzel kapcsolatos figyelmeztetést lát.

További egyedi beállításokért (padding tokenek, eszköz stb.) tekintse meg a tanításhoz használt szkriptet.

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

**Adathalmaz-formátum helyi JSON/JSONL fájlhoz:**

Ennek a módszernek a használatakor győződjön meg róla, hogy a JSON fájljai megfelelően strukturáltak, hogy elkerülje az elemzési hibákat. 

A következő irányelveket kell betartani:
* **Fájlformázás:** A JSON fájlokat integrált fejlesztői környezetben (IDE) kell formázni a megfelelő szerkezet és szintaxis biztosítása érdekében.
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

A Hugging Face adathalmazainak használatakor győződjön meg róla, hogy az adathalmazok megfelelően strukturáltak a zökkenőmentes integráció érdekében. 

A következő irányelveket érdemes követni:
* **Utasítás-válasz pár:** Olyan adathalmazokra összpontosítson, amelyek tartalmaznak egy `instruction-response` párt. Ez a szerkezet elengedhetetlen a kívánt működéshez.
* **Egyedi kulcs módosítása:** Ha az adathalmaz nem felel meg az `instruction-response` szerkezetnek, lehetőség van a `format_instruction()` függvény módosítására. Ez lehetővé teszi az adott kulcsok igény szerinti figyelembevételét.

Példa a módosításra: Abban az esetben, ha az adathalmaz kimenetét módosítani kell, a format_instruction() függvényen belül a válasz részt az igényeinek megfelelően módosíthatja.
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

Ahhoz, hogy a szkript CSV fájlformátumot használjon, győződjön meg róla, hogy a CSV fájl tartalmaz `instruction` és `response` nevű oszlopokat. 
```csv
instruction,response
"Your first instruction here","Expected response here"
"Your second instruction here","Expected response here"
```

### Tanítási paraméterek beállítása

Szerkessze a tanítási szkriptet, és módosítsa a változókat a céljainak megfelelően: **tanulási ráta** (`LR`), **epochok** (`EPOCHS`), **köteg méret** (`BATCH_SIZE`), **gradiens akkumuláció** (`GRAD_ACCUM_STEPS`), valamint LoRA/QLoRA esetén a **rang** (`LORA_R`). Gyorsabb futtatáshoz használjon kevesebb epochot és magasabb tanulási rátát (LR); jobb minőséghez használjon több epochot és alacsonyabb LR-t. Csökkentse a köteg méretét vagy a szekvencia hosszát, ha memóriahiány hibákat tapasztal.
### Memóriaoptimalizálási tippek

Ha memóriahiány-hibákkal találkozik:

**1. Csökkentse a kötegméretet (Batch Size):**
```python
BATCH_SIZE = 1
GRAD_ACCUM_STEPS = 16  # Maintain effective batch size
```

**2. Csökkentse a szekvenciahosszt:**
```python
max_seq_length=256  # Instead of 512
```

**3. Használjon agresszívebb kvantálást:**
```
Full → LoRA → QLoRA
```

**4. Engedélyezze a Gradient Checkpointing funkciót (csak teljes finomhangolásnál):**
```python
model.gradient_checkpointing_enable()
```

---

## Monitorozás és hibakeresés

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

A betanítási szkriptben állítsa be a `report_to="wandb"` értéket, és opcionálisan a `run_name="your-experiment-name"` értéket a trainer konfigurációjában. Ha nem szeretné használni a Wandb-ot, hagyja a `report_to` értékét az alapértelmezett beállításon, vagy állítsa `"none"` értékre.

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

#### Lassú betanítás

**Megoldás:** Növelje a kötegméretet, ha a memória megengedi
```python
BATCH_SIZE = 8
```
## Következő lépések

A sikeres finomhangolás után fontolja meg a következő lépéseket, hogy még többet hozzon ki a modelljéből:

1. **Értékelje** alaposan a modellt elkülönített tesztadatokon, hogy mérje az általánosítóképességet, és elkerülje a túltanulást.
2. **Kísérletezzen** különböző hiperparaméter-értékekkel a jobb pontosság, sebesség és memóriahasználat közötti egyensúly érdekében.
3. **Kövesse nyomon** az összes kísérletét (és a hozzájuk tartozó metrikákat) a Weights & Biases segítségével a reprodukálható kutatás érdekében.
4. **Próbálja ki** a betanítást saját egyedi adathalmazokon, hogy a modellt kifejezetten az Ön felhasználási esetéhez igazítsa.
5. **Alkalmazza** a finomhangolt modellt gyors következtetéshez olyan hatékony háttérrendszerek segítségével, mint a vLLM, kompatibilis hardveren.
6. **Fedezzen fel** fejlett technikákat, beleértve a prompt engineeringet, a vegyes pontosságot és a hosszabb szekvenciahosszokat.
7. **Tanítson be** több LoRA adaptert különböző feladatokhoz vagy területekhez, és szükség szerint cserélje őket.

---