<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Yleiskatsaus

Tämä playbook näyttää, kuinka kielimalli hienosäädetään paikallisesti Unsloth-työkalulla AMD-laitteistolla.

Se käyttää lyhyttä Supervised Fine-Tuning (SFT) -esimerkkiä LoRA-adaptereilla mallilla `unsloth/gemma-4-E4B-it`, hyödyntäen osajoukkoa `mlabonne/FineTome-100k`-datasetistä. Tavoitteena on tarjota yksinkertainen päästä päähän -työnkulku, joka kattaa asennuksen, koulutuksen, inferenssin ja hienosäädetyn tuloksen tallentamisen.

Esimerkki on suunniteltu käytännölliseksi ja helposti muokattavaksi, joten voit käyttää sitä lähtökohtana omille dataseteillesi ja malleillesi.

## Mitä opit

- Kuinka Unsloth-ympäristö asennetaan
- Kuinka LLM hienosäädetään SFT:llä Unsloth-työkalulla
- Kuinka hienosäädetty tulos tallennetaan paikalliseen tallennustilaan

<!-- @device:halo,stx,krk -->
> **Huomio:** Tämän playbookin hienosäätötekniikat vaativat vähintään 24 Gt GPU-muistia ja 32 Gt järjestelmämuistia.
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Huomio:** Tämän playbookin hienosäätötekniikat vaativat vähintään 24 Gt GPU-muistia ja 32 Gt järjestelmämuistia.
<!-- @os:end -->

<!-- @os:linux -->
> **Huomio:** Tämän playbookin hienosäätötekniikat vaativat vähintään 24 Gt **dedikoitua** GPU-muistia ja 32 Gt järjestelmämuistia.
<!-- @os:end -->
<!-- @device:end -->

## Miksi Unsloth?

Unsloth helpottaa LLM-hienosäätöä paikallisella laitteistolla vähentämällä muistinkäyttöä ja nopeuttamalla koulutusta verrattuna tavalliseen asennukseen.

Tässä playbookissa käytämme Unslotha yhdessä **LoRA-pohjaisen SFT:n** kanssa. Tämä tarkoittaa, että perusmalli pysyy suurimmaksi osaksi jäädytettynä, kun taas paljon pienempi joukko adapterin painoja koulutetaan. Tämä sopii hyvin paikalliseen kehitykseen, koska se on kevyempää kuin täysi hienosäätö ja nopeampaa iteroida.

Unsloth tukee myös muita koulutustapoja, kuten QLoRA:a ja vahvistusoppimisen työnkulkuja. Tämä playbook keskittyy ensin yksinkertaisimpaan polkuun: pieneen LoRA-hienosäätöesimerkkiin, jonka käyttäjät voivat ajaa, ymmärtää ja laajentaa.

## Muistikonfiguraation asettaminen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset
> **Huomio**: Jos VS Code ei ole asennettuna, voit asentaa sen Ryzen AI Developer Centerin kautta.

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmistoedellytysten asentaminen

### Luo virtuaaliympäristö

<!-- @os:linux -->
<!-- @device:halo_box -->
Avaa terminaali ja luo venv, johon AMD ROCm™ -ohjelmisto ja PyTorch on jo asennettu:
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
**Myönnä käyttäjällesi pääsy GPU-laitteisiin** (kirjaudu ulos ja takaisin sisään, jotta muutos tulee voimaan):

```bash
sudo usermod -aG render,video $LOGNAME
```

Avaa terminaali ja luo venv:
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
> **Huomio:** Windows vaatii Python 3.13:n.

<!-- @device:halo_box -->
Avaa PowerShell-terminaali ja luo virtuaaliympäristö:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Avaa PowerShell-terminaali ja luo virtuaaliympäristö:
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

> **Huomio:** Tuonnin aikana Unsloth saattaa kokeilla valinnaisia `bitsandbytes`-kiihdytyspolkuja. Joissakin ROCm-versioissa saatat nähdä viestin kuten `bitsandbytes library load error: Configured ROCm binary not found`. Tämä playbook käyttää tavallista LoRA-hienosäätöä `optim="adamw_torch"`-asetuksella, joten emme nojaa `bitsandbytes`-optimoijaan tai 4-bittiseen QLoRA:han. Tämä viesti voidaan turvallisesti ohittaa.

<!-- @os:windows -->
> **Huomio:** Windows ROCm -ympäristössä Unsloth tulostaa useita varoituksia käynnistyksen yhteydessä — katso [Tunnetut varoitukset](#known-warnings) alta. Nämä kaikki voidaan turvallisesti ohittaa; koulutus toimii oikein.
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

Sen sijaan, että suorittaisit jokaisen vaiheen manuaalisesti, tämä playbook tarjoaa selkeän, päästä päähän -skriptin täällä: [test_unsloth.py](assets/test_unsloth.py).

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

Playbookin loppuosa käy käsitteellisesti läpi jokaisen skriptin päävaiheen.

## Kuinka se toimii

test_unsloth.py-skripti suorittaa seuraavat vaiheet:
* **Lataa malli**: Lataa unsloth/gemma-4-E4B-it FastModel-luokan avulla.
* **Valmistelee datan**: Standardisoi datasetin (esim. FineTome-100k) ja soveltaa Gemma-4-chat-mallipohjaa.
* **Soveltaa LoRA:a**: Lisää adapterit kieli-, huomio- ja MLP-moduuleihin tehokasta koulutusta varten.
* **Kouluttaa**: Käyttää SFTTraineria vain vastauksen häviöpeittämisellä.
* **Inferenssi**: Suorittaa nopean generointitestin suorituskyvyn varmistamiseksi.
* **Tallentaa**: Vie LoRA-adapterit paikallisesti.

## Keskeinen konfiguraatio

Voit muokata seuraavia vakioita mukauttaaksesi ajoa:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Esimerkki Unsloth-tervetuloviestistä ja tulosteesta mallin painoja ladattaessa:

![vaihtoehtoinen teksti](assets/welcome.png)

## Valmistele datasetti

Käytämme osajoukkoa seuraavasta:
```text
mlabonne/FineTome-100k
```
Datasetti on:
* Muunnettu chat-muotoon
* Käsitelty Gemma-4-chat-mallipohjalla
* Puhdistettu poistamalla päällekkäiset BOS-tunnukset

## Kouluta malli

Skripti suorittaa lyhyen koulutusesittelyn seuraavilla parametreilla:
- ~50 askelta
- Pieni eräkoko
- Gradienttien kertyminen

Koulutuksen aikana näet lokeja kuten:

![vaihtoehtoinen teksti](assets/training.png)


## Tallentaminen ja käyttöönotto

### Paikallinen tallentaminen (LoRA)

Skripti tallentaa LoRA-adapterit automaattisesti OUTPUT_DIR-hakemistoon.
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
> **Huomio:** vLLM ei tue Windowsia. Ottaaksesi hienosäädetyn mallisi käyttöön Windowsissa, käytä llama.cpp:tä (katso [Vie GGUF](#export-gguf-for-llamacpp) alta) tai siirrä yhdistetty malli Linux-koneelle, jossa vLLM on käynnissä.
<!-- @os:end -->

<!-- @os:linux -->
Yhdistä adapterit täydeksi malliksi vLLM-käyttöönottoa varten:
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

### Vie GGUF (llama.cpp:tä varten)

Muunna suoraan GGUF-muotoon paikallista inferenssiä varten:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Tunnetut varoitukset

Nämä varoitukset tulostaa Unsloth käynnistyksen yhteydessä Windows ROCm -ympäristössä, ja ne kaikki voidaan turvallisesti ohittaa:

| Varoitus | Syy | Turvallinen ohittaa? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes-kirjastolla ei ole Windows ROCm -versiota | Kyllä — tämä playbook käyttää `adamw_torch`-optimoijaa, ei bnb:tä |
| `No ROCm platform found for torch.distributed` | ROCm Windowsilla ei tue hajautettua koulutusta | Kyllä — yksittäisen GPU:n koulutus ei ole vaikuttunut |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth merkitsee muut kuin Linux-versiot | Kyllä — Windows ROCm toimii yksittäisen GPU:n SFT:ssä |
| `triton is not available` | Tritonilla ei ole Windows-versiota | Kyllä — Unsloth käyttää varasuunnitelmana PyTorch-ytimiä |

Koulutus etenee oikein näistä varoituksista huolimatta.
<!-- @os:end -->

## Seuraavat askeleet
- Kokeile [Unsloth Studiota](https://unsloth.ai/docs/new/studio), intuitiivista graafista käyttöliittymää Unslothille
- Kouluta omilla erityisdataseteillasi
- Kokeile hienosäätöä eri hyperparametreilla
- Ota käyttöön vLLM:llä tai llama.cpp:llä
- Kokeile QLoRA:a pienemmän muistinkäytön asennuksessa

## Resurssit

Alla on lisäresursseja Unslothin ja hienosäädön oppimiseen:

* [Unsloth-dokumentaatio](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth-hienosäätöopas](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)