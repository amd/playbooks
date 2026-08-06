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

Ez a playbook bemutatja, hogyan lehet egy nyelvi modellt lokálisan finomhangolni Unsloth segítségével AMD hardveren.

Egy rövid felügyelt finomhangolási (Supervised Fine-Tuning, SFT) példát használ LoRA adapterekkel a `unsloth/gemma-4-E4B-it` modellen, a `mlabonne/FineTome-100k` adathalmaz egy részhalmazát felhasználva. A cél egy egyszerű, végponttól végpontig tartó munkafolyamat bemutatása, amely lefedi a beállítást, a betanítást, a következtetést (inference) és a finomhangolt eredmény mentését.

A példa gyakorlati és könnyen módosítható, így kiindulópontként használhatja saját adathalmazaihoz és modelljeihez.

## Amit meg fog tanulni

- Hogyan állítsa be az Unsloth környezetet
- Hogyan finomhangoljon egy LLM-et SFT segítségével Unsloth használatával
- Hogyan mentse el a finomhangolt eredményt helyi tárhelyre

<!-- @device:halo,stx,krk -->
> **Megjegyzés:** Az ebben a playbookban szereplő finomhangolási technikák legalább **64 GB rendszer RAM-ot** igényelnek, amelyből legalább **24 GB-nak elérhetőnek kell lennie a GPU számára** (a 24 GB a 64 GB részét képezi, nem azon felül értendő).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Megjegyzés:** Az ebben a playbookban szereplő finomhangolási technikák legalább **24 GB teljes GPU memóriát** és **32 GB rendszer RAM-ot** igényelnek.
> - Windows rendszeren a teljes GPU memória a videokártya dedikált VRAM-ját és a megosztott GPU memóriát (amelyet a rendszer RAM-jából kölcsönöz) is tartalmazza.
> - Ezért a 24 GB-nál kevesebb dedikált VRAM-mal rendelkező kártyák is képesek futtatni ezt a playbookot, mivel a megosztott GPU memóriával pótolják a különbséget.
<!-- @os:end -->

<!-- @os:linux -->
> **Megjegyzés:** Az ebben a playbookban szereplő finomhangolási technikák legalább **24 GB dedikált GPU memóriával** és **32 GB rendszer RAM-mal** rendelkező videokártyát igényelnek.
> - Linux rendszeren a betanítás teljes egészében a videokártya dedikált VRAM-jában fut.
> - Nem áll át megosztott GPU memóriára (rendszer RAM-ra), ha a VRAM elfogy.
> - A 24 GB-nál kevesebb dedikált VRAM-mal rendelkező kártyák a betanítás során kifogynak a memóriából Linux rendszeren, még akkor is, ha a rendszerben bőven van RAM.
<!-- @os:end -->
<!-- @device:end -->

## Miért az Unsloth?

Az Unsloth megkönnyíti az LLM-ek finomhangolásának futtatását helyi hardveren azáltal, hogy csökkenti a memóriahasználatot és felgyorsítja a betanítást egy szabványos beállításhoz képest.

Ebben a playbookban az Unslothot **LoRA-alapú SFT**-vel együtt használjuk. Ez azt jelenti, hogy az alapmodell nagyrészt befagyasztott marad, miközben egy sokkal kisebb adapter-súlykészletet tanítunk. Ez jól illeszkedik a helyi fejlesztéshez, mivel könnyebb, mint a teljes finomhangolás, és gyorsabban lehet vele iterálni.

Az Unsloth más betanítási megközelítéseket is támogat, beleértve a QLoRA-t és a megerősítéses tanulási munkafolyamatokat. Ez a playbook a legegyszerűbb útra összpontosít elsőként: egy kis LoRA finomhangolási példára, amelyet a felhasználók futtathatnak, megérthetnek és bővíthetnek.

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
**Adjon felhasználójának hozzáférést a GPU-eszközökhöz** (a hatás érvényesítéséhez jelentkezzen ki, majd vissza):

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
> **Megjegyzés:** Windows rendszeren a Python 3.13 szükséges.

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
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Megjegyzés:** Az importálás során az Unsloth opcionálisan próbálhatja a `bitsandbytes` gyorsítási útvonalakat. Egyes ROCm verziók esetén megjelenhet egy olyan üzenet, mint a `bitsandbytes library load error: Configured ROCm binary not found`. Ez a playbook szabványos LoRA finomhangolást használ `optim="adamw_torch"` beállítással, így nem támaszkodunk a `bitsandbytes` optimalizálóra vagy a 4 bites QLoRA-ra. Ez az üzenet nyugodtan figyelmen kívül hagyható.

<!-- @os:windows -->
> **Megjegyzés:** Windows ROCm alatt az Unsloth indításkor több figyelmeztetést is kiír — lásd az alábbi [Ismert figyelmeztetések](#known-warnings) részt. Ezek mindegyike nyugodtan figyelmen kívül hagyható; a betanítás megfelelően működik.
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

Ahelyett, hogy minden lépést manuálisan hajtana végre, ez a playbook egy tiszta, végponttól végpontig tartó szkriptet biztosít itt: [test_unsloth.py](assets/test_unsloth.py).

A szkript futtatásához hajtsa végre a következő kódot:

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

A playbook hátralévő része koncepcionálisan végigmegy a szkript minden fő lépésén.

## Hogyan működik

A test_unsloth.py szkript a következő lépéseket hajtja végre:
* **Modell betöltése**: Betölti a unsloth/gemma-4-E4B-it modellt a FastModel segítségével.
* **Adatok előkészítése**: Szabványosítja az adathalmazt (pl. FineTome-100k), és alkalmazza a Gemma-4 chat sablont.
* **LoRA alkalmazása**: Adaptereket ad hozzá a nyelvi, figyelmi (attention) és MLP modulokhoz a hatékony betanítás érdekében.
* **Betanítás**: SFTTrainer-t használ, válasz-only veszteségmaszkolással.
* **Következtetés (Inference)**: Egy gyors generálási tesztet futtat a teljesítmény ellenőrzésére.
* **Mentés**: Exportálja a LoRA adaptereket helyi tárhelyre.

## Kulcskonfiguráció

A futtatás testreszabásához a következő konstansokat módosíthatja:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Példa az Unsloth üdvözlő üzenetére és a modellsúlyok betöltésekor megjelenő kimenetre:

![alt text](assets/welcome.png)

## Adathalmaz előkészítése

A következő adathalmaz egy részhalmazát használjuk:
```text
mlabonne/FineTome-100k
```
Az adathalmaz:
* Chat formátumba konvertálva
* A Gemma-4 chat sablon segítségével feldolgozva
* Megtisztítva a duplikált BOS tokenektől

## A modell betanítása

A szkript egy rövid betanítási demót futtat, a következő paraméterekkel:
- ~50 lépés
- Kis kötegméret (batch size)
- Gradiens akkumuláció

A betanítás során az alábbihoz hasonló naplókat fog látni:

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
> **Megjegyzés:** A vLLM nem támogatja a Windows rendszert. Ha a finomhangolt modellt Windows alatt szeretné üzembe helyezni, használja a llama.cpp-t (lásd az alábbi [GGUF exportálása](#export-gguf-for-llamacpp) szakaszt), vagy vigye át az egyesített modellt egy vLLM-et futtató Linux gépre.
<!-- @os:end -->

<!-- @os:linux -->
A vLLM-mel történő üzembe helyezéshez egyesítse az adaptereket egy teljes modellé:
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

Közvetlen konvertálás GGUF formátumba a helyi következtetéshez:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Ismert figyelmeztetések

Ezeket a figyelmeztetéseket az Unsloth jeleníti meg indításkor Windows ROCm rendszeren, és mindegyik biztonságosan figyelmen kívül hagyható:

| Figyelmeztetés | Ok | Biztonságosan figyelmen kívül hagyható? |
|---|---|---|
| `bitsandbytes library load error` | A bitsandbytes-hoz nincs Windows ROCm build | Igen — ez a playbook az `adamw_torch`-ot használja, nem a bnb-t |
| `No ROCm platform found for torch.distributed` | A ROCm Windowson nem támogatja az elosztott tanítást | Igen — az egy GPU-s tanítást ez nem érinti |
| `Unsloth: WARNING! You are using an unsupported platform` | Az Unsloth jelzi a nem Linux buildeket | Igen — a Windows ROCm működik egy GPU-s SFT esetén |
| `triton is not available` | A Tritonhoz nincs Windows build | Igen — az Unsloth ilyenkor a PyTorch kerneleket használja |

A tanítás ezen figyelmeztetések ellenére is helyesen zajlik le.
<!-- @os:end -->

## Következő lépések
- Próbálja ki az [Unsloth Studio](https://unsloth.ai/docs/new/studio) eszközt, egy intuitív felhasználói felületet az Unslothhoz
- Tanítson saját, egyedi adathalmazokon
- Próbálkozzon a finomhangolással különböző hiperparaméterekkel
- Helyezze üzembe vLLM-mel vagy llama.cpp-vel
- Próbálja ki a QLoRA-t egy alacsonyabb memóriaigényű beállításhoz

## Erőforrások

Az alábbiakban további erőforrásokat talál, ha többet szeretne megtudni az Unslothról és a finomhangolásról:

* [Unsloth dokumentáció](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth finomhangolási útmutató](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)