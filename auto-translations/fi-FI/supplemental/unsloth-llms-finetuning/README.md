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

Tässä ohjekirjassa näytetään, miten kielimallia hienosäädetään paikallisesti Unslothilla AMD-laitteistolla.

Siinä käytetään lyhyttä ohjatun hienosäädön (Supervised Fine-Tuning, SFT) esimerkkiä LoRA-sovittimien avulla mallissa `unsloth/gemma-4-E4B-it` käyttäen osajoukkoa `mlabonne/FineTome-100k`-datajoukosta. Tavoitteena on tarjota yksinkertainen, päästä päähän etenevä työnkulku, joka kattaa asennuksen, koulutuksen, päättelyn ja hienosäädetyn tuloksen tallentamisen.

Esimerkki on suunniteltu käytännölliseksi ja helposti muokattavaksi, joten voit käyttää sitä lähtökohtana omille datajoukoillesi ja malleillesi.

## Mitä opit

- Miten Unsloth-ympäristö otetaan käyttöön
- Miten LLM-mallia hienosäädetään SFT:llä Unslothin avulla
- Miten hienosäädetty tulos tallennetaan paikalliseen tallennustilaan

<!-- @device:halo,stx,krk -->
> **Huomautus:** Tässä ohjekirjassa esitetyt hienosäätötekniikat vaativat vähintään **64 Gt järjestelmämuistia**, josta vähintään **24 Gt on oltava GPU:n käytettävissä** (24 Gt on osa 64 Gt:sta, ei sen lisäksi).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Huomautus:** Tässä ohjekirjassa esitetyt hienosäätötekniikat vaativat vähintään **24 Gt GPU-muistia yhteensä** ja **32 Gt järjestelmämuistia**.
> - Windowsissa GPU:n kokonaismuisti muodostuu näytönohjaimen omistetusta VRAM-muistista ja jaetusta GPU-muistista (lainattu järjestelmämuistista).
> - Tämän ansiosta myös näytönohjaimet, joissa on alle 24 Gt omistettua VRAM-muistia, voivat ajaa tätä ohjekirjaa käyttämällä jaettua GPU-muistia erotuksen kattamiseen.
<!-- @os:end -->

<!-- @os:linux -->
> **Huomautus:** Tässä ohjekirjassa esitetyt hienosäätötekniikat vaativat näytönohjaimen, jossa on vähintään **24 Gt omistettua GPU-muistia**, sekä **32 Gt järjestelmämuistia**.
> - Linuxissa koulutus tapahtuu kokonaan näytönohjaimen omistetussa VRAM-muistissa.
> - Se ei siirry käyttämään jaettua GPU-muistia (järjestelmämuistia), kun VRAM-muisti loppuu kesken.
> - Näytönohjaimet, joissa on alle 24 Gt omistettua VRAM-muistia, jäävät ilman muistia koulutuksen aikana Linuxissa, vaikka järjestelmässä olisi runsaasti RAM-muistia.
<!-- @os:end -->
<!-- @device:end -->

## Miksi Unsloth?

Unsloth helpottaa LLM-mallien hienosäätöä paikallisella laitteistolla vähentämällä muistinkäyttöä ja nopeuttamalla koulutusta verrattuna tavanomaiseen asetukseen.

Tässä ohjekirjassa käytämme Unslothia yhdessä **LoRA-pohjaisen SFT:n** kanssa. Tämä tarkoittaa, että perusmalli pysyy suurelta osin jäädytettynä, kun taas huomattavasti pienempi joukko sovitinpainoja koulutetaan. Tämä sopii hyvin paikalliseen kehitystyöhön, koska se on kevyempi kuin täysi hienosäätö ja nopeampi iteroida.

Unsloth tukee myös muita koulutusmenetelmiä, mukaan lukien QLoRA ja vahvistusoppimisen työnkulkuja. Tämä ohjekirja keskittyy ensin yksinkertaisimpaan polkuun: pieneen LoRA-hienosäätöesimerkkiin, jota käyttäjät voivat ajaa, ymmärtää ja laajentaa.

## Muistiasetuksen määrittäminen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Tarkista ohjelmistopäivitykset
> **Huomautus**: Jos VS Code ei ole asennettuna, voit asentaa sen Ryzen AI Developer Centerin kautta.

<!-- @require:software-update -->
<!-- @device:end -->

## Ohjelmiston esivaatimusten asentaminen

### Luo virtuaaliympäristö

<!-- @os:linux -->
<!-- @device:halo_box -->
Avaa pääte ja luo venv, johon on jo asennettu AMD ROCm™ -ohjelmisto ja PyTorch:
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
**Myönnä käyttäjällesi pääsy GPU-laitteisiin** (kirjaudu ulos ja takaisin sisään, jotta muutos astuu voimaan):

```bash
sudo usermod -aG render,video $LOGNAME
```

Avaa pääte ja luo venv:
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
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```bash
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=600 setup=activate-venv -->
```powershell
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git"
pip install triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Huomautus:** Tuonnin aikana Unsloth saattaa testata valinnaisia `bitsandbytes`-kiihdytyspolkuja. Joissakin ROCm-versioissa saatat nähdä viestin, kuten `bitsandbytes library load error: Configured ROCm binary not found`. Tämä ohjekirja käyttää tavanomaista LoRA-hienosäätöä asetuksella `optim="adamw_torch"`, joten emme käytä `bitsandbytes`-optimointia tai 4-bittistä QLoRA:ta. Tämän viestin voi jättää huomiotta.

<!-- @os:windows -->
> **Huomautus:** Windows ROCm -ympäristössä Unsloth tulostaa käynnistyksen yhteydessä useita varoituksia — katso [Known Warnings](#known-warnings) alta. Nämä kaikki voi turvallisesti jättää huomiotta; koulutus toimii oikein.
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

Sen sijaan, että suorittaisit jokaisen vaiheen manuaalisesti, tämä ohjekirja tarjoaa siistin, päästä päähän etenevän skriptin täältä: [test_unsloth.py](assets/test_unsloth.py).

Suorita seuraava koodi ajaaksesi skriptin:

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

Loppuosa ohjekirjasta käy käsitteellisesti läpi skriptin jokaisen pääasteen.

## Miten se toimii

test_unsloth.py-skripti suorittaa seuraavat vaiheet:
* **Lataa malli**: Lataa mallin unsloth/gemma-4-E4B-it käyttäen FastModel-luokkaa.
* **Valmistele data**: Standardoi datajoukon (esim. FineTome-100k) ja soveltaa Gemma-4-keskustelumallipohjaa.
* **Sovella LoRA:a**: Lisää sovittimia kieli-, huomio- ja MLP-moduuleihin tehokasta koulutusta varten.
* **Kouluta**: Käyttää SFTTraineria vastausperusteisella häviön maskauksella.
* **Päättely**: Suorittaa nopean generointitestin suorituskyvyn tarkistamiseksi.
* **Tallenna**: Vie LoRA-sovittimet paikallisesti.

## Keskeinen konfiguraatio

Voit muokata seuraavia vakioita mukauttaaksesi ajoasi:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Esimerkki Unslothin tervetuloviestistä ja tulosteesta mallin painojen lataamisen yhteydessä:

![alt text](assets/welcome.png)

## Valmistele datajoukko

Käytämme osajoukkoa:
```text
mlabonne/FineTome-100k
```
Datajoukko:
* Muunnetaan keskustelumuotoon
* Käsitellään Gemma-4-keskustelumallipohjalla
* Puhdistetaan päällekkäisten BOS-tokenien poistamiseksi

## Kouluta malli

Skripti suorittaa lyhyen koulutusdemon seuraavilla parametreilla:
- ~50 askelta
- Pieni eräkoko
- Gradienttien kumulointi

Koulutuksen aikana näet lokitietoja, kuten:

![alt text](assets/training.png)


## Tallennus ja käyttöönotto
### Paikallinen tallennus (LoRA)

Skripti tallentaa LoRA-sovittimet automaattisesti kansioon OUTPUT_DIR.
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
> **Huomautus:** vLLM ei tue Windowsia. Jos haluat ottaa hienosäädetyn mallisi käyttöön Windowsissa, käytä llama.cpp:tä (katso [Export GGUF](#export-gguf-for-llamacpp) alla) tai siirrä yhdistetty malli Linux-koneelle, jossa vLLM on käynnissä.
<!-- @os:end -->

<!-- @os:linux -->
Kun otat mallin käyttöön vLLM:llä, yhdistä sovittimet koko malliin:
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

### GGUF:n vieminen (llama.cpp:tä varten)

Muunna suoraan GGUF-muotoon paikallista päättelyä varten:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Tunnetut varoitukset

Unsloth tulostaa nämä varoitukset käynnistyksen yhteydessä Windows ROCm -ympäristössä, ja ne kaikki voi turvallisesti jättää huomiotta:

| Varoitus | Syy | Voiko jättää huomiotta? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes-kirjastolle ei ole Windows ROCm -käännöstä | Kyllä — tämä ohje käyttää `adamw_torch`-toteutusta, ei bnb:tä |
| `No ROCm platform found for torch.distributed` | ROCm Windowsilla ei tue hajautettua koulutusta | Kyllä — yhden GPU:n koulutus ei kärsi tästä |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth merkitsee muut kuin Linux-käännökset | Kyllä — Windows ROCm toimii yhden GPU:n SFT-koulutuksessa |
| `triton is not available` | Tritonille ei ole Windows-käännöstä | Kyllä — Unsloth käyttää sen sijaan PyTorch-ytimiä |

Koulutus etenee oikein näistä varoituksista huolimatta.
<!-- @os:end -->

## Seuraavat vaiheet
- Kokeile [Unsloth Studiota](https://unsloth.ai/docs/new/studio), intuitiivista graafista käyttöliittymää Unslothille
- Kouluta omilla erikoistuneilla datajoukoillasi
- Kokeile hienosäätöä eri hyperparametreilla
- Ota käyttöön vLLM:llä tai llama.cpp:llä
- Kokeile QLoRA:a pienemmän muistinkäytön ratkaisuksi

## Resurssit

Alla on lisäresursseja, joiden avulla voit oppia lisää Unslothista ja hienosäädöstä:

* [Unslothin dokumentaatio](https://docs.unsloth.ai)

* [Unslothin GitHub](https://github.com/unslothai/unsloth)

* [Unslothin hienosäätöopas](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)