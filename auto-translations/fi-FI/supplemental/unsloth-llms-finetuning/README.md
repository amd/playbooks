<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Konekäännös.** Tämä sivu on käännetty automaattisesti englannista, eikä sitä ole tarkistanut ihminen. Se voi sisältää virheitä, ja tietyt ohjeet, komennot, lataukset, tuotteiden saatavuus tai muu sisältö voivat vaihdella kielen tai alueen mukaan. Mahdollisten ristiriitaisuuksien tai epäjohdonmukaisuuksien ilmetessä alkuperäinen englanninkielinen playbook on ratkaiseva ja ensisijainen versio.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Yleiskatsaus

Tämä ohjekirja näyttää, miten kielimalli hienosäädetään paikallisesti Unslothilla AMD-laitteistolla.

Se käyttää lyhyttä Supervised Fine-Tuning (SFT) -esimerkkiä LoRA-adaptereilla mallissa `unsloth/gemma-4-E4B-it`, käyttäen osajoukkoa `mlabonne/FineTome-100k`-datajoukosta. Tavoitteena on tarjota yksinkertainen päästä päähän -työnkulku, joka kattaa asennuksen, koulutuksen, päättelyn ja hienosäädetyn tuloksen tallentamisen.

Esimerkki on suunniteltu käytännölliseksi ja helposti muokattavaksi, jotta voit käyttää sitä lähtökohtana omille datajoukoillesi ja malleillesi.

## Mitä opit

- Kuinka asettaa Unsloth-ympäristö
- Kuinka hienosäätää LLM-malli käyttäen SFT:tä Unslothin kanssa
- Kuinka tallentaa hienosäädetty tulos paikalliseen tallennustilaan

<!-- @device:halo,stx,krk -->
> **Huomautus:** Tässä ohjekirjassa esitellyt hienosäätötekniikat vaativat vähintään **64 Gt järjestelmämuistia**, josta vähintään **24 Gt on oltava GPU:n käytettävissä** (24 Gt on osa 64 Gt:sta, ei sen lisäksi).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Huomautus:** Tässä ohjekirjassa esitellyt hienosäätötekniikat vaativat vähintään **24 Gt GPU-muistia yhteensä** ja **32 Gt järjestelmämuistia**.
> - Windowsissa GPU:n kokonaismuisti yhdistää näytönohjaimen omistetun VRAM-muistin ja jaetun GPU-muistin (lainattu järjestelmämuistista).
> - Tämän ansiosta näytönohjaimet, joissa on alle 24 Gt omistettua VRAM-muistia, voivat silti ajaa tämän ohjekirjan käyttämällä jaettua GPU-muistia erotuksen täyttämiseen.
<!-- @os:end -->

<!-- @os:linux -->
> **Huomautus:** Tässä ohjekirjassa esitellyt hienosäätötekniikat vaativat näytönohjaimen, jossa on vähintään **24 Gt omistettua GPU-muistia**, sekä **32 Gt järjestelmämuistia**.
> - Linuxissa koulutus suoritetaan kokonaan näytönohjaimen omistetussa VRAM-muistissa.
> - Se ei siirry käyttämään jaettua GPU-muistia (järjestelmämuistia), kun VRAM-muisti loppuu.
> - Näytönohjaimet, joissa on alle 24 Gt omistettua VRAM-muistia, loppuvat muistista koulutuksen aikana Linuxissa, vaikka järjestelmässä olisi runsaasti RAM-muistia.
<!-- @os:end -->
<!-- @device:end -->

## Miksi Unsloth?

Unsloth helpottaa LLM-mallien hienosäätöä paikallisella laitteistolla vähentämällä muistin käyttöä ja nopeuttamalla koulutusta verrattuna tavalliseen asennukseen.

Tässä ohjekirjassa käytämme Unslothia yhdessä **LoRA-pohjaisen SFT:n** kanssa. Tämä tarkoittaa, että perusmalli pysyy pääosin jäädytettynä, kun taas paljon pienempi joukko adapteripainoja koulutetaan. Tämä sopii hyvin paikalliseen kehitystyöhön, koska se on kevyempi kuin täysi hienosäätö ja nopeampi iteroitava.

Unsloth tukee myös muita koulutusmenetelmiä, mukaan lukien QLoRA ja vahvistusoppimisen työnkulut. Tämä ohjekirja keskittyy ensin yksinkertaisimpaan tapaan: pieneen LoRA-hienosäätöesimerkkiin, jonka käyttäjät voivat ajaa, ymmärtää ja laajentaa.

<!-- @device:halo_box,halo,stx,krk -->
## Muistiasetuksen määrittäminen

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset
> **Huomautus**: Jos VS Code ei ole asennettuna, voit asentaa sen Ryzen AI Developer Centerin kautta.

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmiston esivaatimusten asentaminen

### Luo virtuaaliympäristö

<!-- @os:linux -->
<!-- @device:halo_box -->
Avaa pääte ja luo venv, johon AMD ROCm™ -ohjelmisto ja PyTorch on jo asennettu:
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
python3 -m venv unsloth-env --system-site-packages
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Myönnä käyttäjällesi käyttöoikeus GPU-laitteisiin** (kirjaudu ulos ja takaisin sisään, jotta tämä tulee voimaan):

```bash
sudo usermod -aG render,video $LOGNAME
```

Avaa pääte ja luo venv:
<!-- @test:id=create-venv timeout=300 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv unsloth-env
source unsloth-env/bin/activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="source unsloth-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **Huomautus:** Windowsissa vaaditaan Python 3.13.

<!-- @device:halo_box -->
Avaa PowerShell-pääte ja luo virtuaaliympäristö:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Avaa PowerShell-pääte ja luo virtuaaliympäristö:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Perusriippuvuuksien asentaminen
<!-- @require:driver -->

> **Tärkeää:** Unsloth ei vielä tue PyTorch 2.13 -versiota, joka toimitetaan ROCm 10:n mukana. Tätä ohjekirjaa varten asenna **ROCm 7.14 ja PyTorch 2.12** alla olevilla komennoilla. Älä käytä ROCm 10 / PyTorch 2.13 -paketteja.

**Asenna PyTorch AMD ROCm™ -ohjelmiston tuella** luotuun virtuaaliympäristöön:

<!-- @device:halo,halo_box -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1151]==2.12.0+rocm7.14.0" "torchvision[device-gfx1151]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1150]==2.12.0+rocm7.14.0" "torchvision[device-gfx1150]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:krk -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1152]==2.12.0+rocm7.14.0" "torchvision[device-gfx1152]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx7900xt -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1100]==2.12.0+rocm7.14.0" "torchvision[device-gfx1100]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx9070xt,r9700 -->
<!-- @test:id=install-pytorch timeout=600 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl-multi-arch/ "torch[device-gfx1201]==2.12.0+rocm7.14.0" "torchvision[device-gfx1201]==0.27.0+rocm7.14.0" "torchaudio==2.11.0+rocm7.14.0"
```
<!-- @test:end -->
<!-- @device:end -->

Muiden laitteiden osalta katso täydelliset ohjeet kohdasta [ROCm 7.14 -dokumentaatio](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html).

<!-- @test:id=verify-torch-env timeout=300 hidden=True setup=activate-venv -->
```python
import sys
import torch

print(f"Python executable: {sys.executable}")
print(f"PyTorch version: {torch.__version__}")
print(f"torch.cuda.is_available(): {torch.cuda.is_available()}")

if not torch.cuda.is_available():
    raise SystemExit("FAIL: ROCm-enabled PyTorch is not visible in this venv")

print("PASS: ROCm-enabled PyTorch is visible")
```
<!-- @test:end -->

### Lisäriippuvuudet

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git" triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Huomautus:** Tuonnin aikana Unsloth saattaa tarkistaa valinnaisia `bitsandbytes`-kiihdytyspolkuja. Joissakin ROCm-versioissa saatat nähdä viestin, kuten `bitsandbytes library load error: Configured ROCm binary not found`. Tämä ohjekirja käyttää tavallista LoRA-hienosäätöä asetuksella `optim="adamw_torch"`, joten emme ole riippuvaisia `bitsandbytes`-optimoijasta tai 4-bittisestä QLoRA:sta. Tämän viestin voi jättää huomiotta.

<!-- @os:windows -->
> **Huomautus:** Windows ROCm -ympäristössä Unsloth tulostaa käynnistyksen yhteydessä useita varoituksia — katso [Tunnetut varoitukset](#known-warnings) alla. Nämä kaikki voi turvallisesti jättää huomiotta; koulutus toimii oikein.
<!-- @os:end -->

<!-- @test:id=verify-imports timeout=120 hidden=True setup=activate-venv -->
```python
import unsloth
import torch
from datasets import load_dataset
from transformers import TextStreamer
from unsloth import FastModel
from unsloth.chat_templates import (
    get_chat_template,
    standardize_data_formats,
    train_on_responses_only,
)
from trl import SFTTrainer, SFTConfig

print(f"PyTorch version: {torch.__version__}")
print(f"ROCm available: {torch.cuda.is_available()}")
print("PASS: All required imports succeeded")
```
<!-- @test:end -->

## Lataa Unsloth-hienosäätöskripti

Sen sijaan, että suorittaisit jokaisen vaiheen manuaalisesti, tämä ohjekirja tarjoaa siistin, päästä päähän -skriptin täältä: [test_unsloth.py](assets/test_unsloth.py).

Suorita seuraava koodi skriptin ajamiseksi:

```bash
python test_unsloth.py
```

<!-- @test:id=verify-script timeout=60 hidden=True -->
```python
import os
import sys
import ast

scripts = ["test_unsloth.py", "test_unsloth_ci.py"]
missing = [s for s in scripts if not os.path.exists(s)]

if missing:
    print(f"FAIL: Missing script: {missing}")
    sys.exit(1)
print("PASS: All required script files exist")

for script in scripts:
    with open(script, "r", encoding="utf-8") as f:
        ast.parse(f.read(), filename=script)
    print(f"PASS: {script} has valid syntax")
```
<!-- @test:end -->

<!-- @test:id=quick-train-unsloth timeout=2400 hidden=True setup=activate-venv -->
```bash
python test_unsloth_ci.py
```
<!-- @test:end -->

Ohjekirjan loppuosassa käydään käsitteellisesti läpi jokainen skriptin pääasiallinen vaihe.

## Miten se toimii

test_unsloth.py-skripti suorittaa seuraavat vaiheet:
* **Lataa malli**: Lataa unsloth/gemma-4-E4B-it käyttäen FastModelia.
* **Valmistele data**: Standardoi datajoukon (esim. FineTome-100k) ja soveltaa Gemma-4-keskustelumallipohjaa.
* **Sovella LoRA**: Lisää adaptereita kieli-, huomio- ja MLP-moduuleihin tehokasta koulutusta varten.
* **Kouluta**: Käyttää SFTTraineria vasteperusteisella häviön maskauksella (response-only loss masking).
* **Päättely**: Suorittaa nopean generointitestin suorituskyvyn varmistamiseksi.
* **Tallenna**: Vie LoRA-adapterit paikallisesti.
## Keskeiset asetukset

Voit muokata seuraavia vakioita mukauttaaksesi ajoasi:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Esimerkki Unslothin tervetuloviestistä ja tulosteesta mallin painoja ladattaessa:

![alt text](assets/welcome.png)

## Valmistele tietojoukko

Käytämme osajoukkoa seuraavasta:
```text
mlabonne/FineTome-100k
```
Tietojoukko on:
* Muunnettu chat-muotoon
* Käsitelty Gemma-4-chat-mallipohjalla
* Puhdistettu poistamalla päällekkäiset BOS-tokenit

## Kouluta malli

Skripti suorittaa lyhyen koulutusdemon seuraavilla parametreilla:
- ~50 askelta
- Pieni eräkoko
- Gradienttien kertymä

Koulutuksen aikana näet lokeja, kuten:

![alt text](assets/training.png)


## Tallentaminen ja käyttöönotto

### Paikallinen tallennus (LoRA)

Skripti tallentaa automaattisesti LoRA-sovittimet kohteeseen OUTPUT_DIR.
```python
model.save_pretrained("gemma_4_lora")  
tokenizer.save_pretrained("gemma_4_lora")
```

<!-- @test:id=verify-unsloth-lora-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_lora_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = (
    glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) +
    glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
)
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: Unsloth LoRA output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end -->

### Tallenna yhdistetty malli (vLLM:ää varten)

<!-- @os:windows -->
> **Huomautus:** vLLM ei tue Windowsia. Ota hienosäädetty mallisi käyttöön Windowsissa käyttämällä llama.cpp:tä (katso [Vie GGUF-muotoon](#export-gguf-for-llamacpp) alla) tai siirrä yhdistetty malli Linux-koneelle, jossa vLLM on käytössä.
<!-- @os:end -->

<!-- @os:linux -->
Käyttöönottoa varten vLLM:n kanssa yhdistä sovittimet täydeksi malliksi:
```python
model.save_pretrained_merged("gemma-4-finetune", tokenizer)
```
<!-- @os:end -->

<!-- @test:id=verify-unsloth-merged-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "gemma_4_merged_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing merged model directory: {out_dir}")
    sys.exit(1)

required = [
    "config.json",
    "tokenizer_config.json",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required merged files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Merged model output looks correct")
```
<!-- @test:end -->

### Vie GGUF-muotoon (llama.cpp:tä varten)

Muunna suoraan GGUF-muotoon paikallista päättelyä varten:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Tunnetut varoitukset

Nämä varoitukset tulostaa Unsloth käynnistyksen yhteydessä Windows ROCm -ympäristössä, ja ne kaikki voi turvallisesti jättää huomiotta:

| Varoitus | Syy | Voiko jättää huomiotta? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytesilla ei ole Windows ROCm -käännöstä | Kyllä — tämä ohje käyttää `adamw_torch`-menetelmää, ei bnb:tä |
| `No ROCm platform found for torch.distributed` | ROCm Windowsilla ei tue hajautettua koulutusta | Kyllä — yhden GPU:n koulutukseen tämä ei vaikuta |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth merkitsee ei-Linux-käännökset | Kyllä — Windows ROCm toimii yhden GPU:n SFT-koulutuksessa |
| `triton is not available` | Tritonilla ei ole Windows-käännöstä | Kyllä — Unsloth käyttää sen sijaan PyTorch-ytimiä |

Koulutus etenee oikein näistä varoituksista huolimatta.
<!-- @os:end -->

## Seuraavat vaiheet
- Kokeile [Unsloth Studiota](https://unsloth.ai/docs/new/studio), intuitiivista graafista käyttöliittymää Unslothille
- Kouluta omilla tietojoukoillasi
- Kokeile hienosäätöä eri hyperparametreilla
- Ota käyttöön vLLM:llä tai llama.cpp:llä
- Kokeile QLoRA:a pienemmän muistinkäytön ratkaisuun

## Resurssit

Alla on lisäresursseja, joiden avulla voit oppia lisää Unslothista ja hienosäädöstä:

* [Unsloth-dokumentaatio](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unslothin hienosäätöopas](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)