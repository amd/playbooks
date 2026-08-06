<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

## Pregled

Učinkovito fino prilagajanje je ključnega pomena za prilagajanje velikih jezikovnih modelov (LLM) nalogam nižje v verigi. LLaMA Factory je odprtokodna in uporabniku prijazna platforma, ki poenostavi učenje in fino prilagajanje velikih jezikovnih modelov ter multimodalnih modelov. Uporabnikom omogoča, da lokalno prilagodijo na stotine vnaprej naučenih modelov z minimalnim programiranjem.

Ta priročnik vas nauči, kako fino prilagoditi LLM-je z uporabo LLaMA Factory na lokalni strojni opremi AMD.

<!-- @device:stx,krk -->
> **Opomba:** Tehnike finega prilagajanja v tem priročniku zahtevajo vsaj **32 GB sistemskega pomnilnika RAM**, od tega vsaj **16 GB na voljo GPU-ju** (16 GB je del 32 GB, ne dodatno k njim).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Opomba:** Tehnike finega prilagajanja v tem priročniku zahtevajo vsaj **16 GB skupnega pomnilnika GPU** in **32 GB sistemskega pomnilnika RAM**.
> - V sistemu Windows skupni pomnilnik GPU združuje namenski VRAM grafične kartice s skupno rabo pomnilnika GPU (izposojenega iz sistemskega RAM-a).
> - Zato lahko kartice z manj kot 16 GB namenskega VRAM-a še vedno izvajajo ta priročnik z uporabo skupne rabe pomnilnika GPU za nadomestitev razlike.
<!-- @os:end -->

<!-- @os:linux -->
> **Opomba:** Tehnike finega prilagajanja v tem priročniku zahtevajo grafično kartico z vsaj **16 GB namenskega pomnilnika GPU** in **32 GB sistemskega pomnilnika RAM**.
> - V sistemu Linux se učenje v celoti izvaja v namenskem VRAM-u grafične kartice.
> - Ne pade nazaj na skupno rabo pomnilnika GPU (sistemski RAM), ko VRAM zmanjka.
> - Kartice z manj kot 16 GB namenskega VRAM-a bodo med učenjem v sistemu Linux zmanjkale pomnilnika, tudi če ima sistem obilo RAM-a.
<!-- @os:end -->
<!-- @device:end -->

## Kaj se boste naučili

- Kako nastaviti LLaMA Factory s programsko opremo AMD ROCm™
- Kako konfigurirati parametre finega prilagajanja LLM (na primeru Qwen/Qwen3-4B-Instruct-2507)
- Kako izvesti fino prilagajanje z LLaMA Factory
- Kako izvesti sklepanje s fino prilagojenim modelom
- Kako izvoziti fino prilagojeni model 

## Ocenjeni čas

- Trajanje: Izvedba tega priročnika bo trajala približno 60 minut (odvisno od velikosti vašega modela/nabora podatkov in hitrosti omrežja).
- Za več informacij si oglejte [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory).

## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme

<!-- @require:software-update -->
<!-- @device:end -->

## Namestitev predpogojev programske opreme

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

#### Ustvarite virtualno okolje

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
**Podelite svojemu uporabniku dostop do naprav GPU** (za uveljavitev se odjavite in ponovno prijavite):

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

### Namestitev osnovnih odvisnosti

<!-- @require:pytorch,driver -->
 
### Namestitev dodatnih odvisnosti

> **Opomba**: Prepričajte se, da je različica Pythona 3.11, 3.12 ali 3.13

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

### Namestite LLaMA Factory

LLaMA Factory je odvisen od PyTorch. Ta bi moral biti že nameščen v skladu z zgornjimi zahtevami.

Prenesite izvorno kodo iz [uradnega GitHub repozitorija LLaMA Factory](https://github.com/hiyouga/LlamaFactory) in namestite njegove odvisnosti.

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

Preverite, ali je `llamafactory-cli` izvedljiv.

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

Primer izpisa:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

Ko ste uspešno namestili LLaMA Factory, izvedimo fino prilagajanje z njim.

## Uporaba vmesnika LLaMA Factory CLI za fino prilagajanje 

Ta razdelek obravnava, kako pripraviti nabore podatkov za fino prilagajanje, konfigurirati parametre LoRA/QLoRA in izvesti fino prilagajanje LoRA.

### Priprava nabora podatkov

LLaMA Factory podpira nabore podatkov za fino prilagajanje v obliki Alpaca in obliki ShareGPT. Vsi razpoložljivi nabori podatkov so definirani v [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). Če uporabljate nabor podatkov po meri, poskrbite, da dodate opis nabora podatkov v `dataset_info.json` in pred učenjem določite ime nabora podatkov. Podrobnosti najdete v njihovi dokumentaciji [tukaj](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

V tem priročniku bomo kot primer uporabili nabora podatkov identity in alpaca_en_demo ter v naslednjem koraku konfigurirali informacije o naboru podatkov.
### Konfiguracija parametrov fino uravnavanja

LLaMA Factory podpira več shem fino uravnavanja.

| Sheme fino uravnavanja | Primeri LLaMA Factory |
|-----------|------|
| Polni parametri (Full-Parameter)    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| Fino uravnavanje LoRA  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| Fino uravnavanje QLoRA | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

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

Te primerne konfiguracijske datoteke imajo določene parametre modela, parametre metode fino uravnavanja, parametre nabora podatkov, parametre vrednotenja in druge. Konfigurirate jih lahko glede na svoje potrebe. V tem vodniku bomo uporabili [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml). 

**Razlaga ključnih parametrov:**
- `model_name_or_path` – ime modela na Hugging Face ali pot do lokalne datoteke modela.
- `stage` – faza treniranja. Možnosti: rm (modeliranje nagrajevanja), pt (predtreniranje), sft (nadzorovano fino uravnavanje), PPO, DPO, KTO, ORPO.
- `do_train` – true za treniranje, false za vrednotenje
- `finetuning_type` – metoda fino uravnavanja. Možnosti: freeze, lora, full
- `lora_rank` – dimenzionalnost matrike nizkega ranga, uporabljene pri metodi LoRA, tipične vrednosti: 4, 6, 8, 16 (manjše vrednosti = manj parametrov = hitrejše fino uravnavanje; večje vrednosti = boljša prilagoditev nalogi, vendar večja poraba virov).
- `lora_target` – ciljni moduli za metodo LoRA. Privzeto: all.
- `dataset` – nabor(i) podatkov, ki naj se uporabijo. Za ločevanje več naborov podatkov uporabite »,«
- `output_dir` – izhodna pot fino uravnavanja
- `logging_steps` – interval beleženja v korakih
- `save_steps` – interval shranjevanja kontrolnih točk modela.
- `overwrite_output_dir` – ali naj bo dovoljeno prepisovanje izhodnega imenika.
- `per_device_train_batch_size` – velikost paketa za treniranje na napravo.
- `gradient_accumulation_steps` – število korakov akumulacije gradienta.
- `learning_rate` – stopnja učenja
- `num_train_epochs` – število epoh treniranja
- `lr_scheduler_type` – razporejanje stopnje učenja. Možnosti: linear, cosine, polynomial, constant itd.
- `warmup_ratio` – razmerje ogrevanja stopnje učenja

<!-- @os:linux -->
Privzeto vrednost `lora_rank` bomo spremenili, da bomo lahko zagnali fino uravnavanje na grafičnih procesorjih AMD Ryzen™ in AMD Radeon™.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
Posodobili bomo privzeto konfiguracijo fino uravnavanja LoRA za boljšo združljivost z grafičnimi procesorji AMD Ryzen™ in AMD Radeon™:
- Nastavite `lora_rank` iz `8` na `6`, da zmanjšate porabo pomnilnika med fino uravnavanjem.
- Uporabite `fp16` namesto `bf16` za širšo združljivost z grafičnimi procesorji AMD in nižjo porabo pomnilnika.
- Na sistemu Windows nastavite `dataloader_num_workers` na `0`, da se izognete napakam vrste `"Can't pickle local object<>"`, ki jih povzroča večprocesno nalaganje podatkov.

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

### Zagon fino uravnavanja z orodjem LLaMA Factory 

**llamafactory-cli** je uradno orodje za ukazno vrstico (CLI) za LLaMA Factory, razvito za poenostavitev celotnega poteka dela z velikimi jezikovnimi modeli (priprava podatkov → fino uravnavanje → vrednotenje → uvajanje), brez pisanja zapletene kode.

Za treniranje/fino uravnavanje je **llamafactory-cli train** osrednji podukaz orodja LLaMA Factory CLI. Abstrahira poteke dela fino uravnavanja (predobdelava podatkov, prilagajanje hiperparametrov, optimizacija strojne opreme) v en sam ukaz CLI, podpira več paradigem fino uravnavanja (LoRA/QLoRA/polno fino uravnavanje) in je optimiziran za grafične procesorje z omejenimi viri (npr. QLoRA na 16 GB VRAM).

Fino uravnavanje z orodjem LLaMA Factory lahko zaženete z naslednjim ukazom, ki temelji na spremenjeni konfiguracijski datoteki za fino uravnavanje Qwen3 LoRA.

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

Po zagonu fino uravnavanja LLM so vsi ustvarjeni izhodi shranjeni v »output_dir«, vključno z datotekami kontrolnih točk modela, konfiguracijskimi datotekami in metrikami treniranja.

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

### Preizkus fino uravnanega modela 

**llamafactory-cli chat** je namenjen interaktivnemu klepetu/sklepanju z velikimi jezikovnimi modeli (tako z osnovnimi modeli kot z modeli, fino uravnanimi z LoRA). LLaMA Factory zagotavlja vzorčno konfiguracijo za zagon sklepanja fino uravnanih modelov v [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference). To vzorčno konfiguracijo lahko tudi spremenite, da spremenite nastavitve, na primer zaledje za sklepanje.

Za preizkus fino uravnanega modela Qwen3 uporabite naslednji ukaz:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
Spodaj je prikazan primer klepeta z uporabo fino uravnanega modela:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### Izvoz fino uravnanega modela

Za produkcijske primere uporabe je treba vnaprej treniran model in prilagojevalnik LoRA združiti in izvoziti v en sam model. Ta združeni model se lahko uporablja kot običajna datoteka modela Hugging Face. LLaMA Factory zagotavlja vzorčne konfiguracije v [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora).

Za izvoz fino uravnanega modela Qwen3 uporabite naslednji ukaz:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
Spodaj je prikazan rezultat izvoza fino uravnanega modela.

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
## Uporaba grafičnega vmesnika LLaMA Factory

`LLaMA-Factory` prav tako omogoča brezkodno fino nastavljanje LLM prek spletnega uporabniškega vmesnika v brskalniku.

Za odpiranje uporabite naslednji ukaz:

```bash
llamafactory-cli webui
```
`LlamaFactory Web UI` ponuja poenostavljen vmesnik za upravljanje delovnih tokov strojnega učenja, vključno z učenjem, vrednotenjem, napovedovanjem, klepetom in izvozom modelov. Tukaj je kratek uvod v posamezne zavihke:

* **Train (Učenje)**: Ta zavihek omogoča izbiro modela in nabora podatkov, konfiguracijo parametrov učenja ter zagon postopka učenja. Bistveno je razumeti obvezne in izbirne parametre za optimizacijo nastavitve učenja.
* **Evaluate & Predict (Vrednotenje in napovedovanje)**: Po učenju lahko z uporabo tega zavihka ovrednotite delovanje modela in izdelate napovedi. Zagotavlja vpogled v natančnost in učinkovitost modela na novih podatkih.
* **Chat (Klepet)**: Ko je učenje zaključeno, naložite model v zavihek Chat, da z njim komunicirate in si ogledate rezultate svojega dela. Ta funkcija omogoča komunikacijo z naučenim modelom v realnem času.
* **Export (Izvoz)**: Ta zavihek omogoča izvoz naučenih modelov za uvajanje ali nadaljnjo uporabo. Modele lahko shranite v različnih oblikah, primernih za različne aplikacije.

Za podrobna navodila vas vabimo, da si ogledate uradno dokumentacijo v [repozitoriju LlamaFactory na GitHub](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) in [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest). Poleg tega [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) ponuja koristne vpoglede v vmesnik in njegove funkcionalnosti.

## Naslednji koraki
- Preizkusite različne modele, kot je `gpt-oss`, in druge najsodobnejše modele.
- Eksperimentirajte z različnimi zaledji (backends) na fino nastavljenem modelu
 
Za več dokumentacije obiščite: https://llamafactory.readthedocs.io/en/latest/