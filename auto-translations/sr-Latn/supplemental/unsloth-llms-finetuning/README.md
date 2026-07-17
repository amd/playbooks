<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Pregled

Ovaj playbook pokazuje kako da fino podesite jezički model lokalno pomoću Unsloth na AMD hardveru.

Koristi kratak primer Supervised Fine-Tuning (SFT) sa LoRA adapterima na `unsloth/gemma-4-E4B-it`, koristeći podskup skupa podataka `mlabonne/FineTome-100k`. Cilj je da vam pruži jednostavan end-to-end radni tok koji pokriva podešavanje, obuku, inferenciju i čuvanje fino podešenog rezultata.

Primer je dizajniran da bude praktičan i lak za modifikovanje, tako da ga možete koristiti kao polaznu tačku za sopstvene skupove podataka i modele.

## Šta ćete naučiti

- Kako da podesite Unsloth okruženje
- Kako da fino podesite LLM koristeći SFT sa Unsloth
- Kako da sačuvate fino podešeni rezultat u lokalnom skladištu

<!-- @device:halo,stx,krk -->
> **Napomena:** Tehnike finog podešavanja u ovom playbooку zahtevaju najmanje 24 GB GPU memorije i 32 GB sistemske RAM memorije.
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Napomena:** Tehnike finog podešavanja u ovom playbooку zahtevaju najmanje 24 GB GPU memorije i 32 GB sistemske RAM memorije.
<!-- @os:end -->

<!-- @os:linux -->
> **Napomena:** Tehnike finog podešavanja u ovom playbooку zahtevaju najmanje 24 GB **namenske** GPU memorije i 32 GB sistemske RAM memorije.
<!-- @os:end -->
<!-- @device:end -->

## Zašto Unsloth?

Unsloth olakšava fino podešavanje LLM-a na lokalnom hardveru smanjujući upotrebu memorije i ubrzavajući obuku u poređenju sa standardnim podešavanjem.

U ovom playbooку koristimo Unsloth zajedno sa **SFT zasnovanim na LoRA**. To znači da osnovi model ostaje uglavnom zamrznut, dok se trenira znatno manji skup težina adaptera. Ovo je dobro rešenje za lokalni razvoj jer je lakše od potpunog finog podešavanja i brže za iteracije.

Unsloth takođe podržava druge pristupe obuke, uključujući QLoRA i tokove rada zasnovane na reinforcement learningu. Ovaj playbook se fokusira na najjednostavniji put: mali primer LoRA finog podešavanja koji korisnici mogu pokrenuti, razumeti i proširiti.

## Podešavanje konfiguracije memorije

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Proverite softverska ažuriranja
> **Napomena**: Ako VS Code nije instaliran, možete ga instalirati putem Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalacija softverskih preduslova

### Kreiranje virtuelnog okruženja

<!-- @os:linux -->
<!-- @device:halo_box -->
Otvorite terminal i kreirajte venv sa AMD ROCm™ softverom i PyTorch već instaliranim:
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
**Dodelite svom korisniku pristup GPU uređajima** (odjavite se i ponovo prijavite da bi ovo stupilo na snagu):

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
> **Napomena:** Python 3.13 je neophodan za Windows.

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

### Instalacija osnovnih zavisnosti
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

> **Napomena:** Tokom uvoza, Unsloth može da ispituje opcione `bitsandbytes` putanje ubrzanja. Na nekim ROCm verzijama, možete videti poruku poput `bitsandbytes library load error: Configured ROCm binary not found`. Ovaj playbook koristi standardno LoRA fino podešavanje sa `optim="adamw_torch"`, tako da ne oslanjamo se na `bitsandbytes` optimizer ili 4-bitni QLoRA. Ova poruka se može bezbedno ignorisati.

<!-- @os:windows -->
> **Napomena:** Na Windows ROCm, Unsloth će ispisati nekoliko upozorenja pri pokretanju — pogledajte [Poznata upozorenja](#known-warnings) ispod. Sva su bezbedna za ignorisanje; obuka radi ispravno.
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

## Preuzimanje Unsloth skripta za fino podešavanje

Umesto ručnog izvršavanja svakog koraka, ovaj playbook pruža čist, end-to-end skript ovde: [test_unsloth.py](assets/test_unsloth.py).

Pokrenite sledeći kod da biste izvršili skript:

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

Ostatak playbooка će konceptualno proći kroz svaki glavni korak skripta.

## Kako funkcioniše

Skript test_unsloth.py izvodi sledeće korake:
* **Učitavanje modela**: Učitava unsloth/gemma-4-E4B-it koristeći FastModel.
* **Priprema podataka**: Standardizuje skup podataka (npr. FineTome-100k) i primenjuje Gemma-4 šablon za ćaskanje.
* **Primena LoRA**: Dodaje adaptere na jezičke, attention i MLP module za efikasnu obuku.
* **Obuka**: Koristi SFTTrainer sa maskiranjem gubitka samo za odgovore.
* **Inferencija**: Pokreće brzi test generisanja radi provere performansi.
* **Čuvanje**: Eksportuje LoRA adaptere lokalno.

## Ključna konfiguracija

Možete izmeniti sledeće konstante da biste prilagodili svoje pokretanje:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Primer Unsloth poruke dobrodošlice i izlaza pri učitavanju težina modela:

![alt text](assets/welcome.png)

## Priprema skupa podataka

Koristimo podskup od:
```text
mlabonne/FineTome-100k
```
Skup podataka je:
* Konvertovan u format ćaskanja
* Obrađen korišćenjem Gemma-4 šablona za ćaskanje
* Očišćen radi uklanjanja duplih BOS tokena

## Obuka modela

Skript pokreće kratku demonstraciju obuke sa sledećim parametrima:
- ~50 koraka
- Mala veličina serije
- Akumulacija gradijenata

Tokom obuke, videćete zapise poput:

![alt text](assets/training.png)


## Čuvanje i primena

### Lokalno čuvanje (LoRA)

Skript automatski čuva LoRA adaptere u OUTPUT_DIR.
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
> **Napomena:** vLLM ne podržava Windows. Da biste primenili fino podešeni model na Windows-u, koristite llama.cpp (pogledajte [Eksport GGUF](#export-gguf-for-llamacpp) ispod) ili prenesite spojeni model na Linux mašinu koja pokreće vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Za primenu sa vLLM, spojite adaptere u puni model:
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

### Eksport GGUF (za llama.cpp)

Konvertujte direktno u GGUF za lokalnu inferenciju:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Poznata upozorenja

Ova upozorenja ispisuje Unsloth pri pokretanju na Windows ROCm i sva su bezbedna za ignorisanje:

| Upozorenje | Razlog | Bezbedno za ignorisanje? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes nema Windows ROCm build | Da — ovaj playbook koristi `adamw_torch`, ne bnb |
| `No ROCm platform found for torch.distributed` | ROCm-on-Windows nema distribuiranu obuku | Da — obuka na jednom GPU-u nije pogođena |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth označava non-Linux buildove | Da — Windows ROCm radi za SFT na jednom GPU-u |
| `triton is not available` | Triton nema Windows build | Da — Unsloth prelazi na PyTorch kernele |

Obuka će se odvijati ispravno uprkos ovim upozorenjima.
<!-- @os:end -->

## Sledeći koraci
- Isprobajte [Unsloth Studio](https://unsloth.ai/docs/new/studio), intuitivan GUI za Unsloth
- Trenirajte na sopstvenim specifičnim skupovima podataka
- Isprobajte fino podešavanje sa različitim hiperparametrima
- Primenite sa vLLM ili llama.cpp
- Isprobajte QLoRA za podešavanje sa manjom memorijom

## Resursi

Ispod su neki dodatni resursi za učenje više o Unsloth i finetuning-u:

* [Unsloth dokumentacija](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Unsloth vodič za fino podešavanje](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)