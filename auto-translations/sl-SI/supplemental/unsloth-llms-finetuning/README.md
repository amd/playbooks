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

Ta vodnik prikazuje, kako lokalno natančno prilagoditi jezikovni model z Unsloth na strojni opremi AMD.

Uporablja kratek primer nadzorovanega natančnega prilagajanja (Supervised Fine-Tuning, SFT) s prilagojevalniki LoRA na `unsloth/gemma-4-E4B-it`, pri čemer uporablja podmnožico nabora podatkov `mlabonne/FineTome-100k`. Cilj je zagotoviti preprost celovit potek dela, ki zajema nastavitev, učenje, sklepanje in shranjevanje natančno prilagojenega rezultata.

Primer je zasnovan tako, da je praktičen in ga je enostavno prilagoditi, tako da ga lahko uporabite kot izhodišče za lastne nabore podatkov in modele.

## Kaj se boste naučili

- Kako nastaviti okolje Unsloth
- Kako natančno prilagoditi LLM z uporabo SFT z Unsloth
- Kako shraniti natančno prilagojen rezultat v lokalno shrambo

<!-- @device:halo,stx,krk -->
> **Opomba:** Tehnike natančnega prilagajanja v tem vodniku zahtevajo vsaj **64 GB pomnilnika sistema**, od tega mora biti vsaj **24 GB na voljo GPE-ju** (24 GB je del 64 GB, ne dodatno).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Opomba:** Tehnike natančnega prilagajanja v tem vodniku zahtevajo vsaj **24 GB skupnega pomnilnika GPE** in **32 GB pomnilnika sistema**.
> - V sistemu Windows skupni pomnilnik GPE združuje namenski VRAM grafične kartice s skupnim pomnilnikom GPE (izposojenim iz pomnilnika sistema).
> - Zato lahko kartice z manj kot 24 GB namenskega VRAM-a še vedno poganjajo ta vodnik z uporabo skupnega pomnilnika GPE za nadomestitev razlike.
<!-- @os:end -->

<!-- @os:linux -->
> **Opomba:** Tehnike natančnega prilagajanja v tem vodniku zahtevajo grafično kartico z vsaj **24 GB namenskega pomnilnika GPE** in **32 GB pomnilnika sistema**.
> - V sistemu Linux učenje poteka v celoti v namenskem VRAM-u grafične kartice.
> - Ne preide na skupni pomnilnik GPE (pomnilnik sistema), ko VRAM zmanjka.
> - Kartice z manj kot 24 GB namenskega VRAM-a bodo med učenjem v sistemu Linux zmanjkale pomnilnika, tudi če ima sistem veliko RAM-a.
<!-- @os:end -->
<!-- @device:end -->

## Zakaj Unsloth?

Unsloth olajša izvajanje natančnega prilagajanja LLM na lokalni strojni opremi z zmanjšanjem porabe pomnilnika in pospešitvijo učenja v primerjavi s standardno nastavitvijo.

V tem vodniku uporabljamo Unsloth skupaj z **SFT na osnovi LoRA**. To pomeni, da osnovni model ostane večinoma zamrznjen, medtem ko se uči veliko manjši nabor uteži prilagojevalnikov. To je dobra izbira za lokalni razvoj, ker je lažje od popolnega natančnega prilagajanja in hitrejše za iterativno delo.

Unsloth podpira tudi druge pristope učenja, vključno s QLoRA in poteki dela za spodbujevalno učenje. Ta vodnik se najprej osredotoča na najpreprostejšo pot: majhen primer natančnega prilagajanja LoRA, ki ga lahko uporabniki zaženejo, razumejo in razširijo.

<!-- @device:halo_box,halo,stx,krk -->
## Nastavitev konfiguracije pomnilnika

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Preverjanje posodobitev programske opreme
> **Opomba**: Če VS Code ni nameščen, ga lahko namestite z Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Nameščanje predpogojev programske opreme

### Ustvarjanje navideznega okolja

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
**Podelite svojemu uporabniku dostop do naprav GPE** (odjavite se in se znova prijavite, da se to uveljavi):

```bash
sudo usermod -aG render,video $LOGNAME
```

Odprite terminal in ustvarite venv:
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
> **Opomba:** Za Windows je zahtevan Python 3.13.

<!-- @device:halo_box -->
Odprite terminal PowerShell in ustvarite navidezno okolje:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Odprite terminal PowerShell in ustvarite navidezno okolje:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Nameščanje osnovnih odvisnosti
<!-- @require:driver -->

> **Pomembno:** Unsloth še ne podpira gradnje PyTorch 2.13, ki se dobavlja z ROCm 10. Za ta vodnik namestite **ROCm 7.14 s PyTorch 2.12** z uporabo spodnjih ukazov. Ne uporabljajte paketov ROCm 10 / PyTorch 2.13.

**Namestite PyTorch s podporo za programsko opremo AMD ROCm™** v ustvarjenem navideznem okolju:

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

Za druge naprave si oglejte [ROCm 7.14 Documentation](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html) za popolna navodila.

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
pip install "unsloth[amd] @ git+https://github.com/unslothai/unsloth.git" triton-windows
```
<!-- @test:end -->
<!-- @os:end -->

> **Opomba:** Med uvozom lahko Unsloth preveri neobvezne pospeševalne poti `bitsandbytes`. Pri nekaterih različicah ROCm boste morda videli sporočilo, kot je `bitsandbytes library load error: Configured ROCm binary not found`. Ta vodnik uporablja standardno natančno prilagajanje LoRA z `optim="adamw_torch"`, zato se ne zanašamo na optimizator `bitsandbytes` ali 4-bitni QLoRA. To sporočilo lahko varno prezrete.

<!-- @os:windows -->
> **Opomba:** Na Windows ROCm bo Unsloth ob zagonu izpisal več opozoril – glejte [Znana opozorila](#known-warnings) spodaj. Vsa jih je varno prezreti; učenje deluje pravilno.
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

## Prenos skripta za natančno prilagajanje Unsloth

Namesto ročnega izvajanja vsakega koraka ta vodnik zagotavlja čist, celovit skript tukaj: [test_unsloth.py](assets/test_unsloth.py).

Zaženite naslednjo kodo za izvedbo skripta:

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

Preostanek vodnika bo konceptualno predstavil vsak glavni korak skripta.

## Kako deluje

Skript test_unsloth.py izvede naslednje korake:
* **Nalaganje modela**: Naloži unsloth/gemma-4-E4B-it z uporabo FastModel.
* **Priprava podatkov**: Standardizira nabor podatkov (npr. FineTome-100k) in uporabi predlogo klepeta Gemma-4.
* **Uporaba LoRA**: Doda prilagojevalnike jezikovnim, pozornostnim in MLP modulom za učinkovito učenje.
* **Učenje**: Uporabi SFTTrainer z maskiranjem izgube samo za odgovore.
* **Sklepanje**: Izvede hiter test generiranja za preverjanje zmogljivosti.
* **Shranjevanje**: Izvozi prilagojevalnike LoRA lokalno.
## Ključna konfiguracija

Naslednje konstante lahko spremenite, da prilagodite svoj zagon:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Primer pozdravnega sporočila Unsloth in izpisa pri nalaganju uteži modela:

![alt text](assets/welcome.png)

## Priprava nabora podatkov

Uporabljamo podnabor:
```text
mlabonne/FineTome-100k
```
Nabor podatkov je: 
* Pretvorjen v format klepeta
* Obdelan z uporabo predloge klepeta Gemma-4
* Očiščen, da se odstranijo podvojeni žetoni BOS

## Učenje modela

Skripta izvede kratko demonstracijo učenja z naslednjimi parametri:
- ~50 korakov
- Majhna velikost paketa
- Gradientna akumulacija

Med učenjem boste videli dnevniške zapise, kot so:

![alt text](assets/training.png)


## Shranjevanje in uvajanje

### Lokalno shranjevanje (LoRA)

Skripta samodejno shrani prilagojevalnike LoRA v OUTPUT_DIR.
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
> **Opomba:** vLLM ne podpira sistema Windows. Za uvajanje vašega natančno prilagojenega modela v sistemu Windows uporabite llama.cpp (glejte [Izvoz v GGUF](#export-gguf-for-llamacpp) spodaj) ali prenesite združeni model na napravo Linux, ki poganja vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Za uvajanje z vLLM združite prilagojevalnike v celoten model:
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

### Izvoz v GGUF (za llama.cpp)

Neposredno pretvorite v GGUF za lokalno sklepanje:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Znana opozorila

Ta opozorila izpiše Unsloth ob zagonu v sistemu Windows ROCm in jih je varno prezreti:

| Opozorilo | Razlog | Ali je varno prezreti? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes nima različice za Windows ROCm | Da — ta priročnik uporablja `adamw_torch`, ne bnb |
| `No ROCm platform found for torch.distributed` | ROCm v sistemu Windows ne podpira porazdeljenega učenja | Da — na učenje z eno grafično kartico to ne vpliva |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth označi platforme, ki niso Linux | Da — Windows ROCm deluje za SFT z eno grafično kartico |
| `triton is not available` | Triton nima različice za Windows | Da — Unsloth se privzame na jedra PyTorch |

Učenje bo kljub tem opozorilom potekalo pravilno.
<!-- @os:end -->

## Naslednji koraki
- Preizkusite [Unsloth Studio](https://unsloth.ai/docs/new/studio), intuitiven grafični vmesnik za Unsloth
- Učite na svojih lastnih specifičnih naborih podatkov
- Preizkusite natančno prilagajanje z različnimi hiperparametri
- Uvedite z vLLM ali llama.cpp
- Preizkusite QLoRA za nastavitev z manjšo porabo pomnilnika

## Viri

Spodaj je nekaj dodatnih virov za nadaljnje spoznavanje Unsloth in natančnega prilagajanja:

* [Dokumentacija Unsloth](https://docs.unsloth.ai)

* [Unsloth na GitHub](https://github.com/unslothai/unsloth)

* [Vodnik za natančno prilagajanje Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)