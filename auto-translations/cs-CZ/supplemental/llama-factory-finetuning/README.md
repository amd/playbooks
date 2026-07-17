## Přehled

Efektivní doladění je klíčové pro přizpůsobení velkých jazykových modelů (LLM) konkrétním úlohám. LLaMA-Factory je open-source a uživatelsky přívětivá platforma, která zjednodušuje trénování a doladění velkých jazykových modelů a multimodálních modelů. Umožňuje uživatelům lokálně přizpůsobit stovky předtrénovaných modelů s minimálním psaním kódu.

Tento návod vás naučí, jak doladit LLM pomocí LLaMA-Factory na vašem lokálním hardwaru AMD.

<!-- @device:stx,krk -->
> **Poznámka:** Techniky doladění v tomto návodu vyžadují alespoň **32 GB systémové RAM**, přičemž alespoň **16 GB z ní musí být dostupných pro GPU** (těchto 16 GB je součástí 32 GB, nikoli navíc).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Poznámka:** Techniky doladění v tomto návodu vyžadují alespoň **16 GB celkové paměti GPU** a **32 GB systémové RAM**.
> - Ve Windows se celková paměť GPU skládá z vyhrazené VRAM grafické karty a sdílené paměti GPU (vypůjčené ze systémové RAM).
> - Karty s méně než 16 GB vyhrazené VRAM proto mohou tento návod spustit pomocí sdílené paměti GPU, která vyrovná rozdíl.
<!-- @os:end -->

<!-- @os:linux -->
> **Poznámka:** Techniky doladění v tomto návodu vyžadují grafickou kartu s alespoň **16 GB vyhrazené paměti GPU** a **32 GB systémové RAM**.
> - V Linuxu probíhá trénování výhradně ve vyhrazené VRAM grafické karty.
> - Při nedostatku VRAM se nespoléhá na sdílenou paměť GPU (systémovou RAM).
> - Karty s méně než 16 GB vyhrazené VRAM při trénování v Linuxu vyčerpají paměť, i když má systém dostatek RAM.
<!-- @os:end -->
<!-- @device:end -->

## Co se naučíte

- Jak nastavit LLaMA-Factory se softwarem AMD ROCm™
- Jak konfigurovat parametry doladění LLM (jako příklad použijeme Qwen/Qwen3-4B-Instruct-2507)
- Jak spustit doladění pomocí LLaMA-Factory
- Jak spustit inferenci s doladěným modelem
- Jak exportovat doladěný model

## Odhadovaný čas

- Délka: Spuštění tohoto návodu trvá přibližně 60 minut (v závislosti na velikosti modelu/datové sady a rychlosti sítě).
- Další informace naleznete na [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory).

## Nastavení konfigurace paměti

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace softwarových předpokladů

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

#### Vytvoření virtuálního prostředí

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
**Udělte svému uživateli přístup k zařízením GPU** (pro aktivaci se odhlaste a znovu přihlaste):

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

### Instalace základních závislostí

<!-- @require:pytorch,driver -->
 
### Instalace dalších závislostí

> **Poznámka**: Ujistěte se, že verze Pythonu je 3.11, 3.12 nebo 3.13

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

### Instalace LLaMA-Factory

LLaMA-Factory závisí na PyTorch. Ten byste již měli mít nainstalovaný podle výše uvedených požadavků.

Stáhněte zdrojový kód z [oficiálního repozitáře LLaMA Factory na GitHub](https://github.com/hiyouga/LlamaFactory) a nainstalujte jeho závislosti.

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

Ověřte, zda je `llamafactory-cli` spustitelný.

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

Příklad výstupu:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

Po úspěšné instalaci LLaMA-Factory spustíme doladění.

## Použití LLaMA Factory CLI pro doladění

Tato část popisuje, jak připravit datové sady pro doladění, konfigurovat parametry LoRA/QLoRA a spustit doladění pomocí LoRA.

### Příprava datové sady

LLaMA-Factory podporuje datové sady pro doladění ve formátu Alpaca a ShareGPT. Všechny dostupné datové sady jsou definovány v souboru [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). Pokud používáte vlastní datovou sadu, nezapomeňte přidat popis datové sady do `dataset_info.json` a před trénováním zadat název datové sady. Podrobnosti naleznete v jejich dokumentaci [zde](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

V tomto návodu použijeme jako příklad datové sady identity a alpaca_en_demo a informace o datové sadě nakonfigurujeme v dalším kroku.


### Konfigurace parametrů doladění

LLaMA-Factory podporuje více schémat doladění.

| Schémata doladění | Příklady LLaMA-Factory |
|-----------|------|
| Úplné parametry    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| Doladění LoRA  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| Doladění QLoRA | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

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

Tyto ukázkové konfigurační soubory obsahují parametry modelu, parametry metody doladění, parametry datové sady, parametry vyhodnocení a další. Můžete je nakonfigurovat podle vlastních potřeb. V tomto návodu použijeme soubor [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml).

**Vysvětlení klíčových parametrů:**
- `model_name_or_path` – Název modelu na Hugging Face nebo cesta k lokálnímu souboru modelu.
- `stage` – Fáze trénování. Možnosti: rm (reward modeling), pt (pretrain), sft (Supervised Fine-Tuning), PPO, DPO, KTO, ORPO.
- `do_train` – true pro trénování, false pro vyhodnocení.
- `finetuning_type` – Metoda doladění. Možnosti: freeze, lora, full.
- `lora_rank` – Dimenzionalita matice nízkého ranku používané v LoRA, typické hodnoty: 4, 6, 8, 16 (nižší hodnoty = méně parametrů = rychlejší doladění; vyšší hodnoty = lepší přizpůsobení úloze, ale vyšší nároky na zdroje).
- `lora_target` – Cílové moduly pro metodu LoRA. Výchozí hodnota: all.
- `dataset` – Datová sada (sady) k použití. Pro oddělení více datových sad použijte „,".
- `output_dir` – Výstupní cesta doladění.
- `logging_steps` – Interval protokolování v krocích.
- `save_steps` – Interval ukládání kontrolních bodů modelu.
- `overwrite_output_dir` – Zda povolit přepsání výstupního adresáře.
- `per_device_train_batch_size` – Velikost trénovací dávky na zařízení.
- `gradient_accumulation_steps` – Počet kroků akumulace gradientu.
- `learning_rate` – Rychlost učení.
- `num_train_epochs` – Počet trénovacích epoch.
- `lr_scheduler_type` – Plán rychlosti učení. Možnosti: linear, cosine, polynomial, constant atd.
- `warmup_ratio` – Poměr zahřívání rychlosti učení.

<!-- @os:linux -->
Upravíme výchozí hodnotu `lora_rank` pro spuštění doladění na GPU AMD Ryzen™ a AMD Radeon™.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
Aktualizujeme výchozí konfiguraci doladění LoRA pro lepší kompatibilitu s GPU AMD Ryzen™ a AMD Radeon™:
- Nastavíme `lora_rank` z hodnoty `8` na `6`, aby se snížilo využití paměti během doladění.
- Místo `bf16` použijeme `fp16` pro širší kompatibilitu s GPU AMD a nižší využití paměti.
- Na Windows nastavíme `dataloader_num_workers` na `0`, aby se předešlo chybám `"Can't pickle local object<>"` způsobeným načítáním dat pomocí multiprocessingu.

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

### Spuštění doladění pomocí LLaMA-Factory

**llamafactory-cli** je oficiální nástroj příkazového řádku (CLI) pro LLaMA-Factory, vyvinutý pro zjednodušení kompletních pracovních postupů s LLM (příprava dat → doladění → vyhodnocení → nasazení) bez psaní složitého kódu.

Pro trénování/doladění je **llamafactory-cli train** hlavním dílčím příkazem CLI LLaMA-Factory. Abstrahuje pracovní postupy doladění (předzpracování dat, ladění hyperparametrů, optimalizace hardwaru) do jediného příkazu CLI, podporuje více paradigmat doladění (LoRA/QLoRA/úplné doladění) a je optimalizován pro GPU s omezenými zdroji (např. QLoRA na 16 GB VRAM).

Doladění pomocí LLaMA-Factory můžete spustit následujícím příkazem, který vychází z upraveného konfiguračního souboru pro doladění Qwen3 pomocí LoRA.

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

Po spuštění doladění LLM jsou všechny vygenerované výstupy uloženy v adresáři „output_dir", včetně souborů kontrolních bodů modelu, konfiguračních souborů a metrik trénování.

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

### Testování doladěného modelu

**llamafactory-cli chat** je navržen pro interaktivní chat/inferenci s LLM (jak základními modely, tak modely doladěnými pomocí LoRA). LLaMA-Factory poskytuje ukázkovou konfiguraci pro spuštění inference doladěných modelů v adresáři [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference). Tuto ukázkovou konfiguraci můžete také upravit a změnit nastavení, například backend pro inferenci.

Pomocí následujícího příkazu otestujte doladěný model Qwen3:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
Níže je uveden příklad chatu s doladěným modelem:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### Export doladěného modelu

Pro produkční použití je nutné sloučit předtrénovaný model a adaptér LoRA a exportovat je jako jeden model. Tento sloučený model lze použít jako běžný soubor modelu Hugging Face. LLaMA-Factory poskytuje ukázkové konfigurace v adresáři [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora).

Pomocí následujícího příkazu exportujte doladěný model Qwen3:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
Výsledek exportu doladěného modelu je zobrazen níže.

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

## Použití grafického rozhraní LLaMA-Factory

`LLaMA-Factory` také podporuje doladění LLM bez psaní kódu prostřednictvím webového uživatelského rozhraní v prohlížeči.

Pro jeho otevření použijte následující příkaz:

```bash
llamafactory-cli webui
```
`LlamaFactory Web UI` nabízí přehledné rozhraní pro správu pracovních postupů strojového učení, včetně trénování, vyhodnocení, predikce, chatu a exportu modelů. Zde je stručný úvod k jednotlivým záložkám:

* **Train**: Tato záložka umožňuje vybrat model a datovou sadu, nakonfigurovat parametry trénování a zahájit proces trénování. Pro optimalizaci nastavení trénování je důležité porozumět povinným a volitelným parametrům.
* **Evaluate & Predict**: Po trénování můžete pomocí této záložky vyhodnotit výkon modelu a provádět predikce. Poskytuje přehled o přesnosti a účinnosti modelu na nových datech.
* **Chat**: Po dokončení trénování načtěte model na záložce Chat, abyste s ním mohli interagovat a prohlédnout si výsledky své práce. Tato funkce umožňuje komunikaci s natrénovaným modelem v reálném čase.
* **Export**: Tato záložka usnadňuje export natrénovaných modelů pro nasazení nebo další použití. Modely lze ukládat v různých formátech vhodných pro různé aplikace.

Podrobné pokyny naleznete v oficiální dokumentaci na [repozitáři LlamaFactory na GitHub](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) a v dokumentaci [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest). Cenné informace o rozhraní a jeho funkcích poskytuje také [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui).

## Další kroky
- Vyzkoušejte různé modely, například `gpt-oss` a další nejmodernější modely.
- Experimentujte s různými backendy na doladěném modelu.
 
Další dokumentaci naleznete na: https://llamafactory.readthedocs.io/en/latest/