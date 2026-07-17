<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Áttekintés

Ez a playbook bemutatja, hogyan lehet egy nyelvi modellt helyileg finomhangolni Unsloth segítségével AMD hardveren.

Egy rövid Felügyelt Finomhangolási (SFT) példát használ LoRA adapterekkel az `unsloth/gemma-4-E4B-it` modellen, az `mlabonne/FineTome-100k` adatkészlet egy részhalmazát alkalmazva. A cél egy egyszerű, végponttól végpontig terjedő munkafolyamat bemutatása, amely lefedi a beállítást, a tanítást, a következtetést és a finomhangolt eredmény mentését.

A példa praktikus és könnyen módosítható, így kiindulópontként használhatja saját adatkészleteihez és modelljeihez.

## Mit fog megtanulni

- Hogyan állítsa be az Unsloth környezetet
- Hogyan finomhangolja az LLM-et SFT segítségével Unsloth-tal
- Hogyan mentse el a finomhangolt eredményt helyi tárolóba

<!-- @device:halo,stx,krk -->
> **Megjegyzés:** Az ebben a playbookban szereplő finomhangolási technikákhoz legalább 24 GB GPU memória és 32 GB rendszer RAM szükséges.
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Megjegyzés:** Az ebben a playbookban szereplő finomhangolási technikákhoz legalább 24 GB GPU memória és 32 GB rendszer RAM szükséges.
<!-- @os:end -->

<!-- @os:linux -->
> **Megjegyzés:** Az ebben a playbookban szereplő finomhangolási technikákhoz legalább 24 GB **dedikált** GPU memória és 32 GB rendszer RAM szükséges.
<!-- @os:end -->
<!-- @device:end -->

## Miért Unsloth?

Az Unsloth megkönnyíti az LLM finomhangolását helyi hardveren azáltal, hogy csökkenti a memóriahasználatot és felgyorsítja a tanítást a szokásos beállításhoz képest.

Ebben a playbookban az Unsloth-t **LoRA-alapú SFT**-vel együtt használjuk. Ez azt jelenti, hogy az alapmodell nagyrészt befagyasztva marad, miközben egy sokkal kisebb adapter-súlykészlet kerül betanításra. Ez jól illeszkedik a helyi fejlesztéshez, mivel könnyebb a teljes finomhangolásnál, és gyorsabb az iteráció.

Az Unsloth más tanítási megközelítéseket is támogat, beleértve a QLoRA-t és a megerősítéses tanulási munkafolyamatokat. Ez a playbook a legegyszerűbb útra összpontosít először: egy kis LoRA finomhangolási példára, amelyet a felhasználók futtathatnak, megérthetnek és kiterjeszthetnek.

## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése
> **Megjegyzés**: Ha a VS Code nincs telepítve, a Ryzen AI Developer Center segítségével telepítheti.

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftver-előfeltételek telepítése

### Virtuális környezet létrehozása

<!-- @os:linux -->
<!-- @device:halo_box -->
Nyisson meg egy terminált, és hozzon létre egy venv-et AMD ROCm™ szoftverrel és PyTorch-csal előre telepítve:
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
**Adjon hozzáférést a felhasználójának a GPU eszközökhöz** (a hatályba lépéshez jelentkezzen ki, majd vissza):

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

> **Megjegyzés:** Importálás során az Unsloth opcionális `bitsandbytes` gyorsítási útvonalakat vizsgálhat. Egyes ROCm verziókon megjelenhet egy üzenet, például: `bitsandbytes library load error: Configured ROCm binary not found`. Ez a playbook szabványos LoRA finomhangolást használ `optim="adamw_torch"` beállítással, így nem támaszkodunk a `bitsandbytes` optimalizálóra vagy a 4-bites QLoRA-ra. Ez az üzenet biztonságosan figyelmen kívül hagyható.

<!-- @os:windows -->
> **Megjegyzés:** Windows ROCm esetén az Unsloth indításkor több figyelmeztetést is kiír — lásd az alábbi [Ismert figyelmeztetések](#known-warnings) részt. Ezek mind biztonságosan figyelmen kívül hagyhatók; a tanítás helyesen működik.
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

## Az Unsloth finomhangolási szkript letöltése

Az egyes lépések manuális végrehajtása helyett ez a playbook egy tiszta, végponttól végpontig terjedő szkriptet biztosít itt: [test_unsloth.py](assets/test_unsloth.py).

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

A playbook hátralévő része fogalmilag végigmegy a szkript minden egyes főbb lépésén.

## Hogyan működik

A test_unsloth.py szkript a következő lépéseket hajtja végre:
* **Modell betöltése**: Betölti az unsloth/gemma-4-E4B-it modellt a FastModel segítségével.
* **Adatok előkészítése**: Szabványosítja az adatkészletet (pl. FineTome-100k) és alkalmazza a Gemma-4 chat sablont.
* **LoRA alkalmazása**: Adaptereket ad a nyelvi, figyelmi és MLP modulokhoz a hatékony tanítás érdekében.
* **Tanítás**: SFTTrainer-t használ csak-válasz veszteségmaszkolással.
* **Következtetés**: Gyors generálási tesztet futtat a teljesítmény ellenőrzéséhez.
* **Mentés**: Helyileg exportálja a LoRA adaptereket.

## Főbb konfiguráció

A következő konstansokat módosíthatja a futtatás testreszabásához:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Az Unsloth üdvözlőüzenetének és a modellsúlyok betöltésekor megjelenő kimenetének példája:

![alt text](assets/welcome.png)

## Adatkészlet előkészítése

A következő részhalmazt használjuk:
```text
mlabonne/FineTome-100k
```
Az adatkészlet:
* Chat formátumba konvertálva
* A Gemma-4 chat sablon segítségével feldolgozva
* Megtisztítva a duplikált BOS tokenek eltávolításával

## A modell tanítása

A szkript egy rövid tanítási bemutatót futtat a következő paraméterekkel:
- ~50 lépés
- Kis kötegméret
- Gradiens akkumuláció

A tanítás során az alábbi naplókat fogja látni:

![alt text](assets/training.png)


## Mentés és telepítés

### Helyi mentés (LoRA)

A szkript automatikusan menti a LoRA adaptereket az OUTPUT_DIR könyvtárba.
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

### Összevont modell mentése (vLLM-hez)

<!-- @os:windows -->
> **Megjegyzés:** A vLLM nem támogatja a Windowst. A finomhangolt modell Windows rendszeren való telepítéséhez használja a llama.cpp-t (lásd az alábbi [GGUF exportálása](#export-gguf-for-llamacpp) részt), vagy vigye át az összevont modellt egy vLLM-et futtató Linux gépre.
<!-- @os:end -->

<!-- @os:linux -->
A vLLM-mel való telepítéshez vonja össze az adaptereket egy teljes modellbe:
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

Konvertálás közvetlenül GGUF formátumba helyi következtetéshez:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Ismert figyelmeztetések

Ezeket a figyelmeztetéseket az Unsloth indításkor nyomtatja ki Windows ROCm rendszeren, és mindegyik biztonságosan figyelmen kívül hagyható:

| Figyelmeztetés | Ok | Biztonságosan figyelmen kívül hagyható? |
|---|---|---|
| `bitsandbytes library load error` | A bitsandbytes-nak nincs Windows ROCm buildje | Igen — ez a playbook `adamw_torch`-t használ, nem bnb-t |
| `No ROCm platform found for torch.distributed` | A Windows-on futó ROCm nem támogatja az elosztott tanítást | Igen — az egygépes GPU tanítás nem érintett |
| `Unsloth: WARNING! You are using an unsupported platform` | Az Unsloth jelzi a nem Linux buildeket | Igen — a Windows ROCm működik egygépes GPU SFT esetén |
| `triton is not available` | A Triton-nak nincs Windows buildje | Igen — az Unsloth visszaesik PyTorch kernelekre |

A tanítás ezek ellenére helyesen fog lefutni.
<!-- @os:end -->

## Következő lépések
- Próbálja ki az [Unsloth Studio](https://unsloth.ai/docs/new/studio) alkalmazást, az Unsloth intuitív grafikus felületét
- Tanítson saját specifikus adatkészleteken
- Próbáljon finomhangolni különböző hiperparaméterekkel
- Telepítse vLLM vagy llama.cpp segítségével
- Próbálja ki a QLoRA-t alacsonyabb memóriaigényű beállításhoz

## Erőforrások

Az alábbiakban további erőforrások találhatók az Unsloth és a finomhangolás megismeréséhez:

* [Unsloth dokumentáció](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth finomhangolási útmutató](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)