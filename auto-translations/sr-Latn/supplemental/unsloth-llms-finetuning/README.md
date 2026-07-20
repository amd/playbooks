<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ovaj priručnik koristi posebne oznake koje GitHub ne može da prikaže. Posetite [amd.com/playbooks](https://amd.com/playbooks) da biste ispravno pregledali ovaj sadržaj.
<!-- @github-only:end -->

## Pregled

Ovaj priručnik prikazuje kako da lokalno fino podesite jezički model pomoću Unsloth na AMD hardveru.

Koristi kratak primer nadgledanog fino podešavanja (SFT) sa LoRA adapterima na `unsloth/gemma-4-E4B-it`, koristeći podskup skupa podataka `mlabonne/FineTome-100k`. Cilj je da vam pruži jednostavan sveobuhvatan tok rada koji obuhvata podešavanje, treniranje, zaključivanje i čuvanje fino podešenog rezultata.

Primer je osmišljen da bude praktičan i lak za izmenu, tako da ga možete koristiti kao polaznu tačku za sopstvene skupove podataka i modele.

## Šta ćete naučiti

- Kako da podesite Unsloth okruženje
- Kako da fino podesite LLM koristeći SFT sa Unsloth
- Kako da sačuvate fino podešeni rezultat u lokalnom skladištu

<!-- @device:halo,stx,krk -->
> **Napomena:** Tehnike fino podešavanja u ovom priručniku zahtevaju najmanje 24 GB GPU memorije i 32 GB sistemske RAM memorije.
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Napomena:** Tehnike fino podešavanja u ovom priručniku zahtevaju najmanje 24 GB GPU memorije i 32 GB sistemske RAM memorije.
<!-- @os:end -->

<!-- @os:linux -->
> **Napomena:** Tehnike fino podešavanja u ovom priručniku zahtevaju najmanje 24 GB **namenske** GPU memorije i 32 GB sistemske RAM memorije.
<!-- @os:end -->
<!-- @device:end -->

## Zašto Unsloth?

Unsloth olakšava fino podešavanje LLM-a na lokalnom hardveru smanjujući potrošnju memorije i ubrzavajući treniranje u poređenju sa standardnim podešavanjem.

U ovom priručniku koristimo Unsloth zajedno sa **SFT-om zasnovanim na LoRA**. To znači da osnovni model ostaje uglavnom zamrznut, dok se trenira mnogo manji skup težina adaptera. Ovo je dobar izbor za lokalni razvoj jer je lakše od potpunog fino podešavanja i brže za iteracije.

Unsloth takođe podržava i druge pristupe treniranju, uključujući QLoRA i tokove rada zasnovane na učenju uz pojačanje. Ovaj priručnik se prvo fokusira na najjednostavniji put: mali primer LoRA fino podešavanja koji korisnici mogu da pokrenu, razumeju i prošire.

## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Provera ažuriranja softvera
> **Napomena**: Ako VS Code nije instaliran, možete ga instalirati putem Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instaliranje potrebnog softvera

### Kreiranje virtuelnog okruženja

<!-- @os:linux -->
<!-- @device:halo_box -->
Otvorite terminal i kreirajte venv sa već instaliranim AMD ROCm™ softverom i PyTorch:
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
**Dodelite korisniku pristup GPU uređajima** (odjavite se i ponovo prijavite da bi ovo stupilo na snagu):

```bash
sudo usermod -aG render,video $LOGNAME
```

Otvorite terminal i kreirajte venv:
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
> **Napomena:** Python 3.13 je obavezan za Windows.

<!-- @device:halo_box -->
Otvorite PowerShell terminal i kreirajte virtuelno okruženje:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Otvorite PowerShell terminal i kreirajte virtuelno okruženje:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Instaliranje osnovnih zavisnosti
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

### Dodatne zavisnosti

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

> **Napomena:** Tokom uvoza, Unsloth može da proverava opcione puteve za `bitsandbytes` ubrzanje. Na nekim verzijama ROCm-a, možete videti poruku poput `bitsandbytes library load error: Configured ROCm binary not found`. Ovaj priručnik koristi standardno LoRA fino podešavanje sa `optim="adamw_torch"`, tako da se ne oslanjamo na `bitsandbytes` optimizator ili 4-bitni QLoRA. Ova poruka se može bezbedno zanemariti.

<!-- @os:windows -->
> **Napomena:** Na Windows ROCm-u, Unsloth će ispisati nekoliko upozorenja prilikom pokretanja — pogledajte [Poznata upozorenja](#known-warnings) ispod. Sva su bezbedna za zanemarivanje; treniranje ispravno funkcioniše.
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

## Preuzmite Unsloth skriptu za fino podešavanje

Umesto ručnog izvršavanja svakog koraka, ovaj priručnik pruža čistu, sveobuhvatnu skriptu ovde: [test_unsloth.py](assets/test_unsloth.py).

Pokrenite sledeći kod da biste izvršili skriptu:

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

Ostatak priručnika će konceptualno proći kroz svaki glavni korak skripte. 

## Kako to funkcioniše

Skripta test_unsloth.py izvršava sledeće korake:
* **Učitavanje modela**: Učitava unsloth/gemma-4-E4B-it koristeći FastModel.
* **Priprema podataka**: Standardizuje skup podataka (npr. FineTome-100k) i primenjuje Gemma-4 chat šablon.
* **Primena LoRA**: Dodaje adaptere na jezičke, pažnje (attention) i MLP module radi efikasnog treniranja.
* **Treniranje**: Koristi SFTTrainer sa maskiranjem gubitka samo za odgovore.
* **Zaključivanje**: Pokreće brzi test generisanja radi provere performansi.
* **Čuvanje**: Izvozi LoRA adaptere lokalno.

## Ključna konfiguracija

Možete izmeniti sledeće konstante da biste prilagodili svoje pokretanje:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Primer Unsloth poruke dobrodošlice i izlaza prilikom učitavanja težina modela:

![alt text](assets/welcome.png)

## Priprema skupa podataka

Koristimo podskup: 
```text
mlabonne/FineTome-100k
```
Skup podataka je: 
* Konvertovan u format ćaskanja
* Obrađen korišćenjem Gemma-4 chat šablona
* Očišćen radi uklanjanja duplikata BOS tokena

## Treniranje modela

Skripta pokreće kratku demonstraciju treniranja, sa sledećim parametrima:
- ~50 koraka
- Mala veličina serije (batch)
- Akumulacija gradijenta

Tokom treniranja, videćete zapisnike poput:

![alt text](assets/training.png)


## Čuvanje i implementacija

### Lokalno čuvanje (LoRA)

Skripta automatski čuva LoRA adaptere u OUTPUT_DIR.
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

### Čuvanje spojenog modela (za vLLM) 

<!-- @os:windows -->
> **Napomena:** vLLM ne podržava Windows. Da biste implementirali svoj fino podešeni model na Windows-u, koristite llama.cpp (pogledajte [Izvoz GGUF](#export-gguf-for-llamacpp) ispod) ili prenesite spojeni model na Linux mašinu koja pokreće vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Za implementaciju sa vLLM, spojite adaptere u potpuni model:
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

### Izvoz GGUF (za llama.cpp)

Konvertujte direktno u GGUF za lokalno zaključivanje:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Poznata upozorenja

Ova upozorenja ispisuje Unsloth prilikom pokretanja na Windows ROCm sistemu i sva su bezbedna za ignorisanje:

| Upozorenje | Razlog | Bezbedno za ignorisanje? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes nema Windows ROCm verziju | Da — ovaj vodič koristi `adamw_torch`, a ne bnb |
| `No ROCm platform found for torch.distributed` | ROCm na Windows-u ne podržava distribuirano treniranje | Da — treniranje na jednom GPU-u nije pogođeno |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth označava platforme koje nisu Linux | Da — Windows ROCm radi za SFT treniranje na jednom GPU-u |
| `triton is not available` | Triton nema Windows verziju | Da — Unsloth se vraća na PyTorch kernele |

Treniranje će se ispravno nastaviti uprkos ovim upozorenjima.
<!-- @os:end -->

## Sledeći koraci
- Isprobajte [Unsloth Studio](https://unsloth.ai/docs/new/studio), intuitivan grafički interfejs za Unsloth
- Trenirajte na sopstvenim, specifičnim skupovima podataka
- Isprobajte fino podešavanje sa različitim hiperparametrima
- Postavite model uz pomoć vLLM ili llama.cpp
- Isprobajte QLoRA za postavku sa manjom potrošnjom memorije

## Resursi

Ispod se nalaze dodatni resursi za dalje upoznavanje sa Unsloth-om i fino podešavanjem:

* [Unsloth dokumentacija](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth vodič za fino podešavanje](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)