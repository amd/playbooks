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

Tämä opaskirja näyttää, miten kielimalli hienosäädetään paikallisesti Unslothilla AMD-laitteistolla.

Siinä käytetään lyhyttä ohjatun hienosäädön (Supervised Fine-Tuning, SFT) esimerkkiä LoRA-sovittimilla mallissa `unsloth/gemma-4-E4B-it`, käyttäen osajoukkoa `mlabonne/FineTome-100k`-tietojoukosta. Tavoitteena on antaa yksinkertainen päästä päähän -työnkulku, joka kattaa asennuksen, koulutuksen, päättelyn ja hienosäädetyn tuloksen tallentamisen.

Esimerkki on suunniteltu käytännölliseksi ja helposti muokattavaksi, joten voit käyttää sitä lähtökohtana omille tietojoukoillesi ja malleillesi.

## Mitä opit

- Kuinka Unsloth-ympäristö asennetaan
- Kuinka LLM hienosäädetään SFT:llä Unslothin avulla
- Kuinka hienosäädetty tulos tallennetaan paikalliseen tallennustilaan

<!-- @device:halo,stx,krk -->
> **Huomautus:** Tässä opaskirjassa kuvatut hienosäätötekniikat vaativat vähintään **64 Gt järjestelmämuistia**, josta vähintään **24 Gt tulee olla GPU:n käytettävissä** (24 Gt on osa 64 Gt:sta, ei sen lisäksi).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Huomautus:** Tässä opaskirjassa kuvatut hienosäätötekniikat vaativat vähintään **24 Gt GPU-muistia yhteensä** ja **32 Gt järjestelmämuistia**.
> - Windowsissa GPU:n kokonaismuisti yhdistää näytönohjaimen omistetun VRAM-muistin jaetun GPU-muistin kanssa (joka lainataan järjestelmämuistista).
> - Tämän ansiosta myös näytönohjaimet, joilla on vähemmän kuin 24 Gt omistettua VRAM-muistia, voivat suorittaa tämän opaskirjan käyttämällä jaettua GPU-muistia erotuksen kattamiseen.
<!-- @os:end -->

<!-- @os:linux -->
> **Huomautus:** Tässä opaskirjassa kuvatut hienosäätötekniikat vaativat näytönohjaimen, jolla on vähintään **24 Gt omistettua GPU-muistia**, sekä **32 Gt järjestelmämuistia**.
> - Linuxissa koulutus suoritetaan kokonaan näytönohjaimen omistetussa VRAM-muistissa.
> - Se ei siirry käyttämään jaettua GPU-muistia (järjestelmämuistia), kun VRAM loppuu.
> - Näytönohjaimilta, joilla on vähemmän kuin 24 Gt omistettua VRAM-muistia, muisti loppuu kesken koulutuksen Linuxissa, vaikka järjestelmässä olisi runsaasti RAM-muistia.
<!-- @os:end -->
<!-- @device:end -->

## Miksi Unsloth?

Unsloth helpottaa LLM-mallien hienosäädön suorittamista paikallisella laitteistolla vähentämällä muistinkäyttöä ja nopeuttamalla koulutusta tavalliseen asennukseen verrattuna.

Tässä opaskirjassa käytämme Unslothia yhdessä **LoRA-pohjaisen SFT:n** kanssa. Tämä tarkoittaa, että perusmalli pysyy enimmäkseen jäädytettynä, kun taas paljon pienempi joukko sovitinpainoja koulutetaan. Tämä sopii hyvin paikalliseen kehitystyöhön, koska se on kevyempi kuin täysi hienosäätö ja mahdollistaa nopeamman iteroinnin.

Unsloth tukee myös muita koulutusmenetelmiä, mukaan lukien QLoRA ja vahvistusoppimisen työnkulut. Tämä opaskirja keskittyy ensin yksinkertaisimpaan polkuun: pieneen LoRA-hienosäätöesimerkkiin, jota käyttäjät voivat suorittaa, ymmärtää ja laajentaa.

<!-- @device:halo_box,halo,stx,krk -->
## Muistiasetuksen määrittäminen

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset
> **Huomautus**: Jos VS Code ei ole asennettuna, voit asentaa sen Ryzen AI Developer Centerin kautta.

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmiston edellytysten asentaminen

<!-- @prereq:hf-models-gemma-4-e4b-it,hf-datasets-finetome-100k -->

### Luo virtuaaliympäristö

<!-- @os:linux -->
<!-- @device:halo_box -->
Avaa pääte ja luo venv, johon on jo asennettu AMD ROCm™ -ohjelmisto ja PyTorch:
<!-- @test:id=create-venv timeout=300 -->
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
<!-- @require:driver -->

> **Tärkeää:** Unsloth ei vielä tue ROCm 10:n mukana toimitettavaa PyTorch 2.13 -versiota. Asenna tätä opaskirjaa varten **ROCm 7.14 ja PyTorch 2.12** alla olevilla komennoilla. Älä käytä ROCm 10 / PyTorch 2.13 -paketteja.

**Asenna PyTorch AMD ROCm™ -ohjelmistotuella** luotuun virtuaaliympäristöön:

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

Muita laitteita varten katso täydelliset ohjeet kohdasta [ROCm 7.14 Documentation](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html).

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

> **Huomautus:** Tuonnin aikana Unsloth saattaa tarkistaa valinnaisia `bitsandbytes`-kiihdytyspolkuja. Joissakin ROCm-versioissa saatat nähdä viestin, kuten `bitsandbytes library load error: Configured ROCm binary not found`. Tämä opaskirja käyttää tavallista LoRA-hienosäätöä asetuksella `optim="adamw_torch"`, joten emme ole riippuvaisia `bitsandbytes`-optimoijasta tai 4-bittisestä QLoRA:sta. Tämä viesti voidaan jättää huomiotta.

<!-- @os:windows -->
> **Huomautus:** Windows ROCm:ssa Unsloth tulostaa käynnistyksen yhteydessä useita varoituksia — katso [Tunnetut varoitukset](#known-warnings) alta. Nämä kaikki voidaan turvallisesti jättää huomiotta; koulutus toimii oikein.
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

## Lataa Unslothin hienosäätöskripti

Sen sijaan, että suorittaisit jokaisen vaiheen manuaalisesti, tämä opaskirja tarjoaa siistin, päästä päähän -skriptin täällä: [test_unsloth.py](assets/test_unsloth.py).

Suorita seuraava koodi skriptin suorittamiseksi:

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

Opaskirjan loppuosa käy käsitteellisesti läpi jokaisen skriptin tärkeän vaiheen.

## Miten se toimii

test_unsloth.py-skripti suorittaa seuraavat vaiheet:
* **Lataa malli**: Lataa unsloth/gemma-4-E4B-it:n FastModel-luokan avulla.
* **Valmistele data**: Standardoi tietojoukon (esim. FineTome-100k) ja soveltaa Gemma-4-keskustelumallinetta.
* **Sovella LoRA**: Lisää sovittimia kieli-, attention- ja MLP-moduuleihin tehokasta koulutusta varten.
* **Koulutus**: Käyttää SFTTraineria vastausten mukaisella häviön maskauksella.
* **Päättely**: Suorittaa nopean generointitestin suorituskyvyn vahvistamiseksi.
* **Tallennus**: Vie LoRA-sovittimet paikallisesti.
## Keskeiset asetukset

Voit muokata seuraavia vakioita mukauttaaksesi ajoasi:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Esimerkki Unslothin tervetuloviestistä ja tulosteesta mallin painojen latauksen yhteydessä:

![alt text](assets/welcome.png)

## Valmistele datasetti

Käytämme osajoukkoa seuraavasta:
```text
mlabonne/FineTome-100k
```
Datasetti:
* Muunnetaan chat-muotoon
* Käsitellään Gemma-4-chat-mallipohjalla
* Puhdistetaan päällekkäisten BOS-tokenien poistamiseksi

## Kouluta malli

Skripti suorittaa lyhyen koulutusdemon seuraavilla parametreilla:
- noin 50 askelta
- pieni eräkoko (batch size)
- gradienttien kertyminen (gradient accumulation)

Koulutuksen aikana näet lokeja, kuten:

![alt text](assets/training.png)


## Tallennus ja käyttöönotto

### Paikallinen tallennus (LoRA)

Skripti tallentaa LoRA-adapterit automaattisesti kansioon OUTPUT_DIR.
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
> **Huomio:** vLLM ei tue Windowsia. Jos haluat ottaa hienosäädetyn mallisi käyttöön Windowsissa, käytä llama.cpp:tä (katso [Vie GGUF-muotoon](#export-gguf-for-llamacpp) alla) tai siirrä yhdistetty malli Linux-koneelle, jossa vLLM on käytössä.
<!-- @os:end -->

<!-- @os:linux -->
Käyttöönottoa varten vLLM:n kanssa, yhdistä adapterit täydeksi malliksi:
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
| `bitsandbytes library load error` | bitsandbytesilla ei ole Windows ROCm -versiota | Kyllä — tämä ohje käyttää `adamw_torch`-optimointia, ei bnb:tä |
| `No ROCm platform found for torch.distributed` | Windowsin ROCm-toteutuksesta puuttuu hajautetun koulutuksen tuki | Kyllä — tämä ei vaikuta yhden GPU:n koulutukseen |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth merkitsee muut kuin Linux-ympäristöt | Kyllä — Windows ROCm toimii yhden GPU:n SFT-koulutuksessa |
| `triton is not available` | Tritonilla ei ole Windows-versiota | Kyllä — Unsloth käyttää PyTorch-ytimiä varmuuden vuoksi |

Koulutus etenee oikein näistä varoituksista huolimatta.
<!-- @os:end -->

## Seuraavat vaiheet
- Kokeile [Unsloth Studiota](https://unsloth.ai/docs/new/studio), intuitiivista graafista käyttöliittymää Unslothille
- Harjoittele omilla datasetteilläsi
- Kokeile hienosäätöä erilaisilla hyperparametreilla
- Ota käyttöön vLLM:n tai llama.cpp:n avulla
- Kokeile QLoRA:a vähemmän muistia vaativaa ratkaisua varten

## Resurssit

Alla on lisäresursseja Unslothista ja hienosäädöstä oppimiseen:

* [Unslothin dokumentaatio](https://docs.unsloth.ai)

* [Unslothin GitHub](https://github.com/unslothai/unsloth)

* [Unslothin hienosäätöopas](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)