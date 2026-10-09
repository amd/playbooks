<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din limba engleză și nu a fost revizuită de o persoană. Aceasta poate conține erori, iar anumite instrucțiuni, comenzi, descărcări, disponibilitatea produselor sau alt conținut pot varia în funcție de limbă sau regiune. În cazul oricărei neconcordanțe sau discrepanțe, versiunea originală în limba engleză a playbook-ului prevalează.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Prezentare generală

Acest playbook arată cum să ajustezi fin (fine-tune) un model de limbaj local cu Unsloth pe hardware AMD.

Folosește un exemplu scurt de Supervised Fine-Tuning (SFT) cu adaptoare LoRA pe `unsloth/gemma-4-E4B-it`, utilizând un subset al setului de date `mlabonne/FineTome-100k`. Scopul este să îți ofere un flux de lucru simplu, de la cap la coadă, care acoperă configurarea, antrenarea, inferența și salvarea rezultatului ajustat fin.

Exemplul este conceput să fie practic și ușor de modificat, astfel încât să îl poți folosi ca punct de plecare pentru propriile seturi de date și modele.

## Ce vei învăța

- Cum să configurezi mediul Unsloth
- Cum să ajustezi fin un LLM folosind SFT cu Unsloth
- Cum să salvezi rezultatul ajustat fin în stocarea locală

<!-- @device:halo,stx,krk -->
> **Notă:** Tehnicile de ajustare fină din acest playbook necesită cel puțin **64 GB de memorie RAM de sistem**, din care cel puțin **24 GB disponibili pentru GPU** (cei 24 GB fac parte din cei 64 GB, nu se adaugă suplimentar).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Notă:** Tehnicile de ajustare fină din acest playbook necesită cel puțin **24 GB de memorie GPU totală** și **32 GB de memorie RAM de sistem**.
> - Pe Windows, memoria GPU totală combină VRAM-ul dedicat al plăcii grafice cu memoria GPU partajată (împrumutată din memoria RAM de sistem).
> - Prin urmare, plăcile cu mai puțin de 24 GB de VRAM dedicat pot rula totuși acest playbook folosind memoria GPU partajată pentru a compensa diferența.
<!-- @os:end -->

<!-- @os:linux -->
> **Notă:** Tehnicile de ajustare fină din acest playbook necesită o placă grafică cu cel puțin **24 GB de memorie GPU dedicată** și **32 GB de memorie RAM de sistem**.
> - Pe Linux, antrenarea rulează în întregime în VRAM-ul dedicat al plăcii grafice.
> - Nu se trece la memoria GPU partajată (RAM de sistem) atunci când VRAM-ul se epuizează.
> - Plăcile cu mai puțin de 24 GB de VRAM dedicat vor rămâne fără memorie în timpul antrenării pe Linux, chiar dacă sistemul are suficientă memorie RAM.
<!-- @os:end -->
<!-- @device:end -->

## De ce Unsloth?

Unsloth face ca ajustarea fină a LLM-urilor să fie mai ușor de rulat pe hardware local, reducând utilizarea memoriei și accelerând antrenarea comparativ cu o configurare standard.

În acest playbook, folosim Unsloth împreună cu **SFT bazat pe LoRA**. Asta înseamnă că modelul de bază rămâne în mare parte înghețat, în timp ce un set mult mai mic de ponderi de adaptor este antrenat. Aceasta este o potrivire bună pentru dezvoltarea locală deoarece este mai ușoară decât ajustarea fină completă și mai rapidă pentru iterare.

Unsloth susține de asemenea și alte abordări de antrenare, inclusiv QLoRA și fluxuri de lucru de învățare prin întărire (reinforcement learning). Acest playbook se concentrează mai întâi pe cea mai simplă cale: un exemplu mic de ajustare fină LoRA pe care utilizatorii îl pot rula, înțelege și extinde.

<!-- @device:halo_box,halo,stx,krk -->
## Configurarea memoriei

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Verificarea actualizărilor de software
> **Notă**: Dacă VS Code nu este instalat, îl poți instala cu Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalarea cerințelor preliminare de software

<!-- @prereq:hf-models-gemma-4-e4b-it,hf-datasets-finetome-100k -->

### Crearea unui mediu virtual

<!-- @os:linux -->
<!-- @device:halo_box -->
Deschide un terminal și creează un venv cu software-ul AMD ROCm™ și PyTorch deja instalate:
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
**Acordă-i utilizatorului tău acces la dispozitivele GPU** (deconectează-te și reconectează-te pentru ca aceasta să aibă efect):

```bash
sudo usermod -aG render,video $LOGNAME
```

Deschide un terminal și creează un venv:
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
> **Notă:** Python 3.13 este necesar pentru Windows.

<!-- @device:halo_box -->
Deschide un terminal PowerShell și creează un mediu virtual:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Deschide un terminal PowerShell și creează un mediu virtual:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Instalarea dependențelor de bază
<!-- @require:driver -->

> **Important:** Unsloth nu susține încă varianta PyTorch 2.13 livrată cu ROCm 10. Pentru acest playbook, instalează **ROCm 7.14 cu PyTorch 2.12** folosind comenzile de mai jos. Nu folosi pachetele ROCm 10 / PyTorch 2.13.

**Instalează PyTorch cu suport pentru software-ul AMD ROCm™** în mediul virtual creat:

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

Pentru alte dispozitive, consultă [ROCm 7.14 Documentation](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html) pentru instrucțiuni complete.

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

### Dependențe suplimentare

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

> **Notă:** În timpul importului, Unsloth poate sonda căi opționale de accelerare `bitsandbytes`. Pe unele versiuni de ROCm, poți vedea un mesaj precum `bitsandbytes library load error: Configured ROCm binary not found`. Acest playbook folosește ajustare fină LoRA standard cu `optim="adamw_torch"`, așadar nu ne bazăm pe optimizatorul `bitsandbytes` sau pe QLoRA pe 4 biți. Acest mesaj poate fi ignorat în siguranță.

<!-- @os:windows -->
> **Notă:** Pe Windows ROCm, Unsloth va afișa câteva avertismente la pornire — vezi [Known Warnings](#known-warnings) mai jos. Toate acestea pot fi ignorate în siguranță; antrenarea funcționează corect.
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

## Descarcă scriptul de ajustare fină Unsloth

În loc să execuți manual fiecare pas, acest playbook oferă un script curat, de la cap la coadă, aici: [test_unsloth.py](assets/test_unsloth.py).

Rulează următorul cod pentru a executa scriptul:

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

## Cum funcționează

Scriptul test_unsloth.py efectuează următorii pași:
* **Încărcarea modelului**: Încarcă unsloth/gemma-4-E4B-it folosind FastModel.
* **Pregătirea datelor**: Standardizează setul de date (de exemplu, FineTome-100k) și aplică șablonul de chat Gemma-4.
* **Aplicarea LoRA**: Adaugă adaptoare modulelor de limbaj, atenție și MLP pentru o antrenare eficientă.
* **Antrenare**: Folosește SFTTrainer cu mascarea pierderii doar pe răspunsuri (response-only loss masking).
* **Inferență**: Rulează un test rapid de generare pentru a verifica performanța.
* **Salvare**: Exportă adaptoarele LoRA local.
## Configurarea cheilor

Puteți modifica următoarele constante pentru a personaliza execuția:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Exemplu de mesaj de bun venit Unsloth și rezultatul afișat la încărcarea ponderilor modelului:

![alt text](assets/welcome.png)

## Pregătirea setului de date

Folosim un subset din:
```text
mlabonne/FineTome-100k
```
Setul de date este: 
* Convertit în format de chat
* Procesat folosind șablonul de chat Gemma-4
* Curățat pentru a elimina token-urile BOS duplicate

## Antrenarea modelului

Scriptul rulează o scurtă demonstrație de antrenare, cu următorii parametri:
- ~50 de pași
- Dimensiune mică a lotului
- Acumulare de gradienți

În timpul antrenării, veți vedea jurnale precum:

![alt text](assets/training.png)


## Salvare și implementare

### Salvare locală (LoRA)

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
> **Notă:** vLLM nu acceptă Windows. Pentru a implementa modelul dvs. ajustat fin pe Windows, utilizați llama.cpp (consultați [Export GGUF](#export-gguf-for-llamacpp) mai jos) sau transferați modelul îmbinat către o mașină Linux care rulează vLLM.
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
## Avertismente cunoscute

Aceste avertismente sunt afișate de Unsloth la pornire pe Windows ROCm și pot fi ignorate în siguranță:

| Avertisment | Motiv | Poate fi ignorat în siguranță? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes nu are o versiune compilată pentru Windows ROCm | Da — acest playbook folosește `adamw_torch`, nu bnb |
| `No ROCm platform found for torch.distributed` | ROCm pe Windows nu dispune de antrenare distribuită | Da — antrenarea pe un singur GPU nu este afectată |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth semnalează versiunile non-Linux | Da — Windows ROCm funcționează pentru SFT pe un singur GPU |
| `triton is not available` | Triton nu are o versiune pentru Windows | Da — Unsloth revine la nucleele PyTorch |

Antrenarea va continua corect în ciuda acestor avertismente.
<!-- @os:end -->

## Pașii următori
- Încercați [Unsloth Studio](https://unsloth.ai/docs/new/studio), o interfață grafică intuitivă pentru Unsloth
- Antrenați pe propriile seturi de date specifice
- Încercați ajustarea fină cu diferiți hiperparametri
- Implementați cu vLLM sau llama.cpp
- Încercați QLoRA pentru o configurație cu consum redus de memorie

## Resurse

Mai jos sunt câteva resurse suplimentare pentru a afla mai multe despre Unsloth și ajustarea fină:

* [Documentația Unsloth](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Ghidul de ajustare fină Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)