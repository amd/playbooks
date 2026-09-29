<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

## Áttekintés

A hatékony finomhangolás elengedhetetlen a nagy nyelvi modellek (LLM-ek) alkalmazkodásához a specifikus feladatokhoz. A LLaMA Factory egy nyílt forráskódú és felhasználóbarát platform, amely leegyszerűsíti a nagy nyelvi modellek és multimodális modellek betanítását és finomhangolását. Lehetővé teszi a felhasználók számára, hogy helyben, minimális kódolással testre szabjanak több száz előre betanított modellt.

Ez az útmutató megtanítja Önnek, hogyan finomhangolhat LLM-eket a LLaMA Factory segítségével a helyi AMD hardverén.

<!-- @device:stx,krk -->
> **Megjegyzés:** Az ebben az útmutatóban szereplő finomhangolási technikákhoz legalább **32 GB rendszer RAM** szükséges, amelyből legalább **16 GB-nak elérhetőnek kell lennie a GPU számára** (ez a 16 GB a 32 GB részét képezi, nem azon felül értendő).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Megjegyzés:** Az ebben az útmutatóban szereplő finomhangolási technikákhoz legalább **16 GB összes GPU memória** és **32 GB rendszer RAM** szükséges.
> - Windows rendszeren az összes GPU memória a videokártya dedikált VRAM-ját és a megosztott GPU memóriát (a rendszer RAM-jából kölcsönzött részt) foglalja magában.
> - Ezért a 16 GB-nál kevesebb dedikált VRAM-mal rendelkező kártyák is képesek futtatni ezt az útmutatót, mivel a megosztott GPU memóriával pótolják a különbséget.
<!-- @os:end -->

<!-- @os:linux -->
> **Megjegyzés:** Az ebben az útmutatóban szereplő finomhangolási technikákhoz legalább **16 GB dedikált GPU memóriával** rendelkező videokártya és **32 GB rendszer RAM** szükséges.
> - Linux rendszeren a betanítás teljes egészében a videokártya dedikált VRAM-jában fut.
> - Nem vált át megosztott GPU memóriára (rendszer RAM-ra), ha a VRAM elfogy.
> - A 16 GB-nál kevesebb dedikált VRAM-mal rendelkező kártyák a betanítás során kifogynak a memóriából Linuxon, még akkor is, ha a rendszerben bőven van RAM.
<!-- @os:end -->
<!-- @device:end -->

## Amit tanulni fog

- Hogyan állítsa be a LLaMA Factory-t az AMD ROCm™ szoftverrel
- Hogyan konfigurálja az LLM finomhangolási paramétereit (a Qwen/Qwen3-4B-Instruct-2507 modellt használva példaként)
- Hogyan futtassa a LLaMA Factory finomhangolást
- Hogyan futtasson következtetést a finomhangolt modellel
- Hogyan exportálja a finomhangolt modellt

## Becsült időtartam

- Időtartam: Ennek az útmutatónak a futtatása körülbelül 60 percet vesz igénybe (a modell/adathalmaz méretétől és a hálózati sebességtől függően).
- További információért tekintse meg a [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory) oldalt.

<!-- @device:halo_box,halo,stx,krk -->
## Memóriakonfiguráció beállítása

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftverkövetelmények telepítése

<!-- @os:linux -->
<!-- @test:id=python-prereqs-check timeout=120 hidden=True -->
```bash
python3 --version
pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-prereqs-check timeout=120 hidden=True -->
```powershell
python --version
pip --version
```
<!-- @test:end -->
<!-- @os:end -->

#### Virtuális környezet létrehozása

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv llamafactory-env --system-site-packages
source llamafactory-env/bin/activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="source llamafactory-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Adjon hozzáférést a felhasználójának a GPU-eszközökhöz** (a változás érvénybe lépéséhez jelentkezzen ki, majd vissza):

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv llamafactory-env
source llamafactory-env/bin/activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="source llamafactory-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv llamafactory-env --system-site-packages
llamafactory-env\Scripts\activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="llamafactory-env\Scripts\activate" --> 
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv llamafactory-env
llamafactory-env\Scripts\activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="llamafactory-env\Scripts\activate" --> 
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

### További függőségek telepítése

> **Megjegyzés**: Győződjön meg róla, hogy a Python verziója 3.11, 3.12 vagy 3.13

```bash
pip install huggingface_hub
```

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 hidden=True setup=activate-venv -->
```bash
python3 -m pip install --upgrade pip
python3 -m pip install huggingface_hub
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 hidden=True setup=activate-venv -->
```powershell
python -m pip install --upgrade pip
python -m pip install huggingface_hub
```
<!-- @test:end --> 
<!-- @os:end -->

### A LLaMA Factory telepítése

A LLaMA Factory a PyTorch-tól függ. Ezt már telepítenie kellett a fenti követelmények szerint.

Töltse le a forráskódot a [LLaMA Factory hivatalos GitHub tárolójából](https://github.com/hiyouga/LlamaFactory), és telepítse a függőségeit.

<!-- @device:halo_box -->
<!-- @test:id=install-llamafactory timeout=900 setup=activate-venv -->
```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install setuptools --break-system-packages
pip install -e . --break-system-packages
pip install -r requirements/metrics.txt --break-system-packages
```
<!-- @test:end --> 
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=install-llamafactory timeout=900 setup=activate-venv -->
```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install -e .
pip install -r requirements/metrics.txt 
```
<!-- @test:end --> 
<!-- @device:end -->

Ellenőrizze, hogy a `llamafactory-cli` futtatható-e.

<!-- @os:linux -->
<!-- @test:id=verify-llamafactory-cli timeout=60 hidden=False setup=activate-venv -->
```bash
cd LlamaFactory
llamafactory-cli version || python -m llamafactory.cli version || true
echo "llamafactory-cli is available"
command -v llamafactory-cli
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=verify-llamafactory-cli timeout=60 hidden=False setup=activate-venv -->
```powershell
cd LlamaFactory
if (Get-Command llamafactory-cli -ErrorAction SilentlyContinue) {
    llamafactory-cli version
    Write-Host "llamafactory-cli is available"
} else {
    Write-Host "llamafactory-cli is not available"
}
```
<!-- @test:end --> 
<!-- @os:end -->

Példa kimenet:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

Miután sikeresen telepítette a LLaMA Factory-t, futtassuk rajta a finomhangolást.

## A LLaMA Factory CLI használata finomhangoláshoz

Ez a szakasz bemutatja, hogyan készítsen elő finomhangolási adathalmazokat, hogyan konfigurálja a LoRA/QLoRA paramétereket, és hogyan futtasson LoRA finomhangolást.

### Adathalmaz előkészítése

A LLaMA Factory támogatja az Alpaca formátumú és ShareGPT formátumú finomhangolási adathalmazokat. Az összes elérhető adathalmaz meg van határozva a [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json) fájlban. Ha egyéni adathalmazt használ, ügyeljen arra, hogy adjon hozzá egy adathalmaz-leírást a `dataset_info.json` fájlhoz, és adja meg az adathalmaz nevét a betanítás előtt. A részletek megtalálhatók a dokumentációjukban [itt](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

Ebben az útmutatóban az identity és alpaca_en_demo adathalmazokat fogjuk példaként használni, és a következő lépésben konfiguráljuk az adathalmaz-információkat.
### Finomhangolási paraméterek konfigurálása

A LLaMA Factory több finomhangolási sémát is támogat.

| Finomhangolási séma | LLaMA Factory példák |
|-----------|------|
| Teljes paraméteres    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| LoRA finomhangolás  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| QLoRA finomhangolás | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

<!-- @test:id=verify-llamafactory-files timeout=60 hidden=True setup=activate-venv -->
```python
import os
import sys

base = "LlamaFactory"
required = [
    "examples/train_lora/qwen3_lora_sft.yaml",
    "examples/inference/qwen3_lora_sft.yaml",
    "examples/merge_lora/qwen3_lora_sft.yaml",
]

missing = [p for p in required if not os.path.exists(os.path.join(base, p))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

print("PASS: Required LLaMA Factory example files exist")
```
<!-- @test:end -->

Ezek a példakonfigurációs fájlok megadják a modell paramétereit, a finomhangolási módszer paramétereit, az adathalmaz paramétereit, az értékelési paramétereket és egyebeket. Ezeket saját igényeid szerint konfigurálhatod. Ebben a kézikönyvben a [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml) fájlt fogjuk használni.

**Kulcsfontosságú paraméterek magyarázata:**
- `model_name_or_path` - A Hugging Face modell neve vagy a helyi modellfájl elérési útja.
- `stage` - A tanítási szakasz. Lehetőségek: rm (jutalommodellezés), pt (előtanítás), sft (felügyelt finomhangolás), PPO, DPO, KTO, ORPO.
- `do_train` - true tanításhoz, false kiértékeléshez
- `finetuning_type` - A finomhangolási módszer. Lehetőségek: freeze, lora, full
- `lora_rank` - A LoRA-ban használt alacsony rangú mátrix dimenziószáma, tipikus értékek: 4, 6, 8, 16 (kisebb érték = kevesebb paraméter = gyorsabb finomhangolás; nagyobb érték = jobb feladat-adaptáció, de nagyobb erőforrásigény).
- `lora_target` - A LoRA módszer célmoduljai. Alapértelmezett: all.
- `dataset` - A használandó adathalmaz(ok). Több adathalmaz esetén válaszd el őket „,” jellel
- `output_dir` - A finomhangolás kimeneti elérési útja
- `logging_steps` - A naplózás gyakorisága lépésekben
- `save_steps` - A modell ellenőrzőpontjának mentési gyakorisága.
- `overwrite_output_dir` - Engedélyezett-e a kimeneti könyvtár felülírása.
- `per_device_train_batch_size` - A tanítási kötegméret eszközönként.
- `gradient_accumulation_steps` - A gradiens-akkumulációs lépések száma.
- `learning_rate` - Tanulási ráta
- `num_train_epochs` - A tanítási epochok száma
- `lr_scheduler_type` - A tanulási ráta ütemezése. Lehetőségek: linear, cosine, polynomial, constant stb.
- `warmup_ratio` - A tanulási ráta bemelegítési (warmup) aránya

<!-- @os:linux -->
A `lora_rank` alapértelmezett értékét fogjuk módosítani, hogy finomhangolást futtathassunk AMD Ryzen™ és AMD Radeon™ GPU-kon.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
Frissítjük az alapértelmezett LoRA finomhangolási konfigurációt a jobb kompatibilitás érdekében AMD Ryzen™ és AMD Radeon™ GPU-kon:
- A `lora_rank` értékét `8`-ról `6`-ra állítjuk, hogy csökkentsük a memóriahasználatot a finomhangolás során.
- A `bf16` helyett `fp16`-ot használunk a szélesebb körű AMD GPU-kompatibilitás és az alacsonyabb memóriahasználat érdekében.
- A `dataloader_num_workers` értékét `0`-ra állítjuk Windows rendszeren, hogy elkerüljük a többfolyamatos adatbetöltés által okozott „Can't pickle local object<>” hibákat.

```powershell
$filePath = "examples/train_lora/qwen3_lora_sft.yaml"

# Create a backup before modifying the YAML file
Copy-Item -Path $filePath -Destination "$filePath.bak" -Force

# Read the file and update the training settings
$content = Get-Content -Path $filePath -Raw

$newContent = $content `
  -replace 'lora_rank: 8', 'lora_rank: 6' `
  -replace 'bf16: true', 'fp16: true' `
  -replace 'dataloader_num_workers: 4', 'dataloader_num_workers: 0'

Set-Content -Path $filePath -Value $newContent
```
<!-- @os:end -->

### LLaMA Factory finomhangolás futtatása

A **llamafactory-cli** a LLaMA Factory hivatalos parancssori (CLI) eszköze, amelyet azért fejlesztettek ki, hogy egyszerűsítse a teljes LLM munkafolyamatot (adat-előkészítés → finomhangolás → kiértékelés → üzembe helyezés) bonyolult kód írása nélkül.

A tanításhoz/finomhangoláshoz a **llamafactory-cli train** a LLaMA Factory CLI alapvető alparancsa. Egyetlen CLI-parancsba absztrahálja a finomhangolási munkafolyamatokat (adat-előfeldolgozás, hiperparaméter-hangolás, hardveroptimalizálás), több finomhangolási paradigmát (LoRA/QLoRA/teljes finomhangolás) támogatva, és optimalizált alacsony erőforrású GPU-khoz (pl. QLoRA 16 GB VRAM esetén).

A következő paranccsal futtathatod a LLaMA Factory finomhangolást, amely a Qwen3 LoRA finomhangolás módosított konfigurációs fájlján alapul.

```bash
llamafactory-cli train examples/train_lora/qwen3_lora_sft.yaml
```

<!-- @os:linux -->
<!-- @test:id=quick-train-llamafactory-lora timeout=1200 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory

cp examples/train_lora/qwen3_lora_sft.yaml examples/train_lora/qwen3_lora_sft_ci.yaml

sed -i 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's|output_dir: .*|output_dir: saves/qwen3_lora_sft_ci|g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/overwrite_output_dir: false/overwrite_output_dir: true/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/per_device_train_batch_size: .*/per_device_train_batch_size: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/gradient_accumulation_steps: .*/gradient_accumulation_steps: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/num_train_epochs: .*/num_train_epochs: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/logging_steps: .*/logging_steps: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/save_steps: .*/save_steps: 5/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true

sed -i 's/max_samples: .*/max_samples: 16/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
if grep -q '^max_steps:' examples/train_lora/qwen3_lora_sft_ci.yaml; then
  sed -i 's/^max_steps:.*/max_steps: 5/g' examples/train_lora/qwen3_lora_sft_ci.yaml
else
  printf '\nmax_steps: 5\n' >> examples/train_lora/qwen3_lora_sft_ci.yaml
fi
if grep -q '^save_total_limit:' examples/train_lora/qwen3_lora_sft_ci.yaml; then
  sed -i 's/^save_total_limit:.*/save_total_limit: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml
else
  printf 'save_total_limit: 1\n' >> examples/train_lora/qwen3_lora_sft_ci.yaml
fi

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=quick-train-llamafactory-lora timeout=1200 hidden=True setup=activate-venv -->
```powershell
Set-Location -Path "LlamaFactory"

Copy-Item -Path "examples/train_lora/qwen3_lora_sft.yaml" -Destination "examples/train_lora/qwen3_lora_sft_ci.yaml"

$filePath = "examples/train_lora/qwen3_lora_sft_ci.yaml"
(Get-Content -Path $filePath) -replace 'lora_rank: 8', 'lora_rank: 6' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'bf16:\s*true', 'fp16: true' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'dataloader_num_workers:\s*4', 'dataloader_num_workers: 0' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'output_dir: .*', 'output_dir: saves/qwen3_lora_sft_ci' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'overwrite_output_dir: false', 'overwrite_output_dir: true' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'per_device_train_batch_size: .*', 'per_device_train_batch_size: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'gradient_accumulation_steps: .*', 'gradient_accumulation_steps: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'num_train_epochs: .*', 'num_train_epochs: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'logging_steps: .*', 'logging_steps: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'save_steps: .*', 'save_steps: 5' | Set-Content -Path $filePath

(Get-Content -Path $filePath) -replace 'max_samples: .*', 'max_samples: 16' | Set-Content -Path $filePath
if (Select-String -Path $filePath -Pattern '^max_steps:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^max_steps:.*', 'max_steps: 5' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value ""
    Add-Content -Path $filePath -Value "max_steps: 5"
}
if (Select-String -Path $filePath -Pattern '^save_total_limit:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^save_total_limit:.*', 'save_total_limit: 1' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value "save_total_limit: 1"
}

# Single-process dataset preprocessing to avoid Windows multiprocessing errors.
if (Select-String -Path $filePath -Pattern '^preprocessing_num_workers:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^preprocessing_num_workers:.*', 'preprocessing_num_workers: 1' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value "preprocessing_num_workers: 1"
}

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

Az LLM finomhangolás futtatása után minden létrejött kimenet az „output_dir” könyvtárban tárolódik, beleértve a modell ellenőrzőpont-fájljait, a konfigurációs fájlokat és a tanítási metrikákat.

<p align="center">
  <img src="assets/qwen3_lora.png" alt="Qwen3 LoRA Fine-tuning" width="600"/>
</p>

<!-- @test:id=verify-llamafactory-train-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "LlamaFactory/saves/qwen3_lora_sft_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "trainer_state.json",
    "training_args.bin",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) + glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: LLaMA Factory training output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end --> 

### A finomhangolt modell tesztelése

A **llamafactory-cli chat** interaktív csevegésre/következtetésre (inference) szolgál LLM-ekkel (mind az alapmodellekkel, mind a LoRA-val finomhangolt modellekkel). A LLaMA Factory mintakonfigurációt biztosít a finomhangolt modellek következtetésének futtatásához az [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference) mappában. Ezt a mintakonfigurációt módosíthatod is a beállítások, például a következtetési backend megváltoztatásához.

A következő paranccsal tesztelheted a Qwen3 finomhangolt modellt:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
Az alábbiakban egy példa látható a finomhangolt modellt használó csevegésre:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### A finomhangolt modell exportálása

Éles felhasználási esetekhez az előtanított modellt és a LoRA-adaptert egyesíteni és egyetlen modellbe kell exportálni. Ez az egyesített modell normál Hugging Face modellfájlként használható. A LLaMA Factory mintakonfigurációkat biztosít az [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora) mappában.

A következő paranccsal exportálhatod a Qwen3 finomhangolt modellt:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
A finomhangolt modell exportálásának eredménye az alábbiakban látható.

<p align="center">
  <img src="assets/qwen3_export.png" alt="Export Qwen3 Fine-Tuned model " width="600"/>
</p>

<!-- @os:linux -->
<!-- @test:id=export-llamafactory-model timeout=1800 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory
pip install pyyaml

python - <<'PY'
import yaml
from pathlib import Path

src = Path("examples/merge_lora/qwen3_lora_sft.yaml")
dst = Path("examples/merge_lora/qwen3_lora_sft_ci.yaml")

cfg = yaml.safe_load(src.read_text())

cfg["adapter_name_or_path"] = "saves/qwen3_lora_sft_ci"
cfg["export_dir"] = "saves/qwen3_lora_sft_ci_merged"

dst.write_text(yaml.safe_dump(cfg, sort_keys=False))
print(f"Wrote {dst}")
PY

llamafactory-cli export examples/merge_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=export-llamafactory-model timeout=1800 hidden=True setup=activate-venv -->
```powershell
Set-Location -Path "LlamaFactory"
pip install pyyaml

$script = @'
import yaml
from pathlib import Path

src = Path("examples/merge_lora/qwen3_lora_sft.yaml")
dst = Path("examples/merge_lora/qwen3_lora_sft_ci.yaml")

cfg = yaml.safe_load(src.read_text())

cfg["adapter_name_or_path"] = "saves/qwen3_lora_sft_ci"
cfg["export_dir"] = "saves/qwen3_lora_sft_ci_merged"

dst.write_text(yaml.safe_dump(cfg, sort_keys=False))
print(f"Wrote {dst}")
'@

$tempPy = Join-Path $env:TEMP "write_llamafactory_export_config.py"
Set-Content -Path $tempPy -Value $script -Encoding UTF8

python $tempPy
if ($LASTEXITCODE -ne 0) {
    Remove-Item $tempPy -Force -ErrorAction SilentlyContinue
    throw "FAIL: Could not create qwen3_lora_sft_ci.yaml"
}
Remove-Item $tempPy -Force -ErrorAction SilentlyContinue

if (-not (Test-Path "examples/merge_lora/qwen3_lora_sft_ci.yaml")) {throw "FAIL: examples/merge_lora/qwen3_lora_sft_ci.yaml was not created"}

llamafactory-cli export examples/merge_lora/qwen3_lora_sft_ci.yaml
if ($LASTEXITCODE -ne 0) {throw "FAIL: llamafactory-cli export failed"}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @test:id=verify-llamafactory-export-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "LlamaFactory/saves/qwen3_lora_sft_ci_merged"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing export directory: {out_dir}")
    sys.exit(1)

required = ["config.json",]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required export files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Exported merged model output looks correct")
```
<!-- @test:end -->
## LLaMA Factory GUI használata

A `LLaMA-Factory` a böngészőben elérhető webes felhasználói felületen keresztül is támogatja az LLM-ek kódolás nélküli finomhangolását.

A megnyitásához használja a következő parancsot:

```bash
llamafactory-cli webui
```
A `LlamaFactory Web UI` egy egyszerűsített felületet kínál a gépi tanulási munkafolyamatok kezeléséhez, beleértve a tanítást, kiértékelést, előrejelzést, csevegést és a modellek exportálását. Íme egy rövid bemutatás az egyes lapokról:

* **Train**: Ez a lap lehetővé teszi egy modell és egy adathalmaz kiválasztását, a tanítási paraméterek beállítását, valamint a tanítási folyamat elindítását. Fontos megérteni a kötelező és opcionális paramétereket a tanítási beállítások optimalizálásához.
* **Evaluate & Predict**: A tanítás befejezése után ezen a lapon értékelheti ki a modell teljesítményét, és készíthet előrejelzéseket. Betekintést nyújt a modell pontosságába és hatékonyságába új adatokon.
* **Chat**: A tanítás befejezése után töltse be a modellt a Chat lapon, hogy interakcióba léphessen vele, és láthassa a munkája eredményét. Ez a funkció lehetővé teszi a valós idejű kommunikációt a betanított modellel.
* **Export**: Ez a lap megkönnyíti a betanított modellek exportálását üzembe helyezéshez vagy további felhasználáshoz. A modelleket különféle, más-más alkalmazásokhoz megfelelő formátumokban mentheti.

Részletes útmutatásért javasoljuk, hogy tekintse meg a hivatalos dokumentációt a [LlamaFactory GitHub repository](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) oldalon, valamint a [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest) dokumentációban. Emellett a [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) hasznos betekintést nyújt a felületbe és annak funkcióiba.

## Következő lépések
- Próbáljon ki különböző modelleket, például a `gpt-oss`-t és más, élvonalbeli modelleket.
- Kísérletezzen különböző háttérrendszerekkel a finomhangolt modellen

További dokumentációért látogasson el ide: https://llamafactory.readthedocs.io/en/latest/