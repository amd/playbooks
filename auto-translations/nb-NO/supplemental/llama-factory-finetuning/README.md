<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinoversettelse.** Denne siden ble automatisk oversatt fra engelsk og har ikke blitt gjennomgått av et menneske. Den kan inneholde feil, og enkelte instruksjoner, kommandoer, nedlastinger, produkttilgjengelighet eller annet innhold kan variere etter språk eller region. Ved eventuelle uoverensstemmelser eller avvik er den opprinnelige engelske versjonen av playbook-en gjeldende.
<!-- auto-translated-disclaimer:end -->

## Oversikt

Effektiv finjustering er avgjørende for å tilpasse store språkmodeller (LLM-er) til nedstrømsoppgaver. LLaMA Factory er en åpen kildekode-plattform som er brukervennlig og som forenkler trening og finjustering av store språkmodeller og multimodale modeller. Den lar brukere tilpasse hundrevis av forhåndstrente modeller lokalt med minimal koding.

Denne oppskriften lærer deg hvordan du finjusterer LLM-er ved hjelp av LLaMA Factory på din lokale AMD-maskinvare.

<!-- @device:stx,krk -->
> **Merk:** Finjusteringsteknikkene i denne oppskriften krever minst **32 GB systemminne (RAM)**, hvorav minst **16 GB må være tilgjengelig for GPU-en** (16 GB-en er en del av de 32 GB, ikke i tillegg til dem).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Merk:** Finjusteringsteknikkene i denne oppskriften krever minst **16 GB totalt GPU-minne** og **32 GB systemminne (RAM)**.
> - På Windows kombineres grafikkortets dedikerte VRAM med delt GPU-minne (lånt fra systemminnet) for å utgjøre det totale GPU-minnet.
> - Derfor kan kort med mindre enn 16 GB dedikert VRAM likevel kjøre denne oppskriften ved å bruke delt GPU-minne til å dekke differansen.
<!-- @os:end -->

<!-- @os:linux -->
> **Merk:** Finjusteringsteknikkene i denne oppskriften krever et grafikkort med minst **16 GB dedikert GPU-minne** og **32 GB systemminne (RAM)**.
> - På Linux foregår treningen utelukkende i grafikkortets dedikerte VRAM.
> - Det faller ikke tilbake til delt GPU-minne (systemminne) når VRAM-en går tom.
> - Kort med mindre enn 16 GB dedikert VRAM vil gå tom for minne under trening på Linux, selv om systemet har rikelig med RAM.
<!-- @os:end -->
<!-- @device:end -->

## Hva du vil lære

- Hvordan sette opp LLaMA Factory med AMD ROCm™-programvare
- Hvordan konfigurere parametere for finjustering av LLM (ved bruk av Qwen/Qwen3-4B-Instruct-2507 som eksempel)
- Hvordan kjøre finjustering med LLaMA Factory
- Hvordan kjøre inferens med den finjusterte modellen
- Hvordan eksportere den finjusterte modellen 

## Estimert tid

- Varighet: Det vil ta omtrent 60 minutter å kjøre denne oppskriften (avhengig av modell-/datasettstørrelse og nettverkshastighet).
- Se [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory) for mer informasjon.

## Angi minnekonfigurasjonen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sjekk etter programvareoppdateringer

<!-- @require:software-update -->
<!-- @device:end -->

## Installere programvareforutsetninger

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

#### Opprett et virtuelt miljø

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
**Gi brukeren din tilgang til GPU-enheter** (logg ut og inn igjen for at dette skal tre i kraft):

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

### Installere grunnleggende avhengigheter

<!-- @require:pytorch,driver -->
 
### Installere ytterligere avhengigheter

> **Merk**: Kontroller at Python-versjonen er 3.11, 3.12 eller 3.13

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

LLaMA Factory er avhengig av PyTorch. Du bør allerede ha dette installert i henhold til kravene ovenfor.

Last ned kildekoden fra [LLaMA Factorys offisielle GitHub-repositorium](https://github.com/hiyouga/LlamaFactory), og installer avhengighetene.

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

Kontroller om `llamafactory-cli` er kjørbar.

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

Eksempel på utdata:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

Etter å ha installert LLaMA Factory, la oss kjøre finjustering med den.

## Bruke LLaMA Factory CLI for finjustering 

Denne delen dekker hvordan du forbereder datasett for finjustering, konfigurerer LoRA/QLoRA-parametere og kjører LoRA-finjustering.

### Klargjøring av datasett

LLaMA Factory støtter finjusteringsdatasett i Alpaca-format og ShareGPT-format. Alle tilgjengelige datasett er definert i [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). Hvis du bruker et tilpasset datasett, må du sørge for å legge til en datasettbeskrivelse i `dataset_info.json` og angi datasettnavnet før trening. Detaljer finner du i dokumentasjonen deres [her](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

I denne oppskriften bruker vi datasettene identity og alpaca_en_demo som eksempel, og konfigurerer datasettinformasjonen i neste trinn.
### Konfigurasjon av parametere for finjustering

LLaMA Factory støtter flere finjusteringsmetoder.

| Finjusteringsmetoder | LLaMA Factory-eksempler |
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

Disse eksempelkonfigurasjonsfilene har spesifisert modellparametere, parametere for finjusteringsmetode, datasettparametere, evalueringsparametere og mer. Du kan konfigurere dem etter eget behov. I denne veiledningen bruker vi [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml). 

**Forklaring av sentrale parametere:**
- `model_name_or_path` - Hugging Face-modellnavn eller lokal filbane til modellen.
- `stage` - Treningsfase. Alternativer: rm (belønningsmodellering), pt (forhåndstrening), sft (Supervised Fine-Tuning), PPO, DPO, KTO, ORPO.
- `do_train` - true for trening, false for evaluering
- `finetuning_type` - Finjusteringsmetode. Alternativer: freeze, lora, full
- `lora_rank` - Dimensjonaliteten til lavrangsmatrisen som brukes i LoRA, typiske verdier: 4, 6, 8, 16 (mindre verdier = færre parametere = raskere finjustering; større verdier = bedre tilpasning til oppgaven, men høyere ressursbruk).
- `lora_target` - Målmoduler for LoRA-metoden. Standard: all.
- `dataset` - Datasett som skal brukes. Bruk «,» for å skille flere datasett
- `output_dir` - Utdatabane for finjustering
- `logging_steps` - Intervall for logging, i steg
- `save_steps` - Intervall for lagring av modell-sjekkpunkt.
- `overwrite_output_dir` - Om det skal tillates å overskrive utdatamappen.
- `per_device_train_batch_size` - Treningsbatchstørrelse per enhet.
- `gradient_accumulation_steps` - Antall steg for gradientakkumulering.
- `learning_rate` - Læringsrate
- `num_train_epochs` - Antall treningsepoker
- `lr_scheduler_type` - Plan for læringsrate. Alternativer: linear, cosine, polynomial, constant, osv.
- `warmup_ratio` - Andel for oppvarming av læringsrate

<!-- @os:linux -->
Vi vil endre standardverdien for `lora_rank` for å kjøre finjustering på AMD Ryzen™- og AMD Radeon™-GPUer.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
Vi vil oppdatere standardkonfigurasjonen for LoRA-finjustering for bedre kompatibilitet med AMD Ryzen™- og AMD Radeon™-GPUer:
- Sett `lora_rank` fra `8` til `6` for å redusere minnebruken under finjustering.
- Bruk `fp16` i stedet for `bf16` for bredere kompatibilitet med AMD-GPUer og lavere minnebruk.
- Sett `dataloader_num_workers` til `0` på Windows for å unngå `"Can't pickle local object<>"`-feil forårsaket av flerprosessdatalasting.

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

### Kjør LLaMA Factory-finjustering 

**llamafactory-cli** er det offisielle kommandolinjeverktøyet (CLI) for LLaMA Factory, utviklet for å forenkle hele arbeidsflyten for LLM-er (klargjøring av data → finjustering → evaluering → distribusjon) uten å skrive kompleks kode.

For trening/finjustering er **llamafactory-cli train** hovedunderkommandoen i LLaMA Factory CLI. Den abstraherer arbeidsflyter for finjustering (databehandling, hyperparameterjustering, maskinvareoptimalisering) til én enkelt CLI-kommando, og støtter flere finjusteringsparadigmer (LoRA/QLoRA/full finjustering), og er optimalisert for GPUer med begrensede ressurser (f.eks. QLoRA på 16 GB VRAM).

Du kan kjøre LLaMA Factory-finjustering ved å bruke følgende kommando, som er basert på den endrede konfigurasjonsfilen for Qwen3 LoRA-finjustering.

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

Etter at LLM-finjusteringen er kjørt, lagres alle genererte utdata i «output_dir», inkludert modellsjekkpunktfiler, konfigurasjonsfiler og treningsmetrikker.

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

### Test den finjusterte modellen 

**llamafactory-cli chat** er utviklet for interaktiv chat/inferens med LLM-er (både grunnmodeller og LoRA-finjusterte modeller). LLaMA Factory tilbyr en eksempelkonfigurasjon for å kjøre inferens med finjusterte modeller i [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference). Du kan også endre denne eksempelkonfigurasjonen for å tilpasse innstillingene, for eksempel inferensbackend.

Bruk følgende kommando for å teste den finjusterte Qwen3-modellen:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
Et eksempel på en chat med den finjusterte modellen vises nedenfor:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### Eksporter den finjusterte modellen

For produksjonsbruk må den forhåndstrente modellen og LoRA-adapteren slås sammen og eksporteres til én enkelt modell. Denne sammenslåtte modellen kan brukes som en vanlig Hugging Face-modellfil. LLaMA Factory tilbyr eksempelkonfigurasjoner i [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora).

Bruk følgende kommando for å eksportere den finjusterte Qwen3-modellen:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
Resultatet av å eksportere den finjusterte modellen vises nedenfor.

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
## Bruke LLaMA Factory GUI

`LLaMA-Factory` støtter også kodefri finjustering av LLM-er via et web-grensesnitt i nettleseren.

Bruk følgende kommando for å åpne det:

```bash
llamafactory-cli webui
```
`LlamaFactory Web UI` tilbyr et strømlinjeformet grensesnitt for å administrere maskinlæringsarbeidsflyter, inkludert trening, evaluering, prediksjon, chatting og eksportering av modeller. Her er en kort introduksjon til hver fane:

* **Train**: Denne fanen lar deg velge en modell og et datasett, konfigurere treningsparametere, og starte treningsprosessen. Det er viktig å forstå de obligatoriske og valgfrie parameterne for å optimalisere treningsoppsettet.
* **Evaluate & Predict**: Etter trening kan du evaluere modellens ytelse og gjøre prediksjoner ved hjelp av denne fanen. Den gir innsikt i modellens nøyaktighet og effektivitet på nye data.
* **Chat**: Når treningen er fullført, laster du inn modellen i Chat-fanen for å interagere med den og se resultatene av arbeidet ditt. Denne funksjonen muliggjør kommunikasjon med den trente modellen i sanntid.
* **Export**: Denne fanen forenkler eksport av trente modeller for distribusjon eller videre bruk. Du kan lagre modellene dine i ulike formater som passer for forskjellige applikasjoner.

For detaljert veiledning oppfordrer vi deg til å se den offisielle dokumentasjonen på [LlamaFactory GitHub-repositoriet](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) og [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest). I tillegg gir [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) verdifull innsikt i grensesnittet og funksjonaliteten.

## Neste steg
- Prøv forskjellige modeller som `gpt-oss` og andre toppmoderne modeller.
- Eksperimenter med forskjellige backends på den finjusterte modellen
 
For mer dokumentasjon, besøk: https://llamafactory.readthedocs.io/en/latest/