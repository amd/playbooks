## Yleiskatsaus

Tehokas hienosäätö on välttämätöntä suurten kielimallien (LLM) mukauttamiseksi jatkotehtäviin. LLaMA-Factory on avoimen lähdekoodin ja käyttäjäystävällinen alusta, joka yksinkertaistaa suurten kielimallien ja multimodaalisten mallien kouluttamista ja hienosäätöä. Sen avulla käyttäjät voivat mukauttaa satoja esikoulutettuja malleja paikallisesti minimaalisella koodauksella.

Tämä opas opettaa sinulle, kuinka hienosäätää LLM-malleja LLaMA-Factoryn avulla paikallisella AMD-laitteistollasi.

<!-- @device:stx,krk -->
> **Huomio:** Tämän oppaan hienosäätötekniikat vaativat vähintään **32 Gt järjestelmämuistia (RAM)**, josta vähintään **16 Gt on oltava GPU:n käytettävissä** (nämä 16 Gt sisältyvät 32 Gt:iin, eivät ole sen lisäksi).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Huomio:** Tämän oppaan hienosäätötekniikat vaativat vähintään **16 Gt GPU-muistia yhteensä** ja **32 Gt järjestelmämuistia (RAM)**.
> - Windowsissa GPU-muistin kokonaismäärä koostuu näytönohjaimen omasta VRAM-muistista sekä jaetusta GPU-muistista (lainattu järjestelmämuistista).
> - Siksi näytönohjaimet, joissa on alle 16 Gt omaa VRAM-muistia, voivat silti suorittaa tämän oppaan käyttämällä jaettua GPU-muistia erotuksen kattamiseen.
<!-- @os:end -->

<!-- @os:linux -->
> **Huomio:** Tämän oppaan hienosäätötekniikat vaativat näytönohjaimen, jossa on vähintään **16 Gt omaa GPU-muistia**, sekä **32 Gt järjestelmämuistia (RAM)**.
> - Linuxissa koulutus suoritetaan kokonaan näytönohjaimen omassa VRAM-muistissa.
> - Se ei siirry käyttämään jaettua GPU-muistia (järjestelmämuistia), kun VRAM loppuu.
> - Näytönohjaimet, joissa on alle 16 Gt omaa VRAM-muistia, loppuvat muistista koulutuksen aikana Linuxissa, vaikka järjestelmässä olisi runsaasti RAM-muistia.
<!-- @os:end -->
<!-- @device:end -->

## Mitä opit

- Kuinka asentaa LLaMA-Factory AMD ROCm™ -ohjelmiston kanssa
- Kuinka määrittää LLM-hienosäätöparametrit (esimerkkinä Qwen/Qwen3-4B-Instruct-2507)
- Kuinka suorittaa LLaMA-Factory-hienosäätö
- Kuinka suorittaa päättely hienosäädetyllä mallilla
- Kuinka viedä hienosäädetty malli

## Arvioitu aika

- Kesto: Tämän oppaan suorittaminen kestää noin 60 minuuttia (riippuen mallisi/tietoaineistosi koosta ja verkkonopeudesta).
- Lisätietoja löydät [LLaMA-Factoryn GitHubista](https://github.com/hiyouga/LlamaFactory).

## Muistikonfiguraation asettaminen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmistoedellytysten asentaminen

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

#### Luo virtuaaliympäristö

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
**Myönnä käyttäjällesi pääsy GPU-laitteisiin** (kirjaudu ulos ja takaisin sisään, jotta muutos tulee voimaan):

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

### Perusriippuvuuksien asentaminen

<!-- @require:pytorch,driver -->
 
### Lisäriippuvuuksien asentaminen

> **Huomio**: Varmista, että Python-versio on 3.11, 3.12 tai 3.13

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

### Asenna LLaMA-Factory

LLaMA-Factory on riippuvainen PyTorchista. Sen pitäisi olla jo asennettuna yllä olevien vaatimusten mukaisesti.

Lataa lähdekoodi [LLaMA-Factoryn virallisesta GitHub-repositoriosta](https://github.com/hiyouga/LlamaFactory) ja asenna sen riippuvuudet.

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

Tarkista, onko `llamafactory-cli` suoritettavissa.

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

Esimerkkituloste:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

Kun LLaMA-Factory on asennettu onnistuneesti, suoritetaan hienosäätö sen avulla.

## LLaMA-Factory CLI:n käyttäminen hienosäätöön

Tässä osiossa käsitellään hienosäätötietoaineistojen valmistelua, LoRA/QLoRA-parametrien määrittämistä ja LoRA-hienosäädön suorittamista.

### Tietoaineiston valmistelu

LLaMA-Factory tukee hienosäätötietoaineistoja Alpaca-muodossa ja ShareGPT-muodossa. Kaikki saatavilla olevat tietoaineistot on määritelty tiedostossa [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). Jos käytät mukautettua tietoaineistoa, varmista, että lisäät tietoaineiston kuvauksen `dataset_info.json`-tiedostoon ja määrität tietoaineiston nimen ennen koulutusta. Lisätietoja löytyy heidän dokumentaatiostaan [täältä](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

Tässä oppaassa käytämme esimerkkinä identity- ja alpaca_en_demo-tietoaineistoja ja määritämme tietoaineiston tiedot seuraavassa vaiheessa.


### Hienosäätöparametrien konfigurointi

LLaMA-Factory tukee useita hienosäätömenetelmiä.

| Hienosäätömenetelmät | LLaMA-Factory-esimerkit |
|-----------|------|
| Täysi parametrihienosäätö    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| LoRA-hienosäätö  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| QLoRA-hienosäätö | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

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

Nämä esimerkkikonfiguraatiotiedostot sisältävät malliparametrit, hienosäätömenetelmän parametrit, tietoaineistoparametrit, arviointiparametrit ja paljon muuta. Voit määrittää ne omien tarpeidesi mukaan. Tässä oppaassa käytämme tiedostoa [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml).

**Keskeisten parametrien selitykset:**
- `model_name_or_path` - Hugging Face -mallin nimi tai paikallisen mallitiedoston polku.
- `stage` - Koulutuksen vaihe. Vaihtoehdot: rm (reward modeling), pt (pretrain), sft (ohjattu hienosäätö), PPO, DPO, KTO, ORPO.
- `do_train` - true koulutukselle, false arviointia varten
- `finetuning_type` - Hienosäätömenetelmä. Vaihtoehdot: freeze, lora, full
- `lora_rank` - LoRA:ssa käytetyn matalan rankin matriisin dimensionaalisuus, tyypilliset arvot: 4, 6, 8, 16 (pienemmät arvot = vähemmän parametreja = nopeampi hienosäätö; suuremmat arvot = parempi tehtäväadaptaatio mutta suurempi resurssien käyttö).
- `lora_target` - LoRA-menetelmän kohdemodullit. Oletus: all.
- `dataset` - Käytettävä tietoaineisto tai tietoaineistot. Käytä "," erottamaan useita tietoaineistoja
- `output_dir` - Hienosäädön tulostuspolku
- `logging_steps` - Lokitusväli askeleissa
- `save_steps` - Mallin tarkistuspisteen tallennusväli.
- `overwrite_output_dir` - Sallitaanko tulostushakemiston ylikirjoittaminen.
- `per_device_train_batch_size` - Koulutuksen eräkoko laitetta kohden.
- `gradient_accumulation_steps` - Gradienttien kertymisaskelten määrä.
- `learning_rate` - Oppimisnopeus
- `num_train_epochs` - Koulutusepookkien määrä
- `lr_scheduler_type` - Oppimisnopeuden aikataulu. Vaihtoehdot: linear, cosine, polynomial, constant jne.
- `warmup_ratio` - Oppimisnopeuden lämmittelysuhde

<!-- @os:linux -->
Muutamme `lora_rank`-oletusarvoa suorittaaksemme hienosäädön AMD Ryzen™- ja AMD Radeon™ GPU:illa.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
Päivitämme LoRA-hienosäädön oletuskonfiguraation paremman yhteensopivuuden saavuttamiseksi AMD Ryzen™- ja AMD Radeon™ GPU:iden kanssa:
- Asetetaan `lora_rank` arvosta `8` arvoon `6` muistin käytön vähentämiseksi hienosäädön aikana.
- Käytetään `fp16`:ta `bf16`:n sijaan laajemman AMD GPU -yhteensopivuuden ja pienemmän muistin käytön vuoksi.
- Asetetaan `dataloader_num_workers` arvoon `0` Windowsissa, jotta vältetään `"Can't pickle local object<>"` -virheet, jotka johtuvat moniprosessoinnin datalatauksesta.

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

### Suorita LLaMA-Factory-hienosäätö

**llamafactory-cli** on LLaMA-Factoryn virallinen komentorivityökalu (CLI), joka on kehitetty yksinkertaistamaan LLM-työnkulkuja päästä päähän (datan valmistelu → hienosäätö → arviointi → käyttöönotto) ilman monimutkaisen koodin kirjoittamista.

Koulutusta/hienosäätöä varten **llamafactory-cli train** on LLaMA-Factory CLI:n ydinalikomento. Se abstrahoi hienosäätötyönkulut (datan esikäsittely, hyperparametrien viritys, laitteiston optimointi) yhdeksi CLI-komennoksi, tukee useita hienosäätöparadigmoja (LoRA/QLoRA/täysi hienosäätö) ja on optimoitu vähäresurssisille GPU:ille (esim. QLoRA 16 Gt VRAM:lla).

Voit suorittaa LLaMA-Factory-hienosäädön seuraavalla komennolla, joka perustuu muokattuun Qwen3 LoRA -hienosäätökonfiguraatiotiedostoon.

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

LLM-hienosäädön suorittamisen jälkeen kaikki luodut tulosteet tallennetaan "output_dir"-hakemistoon, mukaan lukien mallin tarkistuspistetiedostot, konfiguraatiotiedostot ja koulutusmetriikat.

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

### Testaa hienosäädetty malli

**llamafactory-cli chat** on suunniteltu interaktiiviseen chat-käyttöön/päättelyyn LLM-mallien kanssa (sekä perusmallit että LoRA-hienosäädetyt mallit). LLaMA-Factory tarjoaa esimerkkikonfiguraation hienosäädettyjen mallien päättelyn suorittamiseen hakemistossa [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference). Voit myös muokata tätä esimerkkikonfiguraatiota muuttaaksesi asetuksia, kuten päättelytaustajärjestelmää.

Käytä seuraavaa komentoa Qwen3-hienosäädetyn mallin testaamiseen:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
Alla on esimerkki chat-keskustelusta hienosäädetyn mallin kanssa:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### Vie hienosäädetty malli

Tuotantokäyttötapauksissa esikoulutettu malli ja LoRA-adapteri on yhdistettävä ja vietävä yhdeksi malliksi. Tätä yhdistettyä mallia voidaan käyttää tavallisena Hugging Face -mallitiedostona. LLaMA-Factory tarjoaa esimerkkikonfiguraatiot hakemistossa [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora).

Käytä seuraavaa komentoa Qwen3-hienosäädetyn mallin viemiseen:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
Hienosäädetyn mallin viennin tulos on esitetty alla.

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

## LLaMA-Factory GUI:n käyttäminen

`LLaMA-Factory` tukee myös LLM-mallien koodittomia hienosäätöjä selaimen verkkokäyttöliittymän kautta.

Avaa se seuraavalla komennolla:

```bash
llamafactory-cli webui
```
`LlamaFactory Web UI` tarjoaa virtaviivaistetun käyttöliittymän koneoppimisen työnkulkujen hallintaan, mukaan lukien koulutus, arviointi, ennustaminen, chat-toiminto ja mallien vienti. Tässä on lyhyt esittely jokaisesta välilehdestä:

* **Train**: Tällä välilehdellä voit valita mallin ja tietoaineiston, määrittää koulutusparametrit ja käynnistää koulutusprosessin. On tärkeää ymmärtää pakolliset ja valinnaiset parametrit koulutusasetuksen optimoimiseksi.
* **Evaluate & Predict**: Koulutuksen jälkeen voit arvioida mallin suorituskykyä ja tehdä ennusteita tällä välilehdellä. Se tarjoaa tietoa mallin tarkkuudesta ja tehokkuudesta uudella datalla.
* **Chat**: Kun koulutus on valmis, lataa malli Chat-välilehdelle ollaksesi vuorovaikutuksessa sen kanssa ja nähdäksesi työsi tulokset. Tämä ominaisuus mahdollistaa reaaliaikaisen viestinnän koulutetun mallin kanssa.
* **Export**: Tämä välilehti helpottaa koulutettujen mallien vientiä käyttöönottoa tai jatkokäyttöä varten. Voit tallentaa mallisi eri muodoissa, jotka sopivat eri sovelluksiin.

Yksityiskohtaista ohjausta varten suosittelemme tutustumaan viralliseen dokumentaatioon [LlamaFactory GitHub -repositoriossa](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) ja [LlamaFactory ReadTheDocsissa](https://llamafactory.readthedocs.io/en/latest). Lisäksi [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) tarjoaa arvokkaita näkemyksiä käyttöliittymästä ja sen toiminnoista.

## Seuraavat vaiheet
- Kokeile eri malleja, kuten `gpt-oss` ja muita huippuluokan malleja.
- Kokeile eri taustajärjestelmiä hienosäädetyllä mallilla
 
Lisää dokumentaatiota löydät osoitteesta: https://llamafactory.readthedocs.io/en/latest/