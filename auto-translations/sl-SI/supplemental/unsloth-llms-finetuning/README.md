<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojni prevod.** Ta stran je bila samodejno prevedena iz angleščine in je ni pregledal človek. Lahko vsebuje napake, določena navodila, ukazi, prenosi, razpoložljivost izdelkov ali druga vsebina pa se lahko razlikujejo glede na jezik ali regijo. V primeru kakršnega koli neskladja ali razhajanja je merodajna in prevladujoča izvirna angleška različica playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Pregled

Ta priročnik prikazuje, kako lokalno fino nastaviti jezikovni model z orodjem Unsloth na strojni opremi AMD.

Uporablja kratek primer nadzorovanega fino nastavljanja (SFT) z adapterji LoRA na modelu `unsloth/gemma-4-E4B-it`, pri čemer se uporablja podmnožica podatkovne zbirke `mlabonne/FineTome-100k`. Cilj je predstaviti enostaven, celovit potek dela, ki zajema nastavitev, učenje, sklepanje in shranjevanje fino nastavljenega rezultata.

Primer je zasnovan tako, da je praktičen in ga je enostavno prilagoditi, zato ga lahko uporabite kot izhodišče za lastne podatkovne zbirke in modele.

## Kaj se boste naučili

- Kako nastaviti okolje Unsloth
- Kako fino nastaviti LLM z uporabo SFT z orodjem Unsloth
- Kako shraniti fino nastavljen rezultat v lokalno shrambo

<!-- @device:halo,stx,krk -->
> **Opomba:** Tehnike fino nastavljanja v tem priročniku zahtevajo vsaj **64 GB sistemskega RAM-a**, od tega mora biti vsaj **24 GB na voljo GPE-ju** (24 GB je del 64 GB, ne dodatek k njim).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Opomba:** Tehnike fino nastavljanja v tem priročniku zahtevajo vsaj **24 GB skupnega pomnilnika GPE** in **32 GB sistemskega RAM-a**.
> - V sistemu Windows skupni pomnilnik GPE združuje namenski VRAM grafične kartice s skupno rabo pomnilnika GPE (izposojenega iz sistemskega RAM-a).
> - Zato lahko kartice z manj kot 24 GB namenskega VRAM-a še vedno poganjajo ta priročnik z uporabo skupne rabe pomnilnika GPE za nadomestitev razlike.
<!-- @os:end -->

<!-- @os:linux -->
> **Opomba:** Tehnike fino nastavljanja v tem priročniku zahtevajo grafično kartico z vsaj **24 GB namenskega pomnilnika GPE** in **32 GB sistemskega RAM-a**.
> - V sistemu Linux se učenje v celoti izvaja v namenskem VRAM-u grafične kartice.
> - Ko VRAM zmanjka, sistem ne preklopi na skupno rabo pomnilnika GPE (sistemski RAM).
> - Kartice z manj kot 24 GB namenskega VRAM-a bodo med učenjem v sistemu Linux zmanjkale pomnilnika, tudi če ima sistem veliko RAM-a.
<!-- @os:end -->
<!-- @device:end -->

## Zakaj Unsloth?

Unsloth olajša izvajanje fino nastavljanja LLM na lokalni strojni opremi z zmanjšanjem porabe pomnilnika in pospešitvijo učenja v primerjavi s standardno nastavitvijo.

V tem priročniku uporabljamo Unsloth skupaj s **SFT, ki temelji na LoRA**. To pomeni, da osnovni model ostane večinoma zamrznjen, medtem ko se uči veliko manjši nabor uteži adapterjev. To je dobra izbira za lokalni razvoj, saj je lažje od popolnega fino nastavljanja in hitrejše za ponavljajoče se izboljšave.

Unsloth podpira tudi druge pristope učenja, vključno s QLoRA in poteki dela okrepljenega učenja. Ta priročnik se najprej osredotoča na najpreprostejšo pot: majhen primer fino nastavljanja LoRA, ki ga lahko uporabniki zaženejo, razumejo in razširijo.

## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme
> **Opomba**: Če VS Code ni nameščen, ga lahko namestite z Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Namestitev predpogojev programske opreme

### Ustvarjanje virtualnega okolja

<!-- @os:linux -->
<!-- @device:halo_box -->
Odprite terminal in ustvarite venv z že nameščeno programsko opremo AMD ROCm™ in PyTorch:
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
**Uporabniku odobrite dostop do naprav GPE** (za uveljavitev te spremembe se odjavite in ponovno prijavite):

```bash
sudo usermod -aG render,video $LOGNAME
```

Odprite terminal in ustvarite venv:
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
> **Opomba:** Za Windows je potreben Python 3.13.

<!-- @device:halo_box -->
Odprite terminal PowerShell in ustvarite virtualno okolje:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Odprite terminal PowerShell in ustvarite virtualno okolje:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Namestitev osnovnih odvisnosti
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

### Dodatne odvisnosti

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

> **Opomba:** Med uvozom lahko Unsloth preveri neobvezne pospeševalne poti `bitsandbytes`. Pri nekaterih različicah ROCm boste morda videli sporočilo, kot je `bitsandbytes library load error: Configured ROCm binary not found`. Ta priročnik uporablja standardno fino nastavljanje LoRA z `optim="adamw_torch"`, zato se ne zanašamo na optimizator `bitsandbytes` ali 4-bitno QLoRA. To sporočilo lahko varno prezrete.

<!-- @os:windows -->
> **Opomba:** Na sistemu Windows ROCm bo Unsloth ob zagonu izpisal več opozoril – glejte [Znana opozorila](#known-warnings) spodaj. Vsa jih je varno prezreti; učenje deluje pravilno.
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

## Prenos skripte za fino nastavljanje Unsloth

Namesto ročnega izvajanja vsakega koraka ta priročnik ponuja pregledno, celovito skripto tukaj: [test_unsloth.py](assets/test_unsloth.py).

Za izvedbo skripte zaženite naslednjo kodo:

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

Preostanek priročnika bo konceptualno obravnaval vsak glavni korak skripte. 

## Kako deluje

Skripta test_unsloth.py izvede naslednje korake:
* **Nalaganje modela**: Naloži unsloth/gemma-4-E4B-it z uporabo FastModel.
* **Priprava podatkov**: Standardizira podatkovno zbirko (npr. FineTome-100k) in uporabi predlogo klepeta Gemma-4.
* **Uporaba LoRA**: Doda adapterje modulom za jezik, pozornost in MLP za učinkovito učenje.
* **Učenje**: Uporablja SFTTrainer z maskiranjem izgube samo za odgovore.
* **Sklepanje**: Zažene hiter preizkus generiranja za preverjanje zmogljivosti.
* **Shranjevanje**: Izvozi adapterje LoRA lokalno.

## Ključna konfiguracija

Naslednje konstante lahko spremenite za prilagoditev svojega zagona:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Primer pozdravnega sporočila Unsloth in izpisa med nalaganjem uteži modela:

![alt text](assets/welcome.png)

## Priprava podatkovne zbirke

Uporabljamo podmnožico:
```text
mlabonne/FineTome-100k
```
Podatkovna zbirka je: 
* Pretvorjena v obliko klepeta
* Obdelana z uporabo predloge klepeta Gemma-4
* Očiščena podvojenih žetonov BOS

## Učenje modela

Skripta zažene kratko predstavitev učenja z naslednjimi parametri:
- ~50 korakov
- Majhna velikost paketa (batch size)
- Kopičenje gradientov

Med učenjem boste videli dnevnike, kot so:

![alt text](assets/training.png)


## Shranjevanje in uvajanje
### Lokalno shranjevanje (LoRA)

Skripta samodejno shrani adapterje LoRA v OUTPUT_DIR.
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

### Shranjevanje združenega modela (za vLLM) 

<!-- @os:windows -->
> **Opomba:** vLLM ne podpira sistema Windows. Za uvajanje vašega natančno prilagojenega modela v sistemu Windows uporabite llama.cpp (glejte [Izvoz GGUF](#export-gguf-for-llamacpp) spodaj) ali prenesite združeni model na napravo Linux, ki poganja vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Za uvajanje z vLLM združite adapterje v celoten model:
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

Neposredno pretvorite v GGUF za lokalno sklepanje:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Znana opozorila

Ta opozorila izpiše Unsloth ob zagonu v sistemu Windows ROCm in jih je vse varno prezreti:

| Opozorilo | Razlog | Ali je varno prezreti? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes nima gradnje za Windows ROCm | Da — ta priročnik uporablja `adamw_torch`, ne bnb |
| `No ROCm platform found for torch.distributed` | ROCm v sistemu Windows ne podpira porazdeljenega učenja | Da — na učenje z eno GPE to ne vpliva |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth označi gradnje, ki niso za Linux | Da — Windows ROCm deluje za SFT z eno GPE |
| `triton is not available` | Triton nima gradnje za Windows | Da — Unsloth se povrne na jedra PyTorch |

Učenje se bo kljub tem opozorilom pravilno nadaljevalo.
<!-- @os:end -->

## Naslednji koraki
- Preizkusite [Unsloth Studio](https://unsloth.ai/docs/new/studio), intuitiven grafični vmesnik za Unsloth
- Učite se na svojih lastnih naborih podatkov
- Preizkusite natančno prilagajanje z različnimi hiperparametri
- Uvedite z vLLM ali llama.cpp
- Preizkusite QLoRA za nastavitev z manjšo porabo pomnilnika

## Viri

Spodaj je nekaj dodatnih virov za nadaljnje spoznavanje Unsloth in natančnega prilagajanja:

* [Dokumentacija Unsloth](https://docs.unsloth.ai)

* [Unsloth na GitHubu](https://github.com/unslothai/unsloth)

* [Vodnik za natančno prilagajanje Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)