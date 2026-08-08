<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tłumaczenie maszynowe.** Ta strona została automatycznie przetłumaczona z języka angielskiego i nie została zweryfikowana przez człowieka. Może zawierać błędy, a niektóre instrukcje, polecenia, pliki do pobrania, dostępność produktów lub inne treści mogą różnić się w zależności od języka lub regionu. W przypadku jakichkolwiek niezgodności lub rozbieżności rozstrzygająca jest oryginalna angielska wersja playbook.
<!-- auto-translated-disclaimer:end -->

## Przegląd

Efektywne dostrajanie ma kluczowe znaczenie dla adaptacji dużych modeli językowych (LLM) do zadań końcowych. LLaMA Factory to otwarta i przyjazna dla użytkownika platforma, która usprawnia trenowanie i dostrajanie dużych modeli językowych oraz modeli multimodalnych. Umożliwia użytkownikom lokalne dostosowywanie setek wstępnie wytrenowanych modeli przy minimalnej ilości kodowania.

Ten przewodnik nauczy Cię, jak dostrajać modele LLM przy użyciu LLaMA Factory na lokalnym sprzęcie AMD.

<!-- @device:stx,krk -->
> **Uwaga:** Techniki dostrajania opisane w tym przewodniku wymagają co najmniej **32 GB pamięci RAM systemu**, przy czym co najmniej **16 GB z tego musi być dostępne dla GPU** (owe 16 GB stanowi część 32 GB, a nie dodatkową wartość).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Uwaga:** Techniki dostrajania opisane w tym przewodniku wymagają co najmniej **16 GB łącznej pamięci GPU** oraz **32 GB pamięci RAM systemu**.
> - W systemie Windows łączna pamięć GPU obejmuje dedykowaną pamięć VRAM karty graficznej oraz współdzieloną pamięć GPU (pożyczoną z pamięci RAM systemu).
> - Dlatego karty z mniej niż 16 GB dedykowanej pamięci VRAM mogą nadal obsługiwać ten przewodnik, wykorzystując współdzieloną pamięć GPU w celu uzupełnienia różnicy.
<!-- @os:end -->

<!-- @os:linux -->
> **Uwaga:** Techniki dostrajania opisane w tym przewodniku wymagają karty graficznej z co najmniej **16 GB dedykowanej pamięci GPU** oraz **32 GB pamięci RAM systemu**.
> - W systemie Linux trenowanie odbywa się w całości w dedykowanej pamięci VRAM karty graficznej.
> - Nie następuje przełączenie na współdzieloną pamięć GPU (pamięć RAM systemu), gdy zabraknie pamięci VRAM.
> - Karty z mniej niż 16 GB dedykowanej pamięci VRAM wyczerpią dostępną pamięć podczas trenowania w systemie Linux, nawet jeśli system dysponuje dużą ilością pamięci RAM.
<!-- @os:end -->
<!-- @device:end -->

## Czego się nauczysz

- Jak skonfigurować LLaMA Factory z oprogramowaniem AMD ROCm™
- Jak skonfigurować parametry dostrajania LLM (na przykładzie Qwen/Qwen3-4B-Instruct-2507)
- Jak uruchomić dostrajanie w LLaMA Factory
- Jak przeprowadzić wnioskowanie przy użyciu dostrojonego modelu
- Jak wyeksportować dostrojony model

## Szacowany czas

- Czas trwania: Uruchomienie tego przewodnika zajmie około 60 minut (w zależności od rozmiaru modelu/zbioru danych oraz prędkości sieci).
- Więcej informacji znajdziesz na stronie [LLaMA Factory GitHub](https://github.com/hiyouga/LlamaFactory).

## Konfiguracja pamięci

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Sprawdzanie aktualizacji oprogramowania

<!-- @require:software-update -->
<!-- @device:end -->

## Instalowanie wymaganego oprogramowania

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
**Nadaj swojemu użytkownikowi dostęp do urządzeń GPU** (wyloguj się i zaloguj ponownie, aby zmiana zaczęła obowiązywać):

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

### Instalowanie LLaMA Factory

LLaMA Factory zależy od PyTorch. Zgodnie z powyższymi wymaganiami powinieneś go już mieć zainstalowanego.

Pobierz kod źródłowy z [oficjalnego repozytorium GitHub LLaMA Factory](https://github.com/hiyouga/LlamaFactory) i zainstaluj jego zależności.

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

Przykładowe dane wyjściowe:

<p align="center">
  <img src="assets/LlamaFactory-version.png" alt="LlaMaFactory version" width="600"/>
</p>

Po pomyślnym zainstalowaniu LLaMA Factory, uruchommy na nim dostrajanie.

## Korzystanie z interfejsu wiersza poleceń LLaMA Factory do dostrajania

Ta sekcja obejmuje przygotowanie zbiorów danych do dostrajania, konfigurację parametrów LoRA/QLoRA oraz uruchamianie dostrajania LoRA.

### Przygotowanie zbioru danych

LLaMA Factory obsługuje zbiory danych do dostrajania w formacie Alpaca oraz formacie ShareGPT. Wszystkie dostępne zbiory danych zostały zdefiniowane w pliku [dataset_info.json](https://github.com/hiyouga/LlamaFactory/blob/main/data/dataset_info.json). Jeśli korzystasz z niestandardowego zbioru danych, upewnij się, że dodałeś jego opis w pliku `dataset_info.json` oraz określ nazwę zbioru danych przed rozpoczęciem trenowania. Szczegóły znajdziesz w ich dokumentacji [tutaj](https://llamafactory.readthedocs.io/en/latest/getting_started/data_preparation.html).

W tym przewodniku, jako przykład, wykorzystamy zbiory danych identity oraz alpaca_en_demo, a informacje o zbiorze danych skonfigurujemy w następnym kroku.
### Konfiguracja parametrów dostrajania

LLaMA Factory obsługuje wiele schematów dostrajania.

| Schematy dostrajania | Przykłady LLaMA Factory |
|-----------|------|
| Pełnoparametrowe    | [examples/train_full](https://github.com/hiyouga/LlamaFactory/tree/main/examples/train_full) |
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

Te przykładowe pliki konfiguracyjne określają parametry modelu, parametry metody dostrajania, parametry zbioru danych, parametry ewaluacji i inne. Możesz je skonfigurować zgodnie z własnymi potrzebami. W tym przewodniku użyjemy pliku [qwen3_lora_sft.yaml](https://github.com/hiyouga/LlamaFactory/blob/main/examples/train_lora/qwen3_lora_sft.yaml). 

**Wyjaśnienie kluczowych parametrów:**
- `model_name_or_path` - Nazwa modelu Hugging Face lub lokalna ścieżka do pliku modelu.
- `stage` - Etap treningu. Opcje: rm (modelowanie nagrody), pt (pretrening), sft (nadzorowane dostrajanie), PPO, DPO, KTO, ORPO.
- `do_train` - true dla treningu, false dla ewaluacji
- `finetuning_type` - Metoda dostrajania. Opcje: freeze, lora, full
- `lora_rank` - Wymiarowość macierzy niskiego rzędu używanej w LoRA, typowe wartości: 4, 6, 8, 16 (mniejsze wartości = mniej parametrów = szybsze dostrajanie; większe wartości = lepsze dopasowanie do zadania, ale wyższe zużycie zasobów).
- `lora_target` - Moduły docelowe dla metody LoRA. Domyślnie: all.
- `dataset` - Zbiór(y) danych do użycia. Użyj „,” aby oddzielić wiele zbiorów danych
- `output_dir` - Ścieżka wyjściowa dostrajania
- `logging_steps` - Interwał logowania w krokach
- `save_steps` - Interwał zapisywania punktów kontrolnych modelu.
- `overwrite_output_dir` - Czy zezwolić na nadpisywanie katalogu wyjściowego.
- `per_device_train_batch_size` - Rozmiar wsadu treningowego na urządzenie.
- `gradient_accumulation_steps` - Liczba kroków akumulacji gradientu.
- `learning_rate` - Współczynnik uczenia
- `num_train_epochs` - Liczba epok treningowych
- `lr_scheduler_type` - Harmonogram współczynnika uczenia. Opcje: linear, cosine, polynomial, constant, itd.
- `warmup_ratio` - Współczynnik rozgrzewki współczynnika uczenia

<!-- @os:linux -->
Zmienimy domyślną wartość `lora_rank`, aby uruchomić dostrajanie na AMD Ryzen™ i AMD Radeon™ GPU.
```bash
sed -i.bak 's/lora_rank: 8/lora_rank: 6/g' examples/train_lora/qwen3_lora_sft.yaml
```
<!-- @os:end -->

<!-- @os:windows -->
Zaktualizujemy domyślną konfigurację dostrajania LoRA w celu lepszej kompatybilności z AMD Ryzen™ i AMD Radeon™ GPU:
- Zmień `lora_rank` z `8` na `6`, aby zmniejszyć zużycie pamięci podczas dostrajania.
- Użyj `fp16` zamiast `bf16` dla szerszej kompatybilności z AMD GPU i niższego zużycia pamięci.
- Ustaw `dataloader_num_workers` na `0` w systemie Windows, aby uniknąć błędów `"Can't pickle local object<>"` spowodowanych wieloprocesowym ładowaniem danych.

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

### Uruchamianie dostrajania LLaMA Factory 

**llamafactory-cli** to oficjalne narzędzie interfejsu wiersza poleceń (CLI) dla LLaMA Factory, opracowane w celu uproszczenia kompleksowych przepływów pracy LLM (przygotowanie danych → dostrajanie → ewaluacja → wdrożenie) bez konieczności pisania złożonego kodu.

Do treningu/dostrajania **llamafactory-cli train** jest podstawowym podpoleceniem CLI LLaMA Factory. Abstrahuje ono przepływy pracy dostrajania (przetwarzanie wstępne danych, dostrajanie hiperparametrów, optymalizacja sprzętowa) do jednego polecenia CLI, obsługując wiele paradygmatów dostrajania (LoRA/QLoRA/pełne dostrajanie) i jest zoptymalizowane pod kątem GPU o niskich zasobach (np. QLoRA na 16 GB VRAM).

Możesz uruchomić dostrajanie LLaMA Factory za pomocą następującego polecenia, opartego na zmodyfikowanym pliku konfiguracyjnym dostrajania Qwen3 LoRA.

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

Po uruchomieniu dostrajania LLM wszystkie wygenerowane dane wyjściowe są przechowywane w katalogu „output_dir”, w tym pliki punktów kontrolnych modelu, pliki konfiguracyjne i metryki treningowe.

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

**llamafactory-cli chat** jest przeznaczone do interaktywnego czatu/wnioskowania z LLM (zarówno modelami bazowymi, jak i modelami dostrojonymi za pomocą LoRA). LLaMA Factory udostępnia przykładową konfigurację do uruchamiania wnioskowania dostrojonych modeli w [examples/inference](https://github.com/hiyouga/LlamaFactory/tree/main/examples/inference). Możesz również zmodyfikować tę przykładową konfigurację, aby zmienić ustawienia, takie jak backend wnioskowania.

Użyj następującego polecenia, aby przetestować dostrojony model Qwen3:

```bash
llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml
```
Poniżej przedstawiono przykładowy czat z użyciem dostrojonego modelu:

<p align="center">
  <img src="assets/qwen3_chat.png" alt="Test Qwen3 Fine-Tuned model" width="600"/>
</p>


### Eksportowanie dostrojonego modelu

W przypadku zastosowań produkcyjnych, wstępnie wytrenowany model i adapter LoRA muszą zostać scalone i wyeksportowane do pojedynczego modelu. Ten scalony model może być używany jako zwykły plik modelu Hugging Face. LLaMA Factory udostępnia przykładowe konfiguracje w [examples/merge_lora](https://github.com/hiyouga/LlamaFactory/tree/main/examples/merge_lora).

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
## Korzystanie z GUI LLaMA Factory

`LLaMA-Factory` obsługuje również bezkodowe dostrajanie LLM-ów za pomocą interfejsu webowego w przeglądarce.

Aby go otworzyć, użyj następującego polecenia:

```bash
llamafactory-cli webui
```
`LlamaFactory Web UI` oferuje uproszczony interfejs do zarządzania przepływami pracy w uczeniu maszynowym, obejmującymi trenowanie, ocenę, przewidywanie, czat oraz eksportowanie modeli. Poniżej znajduje się krótkie wprowadzenie do każdej z zakładek:

* **Train**: Ta zakładka umożliwia wybór modelu i zbioru danych, konfigurację parametrów trenowania oraz uruchomienie procesu trenowania. Istotne jest zrozumienie parametrów obowiązkowych i opcjonalnych w celu optymalizacji konfiguracji trenowania.
* **Evaluate & Predict**: Po zakończeniu trenowania możesz ocenić wydajność modelu i dokonywać przewidywań za pomocą tej zakładki. Dostarcza ona informacji na temat dokładności i skuteczności modelu na nowych danych.
* **Chat**: Po zakończeniu trenowania załaduj model w zakładce Chat, aby wejść z nim w interakcję i zobaczyć efekty swojej pracy. Ta funkcja umożliwia komunikację z wytrenowanym modelem w czasie rzeczywistym.
* **Export**: Ta zakładka ułatwia eksport wytrenowanych modeli w celu wdrożenia lub dalszego wykorzystania. Możesz zapisywać swoje modele w różnych formatach odpowiednich do różnych zastosowań.

Aby uzyskać szczegółowe wskazówki, zachęcamy do zapoznania się z oficjalną dokumentacją w [repozytorium GitHub LlamaFactory](https://github.com/hiyouga/LlamaFactory#fine-tuning-with-llama-board-gui-powered-by-gradio) oraz na stronie [LlamaFactory ReadTheDocs](https://llamafactory.readthedocs.io/en/latest). Dodatkowo, [Wiki LLaMA Board Web UI](https://deepwiki.com/xtong-zhang/Chain-of-Focus/3.2-llama-board-web-ui) zawiera cenne informacje na temat interfejsu i jego funkcjonalności.

## Kolejne kroki
- Wypróbuj różne modele, takie jak `gpt-oss` i inne najnowocześniejsze modele.
- Poeksperymentuj z różnymi backendami na dostrojonym modelu
 
Więcej dokumentacji znajdziesz na stronie: https://llamafactory.readthedocs.io/en/latest/ 