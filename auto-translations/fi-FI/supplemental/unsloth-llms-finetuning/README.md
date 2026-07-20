<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Tässä ohjekirjassa käytetään erikoismerkintöjä, joita GitHub ei pysty renderöimään. Käy osoitteessa [amd.com/playbooks](https://amd.com/playbooks) nähdäksesi tämän sisällön oikein.
<!-- @github-only:end -->

## Yleiskatsaus

Tämä ohjekirja näyttää, miten kielimalli hienosäädetään paikallisesti Unslothilla AMD-laitteistolla.

Siinä käytetään lyhyttä ohjatun hienosäädön (Supervised Fine-Tuning, SFT) esimerkkiä LoRA-adaptereilla mallissa `unsloth/gemma-4-E4B-it`, hyödyntäen osajoukkoa `mlabonne/FineTome-100k`-tietoaineistosta. Tavoitteena on tarjota yksinkertainen päästä päähän -työnkulku, joka kattaa asennuksen, koulutuksen, päättelyn ja hienosäädetyn tuloksen tallentamisen.

Esimerkki on suunniteltu käytännönläheiseksi ja helposti muokattavaksi, joten voit käyttää sitä lähtökohtana omille tietoaineistoillesi ja malleillesi.

## Mitä opit

- Miten Unsloth-ympäristö asennetaan
- Miten LLM hienosäädetään SFT:llä käyttäen Unslothia
- Miten hienosäädetty tulos tallennetaan paikalliseen tallennustilaan

<!-- @device:halo,stx,krk -->
> **Huomautus:** Tässä ohjekirjassa käytettävät hienosäätötekniikat vaativat vähintään 24 Gt GPU-muistia ja 32 Gt järjestelmämuistia.
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Huomautus:** Tässä ohjekirjassa käytettävät hienosäätötekniikat vaativat vähintään 24 Gt GPU-muistia ja 32 Gt järjestelmämuistia.
<!-- @os:end -->

<!-- @os:linux -->
> **Huomautus:** Tässä ohjekirjassa käytettävät hienosäätötekniikat vaativat vähintään 24 Gt **erillistä** GPU-muistia ja 32 Gt järjestelmämuistia.
<!-- @os:end -->
<!-- @device:end -->

## Miksi Unsloth?

Unsloth helpottaa LLM-hienosäädön suorittamista paikallisella laitteistolla vähentämällä muistinkäyttöä ja nopeuttamalla koulutusta verrattuna tavalliseen asetukseen.

Tässä ohjekirjassa käytämme Unslothia yhdessä **LoRA-pohjaisen SFT:n** kanssa. Tämä tarkoittaa, että peruskielimalli pysyy suurelta osin jäädytettynä, kun taas paljon pienempi joukko adapteripainoja koulutetaan. Tämä sopii hyvin paikalliseen kehitykseen, koska se on kevyempi kuin täysi hienosäätö ja nopeampi iteroida.

Unsloth tukee myös muita koulutustapoja, mukaan lukien QLoRA ja vahvistusoppimisen työnkulkuja. Tämä ohjekirja keskittyy ensin yksinkertaisimpaan polkuun: pieneen LoRA-hienosäätöesimerkkiin, jonka käyttäjät voivat suorittaa, ymmärtää ja laajentaa.

## Muistiasetuksen määrittäminen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset
> **Huomautus**: Jos VS Code ei ole asennettuna, voit asentaa sen Ryzen AI Developer Centerin kautta.

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmiston esivaatimusten asentaminen

### Virtuaaliympäristön luominen

<!-- @os:linux -->
<!-- @device:halo_box -->
Avaa pääte ja luo venv-ympäristö, jossa AMD ROCm™ -ohjelmisto ja PyTorch ovat jo asennettuina:
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
**Myönnä käyttäjällesi pääsy GPU-laitteisiin** (kirjaudu ulos ja takaisin sisään, jotta tämä tulee voimaan):

```bash
sudo usermod -aG render,video $LOGNAME
```

Avaa pääte ja luo venv-ympäristö:
<!-- @test:id=create-venv timeout=120 -->
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
> **Huomautus:** Python 3.13 vaaditaan Windowsissa.

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
<!-- @require:pytorch,driver -->

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
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Huomautus:** Tuonnin aikana Unsloth saattaa tutkia valinnaisia `bitsandbytes`-kiihdytyspolkuja. Joissakin ROCm-versioissa saatat nähdä viestin, kuten `bitsandbytes library load error: Configured ROCm binary not found`. Tämä ohjekirja käyttää tavanomaista LoRA-hienosäätöä asetuksella `optim="adamw_torch"`, joten emme ole riippuvaisia `bitsandbytes`-optimoijasta tai 4-bittisestä QLoRA:sta. Tämän viestin voi turvallisesti jättää huomiotta.

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

Sen sijaan, että suoritettaisiin jokainen vaihe manuaalisesti, tämä ohjekirja tarjoaa selkeän, päästä päähän -skriptin täällä: [test_unsloth.py](assets/test_unsloth.py).

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

Ohjekirjan loppuosa käy käsitteellisesti läpi jokaisen skriptin tärkeimmän vaiheen.

## Miten se toimii

test_unsloth.py-skripti suorittaa seuraavat vaiheet:
* **Mallin lataus**: Lataa unsloth/gemma-4-E4B-it -mallin käyttäen FastModel-luokkaa.
* **Datan valmistelu**: Standardisoi tietoaineiston (esim. FineTome-100k) ja soveltaa Gemma-4-keskustelumallipohjaa.
* **LoRA:n soveltaminen**: Lisää adaptereita kieli-, huomio- ja MLP-moduuleihin tehokasta koulutusta varten.
* **Koulutus**: Käyttää SFTTraineria vastauskohtaisella häviön maskauksella.
* **Päättely**: Suorittaa nopean generointitestin suorituskyvyn tarkistamiseksi.
* **Tallennus**: Vie LoRA-adapterit paikallisesti.

## Keskeiset asetukset

Voit muokata seuraavia vakioita ajon mukauttamiseksi:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Esimerkki Unslothin tervetuloviestistä ja tulosteesta mallin painojen latautuessa:

![alt text](assets/welcome.png)

## Tietoaineiston valmistelu

Käytämme osajoukkoa:
```text
mlabonne/FineTome-100k
```
Tietoaineisto on:
* Muunnettu keskustelumuotoon
* Käsitelty Gemma-4-keskustelumallipohjalla
* Puhdistettu duplikaatti-BOS-tunnisteista

## Mallin koulutus

Skripti suorittaa lyhyen koulutusdemonstraation seuraavilla parametreilla:
- ~50 askelta
- Pieni eräkoko
- Gradienttien kumulointi

Koulutuksen aikana näet lokeja, kuten:

![alt text](assets/training.png)


## Tallennus ja käyttöönotto

### Paikallinen tallennus (LoRA)

Skripti tallentaa automaattisesti LoRA-adapterit OUTPUT_DIR-hakemistoon.
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

### Yhdistetyn mallin tallentaminen (vLLM:ää varten)

<!-- @os:windows -->
> **Huomautus:** vLLM ei tue Windowsia. Ottaaksesi hienosäädetyn mallisi käyttöön Windowsissa, käytä llama.cpp:tä (katso [Vie GGUF](#export-gguf-for-llamacpp) alla) tai siirrä yhdistetty malli Linux-koneelle, jossa vLLM on käynnissä.
<!-- @os:end -->

<!-- @os:linux -->
Käyttöönottoa varten vLLM:llä, yhdistä adapterit täydeksi malliksi:
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

### GGUF:n vienti (llama.cpp:tä varten)

Muunna suoraan GGUF-muotoon paikallista päättelyä varten:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Tunnetut varoitukset

Nämä varoitukset tulostaa Unsloth käynnistyksen yhteydessä Windows ROCm -ympäristössä, ja ne kaikki voi turvallisesti jättää huomiotta:

| Varoitus | Syy | Voiko jättää huomiotta? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes-kirjastolle ei ole Windows ROCm -käännöstä | Kyllä — tämä ohje käyttää `adamw_torch`-optimoijaa, ei bnb:tä |
| `No ROCm platform found for torch.distributed` | Windows-versiosta ROCm:sta puuttuu hajautetun koulutuksen tuki | Kyllä — yhden GPU:n koulutus ei tästä kärsi |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth merkitsee muut kuin Linux-käännökset | Kyllä — Windows ROCm toimii yhden GPU:n SFT-koulutukseen |
| `triton is not available` | Tritonille ei ole Windows-käännöstä | Kyllä — Unsloth käyttää tällöin PyTorch-ytimiä |

Koulutus etenee näistä varoituksista huolimatta oikein.
<!-- @os:end -->

## Seuraavat vaiheet
- Kokeile [Unsloth Studiota](https://unsloth.ai/docs/new/studio), intuitiivista graafista käyttöliittymää Unslothille
- Kouluta omilla erityisillä datajoukoillasi
- Kokeile hienosäätöä eri hyperparametreilla
- Ota käyttöön vLLM:llä tai llama.cpp:llä
- Kokeile QLoRA:a vähemmän muistia vaativaa asetusta varten

## Resurssit

Alla on lisää resursseja, joiden avulla voit oppia lisää Unslothista ja hienosäädöstä:

* [Unsloth-dokumentaatio](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth-hienosäätöopas](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)