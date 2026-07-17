<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Acest playbook folosește etichete speciale pe care GitHub nu le poate reda. Vă rugăm să vizitați [amd.com/playbooks](https://amd.com/playbooks) pentru a previzualiza corect acest conținut.
<!-- @github-only:end -->

## Prezentare generală

Acest playbook arată cum să ajustați fin un model de limbaj local cu Unsloth pe hardware AMD.

Folosește un exemplu scurt de Ajustare Fină Supervizată (SFT) cu adaptoare LoRA pe `unsloth/gemma-4-E4B-it`, utilizând un subset al setului de date `mlabonne/FineTome-100k`. Scopul este de a vă oferi un flux de lucru simplu de la capăt la capăt care acoperă configurarea, antrenarea, inferența și salvarea rezultatului ajustat fin.

Exemplul este conceput pentru a fi practic și ușor de modificat, astfel încât să îl puteți folosi ca punct de plecare pentru propriile seturi de date și modele.

## Ce Veți Învăța

- Cum să configurați mediul Unsloth
- Cum să ajustați fin un LLM folosind SFT cu Unsloth
- Cum să salvați rezultatul ajustat fin în stocarea locală

<!-- @device:halo,stx,krk -->
> **Notă:** Tehnicile de ajustare fină din acest playbook necesită cel puțin 24 GB de memorie GPU și 32 GB de RAM de sistem.
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Notă:** Tehnicile de ajustare fină din acest playbook necesită cel puțin 24 GB de memorie GPU și 32 GB de RAM de sistem.
<!-- @os:end -->

<!-- @os:linux -->
> **Notă:** Tehnicile de ajustare fină din acest playbook necesită cel puțin 24 GB de memorie GPU **dedicată** și 32 GB de RAM de sistem.
<!-- @os:end -->
<!-- @device:end -->

## De Ce Unsloth?

Unsloth face ajustarea fină a LLM-urilor mai ușor de rulat pe hardware local, reducând utilizarea memoriei și accelerând antrenarea față de o configurare standard.

În acest playbook, folosim Unsloth împreună cu **SFT bazat pe LoRA**. Aceasta înseamnă că modelul de bază rămâne în mare parte înghețat, în timp ce un set mult mai mic de ponderi ale adaptorului este antrenat. Aceasta este o alegere potrivită pentru dezvoltarea locală, deoarece este mai ușoară decât ajustarea fină completă și mai rapidă pentru iterații.

Unsloth suportă și alte abordări de antrenare, inclusiv QLoRA și fluxuri de lucru de învățare prin consolidare. Acest playbook se concentrează mai întâi pe calea cea mai simplă: un exemplu mic de ajustare fină LoRA pe care utilizatorii îl pot rula, înțelege și extinde.

## Configurarea Memoriei

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificarea Actualizărilor de Software
> **Notă**: Dacă VS Code nu este instalat, îl puteți instala cu Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalarea Cerințelor Preliminare de Software

### Crearea unui Mediu Virtual

<!-- @os:linux -->
<!-- @device:halo_box -->
Deschideți un terminal și creați un venv cu software-ul AMD ROCm™ și PyTorch deja instalate:
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
**Acordați utilizatorului dvs. acces la dispozitivele GPU** (deconectați-vă și reconectați-vă pentru ca aceasta să intre în vigoare):

```bash
sudo usermod -aG render,video $LOGNAME
```

Deschideți un terminal și creați un venv:
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
> **Notă:** Python 3.13 este necesar pentru Windows.

<!-- @device:halo_box -->
Deschideți un terminal PowerShell și creați un mediu virtual:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Deschideți un terminal PowerShell și creați un mediu virtual:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Instalarea Dependențelor de Bază
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

### Dependențe Suplimentare

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

> **Notă:** În timpul importului, Unsloth poate sonda căile opționale de accelerare `bitsandbytes`. Pe unele versiuni ROCm, este posibil să vedeți un mesaj de tipul `bitsandbytes library load error: Configured ROCm binary not found`. Acest playbook folosește ajustarea fină LoRA standard cu `optim="adamw_torch"`, deci nu ne bazăm pe optimizatorul `bitsandbytes` sau pe QLoRA pe 4 biți. Acest mesaj poate fi ignorat în siguranță.

<!-- @os:windows -->
> **Notă:** Pe Windows ROCm, Unsloth va afișa mai multe avertismente la pornire — consultați [Avertismente Cunoscute](#known-warnings) mai jos. Toate acestea pot fi ignorate în siguranță; antrenarea funcționează corect.
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

## Descărcarea Scriptului de Ajustare Fină Unsloth

În loc să executați manual fiecare pas, acest playbook furnizează un script curat, de la capăt la capăt, aici: [test_unsloth.py](assets/test_unsloth.py).

Rulați următorul cod pentru a executa scriptul:

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

Restul playbook-ului va parcurge conceptual fiecare pas major al scriptului.

## Cum Funcționează

Scriptul test_unsloth.py efectuează următorii pași:
* **Încărcare Model**: Încarcă unsloth/gemma-4-E4B-it folosind FastModel.
* **Pregătire Date**: Standardizează setul de date (ex., FineTome-100k) și aplică șablonul de chat Gemma-4.
* **Aplicare LoRA**: Adaugă adaptoare la modulele de limbaj, atenție și MLP pentru antrenare eficientă.
* **Antrenare**: Folosește SFTTrainer cu mascarea pierderii doar pe răspuns.
* **Inferență**: Rulează un test rapid de generare pentru a verifica performanța.
* **Salvare**: Exportă adaptoarele LoRA local.

## Configurare Cheie

Puteți modifica următoarele constante pentru a personaliza rularea:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Exemplu de mesaj de bun venit Unsloth și ieșire la încărcarea ponderilor modelului:

![text alternativ](assets/welcome.png)

## Pregătirea Setului de Date

Folosim un subset din:
```text
mlabonne/FineTome-100k
```
Setul de date este:
* Convertit în format de chat
* Procesat folosind șablonul de chat Gemma-4
* Curățat pentru a elimina tokenurile BOS duplicate

## Antrenarea Modelului

Scriptul rulează o demonstrație scurtă de antrenare, cu următorii parametri:
- ~50 de pași
- Dimensiune mică a lotului
- Acumulare de gradient

În timpul antrenării, veți vedea jurnale precum:

![text alternativ](assets/training.png)


## Salvare și Implementare

### Salvare Locală (LoRA)

Scriptul salvează automat adaptoarele LoRA în OUTPUT_DIR.
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

### Salvarea modelului îmbinat (pentru vLLM)

<!-- @os:windows -->
> **Notă:** vLLM nu suportă Windows. Pentru a implementa modelul dvs. ajustat fin pe Windows, folosiți llama.cpp (consultați [Export GGUF](#export-gguf-for-llamacpp) mai jos) sau transferați modelul îmbinat pe o mașină Linux care rulează vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Pentru implementarea cu vLLM, îmbinați adaptoarele într-un model complet:
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

### Export GGUF (pentru llama.cpp)

Convertiți direct în GGUF pentru inferență locală:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Avertismente Cunoscute

Aceste avertismente sunt afișate de Unsloth la pornire pe Windows ROCm și toate pot fi ignorate în siguranță:

| Avertisment | Motiv | Poate fi ignorat? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes nu are o versiune pentru Windows ROCm | Da — acest playbook folosește `adamw_torch`, nu bnb |
| `No ROCm platform found for torch.distributed` | ROCm pe Windows nu suportă antrenarea distribuită | Da — antrenarea pe un singur GPU nu este afectată |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth semnalează versiunile non-Linux | Da — Windows ROCm funcționează pentru SFT pe un singur GPU |
| `triton is not available` | Triton nu are o versiune pentru Windows | Da — Unsloth revine la kernelurile PyTorch |

Antrenarea va continua corect în ciuda acestor avertismente.
<!-- @os:end -->

## Pași Următori
- Încercați [Unsloth Studio](https://unsloth.ai/docs/new/studio), o interfață grafică intuitivă pentru Unsloth
- Antrenați pe propriile seturi de date specifice
- Încercați ajustarea fină cu diferiți hiperparametri
- Implementați cu vLLM sau llama.cpp
- Încercați QLoRA pentru o configurare cu memorie mai redusă

## Resurse

Mai jos sunt câteva resurse suplimentare pentru a afla mai multe despre Unsloth și ajustarea fină:

* [Documentație Unsloth](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Ghid de Ajustare Fină Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)