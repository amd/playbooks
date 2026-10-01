<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tłumaczenie maszynowe.** Ta strona została automatycznie przetłumaczona z języka angielskiego i nie została zweryfikowana przez człowieka. Może zawierać błędy, a niektóre instrukcje, polecenia, pliki do pobrania, dostępność produktów lub inne treści mogą różnić się w zależności od języka lub regionu. W przypadku jakichkolwiek niezgodności lub rozbieżności rozstrzygająca jest oryginalna angielska wersja playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Przegląd

Ten poradnik pokazuje, jak dostroić model językowy lokalnie przy użyciu Unsloth na sprzęcie AMD.

Wykorzystuje krótki przykład Nadzorowanego Dostrajania (SFT) z adapterami LoRA na `unsloth/gemma-4-E4B-it`, przy użyciu podzbioru zestawu danych `mlabonne/FineTome-100k`. Celem jest przedstawienie prostego, kompleksowego przepływu pracy obejmującego konfigurację, trenowanie, wnioskowanie i zapisywanie dostrojonego wyniku.

Przykład został zaprojektowany tak, aby był praktyczny i łatwy do modyfikacji, dzięki czemu można go wykorzystać jako punkt wyjścia dla własnych zestawów danych i modeli.

## Czego się nauczysz

- Jak skonfigurować środowisko Unsloth
- Jak dostroić LLM przy użyciu SFT w Unsloth
- Jak zapisać dostrojony wynik w pamięci lokalnej

<!-- @device:halo,stx,krk -->
> **Uwaga:** Techniki dostrajania opisane w tym poradniku wymagają co najmniej **64 GB pamięci RAM systemu**, z czego co najmniej **24 GB musi być dostępne dla GPU** (24 GB stanowi część tych 64 GB, a nie dodatkową wartość).
<!-- @device:end -->


<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @os:windows -->
> **Uwaga:** Techniki dostrajania opisane w tym poradniku wymagają co najmniej **24 GB łącznej pamięci GPU** oraz **32 GB pamięci RAM systemu**.
> - W systemie Windows łączna pamięć GPU obejmuje dedykowaną pamięć VRAM karty graficznej oraz współdzieloną pamięć GPU (pożyczaną z pamięci RAM systemu).
> - Dzięki temu karty z mniej niż 24 GB dedykowanej pamięci VRAM mogą nadal obsłużyć ten poradnik, wykorzystując współdzieloną pamięć GPU, aby uzupełnić różnicę.
<!-- @os:end -->

<!-- @os:linux -->
> **Uwaga:** Techniki dostrajania opisane w tym poradniku wymagają karty graficznej z co najmniej **24 GB dedykowanej pamięci GPU** oraz **32 GB pamięci RAM systemu**.
> - W systemie Linux trenowanie odbywa się wyłącznie w dedykowanej pamięci VRAM karty graficznej.
> - Nie następuje przełączenie na współdzieloną pamięć GPU (RAM systemu), gdy pamięć VRAM się wyczerpie.
> - Karty z mniej niż 24 GB dedykowanej pamięci VRAM wyczerpią pamięć podczas trenowania w systemie Linux, nawet jeśli system ma dużo pamięci RAM.
<!-- @os:end -->
<!-- @device:end -->

## Dlaczego Unsloth?

Unsloth ułatwia uruchamianie dostrajania LLM na lokalnym sprzęcie, zmniejszając zużycie pamięci i przyspieszając trenowanie w porównaniu ze standardową konfiguracją.

W tym poradniku używamy Unsloth razem z **SFT opartym na LoRA**. Oznacza to, że model bazowy pozostaje w większości zamrożony, a trenowany jest znacznie mniejszy zestaw wag adapterów. Jest to dobre rozwiązanie do lokalnego rozwoju, ponieważ jest lżejsze niż pełne dostrajanie i szybsze w iteracji.

Unsloth obsługuje również inne podejścia do trenowania, w tym QLoRA i przepływy pracy uczenia ze wzmocnieniem. Ten poradnik koncentruje się najpierw na najprostszej ścieżce: niewielkim przykładzie dostrajania LoRA, który użytkownicy mogą uruchomić, zrozumieć i rozszerzyć.

<!-- @device:halo_box,halo,stx,krk -->
## Ustawianie konfiguracji pamięci

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Sprawdź aktualizacje oprogramowania
> **Uwaga**: Jeśli VS Code nie jest zainstalowany, możesz go zainstalować za pomocą Ryzen AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalowanie wymaganego oprogramowania

### Utwórz środowisko wirtualne

<!-- @os:linux -->
<!-- @device:halo_box -->
Otwórz terminal i utwórz środowisko venv z już zainstalowanym oprogramowaniem AMD ROCm™ i PyTorch:
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
**Nadaj swojemu użytkownikowi dostęp do urządzeń GPU** (wyloguj się i zaloguj ponownie, aby zmiana weszła w życie):

```bash
sudo usermod -aG render,video $LOGNAME
```

Otwórz terminal i utwórz środowisko venv:
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
> **Uwaga:** W systemie Windows wymagany jest Python 3.13.

<!-- @device:halo_box -->
Otwórz terminal PowerShell i utwórz środowisko wirtualne:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env --system-site-packages
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
Otwórz terminal PowerShell i utwórz środowisko wirtualne:
<!-- @test:id=create-venv timeout=120 -->
```powershell
python -m venv unsloth-env
.\unsloth-env\Scripts\activate
```
<!-- @test:end -->
<!-- @setup:id=activate-venv command="unsloth-env\Scripts\activate" -->
<!-- @device:end -->
<!-- @os:end -->

### Instalowanie podstawowych zależności
<!-- @require:driver -->

> **Ważne:** Unsloth nie obsługuje jeszcze wersji PyTorch 2.13 dostarczanej z ROCm 10. W tym poradniku zainstaluj **ROCm 7.14 z PyTorch 2.12** za pomocą poniższych poleceń. Nie używaj pakietów ROCm 10 / PyTorch 2.13.

**Zainstaluj PyTorch z obsługą AMD ROCm™** w utworzonym środowisku wirtualnym:

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

W przypadku innych urządzeń zapoznaj się z pełnymi instrukcjami w [dokumentacji ROCm 7.14](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/frameworks/pytorch/install.html).

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

### Dodatkowe zależności

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

> **Uwaga:** Podczas importu Unsloth może sprawdzać opcjonalne ścieżki akceleracji `bitsandbytes`. W niektórych wersjach ROCm może pojawić się komunikat taki jak `bitsandbytes library load error: Configured ROCm binary not found`. Ten poradnik wykorzystuje standardowe dostrajanie LoRA z `optim="adamw_torch"`, więc nie polegamy na optymalizatorze `bitsandbytes` ani na QLoRA 4-bit. Ten komunikat można bezpiecznie zignorować.

<!-- @os:windows -->
> **Uwaga:** W systemie Windows z ROCm, Unsloth wyświetli kilka ostrzeżeń podczas uruchamiania — zobacz [Znane ostrzeżenia](#known-warnings) poniżej. Wszystkie z nich można bezpiecznie zignorować; trenowanie działa poprawnie.
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

## Pobierz skrypt dostrajania Unsloth

Zamiast ręcznie wykonywać każdy krok, ten poradnik udostępnia czysty, kompleksowy skrypt tutaj: [test_unsloth.py](assets/test_unsloth.py).

Uruchom poniższy kod, aby wykonać skrypt:

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

Reszta poradnika koncepcyjnie omówi każdy główny krok skryptu.

## Jak to działa

Skrypt test_unsloth.py wykonuje następujące kroki:
* **Wczytanie modelu**: Wczytuje unsloth/gemma-4-E4B-it przy użyciu FastModel.
* **Przygotowanie danych**: Standaryzuje zestaw danych (np. FineTome-100k) i stosuje szablon czatu Gemma-4.
* **Zastosowanie LoRA**: Dodaje adaptery do modułów językowych, uwagi (attention) i MLP w celu efektywnego trenowania.
* **Trenowanie**: Wykorzystuje SFTTrainer z maskowaniem straty tylko dla odpowiedzi (response-only loss masking).
* **Wnioskowanie**: Uruchamia szybki test generowania w celu weryfikacji wydajności.
* **Zapis**: Eksportuje adaptery LoRA lokalnie.
## Kluczowa konfiguracja

Możesz zmodyfikować następujące stałe, aby dostosować swoje uruchomienie:

```python
MODEL_NAME = "unsloth/gemma-4-E4B-it"
MAX_SEQ_LEN = 1024
DATASET_NAME = "mlabonne/FineTome-100k"
OUTPUT_DIR = "gemma_4_lora"
```

Przykład powitalnej wiadomości Unsloth i danych wyjściowych podczas wczytywania wag modelu:

![alt text](assets/welcome.png)

## Przygotowanie zbioru danych

Używamy podzbioru:
```text
mlabonne/FineTome-100k
```
Zbiór danych jest: 
* Konwertowany do formatu czatu
* Przetwarzany przy użyciu szablonu czatu Gemma-4
* Czyszczony w celu usunięcia zduplikowanych tokenów BOS

## Trenowanie modelu

Skrypt uruchamia krótkie demo treningowe, z następującymi parametrami:
- ~50 kroków
- Mały rozmiar wsadu (batch)
- Akumulacja gradientu

Podczas trenowania zobaczysz logi takie jak:

![alt text](assets/training.png)


## Zapisywanie i wdrażanie

### Zapis lokalny (LoRA)

Skrypt automatycznie zapisuje adaptery LoRA do OUTPUT_DIR.
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

### Zapisz scalony model (dla vLLM) 

<!-- @os:windows -->
> **Uwaga:** vLLM nie obsługuje systemu Windows. Aby wdrożyć swój dostrojony model na Windows, użyj llama.cpp (zobacz [Eksportowanie GGUF](#export-gguf-for-llamacpp) poniżej) lub przenieś scalony model na maszynę z systemem Linux z uruchomionym vLLM.
<!-- @os:end -->

<!-- @os:linux -->
Aby wdrożyć z vLLM, scal adaptery w pełny model:
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

### Eksportuj GGUF (dla llama.cpp)

Przekonwertuj bezpośrednio do GGUF w celu lokalnego wnioskowania:
```python
model.save_pretrained_gguf("gemma_4_finetune", tokenizer, quantization_method="Q8_0")
```

<!-- @os:windows -->
## Znane ostrzeżenia

Te ostrzeżenia są wyświetlane przez Unsloth podczas uruchamiania na Windows ROCm i wszystkie można bezpiecznie zignorować:

| Ostrzeżenie | Przyczyna | Można bezpiecznie zignorować? |
|---|---|---|
| `bitsandbytes library load error` | bitsandbytes nie ma kompilacji dla Windows ROCm | Tak — ten przewodnik używa `adamw_torch`, a nie bnb |
| `No ROCm platform found for torch.distributed` | ROCm na Windows nie obsługuje trenowania rozproszonego | Tak — trenowanie na pojedynczym GPU nie jest tym dotknięte |
| `Unsloth: WARNING! You are using an unsupported platform` | Unsloth oznacza kompilacje inne niż Linux | Tak — Windows ROCm działa poprawnie przy SFT na pojedynczym GPU |
| `triton is not available` | Triton nie ma kompilacji dla Windows | Tak — Unsloth korzysta wtedy z jąder PyTorch |

Trenowanie będzie przebiegać poprawnie pomimo tych ostrzeżeń.
<!-- @os:end -->

## Kolejne kroki
- Wypróbuj [Unsloth Studio](https://unsloth.ai/docs/new/studio), intuicyjny interfejs GUI dla Unsloth
- Trenuj na własnych, specyficznych zbiorach danych
- Wypróbuj dostrajanie z różnymi hiperparametrami
- Wdróż za pomocą vLLM lub llama.cpp
- Wypróbuj QLoRA dla konfiguracji o niższym zużyciu pamięci

## Zasoby

Poniżej znajduje się kilka dodatkowych zasobów, aby dowiedzieć się więcej o Unsloth i dostrajaniu:

* [Dokumentacja Unsloth](https://docs.unsloth.ai)

* [Unsloth GitHub](https://github.com/unslothai/unsloth)

* [Przewodnik po dostrajaniu Unsloth](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)