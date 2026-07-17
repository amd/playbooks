## Przegląd

Wydajne dostrajanie jest kluczowe dla adaptacji dużych modeli językowych (LLM) do zadań downstream. LLaMA-Factory to otwartoźródłowa i przyjazna użytkownikowi platforma, która upraszcza trenowanie i dostrajanie dużych modeli językowych oraz modeli multimodalnych. Umożliwia użytkownikom lokalne dostosowywanie setek wstępnie wytrenowanych modeli przy minimalnym kodowaniu.

Ten poradnik uczy, jak dostrajać LLM przy użyciu LLaMA-Factory na lokalnym sprzęcie AMD.

<!-- @device:stx,krk -->
> **Uwaga:** Techniki dostrajania opisane w tym poradniku wymagają co najmniej **32 GB pamięci RAM systemu**, z czego co najmniej **16 GB musi być dostępne dla GPU** (te 16 GB jest częścią 32 GB, a nie dodatkiem do nich).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Uwaga:** Techniki dostrajania opisane w tym poradniku wymagają co najmniej **16 GB łącznej pamięci GPU** i **32 GB pamięci RAM systemu**.
> - W systemie Windows łączna pamięć GPU łączy dedykowaną pamięć VRAM karty graficznej z pamięcią GPU współdzieloną (pożyczoną z pamięci RAM systemu).
> - Dlatego karty z mniej niż 16 GB dedykowanej pamięci VRAM mogą nadal uruchamiać ten poradnik, korzystając ze współdzielonej pamięci GPU, aby uzupełnić różnicę.
<!-- @os:end -->

<!-- @os:linux -->
> **Uwaga:** Techniki dostrajania opisane w tym poradniku wymagają karty graficznej z co najmniej **16 GB dedykowanej pamięci GPU** i **32 GB pamięci RAM systemu**.
> - W systemie Linux trenowanie odbywa się wyłącznie w dedykowanej pamięci VRAM karty graficznej.
> - Nie przełącza się na współdzieloną pamięć GPU (pamięć RAM systemu) po wyczerpaniu pamięci VRAM.
> - Karty z mniej niż 16 GB dedykowanej pamięci VRAM wyczerpią pamięć podczas trenowania w systemie Linux, nawet jeśli system dysponuje dużą ilością pamięci RAM.
<!-- @os:end -->
<!-- @device:end -->

## Czego się nauczysz

- Jak skonfigurować LLaMA-Factory z oprogramowaniem AMD ROCm™
- Jak konfigurować parametry dostrajania LLM (na przykładzie Qwen/Qwen3-4B-Instruct-2507)
- Jak uruchomić dostrajanie w LLaMA-Factory
- Jak uruchomić wnioskowanie z dostrojonym modelem
- Jak wyeksportować dostrojony model

## Szacowany czas

- Czas trwania: Uruchomienie tego poradnika zajmie około 60 minut (w zależności od rozmiaru modelu/zbioru danych i prędkości sieci).
- Więcej informacji znajdziesz w [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory).

## Konfigurowanie ustawień pamięci

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania

<!-- @require:software-update -->
<!-- @device:end -->

## Instalowanie wymagań wstępnych oprogramowania

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

#### Tworzenie środowiska wirtualnego

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
**Przyznaj swojemu użytkownikowi dostęp do urządzeń GPU** (wyloguj się i zaloguj ponownie, aby zmiany weszły w życie):

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

### Instalowanie podstawowych zależności

<!-- @require:pytorch,driver -->
 
### Instalowanie dodatkowych zależności

> **Uwaga**: Upewnij się, że wersja Pythona to 3.11, 3.12 lub 3.13

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

### Instalowanie LLaMA-Factory

LLaMA-Factory zależy od PyTorch. Powinieneś mieć go już zainstalowanego zgodnie z powyższymi wymaganiami.

Pobierz kod źródłowy z [oficjalnego repozytorium LLaMA Factory na GitHub](https://github.com/hiyouga/LlamaFactory) i zainstaluj jego zależności.

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

Sprawdź, czy `llamafactory-cli` jest wykonywalny.

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

Przykładowe wyjście:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

Po pomyślnym zainstalowaniu LLaMA-Factory uruchommy na nim dostrajanie.

## Używanie interfejsu CLI LLaMA-Factory do dostrajania

Ta sekcja opisuje, jak przygotować zbiory danych do dostrajania, skonfigurować parametry LoRA/QLoRA i uruchomić dostrajanie LoRA.

### Przygotowanie zbioru danych

LLaMA-Factory obsługuje zbiory danych do dostrajania w formacie Alpaca i formacie ShareGPT. Wszystkie dostępne zbiory danych zostały zdefiniowane w pliku [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). Jeśli używasz niestandardowego zbioru danych, upewnij się, że dodałeś opis zbioru danych w `dataset_info.json` i określiłeś nazwę zbioru danych przed trenowaniem. Szczegóły można znaleźć w dokumentacji [tutaj](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

W tym poradniku użyjemy zbiorów danych identity i alpaca_en_demo jako przykładu i skonfigurujemy informacje o zbiorze danych w następnym kroku.


### Konfiguracja parametrów dostrajania

LLaMA-Factory obsługuje wiele schematów dostrajania.

| Schematy dostrajania | Przykłady LLaMA-Factory |
|-----------|------|
| Pełne parametry    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
| Dostrajanie LoRA  | [examples/train_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_lora) |
| Dostrajanie QLoRA | [examples/train_qlora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_qlora) |

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

Te przykładowe pliki konfiguracyjne określają parametry modelu, parametry metody dostrajania, parametry zbioru danych, parametry ewaluacji i inne. Możesz je konfigurować zgodnie z własnymi potrzebami. W tym poradniku użyjemy pliku [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml).

**Objaśnienie kluczowych parametrów:**
- `model_name_or_path` - Nazwa modelu Hugging Face lub lokalna ścieżka do pliku modelu.
- `stage` - Etap trenowania. Opcje: rm (modelowanie nagród), pt (pretrenowanie), sft (nadzorowane dostrajanie), PPO, DPO, KTO, ORPO.
- `do_train` - true dla trenowania, false dla ewaluacji
- `finetuning_type` - Metoda dostrajania. Opcje: freeze, lora, full
- `lora_rank` - Wymiarowość macierzy niskiej rangi używanej w LoRA, typowe wartości: 4, 6, 8, 16 (mniejsze wartości = mniej parametrów = szybsze dostrajanie; większe wartości = lepsza adaptacja do zadania, ale większe zużycie zasobów).
- `lora_target` - Moduły docelowe dla metody LoRA. Domyślnie: all.
- `dataset` - Zbiór/zbiory danych do użycia. Użyj „," do oddzielenia wielu zbiorów danych
- `output_dir` - Ścieżka wyjściowa dostrajania
- `logging_steps` - Interwał logowania w krokach
- `save_steps` - Interwał zapisywania punktów kontrolnych modelu.
- `overwrite_output_dir` - Czy zezwolić na nadpisanie katalogu wyjściowego.
- `per_device_train_batch_size` - Rozmiar wsadu trenowania na urządzenie.
- `gradient_accumulation_steps` - Liczba kroków akumulacji gradientu.
- `learning_rate` - Współczynnik uczenia
- `num_train_epochs` - Liczba epok trenowania
- `lr_scheduler_type` - Harmonogram współczynnika uczenia. Opcje: linear, cosine, polynomial, constant itp.
- `warmup_ratio` - Współczynnik rozgrzewki współczynnika uczenia

<!-- @os:linux -->
Zmodyfikujemy domyślną wartość `lora_rank`, aby uruchomić dostrajanie na GPU AMD Ryzen™ i AMD Radeon™.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
Zaktualizujemy domyślną konfigurację dostrajania LoRA w celu lepszej zgodności z GPU AMD Ryzen™ i AMD Radeon™:
- Ustawiamy `lora_rank` z `8` na `6`, aby zmniejszyć zużycie pamięci podczas dostrajania.
- Używamy `fp16` zamiast `bf16` dla szerszej zgodności z GPU AMD i mniejszego zużycia pamięci.
- Ustawiamy `dataloader_num_workers` na `0` w systemie Windows, aby uniknąć błędów `"Can't pickle local object<>"` spowodowanych wieloprocesowym ładowaniem danych.

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

### Uruchamianie dostrajania LLaMA-Factory

**llamafactory-cli** to oficjalny interfejs wiersza poleceń (CLI) dla LLaMA-Factory, opracowany w celu uproszczenia kompleksowych przepływów pracy LLM (przygotowanie danych → dostrajanie → ewaluacja → wdrożenie) bez pisania złożonego kodu.

Do trenowania/dostrajania **llamafactory-cli train** jest podstawowym podpoleceniem CLI LLaMA-Factory. Abstrahuje przepływy pracy dostrajania (wstępne przetwarzanie danych, dostrajanie hiperparametrów, optymalizacja sprzętu) do jednego polecenia CLI, obsługując wiele paradygmatów dostrajania (LoRA/QLoRA/pełne dostrajanie) i jest zoptymalizowany pod kątem GPU o niskich zasobach (np. QLoRA na 16 GB VRAM).

Możesz uruchomić dostrajanie LLaMA-Factory za pomocą następującego polecenia, które opiera się na zmodyfikowanym pliku konfiguracyjnym dostrajania LoRA Qwen3.

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

Po uruchomieniu dostrajania LLM wszystkie wygenerowane wyniki są przechowywane w „output_dir", w tym pliki punktów kontrolnych modelu, pliki konfiguracyjne i metryki trenowania.

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

### Testowanie dostrojonego modelu

**llamafactory-cli chat** jest przeznaczony do interaktywnego czatu/wnioskowania z LLM (zarówno modelami bazowymi, jak i modelami dostrojonymi LoRA). LLaMA-Factory udostępnia przykładową konfigurację do uruchamiania wnioskowania dostrojonych modeli w [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference). Możesz również zmodyfikować tę przykładową konfigurację, aby zmienić ustawienia, takie jak backend wnioskowania.

Użyj następującego polecenia, aby przetestować dostrojony model Qwen3:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
Poniżej przedstawiono przykładowy czat z użyciem dostrojonego modelu:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### Eksportowanie dostrojonego modelu

W przypadkach użycia produkcyjnego wstępnie wytrenowany model i adapter LoRA muszą zostać scalone i wyeksportowane do jednego modelu. Ten scalony model może być używany jako normalny plik modelu Hugging Face. LLaMA-Factory udostępnia przykładowe konfiguracje w [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora).

Użyj następującego polecenia, aby wyeksportować dostrojony model Qwen3:

```bash
llamafactory-cli export examples/merge_lora/qwen3_lora_sft.yaml
```
Poniżej przedstawiono wynik eksportowania dostrojonego modelu.

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

## Używanie interfejsu GUI LLaMA-Factory

`LLaMA-Factory` obsługuje również dostrajanie LLM bez kodu za pośrednictwem interfejsu webowego w przeglądarce.

Użyj następującego polecenia, aby go otworzyć:

```bash
llamafactory-cli webui
```
`LlamaFactory Web UI` oferuje uproszczony interfejs do zarządzania przepływami pracy uczenia maszynowego, w tym trenowaniem, ewaluacją, predykcją, czatem i eksportowaniem modeli. Oto krótkie wprowadzenie do każdej karty:

* **Train**: Ta karta umożliwia wybór modelu i zbioru danych, konfigurację parametrów trenowania i zainicjowanie procesu trenowania. Ważne jest zrozumienie obowiązkowych i opcjonalnych parametrów w celu optymalizacji konfiguracji trenowania.
* **Evaluate & Predict**: Po trenowaniu możesz ocenić wydajność modelu i dokonywać predykcji za pomocą tej karty. Zapewnia ona wgląd w dokładność i skuteczność modelu na nowych danych.
* **Chat**: Po zakończeniu trenowania załaduj model w karcie Chat, aby wchodzić z nim w interakcję i zobaczyć wyniki swojej pracy. Ta funkcja umożliwia komunikację w czasie rzeczywistym z wytrenowanym modelem.
* **Export**: Ta karta ułatwia eksport wytrenowanych modeli do wdrożenia lub dalszego użycia. Możesz zapisywać modele w różnych formatach odpowiednich dla różnych zastosowań.

Aby uzyskać szczegółowe wskazówki, zachęcamy do zapoznania się z oficjalną dokumentacją w [repozytorium LlamaFactory na GitHub](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) oraz [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest). Ponadto [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) dostarcza cennych informacji na temat interfejsu i jego funkcjonalności.

## Następne kroki
- Wypróbuj różne modele, takie jak `gpt-oss` i inne najnowocześniejsze modele.
- Eksperymentuj z różnymi backendami na dostrojonym modelu
 
Więcej dokumentacji znajdziesz pod adresem: https://llamafactory.readthedocs.io/en/latest/