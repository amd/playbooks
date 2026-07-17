## Overzicht

Efficiënte fine-tuning is essentieel voor het aanpassen van grote taalmodellen (LLM's) aan downstream-taken. LLaMA-Factory is een open-source en gebruiksvriendelijk platform dat het trainen en fine-tunen van grote taalmodellen en multimodale modellen vereenvoudigt. Het stelt gebruikers in staat om honderden vooraf getrainde modellen lokaal aan te passen met minimale code.

Dit playbook leert u hoe u LLM's kunt fine-tunen met LLaMA-Factory op uw lokale AMD-hardware.

<!-- @device:stx,krk -->
> **Opmerking:** De fine-tuningtechnieken in dit playbook vereisen minimaal **32 GB systeemgeheugen**, waarvan minimaal **16 GB beschikbaar moet zijn voor de GPU** (de 16 GB maakt deel uit van de 32 GB, niet daarboven op).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Opmerking:** De fine-tuningtechnieken in dit playbook vereisen minimaal **16 GB totaal GPU-geheugen** en **32 GB systeemgeheugen**.
> - Op Windows combineert het totale GPU-geheugen het dedicated VRAM van de grafische kaart met gedeeld GPU-geheugen (geleend van het systeemgeheugen).
> - Kaarten met minder dan 16 GB dedicated VRAM kunnen dit playbook dus toch uitvoeren door gedeeld GPU-geheugen te gebruiken om het verschil te compenseren.
<!-- @os:end -->

<!-- @os:linux -->
> **Opmerking:** De fine-tuningtechnieken in dit playbook vereisen een grafische kaart met minimaal **16 GB dedicated GPU-geheugen** en **32 GB systeemgeheugen**.
> - Op Linux wordt training volledig uitgevoerd in het dedicated VRAM van de grafische kaart.
> - Er wordt niet teruggevallen op gedeeld GPU-geheugen (systeemgeheugen) wanneer het VRAM vol is.
> - Kaarten met minder dan 16 GB dedicated VRAM raken tijdens training op Linux door het geheugen heen, zelfs als het systeem voldoende RAM heeft.
<!-- @os:end -->
<!-- @device:end -->

## Wat u leert

- Hoe u LLaMA-Factory instelt met AMD ROCm™-software
- Hoe u LLM fine-tuningparameters configureert (met Qwen/Qwen3-4B-Instruct-2507 als voorbeeld)
- Hoe u LLaMA-Factory fine-tuning uitvoert
- Hoe u inferentie uitvoert met het fine-tuned model
- Hoe u het fine-tuned model exporteert

## Geschatte tijd

- Duur: Dit playbook uitvoeren duurt ongeveer 60 minuten (afhankelijk van uw model-/datasetgrootte en netwerksnelheid).
- Bekijk de [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory) voor meer informatie.

## De geheugenconfiguratie instellen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Controleren op software-updates

<!-- @require:software-update -->
<!-- @device:end -->

## Softwarevereisten installeren

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

#### Een virtuele omgeving aanmaken

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
**Geef uw gebruiker toegang tot GPU-apparaten** (log uit en weer in om dit van kracht te laten worden):

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

### Basisafhankelijkheden installeren

<!-- @require:pytorch,driver -->
 
### Aanvullende afhankelijkheden installeren

> **Opmerking**: Zorg ervoor dat de Python-versie 3.11, 3.12 of 3.13 is

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

### LLaMA-Factory installeren

LLaMA-Factory is afhankelijk van PyTorch. U zou dit al geïnstalleerd moeten hebben op basis van de bovenstaande vereisten.

Download de broncode van de [officiële LLaMA Factory GitHub-repository](https://github.com/hiyouga/LlamaFactory) en installeer de bijbehorende afhankelijkheden.

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

Controleer of `llamafactory-cli` uitvoerbaar is.

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

Voorbeelduitvoer:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

Nu LLaMA-Factory succesvol is geïnstalleerd, gaan we fine-tuning uitvoeren.

## LLaMA Factory CLI gebruiken voor fine-tuning

Dit gedeelte behandelt hoe u fine-tuningdatasets voorbereidt, LoRA/QLoRA-parameters configureert en LoRA fine-tuning uitvoert.

### Datasetvoorbereiding

LLaMA-Factory ondersteunt fine-tuningdatasets in het Alpaca-formaat en het ShareGPT-formaat. Alle beschikbare datasets zijn gedefinieerd in de [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). Als u een aangepaste dataset gebruikt, zorg er dan voor dat u een datasetbeschrijving toevoegt in `dataset_info.json` en de naam van de dataset opgeeft vóór het trainen. Details zijn te vinden in hun documentatie [hier](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

In dit playbook gebruiken we de identity- en alpaca_en_demo-datasets als voorbeeld en configureren we de datasetinformatie in de volgende stap.


### Configuratie van fine-tuningparameters

LLaMA-Factory ondersteunt meerdere fine-tuningschema's.

| Fine-tuningschema's | LLaMA Factory-voorbeelden |
|-----------|------|
| Volledige parameters    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
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

Deze voorbeeldconfiguratiebestanden bevatten modelparameters, fine-tuningmethodeparameters, datasetparameters, evaluatieparameters en meer. U kunt deze naar eigen behoefte configureren. In dit playbook gebruiken we [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml).

**Toelichting op de belangrijkste parameters:**
- `model_name_or_path` - Hugging Face-modelnaam of lokaal modelbestandspad.
- `stage` - Trainingsfase. Opties: rm (reward modeling), pt (pretrain), sft (Supervised Fine-Tuning), PPO, DPO, KTO, ORPO.
- `do_train` - true voor training, false voor evaluatie
- `finetuning_type` - Fine-tuningmethode. Opties: freeze, lora, full
- `lora_rank` - De dimensionaliteit van de laagrangmatrix die wordt gebruikt in LoRA, typische waarden: 4, 6, 8, 16 (kleinere waarden = minder parameters = snellere fine-tuning; grotere waarden = betere taakaanpassing maar hoger resourcegebruik).
- `lora_target` - Doelmodules voor de LoRA-methode. Standaard: all.
- `dataset` - Te gebruiken dataset(s). Gebruik "," om meerdere datasets te scheiden
- `output_dir` - Uitvoerpad voor fine-tuning
- `logging_steps` - Logboekinterval in stappen
- `save_steps` - Opslaginterval voor modelcontrolepunten.
- `overwrite_output_dir` - Of het overschrijven van de uitvoermap is toegestaan.
- `per_device_train_batch_size` - Trainingsgrootte per apparaat.
- `gradient_accumulation_steps` - Aantal stappen voor gradiëntaccumulatie.
- `learning_rate` - Leersnelheid
- `num_train_epochs` - Aantal trainingsepochs
- `lr_scheduler_type` - Leersnelheidsschema. Opties: linear, cosine, polynomial, constant, enz.
- `warmup_ratio` - Opwarmverhouding voor de leersnelheid

<!-- @os:linux -->
We passen de standaardwaarde van `lora_rank` aan om fine-tuning uit te voeren op AMD Ryzen™- en AMD Radeon™-GPU's.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
We passen de standaard LoRA fine-tuningconfiguratie aan voor betere compatibiliteit met AMD Ryzen™- en AMD Radeon™-GPU's:
- Stel `lora_rank` in van `8` naar `6` om het geheugengebruik tijdens fine-tuning te verminderen.
- Gebruik `fp16` in plaats van `bf16` voor bredere AMD GPU-compatibiliteit en lager geheugengebruik.
- Stel `dataloader_num_workers` in op `0` op Windows om `"Can't pickle local object<>"`-fouten te vermijden die worden veroorzaakt door multiprocessing-gegevensladen.

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

### LLaMA Factory fine-tuning uitvoeren

**llamafactory-cli** is de officiële opdrachtregelinterface (CLI) voor LLaMA-Factory, ontwikkeld om end-to-end LLM-workflows te vereenvoudigen (datavoorbereiding → fine-tuning → evaluatie → implementatie) zonder complexe code te schrijven.

Voor training/fine-tuning is **llamafactory-cli train** het kernsubcommando van de LLaMA Factory CLI. Het abstraheert fine-tuningworkflows (datavoorverwerking, hyperparameterafstemming, hardwareoptimalisatie) in één CLI-opdracht, ondersteunt meerdere fine-tuningparadigma's (LoRA/QLoRA/volledige fine-tuning) en is geoptimaliseerd voor GPU's met beperkte resources (bijv. QLoRA op 16 GB VRAM).

U kunt LLaMA Factory fine-tuning uitvoeren met de volgende opdracht, die is gebaseerd op het gewijzigde configuratiebestand voor Qwen3 LoRA fine-tuning.

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

Na het uitvoeren van LLM fine-tuning worden alle gegenereerde uitvoerbestanden opgeslagen in de "output_dir", inclusief modelcontrolepuntbestanden, configuratiebestanden en trainingsstatistieken.

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

### Het fine-tuned model testen

**llamafactory-cli chat** is ontworpen voor interactief chatten/inferentie met LLM's (zowel basismodellen als LoRA-fine-tuned modellen). LLaMA-Factory biedt de voorbeeldconfiguratie om inferentie van fine-tuned modellen uit te voeren in [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference). U kunt deze voorbeeldconfiguratie ook aanpassen om de instellingen te wijzigen, zoals de inferentiebackend.

Gebruik de volgende opdracht om het fine-tuned Qwen3-model te testen:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
Hieronder ziet u een voorbeeldgesprek met het fine-tuned model:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### Het fine-tuned model exporteren

Voor productiegebruik moeten het vooraf getrainde model en de LoRA-adapter worden samengevoegd en geëxporteerd naar één enkel model. Dit samengevoegde model kan worden gebruikt als een normaal Hugging Face-modelbestand. LLaMA-Factory biedt voorbeeldconfiguraties in [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora).

Gebruik de volgende opdracht om het fine-tuned Qwen3-model te exporteren:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
Het resultaat van het exporteren van het fine-tuned model wordt hieronder weergegeven.

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

## LLaMA Factory GUI gebruiken

`LLaMA-Factory` ondersteunt ook codevrije fine-tuning van LLM's via een web-UI in de browser.

Gebruik de volgende opdracht om deze te openen:

```bash
llamafactory-cli webui
```
De `LlamaFactory Web UI` biedt een gestroomlijnde interface voor het beheren van machine learning-workflows, inclusief training, evaluatie, voorspelling, chatten en het exporteren van modellen. Hier volgt een korte introductie van elk tabblad:

* **Train**: Op dit tabblad kunt u een model en dataset selecteren, trainingsparameters configureren en het trainingsproces starten. Het is essentieel om de verplichte en optionele parameters te begrijpen om de trainingsopstelling te optimaliseren.
* **Evaluate & Predict**: Na het trainen kunt u de prestaties van het model evalueren en voorspellingen doen via dit tabblad. Het biedt inzicht in de nauwkeurigheid en effectiviteit van het model op nieuwe gegevens.
* **Chat**: Zodra de training is voltooid, laadt u het model in het Chat-tabblad om ermee te communiceren en de resultaten van uw werk te bekijken. Deze functie maakt realtime communicatie met het getrainde model mogelijk.
* **Export**: Dit tabblad vergemakkelijkt het exporteren van getrainde modellen voor implementatie of verder gebruik. U kunt uw modellen opslaan in verschillende formaten die geschikt zijn voor verschillende toepassingen.

Voor gedetailleerde begeleiding raden we u aan de officiële documentatie te raadplegen op de [LlamaFactory GitHub-repository](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) en de [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest). Daarnaast biedt de [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) waardevolle inzichten in de interface en de functionaliteiten ervan.

## Volgende stappen
- Probeer verschillende modellen zoals `gpt-oss` en andere geavanceerde modellen.
- Experimenteer met verschillende backends op het fine-tuned model
 
Voor meer documentatie, bezoek: https://llamafactory.readthedocs.io/en/latest/