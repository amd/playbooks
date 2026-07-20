<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ta priročnik uporablja posebne oznake, ki jih GitHub ne more upodobiti. Za pravilen predogled te vsebine obiščite [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->

## Pregled

Ta priročnik prikazuje, kako lokalno fino nastaviti jezikovni model z orodjem Unsloth na strojni opremi AMD.

Uporablja kratek primer nadzorovanega fino nastavljanja (Supervised Fine-Tuning, SFT) z adapterji LoRA na modelu `unsloth/gemma-4-E4B-it`, z uporabo podmnožice nabora podatkov `mlabonne/FineTome-100k`. Cilj je predstaviti preprost celovit potek dela, ki zajema nastavitev, učenje, sklepanje in shranjevanje fino nastavljenega rezultata.

Primer je zasnovan tako, da je praktičen in ga je enostavno prilagoditi, zato ga lahko uporabite kot izhodišče za lastne nabore podatkov in modele.

## Kaj se boste naučili

- Kako nastaviti okolje Unsloth
- Kako fino nastaviti LLM z uporabo SFT z orodjem Unsloth
- Kako shraniti fino nastavljen rezultat v lokalno shrambo

<!-- @device:halo,stx,krk -->
> **Opomba:** Tehnike fino nastavljanja v tem priročniku zahtevajo vsaj 24 GB pomnilnika GPE in 32 GB sistemskega RAM-a.
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Opomba:** Tehnike fino nastavljanja v tem priročniku zahtevajo vsaj 24 GB pomnilnika GPE in 32 GB sistemskega RAM-a.
<!-- @os:end -->

<!-- @os:linux -->
> **Opomba:** Tehnike fino nastavljanja v tem priročniku zahtevajo vsaj 24 GB **namenskega** pomnilnika GPE in 32 GB sistemskega RAM-a.
<!-- @os:end -->
<!-- @device:end -->

## Zakaj Unsloth?

Unsloth olajša zagon fino nastavljanja LLM na lokalni strojni opremi z zmanjšanjem porabe pomnilnika in pospešitvijo učenja v primerjavi s standardno nastavitvijo.

V tem priročniku uporabljamo Unsloth skupaj s **SFT, temelječim na LoRA**. To pomeni, da osnovni model ostane večinoma zamrznjen, medtem ko se usposablja veliko manjši nabor uteži adapterjev. To je dobra izbira za lokalni razvoj, saj je lažje od popolnega fino nastavljanja in omogoča hitrejše iteracije.

Unsloth podpira tudi druge pristope učenja, vključno s QLoRA in poteki dela za spodbujevalno učenje. Ta priročnik se najprej osredotoča na najpreprostejšo pot: majhen primer fino nastavljanja LoRA, ki ga lahko uporabniki zaženejo, razumejo in nadgradijo.

## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme
> **Opomba**: Če VS Code ni nameščen, ga lahko namestite z orodjem Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Namestitev zahtevane programske opreme

### Ustvarite virtualno okolje

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
**Uporabniku dodelite dostop do naprav GPE** (za uveljavitev se odjavite in ponovno prijavite):

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

> **Opomba:** Med uvozom lahko Unsloth preveri neobvezne poti pospeševanja `bitsandbytes`. Pri nekaterih različicah ROCm se lahko prikaže sporočilo, kot je `bitsandbytes library load error: Configured ROCm binary not found`. Ta priročnik uporablja standardno fino nastavljanje LoRA z `optim="adamw_torch"`, zato se ne zanašamo na optimizator `bitsandbytes` ali 4-bitni QLoRA. To sporočilo lahko varno prezrete.

<!-- @os:windows -->
> **Opomba:** Na sistemu Windows ROCm bo Unsloth ob zagonu izpisal več opozoril – glejte razdelek [Znana opozorila](#known-warnings) spodaj. Vsa jih je varno prezreti; učenje deluje pravilno.
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

## Prenesite skripto za fino nastavljanje Unsloth

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

Preostanek priročnika bo konceptualno šel skozi vsak glavni korak skripte.

## Kako deluje

Skripta test_unsloth.py izvede naslednje korake:
* **Nalaganje modela**: Naloži unsloth/gemma-4-E4B-it z uporabo FastModel.
* **Priprava podatkov**: Standardizira nabor podatkov (npr. FineTome-100k) in uporabi predlogo klepeta Gemma-4.
* **Uporaba LoRA**: Doda adapterje modulom jezika, pozornosti in MLP za učinkovito učenje.
* **Učenje**: Uporabi SFTTrainer z maskiranjem izgube samo za odgovore.
* **Sklepanje**: Izvede hiter test generiranja za preverjanje delovanja.
* **Shranjevanje**: Izvozi adapterje LoRA lokalno.

## Ključna konfiguracija

Naslednje konstante lahko spremenite za prilagoditev svojega zagona:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Primer pozdravnega sporočila Unsloth in izpisa pri nalaganju uteži modela:

![besedilo alt](assets/welcome.png)

## Priprava nabora podatkov

Uporabljamo podmnožico:
```text
mlabonne/FineTome-100k
```
Nabor podatkov je: 
* Pretvorjen v format klepeta
* Obdelan z uporabo predloge klepeta Gemma-4
* Očiščen za odstranitev podvojenih žetonov BOS

## Učenje modela

Skripta izvede kratko predstavitev učenja z naslednjimi parametri:
- ~50 korakov
- Majhna velikost paketa
- Kopičenje gradientov

Med učenjem boste videli dnevnike, kot so:

![besedilo alt](assets/training.png)


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
> **Opomba:** vLLM ne podpira sistema Windows. Za uvajanje fino nastavljenega modela v sistemu Windows uporabite llama.cpp (glejte [Izvoz GGUF](#export-gguf-for-llamacpp) spodaj) ali prenesite združeni model na napravo Linux z zagnanim vLLM.
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

Ta opozorila izpiše Unsloth ob zagonu v okolju Windows ROCm in jih je varno prezreti:

| Opozorilo | Razlog | Varno za prezreti? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes nima gradnje za Windows ROCm | Da — ta vodnik uporablja `adamw_torch`, ne bnb |
| `No ROCm platform found for torch.distributed` | ROCm na Windowsu ne podpira porazdeljenega učenja | Da — na učenje z eno GPE to ne vpliva |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth označi gradnje, ki niso za Linux | Da — Windows ROCm deluje za SFT z eno GPE |
| `triton is not available` | Triton nima gradnje za Windows | Da — Unsloth se preklopi na PyTorch jedra |

Učenje se bo kljub tem opozorilom pravilno nadaljevalo.
<!-- @os:end -->

## Naslednji koraki
- Preizkusite [Unsloth Studio](https://unsloth.ai/docs/new/studio), intuitiven grafični vmesnik za Unsloth
- Učite na lastnih specifičnih naborih podatkov
- Preizkusite fino nastavljanje z različnimi hiperparametri
- Namestite z vLLM ali llama.cpp
- Preizkusite QLoRA za nastavitev z manjšo porabo pomnilnika

## Viri

Spodaj je nekaj dodatnih virov za več informacij o Unsloth in finem nastavljanju:

* [Unsloth Docs](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Vodnik za fino nastavljanje Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)