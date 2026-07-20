<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->

> [!IMPORTANT]
> Ez a útmutató olyan speciális címkéket használ, amelyeket a GitHub nem tud megjeleníteni. Az tartalom megfelelő előnézetéhez látogasson el a(z) [amd.com/playbooks](https://amd.com/playbooks) oldalra.
<!-- @github-only:end -->

## Áttekintés

Ez az útmutató bemutatja, hogyan lehet egy nyelvi modellt helyben finomhangolni Unsloth segítségével AMD hardveren.

Egy rövid felügyelt finomhangolási (Supervised Fine-Tuning, SFT) példát használ LoRA adapterekkel a `unsloth/gemma-4-E4B-it` modellen, a `mlabonne/FineTome-100k` adathalmaz egy részhalmazát felhasználva. A cél egy egyszerű, végponttól végpontig terjedő munkafolyamat bemutatása, amely lefedi a beállítást, a tanítást, a következtetést és a finomhangolt eredmény mentését.

A példa gyakorlati és könnyen módosítható kialakítású, így kiindulópontként használható saját adathalmazaihoz és modelljeihez.

## Amit meg fog tanulni

- Hogyan állítsa be az Unsloth környezetet
- Hogyan finomhangoljon egy LLM-et SFT segítségével az Unsloth használatával
- Hogyan mentse el a finomhangolt eredményt helyi tárhelyre

<!-- @device:halo,stx,krk -->
> **Megjegyzés:** Az ebben az útmutatóban szereplő finomhangolási technikákhoz legalább 24 GB GPU-memória és 32 GB rendszer-RAM szükséges.
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Megjegyzés:** Az ebben az útmutatóban szereplő finomhangolási technikákhoz legalább 24 GB GPU-memória és 32 GB rendszer-RAM szükséges.
<!-- @os:end -->

<!-- @os:linux -->
> **Megjegyzés:** Az ebben az útmutatóban szereplő finomhangolási technikákhoz legalább 24 GB **dedikált** GPU-memória és 32 GB rendszer-RAM szükséges.
<!-- @os:end -->
<!-- @device:end -->

## Miért az Unsloth?

Az Unsloth megkönnyíti az LLM-ek finomhangolását helyi hardveren azáltal, hogy csökkenti a memóriahasználatot és felgyorsítja a tanítást a szokásos beállításokhoz képest.

Ebben az útmutatóban az Unsloth-ot **LoRA-alapú SFT**-vel együtt használjuk. Ez azt jelenti, hogy az alapmodell nagyrészt lefagyasztva marad, miközben egy jóval kisebb adapter súlykészletet tanítunk. Ez jól illeszkedik a helyi fejlesztéshez, mivel könnyebb, mint a teljes finomhangolás, és gyorsabban lehet vele iterálni.

Az Unsloth más tanítási megközelítéseket is támogat, beleértve a QLoRA-t és a megerősítéses tanulási munkafolyamatokat is. Ez az útmutató először a legegyszerűbb útra összpontosít: egy kis LoRA finomhangolási példára, amelyet a felhasználók futtathatnak, megérthetnek és bővíthetnek.

## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése
> **Megjegyzés**: Ha a VS Code nincs telepítve, telepítheti a Ryzen AI Developer Center segítségével.

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftveres előfeltételek telepítése

### Virtuális környezet létrehozása

<!-- @os:linux -->
<!-- @device:halo_box -->
Nyisson meg egy terminált, és hozzon létre egy venv-et, amelyben már telepítve van az AMD ROCm™ szoftver és a PyTorch:
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
python3 -m venv unsloth-env --system-site-packages
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Adjon hozzáférést felhasználójának a GPU-eszközökhöz** (a hatásbalépéshez jelentkezzen ki, majd vissza):

```bash
sudo usermod -aG render,video $LOGNAME
```

Nyisson meg egy terminált, és hozzon létre egy venv-et:
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv unsloth-env
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **Megjegyzés:** Windows esetén Python 3.13 szükséges.

<!-- @device:halo_box -->
Nyisson meg egy PowerShell terminált, és hozzon létre egy virtuális környezetet:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Nyisson meg egy PowerShell terminált, és hozzon létre egy virtuális környezetet:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Alapvető függőségek telepítése
<!-- @require:pytorch,driver -->

<!-- @test:id=verify-torch-env timeout=300 hidden=True setup=activate-venv -->
```python
import sys
import torch

print(f"Python executable: {sys.executable}")
print(f"PyTorch version: {torch.__version__}")
print(f"torch.cuda.is_available(): {torch.cuda.is_available()}")

if not torch.cuda.is_available():
    raise SystemExit("FAIL: ROCm-enabled PyTorch is not visible in this venv")

print("PASS: ROCm-enabled PyTorch is visible")
```
<!-- @test:end -->

### További függőségek

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Megjegyzés:** Importálás közben az Unsloth megpróbálhatja tesztelni az opcionális `bitsandbytes` gyorsítási útvonalakat. Egyes ROCm verziók esetén megjelenhet egy olyan üzenet, mint például: `bitsandbytes library load error: Configured ROCm binary not found`. Ez az útmutató szabványos LoRA finomhangolást használ `optim="adamw_torch"` beállítással, így nem támaszkodunk a `bitsandbytes` optimalizálóra vagy a 4 bites QLoRA-ra. Ez az üzenet nyugodtan figyelmen kívül hagyható.

<!-- @os:windows -->
> **Megjegyzés:** Windows ROCm esetén az Unsloth induláskor több figyelmeztetést is kiír – lásd a lenti [Ismert figyelmeztetések](#known-warnings) részt. Ezek mind nyugodtan figyelmen kívül hagyhatók; a tanítás megfelelően működik.
<!-- @os:end -->

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
```python
import unsloth
import torch
from datasets import load_dataset
from transformers import TextStreamer
from unsloth import FastModel
from unsloth.chat_templates import (
    get_chat_template,
    standardize_data_formats,
    train_on_responses_only,
)
from trl import SFTTrainer, SFTConfig

print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print("PASS: All required imports succeeded")
```
<!-- @test:end -->

## Az Unsloth finomhangoló szkript letöltése

Ahelyett, hogy minden lépést manuálisan hajtana végre, ez az útmutató egy tiszta, végponttól végpontig terjedő szkriptet biztosít itt: [test_unsloth.py](assets/test_unsloth.py).

Futtassa a következő kódot a szkript végrehajtásához:

```bash
python test_unsloth.py
```

<!-- @test:id=verify-script timeout=60 hidden=True -->
```python
import os
import sys
import ast

scripts = ["test_unsloth.py", "test_unsloth_ci.py"]
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing script: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

for script in scripts:
    with open(script, "r", encoding="utf-8") as f:
        ast.parse(f.read(), filename=script)
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=quick-train-unsloth timeout=2400 hidden=True setup=activate-venv -->
```bash
python test_unsloth_ci.py
```
<!-- @test:end -->

Az útmutató további része koncepcionálisan végigvezeti a szkript minden fő lépését.

## Hogyan működik

A test_unsloth.py szkript a következő lépéseket hajtja végre:
* **Modell betöltése**: Betölti az unsloth/gemma-4-E4B-it modellt a FastModel segítségével.
* **Adatok előkészítése**: Szabványosítja az adathalmazt (pl. FineTome-100k), és alkalmazza a Gemma-4 csevegési sablont.
* **LoRA alkalmazása**: Adaptereket ad a nyelvi, figyelem- és MLP-modulokhoz a hatékony tanítás érdekében.
* **Tanítás**: SFTTrainer-t használ csak-válasz veszteségmaszkolással.
* **Következtetés**: Egy gyors generálási tesztet futtat a teljesítmény ellenőrzésére.
* **Mentés**: Exportálja a LoRA adaptereket helyben.

## Kulcskonfiguráció

A futtatás testreszabásához módosíthatja a következő konstansokat:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Példa az Unsloth üdvözlő üzenetére és a modellsúlyok betöltésekor megjelenő kimenetre:

![alt text](assets/welcome.png)

## Adathalmaz előkészítése

A következő részhalmazát használjuk:
```text
mlabonne/FineTome-100k
```
Az adathalmaz: 
* Csevegési formátumra alakítva
* A Gemma-4 csevegési sablon segítségével feldolgozva
* Megtisztítva az ismétlődő BOS tokenektől

## A modell tanítása

A szkript egy rövid tanítási bemutatót futtat, a következő paraméterekkel:
- ~50 lépés
- Kis kötegméret
- Gradiens akkumuláció

A tanítás során a következőhöz hasonló naplókat fog látni:

![alt text](assets/training.png)


## Mentés és üzembe helyezés

### Helyi mentés (LoRA)

A szkript automatikusan elmenti a LoRA adaptereket az OUTPUT_DIR könyvtárba.
```python
model.save_pretrained("gemma_4_lora")  
tokenizer.save_pretrained("gemma_4_lora")
```

<!-- @test:id=verify-unsloth-lora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_lora_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = (
    glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) +
    glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
)
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: Unsloth LoRA output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end -->

### Egyesített modell mentése (vLLM-hez) 

<!-- @os:windows -->
> **Megjegyzés:** A vLLM nem támogatja a Windows-t. A finomhangolt modell Windows alatti üzembe helyezéséhez használja a llama.cpp-t (lásd a lenti [GGUF exportálása](#export-gguf-for-llamacpp) részt), vagy vigye át az egyesített modellt egy Linux gépre, amelyen vLLM fut.
<!-- @os:end -->

<!-- @os:linux -->
A vLLM-mel történő üzembe helyezéshez egyesítse az adaptereket egy teljes modellbe:
```python
model.save_pretrained_merged("gemma-4-finetune", tokenizer)
```
<!-- @os:end -->

<!-- @test:id=verify-unsloth-merged-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_merged_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing merged model directory: {out_dir}")
    sys.exit(1)

required = [
    "config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required merged files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Merged model output looks correct")
```
<!-- @test:end -->

### GGUF exportálása (llama.cpp-hez)

Konvertálja közvetlenül GGUF formátumra a helyi következtetéshez:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Ismert figyelmeztetések

Ezeket a figyelmeztetéseket az Unsloth nyomtatja ki induláskor Windows ROCm alatt, és mindegyik biztonságosan figyelmen kívül hagyható:

| Figyelmeztetés | Ok | Biztonságosan figyelmen kívül hagyható? |
|---|---|---|
| `bitsandbytes library load error` | A bitsandbytes-nak nincs Windows ROCm buildje | Igen — ez a playbook az `adamw_torch`-ot használja, nem a bnb-t |
| `No ROCm platform found for torch.distributed` | A Windows-on futó ROCm nem támogatja az elosztott tanítást | Igen — az egy-GPU-s tanítást ez nem érinti |
| `Unsloth: WARNING! You are using an unsupported platform` | Az Unsloth jelzi a nem Linux buildeket | Igen — a Windows ROCm működik egy-GPU-s SFT esetén |
| `triton is not available` | A Tritonnak nincs Windows buildje | Igen — az Unsloth visszaáll a PyTorch kernelekre |

A tanítás ezen figyelmeztetések ellenére is helyesen fog lezajlani.
<!-- @os:end -->

## Következő lépések
- Próbáld ki az [Unsloth Studio](https://unsloth.ai/docs/new/studio) programot, egy intuitív felhasználói felületet az Unslothhoz
- Taníts a saját, egyedi adathalmazaidon
- Próbálkozz a finomhangolással eltérő hiperparaméterekkel
- Telepítsd vLLM-mel vagy llama.cpp-vel
- Próbáld ki a QLoRA-t egy kisebb memóriaigényű beállításhoz

## Erőforrások

Az alábbiakban további forrásokat találsz, ha többet szeretnél megtudni az Unslothról és a finomhangolásról:

* [Unsloth dokumentáció](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth finomhangolási útmutató](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)