## Prehľad

Efektívne doladenie je kľúčové pre prispôsobenie veľkých jazykových modelov (LLM) na konkrétne úlohy. LLaMA-Factory je open-source a používateľsky prívetivá platforma, ktorá zjednodušuje trénovanie a doladenie veľkých jazykových modelov a multimodálnych modelov. Umožňuje používateľom lokálne prispôsobiť stovky predtrénovaných modelov s minimálnym kódovaním.

Tento návod vás naučí, ako doladiť LLM pomocou LLaMA-Factory na vašom lokálnom hardvéri AMD.

<!-- @device:stx,krk -->
> **Poznámka:** Techniky doladenia v tomto návode vyžadujú aspoň **32 GB systémovej RAM**, pričom aspoň **16 GB z nej musí byť dostupných pre GPU** (týchto 16 GB je súčasťou 32 GB, nie navyše).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Poznámka:** Techniky doladenia v tomto návode vyžadujú aspoň **16 GB celkovej pamäte GPU** a **32 GB systémovej RAM**.
> - V systéme Windows sa celková pamäť GPU skladá z dedikovanej VRAM grafickej karty a zdieľanej pamäte GPU (požičanej zo systémovej RAM).
> - Karty s menej ako 16 GB dedikovanej VRAM teda môžu tento návod spustiť pomocou zdieľanej pamäte GPU na doplnenie rozdielu.
<!-- @os:end -->

<!-- @os:linux -->
> **Poznámka:** Techniky doladenia v tomto návode vyžadujú grafickú kartu s aspoň **16 GB dedikovanej pamäte GPU** a **32 GB systémovej RAM**.
> - V systéme Linux prebieha trénovanie výhradne v dedikovanej VRAM grafickej karty.
> - Neprebieha záložný prechod na zdieľanú pamäť GPU (systémovú RAM) pri vyčerpaní VRAM.
> - Kartám s menej ako 16 GB dedikovanej VRAM dôjde pamäť počas trénovania v systéme Linux, aj keď má systém dostatok RAM.
<!-- @os:end -->
<!-- @device:end -->

## Čo sa naučíte

- Ako nastaviť LLaMA-Factory so softvérom AMD ROCm™
- Ako konfigurovať parametre doladenia LLM (na príklade Qwen/Qwen3-4B-Instruct-2507)
- Ako spustiť doladenie pomocou LLaMA-Factory
- Ako spustiť inferenciu s doladeným modelom
- Ako exportovať doladený model

## Odhadovaný čas

- Trvanie: Spustenie tohto návodu trvá približne 60 minút (v závislosti od veľkosti modelu/datasetu a rýchlosti siete).
- Ďalšie informácie nájdete na [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory).

## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizácií softvéru

<!-- @require:software-update -->
<!-- @device:end -->

## Inštalácia softvérových predpokladov

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

#### Vytvorenie virtuálneho prostredia

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=120 -->
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
**Udeľte svojmu používateľovi prístup k zariadeniam GPU** (pre uplatnenie zmeny sa odhláste a znova prihláste):

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=120 -->
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

### Inštalácia základných závislostí

<!-- @require:pytorch,driver -->
 
### Inštalácia ďalších závislostí

> **Poznámka**: Uistite sa, že verzia Pythonu je 3.11, 3.12 alebo 3.13

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

### Inštalácia LLaMA-Factory

LLaMA-Factory závisí od PyTorch. Mali by ste ho mať nainštalovaný podľa vyššie uvedených požiadaviek.

Stiahnite zdrojový kód z [oficiálneho repozitára LLaMA Factory na GitHub](https://github.com/hiyouga/LlamaFactory) a nainštalujte jeho závislosti.

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

Overte, či je `llamafactory-cli` spustiteľný.

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

Príklad výstupu:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

Po úspešnej inštalácii LLaMA-Factory spustíme na ňom doladenie.

## Používanie LLaMA Factory CLI na doladenie

Táto časť sa venuje príprave datasetov na doladenie, konfigurácii parametrov LoRA/QLoRA a spusteniu doladenia pomocou LoRA.

### Príprava datasetu

LLaMA-Factory podporuje datasety na doladenie vo formáte Alpaca a formáte ShareGPT. Všetky dostupné datasety sú definované v súbore [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). Ak používate vlastný dataset, nezabudnite pridať popis datasetu do súboru `dataset_info.json` a pred trénovaním zadať názov datasetu. Podrobnosti nájdete v ich dokumentácii [tu](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

V tomto návode použijeme ako príklad datasety identity a alpaca_en_demo a informácie o datasete nakonfigurujeme v nasledujúcom kroku.


### Konfigurácia parametrov doladenia

LLaMA-Factory podporuje viacero schém doladenia.

| Schémy doladenia | Príklady LLaMA-Factory |
|-----------|------|
| Úplné parametre    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| Doladenie LoRA  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| Doladenie QLoRA | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

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

Tieto príkladové konfiguračné súbory obsahujú parametre modelu, parametre metódy doladenia, parametre datasetu, parametre hodnotenia a ďalšie. Môžete ich nakonfigurovať podľa vlastných potrieb. V tomto návode použijeme súbor [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml).

**Vysvetlenie kľúčových parametrov:**
- `model_name_or_path` – Názov modelu na Hugging Face alebo cesta k lokálnemu súboru modelu.
- `stage` – Fáza trénovania. Možnosti: rm (reward modeling), pt (pretrain), sft (Supervised Fine-Tuning), PPO, DPO, KTO, ORPO.
- `do_train` – true pre trénovanie, false pre hodnotenie.
- `finetuning_type` – Metóda doladenia. Možnosti: freeze, lora, full.
- `lora_rank` – Dimenzionalita matice nízkej hodnosti používanej v LoRA, typické hodnoty: 4, 6, 8, 16 (menšie hodnoty = menej parametrov = rýchlejšie doladenie; väčšie hodnoty = lepšia adaptácia na úlohu, ale vyššie nároky na zdroje).
- `lora_target` – Cieľové moduly pre metódu LoRA. Predvolené: all.
- `dataset` – Dataset(y) na použitie. Na oddelenie viacerých datasetov použite ",".
- `output_dir` – Výstupná cesta doladenia.
- `logging_steps` – Interval zaznamenávania v krokoch.
- `save_steps` – Interval ukladania kontrolného bodu modelu.
- `overwrite_output_dir` – Či povoliť prepísanie výstupného adresára.
- `per_device_train_batch_size` – Veľkosť trénovacej dávky na zariadenie.
- `gradient_accumulation_steps` – Počet krokov akumulácie gradientu.
- `learning_rate` – Rýchlosť učenia.
- `num_train_epochs` – Počet trénovacích epoch.
- `lr_scheduler_type` – Plán rýchlosti učenia. Možnosti: linear, cosine, polynomial, constant atď.
- `warmup_ratio` – Pomer zahrievania rýchlosti učenia.

<!-- @os:linux -->
Upravíme predvolenú hodnotu `lora_rank` na spustenie doladenia na GPU AMD Ryzen™ a AMD Radeon™.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
Aktualizujeme predvolenú konfiguráciu doladenia LoRA pre lepšiu kompatibilitu s GPU AMD Ryzen™ a AMD Radeon™:
- Nastavíme `lora_rank` z `8` na `6`, aby sa znížilo využitie pamäte počas doladenia.
- Použijeme `fp16` namiesto `bf16` pre širšiu kompatibilitu s GPU AMD a nižšie využitie pamäte.
- Nastavíme `dataloader_num_workers` na `0` v systéme Windows, aby sme predišli chybám `"Can't pickle local object<>"` spôsobeným načítavaním dát pomocou multiprocessingu.

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

### Spustenie doladenia pomocou LLaMA-Factory

**llamafactory-cli** je oficiálny nástroj príkazového riadka (CLI) pre LLaMA-Factory, vyvinutý na zjednodušenie kompletných pracovných postupov LLM (príprava dát → doladenie → hodnotenie → nasadenie) bez písania zložitého kódu.

Pre trénovanie/doladenie je **llamafactory-cli train** hlavným podpríkazom CLI nástroja LLaMA-Factory. Abstrahuje pracovné postupy doladenia (predspracovanie dát, ladenie hyperparametrov, optimalizácia hardvéru) do jediného príkazu CLI, podporuje viacero paradigiem doladenia (LoRA/QLoRA/úplné doladenie) a je optimalizovaný pre GPU s obmedzenými zdrojmi (napr. QLoRA na 16 GB VRAM).

Doladenie pomocou LLaMA-Factory môžete spustiť nasledujúcim príkazom, ktorý vychádza z upraveného konfiguračného súboru doladenia Qwen3 LoRA.

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

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

Po spustení doladenia LLM sú všetky vygenerované výstupy uložené v adresári „output_dir", vrátane súborov kontrolných bodov modelu, konfiguračných súborov a metrík trénovania.

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

### Testovanie doladeného modelu

**llamafactory-cli chat** je navrhnutý na interaktívny chat/inferenciu s LLM (základnými modelmi aj modelmi doladeným pomocou LoRA). LLaMA-Factory poskytuje ukážkovú konfiguráciu na spustenie inferencie doladených modelov v [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference). Túto ukážkovú konfiguráciu môžete tiež upraviť na zmenu nastavení, napríklad backendu inferencie.

Na testovanie doladeného modelu Qwen3 použite nasledujúci príkaz:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
Príklad chatu s doladeným modelom je zobrazený nižšie:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### Export doladeného modelu

Pre produkčné použitie je potrebné predtrénovaný model a adaptér LoRA zlúčiť a exportovať do jedného modelu. Tento zlúčený model možno používať ako bežný súbor modelu Hugging Face. LLaMA-Factory poskytuje ukážkové konfigurácie v [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora).

Na export doladeného modelu Qwen3 použite nasledujúci príkaz:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
Výsledok exportu doladeného modelu je zobrazený nižšie.

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

## Používanie grafického rozhrania LLaMA-Factory

`LLaMA-Factory` tiež podporuje doladenie LLM bez kódu prostredníctvom webového rozhrania v prehliadači.

Na jeho otvorenie použite nasledujúci príkaz:

```bash
llamafactory-cli webui
```
`LlamaFactory Web UI` ponúka zjednodušené rozhranie na správu pracovných postupov strojového učenia, vrátane trénovania, hodnotenia, predikcie, chatu a exportu modelov. Tu je stručný prehľad jednotlivých záložiek:

* **Train**: Táto záložka umožňuje vybrať model a dataset, nakonfigurovať parametre trénovania a spustiť proces trénovania. Je dôležité porozumieť povinným a voliteľným parametrom na optimalizáciu nastavenia trénovania.
* **Evaluate & Predict**: Po trénovaní môžete pomocou tejto záložky vyhodnotiť výkonnosť modelu a vykonávať predikcie. Poskytuje prehľad o presnosti a účinnosti modelu na nových dátach.
* **Chat**: Po dokončení trénovania načítajte model na záložke Chat, aby ste s ním mohli interagovať a vidieť výsledky svojej práce. Táto funkcia umožňuje komunikáciu s natrénovaným modelom v reálnom čase.
* **Export**: Táto záložka uľahčuje export natrénovaných modelov na nasadenie alebo ďalšie použitie. Modely môžete uložiť v rôznych formátoch vhodných pre rôzne aplikácie.

Pre podrobné pokyny vám odporúčame pozrieť si oficiálnu dokumentáciu v [repozitári LlamaFactory na GitHub](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) a [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest). Okrem toho [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) poskytuje cenné informácie o rozhraní a jeho funkciách.

## Ďalšie kroky
- Vyskúšajte rôzne modely, napríklad `gpt-oss` a iné najmodernejšie modely.
- Experimentujte s rôznymi backendmi na doladenom modeli.
 
Ďalšiu dokumentáciu nájdete na: https://llamafactory.readthedocs.io/en/latest/