<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din limba engleză și nu a fost revizuită de o persoană. Aceasta poate conține erori, iar anumite instrucțiuni, comenzi, descărcări, disponibilitatea produselor sau alt conținut pot varia în funcție de limbă sau regiune. În cazul oricărei neconcordanțe sau discrepanțe, versiunea originală în limba engleză a playbook-ului prevalează.
<!-- auto-translated-disclaimer:end -->

## Prezentare generală

Ajustarea eficientă (fine-tuning) este esențială pentru adaptarea modelelor lingvistice de mari dimensiuni (LLM) la sarcini specifice. LLaMA Factory este o platformă open-source și prietenoasă cu utilizatorul, care simplifică antrenarea și ajustarea modelelor lingvistice de mari dimensiuni și a modelelor multimodale. Aceasta le permite utilizatorilor să personalizeze sute de modele pre-antrenate local, cu un minim de programare.

Acest ghid vă învață cum să efectuați fine-tuning pentru LLM-uri folosind LLaMA Factory pe hardware-ul dvs. local AMD.

<!-- @device:stx,krk -->
> **Notă:** Tehnicile de fine-tuning din acest ghid necesită cel puțin **32 GB de RAM de sistem**, din care cel puțin **16 GB să fie disponibili pentru GPU** (cei 16 GB fac parte din cei 32 GB, nu se adaugă la aceștia).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Notă:** Tehnicile de fine-tuning din acest ghid necesită cel puțin **16 GB de memorie GPU totală** și **32 GB de RAM de sistem**.
> - Pe Windows, memoria GPU totală combină VRAM-ul dedicat al plăcii grafice cu memoria GPU partajată (împrumutată din RAM-ul sistemului).
> - Prin urmare, plăcile cu mai puțin de 16 GB de VRAM dedicat pot totuși rula acest ghid folosind memoria GPU partajată pentru a compensa diferența.
<!-- @os:end -->

<!-- @os:linux -->
> **Notă:** Tehnicile de fine-tuning din acest ghid necesită o placă grafică cu cel puțin **16 GB de memorie GPU dedicată** și **32 GB de RAM de sistem**.
> - Pe Linux, antrenarea rulează în întregime în VRAM-ul dedicat al plăcii grafice.
> - Aceasta nu recurge la memoria GPU partajată (RAM-ul sistemului) atunci când VRAM-ul se epuizează.
> - Plăcile cu mai puțin de 16 GB de VRAM dedicat vor rămâne fără memorie în timpul antrenării pe Linux, chiar dacă sistemul dispune de suficient RAM.
<!-- @os:end -->
<!-- @device:end -->

## Ce veți învăța

- Cum să configurați LLaMA Factory cu software-ul AMD ROCm™
- Cum să configurați parametrii de fine-tuning pentru LLM (folosind Qwen/Qwen3-4B-Instruct-2507 ca exemplu)
- Cum să rulați fine-tuning-ul LLaMA Factory
- Cum să rulați inferența cu modelul ajustat (fine-tuned)
- Cum să exportați modelul ajustat (fine-tuned)

## Timp estimat

- Durată: Rularea acestui ghid va dura aproximativ 60 de minute (în funcție de dimensiunea modelului/setului de date și viteza rețelei).
- Vizitați [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory) pentru mai multe informații.

## Configurarea memoriei

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificarea actualizărilor software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalarea cerințelor software preliminare

<!-- @os:linux -->
<!-- @test:id=python-prereqs-check timeout=120 hidden=True -->
```bash
python3 --version
pip --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=python-prereqs-check timeout=120 hidden=True -->
```powershell
python --version
pip --version
```
<!-- @test:end -->
<!-- @os:end -->

#### Creați un mediu virtual

<!-- @os:linux -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv llamafactory-env --system-site-packages
source llamafactory-env/bin/activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="source llamafactory-env/bin/activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
**Acordați utilizatorului dvs. acces la dispozitivele GPU** (deconectați-vă și reconectați-vă pentru ca aceasta să aibă efect):

```bash
sudo usermod -aG render,video $LOGNAME
```

<!-- @test:id=create-venv timeout=120 -->
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv llamafactory-env
source llamafactory-env/bin/activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="source llamafactory-env/bin/activate" -->
<!-- @device:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @device:halo_box -->
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv llamafactory-env --system-site-packages
llamafactory-env\Scripts\activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="llamafactory-env\Scripts\activate" --> 
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv llamafactory-env
llamafactory-env\Scripts\activate
```
<!-- @test:end --> 
<!-- @setup:id=activate-venv command="llamafactory-env\Scripts\activate" --> 
<!-- @device:end -->
<!-- @os:end -->

### Instalarea dependențelor de bază

<!-- @require:pytorch,driver -->
 
### Instalarea dependențelor suplimentare

> **Notă**: Asigurați-vă că versiunea Python este 3.11, 3.12 sau 3.13

```bash
pip install huggingface_hub
```

<!-- @os:linux -->
<!-- @test:id=install-deps timeout=300 hidden=True setup=activate-venv -->
```bash
python3 -m pip install --upgrade pip
python3 -m pip install huggingface_hub
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=install-deps timeout=300 hidden=True setup=activate-venv -->
```powershell
python -m pip install --upgrade pip
python -m pip install huggingface_hub
```
<!-- @test:end --> 
<!-- @os:end -->

### Instalați LLaMA Factory

LLaMA Factory depinde de PyTorch. Ar trebui să îl aveți deja instalat conform cerințelor de mai sus.

Descărcați codul sursă din [depozitul oficial GitHub al LLaMA Factory](https://github.com/hiyouga/LlamaFactory) și instalați dependențele acestuia.

<!-- @device:halo_box -->
<!-- @test:id=install-llamafactory timeout=900 setup=activate-venv -->
```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install setuptools --break-system-packages
pip install -e . --break-system-packages
pip install -r requirements/metrics.txt --break-system-packages
```
<!-- @test:end --> 
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @test:id=install-llamafactory timeout=900 setup=activate-venv -->
```bash
git clone --depth 1 https://github.com/hiyouga/LlamaFactory.git
cd LlamaFactory
pip install -e .
pip install -r requirements/metrics.txt 
```
<!-- @test:end --> 
<!-- @device:end -->

Verificați dacă `llamafactory-cli` este executabil.

<!-- @os:linux -->
<!-- @test:id=verify-llamafactory-cli timeout=60 hidden=False setup=activate-venv -->
```bash
cd LlamaFactory
llamafactory-cli version || python -m llamafactory.cli version || true
echo "llamafactory-cli is available"
command -v llamafactory-cli
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=verify-llamafactory-cli timeout=60 hidden=False setup=activate-venv -->
```powershell
cd LlamaFactory
if (Get-Command llamafactory-cli -ErrorAction SilentlyContinue) {
    llamafactory-cli version
    Write-Host "llamafactory-cli is available"
} else {
    Write-Host "llamafactory-cli is not available"
}
```
<!-- @test:end --> 
<!-- @os:end -->

Exemplu de rezultat:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

După ce ați instalat cu succes LLaMA Factory, să rulăm fine-tuning-ul pe acesta.

## Utilizarea LLaMA Factory CLI pentru Fine Tuning

Această secțiune va acoperi modul de pregătire a seturilor de date pentru fine-tuning, configurarea parametrilor LoRA/QLoRA și rularea fine-tuning-ului LoRA.

### Pregătirea setului de date

LLaMA Factory acceptă seturi de date pentru fine-tuning în formatul Alpaca și formatul ShareGPT. Toate seturile de date disponibile au fost definite în [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). Dacă utilizați un set de date personalizat, asigurați-vă că adăugați o descriere a setului de date în `dataset_info.json` și specificați numele setului de date înainte de antrenare. Detalii pot fi găsite în documentația lor [aici](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

În acest ghid, vom folosi seturile de date identity și alpaca_en_demo ca exemplu și vom configura informațiile despre setul de date în pasul următor.
### Configurarea parametrilor de fine-tuning

LLaMA Factory acceptă multiple scheme de fine-tuning.

| Scheme de fine-tuning | Exemple LLaMA Factory |
|-----------|------|
| Parametru complet    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| Fine-tuning LoRA  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| Fine-tuning QLoRA | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

<!-- @test:id=verify-llamafactory-files timeout=60 hidden=True setup=activate-venv -->
```python
import os
import sys

base = "LlamaFactory"
required = [
    "examples/train_lora/qwen3_lora_sft.yaml",
    "examples/inference/qwen3_lora_sft.yaml",
    "examples/merge_lora/qwen3_lora_sft.yaml",
]

missing = [p for p in required if not os.path.exists(os.path.join(base, p))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

print("PASS: Required LLaMA Factory example files exist")
```
<!-- @test:end -->

Aceste fișiere de configurare exemplu au specificat parametri ai modelului, parametri ai metodei de fine-tuning, parametri ai setului de date, parametri de evaluare și altele. Le puteți configura în funcție de propriile nevoi. În acest playbook, vom folosi [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml). 

**Explicația parametrilor cheie:**
- `model_name_or_path` - Numele modelului Hugging Face sau calea locală către fișierul modelului.
- `stage` - Etapa de antrenare. Opțiuni: rm (reward modeling), pt (pretrain), sft (Supervised Fine-Tuning), PPO, DPO, KTO, ORPO.
- `do_train` - true pentru antrenare, false pentru evaluare
- `finetuning_type` - Metoda de fine-tuning. Opțiuni: freeze, lora, full
- `lora_rank` - Dimensionalitatea matricei de rang redus utilizate în LoRA, valori tipice: 4, 6, 8, 16 (valori mai mici = mai puțini parametri = fine-tuning mai rapid; valori mai mari = adaptare mai bună la sarcină, dar utilizare mai mare a resurselor).
- `lora_target` - Module țintă pentru metoda LoRA. Implicit: all.
- `dataset` - Setul (seturile) de date de utilizat. Folosiți „,” pentru a separa mai multe seturi de date
- `output_dir` - Calea de ieșire pentru fine-tuning
- `logging_steps` - Intervalul de logging în pași
- `save_steps` - Intervalul de salvare a punctelor de control ale modelului.
- `overwrite_output_dir` - Dacă se permite suprascrierea directorului de ieșire.
- `per_device_train_batch_size` - Dimensiunea batch-ului de antrenare per dispozitiv.
- `gradient_accumulation_steps` - Numărul de pași de acumulare a gradientului.
- `learning_rate` - Rata de învățare
- `num_train_epochs` - Numărul de epoci de antrenare
- `lr_scheduler_type` - Programarea ratei de învățare. Opțiuni: linear, cosine, polynomial, constant etc.
- `warmup_ratio` - Raportul de încălzire (warmup) al ratei de învățare

<!-- @os:linux -->
Vom modifica valoarea implicită a `lora_rank` pentru a rula fine-tuning pe GPU-uri AMD Ryzen™ & AMD Radeon™.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
Vom actualiza configurația implicită de fine-tuning LoRA pentru o compatibilitate mai bună cu GPU-urile AMD Ryzen™ și AMD Radeon™:
- Setați `lora_rank` de la `8` la `6` pentru a reduce utilizarea memoriei în timpul fine-tuning-ului.
- Utilizați `fp16` în loc de `bf16` pentru o compatibilitate mai largă cu GPU-urile AMD și o utilizare mai redusă a memoriei.
- Setați `dataloader_num_workers` la `0` pe Windows pentru a evita erorile de tip `"Can't pickle local object<>"` cauzate de încărcarea datelor prin multiprocessing.

```powershell
$filePath = "examples/train_lora/qwen3_lora_sft.yaml"

# Create a backup before modifying the YAML file
Copy-Item -Path $filePath -Destination "$filePath.bak" -Force

# Read the file and update the training settings
$content = Get-Content -Path $filePath -Raw

$newContent = $content `
  -replace 'lora_rank: 8', 'lora_rank: 6' `
  -replace 'bf16: true', 'fp16: true' `
  -replace 'dataloader_num_workers: 4', 'dataloader_num_workers: 0'

Set-Content -Path $filePath -Value $newContent
```
<!-- @os:end -->

### Rularea fine-tuning-ului LLaMA Factory 

**llamafactory-cli** este instrumentul oficial de interfață de linie de comandă (CLI) pentru LLaMA Factory, dezvoltat pentru a simplifica fluxurile de lucru end-to-end pentru LLM (pregătirea datelor → fine-tuning → evaluare → implementare) fără a scrie cod complex.

Pentru antrenare/fine-tuning, **llamafactory-cli train** este subcomanda de bază a CLI-ului LLaMA Factory. Aceasta abstractizează fluxurile de lucru de fine-tuning (preprocesarea datelor, ajustarea hiperparametrilor, optimizarea hardware) într-o singură comandă CLI, acceptând mai multe paradigme de fine-tuning (LoRA/QLoRA/Full Fine-Tuning) și fiind optimizată pentru GPU-uri cu resurse reduse (de exemplu, QLoRA pe 16GB VRAM).

Puteți rula fine-tuning-ul LLaMA Factory folosind următoarea comandă, bazată pe fișierul de configurare modificat pentru fine-tuning-ul Qwen3 LoRA.

```bash
llamafactory-cli train examples/train_lora/qwen3_lora_sft.yaml
```

<!-- @os:linux -->
<!-- @test:id=quick-train-llamafactory-lora timeout=1200 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory

cp examples/train_lora/qwen3_lora_sft.yaml examples/train_lora/qwen3_lora_sft_ci.yaml

sed -i 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's|output_dir: .*|output_dir: saves/qwen3_lora_sft_ci|g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/overwrite_output_dir: false/overwrite_output_dir: true/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/per_device_train_batch_size: .*/per_device_train_batch_size: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/gradient_accumulation_steps: .*/gradient_accumulation_steps: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/num_train_epochs: .*/num_train_epochs: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/logging_steps: .*/logging_steps: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
sed -i 's/save_steps: .*/save_steps: 5/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true

sed -i 's/max_samples: .*/max_samples: 16/g' examples/train_lora/qwen3_lora_sft_ci.yaml || true
if grep -q '^max_steps:' examples/train_lora/qwen3_lora_sft_ci.yaml; then
  sed -i 's/^max_steps:.*/max_steps: 5/g' examples/train_lora/qwen3_lora_sft_ci.yaml
else
  printf '\nmax_steps: 5\n' >> examples/train_lora/qwen3_lora_sft_ci.yaml
fi
if grep -q '^save_total_limit:' examples/train_lora/qwen3_lora_sft_ci.yaml; then
  sed -i 's/^save_total_limit:.*/save_total_limit: 1/g' examples/train_lora/qwen3_lora_sft_ci.yaml
else
  printf 'save_total_limit: 1\n' >> examples/train_lora/qwen3_lora_sft_ci.yaml
fi

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=quick-train-llamafactory-lora timeout=1200 hidden=True setup=activate-venv -->
```powershell
Set-Location -Path "LlamaFactory"

Copy-Item -Path "examples/train_lora/qwen3_lora_sft.yaml" -Destination "examples/train_lora/qwen3_lora_sft_ci.yaml"

$filePath = "examples/train_lora/qwen3_lora_sft_ci.yaml"
(Get-Content -Path $filePath) -replace 'lora_rank: 8', 'lora_rank: 6' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'bf16:\s*true', 'fp16: true' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'dataloader_num_workers:\s*4', 'dataloader_num_workers: 0' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'output_dir: .*', 'output_dir: saves/qwen3_lora_sft_ci' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'overwrite_output_dir: false', 'overwrite_output_dir: true' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'per_device_train_batch_size: .*', 'per_device_train_batch_size: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'gradient_accumulation_steps: .*', 'gradient_accumulation_steps: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'num_train_epochs: .*', 'num_train_epochs: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'logging_steps: .*', 'logging_steps: 1' | Set-Content -Path $filePath
(Get-Content -Path $filePath) -replace 'save_steps: .*', 'save_steps: 5' | Set-Content -Path $filePath

(Get-Content -Path $filePath) -replace 'max_samples: .*', 'max_samples: 16' | Set-Content -Path $filePath
if (Select-String -Path $filePath -Pattern '^max_steps:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^max_steps:.*', 'max_steps: 5' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value ""
    Add-Content -Path $filePath -Value "max_steps: 5"
}
if (Select-String -Path $filePath -Pattern '^save_total_limit:' -Quiet) {
    (Get-Content -Path $filePath) -replace '^save_total_limit:.*', 'save_total_limit: 1' | Set-Content -Path $filePath
} else {
    Add-Content -Path $filePath -Value "save_total_limit: 1"
}

llamafactory-cli train examples/train_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->

După rularea fine-tuning-ului LLM, toate ieșirile generate sunt stocate în „output_dir”, inclusiv fișierele punctelor de control ale modelului, fișierele de configurare și metricile de antrenare.

<p align="center">
  <img src="assets/qwen3_lora.png" alt="Qwen3 LoRA Fine-tuning" width="600"/>
</p>

<!-- @test:id=verify-llamafactory-train-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "LlamaFactory/saves/qwen3_lora_sft_ci"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing output directory: {out_dir}")
    sys.exit(1)

required = [
    "adapter_config.json",
    "trainer_state.json",
    "training_args.bin",
]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required files: {missing}")
    sys.exit(1)

adapter_weights = glob.glob(os.path.join(out_dir, "adapter_model*.safetensors")) + glob.glob(os.path.join(out_dir, "adapter_model*.bin"))
if not adapter_weights:
    print("FAIL: Missing adapter weights")
    sys.exit(1)

print("PASS: LLaMA Factory training output looks correct")
print(f"Found adapter weights: {adapter_weights}")
```
<!-- @test:end --> 

### Testarea modelului fine-tuned 

**llamafactory-cli chat** este conceput pentru chat/inferență interactivă cu LLM-uri (atât modele de bază, cât și modele fine-tuned cu LoRA). LLaMA Factory oferă configurația exemplu pentru a rula inferența modelelor fine-tuned în [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference). Puteți, de asemenea, să modificați această configurație exemplu pentru a schimba setările, precum backend-ul de inferență.

Utilizați următoarea comandă pentru a testa modelul Qwen3 fine-tuned:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
Mai jos este prezentat un exemplu de chat folosind modelul fine-tuned:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### Exportarea modelului fine-tuned

Pentru cazurile de utilizare în producție, modelul preantrenat și adaptorul LoRA trebuie combinate și exportate într-un singur model. Acest model combinat poate fi utilizat ca un fișier de model Hugging Face obișnuit. LLaMA Factory oferă configurațiile exemplu în [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora).

Utilizați următoarea comandă pentru a exporta modelul Qwen3 fine-tuned:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
Rezultatul exportării modelului fine-tuned este prezentat mai jos.

<p align="center">
  <img src="assets/qwen3_export.png" alt="Export Qwen3 Fine-Tuned model " width="600"/>
</p>

<!-- @os:linux -->
<!-- @test:id=export-llamafactory-model timeout=1800 hidden=True setup=activate-venv -->
```bash
cd LlamaFactory
pip install pyyaml

python - <<'PY'
import yaml
from pathlib import Path

src = Path("examples/merge_lora/qwen3_lora_sft.yaml")
dst = Path("examples/merge_lora/qwen3_lora_sft_ci.yaml")

cfg = yaml.safe_load(src.read_text())

cfg["adapter_name_or_path"] = "saves/qwen3_lora_sft_ci"
cfg["export_dir"] = "saves/qwen3_lora_sft_ci_merged"

dst.write_text(yaml.safe_dump(cfg, sort_keys=False))
print(f"Wrote {dst}")
PY

llamafactory-cli export examples/merge_lora/qwen3_lora_sft_ci.yaml
```
<!-- @test:end --> 
<!-- @os:end -->


<!-- @os:windows -->
<!-- @test:id=export-llamafactory-model timeout=1800 hidden=True setup=activate-venv -->
```powershell
Set-Location -Path "LlamaFactory"
pip install pyyaml

$script = @'
import yaml
from pathlib import Path

src = Path("examples/merge_lora/qwen3_lora_sft.yaml")
dst = Path("examples/merge_lora/qwen3_lora_sft_ci.yaml")

cfg = yaml.safe_load(src.read_text())

cfg["adapter_name_or_path"] = "saves/qwen3_lora_sft_ci"
cfg["export_dir"] = "saves/qwen3_lora_sft_ci_merged"

dst.write_text(yaml.safe_dump(cfg, sort_keys=False))
print(f"Wrote {dst}")
'@

$tempPy = Join-Path $env:TEMP "write_llamafactory_export_config.py"
Set-Content -Path $tempPy -Value $script -Encoding UTF8

python $tempPy
if ($LASTEXITCODE -ne 0) {
    Remove-Item $tempPy -Force -ErrorAction SilentlyContinue
    throw "FAIL: Could not create qwen3_lora_sft_ci.yaml"
}
Remove-Item $tempPy -Force -ErrorAction SilentlyContinue

if (-not (Test-Path "examples/merge_lora/qwen3_lora_sft_ci.yaml")) {throw "FAIL: examples/merge_lora/qwen3_lora_sft_ci.yaml was not created"}

llamafactory-cli export examples/merge_lora/qwen3_lora_sft_ci.yaml
if ($LASTEXITCODE -ne 0) {throw "FAIL: llamafactory-cli export failed"}
```
<!-- @test:end --> 
<!-- @os:end -->

<!-- @test:id=verify-llamafactory-export-output timeout=120 hidden=True setup=activate-venv -->
```python
import os
import sys
import glob

out_dir = "LlamaFactory/saves/qwen3_lora_sft_ci_merged"
if not os.path.isdir(out_dir):
    print(f"FAIL: Missing export directory: {out_dir}")
    sys.exit(1)

required = ["config.json",]
missing = [f for f in required if not os.path.exists(os.path.join(out_dir, f))]
if missing:
    print(f"FAIL: Missing required export files: {missing}")
    sys.exit(1)

model_files = (
    glob.glob(os.path.join(out_dir, "*.safetensors")) +
    glob.glob(os.path.join(out_dir, "pytorch_model*.bin"))
)
if not model_files:
    print("FAIL: Missing merged model weights")
    sys.exit(1)

print("PASS: Exported merged model output looks correct")
```
<!-- @test:end --> 
## Utilizarea interfeței grafice LLaMA Factory

`LLaMA-Factory` acceptă, de asemenea, ajustarea fină (fine-tuning) fără cod a LLM-urilor printr-o interfață web în browser.

Utilizați următoarea comandă pentru a o deschide:

```bash
llamafactory-cli webui
```
`LlamaFactory Web UI` oferă o interfață simplificată pentru gestionarea fluxurilor de lucru de învățare automată, inclusiv antrenare, evaluare, predicție, chat și exportul modelelor. Iată o scurtă prezentare a fiecărei file:

* **Train**: Această filă vă permite să selectați un model și un set de date, să configurați parametrii de antrenare și să inițiați procesul de antrenare. Este esențial să înțelegeți parametrii obligatorii și opționali pentru a optimiza configurația de antrenare.
* **Evaluate & Predict**: După antrenare, puteți evalua performanța modelului și puteți face predicții folosind această filă. Aceasta oferă informații despre acuratețea și eficacitatea modelului pe date noi.
* **Chat**: După finalizarea antrenării, încărcați modelul în fila Chat pentru a interacționa cu acesta și a vedea rezultatele muncii dvs. Această funcție permite comunicarea în timp real cu modelul antrenat.
* **Export**: Această filă facilitează exportul modelelor antrenate pentru implementare sau utilizare ulterioară. Puteți salva modelele în diverse formate potrivite pentru diferite aplicații.

Pentru instrucțiuni detaliate, vă încurajăm să consultați documentația oficială din [repository-ul GitHub LlamaFactory](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) și [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest). În plus, [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) oferă informații valoroase despre interfață și funcționalitățile acesteia.

## Pașii următori
- Încercați modele diferite, precum `gpt-oss` și alte modele de ultimă generație.
- Experimentați cu diferite backend-uri pe modelul ajustat fin

Pentru mai multă documentație, vă rugăm să vizitați: https://llamafactory.readthedocs.io/en/latest/