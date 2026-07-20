## Översikt

Effektiv finjustering är avgörande för att anpassa stora språkmodeller (LLM:er) till specifika nedströmsuppgifter. LLaMA Factory är en öppen källkodsplattform som är enkel att använda och som effektiviserar träning och finjustering av stora språkmodeller och multimodala modeller. Den låter användare anpassa hundratals förtränade modeller lokalt med minimal kodning.

Denna handbok lär dig hur du finjusterar LLM:er med hjälp av LLaMA Factory på din lokala AMD-hårdvara.

<!-- @device:stx,krk -->
> **Obs:** Finjusteringsteknikerna i den här handboken kräver minst **32 GB systemminne (RAM)**, där minst **16 GB av det är tillgängligt för GPU:n** (dessa 16 GB ingår i de 32 GB, inte utöver dem).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Obs:** Finjusteringsteknikerna i den här handboken kräver minst **16 GB totalt GPU-minne** och **32 GB systemminne (RAM)**.
> - I Windows kombinerar det totala GPU-minnet grafikkortets dedikerade VRAM med delat GPU-minne (lånat från systemminnet).
> - Därför kan kort med mindre än 16 GB dedikerat VRAM ändå köra den här handboken genom att använda delat GPU-minne för att kompensera skillnaden.
<!-- @os:end -->

<!-- @os:linux -->
> **Obs:** Finjusteringsteknikerna i den här handboken kräver ett grafikkort med minst **16 GB dedikerat GPU-minne** och **32 GB systemminne (RAM)**.
> - I Linux körs träningen helt i grafikkortets dedikerade VRAM.
> - Den faller inte tillbaka på delat GPU-minne (systemminne) när VRAM tar slut.
> - Kort med mindre än 16 GB dedikerat VRAM kommer att få slut på minne under träning i Linux, även om systemet har gott om RAM.
<!-- @os:end -->
<!-- @device:end -->

## Vad du kommer att lära dig

- Hur du konfigurerar LLaMA Factory med AMD ROCm™-programvara
- Hur du konfigurerar parametrar för finjustering av LLM (med Qwen/Qwen3-4B-Instruct-2507 som exempel)
- Hur du kör finjustering med LLaMA Factory
- Hur du kör inferens med den finjusterade modellen
- Hur du exporterar den finjusterade modellen 

## Uppskattad tid

- Varaktighet: Det tar cirka 60 minuter att köra den här handboken (beroende på storleken på din modell/dataset och nätverkshastighet).
- Se [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory) för mer information.

## Ställa in minneskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrollera efter programvaruuppdateringar

<!-- @require:software-update -->
<!-- @device:end -->

## Installera nödvändig programvara

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

LLaMA Factory bygger på PyTorch. Du bör redan ha det installerat enligt kraven ovan.

Ladda ner källkoden från [LLaMA Factorys officiella GitHub-repository](https://github.com/hiyouga/LlamaFactory), och installera dess beroenden.

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

Verifiera att `llamafactory-cli` går att köra.

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

Exempel på utdata:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

Efter att ha installerat LLaMA Factory ska vi nu köra finjustering med den.

## Använda LLaMA Factory CLI för finjustering 

Detta avsnitt beskriver hur du förbereder dataset för finjustering, konfigurerar LoRA/QLoRA-parametrar och kör LoRA-finjustering.

### Förberedelse av dataset

LLaMA Factory stöder dataset för finjustering i formaten Alpaca och ShareGPT. Alla tillgängliga dataset har definierats i [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). Om du använder ett anpassat dataset, se till att lägga till en datasetbeskrivning i `dataset_info.json` och ange datasetnamnet innan träning. Mer information finns i deras dokumentation [här](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

I den här handboken använder vi dataseten identity och alpaca_en_demo som exempel, och konfigurerar datasetinformationen i nästa steg.
### Konfigurera parametrar för finjustering

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

Dessa exempelkonfigurationsfiler har angivna modellparametrar, parametrar för finjusteringsmetod, datasetparametrar, utvärderingsparametrar med mera. Du kan konfigurera dem enligt dina egna behov. I den här handledningen använder vi [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml). 

**Viktiga parametrar förklarade:**
- `model_name_or_path` - Hugging Face-modellnamn eller lokal sökväg till modellfil.
- `stage` - Träningssteg. Alternativ: rm (reward modeling), pt (pretrain), sft (Supervised Fine-Tuning), PPO, DPO, KTO, ORPO.
- `do_train` - true för träning, false för utvärdering
- `finetuning_type` - Finjusteringsmetod. Alternativ: freeze, lora, full
- `lora_rank` - Dimensionaliteten på den lågrangade matris som används i LoRA, typiska värden: 4, 6, 8, 16 (mindre värden = färre parametrar = snabbare finjustering; större värden = bättre anpassning till uppgiften men högre resursförbrukning).
- `lora_target` - Målmoduler för LoRA-metoden. Standard: all.
- `dataset` - Dataset som ska användas. Använd ”,” för att separera flera dataset
- `output_dir` - Utdatasökväg för finjustering
- `logging_steps` - Loggningsintervall i steg
- `save_steps` - Intervall för sparande av modellkontrollpunkter.
- `overwrite_output_dir` - Om det ska vara tillåtet att skriva över utdatakatalogen.
- `per_device_train_batch_size` - Träningsbatchstorlek per enhet.
- `gradient_accumulation_steps` - Antal steg för gradientackumulering.
- `learning_rate` - Inlärningshastighet
- `num_train_epochs` - Antal träningsepoker
- `lr_scheduler_type` - Schema för inlärningshastighet. Alternativ: linear, cosine, polynomial, constant med mera.
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
- Ställ in `dataloader_num_workers` till `0` på Windows för att undvika `"Can't pickle local object<>"`-fel som orsakas av dataladdning med flera processer.

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

### Kör finjustering med LLaMA Factory 

**llamafactory-cli** är det officiella kommandoradsverktyget (CLI) för LLaMA Factory, utvecklat för att förenkla arbetsflöden för LLM från början till slut (dataförberedelse → finjustering → utvärdering → driftsättning) utan att behöva skriva komplex kod.

För träning/finjustering är **llamafactory-cli train** kärnkommandot i LLaMA Factory CLI. Det abstraherar arbetsflöden för finjustering (dataförbehandling, hyperparameteroptimering, hårdvaruoptimering) till ett enda CLI-kommando, med stöd för flera finjusteringsparadigm (LoRA/QLoRA/Full Fine-Tuning) och är optimerat för GPU:er med begränsade resurser (t.ex. QLoRA på 16 GB VRAM).

Du kan köra finjustering med LLaMA Factory med hjälp av följande kommando, som baseras på den ändrade konfigurationsfilen för Qwen3 LoRA-finjustering.

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

Efter att LLM-finjusteringen har körts lagras all genererad utdata i "output_dir", inklusive filer för modellkontrollpunkter, konfigurationsfiler och träningsmått.

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

**llamafactory-cli chat** är utformat för interaktiv chatt/inferens med LLM (både basmodeller och LoRA-finjusterade modeller). LLaMA Factory tillhandahåller exempelkonfigurationen för att köra inferens av finjusterade modeller i [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference). Du kan även ändra denna exempelkonfiguration för att ändra inställningarna, t.ex. inferensbackend.

Använd följande kommando för att testa den finjusterade Qwen3-modellen:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
Ett exempel på en chatt med den finjusterade modellen visas nedan:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### Exportera den finjusterade modellen

För produktionsanvändning behöver den förtränade modellen och LoRA-adaptern slås samman och exporteras till en enda modell. Denna sammanslagna modell kan användas som en vanlig Hugging Face-modellfil. LLaMA Factory tillhandahåller exempelkonfigurationer i [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora).

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

`LLaMA-Factory` stöder även kodfri finjustering av LLM:er via ett webbgränssnitt i webbläsaren.

Använd följande kommando för att öppna det:

```bash
llamafactory-cli webui
```
`LlamaFactory Web UI` erbjuder ett strömlinjeformat gränssnitt för att hantera maskininlärningsflöden, inklusive träning, utvärdering, prediktion, chatt och export av modeller. Här är en kort introduktion till varje flik:

* **Train**: Med den här fliken kan du välja en modell och ett dataset, konfigurera träningsparametrar och starta träningsprocessen. Det är viktigt att förstå de obligatoriska och valfria parametrarna för att optimera träningsinställningarna.
* **Evaluate & Predict**: Efter träningen kan du utvärdera modellens prestanda och göra prediktioner med den här fliken. Den ger insikter i modellens noggrannhet och effektivitet på ny data.
* **Chat**: När träningen är klar kan du ladda modellen i fliken Chat för att interagera med den och se resultatet av ditt arbete. Den här funktionen möjliggör kommunikation i realtid med den tränade modellen.
* **Export**: Den här fliken underlättar export av tränade modeller för driftsättning eller vidare användning. Du kan spara dina modeller i olika format som lämpar sig för olika tillämpningar.

För detaljerad vägledning uppmuntrar vi dig att läsa den officiella dokumentationen på [LlamaFactory GitHub-repositoriet](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) och [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest). Dessutom ger [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) värdefulla insikter i gränssnittet och dess funktioner.

## Nästa steg
- Prova olika modeller som `gpt-oss` och andra toppmoderna modeller.
- Experimentera med olika backends på den finjusterade modellen
 
För mer dokumentation, besök: https://llamafactory.readthedocs.io/en/latest/