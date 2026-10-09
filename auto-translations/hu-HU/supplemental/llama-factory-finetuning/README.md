<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

## Áttekintés

A hatékony finomhangolás elengedhetetlen a nagy nyelvi modellek (LLM-ek) adaptálásához konkrét feladatokhoz. A LLaMA Factory egy nyílt forráskódú, felhasználóbarát platform, amely egyszerűsíti a nagy nyelvi modellek és multimodális modellek betanítását és finomhangolását. Lehetővé teszi a felhasználók számára, hogy minimális kódolással, helyben testreszabjanak több száz előre betanított modellt.

Ez a playbook megtanítja, hogyan finomhangolj LLM-eket a LLaMA Factory segítségével, a helyi AMD hardveren.

<!-- @device:stx,krk -->
> **Megjegyzés:** Az ebben a playbookban szereplő finomhangolási technikák legalább **32 GB rendszer-RAM-ot** igényelnek, amelyből legalább **16 GB-nak elérhetőnek kell lennie a GPU számára** (a 16 GB a 32 GB része, nem pedig azon felül értendő).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Megjegyzés:** Az ebben a playbookban szereplő finomhangolási technikák legalább **16 GB teljes GPU-memóriát** és **32 GB rendszer-RAM-ot** igényelnek.
> - Windows rendszeren a teljes GPU-memória a videokártya dedikált VRAM-ját és a megosztott GPU-memóriát (amelyet a rendszer-RAM-ból kölcsönöz) egyaránt magában foglalja.
> - Ennek megfelelően a 16 GB-nál kevesebb dedikált VRAM-mal rendelkező kártyák is futtathatják ezt a playbookot, mivel a megosztott GPU-memória pótolja a különbséget.
<!-- @os:end -->

<!-- @os:linux -->
> **Megjegyzés:** Az ebben a playbookban szereplő finomhangolási technikák legalább **16 GB dedikált GPU-memóriával** rendelkező videokártyát és **32 GB rendszer-RAM-ot** igényelnek.
> - Linux rendszeren a betanítás teljes egészében a videokártya dedikált VRAM-jában fut.
> - Nem áll vissza megosztott GPU-memóriára (rendszer-RAM-ra), amikor a VRAM elfogy.
> - A 16 GB-nál kevesebb dedikált VRAM-mal rendelkező kártyák Linux rendszeren a betanítás során kifogynak a memóriából, még akkor is, ha a rendszerben bőven van RAM.
<!-- @os:end -->
<!-- @device:end -->

## Amit megtanulsz

- Hogyan állítsd be a LLaMA Factory-t az AMD ROCm™ szoftverrel
- Hogyan konfiguráld az LLM finomhangolási paramétereit (a Qwen/Qwen3-4B-Instruct-2507 modellt használva példaként)
- Hogyan futtass finomhangolást a LLaMA Factory segítségével
- Hogyan futtass következtetést (inference) a finomhangolt modellel
- Hogyan exportáld a finomhangolt modellt 

## Becsült idő

- Időtartam: Körülbelül 60 percet vesz igénybe ennek a playbooknak a futtatása (a modell/adathalmaz méretétől és a hálózati sebességtől függően).
- Tekintsd meg a [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory) oldalát további információkért.

<!-- @device:halo_box,halo,stx,krk -->
## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftveres előfeltételek telepítése

<!-- @prereq:hf-models-qwen3-4b-instruct-2507 -->

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
**Adj hozzáférést a felhasználódnak a GPU-eszközökhöz** (jelentkezz ki és vissza be, hogy ez érvénybe lépjen):

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

### Kiegészítő függőségek telepítése

> **Megjegyzés**: Győződj meg róla, hogy a Python verziója 3.11, 3.12 vagy 3.13

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

### LLaMA Factory telepítése

A LLaMA Factory a PyTorch-ra épül. A fenti követelmények szerint ennek már telepítve kell lennie.

Töltsd le a forráskódot a [LLaMA Factory hivatalos GitHub tárolójából](https://github.com/hiyouga/LlamaFactory), és telepítsd a függőségeit.

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

Ellenőrizd, hogy a `llamafactory-cli` futtatható-e.

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

Miután sikeresen telepítetted a LLaMA Factory-t, futtassunk rajta finomhangolást.

## A LLaMA Factory CLI használata finomhangoláshoz

Ez a szakasz bemutatja, hogyan kell előkészíteni a finomhangolási adathalmazokat, konfigurálni a LoRA/QLoRA paramétereket, és futtatni a LoRA finomhangolást.

### Adathalmaz előkészítése

A LLaMA Factory támogatja az Alpaca formátumú és a ShareGPT formátumú finomhangolási adathalmazokat. Az összes elérhető adathalmaz meg van határozva a [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json) fájlban. Ha egyéni adathalmazt használsz, ügyelj arra, hogy egy adathalmaz-leírást adj hozzá a `dataset_info.json` fájlhoz, és add meg az adathalmaz nevét a betanítás előtt. A részletek a dokumentációjukban találhatók [itt](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

Ebben a playbookban az identity és az alpaca_en_demo adathalmazokat fogjuk használni példaként, és a következő lépésben konfiguráljuk az adathalmaz-információkat.
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

Ezek a példa konfigurációs fájlok tartalmazzák a modell paramétereit, a finomhangolási módszer paramétereit, az adathalmaz paramétereit, a kiértékelési paramétereket és egyebeket. Ezeket saját igényeid szerint konfigurálhatod. Ebben a playbookban a [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml) fájlt fogjuk használni.

**A legfontosabb paraméterek magyarázata:**
- `model_name_or_path` - A Hugging Face modell neve vagy a helyi modellfájl elérési útja.
- `stage` - A tanítási szakasz. Lehetőségek: rm (reward modeling), pt (pretrain), sft (Supervised Fine-Tuning), PPO, DPO, KTO, ORPO.
- `do_train` - true tanításhoz, false kiértékeléshez
- `finetuning_type` - A finomhangolási módszer. Lehetőségek: freeze, lora, full
- `lora_rank` - A LoRA módszer által használt alacsony rangú mátrix dimenziója, tipikus értékek: 4, 6, 8, 16 (kisebb érték = kevesebb paraméter = gyorsabb finomhangolás; nagyobb érték = jobb feladat-adaptáció, de magasabb erőforrásigény).
- `lora_target` - A LoRA módszer célmodulljai. Alapértelmezett: all.
- `dataset` - A használandó adathalmaz(ok). Több adathalmaz esetén válaszd el őket „,” karakterrel
- `output_dir` - A finomhangolás kimeneti elérési útja
- `logging_steps` - A naplózási intervallum lépésekben
- `save_steps` - A modell ellenőrzőpont (checkpoint) mentési intervalluma.
- `overwrite_output_dir` - Megengedett-e a kimeneti könyvtár felülírása.
- `per_device_train_batch_size` - A tanítási köteg (batch) mérete eszközönként.
- `gradient_accumulation_steps` - A gradiens-akkumulációs lépések száma.
- `learning_rate` - Tanulási ráta
- `num_train_epochs` - A tanítási epochok száma
- `lr_scheduler_type` - A tanulási ráta ütemezése. Lehetőségek: linear, cosine, polynomial, constant, stb.
- `warmup_ratio` - A tanulási ráta bemelegítési (warmup) aránya

<!-- @os:linux -->
Módosítani fogjuk a `lora_rank` alapértelmezett értékét, hogy AMD Ryzen™ és AMD Radeon™ GPU-kon futtassuk a finomhangolást.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
Frissíteni fogjuk az alapértelmezett LoRA finomhangolási konfigurációt a jobb kompatibilitás érdekében az AMD Ryzen™ és AMD Radeon™ GPU-kkal:
- A `lora_rank` értékét `8`-ról `6`-ra állítjuk, hogy csökkentsük a memóriahasználatot a finomhangolás során.
- A `bf16` helyett `fp16`-ot használunk a szélesebb körű AMD GPU-kompatibilitás és az alacsonyabb memóriahasználat érdekében.
- A `dataloader_num_workers` értékét Windows rendszeren `0`-ra állítjuk, hogy elkerüljük a többfolyamatos adatbetöltés által okozott `"Can't pickle local object<>"` hibákat.

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

A **llamafactory-cli** a LLaMA Factory hivatalos parancssori (CLI) eszköze, amelyet azért fejlesztettek ki, hogy egyszerűsítse a teljes LLM-munkafolyamatokat (adat-előkészítés → finomhangolás → kiértékelés → üzembe helyezés) bonyolult kód írása nélkül.

A tanításhoz/finomhangoláshoz a **llamafactory-cli train** a LLaMA Factory CLI alapvető alparancsa. A finomhangolási munkafolyamatokat (adatok előfeldolgozása, hiperparaméter-hangolás, hardveroptimalizálás) egyetlen CLI-parancsba foglalja, több finomhangolási paradigmát támogat (LoRA/QLoRA/teljes finomhangolás), és alacsony erőforrású GPU-khoz is optimalizált (pl. QLoRA 16 GB VRAM mellett).

A LLaMA Factory finomhangolást az alábbi paranccsal futtathatod, amely a Qwen3 LoRA finomhangolás módosított konfigurációs fájlján alapul.

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

Az LLM-finomhangolás futtatása után minden generált kimenet az "output_dir" könyvtárban kerül tárolásra, beleértve a modell ellenőrzőpont-fájljait, konfigurációs fájljait és a tanítási metrikákat.

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

A **llamafactory-cli chat** parancsot interaktív csevegésre/inferenciára tervezték LLM-ekkel (mind alapmodellekkel, mind LoRA-val finomhangolt modellekkel). A LLaMA Factory biztosít egy mintakonfigurációt a finomhangolt modellek inferenciájának futtatásához az [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference) könyvtárban. Ezt a mintakonfigurációt módosíthatod is a beállítások, például az inferencia háttérrendszer (backend) megváltoztatásához.

A finomhangolt Qwen3 modell teszteléséhez használd az alábbi parancsot:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
Az alábbiakban egy példa látható a finomhangolt modell használatával történő csevegésre:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### A finomhangolt modell exportálása

Éles (production) felhasználási esetekhez az előtanított modellt és a LoRA adaptert össze kell vonni és egyetlen modellként exportálni. Ez az összevont modell normál Hugging Face modellfájlként használható. A LLaMA Factory biztosítja a mintakonfigurációkat az [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora) könyvtárban.

A finomhangolt Qwen3 modell exportálásához használd az alábbi parancsot:

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

A `LLaMA-Factory` lehetővé teszi az LLM-ek kódolás nélküli finomhangolását egy böngészőben futó webes felületen keresztül is.

A megnyitásához használd a következő parancsot:

```bash
llamafactory-cli webui
```
A `LlamaFactory Web UI` áttekinthető felületet kínál a gépi tanulási munkafolyamatok kezeléséhez, beleértve a tanítást, kiértékelést, előrejelzést, csevegést és a modellek exportálását. Íme egy rövid bemutatás az egyes lapokról:

* **Train**: Ez a lap lehetővé teszi egy modell és egy adathalmaz kiválasztását, a tanítási paraméterek konfigurálását, valamint a tanítási folyamat elindítását. Fontos megérteni a kötelező és opcionális paramétereket a tanítási beállítások optimalizálásához.
* **Evaluate & Predict**: A tanítás után ezen a lapon értékelheted ki a modell teljesítményét, és végezhetsz előrejelzéseket. Betekintést nyújt a modell pontosságába és hatékonyságába új adatokon.
* **Chat**: A tanítás befejezése után töltsd be a modellt a Chat lapon, hogy interakcióba léphess vele, és megtekinthesd a munkád eredményeit. Ez a funkció valós idejű kommunikációt tesz lehetővé a betanított modellel.
* **Export**: Ez a lap megkönnyíti a betanított modellek exportálását üzembe helyezéshez vagy további felhasználáshoz. A modelleket különböző, más-más alkalmazásokhoz megfelelő formátumokban mentheted el.

Részletes útmutatásért javasoljuk, hogy tekintsd meg a hivatalos dokumentációt a [LlamaFactory GitHub repository](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) oldalon és a [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest) oldalon. Emellett a [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) hasznos betekintést nyújt a felületbe és annak funkcióiba.

## Következő lépések
- Próbálj ki különböző modelleket, például a `gpt-oss`-t és más élvonalbeli modelleket.
- Kísérletezz különböző háttérrendszerekkel a finomhangolt modellen
 
További dokumentációért keresd fel: https://llamafactory.readthedocs.io/en/latest/