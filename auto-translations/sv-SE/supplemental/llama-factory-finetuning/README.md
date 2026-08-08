<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinöversättning.** Den här sidan har automatiskt översatts från engelska och har inte granskats av en människa. Den kan innehålla fel, och vissa instruktioner, kommandon, nedladdningar, produkttillgänglighet eller annat innehåll kan variera beroende på språk eller region. Vid eventuella motsägelser eller avvikelser är det den ursprungliga engelska versionen av playbook som gäller och har företräde.
<!-- auto-translated-disclaimer:end -->

## Översikt

Effektiv finjustering är avgörande för att anpassa stora språkmodeller (LLM) till nedströmsuppgifter. LLaMA Factory är en öppen källkodsplattform som är enkel att använda och som effektiviserar träning och finjustering av stora språkmodeller och multimodala modeller. Den gör det möjligt för användare att anpassa hundratals förtränade modeller lokalt med minimal kodning.

Denna handbok lär dig hur du finjusterar LLM med LLaMA Factory på din lokala AMD-hårdvara.

<!-- @device:stx,krk -->
> **Obs:** Finjusteringsteknikerna i denna handbok kräver minst **32 GB systemminne**, varav minst **16 GB måste vara tillgängligt för GPU:n** (dessa 16 GB ingår i de 32 GB, inte utöver dem).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Obs:** Finjusteringsteknikerna i denna handbok kräver minst **16 GB totalt GPU-minne** och **32 GB systemminne**.
> - I Windows kombinerar det totala GPU-minnet grafikkortets dedikerade VRAM med delat GPU-minne (lånat från systemminnet).
> - Därför kan kort med mindre än 16 GB dedikerat VRAM ändå köra denna handbok genom att använda delat GPU-minne för att täcka skillnaden.
<!-- @os:end -->

<!-- @os:linux -->
> **Obs:** Finjusteringsteknikerna i denna handbok kräver ett grafikkort med minst **16 GB dedikerat GPU-minne** och **32 GB systemminne**.
> - I Linux körs träningen helt i grafikkortets dedikerade VRAM.
> - Den faller inte tillbaka på delat GPU-minne (systemminne) när VRAM tar slut.
> - Kort med mindre än 16 GB dedikerat VRAM kommer att få slut på minne under träning i Linux, även om systemet har gott om RAM.
<!-- @os:end -->
<!-- @device:end -->

## Vad du kommer att lära dig

- Hur du konfigurerar LLaMA Factory med AMD ROCm™-programvara
- Hur du konfigurerar parametrar för LLM-finjustering (med Qwen/Qwen3-4B-Instruct-2507 som exempel)
- Hur du kör LLaMA Factory-finjustering
- Hur du kör inferens med den finjusterade modellen
- Hur du exporterar den finjusterade modellen 

## Uppskattad tid

- Varaktighet: Det tar cirka 60 minuter att köra denna handbok (beroende på storleken på din modell/dataset och nätverkshastighet).
- Se [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory) för mer information.

## Konfigurera minnesinställningarna

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrollera programvaruuppdateringar

<!-- @require:software-update -->
<!-- @device:end -->

## Installera programvaruförutsättningar

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

#### Skapa en virtuell miljö

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
**Ge din användare åtkomst till GPU-enheter** (logga ut och in igen för att detta ska träda i kraft):

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

### Installera grundläggande beroenden

<!-- @require:pytorch,driver -->
 
### Installera ytterligare beroenden

> **Obs**: Se till att Python-versionen är 3.11, 3.12 eller 3.13

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

### Installera LLaMA Factory

LLaMA Factory är beroende av PyTorch. Du bör redan ha det installerat enligt kraven ovan.

Ladda ner källkoden från [LLaMA Factorys officiella GitHub-repository](https://github.com/hiyouga/LlamaFactory) och installera dess beroenden.

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

Verifiera om `llamafactory-cli` går att köra.

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

Exempelresultat:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

Nu när du har installerat LLaMA Factory, låt oss köra finjustering med den.

## Använda LLaMA Factory CLI för finjustering 

Detta avsnitt beskriver hur du förbereder finjusteringsdataset, konfigurerar LoRA/QLoRA-parametrar och kör LoRA-finjustering.

### Förberedelse av dataset

LLaMA Factory stöder finjusteringsdataset i formaten Alpaca och ShareGPT. Alla tillgängliga dataset har definierats i [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). Om du använder ett anpassat dataset, se till att lägga till en datasetbeskrivning i `dataset_info.json` och ange datasetnamnet innan träningen. Detaljer finns i deras dokumentation [här](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

I denna handbok använder vi dataseten identity och alpaca_en_demo som exempel och konfigurerar datasetinformationen i nästa steg.
### Konfiguration av finjusteringsparametrar

LLaMA Factory stöder flera olika finjusteringsscheman.

| Finjusteringsscheman | LLaMA Factory-exempel |
|-----------|------|
| Full-Parameter    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| LoRA-finjustering  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| QLoRA-finjustering | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

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

Dessa exempelkonfigurationsfiler har angett modellparametrar, parametrar för finjusteringsmetod, datasetparametrar, utvärderingsparametrar med mera. Du kan konfigurera dem enligt dina egna behov. I den här handboken kommer vi att använda [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml). 

**Förklaring av viktiga parametrar:**
- `model_name_or_path` - Namn på Hugging Face-modell eller lokal sökväg till modellfil.
- `stage` - Träningssteg. Alternativ: rm (reward modeling), pt (förträning), sft (Supervised Fine-Tuning), PPO, DPO, KTO, ORPO.
- `do_train` - true för träning, false för utvärdering
- `finetuning_type` - Finjusteringsmetod. Alternativ: freeze, lora, full
- `lora_rank` - Dimensionaliteten hos den lågrangade matris som används i LoRA, typiska värden: 4, 6, 8, 16 (mindre värden = färre parametrar = snabbare finjustering; större värden = bättre uppgiftsanpassning men högre resursanvändning).
- `lora_target` - Målmoduler för LoRA-metoden. Standard: all.
- `dataset` - Dataset som ska användas. Använd "," för att separera flera dataset
- `output_dir` - Utdatasökväg för finjustering
- `logging_steps` - Loggningsintervall i steg
- `save_steps` - Intervall för sparande av modellcheckpoints.
- `overwrite_output_dir` - Om det ska vara tillåtet att skriva över utdatakatalogen.
- `per_device_train_batch_size` - Träningsbatchstorlek per enhet.
- `gradient_accumulation_steps` - Antal steg för gradientackumulering.
- `learning_rate` - Inlärningshastighet
- `num_train_epochs` - Antal träningsepoker
- `lr_scheduler_type` - Schema för inlärningshastighet. Alternativ: linear, cosine, polynomial, constant, etc.
- `warmup_ratio` - Uppvärmningskvot för inlärningshastighet

<!-- @os:linux -->
Vi kommer att ändra standardvärdet för `lora_rank` för att köra finjustering på AMD Ryzen™- och AMD Radeon™-GPU:er.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
Vi kommer att uppdatera standardkonfigurationen för LoRA-finjustering för bättre kompatibilitet med AMD Ryzen™- och AMD Radeon™-GPU:er:
- Ändra `lora_rank` från `8` till `6` för att minska minnesanvändningen under finjustering.
- Använd `fp16` istället för `bf16` för bredare kompatibilitet med AMD-GPU:er och lägre minnesanvändning.
- Ställ in `dataloader_num_workers` till `0` på Windows för att undvika felen `"Can't pickle local object<>"` som orsakas av multiprocessorbaserad datainläsning.

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

### Kör LLaMA Factory-finjustering 

**llamafactory-cli** är det officiella kommandoradsverktyget (CLI) för LLaMA Factory, utvecklat för att förenkla hela LLM-arbetsflödet (dataförberedelse → finjustering → utvärdering → driftsättning) utan att behöva skriva komplex kod.

För träning/finjustering är **llamafactory-cli train** kärnkommandot i LLaMA Factory CLI. Det abstraherar finjusteringsarbetsflöden (dataförbehandling, hyperparameterjustering, hårdvaruoptimering) till ett enda CLI-kommando, stöder flera finjusteringsparadigm (LoRA/QLoRA/Full Fine-Tuning) och är optimerat för GPU:er med begränsade resurser (t.ex. QLoRA på 16 GB VRAM).

Du kan köra LLaMA Factory-finjustering med följande kommando, som baseras på den modifierade konfigurationsfilen för Qwen3 LoRA-finjustering.

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

Efter att LLM-finjusteringen körts lagras alla genererade utdata i "output_dir", inklusive modellcheckpointfiler, konfigurationsfiler och träningsmått.

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

### Testa den finjusterade modellen 

**llamafactory-cli chat** är utformat för interaktiv chatt/inferens med LLM:er (både basmodeller och LoRA-finjusterade modeller). LLaMA Factory tillhandahåller exempelkonfigurationen för att köra inferens med finjusterade modeller i [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference). Du kan också ändra denna exempelkonfiguration för att ändra inställningarna, t.ex. inferensbackend.

Använd följande kommando för att testa den finjusterade Qwen3-modellen:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
Ett exempel på en chatt med den finjusterade modellen visas nedan:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### Exportera den finjusterade modellen

För produktionsanvändningsfall behöver den förtränade modellen och LoRA-adaptern slås samman och exporteras till en enda modell. Denna sammanslagna modell kan användas som en vanlig Hugging Face-modellfil. LLaMA Factory tillhandahåller exempelkonfigurationer i [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora).

Använd följande kommando för att exportera den finjusterade Qwen3-modellen:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
Resultatet av att exportera den finjusterade modellen visas nedan.

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
## Använda LLaMA Factory GUI

`LLaMA-Factory` stöder också nollkodsfinjustering av LLM:er via ett webbgränssnitt i webbläsaren.

Använd följande kommando för att öppna det:

```bash
llamafactory-cli webui
```
`LlamaFactory Web UI` erbjuder ett strömlinjeformat gränssnitt för att hantera arbetsflöden för maskininlärning, inklusive träning, utvärdering, förutsägelse, chatt och export av modeller. Här är en kort introduktion till varje flik:

* **Train**: Med den här fliken kan du välja en modell och ett dataset, konfigurera träningsparametrar och starta träningsprocessen. Det är viktigt att förstå de obligatoriska och valfria parametrarna för att optimera träningsuppsättningen.
* **Evaluate & Predict**: Efter träningen kan du utvärdera modellens prestanda och göra förutsägelser med hjälp av den här fliken. Den ger insikter om modellens noggrannhet och effektivitet på ny data.
* **Chat**: När träningen är klar, ladda modellen i fliken Chat för att interagera med den och se resultaten av ditt arbete. Med den här funktionen kan du kommunicera med den tränade modellen i realtid.
* **Export**: Den här fliken underlättar exporten av tränade modeller för driftsättning eller vidare användning. Du kan spara dina modeller i olika format som passar för olika tillämpningar.

För detaljerad vägledning uppmuntrar vi dig att läsa den officiella dokumentationen i [LlamaFactory GitHub-repositoriet](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) och [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest). Dessutom ger [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) värdefulla insikter om gränssnittet och dess funktioner.

## Nästa steg
- Prova olika modeller som `gpt-oss` och andra toppmoderna modeller.
- Experimentera med olika backends på den finjusterade modellen
 
För mer dokumentation, besök: https://llamafactory.readthedocs.io/en/latest/