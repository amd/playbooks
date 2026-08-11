<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversættelse.** Denne side er automatisk oversat fra engelsk og er ikke blevet gennemgået af et menneske. Den kan indeholde fejl, og visse instruktioner, kommandoer, downloads, produkttilgængelighed eller andet indhold kan variere afhængigt af sprog eller region. I tilfælde af uoverensstemmelse eller afvigelse er den oprindelige engelske version af playbook'en gældende og har forrang.
<!-- auto-translated-disclaimer:end -->

## Oversigt

Effektiv finjustering er afgørende for at tilpasse store sprogmodeller (LLM'er) til specifikke opgaver. LLaMA Factory er en open source og brugervenlig platform, der effektiviserer træning og finjustering af store sprogmodeller og multimodale modeller. Den giver brugere mulighed for at tilpasse hundredvis af foruddannede modeller lokalt med minimal kodning.

Denne playbook lærer dig, hvordan du finjusterer LLM'er ved hjælp af LLaMA Factory på din lokale AMD-hardware.

<!-- @device:stx,krk -->
> **Bemærk:** Finjusteringsteknikkerne i denne playbook kræver mindst **32 GB systemhukommelse**, hvoraf mindst **16 GB skal være tilgængelig for GPU'en** (de 16 GB er en del af de 32 GB, ikke i tillæg til dem).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Bemærk:** Finjusteringsteknikkerne i denne playbook kræver mindst **16 GB samlet GPU-hukommelse** og **32 GB systemhukommelse**.
> - På Windows kombinerer den samlede GPU-hukommelse grafikkortets dedikerede VRAM med delt GPU-hukommelse (lånt fra systemhukommelsen).
> - Derfor kan kort med mindre end 16 GB dedikeret VRAM stadig køre denne playbook ved at bruge delt GPU-hukommelse til at udligne forskellen.
<!-- @os:end -->

<!-- @os:linux -->
> **Bemærk:** Finjusteringsteknikkerne i denne playbook kræver et grafikkort med mindst **16 GB dedikeret GPU-hukommelse** og **32 GB systemhukommelse**.
> - På Linux kører træningen udelukkende i grafikkortets dedikerede VRAM.
> - Den falder ikke tilbage til delt GPU-hukommelse (systemhukommelse), når VRAM løber tør.
> - Kort med mindre end 16 GB dedikeret VRAM vil løbe tør for hukommelse under træning på Linux, selv hvis systemet har rigelig RAM.
<!-- @os:end -->
<!-- @device:end -->

## Hvad du vil lære

- Hvordan man opsætter LLaMA Factory med AMD ROCm™-software
- Hvordan man konfigurerer parametre for LLM-finjustering (med Qwen/Qwen3-4B-Instruct-2507 som eksempel)
- Hvordan man kører finjustering med LLaMA Factory
- Hvordan man kører inferens med den finjusterede model
- Hvordan man eksporterer den finjusterede model

## Estimeret tid

- Varighed: Det tager cirka 60 minutter at gennemføre denne playbook (afhængigt af din model-/datasætstørrelse og netværkshastighed).
- Se [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory) for mere information.

## Indstilling af hukommelseskonfiguration

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tjek for softwareopdateringer

<!-- @require:software-update -->
<!-- @device:end -->

## Installation af softwareforudsætninger

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

#### Opret et virtuelt miljø

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
**Giv din bruger adgang til GPU-enheder** (log ud og ind igen, for at dette træder i kraft):

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

### Installation af grundlæggende afhængigheder

<!-- @require:pytorch,driver -->
 
### Installation af yderligere afhængigheder

> **Bemærk**: Sørg for, at Python-versionen er 3.11, 3.12 eller 3.13

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

### Installer LLaMA Factory

LLaMA Factory afhænger af PyTorch. Du burde allerede have det installeret i henhold til ovenstående krav.

Download kildekoden fra [LLaMA Factorys officielle GitHub-repository](https://github.com/hiyouga/LlamaFactory), og installer dens afhængigheder.

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

Bekræft, at `llamafactory-cli` kan eksekveres.

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

Eksempel på output:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

Efter at have installeret LLaMA Factory med succes, lad os køre finjustering med den.

## Brug af LLaMA Factory CLI til finjustering

Dette afsnit dækker, hvordan man forbereder finjusteringsdatasæt, konfigurerer LoRA/QLoRA-parametre, og kører LoRA-finjustering.

### Forberedelse af datasæt

LLaMA Factory understøtter finjusteringsdatasæt i Alpaca-format og ShareGPT-format. Alle tilgængelige datasæt er defineret i [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). Hvis du bruger et brugerdefineret datasæt, skal du sørge for at tilføje en datasætbeskrivelse i `dataset_info.json` og angive datasættets navn før træning. Detaljer kan findes i deres dokumentation [her](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

I denne playbook vil vi bruge identity- og alpaca_en_demo-datasættene som eksempel og konfigurere datasætinformationen i det næste trin.
### Konfiguration af finetuning-parametre

LLaMA Factory understøtter flere finetuning-metoder.

| Finetuning-metode | LLaMA Factory-eksempler |
|-----------|------|
| Full-Parameter    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| LoRA fine-tuning  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| QLoRA fine-tuning | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

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

Disse eksempel-konfigurationsfiler har angivet modelparametre, parametre for finetuning-metoden, datasæt-parametre, evalueringsparametre med mere. Du kan konfigurere dem efter dine egne behov. I denne playbook bruger vi [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml). 

**Vigtige parametre forklaret:**
- `model_name_or_path` - Hugging Face-modelnavn eller lokal filsti til modellen.
- `stage` - Træningsfase. Muligheder: rm (reward modeling), pt (pretrain), sft (Supervised Fine-Tuning), PPO, DPO, KTO, ORPO.
- `do_train` - true for træning, false for evaluering
- `finetuning_type` - Finetuning-metode. Muligheder: freeze, lora, full
- `lora_rank` - Dimensionaliteten af den lavrangerede matrix, der bruges i LoRA, typiske værdier: 4, 6, 8, 16 (mindre værdier = færre parametre = hurtigere finetuning; større værdier = bedre tilpasning til opgaven, men højere ressourceforbrug).
- `lora_target` - Målmoduler for LoRA-metoden. Standard: all.
- `dataset` - Datasæt, der skal bruges. Brug “,” til at adskille flere datasæt
- `output_dir` - Output-sti for finetuning
- `logging_steps` - Interval for logning i antal trin
- `save_steps` - Interval for gemning af modelcheckpoints.
- `overwrite_output_dir` - Om det er tilladt at overskrive output-mappen.
- `per_device_train_batch_size` - Trænings-batchstørrelse pr. enhed.
- `gradient_accumulation_steps` - Antal trin for gradientakkumulering.
- `learning_rate` - Læringsrate
- `num_train_epochs` - Antal træningsepoker
- `lr_scheduler_type` - Læringsrate-skema. Muligheder: linear, cosine, polynomial, constant osv.
- `warmup_ratio` - Opvarmningsandel for læringsrate

<!-- @os:linux -->
Vi vil ændre standardværdien af `lora_rank` for at køre finetuning på AMD Ryzen™ & AMD Radeon™ GPU'er.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
Vi opdaterer standardkonfigurationen for LoRA-finetuning for bedre kompatibilitet med AMD Ryzen™ og AMD Radeon™ GPU'er:
- Sæt `lora_rank` fra `8` til `6` for at reducere hukommelsesforbruget under finetuning.
- Brug `fp16` i stedet for `bf16` for bredere kompatibilitet med AMD GPU'er og lavere hukommelsesforbrug.
- Sæt `dataloader_num_workers` til `0` på Windows for at undgå `"Can't pickle local object<>"`-fejl forårsaget af multiprocessing-dataindlæsning.

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

### Kør LLaMA Factory-finetuning 

**llamafactory-cli** er det officielle kommandolinjeværktøj (CLI) til LLaMA Factory, udviklet for at forenkle end-to-end LLM-arbejdsgange (dataforberedelse → finetuning → evaluering → deployment) uden at skulle skrive kompleks kode.

Til træning/finetuning er **llamafactory-cli train** den centrale underkommando i LLaMA Factory CLI'en. Den abstraherer finetuning-arbejdsgange (databehandling, hyperparameterjustering, hardwareoptimering) til en enkelt CLI-kommando, understøtter flere finetuning-paradigmer (LoRA/QLoRA/Full Fine-Tuning) og er optimeret til GPU'er med begrænsede ressourcer (f.eks. QLoRA på 16 GB VRAM).

Du kan køre LLaMA Factory-finetuning med følgende kommando, som er baseret på den modificerede konfigurationsfil til Qwen3 LoRA-finetuning.

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

Efter kørsel af LLM-finetuning gemmes alt genereret output i "output_dir", herunder modelcheckpoint-filer, konfigurationsfiler og træningsmålinger.

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

### Test den finetunede model 

**llamafactory-cli chat** er designet til interaktiv chat/inferens med LLM'er (både basismodeller og LoRA-finetunede modeller). LLaMA Factory tilbyder eksempelkonfigurationen til at køre inferens på finetunede modeller i [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference). Du kan også ændre denne eksempelkonfiguration for at justere indstillingerne, f.eks. inferens-backenden.

Brug følgende kommando til at teste den finetunede Qwen3-model:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
Et eksempel på en chat med den finetunede model er vist nedenfor:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### Eksportér den finetunede model

Til produktionsscenarier skal den fortrænede model og LoRA-adapteren flettes sammen og eksporteres til en enkelt model. Denne flettede model kan bruges som en almindelig Hugging Face-modelfil. LLaMA Factory tilbyder eksempelkonfigurationerne i [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora).

Brug følgende kommando til at eksportere den finetunede Qwen3-model:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
Resultatet af eksporten af den finetunede model er vist nedenfor.

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
## Brug af LLaMA Factory GUI

`LLaMA-Factory` understøtter også kodefri finjustering af LLM'er gennem en webbrugerflade i browseren.

Brug følgende kommando til at åbne den:

```bash
llamafactory-cli webui
```
`LlamaFactory Web UI` tilbyder en strømlinet grænseflade til at administrere maskinlæringsarbejdsgange, herunder træning, evaluering, forudsigelse, chat og eksport af modeller. Her er en kort introduktion til hver fane:

* **Train**: Denne fane giver dig mulighed for at vælge en model og et datasæt, konfigurere træningsparametre og starte træningsprocessen. Det er vigtigt at forstå de obligatoriske og valgfrie parametre for at optimere træningsopsætningen.
* **Evaluate & Predict**: Efter træning kan du evaluere modellens ydeevne og lave forudsigelser ved hjælp af denne fane. Den giver indsigt i modellens nøjagtighed og effektivitet på nye data.
* **Chat**: Når træningen er fuldført, kan du indlæse modellen i fanen Chat for at interagere med den og se resultaterne af dit arbejde. Denne funktion muliggør kommunikation med den trænede model i realtid.
* **Export**: Denne fane letter eksporten af trænede modeller til implementering eller yderligere brug. Du kan gemme dine modeller i forskellige formater, der passer til forskellige anvendelser.

For detaljeret vejledning opfordrer vi dig til at se den officielle dokumentation på [LlamaFactory GitHub-repositoriet](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) og [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest). Derudover giver [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) værdifuld indsigt i grænsefladen og dens funktionaliteter.

## Næste skridt
- Prøv forskellige modeller som `gpt-oss` og andre state-of-the-art-modeller.
- Eksperimenter med forskellige backends på den finjusterede model
 
For mere dokumentation, besøg venligst: https://llamafactory.readthedocs.io/en/latest/