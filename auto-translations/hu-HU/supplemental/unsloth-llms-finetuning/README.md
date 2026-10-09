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

Ez a playbook bemutatja, hogyan lehet egy nyelvi modellt helyben finomhangolni az Unsloth segítségével AMD hardveren.

Egy rövid, felügyelt finomhangolási (Supervised Fine-Tuning, SFT) példát használ LoRA adapterekkel a `unsloth/gemma-4-E4B-it` modellen, a `mlabonne/FineTome-100k` adathalmaz egy részhalmazát felhasználva. A cél egy egyszerű, végponttól végpontig tartó munkafolyamat bemutatása, amely magában foglalja a beállítást, a tanítást, a következtetést és a finomhangolt eredmény mentését.

A példa gyakorlati és könnyen módosítható kialakítást kapott, így kiindulópontként használhatja saját adathalmazaihoz és modelljeihez.

## Mit fogsz megtanulni

- Hogyan állítsd be az Unsloth környezetet
- Hogyan hangolj finomra egy LLM-et SFT segítségével az Unsloth használatával
- Hogyan mentsd el a finomhangolt eredményt helyi tárhelyen

<!-- @device:halo,stx,krk -->
> **Megjegyzés:** Az ebben a playbookban szereplő finomhangolási technikák legalább **64 GB rendszermemóriát** igényelnek, amelyből legalább **24 GB-nak elérhetőnek kell lennie a GPU számára** (ez a 24 GB a 64 GB része, nem pedig azon felül értendő).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Megjegyzés:** Az ebben a playbookban szereplő finomhangolási technikák legalább **24 GB teljes GPU-memóriát** és **32 GB rendszermemóriát** igényelnek.
> - Windows rendszeren a teljes GPU-memória a grafikus kártya dedikált VRAM-ját és a megosztott GPU-memóriát (amelyet a rendszermemóriából kölcsönöz) foglalja magában.
> - Ezért a 24 GB-nál kevesebb dedikált VRAM-mal rendelkező kártyák is képesek futtatni ezt a playbookot, mivel a megosztott GPU-memória kiegészíti a különbséget.
<!-- @os:end -->

<!-- @os:linux -->
> **Megjegyzés:** Az ebben a playbookban szereplő finomhangolási technikák olyan grafikus kártyát igényelnek, amely legalább **24 GB dedikált GPU-memóriával** és **32 GB rendszermemóriával** rendelkezik.
> - Linux rendszeren a tanítás teljes egészében a grafikus kártya dedikált VRAM-jában fut.
> - Nem áll vissza megosztott GPU-memóriára (rendszermemóriára), ha elfogy a VRAM.
> - A 24 GB-nál kevesebb dedikált VRAM-mal rendelkező kártyák Linux rendszeren a tanítás közben kifogynak a memóriából, még akkor is, ha a rendszerben bőven van RAM.
<!-- @os:end -->
<!-- @device:end -->

## Miért az Unsloth?

Az Unsloth megkönnyíti az LLM-ek finomhangolását helyi hardveren azáltal, hogy csökkenti a memóriahasználatot, és felgyorsítja a tanítást egy szokásos beállításhoz képest.

Ebben a playbookban az Unsloth-ot **LoRA-alapú SFT-vel** együtt használjuk. Ez azt jelenti, hogy az alapmodell nagyrészt befagyasztva marad, miközben egy sokkal kisebb adaptersúly-készlet kerül tanításra. Ez jól illeszkedik a helyi fejlesztéshez, mivel könnyebb, mint a teljes finomhangolás, és gyorsabban lehet rajta iterálni.

Az Unsloth más tanítási megközelítéseket is támogat, például a QLoRA-t és a megerősítéses tanulási (reinforcement learning) munkafolyamatokat. Ez a playbook a legegyszerűbb útra összpontosít: egy kis LoRA finomhangolási példára, amelyet a felhasználók futtatni, megérteni és bővíteni tudnak.

<!-- @device:halo_box,halo,stx,krk -->
## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése
> **Megjegyzés**: Ha a VS Code nincs telepítve, a Ryzen AI Developer Center segítségével telepítheti.

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftveres előfeltételek telepítése

<!-- @prereq:hf-models-gemma-4-e4b-it,hf-datasets-finetome-100k -->

### Virtuális környezet létrehozása

<!-- @os:linux -->
<!-- @device:halo_box -->
Nyisson meg egy terminált, és hozzon létre egy venv-et, amelyben már telepítve van az AMD ROCm™ szoftver és a PyTorch:
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
python3 -m venv unsloth-env --system-site-packages
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Adjon hozzáférést a felhasználójának a GPU-eszközökhöz** (ennek érvénybe lépéséhez jelentkezzen ki, majd be):

```bash
sudo usermod -aG render,video $LOGNAME
```

Nyisson meg egy terminált, és hozzon létre egy venv-et:
<!-- @test:id=create-venv timeout=300 -->
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
<!-- @require:driver -->

> **Fontos:** Az Unsloth egyelőre nem támogatja a ROCm 10 mellett érkező PyTorch 2.13 buildet. Ehhez a playbookhoz telepítse a **ROCm 7.14-et PyTorch 2.12-vel** az alábbi parancsok segítségével. Ne használja a ROCm 10 / PyTorch 2.13 csomagokat.

**Telepítse a PyTorch-ot AMD ROCm™ szoftvertámogatással** a létrehozott virtuális környezetben:

<!-- @device:halo,halo_box -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1151]==2.12.0+rocm7.14.0" "torchvision[device-gfx1151]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1150]==2.12.0+rocm7.14.0" "torchvision[device-gfx1150]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:krk -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1152]==2.12.0+rocm7.14.0" "torchvision[device-gfx1152]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx7900xt -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1100]==2.12.0+rocm7.14.0" "torchvision[device-gfx1100]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx9070xt,r9700 -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1201]==2.12.0+rocm7.14.0" "torchvision[device-gfx1201]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

Más eszközök esetén a teljes útmutatóért tekintse meg a [ROCm 7.14 dokumentációját](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html).

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
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git" triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Megjegyzés:** Importálás közben az Unsloth opcionálisan megvizsgálhatja a `bitsandbytes` gyorsítási útvonalakat. Egyes ROCm verziókon előfordulhat egy olyan üzenet, mint a `bitsandbytes library load error: Configured ROCm binary not found`. Ez a playbook szabványos LoRA finomhangolást használ `optim="adamw_torch"` beállítással, így nem támaszkodunk a `bitsandbytes` optimalizálóra vagy a 4 bites QLoRA-ra. Ez az üzenet nyugodtan figyelmen kívül hagyható.

<!-- @os:windows -->
> **Megjegyzés:** Windows ROCm esetén az Unsloth indításkor több figyelmeztetést is kiír — lásd az alábbi [Ismert figyelmeztetések](#known-warnings) részt. Ezek mind biztonságosan figyelmen kívül hagyhatók; a tanítás megfelelően működik.
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

A playbook hátralévő része koncepcionálisan végigvezet a szkript minden fő lépésén.

## Hogyan működik

A test_unsloth.py szkript a következő lépéseket hajtja végre:
* **Modell betöltése**: Betölti a unsloth/gemma-4-E4B-it modellt a FastModel segítségével.
* **Adatok előkészítése**: Egységesíti az adathalmazt (pl. FineTome-100k), és alkalmazza a Gemma-4 csevegési sablont.
* **LoRA alkalmazása**: Adaptereket ad hozzá a nyelvi, figyelem (attention) és MLP modulokhoz a hatékony tanítás érdekében.
* **Tanítás**: SFTTrainer-t használ, csak a válaszra vonatkozó veszteségmaszkolással.
* **Következtetés**: Gyors generálási tesztet futtat a teljesítmény ellenőrzésére.
* **Mentés**: Exportálja a LoRA adaptereket helyben.
## Kulcsfontosságú konfiguráció

A futtatás testreszabásához a következő konstansokat módosíthatod:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Példa az Unsloth üdvözlő üzenetére és a modellsúlyok betöltésekor megjelenő kimenetre:

![alt text](assets/welcome.png)

## Adathalmaz előkészítése

A következő egy részhalmazát használjuk:
```text
mlabonne/FineTome-100k
```
Az adathalmaz: 
* Chat formátumba konvertálva
* A Gemma-4 chat sablonnal feldolgozva
* Megtisztítva a duplikált BOS tokenektől

## A modell betanítása

A szkript egy rövid betanítási demót futtat, a következő paraméterekkel:
- ~50 lépés
- Kis batch méret
- Gradiens akkumuláció

A betanítás során az alábbihoz hasonló naplóbejegyzéseket fogsz látni:

![alt text](assets/training.png)


## Mentés és üzembe helyezés

### Helyi mentés (LoRA)

A szkript automatikusan elmenti a LoRA adaptereket az OUTPUT_DIR mappába.
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
> **Megjegyzés:** A vLLM nem támogatja a Windows rendszert. A finomhangolt modell Windows rendszeren történő üzembe helyezéséhez használd a llama.cpp-t (lásd [GGUF exportálása](#export-gguf-for-llamacpp) alább), vagy másold át az egyesített modellt egy vLLM-et futtató Linux gépre.
<!-- @os:end -->

<!-- @os:linux -->
A vLLM-mel történő üzembe helyezéshez egyesítsd az adaptereket egy teljes modellbe:
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

Közvetlen konvertálás GGUF formátumba a helyi inferenciához:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Ismert figyelmeztetések

Ezeket a figyelmeztetéseket az Unsloth jeleníti meg induláskor Windows ROCm esetén, és mindegyik biztonságosan figyelmen kívül hagyható:

| Figyelmeztetés | Ok | Figyelmen kívül hagyható? |
|---|---|---|
| `bitsandbytes library load error` | A bitsandbytes-nak nincs Windows ROCm buildje | Igen — ez a playbook az `adamw_torch`-ot használja, nem a bnb-t |
| `No ROCm platform found for torch.distributed` | A Windows-on futó ROCm nem támogatja a elosztott betanítást | Igen — az egy-GPU-s betanítást ez nem érinti |
| `Unsloth: WARNING! You are using an unsupported platform` | Az Unsloth jelzi a nem Linux buildeket | Igen — a Windows ROCm működik egy-GPU-s SFT esetén |
| `triton is not available` | A Tritonnak nincs Windows buildje | Igen — az Unsloth visszaáll a PyTorch kernelekre |

A betanítás ezen figyelmeztetések ellenére is helyesen fog lezajlani.
<!-- @os:end -->

## Következő lépések
- Próbáld ki az [Unsloth Studio](https://unsloth.ai/docs/new/studio) alkalmazást, az Unsloth intuitív grafikus felhasználói felületét
- Végezz betanítást saját, specifikus adathalmazokon
- Próbálkozz finomhangolással különböző hiperparaméterekkel
- Helyezd üzembe vLLM vagy llama.cpp segítségével
- Próbáld ki a QLoRA-t egy alacsonyabb memóriaigényű beállításhoz

## Erőforrások

Az alábbiakban néhány további erőforrást találsz, hogy többet megtudj az Unsloth-ról és a finomhangolásról:

* [Unsloth dokumentáció](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth finomhangolási útmutató](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)