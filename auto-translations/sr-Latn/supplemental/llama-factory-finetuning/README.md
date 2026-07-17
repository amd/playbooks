## Pregled

Efikasno fino podešavanje je ključno za prilagođavanje velikih jezičkih modela (LLM) zadacima nizvodno. LLaMA-Factory je platforma otvorenog koda, prilagođena korisnicima, koja pojednostavljuje obuku i fino podešavanje velikih jezičkih modela i multimodalnih modela. Korisnicima omogućava da lokalno prilagode stotine unapred obučenih modela uz minimalno kodiranje.

Ovaj priručnik vas uči kako da fino podesite LLM-ove koristeći LLaMA-Factory na vašem lokalnom AMD hardveru.

<!-- @device:stx,krk -->
> **Napomena:** Tehnike finog podešavanja u ovom priručniku zahtevaju najmanje **32 GB sistemske RAM memorije**, od čega je najmanje **16 GB dostupno GPU-u** (tih 16 GB je deo 32 GB, a ne dodatak).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Napomena:** Tehnike finog podešavanja u ovom priručniku zahtevaju najmanje **16 GB ukupne GPU memorije** i **32 GB sistemske RAM memorije**.
> - Na Windows-u, ukupna GPU memorija kombinuje namenski VRAM grafičke kartice sa deljenom GPU memorijom (pozajmljenom iz sistemske RAM memorije).
> - Stoga, kartice sa manje od 16 GB namenskog VRAM-a i dalje mogu da pokrenu ovaj priručnik korišćenjem deljene GPU memorije kako bi nadoknadile razliku.
<!-- @os:end -->

<!-- @os:linux -->
> **Napomena:** Tehnike finog podešavanja u ovom priručniku zahtevaju grafičku karticu sa najmanje **16 GB namenske GPU memorije** i **32 GB sistemske RAM memorije**.
> - Na Linux-u, obuka se odvija isključivo u namenskom VRAM-u grafičke kartice.
> - Ne prelazi na deljenu GPU memoriju (sistemsku RAM memoriju) kada se VRAM popuni.
> - Kartice sa manje od 16 GB namenskog VRAM-a će ostati bez memorije tokom obuke na Linux-u, čak i ako sistem ima dovoljno RAM memorije.
<!-- @os:end -->
<!-- @device:end -->

## Šta ćete naučiti

- Kako da podesite LLaMA-Factory sa AMD ROCm™ softverom
- Kako da konfigurišete parametre finog podešavanja LLM-a (koristeći Qwen/Qwen3-4B-Instruct-2507 kao primer)
- Kako da pokrenete fino podešavanje u LLaMA-Factory
- Kako da pokrenete inferenciju sa fino podešenim modelom
- Kako da izvezete fino podešeni model

## Procenjeno vreme

- Trajanje: Izvršavanje ovog priručnika trajaće oko 60 minuta (zavisno od veličine vašeg modela/skupa podataka i brzine mreže).
- Pogledajte [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory) za više informacija.

## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Proverite softverska ažuriranja

<!-- @require:software-update -->
<!-- @device:end -->

## Instalacija softverskih preduslova

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

#### Kreiranje virtuelnog okruženja

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
**Dodelite svom korisniku pristup GPU uređajima** (odjavite se i ponovo prijavite da bi ovo stupilo na snagu):

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

### Instalacija osnovnih zavisnosti

<!-- @require:pytorch,driver -->
 
### Instalacija dodatnih zavisnosti

> **Napomena**: Uverite se da je verzija Python-a 3.11, 3.12 ili 3.13

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

### Instalacija LLaMA-Factory

LLaMA-Factory zavisi od PyTorch-a. Trebalo bi da ga već imate instaliranog prema gorenavedenim zahtevima.

Preuzmite izvorni kod iz [zvaničnog GitHub repozitorijuma LLaMA-Factory](https://github.com/hiyouga/LlamaFactory) i instalirajte njegove zavisnosti.

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

Proverite da li je `llamafactory-cli` izvršiv.

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

Primer izlaza:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

Nakon uspešne instalacije LLaMA-Factory, pokrenimo fino podešavanje na njemu.

## Korišćenje LLaMA Factory CLI za fino podešavanje

Ovaj odeljak će obuhvatiti kako da pripremite skupove podataka za fino podešavanje, konfigurišete LoRA/QLoRA parametre i pokrenete LoRA fino podešavanje.

### Priprema skupa podataka

LLaMA-Factory podržava skupove podataka za fino podešavanje u Alpaca formatu i ShareGPT formatu. Svi dostupni skupovi podataka definisani su u [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). Ako koristite prilagođeni skup podataka, obavezno dodajte opis skupa podataka u `dataset_info.json` i navedite naziv skupa podataka pre obuke. Detalji se mogu pronaći u njihovoj dokumentaciji [ovde](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

U ovom priručniku, koristićemo skupove podataka identity i alpaca_en_demo kao primer i konfigurisati informacije o skupu podataka u sledećem koraku.


### Konfiguracija parametara finog podešavanja

LLaMA-Factory podržava više šema finog podešavanja.

| Šeme finog podešavanja | Primeri u LLaMA-Factory |
|-----------|------|
| Puni parametri    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| LoRA fino podešavanje  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| QLoRA fino podešavanje | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

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

Ovi primeri konfiguracijskih fajlova specificiraju parametre modela, parametre metode finog podešavanja, parametre skupa podataka, parametre evaluacije i još mnogo toga. Možete ih konfigurisati prema sopstvenim potrebama. U ovom priručniku, koristićemo [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml).

**Objašnjenje ključnih parametara:**
- `model_name_or_path` - Naziv modela na Hugging Face ili putanja do lokalnog fajla modela.
- `stage` - Faza obuke. Opcije: rm (modelovanje nagrade), pt (predobuka), sft (nadzirano fino podešavanje), PPO, DPO, KTO, ORPO.
- `do_train` - true za obuku, false za evaluaciju
- `finetuning_type` - Metoda finog podešavanja. Opcije: freeze, lora, full
- `lora_rank` - Dimenzionalnost matrice niskog ranga koja se koristi u LoRA, tipične vrednosti: 4, 6, 8, 16 (manje vrednosti = manji broj parametara = brže fino podešavanje; veće vrednosti = bolja adaptacija zadatku, ali veća potrošnja resursa).
- `lora_target` - Ciljni moduli za LoRA metodu. Podrazumevano: all.
- `dataset` - Skup(ovi) podataka koji se koriste. Koristite "," za razdvajanje više skupova podataka
- `output_dir` - Putanja izlaza finog podešavanja
- `logging_steps` - Interval beleženja u koracima
- `save_steps` - Interval čuvanja kontrolnih tačaka modela.
- `overwrite_output_dir` - Da li se dozvoljava prepisivanje izlaznog direktorijuma.
- `per_device_train_batch_size` - Veličina serije za obuku po uređaju.
- `gradient_accumulation_steps` - Broj koraka akumulacije gradijenta.
- `learning_rate` - Stopa učenja
- `num_train_epochs` - Broj epoha obuke
- `lr_scheduler_type` - Raspored stope učenja. Opcije: linear, cosine, polynomial, constant, itd.
- `warmup_ratio` - Odnos zagrevanja stope učenja

<!-- @os:linux -->
Izmeniće mo podrazumevanu vrednost `lora_rank` kako bismo pokrenuli fino podešavanje na AMD Ryzen™ i AMD Radeon™ GPU-ovima.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
Ažuriraćemo podrazumevanu konfiguraciju LoRA finog podešavanja radi bolje kompatibilnosti sa AMD Ryzen™ i AMD Radeon™ GPU-ovima:
- Postavite `lora_rank` sa `8` na `6` kako biste smanjili korišćenje memorije tokom finog podešavanja.
- Koristite `fp16` umesto `bf16` za širu kompatibilnost sa AMD GPU-ovima i manje korišćenje memorije.
- Postavite `dataloader_num_workers` na `0` na Windows-u kako biste izbegli greške `"Can't pickle local object<>"` uzrokovane višeprocesnim učitavanjem podataka.

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

### Pokretanje finog podešavanja u LLaMA-Factory

**llamafactory-cli** je zvanični alat komandne linije (CLI) za LLaMA-Factory, razvijen radi pojednostavljivanja end-to-end LLM tokova rada (priprema podataka → fino podešavanje → evaluacija → primena) bez pisanja složenog koda.

Za obuku/fino podešavanje, **llamafactory-cli train** je osnovna podkomanda LLaMA Factory CLI-ja. Apstrahuje tokove rada finog podešavanja (predobrada podataka, podešavanje hiperparametara, optimizacija hardvera) u jednu CLI komandu, podržava više paradigmi finog podešavanja (LoRA/QLoRA/potpuno fino podešavanje) i optimizovan je za GPU-ove sa ograničenim resursima (npr. QLoRA na 16 GB VRAM-a).

Možete pokrenuti fino podešavanje u LLaMA-Factory koristeći sledeću komandu, koja se zasniva na izmenjenom konfiguracinom fajlu za Qwen3 LoRA fino podešavanje.

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

Nakon pokretanja finog podešavanja LLM-a, svi generisani izlazi se čuvaju u "output_dir", uključujući fajlove kontrolnih tačaka modela, konfiguracione fajlove i metrike obuke.

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

### Testiranje fino podešenog modela

**llamafactory-cli chat** je dizajniran za interaktivni razgovor/inferenciju sa LLM-ovima (i baznim modelima i LoRA fino podešenim modelima). LLaMA-Factory pruža primer konfiguracije za pokretanje inferencije fino podešenih modela u [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference). Takođe možete izmeniti ovu primer konfiguraciju kako biste promenili podešavanja, kao što je pozadinski sistem za inferenciju.

Koristite sledeću komandu za testiranje fino podešenog Qwen3 modela:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
Primer razgovora koristeći fino podešeni model prikazan je ispod:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### Izvoz fino podešenog modela

Za slučajeve produkcijske upotrebe, unapred obučeni model i LoRA adapter moraju biti spojeni i izvezeni u jedan model. Ovaj spojeni model može se koristiti kao normalan Hugging Face fajl modela. LLaMA-Factory pruža primer konfiguracija u [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora).

Koristite sledeću komandu za izvoz fino podešenog Qwen3 modela:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
Rezultat izvoza fino podešenog modela prikazan je ispod.

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

## Korišćenje LLaMA Factory GUI

`LLaMA-Factory` takođe podržava fino podešavanje LLM-ova bez koda putem web korisničkog interfejsa u pregledaču.

Koristite sledeću komandu da ga otvorite:

```bash
llamafactory-cli webui
```
`LlamaFactory Web UI` nudi pojednostavljen interfejs za upravljanje tokovima rada mašinskog učenja, uključujući obuku, evaluaciju, predikciju, razgovor i izvoz modela. Sledi kratak uvod u svaku karticu:

* **Train**: Ova kartica vam omogućava da izaberete model i skup podataka, konfigurišete parametre obuke i pokrenete proces obuke. Važno je razumeti obavezne i opcione parametre kako biste optimizovali podešavanje obuke.
* **Evaluate & Predict**: Nakon obuke, možete evaluirati performanse modela i vršiti predikcije koristeći ovu karticu. Pruža uvid u tačnost i efikasnost modela na novim podacima.
* **Chat**: Kada je obuka završena, učitajte model na kartici Chat kako biste komunicirali sa njim i videli rezultate svog rada. Ova funkcija omogućava komunikaciju u realnom vremenu sa obučenim modelom.
* **Export**: Ova kartica olakšava izvoz obučenih modela za primenu ili dalju upotrebu. Možete sačuvati svoje modele u različitim formatima pogodnim za različite primene.

Za detaljno uputstvo, preporučujemo vam da pogledate zvaničnu dokumentaciju na [LlamaFactory GitHub repozitorijumu](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) i [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest). Pored toga, [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) pruža vredne uvide u interfejs i njegove funkcionalnosti.

## Sledeći koraci
- Isprobajte različite modele kao što su `gpt-oss` i drugi najsavremeniji modeli.
- Eksperimentišite sa različitim pozadinskim sistemima na fino podešenom modelu
 
Za više dokumentacije, posetite: https://llamafactory.readthedocs.io/en/latest/